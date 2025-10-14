"""classify_feedback.py
Apply a simple keyword-based hierarchical classification to `results/combined.csv` and write back the categories.
Usage: python classify_feedback.py
"""
import os
import pandas as pd

OUT = 'results/combined.csv'

KEYWORDS = {
    'Product': {
        'Battery & Range': ['battery','range','charging','charge','degrade','degradation','fast charging'],
        'Performance & Power': ['acceleration','speed','motor','power','torque'],
        'Build Quality': ['build','quality','sturdy','finish','frame']
    },
    'Software': {
        'Connectivity': ['app','bluetooth','connect','ota','update'],
        'UI': ['display','screen','dashboard','touch']
    },
    'Value & Price': {
        'Price': ['price','expensive','cheap','value']
    }
}


def classify_text(text):
    t = text.lower()
    for c1, subs in KEYWORDS.items():
        for c2, kws in subs.items():
            for kw in kws:
                if kw in t:
                    return c1, c2, kw
    return 'Other','Other',''


def apply_classification():
    if not os.path.exists(OUT):
        raise FileNotFoundError(OUT+' not found. Run combine_data.py first')
    df = pd.read_csv(OUT)
    cats = df['content'].fillna('').apply(classify_text)
    df['category1'] = cats.apply(lambda x: x[0])
    df['category2'] = cats.apply(lambda x: x[1])
    df['category3'] = cats.apply(lambda x: x[2])
    df.to_csv(OUT, index=False)
    return OUT

if __name__ == '__main__':
    print('Classifying feedback...')
    print(apply_classification())
