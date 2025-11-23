# UET Framework Integration Plan - Comprehensive Analysis

**Generated**: 2025-11-23  
**Evaluator**: GitHub Copilot CLI  
**Target**: 7-Week UET Integration Plan  
**Status**: ✅ APPROVED with Critical Recommendations

---

## Executive Summary

### Overall Assessment: **FEASIBLE & WELL-STRUCTURED** ⭐⭐⭐⭐½

Your UET integration plan is **architecturally sound** and demonstrates deep understanding of both systems. However, **significant foundational work already exists** in your codebase that will **accelerate** implementation while requiring **strategic alignment**.

**Key Finding**: You're **~40% complete** already. Many components exist but need UET schema alignment and patch-first refactoring.

---

## Current State vs. Plan Requirements

### ✅ Already Implemented (Existing Foundation)

| Component | Status | Location | Notes |
|-----------|--------|----------|-------|
| **Worker Lifecycle** | ✅ 80% Complete | `core/engine/worker.py` | Has SPAWNING→IDLE→BUSY→DRAINING→TERMINATED states |
| **Worker Pool** | ✅ 70% Complete | `core/engine/worker.py` | WorkerPool class exists |
| **Event Bus** | ✅ 85% Complete | `core/engine/event_bus.py` | EventType enum + 28 event types defined |
| **Integration Worker** | ✅ 60% Complete | `core/engine/integration_worker.py` | MergeConflict, MergeResult classes exist |
| **Patch Manager** | ✅ 50% Complete | `core/engine/patch_manager.py` | PatchArtifact, PatchParseResult exist |
| **Cost Tracker** | ✅ 75% Complete | `core/engine/cost_tracker.py` | CostBudget, ModelPricing, budget enforcement |
| **Test Gates** | ✅ 65% Complete | `core/engine/test_gates.py` | TestGate, GateResult, TestGateEnforcer |
| **Compensation** | ✅ 40% Complete | `core/engine/compensation.py` | CompensationEngine stub with rollback methods |
| **Circuit Breakers** | ✅ Exists | `core/engine/circuit_breakers.py` | Already in codebase |
| **Tool Adapters** | ✅ Base + 3 | `core/engine/adapters/` | base, aider, codex, claude |

### 🟡 Partial Implementation (Needs UET Alignment)

| Component | Gap | Required Work |
|-----------|-----|---------------|
| **Schemas** | Missing UET v1 schemas | Copy 17 JSON schemas from UET framework |
| **Patch Ledger** | No state machine tracking | Create `core/patches/patch_ledger.py` with full lifecycle |
| **Patch Validator** | Basic parsing only | Add format/scope/constraint validation |
| **Database** | No ULID, no patches table | Migration script + schema update |
| **Adapters** | Direct file edits | Refactor to patch-first (unified diff output) |
| **Context Manager** | Estimator exists | Add pruning/summarization/chunking |
| **Human Review** | Manual | Structured escalation workflow needed |

### ❌ Not Implemented (Greenfield)

| Component | Priority | Effort Estimate |
|-----------|----------|-----------------|
| **Patch Artifact (UET)** | HIGH | 8 hours (wrap existing PatchArtifact) |
| **Patch Ledger System** | HIGH | 16 hours (state machine + DB integration) |
| **Patch Policy Engine** | MEDIUM | 12 hours (constraint validation) |
| **DAG Scheduler** | MEDIUM | 12 hours (replace current scheduler) |
| **Merge Orchestration** | MEDIUM | 10 hours (deterministic merge strategy) |
| **Feedback Loop** | LOW | 8 hours (test-driven task creation) |
| **Security Isolation** | LOW | 16 hours (sandboxing + quotas) |

---

## Phase-by-Phase Feasibility Analysis

### ✅ Phase 1: Schema Foundation + Patch System (Week 1)

**Status**: **ACCELERATED** - Can complete in 3-4 days instead of 1 week

**Why Faster**:
- ✅ UET schemas already exist at `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/schema/` (17 files verified)
- ✅ `PatchArtifact` class exists in `core/engine/patch_manager.py`
- ✅ Database infrastructure exists at `core/state/db.py`

**Required Work**:
1. **Copy UET Schemas** (2 hours)
   ```powershell
   Copy-Item UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\schema\*.json schema\uet\ -Recurse
   ```

2. **Create Patch Ledger** (8 hours)
   - New file: `core/patches/patch_ledger.py`
   - State machine: created → validated → queued → applied → verified → committed
   - Integration with event bus

3. **Database Migration** (6 hours)
   - Add `patches` table with ULID support
   - Add `patch_ledger_entries` table
   - Add `run_events` table for event sourcing
   - Script: `scripts/migrate_db_to_uet.py`

4. **Patch Validator** (8 hours)
   - New file: `core/patches/patch_validator.py`
   - Validate format (unified diff only)
   - Validate scope (file paths, line counts)
   - Validate constraints (policy enforcement)

**Risks**: ⚠️ **MEDIUM**
- Database migration may affect existing workstreams
- Need backward compatibility for current PatchArtifact usage

**Recommendation**: Start here. This is your critical path.

---

### ✅ Phase 2: Worker Lifecycle + Event Bus (Week 2)

**Status**: **MOSTLY COMPLETE** - Can finish in 1-2 days

