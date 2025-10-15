Ather Sentiment Analysis System

An end-to-end sentiment and feedback mining project built to understand public opinion on the **Ather Rizta** electric scooter. This project combines web scraping, natural language processing (NLP), and data visualization to uncover actionable insights from community discussions on **Reddit** and **YouTube**.

---

##  Project Overview

This system automates the full analytics pipeline — from gathering user-generated content to performing multi-level sentiment and feedback categorization. It identifies public perception, recurring themes, and improvement areas for the Ather Rizta EV.

**Core Functions:**
- Automated data collection from Reddit & YouTube
- Sentiment classification into Positive, Negative, and Neutral
- Three-level hierarchical categorization for detailed insight mapping
- Statistical and visual analysis of sentiment trends
- Data cleaning, normalization, and duplicate removal

---

##  Deliverables

1. **Clean Processed Dataset**  
   CSV file containing all comments, metadata, sentiment scores, and hierarchical category tags.  
   → Output location: `results/rizta_sentiment_analysis_final.csv`

2. **Insight Report**  
   A two-page summary highlighting major findings — top praises, critical issues, and the analytical methodology used.  
   → Output: `results/ather_rizta_summary_report.pdf`

3. **Source Code & Dependencies**  
   All scripts for scraping, analysis, and visualization, along with a `requirements.txt` for reproducibility.

---

##  Project Layout

├── reddit_collector.py # Script for Reddit comment extraction
├── youtube_collector.py # Script for YouTube comment collection
├── unify_data.py # Combines and standardizes collected data
├── evaluate_sentiment.py # Performs sentiment and hierarchical analysis
├── requirements.txt # All required Python dependencies
├── README.md # Documentation and usage guide
├── data/ # Raw Reddit/YouTube data
└── results/ # Cleaned datasets, visuals, and reports


---

##  Setup & Installation

### Prerequisites
- Python 3.8 or above  
- pip package manager  

### Installation Steps
```bash
git clone <your-repository-url>
cd rizta_sentiment_analysis_project
pip install -r requirements.txt

▶️ Execution Workflow

Run the scripts in the following order to reproduce the full analysis:

Collect Data

python reddit_collector.py
python youtube_collector.py


Combine and Clean

python unify_data.py


Run Analysis

python evaluate_sentiment.py

📊 Data Schema
Column	Description
source	Origin platform (Reddit / YouTube)
date	Timestamp of comment or post
username	Comment author
title	Post title (for Reddit threads)
content	Actual comment or post text
engagement	Likes / upvotes count
url	Source URL of post/comment
content_type	Type of post (YouTube Comment, Reddit Thread, etc.)
positive_score	Probability of positive sentiment
neutral_score	Probability of neutral sentiment
negative_score	Probability of negative sentiment
sentiment	Final sentiment label (Positive / Neutral / Negative)
category1	Main category (Product, Software, Service, etc.)
category2	Sub-category (Battery, Design, Comfort, etc.)
category3	Specific praise/issue (Fast Charging, Seat Comfort, etc.)
🧭 Hierarchical Feedback Taxonomy
Level 1 (Primary Categories)

Product

Software & Connectivity

Charging & Infrastructure

Service & Support

Pricing & Value

User Experience

Level 2 (Subcategories)

Battery & Range, Build Quality, Ride Comfort

Display, App Integration, Firmware Updates

Charge Time, Port Availability, Infrastructure

Service Delay, Warranty Claims, Staff Response

Affordability, Price Justification, Subscription Costs

Level 3 (Detailed Mentions)

Examples:
“Slow OTA updates,” “Excellent ride comfort,” “Range exceeds expectations,” “Plastic quality feels flimsy,” “Long charging duration.”

🧠 Technical Details

Model: RoBERTa (cardiffnlp/twitter-roberta-base-sentiment)

Libraries:

Text Processing: regex, nltk, langdetect

NLP: transformers, torch

Data Handling: pandas, numpy

Visualization: matplotlib, seaborn

Classification System: Keyword-driven multi-level mapping with adjustable label dictionaries.

 Outputs

The project produces the following key artifacts:
CSV Outputs
rizta_sentiment_analysis_final.csv (full sentiment results)
clean_rizta_feedback.csv (essential columns only)
Visuals
Sentiment distribution pie/bar chart
Positive vs. Negative category heatmap
Frequency chart of top issues and praises
Report
ather_rizta_summary_report.pdf – summarizes findings and methodology

 Future Enhancements

Integrate transformer-based aspect-level sentiment analysis
Introduce trend analysis over time
Expand data sources (Twitter, auto forums)
Add topic modeling for automatic theme extraction
Build a simple web dashboard for visualization

 License & Usage

This repository is for academic and research purposes only.
Please ensure compliance with the terms of service of Reddit, YouTube, and other data platforms when using this code.

---

## Credentials & Environment Variables

This project reads API credentials from environment variables. You can create a local `.env` file in the project root (recommended for development) with the following variables:

- `REDDIT_CLIENT_ID` - Reddit application client id (or `REDDIT_APP_ID` if you prefer — see note below)
- `REDDIT_CLIENT_SECRET` - Reddit application client secret
- `REDDIT_USER_AGENT` - Optional; defaults to `ather-rizta-sentiment/0.1`
- `YOUTUBE_API_KEY` - YouTube Data API key

Example `.env` contents:

```
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=SIgnalyze bot
YOUTUBE_API_KEY=your_youtube_api_key_here
```

Note: you provided an App Name and App ID. I saved them to a `.env` file as `APP_NAME` and `REDDIT_APP_ID` for convenience. The project currently expects `REDDIT_CLIENT_ID`; if you'd like I can update the code to also look for `REDDIT_APP_ID` as an alias.

Security: `.env` is added to `.gitignore` to prevent accidental commits. For production, prefer setting real environment variables in your deployment environment rather than storing secrets in files.