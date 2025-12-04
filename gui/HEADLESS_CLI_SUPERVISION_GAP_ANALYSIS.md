# Headless CLI Supervision - Gap Analysis

**Date**: 2025-12-04
**Related Plan**: `HEADLESS_CLI_SUPERVISION_PLAN.json`
**Status**: Pre-Implementation Review

---

## Executive Summary

After thorough analysis of the codebase and the proposed plan, **7 critical gaps** have been identified that must be addressed for full functionality. The plan is comprehensive but missing key operational, architectural, and user interaction components.

---

## Critical Gaps

### 1. **User Approval Decision Mechanism (CRITICAL)**

**Status**: ❌ **COMPLETELY MISSING**

**Problem**:
- Plan creates `approvals` table and displays pending approvals in TUI
- **BUT**: No mechanism for user to actually approve/reject
- TUI is read-only for approvals
- No CLI command to approve/reject
- No API endpoint for external approval

**Impact**: Approvals will pile up forever with no way to resolve them

**Required Solutions**:

#### Option A: TUI Interactive Mode (Recommended)
```python
# Add to ToolHealthWidget or new ApprovalsPanel
class ApprovalsWidget:
    BINDINGS = [
        ("a", "approve_selected", "Approve"),
        ("r", "reject_selected", "Reject"),
        ("up", "cursor_up", "↑"),
        ("down", "cursor_down", "↓"),
    ]

    def action_approve_selected(self):
        approval = self.get_selected_approval()
        self.state_client.update_approval_status(
            approval.approval_id,
            "approved",
            approval.options[0]["value"],  # or user choice
            datetime.now()
        )
```

#### Option B: CLI Approval Command
```bash
# New command in core/ui_cli.py
python -m core.ui_cli approve AP-00123 --choice approve
python -m core.ui_cli approve AP-00123 --reject
python -m core.ui_cli approvals list  # Show pending
```

#### Option C: HTTP API (for web/external control)
```python
# New module: core/approval_api.py
@app.post("/approvals/{approval_id}/approve")
def approve(approval_id: str, choice: str):
    ...
```

**Missing from Plan**:
- Task for implementing approval decision UI/CLI
- Keybinding design for TUI
- API design if using HTTP approach
- Security/authorization for approvals

---

### 2. **Tool Resume/Retry After Approval (CRITICAL)**

**Status**: ❌ **NOT SPECIFIED**

**Problem**:
- Tool exits with code 90 when approval needed
- User approves in DB
- **BUT**: Nothing restarts the tool with the approval decision
- Plan mentions "polling pattern" vs "event-driven pattern" but doesn't mandate implementation

**Impact**: Approvals are recorded but tools never resume

**Required Implementation**:

```python
# In orchestrator or supervisor
def handle_waiting_approval_tools():
    """Background worker to resume approved tools"""
    while True:
        # Find tool_runs with status='waiting_approval'
        waiting = db.query(
            "SELECT * FROM tool_runs WHERE status='waiting_approval'"
        )

        for tool_run in waiting:
            # Check if approval is decided
            approval = db.query(
                "SELECT * FROM approvals WHERE tool_run_id=? AND status!='pending'",
                (tool_run.tool_run_id,)
            )

            if approval and approval.status == 'approved':
                # Re-run tool with approval context
                run_cli_tool(
                    tool_run.tool_name,
                    original_args + [f"--approval-id={approval.approval_id}"],
                    tool_run.execution_id,
                    env={"AUTO_APPROVE": approval.chosen_value}
                )
            elif approval and approval.status in ['rejected', 'expired']:
                # Mark tool as failed
                db.update_tool_run(tool_run.tool_run_id, status='failed')

        time.sleep(5)  # Poll interval
```

**Missing from Plan**:
- Task: Implement approval resume worker
- Task: Define tool contract for consuming approval decisions
- Task: Handle tool restart with approval context
- Configuration: Resume polling interval
- Error handling: What if tool fails on retry?

---

### 3. **Database Schema Migration Strategy (HIGH PRIORITY)**

**Status**: ⚠️ **PARTIALLY ADDRESSED**

**Problem**:
- Plan says "ALTER TABLE with defaults for backwards compatibility"
- SQLite doesn't support all ALTER TABLE operations reliably
- Existing data migration not specified
- No rollback strategy
- Multiple DBs in repo: `core/state/db.py`, `gui/src/tui_app/core/sqlite_state_backend.py`, `.worktrees/pipeline_state.db`

