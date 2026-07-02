import os
from pathlib import Path
for line in Path('pollination-bd-tracker/.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1); os.environ.setdefault(k.strip(), v.strip())
from supabase import create_client
sb = create_client(os.environ['NEXT_PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])

all_co = []
offset = 0
while True:
    r = sb.table('companies').select('id,name,asx_code,sector,asrs_group,sbti_status,target_classification,target_description,score_overall').range(offset, offset+999).execute()
    all_co.extend(r.data)
    if len(r.data) < 1000: break
    offset += 1000

committed = [c for c in all_co if c.get('sbti_status') and 'committed' in c['sbti_status'].lower() and 'removed' not in c['sbti_status'].lower()]
aspirational = [c for c in all_co if c.get('target_classification') == 'Aspirational' and not (c.get('sbti_status') and 'committed' in (c.get('sbti_status') or '').lower())]
quant_nv = [c for c in all_co if c.get('target_classification') == 'Quantitative non-validated' and not (c.get('sbti_status') and 'committed' in (c.get('sbti_status') or '').lower())]

print(f'SBTi Committed (no existing target_description): {len(committed)}')
for c in committed:
    print(f'  {c["name"][:45]:47} | {c.get("asrs_group")} | score={c.get("score_overall")}')

print(f'\nAspirational: {len(aspirational)}')
for c in aspirational:
    print(f'  {c["name"][:45]:47} | {c.get("asrs_group")} | {(c.get("target_description") or "")[:60]}')

print(f'\nQuantitative non-validated: {len(quant_nv)}')
for c in quant_nv:
    print(f'  {c["name"][:45]:47} | {c.get("asrs_group")} | {(c.get("target_description") or "")[:60]}')

print(f'\nTotals: {len(committed)} committed + {len(aspirational)} aspirational + {len(quant_nv)} quant-nv = {len(committed)+len(aspirational)+len(quant_nv)} total')
