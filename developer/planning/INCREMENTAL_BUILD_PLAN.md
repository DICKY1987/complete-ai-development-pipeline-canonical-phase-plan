---
doc_id: DOC-GUIDE-INCREMENTAL-BUILD-PLAN-1245
---

# Incremental Build Plan - AI Orchestration System
## Each Part Immediately Useful for the Next

**Date**: 2025-11-23  
**Strategy**: Build foundation → Use it to build next layer → Repeat  
**Philosophy**: Every step produces working tools that accelerate subsequent steps

---

## Layer 0: Immediate Foundation (30 minutes)

### Goal
Create the minimal infrastructure to observe and validate everything that follows.

### What We Build

#### File 1: `.state/` Directory Structure
```powershell
# Create observability infrastructure
New-Item -ItemType Directory -Force -Path .state\snapshots
New-Item -ItemType Directory -Force -Path .state\indices
New-Item -ItemType Directory -Force -Path .state\workers

# Create empty files
@{schema_version="StateV1"; timestamp=(Get-Date -Format "o")} | 
    ConvertTo-Json | Out-File .state\current.json

"" | Out-File .state\transitions.jsonl
```

#### File 2: `scripts\validate\validate_state.ps1` (Validation Tool)
```powershell
<#
.SYNOPSIS
    Validate .state/ directory structure
.DESCRIPTION
    Quick check that state infrastructure exists and is valid
#>

$errors = @()

# Check directories
$requiredDirs = '.state', '.state\snapshots', '.state\indices', '.state\workers'
foreach ($dir in $requiredDirs) {
    if (-not (Test-Path $dir)) {
        $errors += "Missing directory: $dir"
    }
}

# Check files
$requiredFiles = '.state\current.json', '.state\transitions.jsonl'
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        $errors += "Missing file: $file"
    }
}

# Validate current.json is valid JSON
if (Test-Path .state\current.json) {
    try {
        Get-Content .state\current.json -Raw | ConvertFrom-Json | Out-Null
    } catch {
        $errors += "Invalid JSON in current.json: $_"
    }
}

# Report
if ($errors.Count -eq 0) {
    Write-Host "✅ State infrastructure valid" -ForegroundColor Green
    exit 0
} else {
    Write-Host "❌ Validation failed:" -ForegroundColor Red
    $errors | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    exit 1
}
```

### How We Use It Immediately
```powershell
# Validate after creation
pwsh scripts\validate\validate_state.ps1
```

**Output**: ✅ State infrastructure valid

### Why This Matters
- Every subsequent step can **validate itself** using this script
- We have a **working checkpoint system** from minute 1
- **AI agents can query** `.state/current.json` immediately

---

## Layer 1: Event Logging (45 minutes)

### Goal
Create event logging so every action is observable.

### What We Build

#### File 1: `core\engine\event_logger.py`
```python
"""Simple event logger - writes to .state/transitions.jsonl"""

import json
from datetime import datetime, timezone
from pathlib import Path

class EventLogger:
    def __init__(self, log_path: str = ".state/transitions.jsonl"):
        self.log_path = Path(log_path)
    
    def log(self, event_type: str, actor: str, context: dict, 
            severity: str = "info", caused_by: str = None):
        """Log an event to JSONL."""
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "actor": actor,
            "context": context,
            "severity": severity,
            "caused_by": caused_by
        }
        
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(event) + "\n")
        
        return event

# Global logger instance
logger = EventLogger()

def log_event(event_type: str, actor: str, context: dict, **kwargs):
    """Convenience function for logging."""
    return logger.log(event_type, actor, context, **kwargs)
```

#### File 2: `scripts\query_events.ps1` (Event Query Tool)
```powershell
<#
.SYNOPSIS
    Query events from transitions.jsonl
.EXAMPLE
    .\scripts\query_events.ps1 -EventType "state_snapshot_created"
    .\scripts\query_events.ps1 -Last 10
#>

param(
    [string]$EventType,
    [string]$Actor,
    [string]$Severity,
    [int]$Last = 0
)

$events = Get-Content .state\transitions.jsonl | 
    ForEach-Object { $_ | ConvertFrom-Json }

# Filter
if ($EventType) {
    $events = $events | Where-Object { $_.event_type -eq $EventType }
}
if ($Actor) {
    $events = $events | Where-Object { $_.actor -eq $Actor }
}
if ($Severity) {
    $events = $events | Where-Object { $_.severity -eq $Severity }
}

# Limit
if ($Last -gt 0) {
    $events = $events | Select-Object -Last $Last
}

# Display
$events | Format-Table timestamp, event_type, actor, severity -AutoSize
```

