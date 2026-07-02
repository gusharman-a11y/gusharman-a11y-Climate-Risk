import os
from pathlib import Path
for line in Path('pollination-bd-tracker/.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip())
from supabase import create_client
sb = create_client(os.environ['NEXT_PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])

r = sb.table('companies').select(
    'name,net_zero_year,target_year,sbti_status,asrs_group,sector,score_overall'
).not_.is_('net_zero_year', 'null').order('net_zero_year').execute()

print(f'Companies with net_zero_year set ({len(r.data)} total):')
print(f"  {'NZ Year':7} {'Target':6} {'Score':5} {'ASRS':7} {'SBTi':12} Name")
for c in r.data:
    nzy = c.get('net_zero_year') or ''
    ty  = c.get('target_year') or ''
    sc  = c.get('score_overall') or ''
    grp = c.get('asrs_group') or ''
    sbti = (c.get('sbti_status') or '')[:11]
    name = c['name'][:50]
    print(f'  {str(nzy):7} {str(ty):6} {str(sc):5} {str(grp):7} {sbti:12} {name}')
