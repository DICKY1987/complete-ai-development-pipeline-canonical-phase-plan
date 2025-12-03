-- Migration 002: Add workers table for WorkerLifecycle tracking
-- Created: 2025-11-23
-- Implements: WS-NEXT-002-001

CREATE TABLE IF NOT EXISTS workers (
    worker_id TEXT PRIMARY KEY,
    worker_type TEXT NOT NULL CHECK(worker_type IN ('executor', 'monitor', 'validator', 'scheduler', 'custom')),
    state TEXT NOT NULL CHECK(state IN ('idle', 'busy', 'paused', 'stopped', 'crashed')),
    current_task_id TEXT,
    started_at TEXT NOT NULL,
    last_heartbeat TEXT,
    stopped_at TEXT,
    crash_info TEXT,
    statistics TEXT,
    config TEXT,
    metadata TEXT,
    CONSTRAINT fk_current_task
        FOREIGN KEY (current_task_id)
        REFERENCES runs(run_id)
        ON DELETE SET NULL
);

-- Indices for performance
CREATE INDEX IF NOT EXISTS idx_workers_state ON workers(state);
CREATE INDEX IF NOT EXISTS idx_workers_type ON workers(worker_type);
CREATE INDEX IF NOT EXISTS idx_workers_heartbeat ON workers(last_heartbeat);

-- Comments
-- worker_id: ULID format worker identifier
-- worker_type: Type of worker (executor, monitor, etc.)
-- state: Current state (idle, busy, paused, stopped, crashed)
-- current_task_id: ULID of currently executing task (if busy)
-- crash_info, statistics, config, metadata: JSON-serialized objects
