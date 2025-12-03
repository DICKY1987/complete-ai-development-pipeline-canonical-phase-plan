# Phase 7 – Monitoring, Completion & Archival

**Purpose**: Live monitoring, dashboards, run completion, artifact archival, reporting.

## Phase Contents

Located in: `phase7_monitoring/`

- `gui/` - UI components and dashboards
- `state/` - State persistence and databases
- `README.md` - This file

## Current Components

### GUI Components (`gui/`)
- `ui_infrastructure_usage.py` - Infrastructure dashboard ⚠️ (partial)
- `ui_tool_selection_demo.py` - Tool selection UI ⚠️ (partial)

### State Persistence (`state/`)
- Working state directory
- Alternative to `.state/` for state files

### Implementation (`core/`)
Located in cross-cutting `core/` directory:
- `core/ui_cli.py` - CLI dashboard interface ⚠️ (minimal)
- `core/ui_models.py` - UI data models ✅
- `core/ui_settings.py` - UI configuration ✅
- `core/ui_settings_cli.py` - CLI settings ✅
- `core/engine/monitoring/progress_tracker.py` - Progress visualization ✅
- `core/engine/monitoring/run_monitor.py` - Run status tracking ✅
- `core/planning/archive.py` - Artifact archival ✅

## Main Operations
- Show runs/workstreams/tasks status in CLI dashboard, UI, or JSON
- Surface tool health metrics and error counts
- Mark runs as COMPLETED/FAILED/PARTIAL
- Archive artifacts, logs, final DB snapshot

## Database Views
- `runs` - Run records
- `workstreams` - Workstream status
- `file_lifecycle` - File state tracking
- `tool_health_metrics` - Tool performance
- `error_records` - Error history

## Missing Components
- ❌ Dashboard/TUI (rich CLI)
- ❌ Web UI
- ❌ Artifact compression
- ❌ Report generation templates
- ❌ Metrics export (Prometheus, etc.)
- ❌ Historical run analysis

## Test Coverage
~15 tests for monitoring components

## Status
⚠️ Partial (30%) - UI components need implementation
