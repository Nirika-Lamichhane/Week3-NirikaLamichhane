import logging
import os
import time
from fastapi import FastAPI
from sql_generator import generate_structured_sql, generate_summary
from executor import execute_agent_pipeline

# Configure Logger
LOG_FILE_PATH = os.path.join("logs", "app.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE_PATH), logging.StreamHandler()]
)

app = FastAPI(title="Agentic Text-to-SQL System - Task 4")

@app.post("/agent/sql")
def process_agent_query(payload: dict):
    question = payload.get("question")
    if not question:
        return {"error": "No question provided"}

    start_time = time.time()
    logging.info(f"Incoming User Query: '{question}'")

    # Step 1 & 2: Decomposition
    decomposition_result = generate_structured_sql(question)
    logging.info(f"Decomposition: {decomposition_result.model_dump()}")
    
    # Step 3 & 4: Execute with Self-Correction Loop
    final_output = execute_agent_pipeline(question, decomposition_result)
    
    # Step 5: Final Output & Summary Generation
    execution_time = time.time() - start_time
    logging.info(f"Execution took {execution_time:.2f} seconds")
    
    summary = "I'm sorry, I couldn't retrieve the answer for this query."
    if final_output.get("success"):
        summary = generate_summary(question, final_output.get("data"))
    
    return {
        "sql": final_output.get("sql"),
        "result": final_output.get("data", []),
        "summary": summary,
        "status": "success" if final_output.get("success") else "failed"
    }