import os, json
from pathlib import Path
for line in Path('pollination-bd-tracker/.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip())
from supabase import create_client
sb = create_client(os.environ['NEXT_PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])

r = sb.table('companies').select(
    'name,asx_code,sector,asrs_group,relationship_status,sbti_status,sbti_date_updated,'
    'target_classification,target_description,nzt_end_year,target_year,'
    'score_overall,score_target_gap,score_relationship,score_asrs'
).not_.is_('score_overall', 'null').execute()

cos = r.data

# Score signals
def signals(c):
    out = []
    rel = c.get('relationship_status','')
    sbti = (c.get('sbti_status') or '').lower()
    nzt_yr = c.get('nzt_end_year') or 0
    tgt_yr = c.get('target_year') or 0
    nearest_yr = min(y for y in [nzt_yr, tgt_yr] if y) if any([nzt_yr, tgt_yr]) else None

    if rel in ('warm_contact','current_client','past_client'):
        out.append(f'REL:{rel}')
    if 'committed' in sbti and 'removed' not in sbti:
        out.append('SBTI_COMMITTED')
    if 'removed' in sbti:
        out.append('SBTI_REMOVED')
    if 'targets set' in sbti:
        out.append('SBTI_VALIDATED')
    if nearest_yr and nearest_yr <= 2030:
        out.append(f'NZ_BY_{nearest_yr}')
    if nearest_yr and nearest_yr <= 2027:
        out.append(f'URGENT_NZ_{nearest_yr}')
    return out

results = []
for c in cos:
    sigs = signals(c)
    priority = 0
    # Relationship = strong positive
    if 'REL:warm_contact' in sigs: priority += 30
    if 'REL:current_client' in sigs: priority += 20
    if 'REL:past_client' in sigs: priority += 15
    # SBTi committed = ticking clock
    if 'SBTI_COMMITTED' in sigs: priority += 25
    # SBTi removed = re-engagement
    if 'SBTI_REMOVED' in sigs: priority += 20
    # Urgent net zero date
    if any('URGENT_NZ' in s for s in sigs): priority += 20
    elif any('NZ_BY_' in s for s in sigs): priority += 10
    # Overall score
    priority += float(c.get('score_overall') or 0) * 5
    # Group 1 = must report
    if c.get('asrs_group') == 'Group 1': priority += 10
    results.append({**c, '_priority': priority, '_signals': sigs})

results.sort(key=lambda x: -x['_priority'])

print(f"{'RANK':<4} {'COMPANY':<45} {'SECTOR':<20} {'ASRS':<8} {'SCORE':>5}  SIGNALS")
print('-' * 130)
for i, c in enumerate(results[:20], 1):
    name = (c['name'] or '')[:44]
    sector = (c['sector'] or '')[:19]
    grp = c.get('asrs_group','')[:7]
    score = c.get('score_overall') or 0
    sigs = ' | '.join(c['_signals'])
    print(f"{i:<4} {name:<45} {sector:<20} {grp:<8} {score:>5.1f}  {sigs}")
