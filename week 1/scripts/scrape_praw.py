"""
reddit_scraper.py
-----------------
Collects Reddit comments from target subreddits using the PRAW API and
stores them in CSV format under the 'data/' folder.

Usage:
  python reddit_scraper.py --subs "AtherEnergy,electricvehicles" --limit 200
"""

import os
import csv
import argparse
from datetime import datetime
from dotenv import load_dotenv
import praw
import prawcore

# Load environment variables
load_dotenv()

def fetch_reddit_comments(sub_list, limit=200, output_file='data/reddit_comments.csv'):
    """Collects recent Reddit comments from given subreddits."""
    # Read credentials from environment (support both REDDIT_CLIENT_ID and REDDIT_APP_ID)
    client_id = os.getenv('REDDIT_CLIENT_ID') or os.getenv('REDDIT_APP_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT') or os.getenv('APP_NAME') or 'signalyze-bot/0.1'

    if not all([client_id, client_secret, user_agent]):
        raise EnvironmentError("Missing Reddit API credentials. Check your .env file.")

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )

    results = []
    for sub in sub_list:
        name = sub.strip()
        # subreddit names cannot contain spaces; try to normalize common user input
        if ' ' in name:
            candidate = name.replace(' ', '')
        else:
            candidate = name
        print(f"Fetching comments from r/{candidate} ...")
        try:
            subreddit = reddit.subreddit(candidate)
            # force a quick lookup to trigger NotFound if the subreddit doesn't exist
            _ = subreddit.id
        except prawcore.exceptions.NotFound:
            print(f"⚠️  Subreddit not found: r/{candidate} — skipping")
            continue
        except Exception as e:
            print(f"⚠️  Could not access r/{candidate}: {e} — skipping")
            continue
    for post in subreddit.hot(limit=limit):
            try:
                # Some submissions may be removed or cause 404s when fetched; guard the whole block
                post.comments.replace_more(limit=0)
                for comment in post.comments.list():
                    results.append({
                        "source": "reddit",
                        "date": datetime.utcfromtimestamp(
                            getattr(comment, "created_utc", post.created_utc)
                        ).isoformat(),
                        "username": str(getattr(comment, "author", "")),
                        "content": getattr(comment, "body", ""),
                        "url": f"https://reddit.com{getattr(comment, 'permalink', post.permalink)}",
                        "engagement": getattr(comment, "score", 0)
                    })
            except prawcore.exceptions.NotFound:
                print(f"⚠️  Submission not found in r/{candidate} — skipping this post")
                continue
            except Exception as e:
                print(f"⚠️  Error processing a post in r/{candidate}: {e} — skipping")
                continue

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    # Ensure we have at least the expected columns if no results
    if not results:
        keys = ['source','date','username','content','url','engagement']
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
    else:
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

    print(f"\n✅ Data saved: {output_file}")
    print(f"Total comments collected: {len(results)}")
    return output_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect Reddit comments about Ather Rizta.")
    parser.add_argument("--subs", default="AtherEnergy,ElectricScooters,electricvehicles")
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--out", default="data/reddit_comments.csv")
    parser.add_argument('--keywords', default='', help='Comma-separated keywords to search for (overrides subs if provided)')
    args = parser.parse_args()
    if args.keywords:
        # perform a subreddit-agnostic search for the keywords and collect comments from matched submissions
        keywords = [k.strip() for k in args.keywords.split(',') if k.strip()]
        # use reddit.search to find submissions matching keywords
        client_id = os.getenv('REDDIT_CLIENT_ID') or os.getenv('REDDIT_APP_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        user_agent = os.getenv('REDDIT_USER_AGENT') or os.getenv('APP_NAME') or 'signalyze-bot/0.1'
        reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
        results = []
        for kw in keywords:
            print(f"Searching Reddit for: {kw}")
            try:
                for submission in reddit.subreddit('all').search(kw, limit=args.limit):
                    try:
                        submission.comments.replace_more(limit=0)
                        for comment in submission.comments.list():
                            results.append({
                                "source": "reddit",
                                "date": datetime.utcfromtimestamp(getattr(comment, "created_utc", submission.created_utc)).isoformat(),
                                "username": str(getattr(comment, "author", "")),
                                "content": getattr(comment, "body", ""),
                                "url": f"https://reddit.com{getattr(comment, 'permalink', submission.permalink)}",
                                "engagement": getattr(comment, "score", 0)
                            })
                    except Exception:
                        continue
            except Exception as e:
                print('Search failed for', kw, e)
        # write results
        os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)
        keys = ['source','date','username','content','url','engagement']
        with open(args.out, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for r in results:
                writer.writerow(r)
        print(f"\n✅ Data saved: {args.out}")
        print(f"Total comments collected: {len(results)}")
    else:
        subreddits = [s.strip() for s in args.subs.split(",") if s.strip()]
        fetch_reddit_comments(subreddits, limit=args.limit, output_file=args.out)
