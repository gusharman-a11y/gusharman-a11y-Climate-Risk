import os, json, re
from pathlib import Path

for line in Path('pollination-bd-tracker/.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip())
from supabase import create_client
sb = create_client(os.environ['NEXT_PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])

raw = Path(r'C:\Users\ANGUS~1.HAR\AppData\Local\Temp\claude\C--Users-angus-harman\8afa0a21-674f-4471-a1f3-e99bd6ccb3ec\tasks\wdy8ocggx.output').read_text(encoding='utf-8')
data = json.loads(raw)
results = data['result']

_STRIP = re.compile(r'\b(?:pty|ltd|limited|holdings|group|australia|australian|corp|inc|plc|airways|partners|trust)\b', re.I)
def nkey(n):
    n = re.sub(r'[^a-z0-9 ]', ' ', str(n).lower())
    n = _STRIP.sub('', n)
    return re.sub(r'\s+', ' ', n).strip()

hot = sb.table('companies').select('id,name').eq('hot_sheet', True).execute().data
hot_map = {nkey(c['name']): c['id'] for c in hot}

def find_id(name):
    nk = nkey(name)
    if nk in hot_map: return hot_map[nk]
    for hk, hid in hot_map.items():
        if nk[:5] == hk[:5] and len(nk) >= 5: return hid
    return None

for item in results:
    cid = find_id(item.get('company', ''))
    if not cid:
        print(f"  [NO MATCH] {item.get('company')}")
        continue
    sb.table('companies').update({'key_contacts': json.dumps(item)}).eq('id', cid).execute()
    ceo = item.get('ceo', {}).get('name', '?')
    cfo = item.get('cfo', {}).get('name', '?')
    sus = item.get('head_of_sustainability', {}).get('name', '?')
    print(f"  [OK] {item.get('company')[:35]} | CEO:{ceo} CFO:{cfo} Sustainability:{sus}")

print(f"\nDone: {len(results)} contacts saved")
