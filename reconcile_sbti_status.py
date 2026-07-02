"""
Reconcile sbti_status in DB against current sbti_companies_latest.xlsx.
Clears sbti_status for any DB company that can't be matched to the live SBTi file.

Run: py -3 reconcile_sbti_status.py [--apply]
Without --apply: dry run only (shows what would change).
"""
import os, re, sys
import pandas as pd
from pathlib import Path

APPLY = '--apply' in sys.argv

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

def strict_match(a, b):
    """Conservative match: require 8-char prefix OR 2+ significant shared words."""
    if not a or not b:
        return False
    if a == b:
        return True
    # 8-char prefix (tighter than the 5-6 used during ingestion)
    min_len = min(len(a), len(b))
    if min_len >= 8 and a[:8] == b[:8]:
        return True
    # Word overlap — only words >3 chars count as significant
    wa = {w for w in a.split() if len(w) > 3}
    wb = {w for w in b.split() if len(w) > 3}
    if len(wa & wb) >= 2:
        return True
    return False

# Load SBTi latest (AU only)
df = pd.read_excel(Path('data/sbti_companies_latest.xlsx'))
au = df[df['location'] == 'Australia'].copy()
sbti_nkeys = {nkey(row['company_name']): str(row['near_term_status']) for _, row in au.iterrows()}
sbti_nkey_set = set(sbti_nkeys.keys())
sbti_names = list(au['company_name'].astype(str))

print(f'SBTi AU companies in file: {len(sbti_nkey_set)}')

# Load DB companies with sbti_status set
r = sb.table('companies').select('id,name,sbti_status,sbti_date_updated').not_.is_('sbti_status', 'null').neq('sbti_status', '').execute()
print(f'DB companies with sbti_status set: {len(r.data)}')
print()

to_clear = []
to_keep = []

for c in r.data:
    nk = nkey(c['name'])
    status = c.get('sbti_status') or ''

    # Exact match
    if nk in sbti_nkey_set:
        to_keep.append((c['name'], status, 'exact'))
        continue

    # Strict fuzzy match against all SBTi nkeys
    matched = False
    for sbti_nk in sbti_nkey_set:
        if strict_match(nk, sbti_nk):
            to_keep.append((c['name'], status, f'fuzzy->{sbti_names[list(sbti_nkey_set).index(sbti_nk)] if sbti_nk in sbti_nkey_set else sbti_nk}'))
            matched = True
            break

    if not matched:
        to_clear.append(c)

print(f'=== KEEP ({len(to_keep)}) ===')
for name, status, how in sorted(to_keep, key=lambda x: x[0]):
    print(f'  [{how:30}] {name[:50]:50} {status}')

print(f'\n=== CLEAR ({len(to_clear)}) — no match in SBTi file ===')
for c in sorted(to_clear, key=lambda x: x['name']):
    print(f'  {c["name"][:55]:55} was: {c.get("sbti_status")}')

# Manual overrides based on known data
# These failed name matching but are confirmed on SBTi website
FORCE_KEEP = {
    'ausgrid operator partnership',   # on SBTi as "Ausgrid"
    'nib holdings limited',           # confirmed committed on SBTi website
}
# These have sbti_status but internal reports claim validation not confirmed on SBTi website
CLAIM_NOT_CONFIRMED = {
    'south32 limited',
}

to_clear_final = []
for c in to_clear:
    nk = nkey(c['name'])
    if nk in FORCE_KEEP:
        print(f'  [FORCE KEEP] {c["name"]} — confirmed on SBTi website, name mismatch only')
    elif nk in CLAIM_NOT_CONFIRMED:
        to_clear_final.append((c, True))  # True = flag South32-style
    else:
        to_clear_final.append((c, False))

print(f'\nWill clear: {len(to_clear_final)} | Force-kept: {sum(1 for c in to_clear if nkey(c["name"]) in FORCE_KEEP)}')

if not APPLY:
    print(f'DRY RUN — pass --apply to execute')
else:
    cleared = 0
    for c, is_claim in to_clear_final:
        patch = {'sbti_status': None, 'sbti_date_updated': None}
        if is_claim:
            patch['top_signal'] = 'Claims SBTi validation in annual report — not confirmed on SBTi website'
        sb.table('companies').update(patch).eq('id', c['id']).execute()
        label = '[CLAIM-FLAG]' if is_claim else '[CLEAR]'
        print(f'  {label} {c["name"]}')
        cleared += 1
    print(f'\nDone — cleared/flagged {cleared} companies')
