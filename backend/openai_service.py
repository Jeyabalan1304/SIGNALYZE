import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return AsyncOpenAI(api_key=api_key)

client = get_openai_client()

async def analyze_feedback(text):
    """
    Analyzes feedback using OpenAI and returns structured JSON based on user taxonomy.
    """
    if not client:
        print("OpenAI client not initialized. Check API key.")
        return None

    prompt = f"""You are a product intelligence system.
Analyze the customer feedback and return ONLY valid JSON.

Fields:
- item_type
- product_category
- product_subcategory
- make_brand
- model
- variant
- color
- size_capacity
- configuration
- release_year
- price_band
- market_segment
- verified_purchase (true/false/null)
- purchase_channel
- purchase_region
- usage_duration_bucket
- ownership_stage
- disposition_1
- disposition_2
- disposition_3
- disposition_4
- disposition_5
- sentiment (Positive, Negative, Neutral)

Rules:
- Use null if not mentioned
- Do NOT hallucinate brand/model
- Output JSON only
- No explanation

Customer feedback:
{text}
"""
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        return None
