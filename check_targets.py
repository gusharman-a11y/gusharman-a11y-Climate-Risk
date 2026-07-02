import os
from pathlib import Path
for line in Path('pollination-bd-tracker/.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip())
from supabase import create_client
sb = create_client(os.environ['NEXT_PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])
r = sb.table('companies').select('name,sbti_status,target_classification,target_description,target_year,net_zero_year').execute()

print('=== SBTi targets_set but no target_description ===')
count = 0
for c in r.data:
    sbti = (c.get('sbti_status') or '').lower()
    if 'targets set' in sbti and not c.get('target_description'):
        name = c['name']
        print(f'  {name[:55]}  sbti_status={c["sbti_status"]}')
        count += 1
print(f'  Total: {count}')

print()
print('=== Committed but no target_description ===')
count2 = 0
for c in r.data:
    sbti = (c.get('sbti_status') or '').lower()
    if sbti == 'committed' and not c.get('target_description'):
        name = c['name']
        print(f'  {name[:55]}')
        count2 += 1
print(f'  Total: {count2}')
