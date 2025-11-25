-- Pattern Telemetry Schema
-- Migration: add_pattern_telemetry
-- Purpose: Enable pattern automation and learning

-- Execution logs: Track every pattern execution
CREATE TABLE IF NOT EXISTS execution_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    operation_kind TEXT NOT NULL,
    pattern_id TEXT,
    file_types TEXT,  -- JSON array
    tools_used TEXT,  -- JSON array
    input_signature TEXT,  -- Hash of input structure
    output_signature TEXT,  -- Hash of output structure
    success BOOLEAN NOT NULL,
    time_taken_seconds INTEGER,
    user_id TEXT,
    context TEXT  -- JSON metadata
);

-- Pattern metrics: Aggregate performance data
CREATE TABLE IF NOT EXISTS pattern_metrics (
    pattern_id TEXT PRIMARY KEY,
    version TEXT NOT NULL,
    total_uses INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    total_time_saved_minutes INTEGER DEFAULT 0,
    avg_execution_seconds REAL DEFAULT 0.0,
    last_used DATETIME,
    confidence_score REAL DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Pattern candidates: Auto-detected patterns pending approval
CREATE TABLE IF NOT EXISTS pattern_candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    signature TEXT NOT NULL,  -- Hash of pattern signature
    example_executions TEXT,  -- JSON array of execution IDs
    confidence REAL NOT NULL,
    status TEXT DEFAULT 'pending',  -- pending|approved|rejected|quarantined
    auto_generated_spec TEXT,  -- YAML content
    failure_count INTEGER DEFAULT 0,
    notes TEXT
);

-- Anti-patterns: Learned failure patterns
CREATE TABLE IF NOT EXISTS anti_patterns (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    occurrences INTEGER DEFAULT 1,
    affected_patterns TEXT,  -- JSON array
    failure_signature TEXT,  -- What characterizes this anti-pattern
    recommendation TEXT,  -- How to fix
    status TEXT DEFAULT 'active'  -- active|fixed|archived
);

-- Error patterns: Learned error resolutions (AUTO-003)
CREATE TABLE IF NOT EXISTS error_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    error_type TEXT NOT NULL,
    error_signature TEXT NOT NULL,  -- Pattern to match
    file_types TEXT,  -- JSON array
    tool_context TEXT,
    resolution_steps TEXT,  -- JSON array
    occurrences INTEGER DEFAULT 1,
    successful_resolutions INTEGER DEFAULT 0,
    failed_resolutions INTEGER DEFAULT 0,
    success_rate REAL DEFAULT 0.0,
    auto_apply BOOLEAN DEFAULT 0,  -- Auto-apply if success_rate >= 0.9
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_executions_pattern ON execution_logs(pattern_id);
CREATE INDEX IF NOT EXISTS idx_executions_timestamp ON execution_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_executions_success ON execution_logs(success);
CREATE INDEX IF NOT EXISTS idx_candidates_status ON pattern_candidates(status);
CREATE INDEX IF NOT EXISTS idx_candidates_confidence ON pattern_candidates(confidence);
CREATE INDEX IF NOT EXISTS idx_error_patterns_type ON error_patterns(error_type);
CREATE INDEX IF NOT EXISTS idx_anti_patterns_status ON anti_patterns(status);

-- Views for reporting
CREATE VIEW IF NOT EXISTS pattern_performance AS
SELECT 
    pattern_id,
    version,
    total_uses,
    CAST(success_count AS REAL) / NULLIF(total_uses, 0) AS success_rate,
    total_time_saved_minutes,
    avg_execution_seconds,
    confidence_score,
    last_used,
    JULIANDAY('now') - JULIANDAY(last_used) AS days_since_last_use
FROM pattern_metrics
ORDER BY total_uses DESC;

CREATE VIEW IF NOT EXISTS top_patterns_weekly AS
SELECT 
    pattern_id,
    COUNT(*) AS uses_this_week,
    SUM(time_taken_seconds) / 60 AS minutes_spent,
    CAST(SUM(CASE WHEN success THEN 1 ELSE 0 END) AS REAL) / COUNT(*) AS success_rate
FROM execution_logs
WHERE timestamp >= datetime('now', '-7 days')
GROUP BY pattern_id
ORDER BY uses_this_week DESC
LIMIT 10;

CREATE VIEW IF NOT EXISTS pattern_candidates_summary AS
SELECT 
    status,
    COUNT(*) AS count,
    AVG(confidence) AS avg_confidence,
    MAX(detected_at) AS latest_detection
FROM pattern_candidates
GROUP BY status;
