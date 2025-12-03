-- Migration 003: Add patch_ledger table for PatchLedger tracking
-- Created: 2025-11-23
-- Implements: WS-NEXT-002-002

CREATE TABLE IF NOT EXISTS patch_ledger (
    ledger_id TEXT PRIMARY KEY,
    patch_id TEXT NOT NULL,
    project_id TEXT NOT NULL,
    phase_id TEXT,
    workstream_id TEXT,
    execution_request_id TEXT,
    state TEXT NOT NULL CHECK(state IN (
        'created', 'validated', 'queued', 'applied', 'apply_failed',
        'verified', 'committed', 'rolled_back', 'quarantined', 'dropped'
    )),
    state_history TEXT,
    validation TEXT NOT NULL,
    apply TEXT,
    quarantine TEXT,
    relations TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    CONSTRAINT fk_execution_request
        FOREIGN KEY (execution_request_id)
        REFERENCES runs(run_id)
        ON DELETE SET NULL
);

-- Indices for performance
CREATE INDEX IF NOT EXISTS idx_patch_ledger_patch_id ON patch_ledger(patch_id);
CREATE INDEX IF NOT EXISTS idx_patch_ledger_project ON patch_ledger(project_id);
CREATE INDEX IF NOT EXISTS idx_patch_ledger_state ON patch_ledger(state);
CREATE INDEX IF NOT EXISTS idx_patch_ledger_workstream ON patch_ledger(workstream_id);
CREATE INDEX IF NOT EXISTS idx_patch_ledger_created ON patch_ledger(created_at);

-- Comments
-- ledger_id: ULID format ledger entry identifier
-- patch_id: ULID of the patch being tracked
-- state: Current state in patch lifecycle
-- state_history, validation, apply, quarantine, relations: JSON-serialized objects
-- created_at, updated_at: ISO8601 timestamps
