"""
Ingest CER NGER 2024-25 data into the BD tracker database.
Downloads:
  - Corporate emissions (scope 1/2 per controlling corporation)
  - Safeguard responsible emitters register (ABN bridge)
  - Safeguard baselines and emissions table (compliance data)

Run: py -3 pollination-bd-tracker/scripts/ingest_cer_nger.py
"""
import os, re, io
from pathlib import Path
import requests
import pandas as pd

ROOT = Path(__file__).parent.parent
for line in (ROOT / '.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1); os.environ.setdefault(k.strip(), v.strip())

from supabase import create_client
sb = create_client(os.environ['NEXT_PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])

HEADERS = {'User-Agent': 'Mozilla/5.0 (BD-Tracker/1.0; research use)'}

CER_URLS = {
    'nger_corporate': 'https://cer.gov.au/document/greenhouse-and-energy-information-registered-corporation-2024-25-0',
    'safeguard_emitters': 'https://cer.gov.au/document/national-greenhouse-and-energy-register-responsible-emitters-2024-25-0',
    'safeguard_baselines': 'https://cer.gov.au/document/baselines-and-emissions-table-2024-25',
}

def fetch_csv(url):
    print(f'  Fetching {url[:80]}...')
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    # Try to detect encoding
    content = r.content
    try:
        return pd.read_csv(io.BytesIO(content), encoding='utf-8-sig', thousands=',')
    except Exception:
        return pd.read_csv(io.BytesIO(content), encoding='latin-1', thousands=',')

def normalise_name(n):
    n = re.sub(r'[^a-z0-9 ]', ' ', str(n).lower())
    stopwords = r'\b(?:pty|ltd|limited|holdings|holding|group|australia|australian|corporation|corp|inc|incorporated|co|plc|pte|metals|energy|resources|services)\b'
    n = re.sub(stopwords, '', n)
    return re.sub(r'\s+', ' ', n).strip()

def normalise_abn(abn):
    if not abn or pd.isna(abn): return None
    return re.sub(r'\D', '', str(abn)).zfill(11)

print('=== CER NGER Ingest 2024-25 ===\n')

# 1. Download NGER corporate emissions
print('1. Fetching NGER corporate emissions...')
try:
    nger = fetch_csv(CER_URLS['nger_corporate'])
    print(f'   Rows: {len(nger)}, Columns: {list(nger.columns)}')
    nger.to_csv(ROOT.parent / 'data' / 'cer_nger_2024_25.csv', index=False)
    print('   Saved to data/cer_nger_2024_25.csv')
except Exception as e:
    print(f'   ERROR: {e}')
    nger = None

# 2. Download Safeguard responsible emitters (ABN bridge)
print('\n2. Fetching Safeguard responsible emitters register...')
try:
    safeguard_emitters = fetch_csv(CER_URLS['safeguard_emitters'])
    print(f'   Rows: {len(safeguard_emitters)}, Columns: {list(safeguard_emitters.columns)}')
    safeguard_emitters.to_csv(ROOT.parent / 'data' / 'cer_safeguard_emitters_2024_25.csv', index=False)
except Exception as e:
    print(f'   ERROR: {e}')
    safeguard_emitters = None

# 3. Download Safeguard baselines and emissions
print('\n3. Fetching Safeguard baselines and emissions table...')
try:
    safeguard_baselines = fetch_csv(CER_URLS['safeguard_baselines'])
    print(f'   Rows: {len(safeguard_baselines)}, Columns: {list(safeguard_baselines.columns)}')
    safeguard_baselines.to_csv(ROOT.parent / 'data' / 'cer_safeguard_baselines_2024_25.csv', index=False)
except Exception as e:
    print(f'   ERROR: {e}')
    safeguard_baselines = None

# 4. Load DB companies
print('\n4. Loading DB companies...')
all_db = []
offset = 0
while True:
    r = sb.table('companies').select('id,name,abn,asx_code,nger_scope1_tco2e').range(offset, offset+999).execute()
    all_db.extend(r.data)
    if len(r.data) < 1000: break
    offset += 1000
print(f'   DB companies: {len(all_db)}')

# Build lookup maps
db_by_abn = {normalise_abn(c['abn']): c for c in all_db if c.get('abn')}
db_by_name = {normalise_name(c['name']): c for c in all_db}

def find_company(name, abn=None):
    # Try ABN first
    if abn:
        norm_abn = normalise_abn(abn)
        if norm_abn and norm_abn in db_by_abn:
            return db_by_abn[norm_abn]
    # Try exact normalised name
    nk = normalise_name(name)
    if nk in db_by_name:
        return db_by_name[nk]
    # Try prefix match (first 8 chars)
    prefix = nk[:8]
    for db_nk, c in db_by_name.items():
        if len(prefix) >= 6 and (db_nk.startswith(prefix) or nk.startswith(db_nk[:8])):
            return c
    return None

# 5. Match and update NGER emissions
print('\n5. Matching NGER corporate emissions to DB...')
updates = 0
unmatched = []

if nger is not None:
    # Identify columns (CER CSV column names may vary slightly)
    name_col = next((c for c in nger.columns if 'organisation' in c.lower() or 'name' in c.lower()), nger.columns[0])
    abn_col = next((c for c in nger.columns if 'abn' in c.lower() or 'identifying' in c.lower()), None)
    s1_col = next((c for c in nger.columns if 'scope 1' in c.lower()), None)
    s2_col = next((c for c in nger.columns if 'scope 2' in c.lower()), None)

    print(f'   Name col: {name_col}, ABN col: {abn_col}, S1 col: {s1_col}, S2 col: {s2_col}')

    for _, row in nger.iterrows():
        name = str(row.get(name_col, '')).strip()
        if not name or name.lower() == 'nan': continue

        abn = str(row.get(abn_col, '')) if abn_col else None

        try:
            s1 = float(str(row.get(s1_col, '') or '').replace(',', '')) if s1_col else None
        except (ValueError, TypeError):
            s1 = None
        try:
            s2 = float(str(row.get(s2_col, '') or '').replace(',', '')) if s2_col else None
        except (ValueError, TypeError):
            s2 = None

        company = find_company(name, abn)
        if company:
            patch = {'nger_year': '2024-25'}
            if s1 and s1 > 0: patch['nger_scope1_tco2e'] = s1
            if s2 and s2 > 0: patch['nger_scope2_tco2e'] = s2
            if abn: patch['abn'] = normalise_abn(abn)
            sb.table('companies').update(patch).eq('id', company['id']).execute()
            updates += 1
            if updates <= 5:
                print(f'   Matched: {name[:45]:47} -> {company["name"][:35]} | S1={s1:,.0f}' if s1 else f'   Matched: {name[:45]:47} -> {company["name"][:35]}')
        else:
            unmatched.append({'name': name, 'abn': abn, 's1': s1})

print(f'\n   Updated: {updates} companies with NGER 2024-25 data')
print(f'   Unmatched: {len(unmatched)} CER companies not in DB')

# Show top unmatched (potential new companies to add)
if unmatched:
    unmatched_sorted = sorted([u for u in unmatched if u.get('s1')], key=lambda x: x['s1'] or 0, reverse=True)
    print('\n   Top unmatched by scope 1 (candidates to add to DB):')
    for u in unmatched_sorted[:15]:
        print(f'     {u["name"][:50]:52} ABN={u["abn"] or "?":12} S1={u["s1"]:>12,.0f} tCO2e')

# 6. Match Safeguard data
print('\n6. Matching Safeguard covered facilities...')
safeguard_updates = 0

if safeguard_baselines is not None:
    emitter_col = next((c for c in safeguard_baselines.columns if 'emitter' in c.lower() or 'responsible' in c.lower() or 'operator' in c.lower()), safeguard_baselines.columns[0])
    baseline_col = next((c for c in safeguard_baselines.columns if 'baseline' in c.lower()), None)
    actual_col = next((c for c in safeguard_baselines.columns if 'actual' in c.lower() or 'covered emissions' in c.lower()), None)

    print(f'   Emitter col: {emitter_col}, Baseline col: {baseline_col}, Actual col: {actual_col}')

    seen = set()
    for _, row in safeguard_baselines.iterrows():
        emitter = str(row.get(emitter_col, '')).strip()
        if not emitter or emitter.lower() == 'nan' or emitter in seen: continue
        seen.add(emitter)

        try:
            baseline = float(str(row.get(baseline_col, '') or '').replace(',', '')) if baseline_col else None
        except (ValueError, TypeError):
            baseline = None

        company = find_company(emitter)
        if company:
            patch = {'safeguard_covered': True}
            if baseline and baseline > 0: patch['safeguard_baseline'] = baseline
            sb.table('companies').update(patch).eq('id', company['id']).execute()
            safeguard_updates += 1

print(f'   Marked {safeguard_updates} companies as Safeguard covered')

print('\n=== Done! ===')
print('Next: run enrich_database.py to rescore with updated NGER data')
