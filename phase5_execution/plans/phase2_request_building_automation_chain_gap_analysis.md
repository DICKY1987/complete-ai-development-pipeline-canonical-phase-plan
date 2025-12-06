---
doc_id: DOC-GUIDE-PHASE2-REQUEST-BUILDING-AUTOMATION-254
---

# Automation Chain Gap Analysis – Phase 2 Request Building (CLI)

## 8.1 Executive Summary
- Total gaps identified: 3; chain breaks: 3; critical chain breaks: 1; high-impact quick wins: 2.
- Phase2 is documented as production-ready, but this directory contains only docs (no runnable CLI/wrapper); automation relies on manual invocation.
- No visible hook from phase1 completion to auto-trigger request building; state/log emission and validation gates are described but not implemented here.
- Potential time savings from fixes: ~4-6 hours/week; estimated effort: ~10-14 hours for initial automation wiring.

## 8.2 Automation Chain Map (Request Building Pipeline)
- Nodes (STEP IDs):
  - STEP-201 (ENTRY_POINT): Trigger after phase1 planning completion; current automation_class: MANUAL (no orchestrated hook present in this directory); trigger: CLI_manual; state_integration: none; error_handling: none.
  - STEP-202 (INTERNAL_STEP): Build execution request via `execution_request_builder` (intended `orchestrator request --workstream <id>` / `python -m core.engine.execution_request_builder`); automation_class: MANUAL; trigger: CLI_manual; state_integration: none; error_handling: none.
  - STEP-203 (INTERNAL_STEP): Validate request against `schema/execution_request.v1.json`; automation_class: SEMI_MANUAL (validation only runs if invoked manually); trigger: CLI_manual; state_integration: logs_only (planned); error_handling: log_only.
  - STEP-204 (TERMINAL_STEP): Persist run records to `.state/orchestration.db`, append `.state/transitions.jsonl`, emit events `RUN_CREATED`/`EXECUTION_REQUEST_VALIDATED`; automation_class: MANUAL (no evidence of automatic write/emit from this dir); trigger: none; state_integration: none; error_handling: none.
- Edges (handoffs with BREAK IDs):
  - BREAK-201: STEP-201 → STEP-202 (Manual Start) – No automated trigger from phase1 success to start request building.
  - BREAK-202: STEP-202 → STEP-203 (Patternless CLI Use) – CLI described but no wrapper/state integration; manual invocation required for validation.
  - BREAK-203: STEP-203 → STEP-204 (Missing Handoff) – No automated persistence/events observed; outputs only described in README.

## 8.3 Gap Inventory (Priority-Sorted)
| Gap ID | Type | Priority | Pipeline | Time Savings | Effort | Chain Impact |
| --- | --- | --- | --- | --- | --- | --- |
| GAP-201 | Chain Break | Critical | Request Build | 2-3 hrs/week | 6-8 hrs | Connects phase1 completion to automated request creation |
| GAP-202 | Patternless Execution | High | Request Build | 1-2 hrs/week | 2-3 hrs | Ensures CLI runs with state/logs and retries |
| GAP-203 | Missing Persistence Handoff | High | Request Build | 1 hr/week | 2-3 hrs | Enables downstream scheduling via DB/state updates |

## 8.4 Detailed Recommendations

### GAP-201 (Chain Break) – Auto-trigger request builder after phase1
- Priority: Critical
- RECOMMENDATION: Wire an automated trigger from phase1 completion to request builder.
- Solution:
  - Tool/Technology: CI/workflow hook or file/state watcher on phase1 outputs; CLI wrapper call.
  - Implementation: Add orchestrator step that, on `PLANNING_COMPLETE` flag or presence of `workstreams/*.json`, invokes `python -m core.engine.execution_request_builder --workstream <id>`.
  - Integration point: `phase2_request_building/README.md:90-99` (entrypoints) and phase contract inputs.
