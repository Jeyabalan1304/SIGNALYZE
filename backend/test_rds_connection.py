import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn_string = os.getenv("DATABASE_URL")
print(f"Testing connection to: {conn_string.split('@')[1] if conn_string else 'None'}")

try:
    conn = psycopg2.connect(conn_string, connect_timeout=5)
    print("SUCCESS: Connected to RDS!")
    conn.close()
except Exception as e:
    print(f"FAILED: {e}")
