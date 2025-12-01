---
doc_id: DOC-GUIDE-GUI-MODULE-ANALYSIS-SUMMARY-157
---

# GUI Module Analysis Summary

**Analysis Date:** 2025-11-26
**Task:** Determine Module Outputs & Suggested Visuals for Tile-Based Hybrid GUI
**Status:** ✅ Complete

---

## Quick Reference

**Full Analysis Document:** `MODULE_OUTPUTS_AND_VISUALS_ANALYSIS.md` (in same directory)

This summary provides a quick overview of what was analyzed and the key findings for your hybrid GUI–TUI pipeline system.

---

## Analysis Overview

### What Was Analyzed

I performed a read-only scan of your codebase to identify:
1. What outputs each engine/module produces (logs, JSON, DB tables, metrics)
2. What visualizations make sense for those outputs in your tile-based GUI

### Interface Context

Your application uses a **hybrid GUI shell** wrapped around a **TUI/terminal engine**:
- **Bottom 1/3:** Embedded terminal window (where tools like Aider, Codex, tests, git actually run)
- **Top 2/3:** Grid of tiles (plugin panels) that visualize state and results
- **GUI never calls tools directly** - only reads from engine's state store and job results

---

## Modules Discovered

### Engine Layer (New Architecture)

| Module | Role | Key Outputs |
|--------|------|-------------|
| `engine/orchestrator` | Job dispatch & execution | Logs, JSON error reports, DB step_attempts |
| `engine/queue` | Priority job queue | SQLite job_queue table, queue stats |
| `engine/state_store` | Job state persistence | SQLite runs/workstreams/step_attempts/events/errors |
| `engine/adapters` | Tool wrappers (aider, codex, tests, git) | Tool logs, JobResult objects |

### Core Modules (Legacy/Hybrid)

| Module | Role | Key Outputs |
|--------|------|-------------|
| `modules/core-state` | DB layer, telemetry | SQLite execution_logs, pattern_metrics |
| `modules/core-planning` | Workstream planning | JSON workstream bundles (stub) |
| `modules/core-engine` | UET router, scheduler | SQLite UET runs/steps/events, routing logs |
| `modules/error-engine` | Error pipeline, quarantine | JSONL error logs, validation reports |
| `modules/error-plugin-*` | 20+ error detectors | Plugin-specific JSON reports |
| `modules/aim-*` | AI tool registry | JSON registry, audit logs |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK` | Pattern system | Pattern events, telemetry |

---

## Output Categories

All modules produce outputs in these categories:

### 1. Database Tables (SQLite)
- **3 separate databases** with different schemas
- **15+ tables total:** runs, workstreams, step_attempts, events, errors, job_queue, pattern_metrics, etc.
- **Query patterns documented** in analysis document

### 2. Log Files
- **Tool logs:** `job["paths"]["log_file"]` (per-job execution logs)
- **System logs:** Console output from orchestrator, router, adapters
- **Error logs:** `pipeline_errors.jsonl` (aggregated error events)

### 3. JSON Reports
- **Error reports:** `job["paths"]["error_report"]` (per-job error details)
- **Validation reports:** `<file>_VALIDATED_<ts>_<run_id>.json` (error pipeline output)
- **Registry files:** `AIM_registry.json`, `router_config.json`

### 4. Real-Time Metrics
- **Queue stats:** queued, waiting, running, completed, failed counts
- **Pattern telemetry:** execution logs, success rates, avg durations
- **Circuit breakers:** open/closed states (planned)

---

## Top 10 Recommended Tiles

Based on the analysis, here are the highest-priority tiles to build:

### Phase 1: Essential (Build First)
1. **RunSelectorTile** - Choose which run to view (dropdown + recent runs list)
2. **JobQueueTile** - Show queued/waiting/running jobs (table + status bar)
3. **JobHistoryTile** - List recent jobs with status/duration (table with filters)
4. **GenericOutputTile** - Universal viewer for logs/JSON/tables (tabbed interface)

### Phase 2: Core Operations
5. **OrchestratorStatusTile** - Live orchestrator activity (log feed + status chips)
6. **ErrorQuarantineTile** - Manage quarantined items (table + release actions)
7. **WorkstreamKanbanTile** - Workflow visualization (kanban columns by status)

### Phase 3: Metrics & Insights
8. **GlobalDashboardTile** - System health overview (multi-panel dashboard)
9. **PatternMetricsTile** - Pattern usage analytics (table + charts)
10. **ToolHealthTile** - AIM registry status (status grid per tool)

---

## Visual Types Used

The analysis maps outputs to these visual patterns:

| Visual Type | Use Cases | Examples |
|-------------|-----------|----------|
| **Table** | Structured records | Jobs, errors, runs, queue items |
| **Timeline** | Events over time | Job starts/completions, error spikes |
| **Kanban Board** | Workflow stages | Workstreams (pending → running → done) |
| **Status Chips** | State indicators | Job status, tool health, quarantine flag |
| **Log Feed** | Live logs | Console output, tool execution logs |
| **DAG Visualization** | Dependencies | Job dependencies, workstream relationships |
| **Gauge/Sparkline** | Quick metrics | Queue depth, success rate, durations |
| **Card Grid** | Entity collections | Tool registry, plugins, patterns |
| **JSON Viewer** | Raw data | Job metadata, config files |
| **Progress Bar** | Completion % | Phase progress, run completion |

---

## Data Access Patterns

### For GUI to Read Data

**Database Queries:**
```python
from modules.core_state import m010003_crud as crud
runs = crud.list_runs(limit=20, status="running")

