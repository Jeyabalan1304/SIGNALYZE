"""combine_data.py
Combine raw CSVs (`data/reddit_raw.csv`, `data/youtube_raw.csv`) into a standardized `results/combined.csv` using the schema required for submission.
Output fields: source,date,username,content,url,engagement,sentiment,category1,category2,category3
"""
import os
import pandas as pd

RAW_REDDIT = 'data/reddit_raw.csv'
RAW_YOUTUBE = 'data/youtube_raw.csv'
OUT = 'results/combined.csv'


def standardize(df):
    # Keep only required columns and ensure names
    df = df.rename(columns={'likeCount':'engagement','score':'engagement'})
    for c in ['source','date','username','content','url','engagement']:
        if c not in df.columns:
            df[c] = ''
    df = df[['source','date','username','content','url','engagement']]
    df['content'] = df['content'].fillna('').astype(str)
    df = df[df['content'].str.strip().str.len() > 0]
    return df


def combine_and_save():
    parts = []
    if os.path.exists(RAW_REDDIT):
        parts.append(standardize(pd.read_csv(RAW_REDDIT)))
    if os.path.exists(RAW_YOUTUBE):
        parts.append(standardize(pd.read_csv(RAW_YOUTUBE)))
    if not parts:
        raise FileNotFoundError('No raw data files found in data/')
    df = pd.concat(parts, ignore_index=True)
    df = df.drop_duplicates(subset=['content'])
    df['sentiment'] = ''
    df['category1'] = ''
    df['category2'] = ''
    df['category3'] = ''
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    df.to_csv(OUT, index=False)
    return OUT

if __name__ == '__main__':
    print('Combining raw CSVs...')
    print(combine_and_save())
