import time
import asyncio
from sqlalchemy.orm import Session
from models import PreprocessedFeedback, ClassifiedInsight
from openai_service import analyze_feedback
from pipelines.classification import clean_val

async def run_classification_pipeline(db: Session, batch_size: int = 20):
    """
    1. Fetch unclassified preprocessed rows
    2. Parallel processing using asyncio.gather
    3. Bulk save results
    """
    # Find preprocessed items that don't have a classified insight yet
    unprocessed = db.query(PreprocessedFeedback).outerjoin(ClassifiedInsight).filter(ClassifiedInsight.id == None).limit(batch_size).all()
    
    if not unprocessed:
        return 0

    print(f"PIPELINE: Processing batch of {len(unprocessed)} in parallel...")
    
    # Create tasks for all records in the batch
    # Use translated text if available, else cleaned text
    tasks = [analyze_feedback(record.translated_text if record.is_translated else record.cleaned_text) for record in unprocessed]
    
    # Run all OpenAI calls concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    results_count = 0
    for record, structured_data in zip(unprocessed, results):
        if isinstance(structured_data, Exception):
            print(f"ERROR: OpenAI task failed for {record.id}: {structured_data}")
            continue
            
        if structured_data:
            try:
                # Create result entry (ClassifiedInsight)
                new_insight = ClassifiedInsight(
                    preprocessed_id=record.id,
                    item_id=clean_val(structured_data.get("item_id")),
                    item_type=clean_val(structured_data.get("item_type")),
                    product_category=clean_val(structured_data.get("product_category")),
                    product_subcategory=clean_val(structured_data.get("product_subcategory")),
                    make_brand=clean_val(structured_data.get("make_brand")),
                    model=clean_val(structured_data.get("model")),
                    variant=clean_val(structured_data.get("variant")),
                    color=clean_val(structured_data.get("color")),
                    size_capacity=clean_val(structured_data.get("size_capacity")),
                    configuration=clean_val(structured_data.get("configuration")),
                    release_year=clean_val(structured_data.get("release_year")),
                    price_band=clean_val(structured_data.get("price_band")),
                    market_segment=clean_val(structured_data.get("market_segment")),
                    verified_purchase=structured_data.get("verified_purchase", False),
                    purchase_channel=clean_val(structured_data.get("purchase_channel")),
                    purchase_region=clean_val(structured_data.get("purchase_region")),
                    usage_duration_bucket=clean_val(structured_data.get("usage_duration_bucket")),
                    ownership_stage=clean_val(structured_data.get("ownership_stage")),
                    disposition_1=clean_val(structured_data.get("disposition_1")),
                    disposition_2=clean_val(structured_data.get("disposition_2")),
                    disposition_3=clean_val(structured_data.get("disposition_3")),
                    disposition_4=clean_val(structured_data.get("disposition_4")),
                    disposition_5=clean_val(structured_data.get("disposition_5")),
                    sentiment=clean_val(structured_data.get("sentiment")),
                    raw_llm_response=structured_data
                )
                db.add(new_insight)
                results_count += 1
            except Exception as e:
                print(f"ERROR: Mapping failed for {record.id}: {e}")
        else:
            print(f"FAILED: OpenAI returned nothing for {record.id}")
            
    # Commit the entire batch at once
    try:
        db.commit()
    except Exception as e:
        print(f"ERROR: Batch commit failed: {e}")
        db.rollback()
        return 0
            
    return results_count
