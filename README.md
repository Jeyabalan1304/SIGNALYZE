# Signalyze: Technical Implementation

Signalyze transforms raw customer feedback into product insights using OpenAI.

## Project Structure
- **/backend**: FastAPI application, SQLAlchemy models, OpenAI integration, and scrapers.
- **/frontend**: Vite + React + Tailwind CSS dashboard with Recharts.

## Backend Setup
1. `cd backend`
2. Create a virtual environment: `python -m venv venv`
3. Activate venv: `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Create `.env` file based on `.env.example`.
6. Run the server: `python main.py`

## Frontend Setup
1. `cd frontend`
2. Install dependencies: `npm install --legacy-peer-deps`
3. Run the development server: `npm run dev`

## Features Implemented
- **Multi-Source Ingestion**: CSV upload (completed), YouTube/Reddit placeholders provided.
- **Preprocessing**: Cleaning and MD5 de-duplication.
- **AI Classification**: Integration with OpenAI GPT-4o-mini (Mocked for local dev if no key).
- **Dashboard**: Real-time stats and "Double Insight" view (Positive vs Negative charts).
- **Database**: SQLite used for local prototyping (easily switchable to PostgreSQL via `DATABASE_URL`).
