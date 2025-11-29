# Multi-Agent Orchestration - Usage Guide

## Quick Start

### **Option 1: Run with 3 Agents (Recommended)**

```bash
# Install dependencies
pip install networkx

# Create logs directory
mkdir -p logs reports .state

# Run orchestration
python scripts/multi_agent_orchestrator.py
```

**Expected timeline**: 1-2 weeks for 39 workstreams

---

### **Option 2: Dry Run (Test First)**

```bash
# Test with mock execution (no actual AI agent calls)
python scripts/multi_agent_orchestrator.py --dry-run
```

---

### **Option 3: Single Agent Mode**

```bash
# Edit scripts/multi_agent_orchestrator.py
# Change agent_configs to:
agent_configs = [
    {"id": "agent-1", "type": "aider", "track": None}
]

# Run
python scripts/multi_agent_orchestrator.py
```

**Expected timeline**: 3-4 weeks sequential

---

## Configuration

### **Edit Agent Configuration**

In `scripts/multi_agent_orchestrator.py`, modify:

```python
agent_configs = [
    {"id": "agent-1", "type": "aider", "track": "pipeline_plus"},
    {"id": "agent-2", "type": "aider", "track": "core_refactor"},
    {"id": "agent-3", "type": "aider", "track": "error_engine"},
    # Add more agents as needed
]
```

### **Edit Track Assignments**

```python
track_assignments = {
    "pipeline_plus": [
        "ws-22", "ws-23", "ws-24", "ws-25", 
        "ws-26", "ws-27", "ws-28", "ws-29", "ws-30"
    ],
    "core_refactor": [
        "ws-03", "ws-04", "ws-05", "ws-06", 
        "ws-07", "ws-08", "ws-09"
    ],
    "error_engine": [
        "ws-12", "ws-13", "ws-14", "ws-15", 
        "ws-16", "ws-17"
    ],
    # Add custom tracks
}
```

---

## Monitoring

### **Check Status in Real-Time**

```bash
# Watch execution log
tail -f logs/orchestrator.log

# Check database status
watch -n 5 'sqlite3 .state/orchestration.db "SELECT workstream_id, status, agent_id FROM workstream_status ORDER BY started_at"'

# Count completed
sqlite3 .state/orchestration.db "SELECT COUNT(*) FROM workstream_status WHERE status='completed'"
```

### **Generate Status Report**

```bash
python scripts/check_orchestration_status.py
```

---

## How It Works

### **Dependency Resolution**

```
1. Orchestrator loads all workstreams from workstreams/*.json
2. Builds dependency graph using NetworkX
3. Identifies "ready" workstreams (all dependencies met)
4. Assigns ready workstreams to available agents
5. Executes in parallel
6. Repeats until all workstreams complete
```

### **Parallel Execution Example**

```
Iteration 1:
  Agent 1: ws-22 (Pipeline Plus Phase 0)
  Agent 2: ws-03 (Meta Refactor)
  Agent 3: ws-12 (Error Utils)

Iteration 2 (after Wave 1 completes):
  Agent 1: ws-23 (Pipeline Plus Phase 1a)
  Agent 2: ws-06 (AIM Refactor)
  Agent 3: ws-13 (Error Plugins)

... continues until all done
```

---

## Safety Features

### **1. Automatic State Tracking**

All execution state is stored in SQLite:
- Which workstreams are running/completed/failed
- Which agent executed each workstream
- Timestamps and error messages

### **2. Dependency Enforcement**

Orchestrator WILL NOT start a workstream until ALL dependencies are completed.

### **3. Conflict Avoidance**

Track assignments prevent multiple agents from editing same files simultaneously.

### **4. Graceful Failure Handling**

If a workstream fails:
- Agent is released
- Workstream marked as "failed"
- Other workstreams continue
- Failed workstreams can be retried manually

---

## Troubleshooting

### **"No agents available"**

**Problem**: All agents are busy  
**Solution**: Wait for current workstreams to complete, or add more agents

### **"Workstream failed"**

**Problem**: Workstream execution returned non-zero exit code  
**Solution**: 
1. Check logs: `cat logs/orchestrator.log | grep ws-XX`
2. Check database: `sqlite3 .state/orchestration.db "SELECT * FROM workstream_status WHERE workstream_id='ws-XX'"`
3. Manually fix and retry

### **"Waiting for dependencies"**

**Problem**: All ready workstreams have unmet dependencies  
**Solution**: This is normal - orchestrator waits for running workstreams to complete

---

## Advanced Usage

### **Custom Execution Logic**

Modify `AgentPool._build_aider_command()` to customize how agents execute workstreams:

```python
def _build_aider_command(self, ws_id: str, ws_data: Dict) -> str:
    # Use execution patterns instead of raw aider
    pattern_id = determine_pattern(ws_id)
    return f"execute-pattern {pattern_id} --workstream {ws_id}"
```

### **Add More Agent Types**

```python
class AgentType(Enum):
    AIDER = "aider"
    CODEX = "codex"
    CLAUDE_CODE = "claude_code"
    CURSOR = "cursor"  # Add new type
```

Then implement `_build_cursor_command()` in AgentPool.

---

## Integration with Existing Patterns

### **Use Module Refactor Patterns**

