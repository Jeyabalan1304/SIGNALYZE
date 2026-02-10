
import os
import sys
from sqlalchemy import func

# Add backend directory to path to import models and database
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from database import SessionLocal
from models import ClassifiedInsight

def cleanup_duplicates():
    session = SessionLocal()
    try:
        # 1. Find preprocessed_ids that have duplicates
        # We use a subquery or just group by and count
        duplicate_ids_query = (
            session.query(ClassifiedInsight.preprocessed_id)
            .group_by(ClassifiedInsight.preprocessed_id)
            .having(func.count(ClassifiedInsight.id) > 1)
        )
        
        duplicate_p_ids = [r[0] for r in duplicate_ids_query.all()]
        
        if not duplicate_p_ids:
            print("No duplicates found.")
            return 0
            
        total_removed = 0
        
        for p_id in duplicate_p_ids:
            # 2. Get all records for this preprocessed_id, ordered by created_at
            records = (
                session.query(ClassifiedInsight)
                .filter(ClassifiedInsight.preprocessed_id == p_id)
                .order_by(ClassifiedInsight.created_at.asc())
                .all()
            )
            
            # Keep the first one (earliest), delete the rest
            # If they have the exact same created_at, SQLAlchemy will still pick them in some order.
            to_delete = records[1:]
            for record in to_delete:
                session.delete(record)
                total_removed += 1
        
        session.commit()
        print(f"Successfully removed {total_removed} duplicate records.")
        return total_removed
    except Exception as e:
        session.rollback()
        print(f"Error during cleanup: {e}")
        raise e
    finally:
        session.close()

if __name__ == "__main__":
    count = cleanup_duplicates()
    print(f"TOTAL_REMOVED:{count}")
