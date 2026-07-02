"""
Backfill target_description, target_scope, target_year, net_zero_year
from the Net Zero Tracker snapshot.

Run: py -3 pollination-bd-tracker/scripts/backfill_nzt_targets.py
"""
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

# Load NZT — row 0 is group headers, row 1 is field names
raw = pd.read_excel(DATA / 'nzt_snapshot.xlsx', header=None)
# Row 1 contains actual column names
cols = raw.iloc[1].tolist()
df = raw.iloc[2:].copy()
df.columns = cols
df = df.reset_index(drop=True)

# Filter to Australia
au = df[(df['Country'].astype(str).str.strip() == 'AUS') & (df['Entity_type'] == 'Company')].copy()
print(f'NZT AU companies: {len(au)}')

_STRIP = re.compile(
    r'\b(?:pty|ltd|limited|holdings|holding|group|australia|australian|corporation|'
    r'corp|inc|incorporated|co|plc|pte|metals|energy|resources|services|management|'
    r'investments|finance|financial)\b', re.I
)
def nkey(n):
    n = re.sub(r'[^a-z0-9 ]', ' ', str(n).lower())
    n = _STRIP.sub('', n)
    return re.sub(r'\s+', ' ', n).strip()

def clean(v):
    s = str(v).strip()
    return None if s in ('nan', 'None', '', '-', 'N/A') else s

def safe_int(v):
    try: return int(float(str(v)))
    except: return None

def build_scope(row):
    parts = []
    if clean(row.get('Scope_1_coverage')) in ('Yes', '1'): parts.append('Scope 1')
    if clean(row.get('Scope_2_coverage')) in ('Yes', '1'): parts.append('Scope 2')
    if clean(row.get('Scope_3_coverage')) in ('Yes', '1'): parts.append('Scope 3')
    return ' + '.join(parts) if parts else None

def build_description(row):
    end_text = clean(row.get('End_target_text'))
    interim_text = clean(row.get('Interim_target_text'))
    pct = clean(row.get('End_target_percentage_reduction'))
    base_year = clean(row.get('End_target_baseline_year'))
    end_year = clean(row.get('End_target_year'))
    interim_pct = clean(row.get('Interim_target_percentage_reduction'))
    interim_year = clean(row.get('Interim_target_year'))

    parts = []
    if end_text:
        parts.append(end_text)
    elif pct and end_year:
        base = f' vs {base_year} baseline' if base_year else ''
        parts.append(f'{pct}% reduction by {end_year}{base}')

    if interim_text and interim_text != end_text:
        parts.append(f'Interim: {interim_text}')
    elif interim_pct and interim_year:
        parts.append(f'Interim: {interim_pct}% reduction by {interim_year}')

    return ' | '.join(parts)[:1000] if parts else None

# Load DB
print('Loading DB companies...')
all_db = []
offset = 0
while True:
    r = sb.table('companies').select('id,name').range(offset, offset+999).execute()
    all_db.extend(r.data)
    if len(r.data) < 1000: break
    offset += 1000
print(f'DB companies: {len(all_db)}')

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

updated = 0
unmatched = []

for _, row in au.iterrows():
    name = clean(row.get('Name'))
    if not name: continue

    desc = build_description(row)
    scope = build_scope(row)
    end_year = safe_int(row.get('End_target_year'))
    target_class = clean(row.get('End_target'))
    pct = clean(row.get('End_target_percentage_reduction'))
    published_plan = clean(row.get('Published_plan'))
    race_to_zero = clean(row.get('Race_to_zero_member'))

    company = find_company(name)
    if company:
        patch = {}
        if desc: patch['target_description'] = desc
        if scope: patch['target_scope'] = scope
        if end_year and 2020 < end_year < 2080: patch['net_zero_year'] = end_year
        if target_class: patch['target_classification'] = target_class
        if published_plan: patch['nzt_published_plan'] = published_plan in ('Yes', '1', 'True')
        if race_to_zero: patch['nzt_race_to_zero'] = race_to_zero in ('Yes', '1', 'True')

        if patch:
            sb.table('companies').update(patch).eq('id', company['id']).execute()
            updated += 1
            if updated <= 8:
                print(f'  {name[:40]:42} -> {desc[:70] if desc else "(no desc)"}')
    else:
        unmatched.append(name)

print(f'\nUpdated: {updated} companies')
print(f'Unmatched: {len(unmatched)}')
if unmatched:
    print('Unmatched NZT companies:')
    for n in unmatched:
        print(f'  {n}')
