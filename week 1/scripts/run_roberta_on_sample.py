import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

MODEL = 'cardiffnlp/twitter-roberta-base-sentiment'

def main():
    df = pd.read_csv('results/sample_500.csv')
    texts = df['content'].astype(str).tolist()

    print('Loading tokenizer and model...')
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL)
    model.eval()

    labels_map = {0:'negative',1:'neutral',2:'positive'}
    batch_size = 8
    preds = []
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            enc = tokenizer(batch, padding=True, truncation=True, max_length=512, return_tensors='pt')
            out = model(**enc)
            probs = torch.softmax(out.logits, dim=1).cpu().numpy()
            batch_labels = [labels_map[p.argmax()] for p in probs]
            preds.extend(batch_labels)

    df['roberta_label'] = preds
    df.to_csv('results/sample_500_with_roberta.csv', index=False)
    print('Wrote results/sample_500_with_roberta.csv')

if __name__ == '__main__':
    main()