**Existing Implementation**:
- ✅ `core/engine/worker.py` has full WorkerState enum
- ✅ WorkerPool class exists with worker management
- ✅ Event bus at `core/engine/event_bus.py` has 28 event types including:
  - WORKER_SPAWNED, WORKER_TERMINATED
  - TASK_ASSIGNED, TASK_STARTED, TASK_PROGRESS, TASK_COMPLETED, TASK_FAILED
  - FILE_DISCOVERED, FILE_QUARANTINED, etc.

**Required Work**:
1. **Worker Health Checks** (4 hours)
   - New file: `core/engine/worker_health.py`
   - Heartbeat monitoring
   - Quarantine unhealthy workers

2. **Event Persistence** (4 hours)
   - Store events in `run_events` table
   - Event replay for debugging
   - Event subscribers for orchestrator

3. **Missing Event Types** (2 hours)
   - Add: WORKER_IDLE, WORKER_BUSY, WORKER_DRAINING
   - Add: PATCH_CREATED, PATCH_APPLIED, PATCH_QUARANTINED

**Risks**: ✅ **LOW**
- Workers already functional
- Event bus already integrated

**Recommendation**: Quick win. Do this second.

---

### 🟡 Phase 3: Parallelism Strategy + Integration Worker (Week 3)

**Status**: **PARTIAL** - Needs strategic refactoring

**Existing Implementation**:
- ✅ `core/engine/integration_worker.py` has MergeConflict and MergeResult
- ✅ `core/engine/scheduler.py` exists (current implementation)
- ⚠️ Current scheduler is NOT DAG-based

**Required Work**:
1. **DAG Scheduler** (12 hours) ⚠️ **CRITICAL CHANGE**
   - Replace `core/engine/scheduler.py` with UET's DAG version
   - Parse task dependencies from workstream specs
   - Topological sort for execution order
   - Parallel execution of independent tasks

2. **Merge Orchestration** (10 hours)
   - New file: `core/engine/merge_strategy.py`
   - Deterministic merge order (priority/dependency/age)
   - Conflict detection → E_MERGE_CONFLICT event
   - Rollback on merge failure

3. **Context Manager** (8 hours)
   - New file: `core/engine/context_manager.py`
   - Token estimation (exists as `context_estimator.py`, needs expansion)
   - Pruning strategy (remove less relevant sections)
   - Summarization (compact summaries for large context)
   - Chunking (split large tasks)

**Risks**: ⚠️ **HIGH**
- DAG scheduler is **architectural change**
- Existing workstreams may not have explicit dependencies
- Need migration path for current scheduler

**Recommendation**: 
- Start with context manager (low risk, high value)
- Implement DAG scheduler in parallel branch
- A/B test before full migration

---

### ✅ Phase 4: Test Gates + Feedback Loops (Week 4)

**Status**: **MOSTLY DONE** - Needs feedback loop only

**Existing Implementation**:
- ✅ `core/engine/test_gates.py` has TestGate, GateResult, TestGateEnforcer
- ✅ Gate types: static, runtime, custom
- ✅ Blocking and wave_boundary support

**Required Work**:
1. **Enhance Gate System** (4 hours)
   - Add predefined gates: GATE_LINT, GATE_UNIT, GATE_INTEGRATION, GATE_SECURITY
   - Gate dependency graph (UNIT blocks INTEGRATION)

2. **Feedback Loop** (8 hours)
   - New file: `core/engine/feedback_loop.py`
   - Auto-create fix tasks on test failures
   - Prioritize based on failure impact
   - Block dependent tasks until fixed

3. **Gate Integration** (4 hours)
   - Event emission: GATE_PASSED, GATE_FAILED, GATE_BLOCKED
   - Store gate results in DB for audit

**Risks**: ✅ **LOW**
- TestGateEnforcer already functional
- Just needs integration points

**Recommendation**: Low-hanging fruit. Quick implementation.

---

### 🟡 Phase 5: Adapters + Patch-First Workflow (Week 5)

**Status**: **REQUIRES BREAKING CHANGES** ⚠️

**Existing Adapters**:
- ✅ `core/engine/adapters/base.py` - ToolAdapter abstract class
- ✅ `core/engine/adapters/aider_adapter.py` - Aider integration
- ✅ `core/engine/adapters/codex_adapter.py` - Codex integration
- ✅ `core/engine/adapters/claude_adapter.py` - Claude integration

**Current Behavior**: Direct file edits (NOT patch-first)

**Required Refactoring** (16 hours): ⚠️ **BREAKING CHANGE**

1. **Aider Adapter** - Output unified diff instead of committing
   ```python
   # OLD: aider --yes --auto-commits
   # NEW: aider --yes --no-auto-commits --output-diff
   ```

2. **Codex/Claude Adapters** - Capture tool output as patch
   - Parse tool edits into unified diff format
   - Create PatchArtifact from diff
   - Return patch instead of applying directly

3. **New Workflow**:
   ```
   Tool → Generate Patch → Validate → Apply → Test → Commit
   (NOT: Tool → Direct Edit → Test → Commit)
   ```

4. **Task Mode Support** (8 hours)
   - `mode: "prompt"` - Tool generates patch
   - `mode: "patch_review"` - Tool reviews existing patch (no edits)
   - `mode: "patch_apply_validate"` - Apply patch + run tests

**Risks**: ⚠️ **VERY HIGH**
- **BREAKING CHANGE** to all adapters
- Existing workstreams expect direct edits
- Need dual-mode support during migration
- Testing burden is significant

