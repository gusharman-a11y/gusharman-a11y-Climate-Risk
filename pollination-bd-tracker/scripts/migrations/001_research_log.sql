
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
