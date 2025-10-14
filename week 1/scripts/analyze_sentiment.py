"""analyze_sentiment.py
Run sentiment analysis on `results/combined.csv` using cardiffnlp/twitter-roberta-base-sentiment and save probability columns and labels.
Requires: transformers, torch
Usage: python analyze_sentiment.py
"""
import os
import pandas as pd
import numpy as np

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
except Exception:
    torch = None

MODEL_NAME = 'cardiffnlp/twitter-roberta-base-sentiment'
OUT = 'results/combined.csv'


def load_model():
    if torch is None:
        raise RuntimeError('transformers/torch not installed. Install with pip install transformers torch')
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    return tokenizer, model


def analyze():
    if not os.path.exists(OUT):
        raise FileNotFoundError(OUT+' not found. Run combine_data.py first')
    df = pd.read_csv(OUT)
    texts = df['content'].fillna('').astype(str).tolist()
    tokenizer, model = load_model()
    model.eval()
    probs = []
    batch = []
    for i, t in enumerate(texts):
        batch.append(t)
        if len(batch) >= 16 or i == len(texts)-1:
            enc = tokenizer(batch, padding=True, truncation=True, return_tensors='pt')
            with torch.no_grad():
                out = model(**enc)
                p = torch.softmax(out.logits, dim=1).numpy()
                probs.extend(p.tolist())
            batch = []
    probs = np.array(probs)
    df['prob_negative'] = probs[:,0]
    df['prob_neutral'] = probs[:,1]
    df['prob_positive'] = probs[:,2]
    df['sentiment'] = np.array(['negative','neutral','positive'])[probs.argmax(axis=1)]
    df.to_csv(OUT, index=False)
    return OUT

if __name__ == '__main__':
    print('Running sentiment analysis...')
    print(analyze())
