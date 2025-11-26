**High-Level Summary**
- Major runtime modules: `engine/orchestrator`, `engine/adapters` (aider/codex/tests/git), `engine/state_store`, `engine/queue`, `error/engine`, and the shared state/observability stack in `modules/core-state` + `core/*` UI infra (file lifecycle, tool health, error/quarantine, events).
- Primary outputs: per-job log files and error reports, `JobResult` JSON payloads, SQLite tables (`runs`, `workstreams`, `step_attempts`, `events`, `errors`, `patches`, `job_queue`, `file_lifecycle`, `tool_health_metrics`, `error_records`, `uet_events`, `jobs`), validation caches, and structured error/pattern reports.
- Cross-module visuals: global “Pipeline Radar” (runs/workstreams/jobs over time), “Event Stream” (events/uet_events), “File Lifecycle” (file_lifecycle + tool touches), “Tool Health” (tool_health_metrics), “Error/Quarantine” (error_records + adapter error reports).

## Module: engine/orchestrator/orchestrator.py
**Role**: CLI/entrypoint that loads a job JSON, routes to the right adapter, and writes state updates via `JobStateStore`.

### Outputs
| Output ID | Type | Source (file/DB/API) | Key Fields / Schema (approx) |
|-----------|------|----------------------|------------------------------|
| ORC-1 | log_text | stdout/stderr from `python -m engine.orchestrator run-job ...` | `[Orchestrator]` lines: job_id, tool, workstream_id, status transitions, exit_code, duration |
| ORC-2 | job_result (in-memory/propagated) | return value `JobResult` | exit_code, duration_s, success, stdout (truncated), stderr (truncated), error_report_path |
| ORC-3 | state_update | `JobStateStore.update_job_result` → SQLite `.worktrees/pipeline_state.db` | `step_attempts`: job_id (in result_json), status, exit_code, duration_s, stdout_preview, stderr_preview, metadata; `events`: `job.completed` payload |

### Suggested Visuals (Tiles)
| Tile Name | Uses Output IDs | Visual Type | Description |
|-----------|-----------------|-------------|-------------|
| JobRunConsoleTile | ORC-1 | Live log viewer | Stream orchestrator prints + adapter tail for bottom terminal pane |
| JobResultSummaryTile | ORC-2, ORC-3 | Status chips + key metrics | Show exit_code, duration, success flag, error_report link |
| JobStateUpdateTile | ORC-3 | Timeline/table | Latest job status transitions and event payloads |

### Generic Output Example
```text
[Orchestrator] Starting job: job-2025-11-20-001
[Orchestrator] Tool: aider
[Orchestrator] Workstream: ws-PH07-refactor-path-resolver
[Orchestrator] Marked job as running: job-2025-11-20-001
[Orchestrator] Updated state store with result
[Orchestrator] Job completed: job-2025-11-20-001
[Orchestrator] Exit code: 0
[Orchestrator] Duration: 12.34s
[Orchestrator] Success: True
```

## Module: engine/adapters/aider_adapter.py
**Role**: Builds/runs Aider command, writes job log and error report, returns `JobResult`.

### Outputs
| Output ID | Type | Source (file/DB/API) | Key Fields / Schema (approx) |
|-----------|------|----------------------|------------------------------|
| AID-1 | log_text | `job["paths"]["log_file"]` (e.g., `logs/<ws>/job-...log`) | headers, command, working_dir, STDOUT, STDERR, exit_code |
| AID-2 | json_report | `job["paths"]["error_report"]` (on non-zero exit) | job_id, tool="aider", exit_code, summary, details[], workstream_id |
| AID-3 | job_result | return `JobResult` | exit_code, duration_s, stdout/snippets, stderr/snippets, error_report_path |

### Suggested Visuals (Tiles)
| Tile Name | Uses Output IDs | Visual Type | Description |
|-----------|-----------------|-------------|-------------|
| AiderLogTile | AID-1 | Raw log viewer | Scrollable log with STDERR highlight |
| AiderErrorReportTile | AID-2 | JSON inspector | Show structured failure details |
| AiderRunStatsTile | AID-3 | Mini-cards | Exit code, duration, timeout/err badges |

