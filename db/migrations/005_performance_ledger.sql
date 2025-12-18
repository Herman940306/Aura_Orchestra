-- 005_performance_ledger.sql
-- Performance tracking and governance (Accountant)

CREATE TABLE IF NOT EXISTS model_performance (
  id BIGSERIAL PRIMARY KEY,
  model_name TEXT NOT NULL,
  job_id UUID,
  score NUMERIC(5,2),
  penalties TEXT[],
  error_severity TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_model_performance_model ON model_performance(model_name);
CREATE INDEX IF NOT EXISTS idx_model_performance_created ON model_performance(created_at DESC);

-- Governance fields
ALTER TABLE models ADD COLUMN IF NOT EXISTS suspended BOOLEAN DEFAULT FALSE;
ALTER TABLE models ADD COLUMN IF NOT EXISTS suspension_reason TEXT;
ALTER TABLE models ADD COLUMN IF NOT EXISTS warnings_count INT DEFAULT 0;
ALTER TABLE models ADD COLUMN IF NOT EXISTS last_warning_at TIMESTAMPTZ;
