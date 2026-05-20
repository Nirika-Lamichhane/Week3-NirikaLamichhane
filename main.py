from fastapi import FastAPI
import logging
import os
from sql_generator import generate_structured_sql
from executor import execute_agent_pipeline

# 1. CONFIGURE THE LOGGER TO WRITE TO THE LOGS FOLDER
LOG_FILE_PATH = os.path.join("logs", "app.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH), # Writes logs to your logs/app.log file
        logging.StreamHandler()            # Still prints logs to your terminal window
    ]
)

app = FastAPI(title="Agentic Text-to-SQL System - Task 3")

@app.post("/query")
def process_user_query(payload: dict):
    question = payload.get("question")
    if not question:
        logging.warning("Received a request with an empty payload.")
        return {"error": "No question payload provided"}
        
    logging.info(f"Incoming User Query: '{question}'")
    
    # Step 1 & 2: Structured Decomposition & Planning Generation
    decomposition_result = generate_structured_sql(question)
    logging.info(f"Generated SQL Intent: {decomposition_result.intent}")
    logging.info(f"Initial Proposed SQL: {decomposition_result.generated_sql}")
    
    # Step 3 & 4: Execution Engine with Validator Handshake Routing
    final_output = execute_agent_pipeline(question, decomposition_result)
    
    if not final_output.get("success"):
        logging.error(f"Execution failed: {final_output.get('error', 'Unknown Error')}")
    
    # map the sucess boolean value to a clear text status string
    status_string = "Success" if final_output.get("success") else "Failed"

    if final_output.get("success"):
        logging.info(f"Query executed successfully. Self-correction needed: {final_output.get('retry_needed')}")
    else:
        logging.error(f"Query execution completely failed. Error: {final_output.get('error')}")
        
    return {
        "question": question,                           # Pulled from payload
        "sql": final_output.get("sql"),                 # Extracted from executor return
        "result": final_output.get("data", []),         # Renamed 'data' to 'result'
        "status": status_string                         # Map boolean to text value
    }

'''
here return is structured like this cause our requirement is to show the output like this.

'''