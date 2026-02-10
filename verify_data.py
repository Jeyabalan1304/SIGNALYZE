import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load database credentials
base_path = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(base_path, "backend", ".env")
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

def verify_data():
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found in backend/.env")
        return

    engine = create_engine(DATABASE_URL)
    
    queries = [
        ("Raw Feedback Count", "SELECT COUNT(*) FROM raw_feedback"),
        ("Preprocessed Feedback Count", "SELECT COUNT(*) FROM preprocessed_feedback"),
        ("Classified Insights Count", "SELECT COUNT(*) FROM classified_insights"),
        ("Latest 5 Classified Items", "SELECT model, disposition_5, created_at FROM classified_insights ORDER BY created_at DESC LIMIT 5")
    ]

    print(f"{'='*50}")
    print(f"SIGNALYZE DATABASE VERIFICATION")
    print(f"{'='*50}")

    with engine.connect() as conn:
        for title, sql in queries:
            print(f"\n>>> {title}:")
            try:
                result = conn.execute(text(sql))
                if "Latest" in title:
                    rows = result.fetchall()
                    if not rows:
                        print("    (No records found yet)")
                    for row in rows:
                        print(f"    - Model: {row[0]} | Sentiment: {row[1]} | Date: {row[2]}")
                else:
                    count = result.scalar()
                    print(f"    Count: {count}")
            except Exception as e:
                print(f"    Error running query: {e}")
    
    print(f"\n{'='*50}")
    print("TIP: You can also visit http://localhost:8000/classified-feedback in your browser.")
    print(f"{'='*50}")

if __name__ == "__main__":
    verify_data()
