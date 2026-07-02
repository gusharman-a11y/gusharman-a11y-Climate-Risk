import os
from pathlib import Path
for line in Path('pollination-bd-tracker/.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip())
from supabase import create_client
sb = create_client(os.environ['NEXT_PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])

r = sb.table('companies').select(
    'name,relationship_status,sbti_status,nzt_end_year,target_year,score_overall,asrs_group,sector'
).neq('relationship_status','none').not_.is_('relationship_status','null').execute()

print(f"{'COMPANY':<45} {'REL':<18} {'SBTI':<25} {'NZT_YR'} {'SCORE'}")
print('-'*110)
for c in sorted(r.data, key=lambda x: -(x.get('score_overall') or 0)):
    print(f"{(c['name'] or '')[:44]:<45} {(c['relationship_status'] or ''):<18} {(c['sbti_status'] or '')[:24]:<25} {c.get('nzt_end_year') or ''!s:<7} {c.get('score_overall') or '':>5}")
