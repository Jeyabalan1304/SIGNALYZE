import sqlalchemy
from sqlalchemy import create_engine, text

# Check SQLite
db_url = "sqlite:///c:/Users/jeyab/Desktop/prasath/backend/signalyze.db"
print(f"Connecting to Local SQLite")

try:
    engine = create_engine(db_url)
    with engine.connect() as conn:
        for table in ["raw_feedback", "preprocessed_feedback", "classified_insights"]:
            try:
                res = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = res.scalar()
                print(f"{table}: {count}")
            except Exception as e:
                print(f"{table}: Not found")
except Exception as e:
    print(f"Error: {e}")