```python
def _build_aider_command(self, ws_id: str, ws_data: Dict) -> str:
    # For section refactors, use module refactor pattern
    if ws_id in ["ws-03", "ws-04", "ws-05", "ws-06", "ws-07", "ws-08"]:
        module_id = extract_module_id(ws_data)
        return f"execute-pattern PAT-MODULE-REFACTOR-MIGRATE-003 --module-id {module_id}"
    
    # For schema creation
    if ws_id == "ws-22":
        return f"execute-pattern PAT-ATOMIC-CREATE-001 --workstream {ws_id}"
    
    # Default: use aider
    return default_aider_command(ws_id, ws_data)
```

---

## Performance Metrics

### **Expected Results with 3 Agents**

| Metric | Value |
|--------|-------|
| Total workstreams | 39 |
| Independent workstreams | 11 |
| Longest dependency chain | 9 (Pipeline Plus) |
| **Sequential time (1 agent)** | **3-4 weeks** |
| **Parallel time (3 agents)** | **1-2 weeks** |
| **Speedup** | **2-3x** |

### **Resource Utilization**

```
Week 1:
  Agent 1: 85% utilized (Pipeline Plus critical path)
  Agent 2: 90% utilized (Core refactor track)
  Agent 3: 80% utilized (Error engine track)

Week 2:
  Agent 1: 70% utilized (remaining Pipeline Plus)
  Agent 2: 60% utilized (integration work)
  Agent 3: 50% utilized (cleanup)
```

---

## Example Execution Log

```
2025-11-28 10:00:00 [orchestrator] INFO: === Multi-Agent Orchestrator Initialized ===
2025-11-28 10:00:00 [orchestrator] INFO: Total workstreams: 39
2025-11-28 10:00:00 [orchestrator] INFO: Independent workstreams: 11
2025-11-28 10:00:00 [orchestrator] INFO: Agents: 3

2025-11-28 10:00:01 [orchestrator] INFO: === Iteration 1 ===
2025-11-28 10:00:01 [orchestrator] INFO: Completed: 0/39, Running: 0
2025-11-28 10:00:01 [orchestrator] INFO: Ready to execute: ['ws-01', 'ws-03', 'ws-04', 'ws-05', 'ws-12', 'ws-22', ...]
2025-11-28 10:00:01 [orchestrator] INFO: Assigned ws-22 to agent-1
2025-11-28 10:00:01 [orchestrator] INFO: Assigned ws-03 to agent-2
2025-11-28 10:00:01 [orchestrator] INFO: Assigned ws-12 to agent-3
2025-11-28 10:00:01 [orchestrator] INFO: Executing 3 workstreams in parallel
2025-11-28 10:00:01 [orchestrator] INFO: 🚀 Starting ws-22 on agent-1
2025-11-28 10:00:01 [orchestrator] INFO: 🚀 Starting ws-03 on agent-2
2025-11-28 10:00:01 [orchestrator] INFO: 🚀 Starting ws-12 on agent-3

... 1 hour later ...

2025-11-28 11:00:15 [orchestrator] INFO: ✅ ws-22 completed by agent-1
2025-11-28 11:15:22 [orchestrator] INFO: ✅ ws-12 completed by agent-3
2025-11-28 14:30:45 [orchestrator] INFO: ✅ ws-03 completed by agent-2

2025-11-28 14:30:46 [orchestrator] INFO: === Iteration 2 ===
2025-11-28 14:30:46 [orchestrator] INFO: Completed: 3/39, Running: 0
2025-11-28 14:30:46 [orchestrator] INFO: Ready to execute: ['ws-04', 'ws-05', 'ws-13', 'ws-23', ...]
...
```

---

## Database Schema

### **workstream_status Table**

```sql
workstream_id    TEXT PRIMARY KEY
status           TEXT (pending|running|completed|failed)
agent_id         TEXT
track            TEXT
started_at       TEXT (ISO 8601)
completed_at     TEXT (ISO 8601)
exit_code        INTEGER
attempt          INTEGER
error_message    TEXT
```

### **execution_log Table**

```sql
id               INTEGER PRIMARY KEY
timestamp        TEXT (ISO 8601)
workstream_id    TEXT
agent_id         TEXT
event_type       TEXT (started|completed|failed|retry)
message          TEXT
```

---

## Next Steps

1. ✅ **Test with dry run**: `python scripts/multi_agent_orchestrator.py --dry-run`
2. ✅ **Review configuration**: Edit agent_configs and track_assignments
3. ✅ **Run with 1 agent first**: Validate on small subset
4. ✅ **Scale to 3 agents**: Full parallel execution
5. ✅ **Monitor and optimize**: Watch logs, adjust as needed

---

## FAQ

**Q: Can I pause and resume?**  
A: Yes! State is persisted in SQLite. Just stop the script and restart it.

**Q: What if an agent crashes?**  
A: Orchestrator will mark workstream as failed. You can manually restart it or the entire orchestration.

**Q: Can I add agents mid-execution?**  
A: Not currently. Stop orchestrator, update config, restart.

**Q: How do I prioritize certain workstreams?**  
A: Assign them to dedicated agent tracks. Critical path (Pipeline Plus) gets agent-1.

**Q: Can I run more than 3 agents?**  
A: Yes! Just add more entries to agent_configs. Optimal is 3-6 agents for this workload.

---

**Created**: 2025-11-28  
**Status**: Ready for use  
**Estimated setup time**: 10 minutes  
**Estimated execution time**: 1-2 weeks with 3 agents
