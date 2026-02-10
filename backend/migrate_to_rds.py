import sqlite3
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

RDS_URL = os.getenv("DATABASE_URL")
SQLITE_PATH = "signalyze.db"

def migrate():
    if not os.path.exists(SQLITE_PATH):
        print("SQLite file not found.")
        return

    print(f"Connecting to RDS: {RDS_URL.split('@')[1]}")
    rds_engine = create_engine(RDS_URL)
    
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    cursor = sqlite_conn.cursor()

    tables = ['raw_feedback', 'preprocessed_feedback', 'classified_insights']
    
    for table in tables:
        print(f"Migrating {table}...")
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        
        if not rows:
            print(f"No data in {table}, skipping.")
            continue

        # Get column names
        cols = rows[0].keys()
        col_str = ", ".join(cols)
        placeholder_str = ", ".join([f":{col}" for col in cols])
        
        insert_query = text(f"INSERT INTO {table} ({col_str}) VALUES ({placeholder_str}) ON CONFLICT DO NOTHING")
        
        with rds_engine.begin() as rds_conn:
            count = 0
            for row in rows:
                rds_conn.execute(insert_query, dict(row))
                count += 1
            print(f"Successfully migrated {count} rows to {table}")

    sqlite_conn.close()
    print("Migration complete!")

if __name__ == "__main__":
    migrate()
