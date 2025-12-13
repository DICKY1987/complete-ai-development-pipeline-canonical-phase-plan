 MINI_PIPE + Canonical System Integration Plan

 Executive Summary

 This plan integrates MINI_PIPE (mature execution engine, ~23K LOC)
 into the Canonical System (SSOT state machine framework, ~7.5K LOC)
 via monorepo merge following a "Canonical as Authority, MINI_PIPE as
 Engine" model:

 - Canonical System owns: State definitions, database schema,
 persistence layer, formal contracts
 - MINI_PIPE provides: Execution logic, tool routing, AI integration,
 resilience patterns

 Integration Approach:
 1. Monorepo Merge: Consolidate both codebases into the Canonical
 repository
 2. Bridge Adapter Layer: Create CanonicalBridge module to adapt
 MINI_PIPE execution to Canonical state machines
 3. Full Integration: Implement state validation, persistence, and
 event unification systematically

 ---
 Codebase Comparison Table

 | Dimension   | MINI_PIPE                           | Canonical System
                                                               |
 |-------------|-------------------------------------|-----------------
 --------------------------------------------------------------|
 | Location    | C:\Users\richg\ALL_AI\MINI_PIPE     |
 C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical
 Phase Plan |
 | Purpose     | Autonomous code modification engine | SSOT state
 machine orchestration framework                                    |
 | Total LOC   | ~23,000                             | ~7,500
                                                               |
 | Maturity    | Production-ready execution          | Phases 1-3
 complete, 4-7 designed                                             |
 | State Mgmt  | Internal tracking                   | Formal state
 machines with validation                                         |
 | Persistence | File-based JSON                     | SQLite with DAO
 layer                                                         |
 | Entry Point | MINI_PIPE_src/acms/controller.py    |
 phase2_implementation/core/state/*.py
         |

 ---
 Overlap Analysis

 | Component       | MINI_PIPE                           | Canonical
                | Resolution                                  |
 |-----------------|-------------------------------------|-------------
 ---------------|---------------------------------------------|
 | Orchestrator    | minipipe/orchestrator.py (700 LOC)  |
 RunOrchestrator (stub)     | Keep MINI_PIPE, adapt to Canonical states
    |
 | Scheduler       | minipipe/scheduler.py (296 LOC)     |
 TaskScheduler (stub)       | Keep MINI_PIPE, use Canonical TaskDAO
    |
 | Worker Pool     | workstream_worker_pool.py (480 LOC) |
 WorkerPoolManager (stub)   | Keep MINI_PIPE, align states
    |
 | Patch Ledger    | patch_ledger.py (795 LOC)           |
 PatchLedgerStateMachine    | Merge: MINI_PIPE logic + Canonical states
    |
 | Circuit Breaker | circuit_breakers.py (190 LOC)       |
 CircuitBreakerStateMachine | Merge: MINI_PIPE config + Canonical
 machine |
 | Run States      | Internal (SUCCESS/FAILED)           | Formal
 (succeeded/failed)  | Canonical wins - align naming               |
 | Event System    | Internal EventBus                   | EventEmitter
  + JSONL       | Canonical wins - unified audit              |

 ---
 Modular Responsibility Map

 ┌─────────────────────────────────────────────────────────────────┐
 │                    ACMS CONTROLLER (MINI_PIPE)                  │
 │  Owner: MINI_PIPE | File: acms/controller.py                    │
 │  Role: Top-level pipeline orchestration (6-phase)               │
 └────────────────────────────┬────────────────────────────────────┘
                              │
 ┌────────────────────────────▼────────────────────────────────────┐
 │                  CANONICAL BRIDGE (NEW)                         │
 │  Owner: Integration | File: minipipe/canonical_bridge.py        │
 │  Role: Adapts MINI_PIPE calls to Canonical state machines       │
 └────────────────────────────┬────────────────────────────────────┘
          │                   │                    │
 ┌────────▼────────┐  ┌───────▼───────┐  ┌────────▼────────┐
 │ EXECUTION       │  │ STATE         │  │ PERSISTENCE     │
 │ (MINI_PIPE)     │  │ (CANONICAL)   │  │ (CANONICAL)     │
 ├─────────────────┤  ├───────────────┤  ├─────────────────┤
 │ orchestrator.py │  │ run.py        │  │ run_dao.py      │
 │ scheduler.py    │  │ task.py       │  │ task_dao.py     │
 │ router.py       │  │ workstream.py │  │ workstream_dao  │
 │ executor.py     │  │ worker.py     │  │ patch_dao.py    │
 │ tools.py        │  │ patch_ledger  │  │ circuit_dao.py  │
 │ worker_pool.py  │  │ circuit_brk   │  │                 │
 └─────────────────┘  └───────────────┘  └─────────────────┘
          │                   │                    │
          └───────────────────┴────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  SQLite Database  │
                    │ (Canonical Schema)│
                    └───────────────────┘

 ---
 Integration Strategy

 Phase A: Monorepo Merge

 A.1 - Repository Consolidation
 - Copy MINI_PIPE source into Canonical repo under execution_engine/
 directory
 - Preserve MINI_PIPE's folder structure:
 Complete AI Development Pipeline – Canonical Phase Plan/
 ├── phase2_implementation/     (existing - state machines)
 ├── phase3_implementation/     (existing - DAO layer)
 ├── execution_engine/          (NEW - MINI_PIPE code)
 │   ├── acms/                  (from MINI_PIPE_src/acms/)
 │   ├── minipipe/              (from MINI_PIPE_src/minipipe/)
 │   ├── config/                (from MINI_PIPE_config/)
 │   ├── schemas/               (from MINI_PIPE_schemas/)
 │   └── tests/                 (from MINI_PIPE_tests/)
 └── ...
 - Update all import paths in MINI_PIPE code
 - Merge pyproject.toml configurations

 A.2 - Create CanonicalBridge Module
 - New File: execution_engine/minipipe/canonical_bridge.py
 - Wraps Canonical state machines and DAOs
 - Validates all state transitions before execution
 - Translates state names (SUCCESS→succeeded, FAILED→failed)

 # Interface sketch:
 class CanonicalBridge:
     def __init__(self, db_path: str): ...
     def create_run(self, run_data: Dict) -> str: ...
     def transition_task(self, task_id: str, new_state: str, reason:
 str): ...
     def persist_patch(self, patch_data: Dict) -> str: ...

 A.3 - Database Schema Extension
 - Add missing states to Canonical migrations: quarantined,
 awaiting_review, committed
 - Create migration script _009_add_minipipe_states.py

 Phase B: Core Component Adaptation

 B.1 - Adapt Orchestrator
 - File: execution_engine/minipipe/orchestrator.py
 - Import CanonicalBridge instead of internal state tracking
 - Replace SUCCESS/FAILED with succeeded/failed
 - Route all DB writes through bridge

 B.2 - Adapt Scheduler
 - File: execution_engine/minipipe/scheduler.py
 - Add states: validating, retrying, blocked, cancelled
 - Change ready → queued naming
 - Persist task state via TaskDAO

 B.3 - Adapt Executor
 - File: execution_engine/minipipe/executor.py
 - Add validating state transition after task completion
 - Emit events through Canonical EventEmitter

 Phase C: Unified Components

 C.1 - Unify Patch Ledger
 - File: execution_engine/minipipe/patch_ledger.py
 - Keep execution logic, import Canonical PatchLedgerStateMachine for
 state validation
 - Persist via PatchDAO
 - Map: created→PENDING, validated→VALIDATING, applied→APPLIED,
 verified→VERIFIED

 C.2 - Unify Circuit Breakers
 - File: execution_engine/minipipe/circuit_breakers.py
 - Keep config loading, use Canonical CircuitBreaker for runtime state
 - Persist via CircuitBreakerDAO

 C.3 - Adapt Worker Pool
 - File: execution_engine/minipipe/workstream_worker_pool.py
 - Import Canonical WorkstreamStateMachine
 - Add missing states: planned, validating
 - Persist via WorkstreamDAO

 Phase D: Testing & Validation

 D.1 - Integration Tests
 - Full ACMS cycle with Canonical persistence
 - Verify all state transitions logged to state_transitions table
 - Verify events in JSONL format

 D.2 - Performance Benchmarks
 - Compare against MINI_PIPE baselines
 - Profile DAO overhead

 ---
 Suggested Refactors

 Execution Engine (After Merge)

 | File                                          | Refactor
                               | Reason
 |
 |-----------------------------------------------|---------------------
 ------------------------------|---------------------------------------
 |
 | execution_engine/minipipe/orchestrator.py     | Replace internal
 state tracking with bridge calls | Canonical state authority
    |
 | execution_engine/minipipe/scheduler.py        | Add 4 missing task
 states                         | Align with Canonical TaskStateMachine
  |
 | execution_engine/minipipe/executor.py         | Add validating state
  handling                     | Match Canonical workflow
 |
 | execution_engine/minipipe/patch_ledger.py     | Use PatchDAO for
 persistence                      | Single data source
    |
 | execution_engine/minipipe/circuit_breakers.py | Facade over
 Canonical CB                          | Unified implementation
         |
 | All MINI_PIPE files                           | Update imports: src.
  → execution_engine.          | Monorepo path alignment
 |

 Canonical Extensions

 | File                                                 | Refactor
                      | Reason                  |
 |------------------------------------------------------|--------------
 ---------------------|-------------------------|
 | _009_add_minipipe_states.py                          | New migration
  for extended states | MINI_PIPE compatibility |
 | phase2_implementation/core/state/run.py              | Add
 quarantined state             | MINI_PIPE uses this     |
 | phase2_implementation/core/uet/state/patch_ledger.py | Add
 awaiting_review, committed    | MINI_PIPE workflow      |

 Deletions/Removals

 | File/Code                                | Action
     | Reason                     |
 |------------------------------------------|--------------------------
 ----|----------------------------|
 | Internal RunStateMachine in orchestrator | Remove import
     | Use Canonical              |
 | File-based state JSON writes             | Remove
     | Use DAO persistence        |
 | Duplicate event emission                 | Remove
     | Use Canonical EventEmitter |
 | Original MINI_PIPE repo                  | Archive after merge
 complete | Single source maintained   |

 ---
 Implementation Plan

 Step 1: Monorepo Merge (Day 1)

 Target: C:\Users\richg\ALL_AI\Complete AI Development Pipeline –
 Canonical Phase Plan\

 1. Create execution_engine/ directory
 2. Copy MINI_PIPE components:
    - MINI_PIPE_src/acms/ → execution_engine/acms/
    - MINI_PIPE_src/minipipe/ → execution_engine/minipipe/
    - MINI_PIPE_config/ → execution_engine/config/
    - MINI_PIPE_schemas/ → execution_engine/schemas/
    - MINI_PIPE_tests/ → execution_engine/tests/
 3. Update all imports in copied files (src. → execution_engine.)
 4. Merge pyproject.toml dependencies
 5. Verify existing tests still pass

 Step 2: CanonicalBridge (Day 2)

 Create: execution_engine/minipipe/canonical_bridge.py
 - Import from phase2_implementation.core.state.*
 - Import from phase3_implementation.core.dao.*
 - Implement state translation layer
 - Write unit tests

 Step 3: Orchestrator Adaptation (Day 3)

 Modify: execution_engine/minipipe/orchestrator.py
 - Import CanonicalBridge
 - Replace create_run() to use bridge
 - Replace start_run() to use bridge
 - Replace complete_run() to use bridge
 - Run existing tests

 Step 4: Scheduler Adaptation (Day 4)

 Modify: execution_engine/minipipe/scheduler.py
 - Add Task states: validating, retrying, blocked, cancelled
 - Update get_ready_tasks() → get_queued_tasks()
 - Add TaskDAO persistence calls
 - Run scheduler tests

 Step 5: Executor Adaptation (Day 5)

 Modify: execution_engine/minipipe/executor.py
 - Add validating state after execution
 - Connect to Canonical EventEmitter
 - Update result reporting
 - Run executor tests

 Step 6: Patch Ledger Unification (Day 6)

 Modify: execution_engine/minipipe/patch_ledger.py
 - Import PatchLedgerStateMachine
 - Create state mapping layer
 - Route persistence to PatchDAO
 - Maintain backward-compatible methods

 Step 7: Circuit Breaker & Worker Pool (Day 7)

 Modify: execution_engine/minipipe/circuit_breakers.py
         execution_engine/minipipe/workstream_worker_pool.py
 - Create CircuitBreakerManager facade
 - Align workstream states
 - Add missing states
 - Connect to respective DAOs

 Step 8: Integration Testing (Day 8)

 Create:
 execution_engine/tests/integration/test_canonical_integration.py
 - Full ACMS cycle tests
 - State persistence verification
 - Event audit verification
 - Rollback scenario tests

 ---
 Critical Files Reference

 Base Path: C:\Users\richg\ALL_AI\Complete AI Development Pipeline –
 Canonical Phase Plan\

 Execution Engine (MINI_PIPE - After Merge)

 - execution_engine/minipipe/orchestrator.py - Run lifecycle management
 - execution_engine/minipipe/scheduler.py - DAG task scheduling
 - execution_engine/minipipe/executor.py - Parallel task execution
 - execution_engine/minipipe/patch_ledger.py - Patch lifecycle
 - execution_engine/minipipe/circuit_breakers.py - Resilience patterns
 - execution_engine/minipipe/workstream_worker_pool.py - Worker pool
 - execution_engine/acms/controller.py - ACMS entry point

 Canonical State Machines (Authority)

 - doc_ssot_state_machines.md - SSOT specification
 - phase2_implementation/core/state/base.py - Base state machine
 - phase2_implementation/core/state/run.py - RunStateMachine
 - phase2_implementation/core/state/task.py - TaskStateMachine
 - phase2_implementation/core/state/workstream.py -
 WorkstreamStateMachine
 - phase2_implementation/core/state/circuit_breaker.py -
 CircuitBreakerStateMachine

 Canonical DAO Layer (Persistence)

 - phase3_implementation/core/dao/base.py - BaseDAO
 - phase3_implementation/core/dao/run_dao.py - RunDAO
 - phase3_implementation/core/dao/task_dao.py - TaskDAO
 - phase3_implementation/core/dao/patch_dao.py - PatchDAO

 New Files (To Create)

 - execution_engine/minipipe/canonical_bridge.py - Bridge adapter
 - phase3_implementation/core/db/migrations/_009_add_minipipe_states.py
  - Schema extension

 ---
 Risk Mitigation

 | Risk                                      | Mitigation
                         |
 |-------------------------------------------|-------------------------
 ------------------------|
 | State name mismatches during migration    | Dual-write period;
 validate both state systems  |
 | Performance degradation from DAO overhead | Batch writes; use
 transactions; benchmark early |
 | Circular imports between packages         | Use lazy imports;
 abstract interfaces           |
 | Running executions during migration       | Add feature flag for
 Canonical persistence      |
 | Test coverage gaps                        | Create state combination
  matrix tests           |

 ---
 Success Criteria

 1. All MINI_PIPE execution persists to Canonical database
 2. All state transitions validated by Canonical state machines
 3. Unified event audit trail in JSONL format
 4. Existing MINI_PIPE tests pass (95+ tests)
 5. Canonical tests pass (95+ tests)
 6. No code duplication between systems
 7. Clear ownership boundaries maintained