**Discovered Issues**:
1. **Two separate DB systems**:
   - `core/state/db.py` → `.ledger/framework.db` (has `runs`, `step_attempts`)
   - `gui/tui_app/core/sqlite_state_backend.py` → `.worktrees/pipeline_state.db` (has `uet_executions`, `patch_ledger`)

2. **Schema divergence**: Plan targets TUI DB but orchestrator uses different DB

**Required Clarification**:

```yaml
database_architecture_decision:
  options:
    1_unified_db:
      description: "Merge both DBs into single schema"
      pros: ["Single source of truth", "Atomic transactions"]
      cons: ["Large migration effort", "Breaking change"]

    2_dual_db_with_sync:
      description: "Keep separate but sync tool_runs to both"
      pros: ["Less disruptive", "Gradual migration"]
      cons: ["Consistency issues", "Duplicate data"]

    3_supervisor_writes_to_both:
      description: "cli_supervisor.py writes to both DBs"
      pros: ["Quick implementation", "Works with both systems"]
      cons: ["Technical debt", "Double writes"]
```

**Missing from Plan**:
- Decision: Which database to use?
- Task: Merge or sync strategy
- Task: Data migration script
- Task: Schema versioning
- Task: Rollback procedure
- Testing: Migration with existing data

---

### 4. **Heartbeat Implementation in Tools (HIGH PRIORITY)**

**Status**: ❌ **TOOL-SIDE NOT SPECIFIED**

**Problem**:
- Plan requires tools to emit `{"event": "heartbeat"}` events
- **BUT**: No specification for how tools do this
- No reference implementation
- No guidance for integrating with existing tools (aider, codex, etc.)

**Impact**: Stall detection won't work without tool cooperation

**Required Implementations**:

#### For Custom Tools (under our control)
```python
# lib/tool_heartbeat.py (new shared library)
import json
import sys
import time
import threading

class HeartbeatEmitter:
    """Emit heartbeat events for long-running tools"""

    def __init__(self, tool_name: str, execution_id: str, interval: int = 30):
        self.tool_name = tool_name
        self.execution_id = execution_id
        self.interval = interval
        self._stop = threading.Event()
        self._thread = None

    def start(self):
        self._thread = threading.Thread(target=self._emit_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    def _emit_loop(self):
        while not self._stop.is_set():
            event = {
                "event": "heartbeat",
                "tool": self.tool_name,
                "execution_id": self.execution_id,
                "timestamp": datetime.now(UTC).isoformat()
            }
            print(json.dumps(event), file=sys.stderr, flush=True)
            time.sleep(self.interval)

# Usage in tools:
# heartbeat = HeartbeatEmitter("aider", execution_id)
# heartbeat.start()
# ... do work ...
# heartbeat.stop()
```

#### For Third-Party Tools (aider, ruff, etc.)
```python
# Wrapper approach in cli_supervisor.py
def inject_heartbeat_wrapper(tool_name: str, args: list[str]) -> list[str]:
    """Wrap tool execution with heartbeat script"""
    if tool_name in ["aider", "codex"]:  # Tools that take long
        wrapper_script = create_heartbeat_wrapper_script(tool_name)
        return ["python", wrapper_script, "--", tool_name] + args
    return [tool_name] + args
```

**Missing from Plan**:
- Task: Create HeartbeatEmitter library
- Task: Integrate into custom tools
- Task: Wrapper for third-party tools
- Configuration: Heartbeat interval per tool
- Testing: Heartbeat emission and detection

---

### 5. **Approval Event Format Standardization (MEDIUM PRIORITY)**

**Status**: ⚠️ **INCOMPLETE SPECIFICATION**

**Problem**:
- Plan defines `approval_needed` event format
- **BUT**: Tools need to know:
  - How to construct approval_id (UUID? ULID? Coordinator assigns?)
  - Where to write event (stdout vs stderr vs both?)
  - How to handle multiple approvals in same run
  - What if tool crashes before DB write?

**Required Specification**:

```yaml
approval_protocol_specification:
  approval_id_generation:
    rule: "Tool MUST NOT generate approval_id"
    reason: "Supervisor generates to avoid collisions"
    implementation: |
      Tool emits event WITHOUT approval_id:
      {"event": "approval_needed", "question": "...", "options": [...]}

      Supervisor parses, generates ID, inserts to DB, responds:
      {"event": "approval_registered", "approval_id": "AP-00123"}

  output_stream:
    rule: "MUST write to stderr (not stdout)"
    reason: "stdout may be parsed as tool output; stderr for control messages"
    exception: "Unless tool output is already JSON stream"

  atomicity:
    rule: "Supervisor MUST write to DB before tool exits"
    implementation: "Supervisor blocks on DB insert, then sends SIGTERM to tool"

  multiple_approvals:
    rule: "One approval per tool run"
    reason: "Simplifies state machine"
    workaround: "If multiple decisions needed, create multiple tool runs"
```

