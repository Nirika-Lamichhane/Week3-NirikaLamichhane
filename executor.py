from database import get_db_connection
from psycopg2.extras import RealDictCursor
from validator import self_correct_sql
import logging

def is_query_safe(sql_string: str) -> bool:
    """Returns False if any destructive SQL keywords are detected."""
    forbidden_keywords = ["delete", "drop", "update", "insert", "truncate", "alter"]
    cleaned_sql = sql_string.lower().strip()
    
    # 1. Ensure it starts with SELECT
    # Handles cases where LLM might add parentheses
    if not cleaned_sql.lstrip('(').startswith("select"):
        return False
        
    # 2. Guard against chained destructive statements
    # Split by spaces to check whole words only (prevents blocking 'user_updates')
    words = cleaned_sql.split()
    for word in words:
        clean_word = word.strip("(),;")
        if clean_word in forbidden_keywords:
            return False
            
    return True

def execute_agent_pipeline(question: str, structured_data):
    """
    Executes the query, running a self-correction loop (max 3 attempts) 
    if a database exception occurs.
    """
    sql = structured_data.generated_sql
    retry_needed = "No"
    
    # SECURITY CHECK (Non-negotiable requirement)
    if not is_query_safe(sql):
        logging.error(f"Security blocked unsafe query: {sql}")
        return {
            "decomposition": structured_data.model_dump(), 
            "sql": sql, 
            "success": False, 
            "retry_needed": "No", 
            "data": [],
            "error": "Security Violation: Only SELECT queries are permitted."
        }
    
    # RETRY LOOP: 3 Attempts Total (1 initial + 2 retries)
    for attempt in range(3):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return {
                "decomposition": structured_data.model_dump(), 
                "sql": sql, 
                "success": True, 
                "retry_needed": retry_needed, 
                "data": [dict(row) for row in results]
            }
            
        except Exception as e:
            retry_needed = "Yes"
            logging.warning(f"Attempt {attempt + 1} failed: {e}")
            
            # If we have attempts left, try to fix the SQL
            if attempt < 2:
                try:
                    # Ask the LLM to fix the logic based on the error
                    corrected_data = self_correct_sql(question, sql, str(e))
                    sql = corrected_data.generated_sql
                    structured_data = corrected_data
                    
                    # Security re-check on the new SQL
                    if not is_query_safe(sql):
                        return {
                            "decomposition": structured_data.model_dump(),
                            "sql": sql,
                            "success": False,
                            "error": "Security Violation in fixed query.",
                            "data": []
                        }
                except Exception as fix_error:
                    return {
                        "decomposition": structured_data.model_dump(),
                        "sql": sql,
                        "success": False,
                        "error": f"Correction process failed: {str(fix_error)}",
                        "data": []
                    }
            else:
                # If we exhausted 3 attempts
                return {
                    "decomposition": structured_data.model_dump(),
                    "sql": sql,
                    "success": False,
                    "retry_needed": retry_needed,
                    "data": [],
                    "error": f"Max retries reached. Final error: {str(e)}"
                }