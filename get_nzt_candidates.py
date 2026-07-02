import os, json
from pathlib import Path
for line in Path('pollination-bd-tracker/.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip())
from supabase import create_client
sb = create_client(os.environ['NEXT_PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])
r = sb.table('companies').select('name,nzt_status,nzt_end_year,nzt_end_target,sector').not_.is_('nzt_status', 'null').is_('target_description', 'null').execute()
print(json.dumps(r.data, indent=2))