### Generic Output Example
```text
=== Aider Job: job-2025-11-20-001 ===
Command: aider --message-file PHASE_DEV_DOCS/AIDER_INSTRUCTIONS_PH07.txt --yes-always --no-suggest-shell-commands
Working dir: C:/Users/richg/ALL_AI/Complete AI Development Pipeline - Canonical Phase Plan

=== STDOUT ===
Applied patch to core/planning/planner.py
=== STDERR ===
(empty)

=== Exit Code: 0 ===
```

## Module: engine/adapters/codex_adapter.py
**Role**: Runs GitHub Copilot CLI job (escalation/alt AI path).

### Outputs
| Output ID | Type | Source | Key Fields |
|-----------|------|--------|------------|
| COD-1 | log_text | `job["paths"]["log_file"]` | same structure as AID-1 |
| COD-2 | json_report | `job["paths"]["error_report"]` | job_id, tool="codex", exit_code, summary, details[], workstream_id |
| COD-3 | job_result | return `JobResult` | exit_code, duration_s, stdout/stderr snippets |

### Suggested Visuals
| Tile Name | Uses Output IDs | Visual Type | Description |
|-----------|-----------------|-------------|-------------|
| CodexLogTile | COD-1 | Raw log viewer | Focus on Copilot CLI output |
| CodexEscalationTile | COD-2 | Table/JSON | Show why escalation triggered and details |
| CodexRunStatsTile | COD-3 | Cards | Duration vs Aider; exit distribution |

### Generic Output Example
```text
=== Codex Job: job-2025-11-20-001-escalated-codex ===
Command: gh copilot suggest --target shell "Fix the issue: failing pytest"
=== STDOUT ===
copilot> Suggestion applied to tests/test_api.py
=== STDERR ===
(empty)
=== Exit Code: 0 ===
```

## Module: engine/adapters/tests_adapter.py
**Role**: Executes test runners, parses summaries, writes error report on failure.

### Outputs
| Output ID | Type | Source | Key Fields |
|-----------|------|--------|------------|
| TST-1 | log_text | `job["paths"]["log_file"]` | command, STDOUT/STDERR, exit_code, embedded `Test Summary` JSON |
| TST-2 | json_report | `job["paths"]["error_report"]` (when fail/timeout) | job_id, tool="tests", exit_code, summary string, test_results {passed, failed, skipped, total}, details[] |
| TST-3 | job_result | return `JobResult` with `metadata=test_summary` | exit_code, duration_s, stdout/stderr snippets, metadata summary |

### Suggested Visuals
| Tile Name | Uses Output IDs | Visual Type | Description |
|-----------|-----------------|-------------|-------------|
| TestRunTile | TST-1 | Log + badges | Show failing tests highlighted |
| TestFailureReportTile | TST-2 | Table/JSON | Failures by file/test id |
| TestSummaryTile | TST-3 | Bar/stacked chips | passed/failed/skipped counts, duration |

### Generic Output Example
```text
=== Tests Job: job-2025-11-20-004 ===
Command: pytest -q
=== STDOUT ===
3 passed, 1 failed, 1 skipped in 12.34s
=== STDERR ===
tests/test_api.py::test_returns_200 AssertionError: expected 200 got 500

=== Test Summary ===
{
  "total": 5,
  "passed": 3,
  "failed": 1,
  "skipped": 1,
  "errors": 0
}
=== Exit Code: 1 ===
```

## Module: engine/adapters/git_adapter.py
**Role**: Runs git operations non-interactively.

### Outputs
| Output ID | Type | Source | Key Fields |
|-----------|------|--------|------------|
| GIT-1 | log_text | `job["paths"]["log_file"]` | command, STDOUT/STDERR, exit_code |
| GIT-2 | json_report | `job["paths"]["error_report"]` on failure | job_id, tool="git", exit_code, summary, git_command, details[] |
| GIT-3 | job_result | return `JobResult` | exit_code, duration_s, stdout/stderr snippets |

### Suggested Visuals
| Tile Name | Uses Output IDs | Visual Type | Description |
|-----------|-----------------|-------------|-------------|
| GitOpsTile | GIT-1 | Raw log viewer | Show git output and conflicts |
| GitErrorTile | GIT-2 | Table | Command, exit code, stderr lines |
| GitOutcomeTile | GIT-3 | Status chips | success/fail/timeout, duration |

### Generic Output Example
```text
=== Git Job: job-2025-11-20-007 ===
Command: git status --short
=== STDOUT ===
 M engine/orchestrator/orchestrator.py
?? new_file.txt
=== STDERR ===
(empty)
=== Exit Code: 0 ===
```

