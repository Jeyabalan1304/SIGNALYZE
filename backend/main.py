from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Depends
from sqlalchemy.orm import Session
import pandas as pd
import io
import os
import asyncio
from contextlib import asynccontextmanager
from dotenv import load_dotenv

import models
from database import engine, get_db, SessionLocal
from pipelines.ingestion import ingest_raw_data
from pipelines.preprocessing import process_raw_item
from pipelines.classification import classify_preprocessed_item
from classification_service import run_classification_pipeline
from routers import classification_router

load_dotenv()

from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Run classification in the background
    asyncio.create_task(run_full_pipeline())
    yield

app = FastAPI(title="Signalyze API - Production Ready", lifespan=lifespan)

app.include_router(classification_router.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def run_full_pipeline():
    """
    Background worker that moves data through the 3 layers.
    RAW -> CLEANED -> CLASSIFIED
    """
    db = SessionLocal()
    try:
        print("PIPELINE: Starting background worker...")
        while True:
            # 1. RAW -> PREPROCESSED
            raw_unprocessed = db.query(models.RawFeedback).outerjoin(models.PreprocessedFeedback).filter(models.PreprocessedFeedback.id == None).limit(50).all()
            for raw in raw_unprocessed:
                try:
                    await process_raw_item(db, raw.id)
                    db.commit()
                except Exception as e:
                    print(f"PIPELINE: Preprocessing error for {raw.id}: {e}")
                    db.rollback()

            # 2. PREPROCESSED -> CLASSIFIED
            # This handles the OpenAI batching (Parallel 20)
            new_count = await run_classification_pipeline(db, batch_size=20)
            
            if new_count > 0:
                print(f"PIPELINE: Success! Classified {new_count} records.")
                await asyncio.sleep(1) 
            elif len(raw_unprocessed) > 0:
                print(f"PIPELINE: Preprocessed {len(raw_unprocessed)} items. Continuing...")
                await asyncio.sleep(1)
            else:
                await asyncio.sleep(10) 
            
    except Exception as e:
        print(f"PIPELINE FATAL ERROR: {e}")
    finally:
        db.close()

@app.post("/classify")
async def classify_single(data: dict, db: Session = Depends(get_db)):
    text = data.get("text")
    source = data.get("source", "manual")
    if not text:
        return {"error": "Text is required"}
    
    # 1. Ingest Raw
    raw = await ingest_raw_data(db, text, source=source)
    
    # 2. Preprocess
    pre = await process_raw_item(db, raw.id)
    if not pre:
        return {"error": "Preprocessing failed"}
    
    # 3. Classify
    insight = await classify_preprocessed_item(db, pre.id)
    
    if insight:
        return {
            "id": insight.id,
            "sentiment": insight.sentiment,
            "dispositions": [insight.disposition_1, insight.disposition_2, insight.disposition_3, insight.disposition_4, insight.disposition_5],
            "product_info": {
                "make": insight.make_brand,
                "model": insight.model,
                "category": insight.product_category
            },
            "annotator_note": "AI Primary Classification"
        }
    
    return {"error": "AI classification failed"}

@app.post("/analytics/process")
async def trigger_processing():
    # Loop is already running from lifespan, no need to start another one
    return {"message": "Background worker is already active and monitoring for new data."}

@app.get("/")
async def root():
    return {"message": "Signalyze API - Production Ready"}

from scrapers.reddit_scraper import fetch_reddit_comments
from scrapers.youtube_scraper import fetch_youtube_comments

@app.post("/ingest/reddit")
async def ingest_reddit(subreddit: str, db: Session = Depends(get_db)):
    comments = fetch_reddit_comments(subreddit)
    for text in comments:
        await ingest_raw_data(db, text, source='reddit', metadata={"subreddit": subreddit})
    return {"source": "reddit", "records_added": len(comments)}

@app.post("/ingest/youtube")
async def ingest_youtube(video_id: str, db: Session = Depends(get_db)):
    comments = fetch_youtube_comments(video_id)
    for text in comments:
        await ingest_raw_data(db, text, source='youtube', metadata={"video_id": video_id})
    return {"source": "youtube", "records_added": len(comments)}

@app.post("/ingest/csv")
@app.post("/upload-csv")
async def ingest_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        
        records_added = 0
        # Common column names for feedback
        possible_cols = ['text', 'comment', 'review', 'body', 'content', 'feedback']
        
        # Find which column matches
        text_col = next((col for col in possible_cols if col in df.columns), None)
        
        if not text_col:
             # Fallback: Use the first column if no known name matches
             text_col = df.columns[0]

        for _, row in df.iterrows():
            text = str(row.get(text_col, ''))
            if not text or text.lower() == 'nan': continue
            
            await ingest_raw_data(db, text, source='csv', metadata={"filename": file.filename})
            records_added += 1
        
        return {"filename": file.filename, "records_added": records_added}
    except Exception as e:
        return {"error": str(e)}

@app.get("/analytics/summary")
async def get_summary(db: Session = Depends(get_db)):
    total_raw = db.query(models.RawFeedback).count()
    total_classified = db.query(models.ClassifiedInsight).count()
    return {
        "total_feedback": total_raw,
        "classified_signal": round((total_classified / total_raw * 100), 2) if total_raw > 0 else 0,
        "pending_processing": total_raw - total_classified
    }

@app.get("/analytics/charts")
async def get_charts(db: Session = Depends(get_db)):
    from sqlalchemy import func
    # Using the new sentiment column for primary indicators
    sentiment_data = db.query(models.ClassifiedInsight.sentiment, func.count(models.ClassifiedInsight.id)).group_by(models.ClassifiedInsight.sentiment).all()
    category_data = db.query(models.ClassifiedInsight.product_category, func.count(models.ClassifiedInsight.id)).group_by(models.ClassifiedInsight.product_category).all()
    
    return {
        "sentiment": [{"name": s or "Unknown", "value": c} for s, c in sentiment_data],
        "area": [{"name": cat or "Unknown", "value": c} for cat, c in category_data]
    }

@app.get("/feedback")
@app.get("/classified-feedback")
async def get_feedback(db: Session = Depends(get_db), limit: int = 50):
    insights = db.query(models.ClassifiedInsight).order_by(models.ClassifiedInsight.created_at.desc()).limit(limit).all()
    # Return with all fields mapped for frontend
    return [{
        "id": i.id,
        "source": i.preprocessed.raw.source if i.preprocessed and i.preprocessed.raw else "unknown",
        "raw_text": i.preprocessed.cleaned_text if i.preprocessed else "N/A",
        
        # Detailed Taxonomy
        "item_id": i.item_id,
        "item_type": i.item_type,
        "product_category": i.product_category,
        "product_subcategory": i.product_subcategory,
        "make_brand": i.make_brand,
        "model": i.model,
        "variant": i.variant,
        "color": i.color,
        "size_capacity": i.size_capacity,
        "configuration": i.configuration,
        "release_year": i.release_year,
        "price_band": i.price_band,
        "market_segment": i.market_segment,
        "verified_purchase": i.verified_purchase,
        "purchase_channel": i.purchase_channel,
        "purchase_region": i.purchase_region,
        "usage_duration_bucket": i.usage_duration_bucket,
        "ownership_stage": i.ownership_stage,
        
        # Signalyze Output
        "sentiment": i.sentiment or i.disposition_5, # Fallback to disp5 if sentiment is null for old records
        "disposition_1": i.disposition_1,
        "disposition_2": i.disposition_2,
        "disposition_3": i.disposition_3,
        "disposition_4": i.disposition_4,
        "disposition_5": i.disposition_5,
        
        # Backward compatibility for existing UI components
        "area": i.product_category,
        "product_info": {
            "make": i.make_brand,
            "model": i.model,
            "category": i.product_category
        },
        "annotator_note": i.disposition_4,
        "created_at": i.created_at
    } for i in insights]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
