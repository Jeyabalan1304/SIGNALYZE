"""Orchestrator for the pipeline. Options to collect, process, analyze, and visualize."""
import argparse
import os
from pathlib import Path

here = Path(__file__).parent
outputs = here.parent / 'outputs'
outputs.mkdir(exist_ok=True)


def main(args):
    if args.collect:
        try:
            from src.collect_reddit import collect_from_subreddits
            from src.collect_youtube import collect_comments_from_video
            print('Collecting (requires API keys)...')
            collect_from_subreddits(['ElectricScooters','scooters','electricvehicles'], limit=200)
            # collect_comments_from_video('VIDEO_ID', max_results=200)
        except Exception as e:
            print('Collect step failed or skipped:', e)
    if args.process:
        from src.process_data import process_raw_files
        raw1 = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'reddit_raw.csv')
        raw2 = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'youtube_raw.csv')
        try:
            path = process_raw_files([raw1, raw2])
            print('Processed dataset at', path)
        except Exception as e:
            print('Process step failed:', e)
    if args.analyze:
        try:
            from src.sentiment_analysis import SentimentAnalyzer
            import pandas as pd
            df = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'outputs', 'clean_dataset.csv'))
            sa = SentimentAnalyzer()
            probs, labels = sa.predict_and_label(df['content'].tolist())
            df['sentiment'] = labels
            # Save probabilities as columns
            df['prob_negative'] = probs[:,0]
            df['prob_neutral'] = probs[:,1]
            df['prob_positive'] = probs[:,2]
            df.to_csv(os.path.join(os.path.dirname(__file__), '..', 'outputs', 'clean_dataset.csv'), index=False)
            print('Analysis done and saved')
        except Exception as e:
            print('Analyze step failed:', e)
    if args.classify:
        try:
            from src.hierarchical_classifier import classify
            import pandas as pd
            df = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'outputs', 'clean_dataset.csv'))
            cats = df['content'].fillna('').apply(lambda t: classify(t))
            df['category1'] = cats.apply(lambda x: x[0])
            df['category2'] = cats.apply(lambda x: x[1])
            df['category3'] = cats.apply(lambda x: x[2])
            df.to_csv(os.path.join(os.path.dirname(__file__), '..', 'outputs', 'clean_dataset.csv'), index=False)
            print('Classification applied')
        except Exception as e:
            print('Classification step failed:', e)
    if args.visualize:
        try:
            from src.visualize import plot_sentiment_distribution, plot_category_distribution, plot_heatmap
            import pandas as pd
            df = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'outputs', 'clean_dataset.csv'))
            print('Generating visualizations...')
            print(plot_sentiment_distribution(df))
            print(plot_category_distribution(df))
            print(plot_heatmap(df))
        except Exception as e:
            print('Visualize step failed:', e)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--collect', action='store_true')
    parser.add_argument('--process', action='store_true')
    parser.add_argument('--analyze', action='store_true')
    parser.add_argument('--classify', action='store_true')
    parser.add_argument('--visualize', action='store_true')
    args = parser.parse_args()
    main(args)
