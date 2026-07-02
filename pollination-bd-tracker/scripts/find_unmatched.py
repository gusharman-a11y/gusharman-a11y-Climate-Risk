import os, re
from pathlib import Path
for line in (Path('pollination-bd-tracker/.env.local')).read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1); os.environ.setdefault(k.strip(), v.strip())
from supabase import create_client
sb = create_client(os.environ['NEXT_PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])

all_db = []
offset = 0
while True:
    r = sb.table('companies').select('id,name').range(offset, offset+999).execute()
    all_db.extend(r.data)
    if len(r.data) < 1000: break
    offset += 1000

for search in ['BDO', 'Glad', 'MYOB', 'OCS', 'Quad']:
    matches = [c for c in all_db if search.lower() in c['name'].lower()]
    print(f'{search}: {[c["name"] for c in matches[:3]]}')
