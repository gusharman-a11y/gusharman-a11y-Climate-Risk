"""Save NGER company climate targets from workflow research to DB."""
import os, re, json
from pathlib import Path

ROOT = Path(__file__).parent.parent
for line in (ROOT / '.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1); os.environ.setdefault(k.strip(), v.strip())
from supabase import create_client
sb = create_client(os.environ['NEXT_PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])

_STRIP = re.compile(r'\b(?:pty|ltd|limited|holdings|holding|group|australia|australian|corporation|corp|inc|plc|metals|energy|resources|services|management|investments|finance|financial)\b', re.I)
def nkey(n):
    n = re.sub(r'[^a-z0-9 ]', ' ', str(n).lower())
    n = _STRIP.sub('', n)
    return re.sub(r'\s+', ' ', n).strip()

TARGETS = [
    {"name":"AGL Energy","target_description":"Net zero Scope 1+2+3 by 2050 (ambition); post-coal-closure net zero Scope 1+2 following FY35 coal exit (90% gross reduction, up to 10% offsets). Interim: 19% gross Scope 1+2 reduction vs FY19 by FY27; 6 GW new renewable/firming by FY30; 60% Scope 3 reduction vs FY19 by FY35.","net_zero_year":2050,"target_year":2027,"target_scope":"Scope 1+2+3","target_classification":"Net zero"},
    {"name":"EnergyAustralia","target_description":"Net zero ambition across Scope 1+2+3 by 2050. Interim: >60% absolute reduction in Scope 1 emissions by 2030.","net_zero_year":2050,"target_year":2030,"target_scope":"Scope 1+2+3","target_classification":"Net zero"},
    {"name":"Stanwell Corporation","target_description":"No corporate net zero or absolute reduction target set. Sustainability commitment framed as reducing emissions intensity of portfolio only.","net_zero_year":None,"target_year":None,"target_scope":"Scope 1","target_classification":"No public target"},
    {"name":"Origin Energy","target_description":"Net zero Scope 1+2+3 equity emissions by 2050. Interim: 20 Mt CO2e absolute reduction in Scope 1+2+3 equity emissions by 2030 (vs FY2019 baseline of 53 Mt); AND 40% reduction in Scope 1+2+3 equity emissions intensity to 40t CO2e/TJ by 2030 (vs FY2019 baseline of 67t CO2e/TJ).","net_zero_year":2050,"target_year":2030,"target_scope":"Scope 1+2+3","target_classification":"Net zero"},
    {"name":"Chevron Australia","target_description":"Scope 1 net zero by 2050 - legally binding regulatory condition on Gorgon and Wheatstone LNG facilities. Corporate interim: 35% reduction in oil and gas GHG intensity by 2028 vs 2016 baseline; zero routine flaring by 2030.","net_zero_year":2050,"target_year":2028,"target_scope":"Scope 1","target_classification":"Net zero"},
    {"name":"Woodside Energy","target_description":"Net zero aspiration by 2050 or sooner for Scope 1+2 (at least 95%) and most relevant Scope 3 emissions. Interim: 30% reduction in net equity Scope 1+2 GHG emissions by 2030 below 2016-2020 average baseline (6.27 Mt CO2e). 15% milestone by 2025 was met.","net_zero_year":2050,"target_year":2030,"target_scope":"Scope 1+2","target_classification":"Net zero"},
    {"name":"Rio Tinto","target_description":"Net zero Scope 1+2 emissions from operations by 2050. Interim: 50% absolute reduction in Scope 1+2 emissions by 2030 vs 2018 baseline (32.6 Mt CO2e).","net_zero_year":2050,"target_year":2030,"target_scope":"Scope 1+2","target_classification":"Net zero"},
    {"name":"BlueScope Steel","target_description":"Net zero Scope 1+2 emissions by 2050 across global operations. Interim: 12% reduction in Scope 1+2 emissions intensity from steelmaking sites by 2030 vs FY2018 baseline; 30% reduction in Scope 1+2 emissions intensity from midstream sites by 2030.","net_zero_year":2050,"target_year":2030,"target_scope":"Scope 1+2","target_classification":"Net zero"},
    {"name":"Glencore","target_description":"Net zero industrial Scope 1+2+3 emissions ambition by end of 2050. Interim: at least 15% reduction by end of 2026; at least 25% by end of 2030; at least 50% by end of 2035 - all vs restated 2019 baseline.","net_zero_year":2050,"target_year":2030,"target_scope":"Scope 1+2+3","target_classification":"Net zero"},
    {"name":"Alcoa","target_description":"Net zero GHG emissions ambition across all global operations by 2050 (Scope 1+2). Interim: 50% reduction in GHG emission intensity (Scope 1+2) from alumina refining and aluminium smelting by 2030 vs 2015 baseline.","net_zero_year":2050,"target_year":2030,"target_scope":"Scope 1+2","target_classification":"Net zero"},
    {"name":"South32","target_description":"Net zero operational Scope 1+2 emissions by 2050; net zero Scope 3 emissions by 2050 (goal). Interim: 50% absolute reduction in Scope 1+2 emissions by FY2035 vs FY2021 baseline.","net_zero_year":2050,"target_year":2035,"target_scope":"Scope 1+2","target_classification":"Net zero"},
    {"name":"Yancoal","target_description":"No net zero or voluntary interim reduction targets set. Complies with Safeguard Mechanism declining baselines only.","net_zero_year":None,"target_year":None,"target_scope":"Scope 1","target_classification":"No public target"},
    {"name":"Anglo American","target_description":"Carbon neutral operations (Scope 1+2) by 2040. Interim: 30% absolute reduction in Scope 1+2 emissions by 2030 vs 2020 baseline; 100% renewable electricity for Australian managed operations from start of 2025.","net_zero_year":2040,"target_year":2030,"target_scope":"Scope 1+2","target_classification":"Net zero"},
    {"name":"Santos","target_description":"Net zero Scope 1 (equity share) by 2040; net zero Scope 2 (equity share) by 2050. Interim: 30% absolute reduction in Scope 1+2 (equity share) by 2030 vs 2019-20 baseline. As of 2024, 26% reduction achieved (84% progress).","net_zero_year":2040,"target_year":2030,"target_scope":"Scope 1+2","target_classification":"Net zero"},
    {"name":"Cement Australia","target_description":"Aspirational net zero by 2050 stated on company website; no formally adopted entity-level target with numeric milestones.","net_zero_year":2050,"target_year":None,"target_scope":"Scope 1","target_classification":"Net zero"},
    {"name":"Fortescue","target_description":"Real Zero (100% elimination of Scope 1+2 without offsets) from Australian Pilbara iron ore operations by 2030. Separate Net Zero Scope 3 target by 2040. Interim: FY25 absolute Scope 1+2 budget of 2.66 Mt CO2e.","net_zero_year":2030,"target_year":2025,"target_scope":"Scope 1+2","target_classification":"Net zero"},
    {"name":"Whitehaven Coal","target_description":"No net zero target set. Interim: 32% reduction in net Scope 1 emissions intensity by FY2030 vs FY2023 baseline (Blackwater, Daunia, Narrabri, Maules Creek).","net_zero_year":None,"target_year":2030,"target_scope":"Scope 1","target_classification":"Reduction target"},
    {"name":"Aurizon","target_description":"Net zero operational Scope 1+2 emissions by 2050. Interim: 10% reduction in operational emissions intensity (kgCO2e per 1,000 net tonne kilometres) by 2030 vs FY2021 baseline.","net_zero_year":2050,"target_year":2030,"target_scope":"Scope 1+2","target_classification":"Net zero"},
    {"name":"Incitec Pivot","target_description":"Net zero GHG emissions by 2050 or sooner (now under Dyno Nobel Limited, ASX:DNL). Interim: 25% absolute Scope 1+2 reduction by 2030 vs 2020 baseline; 50% absolute Scope 1+2 reduction by 2036 vs 2020 baseline. As of FY2025, ~39% like-for-like reduction achieved.","net_zero_year":2050,"target_year":2030,"target_scope":"Scope 1+2","target_classification":"Net zero"},
    {"name":"Orica","target_description":"Net zero GHG emissions ambition covering global Scope 1+2 and material Scope 3 by 2050. Interim: at least 45% reduction in net operational Scope 1+2 emissions by 2030 from 2019 baseline. Separate Scope 3 ambition: 25% reduction by 2035 from 2022 baseline.","net_zero_year":2050,"target_year":2030,"target_scope":"Scope 1+2","target_classification":"Net zero"},
    {"name":"Boral","target_description":"Net zero by 2050. Interim: 46% absolute Scope 1+2 reduction by FY2030 vs FY2019 (SBTi-validated, 1.5C-aligned; under revision to intensity-based target). 22% Scope 3 intensity reduction by FY2030 vs FY2019.","net_zero_year":2050,"target_year":2030,"target_scope":"Scope 1+2","target_classification":"Net zero"},
    {"name":"Pacific National","target_description":"No formal corporate net zero or voluntary interim emissions reduction target. Only binding obligation is Safeguard Mechanism 4.9%/year intensity baseline decline to 2030.","net_zero_year":None,"target_year":None,"target_scope":"Scope 1","target_classification":"No public target"},
    {"name":"Viva Energy","target_description":"Net zero Scope 1+2 across group by 2050. Non-refining operations (Retail, Fuels and Marketing) to reach net zero Scope 1+2 by 2030. Interim: 10% reduction in Scope 1+2 emissions intensity at Geelong Refinery by 2030 vs FY2019 baseline.","net_zero_year":2050,"target_year":2030,"target_scope":"Scope 1+2","target_classification":"Net zero"},
    {"name":"Ampol","target_description":"Net zero absolute Scope 1+2 emissions across Australian operations by 2040 (assumes Lytton refinery no longer operates as a hydrocarbon refinery by 2040). Interim: Convenience Retail 50% absolute Scope 1+2 reduction by 2030 vs 2021 baseline; Fuels and Infrastructure 10% emissions intensity reduction by 2030.","net_zero_year":2040,"target_year":2030,"target_scope":"Scope 1+2","target_classification":"Net zero"},
]

# Load DB
all_db = []
offset = 0
while True:
    r = sb.table('companies').select('id,name').range(offset, offset+999).execute()
    all_db.extend(r.data)
    if len(r.data) < 1000: break
    offset += 1000

by_name = {nkey(c['name']): c for c in all_db}

def find_company(name):
    nk = nkey(str(name))
    if nk in by_name: return by_name[nk]
    prefix = nk[:8]
    if len(prefix) >= 6:
        for db_nk, c in by_name.items():
            if db_nk.startswith(prefix) or nk.startswith(db_nk[:min(8,len(db_nk))]):
                return c
    return None

updated = 0
unmatched = []
for t in TARGETS:
    company = find_company(t['name'])
    if company:
        patch = {k: v for k, v in t.items() if k != 'name' and v is not None}
        sb.table('companies').update(patch).eq('id', company['id']).execute()
        updated += 1
        print(f'  {t["name"]:30} -> {t["target_classification"]} | {str(t.get("net_zero_year") or "")[:4]}')
    else:
        unmatched.append(t['name'])

print(f'\nUpdated: {updated} | Unmatched: {len(unmatched)}')
if unmatched:
    for n in unmatched: print(f'  Unmatched: {n}')