## Module: engine/state_store/job_state_store.py
**Role**: Adapter over pipeline DB for job-centric reads/writes (uses `modules/core-state/m010003_db` + `crud`).

### Outputs
| Output ID | Type | Source | Key Fields / Schema (approx) |
|-----------|------|--------|------------------------------|
| ST-1 | db_table | SQLite `.worktrees/pipeline_state.db` → `runs` | run_id, status, created_at, updated_at, metadata_json |
| ST-2 | db_table | `workstreams` | ws_id, run_id, status, depends_on, metadata_json |
| ST-3 | db_table | `step_attempts` (jobs stored here) | id, run_id, ws_id, step_name=tool, status (running/completed/failed/timeout), started_at, completed_at, result_json{job_id, exit_code, duration_s, stdout_preview, stderr_preview, metadata} |
| ST-4 | db_table | `events` via `record_event` | id, timestamp, run_id, ws_id, event_type (e.g., job.completed), payload_json{job_id,status,exit_code,duration_s} |
| ST-5 | db_table | `errors` (deduped) | error_code, signature, message, count, context_json, first_seen_at, last_seen_at |
| ST-6 | db_table | `patches` (from CRUD) | patch_file, diff_hash, files_modified[], validated/applied flags, timestamps |

### Suggested Visuals
| Tile Name | Uses Output IDs | Visual Type | Description |
|-----------|-----------------|-------------|-------------|
| RunSummaryTile | ST-1 | Cards/table | Recent runs with status + updated_at |
| WorkstreamListTile | ST-2 | Table + dependency badges | ws_id, status, depends_on |
| JobAttemptsTile | ST-3 | Table + sparkline | jobs per run with status/exit/duration |
| EventStreamTile | ST-4 | Live list | job.completed and other events |
| PatchHistoryTile | ST-6 | List | patch files, hashes, validated/applied flags |

### Generic Output Example
```json
{
  "id": 42,
  "run_id": "run-20251120-001",
  "ws_id": "ws-PH07-refactor-path-resolver",
  "step_name": "aider",
  "status": "completed",
  "started_at": "2025-11-20T10:03:01Z",
  "completed_at": "2025-11-20T10:03:45Z",
  "result": {
    "job_id": "job-2025-11-20-001",
    "exit_code": 0,
    "duration_s": 44.1,
    "stdout_preview": "Applied patch...",
    "stderr_preview": "",
    "metadata": {}
  }
}
```

## Module: engine/queue (job_queue.py, queue_manager.py, worker_pool.py, escalation.py)
**Role**: Async priority queue with persistence, worker pool execution, retry/escalation logic.

### Outputs
| Output ID | Type | Source | Key Fields / Schema |
|-----------|------|--------|---------------------|
| Q-1 | db_table | SQLite `pipeline.db` → `job_queue` | job_id, job_data JSON, priority, status (queued/waiting/running/retry/completed/failed/cancelled), depends_on[], retry_count, max_retries, queued_at, started_at, completed_at, metadata |
| Q-2 | metrics/map | `JobQueue.get_stats()` | queued, waiting, running, completed, failed, total |
| Q-3 | dict | `QueueManager.get_job_status()` | job_id, status, priority, retry_count, queued_at, started_at (if running), depends_on (if waiting) |
| Q-4 | policy map | `EscalationManager.rules` | on_failure/on_timeout targets, escalate_priority, max_retries_before_escalation |

### Suggested Visuals
| Tile Name | Uses Output IDs | Visual Type | Description |
|-----------|-----------------|-------------|-------------|
| JobQueueTile | Q-1, Q-2 | Table + counters | Priority/status grid with counts |
| JobStatusDetailTile | Q-3 | Detail card | Selected job lifecycle + retries |
| EscalationRulesTile | Q-4 | Config viewer | Show escalation chains per tool |
| WorkerPoolTile | Q-2 | Mini dashboard | Active workers, running count (from `WorkerPool.get_status`) |

### Generic Output Example
```json
{
  "job_id": "job-2025-11-20-001",
  "priority": 1,
  "status": "running",
  "queued_at": "2025-11-20T10:00:00",
  "started_at": "2025-11-20T10:00:05",
  "retry_count": 0,
  "depends_on": ["job-2025-11-19-099"]
}
```

