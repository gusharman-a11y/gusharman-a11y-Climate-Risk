import os
from pathlib import Path
from collections import Counter

for line in Path('C:/Users/angus.harman/Climate-Risk/pollination-bd-tracker/.env.local').read_text().splitlines():
    if '=' in line:
        k, v = line.split('=', 1); os.environ[k.strip()] = v.strip()

from supabase import create_client
sb = create_client(os.environ['NEXT_PUBLIC_SUPABASE_URL'], os.environ['SUPABASE_SECRET_KEY'])

# Sample non-unclassified companies
r = sb.table('companies').select('name,score_overall,score_asrs,score_target_gap,score_risk,score_intent,score_relationship,asrs_group,target_classification,sbti_status').neq('asrs_group', 'Unclassified').neq('sbti_status', 'Targets set').limit(30).execute()

print('Sample scores for non-Unclassified, non-Targets-set companies:')
for c in r.data[:20]:
    print(f"  {c['score_overall']:.2f} | asrs={c['score_asrs']} tg={c['score_target_gap']} | {c['asrs_group']:10} | {(c['sbti_status'] or 'none'):20} | {c['name'][:35]}")

print()
# Count by score bucket
all_c = []
offset = 0
while True:
    r2 = sb.table('companies').select('score_overall,asrs_group,sbti_status').neq('asrs_group', 'Unclassified').neq('sbti_status', 'Targets set').range(offset, offset+999).execute()
    all_c.extend(r2.data)
    if len(r2.data) < 1000: break
    offset += 1000

print(f'Total non-unclassified non-validated: {len(all_c)}')
buckets = Counter(round(c['score_overall'], 1) for c in all_c if c.get('score_overall'))
print('Score distribution:')
for k in sorted(buckets.keys(), reverse=True)[:15]:
    print(f'  {k:.1f}: {buckets[k]} companies')

# What should a Group 1, no target, cold company score?
print()
print('Expected score for Group 1 + No target + Cold:')
sa, stg, sr, si, srel = 5.0, 5.0, 1.0, 1.0, 1.0
w = {"asrs_urgency":0.25,"target_gap":0.30,"risk_signals":0.25,"intent_signals":0.10,"relationship":0.10}
expected = sa*w["asrs_urgency"] + stg*w["target_gap"] + sr*w["risk_signals"] + si*w["intent_signals"] + srel*w["relationship"]
print(f'  {expected:.2f}')
