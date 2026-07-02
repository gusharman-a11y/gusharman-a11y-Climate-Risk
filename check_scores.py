import os
from pathlib import Path
for line in Path('pollination-bd-tracker/.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip())
from supabase import create_client
sb = create_client(os.environ['NEXT_PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])

r = sb.table('companies').select(
    'name,sbti_status,target_classification,score_asrs,score_target_gap,score_risk,score_intent,score_relationship,score_overall,top_signal,sector,asrs_group,nger_scope1_tco2e,market_cap_tier'
).not_.is_('score_overall', 'null').order('score_overall', desc=True).limit(30).execute()

print(f'Top {len(r.data)} companies by score_overall:')
print(f"  {'Score':5} {'ASRS':4} {'Gap':3} {'Risk':4} {'Intent':6} {'Rel':3} | {'SBTi':12} {'ASRS Grp':8} {'Name'}")
for c in r.data:
    tot  = c.get('score_overall') or 0
    asrs = c.get('score_asrs') or 0
    gap  = c.get('score_target_gap') or 0
    risk = c.get('score_risk') or 0
    intent = c.get('score_intent') or 0
    rel  = c.get('score_relationship') or 0
    sbti = (c.get('sbti_status') or '')[:12]
    grp  = c.get('asrs_group') or ''
    name = c['name'][:45]
    print(f'  {tot:5.1f} {asrs:4} {gap:3} {risk:4} {intent:6} {rel:3} | {sbti:12} {str(grp):8} {name}')
