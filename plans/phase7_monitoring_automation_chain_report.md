# Phase 7 Monitoring Automation Chain Analysis

## 8.1 Executive Summary
- Total gaps identified: 4
- Total chain breaks: 5 (Critical: 2)
- High-impact quick wins: 3
- Total potential time savings: ~8-12 hours/month
- Estimated implementation effort: ~18-26 hours

## 8.2 Automation Chain Map (Monitoring/Archival)
Nodes (STEP-ID | automation_class | trigger | chain_role):
- STEP-701: Run created in `.state/orchestration.db` (SEMI_MANUAL; upstream orchestration; ENTRY_POINT)
- STEP-702: Operator starts monitoring UI (`python -m gui.tui_app.main` or `orchestrator monitor --run <id>`) (MANUAL; CLI_manual; INTERNAL_STEP)
- STEP-703: UI reads state from `.worktrees/pipeline_state.db` or in-memory mocks (SEMI_MANUAL; file_access; INTERNAL_STEP)
- STEP-704: Operator triggers archival (`orchestrator archive --run <id>`) (MANUAL; CLI_manual; INTERNAL_STEP)
- STEP-705: Operator triggers report generation (`orchestrator report --run <id>`) (MANUAL; CLI_manual; TERMINAL_STEP)

Edges (handoffs) and Breaks:
- BREAK-701: STEP-701 → STEP-702 (Manual Start) – monitoring not auto-started on run creation.
- BREAK-702: STEP-702 → STEP-703 (Missing Handoff) – UI backend not wired to required `.state/orchestration.db`; defaults to empty `.worktrees/pipeline_state.db`.
- BREAK-703: STEP-702 → STEP-704 (Manual Approval/Start) – archival not triggered by monitoring status changes.
- BREAK-704: STEP-704 → STEP-705 (Manual Start) – reports not chained from archival completion.
- BREAK-705: STEP-703 → downstream observability (No Error Propagation) – pattern event JSONL in `state_manager/src/state/events/*.jsonl` not ingested into UI/monitor logs.

## 8.3 Gap Inventory (Priority-Sorted)
| Gap ID | Type | Priority | Pipeline | Time Savings | Effort | Chain Impact |
|--------|------|----------|----------|--------------|--------|--------------|
| GAP-701 | Chain Break (Manual Start) | Critical | Monitoring | 2-3 hrs/run | 6-8 hrs | Run creation → monitoring never auto-starts |
| GAP-702 | Missing Validation/State Wiring | High | Monitoring | 1-2 hrs/week | 4-6 hrs | UI reads empty DB; no live data |
| GAP-703 | Manual Workflow | High | Archival/Reporting | 3-4 hrs/month | 4-6 hrs | Archival/report not triggered automatically |
| GAP-704 | Patternless CLI Execution | Medium | Observability | 1-2 hrs/week | 4-6 hrs | JSONL events not surfaced; no alerting |

## 8.4 Detailed Recommendations

### GAP-701
- Chain Break ID: BREAK-701
- Priority: Critical
- RECOMMENDATION
  - Title: Auto-start monitoring on run creation
  - Solution: Add watcher/trigger that launches monitoring pipeline when `runs` table marks a new run or `RUN_CREATED` flag appears.
    - Tool/Technology: SQLite trigger + lightweight daemon (Python) watching `.state/orchestration.db`; or hook in orchestrator CLI to spawn monitoring.
    - Implementation:
      1. Add `orchestrator monitor --auto` mode that subscribes to `runs` table changes and starts `PipelineTUI` with `use_mock_data=False`.
      2. Extend monitoring entry to emit heartbeat to `logs/monitor.jsonl`.
      3. Make run completion emit `RUN_COMPLETED` → auto-stop monitoring.
    - Integration point: `phase7_monitoring/README.md` entrypoints; `gui/tui_app/main.py` CLI wrapper.
  - Effort Estimate: 6-8 hours
  - Expected Benefits: Auto coverage for every run; ~2-3 hrs saved/run; removes manual “start monitor” step.
  - Implementation Steps:
    1. Add CLI flag `--auto` in `gui/tui_app/main.py` to poll `.state/orchestration.db` for active run.
    2. Wire orchestrator command `monitor --run <id>` to default to auto when `RUN_CREATED` is set.
    3. Document behavior in `phase7_monitoring/README.md`.
  - Dependencies: Access to `.state/orchestration.db`; run metadata populated upstream.
  - Quick Win Potential: Yes – wrapper + polling loop, no schema changes.

