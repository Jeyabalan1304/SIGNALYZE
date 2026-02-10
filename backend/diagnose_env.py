import os
from dotenv import load_dotenv, find_dotenv

print(f"Current Working Directory: {os.getcwd()}")
dotenv_path = find_dotenv()
print(f"Proposed dotenv path: {dotenv_path}")

if dotenv_path:
    load_dotenv(dotenv_path)
    print("load_dotenv() called.")
else:
    print("find_dotenv() found nothing.")

db_url = os.getenv("DATABASE_URL")
print(f"DATABASE_URL value: {'Found' if db_url else 'Not Found'}")
if db_url:
    print(f"DATABASE_URL: {db_url}")

print("File content of .env (if exists):")
if os.path.exists(".env"):
    with open(".env", "r") as f:
        print(f.read())
else:
    print(".env NOT FOUND in current directory.")

print("Directory structure of current directory:")
print(os.listdir("."))
