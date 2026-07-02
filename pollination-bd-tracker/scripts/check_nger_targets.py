import os
from pathlib import Path
for line in Path('pollination-bd-tracker/.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k,v=line.split('=',1); os.environ.setdefault(k.strip(),v.strip())
from supabase import create_client
sb = create_client(os.environ['NEXT_PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])

all_c = []
offset = 0
while True:
    r = sb.table('companies').select('name,nger_scope1_tco2e,sbti_status,target_description,target_classification,net_zero_year').range(offset, offset+999).execute()
    all_c.extend(r.data)
    if len(r.data) < 1000: break
    offset += 1000

nger = [c for c in all_c if c.get('nger_scope1_tco2e')]
print(f'Total companies with NGER data: {len(nger)}')
print()

has_sbti = [c for c in nger if c.get('sbti_status') and c['sbti_status'] != 'Commitment removed']
has_desc = [c for c in nger if c.get('target_description')]
has_class = [c for c in nger if c.get('target_classification')]
has_nz = [c for c in nger if c.get('net_zero_year')]

has_any = set(c['name'] for c in has_sbti) | set(c['name'] for c in has_desc) | set(c['name'] for c in has_class) | set(c['name'] for c in has_nz)

print(f'Have SBTi target:           {len(has_sbti)}')
print(f'Have target description:    {len(has_desc)}')
print(f'Have target classification: {len(has_class)}')
print(f'Have net zero year:         {len(has_nz)}')
print(f'Have ANY target data:       {len(has_any)}')
print(f'Have NO target data:        {len(nger) - len(has_any)}')
print()

no_target = sorted([c for c in nger if c['name'] not in has_any], key=lambda x: x['nger_scope1_tco2e'] or 0, reverse=True)
print(f'Top {min(20,len(no_target))} NGER companies with NO target data (by emissions):')
for c in no_target[:20]:
    s1 = c['nger_scope1_tco2e'] or 0
    print(f'  {s1:>12,.0f} tCO2e  {c["name"]}')
