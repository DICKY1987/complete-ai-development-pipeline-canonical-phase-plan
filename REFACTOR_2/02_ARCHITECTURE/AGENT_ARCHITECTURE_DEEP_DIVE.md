---
doc_id: DOC-GUIDE-AGENT-ARCHITECTURE-DEEP-DIVE-1532
---

# Agent Architecture Deep Dive: Self-Replication vs Background Tasks

**Created**: 2025-11-29  
**Purpose**: Detailed analysis of multi-agent orchestration approaches for the refactor pipeline

---

## Executive Summary

| Approach | Complexity | Overhead | Control | Resilience | Best For |
|----------|-----------|----------|---------|------------|----------|
| **Self-Replication** | Medium | Low | High | Medium | Parallel workstreams with coordination |
| **Background Tasks** | Low | Medium | Low | High | Fire-and-forget, crash recovery |
| **Hybrid (Recommended)** | High | Medium | High | Very High | Production-grade multi-agent systems |

---

## 🔁 Approach 2: Self-Replication (Deep Dive)

### How It Works

```
┌─────────────────────────────────────────────────────────┐
│ Orchestrator Process (PID 1000)                         │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 1. Read workstreams from INDEPENDENT_WORKSTREAMS_   │ │
│ │    ANALYSIS.md                                       │ │
│ │ 2. Create worktrees for each workstream              │ │
│ │ 3. Spawn worker processes:                           │ │
│ │    python multi_agent_orchestrator.py \              │ │
│ │      --mode worker \                                 │ │
│ │      --workstream WS-001 \                           │ │
│ │      --worktree .worktrees/ws-001                    │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ Worker 1         │ │ Worker 2         │ │ Worker 3         │
│ PID 1001         │ │ PID 1002         │ │ PID 1003         │
│                  │ │                  │ │                  │
│ WS-001: Core     │ │ WS-002: Error    │ │ WS-003: AIM      │
│ Worktree: ws-001 │ │ Worktree: ws-002 │ │ Worktree: ws-003 │
│                  │ │                  │ │                  │
│ Tool: aider      │ │ Tool: aider      │ │ Tool: aider      │
│ Fallback: LLM    │ │ Fallback: LLM    │ │ Fallback: LLM    │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

### Implementation Details

#### A. Process Spawning (PowerShell)

```python
# multi_agent_orchestrator.py

import subprocess
import sys
from pathlib import Path

class MultiAgentOrchestrator:
    def spawn_worker(self, workstream_id: str, worktree_path: Path):
        """Spawn a copy of itself as a worker process"""
        
        # Build command to spawn worker
        cmd = [
            sys.executable,  # Same Python interpreter
            __file__,        # This same script
            "--mode", "worker",
            "--workstream", workstream_id,
            "--worktree", str(worktree_path)
        ]
        
        # Spawn as subprocess
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP  # Windows
        )
        
        return process
    
    def orchestrate(self):
        """Main orchestrator logic"""
        workstreams = self.load_workstreams()
        processes = []
        
        for ws in workstreams:
            # Create worktree
            worktree_path = self.worktree_manager.create(ws.id)
            
            # Spawn worker
            proc = self.spawn_worker(ws.id, worktree_path)
            processes.append(proc)
            
            print(f"✅ Spawned worker PID {proc.pid} for {ws.id}")
        
        # Wait for all workers
        for proc in processes:
            proc.wait()
            print(f"✅ Worker PID {proc.pid} completed")
```

#### B. Worker Mode Logic

```python
def worker_mode(self, workstream_id: str, worktree_path: Path):
    """Execute a single workstream as a worker"""
    
    # Change to worktree directory
    os.chdir(worktree_path)
    
    # Load workstream tasks
    tasks = self.load_workstream_tasks(workstream_id)
    
    # Execute with tool fallback
    for task in tasks:
        try:
            # Try aider first
            result = self.execute_with_aider(task)
        except AiderFailure as e:
            print(f"⚠️  Aider failed: {e}, falling back to direct LLM")
            result = self.execute_with_llm(task)
        
        # Save result
        self.save_task_result(task, result)
    
    print(f"✅ Worker completed {workstream_id}")
```

### Complexity Analysis

**Creation Complexity**: ⭐⭐⭐ (3/5 - Medium)

- Need to implement mode flag handling (`--mode worker`)
- Process spawning logic (20-30 lines)
- IPC mechanism for status updates (optional but recommended)

**Maintenance Complexity**: ⭐⭐ (2/5 - Low)

- Single codebase (same script runs as orchestrator or worker)
- Easy to debug (can run worker mode manually)
- No external dependencies

**Code Estimate**: ~150-200 lines total

### System Overhead

**Memory**: Low
- Each worker is a full Python process (~50-100 MB)
- 3 workers = ~300 MB total (minimal)

**CPU**: Low
- Workers are mostly I/O bound (waiting for aider/LLM)
- Minimal CPU except during git operations

**Disk**: Low
- Worktrees share objects (minimal disk usage)
- Each worktree only stores modified files

### Control & Monitoring

**High Control**:
- Orchestrator can kill workers (`proc.terminate()`)
- Can monitor worker progress via stdout/stderr
- Can implement timeout logic

```python
# Timeout example
import time

