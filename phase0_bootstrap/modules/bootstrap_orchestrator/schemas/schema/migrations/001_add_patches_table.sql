-- Migration: 001_add_patches_table
-- Purpose: Add patches table for patch-based CLI tool integration
-- Date: 2025-11-19

CREATE TABLE IF NOT EXISTS patches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    ws_id TEXT NOT NULL,
    step_name TEXT NOT NULL,
    attempt INTEGER NOT NULL,
    patch_file TEXT NOT NULL,
    diff_hash TEXT NOT NULL,
    line_count INTEGER NOT NULL,
    files_modified TEXT NOT NULL,
    created_at TEXT NOT NULL,
    validated INTEGER DEFAULT 0,
    applied INTEGER DEFAULT 0,
    FOREIGN KEY (run_id, ws_id) REFERENCES workstreams(run_id, ws_id)
);

CREATE INDEX IF NOT EXISTS idx_patches_diff_hash ON patches(ws_id, diff_hash);
CREATE INDEX IF NOT EXISTS idx_patches_run_ws ON patches(run_id, ws_id);
