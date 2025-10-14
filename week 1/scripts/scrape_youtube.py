"""scrape_youtube.py
Collect YouTube comments from provided video IDs using google-api-python-client and save to a CSV in `data/`.
Usage:
  python scrape_youtube.py --videos VIDEO_ID1,VIDEO_ID2 --max 200
Requires environment variable: YOUTUBE_API_KEY
"""
import os
import csv
import argparse

try:
    from googleapiclient.discovery import build
except Exception:
    build = None


def collect_video_comments(video_id, max_results=200):
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        raise EnvironmentError('Set YOUTUBE_API_KEY in your environment')
    if build is None:
        raise RuntimeError('google-api-python-client not installed. Install with `pip install google-api-python-client`.')
    youtube = build('youtube', 'v3', developerKey=api_key)
    rows = []
    request = youtube.commentThreads().list(part='snippet', videoId=video_id, maxResults=100, textFormat='plainText')
    while request and len(rows) < max_results:
        resp = request.execute()
        for item in resp.get('items', []):
            s = item['snippet']['topLevelComment']['snippet']
            rows.append({
                'source': 'youtube',
                'date': s.get('publishedAt'),
                'username': s.get('authorDisplayName'),
                'content': s.get('textDisplay'),
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'engagement': s.get('likeCount', 0)
            })
        request = youtube.commentThreads().list_next(request, resp)
    return rows


def collect_multiple(video_ids, max_per_video=200, out_path='data/youtube_raw.csv'):
    all_rows = []
    for vid in [v.strip() for v in video_ids.split(',') if v.strip()]:
        print('Collecting', vid)
        rows = collect_video_comments(vid, max_results=max_per_video)
        all_rows.extend(rows)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    keys = ['source','date','username','content','url','engagement']
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in all_rows:
            writer.writerow(r)
    return out_path

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--videos', required=True)
    parser.add_argument('--max', type=int, default=200)
    parser.add_argument('--out', default='data/youtube_raw.csv')
    args = parser.parse_args()
    out = collect_multiple(args.videos, max_per_video=args.max, out_path=args.out)
    print('Saved', out)
