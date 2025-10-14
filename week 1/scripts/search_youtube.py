"""search_youtube.py
Search YouTube for videos matching a query and print top video IDs comma-separated.
Requires YOUTUBE_API_KEY in environment.
"""
import os
from googleapiclient.discovery import build

API_KEY = os.getenv('YOUTUBE_API_KEY')
if not API_KEY:
    raise EnvironmentError('YOUTUBE_API_KEY not set')

yt = build('youtube', 'v3', developerKey=API_KEY)
query = 'Ather Rizta review'
resp = yt.search().list(part='id', q=query, type='video', maxResults=8, order='relevance').execute()
ids = [item['id']['videoId'] for item in resp.get('items', [])]
print(','.join(ids))
