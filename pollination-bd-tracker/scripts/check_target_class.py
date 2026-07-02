import os
from pathlib import Path
from collections import Counter
for line in Path('pollination-bd-tracker/.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k,v=line.split('=',1); os.environ.setdefault(k.strip(),v.strip())
from supabase import create_client
sb = create_client(os.environ['NEXT_PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])

r = sb.table('companies').select('name,target_classification,nger_scope1_tco2e').gt('nger_scope1_tco2e', 0).limit(30).execute()

vals = Counter(c['target_classification'] for c in r.data)
print('target_classification values (NGER companies):')
for k,v in sorted(vals.items(), key=lambda x:-x[1]):
    print(f'  {repr(k)}: {v}')

print()
print('Sample rows:')
for c in r.data[:15]:
    tc = str(c['target_classification'])
    name = c['name']
    s1 = c['nger_scope1_tco2e']
    print(f'  {tc:35} | {name}')
