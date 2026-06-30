-- UET Migration 001: Unified State Schema
-- Adds UET-specific tables while preserving existing schema

CREATE TABLE IF NOT EXISTS uet_executions (
    execution_id TEXT PRIMARY KEY,
    phase_name TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT CHECK(status IN ('pending', 'running', 'completed', 'failed')),
    metadata JSON
);

CREATE TABLE IF NOT EXISTS uet_tasks (
    task_id TEXT PRIMARY KEY,
    execution_id TEXT REFERENCES uet_executions(execution_id),
    task_type TEXT NOT NULL,
    dependencies JSON,
    status TEXT CHECK(status IN ('pending', 'running', 'completed', 'failed', 'skipped')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    result JSON
);

CREATE TABLE IF NOT EXISTS patch_ledger (
    patch_id TEXT PRIMARY KEY,
    execution_id TEXT REFERENCES uet_executions(execution_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    state TEXT CHECK(state IN ('created', 'validated', 'queued', 'applied', 'verified', 'committed', 'apply_failed', 'quarantined', 'dropped')),
    patch_content TEXT,
    validation_result JSON,
    metadata JSON
);

CREATE INDEX IF NOT EXISTS idx_tasks_execution ON uet_tasks(execution_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON uet_tasks(status);
CREATE INDEX IF NOT EXISTS idx_patches_execution ON patch_ledger(execution_id);
CREATE INDEX IF NOT EXISTS idx_patches_state ON patch_ledger(state);