**Missing from Plan**:
- Task: Document approval protocol contract
- Task: Create reference implementation for tools
- Task: Validation in supervisor for malformed events

---

### 6. **Error Handling and Edge Cases (MEDIUM PRIORITY)**

**Status**: ⚠️ **MINIMAL COVERAGE**

**Problems Not Addressed**:

#### A. Timeout During Approval Wait
```python
# What if user never approves?
# Plan mentions "approval expiry" but doesn't specify:

EDGE_CASE_1_timeout_during_approval:
  scenario: "Tool exits with code 90, user never approves"
  current_plan: "Mark as expired after N hours"
  missing:
    - "Who marks it expired? Background job?"
    - "What triggers the background job?"
    - "What happens to tool_run status?"
    - "Does tool get retried or marked failed?"
```

#### B. Supervisor Crash During Tool Execution
```python
EDGE_CASE_2_supervisor_crash:
  scenario: "Supervisor dies, tool keeps running"
  problem: "Orphan processes, DB not updated"
  required_solution:
    - "PID tracking in tool_runs table"
    - "Startup reconciliation: find orphan processes"
    - "Kill or adopt orphan processes"
    - "Mark stale running rows as 'stalled'"
```

#### C. Database Lock Contention
```python
EDGE_CASE_3_db_locks:
  scenario: "Multiple supervisors writing, TUI reading simultaneously"
  problem: "SQLite LOCKED errors"
  required_solution:
    - "WAL mode: conn.execute('PRAGMA journal_mode=WAL')"
    - "Retry logic with exponential backoff"
    - "Read-only connections for TUI"
```

#### D. Tool Emits Invalid JSON
```python
EDGE_CASE_4_malformed_events:
  scenario: "Tool outputs broken JSON or wrong schema"
  problem: "Supervisor crashes or misinterprets"
  required_solution:
    - "Schema validation (jsonschema library)"
    - "Log malformed events, continue processing"
    - "Don't crash supervisor on parse errors"
```

**Missing from Plan**:
- Task: Implement approval expiry background job
- Task: Startup reconciliation for zombie processes
- Task: Enable SQLite WAL mode
- Task: JSON event schema validation
- Task: Error recovery stress testing

---

### 7. **Configuration and Deployment (LOW-MEDIUM PRIORITY)**

**Status**: ⚠️ **UNDER-SPECIFIED**

**Missing Operational Details**:

#### A. Configuration Files
```yaml
# Required: config/supervision.yaml (NEW FILE)
supervision:
  timeouts:
    hard_timeout_seconds: 1800
    no_output_timeout_seconds: 300
    heartbeat_interval_seconds: 30
    heartbeat_grace_period_seconds: 90  # 3x interval

  approvals:
    auto_expire_hours: 24
    check_interval_seconds: 60

  database:
    path: ".worktrees/pipeline_state.db"
    wal_mode: true
    busy_timeout_ms: 5000

  logging:
    combined_log_path: "logs/combined.log"
    supervisor_log_path: "logs/supervisor.log"
    max_log_size_mb: 100
    rotate_count: 5
```

#### B. Deployment/Startup
```bash
# Missing: How does supervisor start?
# Option 1: Part of orchestrator
python -m core.engine.orchestrator --enable-supervision

# Option 2: Separate daemon
python -m core.cli_supervisor daemon --config config/supervision.yaml

# Option 3: Systemd service (Linux)
[Unit]
Description=AI Pipeline CLI Supervisor
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python -m core.cli_supervisor daemon
Restart=always

[Install]
WantedBy=multi-user.target
```

#### C. Monitoring and Observability
```python
# Missing: Supervisor health metrics
# Required: Prometheus/OpenTelemetry instrumentation

from prometheus_client import Counter, Histogram, Gauge

supervisor_tools_started = Counter('supervisor_tools_started_total', 'Tools started', ['tool_name'])
supervisor_tools_completed = Counter('supervisor_tools_completed_total', 'Tools completed', ['tool_name', 'status'])
supervisor_tool_duration = Histogram('supervisor_tool_duration_seconds', 'Tool execution time', ['tool_name'])
supervisor_active_tools = Gauge('supervisor_active_tools', 'Currently running tools')
supervisor_pending_approvals = Gauge('supervisor_pending_approvals', 'Pending approvals')
```

