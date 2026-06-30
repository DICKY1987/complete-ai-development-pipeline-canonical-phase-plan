-- UET Migration 001: Add UET Tables
-- Created: 2025-11-25
-- Purpose: Add UET engine tables without breaking existing schema

-- Table: uet_runs
CREATE TABLE IF NOT EXISTS uet_runs (
    run_id TEXT PRIMARY KEY,
    project_id TEXT,
    phase_id TEXT,
    state TEXT CHECK(state IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    created_at TEXT DEFAULT (datetime('now')),
    started_at TEXT,
    completed_at TEXT,
    error_message TEXT,
    metadata TEXT
);

-- Table: step_attempts
CREATE TABLE IF NOT EXISTS step_attempts (
    step_attempt_id TEXT PRIMARY KEY,
    run_id TEXT REFERENCES uet_runs(run_id) ON DELETE CASCADE,
    step_id TEXT NOT NULL,
    workstream_id TEXT,
    status TEXT CHECK(status IN ('pending', 'running', 'completed', 'failed', 'skipped')),
    started_at TEXT,
    completed_at TEXT,
    exit_code INTEGER,
    stdout TEXT,
    stderr TEXT,
    metadata TEXT
);

-- Table: run_events
CREATE TABLE IF NOT EXISTS run_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT REFERENCES uet_runs(run_id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    timestamp TEXT DEFAULT (datetime('now')),
    payload TEXT,
    severity TEXT CHECK(severity IN ('debug', 'info', 'warning', 'error', 'critical'))
);

-- Table: patch_ledger
CREATE TABLE IF NOT EXISTS patch_ledger (
    patch_id TEXT PRIMARY KEY,
    workstream_id TEXT,
    run_id TEXT REFERENCES uet_runs(run_id) ON DELETE SET NULL,
    content TEXT NOT NULL,
    status TEXT CHECK(status IN ('created', 'validated', 'queued', 'applied', 'verified', 'committed', 'quarantined')),
    created_at TEXT DEFAULT (datetime('now')),
    applied_at TEXT,
    verified_at TEXT,
    committed_at TEXT,
    error_message TEXT,
    metadata TEXT
);

-- Compatibility view for legacy workstreams table
CREATE VIEW IF NOT EXISTS workstreams_compat AS
SELECT
    run_id as id,
    phase_id as phase,
    state as status,
    created_at,
    completed_at
FROM uet_runs;

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_uet_runs_state ON uet_runs(state);
CREATE INDEX IF NOT EXISTS idx_uet_runs_phase ON uet_runs(phase_id);
CREATE INDEX IF NOT EXISTS idx_step_attempts_run ON step_attempts(run_id);
CREATE INDEX IF NOT EXISTS idx_step_attempts_status ON step_attempts(status);
CREATE INDEX IF NOT EXISTS idx_run_events_run ON run_events(run_id);
CREATE INDEX IF NOT EXISTS idx_run_events_timestamp ON run_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_patch_ledger_workstream ON patch_ledger(workstream_id);
CREATE INDEX IF NOT EXISTS idx_patch_ledger_status ON patch_ledger(status);
