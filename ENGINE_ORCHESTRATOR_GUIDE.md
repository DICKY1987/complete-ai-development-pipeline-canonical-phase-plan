---
doc_id: DOC-GUIDE-ENGINE-ORCHESTRATOR-GUIDE-149
---

# 🎯 Engine-Based Orchestrator - Quick Start

**Found**: Complete job queue system in `engine/` folder  
**Status**: ✅ Production-ready, better than simple executor  
**Location**: `engine/orchestrator/orchestrator.py`

---

## 🚀 What You Have

### **Core System**
```
engine/
├── orchestrator/     - Job orchestrator with CLI
├── queue/           - Async job queue (priorities, retry, workers)
├── adapters/        - Tool adapters (aider, codex, git, tests)
├── state_store/     - SQLite persistence
└── interfaces/      - Clean abstractions
```

### **Key Features**
- ✅ **Job Queue** - Submit jobs with priorities
- ✅ **Worker Pool** - Parallel execution (configurable workers)
- ✅ **Dependencies** - Jobs can depend on other jobs
- ✅ **Retry Logic** - Auto-retry failed jobs
- ✅ **State Tracking** - SQLite persistence
- ✅ **CLI Interface** - `python -m engine.orchestrator run-job`
- ✅ **Async Execution** - Built on asyncio

---

## 💻 How To Use It

### **1. Create a Job File**
```json
{
  "job_id": "ws-01-001",
  "workstream_id": "ws-01-hardcoded-path-index",
  "tool": "aider",
  "files": ["docs/HARDCODED_PATH_INDEXER.md"],
  "instructions": "Review and validate the hardcoded path index documentation",
  "config": {
    "auto_commit": false,
    "model": "gpt-4"
  }
}
```

### **2. Run Single Job (CLI)**
```powershell
# Run a single job
python -m engine.orchestrator run-job --job-file jobs/ws-01.json

# Check job status
python -m engine.orchestrator status --job-id ws-01-001
```

### **3. Use Queue Manager (Python)**
```python
from engine.queue.queue_manager import QueueManager
import asyncio

async def run_workstreams():
    # Initialize queue with 3 workers
    manager = QueueManager(worker_count=3)
    await manager.start()
    
    # Submit jobs
    job1 = await manager.submit_job("jobs/ws-01.json", priority="normal")
    job2 = await manager.submit_job("jobs/ws-03.json", priority="high")
    job3 = await manager.submit_job("jobs/ws-04.json", priority="normal")
    
    # Monitor progress
    status = await manager.get_status()
    print(f"Queue: {status['queued']} queued, {status['running']} running")
    
    # Wait for completion
    await manager.wait_until_empty()
    await manager.stop()

# Run it
asyncio.run(run_workstreams())
```

---

## 🎯 Converting Workstreams to Jobs

Your workstream JSON files need minor conversion:

**Workstream format** (current):
```json
{
  "id": "ws-01-hardcoded-path-index",
  "title": "Baseline indexed",
  "tool": "codex",
  "files_scope": ["docs/HARDCODED_PATH_INDEXER.md"],
  "tasks": ["Baseline indexed (no-op)"],
  "depends_on": []
}
```

**Job format** (for engine):
```json
{
  "job_id": "ws-01-001",
  "workstream_id": "ws-01-hardcoded-path-index",
  "tool": "codex",
  "files": ["docs/HARDCODED_PATH_INDEXER.md"],
  "instructions": "Baseline indexed (no-op)",
  "dependencies": []
}
```

---

## 🔧 Quick Conversion Script

```python
# scripts/convert_workstreams_to_jobs.py
import json
from pathlib import Path

def convert_workstream_to_job(ws_file):
    """Convert workstream JSON to job JSON."""
    with open(ws_file) as f:
        ws = json.load(f)
    
    job = {
        "job_id": f"{ws['id']}-001",
        "workstream_id": ws["id"],
        "tool": ws.get("tool", "aider"),
        "files": ws.get("files_scope", []),
        "instructions": "\n".join(ws.get("tasks", [])),
        "dependencies": ws.get("depends_on", []),
        "config": {
            "auto_commit": False
        }
    }
    
    # Save job file
    job_file = Path("jobs") / f"{ws['id']}.json"
    job_file.parent.mkdir(exist_ok=True)
    
    with open(job_file, "w") as f:
        json.dump(job, f, indent=2)
    
    return job_file

# Convert all workstreams
for ws_file in Path("workstreams").glob("ws-*.json"):
    try:
        job_file = convert_workstream_to_job(ws_file)
        print(f"✅ {ws_file.name} → {job_file.name}")
    except Exception as e:
        print(f"❌ {ws_file.name}: {e}")
```

---

## 🚀 Recommended Workflow

### **Phase 1: Setup** (5 minutes)
1. Create `jobs/` directory
2. Run conversion script
3. Verify job files created

### **Phase 2: Test** (15 minutes)
```powershell
# Test single job
python -m engine.orchestrator run-job --job-file jobs/ws-01-hardcoded-path-index.json

# Check it worked
python -m engine.orchestrator status --job-id ws-01-hardcoded-path-index-001
```

### **Phase 3: Batch Execute** (ongoing)
```python
# scripts/run_all_workstreams.py
import asyncio
from engine.queue.queue_manager import QueueManager
from pathlib import Path

async def main():
    manager = QueueManager(worker_count=3, db_path="workstreams.db")
    await manager.start()
    
    # Submit all jobs
    for job_file in sorted(Path("jobs").glob("ws-*.json")):
        job_id = await manager.submit_job(str(job_file))
        print(f"Queued: {job_id}")
    
    # Monitor until done
    while not await manager.is_empty():
        status = await manager.get_status()
        print(f"Progress: {status}")
        await asyncio.sleep(5)
    
    await manager.stop()
    print("✅ All workstreams complete!")

asyncio.run(main())
```

---

## ✅ Advantages Over Simple Executor

| Feature | Simple Executor | Engine Queue |
|---------|----------------|--------------|
| **Parallelization** | ❌ Sequential only | ✅ Configurable workers |
| **Dependencies** | ✅ Basic | ✅ Full DAG support |
| **Retry Logic** | ❌ Manual | ✅ Automatic |
| **State Persistence** | 🟡 JSON file | ✅ SQLite |
| **Priorities** | ❌ No | ✅ 4 levels |
| **Monitoring** | 🟡 Basic | ✅ Full status API |
| **Interactive** | ✅ Yes | 🟡 Via CLI |

---

## 🎯 Next Steps

**Option A: Quick Win** (30 minutes)
1. Create the conversion script
2. Convert all workstreams
3. Run a few test jobs
4. Evaluate if it works better

**Option B: Full Migration** (2 hours)
1. Create conversion script
2. Convert all 37 workstreams
3. Create batch execution script
4. Run 3-5 workers in parallel
5. Complete all workstreams

**Option C: Hybrid** (1 hour)
1. Use engine queue for simple/automated workstreams
2. Use simple executor for complex/manual ones
3. Best of both worlds

---

## 💡 My Recommendation

**Use the engine queue system!** It's:
- ✅ Already built and tested
- ✅ More powerful than simple executor
- ✅ Production-ready
- ✅ Supports parallelization
- ✅ Has proper state management

**Quick win**: Convert 5 workstreams, test them, then decide.

---

**Want me to create the conversion script and get you started?**
