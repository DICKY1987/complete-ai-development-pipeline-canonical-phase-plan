---
doc_id: DOC-GUIDE-PHASE4-ROUTING-AUTOMATION-CHAIN-REPORT-171
---

# Phase 4 Routing — Automation Chain & Gap Report

## Executive Summary
- Total gaps: 5; chain breaks: 4 (critical: 2, high: 2). Quick-win opportunities: 3. Estimated savings: ~14-18 hrs/month with ~20-26 hrs effort.
- Routing entry is documented as “automatic” but implemented as ad-hoc CLI/manual runs; no watcher, queue consumer, or state propagation (`phase4_routing/README.md` entrypoints are standalone).
- Adapter/pool layer is partial: registry loading is a stub, routing lacks retries/health escalation, and no events/states are emitted to phase5 (`.../aim/process_pool.py`, `cluster_manager.py`).
- Log aggregation/analysis is entirely manual, with hardcoded absolute paths and TTY-only scripts; scheduled-task helper points to a non-existent path and is not wired to the router pipeline (`.../ai-logs-analyzer/scripts/*.ps1`).
- Pool-aware adapter is patternless (direct `/ask` sends, no error/reporting hooks), so routing decisions are not observable or recoverable (`.../pool_adapter_mixin.py`).

## Automation Chain Map

### Pipeline A — Task Routing to Adapters
- STEP-401 (ENTRY_POINT, MANUAL, trigger=CLI_manual): Operator runs `orchestrator route --run <id>` or `python -m core.engine.router`; no watcher/queue consumer exists (`phase4_routing/README.md`).
- STEP-402 (INTERNAL_STEP, SEMI_MANUAL, trigger=code_call, state_integration=none): Adapter selection via `ClusterManager`/`create_router` using in-memory state only; no registry persistence (`modules/aim_tools/src/aim/cluster_manager.py`, `routing.py`).
- STEP-403 (INTERNAL_STEP, SEMI_MANUAL, trigger=code_call, state_integration=logs_only): Tool invocation via `ToolProcessPool` spawning long-lived CLIs with stdout/stderr queues; registry loader is a TODO stub and there is no timeout/backoff (`modules/aim_tools/src/aim/process_pool.py`).
- STEP-404 (TERMINAL_STEP, MANUAL, trigger=human_followup, state_integration=none): No emitted events or `.state/routing_decisions.json`; downstream phase5 handoff is undocumented in code.

Edges / Breaks:
- BREAK-401 (Manual Start): STEP-401 is not auto-triggered from phase3 state queue.
- BREAK-402 (Missing Handoff): No state/DB/log event links STEP-402 → STEP-404; results never persisted.
- BREAK-403 (No Error Propagation): Pool errors/health not surfaced to any central monitor; failures stop silently.

### Pipeline B — AI Tool Log Aggregation & Analysis
- STEP-501 (ENTRY_POINT, MANUAL, trigger=CLI_manual): `aggregate-logs.ps1` run by hand with hardcoded repo path (`.../ai-logs-analyzer/scripts/aggregate-logs.ps1`).
- STEP-502 (INTERNAL_STEP, MANUAL, trigger=CLI_manual): `analyze-logs.ps1` assumes prior manual aggregation and renders ad-hoc reports (`.../scripts/analyze-logs.ps1`).
- STEP-503 (TERMINAL_STEP, MANUAL, trigger=CLI_manual): `watch-logs.ps1` TTY loop for eyeballing activity; no alerting or export (`.../scripts/watch-logs.ps1`).
- STEP-504 (TERMINAL_STEP, SEMI_MANUAL, trigger=scheduled_task_manual): `setup-scheduled-task.ps1` can register a daily task but points to a non-existent absolute path and is never invoked by the routing pipeline.

Edges / Breaks:
- BREAK-501 (Manual Start): Aggregation is never auto-run; depends on operator.
- BREAK-502 (Missing Handoff): Analysis consumes manual output only; no metrics pushed to router/monitoring.
- BREAK-503 (Patternless CLI Use): Log watching is TTY-only with no alerts or retention.

## Gap Inventory (priority-sorted)
- GAP-401 | Chain Break | Critical | Routing | 4-6 hrs/mo saved | 6-8 hrs | Entry to router is manual; no watcher from phase3 queue.
- GAP-402 | Incomplete Automation | High | Routing | 3-4 hrs/mo | 6-8 hrs | Router/pool lacks registry/state integration and retries; results not persisted.
- GAP-403 | Patternless Execution | High | Routing | 2-3 hrs/mo | 4-6 hrs | PoolAware adapter bypasses observability/error hooks.
- GAP-501 | Manual Workflow | Medium | Logs | 3-4 hrs/mo | 3-5 hrs | Log aggregation/analysis entirely manual with brittle paths.
- GAP-502 | Missing Validation | Medium | Logs | 1-2 hrs/mo | 2-3 hrs | No alerting/health signals from log monitors; TTY-only.

## Detailed Recommendations

