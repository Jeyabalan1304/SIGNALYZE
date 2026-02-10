import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from openai_service import classify_feedback
from dotenv import load_dotenv

load_dotenv('backend/.env')

async def test_classification():
    print("Testing OpenAI Classification...")
    text = "The Ather 450X battery life is amazing but the seat is a bit hard."
    result = await classify_feedback(text)
    print("Result:")
    print(result)

if __name__ == "__main__":
    asyncio.run(test_classification())
