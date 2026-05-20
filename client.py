import requests
import json

# The backend API gateway URL
URL = "http://127.0.0.1:8000/query"

def interactive_agent_chat():
    print("====================================================")
    print("   🤖 AI TEXT-TO-SQL AGENT INTERACTIVE CONSOLE 🤖   ")
    print("====================================================")
    print("Type your database question below (or type 'exit' to quit).\n")
    
    while True:
        # 1. Capture the input question dynamically from the user
        user_question = input("User 👤: ")
        
        # Check if the user wants to break out of the loop
        if user_question.lower().strip() == 'exit':
            print("\nGoodbye! Happy data analyzing! 👋")
            break
            
        if not user_question.strip():
            print("Please type a valid question.")
            continue
            
        try:
            # 2. Package the question into a JSON dictionary payload and send it
            payload = {"question": user_question}
            response = requests.post(URL, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                # 3. Extract and display the structural data results nicely
                print(f"\n🤖 AI Agent Intent Identification: {result['decomposition']['intent']}")
                print(f"💻 Generated SQL Query Line: {result['sql']}")
                print(f"🔄 Self-Correction Recovery Loop Triggered? {result['retry_needed']}")
                
                print("\n📊 Retrieved Warehouse Data Results:")
                data_rows = result.get("data", [])
                
                if not data_rows:
                    print("   [Empty Data Array Return - No matches found in database]")
                else:
                    # Print out just the first 3 rows cleanly so it doesn't flood the terminal screen
                    for row in data_rows[:3]:
                        print(f"   {row}")
                    if len(data_rows) > 3:
                        print(f"   ... and {len(data_rows) - 3} more matching records.")
                print("-" * 52 + "\n")
                
            else:
                print(f"❌ Server Error code: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Failed to reach the FastAPI server: {e}")

if __name__ == "__main__":
    interactive_agent_chat()