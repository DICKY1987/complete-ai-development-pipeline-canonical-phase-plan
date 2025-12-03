-- Migration 005: Add costs table for CostTracker
-- Created: 2025-11-23
-- Implements: WS-NEXT-002-004

CREATE TABLE IF NOT EXISTS costs (
    cost_id TEXT PRIMARY KEY,
    execution_request_id TEXT,
    project_id TEXT,
    resource_type TEXT NOT NULL CHECK(resource_type IN (
        'api_call', 'compute_time', 'storage', 'network', 'tool_usage', 'custom'
    )),
    resource_name TEXT,
    amount REAL NOT NULL CHECK(amount >= 0),
    currency TEXT NOT NULL,
    usage TEXT,
    recorded_at TEXT NOT NULL,
    metadata TEXT,
    CONSTRAINT fk_execution_request
        FOREIGN KEY (execution_request_id)
        REFERENCES runs(run_id)
        ON DELETE SET NULL
);

-- Indices for performance
CREATE INDEX IF NOT EXISTS idx_costs_execution ON costs(execution_request_id);
CREATE INDEX IF NOT EXISTS idx_costs_project ON costs(project_id);
CREATE INDEX IF NOT EXISTS idx_costs_resource_type ON costs(resource_type);
CREATE INDEX IF NOT EXISTS idx_costs_recorded ON costs(recorded_at);

-- Comments
-- cost_id: ULID format cost identifier
-- resource_type: Type of resource (api_call, compute_time, etc.)
-- amount: Cost amount (non-negative)
-- currency: ISO 4217 currency code (e.g., USD, EUR)
-- usage, metadata: JSON-serialized objects
-- recorded_at: ISO8601 timestamp
