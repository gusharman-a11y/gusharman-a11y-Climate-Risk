"""
Insert the 50 non-SME SBTi AU companies missing from our DB.
Also fixes the NIB name mismatch.
Run: py -3 insert_missing_sbti.py
"""
import os, re, json
import pandas as pd
from pathlib import Path

ROOT = Path('pollination-bd-tracker')
for line in (ROOT / '.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip())
from supabase import create_client
sb = create_client(os.environ['NEXT_PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])

cfg = json.loads((ROOT / 'scoring.config.json').read_text())

_STRIP = re.compile(
    r'\b(?:pty|ltd|limited|holdings|holding|group|australia|australian|corporation|corp|inc|'
    r'plc|services|management|investments|finance|financial|partners|partnership|'
    r'trust|reit|fund|no\b|co\b|pte|the)\b', re.I
)
def nkey(n):
    n = re.sub(r'[^a-z0-9 ]', ' ', str(n).lower())
    n = _STRIP.sub('', n)
    return re.sub(r'\s+', ' ', n).strip()

SECTOR_MAP = {
    'Financial Services': 'Financials',
    'Banks, Diverse Financials and Capital Markets': 'Financials',
    'Banks, Diverse Financials': 'Financials',
    'Professional Services': 'Industrials',
    'Technology Hardware and Equipment': 'Information Technology',
    'Software and Services': 'Information Technology',
    'Construction': 'Industrials',
    'Ground Transportation - Trucks, Trains, Ships': 'Industrials',
    'Trading Companies and Distributors': 'Industrials',
    'Solid Waste Management Utilities': 'Utilities',
    'Water Utilities': 'Utilities',
    'Electric Utilities': 'Utilities',
    'Real Estate': 'Real Estate',
    'Healthcare Providers and Services': 'Health Care',
    'Pharmaceuticals, Biotechnology and Life Sciences': 'Health Care',
    'Food and Beverage Processing': 'Consumer Staples',
    'Food Production - Animal': 'Consumer Staples',
    'Food and Staples Retailing': 'Consumer Staples',
    'Forest and Paper Products': 'Materials',
    'Containers and Packaging': 'Materials',
    'Textiles, Apparel, Footwear and Accessories': 'Consumer Discretionary',
    'Consumer Durables, Household and Personal Products': 'Consumer Discretionary',
    'Hotels, Restaurants and Leisure': 'Consumer Discretionary',
    'Telecommunication Services': 'Communication Services',
    'Media': 'Communication Services',
}

# Companies that are definitely large enough for Group 1
GROUP1_KEYWORDS = {
    'nbn', 'south east water', 'yarra valley', 'bank australia', 'sbs',
    'sunrice', 'pact', 'arnotts', 'baiada', 'bundaberg', 'sg fleet',
    'myob', 'cybercx', 'culture amp', 'intrepid'
}

def asrs_group(name_nk, sbti_sector):
    for kw in GROUP1_KEYWORDS:
        if kw in name_nk:
            return 'Group 1'
    large_sectors = ['Electric Utilities', 'Water Utilities', 'Solid Waste Management',
                     'Telecommunication', 'Banks', 'Financial Services', 'Ground Transportation']
    if any(s.lower() in sbti_sector.lower() for s in large_sectors):
        return 'Group 2'
    return 'Group 2'  # Non-SME SBTi companies are at minimum Group 2

def scores(asrs_grp, sbti_status, sbti_date):
    sa = float(cfg['asrs_urgency'].get(asrs_grp, 1))
    s = str(sbti_status).lower()
    if 'removed' in s:
        stg = 5.0
    elif sbti_date and sbti_date[:4] < '2023':
        stg = 4.0
    elif 'targets set' in s:
        stg = 1.0
    else:
        stg = 3.0
    w = cfg.get('weights', {'asrs_urgency': 0.25, 'target_gap': 0.30, 'risk_signals': 0.25, 'intent_signals': 0.10, 'relationship': 0.10})
    overall = round(sa * w['asrs_urgency'] + stg * w['target_gap'] + 1.0 * w['risk_signals'] + 1.0 * w['intent_signals'] + 1.0 * w['relationship'], 2)
    return {'score_asrs': sa, 'score_target_gap': stg, 'score_risk': 1.0, 'score_intent': 1.0, 'score_relationship': 1.0, 'score_overall': overall}

def top_signal(sbti_status, sbti_date):
    s = str(sbti_status).lower()
    if 'removed' in s:
        return 'SBTi commitment removed — re-engagement opportunity'
    if sbti_date and sbti_date[:4] < '2023':
        return f'SBTi validated {sbti_date[:4]} — V2 standard may require resubmission'
    if 'committed' in s:
        return 'SBTi committed — 24-month validation clock ticking'
    return 'SBTi targets set — monitor for ambition gap'

# Load SBTi file
df = pd.read_excel(Path('data/sbti_companies_latest.xlsx'))
au = df[df['location'] == 'Australia'].copy()
non_sme = au[~au['organization_type'].astype(str).str.contains('SME', case=False, na=False)]

# Load all DB nkeys
all_db = []
offset = 0
while True:
    r = sb.table('companies').select('id,name,sbti_status').range(offset, offset + 999).execute()
    all_db.extend(r.data)
    if len(r.data) < 1000: break
    offset += 1000
db_nkeys = {nkey(c['name']): c for c in all_db}

def find_in_db(sbti_name):
    nk = nkey(sbti_name)
    if nk in db_nkeys: return db_nkeys[nk]
    for length in [8, 7, 6]:
        for dk, dc in db_nkeys.items():
            if len(nk) >= length and len(dk) >= length and nk[:length] == dk[:length]:
                return dc
    wa = {w for w in nk.split() if len(w) > 3}
    for dk, dc in db_nkeys.items():
        wb = {w for w in dk.split() if len(w) > 3}
        if len(wa & wb) >= 2:
            return dc
    return None

# ── Fix NIB name mismatch ──────────────────────────────────────────────────────
print('Fixing NIB name mismatch...')
nib_row = non_sme[non_sme['company_name'].astype(str).str.contains('nib', case=False, na=False)]
if len(nib_row):
    nib_status = str(nib_row.iloc[0]['near_term_status'])
    nib_date = str(nib_row.iloc[0]['date_updated'])[:10] if pd.notna(nib_row.iloc[0].get('date_updated')) else None
    sb.table('companies').update({'sbti_status': nib_status, 'sbti_date_updated': nib_date}).ilike('name', 'NIB HOLDINGS%').execute()
    print(f'  NIB: status confirmed as {nib_status}')

# ── Insert missing companies ───────────────────────────────────────────────────
print('\nInserting missing companies...')
inserted = skipped = 0

for _, row in non_sme.iterrows():
    name = str(row['company_name'])
    existing = find_in_db(name)
    if existing:
        skipped += 1
        continue

    sbti_status = str(row.get('near_term_status') or '')
    sbti_date = str(row['date_updated'])[:10] if pd.notna(row.get('date_updated')) else None
    sbti_sector = str(row.get('sector') or '')
    org_type = str(row.get('organization_type') or '')
    sector = SECTOR_MAP.get(sbti_sector, sbti_sector or None)
    nk = nkey(name)
    grp = asrs_group(nk, sbti_sector)
    sc = scores(grp, sbti_status, sbti_date)
    sig = top_signal(sbti_status, sbti_date)

    target_class = (
        'Targets set' if 'targets set' in sbti_status.lower() else
        'SBTi committed' if 'committed' in sbti_status.lower() else
        'SBTi removed'
    )

    record = {
        'name': name,
        'sector': sector,
        'is_listed': False,
        'is_private': True,
        'asrs_group': grp,
        'sbti_status': sbti_status,
        'sbti_date_updated': sbti_date,
        'target_classification': target_class,
        'relationship_status': 'none',
        'top_signal': sig,
        **sc,
    }

    try:
        sb.table('companies').insert({k: v for k, v in record.items() if v is not None}).execute()
        inserted += 1
        print(f'  + [{sbti_status:20}] {name}')
    except Exception as e:
        print(f'  ! {name}: {e}')

print(f'\nDone: {inserted} inserted, {skipped} already in DB')
