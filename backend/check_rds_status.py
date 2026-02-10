from database import SessionLocal
import models
from sqlalchemy import text

def check_rds():
    db = SessionLocal()
    try:
        # Check tables
        result = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        tables = [row[0] for row in result]
        print(f"Tables in RDS: {tables}")
        
        raw_count = db.query(models.RawFeedback).count()
        processed_count = db.query(models.PreprocessedFeedback).count()
        classified_count = db.query(models.ClassifiedInsight).count()
        
        print(f"Raw Items: {raw_count}")
        print(f"Processed Items: {processed_count}")
        print(f"Classified Items: {classified_count}")
    except Exception as e:
        print(f"Error checking RDS: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_rds()
