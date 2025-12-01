---
doc_id: DOC-GUIDE-HYBRID-GUI-PLAN-158
---


### 3.1 Module: engine/orchestrator

**Role:** CLI/entrypoint that loads a job JSON, routes to the right adapter, and writes state updates via JobStateStore.

**Outputs:**

| Output ID | Type | Source (file/DB/API) | Key Fields / Schema (approx) |
|-----------|------|----------------------|------------------------------|
| ORC-1 | log_text | stdout/stderr from `python -m engine.orchestrator run-job ...` | `[Orchestrator]` lines: job_id, tool, workstream_id, status transitions, exit_code, duration |
| ORC-2 | job_result | return value `JobResult` | exit_code, duration_s, success, stdout (truncated), stderr (truncated), error_report_path |
| ORC-3 | state_update | `JobStateStore.update_job_result` → SQLite `.worktrees/pipeline_state.db` | `step_attempts`: job_id (in result_json), status, exit_code, duration_s; `events`: `job.completed` payload |

**Suggested Visuals (Tiles):**

| Tile Name | Uses Output IDs | Visual Type | Description |
|-----------|-----------------|-------------|-------------|
| JobRunConsoleTile | ORC-1 | Live log viewer | Stream orchestrator prints + adapter tail for bottom terminal pane |
| JobResultSummaryTile | ORC-2, ORC-3 | Status chips + key metrics | Show exit_code, duration, success flag, error_report link |

**Generic Output Example:**
```
[Orchestrator] Starting job: job-2025-11-20-001
[Orchestrator] Tool: aider
[Orchestrator] Workstream: ws-PH07-refactor-path-resolver
[Orchestrator] Exit code: 0
[Orchestrator] Duration: 12.34s
```

### 3.2 Module: engine/queue

**Role:** Priority-based job queue with dependency resolution, retry logic, worker pool management.

**Outputs:**

| Output ID | Type | Source | Key Fields |
|-----------|------|--------|------------|
| Q-1 | db_table | SQLite `pipeline.db` → `job_queue` | job_id, priority, status (queued/waiting/running/completed/failed), depends_on[], retry_count, timestamps |
| Q-2 | metrics | `JobQueue.get_stats()` API | queued, waiting, running, completed, failed, total |

**Suggested Visuals (Tiles):**

| Tile Name | Uses Output IDs | Visual Type | Description |
|-----------|-----------------|-------------|-------------|
| JobQueueTile | Q-1, Q-2 | Table + counters | Priority/status grid with counts |
| WorkerPoolTile | Q-2 | Mini dashboard | Active workers, running count |


### 3.3 Module: engine/state_store

**Role:** Job-centric state persistence layer using SQLite.

**Key Tables:**
- `runs` - run_id, status, timestamps
- `workstreams` - ws_id, run_id, status, depends_on
- `step_attempts` - job execution records with result_json
- `events` - event log with job.completed, step_complete, etc.
- `errors` - deduped error records
- `patches` - patch files with validation flags

**Suggested Tiles:** RunTimelineTile, WorkstreamBoardTile, EventStreamTile

### 3.4 Module: error/engine

**Role:** Plugin-based error detection pipeline with quarantine management.

**Key Outputs:**
- ERR-1: JSON error reports with normalized issues
- ERR-2: Validation cache (`.state/validation_cache.json`)
- ERR-3: Error state machine context
- ERR-5: `error_records` table with quarantine metadata

**Suggested Tiles:** ErrorQuarantineTile, ErrorScanSummaryTile, ValidationCacheTile

---

## 4. Tile Catalog & UX Layout

### 4.1 Tile Manifest Format

Every tile has a `.panel.json` manifest defining its data sources and behavior:

```json
{
  "panel_id": "job_queue_tile",
  "display_name": "Job Queue",
  "data_sources": [
    {
      "source_type": "db_table",
      "source_path": "pipeline.db:job_queue",
      "refresh_interval": 5000
    },
    {
      "source_type": "api_call",
      "source_path": "JobQueue.get_stats()",
      "refresh_interval": 5000
    }
  ],
  "visual_type": "table_with_summary_bar",
  "supports_filtering": true,
  "supports_drill_down": false
}
```

### 4.2 Visual Types Taxonomy

