-- 001_init_schema.sql
-- Aura Orchestra Core Schema
-- Establishes foundational tables for orchestration, audit, and governance

-- Projects: Top-level organizational unit
CREATE TABLE IF NOT EXISTS projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Orchestra Runs: Execution instances
CREATE TABLE IF NOT EXISTS orchestra_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id),
  manager_id TEXT NOT NULL,
  status TEXT NOT NULL,
  confidence_score NUMERIC,
  started_at TIMESTAMPTZ DEFAULT NOW(),
  finished_at TIMESTAMPTZ
);

-- Task Queue: Work items
CREATE TABLE IF NOT EXISTS task_queue (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id UUID REFERENCES orchestra_runs(id),
  assigned_agent TEXT,
  status TEXT NOT NULL,
  priority INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- Jobs: Individual work units (from Batch 2 spec)
CREATE TABLE IF NOT EXISTS jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id),
  role TEXT NOT NULL,
  assigned_model TEXT,
  status TEXT NOT NULL DEFAULT 'QUEUED',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  retry_count INT DEFAULT 0
);

-- Job Events: Audit trail for job lifecycle
CREATE TABLE IF NOT EXISTS job_events (
  id BIGSERIAL PRIMARY KEY,
  job_id UUID REFERENCES jobs(id),
  event_type TEXT NOT NULL,
  details JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent Activity Logs: Model worker telemetry
CREATE TABLE IF NOT EXISTS agent_activity_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id TEXT NOT NULL,
  task_id UUID,
  message TEXT,
  severity TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit Events: System-wide audit trail
CREATE TABLE IF NOT EXISTS audit_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source TEXT,
  severity TEXT,
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit Log: Governance actions (from existing schema)
CREATE TABLE IF NOT EXISTS audit_log (
  id SERIAL PRIMARY KEY,
  actor TEXT NOT NULL,
  action TEXT NOT NULL,
  details JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Director Actions: Human oversight
CREATE TABLE IF NOT EXISTS director_actions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  director_id TEXT,
  action TEXT,
  target_id UUID,
  reason TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Project State: Current system state (from existing schema)
CREATE TABLE IF NOT EXISTS project_state (
  id SERIAL PRIMARY KEY,
  phase TEXT NOT NULL,
  status TEXT NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Archived Jobs: Completed work with retention
CREATE TABLE IF NOT EXISTS archived_jobs (
  id UUID PRIMARY KEY,
  project_id UUID,
  final_status TEXT,
  archived_at TIMESTAMPTZ DEFAULT NOW(),
  retention_until TIMESTAMPTZ
);

-- Job Validation Ticks: Test/validation results
CREATE TABLE IF NOT EXISTS job_validation_ticks (
  id BIGSERIAL PRIMARY KEY,
  job_id UUID REFERENCES jobs(id),
  tick_type TEXT NOT NULL,
  result JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