### GAP-702
- Chain Break ID: BREAK-702
- Priority: High
- RECOMMENDATION
  - Title: Point monitoring UI at authoritative state DB with validation
  - Solution:
    - Tool/Technology: SQLiteStateBackend enhancements with DSN from config.
    - Implementation:
      1. Align backend path to `.state/orchestration.db` instead of `.worktrees/pipeline_state.db` (configurable override).
      2. Add startup validation that required tables (`runs`, `tasks`, `workstreams`) exist; fail fast with logged error.
      3. Add health-check action in TUI to surface DB connection issues.
    - Integration point: `gui/tui_app/core/sqlite_state_backend.py`, `tui_app/config/tui_config.yaml`.
  - Effort Estimate: 4-6 hours
  - Expected Benefits: Eliminates empty dashboards; prevents silent misroutes of state.
  - Implementation Steps:
    1. Add config field `state_db_path` with default `.state/orchestration.db`.
    2. Implement validation helper to assert tables exist; display warning panel when missing.
    3. Update README to instruct setting path and validation behavior.
  - Dependencies: Actual DB available at `.state/orchestration.db`.
  - Quick Win Potential: Yes.

### GAP-703
- Chain Break IDs: BREAK-703, BREAK-704
- Priority: High
- RECOMMENDATION
  - Title: Chain archival and reporting to run completion
  - Solution:
    - Tool/Technology: Orchestrator hook or small scheduler to watch `runs.status` transitions.
    - Implementation:
      1. Add watcher that triggers `orchestrator archive --run <id>` when `runs.status` becomes `COMPLETED/FAILED`.
      2. After archival success, auto-run `orchestrator report --run <id>`; write results to `reports/<run_id>_summary.json`.
      3. Emit events `RUN_ARCHIVED`, `REPORT_GENERATED` to `logs/archival.jsonl`.
    - Integration point: Documented in `phase7_monitoring/README.md` entrypoints.
  - Effort Estimate: 4-6 hours
  - Expected Benefits: Removes two manual steps; saves 3-4 hrs/month; consistent artifacts.
  - Implementation Steps:
    1. Add CLI wrapper `orchestrator monitor --complete` to run archive+report chain when run ends.
    2. Add retry with backoff for archival/report failures.
    3. Surface completion status in monitoring UI footer.
  - Dependencies: Archival/report commands functional.
  - Quick Win Potential: Yes.

### GAP-704
- Chain Break ID: BREAK-705
- Priority: Medium
- RECOMMENDATION
  - Title: Ingest pattern event JSONL into monitoring UI with alerts
  - Solution:
    - Tool/Technology: JSONL tailer feeding SQLite tables or in-memory adapter.
    - Implementation:
      1. Add loader that ingests `state_manager/src/state/events/pattern_events.jsonl` into `uet_executions`/`uet_tasks` on startup.
      2. Add log tailing to stream new events into `logs/monitor.jsonl` and trigger UI refresh.
      3. Add alerting rule when `event_type` ends with `.failed` to highlight in dashboard.
    - Integration point: `gui/tui_app/core/sqlite_state_backend.py` (ingest) and `pattern_client` for event sourcing.
  - Effort Estimate: 4-6 hours
  - Expected Benefits: Surfaces failures automatically; 1-2 hrs/week saved in log-scraping; better MTTR.
  - Implementation Steps:
    1. Implement ingestion utility using JSONL reader with checkpointing.
    2. Add CLI flag `--ingest-events` to `gui.tui_app.main`.
    3. Expose last error in dashboard panel.
  - Dependencies: Access to JSONL files; write access to state DB.
  - Quick Win Potential: Yes.

## 8.5 Implementation Roadmap
- Phase 1 (Quick Wins – Week 1-2): Implement GAP-702 (state DB alignment/validation); add `--ingest-events` flag and JSONL ingestion (GAP-704).
- Phase 2 (High Impact – Month 1): Auto-start monitoring (GAP-701) with heartbeat logging; chain archival+report (GAP-703).
- Phase 3 (Long-term – Quarter 1): Expand monitoring to raise alerts/metrics to central system and add retries/backoff around archival/report flows.

## 8.6 Appendix
- Evidence:
  - Manual entrypoints only (`phase7_monitoring/README.md`): `orchestrator monitor/archive/report` listed as CLI calls; no automation glue.
  - TUI manual invocation & no orchestration (`modules/gui_components/src/gui/tui_app/main.py`): argparse-only CLI; no triggers/timeouts/alerts.
  - State backend default mismatch (`modules/gui_components/src/gui/tui_app/core/sqlite_state_backend.py`): defaults to `.worktrees/pipeline_state.db`, not `.state/orchestration.db`; creates empty schema silently.
  - Event logs unused (`modules/state_manager/src/state/events/pattern_events.jsonl` and per-job JSONL files): recorded events not consumed by UI or monitor.
  - Archival/report only described, not chained (`phase7_monitoring/README.md` exit_artifacts and entrypoints).
