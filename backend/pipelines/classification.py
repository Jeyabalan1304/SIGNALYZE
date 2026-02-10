from sqlalchemy.orm import Session
import models
from openai_service import analyze_feedback as classify_feedback

def clean_val(val):
    if val is None: return None
    if isinstance(val, str) and val.lower() in ["null", "n/a", "unknown", "none"]:
        return None
    return val

async def classify_preprocessed_item(db: Session, preprocessed_id: str):
    item = db.query(models.PreprocessedFeedback).filter(models.PreprocessedFeedback.id == preprocessed_id).first()
    if not item: return None

    # De-duplication check: Don't classify if already classified
    existing = db.query(models.ClassifiedInsight).filter(models.ClassifiedInsight.preprocessed_id == preprocessed_id).first()
    if existing: 
        print(f"PIPELINE: Item {preprocessed_id} already classified. Skipping.")
        return existing

    # Use translated text if available, else cleaned text
    text_to_classify = item.translated_text if item.is_translated else item.cleaned_text
    
    # AI Classification
    result = await classify_feedback(text_to_classify)
    if not result: return None

    # Map to Schema with NULL handling
    insight = models.ClassifiedInsight(
        preprocessed_id=preprocessed_id,
        item_id=clean_val(result.get("item_id")),
        item_type=clean_val(result.get("item_type")),
        product_category=clean_val(result.get("product_category")),
        product_subcategory=clean_val(result.get("product_subcategory")),
        make_brand=clean_val(result.get("make_brand")),
        model=clean_val(result.get("model")),
        variant=clean_val(result.get("variant")),
        color=clean_val(result.get("color")),
        size_capacity=clean_val(result.get("size_capacity")),
        configuration=clean_val(result.get("configuration")),
        release_year=clean_val(result.get("release_year")),
        price_band=clean_val(result.get("price_band")),
        market_segment=clean_val(result.get("market_segment")),
        verified_purchase=result.get("verified_purchase", False),
        purchase_channel=clean_val(result.get("purchase_channel")),
        purchase_region=clean_val(result.get("purchase_region")),
        usage_duration_bucket=clean_val(result.get("usage_duration_bucket")),
        ownership_stage=clean_val(result.get("ownership_stage")),
        disposition_1=clean_val(result.get("disposition_1")),
        disposition_2=clean_val(result.get("disposition_2")),
        disposition_3=clean_val(result.get("disposition_3")),
        disposition_4=clean_val(result.get("disposition_4")),
        disposition_5=clean_val(result.get("disposition_5")),
        sentiment=clean_val(result.get("sentiment")),
        raw_llm_response=result
    )

    db.add(insight)
    db.commit()
    return insight
