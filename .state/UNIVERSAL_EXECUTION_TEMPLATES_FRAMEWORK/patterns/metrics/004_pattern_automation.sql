-- Pattern automation tables
-- Migration: 004_pattern_automation
-- Created: 2025-11-27

CREATE TABLE IF NOT EXISTS execution_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    operation_kind TEXT NOT NULL,
    file_types TEXT,
    tools_used TEXT,
    input_signature TEXT,
    output_signature TEXT,
    success BOOLEAN NOT NULL,
    time_taken_seconds REAL,
    context TEXT
);

CREATE TABLE IF NOT EXISTS pattern_candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_id TEXT UNIQUE,
    signature TEXT,
    example_executions TEXT,
    confidence REAL,
    auto_generated_spec TEXT,
    status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS anti_patterns (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    affected_patterns TEXT,
    failure_signature TEXT,
    recommendation TEXT,
    status TEXT DEFAULT 'active',
    occurrences INTEGER DEFAULT 1,
    first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_execution_timestamp ON execution_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_execution_operation ON execution_logs(operation_kind);
CREATE INDEX IF NOT EXISTS idx_execution_success ON execution_logs(success);
CREATE INDEX IF NOT EXISTS idx_execution_signature ON execution_logs(input_signature, output_signature);
CREATE INDEX IF NOT EXISTS idx_pattern_status ON pattern_candidates(status);
CREATE INDEX IF NOT EXISTS idx_anti_pattern_status ON anti_patterns(status);
