-- Migration 002: UET Foundation
-- Adds worker management, event bus, cost tracking, and merge conflict tables
-- Idempotent and safe to re-run

PRAGMA foreign_keys = ON;

-- Worker Management
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

CREATE INDEX IF NOT EXISTS idx_workers_state ON workers(state);

-- UET Event Bus (separate from legacy events table)
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

CREATE INDEX IF NOT EXISTS idx_uet_events_timestamp ON uet_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_uet_events_type ON uet_events(event_type);

-- Cost Tracking
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

CREATE INDEX IF NOT EXISTS idx_cost_run ON cost_tracking(run_id);

-- Merge Conflict Tracking
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

-- Record migration version
INSERT OR REPLACE INTO schema_meta (key, value) VALUES ('migration_version', '002_uet_foundation');
