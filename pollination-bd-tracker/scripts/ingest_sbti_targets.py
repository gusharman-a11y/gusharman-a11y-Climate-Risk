"""
Ingest SBTi targets-excel.xlsx into DB for all AU companies.
Groups multiple targets per company, builds full description, updates:
  sbti_target_text, target_description, target_scope, target_year, net_zero_year, target_classification

Run: py -3 pollination-bd-tracker/scripts/ingest_sbti_targets.py
Cadence: weekly (same as update_targets.py --sbti)
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

def clean(v):
    s = str(v).strip()
    return None if s in ('nan', 'None', 'NaT', '', '-', 'N/A') else s

def safe_int(v):
    try:
        i = int(float(str(v)))
        return i if 2010 < i < 2080 else None
    except: return None

def safe_pct(v):
    s = str(v).strip().rstrip('%')
    try:
        f = float(s)
        return int(round(f * 100)) if f < 1 else int(round(f))
    except: return None

_STRIP = re.compile(r'\b(?:pty|ltd|limited|holdings|holding|group|australia|australian|corporation|corp|inc|plc|services|management|investments|finance|financial|partners|partnership|uniforms|engineering)\b', re.I)
def nkey(n):
    n = re.sub(r'[^a-z0-9 ]', ' ', str(n).lower())
    n = _STRIP.sub('', n)
    return re.sub(r'\s+', ' ', n).strip()

# ── Load targets file ──────────────────────────────────────────────────────────
print('Loading SBTi targets file...')
df = pd.read_excel(DATA / 'sbti_targets.xlsx')
au = df[df['location'].astype(str).str.upper() == 'AUSTRALIA'].copy()
print(f'  AU targets: {len(au)}')

# ── Group by sbti_id (company) ─────────────────────────────────────────────────
def build_company_record(rows):
    """Aggregate multiple target rows for one company into a single DB patch."""
    rows = rows.sort_values('target', key=lambda x: x.map({'Near-term': 0, 'Long-term': 1, 'Net-zero': 2}).fillna(3))

    company_name = clean(rows.iloc[0]['company_name']) or ''
    status_vals = rows['status'].astype(str).str.strip().unique().tolist()
    action_vals = rows['action'].astype(str).str.strip().unique().tolist()

    has_validated = any('target set' in str(s).lower() for s in status_vals) or 'Target' in action_vals
    has_commitment = 'Commitment' in action_vals
    is_removed = all('removed' in str(s).lower() for s in status_vals)

    # Build target description from individual target rows
    target_lines = []
    scopes = set()
    target_years = []
    net_zero_year = None
    sbti_text_parts = []

    for _, row in rows.iterrows():
        action = clean(row.get('action')) or ''
        status = clean(row.get('status')) or ''
        target_type = clean(row.get('target')) or ''  # Near-term / Long-term / Net-zero
        wording = clean(row.get('full_target_language')) or clean(row.get('target_wording'))
        scope = clean(row.get('scope'))
        target_val = clean(row.get('target_value'))
        t_type = clean(row.get('type'))  # Absolute / Intensity
        base_yr = safe_int(row.get('base_year'))
        tgt_yr = safe_int(row.get('target_year'))
        deadline = clean(row.get('commitment_deadline'))
        temp_align = clean(row.get('company_temperature_alignment'))
        classification = clean(row.get('target_classification_short'))

        if scope:
            scopes.add(f'Scope {scope}')

        if action == 'Commitment':
            deadline_str = str(deadline)[:10] if deadline else 'TBD'
            line = f'SBTi near-term target commitment (deadline: {deadline_str})'
            if temp_align:
                line += f' — {temp_align} aligned'
            target_lines.append(line)
            sbti_text_parts.append(line)
        elif action == 'Target' and 'removed' not in status.lower():
            if wording:
                target_lines.append(wording)
                sbti_text_parts.append(wording)
            elif target_val and tgt_yr:
                pct = safe_pct(target_val)
                pct_str = f'{pct}%' if pct else target_val
                t_desc = f'{t_type or "Absolute"} {pct_str} reduction by {tgt_yr}'
                if base_yr: t_desc += f' from {base_yr} baseline'
                if scope: t_desc += f' (Scope {scope})'
                target_lines.append(t_desc)
                sbti_text_parts.append(t_desc)

            if tgt_yr:
                if target_type == 'Net-zero':
                    net_zero_year = tgt_yr
                else:
                    target_years.append(tgt_yr)

    # Determine primary target year (earliest non-net-zero)
    primary_year = min(target_years) if target_years else None

    # Determine classification
    if is_removed:
        classification_out = 'SBTi removed'
    elif has_validated:
        classification_out = 'Net zero' if net_zero_year else 'Reduction target'
    else:
        classification_out = 'Net zero' if net_zero_year else 'Reduction target'

    combined_desc = ' | '.join(target_lines) if target_lines else None
    combined_sbti = ' | '.join(sbti_text_parts) if sbti_text_parts else None
    scope_str = ' + '.join(sorted(scopes, key=lambda x: x.replace('Scope ', ''))) if scopes else None

    return {
        'company_name': company_name,
        'sbti_target_text': combined_sbti[:2000] if combined_sbti else None,
        'target_description': combined_desc[:2000] if combined_desc else None,
        'target_scope': scope_str,
        'target_year': primary_year,
        'net_zero_year': net_zero_year,
        'target_classification': classification_out,
        'has_validated': has_validated,
    }

# Build per-company records
records = {}
for sbti_id, grp in au.groupby('sbti_id'):
    rec = build_company_record(grp)
    records[str(sbti_id)] = rec

print(f'  Unique AU companies: {len(records)}')

# ── Load DB companies ──────────────────────────────────────────────────────────
print('Loading DB companies...')
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
    # Try prefix match
    for length in [8, 6, 5]:
        if len(nk) >= length:
            prefix = nk[:length]
            for db_nk, c in by_name.items():
                if db_nk.startswith(prefix) or nk.startswith(db_nk[:min(length, len(db_nk))]):
                    return c
    return None

# ── Write to DB ────────────────────────────────────────────────────────────────
print('Writing to DB...')
updated = validated_count = committed_count = 0
unmatched = []

for sbti_id, rec in records.items():
    company = find_company(rec['company_name'])
    if not company:
        unmatched.append(rec['company_name'])
        continue

    patch = {}
    is_removed = rec.get('target_classification') == 'SBTi removed'
    if rec.get('sbti_target_text'): patch['sbti_target_text'] = rec['sbti_target_text']
    # Don't overwrite target_description for removed companies — they may have real targets from other sources
    if rec.get('target_description') and not is_removed: patch['target_description'] = rec['target_description']
    if rec.get('target_scope') and not is_removed: patch['target_scope'] = rec['target_scope']
    if rec.get('target_year') and not is_removed: patch['target_year'] = rec['target_year']
    if rec.get('net_zero_year') and not is_removed: patch['net_zero_year'] = rec['net_zero_year']
    if rec.get('target_classification'): patch['target_classification'] = rec['target_classification']

    if patch:
        sb.table('companies').update(patch).eq('id', company['id']).execute()
        updated += 1
        if rec['has_validated']:
            validated_count += 1
        else:
            committed_count += 1
        marker = 'V' if rec['has_validated'] else 'C'
        print(f'  [{marker}] {rec["company_name"][:45]:47} | {rec["target_classification"]} | yr={rec.get("target_year") or "—"} | nz={rec.get("net_zero_year") or "—"}')

print(f'\nUpdated: {updated} ({validated_count} validated, {committed_count} committed)')
print(f'Unmatched: {len(unmatched)}')
for n in unmatched: print(f'  {n}')