| Visual Type | Use Cases | Examples |
|-------------|-----------|----------|
| **Table** | Structured records | Jobs, errors, runs, queue items |
| **Timeline** | Events over time | Job starts/completions, error spikes |
| **Kanban Board** | Workflow stages | Workstreams (pending → running → done) |
| **Status Chips** | State indicators | Job status, tool health, quarantine flag |
| **Log Feed** | Live logs | Console output, tool execution logs |
| **Gauge/Sparkline** | Quick metrics | Queue depth, success rate, durations |
| **JSON Viewer** | Raw data | Job metadata, config files |
| **Health Dashboard** | System status | Tool availability, worker status |

### 4.3 Top 10 Priority Tiles

**Phase 1: Essential (Build First)**
1. **RunSelectorTile** - Choose which run to view
2. **JobQueueTile** - Show queued/running jobs
3. **JobHistoryTile** - List recent jobs with status
4. **GenericOutputTile** - Universal viewer for logs/JSON/tables

**Phase 2: Core Operations**
5. **OrchestratorStatusTile** - Live orchestrator activity
6. **ErrorQuarantineTile** - Manage quarantined items
7. **WorkstreamKanbanTile** - Workflow visualization

**Phase 3: Metrics & Insights**
8. **GlobalDashboardTile** - System health overview
9. **PatternMetricsTile** - Pattern usage analytics
10. **ToolHealthTile** - AIM registry status

---

## 5. Data Access Layer & Tile Manifests

### 5.1 Database Query Patterns

**Direct SQLite queries:**
```python
import sqlite3

conn = sqlite3.connect('.worktrees/pipeline_state.db')
cursor = conn.execute('''
    SELECT job_id, status, started_at, completed_at
    FROM step_attempts
    WHERE run_id = ? AND status = 'running'
    ORDER BY started_at DESC
''', (run_id,))
jobs = cursor.fetchall()
```

**Python API wrappers:**
```python
from modules.core_state import m010003_crud as crud
runs = crud.list_runs(limit=20, status="running")

from engine.queue.job_queue import JobQueue
queue = JobQueue()
stats = queue.get_stats()
```

### 5.2 Refresh Strategies

| Data Type | Refresh Rate | Method |
|-----------|--------------|--------|
| Live log viewers | 500ms - 1s | Tail file, watch file mtime |
| Job queue status | 2-5s | Poll DB table |
| Metrics/charts | 10-30s | API call or DB query |
| Historical data | On-demand | User-triggered refresh |

### 5.3 Example: Wiring Up JobQueueTile

**Data Sources:**
```python
# Query database
conn = sqlite3.connect("pipeline.db")
cursor = conn.execute('''
    SELECT job_id, priority, status, queued_at
    FROM job_queue
    WHERE status IN ('queued', 'waiting', 'running')
    ORDER BY priority, queued_at
''')
jobs = cursor.fetchall()

# Get stats
from engine.queue.job_queue import JobQueue
queue = JobQueue(db_path="pipeline.db")
stats = queue.get_stats()
# Returns: {'queued': 5, 'running': 3, 'completed': 47, ...}
```

---

## 6. Implementation Phasing & Roadmap

### 6.1 Phase 1: MVP / Generic Output Tile (Weeks 1-2)

**Goals:**
- Build universal adapter tile that can display any output
- Wire up basic terminal integration
- Prove data access patterns work

**Deliverables:**
- GenericOutputTile with tabs: Log, JSON, Table, Raw
- RunSelectorTile (dropdown of recent runs)
- Basic terminal pane embedding
- Data access layer skeleton

**Estimated Time:** 2 weeks

### 6.2 Phase 2: Core Operational Tiles (Weeks 3-5)

**Goals:**
- Essential tiles for daily pipeline monitoring
- Replace generic viewers with specialized visuals

**Deliverables:**
- JobQueueTile
- JobHistoryTile  
- ErrorQuarantineTile
- OrchestratorStatusTile
- WorkstreamKanbanTile

**Estimated Time:** 3 weeks

### 6.3 Phase 3: Metrics & Insights Tiles (Weeks 6-8)

**Goals:**
- Analytics and telemetry visualization
- Cross-module aggregation

**Deliverables:**
- GlobalDashboardTile (Pipeline Radar)
- PatternMetricsTile
- ToolHealthTile
- CostDashboardTile

**Estimated Time:** 3 weeks

### 6.4 Phase 4: Advanced Interactivity (Weeks 9-12)

**Goals:**
- Drill-down navigation
- Actions (retry, release from quarantine)
- Live updates via WebSockets

**Deliverables:**
- Drill-down: click workstream → detail tile
- Actions: retry button, release quarantine
- WebSocket refresh for live tiles
- Dependency graph visualization

**Estimated Time:** 4 weeks

---

## 7. Open Questions, Risks & Design Decisions

### 7.1 Database Choice

