"""Generate visualizations: sentiment distributions, category distributions, heatmaps."""
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs')


def plot_sentiment_distribution(df):
    plt.figure(figsize=(6,4))
    sns.countplot(x='sentiment', data=df, order=['positive','neutral','negative'])
    plt.title('Sentiment Distribution')
    path = os.path.join(OUTPUT_DIR, 'sentiment_distribution.png')
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    return path


def plot_category_distribution(df):
    plt.figure(figsize=(8,6))
    sns.countplot(y='category1', data=df, order=df['category1'].value_counts().index)
    plt.title('Category1 Distribution')
    path = os.path.join(OUTPUT_DIR, 'category1_distribution.png')
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    return path


def plot_heatmap(df):
    # simple crosstab heatmap between category1 and category2
    ct = pd.crosstab(df['category1'], df['category2'])
    plt.figure(figsize=(10,6))
    sns.heatmap(ct, annot=True, fmt='d', cmap='Blues')
    path = os.path.join(OUTPUT_DIR, 'category_heatmap.png')
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    return path

if __name__ == '__main__':
    sample = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'clean_dataset.csv')
    if os.path.exists(sample):
        df = pd.read_csv(sample)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        print('Generating plots...')
        print(plot_sentiment_distribution(df))
        print(plot_category_distribution(df))
        print(plot_heatmap(df))
    else:
        print('No clean dataset found to visualize.')
