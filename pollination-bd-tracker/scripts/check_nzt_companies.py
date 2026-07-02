import pandas as pd
raw = pd.read_excel('data/nzt_snapshot.xlsx', header=None)
cols = raw.iloc[1].tolist()
df = raw.iloc[2:].copy()
df.columns = cols
df = df.reset_index(drop=True)
au_companies = df[(df['Country'].astype(str).str.strip() == 'AUS') & (df['Entity_type'] == 'Company')]
print(f'AU companies in NZT: {len(au_companies)}')
print()
for _, r in au_companies.iterrows():
    name = str(r['Name'])[:50]
    target = str(r['End_target'])[:30]
    year = str(r['End_target_year'])
    pct = str(r['End_target_percentage_reduction'])
    text = str(r['End_target_text'])[:80]
    print(f'{name:52} | {target:32} | yr={year} | {pct}% | {text}')
