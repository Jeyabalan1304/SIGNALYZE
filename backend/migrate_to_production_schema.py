import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from models import Feedback, RawFeedback, Base

load_dotenv("backend/.env")
db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

def migrate_raw_to_production():
    # Ensure tables match models by dropping existing production tables if they have schema mismatches
    print("Dropping production tables to ensure schema alignment...")
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS classification_results CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS feedback CASCADE;"))
        conn.commit()
    
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    # Check if feedback already has data
    count = session.query(Feedback).count()
    if count > 0:
        print(f"Feedback table already has {count} records skipping migration.")
        return

    print("Migrating records from raw_feedback to feedback table...")
    raw_records = session.query(RawFeedback).all()
    
    new_records = []
    for r in raw_records:
        # Extract company and product from source_metadata if available
        meta = r.source_metadata or {}
        company = meta.get("company", "Unknown")
        product = meta.get("product", "Unknown")
        
        new_records.append(Feedback(
            text=r.raw_text,
            source=r.source,
            company_name=company,
            product=product,
            created_at=r.created_at
        ))
        
        if len(new_records) >= 100:
            session.bulk_save_objects(new_records)
            session.commit()
            new_records = []
            print(f"Migrated batch...")

    if new_records:
        session.bulk_save_objects(new_records)
        session.commit()
    
    print(f"Successfully migrated {len(raw_records)} records.")

if __name__ == "__main__":
    migrate_raw_to_production()
