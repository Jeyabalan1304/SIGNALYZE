import asyncio
import os
import sys
from sqlalchemy.orm import Session
from dotenv import load_dotenv

backend_path = 'c:/Users/jeyab/Desktop/prasath/backend'
if backend_path not in sys.path:
    sys.path.append(backend_path)

load_dotenv(os.path.join(backend_path, '.env'))

import models
from database import SessionLocal
from pipelines.classification import classify_preprocessed_item

async def worker():
    db = SessionLocal()
    try:
        print("WORKER: Starting classification worker...")
        while True:
            # Find preprocessed items that don't have an insight yet
            pre_pending = db.query(models.PreprocessedFeedback).outerjoin(models.ClassifiedInsight).filter(models.ClassifiedInsight.id == None).limit(10).all()
            
            if not pre_pending:
                print("WORKER: No more items to classify. Sleeping 30s...")
                await asyncio.sleep(30)
                continue

            print(f"WORKER: Classifying {len(pre_pending)} items...")
            for pre in pre_pending:
                try:
                    await classify_preprocessed_item(db, pre.id)
                    print(f"WORKER: Classified {pre.id[:8]}")
                except Exception as e:
                    print(f"WORKER: Error {pre.id[:8]}: {e}")
            
            # Rate limit/Sleep
            await asyncio.sleep(1)
            
    except Exception as e:
        print(f"WORKER FATAL: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(worker())
