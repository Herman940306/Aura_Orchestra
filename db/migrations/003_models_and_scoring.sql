-- 003_models_and_scoring.sql
-- Models registry and scoring history

CREATE TABLE IF NOT EXISTS models (
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,         -- employee_ollama, employee_openai, employee_gemini
  kind TEXT NOT NULL,                -- local | cloud
  endpoint TEXT,                     -- service URL or local socket
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS model_runs (
  id BIGSERIAL PRIMARY KEY,
  model_id INT REFERENCES models(id),
  job_id UUID,                     -- Loose reference to jobs(id) or string if needed
  project_id INT,
  success BOOLEAN,
  confidence NUMERIC,       -- claimed or computed confidence
  score NUMERIC,            -- final computed score from Accountant
  details JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS model_scores (
  id BIGSERIAL PRIMARY KEY,
  model_id INT REFERENCES models(id),
  window_start TIMESTAMPTZ,
  window_end TIMESTAMPTZ,
  avg_score NUMERIC,
  tasks_completed INT,
  promotions INT DEFAULT 0,
  penalties INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS promotions (
  id BIGSERIAL PRIMARY KEY,
  model_id INT REFERENCES models(id),
  action TEXT, -- promote | demote | restrict | restore
  reason TEXT,
  performed_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS model_artifacts (
  id BIGSERIAL PRIMARY KEY,
  job_id UUID,
  model_id INT REFERENCES models(id),
  artifact_type TEXT,   -- diff, patch, result, docs
  artifact JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);