**Recommendation**: 
- Implement in feature branch
- Add `patch_mode: true/false` to adapter config
- Gradual migration workstream-by-workstream
- **PRIORITY**: Do this AFTER Phase 1-4 are stable

---

### 🟡 Phase 6: Human Review + Rollback/Compensation (Week 6)

**Status**: **STUB IMPLEMENTATION**

**Existing**:
- ✅ `core/engine/compensation.py` has CompensationEngine stub
- ❌ No structured human review workflow

**Required Work**:

1. **Human Review Workflow** (12 hours)
   - New file: `core/engine/human_review.py`
   - HUMAN_REVIEW task type
   - Escalation triggers:
     - Gate failure after N retries
     - Merge conflict detected
     - Patch quarantined
     - Budget threshold exceeded
   - Structured feedback: approve / reject / adjust

2. **Compensation Engine** (12 hours)
   - Expand `core/engine/compensation.py`
   - Saga pattern implementation:
     - forward_actions (what phase did)
     - compensation_actions (how to undo)
   - Rollback scopes:
     - Single patch (git revert)
     - Single task (undo step)
     - Single phase (compensation cascade)
     - Multi-phase (full rollback)

3. **Checkpoint System** (8 hours)
   - Git tag at phase boundaries
   - Worktree snapshots
   - Database backups
   - Fast restore from checkpoint

**Risks**: ⚠️ **MEDIUM**
- Human review breaks automation flow
- Compensation may be complex for some phases (e.g., database changes)
- Git history pollution if overused

**Recommendation**:
- Start with patch rollback (simpler)
- Add phase rollback later
- Human review should be **exception handling**, not normal flow

---

### ✅ Phase 7: Cost Tracking + Security (Week 7)

**Status**: **COST DONE, SECURITY GREENFIELD**

**Existing**:
- ✅ `core/engine/cost_tracker.py` fully implemented
- ✅ CostBudget with warning_threshold and enforcement_mode
- ✅ ModelPricing table for GPT-4, GPT-3.5, Claude models
- ❌ No security isolation

**Required Work**:

1. **Enhance Cost Tracking** (4 hours)
   - Per-phase budget tracking
   - Budget policies:
     - max_cost_total
     - max_cost_per_phase
     - max_cost_per_task
   - Actions on budget approach:
     - Reduce parallelism (fewer workers)
     - Pause non-critical tasks
     - Require human approval

2. **Security & Isolation** (16 hours) ⚠️ **COMPLEX**
   - Process sandboxing:
     - Windows: AppContainer or Job Objects
     - Limited file system access
   - Resource quotas:
     - CPU limits (Job Objects)
     - Memory limits (Job Objects)
     - Disk quotas (NTFS quotas)
   - Credential management:
     - Least-privilege tokens
     - Secrets in environment only (not args)
   - Malicious code detection:
     - Static analysis before execution
     - Suspicious pattern detection (eval, exec, system calls)

**Risks**: ⚠️ **HIGH** (Security only)
- Windows sandboxing is complex
- May break existing adapters expecting full privileges
- Performance overhead

**Recommendation**:
- Cost tracking: Ready to use NOW
- Security: Optional enhancement, not MVP requirement
- Consider containerization (Docker) for true isolation

---

## Critical Architectural Concerns

### 🔴 CONCERN #1: Patch-First Workflow is a **Breaking Change**

**Impact**: HIGH  
**Affected Systems**: All adapters, all workstreams, orchestrator

**Current Flow**:
```
Workstream → Orchestrator → Adapter → Tool (edits files directly) → Git commit
```

**UET Flow**:
```
Workstream → Orchestrator → Adapter → Tool (outputs patch) → Patch Ledger → Validate → Apply → Test → Commit
```

**Migration Strategy**:
1. Add `patch_mode: boolean` to PROJECT_PROFILE.yaml
2. Implement dual-mode adapters (support both flows)
3. Migrate one workstream type at a time:
   - Start: Documentation workstreams (low risk)
   - Then: Simple code workstreams (single file edits)
   - Last: Complex refactorings (multi-file, renames)
4. Deprecate direct-edit mode after 3 months

**Timeline**: Add 2-3 weeks for migration testing

---

### 🔴 CONCERN #2: DAG Scheduler Replaces Existing Scheduler

**Impact**: HIGH  
**Affected Systems**: Core orchestration logic

**Current Scheduler**: `core/engine/scheduler.py` (sequential or simple parallel)  
**UET Scheduler**: DAG-based with dependency resolution

**Risk**: Existing workstreams may not have explicit dependencies defined

**Migration Strategy**:
1. Analyze current workstream JSONs for implicit dependencies
2. Add `dependencies: []` field to task schema
3. Default: If no dependencies, assume sequential (preserve current behavior)
4. Gradual opt-in: Workstreams declare `parallel: true` to use DAG

**Timeline**: Add 1 week for dependency analysis + migration

---

### 🟡 CONCERN #3: ULID vs. Current ID System

**Impact**: MEDIUM  
**Affected Systems**: Database, all ID references

**Current**: Mix of auto-increment integers and custom IDs  
**UET**: ULID (26-character Base32, sortable, globally unique)

**Migration Strategy**:
1. Add ULID columns alongside existing IDs
2. Populate ULIDs for existing records
3. Update code to use ULIDs for new records
4. Dual-key support during transition
5. Drop old ID columns after validation

