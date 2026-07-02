"""
Master target update pipeline for the BD Tracker.
Run this whenever you want to refresh all climate target and emissions data.

Usage:
  py -3 pollination-bd-tracker/scripts/update_targets.py          # full run
  py -3 pollination-bd-tracker/scripts/update_targets.py --sbti   # SBTi only
  py -3 pollination-bd-tracker/scripts/update_targets.py --nger   # NGER only
  py -3 pollination-bd-tracker/scripts/update_targets.py --score  # rescore only

Data sources and their cadence:
  SBTi companies list    -> download from sciencebasedtargets.org  (weekly)
  CER NGER emissions     -> download from cer.gov.au               (annually, Feb)
  Rescore                -> always run after any data update

Steps in order:
  1. Download latest SBTi Excel -> data/sbti_companies.xlsx
  2. Match SBTi companies to DB -> updates sbti_status, sbti_date_updated
  3. Backfill SBTi target text  -> updates sbti_target_text
  4. Download CER NGER CSV      -> updates nger_scope1_tco2e, safeguard_covered
  5. Rescore all companies      -> updates score_overall and sub-scores
"""
import os, sys, re, io, argparse
from pathlib import Path
import requests
import pandas as pd

ROOT = Path(__file__).parent.parent
DATA = ROOT.parent / 'data'

