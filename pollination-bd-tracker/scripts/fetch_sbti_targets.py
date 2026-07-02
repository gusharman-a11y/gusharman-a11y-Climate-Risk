"""
Download SBTi targets-excel.xlsx (per-target detail) and update AU companies.
More granular than companies-excel.xlsx — has scope, base year, % reduction per target.

Run: py -3 pollination-bd-tracker/scripts/fetch_sbti_targets.py
"""
import os, re, requests
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent.parent
DATA = ROOT.parent / 'data'

for line in (ROOT / '.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1); os.environ.setdefault(k.strip(), v.strip())
from supabase import create_client
sb = create_client(os.environ['NEXT_PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])

# ── Download ──────────────────────────────────────────────────────────────────
TARGETS_URL = 'https://files.sciencebasedtargets.org/production/files/targets-excel.xlsx'
COMPANIES_URL = 'https://files.sciencebasedtargets.org/production/files/companies-excel.xlsx'

targets_path = DATA / 'sbti_targets.xlsx'
companies_path = DATA / 'sbti_companies_latest.xlsx'

print('Downloading SBTi targets file...')
r = requests.get(TARGETS_URL, timeout=60)
r.raise_for_status()
targets_path.write_bytes(r.content)
print(f'  {len(r.content)//1024} KB -> {targets_path}')

print('Downloading SBTi companies file...')
r2 = requests.get(COMPANIES_URL, timeout=60)
r2.raise_for_status()
companies_path.write_bytes(r2.content)
print(f'  {len(r2.content)//1024} KB -> {companies_path}')

# ── Inspect targets file ───────────────────────────────────────────────────────
df_t = pd.read_excel(targets_path)
print(f'\nTargets file: {len(df_t)} rows, {len(df_t.columns)} columns')
print('Columns:', list(df_t.columns))

au_t = df_t[df_t['location'].astype(str).str.upper() == 'AUSTRALIA'] if 'location' in df_t.columns else df_t
print(f'\nAU targets: {len(au_t)}')

# ── Inspect companies file ─────────────────────────────────────────────────────
df_c = pd.read_excel(companies_path)
print(f'\nCompanies file: {len(df_c)} rows, {len(df_c.columns)} columns')
print('Columns:', list(df_c.columns))

au_c = df_c[df_c['location'].astype(str).str.upper() == 'AUSTRALIA'] if 'location' in df_c.columns else df_c
committed_c = au_c[au_c['near_term_status'].astype(str).str.lower().str.contains('committed', na=False) &
                   ~au_c['near_term_status'].astype(str).str.lower().str.contains('removed', na=False)]
print(f'AU committed companies: {len(committed_c)}')

# Show first committed company's target detail
if len(committed_c) > 0 and 'company_name' in committed_c.columns:
    first_name = committed_c.iloc[0]['company_name']
    related_targets = au_t[au_t.get('company_name', au_t.columns[0]).astype(str).str.contains(str(first_name)[:10], case=False, na=False)] if len(au_t) > 0 else pd.DataFrame()
    print(f'\nSample company: {first_name}')
    print(f'Targets for this company: {len(related_targets)}')
    if len(related_targets) > 0:
        for col in related_targets.columns:
            val = str(related_targets.iloc[0][col]).strip()
            if val and val not in ('nan', 'None', ''):
                print(f'  {col}: {val[:100]}')
