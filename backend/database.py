import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv, find_dotenv

# Try to find the .env file explicitly
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)
else:
    # Manual fallback if find_dotenv fails
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# STRICTLY USING RDS AS PER USER INSTRUCTION
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    # DEBUG: Print environment to see what is loaded
    print(f"DEBUG: Current CWD: {os.getcwd()}")
    print(f"DEBUG: .env path used: {dotenv_path}")
    print(f"DEBUG: Keys in os.environ: {list(os.environ.keys())}")
    raise ValueError("DATABASE_URL not found in .env file. Please check your configuration.")

print(f"DATABASE CONFIG: Connecting to RDS at {SQLALCHEMY_DATABASE_URL.split('@')[1]}")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
