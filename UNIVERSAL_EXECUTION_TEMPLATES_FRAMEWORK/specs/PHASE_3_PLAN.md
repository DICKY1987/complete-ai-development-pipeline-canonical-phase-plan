# Phase 3: Orchestration Engine - Implementation Plan

**Date:** 2025-11-20  
**Status:** 🚀 STARTING  
**Estimated Duration:** 15 days (3 weeks)  
**Current Progress:** 0%

---

## Overview

Phase 3 builds the runtime orchestration system that executes workstreams autonomously. This is the core execution engine that:
- Manages workstream runs and state
- Routes tasks to appropriate tools
- Handles retries and circuit breakers
- Tracks progress and generates reports

---

## Architecture

```
Phase 3: Orchestration Engine
├── PH-03-01: Core Orchestrator
│   ├── WS-03-01A: Run Management (6 days) ← START HERE
│   ├── WS-03-01B: Task Router (5 days)
│   └── WS-03-01C: Execution Scheduler (4 days)
│
├── PH-03-02: Tool Integration
│   ├── WS-03-02A: Tool Adapter Framework (5 days)
│   ├── WS-03-02B: Aider Integration (4 days)
│   └── WS-03-02C: Built-in Tools (3 days)
│
└── PH-03-03: Resilience & Monitoring
    ├── WS-03-03A: Circuit Breakers (3 days)
    ├── WS-03-03B: Retry Logic (2 days)
    └── WS-03-03C: Progress Tracking (3 days)
```

---

## Phase 3 Workstreams (Prioritized)

### **WS-03-01A: Run Management** (NEXT - Start immediately)
**Priority:** CRITICAL  
**Estimated:** 6 days  
**Status:** Ready to start

**Deliverables:**
- `core/engine/orchestrator.py` - Main orchestration logic
- `core/state/db.py` - SQLite backend for state
- `core/state/models.py` - Data models (RunRecord, StepAttempt, RunEvent)
- `core/engine/state_machine.py` - Run state transitions
- `tests/engine/test_run_lifecycle.py` - Comprehensive tests

**Tasks:**
1. Create database schema for runs (tables: runs, step_attempts, run_events)
2. Implement Run state machine (pending → running → succeeded/failed/quarantined)
3. Implement Run CRUD operations
4. Implement event emission for state transitions
5. Write comprehensive tests

**Dependencies:** Phase 2 ✅ (COMPLETE)

**Success Criteria:**
- Run lifecycle follows COOPERATION_SPEC state machine
- Events emitted for all state transitions
- Database persists run state correctly
- Test coverage >90%

---

### **WS-03-01B: Task Router**
**Priority:** CRITICAL  
**Estimated:** 5 days  
**Status:** Blocked (needs WS-03-01A)

**Deliverables:**
- `core/engine/router.py` - Task routing engine
- `core/engine/execution_request_builder.py` - Build execution requests
- `tests/engine/test_routing.py` - Routing tests

**Tasks:**
1. Load and parse router_config.json
2. Implement routing rules engine (match task → tool)
3. Implement ExecutionRequest builder
4. Add routing strategies (fixed, round_robin, auto)
5. Test routing with multiple tools

**Dependencies:** WS-03-01A

---

### **WS-03-01C: Execution Scheduler**
**Priority:** HIGH  
**Estimated:** 4 days  
**Status:** Blocked (needs WS-03-01B)

**Deliverables:**
- `core/engine/scheduler.py` - Task scheduling logic
- `core/engine/executor.py` - Tool execution wrapper
- `tests/engine/test_scheduling.py` - Scheduler tests

**Tasks:**
1. Implement dependency resolution
2. Implement parallel execution (when tasks are independent)
3. Implement sequential execution (when tasks depend on each other)
4. Add timeout handling
5. Test complex dependency graphs

**Dependencies:** WS-03-01B

---

### **WS-03-02A: Tool Adapter Framework**
**Priority:** HIGH  
**Estimated:** 5 days  
**Status:** Blocked (needs WS-03-01C)

**Deliverables:**
- `core/adapters/base.py` - Base tool adapter interface
- `core/adapters/shell.py` - Shell command adapter
- `core/adapters/python.py` - Python function adapter
- `tests/adapters/test_adapters.py` - Adapter tests

---

## Quick Start for WS-03-01A

### Step 1: Create directory structure
```bash
mkdir -p core/engine core/state tests/engine
```

### Step 2: Define database schema
Create `core/state/db.py` with tables:
- `runs` - Main run records
- `step_attempts` - Individual task execution attempts
- `run_events` - Event log for audit trail

### Step 3: Implement state machine
Create `core/engine/state_machine.py` with states:
- `pending` - Run created but not started
- `running` - Run in progress
- `succeeded` - Run completed successfully
- `failed` - Run failed
- `quarantined` - Run isolated due to errors
- `canceled` - Run canceled by user

### Step 4: Build orchestrator
Create `core/engine/orchestrator.py` with:
- `create_run(workstream_spec)` - Initialize new run
- `start_run(run_id)` - Begin execution
- `execute_step(run_id, step_id)` - Execute single step
- `complete_run(run_id, status)` - Finalize run

### Step 5: Write tests
Create comprehensive tests covering:
- State transitions
- CRUD operations
- Event emission
- Error handling

---

## Phase 3 Success Criteria

**By end of Phase 3, the framework must:**
- ✅ Execute complete workstreams autonomously
- ✅ Persist run state to database
- ✅ Route tasks to appropriate tools
- ✅ Handle parallel and sequential execution
- ✅ Retry failed tasks with backoff
- ✅ Quarantine problematic runs
- ✅ Generate progress reports
- ✅ Support circuit breakers for failing tools

---

## Estimated Timeline

| Week | Workstreams | Deliverables |
|------|-------------|--------------|
| Week 1 | WS-03-01A | Run management, database, state machine |
| Week 2 | WS-03-01B, WS-03-01C | Task routing, scheduling |
| Week 3 | WS-03-02A, WS-03-03A | Tool adapters, circuit breakers |

---

## Current Status

**Framework Progress:** 55% → 70% (projected after Phase 3)  
**Next Action:** Begin WS-03-01A (Run Management)  
**Blocking Issues:** None - ready to proceed  

---

## Notes

- Phase 2 provides the bootstrap foundation ✅
- Schemas define all data structures ✅
- Focus on minimal viable implementation first
- Add advanced features (parallel execution, retries) incrementally
- Keep tests comprehensive from the start

**Ready to begin!** 🚀
