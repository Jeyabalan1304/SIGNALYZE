"""Keyword-based hierarchical classifier."""
from collections import OrderedDict

# Define keywords for category mapping. These are minimal examples and can be extended.
CATEGORY_KEYWORDS = {
    'Product': {
        'Battery & Range': ['battery','range','km','charge','charging','degradation'],
        'Performance & Power': ['motor','power','acceleration','top speed','torque'],
        'Build Quality': ['build','finish','fit','frame','quality','sturdy'],
    },
    'Technology & Software': {
        'Infotainment & UI': ['display','screen','dashboard','ui','touchscreen'],
        'Connectivity': ['app','bluetooth','ota','software update','connect'],
    },
    'Value & Price': {
        'Price': ['price','cost','expensive','affordable','value'],
        'Incentives': ['discount','offer','subsidy']
    },
    'Customer Service': {
        'Service Experience': ['service','support','dealer','warranty']
    },
    'User Experience': {
        'Comfort': ['seat','comfort','ride comfort'],
        'Noise & Vibration': ['noise','vibration','rattle']
    }
}


def classify(text):
    text_l = text.lower()
    cat1 = 'Other'
    cat2 = 'Other'
    cat3 = ''
    for c1, sub in CATEGORY_KEYWORDS.items():
        for c2, kws in sub.items():
            for kw in kws:
                if kw in text_l:
                    cat1 = c1
                    cat2 = c2
                    cat3 = kw
                    return cat1, cat2, cat3
    return cat1, cat2, cat3

if __name__ == '__main__':
    examples = ['Battery degrades quickly after 6 months', 'App update broke connectivity','Very comfortable seat']
    for e in examples:
        print(e, '->', classify(e))
