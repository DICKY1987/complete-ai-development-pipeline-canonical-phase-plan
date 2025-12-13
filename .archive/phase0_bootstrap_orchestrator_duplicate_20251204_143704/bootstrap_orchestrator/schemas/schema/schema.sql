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

-- UI Infrastructure: File Lifecycle Tracking
CREATE TABLE IF NOT EXISTS file_lifecycle (
  file_id TEXT PRIMARY KEY,
  current_path TEXT NOT NULL,
  origin_path TEXT,
  file_role TEXT CHECK(file_role IN ('code', 'spec', 'plan', 'test', 'config', 'docs', 'asset', 'other')),
  current_state TEXT NOT NULL CHECK(current_state IN ('discovered', 'classified', 'intake', 'routed', 'processing', 'in_flight', 'awaiting_review', 'awaiting_commit', 'committed', 'quarantined')),
  workstream_id TEXT,
  job_id TEXT,
  run_id TEXT,
  first_seen TEXT NOT NULL,
  last_processed TEXT,
  committed_sha TEXT,
  committed_repo_path TEXT,
  quarantine_reason TEXT,
  quarantine_folder TEXT,
  metadata_json TEXT,
  FOREIGN KEY (workstream_id) REFERENCES workstreams(ws_id) ON DELETE SET NULL,
  FOREIGN KEY (run_id) REFERENCES runs(run_id) ON DELETE SET NULL
);

-- UI Infrastructure: File State History
CREATE TABLE IF NOT EXISTS file_state_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  file_id TEXT NOT NULL,
  state TEXT NOT NULL,
  timestamp TEXT NOT NULL,
  FOREIGN KEY (file_id) REFERENCES file_lifecycle(file_id) ON DELETE CASCADE
);

-- UI Infrastructure: File Tool Touch History
CREATE TABLE IF NOT EXISTS file_tool_touches (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  file_id TEXT NOT NULL,
  tool_id TEXT NOT NULL,
  tool_name TEXT NOT NULL,
  action TEXT NOT NULL,
  status TEXT NOT NULL,
  error_message TEXT,
  timestamp TEXT NOT NULL,
  FOREIGN KEY (file_id) REFERENCES file_lifecycle(file_id) ON DELETE CASCADE
);

-- UI Infrastructure: Enhanced Error Records
CREATE TABLE IF NOT EXISTS error_records (
  error_id TEXT PRIMARY KEY,
  entity_type TEXT NOT NULL,
  file_id TEXT,
  job_id TEXT,
  ws_id TEXT,
  tool_id TEXT,
  run_id TEXT,
  plugin TEXT,
  severity TEXT CHECK(severity IN ('warning', 'error', 'critical')),
  category TEXT CHECK(category IN ('syntax', 'config', 'network', 'tool_timeout', 'ai_refusal', 'validation_failed', 'build_failed', 'test_failed', 'merge_conflict', 'permission_denied', 'unknown')),
  human_message TEXT NOT NULL,
  technical_details TEXT,
  recommendation TEXT,
  first_seen TEXT NOT NULL,
  last_seen TEXT NOT NULL,
  occurrence_count INTEGER DEFAULT 1,
  quarantine_path TEXT,
  can_retry INTEGER DEFAULT 1,
  auto_fix_available INTEGER DEFAULT 0,
  FOREIGN KEY (file_id) REFERENCES file_lifecycle(file_id) ON DELETE SET NULL,
  FOREIGN KEY (ws_id) REFERENCES workstreams(ws_id) ON DELETE SET NULL,
  FOREIGN KEY (run_id) REFERENCES runs(run_id) ON DELETE SET NULL
);

-- UI Infrastructure: Tool Health Metrics
CREATE TABLE IF NOT EXISTS tool_health_metrics (
  tool_id TEXT PRIMARY KEY,
  display_name TEXT NOT NULL,
  category TEXT CHECK(category IN ('ai_editor', 'test_runner', 'scm', 'linter', 'error_engine', 'build_tool', 'other')),
  version TEXT,
  status TEXT CHECK(status IN ('healthy', 'degraded', 'unreachable', 'circuit_open', 'unknown')),
  status_reason TEXT,
  last_successful_invocation TEXT,
  requests_5min INTEGER DEFAULT 0,
  requests_15min INTEGER DEFAULT 0,
  requests_60min INTEGER DEFAULT 0,
  success_count INTEGER DEFAULT 0,
  failure_count INTEGER DEFAULT 0,
  success_rate REAL DEFAULT 0.0,
  mean_latency REAL DEFAULT 0.0,
  p95_latency REAL DEFAULT 0.0,
  p99_latency REAL DEFAULT 0.0,
  max_concurrency INTEGER DEFAULT 1,
  current_in_flight INTEGER DEFAULT 0,
  queue_length INTEGER DEFAULT 0,
  retry_count INTEGER DEFAULT 0,
  time_since_last_failure REAL,
  avg_output_size_bytes REAL,
  updated_at TEXT NOT NULL
);

-- UI Infrastructure: Jobs (for job-based execution engine)
CREATE TABLE IF NOT EXISTS jobs (
  job_id TEXT PRIMARY KEY,
  parent_ws_id TEXT,
  run_id TEXT,
  tools_invoked_json TEXT,
  latest_step_status TEXT,
  latest_step_description TEXT,
  exit_code INTEGER,
  completed INTEGER DEFAULT 0,
  start_time TEXT,
  end_time TEXT,
  metadata_json TEXT,
  FOREIGN KEY (parent_ws_id) REFERENCES workstreams(ws_id) ON DELETE SET NULL,
  FOREIGN KEY (run_id) REFERENCES runs(run_id) ON DELETE SET NULL
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

-- UI Infrastructure indexes
CREATE INDEX IF NOT EXISTS idx_file_lifecycle_state ON file_lifecycle(current_state);
CREATE INDEX IF NOT EXISTS idx_file_lifecycle_ws ON file_lifecycle(workstream_id);
CREATE INDEX IF NOT EXISTS idx_file_lifecycle_run ON file_lifecycle(run_id);
CREATE INDEX IF NOT EXISTS idx_file_state_history_file ON file_state_history(file_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_file_tool_touches_file ON file_tool_touches(file_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_file_tool_touches_tool ON file_tool_touches(tool_id);
CREATE INDEX IF NOT EXISTS idx_error_records_ws ON error_records(ws_id);
CREATE INDEX IF NOT EXISTS idx_error_records_run ON error_records(run_id);
CREATE INDEX IF NOT EXISTS idx_error_records_severity ON error_records(severity);
CREATE INDEX IF NOT EXISTS idx_error_records_category ON error_records(category);
CREATE INDEX IF NOT EXISTS idx_jobs_ws ON jobs(parent_ws_id);
CREATE INDEX IF NOT EXISTS idx_jobs_run ON jobs(run_id);
