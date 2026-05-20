import requests
import time
import json

# The endpoint of your live FastAPI server
URL = "http://127.0.0.1:8000/query"

# 1. DEFINE YOUR BENCHMARK DATASET HERE
# Add the exact questions provided in your assignment document
BENCHMARK_QUESTIONS = [
    "List all products",
    "How many customers are located in the USA?",
    "Show orders shipped from Germany",
    # Add the rest of your assignment's test questions here...
]

def send_query_with_retry(question, retries=3):
    """Sends a request to the server, with exponential backoff for 429 errors."""
    for i in range(retries):
        response = requests.post(URL, json={"question": question})
        if response.status_code == 200:
            return response
        elif response.status_code == 429:
            wait = (i + 1) * 15  # Wait 15, 30, 45 seconds
            print(f"[!] Rate limited. Waiting {wait} seconds...")
            time.sleep(wait)
        else:
            return response # If it's a 500 or 400 error, return immediately
    return response

def run_evaluation():
    print(f"| {'Question':<35} | {'Generated SQL':<30} | {'Executed Successfully':<21} | {'Retry Needed':<12} | {'Latency':<7} | {'Final Status':<8} |")
    print(f"|{'-'*37}|{'-'*32}|{'-'*23}|{'-'*14}|{'-'*9}|{'-'*10}|")
    
    logs = []
    
    for q in BENCHMARK_QUESTIONS:
        start_time = time.time()

        response = send_query_with_retry(q)

        try:
            latency = round(time.time() - start_time, 3)
            
            if response.status_code == 200:
                res_data = response.json()
                decomposition = res_data.get("decomposition", {})
                sql = res_data.get("sql", "N/A")
                success = "Yes" if res_data.get("success") else "No"
                retry = res_data.get("retry_needed", "No")
                status = "Success" if res_data.get("success") else "Failed"
                
                # Truncate SQL slightly just for a clean console log layout
                short_sql = sql if len(sql) < 30 else sql[:27] + "..."
                
                print(f"| {q:<35} | {short_sql:<30} | {success:<21} | {retry:<12} | {latency:<7}s | {status:<8} |")
                
                # Save data for formal file logs
                logs.append({
                    "question": q,
                    "generated_sql": sql,
                    "executed_successfully": success,
                    "retry_needed": retry,
                    "latency_seconds": latency,
                    "final_status": status,
                    "returned_data_sample": res_data.get("data", [])[:2] # safe snippet
                })
            else:
                print(f"| {q:<35} | {'HTTP Error':<30} | {'No':<21} | {'No':<12} | {latency:<7}s | {'Failed':<8} |")
        except Exception as e:
            print(f"| {q:<35} | {'Server Connection Error':<30} | {'No':<21} | {'No':<12} | {'0.00':<7}s | {'Failed':<8} |")

    # Save the deep comprehensive query execution logs package
    with open("query_execution_logs.json", "w") as f:
        json.dump(logs, f, indent=2)
    print("\n[INFO] Complete comprehensive log data saved cleanly to query_execution_logs.json")

if __name__ == "__main__":
    run_evaluation()