"""Show all columns and data for AU committed companies in the SBTi file."""
import pandas as pd
from pathlib import Path

DATA = Path(__file__).parent.parent.parent / 'data'
df = pd.read_excel(DATA / 'sbti_companies.xlsx')
print(f'Columns ({len(df.columns)}):')
for c in df.columns: print(f'  {c}')

au = df[df['location'].astype(str).str.upper() == 'AUSTRALIA']
committed = au[au['near_term_status'].astype(str).str.lower().str.contains('committed', na=False) &
               ~au['near_term_status'].astype(str).str.lower().str.contains('removed', na=False)]
print(f'\nAU committed: {len(committed)}')
print()
for _, row in committed.iterrows():
    print(f'Company: {row.get("company_name", row.get("name","?"))}')
    for col in df.columns:
        val = str(row[col]).strip()
        if val and val not in ('nan', 'None', ''):
            print(f'  {col}: {val[:120]}')
    print()
