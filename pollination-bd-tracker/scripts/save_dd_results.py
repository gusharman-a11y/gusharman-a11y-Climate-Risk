"""
Save DD research results to DB + audit log.
Run after workflow completes with results JSON.

Usage:
    py -3 pollination-bd-tracker/scripts/save_dd_results.py results.json

Or pipe stdin:
    py -3 pollination-bd-tracker/scripts/save_dd_results.py < results.json
"""
import os, sys, json, re
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
for line in (ROOT / '.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1); os.environ.setdefault(k.strip(), v.strip())

from supabase import create_client
sb = create_client(os.environ['NEXT_PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])

# ── Load results ───────────────────────────────────────────────────────────────
if len(sys.argv) > 1:
    with open(sys.argv[1], encoding='utf-8') as f:
        results = json.load(f)
else:
    results = json.load(sys.stdin)

if not isinstance(results, list):
    # Workflow may wrap in dict
    results = results.get('results', results.get('data', []))

print(f'Loaded {len(results)} research results')

# ── Load DB companies ──────────────────────────────────────────────────────────
_STRIP = re.compile(r'\b(?:pty|ltd|limited|holdings|holding|group|australia|australian|corporation|corp|inc|plc|services|management|investments|finance|financial|partners|partnership)\b', re.I)
def nkey(n):
    n = re.sub(r'[^a-z0-9 ]', ' ', str(n).lower())
    n = _STRIP.sub('', n)
    return re.sub(r'\s+', ' ', n).strip()

all_db = []
offset = 0
while True:
    r = sb.table('companies').select('id,name,target_classification,target_description,sbti_status').range(offset, offset+999).execute()
    all_db.extend(r.data)
    if len(r.data) < 1000: break
    offset += 1000

by_name = {nkey(c['name']): c for c in all_db}

def find_company(name):
    nk = nkey(str(name))
    if nk in by_name: return by_name[nk]
    for length in [8, 6, 5]:
        if len(nk) >= length:
            pfx = nk[:length]
            for db_nk, c in by_name.items():
                if db_nk.startswith(pfx) or nk.startswith(db_nk[:min(length, len(db_nk))]):
                    return c
    return None

# ── Check for audit table ──────────────────────────────────────────────────────
has_log_table = False
try:
    sb.table('target_research_log').select('id').limit(1).execute()
    has_log_table = True
    print('Audit table: found — will write log entries')
except Exception:
    print('Audit table: NOT found — skipping log entries (run scripts/migrations/001_research_log.sql)')

# ── Process results ────────────────────────────────────────────────────────────
updated = skipped = unmatched = 0
log_rows = []

for res in results:
    if not res:
        continue

    company_name = res.get('company_name', '')
    confidence = res.get('confidence', 'low')
    classification = res.get('target_classification', '')
    description = res.get('target_description', '')
    net_zero_year = res.get('net_zero_year')
    target_year = res.get('target_year')
    scope = res.get('target_scope', '')
    sources = res.get('sources', [])
    notes = res.get('notes', '') or res.get('sbti_notes', '')

    company = find_company(company_name)
    if not company:
        print(f'  [UNMATCHED] {company_name}')
        unmatched += 1
        continue

    # Only update if we found something useful and confidence is at least medium
    if confidence == 'not_found' or confidence == 'low':
        print(f'  [SKIP low conf] {company_name} ({confidence})')
        skipped += 1
    else:
        patch = {}
        # Don't overwrite SBTi-validated target_classification with DD findings
        existing_class = company.get('target_classification', '')
        sbti_validated = company.get('sbti_status', '') and 'targets set' in (company.get('sbti_status') or '').lower()

        if description and not sbti_validated:
            patch['target_description'] = description[:2000]
        if classification and not sbti_validated:
            patch['target_classification'] = classification
        if net_zero_year:
            patch['net_zero_year'] = net_zero_year
        if target_year:
            patch['target_year'] = target_year
        if scope:
            patch['target_scope'] = scope

        if patch:
            sb.table('companies').update(patch).eq('id', company['id']).execute()
            updated += 1
            print(f'  [OK {confidence}] {company_name} → {classification} | {description[:60] if description else "no desc"}')
        else:
            skipped += 1
            print(f'  [NO CHANGE] {company_name}')

    # Build audit log row regardless of confidence
    log_rows.append({
        'company_id': company['id'],
        'company_name': company['name'],
        'research_task': 'dd_target_research',
        'finding': description or f'No target found ({confidence})',
        'confidence': confidence,
        'fields_updated': json.dumps(patch if confidence not in ('not_found', 'low') else {}),
        'sources': sources,
        'agent_raw': json.dumps(res),
    })

# ── Write audit log ────────────────────────────────────────────────────────────
if has_log_table and log_rows:
    # Insert in batches of 50
    for i in range(0, len(log_rows), 50):
        batch = log_rows[i:i+50]
        sb.table('target_research_log').insert(batch).execute()
    print(f'\nWrote {len(log_rows)} audit log entries')

# ── Save raw JSON ──────────────────────────────────────────────────────────────
out = ROOT.parent / 'data' / 'dd_research_results.json'
out.parent.mkdir(exist_ok=True)
with open(out, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)
print(f'Saved raw results → {out}')

print(f'\nDone: {updated} updated, {skipped} skipped, {unmatched} unmatched')