start_time = time.time()
while proc.poll() is None:  # Still running
    if time.time() - start_time > timeout:
        proc.terminate()
        print(f"❌ Worker timed out, killed PID {proc.pid}")
        break
    time.sleep(1)
```

### Pros & Cons

**Pros**:
✅ Full control over worker lifecycle  
✅ Easy to implement shared progress tracking  
✅ Workers inherit orchestrator environment  
✅ Can pass data via command-line args or files  
✅ Easy to debug (just run with `--mode worker`)

**Cons**:
❌ Workers die if orchestrator crashes  
❌ Need to handle SIGINT/SIGTERM gracefully  
❌ IPC requires file-based or network communication

---

## 🚀 Approach 3: Background Tasks (Deep Dive)

### How It Works

```
┌─────────────────────────────────────────────────────────┐
│ Orchestrator Process (PID 1000)                         │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 1. Read workstreams                                  │ │
│ │ 2. Create worktrees                                  │ │
│ │ 3. Start detached processes:                         │ │
│ │    Start-Process -NoNewWindow -FilePath python \     │ │
│ │      -ArgumentList "worker.py --workstream WS-001"   │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ Detached Task 1  │ │ Detached Task 2  │ │ Detached Task 3  │
│ PID 2001         │ │ PID 2002         │ │ PID 2003         │
│ (Survives crash) │ │ (Survives crash) │ │ (Survives crash) │
│                  │ │                  │ │                  │
│ Writes status to │ │ Writes status to │ │ Writes status to │
│ .status/ws-001   │ │ .status/ws-002   │ │ .status/ws-003   │
└──────────────────┘ └──────────────────┘ └──────────────────┘

   ┌────────────────────────────────────────┐
   │ Orchestrator crashes or exits           │
   │ Background tasks continue running! ✅   │
   └────────────────────────────────────────┘
```

### Implementation Details

#### A. Detached Process Spawning (PowerShell)

```python
import subprocess

def spawn_detached_worker(workstream_id: str, worktree_path: Path):
    """Spawn a completely detached background worker"""
    
    # PowerShell command to start detached process
    ps_cmd = f"""
    Start-Process -NoNewWindow -FilePath python `
        -ArgumentList "worker.py --workstream {workstream_id} --worktree {worktree_path}" `
        -RedirectStandardOutput .logs/{workstream_id}.log `
        -RedirectStandardError .logs/{workstream_id}.err
    """
    
    subprocess.run(
        ["powershell", "-Command", ps_cmd],
        check=True
    )
    
    print(f"🚀 Launched detached worker for {workstream_id}")
```

#### B. Status File Communication

```python
# worker.py (detached process)

import json
import time
from pathlib import Path

def update_status(workstream_id: str, status: dict):
    """Write status to file for orchestrator to read"""
    status_file = Path(f".status/{workstream_id}.json")
    status_file.parent.mkdir(exist_ok=True)
    
    status["last_update"] = time.time()
    status_file.write_text(json.dumps(status, indent=2))

# Main worker loop
while tasks_remaining:
    task = next_task()
    update_status(workstream_id, {
        "status": "running",
        "current_task": task.id,
        "progress": "3/10"
    })
    
    execute_task(task)

update_status(workstream_id, {
    "status": "completed",
    "exit_code": 0
})
```

#### C. Orchestrator Monitoring

```python
# multi_agent_orchestrator.py

def monitor_detached_workers(self):
    """Poll status files to track progress"""
    
    status_dir = Path(".status")
    
    while True:
        all_complete = True
        
        for ws_id in self.workstreams:
            status_file = status_dir / f"{ws_id}.json"
            
            if not status_file.exists():
                all_complete = False
                continue
            
            status = json.loads(status_file.read_text())
            
            if status["status"] != "completed":
                all_complete = False
            
            print(f"{ws_id}: {status['status']} - {status.get('progress', 'N/A')}")
        
        if all_complete:
            print("✅ All workers completed!")
            break
        
        time.sleep(10)  # Poll every 10 seconds
```

### Complexity Analysis

**Creation Complexity**: ⭐⭐ (2/5 - Low)

- Simpler than self-replication (no mode flags needed)
- Just need PowerShell command or subprocess.Popen with detach flags
- File-based status is simple

**Maintenance Complexity**: ⭐⭐⭐ (3/5 - Medium)

- Harder to debug (processes run independently)
- Need to manage orphaned processes
- Status file cleanup required

**Code Estimate**: ~100-150 lines

### System Overhead

**Memory**: Medium
- Each worker is a full process (~50-100 MB)
- Workers persist even after orchestrator exits (can accumulate)

**CPU**: Low
- Same as self-replication

**Disk**: Medium
- Status files accumulate (need cleanup)
- Log files can grow large

### Control & Monitoring

**Low Control**:
- Orchestrator **cannot** kill detached workers directly
- Must use OS tools (`taskkill`, `pkill`)
- Hard to implement timeouts

```python
# To kill detached workers (requires PID tracking)
import psutil

