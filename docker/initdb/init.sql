CREATE TABLE IF NOT EXISTS state_logs (
  id BIGSERIAL PRIMARY KEY,
  key TEXT NOT NULL,
  value JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_state_logs_created_at ON state_logs (created_at);
