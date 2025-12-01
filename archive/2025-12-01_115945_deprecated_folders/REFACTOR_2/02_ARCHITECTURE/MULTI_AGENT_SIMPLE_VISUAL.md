---
doc_id: DOC-GUIDE-MULTI-AGENT-SIMPLE-VISUAL-1534
---

# How 1 CLI Command Runs 3 Simultaneous AI Agents - Simple Visual Guide

## 🎯 **What You Type**

```powershell
.\scripts\run_multi_agent_refactor.ps1
```

**ONE COMMAND = 3 agents working simultaneously for 1-2 weeks!**

---

## 📊 **Visual: The Complete Stack**

```
YOU
 │
 │ Type command
 ▼
┌─────────────────────────────────────┐
│  PowerShell (1 process)             │
│  "Launcher & Coordinator"           │
│  PID: 12345                         │
└──────────┬──────────────────────────┘
           │ Spawns
           ▼
┌─────────────────────────────────────┐
│  Python Orchestrator (1 process)    │
│  "Brain - Manages 3 agents"         │
│  PID: 12347                         │
│  Uses: asyncio event loop           │
└──┬────────┬──────────┬──────────────┘
   │        │          │
   │Spawns  │Spawns    │Spawns
   ▼        ▼          ▼
┌──────┐ ┌──────┐  ┌──────┐
│Aider │ │Aider │  │Aider │  ← 3 AI workers
│Agent1│ │Agent2│  │Agent3│
│12348 │ │12349 │  │12350 │
└──┬───┘ └──┬───┘  └──┬───┘
   │        │         │
   │Works   │Works    │Works
   │in      │in       │in
   ▼        ▼         ▼
┌──────┐ ┌──────┐ ┌──────┐
│.work │ │.work │ │.work │  ← Isolated workspaces
│trees/│ │trees/│ │trees/│
│agent │ │agent │ │agent │
│-1-ws │ │-2-ws │ │-3-ws │
│-22/  │ │-03/  │ │-12/  │
└──────┘ └──────┘ └──────┘

Total: 5 processes
3 working simultaneously!
```

---

## 🔄 **Step-by-Step: What Happens**

### **STEP 1: You Execute** (Instant)

```
PS> .\scripts\run_multi_agent_refactor.ps1
    ↓
Windows creates PowerShell process (PID 12345)
```

---

### **STEP 2: PowerShell Validates** (10 seconds)

```
PowerShell (12345)
  ├─ Checks git is installed ✅
  ├─ Checks aider is available ✅
  ├─ Checks 39 workstream files exist ✅
  ├─ Checks disk space (45 GB free) ✅
  └─ Creates directories:
     ├─ logs/
     ├─ reports/
     ├─ .state/
     └─ .worktrees/

Output: ✅ All pre-flight checks passed!
```

---

### **STEP 3: Launch Orchestrator** (5 seconds)

```
PowerShell (12345)
  └─ python scripts\multi_agent_orchestrator.py
     ↓
     Creates Python process (PID 12347)
       ├─ Loads 39 workstream files
       ├─ Builds dependency graph
       ├─ Creates SQLite database
       └─ Initializes 3 agents:
          • agent-1 (idle)
          • agent-2 (idle)
          • agent-3 (idle)

Output: === Multi-Agent Orchestrator Initialized ===
        Total workstreams: 39
        Agents: 3
        Worktree isolation: ENABLED
```

---

### **STEP 4: Start Execution** ⚡ **SIMULTANEITY BEGINS!**

```
Python Orchestrator (12347) event loop:

  ┌─ Iteration 1 ────────────────────────┐
  │                                      │
  │ Find ready workstreams:              │
  │   [WS-22, WS-03, WS-12]             │
  │   (no dependencies)                  │
  │                                      │
  │ Assign WS-22 → Agent 1               │
  │   Create async task #1 ←─────────┐  │
  │                                   │  │
  │ Assign WS-03 → Agent 2            │  │
  │   Create async task #2 ←─────────┼──┤ All 3 tasks
  │                                   │  │ run at same
  │ Assign WS-12 → Agent 3            │  │ time!
  │   Create async task #3 ←─────────┘  │
  │                                      │
  └──────────────────────────────────────┘
```

**Process tree at this moment:**

```
PowerShell (12345)
  └─ Python (12347)
     ├─ Task #1 (Agent 1, WS-22) STARTED
     ├─ Task #2 (Agent 2, WS-03) STARTED
     └─ Task #3 (Agent 3, WS-12) STARTED
```

