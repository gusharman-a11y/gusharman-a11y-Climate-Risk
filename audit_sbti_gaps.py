"""
Find SBTi AU companies in the source file that are NOT in our DB.
Shows what we're missing and why.
"""
import os, re
import pandas as pd
from pathlib import Path

for line in Path('pollination-bd-tracker/.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip())
from supabase import create_client
sb = create_client(os.environ['NEXT_PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])

_STRIP = re.compile(
    r'\b(?:pty|ltd|limited|holdings|holding|group|australia|australian|corporation|corp|inc|'
    r'plc|services|management|investments|finance|financial|partners|partnership|'
    r'trust|reit|fund|no\b|co\b|pte|the)\b', re.I
)
def nkey(n):
    n = re.sub(r'[^a-z0-9 ]', ' ', str(n).lower())
    n = _STRIP.sub('', n)
    return re.sub(r'\s+', ' ', n).strip()

# Load SBTi file
df = pd.read_excel(Path('data/sbti_companies_latest.xlsx'))
au = df[df['location'] == 'Australia'].copy()

# Exclude SMEs based on organization_type
print('Organisation types in AU SBTi file:')
print(au['organization_type'].value_counts().to_string())
print()

non_sme = au[~au['organization_type'].astype(str).str.contains('SME', case=False, na=False)]
print(f'AU total: {len(au)} | Non-SME: {len(non_sme)}')
print()

# Load all DB company nkeys
all_db = []
offset = 0
while True:
    r = sb.table('companies').select('id,name,sbti_status').range(offset, offset+999).execute()
    all_db.extend(r.data)
    if len(r.data) < 1000: break
    offset += 1000

db_nkeys = {nkey(c['name']): c for c in all_db}

def find_in_db(sbti_name):
    nk = nkey(sbti_name)
    if nk in db_nkeys: return db_nkeys[nk], 'exact'
    for length in [8, 7, 6]:
        for dk, dc in db_nkeys.items():
            if len(nk) >= length and len(dk) >= length and nk[:length] == dk[:length]:
                return dc, f'prefix-{length}'
    wa = {w for w in nk.split() if len(w) > 3}
    for dk, dc in db_nkeys.items():
        wb = {w for w in dk.split() if len(w) > 3}
        if len(wa & wb) >= 2:
            return dc, 'words'
    return None, None

print('=== NON-SME SBTi AU companies NOT in our DB ===')
missing = []
for _, row in non_sme.iterrows():
    name = str(row['company_name'])
    status = str(row.get('near_term_status') or '')
    sector = str(row.get('sector') or '')
    org_type = str(row.get('organization_type') or '')
    match, how = find_in_db(name)
    if not match:
        missing.append({'name': name, 'status': status, 'sector': sector, 'org_type': org_type})

print(f'Missing: {len(missing)} companies\n')
by_status = {}
for m in missing:
    by_status.setdefault(m['status'], []).append(m)

for status in ['Targets set', 'Committed', 'Commitment removed']:
    grp = by_status.get(status, [])
    if not grp: continue
    print(f'\n--- {status} ({len(grp)}) ---')
    for m in grp:
        print(f'  [{m["sector"][:25]:25}] {m["name"]}')
