"""
Backfill DB from SBTi file for AU committed companies.
Writes target_description, sbti_target_text, net_zero_year, target_classification.

Run: py -3 pollination-bd-tracker/scripts/backfill_sbti_committed.py
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

df = pd.read_excel(DATA / 'sbti_companies.xlsx')
au = df[df['location'].astype(str).str.upper() == 'AUSTRALIA']
committed = au[
    au['near_term_status'].astype(str).str.lower().str.contains('committed', na=False) &
    ~au['near_term_status'].astype(str).str.lower().str.contains('removed', na=False)
].copy()
print(f'AU committed in SBTi file: {len(committed)}')

_STRIP = re.compile(r'\b(?:pty|ltd|limited|holdings|holding|group|australia|australian|corporation|corp|inc|plc|services|management|investments|finance|financial|partners|partnership)\b', re.I)
def nkey(n):
    n = re.sub(r'[^a-z0-9 ]', ' ', str(n).lower())
    n = _STRIP.sub('', n)
    return re.sub(r'\s+', ' ', n).strip()

def clean(v):
    s = str(v).strip()
    return None if s in ('nan', 'None', 'NaT', '', '-', 'N/A') else s

def safe_int(v):
    try: return int(float(str(v)))
    except: return None

def build_description(row):
    parts = []
    nt = clean(row.get('near_term_status'))
    lt = clean(row.get('long_term_status'))
    nz = clean(row.get('net_zero_status'))
    nz_year = safe_int(row.get('net_zero_year'))
    lt_year = safe_int(row.get('long_term_target_year'))
    nt_year = safe_int(row.get('near_term_target_year'))
    full = clean(row.get('full_target_language'))
    reason = clean(row.get('reason_for_extension_or_removal'))
    date = clean(row.get('date_updated'))
    date_str = str(date)[:10] if date else None

    if full:
        parts.append(full)
    else:
        parts.append(f'SBTi near-term target: {nt or "Committed"} (commitment date: {date_str or "unknown"}).')
        if lt:
            lt_txt = f'by {lt_year}' if lt_year else ''
            parts.append(f'Long-term target: {lt} {lt_txt}.'.strip())
        if nz:
            nz_txt = f'by {nz_year}' if nz_year else ''
            parts.append(f'Net zero: {nz} {nz_txt}.'.strip())
        if reason:
            parts.append(f'Note: {reason}')

    return ' '.join(parts)

def build_sbti_text(row):
    full = clean(row.get('full_target_language'))
    if full: return full
    nt = clean(row.get('near_term_status')) or 'Committed'
    date = clean(row.get('date_updated'))
    date_str = str(date)[:10] if date else 'unknown'
    nz = clean(row.get('net_zero_status'))
    nz_year = safe_int(row.get('net_zero_year'))
    lt_year = safe_int(row.get('long_term_target_year'))
    parts = [f'Near-term: {nt} (as of {date_str})']
    if nz:
        parts.append(f'Net zero: {nz}' + (f' by {nz_year}' if nz_year else ''))
    if lt_year:
        parts.append(f'Long-term target year: {lt_year}')
    return ' | '.join(parts)

# Load DB companies
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
    # prefix match
    prefix = nk[:8]
    if len(prefix) >= 5:
        for db_nk, c in by_name.items():
            if db_nk.startswith(prefix[:6]) or nk.startswith(db_nk[:min(6, len(db_nk))]):
                return c
    return None

updated = 0
unmatched = []
for _, row in committed.iterrows():
    name = clean(row.get('company_name')) or clean(row.get('name')) or ''
    if not name: continue

    company = find_company(name)
    if not company:
        unmatched.append(name)
        continue

    desc = build_description(row)
    sbti_text = build_sbti_text(row)
    nz_year = safe_int(row.get('net_zero_year'))
    lt_year = safe_int(row.get('long_term_target_year'))
    tc = 'Net zero' if clean(row.get('net_zero_status')) else 'Reduction target'

    patch = {
        'target_description': desc[:2000],
        'sbti_target_text': sbti_text[:2000],
        'target_classification': tc,
    }
    if nz_year and 2020 < nz_year < 2080:
        patch['net_zero_year'] = nz_year
    if lt_year and 2020 < lt_year < 2080:
        patch['target_year'] = lt_year

    sb.table('companies').update(patch).eq('id', company['id']).execute()
    updated += 1
    print(f'  {name[:45]:47} -> {tc} | nz={nz_year or "—"}')

print(f'\nUpdated: {updated} | Unmatched: {len(unmatched)}')
for n in unmatched:
    print(f'  Unmatched: {n}')
