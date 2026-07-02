"""
Create target_research_log table in Supabase for audit trail.
Run once before launching research workflows.

SQL also saved to: scripts/migrations/001_research_log.sql
"""
import os, requests
from pathlib import Path

ROOT = Path(__file__).parent.parent
for line in (ROOT / '.env.local').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1); os.environ.setdefault(k.strip(), v.strip())

SUPABASE_URL = os.environ['NEXT_PUBLIC_SUPABASE_URL']
SERVICE_KEY = os.environ['SUPABASE_SECRET_KEY']

SQL = """
CREATE TABLE IF NOT EXISTS target_research_log (
    id              uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    company_id      uuid REFERENCES companies(id) ON DELETE CASCADE,
    company_name    text NOT NULL,
    researched_at   timestamptz DEFAULT now(),
    research_task   text,
    finding         text,
    confidence      text CHECK (confidence IN ('high','medium','low','not_found')),
    fields_updated  jsonb,
    sources         text[],
    agent_raw       text
);

CREATE INDEX IF NOT EXISTS idx_research_log_company ON target_research_log(company_id);
CREATE INDEX IF NOT EXISTS idx_research_log_at ON target_research_log(researched_at DESC);
"""

# Save SQL for manual run
migrations = ROOT / 'scripts' / 'migrations'
migrations.mkdir(exist_ok=True)
(migrations / '001_research_log.sql').write_text(SQL, encoding='utf-8')
print('SQL saved to scripts/migrations/001_research_log.sql')
print()
print('To create the table, run this SQL in your Supabase dashboard:')
print('  https://supabase.com/dashboard/project/ahoyjvqvgbmcoydjgzpb/editor')
print()
print(SQL)

# Try to create via API
try:
    headers = {
        'apikey': SERVICE_KEY,
        'Authorization': f'Bearer {SERVICE_KEY}',
        'Content-Type': 'application/json',
    }
    # Try Supabase SQL endpoint
    r = requests.post(
        f'{SUPABASE_URL}/rest/v1/rpc/exec_sql',
        headers=headers,
        json={'query': SQL},
        timeout=10
    )
    if r.status_code == 200:
        print('Table created via API.')
    else:
        print(f'API method not available (status {r.status_code}) — please run SQL manually in dashboard.')
except Exception as e:
    print(f'API attempt failed ({e}) — please run SQL manually in dashboard.')
