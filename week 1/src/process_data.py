"""Process raw CSVs, clean text, deduplicate, and output final dataset with required schema."""
import os
import pandas as pd
import re

OUTPUT_CSV = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'clean_dataset.csv')


def clean_text(text):
    if pd.isna(text):
        return ''
    text = re.sub(r'http\S+', '', text)  # remove urls
    text = re.sub(r'www\.[^\s]+', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def process_raw_files(raw_paths):
    dfs = []
    for p in raw_paths:
        if not os.path.exists(p):
            continue
        df = pd.read_csv(p)
        dfs.append(df)
    if not dfs:
        raise FileNotFoundError('No raw files found')
    df = pd.concat(dfs, ignore_index=True, sort=False)

    # normalize columns
    df = df.rename(columns={
        'likeCount': 'engagement',
        'score': 'engagement',
        'created_utc': 'date'
    })
    # ensure required columns
    for c in ['source','date','username','content','url']:
        if c not in df.columns:
            df[c] = ''
    df['content'] = df['content'].map(clean_text)
    df = df[df['content'].str.len() > 0]
    # dedupe by content
    df = df.drop_duplicates(subset=['content'])
    # keep only required schema plus engagement
    out = df[['source','date','username','content','url']].copy()
    out['sentiment'] = ''
    out['category1'] = ''
    out['category2'] = ''
    out['category3'] = ''
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    out.to_csv(OUTPUT_CSV, index=False)
    return OUTPUT_CSV

if __name__ == '__main__':
    raw1 = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'reddit_raw.csv')
    raw2 = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'youtube_raw.csv')
    print('Processing raw files...')
    path = process_raw_files([raw1, raw2])
    print('Saved clean dataset to', path)
