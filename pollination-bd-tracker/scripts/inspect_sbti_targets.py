"""Inspect SBTi targets file for AU companies."""
import pandas as pd
from pathlib import Path

DATA = Path(__file__).parent.parent.parent / 'data'
df_t = pd.read_excel(DATA / 'sbti_targets.xlsx')
au = df_t[df_t['location'].astype(str).str.upper() == 'AUSTRALIA']

def clean(v):
    s = str(v).strip()
    return None if s in ('nan', 'None', 'NaT', '', '-') else s

# Show committed companies
committed = au[au['status'].astype(str).str.lower() == 'active']
validated = au[au['status'].astype(str).str.lower() != 'active']

print(f'AU active (committed): {len(committed)}')
print(f'AU other (validated/removed): {len(validated)}')
print(f'\nStatus values: {au["status"].unique()}')
print(f'Action values: {au["action"].unique()}')
print()

# Show a few validated targets with full detail
targets_set = au[au['action'].astype(str).str.lower().str.contains('target', na=False)]
print(f'AU validated targets: {len(targets_set)}')
print('\nSample validated target:')
for _, row in targets_set.head(2).iterrows():
    for col in df_t.columns:
        val = clean(row[col])
        if val:
            print(f'  {col}: {val[:120]}')
    print()

# Show committed targets
print('Sample committed entry:')
for _, row in committed.head(2).iterrows():
    for col in df_t.columns:
        val = clean(row[col])
        if val:
            print(f'  {col}: {val[:120]}')
    print()