---

### **STEP 5: Each Task Creates Worktree** (2 seconds each)

**Agent 1:**
```
Task #1 executes:
  1. git checkout -b ws/ws-22/agent-1 main
  2. git worktree add .worktrees/agent-1-ws-22 ws/ws-22/agent-1

Result: .worktrees/agent-1-ws-22/ created (full repo copy)
```

**Agent 2 & 3 do the same simultaneously:**
```
.worktrees/
├─ agent-1-ws-22/  ← Agent 1's workspace
├─ agent-2-ws-03/  ← Agent 2's workspace
└─ agent-3-ws-12/  ← Agent 3's workspace

3 isolated directories!
```

---

### **STEP 6: Each Task Launches Aider** (Main work!)

**Agent 1:**
```
Task #1 executes:
  aider core/state/db.py \\
    --message "WS-22: Add Pipeline Plus schema" \\
    --yes \\
    --auto-commits

Spawns: aider.exe (PID 12348)
Working directory: .worktrees/agent-1-ws-22/
```

**All 3 agents launch aider simultaneously:**

```
Python (12347)
  ├─ aider (12348) - Agent 1
  │  └─ Editing in: .worktrees/agent-1-ws-22/
  │  └─ Files: core/state/db.py
  │
  ├─ aider (12349) - Agent 2
  │  └─ Editing in: .worktrees/agent-2-ws-03/
  │  └─ Files: core/engine/orchestrator.py
  │
  └─ aider (12350) - Agent 3
     └─ Editing in: .worktrees/agent-3-ws-12/
     └─ Files: error/plugins/base.py

3 AIDER PROCESSES RUNNING AT SAME TIME!
```

**Key:** Each aider is in a **different directory**, so they **never interfere**!

---

### **STEP 7: Event Loop Monitors** (Continuous)

**Python's asyncio event loop checks progress:**

```
Loop (every 100ms):
  
  Check Task #1 (Agent 1):
    ├─ Is aider done? No
    └─ Continue to next
  
  Check Task #2 (Agent 2):
    ├─ Is aider done? No
    └─ Continue to next
  
  Check Task #3 (Agent 3):
    ├─ Is aider done? No
    └─ Continue to next
  
  Sleep 100ms, repeat...
```

**1 hour later:**

```
Loop check:
  
  Check Task #1 (Agent 1):
    ├─ Is aider done? YES! ✅
    └─ Process result...
```

---

### **STEP 8: Agent Completes & Merges** (When aider finishes)

**Agent 1 finishes WS-22:**

```
Task #1 detects aider exit:
  1. aider (12348) exited with code 0 ✅
  2. Read changes:
     - core/state/db.py modified
  3. Merge to main:
     $ git checkout main
     $ git merge ws/ws-22/agent-1
  4. Cleanup:
     $ git worktree remove .worktrees/agent-1-ws-22
  5. Mark agent-1 as available

Output: ✅ WS-22 completed successfully
        Merged ws/ws-22/agent-1 → main
        Removed worktree
```

**Meanwhile, Agents 2 & 3 still working:**

```
Python (12347)
  ├─ Agent 1: IDLE (ready for next task)
  ├─ aider (12349) - Agent 2 still working
  └─ aider (12350) - Agent 3 still working
```

---

### **STEP 9: Agent Picks Up Next Task** (Immediately)

```
Event loop:
  
  Find ready workstreams:
    ├─ WS-23 (depends on WS-22 ✅ complete)
    └─ Ready to assign!
  
  Get available agent:
    └─ agent-1 is IDLE
  
  Assign WS-23 → Agent 1:
    └─ Create async task #4

Agent 1 immediately starts working again!
```

**Process tree:**

```
Python (12347)
  ├─ aider (12351) - Agent 1, WS-23 (NEW!)
  ├─ aider (12349) - Agent 2, WS-03 (still working)
  └─ aider (12350) - Agent 3, WS-12 (still working)

Back to 3 agents working simultaneously!
```

---

### **STEP 10: Repeat Until All 39 Done** (1-2 weeks)

```
Loop continues:
  - Agents complete workstreams
  - Merge to main
  - Pick up next ready workstream
  - Repeat

Until: All 39 workstreams completed!
```

---

## ⚡ **The Key Technology: Asyncio**

