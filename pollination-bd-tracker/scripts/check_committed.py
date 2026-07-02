import os
from pathlib import Path
for line in Path('pollination-bd-tracker/.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1); os.environ.setdefault(k.strip(), v.strip())
from supabase import create_client
sb = create_client(os.environ['NEXT_PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])

all_companies = []
offset = 0
while True:
    r = sb.table('companies').select('id,name,sbti_status,sbti_target_text,target_description').range(offset, offset+999).execute()
    all_companies.extend(r.data)
    if len(r.data) < 1000: break
    offset += 1000

committed = [c for c in all_companies if c.get('sbti_status') and 'committed' in c['sbti_status'].lower() and 'removed' not in c['sbti_status'].lower()]
print(f'Committed companies: {len(committed)}')
for c in committed:
    has_text = bool(c.get('sbti_target_text'))
    has_desc = bool(c.get('target_description'))
    print(f'  {c["name"][:45]:47} | sbti_text={has_text} | target_desc={has_desc}')

targets_set = [c for c in all_companies if c.get('sbti_status') and 'targets set' in c['sbti_status'].lower()]
missing = [c for c in targets_set if not c.get('target_description') and c.get('sbti_target_text')]
print(f'\nTargets-set with sbti_text but no target_description: {len(missing)}')
for c in missing[:10]:
    print(f'  {c["name"][:50]}')
