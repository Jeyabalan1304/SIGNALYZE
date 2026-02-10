import asyncio
import json
import os
from dotenv import load_dotenv

# Load env from backend folder
load_dotenv(dotenv_path="backend/.env")

from backend.openai_service import classify_feedback
from backend.database import SessionLocal
from backend import models

async def test_system():
    print("--- 1. Testing OpenAI Classification ---")
    test_text = "The Ather Rizta's range dropped suddenly after the last update. Very disappointing."
    try:
        result = await classify_feedback(test_text)
        print("Classification Result:")
        print(json.dumps(result, indent=2))
        if result.get('sentiment') == 'Negative' and result.get('company') == 'Ather':
            print("✅ OpenAI Classification working correctly.")
        else:
            print("⚠️ OpenAI Classification responded but results might be unexpected (check for Mock mode).")
    except Exception as e:
        print(f"❌ OpenAI Classification failed: {e}")

    print("\n--- 2. Testing Database Connection ---")
    db = SessionLocal()
    try:
        # Check if we can query the table
        count = db.query(models.Feedback).count()
        print(f"✅ Database connected. Total feedback records: {count}")
    except Exception as e:
        print(f"❌ Database query failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Ensure we are in the right directory for imports
    import sys
    import os
    sys.path.append(os.getcwd())
    asyncio.run(test_system())