from engine.queue.job_queue import JobQueue
queue = JobQueue()
stats = queue.get_stats()
```

**File Watching:**
- Tail `pipeline_errors.jsonl` for new error events
- Tail `job["paths"]["log_file"]` for live job logs
- Watch DB file modified timestamp for changes

**Suggested Refresh Rates:**
- Live log viewers: 500ms - 1s
- Job queue status: 2-5s
- Metrics/charts: 10-30s
- Historical data: On-demand

---

## Database Schema Quick Reference

### Main Tables You'll Query

**runs** - Overall run records
- Fields: `run_id`, `status`, `created_at`, `metadata_json`

**workstreams** - Workstream definitions
- Fields: `run_id`, `ws_id`, `metadata_json`

**step_attempts** - Individual job executions
- Fields: `id`, `run_id`, `ws_id`, `step_name`, `status`, `started_at`, `completed_at`, `result_json`

**events** - Event log
- Fields: `id`, `run_id`, `ws_id`, `event_type`, `payload_json`, `timestamp`

**errors** - Error records
- Fields: `id`, `run_id`, `ws_id`, `category`, `tool`, `message`, `path`, `created_at`

**job_queue** - Queue state
- Fields: `job_id`, `priority`, `status`, `depends_on`, `retry_count`, `queued_at`, `started_at`

**pattern_metrics** - Pattern usage stats
- Fields: `pattern_id`, `total_uses`, `success_count`, `failure_count`, `avg_execution_seconds`, `last_used`

*(Full schemas with CREATE TABLE statements are in the main analysis document)*

---

## Cross-Module Visualizations

### 1. Pipeline Radar (Global)
Combines: Job queue + error pipeline + tool status
- Shows: Active runs, queued jobs, error rate, quarantine count
- Visual: Multi-metric dashboard with sparklines

### 2. System Event Timeline (Global)
Combines: events + error logs + pattern events
- Shows: Unified timeline of all events across modules
- Visual: Horizontal timeline with color-coded event types

### 3. Tool Status Grid (Global)
Combines: AIM registry + adapter results + circuit breakers
- Shows: Health/status of each tool (aider, codex, tests, git)
- Visual: Grid of status cards (green/yellow/red)

---

## Implementation Strategy

### Generic Output Tile First
Build a **universal tile** that can display any output:
- Tabs: Log (text), JSON (tree), Table (grid), Raw (plaintext)
- Syntax highlighting
- Search/filter
- Auto-refresh toggle

**Why:** You can wire up *any* module output immediately while designing custom visuals

### Then Build Custom Tiles Incrementally
1. Start with Phase 1 (essentials: run selector, job queue, job history)
2. Add Phase 2 (operations: orchestrator status, error quarantine)
3. Add Phase 3 (metrics: dashboard, patterns, tool health)
4. Add Phase 4 (advanced: dependency graphs, AI recommendations)

### Tile Manifest Pattern
Each tile should have a `.panel.json` manifest:
```json
{
  "panel_id": "job_queue_tile",
  "display_name": "Job Queue",
  "data_sources": [
    {
      "source_type": "db_table",
      "source_path": "pipeline.db:job_queue",
      "refresh_interval": 5000
    }
  ],
  "visual_type": "table_with_summary_bar",
  "supports_filtering": true
}
```

---

## Key Findings

### What's Available Now
✅ **Rich state data** in multiple SQLite databases
✅ **Detailed logs** from all tools and adapters
✅ **JSON reports** for errors and validation
✅ **Real-time metrics** from queue and patterns
✅ **Event streams** for timeline visualizations

### What's Well-Suited for Tiles
✅ **Job queue status** - Clear table/kanban view
✅ **Error quarantine** - Action-oriented tile (view/release)
✅ **Run timeline** - Event stream visualization
✅ **Pattern metrics** - Analytics dashboard
✅ **Tool health** - Status grid

### What Needs Generic Viewer Initially
⚠️ **Raw logs** - Use generic log viewer until custom formatter built
⚠️ **Complex JSON** - Use generic JSON tree viewer
⚠️ **Router decisions** - Use generic log feed initially

---

## Next Steps for GUI Development

### 1. Read the Full Analysis
Open `MODULE_OUTPUTS_AND_VISUALS_ANALYSIS.md` for:
- Detailed output schemas for each module
- Generic output examples (sample data)
- Complete database CREATE TABLE statements
- Specific tile suggestions with data source mappings

### 2. Build Data Access Layer
Create `gui/data_access/` module with helpers:
```python
# gui/data_access/state_queries.py
def get_recent_runs(limit=20):
    """Query runs table"""

