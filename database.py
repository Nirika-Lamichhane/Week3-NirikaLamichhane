import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Creates and returns a connection to the PostgreSQL database."""
    return psycopg2.connect(os.getenv("DATABASE_URL"))