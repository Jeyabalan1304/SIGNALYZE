import pandas as pd
import re

in_path = r"results/combined.csv"
out_path = r"results/combined_ather.csv"

df = pd.read_csv(in_path)

# pattern to match ather, rizta and common misspellings
pattern = re.compile(r"\b(ather|rizta|ritza|rizta|rista|rizta|riza|rizta)\b", flags=re.I)

mask = df['content'].astype(str).apply(lambda s: bool(pattern.search(s)))
filtered = df[mask].copy()
filtered.to_csv(out_path, index=False, encoding='utf-8')

print(f"Read {len(df)} rows from {in_path}")
print(f"Found {len(filtered)} rows mentioning Ather/Rizta -> wrote {out_path}")
