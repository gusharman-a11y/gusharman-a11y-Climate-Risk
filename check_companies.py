import os
from pathlib import Path
for line in Path('pollination-bd-tracker/.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip())
from supabase import create_client
sb = create_client(os.environ['NEXT_PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])

for term in ['ampol', 'cdc', 'data centre']:
    r = sb.table('companies').select('name,relationship_status,sbti_status,nzt_end_year,target_year,score_overall,asrs_group,sector,target_description').ilike('name', f'%{term}%').execute()
    for c in r.data:
        print(f"{c['name'][:50]:<52} rel={c.get('relationship_status',''):<18} sbti={c.get('sbti_status') or '':<25} score={c.get('score_overall') or ''}")
