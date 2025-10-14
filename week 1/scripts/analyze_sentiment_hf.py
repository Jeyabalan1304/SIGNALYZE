"""analyze_sentiment_hf.py
Run sentiment (DistilBERT SST-2) and zero-shot Category1 (BART-MNLI) on a CSV with `content` column.
Writes probability/label columns and saves to output CSV.
Requires: transformers, torch
Usage:
    python scripts\analyze_sentiment_hf.py --in results/combined.csv --out results/combined_with_models.csv
"""
import argparse
import os
import pandas as pd

try:
    import torch
    from transformers import pipeline
except Exception:
    torch = None


SENT_MODEL = 'distilbert-base-uncased-finetuned-sst-2-english'
ZS_MODEL = 'facebook/bart-large-mnli'


def annotate(in_path, out_path, batch_size=32, device=None, labels=None):
    if torch is None:
        raise RuntimeError('transformers/torch not installed. pip install transformers torch')
    if not os.path.exists(in_path):
        raise FileNotFoundError(in_path + ' not found')

    df = pd.read_csv(in_path)
    texts = df['content'].fillna('').astype(str).tolist()

    # sentiment classifier (distilbert sst2)
    sentiment = pipeline('sentiment-analysis', model=SENT_MODEL, device=device)

    # zero-shot classifier for Category1 (broad area)
    if labels is None:
        labels = [
            'Product', 'Software', 'Battery & Range', 'Performance & Power',
            'Value & Price', 'Build Quality', 'Service', 'Other'
        ]
    zsc = pipeline('zero-shot-classification', model=ZS_MODEL, device=device)

    all_sent = []
    all_sent_label = []
    all_zs_label = []
    all_zs_scores = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        # sentiment
        sent_out = sentiment(batch)
        for so in sent_out:
            label = so['label'].lower()
            score = so['score']
            # distilbert labels are POSITIVE/NEGATIVE
            all_sent_label.append(label)
            all_sent.append(score)
        # zero-shot - we use multi-label=False (single best) with candidate labels
        zs_out = zsc(batch, candidate_labels=labels)
        # if single item, pipeline returns dict not list
        if isinstance(zs_out, dict):
            zs_out = [zs_out]
        for z in zs_out:
            all_zs_label.append(z['labels'][0])
            all_zs_scores.append(z['scores'][0])

    df['sentiment_hf'] = all_sent_label
    df['sentiment_hf_confidence'] = all_sent
    df['category1_zs'] = all_zs_label
    df['category1_zs_confidence'] = all_zs_scores

    df.to_csv(out_path, index=False, encoding='utf-8')
    return out_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--in', dest='in_path', default='results/combined.csv')
    parser.add_argument('--out', dest='out_path', default='results/combined_with_models.csv')
    parser.add_argument('--batch', dest='batch_size', type=int, default=32)
    parser.add_argument('--device', dest='device', type=int, default=None,
                        help='CUDA device id or leave empty for CPU (use -1 for CPU)')
    args = parser.parse_args()
    device = args.device if args.device is not None and args.device >= 0 else -1
    print('Annotating', args.in_path, '->', args.out_path)
    print('Device:', device)
    out = annotate(args.in_path, args.out_path, batch_size=args.batch_size, device=device)
    print('Wrote', out)
