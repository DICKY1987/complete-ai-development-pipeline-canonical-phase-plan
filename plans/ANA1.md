---
doc_id: DOC-GUIDE-ANA1-181
---


• Added plans\phase4_routing_automation_chain_report.md (+99 -0)
     1 +# Phase 4 Routing — Automation Chain & Gap Report
     2 +
     3 +## Executive Summary
     4 +- Total gaps: 5; chain breaks: 4 (critical: 2, high: 2). Qu
        ick-win opportunities: 3. Estimated savings: ~14-18 hrs/mon
        th with ~20-26 hrs effort.
     5 +- Routing entry is documented as “automatic” but implemente
        d as ad-hoc CLI/manual runs; no watcher, queue consumer, or
         state propagation (`phase4_routing/README.md` entrypoints
        are standalone).
     6 +- Adapter/pool layer is partial: registry loading is a stub
        , routing lacks retries/health escalation, and no events/st
        ates are emitted to phase5 (`.../aim/process_pool.py`, `clu
        ster_manager.py`).
     7 +- Log aggregation/analysis is entirely manual, with hardcod
        ed absolute paths and TTY-only scripts; scheduled-task help
        er points to a non-existent path and is not wired to the ro
        uter pipeline (`.../ai-logs-analyzer/scripts/*.ps1`).
     8 +- Pool-aware adapter is patternless (direct `/ask` sends, n
        o error/reporting hooks), so routing decisions are not obse
        rvable or recoverable (`.../pool_adapter_mixin.py`).
     9 +
    10 +## Automation Chain Map
    11 +
    12 +### Pipeline A — Task Routing to Adapters
    13 +- STEP-401 (ENTRY_POINT, MANUAL, trigger=CLI_manual): Opera
        tor runs `orchestrator route --run <id>` or `python -m core
        .engine.router`; no watcher/queue consumer exists (`phase4_
        routing/README.md`).
    14 +- STEP-402 (INTERNAL_STEP, SEMI_MANUAL, trigger=code_call,
        state_integration=none): Adapter selection via `ClusterMana
        ger`/`create_router` using in-memory state only; no registr
        y persistence (`modules/aim_tools/src/aim/cluster_manager.p
        y`, `routing.py`).
    15 +- STEP-403 (INTERNAL_STEP, SEMI_MANUAL, trigger=code_call,
        state_integration=logs_only): Tool invocation via `ToolProc
        essPool` spawning long-lived CLIs with stdout/stderr queues
        ; registry loader is a TODO stub and there is no timeout/ba
        ckoff (`modules/aim_tools/src/aim/process_pool.py`).
    16 +- STEP-404 (TERMINAL_STEP, MANUAL, trigger=human_followup,
        state_integration=none): No emitted events or `.state/routi
        ng_decisions.json`; downstream phase5 handoff is undocument
        ed in code.
    17 +
    18 +Edges / Breaks:
    19 +- BREAK-401 (Manual Start): STEP-401 is not auto-triggered
        from phase3 state queue.
    20 +- BREAK-402 (Missing Handoff): No state/DB/log event links
        STEP-402 → STEP-404; results never persisted.
    21 +- BREAK-403 (No Error Propagation): Pool errors/health not
        surfaced to any central monitor; failures stop silently.
    22 +
    23 +### Pipeline B — AI Tool Log Aggregation & Analysis
    24 +- STEP-501 (ENTRY_POINT, MANUAL, trigger=CLI_manual): `aggr
        egate-logs.ps1` run by hand with hardcoded repo path (`.../
        ai-logs-analyzer/scripts/aggregate-logs.ps1`).
    25 +- STEP-502 (INTERNAL_STEP, MANUAL, trigger=CLI_manual): `an
        alyze-logs.ps1` assumes prior manual aggregation and render
        s ad-hoc reports (`.../scripts/analyze-logs.ps1`).
    26 +- STEP-503 (TERMINAL_STEP, MANUAL, trigger=CLI_manual): `wa
        tch-logs.ps1` TTY loop for eyeballing activity; no alerting
         or export (`.../scripts/watch-logs.ps1`).
    27 +- STEP-504 (TERMINAL_STEP, SEMI_MANUAL, trigger=scheduled_t
        ask_manual): `setup-scheduled-task.ps1` can register a dail
        y task but points to a non-existent absolute path and is ne
        ver invoked by the routing pipeline.
    28 +
    29 +Edges / Breaks:
    30 +- BREAK-501 (Manual Start): Aggregation is never auto-run;
        depends on operator.
    31 +- BREAK-502 (Missing Handoff): Analysis consumes manual out
        put only; no metrics pushed to router/monitoring.
    32 +- BREAK-503 (Patternless CLI Use): Log watching is TTY-only
         with no alerts or retention.
    33 +
    34 +## Gap Inventory (priority-sorted)
    35 +- GAP-401 | Chain Break | Critical | Routing | 4-6 hrs/mo s
        aved | 6-8 hrs | Entry to router is manual; no watcher from
         phase3 queue.
    36 +- GAP-402 | Incomplete Automation | High | Routing | 3-4 hr
        s/mo | 6-8 hrs | Router/pool lacks registry/state integrati
        on and retries; results not persisted.
    37 +- GAP-403 | Patternless Execution | High | Routing | 2-3 hr
        s/mo | 4-6 hrs | PoolAware adapter bypasses observability/e
        rror hooks.
    38 +- GAP-501 | Manual Workflow | Medium | Logs | 3-4 hrs/mo |
        3-5 hrs | Log aggregation/analysis entirely manual with bri
        ttle paths.
    39 +- GAP-502 | Missing Validation | Medium | Logs | 1-2 hrs/mo
         | 2-3 hrs | No alerting/health signals from log monitors;
        TTY-only.
    40 +
    41 +## Detailed Recommendations
    42 +
    43 +### GAP-401 (Priority: Critical)
    44 +- Title: Add queue watcher to auto-trigger routing
    45 +- Solution: Implement a lightweight watcher that tails `.st
        ate/task_queue.json` (or DB `tasks` table) and invokes rout
        er when new tasks appear.
    46 +  - Tool/Tech: Python/psutil watchdog (or existing orchestr
        ator runner if available).
    47 +  - Implementation: new `core/engine/router_runner.py` wrap
        per to poll/subscribe, call `route_tasks()`, enforce timeou
        t, and write `.state/routing_decisions.json`.
    48 +  - Integration: Hook into phase3 completion event (or file
         watcher) and emit `ROUTING_COMPLETE`.
    49 +- Effort: 6-8 hrs. Benefits: removes manual start; enables
        full auto chain to phase4. Quick Win: Yes (scoped wrapper).
    50 +- Dependencies: Access to phase3 queue format.
    51 +
    52 +### GAP-402 (Priority: High)
    53 +- Title: Wire router/pool to real registry + persisted stat
        e
    54 +- Solution: Replace stub registry with loader + validation;
         persist routing outcomes.
    55 +  - Tool/Tech: Use existing `config/tool_profiles/*.yaml` l
        oader; add JSONL writer for routing decisions.
    56 +  - Implementation: in `process_pool.py`, load registry fro
        m config; add startup health check and per-send timeout/bac
        koff; in `cluster_manager.py`, on send/read, log to `logs/a
        dapter_selection.jsonl` and emit `routing_decisions.json`.
    57 +  - Integration: Phase4 `.state` outputs defined in `README
        .md` and phase5 intake.
    58 +- Effort: 6-8 hrs. Benefits: stateful routing, auditable ha
        ndoff, fewer silent drops. Quick Win: Partial (registry loa
        der is straightforward).
    59 +- Dependencies: Access to tool profile schema; disk write l
        ocation.
    60 +
    61 +### GAP-403 (Priority: High)
    62 +- Title: Standardize pool-aware adapter invocation + metric
        s
    63 +- Solution: Add adapter wrapper that routes through `Cluste
        rManager` with structured telemetry.
    64 +  - Tool/Tech: Decorator or mixin update in `pool_adapter_m
        ixin.py`.
    65 +  - Implementation: add timing/timeout handling, retries on
         dead instance, and event logging (JSONL) for send/read; ac
        cept a logger/state sink to avoid silent failures; expose `
        get_pool_status()` to health monitor.
    66 +  - Integration: Hook into adapter registry so all adapter
        invocations pass through wrapper.
    67 +- Effort: 4-6 hrs. Benefits: observability + automatic fail
        over; enables automated alerts. Quick Win: Yes.
    68 +- Dependencies: Logging path and schema alignment with phas
        e6/phase7.
    69 +
    70 +### GAP-501 (Priority: Medium)
    71 +- Title: Automate log aggregation and analysis with correct
         paths
    72 +- Solution: Wrap `aggregate-logs.ps1` + `analyze-logs.ps1`
        in a scheduled runner with repo-relative paths.
    73 +  - Tool/Tech: PowerShell scheduled task or Python cron-equ
        ivalent (cross-platform).
    74 +  - Implementation: fix script path resolution (use `$PSScr
        iptRoot`), add non-interactive mode, write summary to `logs
        /ai-tools/summary.json`, and return non-zero on failure.
    75 +  - Integration: Trigger after routing runs; drop metrics f
        or phase7 monitoring.
    76 +- Effort: 3-5 hrs. Benefits: saves manual runs; creates con
        sumable metrics. Quick Win: Yes (path fix + scheduled task)
        .
    77 +- Dependencies: Permissions to register scheduled task or r
        un CI job.
    78 +
    79 +### GAP-502 (Priority: Medium)
    80 +- Title: Add alerting/health signals for AI tool activity
    81 +- Solution: Extend `watch-logs.ps1` to emit notifications (
        email/Teams/webhook) and expose a JSON heartbeat file consu
        med by monitors.
    82 +  - Tool/Tech: PowerShell + webhook; simple JSON heartbeat
        writer.
    83 +  - Implementation: add `-NonInteractive` flag, write heart
        beat to `.state/ai_logs_heartbeat.json`, optionally send we
        bhook on anomalies.
    84 +  - Integration: Phase7 monitoring ingestion.
    85 +- Effort: 2-3 hrs. Benefits: converts eyeballing into actio
        nable alerts; reduces missed failures. Quick Win: Partial.
    86 +- Dependencies: Destination for alerts (webhook URL).
    87 +
    88 +## Implementation Roadmap
    89 +- Phase 1 (Week 1-2): GAP-401 watcher + GAP-501 path fix/sc
        heduler; start JSONL logging for GAP-402.
    90 +- Phase 2 (Month 1): Complete GAP-402 registry/state persis
        tence; GAP-403 adapter telemetry/retries.
    91 +- Phase 3 (Quarter 1): GAP-502 alerting + integrate routing
        /aggregation outputs into phase7 monitors.
    92 +
    93 +## Appendix
    94 +- Evidence
    95 +  - Manual entrypoint only: `phase4_routing/README.md` (inv
        ocation_mode and CLI entrypoints).
    96 +  - Stub registry/no state: `modules/aim_tools/src/aim/proc
        ess_pool.py` (`load_aim_registry()` TODO, no timeouts/loggi
        ng); `cluster_manager.py` (in-memory metrics only).
    97 +  - Patternless adapter: `modules/aim_tools/src/aim/pool_ad
        apter_mixin.py` (direct `/ask` calls, no error/telemetry).
    98 +  - Manual log workflows: `modules/aim_tools/src/aim/ai-log
        s-analyzer/scripts/aggregate-logs.ps1`, `analyze-logs.ps1`,
         `watch-logs.ps1`, `setup-scheduled-task.ps1` (hardcoded pa
        th).
    99 +  - Entry/exit artifacts missing in code: `.state/routing_d
        ecisions.json` not produced anywhere in module sources.