## Module: error/engine (error_engine.py, error_state_machine, pipeline service/context)
**Role**: Plugin-based detection pipeline with state machine escalation; produces normalized error reports and caches.

### Outputs
| Output ID | Type | Source | Key Fields / Schema |
|-----------|------|--------|---------------------|
| ERR-1 | json_report (in-memory/return) | `run_error_pipeline` | summary {total_issues, issues_by_tool, issues_by_category, has_hard_fail, total_errors, total_warnings, style_only}, issues[] {tool, path, line, column, code, category, severity, message}, outputs[] {input, output}, run_id, workstream_id, attempt_number, ai_agent |
| ERR-2 | file_cache | `.state/validation_cache.json` | path → {hash, last_checked_utc, status} |
| ERR-3 | json_context | `.state/error_pipeline/<run>/<ws>/context.json` (or ERROR_PIPELINE_DB) | current_state, workstream_id, run_id, attempt_number, last_error_report, mechanical_fix_applied, current_agent |
| ERR-4 | json_report files | `.state/error_pipeline/<run>/<ws>/error_reports/error_report_attempt_<n>.json` | attempt metadata + normalized issues/summary |
| ERR-5 | db_table (optional sqlite path) | `modules/core-state/m010003_db_sqlite` tables (`runs`, `workstreams`, `step_attempts`, `events`, `errors`) when ERROR_PIPELINE_DB set | event payloads for error reports/AI attempts |

### Suggested Visuals
| Tile Name | Uses Output IDs | Visual Type | Description |
|-----------|-----------------|-------------|-------------|
| ErrorScanSummaryTile | ERR-1 | Donut + table | Issues by category/tool, hard-fail flag |
| ErrorContextTile | ERR-3 | State machine timeline | Current_state, attempt_number, agent |
| ErrorReportsTile | ERR-4 | List/JSON viewer | Per-attempt reports with summaries |
| ValidationCacheTile | ERR-2 | Table | Files, hash, last_checked, status (cached vs rechecked) |

### Generic Output Example
```json
{
  "summary": {
    "total_issues": 4,
    "issues_by_tool": {"ruff": 3, "pytest": 1},
    "issues_by_category": {"style": 3, "test_failure": 1},
    "has_hard_fail": true,
    "total_errors": 1,
    "total_warnings": 3
  },
  "issues": [
    {"tool": "pytest", "path": "tests/test_api.py", "line": 18, "code": "AssertionError", "category": "test_failure", "severity": "error", "message": "expected 200 got 500"}
  ]
}
```

## Module: modules/core-state (db, crud, events) — backing store for engine + UI infra
**Role**: SQLite helper layer (`.worktrees/pipeline_state.db` default) with CRUD over runs/workstreams/step_attempts/errors/events/patches and event helpers.

### Outputs
| Output ID | Type | Source | Key Fields / Schema |
|-----------|------|--------|---------------------|
| CS-1 | db_table | `runs`, `workstreams` | run_id/ws_id, status, timestamps, metadata_json |
| CS-2 | db_table | `step_attempts` | run_id, ws_id, step_name, status, started_at, completed_at, result_json |
| CS-3 | db_table | `errors` (deduped) | error_code, signature, message, context_json, count, first_seen_at, last_seen_at |
| CS-4 | db_table | `events` | id, timestamp, run_id, ws_id, event_type, payload_json |
| CS-5 | db_table | `patches` | patch_file, diff_hash, files_modified[], validated/applied, created_at |
| CS-6 | event helper | `get_events_since`, `get_recent_events` | filters by last_event_id/limit; payload JSON expanded |

### Suggested Visuals
| Tile Name | Uses Output IDs | Visual Type | Description |
|-----------|-----------------|-------------|-------------|
| StateDBBrowserTile | CS-1..CS-5 | Table explorer | Quick DB browser per table |
| EventDeltaTile | CS-4/CS-6 | Live tail | New events since cursor |
| PatchAuditTile | CS-5 | List | Patches with validated/applied flags |

### Generic Output Example
```json
{
  "event_type": "job.completed",
  "timestamp": "2025-11-20T10:03:45Z",
  "run_id": "run-20251120-001",
  "ws_id": "ws-PH07-refactor-path-resolver",
  "payload": {
    "job_id": "job-2025-11-20-001",
    "tool": "aider",
    "status": "completed",
    "exit_code": 0,
    "duration_s": 44.1
  }
}
```