### How We Use It Immediately

#### Test Event Logging
```python
# Test the logger
from core.engine.event_logger import log_event

log_event(
    event_type="layer_1_built",
    actor="builder",
    context={"layer": 1, "component": "event_logger"}
)
```

#### Query Events
```powershell
# See our test event
pwsh scripts\query_events.ps1 -Last 5
```

### Why This Matters
- **Every action from now on gets logged**
- We can **debug by reading events**, not guessing
- **AI agents can read the event stream** to understand what happened
- We now have **two working tools**: validator + event query

---

## Layer 2: State Snapshots (60 minutes)

### Goal
Create snapshots of system state so we can always see "what's running now"

### What We Build

#### File 1: `core\state\snapshot.py`
```python
"""State snapshot creator - uses event logger from Layer 1"""

import json
from datetime import datetime, timezone
from pathlib import Path
from core.engine.event_logger import log_event

def create_snapshot(description: str = "manual snapshot"):
    """Create a complete state snapshot."""
    
    timestamp = datetime.now(timezone.utc).isoformat()
    
    # Build snapshot
    snapshot = {
        "schema_version": "StateV1",
        "timestamp": timestamp,
        "description": description,
        "active_workstreams": [],  # Will populate later
        "worker_status": {},        # Will populate later
        "system_health": {
            "status": "ok",
            "checks": []
        }
    }
    
    # Write timestamped snapshot
    ts_safe = timestamp.replace(':', '-').replace('.', '-')
    snapshot_file = Path(f".state/snapshots/{ts_safe}.json")
    snapshot_file.write_text(json.dumps(snapshot, indent=2))
    
    # Update current.json atomically
    tmp_file = Path(".state/current.json.tmp")
    tmp_file.write_text(json.dumps(snapshot, indent=2))
    tmp_file.replace(".state/current.json")
    
    # Log the event (using Layer 1!)
    log_event(
        event_type="state_snapshot_created",
        actor="snapshot_creator",
        context={
            "snapshot_file": str(snapshot_file),
            "description": description
        }
    )
    
    return snapshot

if __name__ == "__main__":
    snapshot = create_snapshot("Layer 2 test snapshot")
    print(f"✅ Created snapshot at {snapshot['timestamp']}")
```

#### File 2: `scripts\snapshot.ps1` (Convenience Wrapper)
```powershell
<#
.SYNOPSIS
    Create state snapshot
.EXAMPLE
    .\scripts\snapshot.ps1 -Description "Before major change"
#>

param(
    [string]$Description = "manual snapshot"
)

python -c "from core.state.snapshot import create_snapshot; create_snapshot('$Description')"

# Validate it worked
pwsh scripts\validate\validate_state.ps1

# Show recent snapshots
Write-Host "`nRecent snapshots:" -ForegroundColor Cyan
Get-ChildItem .state\snapshots\*.json | 
    Sort-Object LastWriteTime -Descending | 
    Select-Object -First 5 | 
    Format-Table Name, LastWriteTime -AutoSize