**Timeline**: 1 week for migration script + testing

---

### 🟢 CONCERN #4: Windows PowerShell Compatibility

**Impact**: LOW  
**Affected Systems**: Adapters, worker spawning

**Good News**: Your codebase is already Windows-first!
- ✅ Scripts use `.ps1` extension
- ✅ Path handling uses Windows backslashes
- ✅ `AGENTS.md` specifies PowerShell preference

**Validation Needed**:
- PSScriptAnalyzer for PowerShell linting
- Pester for PowerShell testing

**Recommendation**: Add to Phase 4 test gates

---

## Revised Timeline & Effort

### Original Estimate: 7 weeks, 50-60 hours

### **Realistic Estimate**: 9-10 weeks, 75-90 hours

| Phase | Original | Revised | Reason |
|-------|----------|---------|--------|
| 1: Schema + Patch | 1 week | **3-4 days** | Foundation already exists |
| 2: Worker + Events | 1 week | **1-2 days** | 85% complete |
| 3: DAG + Integration | 1 week | **2 weeks** | DAG is complex, needs migration |
| 4: Gates + Feedback | 1 week | **3-4 days** | Gates done, just feedback needed |
| 5: Adapters (Patch) | 1 week | **2-3 weeks** | Breaking change, needs dual-mode |
| 6: Review + Rollback | 1 week | **1.5 weeks** | Compensation is complex |
| 7: Cost + Security | 1 week | **1 week** | Cost done, security optional |
| **Migration & Testing** | - | **+2 weeks** | Integration testing, backward compat |

**Total**: 9-10 weeks for full UET alignment

**Fast Track** (MVP without security): 7-8 weeks

---

## Recommended Implementation Order

### 🚀 Phase A: Quick Wins (Week 1-2)

**Goal**: Immediate value, low risk

1. ✅ Copy UET schemas (2 hours)
2. ✅ Worker health checks (4 hours)
3. ✅ Event persistence (4 hours)
4. ✅ Feedback loop (8 hours)
5. ✅ Context manager enhancements (8 hours)

**Value**: Better monitoring, test-driven execution, context management

---

### 🎯 Phase B: Patch System (Week 3-4)

**Goal**: Core patch infrastructure

1. ✅ Database migration (ULID + patches table) (6 hours)
2. ✅ Patch ledger system (16 hours)
3. ✅ Patch validator (8 hours)
4. ✅ Patch policy engine (12 hours)

**Value**: Full patch lifecycle tracking, validation, quarantine

---

### ⚙️ Phase C: Orchestration (Week 5-6)

**Goal**: Parallelism and coordination

1. ✅ DAG scheduler (12 hours)
2. ✅ Merge orchestration (10 hours)
3. ✅ Integration worker enhancements (8 hours)
4. ✅ Test gate integration (4 hours)

**Value**: True parallel execution, deterministic merges

---

### 🔄 Phase D: Patch-First Adapters (Week 7-9)

**Goal**: Adapter refactoring (BREAKING CHANGE)

1. ⚠️ Dual-mode adapter support (8 hours)
2. ⚠️ Aider adapter patch-first (6 hours)
3. ⚠️ Codex adapter patch-first (6 hours)
4. ⚠️ Claude adapter patch-first (6 hours)
5. ⚠️ Migration testing (16 hours)

**Value**: Patch-first workflow, full audit trail

---

### 🛡️ Phase E: Resilience (Week 10)

**Goal**: Rollback and human review

1. ✅ Compensation engine (12 hours)
2. ✅ Checkpoint system (8 hours)
3. ✅ Human review workflow (12 hours)

**Value**: Recovery from failures, human oversight

---

## Success Metrics

### Must-Have (MVP)

- ✅ All 17 UET schemas in `schema/uet/`
- ✅ Patch ledger with full state machine
- ✅ Event bus with persistence
- ✅ Worker lifecycle management
- ✅ Cost tracking with budget enforcement
- ✅ Test gates enforced
- ✅ Compensation/rollback for patches

### Should-Have (Full UET Alignment)

- ✅ DAG scheduler
- ✅ Patch-first adapters (all tools)
- ✅ Integration worker with merge orchestration
- ✅ Context management (pruning/summarization)
- ✅ Human review workflow
- ✅ Feedback loop (test-driven task creation)

### Nice-to-Have (Future)

- ⚠️ Security isolation (sandboxing)
- ⚠️ Resource quotas
- ⚠️ Malicious code detection
- ⚠️ Multi-project orchestration

---

## Risk Mitigation Strategies

### Risk: Adapter Refactoring Breaks Existing Workstreams

**Mitigation**:
1. Feature flag: `patch_mode: true/false` in config
2. Dual-mode support for 3 months
3. Workstream-by-workstream migration
4. Comprehensive regression testing
5. Rollback plan: Keep old adapters in `core/engine/adapters/legacy/`

---

### Risk: DAG Scheduler Changes Execution Order

**Mitigation**:
1. Analyze existing workstreams for implicit dependencies
2. Default to sequential if no dependencies specified
3. Opt-in flag: `parallel_strategy: "dag"` vs `"sequential"`
4. Shadow mode: Run both schedulers, compare results
5. Gradual rollout by workstream complexity

---

### Risk: Database Migration Causes Data Loss

