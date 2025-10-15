"""Filter raw Reddit/YouTube comments for mentions of Ather (AtherEnergy, Rizta, battery, etc.).
Writes `data/ather_raw.csv` and `results/combined_ather.csv`.

Usage:
  python scripts\filter_ather_comments.py --reddit data/reddit_raw.csv --youtube data/youtube_raw.csv
"""
import os
import argparse
import pandas as pd


KEYWORDS = [
    'ather',
    'atherenergy',
    'rizta',
    'ather battery',
    'atherbattery',
    'ather rizta'
]


def load_if_exists(path):
    if not path or not os.path.exists(path):
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def contains_keyword(text):
    if not isinstance(text, str):
        return False
    t = text.lower()
    for k in KEYWORDS:
        if k in t:
            return True
    return False


def main(reddit_path, youtube_path, out_data='data/ather_raw.csv', out_results='results/combined_ather.csv'):
    dfs = []
    r = load_if_exists(reddit_path)
    if not r.empty:
        r['source'] = r.get('source', 'reddit')
        dfs.append(r)
    y = load_if_exists(youtube_path)
    if not y.empty:
        y['source'] = y.get('source', 'youtube')
        dfs.append(y)

    if not dfs:
        print('No input files found. Exiting.')
        return

    df = pd.concat(dfs, ignore_index=True, sort=False)
    df['content'] = df['content'].fillna('').astype(str)
    mask = df['content'].apply(contains_keyword)
    filtered = df[mask].copy()

    os.makedirs(os.path.dirname(out_data), exist_ok=True)
    os.makedirs(os.path.dirname(out_results), exist_ok=True)

    filtered.to_csv(out_data, index=False)
    # normalize output columns for combined results
    cols = ['source','date','username','content','url']
    for c in cols:
        if c not in filtered.columns:
            filtered[c] = ''
    out_df = filtered[cols].copy()
    out_df.to_csv(out_results, index=False)

    print(f'Found {len(filtered)} Ather-related comments')
    print('Wrote:', out_data)
    print('Wrote:', out_results)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--reddit', default='data/reddit_raw.csv')
    parser.add_argument('--youtube', default='data/youtube_raw.csv')
    parser.add_argument('--out-data', default='data/ather_raw.csv')
    parser.add_argument('--out-results', default='results/combined_ather.csv')
    args = parser.parse_args()
    main(args.reddit, args.youtube, args.out_data, args.out_results)