## Module: core UI Infrastructure (file_lifecycle, tool_instrumentation, error_records, ui_clients)
**Role**: Observability layer for GUI/TUI panels; writes to same SQLite DB using extended tables from `schema/schema.sql`.

### Outputs
| Output ID | Type | Source | Key Fields / Schema |
|-----------|------|--------|---------------------|
| UI-1 | db_table | `file_lifecycle` | file_id, current_path, origin_path, file_role, current_state (discovered → quarantined), workstream_id, job_id, run_id, timestamps, quarantine_reason, metadata_json |
| UI-2 | db_table | `file_state_history` | file_id, state, timestamp |
| UI-3 | db_table | `file_tool_touches` | file_id, tool_id, tool_name, action, status, error_message, timestamp |
| UI-4 | db_table | `tool_health_metrics` (via `tool_instrumentation`) | tool_id, display_name, category, status, status_reason, last_successful_invocation, success_count, failure_count, success_rate, mean_latency, p95_latency, queue_length, updated_at |
| UI-5 | db_table | `error_records` (via `error_records.py`) | error_id, entity_type, file_id/job_id/ws_id/tool_id, severity, category, human_message, technical_details, recommendation, occurrence_count, quarantine_path, can_retry, auto_fix_available, timestamps |
| UI-6 | db_table | `uet_events` (from event bus) | event_type, worker_id, task_id, run_id, workstream_id, timestamp, payload_json |

### Suggested Visuals
| Tile Name | Uses Output IDs | Visual Type | Description |
|-----------|-----------------|-------------|-------------|
| FileLifecycleTile | UI-1, UI-2 | Table + state timeline | File state, role, quarantine flags |
| FileToolTouchesTile | UI-3 | List/table | Recent tool touches per file |
| ToolHealthTile | UI-4 | Health cards + sparkline | Status (healthy/degraded), success rate, latency |
| ErrorQuarantineTile | UI-5 | Table + filters | Error severity/category, occurrence count, retry/auto-fix flags |
| EventStreamTile (UI) | UI-6 | Live event list | Worker/task/run events with payload snippet |

### Generic Output Example
```json
{
  "tool_id": "aider",
  "status": "healthy",
  "success_rate": 0.92,
  "success_count": 12,
  "failure_count": 1,
  "mean_latency": 35.4,
  "p95_latency": 42.5,
  "last_successful_invocation": "2025-11-26T09:14:00Z",
  "updated_at": "2025-11-26T09:14:00Z"
}
```

## Module: schema/jobs (job.schema.json + examples)
**Role**: Contract for all job inputs consumed by orchestrator/adapters.

### Outputs
| Output ID | Type | Source | Key Fields / Schema |
|-----------|------|--------|---------------------|
| JOB-1 | json_schema | `schema/jobs/job.schema.json` | job_id, workstream_id, tool, command {exe,args[]}, env map, paths {repo_root, working_dir, log_file, error_report}, metadata {retry_policy, timeout_seconds, max_retries, message_file, files_scope[]} |
| JOB-2 | job_example | `schema/jobs/examples/*.json` | concrete sample jobs with log/error paths and metadata |

### Suggested Visuals
| Tile Name | Uses Output IDs | Visual Type | Description |
|-----------|-----------------|-------------|-------------|
| JobSpecTile | JOB-1 | Schema viewer | Render required fields / enums |
| JobExampleTile | JOB-2 | JSON viewer | Sample job payloads for quick launch |

### Generic Output Example
```json
{
  "job_id": "job-2025-11-20-001",
  "tool": "aider",
  "paths": {
    "log_file": "logs/ws-PH07-refactor-path-resolver/job-2025-11-20-001.log",
    "error_report": "logs/ws-PH07-refactor-path-resolver/job-2025-11-20-001.error.json"
  },
  "metadata": {
    "retry_policy": "escalate_to_codex",
    "timeout_seconds": 600,
    "files_scope": ["core/planning/planner.py", "core/planning/archive.py"]
  }
}
```

**Natural next steps**: Wire each tile to the noted log/error/report/DB sources; start with generic JSON/log viewers, then layer tables/timelines for queue, state store, error/quarantine, file lifecycle, and tool health.
