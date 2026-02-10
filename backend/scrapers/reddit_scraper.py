import os
import praw
from dotenv import load_dotenv

load_dotenv()

def fetch_reddit_comments(subreddit_name: str, limit: int = 100):
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT", "Signalyze v1.0")

    if not all([client_id, client_secret]):
        print("Reddit API credentials missing")
        return []

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )

    try:
        subreddit = reddit.subreddit(subreddit_name)
        comments = []
        for comment in subreddit.comments(limit=limit):
            comments.append(comment.body)
        return comments
    except Exception as e:
        print(f"Error fetching Reddit comments: {e}")
        return []

if __name__ == "__main__":
    # Example usage
    # comments = fetch_reddit_comments("atherenergy")
    # print(comments)
    pass
