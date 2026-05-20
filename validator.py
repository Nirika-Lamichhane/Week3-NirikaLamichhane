from openai import OpenAI
import os
from prompts.templates import SCHEMA_CONTEXT
from sql_generator import QueryDecomposition
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("OPENAI_API_KEY")
)
def self_correct_sql(question: str, failed_sql: str, error_message: str):
    """Feeds a database error traceback back to the LLM to patch structural column or query issues."""
    completion = client.beta.chat.completions.parse(
        model="gemini-2.5-flash",
        messages=[
            {"role": "system", "content": SCHEMA_CONTEXT},
            {"role": "user", "content": f"Deconstruct and generate SQL for: {question}"},
            {"role": "assistant", "content": f"Generated SQL: {failed_sql}"},
            {"role": "user", "content": f"Execution failed with database error: {error_message}. Please check your column mappings, apply double quotes where needed, and return a fixed SQL query object."}
        ],
        response_format=QueryDecomposition,
    )
    return completion.choices[0].message.parsed