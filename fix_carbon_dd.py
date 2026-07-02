import os, json
from pathlib import Path

for line in Path('pollination-bd-tracker/.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip())
from supabase import create_client
sb = create_client(os.environ['NEXT_PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])

data = json.loads(Path('carbon_dd_results.json').read_text(encoding='utf-8'))

# BHP carbon
bhp_carbon = next((c for c in data['carbon'] if 'BHP' in c.get('company','')), None)
# Ampol news
ampol_news = next((n for n in data['news'] if 'Ampol' in n.get('company','')), None)

if bhp_carbon:
    r = sb.table('companies').update({'carbon_market_research': json.dumps(bhp_carbon)}).ilike('name', 'BHP%').eq('hot_sheet', True).execute()
    print(f"BHP carbon saved: {bhp_carbon.get('confidence')}")

if ampol_news:
    r = sb.table('companies').update({'news_6m_summary': json.dumps(ampol_news)}).ilike('name', 'AMPOL%').eq('hot_sheet', True).execute()
    print(f"Ampol news saved: {len(ampol_news.get('news_items',[]))} items")

print("Done")