**Missing from Plan**:
- Task: Create supervision config schema
- Task: Document deployment modes (embedded vs daemon)
- Task: Add health check endpoint
- Task: Implement metrics instrumentation
- Task: Create deployment guide (dev/prod)

---

## Architecture Gaps

### 8. **State Synchronization Between Systems**

**Issue**: Codebase has TWO separate state systems:
1. `core/state/db.py` → Used by orchestrator (`runs`, `step_attempts`)
2. `gui/tui_app/core/sqlite_state_backend.py` → Used by TUI (`uet_executions`, `patch_ledger`)

**Plan Assumption**: Adds tables to TUI DB only

**Problem**: Orchestrator won't see new `tool_runs`/`approvals` tables

**Required Decision**:
- Unify schemas, OR
- Make cli_supervisor write to both, OR
- Create sync daemon

---

### 9. **Tool Adapter Integration**

**Current Architecture**:
```
Orchestrator → Executor → Router → ToolConfig → SubprocessAdapter
```

**Plan's Architecture**:
```
Orchestrator → run_cli_tool() [supervisor] → subprocess
```

**Conflict**: Bypasses existing adapter system

**Required Reconciliation**:
```python
# Integrate supervisor INTO adapter system

class SupervisedSubprocessAdapter(SubprocessAdapter):
    def execute(self, task: Task, tool_config: ToolConfig) -> AdapterResult:
        from core.cli_supervisor import run_cli_tool

        exit_code = run_cli_tool(
            tool_name=tool_config.name,
            args=self._build_args(task, tool_config),
            execution_id=task.execution_id,
            ...
        )

        return AdapterResult(exit_code=exit_code, ...)
```

**Missing from Plan**:
- Task: Integrate supervisor with existing adapter architecture
- Decision: Refactor or wrap SubprocessAdapter?

---

## Testing Gaps

### 10. **Integration Test Scenarios**

Plan lists test cases but missing **specific scenarios**:

```python
# MISSING SCENARIOS:

test_approval_timeout_expires:
    """Approval not decided within expiry window"""
    1. Tool requests approval
    2. Wait past expiry threshold
    3. Verify approval marked 'expired'
    4. Verify tool_run marked 'failed'

test_supervisor_restart_recovery:
    """Supervisor restarts with tools running"""
    1. Start 3 tools
    2. Kill supervisor (not tools)
    3. Restart supervisor
    4. Verify supervisor reconciles state
    5. Verify orphan tools handled

test_concurrent_approval_decisions:
    """Two users try to approve same request"""
    1. Create approval
    2. User A approves via TUI
    3. User B approves via CLI (race condition)
    4. Verify only one approval processed
    5. Verify second attempt fails gracefully

test_db_corruption_recovery:
    """Database becomes corrupted during write"""
    1. Simulate DB lock/corruption
    2. Verify supervisor doesn't crash
    3. Verify error logged
    4. Verify fallback behavior

test_log_rotation_during_execution:
    """Log file rotates while tool running"""
    1. Start long-running tool
    2. Trigger log rotation
    3. Verify events still captured
    4. Verify no data loss
```

**Missing from Plan**:
- Detailed integration test scenarios
- Chaos engineering tests (kill processes, corrupt DB, fill disk)
- Load testing (100+ concurrent tools)
- TUI interaction tests (Textual supports this)

---

## Documentation Gaps

### 11. **User-Facing Documentation**

**Missing Documents**:

1. **HEADLESS_MODE_QUICKSTART.md**
   - How to run tools in headless mode
   - How to check for stuck tools
   - How to approve pending requests
   - Troubleshooting guide

2. **TOOL_DEVELOPER_GUIDE.md**
   - How to make your tool headless-compatible
   - Heartbeat emission best practices
   - Approval request API
   - Testing your tool with supervisor

3. **OPERATOR_RUNBOOK.md**
   - How to deploy supervisor
   - Monitoring dashboards
   - Alert thresholds
   - Recovery procedures
   - Log analysis

4. **API_REFERENCE.md**
   - StateClient new methods
   - ApprovalInfo schema
   - ToolRunInfo schema
   - Event formats (complete spec)

**Missing from Plan**:
- Tasks for creating user documentation
- Tasks for creating developer documentation
- Tasks for creating operator documentation

---

## Prioritized Implementation Order