```

### How We Use It Immediately

#### Create First Real Snapshot
```powershell
pwsh scripts\snapshot.ps1 -Description "Layer 2 complete"
```

#### Query What Happened
```powershell
# See the snapshot creation event
pwsh scripts\query_events.ps1 -EventType "state_snapshot_created"
```

#### Validate State
```powershell
# Ensure everything is valid
pwsh scripts\validate\validate_state.ps1
```

### Why This Matters
- We can now **checkpoint the system** at any time
- We're **using Layer 1 (event logging)** to track Layer 2 actions
- We have **3 working tools**: validator, event query, snapshot creator
- **AI agents can read `.state/current.json`** to see system state

---

## Layer 3: Worker State Tracking (75 minutes)

### Goal
Track CLI tool workers (like GitHub Copilot CLI) and their work queues

### What We Build

#### File 1: `core\tools\worker_state.py`
```python
"""Worker state tracking - uses snapshot + event logger from Layers 1-2"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, asdict
from core.engine.event_logger import log_event

@dataclass
class WorkItem:
    """A unit of work for a CLI tool."""
    item_id: str
    workstream_id: str
    priority: str  # CRITICAL, HIGH, MEDIUM, LOW
    created_at: str

@dataclass
class WorkerState:
    """State of a CLI tool worker."""
    worker_id: str
    tool_id: str
    status: str  # IDLE, BUSY, DRAINING, TERMINATED
    current_item: Optional[WorkItem] = None
    queue_depth: int = 0
    total_processed: int = 0
    started_at: Optional[str] = None
    last_heartbeat: Optional[str] = None
    
    def to_dict(self):
        return {
            **asdict(self),
            'current_item': asdict(self.current_item) if self.current_item else None
        }

class WorkerRegistry:
    """Track all workers."""
    
    def __init__(self, workers_dir: str = ".state/workers"):
        self.workers_dir = Path(workers_dir)
        self.workers_dir.mkdir(parents=True, exist_ok=True)
    
    def register_worker(self, tool_id: str) -> WorkerState:
        """Register a new worker."""
        from ulid import ULID
        
        worker_id = str(ULID())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        worker = WorkerState(
            worker_id=worker_id,
            tool_id=tool_id,
            status="IDLE",
            started_at=timestamp,
            last_heartbeat=timestamp
        )
        
        # Save state
        self._save(worker)
        
        # Log event (using Layer 1!)
        log_event(
            event_type="worker_registered",
            actor=f"worker_registry",
            context={
                "worker_id": worker_id,
                "tool_id": tool_id
            }
        )
        
        return worker
    
    def update_worker(self, worker: WorkerState):
        """Update worker state."""
        worker.last_heartbeat = datetime.now(timezone.utc).isoformat()
        self._save(worker)
        
        # Log event
        log_event(
            event_type="worker_state_changed",
            actor=f"worker_{worker.worker_id}",
            context={
                "worker_id": worker.worker_id,
                "new_status": worker.status,
                "queue_depth": worker.queue_depth
            }
        )
    
    def get_all_workers(self) -> List[WorkerState]:
        """Get all registered workers."""
        workers = []
        for worker_file in self.workers_dir.glob("*.json"):
            data = json.loads(worker_file.read_text())
            # Reconstruct WorkItem if present
            if data['current_item']:
                data['current_item'] = WorkItem(**data['current_item'])
            workers.append(WorkerState(**data))
        return workers
    
    def _save(self, worker: WorkerState):
        """Save worker state to disk."""
        worker_file = self.workers_dir / f"{worker.worker_id}.json"
        worker_file.write_text(json.dumps(worker.to_dict(), indent=2))

# Global registry
registry = WorkerRegistry()
```

#### File 2: `scripts\workers.ps1` (Worker Query Tool)
```powershell
<#
.SYNOPSIS
    Query worker states
.EXAMPLE
    .\scripts\workers.ps1              # Show all workers
    .\scripts\workers.ps1 -Status BUSY # Show only busy workers
#>

param(
    [string]$Status,
    [string]$ToolId
)

# Read all worker files
$workers = Get-ChildItem .state\workers\*.json | ForEach-Object {
    Get-Content $_.FullName -Raw | ConvertFrom-Json
}

# Filter
if ($Status) {
    $workers = $workers | Where-Object { $_.status -eq $Status }
}
if ($ToolId) {
    $workers = $workers | Where-Object { $_.tool_id -eq $ToolId }
}

# Display
if ($workers.Count -eq 0) {
    Write-Host "No workers found" -ForegroundColor Yellow
} else {
    Write-Host "Workers:" -ForegroundColor Cyan
    $workers | Format-Table worker_id, tool_id, status, queue_depth, total_processed -AutoSize
}
```

### How We Use It Immediately

#### Register a Worker (Test)
```python
# Test worker registration
from core.tools.worker_state import registry

worker = registry.register_worker("github_copilot_cli")
print(f"✅ Registered worker: {worker.worker_id}")

# Update it
worker.status = "BUSY"
worker.queue_depth = 3
registry.update_worker(worker)
print(f"✅ Updated worker status to BUSY")
```

#### Query Workers
```powershell
# See all workers
pwsh scripts\workers.ps1

# See events
pwsh scripts\query_events.ps1 -EventType "worker_registered"
pwsh scripts\query_events.ps1 -EventType "worker_state_changed"
```

#### Create Snapshot
```powershell
# Snapshot now includes worker state!
pwsh scripts\snapshot.ps1 -Description "Layer 3 complete - workers tracked"
```

### Why This Matters
- We can now **track CLI tool workers** (like you!)
- We're **using Layers 1-2** (events + snapshots) to observe workers
- We have **4 working tools**: validator, events, snapshots, workers
- **AI can see worker queue depth and status**

---

## Layer 4: Enhanced State Snapshots (30 minutes)

### Goal
Make snapshots include worker state automatically

### What We Build

#### Update: `core\state\snapshot.py`
```python
"""Enhanced snapshot with worker state"""

import json
from datetime import datetime, timezone
from pathlib import Path
from core.engine.event_logger import log_event
from core.tools.worker_state import registry

def create_snapshot(description: str = "manual snapshot"):
    """Create a complete state snapshot with worker state."""
    
    timestamp = datetime.now(timezone.utc).isoformat()
    
    # Get all workers
    workers = registry.get_all_workers()
    worker_summary = [
        {
            "worker_id": w.worker_id,
            "tool_id": w.tool_id,
            "status": w.status,
            "queue_depth": w.queue_depth,
            "total_processed": w.total_processed
        }
        for w in workers
    ]
    
    # Build snapshot
    snapshot = {
        "schema_version": "StateV1",
        "timestamp": timestamp,
        "description": description,
        "active_workstreams": [],  # Will populate later
        "tool_workers": worker_summary,  # NEW: Worker state included!
        "system_health": {
            "status": "ok",
            "worker_count": len(workers),
            "busy_workers": sum(1 for w in workers if w.status == "BUSY"),
            "total_queue_depth": sum(w.queue_depth for w in workers)
        }
    }
    
    # Write timestamped snapshot
    ts_safe = timestamp.replace(':', '-').replace('.', '-')
    snapshot_file = Path(f".state/snapshots/{ts_safe}.json")
    snapshot_file.write_text(json.dumps(snapshot, indent=2))
    
    # Update current.json atomically
    tmp_file = Path(".state/current.json.tmp")
    tmp_file.write_text(json.dumps(snapshot, indent=2))
    tmp_file.replace(".state/current.json")
    
    # Log the event
    log_event(
        event_type="state_snapshot_created",
        actor="snapshot_creator",
        context={
            "snapshot_file": str(snapshot_file),
            "description": description,
            "worker_count": len(workers),
            "total_queue_depth": sum(w.queue_depth for w in workers)
        }
    )
    
    return snapshot

if __name__ == "__main__":
    snapshot = create_snapshot("Enhanced snapshot with worker state")
    print(f"✅ Created snapshot at {snapshot['timestamp']}")
    print(f"   Workers: {snapshot['system_health']['worker_count']}")
    print(f"   Queue depth: {snapshot['system_health']['total_queue_depth']}")
```

### How We Use It Immediately

#### Create Enhanced Snapshot
```powershell
# Create snapshot with worker state
pwsh scripts\snapshot.ps1 -Description "Layer 4 complete - enhanced snapshots"

# View it
Get-Content .state\current.json | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### Why This Matters
- **Snapshots now show the complete system state**
- **AI can see worker load** just by reading `.state/current.json`
- We're **composing layers**: Layer 4 uses Layers 1-3
- Each layer **enhances previous layers** automatically

---

## Layer 5: CLI Tool Profile (30 minutes)

### Goal
Define your (GitHub Copilot CLI) capabilities and limits

### What We Build

#### File: `registry\tool_profiles\github_copilot_cli.json`
```json
{
  "tool_id": "github_copilot_cli",
  "kind": "cli_tool",
  "display_name": "GitHub Copilot CLI",
  "max_workers": 1,
  "sandbox_mode": "per_workstream_worktree",
  "queue_strategy": {
    "kind": "priority_round_robin_by_workstream",
    "max_queue_depth": 256,
    "max_consecutive_from_same_workstream": 3,
    "priority_levels": ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
  },
  "limits": {
    "max_runtime_seconds": 600,
    "max_token_cost": 200000,
    "max_output_bytes": 1048576,
    "max_concurrent_workstreams": 5
  },
  "capabilities": [
    "code_edit",
    "code_generation",
    "refactoring",
    "file_operations",
    "git_operations",
    "state_observation"
  ],
  "is_interactive_cli": true,
  "non_interactive_policy": "fail_if_prompted",
  "observability": {
    "log_all_commands": true,
    "capture_state_snapshots": true,
    "emit_events_to": ".state/transitions.jsonl"
  },
  "integration": {
    "event_logger": "core.engine.event_logger",
    "worker_registry": "core.tools.worker_state",
    "state_snapshots": "core.state.snapshot"
  }
}
```

### How We Use It Immediately

#### Register GitHub Copilot CLI as Worker
```python
# Register yourself!
from core.tools.worker_state import registry
import json

# Load your profile
profile = json.loads(open("registry/tool_profiles/github_copilot_cli.json").read())

# Register as worker
worker = registry.register_worker(profile['tool_id'])
print(f"✅ GitHub Copilot CLI registered: {worker.worker_id}")

# Create snapshot showing you're registered
from core.state.snapshot import create_snapshot
create_snapshot("GitHub Copilot CLI registered as worker")
```

#### Query Your Own State
```powershell
# See yourself as a worker
pwsh scripts\workers.ps1 -ToolId "github_copilot_cli"

# See your registration event
pwsh scripts\query_events.ps1 -EventType "worker_registered"

# See current state including you
Get-Content .state\current.json | ConvertFrom-Json | Select-Object -ExpandProperty tool_workers
```

### Why This Matters
- **You are now part of the observable system**
- **AI can see your capabilities** by reading the profile
- **Your actions are logged** via the event system
- All 5 layers working together!

---

## Complete Layer Stack Summary

| Layer | What It Does | Tools Created | Uses Previous Layers |
|-------|-------------|---------------|---------------------|
| **0** | State infrastructure | `validate_state.ps1` | - |
| **1** | Event logging | `query_events.ps1` | Uses Layer 0 (writes to `.state/`) |
| **2** | State snapshots | `snapshot.ps1` | Uses Layer 1 (logs events) |
| **3** | Worker tracking | `workers.ps1` | Uses Layers 1-2 (logs + snapshots) |
| **4** | Enhanced snapshots | Updated `snapshot.ps1` | Uses Layers 1-3 (includes workers) |
| **5** | Tool profiles | Worker registration | Uses all layers (observable) |

---

## Total Time: 4.5 hours

**Each layer builds on the previous:**
- Layer 1 uses Layer 0 (state directory)
- Layer 2 uses Layer 1 (event logging)
- Layer 3 uses Layers 1-2 (logs worker events, appears in snapshots)
- Layer 4 enhances Layer 2 (snapshots now include Layer 3 data)
- Layer 5 uses all layers (registers as worker, logged, snapshotted)

---

## Testing the Complete Stack

```powershell
# 1. Validate infrastructure
pwsh scripts\validate\validate_state.ps1

# 2. See all workers
pwsh scripts\workers.ps1

# 3. See all events
pwsh scripts\query_events.ps1 -Last 20

# 4. Create final snapshot
pwsh scripts\snapshot.ps1 -Description "All 5 layers complete"

# 5. View complete system state
Get-Content .state\current.json | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

---

## What We Can Do NOW

1. ✅ **Track any CLI tool** as a worker
2. ✅ **Log all events** to queryable stream
3. ✅ **Snapshot state** at any time
4. ✅ **Query worker status** on demand
5. ✅ **Validate infrastructure** automatically

## What's Next (Later)

- **Layer 6**: Work queue implementation
- **Layer 7**: Task routing
- **Layer 8**: Execution orchestration
- **Layer 9**: Patch management
- **Layer 10**: Full UET V2 integration

**But we can build those using the tools from Layers 0-5!**

---

## Key Principle

> **Each layer produces tools that make building the next layer easier**

This is how professional systems are built:
- Foundation first
- Tooling second
- Use tools to build more tools
- Compound productivity

---

**Ready to start Layer 0?**