**Mitigation**:
1. **Backup before migration**: `cp .worktrees/pipeline_state.db .worktrees/pipeline_state.db.backup`
2. Idempotent migration script (can re-run safely)
3. Dual-key support (old IDs + ULIDs coexist)
4. Validation queries after migration
5. Rollback script: `scripts/rollback_db_migration.py`

---

### Risk: ULID Migration Breaks ID References

**Mitigation**:
1. Add ULID columns, keep existing ID columns
2. Update code to accept both ID types
3. Populate ULIDs for all existing records
4. Transition period: 1 month of dual support
5. Drop old IDs only after full validation

---

## Critical Path Items

### Blockers (Must Complete Before Others)

1. **UET Schema Copy** → Blocks: All schema-dependent work
2. **Database Migration** → Blocks: Patch ledger, event persistence
3. **Patch Ledger** → Blocks: Patch-first adapters
4. **DAG Scheduler** → Blocks: True parallelism

### Enablers (Unlock Multiple Workstreams)

1. **Event Persistence** → Enables: Replay, debugging, audit
2. **Worker Health** → Enables: Quarantine, resilience
3. **Context Manager** → Enables: Large task handling
4. **Compensation Engine** → Enables: Rollback, human review

---

## Validation Checklist

After each phase, verify:

### Phase 1: Schema + Patch
- [ ] All 17 UET schemas copied to `schema/uet/`
- [ ] `patches` table exists in database
- [ ] `patch_ledger_entries` table exists
- [ ] PatchLedger state machine transitions work
- [ ] Patch validation catches invalid diffs
- [ ] ULIDs generated for new records

### Phase 2: Worker + Events
- [ ] Worker states transition correctly
- [ ] Events persisted to `run_events` table
- [ ] Worker health checks detect failures
- [ ] Unhealthy workers quarantined
- [ ] Event replay works for debugging

### Phase 3: DAG + Integration
- [ ] DAG scheduler respects task dependencies
- [ ] Parallel tasks execute concurrently
- [ ] Integration worker detects merge conflicts
- [ ] Deterministic merge order enforced
- [ ] Context manager estimates token usage

### Phase 4: Gates + Feedback
- [ ] GATE_LINT, GATE_UNIT, GATE_INTEGRATION enforced
- [ ] Failed gates block dependent tasks
- [ ] Feedback loop creates fix tasks
- [ ] Gate results stored in database

### Phase 5: Adapters (Patch-First)
- [ ] Aider outputs unified diff (not direct edits)
- [ ] Codex outputs unified diff
- [ ] Claude outputs unified diff
- [ ] Task modes work: prompt, patch_review, patch_apply_validate
- [ ] Existing workstreams still execute (dual-mode)

### Phase 6: Review + Rollback
- [ ] Human review tasks created on escalation
- [ ] Compensation actions defined per phase
- [ ] Patch rollback works (git revert)
- [ ] Phase rollback works (compensation cascade)
- [ ] Checkpoint restore works

### Phase 7: Cost + Security
- [ ] Budget enforcement halts execution at limit
- [ ] Per-phase cost tracking accurate
- [ ] Warning at 80% budget threshold
- [ ] (Optional) Worker sandboxing enabled
- [ ] (Optional) Resource quotas enforced

---

## Files to Create (Comprehensive List)

### Patch Management (`core/patches/`)
```
core/patches/
├── __init__.py
├── patch_artifact.py       # Wrap existing PatchArtifact with UET schema
├── patch_ledger.py         # State machine + lifecycle tracking
├── patch_validator.py      # Format/scope/constraint validation
├── patch_applier.py        # Apply with rollback support
└── patch_policy.py         # Policy enforcement engine
```

### Worker Management (Enhance Existing)
```
core/engine/
├── worker_health.py        # NEW: Health checks + heartbeat
├── worker.py               # ENHANCE: Add health check integration
└── worker_pool.py          # ENHANCE: Health-based worker management
```

### Orchestration (Enhance/Replace)
```
core/engine/
├── scheduler_dag.py        # NEW: DAG-based scheduler
├── scheduler.py            # DEPRECATE or keep as fallback
├── merge_strategy.py       # NEW: Deterministic merge orchestration
├── context_manager.py      # NEW: Token tracking + pruning/chunking
└── integration_worker.py   # ENHANCE: Add merge orchestration
```

### Gates & Feedback (Enhance Existing)
```
core/engine/
├── test_gates.py           # ENHANCE: Add predefined gates
├── feedback_loop.py        # NEW: Test-driven task creation
└── gates.py                # NEW: Gate dependency graph
```

### Compensation & Review
```
core/engine/
├── compensation.py         # ENHANCE: Full Saga pattern
├── human_review.py         # NEW: Structured escalation
└── checkpoint.py           # NEW: Git tags + snapshots
```

### Adapters (Refactor to Patch-First)
```
core/engine/adapters/
├── base.py                 # ENHANCE: Add patch_mode support
├── aider_adapter.py        # REFACTOR: Output unified diff
├── codex_adapter.py        # REFACTOR: Output unified diff
└── claude_adapter.py       # REFACTOR: Output unified diff
```

### Database
```
schema/
├── uet/                    # NEW: Copy all UET schemas here
│   ├── patch_artifact.v1.json
│   ├── patch_ledger_entry.v1.json
│   ├── patch_policy.v1.json
│   └── [14 other UET schemas]
└── migrations/
    └── 001_uet_alignment.sql   # NEW: ULID + patches + events tables

scripts/
├── migrate_db_to_uet.py    # NEW: Database migration script
└── rollback_db_migration.py # NEW: Rollback script
```

