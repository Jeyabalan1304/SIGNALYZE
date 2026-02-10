from sqlalchemy.orm import Session
import models
from utils import clean_text, get_text_hash, detect_language, translate_if_needed

async def process_raw_item(db: Session, raw_id: str):
    raw_item = db.query(models.RawFeedback).filter(models.RawFeedback.id == raw_id).first()
    if not raw_item: return None

    # Cleaning
    cleaned = clean_text(raw_item.raw_text)
    t_hash = get_text_hash(cleaned)

    # De-duplication check
    exists = db.query(models.PreprocessedFeedback).filter(models.PreprocessedFeedback.text_hash == t_hash).first()
    if exists: return exists

    # Language & Translation
    lang = detect_language(cleaned)
    translated_text, is_translated = await translate_if_needed(cleaned, lang)

    preprocessed = models.PreprocessedFeedback(
        raw_id=raw_id,
        cleaned_text=cleaned,
        language=lang,
        is_translated=is_translated,
        translated_text=translated_text,
        text_hash=t_hash
    )
    db.add(preprocessed)
    db.commit()
    db.refresh(preprocessed)
    return preprocessed
