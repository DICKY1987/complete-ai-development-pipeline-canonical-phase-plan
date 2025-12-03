# Phase 7 – Monitoring, Completion & Archival

**Purpose**: Live monitoring, dashboards, run completion, artifact archival, reporting.

## Current Components
- See `gui/` for UI components
- See `state/` for state persistence
- See `core/ui_cli.py`

## Main Operations
- Show runs/workstreams/tasks status in CLI dashboard, UI, or JSON
- Surface tool health metrics and error counts
- Mark runs as COMPLETED/FAILED/PARTIAL
- Archive artifacts, logs, final DB snapshot

## Related Code
- GUI/TUI pipelines
- DB views: `runs`, `workstreams`, `file_lifecycle`, `tool_health_metrics`, `error_records`
- Visual dashboards
