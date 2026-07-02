import os
from pathlib import Path
for line in Path('pollination-bd-tracker/.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip())
from supabase import create_client
sb = create_client(os.environ['NEXT_PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])

# Remove false positives from hot sheet
# ACDC METALS - not CDC Data Centres
# QANTAS AIRWAYS LIMITED - bond issuer sub, keep "Qantas" (the operating entry)
r = sb.table('companies').select('id,name,hot_sheet').in_('name', [
    'ACDC METALS LTD', 'QANTAS AIRWAYS LIMITED'
]).execute()

for c in r.data:
    sb.table('companies').update({'hot_sheet': False, 'pipeline_stage': None}).eq('id', c['id']).execute()
    print(f"Removed: {c['name']}")

# Verify final hot sheet
final = sb.table('companies').select('name,hot_sheet,pipeline_stage,relationship_status').eq('hot_sheet', True).execute()
print(f"\nFinal hot sheet ({len(final.data)} companies):")
for c in final.data:
    print(f"  {c['name']}")