- Effort Estimate: 6-8 hrs
- Expected Benefits:
  - Time saved: 2-3 hrs/week (eliminates manual starts)
  - Error reduction: Lowers missed/late request creation; consistent trigger
  - Chain impact: Removes BREAK-201; establishes automated ENTRY_POINT
- Implementation Steps:
  1) Add watcher/CI job that detects phase1 completion and invokes the builder CLI.
  2) Pass workstream IDs from phase1 outputs to the CLI automatically.
  3) Emit start/finish status to logs for monitoring.
- Dependencies: Workstream JSON availability; schema files accessible.
- Quick Win Potential: Yes – small orchestrator hook and CLI call.

### GAP-202 (Patternless Execution) – Standardize CLI wrapper with state/logs
- Priority: High
- RECOMMENDATION: Run the request builder via a standard wrapper that enforces timeouts, structured logs, and retries.
- Solution:
  - Tool/Technology: Existing orchestrator CLI wrapper pattern; JSONL logging to `logs/request_builder.jsonl`; timeout/resilience guard.
  - Implementation: Wrap `execution_request_builder` invocation so stdout/stderr and exit codes are captured; enforce timeout and retry once on transient errors; record results in `.state/transitions.jsonl`.
  - Integration point: `phase2_request_building/README.md:57-68` (main ops) and `phase2_request_building/README.md:104-118` (observability).
- Effort Estimate: 2-3 hrs
- Expected Benefits:
  - Time saved: 1-2 hrs/week (fewer reruns/manual checks)
  - Error reduction: Better visibility and retry reduces failed attempts
  - Chain impact: Addresses BREAK-202; improves INTERNAL_STEP reliability
- Implementation Steps:
  1) Add wrapper command that logs invocation metadata and enforces timeout.
  2) Persist validation results and any errors to `logs/request_builder.jsonl`.
  3) Integrate with existing resilience/error hooks if available.
- Dependencies: Logging location writeable; resilience utilities available.
- Quick Win Potential: Yes – minimal code around existing CLI.

### GAP-203 (Missing Persistence Handoff) – Automate DB/state writes and events
- Priority: High
- RECOMMENDATION: Ensure request builder writes run records and emits events automatically.
- Solution:
  - Tool/Technology: SQLite writes to `.state/orchestration.db`, JSONL appends, event emitter.
  - Implementation: After validation, automatically create `runs` rows and append `.state/transitions.jsonl`; emit `RUN_CREATED` and `EXECUTION_REQUEST_VALIDATED` events for schedulers to consume.
  - Integration point: `phase2_request_building/README.md:31-44` (exit artifacts) and `phase2_request_building/README.md:104-118` (observability).
- Effort Estimate: 2-3 hrs
- Expected Benefits:
  - Time saved: ~1 hr/week (no manual DB edits/log copying)
  - Error reduction: Lowers risk of missing run records or inconsistent state
  - Chain impact: Closes BREAK-203; enables phase3 scheduling automatically
- Implementation Steps:
  1) Add persistence layer call after successful validation to update DB and transitions ledger.
  2) Emit events/signals consumable by phase3 schedulers.
  3) Include failure paths that log and return non-zero exit codes for monitoring.
- Dependencies: DB schema availability; ledger write access.
- Quick Win Potential: Yes – leverage existing state modules referenced in README.

## 8.5 Implementation Roadmap
- Phase 1 (Week 1-2): Close GAP-201 by adding automated trigger from phase1 outputs.
- Phase 2 (Week 2): Close GAP-202 with wrapper/timeout/logging.
- Phase 3 (Week 2-3): Close GAP-203 with DB/ledger writes and event emission.

## 8.6 Appendix (Evidence)
- `phase2_request_building/README.md:90-99` lists entrypoints but no executable scripts in this directory.
- `phase2_request_building/README.md:31-44` describes required outputs, yet this folder contains only README files (no builders/loggers).
- `phase2_request_building/README.md:104-118` documents observability targets, but no log/state-producing code is present here, indicating missing automation wiring.
