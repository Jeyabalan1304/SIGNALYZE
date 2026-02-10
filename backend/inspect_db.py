
import os
import sys
from sqlalchemy import func

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from database import SessionLocal
from models import ClassifiedInsight, PreprocessedFeedback

def inspect_db():
    session = SessionLocal()
    try:
        total_insights = session.query(ClassifiedInsight).count()
        print(f"Total Classified Insights: {total_insights}")
        
        counts = (
            session.query(ClassifiedInsight.preprocessed_id, func.count(ClassifiedInsight.id))
            .group_by(ClassifiedInsight.preprocessed_id)
            .all()
        )
        
        p_ids_with_counts = [r for r in counts if r[1] > 1]
        print(f"Preprocessed IDs with duplicates: {p_ids_with_counts}")
        
        # Also check PreprocessedFeedback just in case
        total_preprocessed = session.query(PreprocessedFeedback).count()
        print(f"Total Preprocessed Feedback: {total_preprocessed}")

    finally:
        session.close()

if __name__ == "__main__":
    inspect_db()
