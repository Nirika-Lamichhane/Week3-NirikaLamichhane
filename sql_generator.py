from openai import OpenAI
from pydantic import BaseModel
from typing import List, Optional
import os
from prompts.templates import SCHEMA_CONTEXT
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("OPENAI_API_KEY")
)

class QueryDecomposition(BaseModel):
    intent: str
    tables: List[str]
    columns: List[str]
    filters: Optional[str] = "None"
    joins: Optional[str] = "None"
    generated_sql: str

def generate_structured_sql(question: str):
    """Calls OpenAI to decompose the text and generate an initial SQL query matching Task 2 parameters."""
    completion = client.beta.chat.completions.parse(
        model="gemini-2.5-flash",
        messages=[
            {"role": "system", "content": SCHEMA_CONTEXT},
            {"role": "user", "content": f"Deconstruct and generate SQL for: {question}"}
        ],
        response_format=QueryDecomposition,
    )
    return completion.choices[0].message.parsed

'''
our response format in the pydantic includes the intents and all along with the generated string sql as well
so when we call this generate function, it returns the sql decomposition as well as the sql queries

'''