# Save PID when spawning
pid_file = Path(f".pids/{workstream_id}.pid")
# ... (worker writes its PID to file)

# Kill later
pid = int(pid_file.read_text())
psutil.Process(pid).terminate()
```

### Pros & Cons

**Pros**:
✅ Survives orchestrator crashes  
✅ True background execution  
✅ Can reconnect to running workers  
✅ Simple spawn logic  

**Cons**:
❌ Difficult to control/kill workers  
❌ Orphaned processes if not cleaned up  
❌ Only file-based or network communication  
❌ Harder to debug  
❌ Need to track PIDs manually

---

## 🎯 Hybrid Approach (Recommended)

### Architecture

```python
class MultiAgentOrchestrator:
    def execute_workstreams(self, detached=False):
        """Execute with configurable resilience"""
        
        if detached:
            # Use background tasks for crash resilience
            return self._execute_detached()
        else:
            # Use self-replication for better control
            return self._execute_self_replication()
    
    def _execute_self_replication(self):
        """Default mode: spawn worker subprocesses"""
        processes = []
        
        for ws in self.workstreams:
            worktree = self.create_worktree(ws.id)
            proc = self.spawn_worker(ws.id, worktree)
            processes.append(proc)
        
        # Monitor in real-time
        for proc in processes:
            proc.wait()
        
        return self.collect_results()
    
    def _execute_detached(self):
        """Resilient mode: detached background tasks"""
        
        for ws in self.workstreams:
            worktree = self.create_worktree(ws.id)
            self.spawn_detached_worker(ws.id, worktree)
        
        # Monitor via status files
        self.monitor_detached_workers()
        
        return self.collect_results()
```

### When to Use Which

| Scenario | Use | Reason |
|----------|-----|--------|
| **Normal execution** | Self-Replication | Better control, real-time monitoring |
| **Long-running refactor (>1 hour)** | Detached | Survive crashes, can disconnect |
| **Testing/Development** | Self-Replication | Easier to debug, can Ctrl+C to stop |
| **Production CI/CD** | Hybrid (detached with heartbeat) | Resilience + monitoring |

### Implementation Plan

```python
# CLI interface
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["orchestrator", "worker"], default="orchestrator")
    parser.add_argument("--detached", action="store_true", help="Use detached background tasks")
    parser.add_argument("--workstream", help="Worker mode: workstream ID")
    parser.add_argument("--worktree", help="Worker mode: worktree path")
    
    args = parser.parse_args()
    
    if args.mode == "orchestrator":
        orchestrator = MultiAgentOrchestrator()
        orchestrator.execute_workstreams(detached=args.detached)
    elif args.mode == "worker":
        worker = WorkstreamWorker(args.workstream, args.worktree)
        worker.execute()
```

---

## Comparison Matrix

| Feature | Self-Replication | Background Tasks | Hybrid |
|---------|-----------------|------------------|--------|
| **Creation Complexity** | Medium | Low | High |
| **Maintenance Complexity** | Low | Medium | Medium |
| **Memory Overhead** | Low (300 MB) | Medium (300 MB + persist) | Medium |
| **CPU Overhead** | Low | Low | Low |
| **Control** | High | Low | Medium-High |
| **Resilience** | Medium | High | Very High |
| **Debugging** | Easy | Hard | Medium |
| **Crash Recovery** | No | Yes | Yes |
| **Real-time Monitoring** | Yes | No (polling only) | Yes |
| **Best For** | Development, Testing | Production, Long-running | Both |

---

## Recommended Implementation Roadmap

### Phase 1: Self-Replication (Week 1)
- Implement `--mode worker` flag
- Add process spawning logic
- Test with 3 workstreams locally

**Deliverable**: Working multi-agent orchestrator (200 lines)

### Phase 2: Status Tracking (Week 1)
- Add file-based status updates from workers
- Implement progress monitoring in orchestrator
- Add graceful shutdown handling

**Deliverable**: Real-time progress dashboard (50 lines)

### Phase 3: Detached Mode (Week 2)
- Implement `--detached` flag
- Add PID tracking
- Add orphan process cleanup

**Deliverable**: Crash-resilient execution (100 lines)

### Phase 4: Tool Fallback (Week 2)
- Integrate aider in workers
- Add LLM fallback logic
- Add tool selection strategy

**Deliverable**: Complete resilient system (150 lines)

**Total Code**: ~500 lines (manageable for 1-2 week implementation)

---

## Conclusion

**Use self-replication by default** for simplicity and control, with **detached mode as an option** for long-running or production scenarios. The hybrid approach gives you the best of both worlds with minimal complexity.

The orchestrator becomes a powerful, resilient system that can:
- Execute 3 workstreams in parallel (2-3x speedup)
- Survive crashes (with detached mode)
- Fall back between tools (aider → LLM)
- Monitor progress in real-time
- Clean up resources automatically

**Next Step**: Implement Phase 1 (self-replication) first, test thoroughly, then add detached mode later if needed.
