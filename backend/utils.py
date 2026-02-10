import re
import hashlib
from langdetect import detect, DetectorFactory

# Ensure consistent results for langdetect
DetectorFactory.seed = 0

def clean_text(text: str) -> str:
    # Strip irrelevant URLs
    text = re.sub(r'http\S+', '', text)
    # Remove bot-generated markers
    text = re.sub(r'\[bot\]', '', text, flags=re.IGNORECASE)
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s\.,!\?\-]', '', text)
    text = text.strip()
    return text

def get_text_hash(text: str) -> str:
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def detect_language(text: str) -> str:
    try:
        if not text or len(text) < 3: return "unknown"
        return detect(text)
    except:
        return "unknown"

async def translate_if_needed(text: str, source_lang: str):
    """
    Placeholder for translation service. 
    In production, this would call GPT or Google Translate API.
    """
    if source_lang == 'en':
        return text, False
    # For now, we mock translation as we'll use LLM for classification anyway
    # which usually handles multi-language well.
    return text, False
