from database import get_db_connection
from psycopg2.extras import RealDictCursor
from validator import self_correct_sql 

'''
we add the new function to make sure we dont face the sql injection
'''
def is_query_safe(sql_string: str) -> bool:
    """Returns False if any destructive SQL keywords are detected."""
    forbidden_keywords = ["delete", "drop", "update", "insert", "truncate", "alter"]
    cleaned_sql = sql_string.lower().strip()
    
    # 1. Ensure it starts with SELECT
    if not cleaned_sql.startswith("select"):
        return False
        
    # 2. Guard against chained destructive statements (e.g., SELECT...; DROP TABLE...)
    for keyword in forbidden_keywords:
        if keyword in cleaned_sql:
            return False
            
    return True

def execute_agent_pipeline(question: str, structured_data):
    """Executes the query, running a self-correction loop if a database exception occurs."""
    sql = structured_data.generated_sql
    retry_needed = "No"
    
    # security check here to make sure we dont run any destructive queries
    if not is_query_safe(sql):
        return {
            "decomposition": structured_data.model_dump(), 
            "sql": sql, 
            "success": False, 
            "retry_needed": "No", 
            "data": [],
            "error": "Security Violation: Only SELECT queries are permitted. Destructive operations are blocked."
        }
    
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
        # Initial attempt failed, trigger the Self-Correction Loop!
        retry_needed = "Yes"
        error_msg = str(e)
        
        try:
            # Call validator file to fix the broken logic string
            corrected_data = self_correct_sql(question, sql, error_msg)
            new_sql = corrected_data.generated_sql
            
            # Retry running the updated statement
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(new_sql)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            return {
                "decomposition": corrected_data.model_dump(), 
                "sql": new_sql, 
                "success": True, 
                "retry_needed": retry_needed, 
                "data": [dict(row) for row in results]
            }
        except Exception as retry_error:
            return {
                "decomposition": structured_data.model_dump(), 
                "sql": sql, 
                "success": False, 
                "retry_needed": retry_needed, 
                "data": [], 
                "error": str(retry_error)
            }