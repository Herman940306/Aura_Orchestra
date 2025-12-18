CREATE TABLE agents (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  role TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE events (
  id UUID PRIMARY KEY,
  agent_id UUID,
  type TEXT,
  payload JSONB,
  created_at TIMESTAMP DEFAULT now()
);
