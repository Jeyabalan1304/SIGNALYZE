import os
import csv
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# Ensure VADER lexicon is available
nltk.download('vader_lexicon')
from langdetect import detect
import re

DATA_FILES = [
    'data/reddit_raw.csv',
    'data/youtube_raw.csv'
]

OUTPUT_CSV = 'results/combined_analysis.csv'
OUTPUT_SUMMARY = 'results/summary.md'


def load_data():
    rows = []
    for f in DATA_FILES:
        if not os.path.exists(f):
            continue
        df = pd.read_csv(f)
        if 'source' not in df.columns:
            df['source'] = os.path.splitext(os.path.basename(f))[0]
        rows.append(df)
    if not rows:
        return pd.DataFrame(columns=['source','date','username','content','url','engagement'])
    return pd.concat(rows, ignore_index=True)


def is_english(text):
    try:
        return detect(text) == 'en'
    except Exception:
        return False


def simple_hierarchical_classify(text):
    t = text.lower()
    # Category 1: Product, Service, Charging, Price, User Experience
    if any(k in t for k in ['battery', 'range', 'charging', 'charger']):
        c1 = 'Product'
        c2 = 'Battery & Charging'
        if 'fast' in t or 'quick' in t:
            c3 = 'Fast charging praised'
        elif 'long' in t or 'range' in t:
            c3 = 'Range mention'
        else:
            c3 = 'Battery mention'
    elif any(k in t for k in ['service', 'support', 'customer', 'warranty']):
        c1 = 'Service'
        c2 = 'After-sales'
        c3 = 'Service experience'
    elif any(k in t for k in ['app', 'display', 'software', 'ota', 'firmware']):
        c1 = 'Product'
        c2 = 'Software & Display'
        c3 = 'App/OTA mention'
    elif any(k in t for k in ['price', 'cost', 'expensive', 'value']):
        c1 = 'Pricing'
        c2 = 'Affordability'
        c3 = 'Price perception'
    else:
        c1 = 'User Experience'
        c2 = 'Ride & Comfort'
        c3 = 'General mention'
    return c1, c2, c3


def main():
    os.makedirs('results', exist_ok=True)
    df = load_data()
    print('Loaded rows:', len(df))

    analyzer = SentimentIntensityAnalyzer()
    out_rows = []
    for _, r in df.iterrows():
        text = str(r.get('content','') or '')
        if not text.strip():
            continue
        if not is_english(text):
            continue
        vs = analyzer.polarity_scores(text)
        compound = vs['compound']
        if compound >= 0.05:
            sentiment = 'positive'
        elif compound <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        c1, c2, c3 = ('','','')
        if sentiment != 'neutral':
            c1, c2, c3 = simple_hierarchical_classify(text)

        out_rows.append({
            'source': r.get('source',''),
            'date': r.get('date',''),
            'username': r.get('username',''),
            'content': text,
            'url': r.get('url',''),
            'engagement': r.get('engagement',''),
            'sentiment': sentiment,
            'compound': compound,
            'category1': c1,
            'category2': c2,
            'category3': c3,
        })

    out_df = pd.DataFrame(out_rows)
    out_df.to_csv(OUTPUT_CSV, index=False)
    print('Wrote', OUTPUT_CSV)

    # Simple summary: top categories and top positives/negatives
    pos = out_df[out_df['sentiment']=='positive']
    neg = out_df[out_df['sentiment']=='negative']

    def top_n_terms(df, n=5):
        words = ' '.join(df['content'].astype(str)).lower()
        words = re.findall(r"\w+", words)
        stop = set(['the','and','a','to','is','it','of','in','for','you','on','that','this','with'])
        freqs = {}
        for w in words:
            if w in stop or len(w)<3:
                continue
            freqs[w] = freqs.get(w,0)+1
        items = sorted(freqs.items(), key=lambda x: x[1], reverse=True)
        return items[:n]

    summary_lines = []
    summary_lines.append('# Signalyze Ather Rizta Quick Summary')
    summary_lines.append(f'Total comments analyzed: {len(out_df)}')
    summary_lines.append(f'Positive: {len(pos)}, Neutral: {len(out_df)-len(pos)-len(neg)}, Negative: {len(neg)}')
    summary_lines.append('\n## Top positive themes (keywords)')
    for k,v in top_n_terms(pos,5):
        summary_lines.append(f'- {k} ({v})')
    summary_lines.append('\n## Top negative themes (keywords)')
    for k,v in top_n_terms(neg,5):
        summary_lines.append(f'- {k} ({v})')

    with open(OUTPUT_SUMMARY, 'w', encoding='utf-8') as f:
        f.write('\n'.join(summary_lines))
    print('Wrote summary to', OUTPUT_SUMMARY)


if __name__ == '__main__':
    main()