### Configuration
```
config/
├── patch_policies/         # NEW: Patch policy definitions
│   ├── global.json
│   ├── python_strict.json
│   └── docs_permissive.json
└── router_config.json      # ENHANCE: Add patch-first routing
```

---

## Schema Integration Details

### UET Schemas to Copy (All 17)

From `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/schema/`:

**Core Execution** (6):
1. `phase_spec.v1.json` - Phase definitions
2. `workstream_spec.v1.json` - Workstream bundles
3. `task_spec.v1.json` - Task definitions
4. `execution_request.v1.json` - Tool routing
5. `run_record.v1.json` - Run state
6. `step_attempt.v1.json` - Execution attempts

**Patch System** (3):
7. `patch_artifact.v1.json` ⭐ Critical
8. `patch_ledger_entry.v1.json` ⭐ Critical
9. `patch_policy.v1.json` ⭐ Critical

**Events & Config** (4):
10. `run_event.v1.json` - Event sourcing
11. `router_config.v1.json` - Tool routing rules
12. `prompt_instance.v1.json` - Prompt templates
13. `profile_extension.v1.json` - Profile configs

**Bootstrap & Meta** (4):
14. `project_profile.v1.json` - Project config
15. `bootstrap_discovery.v1.json` - Bootstrap phase
16. `bootstrap_report.v1.json` - Bootstrap output
17. `doc-meta.v1.json` - Document metadata

---

## Database Schema Changes

### New Tables

```sql
-- Patches table
CREATE TABLE patches (
    patch_id TEXT PRIMARY KEY,  -- ULID
    format TEXT NOT NULL,       -- 'unified_diff'
    target_repo TEXT NOT NULL,
    base_ref TEXT,
    base_commit TEXT,
    execution_request_id TEXT,  -- ULID
    tool_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    diff_text TEXT NOT NULL,
    summary TEXT,
    files_touched TEXT,         -- JSON array
    line_insertions INTEGER DEFAULT 0,
    line_deletions INTEGER DEFAULT 0,
    hunks INTEGER DEFAULT 0
);

-- Patch ledger entries
CREATE TABLE patch_ledger_entries (
    ledger_id TEXT PRIMARY KEY,         -- ULID
    patch_id TEXT NOT NULL,             -- FK to patches
    project_id TEXT NOT NULL,
    phase_id TEXT,
    workstream_id TEXT,
    execution_request_id TEXT,          -- ULID
    state TEXT NOT NULL,                -- created, validated, applied, etc.
    state_history TEXT,                 -- JSON array
    validation_format_ok INTEGER DEFAULT 0,
    validation_scope_ok INTEGER DEFAULT 0,
    validation_constraints_ok INTEGER DEFAULT 0,
    validation_tests_ran INTEGER DEFAULT 0,
    validation_tests_passed INTEGER DEFAULT 0,
    validation_errors TEXT,             -- JSON array
    apply_attempts INTEGER DEFAULT 0,
    apply_last_attempt_at TEXT,
    apply_last_error_code TEXT,
    apply_last_error_message TEXT,
    apply_workspace_path TEXT,
    apply_applied_files TEXT,           -- JSON array
    quarantine_is_quarantined INTEGER DEFAULT 0,
    quarantine_reason TEXT,
    quarantine_path TEXT,
    quarantine_at TEXT,
    relations_replaces_patch_id TEXT,
    relations_rollback_of_patch_id TEXT,
    relations_chain_id TEXT,
    FOREIGN KEY (patch_id) REFERENCES patches(patch_id)
);

-- Run events (event sourcing)
CREATE TABLE run_events (
    event_id TEXT PRIMARY KEY,          -- ULID
    run_id TEXT NOT NULL,
    event_type TEXT NOT NULL,           -- EventType enum value
    timestamp TEXT NOT NULL,
    payload TEXT,                       -- JSON
    source TEXT,                        -- worker_id, task_id, etc.
    FOREIGN KEY (run_id) REFERENCES runs(run_id)
);

-- Migration: Add ULIDs to existing tables
ALTER TABLE runs ADD COLUMN run_ulid TEXT;
ALTER TABLE workstreams ADD COLUMN workstream_ulid TEXT;
ALTER TABLE attempts ADD COLUMN attempt_ulid TEXT;
```

### Migration Script (`scripts/migrate_db_to_uet.py`)

```python
import sqlite3
from pathlib import Path
from ulid import ULID  # pip install python-ulid

def migrate_db_to_uet(db_path: str = ".worktrees/pipeline_state.db"):
    """Migrate database to UET schema."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Create new tables
    cursor.executescript(Path("schema/migrations/001_uet_alignment.sql").read_text())
    
    # 2. Add ULID columns to existing tables
    cursor.execute("ALTER TABLE runs ADD COLUMN run_ulid TEXT")
    cursor.execute("ALTER TABLE workstreams ADD COLUMN workstream_ulid TEXT")
    cursor.execute("ALTER TABLE attempts ADD COLUMN attempt_ulid TEXT")
    
    # 3. Populate ULIDs for existing records
    cursor.execute("SELECT run_id FROM runs WHERE run_ulid IS NULL")
    for (run_id,) in cursor.fetchall():
        ulid = str(ULID())
        cursor.execute("UPDATE runs SET run_ulid = ? WHERE run_id = ?", (ulid, run_id))
    
    # Repeat for workstreams, attempts, etc.
    
    conn.commit()
    conn.close()
    print("✅ Database migrated to UET schema")

if __name__ == "__main__":
    migrate_db_to_uet()
```

