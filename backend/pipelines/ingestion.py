from sqlalchemy.orm import Session
import models
from utils import clean_text, get_text_hash

async def ingest_raw_data(db: Session, raw_text: str, source: str, metadata: dict = None):
    # Step 1: Just store raw data as it comes
    raw_item = models.RawFeedback(
        raw_text=raw_text,
        source=source,
        source_metadata=metadata
    )
    db.add(raw_item)
    db.commit()
    db.refresh(raw_item)
    return raw_item
