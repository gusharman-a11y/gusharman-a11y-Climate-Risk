"""
Save carbon market DD + news workflow results to DB.
Run after workflow wf_56fd63c8-826 completes.
"""
import os, json, re
from pathlib import Path

for line in Path('pollination-bd-tracker/.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip())
from supabase import create_client
sb = create_client(os.environ['NEXT_PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])

import sys
result_file = sys.argv[1] if len(sys.argv) > 1 else 'carbon_dd_results.json'
raw = Path(result_file).read_text(encoding='utf-8')
data = json.loads(raw)
result = data.get('result', data)
carbon_list = result.get('carbon', [])
news_list = result.get('news', [])

_STRIP = re.compile(r'\b(?:pty|ltd|limited|holdings|holding|group|australia|australian|corporation|corp|inc|plc|services|management|investments|finance|financial|partners|trust|reit|fund|co\b|the)\b', re.I)
def nkey(n):
    n = re.sub(r'[^a-z0-9 ]', ' ', str(n).lower())
    n = _STRIP.sub('', n)
    return re.sub(r'\s+', ' ', n).strip()

# Load hot sheet companies
hot = sb.table('companies').select('id,name').eq('hot_sheet', True).execute().data
hot_map = {nkey(c['name']): c['id'] for c in hot}

def find_id(name):
    nk = nkey(name)
    if nk in hot_map: return hot_map[nk]
    for hk, hid in hot_map.items():
        if nk[:6] == hk[:6] and len(nk) >= 6: return hid
    return None

updated = 0
for item in carbon_list:
    cid = find_id(item.get('company',''))
    if not cid:
        print(f"  [NO MATCH] {item.get('company')}")
        continue
    sb.table('companies').update({'carbon_market_research': json.dumps(item)}).eq('id', cid).execute()
    print(f"  [CARBON OK] {item.get('company')} → confidence={item.get('confidence')}")
    updated += 1

for item in news_list:
    cid = find_id(item.get('company',''))
    if not cid:
        print(f"  [NO MATCH] {item.get('company')}")
        continue
    sb.table('companies').update({'news_6m_summary': json.dumps(item)}).eq('id', cid).execute()
    print(f"  [NEWS OK] {item.get('company')} → {len(item.get('news_items',[]))} items")

print(f"\nDone: {updated} carbon records, {len(news_list)} news records saved")
