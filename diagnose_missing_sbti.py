import os, re, pandas as pd
from pathlib import Path

DATA = Path('data')
df = pd.read_excel(DATA / 'sbti_targets.xlsx')
au = df[df['location'].astype(str).str.upper() == 'AUSTRALIA'].copy()

_STRIP = re.compile(r'\b(?:pty|ltd|limited|holdings|holding|group|australia|australian|corporation|corp|inc|plc|services|management|investments|finance|financial|partners|partnership)\b', re.I)
def nkey(n):
    n = re.sub(r'[^a-z0-9 ]', ' ', str(n).lower())
    n = _STRIP.sub('', n)
    return re.sub(r'\s+', ' ', n).strip()

MISSING = [
    'ADHERIS HEALTH LIMITED', 'BANK OF QUEENSLAND LIMITED.', 'CLEAN TEQ WATER LIMITED',
    'CRITICA LIMITED', 'CRITICAL RESOURCES LIMITED', 'CSL FINANCE PLC',
    'DEXUS CONVENIENCE RETAIL REIT', 'DEXUS INDUSTRIA REIT.', 'BP CAPITAL MARKETS P.L.C.',
    'ENERGY RESOURCES OF AUSTRALIA LIMITED', 'GREAT BOULDER RESOURCES LIMITED',
    'GREAT DIRT RESOURCES LTD', 'GREAT DIVIDE MINING LTD', 'GREAT NORTHERN MINERALS LIMITED',
    'GREAT SOUTHERN MINING LIMITED', 'INVESTIGATOR SILVER LIMITED', 'INVESTOR CENTRE LIMITED',
    'INVESTSMART GROUP LIMITED', 'LOCALITY PLANNING ENERGY HOLDINGS LIMITED',
]

sbti_nkeys = {nkey(n): n for n in au['company_name'].astype(str).tolist()}

for db_name in MISSING:
    nk = nkey(db_name)
    if nk in sbti_nkeys:
        sbti_match = sbti_nkeys[nk]
        rows = au[au['company_name'] == sbti_match]
        wordings = [str(w) for w in rows['full_target_language'].tolist() if str(w) not in ('nan','None','')]
        statuses = rows['status'].astype(str).tolist()
        print(f'[MATCHED] {db_name[:45]} -> {sbti_match}')
        print(f'  status: {statuses}')
        print(f'  wording: {[w[:80] for w in wordings] or "(empty)"}')
    else:
        fuzzy = [(nk2, n) for nk2, n in sbti_nkeys.items() if nk[:5] in nk2]
        print(f'[NO MATCH] {db_name[:45]}  nkey={nk!r}')
        if fuzzy:
            print(f'  possible: {[n for _,n in fuzzy[:3]]}')
