# Intelligent Text-to-SQL Agent

A production-grade, secure Text-to-SQL agent designed to bridge the gap between natural language user input and relational database management systems. Built with **FastAPI**, **Gemini API**, and **PostgreSQL**.

---

## Project Architecture & Workflow

This system employs a **Multi-Stage Agentic Prompt Chaining Architecture**. Unlike standard LLM implementations, this agent treats the SQL generation and execution as a dynamic loop.


### The Agentic Loop:
1.  **Semantic Parsing:** Natural language queries are processed by the Gemini 2.5-Flash LLM.
2.  **Safety Validation:** The generated SQL undergoes static analysis via the `is_query_safe` module to detect and block malicious patterns (DML/DDL operations).
3.  **Execution:** Validated SQL is executed against the PostgreSQL database.
4.  **Self-Healing (Runtime Correction):** If a runtime error occurs (e.g., table/column mismatch), the database error is fed back to the LLM as a "correction hint," allowing the agent to regenerate the query autonomously.

## Security Guardrails
Security is handled at the **application layer**. Before any query is executed, the agent validates the string against an explicit blacklist:
* **Permitted:** `SELECT` statements (Read-only).
* **Blocked:** `DELETE`, `DROP`, `TRUNCATE`, `ALTER`, `INSERT`, `UPDATE`, `EXEC`, `UNION`.
* **Constraint:** This ensures the agent acts in a "Read-Only" capacity, significantly reducing injection and data-loss risks.

## Evaluation & Performance
The system was benchmarked against a standardized test set to ensure accuracy and latency constraints were met.

| Question | Generated SQL | Latency | Final Status |
| :--- | :--- | :--- | :--- |
| List all products | `SELECT * FROM products;` | 1.99s | Success |
| How many customers are in USA? | `SELECT COUNT(...)` | 2.56s | Success |
| Show orders from Germany | `SELECT T1.* FROM orders...` | 2.38s | Success |

*Note: The system includes a custom `send_query_with_retry` mechanism with exponential backoff to ensure compliance with API rate limits and stability.*

## Tech Stack
* **LLM Engine:** Google Gemini 2.5 Flash
* **Backend:** FastAPI (Async Endpoints)
* **Database:** PostgreSQL (with `psycopg2` driver)
* **Orchestration:** Pydantic (for Structured Schema Validation)
* **Containerization:** Docker

##  Deployment Guide

### 1. Environment Setup
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_key_here
DB_NAME=postgres
DB_USER=admin
DB_PASSWORD=secret
DB_HOST=localhost

### 2. Dependency Installation
Install the required Python packages:
**pip install -r requirements.txt**

### 3. Launching the Agent
- Start the API Server 
**uvicorn main:app --reload**

- Run the evaluation
**python evaluate.py**