### Phase 0: Architecture Decisions (MUST DO FIRST)
1. ✅ **Decide**: Single DB vs Dual DB strategy
2. ✅ **Decide**: Embedded supervisor vs Daemon
3. ✅ **Decide**: TUI interactive approvals vs CLI vs API
4. ✅ **Decide**: Tool resume strategy (polling vs event-driven)

### Phase 1-3: Core Implementation (As Planned)
- Database schema
- StateClient extensions
- CLI Supervisor base

### Phase 3.5: **CRITICAL ADDITIONS**
1. ✅ **Implement approval decision mechanism** (TUI keybindings OR CLI command)
2. ✅ **Implement tool resume worker** (handle approved tools)
3. ✅ **Implement approval expiry background job**
4. ✅ **Add HeartbeatEmitter library** for tools

### Phase 4-5: TUI and Orchestrator (As Planned + Fixes)
- TUI panels (add interactive approval widget)
- Orchestrator integration (integrate with adapters)

### Phase 6: Extended Testing
- Integration scenarios (not just unit tests)
- Chaos tests
- Load tests
- Migration tests with real data

### Phase 7: Documentation + Phase 8: Operations
- User guides
- Developer guides
- Deployment automation
- Monitoring setup

---

## Summary: What's Missing

| Category | Missing Items | Priority | Impact |
|----------|---------------|----------|--------|
| **User Interaction** | Approval decision UI/CLI | CRITICAL | Feature unusable |
| **Tool Resume** | Resume after approval logic | CRITICAL | Approvals don't work |
| **Database** | Unified schema or sync strategy | HIGH | Data inconsistency |
| **Tool Integration** | Heartbeat library & integration | HIGH | Stall detection fails |
| **Error Handling** | Edge case handling (10+ scenarios) | MEDIUM | Production instability |
| **Configuration** | Config files, deployment docs | MEDIUM | Hard to deploy |
| **Testing** | Integration scenarios, chaos tests | MEDIUM | Unknown bugs |
| **Documentation** | User/dev/ops guides (4+ docs) | LOW | Adoption issues |

---

## Recommendations

### Immediate Actions (Before Implementation)

1. **Create Phase 0 decision document** addressing 4 architecture decisions
2. **Add Phase 3.5** to plan with critical missing tasks
3. **Expand test plan** with specific integration scenarios
4. **Add documentation phase** (Phase 8)

### Plan Modifications Required

```json
{
  "phase": 0,
  "name": "Architecture Decisions",
  "tasks": [
    "ARCH-001: Decide single vs dual DB strategy",
    "ARCH-002: Decide supervisor deployment mode",
    "ARCH-003: Design approval decision mechanism",
    "ARCH-004: Design tool resume strategy"
  ]
},
{
  "phase": 3.5,
  "name": "Critical Missing Features",
  "tasks": [
    "CRIT-001: Implement approval decision UI/CLI",
    "CRIT-002: Implement tool resume worker",
    "CRIT-003: Implement approval expiry daemon",
    "CRIT-004: Create HeartbeatEmitter library",
    "CRIT-005: Edge case error handlers"
  ]
},
{
  "phase": 8,
  "name": "Operations & Documentation",
  "tasks": [
    "OPS-001: Create supervision config schema",
    "OPS-002: Deployment guides (dev/prod)",
    "OPS-003: Monitoring instrumentation",
    "OPS-004: User documentation suite",
    "OPS-005: Developer documentation suite",
    "OPS-006: Operator runbook"
  ]
}
```

### Risk Assessment

**Without addressing gaps**:
- 🔴 **HIGH RISK**: Feature will appear complete but be non-functional
- 🔴 **HIGH RISK**: Approvals pile up with no resolution path
- 🟡 **MEDIUM RISK**: Data corruption from DB schema issues
- 🟡 **MEDIUM RISK**: Production failures from edge cases

**With gap mitigation**:
- 🟢 **LOW RISK**: Full end-to-end functionality
- 🟢 **LOW RISK**: Production-ready with monitoring
- 🟢 **LOW RISK**: Well-documented and testable

---

## Next Steps

1. Review this gap analysis
2. Make Phase 0 architecture decisions
3. Update `HEADLESS_CLI_SUPERVISION_PLAN.json` with:
   - Phase 0 tasks
   - Phase 3.5 tasks
   - Phase 8 tasks
   - Extended test scenarios
4. Create decision log document
5. Begin implementation with Phase 0

---

**Estimated Additional Effort**: +40-60% over original plan
**Original Plan**: ~40 tasks, 7 phases
**With Gaps Fixed**: ~65 tasks, 9 phases

**ROI**: Essential for production readiness. Without these additions, feature is ~60% complete but appears 100% done.
