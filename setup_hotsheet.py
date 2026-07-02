"""
Mark the top 10 hot sheet companies, set pipeline_stage for them,
and clear pipeline_stage for everyone else.
"""
import os, re
from pathlib import Path

for line in Path('pollination-bd-tracker/.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip())
from supabase import create_client
sb = create_client(os.environ['NEXT_PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])

HOT_10 = [
    'SOUTH32',
    'STOCKLAND',
    'DOWNER EDI',
    'INGHAMS',
    'COLES',
    'AMPOL',
    'QANTAS',
    'RIO TINTO',
    'CDC',
    'BHP',
]

def matches(name, term):
    return term.lower() in name.lower()

# Get all companies
all_cos = []
offset = 0
while True:
    r = sb.table('companies').select('id,name,pipeline_stage,hot_sheet').range(offset, offset+999).execute()
    all_cos.extend(r.data)
    if len(r.data) < 1000: break
    offset += 1000

hot_ids = []
for c in all_cos:
    if any(matches(c['name'], t) for t in HOT_10):
        hot_ids.append(c['id'])
        print(f"  HOT: {c['name']}")

print(f"\n{len(hot_ids)} companies matched")

# Mark hot_sheet = true for the 10, false for everyone else
sb.table('companies').update({'hot_sheet': True, 'pipeline_stage': 'prospect'}).in_('id', hot_ids).execute()

# Clear pipeline for non-hot companies that have a pipeline_stage
other_pipeline = [c['id'] for c in all_cos if c['id'] not in hot_ids and c.get('pipeline_stage')]
if other_pipeline:
    sb.table('companies').update({'pipeline_stage': None, 'hot_sheet': False}).in_('id', other_pipeline).execute()
    print(f"Cleared pipeline_stage for {len(other_pipeline)} other companies")

# Clear hot_sheet for non-hot
other_ids = [c['id'] for c in all_cos if c['id'] not in hot_ids]
# Do in batches of 500
for i in range(0, len(other_ids), 500):
    sb.table('companies').update({'hot_sheet': False}).in_('id', other_ids[i:i+500]).execute()

print("Done")