for line in (ROOT / '.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1); os.environ.setdefault(k.strip(), v.strip())

from supabase import create_client
sb = create_client(os.environ['NEXT_PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])

HEADERS = {'User-Agent': 'Mozilla/5.0 (BD-Tracker/1.0)'}

_STRIP = re.compile(
    r'\b(?:corporation|corp|incorporated|inc|limited|ltd|group|holdings|holding|'
    r'company|co|plc|pte|australia|australian|pty|metals|energy|resources|services|'
    r'management|investments|finance|financial)\b', re.I
)
def nkey(n):
    n = re.sub(r'[^a-z0-9 ]', ' ', str(n).lower())
    n = _STRIP.sub('', n)
    return re.sub(r'\s+', ' ', n).strip()

def normalise_abn(abn):
    if not abn or str(abn) in ('nan', 'None', ''): return None
    return re.sub(r'\D', '', str(abn)).zfill(11)

def load_db_companies():
    print('  Loading DB companies...')
    all_db = []
    offset = 0
    while True:
        r = sb.table('companies').select('id,name,abn').range(offset, offset+999).execute()
        all_db.extend(r.data)
        if len(r.data) < 1000: break
        offset += 1000
    print(f'  Loaded {len(all_db)} companies from DB')
    return all_db

def build_lookup(all_db):
    by_abn = {normalise_abn(c['abn']): c for c in all_db if c.get('abn')}
    by_name = {nkey(c['name']): c for c in all_db}
    return by_abn, by_name

def find_company(name, abn, by_abn, by_name):
    if abn:
        norm = normalise_abn(abn)
        if norm and norm in by_abn:
            return by_abn[norm]
    nk = nkey(str(name))
    if nk in by_name:
        return by_name[nk]
    prefix = nk[:8]
    if len(prefix) >= 6:
        for db_nk, c in by_name.items():
            if db_nk.startswith(prefix) or nk.startswith(db_nk[:min(8,len(db_nk))]):
                return c
    return None

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: Download latest SBTi data
# ─────────────────────────────────────────────────────────────────────────────
def step_download_sbti():
    print('\n[1/5] Downloading latest SBTi companies list...')
    # SBTi hosts the file at different URLs — try each in order
    urls = [
        'https://sciencebasedtargets.org/resources/files/SBTi-Companies.xlsx',
        'https://sciencebasedtargets.org/resources/files/SBTiCompanies.xlsx',
        'https://sciencebasedtargets.org/resources/files/companies.xlsx',
    ]
    for url in urls:
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            if r.status_code == 200 and len(r.content) > 10000:
                out = DATA / 'sbti_companies.xlsx'
                out.write_bytes(r.content)
                df = pd.read_excel(out)
                au = df[df['location'] == 'Australia'] if 'location' in df.columns else df
                print(f'  Downloaded {len(df)} companies ({len(au)} AU) -> {out}')
                return True
        except Exception as e:
            print(f'  {url}: {e}')
    print('  WARNING: Could not download fresh SBTi data. Using existing file.')
    if (DATA / 'sbti_companies.xlsx').exists():
        df = pd.read_excel(DATA / 'sbti_companies.xlsx')
        au = df[df['location'] == 'Australia']
        print(f'  Using cached file: {len(df)} companies ({len(au)} AU)')
        return True
    print('  ERROR: No SBTi file available.')
    return False

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 + 3: Match SBTi to DB and backfill target text
# ─────────────────────────────────────────────────────────────────────────────
def step_update_sbti():
    print('\n[2/5] Matching SBTi companies to DB...')
    sbti_file = DATA / 'sbti_companies.xlsx'
    if not sbti_file.exists():
        print('  ERROR: sbti_companies.xlsx not found. Run step 1 first.')
        return

    df = pd.read_excel(sbti_file)
    au = df[df['location'] == 'Australia'].copy() if 'location' in df.columns else df.copy()
    print(f'  AU companies in SBTi file: {len(au)}')

    all_db = load_db_companies()
    by_abn, by_name = build_lookup(all_db)

    updated = 0
    unmatched = []
    for _, row in au.iterrows():
        name = str(row.get('company_name', '')).strip()
        if not name or name == 'nan': continue

        isin = str(row.get('isin', '') or '')
        lei = str(row.get('lei', '') or '')
        status = str(row.get('near_term_status', '') or '').strip()
        classification = str(row.get('near_term_target_classification', '') or '').strip()
        date_updated = str(row.get('date_updated', '') or row.get('action_date', '') or '').strip()
        target_text = str(row.get('full_target_language', '') or '').strip()
        if target_text == 'nan': target_text = ''

        company = find_company(name, None, by_abn, by_name)
        if company:
            patch = {}
            if status and status != 'nan': patch['sbti_status'] = status
            # sbti_target_classification is not a DB column; skip
            if date_updated and date_updated != 'nan': patch['sbti_date_updated'] = date_updated[:10]
            if target_text: patch['sbti_target_text'] = target_text[:2000]
            if patch:
                sb.table('companies').update(patch).eq('id', company['id']).execute()
                updated += 1
                if updated <= 5:
                    print(f'  Matched: {name[:45]:47} -> {status}')
        else:
            unmatched.append(name)

    print(f'  Updated: {updated} | Unmatched: {len(unmatched)}')
    if unmatched:
        print('  Top unmatched:')
        for n in unmatched[:10]:
            print(f'    {n}')

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: Download and ingest CER NGER data (annual — Feb each year)
# ─────────────────────────────────────────────────────────────────────────────
def step_update_nger():
    print('\n[3/5] Downloading CER NGER 2024-25 data...')
    nger_url = 'https://cer.gov.au/document/greenhouse-and-energy-information-registered-corporation-2024-25-0'
    safeguard_url = 'https://cer.gov.au/document/national-greenhouse-and-energy-register-responsible-emitters-2024-25-0'
    baselines_url = 'https://cer.gov.au/document/baselines-and-emissions-table-2024-25'

    def fetch(url, label):
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            r.raise_for_status()
            try:
                return pd.read_csv(io.BytesIO(r.content), encoding='utf-8-sig', thousands=',')
            except Exception:
                return pd.read_csv(io.BytesIO(r.content), encoding='latin-1', thousands=',')
        except Exception as e:
            print(f'  WARNING: Could not fetch {label}: {e}')
            # Try cached version
            cached = DATA / f'cer_{label}.csv'
            if cached.exists():
                print(f'  Using cached {cached.name}')
                return pd.read_csv(cached, encoding='utf-8-sig', thousands=',')
            return None

    nger = fetch(nger_url, 'nger_2024_25')
    safeguard = fetch(baselines_url, 'safeguard_baselines_2024_25')

    if nger is None and safeguard is None:
        print('  ERROR: No NGER data available.')
        return

    all_db = load_db_companies()
    by_abn, by_name = build_lookup(all_db)

    # Update NGER emissions
    if nger is not None:
        # Save cache
        nger.to_csv(DATA / 'cer_nger_2024_25.csv', index=False)
        print(f'  NGER file: {len(nger)} rows, columns: {list(nger.columns[:5])}')

        name_col = next((c for c in nger.columns if 'organisation' in c.lower() or 'name' in c.lower()), nger.columns[0])
        abn_col = next((c for c in nger.columns if 'abn' in c.lower() or 'identifying' in c.lower()), None)
        s1_col = next((c for c in nger.columns if 'scope 1' in c.lower()), None)
        s2_col = next((c for c in nger.columns if 'scope 2' in c.lower()), None)

        nger_updated = 0
        for _, row in nger.iterrows():
            name = str(row.get(name_col, '')).strip()
            if not name or name == 'nan': continue
            abn = str(row.get(abn_col, '') or '') if abn_col else None
            try: s1 = float(str(row.get(s1_col, '') or '').replace(',', '')) if s1_col else None
            except: s1 = None
            try: s2 = float(str(row.get(s2_col, '') or '').replace(',', '')) if s2_col else None
            except: s2 = None

            company = find_company(name, abn, by_abn, by_name)
            if company:
                patch = {'nger_year': '2024-25'}
                if s1 and s1 > 0: patch['nger_scope1_tco2e'] = s1
                if s2 and s2 > 0: patch['nger_scope2_tco2e'] = s2
                if abn: patch['abn'] = normalise_abn(abn)
                sb.table('companies').update(patch).eq('id', company['id']).execute()
                nger_updated += 1
        print(f'  NGER: updated {nger_updated} companies')

    # Update Safeguard coverage
    if safeguard is not None:
        safeguard.to_csv(DATA / 'cer_safeguard_baselines_2024_25.csv', index=False)
        emitter_col = next((c for c in safeguard.columns if 'emitter' in c.lower() or 'responsible' in c.lower() or 'operator' in c.lower()), safeguard.columns[0])
        baseline_col = next((c for c in safeguard.columns if 'baseline' in c.lower()), None)

        sg_updated = 0
        seen = set()
        for _, row in safeguard.iterrows():
            emitter = str(row.get(emitter_col, '')).strip()
            if not emitter or emitter == 'nan' or emitter in seen: continue
            seen.add(emitter)
            try: baseline = float(str(row.get(baseline_col, '') or '').replace(',', '')) if baseline_col else None
            except: baseline = None
            company = find_company(emitter, None, by_abn, by_name)
            if company:
                patch = {'safeguard_covered': True}
                if baseline and baseline > 0: patch['safeguard_baseline'] = baseline
                sb.table('companies').update(patch).eq('id', company['id']).execute()
                sg_updated += 1
        print(f'  Safeguard: marked {sg_updated} companies as covered')

# ─────────────────────────────────────────────────────────────────────────────
# STEP 5: Rescore all companies
# ─────────────────────────────────────────────────────────────────────────────
def step_rescore():
    print('\n[4/5] Rescoring all companies...')
    import subprocess
    result = subprocess.run(
        ['py', '-3', str(ROOT / 'scripts' / 'enrich_database.py')],
        capture_output=True, text=True, cwd=ROOT.parent
    )
    if result.returncode == 0:
        # Print last 10 lines of output
        lines = result.stdout.strip().split('\n')
        for line in lines[-10:]:
            print(f'  {line}')
    else:
        print(f'  ERROR: {result.stderr[-500:]}')

# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='Update all climate target data')
    parser.add_argument('--sbti', action='store_true', help='SBTi update only')
    parser.add_argument('--nger', action='store_true', help='NGER/CER update only')
    parser.add_argument('--score', action='store_true', help='Rescore only')
    args = parser.parse_args()

    run_all = not (args.sbti or args.nger or args.score)

    print('=== BD Tracker: Target Update Pipeline ===')
    print(f'Date: 2026-06-23')

    if run_all or args.sbti:
        step_download_sbti()
        step_update_sbti()

    if run_all or args.nger:
        step_update_nger()

    if run_all or args.score:
        step_rescore()

    print('\n=== Done ===')
    print('Cadence reminder:')
    print('  SBTi:  run weekly  (py -3 scripts/update_targets.py --sbti)')
    print('  NGER:  run in Feb  (py -3 scripts/update_targets.py --nger)')
    print('  Score: run after any data change  (py -3 scripts/update_targets.py --score)')

if __name__ == '__main__':
    main()