**Question:** Direct SQLite queries vs Python API wrappers?

**Context:** Tiles need to read from 3 separate SQLite databases.

**Options:**
1. **Direct SQL:** Faster, simpler, but couples GUI to schema
2. **API wrappers:** More abstraction, but adds dependency layer
3. **Hybrid:** Direct SQL for simple queries, API for complex aggregations

**Recommendation:** Start with **hybrid approach**. Use direct SQL for table reads, API for stats/metrics.

### 7.2 Refresh Strategy

**Question:** Polling vs file watching vs pub-sub events vs WebSockets?

**Context:** Tiles need real-time updates without hammering DB.

**Options:**
1. **Polling:** Simple but inefficient
2. **File watching:** Works for logs, not for DB changes
3. **Pub-sub:** Requires event bus infrastructure
4. **WebSockets:** Best UX but complex

**Recommendation:** Start with **polling (Phase 1-2)**, add **WebSockets in Phase 4** for live tiles.

### 7.3 Multi-Run Support

**Question:** Can user view multiple runs simultaneously?

**Context:** Useful for comparing runs or monitoring parallel pipelines.

**Options:**
1. **Single run mode:** Simpler, one run selector
2. **Multi-run tabs:** Separate tile grids per run
3. **Multi-run overlay:** Single grid, data from multiple runs

**Recommendation:** Start with **single run mode**, add **multi-run tabs in Phase 4**.

### 7.4 State Sync

**Question:** How does GUI detect when terminal completes a job?

**Context:** Terminal and tile grid need to stay in sync.

**Options:**
1. **Poll events table:** Check for new `job.completed` events
2. **Watch log file:** Detect when log file stops growing
3. **Terminal hooks:** Inject callbacks into orchestrator

**Recommendation:** **Poll events table** (2-5s interval). Clean, no engine changes needed.

### 7.5 Performance & Scalability

**Question:** Can GUI handle large queues (1000+ jobs) and long logs (100+ MB)?

**Context:** Production pipelines may have high throughput.

**Risks:**
- Large table queries slow down UI
- Log file tailing consumes memory
- Too many tiles polling simultaneously

**Mitigations:**
- Pagination for large tables (LIMIT 50, offset controls)
- Virtual scrolling for log viewers
- Debounce/throttle tile refresh calls
- Lazy load tiles (only active tiles poll)

---

## Appendices

### A. File Locations Quick Reference

**Analysis Documents:**
- This plan: `HYBRID_GUI_PLAN.md`
- Execution patterns: `GUI_PLAN_EXECUTION_PATTERNS.md`
- Module analysis: `GUI_MODULE_ANALYSIS_SUMMARY.md`
- Detailed analysis: `module_outputs_and_visuals.md`

**Database Locations:**
- `pipeline.db` - Job queue
- `.worktrees/pipeline_state.db` - Runs/workstreams/steps
- `.state/orchestrator.db` - Observability tables

**Log Locations:**
- `job["paths"]["log_file"]` - Per-job logs
- `pipeline_errors.jsonl` - Aggregated errors
- Console stdout - Orchestrator logs

### B. Success Metrics

**Phase 1 Success:**
- [ ] GenericOutputTile displays logs, JSON, tables
- [ ] Can select a run and view its jobs
- [ ] Terminal pane runs tools natively

**Phase 2 Success:**
- [ ] All 5 core tiles implemented
- [ ] Can monitor active pipeline from tiles
- [ ] Error quarantine workflow functional

**Phase 3 Success:**
- [ ] Dashboard shows global system health
- [ ] Pattern and tool metrics visible
- [ ] Cost tracking integrated

**Phase 4 Success:**
- [ ] Drill-down navigation works
- [ ] Can retry jobs from GUI
- [ ] Live updates via WebSockets

---

## Conclusion

This plan provides a **complete, actionable roadmap** for building the Hybrid GUI Shell. By following the **pattern-based approach** (pre-made decisions, generic-first, phased delivery), development time is reduced from **8-10 months** to **8-12 weeks**.

**Next Steps:**
1. Review and approve this plan
2. Set up development environment
3. Build Phase 1 MVP (GenericOutputTile + data access layer)
4. Iterate through Phases 2-4 based on user feedback

**Key Success Factors:**
- Stick to read-only observability (no tool execution in GUI)
- Build generic output tile first (immediate value)
- Use execution patterns (avoid decision paralysis)
- Deliver incrementally (Phase 1 in 2 weeks, not 12)

---

**END OF HYBRID GUI PLAN DOCUMENT**

