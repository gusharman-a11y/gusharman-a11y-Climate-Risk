import pandas as pd
from collections import Counter
from pathlib import Path

df = pd.read_excel(Path(__file__).parent.parent.parent / 'data' / 'sbti_companies.xlsx')
au = df[df['location'] == 'Australia']
print(f'Total AU companies: {len(au)}')

print('\nStatus breakdown:')
for k,v in sorted(Counter(au['near_term_status'].fillna('Unknown')).items(), key=lambda x:-x[1]):
    print(f'  {k}: {v}')

print('\nAll AU companies with Targets set:')
validated = au[au['near_term_status'] == 'Targets set'].sort_values('company_name')
for _, r in validated.iterrows():
    name = str(r['company_name'])[:50]
    cls = str(r['near_term_target_classification'])[:25]
    sector = str(r['sector'])[:30]
    print(f'  {name:52} | {cls:27} | {sector}')

print(f'\nTotal validated: {len(validated)}')

print('\nCommitted (not yet validated):')
committed = au[au['near_term_status'] == 'Committed'].sort_values('company_name')
for _, r in committed.iterrows():
    print(f'  {str(r["company_name"])[:50]}')
