"""
Audit all DB companies with sbti_status set against sbti_companies_latest.xlsx.
Shows match quality, status accuracy, and flags discrepancies.
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

def best_match(nk, sbti_dict):
    if nk in sbti_dict:
        return nk, 'exact'
    # 8-char prefix
    for sk in sbti_dict:
        min_l = min(len(nk), len(sk))
        if min_l >= 8 and nk[:8] == sk[:8]:
            return sk, 'prefix-8'
    # 6-char prefix
    for sk in sbti_dict:
        min_l = min(len(nk), len(sk))
        if min_l >= 6 and nk[:6] == sk[:6]:
            return sk, 'prefix-6'
    # 2+ significant words
    wa = {w for w in nk.split() if len(w) > 3}
    for sk in sbti_dict:
        wb = {w for w in sk.split() if len(w) > 3}
        if len(wa & wb) >= 2:
            return sk, 'words'
    return None, None

# Load SBTi file — AU only
df = pd.read_excel(Path('data/sbti_companies_latest.xlsx'))
au = df[df['location'] == 'Australia'].copy()
sbti = {}
for _, row in au.iterrows():
    nk = nkey(str(row['company_name']))
    sbti[nk] = {
        'name': str(row['company_name']),
        'status': str(row.get('near_term_status') or ''),
        'date': str(row.get('date_updated') or '')[:10],
    }

# Load DB companies with sbti_status
r = sb.table('companies').select(
    'name,sbti_status,sbti_date_updated,target_classification,target_description,asrs_group,score_overall'
).not_.is_('sbti_status', 'null').neq('sbti_status', '').order('sbti_status').execute()

print(f'DB companies with sbti_status: {len(r.data)}')
print(f'SBTi AU companies in file: {len(sbti)}')
print()

STATUS_ORDER = {'Targets set': 0, 'Committed': 1, 'Commitment removed': 2}
rows = sorted(r.data, key=lambda x: (STATUS_ORDER.get(x.get('sbti_status',''), 9), x['name']))

results = []
for c in rows:
    nk = nkey(c['name'])
    matched_nk, match_type = best_match(nk, sbti)
    sbti_rec = sbti.get(matched_nk) if matched_nk else None

    db_status = c.get('sbti_status') or ''
    file_status = sbti_rec['status'] if sbti_rec else 'NOT IN FILE'
    file_name = sbti_rec['name'] if sbti_rec else ''

    # Flag issues
    flags = []
    if file_status == 'NOT IN FILE':
        flags.append('NOT IN FILE')
    elif db_status != file_status:
        flags.append(f'STATUS MISMATCH: file={file_status}')
    if match_type in ('prefix-6', 'words') and file_name:
        flags.append(f'loose-match->{file_name[:30]}')

    results.append({
        'name': c['name'],
        'db_status': db_status,
        'file_status': file_status,
        'match': match_type or '-',
        'flags': ' | '.join(flags),
        'asrs': c.get('asrs_group') or '',
        'has_desc': bool(c.get('target_description')),
    })

# Print by group
for group_status in ['Targets set', 'Committed', 'Commitment removed']:
    grp = [r for r in results if r['db_status'] == group_status]
    print(f'\n=== {group_status.upper()} ({len(grp)}) ===')
    print(f'  {"ASRS":7} {"Match":9} {"Has Desc":8} {"Name":45} {"Flags"}')
    for r in grp:
        desc = 'YES' if r['has_desc'] else 'no'
        flag = r['flags'] or 'OK'
        print(f'  {r["asrs"]:7} {r["match"]:9} {desc:8} {r["name"][:45]:45} {flag}')

# Summary
not_in_file = [r for r in results if 'NOT IN FILE' in r['flags']]
mismatch = [r for r in results if 'STATUS MISMATCH' in r['flags']]
loose = [r for r in results if 'loose-match' in r['flags']]
ok = [r for r in results if not r['flags']]

print(f'\n=== SUMMARY ===')
print(f'  OK (exact/prefix-8 match, status correct): {len(ok)}')
print(f'  Status mismatch:                           {len(mismatch)}')
print(f'  Not in SBTi file:                          {len(not_in_file)}')
print(f'  Loose match (needs review):                {len(loose)}')