**How 1 Python process manages 3 agents:**

```python
# Create 3 tasks (doesn't block!)
task1 = asyncio.create_task(run_agent_1())
task2 = asyncio.create_task(run_agent_2())
task3 = asyncio.create_task(run_agent_3())

# Event loop checks them continuously
while not all_done:
    for task in [task1, task2, task3]:
        if task.done():
            process_result(task)
            start_new_workstream()
    
    await asyncio.sleep(0.1)  # Check every 100ms
```

**Benefits:**
- ✅ Single thread (no race conditions)
- ✅ Efficient (doesn't waste CPU)
- ✅ Simple code
- ✅ Easy to debug

---

## 📊 **Timeline Example**

```
10:00 AM - START
═════════════════════════════════════════════════
PowerShell: Launch orchestrator
Python: Initialize 3 agents
  ↓
Agents start simultaneously:
  Agent 1 → WS-22 (1 hour)
  Agent 2 → WS-03 (4 hours)
  Agent 3 → WS-12 (2 hours)

Process count: 5 (PowerShell + Python + 3 aiders)

─────────────────────────────────────────────────
11:00 AM - AGENT 1 DONE
═════════════════════════════════════════════════
Agent 1: ✅ WS-22 complete, merged to main
       → Starts WS-23 (2 hours)

Agent 2: Still working (3h left)
Agent 3: Still working (1h left)

Process count: 5 (same processes, Agent 1 restarted)

─────────────────────────────────────────────────
12:00 PM - AGENT 3 DONE
═════════════════════════════════════════════════
Agent 1: Still working (1h left)
Agent 2: Still working (2h left)
Agent 3: ✅ WS-12 complete, merged to main
       → Starts WS-13 (2 hours)

Process count: 5

─────────────────────────────────────────────────
2:00 PM - AGENT 2 DONE
═════════════════════════════════════════════════
Agent 1: ✅ WS-23 complete
Agent 2: ✅ WS-03 complete
Agent 3: Still working

All 3 agents pick up new workstreams...

─────────────────────────────────────────────────
...continues for 1-2 weeks
═════════════════════════════════════════════════

FINAL RESULT:
  ✅ 39 workstreams completed
  ✅ All merged to main
  ✅ Zero conflicts
  ✅ Clean git history
```

---

## 🎯 **Why It Works**

### **1. Worktree Isolation**

```
Each agent in own directory:
  
  .worktrees/agent-1-ws-22/core/state/db.py  ← Agent 1 edits
  .worktrees/agent-2-ws-03/core/state/db.py  ← Agent 2 edits
  .worktrees/agent-3-ws-12/core/state/db.py  ← Agent 3 edits

Same file, but 3 DIFFERENT COPIES = Zero conflicts!
```

### **2. Async Execution**

```
Python asyncio:
  - Creates 3 tasks
  - All run "simultaneously"
  - Event loop manages them
  - No threading complexity
```

### **3. Sequential Merges**

```
Even though agents work in parallel,
merges happen one at a time:

  1. Agent 1 merges → main updated
  2. Agent 2 merges → main updated (includes Agent 1's work)
  3. Agent 3 merges → main updated (includes all previous work)

Result: Clean history, no conflicts!
```

---

## 📦 **Final Summary**

### **What You Get:**

| Metric | Value |
|--------|-------|
| **Input** | 1 PowerShell command |
| **Processes** | 5 total (2 managers + 3 workers) |
| **Memory** | ~50 MB overhead |
| **Speed** | 2-3x faster than sequential |
| **Conflicts** | Zero (worktrees prevent) |
| **Time** | 1-2 weeks for 39 workstreams |
| **Automation** | 100% (no manual intervention) |

### **Technology Stack:**

```
PowerShell → Launcher
  └─ Python + asyncio → Orchestrator
     └─ Aider (×3) → Workers
        └─ Git worktrees → Isolation
           └─ SQLite → Progress tracking
```

### **The Magic:**

✅ **Asyncio** = 1 Python process manages 3 agents  
✅ **Worktrees** = Each agent has isolated workspace  
✅ **Event loop** = Efficient, no CPU waste  
✅ **Dependencies** = Correct execution order  

**Result: Maximum parallelism with zero conflicts!** 🚀

---

**Created**: 2025-11-28  
**Format**: Simple visual guide  
**Time to read**: 10 minutes  
**Audience**: Quick overview
