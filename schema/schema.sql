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

-- UET Foundation: Worker Management
CREATE TABLE IF NOT EXISTS workers (
  worker_id TEXT PRIMARY KEY,
  adapter_type TEXT NOT NULL,
  state TEXT NOT NULL CHECK(state IN ('SPAWNING', 'IDLE', 'BUSY', 'DRAINING', 'TERMINATED')),
  current_task_id TEXT,
  sandbox_path TEXT,
  heartbeat_at TEXT,
  spawned_at TEXT NOT NULL,
  terminated_at TEXT,
  metadata_json TEXT
);

-- UET Foundation: Event Bus
CREATE TABLE IF NOT EXISTS uet_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_type TEXT NOT NULL,
  worker_id TEXT,
  task_id TEXT,
  run_id TEXT,
  workstream_id TEXT,
  timestamp TEXT NOT NULL,
  payload_json TEXT,
  FOREIGN KEY (worker_id) REFERENCES workers(worker_id)
);

-- UET Foundation: Cost Tracking
CREATE TABLE IF NOT EXISTS cost_tracking (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT NOT NULL,
  workstream_id TEXT,
  step_id TEXT,
  worker_id TEXT,
  input_tokens INTEGER DEFAULT 0,
  output_tokens INTEGER DEFAULT 0,
  estimated_cost_usd REAL DEFAULT 0.0,
  actual_cost_usd REAL,
  model_name TEXT,
  timestamp TEXT NOT NULL,
  FOREIGN KEY (worker_id) REFERENCES workers(worker_id)
);

-- UET Foundation: Merge Conflicts
CREATE TABLE IF NOT EXISTS merge_conflicts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT NOT NULL,
  workstream_a TEXT NOT NULL,
  workstream_b TEXT NOT NULL,
  conflicted_files_json TEXT NOT NULL,
  resolution_status TEXT CHECK(resolution_status IN ('PENDING', 'AUTO_RESOLVED', 'AGENT_RESOLVED', 'HUMAN_RESOLVED', 'QUARANTINED')),
  resolution_details_json TEXT,
  created_at TEXT NOT NULL,
  resolved_at TEXT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status);
CREATE INDEX IF NOT EXISTS idx_workstreams_run_status ON workstreams(run_id, status);
CREATE INDEX IF NOT EXISTS idx_step_attempts_rws ON step_attempts(run_id, ws_id, step_name);
CREATE INDEX IF NOT EXISTS idx_errors_rws_sig ON errors(run_id, ws_id, signature);
CREATE INDEX IF NOT EXISTS idx_events_rws_type ON events(run_id, ws_id, event_type);
CREATE INDEX IF NOT EXISTS idx_uet_events_timestamp ON uet_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_uet_events_type ON uet_events(event_type);
CREATE INDEX IF NOT EXISTS idx_cost_run ON cost_tracking(run_id);
CREATE INDEX IF NOT EXISTS idx_workers_state ON workers(state);

