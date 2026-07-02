import os
from pathlib import Path
for line in Path('pollination-bd-tracker/.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1); os.environ.setdefault(k.strip(), v.strip())
from supabase import create_client
sb = create_client(os.environ['NEXT_PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])
try:
    r = sb.table('target_research_log').select('id').limit(1).execute()
    print('target_research_log table EXISTS — ready for audit trail')
except Exception as e:
    print(f'Table NOT found: {e}')
    print()
    print('Please run this SQL in the Supabase dashboard:')
    print('https://supabase.com/dashboard/project/ahoyjvqvgbmcoydjgzpb/editor')
