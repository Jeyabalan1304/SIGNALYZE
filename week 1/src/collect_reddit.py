"""Collect Reddit comments using PRAW. Requires environment variables: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT"""
import os
import csv
from datetime import datetime
from praw import Reddit

OUTPUT_CSV = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'reddit_raw.csv')

def collect_from_subreddits(subreddits, limit=500):
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT', 'ather-rizta-sentiment/0.1')
    if not client_id or not client_secret:
        raise EnvironmentError('REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET must be set')

    reddit = Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
    rows = []
    for subreddit in subreddits:
        sub = reddit.subreddit(subreddit)
        for submission in sub.hot(limit=limit):
            submission.comments.replace_more(limit=0)
            for comment in submission.comments.list():
                rows.append({
                    'source': 'reddit',
                    'date': datetime.utcfromtimestamp(comment.created_utc).isoformat(),
                    'username': str(comment.author),
                    'content': comment.body,
                    'url': f'https://reddit.com{comment.permalink}',
                    'score': getattr(comment, 'score', 0)
                })
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    keys = ['source','date','username','content','url','score']
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    return OUTPUT_CSV

if __name__ == '__main__':
    subs = ['ElectricScooters','scooters','electricvehicles']
    print('Collecting reddit comments...')
    path = collect_from_subreddits(subs, limit=100)
    print('Saved to', path)