---

## Adapter Refactoring Example

### Before (Direct Edit):

```python
# core/engine/adapters/aider_adapter.py (CURRENT)
def build_command(self, task: Dict[str, Any], prompt_file: Optional[Path] = None) -> List[str]:
    command = ['aider', '--yes']  # Auto-commits enabled
    # ... add files, prompt
    return command
```

### After (Patch-First):

```python
# core/engine/adapters/aider_adapter.py (UET-ALIGNED)
def build_command(self, task: Dict[str, Any], prompt_file: Optional[Path] = None) -> List[str]:
    mode = task.get('mode', 'prompt')
    patch_mode = self.config.get('patch_mode', True)  # NEW: Feature flag
    
    if mode == 'prompt':
        command = ['aider', '--no-auto-commits', '--yes']  # Changed!
        if patch_mode:
            command.append('--output-diff')  # Output unified diff
        # ... add files, prompt
        return command
    
    elif mode == 'patch_apply_validate':
        # Apply existing patch
        patch_file = task['payload']['patch_file']
        return ['git', 'apply', str(patch_file)]
    
    elif mode == 'patch_review':
        # Review patch without editing
        patch_file = task['payload']['patch_file']
        return ['aider', '--review-only', '--message-file', str(prompt_file)]
    
    else:
        raise ValueError(f"Unsupported mode: {mode}")

def execute(self, command: List[str], cwd: str, timeout: int = 600) -> ExecutionResult:
    result = self._run_subprocess(command, cwd, timeout)
    
    # NEW: Extract patch from stdout if patch_mode enabled
    if self.config.get('patch_mode', True) and '--output-diff' in command:
        result.artifacts['patch'] = self._extract_patch(result.stdout)
    
    return result

def _extract_patch(self, stdout: str) -> Optional[str]:
    """Extract unified diff from tool output."""
    # Parse stdout for diff section
    if 'diff --git' in stdout:
        lines = stdout.split('\n')
        diff_start = next(i for i, line in enumerate(lines) if line.startswith('diff --git'))
        return '\n'.join(lines[diff_start:])
    return None
```

---

## Testing Strategy

### Unit Tests (Per Component)

```python
# tests/patches/test_patch_ledger.py
def test_patch_state_machine():
    ledger = PatchLedger()
    patch_id = "01HXF..."
    
    # created → validated
    ledger.transition(patch_id, 'validated')
    assert ledger.get_state(patch_id) == 'validated'
    
    # validated → applied
    ledger.transition(patch_id, 'applied')
    assert ledger.get_state(patch_id) == 'applied'
    
    # Invalid transition should fail
    with pytest.raises(InvalidTransitionError):
        ledger.transition(patch_id, 'created')  # Can't go back

def test_patch_validation():
    validator = PatchValidator()
    
    # Valid patch
    patch = """
    diff --git a/file.py b/file.py
    --- a/file.py
    +++ b/file.py
    @@ -1,3 +1,4 @@
    +# New line
     def foo():
         pass
    """
    result = validator.validate(patch)
    assert result.format_ok == True
    assert result.scope_ok == True
    
    # Invalid: too many lines changed
    policy = PatchPolicy(max_lines_changed=5)
    large_patch = "..." # 100 lines
    result = validator.validate(large_patch, policy)
    assert result.constraints_ok == False
```

### Integration Tests (End-to-End)

```python
# tests/integration/test_patch_workflow.py
def test_patch_workflow_end_to_end(tmp_path):
    """Test full patch-first workflow."""
    # 1. Tool generates patch
    task = {
        'mode': 'prompt',
        'payload': {'description': 'Add docstring', 'files': ['app.py']}
    }
    adapter = AiderAdapter(config={'patch_mode': True})
    result = adapter.execute_task(task, str(tmp_path))
    assert 'patch' in result.artifacts
    
    # 2. Create PatchArtifact
    patch_artifact = PatchArtifact.from_diff(result.artifacts['patch'])
    assert patch_artifact.format == 'unified_diff'
    
    # 3. Validate patch
    validator = PatchValidator()
    validation = validator.validate(patch_artifact)
    assert validation.format_ok == True
    
    # 4. Apply patch
    applier = PatchApplier()
    apply_result = applier.apply(patch_artifact, tmp_path)
    assert apply_result.success == True
    
    # 5. Run tests
    test_result = run_tests(tmp_path)
    assert test_result.passed == True
    
    # 6. Commit
    git_commit(tmp_path, f"Apply patch {patch_artifact.patch_id}")
```

### Regression Tests (Backward Compatibility)

```python
# tests/regression/test_direct_edit_mode.py
def test_direct_edit_mode_still_works():
    """Ensure old direct-edit mode still works during migration."""
    adapter = AiderAdapter(config={'patch_mode': False})  # OLD MODE
    task = {'mode': 'prompt', 'payload': {...}}
    result = adapter.execute_task(task, ...)
    
    # Should NOT output patch
    assert 'patch' not in result.artifacts
    
    # Should have edited files directly
    assert Path('app.py').read_text() != original_content
```

