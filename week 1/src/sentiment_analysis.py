"""Sentiment analysis using cardiffnlp/twitter-roberta-base-sentiment"""
import os
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np

MODEL_NAME = 'cardiffnlp/twitter-roberta-base-sentiment'

class SentimentAnalyzer:
    def __init__(self, model_name=MODEL_NAME, device=None):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self.labels = ['negative','neutral','positive']

    def predict(self, texts, batch_size=16):
        probs = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            enc = self.tokenizer(batch, padding=True, truncation=True, return_tensors='pt')
            enc = {k:v.to(self.device) for k,v in enc.items()}
            with torch.no_grad():
                out = self.model(**enc)
                logits = out.logits
                batch_probs = torch.softmax(logits, dim=1).cpu().numpy()
                probs.extend(batch_probs.tolist())
        return np.array(probs)

    def predict_and_label(self, texts):
        probs = self.predict(texts)
        labels = [self.labels[p.argmax()] for p in probs]
        return probs, labels

if __name__ == '__main__':
    print('Loading analyzer (this will download model weights if not present)...')
    sa = SentimentAnalyzer()
    s, l = sa.predict_and_label(['I love the Rizta, great ride!','Battery life is poor','It is okay'])
    print(l)
