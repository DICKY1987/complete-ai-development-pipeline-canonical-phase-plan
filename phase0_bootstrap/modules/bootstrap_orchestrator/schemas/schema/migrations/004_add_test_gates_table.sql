-- Migration 004: Add test_gates table for TestGate tracking
-- Created: 2025-11-23
-- Implements: WS-NEXT-002-003

CREATE TABLE IF NOT EXISTS test_gates (
    gate_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    gate_type TEXT NOT NULL CHECK(gate_type IN (
        'unit_tests', 'integration_tests', 'e2e_tests',
        'security_scan', 'lint', 'custom'
    )),
    state TEXT NOT NULL CHECK(state IN (
        'pending', 'running', 'passed', 'failed', 'skipped', 'error'
    )),
    project_id TEXT,
    execution_request_id TEXT,
    criteria TEXT NOT NULL,
    execution TEXT,
    results TEXT,
    decision TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata TEXT,
    CONSTRAINT fk_execution_request
        FOREIGN KEY (execution_request_id)
        REFERENCES runs(run_id)
        ON DELETE SET NULL
);

-- Indices for performance
CREATE INDEX IF NOT EXISTS idx_test_gates_state ON test_gates(state);
CREATE INDEX IF NOT EXISTS idx_test_gates_type ON test_gates(gate_type);
CREATE INDEX IF NOT EXISTS idx_test_gates_project ON test_gates(project_id);
CREATE INDEX IF NOT EXISTS idx_test_gates_created ON test_gates(created_at);

-- Comments
-- gate_id: ULID format gate identifier
-- gate_type: Type of quality gate (unit_tests, integration_tests, etc.)
-- state: Current state (pending, running, passed, failed, skipped, error)
-- criteria, execution, results, decision, metadata: JSON-serialized objects
-- created_at, updated_at: ISO8601 timestamps
