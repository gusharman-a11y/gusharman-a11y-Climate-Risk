"""Revert bad NZT matches — clears target_description/scope/net_zero_year
for government/city entities that were incorrectly matched to companies."""
import os, re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent.parent
DATA = ROOT.parent / 'data'
for line in (ROOT / '.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1); os.environ.setdefault(k.strip(), v.strip())
from supabase import create_client
sb = create_client(os.environ['NEXT_PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])

_STRIP = re.compile(r'\b(?:pty|ltd|limited|holdings|group|australia|australian|corporation|corp)\b', re.I)
def nkey(n):
    n = re.sub(r'[^a-z0-9 ]', ' ', str(n).lower())
    n = _STRIP.sub('', n)
    return re.sub(r'\s+', ' ', n).strip()

raw = pd.read_excel(DATA / 'nzt_snapshot.xlsx', header=None)
cols = raw.iloc[1].tolist()
df = raw.iloc[2:].copy()
df.columns = cols
df = df.reset_index(drop=True)

# Get the bad entities (non-company AU entries)
bad = df[(df['Country'].astype(str).str.strip() == 'AUS') & (df['Entity_type'] != 'Company')]
print(f'Bad entries to revert: {len(bad)}')

all_db = []
offset = 0
while True:
    r = sb.table('companies').select('id,name').range(offset, offset+999).execute()
    all_db.extend(r.data)
    if len(r.data) < 1000: break
    offset += 1000

by_name = {nkey(c['name']): c for c in all_db}

def find_company(name):
    nk = nkey(str(name))
    if nk in by_name: return by_name[nk]
    prefix = nk[:8]
    if len(prefix) >= 6:
        for db_nk, c in by_name.items():
            if db_nk.startswith(prefix) or nk.startswith(db_nk[:min(8,len(db_nk))]):
                return c
    return None

reverted = 0
for _, row in bad.iterrows():
    name = str(row.get('Name', '')).strip()
    company = find_company(name)
    if company:
        sb.table('companies').update({
            'target_description': None,
            'target_scope': None,
            'net_zero_year': None,
            'nzt_published_plan': None,
            'nzt_race_to_zero': None,
        }).eq('id', company['id']).execute()
        reverted += 1
        print(f'  Reverted: {name} -> {company["name"]}')

print(f'\nReverted {reverted} bad matches')