def get_job_queue_stats():
    """Query job_queue table"""

def tail_log_file(path, lines=100):
    """Read last N lines from log"""
```

### 3. Implement Generic Output Tile
Build your universal adapter tile:
- Can display any log file
- Can display any JSON file
- Can display any DB table (via queries)
- Can auto-refresh

### 4. Build Phase 1 Tiles
Start with the 4 essential tiles:
- RunSelectorTile
- JobQueueTile
- JobHistoryTile
- GenericOutputTile

### 5. Wire Up Terminal Integration
Connect bottom terminal pane to show:
- Live tool execution (tailed from log files)
- Manual shell access
- System logs

---

## Example: Wiring Up a Tile

### JobQueueTile Example

**Data Sources:**
```python
# Query database
from engine.queue.job_queue import JobQueue
queue = JobQueue(db_path="pipeline.db")
stats = queue.get_stats()
# Returns: {'queued': 5, 'running': 3, 'completed': 47, ...}

# Get job list
conn = sqlite3.connect("pipeline.db")
cursor = conn.execute("""
    SELECT job_id, priority, status, queued_at
    FROM job_queue
    WHERE status IN ('queued', 'waiting', 'running')
    ORDER BY priority, queued_at
""")
jobs = cursor.fetchall()
```

**Visual Layout:**
```
+--------------------------------------------------+
| Job Queue                    [Refresh] [Filter]  |
+--------------------------------------------------+
| Status Summary:                                  |
| ⏳ Queued: 5  ⏸️ Waiting: 2  ▶️ Running: 3       |
+--------------------------------------------------+
| Job ID             | Priority | Status  | Queued |
|--------------------|----------|---------|--------|
| job-20251126-001   | 1 (High) | Running | 12:00  |
| job-20251126-002   | 2 (Med)  | Queued  | 12:05  |
| job-20251126-003   | 2 (Med)  | Waiting | 12:08  |
+--------------------------------------------------+
```

---

## File Locations

### Analysis Documents
- **This summary:** `GUI_MODULE_ANALYSIS_SUMMARY.md`
- **Full analysis:** `MODULE_OUTPUTS_AND_VISUALS_ANALYSIS.md`

### Key Source Files Referenced
- `engine/orchestrator/orchestrator.py` - Job orchestration
- `engine/queue/job_queue.py` - Queue implementation
- `engine/state_store/job_state_store.py` - State API
- `modules/core-state/m010003_db_sqlite.py` - DB schema
- `modules/error-engine/m010004_pipeline_engine.py` - Error pipeline

### Database Locations
- `pipeline.db` - Job queue
- `state/pipeline_state.db` - Legacy state
- `.worktrees/pipeline_state.db` - UET state
- `.state/orchestrator.db` - Orchestrator state

### Log Locations
- `job["paths"]["log_file"]` - Per-job logs (path in job JSON)
- `pipeline_errors.jsonl` - Aggregated error events
- Console stdout - Orchestrator/router logs

---

## Questions to Consider

As you build the GUI, consider:

1. **Database Choice:** Will GUI query SQLite directly, or go through Python API?
2. **Refresh Strategy:** Polling vs file watching vs pub-sub events?
3. **Multi-Run Support:** Can user view multiple runs simultaneously?
4. **Tile Swapping:** How easy is it to replace/rearrange tiles?
5. **State Sync:** How does GUI detect when terminal completes a job?

The full analysis document provides technical details to inform these decisions.

---

## Summary

✅ **9 major modules analyzed**
✅ **20+ tile suggestions documented**
✅ **4 database schemas mapped**
✅ **Generic output tile pattern defined**
✅ **Implementation roadmap provided**

**You now have a complete reference** for building your tile-based GUI on top of the existing engine infrastructure. Each module's outputs are documented with suggested visualizations, and you have a phased implementation plan to follow.

---

**See `MODULE_OUTPUTS_AND_VISUALS_ANALYSIS.md` for complete technical details.**
