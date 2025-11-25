-- UET Migration 001 Rollback
-- Removes all UET tables and restores to pre-migration state

-- Drop indexes first
DROP INDEX IF EXISTS idx_patch_ledger_status;
DROP INDEX IF EXISTS idx_patch_ledger_workstream;
DROP INDEX IF EXISTS idx_run_events_timestamp;
DROP INDEX IF EXISTS idx_run_events_run;
DROP INDEX IF EXISTS idx_step_attempts_status;
DROP INDEX IF EXISTS idx_step_attempts_run;
DROP INDEX IF EXISTS idx_uet_runs_phase;
DROP INDEX IF EXISTS idx_uet_runs_state;

-- Drop view
DROP VIEW IF EXISTS workstreams_compat;

-- Drop tables (reverse order due to foreign keys)
DROP TABLE IF EXISTS patch_ledger;
DROP TABLE IF EXISTS run_events;
DROP TABLE IF EXISTS step_attempts;
DROP TABLE IF EXISTS uet_runs;
