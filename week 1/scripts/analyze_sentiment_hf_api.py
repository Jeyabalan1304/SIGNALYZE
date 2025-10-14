"""analyze_sentiment_hf_api.py
Use the Hugging Face Inference API to run sentiment (DistilBERT SST-2)
and zero-shot classification (BART-MNLI) on a CSV with `content`.

Requires: requests, pandas

Usage:
  # set HF_API_TOKEN environment variable OR pass --token
  python scripts\analyze_sentiment_hf_api.py --in results/combined_ather.csv --out results/combined_ather_with_models_api.csv

Notes:
 - This avoids installing local torch. It uses the Hugging Face Inference API and requires a valid HF API token.
 - Rate limits and latency depend on HF service plan.
"""
import os
import time
import argparse
import json
import requests
import pandas as pd
from tqdm import tqdm


# Use a RoBERTa sentiment model (CardiffNLP) via the HF Inference API
HF_SENT_MODEL = 'cardiffnlp/twitter-roberta-base-sentiment'
HF_ZS_MODEL = 'facebook/bart-large-mnli'
API_URL = 'https://api-inference.huggingface.co/models/'


def hf_request(model: str, payload: dict, token: str, max_retries=3, backoff=1.0):
    url = API_URL + model
    headers = { 'Authorization': f'Bearer {token}' }
    for attempt in range(max_retries):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            if resp.status_code == 200:
                return resp.json()
            # 429 or 503 might be transient
            if resp.status_code in (429, 502, 503, 504):
                time.sleep(backoff * (2 ** attempt))
                continue
            # other errors - raise with message
            raise RuntimeError(f'HF API error {resp.status_code}: {resp.text}')
        except requests.RequestException as e:
            time.sleep(backoff * (2 ** attempt))
            last_exc = e
    raise last_exc


def annotate(in_path, out_path, token=None, batch_size=8, labels=None):
    if token is None:
        raise RuntimeError('HF API token required (set HF_API_TOKEN env or pass --token)')
    if not os.path.exists(in_path):
        raise FileNotFoundError(in_path + ' not found')

    df = pd.read_csv(in_path)
    texts = df['content'].fillna('').astype(str).tolist()

    if labels is None:
        labels = ['Product','Software','Battery & Range','Performance & Power','Value & Price','Build Quality','Service','Other']

    sent_labels = []
    sent_scores = []
    zs_labels = []
    zs_scores = []

    for i in tqdm(range(0, len(texts), batch_size), desc='Batches'):
        batch = texts[i:i+batch_size]

        # sentiment
        # sentiment: call model per text (API models vary in label naming; map LABEL_* if present)
        for text in batch:
            payload = { 'inputs': text }
            out = hf_request(HF_SENT_MODEL, payload, token)
            # CardifflNLP RoBERTa may return [{'label':'LABEL_0','score':...}, ...]
            if isinstance(out, list) and out:
                lbl = out[0].get('label','')
                score = out[0].get('score', 0.0)
                # map LABEL_* to readable labels where applicable
                if isinstance(lbl, str) and lbl.startswith('LABEL_'):
                    label_map = {'LABEL_0':'negative','LABEL_1':'neutral','LABEL_2':'positive'}
                    lbl = label_map.get(lbl, lbl)
                sent_labels.append(lbl)
                sent_scores.append(score)
            else:
                sent_labels.append('')
                sent_scores.append(0.0)

        # zero-shot for the batch: use multi inputs to reduce calls
        for text in batch:
            payload = { 'inputs': text, 'parameters': { 'candidate_labels': labels } }
            out = hf_request(HF_ZS_MODEL, payload, token)
            # expected format: {'labels': [...], 'scores': [...]}
            if isinstance(out, dict) and out.get('labels'):
                zs_labels.append(out['labels'][0])
                zs_scores.append(out['scores'][0])
            else:
                zs_labels.append('')
                zs_scores.append(0.0)

    df['sentiment_hf'] = [l.lower() if isinstance(l,str) else '' for l in sent_labels]
    df['sentiment_hf_confidence'] = sent_scores
    df['category1_zs'] = zs_labels
    df['category1_zs_confidence'] = zs_scores

    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    df.to_csv(out_path, index=False, encoding='utf-8')
    return out_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--in', dest='in_path', default='results/combined_ather.csv')
    parser.add_argument('--out', dest='out_path', default='results/combined_ather_with_models_api.csv')
    parser.add_argument('--batch', dest='batch_size', type=int, default=8)
    parser.add_argument('--token', dest='token', default=None)
    args = parser.parse_args()
    token = args.token or os.environ.get('HF_API_TOKEN') or os.environ.get('HUGGINGFACE_API_TOKEN')
    print('Using HF API token from argument/env:', 'yes' if token else 'NO')
    out = annotate(args.in_path, args.out_path, token=token, batch_size=args.batch_size)
    print('Wrote', out)


if __name__ == '__main__':
    main()
