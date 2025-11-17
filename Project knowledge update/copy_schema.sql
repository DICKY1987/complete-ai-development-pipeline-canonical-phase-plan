-- SQLite schema for the AI Development Pipeline state store
-- Idempotent DDL with essential tables, indexes, and FKs

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_meta (
  key TEXT PRIMARY KEY,
  value TEXT
);

CREATE TABLE IF NOT EXISTS runs (
  run_id TEXT PRIMARY KEY,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  metadata_json TEXT
);

CREATE TABLE IF NOT EXISTS workstreams (
  ws_id TEXT PRIMARY KEY,
  run_id TEXT REFERENCES runs(run_id) ON DELETE SET NULL,
  status TEXT NOT NULL,
  depends_on TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  metadata_json TEXT
);

CREATE TABLE IF NOT EXISTS step_attempts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
  ws_id TEXT NOT NULL REFERENCES workstreams(ws_id) ON DELETE CASCADE,
  step_name TEXT NOT NULL,
  status TEXT NOT NULL,
  started_at TEXT,
  completed_at TEXT,
  result_json TEXT
);

CREATE TABLE IF NOT EXISTS errors (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT REFERENCES runs(run_id) ON DELETE SET NULL,
  ws_id TEXT REFERENCES workstreams(ws_id) ON DELETE SET NULL,
  step_name TEXT,
  error_code TEXT,
  signature TEXT,
  message TEXT,
  context_json TEXT,
  count INTEGER DEFAULT 1,
  first_seen_at TEXT,
  last_seen_at TEXT
);

CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT NOT NULL,
  run_id TEXT REFERENCES runs(run_id) ON DELETE SET NULL,
  ws_id TEXT REFERENCES workstreams(ws_id) ON DELETE SET NULL,
  event_type TEXT NOT NULL,
  payload_json TEXT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status);
CREATE INDEX IF NOT EXISTS idx_workstreams_run_status ON workstreams(run_id, status);
CREATE INDEX IF NOT EXISTS idx_step_attempts_rws ON step_attempts(run_id, ws_id, step_name);
CREATE INDEX IF NOT EXISTS idx_errors_rws_sig ON errors(run_id, ws_id, signature);
CREATE INDEX IF NOT EXISTS idx_events_rws_type ON events(run_id, ws_id, event_type);

