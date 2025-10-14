"""scrape_praw.py
Collect Reddit comments from target subreddits using PRAW and save to a CSV in the `data/` folder.
Usage:
  python scrape_praw.py --subreddits Ather ElectricScooters,ather scooters,ather electricvehicles --limit 200

Requires environment variables:
  REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
"""
import os
import csv
import argparse
from datetime import datetime

try:
    import praw
except Exception:
    praw = None


def collect_comments(subreddits, limit=200, out_path='data/reddit_raw.csv'):
    if praw is None:
        raise RuntimeError('praw is not installed. Install with `pip install praw`.')
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT', 'ather-rizta/0.1')
    if not client_id or not client_secret:
        raise EnvironmentError('Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in your environment')

    reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
    rows = []
    for sub in subreddits:
        subreddit = reddit.subreddit(sub)
        for submission in subreddit.hot(limit=limit):
            try:
                submission.comments.replace_more(limit=0)
            except Exception:
                pass
            for comment in submission.comments.list():
                rows.append({
                    'source': 'reddit',
                    'date': datetime.utcfromtimestamp(getattr(comment, 'created_utc', submission.created_utc)).isoformat(),
                    'username': str(getattr(comment, 'author', '')),
                    'content': getattr(comment, 'body', '') or '',
                    'url': f'https://reddit.com{getattr(comment, "permalink", submission.permalink)}',
                    'engagement': getattr(comment, 'score', 0)
                })
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    keys = ['source','date','username','content','url','engagement']
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    return out_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--subreddits', default='ather ElectricScooters,ather scooters,ather electricvehicles')
    parser.add_argument('--limit', type=int, default=200)
    parser.add_argument('--out', default='data/reddit_raw.csv')
    args = parser.parse_args()
    subs = [s.strip() for s in args.subreddits.split(',') if s.strip()]
    print('Collecting from', subs)
    path = collect_comments(subs, limit=args.limit, out_path=args.out)
    print('Saved', path)
