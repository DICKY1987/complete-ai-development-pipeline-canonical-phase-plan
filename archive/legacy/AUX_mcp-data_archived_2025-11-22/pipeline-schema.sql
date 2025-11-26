-- R_PIPELINE Documentation Schema for Autonomous Development Pipeline
-- This schema supports: policy versioning, run tracking, module lineage, and audit trails

-- Policy Versions Table
-- Tracks immutable git-tagged policy documents
CREATE TABLE IF NOT EXISTS policy_versions (
    policy_id TEXT PRIMARY KEY,
    policy_name TEXT NOT NULL,
    version TEXT NOT NULL,
    git_tag TEXT NOT NULL,
    file_path TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    created_by TEXT,
    UNIQUE(policy_name, version)
);

-- Run Execution Traces
-- Tracks each autonomous execution with ULID
CREATE TABLE IF NOT EXISTS run_traces (
    run_ulid TEXT PRIMARY KEY,
    github_issue_key TEXT, -- gh://owner/repo/issues/{number}
    github_pr_key TEXT,    -- gh://owner/repo/pulls/{number}
    status TEXT CHECK(status IN ('pending', 'running', 'success', 'failed', 'rolled_back')),
    phase TEXT, -- Intent, Planning, Execution, Validation, Integration, Observability
    started_at TEXT DEFAULT (datetime('now')),
    completed_at TEXT,
    error_message TEXT,
    policy_snapshot TEXT -- JSON snapshot of policies active during this run
);

-- Module Registry
-- Two-ID naming system: Module ID + Module File ID
CREATE TABLE IF NOT EXISTS modules (
    module_id TEXT PRIMARY KEY,
    module_file_id TEXT NOT NULL,
    module_name TEXT NOT NULL,
    category TEXT CHECK(category IN ('Data Acquisition', 'Data Transformation', 'State Change', 'Configuration/Validation', 'Orchestration')),
    description TEXT,
    entry_point TEXT, -- Python entry point for plugin discovery
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Workstream Tracking
-- Tracks parallel execution workstreams
CREATE TABLE IF NOT EXISTS workstreams (
    workstream_id TEXT PRIMARY KEY,
    lineage_id TEXT NOT NULL, -- Workstream Lineage ID
    instance_id TEXT NOT NULL, -- Workstream Instance ID
    run_ulid TEXT NOT NULL,
    parent_workstream_id TEXT,
    git_worktree_path TEXT,
    modification_plan_path TEXT, -- YAML modification plan
    status TEXT CHECK(status IN ('created', 'in_progress', 'completed', 'failed', 'merged')),
    created_at TEXT DEFAULT (datetime('now')),
    completed_at TEXT,
    FOREIGN KEY (run_ulid) REFERENCES run_traces(run_ulid),
    FOREIGN KEY (parent_workstream_id) REFERENCES workstreams(workstream_id)
);

-- Epic/Story/Task Hierarchy
-- Machine-readable planning structure
CREATE TABLE IF NOT EXISTS planning_items (
    item_id TEXT PRIMARY KEY,
    item_type TEXT CHECK(item_type IN ('epic', 'story', 'task')),
    github_issue_key TEXT, -- gh://owner/repo/issues/{number}
    parent_item_id TEXT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT CHECK(status IN ('todo', 'in_progress', 'review', 'done', 'blocked')),
    assigned_agent TEXT, -- Which AI agent (Jules, Aider, Copilot, WebBrowser)
    complexity_score INTEGER CHECK(complexity_score BETWEEN 1 AND 10),
    estimated_effort_hours REAL,
    actual_effort_hours REAL,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (parent_item_id) REFERENCES planning_items(item_id)
);

-- JSONL Event Log (Structured)
-- Complete audit trail for governance
CREATE TABLE IF NOT EXISTS event_log (
    event_id TEXT PRIMARY KEY,
    event_ulid TEXT NOT NULL,
    run_ulid TEXT,
    event_type TEXT NOT NULL,
    timestamp TEXT DEFAULT (datetime('now')),
    actor TEXT, -- User, AI Agent, System
    target_entity TEXT, -- What was acted upon
    action TEXT NOT NULL,
    details TEXT, -- JSON details
    git_commit_sha TEXT,
    FOREIGN KEY (run_ulid) REFERENCES run_traces(run_ulid)
);

-- SafePatch Checkpoints
-- Git checkpoints after each phase
CREATE TABLE IF NOT EXISTS safepatch_checkpoints (
    checkpoint_id TEXT PRIMARY KEY,
    run_ulid TEXT NOT NULL,
    workstream_id TEXT,
    phase TEXT NOT NULL,
    git_commit_sha TEXT NOT NULL,
    files_changed INTEGER,
    lines_added INTEGER,
    lines_deleted INTEGER,
    checkpoint_at TEXT DEFAULT (datetime('now')),
    rollback_available INTEGER DEFAULT 1 CHECK(rollback_available IN (0,1)),
    FOREIGN KEY (run_ulid) REFERENCES run_traces(run_ulid),
    FOREIGN KEY (workstream_id) REFERENCES workstreams(workstream_id)
);

-- V-Model Gates
-- Quality gates and validation results
CREATE TABLE IF NOT EXISTS v_model_gates (
    gate_id TEXT PRIMARY KEY,
    run_ulid TEXT NOT NULL,
    gate_name TEXT NOT NULL,
    gate_type TEXT CHECK(gate_type IN ('requirements', 'design', 'implementation', 'unit_test', 'integration_test', 'acceptance_test')),
    status TEXT CHECK(status IN ('pending', 'passed', 'failed', 'skipped')),
    validation_result TEXT, -- JSON validation details
    executed_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (run_ulid) REFERENCES run_traces(run_ulid)
);

-- Plugin Conformance Tests
-- Track plugin contract compliance
CREATE TABLE IF NOT EXISTS plugin_conformance (
    test_id TEXT PRIMARY KEY,
    module_id TEXT NOT NULL,
    test_name TEXT NOT NULL,
    contract_version TEXT NOT NULL,
    status TEXT CHECK(status IN ('passed', 'failed', 'skipped')),
    error_details TEXT,
    tested_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (module_id) REFERENCES modules(module_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_run_traces_issue ON run_traces(github_issue_key);
CREATE INDEX IF NOT EXISTS idx_workstreams_run ON workstreams(run_ulid);
CREATE INDEX IF NOT EXISTS idx_planning_parent ON planning_items(parent_item_id);
CREATE INDEX IF NOT EXISTS idx_event_log_run ON event_log(run_ulid);
CREATE INDEX IF NOT EXISTS idx_event_log_timestamp ON event_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_checkpoints_run ON safepatch_checkpoints(run_ulid);

-- Insert sample policy version
INSERT OR IGNORE INTO policy_versions (policy_id, policy_name, version, git_tag, file_path, content_hash, created_by)
VALUES ('pol_001', 'plugin_spec', 'v1.0.0', 'v1.0.0-plugin-spec', '/mnt/project/plugin_spec.json', 'sha256:placeholder', 'system');
