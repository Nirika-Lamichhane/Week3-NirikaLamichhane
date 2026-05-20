# Pipeline Architecture & Design

## Architecture
The system uses a **Multi-Stage Agentic Prompt Chaining Architecture**.
1. **Semantic Parsing:** Gemini generates SQL from natural language.
2. **Security Guardrail:** The `is_query_safe` validator strips malicious keywords (`DELETE`, `DROP`).
3. **Execution Engine:** Runs valid queries against PostgreSQL.



## Design Decisions
- **Decoupling:** I separated the Generator from the Validator to ensure that the LLM could be swapped out without breaking security protocols.
- **Resilience:** I implemented a retry mechanism that captures database errors and feeds them back into the LLM, allowing for "self-healing" queries.

## Example Query Cases

### Successful Case
- **Question:** "List all products"
- **Logic:** The LLM successfully mapped the natural language request to a simple `SELECT *` statement. No retries were needed.

### Failed Case & Retry Handling
- **Scenario:** The user asks for a table that does not exist.
- **Behavior:** The `executor.py` catches a `DatabaseError`. 
- **Retry Logic:** The system logs the failure, marks `retry_needed: Yes`, and passes the error back to the LLM. The agent recognizes the missing table error and prompts the user for clarification.