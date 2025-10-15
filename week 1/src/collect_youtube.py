"""Collect YouTube comments using google-api-python-client. Requires environment variable: YOUTUBE_API_KEY"""
import os
import csv
from datetime import datetime
from googleapiclient.discovery import build

OUTPUT_CSV = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'youtube_raw.csv')


def collect_comments_from_video(video_id, max_results=200):
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        raise EnvironmentError('YOUTUBE_API_KEY must be set')
    youtube = build('youtube', 'v3', developerKey=api_key)
    rows = []
    request = youtube.commentThreads().list(part='snippet', videoId=video_id, maxResults=100, textFormat='plainText')
    while request:
        resp = request.execute()
        for item in resp.get('items', []):
            snippet = item['snippet']['topLevelComment']['snippet']
            rows.append({
                'source': 'youtube',
                'date': snippet.get('publishedAt'),
                'username': snippet.get('authorDisplayName'),
                'content': snippet.get('textDisplay'),
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'likeCount': snippet.get('likeCount', 0)
            })
        request = youtube.commentThreads().list_next(request, resp)
        if len(rows) >= max_results:
            break
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    keys = ['source','date','username','content','url','likeCount']
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    return OUTPUT_CSV

if __name__ == '__main__':
    # Example video id placeholder
    vid = 'VIDEO_ID'
    print('Collecting youtube comments...')
    path = collect_comments_from_video(vid, max_results=200)
    print('Saved to', path)
