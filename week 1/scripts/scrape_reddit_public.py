"""scrape_reddit_public.py
Fallback Reddit scraper using public JSON endpoints (no OAuth).
Collects comments from subreddit hot posts and saves to data/reddit_raw.csv
Usage: python scrape_reddit_public.py --subreddits ElectricScooters,scooters,electricvehicles --max_comments 250
"""
import requests
import time
import csv
import argparse
import os
from datetime import datetime
from tqdm import tqdm

HEADERS = {'User-Agent': 'ather-rizta-sentiment/0.1 (by /u/yourname)'}


def fetch_hot_posts(subreddit, limit=50):
    url = f'https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}'
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    posts = [p['data'] for p in data.get('data', {}).get('children', [])]
    return posts


def fetch_comments_for_post(post_id):
    url = f'https://www.reddit.com/comments/{post_id}.json?limit=500'
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    comments = []
    if len(data) > 1:
        comment_tree = data[1].get('data', {}).get('children', [])
        for c in comment_tree:
            comments.extend(flatten_comment_node(c))
    return comments


def flatten_comment_node(node):
    # node is an object with kind and data
    rows = []
    kind = node.get('kind')
    data = node.get('data', {})
    if kind != 'more' and data.get('body'):
        rows.append({
            'source': 'reddit',
            'date': datetime.utcfromtimestamp(data.get('created_utc', 0)).isoformat() if data.get('created_utc') else '',
            'username': data.get('author'),
            'content': data.get('body', ''),
            'url': f"https://reddit.com{data.get('permalink', '')}",
            'engagement': data.get('score', 0)
        })
    # recurse into replies
    for child in data.get('replies', {}).get('data', {}).get('children', []):
        rows.extend(flatten_comment_node(child))
    return rows


def collect(subreddits, limit_posts=50, max_comments=250, out_path='data/reddit_raw.csv'):
    all_comments = []
    for sub in subreddits:
        try:
            posts = fetch_hot_posts(sub, limit=limit_posts)
        except Exception as e:
            print('Failed to fetch posts for', sub, '->', e)
            continue
        for p in posts:
            pid = p.get('id')
            try:
                comments = fetch_comments_for_post(pid)
                for c in comments:
                    all_comments.append(c)
                # be gentle
                time.sleep(1)
            except Exception as e:
                # skip failures
                # print('Failed comments for', pid, e)
                time.sleep(1)
            if len(all_comments) >= max_comments:
                break
        if len(all_comments) >= max_comments:
            break
    # dedupe by content
    seen = set()
    unique = []
    for c in all_comments:
        text = (c.get('content') or '').strip()
        if not text:
            continue
        if text in seen:
            continue
        seen.add(text)
        unique.append(c)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    keys = ['source','date','username','content','url','engagement']
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in unique[:max_comments]:
            writer.writerow(r)
    return out_path, len(unique[:max_comments])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--subreddits', default='ElectricScooters,scooters,electricvehicles')
    parser.add_argument('--limit', type=int, default=50, help='posts per subreddit')
    parser.add_argument('--max_comments', type=int, default=250)
    parser.add_argument('--out', default='data/reddit_raw.csv')
    args = parser.parse_args()
    subs = [s.strip() for s in args.subreddits.split(',') if s.strip()]
    print('Collecting from', subs)
    path, count = collect(subs, limit_posts=args.limit, max_comments=args.max_comments, out_path=args.out)
    print('Saved', path, 'with', count, 'unique comments')
