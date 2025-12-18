-- 004_cost_tracking.sql
-- Cost tracking and model pricing

ALTER TABLE model_runs ADD COLUMN IF NOT EXISTS tokens_used JSONB;
ALTER TABLE model_runs ADD COLUMN IF NOT EXISTS estimated_cost NUMERIC(10,4);

CREATE TABLE IF NOT EXISTS model_costs (
  id SERIAL PRIMARY KEY,
  model_id INT REFERENCES models(id),
  cost_per_1k_input NUMERIC(10,6),
  cost_per_1k_output NUMERIC(10,6),
  currency VARCHAR(3) DEFAULT 'USD',
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Insert default costs (as of 2024)
-- OpenAI GPT-4o-mini: $0.15/$0.60 per 1M tokens = $0.00015/$0.0006 per 1k
-- Gemini 1.5 Pro: $0.00125/$0.005 per 1k (estimate)
-- Ollama: free (local)

INSERT INTO model_costs (model_id, cost_per_1k_input, cost_per_1k_output)
SELECT id, 0.00015, 0.0006 FROM models WHERE name = 'employee_openai'
ON CONFLICT DO NOTHING;

INSERT INTO model_costs (model_id, cost_per_1k_input, cost_per_1k_output)
SELECT id, 0.00125, 0.005 FROM models WHERE name = 'employee_gemini'
ON CONFLICT DO NOTHING;

INSERT INTO model_costs (model_id, cost_per_1k_input, cost_per_1k_output)
SELECT id, 0.0, 0.0 FROM models WHERE name = 'employee_ollama'
ON CONFLICT DO NOTHING;