---

## Recommendations Summary

### ✅ DO THIS NOW (Phase A - Quick Wins)

1. **Copy UET schemas** - 2 hours, zero risk, enables everything
2. **Worker health checks** - 4 hours, improves resilience
3. **Event persistence** - 4 hours, enables debugging
4. **Feedback loop** - 8 hours, test-driven execution

**Total**: 18 hours, 1-2 weeks

---

### ✅ DO THIS NEXT (Phase B - Patch System)

1. **Database migration** - 6 hours, required for patch system
2. **Patch ledger** - 16 hours, core lifecycle tracking
3. **Patch validator** - 8 hours, quality gates
4. **Patch policy engine** - 12 hours, constraint enforcement

**Total**: 42 hours, 2-3 weeks

---

### 🟡 DO THIS CAREFULLY (Phase C - Orchestration)

1. **Context manager** - 8 hours, LOW RISK
2. **Merge orchestration** - 10 hours, MEDIUM RISK
3. **DAG scheduler** - 12 hours, **HIGH RISK** - needs migration plan

**Total**: 30 hours, 2-3 weeks

---

### 🔴 DO THIS LAST (Phase D - Breaking Changes)

1. **Dual-mode adapters** - 8 hours, foundation for migration
2. **Patch-first adapters** - 18 hours, **BREAKING CHANGE**
3. **Migration testing** - 16 hours, ensure backward compat

**Total**: 42 hours, 3-4 weeks

---

### ⚠️ OPTIONAL (Phase E - Advanced)

1. **Compensation engine** - 12 hours, nice-to-have
2. **Human review** - 12 hours, exception handling
3. **Security isolation** - 16 hours, complex, Windows-specific

**Total**: 40 hours, 2-3 weeks

---

## Final Assessment

### Overall Plan Quality: ⭐⭐⭐⭐½ (4.5/5)

**Strengths**:
- ✅ Comprehensive understanding of UET framework
- ✅ Logical phasing (dependencies respected)
- ✅ Patch-first workflow is architecturally sound
- ✅ Event sourcing + audit trail is best practice
- ✅ Worker lifecycle aligns with UET spec
- ✅ Cost tracking and gates are well-designed

**Weaknesses**:
- ⚠️ Underestimates migration complexity (direct edit → patch-first)
- ⚠️ DAG scheduler needs clearer dependency migration strategy
- ⚠️ ULID migration could break existing integrations
- ⚠️ Security isolation may be overkill for MVP

**Critical Success Factors**:
1. **Database migration** must be bulletproof (backups + rollback)
2. **Adapter refactoring** needs dual-mode support (not big-bang)
3. **DAG scheduler** needs opt-in flag (gradual adoption)
4. **Testing** is critical (unit + integration + regression)

---

## Next Steps

### Immediate Actions (This Week)

1. ✅ **Copy UET schemas** to `schema/uet/`
   ```powershell
   Copy-Item UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\schema\*.json schema\uet\
   ```

2. ✅ **Review existing components** against UET specs
   - Compare `core/engine/patch_manager.py` to `patch_artifact.v1.json`
   - Compare `core/engine/worker.py` to UET worker lifecycle
   - Compare `core/engine/event_bus.py` to `run_event.v1.json`

3. ✅ **Create database migration script** (draft)
   ```python
   python scripts/migrate_db_to_uet.py --dry-run
   ```

4. ✅ **Add feature flags** to `PROJECT_PROFILE.yaml`
   ```yaml
   execution:
     patch_mode: false          # Feature flag for patch-first
     parallel_strategy: sequential  # vs "dag"
     ulid_enabled: false        # Gradual ULID migration
   ```

---

### Week 1-2: Phase A (Quick Wins)

- [ ] Worker health checks
- [ ] Event persistence
- [ ] Feedback loop
- [ ] Context manager enhancements

---

### Week 3-4: Phase B (Patch System)

- [ ] Database migration (with backup!)
- [ ] Patch ledger
- [ ] Patch validator
- [ ] Patch policy engine

---

### Week 5-6: Phase C (Orchestration)

- [ ] Context manager (token tracking)
- [ ] Merge orchestration
- [ ] DAG scheduler (feature branch)

---

### Week 7-9: Phase D (Adapters)

- [ ] Dual-mode adapter support
- [ ] Patch-first refactoring
- [ ] Migration testing

---

### Week 10: Phase E (Optional)

- [ ] Compensation engine
- [ ] Human review workflow
- [ ] (Skip security isolation for MVP)

---

## Conclusion

Your UET integration plan is **architecturally sound and feasible**. The ~40% existing implementation will **accelerate** the timeline, but **adapter refactoring and DAG scheduler migration** are **breaking changes** that need careful handling.

**Recommendation**: Start with **Phases A & B** (quick wins + patch system) to build momentum, then tackle **Phase C** (orchestration) with feature flags for gradual adoption. **Phase D** (adapters) should be last, with dual-mode support to avoid breaking existing workstreams.

**Revised Timeline**: 9-10 weeks for full UET alignment (vs. original 7 weeks)

**MVP Timeline**: 6-7 weeks (skip security, human review optional)

**Estimated Effort**: 75-90 hours (vs. original 50-60 hours)

---

**Your plan is APPROVED with the recommended phasing and migration strategies above.**

Good luck! 🚀
