from sqlalchemy import Column, String, Text, DateTime, Index, ForeignKey, JSON, Boolean, Integer
from sqlalchemy.orm import relationship
import uuid
import datetime
from database import Base

class RawFeedback(Base) :
    __tablename__ = "raw_feedback"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    raw_text = Column(Text, nullable=False)
    source = Column(String(50)) # youtube, reddit, csv
    source_metadata = Column(JSON, nullable=True) # Storage for video_id, subreddit etc.
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    preprocessed = relationship("PreprocessedFeedback", back_populates="raw", uselist=False)

class PreprocessedFeedback(Base):
    __tablename__ = "preprocessed_feedback"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    raw_id = Column(String, ForeignKey("raw_feedback.id"), nullable=False)
    cleaned_text = Column(Text, nullable=False)
    language = Column(String(10))
    is_translated = Column(Boolean, default=False)
    translated_text = Column(Text, nullable=True)
    text_hash = Column(String(32), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    raw = relationship("RawFeedback", back_populates="preprocessed")
    insight = relationship("ClassifiedInsight", back_populates="preprocessed", uselist=False)

class ClassifiedInsight(Base):
    __tablename__ = "classified_insights"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    preprocessed_id = Column(String, ForeignKey("preprocessed_feedback.id"), nullable=False, unique=True)
    
    # Core Identity
    item_id = Column(String(100))
    item_type = Column(String(100))

    # Commercial Attributes
    product_category = Column(String(100))
    product_subcategory = Column(String(100))
    make_brand = Column(String(100))
    model = Column(String(100))
    variant = Column(String(100))
    color = Column(String(50))
    size_capacity = Column(String(50))
    configuration = Column(String(100))
    release_year = Column(Integer, nullable=True)
    price_band = Column(String(50))
    market_segment = Column(String(100))

    # Purchase Context
    verified_purchase = Column(Boolean, default=False)
    purchase_channel = Column(String(100))
    purchase_region = Column(String(100))
    usage_duration_bucket = Column(String(100))
    ownership_stage = Column(String(100))

    # Signalyze AI Output
    disposition_1 = Column(String(255))
    disposition_2 = Column(String(255))
    disposition_3 = Column(String(255))
    disposition_4 = Column(String(255))
    disposition_5 = Column(String(255))
    sentiment = Column(String(50)) # Positive, Negative, Neutral

    raw_llm_response = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship
    preprocessed = relationship("PreprocessedFeedback", back_populates="insight")

# Note: Deleted old Feedback table to enforce new 3-layer schema
