"""Collect Reddit comments using PRAW. Requires environment variables: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT"""
import os
try:
    # If python-dotenv is available, load .env for local development
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass
import csv
from datetime import datetime
from praw import Reddit
import prawcore

OUTPUT_CSV = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'reddit_raw.csv')

def collect_from_subreddits(subreddits, limit=500):
    # Accept either REDDIT_CLIENT_ID or REDDIT_APP_ID (alias)
    client_id = os.getenv('REDDIT_CLIENT_ID') or os.getenv('REDDIT_APP_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    # Use REDDIT_USER_AGENT, or APP_NAME if set, or fallback default
    user_agent = os.getenv('REDDIT_USER_AGENT') or os.getenv('APP_NAME') or 'ather-rizta-sentiment/0.1'
    if not client_id or not client_secret:
        raise EnvironmentError('REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET must be set')

    reddit = Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
    rows = []
    for subreddit in subreddits:
        name = subreddit.strip()
        if ' ' in name:
            name = name.replace(' ', '')
        try:
            sub = reddit.subreddit(name)
            # trigger lookup to raise if subreddit doesn't exist
            _ = sub.id
        except prawcore.exceptions.NotFound:
            print(f"⚠️  Subreddit not found: r/{name} — skipping")
            continue
        except Exception as e:
            print(f"⚠️  Could not access r/{name}: {e} — skipping")
            continue

        for submission in sub.hot(limit=limit):
            try:
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
            except prawcore.exceptions.NotFound:
                print(f"⚠️  Submission not found in r/{name} — skipping this post")
                continue
            except Exception as e:
                print(f"⚠️  Error processing a submission in r/{name}: {e} — skipping")
                continue
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    keys = ['source','date','username','content','url','score']
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    return OUTPUT_CSV

if __name__ == '__main__':
    subs = ['ather ElectricScooters','ather scooters','ather battery']
    print('Collecting reddit comments...')
    path = collect_from_subreddits(subs, limit=100)
    print('Saved to', path)
