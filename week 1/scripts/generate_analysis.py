"""generate_analysis.py
Simple rule-based sentiment scoring and visualization to produce analytics similar to the screenshots.
Reads `results/combined.csv` and writes multiple outputs under `results/`.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

IN = 'results/combined.csv'
OUT_CSV = 'results/sentiment_analysis_fast.csv'

POS_WORDS = set(['love','great','good','excellent','fast','comfortable','smooth','awesome','amazing'])
NEG_WORDS = set(['poor','bad','drain','drains','slow','issue','problem','expensive','flaky','degrade','degradation'])


def score_text(t):
    t_l = t.lower()
    pos = sum(1 for w in POS_WORDS if w in t_l)
    neg = sum(1 for w in NEG_WORDS if w in t_l)
    comp = (pos - neg)
    if comp > 0:
        label = 'positive'
    elif comp < 0:
        label = 'negative'
    else:
        label = 'neutral'
    return pos, neg, comp, label


def run():
    if not os.path.exists(IN):
        raise FileNotFoundError(IN+' not found')
    df = pd.read_csv(IN)
    scored = df['content'].fillna('').apply(lambda t: score_text(t))
    df['pos_count'] = scored.apply(lambda x: x[0])
    df['neg_count'] = scored.apply(lambda x: x[1])
    df['score'] = scored.apply(lambda x: x[2])
    df['sentiment'] = scored.apply(lambda x: x[3])
    os.makedirs('results', exist_ok=True)
    df.to_csv(OUT_CSV, index=False)

    # plots
    plt.figure(figsize=(6,4))
    order = ['positive','neutral','negative']
    sns.countplot(x='sentiment', data=df, order=order)
    plt.title('Sentiment Distribution')
    plt.savefig('results/polarity_distribution.png', bbox_inches='tight')
    plt.close()

    plt.figure(figsize=(8,6))
    df['category1'].value_counts().plot(kind='barh')
    plt.title('Category1 Distribution')
    plt.savefig('results/category1_distribution.png', bbox_inches='tight')
    plt.close()

    # heatmap category1 vs category2
    ct = pd.crosstab(df['category1'], df['category2'])
    plt.figure(figsize=(8,6))
    sns.heatmap(ct, annot=True, fmt='d', cmap='Blues')
    plt.title('Category1 vs Category2')
    plt.savefig('results/category_heatmap.png', bbox_inches='tight')
    plt.close()

    top_pos = df.sort_values('score', ascending=False).head(10)
    top_neg = df.sort_values('score').head(10)
    top_pos[['content','score']].to_csv('results/top_positive_praises.csv', index=False)
    top_neg[['content','score']].to_csv('results/top_negative_issues.csv', index=False)
    print('Wrote analysis files in results/')

if __name__ == '__main__':
    run()
