from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import RawFeedback, ClassifiedInsight, PreprocessedFeedback

router = APIRouter(tags=["Classification"])

@router.get("/analytics/summary")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total = db.query(RawFeedback).count()
    classified = db.query(ClassifiedInsight).count()
    pending = total - classified
    signal_pct = int((classified / total * 100)) if total > 0 else 0
    
    return {
        "total_feedback": total,
        "classified_signal": signal_pct,
        "pending_processing": pending
    }

@router.get("/analytics/charts")
def get_dashboard_charts(db: Session = Depends(get_db)):
    # Sentiment
    sentiment_data = db.query(
        ClassifiedInsight.sentiment, func.count(ClassifiedInsight.id)
    ).group_by(ClassifiedInsight.sentiment).all()
    
    sentiment_list = [
        {"name": s[0] if s[0] else "Neutral", "value": s[1]} 
        for s in sentiment_data
    ]
    
    # Area (Product Category)
    area_data = db.query(
        ClassifiedInsight.product_category, func.count(ClassifiedInsight.id)
    ).group_by(ClassifiedInsight.product_category).all()
    
    area_list = [
        {"name": a[0] if a[0] else "Other", "value": a[1]}
        for a in area_data
    ]
    
    return {
        "sentiment": sentiment_list,
        "area": area_list
    }

@router.get("/classified-feedback")
def get_verified_data(limit: int = 50, db: Session = Depends(get_db)):
    """
    Returns joined data for the Verification View table.
    """
    query = db.query(
        ClassifiedInsight, 
        RawFeedback.raw_text.label("raw_text"),
        RawFeedback.source.label("source")
    ).select_from(ClassifiedInsight)\
     .join(PreprocessedFeedback, ClassifiedInsight.preprocessed_id == PreprocessedFeedback.id)\
     .join(RawFeedback, PreprocessedFeedback.raw_id == RawFeedback.id)\
     .order_by(ClassifiedInsight.created_at.desc())\
     .limit(limit).all()
    
    results = []
    for row in query:
        res_obj = row.ClassifiedInsight
        data = {column.name: getattr(res_obj, column.name) for column in res_obj.__table__.columns}
        data["raw_text"] = row.raw_text
        data["source"] = row.source
        results.append(data)
    return results

@router.get("/insights/summary")
def get_insights_summary(db: Session = Depends(get_db)):
    """
    Group by: disposition_1, product_category, model, sentiment
    """
    disp_summary = db.query(
        ClassifiedInsight.disposition_1, 
        func.count(ClassifiedInsight.id)
    ).group_by(ClassifiedInsight.disposition_1).all()

    category_summary = db.query(
        ClassifiedInsight.product_category, 
        func.count(ClassifiedInsight.id)
    ).group_by(ClassifiedInsight.product_category).all()

    model_summary = db.query(
        ClassifiedInsight.model, 
        func.count(ClassifiedInsight.id)
    ).group_by(ClassifiedInsight.model).all()

    sentiment_summary = db.query(
        ClassifiedInsight.sentiment, 
        func.count(ClassifiedInsight.id)
    ).group_by(ClassifiedInsight.sentiment).all()

    return {
        "disposition_distribution": dict(disp_summary),
        "category_distribution": dict(category_summary),
        "model_distribution": dict(model_summary),
        "sentiment_distribution": dict(sentiment_summary)
    }

@router.get("/insights/company/{company_name}")
def get_company_insights(company_name: str, db: Session = Depends(get_db)):
    """
    Returns classified data filtered by company name joining with RawFeedback table.
    """
    # Note: company_name logic depends on how you store it in JSON source_metadata
    results = db.query(ClassifiedInsight)\
        .join(PreprocessedFeedback, ClassifiedInsight.preprocessed_id == PreprocessedFeedback.id)\
        .join(RawFeedback, PreprocessedFeedback.raw_id == RawFeedback.id)\
        .all() 
    return results
