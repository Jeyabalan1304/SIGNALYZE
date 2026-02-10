import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

def fetch_youtube_comments(video_id: str):
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("YOUTUBE_API_KEY not found in .env")
        return []

    youtube = build('youtube', 'v3', developerKey=api_key)

    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100
        )
        response = request.execute()
        
        comments = []
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)
        return comments
    except Exception as e:
        print(f"Error fetching YouTube comments: {e}")
        return []

if __name__ == "__main__":
    # Example usage
    # comments = fetch_youtube_comments("VIDEO_ID")
    # print(comments)
    pass
