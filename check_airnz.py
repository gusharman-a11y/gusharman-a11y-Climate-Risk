import os, re, pandas as pd
from pathlib import Path

# Check source file
df = pd.read_excel(Path('data/sbti_targets.xlsx'))
airnz = df[df['company_name'].astype(str).str.contains('Air New Zealand', case=False, na=False)]
print('=== SBTi source file ===')
print(airnz[['company_name','action','status','target','full_target_language']].to_string())

# Check DB
for line in Path('pollination-bd-tracker/.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip())
from supabase import create_client
sb = create_client(os.environ['NEXT_PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])
r = sb.table('companies').select('name,sbti_status,target_classification,target_description,sbti_target_text').ilike('name', '%air new zealand%').execute()
print('\n=== DB records ===')
for c in r.data:
    print(f'  name: {c["name"]}')
    print(f'  sbti_status: {c.get("sbti_status")}')
    print(f'  target_classification: {c.get("target_classification")}')
    print(f'  target_description: {(c.get("target_description") or "")[:100]}')
