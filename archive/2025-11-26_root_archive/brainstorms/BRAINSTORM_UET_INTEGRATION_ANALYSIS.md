---
doc_id: DOC-GUIDE-BRAINSTORM-UET-INTEGRATION-ANALYSIS-1136
---

# DEEP DIVE ANALYSIS: Integration Gaps Between UET Framework & Main Pipeline

## Executive Summary

You have **THREE SEPARATE EXECUTION ENGINES** that need unification:

1. **UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/** - Project-agnostic bootstrapping system
2. **core/engine/** - Workstream-based orchestrator with EDIT→STATIC→RUNTIME flow
3. **engine/** - Job-based execution engine with GUI/Terminal/TUI hybrid architecture

**Critical Finding**: These are NOT fully integrated and have overlapping but distinct architectures.

---

## 1. ARCHITECTURE COMPARISON

### UET Framework (UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/)
**Design Philosophy**: Project-agnostic orchestration for ANY codebase
**Execution Model**: Bootstrap → Profile Selection → Task Routing → Tool Execution
**State Management**: Minimal (designed to be portable)
**Core Strength**: Autonomous project discovery and configuration

**Key Components**:
- Bootstrap orchestrator (discovers project, selects profile)
- Profile system (5 domain templates)
- Task router (routes tasks to appropriate tools)
- Execution scheduler (dependency resolution, parallel batching)
- Resilient executor (circuit breakers, retries)
- Progress tracker (real-time monitoring)

**Schemas**: 17 JSON schemas for type-safe operations
**Testing**: 196/196 tests passing
**Status**: 78% complete, Phase 3 done

---

### Main Pipeline (core/engine/)
**Design Philosophy**: Workstream-based development workflow orchestration
**Execution Model**: Workstream → EDIT → STATIC → RUNTIME (with FIX loops)
**State Management**: SQLite database (.worktrees/pipeline_state.db)
**Core Strength**: Deep integration with state, worktrees, AIM, circuit breakers

**Key Components**:
- Orchestrator (workstream lifecycle)
- Scheduler (wave-based parallel execution with dependencies)
- Tools adapter (unified tool invocation interface)
- Circuit breakers (prevents infinite FIX loops)
- Recovery manager (retry strategies)
- AIM integration (capability-based routing)
- Cost tracker, metrics, event bus

**Configuration**:
- Tool profiles (config/tool_profiles.json)
- Circuit breaker config (config/circuit_breaker_config.yaml)
- Decomposition rules (config/decomposition_rules.yaml)

**Status**: Production-ready, fully integrated with state/planning/error systems

---

### Job Engine (engine/)
**Design Philosophy**: Hybrid GUI/Terminal/TUI with job-based execution
**Execution Model**: Job JSON → Adapter → Subprocess Execution → Result
**State Management**: JobStateStore (protocol-based interface)
**Core Strength**: Clean separation between GUI and execution engine

**Key Components**:
- Protocol-based interfaces (StateInterface, AdapterInterface, OrchestratorInterface)
- Job schema (schema/jobs/job.schema.json)
- Tool adapters (aider, codex, tests, git)
- Queue management
- Worker pools

**Design Pattern**: GUI never calls tools directly, only submits jobs via CLI
**Status**: Phase 1 foundation complete, pending integration with core/state/

---

## 2. CRITICAL INTEGRATION GAPS

### Gap 1: State Management Fragmentation
**Problem**:
- UET uses minimal state (designed for portability)
- core/engine uses SQLite with runs/workstreams/events/steps
- engine/ has JobStateStore interface but not integrated with core/state/db.py

**Impact**: No unified view of execution state across systems

**Solution Needed**:
`
Unified State Layer
├── core/state/db.py (workstreams, runs, worktrees)
├── engine/state_store/job_state_store.py (jobs)
└── UET state adapter (maps UET concepts → core.state)
`

---

### Gap 2: Execution Model Mismatch
**Problem**:
- UET: Bootstrap → Tasks (capability-based routing)
- core/engine: Workstreams → EDIT/STATIC/RUNTIME steps
- engine/: Jobs → Tool adapters

**Current State**:
`
UET Framework        core/engine         engine/
    Task     ───?───▶ Workstream  ───?───▶ Job
    │                    │                  │
    ├─ capability        ├─ EDIT           ├─ tool
    ├─ tool              ├─ STATIC         ├─ command
    └─ domain            └─ RUNTIME        └─ env
`

**Missing Bridge**: No translation layer between execution models

**Solution Needed**:
- UET Task → Workstream Bundle converter
- Workstream Step → Job converter
- Unified execution request format

---

### Gap 3: Tool Adapter Duplication
**Problem**: Three separate tool adapter implementations

**UET Framework**:
`python
# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/adapters/
├── base.py (BaseAdapter)
├── subprocess_adapter.py (SubprocessAdapter)
└── registry.py (AdapterRegistry)
`

**Main Pipeline**:
`python
# core/engine/
├── tools.py (run_tool, load_tool_profiles)
└── adapters/
    ├── base.py
    ├── aider_adapter.py
    ├── claude_adapter.py
    └── codex_adapter.py
`

**Job Engine**:
`python
# engine/adapters/
├── aider_adapter.py (run_aider_job)
├── codex_adapter.py (run_codex_job)
├── tests_adapter.py (run_tests_job)
└── git_adapter.py (run_git_job)
`

**Impact**: Inconsistent behavior, duplicated code, maintenance burden

**Solution Needed**: Unified adapter registry with shared base implementation

---

### Gap 4: Orchestration Logic Fragmentation
**Three separate orchestrators with different responsibilities**:

| Feature | UET | core/engine | engine/ |
|---------|-----|-------------|---------|
| Dependency resolution | ✅ (scheduler) | ✅ (scheduler) | ❌ |
| Parallel execution | ✅ (batching) | ✅ (waves) | ✅ (workers) |
| Circuit breakers | ✅ (resilience) | ✅ (circuit_breakers) | ❌ |
| Retry logic | ✅ (resilience) | ✅ (recovery_manager) | ❌ |
| Progress tracking | ✅ (progress_tracker) | ✅ (metrics) | ❌ |
| State persistence | ❌ | ✅ (SQLite) | ✅ (JobStateStore) |
| Bootstrap | ✅ | ❌ | ❌ |
| Profile selection | ✅ | ❌ | ❌ |
| AIM integration | ❌ | ✅ | ❌ |
| Cost tracking | ❌ | ✅ | ❌ |

**Problem**: No single orchestrator with all capabilities

---

### Gap 5: Schema Inconsistency
**UET Schemas** (17 schemas in UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/schema/):
- phase_spec.v1.json
- task_spec.v1.json
- execution_request.v1.json
- profile.v1.json
- etc.

**Main Pipeline Schemas** (schema/):
- workstream.schema.json
- workstream_sidecar.schema.json
- tool_profile.schema.json

**Job Engine Schemas** (schema/jobs/):
- job.schema.json
- aider_job.example.json

**Problem**: Overlapping concepts with different schemas
- UET "task" ≠ main pipeline "step" ≠ job engine "job"
- UET "profile" overlaps with main pipeline "tool_profile"
- No schema for translating between systems

---

## 3. MISSING ELEMENTS (What UET Has That Main Pipeline Lacks)

### From UET Framework:
1. **Autonomous Bootstrap** ✨
   - Project discovery and auto-configuration
   - Language/framework detection
   - Profile selection logic
   - Artifact generation

2. **Profile System** ✨
   - Domain-specific templates (Python, data, docs, ops, generic)
   - Phase templates pre-configured
   - Tool routing per profile

3. **Resilience Patterns** (partial overlap with core/engine)
   - ResilientExecutor with per-tool configuration
   - Exponential backoff
   - Circuit breaker with recovery timeout

4. **Progress Tracking** (different from core/engine metrics)
   - Task-level progress (0-100%)
   - ETA estimation
   - Real-time snapshots

5. **Execution Request Builder**
   - Converts tasks → execution requests
   - Variable substitution
   - Validation

---

## 4. MISSING ELEMENTS (What Main Pipeline Has That UET Lacks)

### From core/engine:
1. **State Persistence** ✨
   - Full SQLite database
   - Run/workstream/step tracking
   - Event history
   - Worktree management

2. **AIM Integration** ✨
   - Capability-based routing
   - Tool discovery
   - Fallback chains

3. **FIX Loop Logic** ✨
   - STATIC with FIX (linting errors → repair)
   - RUNTIME with FIX (test failures → repair)
   - Oscillation detection

4. **Compensation Actions**
   - Rollback on failure
   - Cleanup operations

5. **Cost Tracking & Budgets**
   - Token usage tracking
   - Budget enforcement
   - Model-specific pricing

6. **Event Bus**
   - Observer pattern
   - Observability hooks

7. **Worker Pools** (wave-based parallelism)
   - Conflict groups
   - Fail-fast mode

---

## 5. MISSING ELEMENTS (What Job Engine Has That Others Lack)

### From engine/:
1. **Protocol-Based Interfaces** ✨
   - Clean contracts (StateInterface, AdapterInterface)
   - Loose coupling
   - Easy mocking for tests

2. **GUI Separation** ✨
   - GUI never calls tools directly
   - All execution via orchestrator CLI
   - Clean read/write separation

3. **Job Schema**
   - Standardized job format
   - Paths configuration (repo_root, working_dir, log_file, error_report)
   - Environment variables per job

---

## 6. INTEGRATION STRATEGY (Recommended Approach)

### Option A: Merge Into Core (Recommended)
**Migrate best features from UET + engine/ → core/engine/**

`
core/
├── state/
│   ├── db.py (unified: runs + workstreams + jobs)
│   ├── bundles.py
│   └── worktree.py
├── engine/
│   ├── orchestrator.py (unified: workstreams + jobs + bootstrap)
│   ├── scheduler.py (unified: waves + batches)
│   ├── executor.py (unified: tools + adapters)
│   ├── bootstrap/ (from UET)
│   │   ├── discovery.py
│   │   ├── selector.py
│   │   └── generator.py
│   ├── profiles/ (from UET)
│   │   └── *.yaml
│   ├── resilience/ (merge UET + core patterns)
│   │   ├── circuit_breakers.py
│   │   ├── retry.py
│   │   └── recovery.py
│   ├── monitoring/
│   │   ├── progress_tracker.py (from UET)
│   │   ├── run_monitor.py (from core)
│   │   └── metrics.py
│   ├── interfaces/ (from engine/)
│   │   ├── state_interface.py
│   │   ├── adapter_interface.py
│   │   └── orchestrator_interface.py
│   └── adapters/ (unified)
│       ├── base.py
│       ├── aider_adapter.py
│       ├── codex_adapter.py
│       ├── tests_adapter.py
│       └── git_adapter.py
└── planning/
    └── planner.py
`

**Migrations**:
1. Move UET bootstrap → core/engine/bootstrap/
2. Move UET profiles → core/engine/profiles/
3. Move engine/ protocols → core/engine/interfaces/
4. Unify adapters → core/engine/adapters/
5. Unify schemas → schema/ (create translation schemas)
6. Create unified orchestrator supporting:
   - Bootstrap mode (UET)
   - Workstream mode (current)
   - Job mode (engine/)

---

### Option B: Keep Separate with Adapters
**Keep all three systems, create translation layer**

`
UET Framework ──▶ Translation Layer ──▶ core/engine ──▶ engine/ (job execution)
                        │
                        └─── Unified State (core/state/db.py)
`

**Pros**: Less refactoring, preserves existing code
**Cons**: Complexity, maintenance burden, unclear ownership

---

## 7. UNIFICATION ROADMAP (Phased Approach)

### Phase 1: Unify State (Week 1)
**Goal**: Single source of truth for execution state

**Tasks**:
- [ ] Extend core/state/db.py with job tables
- [ ] Create state adapters for UET concepts
- [ ] Implement JobStateStore using core/state/db.py
- [ ] Migrate engine/ to use core/state/

**Deliverable**: All three systems write to same database

---

### Phase 2: Unify Schemas (Week 2)
**Goal**: Consistent data contracts

**Tasks**:
- [ ] Map UET task → Workstream bundle
- [ ] Map Workstream step → Job
- [ ] Create translation schemas
- [ ] Implement converters (task_to_workstream.py, step_to_job.py)

**Deliverable**: Schema translation layer

---

### Phase 3: Unify Adapters (Week 3)
**Goal**: Single adapter registry

**Tasks**:
- [ ] Merge adapter implementations
- [ ] Create base adapter protocol (from engine/)
- [ ] Implement unified AdapterRegistry
- [ ] Update all orchestrators to use unified registry

**Deliverable**: core/engine/adapters/ with all tools

---

### Phase 4: Integrate Bootstrap (Week 4)
**Goal**: Add UET bootstrap to main pipeline

**Tasks**:
- [ ] Move UET bootstrap → core/engine/bootstrap/
- [ ] Move UET profiles → core/engine/profiles/
- [ ] Add bootstrap CLI command
- [ ] Integrate with run_workstream flow

**Deliverable**: python core/engine/orchestrator.py bootstrap /path/to/project

---

### Phase 5: Unified Orchestrator (Week 5-6)
**Goal**: Single orchestrator with multiple modes

**Tasks**:
- [ ] Create OrchestratorV2 with mode parameter
- [ ] Implement bootstrap mode (UET logic)
- [ ] Implement workstream mode (current logic)
- [ ] Implement job mode (engine/ logic)
- [ ] Add mode auto-detection

**Deliverable**: Backward-compatible unified orchestrator

---

### Phase 6: Protocol Adoption (Week 7)
**Goal**: Clean interfaces for GUI integration

**Tasks**:
- [ ] Adopt engine/ protocols (StateInterface, AdapterInterface)
- [ ] Refactor core/engine to use protocols
- [ ] Create GUI adapter layer
- [ ] Update documentation

**Deliverable**: GUI can integrate cleanly via protocols

---

## 8. BREAKING CHANGES TO ADDRESS

### Import Paths
**Current**:
`python
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.bootstrap import orchestrator
from core.engine.orchestrator import run_workstream
from engine.orchestrator import Orchestrator
`

**Unified**:
`python
from core.engine.orchestrator import UnifiedOrchestrator
from core.engine.bootstrap import bootstrap_project
from core.engine.adapters import get_adapter
`

### Configuration
**Current**:
- UET: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/profiles/
- Main: config/tool_profiles.json, config/circuit_breaker_config.yaml
- Job: schema/jobs/*.json

**Unified**:
`
config/
├── profiles/ (UET profiles)
├── tool_profiles.json (merge with UET adapter configs)
├── circuit_breaker_config.yaml
└── bootstrap_config.yaml (new)
`

---

## 9. TESTING STRATEGY

### Integration Tests Needed
1. **Bootstrap → Workstream** test
   - Bootstrap project → Generate bundles → Run workstream

2. **Workstream → Job** test
   - Execute workstream → Generate jobs → Job completion

3. **State Consistency** test
   - Write via UET → Read via core → Verify consistency

4. **Adapter Compatibility** test
   - Same tool invoked via UET, core, engine produces same result

5. **End-to-End** test
   - Bootstrap → Workstream → Job → Completion → Metrics

---

## 10. IMMEDIATE NEXT STEPS (This Week)

### Action Items (Priority Order)

1. **Decision Meeting** 🎯
   - Choose Option A (merge) or Option B (adapters)
   - Define ownership boundaries
   - Assign team members

2. **Create Unified State Schema** 📐
   - Design tables for jobs, tasks, profiles
   - Write migration script for existing data
   - Get stakeholder approval

3. **Proof of Concept** 🔬
   - Build minimal translation layer
   - Bootstrap project → Generate workstream → Execute job
   - Measure integration complexity

4. **Documentation Audit** 📝
   - Map all execution concepts (task/workstream/job)
   - Create terminology glossary
   - Update architecture diagrams

5. **Deprecation Plan** ⚠️
   - Identify which code paths to sunset
   - Create backward-compatibility shims
   - Set sunset dates

---

## 11. RISKS & MITIGATION

### Risk 1: Breaking Existing Workflows
**Mitigation**: Backward-compatible shims, phased rollout

### Risk 2: State Migration Failures
**Mitigation**: Comprehensive backups, rollback scripts

### Risk 3: Performance Degradation
**Mitigation**: Benchmark before/after, optimize hotspots

### Risk 4: Scope Creep
**Mitigation**: Strict phase boundaries, feature freeze during migration

---

## 12. SUCCESS CRITERIA

✅ **Single Database**: All execution state in core/state/db.py
✅ **Unified Adapters**: One adapter per tool (no duplication)
✅ **Backward Compatible**: Existing workstreams run unchanged
✅ **Bootstrap Working**: UET bootstrap integrated into main flow
✅ **Tests Passing**: 100% test coverage maintained
✅ **Documentation Complete**: Architecture clearly documented
✅ **Performance Maintained**: No >10% slowdown

---

## CONCLUSION

**The UET Framework is NOT missing elements—it's a PARALLEL SYSTEM with different design goals.**

**Main Issues**:
1. Three execution engines with overlapping responsibilities
2. No translation layer between execution models
3. Fragmented state management
4. Duplicated adapter implementations
5. Unclear integration path

**Recommended Path**: **Option A (Merge)** - Unify into core/engine over 7 weeks

**Quick Wins** (Do First):
1. Unify state (extend core/state/db.py)
2. Map schemas (create converters)
3. Merge adapters (single registry)

**Key Decision**: Should UET remain standalone (for portability) or fully merge into core?