### GAP-401 (Priority: Critical)
- Title: Add queue watcher to auto-trigger routing
- Solution: Implement a lightweight watcher that tails `.state/task_queue.json` (or DB `tasks` table) and invokes router when new tasks appear.
  - Tool/Tech: Python/psutil watchdog (or existing orchestrator runner if available).
  - Implementation: new `core/engine/router_runner.py` wrapper to poll/subscribe, call `route_tasks()`, enforce timeout, and write `.state/routing_decisions.json`.
  - Integration: Hook into phase3 completion event (or file watcher) and emit `ROUTING_COMPLETE`.
- Effort: 6-8 hrs. Benefits: removes manual start; enables full auto chain to phase4. Quick Win: Yes (scoped wrapper).
- Dependencies: Access to phase3 queue format.

### GAP-402 (Priority: High)
- Title: Wire router/pool to real registry + persisted state
- Solution: Replace stub registry with loader + validation; persist routing outcomes.
  - Tool/Tech: Use existing `config/tool_profiles/*.yaml` loader; add JSONL writer for routing decisions.
  - Implementation: in `process_pool.py`, load registry from config; add startup health check and per-send timeout/backoff; in `cluster_manager.py`, on send/read, log to `logs/adapter_selection.jsonl` and emit `routing_decisions.json`.
  - Integration: Phase4 `.state` outputs defined in `README.md` and phase5 intake.
- Effort: 6-8 hrs. Benefits: stateful routing, auditable handoff, fewer silent drops. Quick Win: Partial (registry loader is straightforward).
- Dependencies: Access to tool profile schema; disk write location.

### GAP-403 (Priority: High)
- Title: Standardize pool-aware adapter invocation + metrics
- Solution: Add adapter wrapper that routes through `ClusterManager` with structured telemetry.
  - Tool/Tech: Decorator or mixin update in `pool_adapter_mixin.py`.
  - Implementation: add timing/timeout handling, retries on dead instance, and event logging (JSONL) for send/read; accept a logger/state sink to avoid silent failures; expose `get_pool_status()` to health monitor.
  - Integration: Hook into adapter registry so all adapter invocations pass through wrapper.
- Effort: 4-6 hrs. Benefits: observability + automatic failover; enables automated alerts. Quick Win: Yes.
- Dependencies: Logging path and schema alignment with phase6/phase7.

### GAP-501 (Priority: Medium)
- Title: Automate log aggregation and analysis with correct paths
- Solution: Wrap `aggregate-logs.ps1` + `analyze-logs.ps1` in a scheduled runner with repo-relative paths.
  - Tool/Tech: PowerShell scheduled task or Python cron-equivalent (cross-platform).
  - Implementation: fix script path resolution (use `$PSScriptRoot`), add non-interactive mode, write summary to `logs/ai-tools/summary.json`, and return non-zero on failure.
  - Integration: Trigger after routing runs; drop metrics for phase7 monitoring.
- Effort: 3-5 hrs. Benefits: saves manual runs; creates consumable metrics. Quick Win: Yes (path fix + scheduled task).
- Dependencies: Permissions to register scheduled task or run CI job.

### GAP-502 (Priority: Medium)
- Title: Add alerting/health signals for AI tool activity
- Solution: Extend `watch-logs.ps1` to emit notifications (email/Teams/webhook) and expose a JSON heartbeat file consumed by monitors.
  - Tool/Tech: PowerShell + webhook; simple JSON heartbeat writer.
  - Implementation: add `-NonInteractive` flag, write heartbeat to `.state/ai_logs_heartbeat.json`, optionally send webhook on anomalies.
  - Integration: Phase7 monitoring ingestion.
- Effort: 2-3 hrs. Benefits: converts eyeballing into actionable alerts; reduces missed failures. Quick Win: Partial.
- Dependencies: Destination for alerts (webhook URL).

## Implementation Roadmap
- Phase 1 (Week 1-2): GAP-401 watcher + GAP-501 path fix/scheduler; start JSONL logging for GAP-402.
- Phase 2 (Month 1): Complete GAP-402 registry/state persistence; GAP-403 adapter telemetry/retries.
- Phase 3 (Quarter 1): GAP-502 alerting + integrate routing/aggregation outputs into phase7 monitors.

## Appendix
- Evidence
  - Manual entrypoint only: `phase4_routing/README.md` (invocation_mode and CLI entrypoints).
  - Stub registry/no state: `modules/aim_tools/src/aim/process_pool.py` (`load_aim_registry()` TODO, no timeouts/logging); `cluster_manager.py` (in-memory metrics only).
  - Patternless adapter: `modules/aim_tools/src/aim/pool_adapter_mixin.py` (direct `/ask` calls, no error/telemetry).
  - Manual log workflows: `modules/aim_tools/src/aim/ai-logs-analyzer/scripts/aggregate-logs.ps1`, `analyze-logs.ps1`, `watch-logs.ps1`, `setup-scheduled-task.ps1` (hardcoded path).
  - Entry/exit artifacts missing in code: `.state/routing_decisions.json` not produced anywhere in module sources.
