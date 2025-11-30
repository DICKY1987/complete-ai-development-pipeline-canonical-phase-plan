---
doc_id: DOC-GUIDE-FINAL-RECOMMENDATION-225
---

# Migration Plan Comparison & Final Recommendation

**Date**: 2025-11-25  
**Analysis**: Comparing original vs pattern-enhanced UET migration plans

---

## Plans Compared

### Plan A: Original UET Migration
**File**: `engine_migration_plan.txt`
- Timeline: 6-8 weeks
- Approach: Sequential phases
- Risk: High
- Decision overhead: ~50 decisions per phase
- Pattern integration: None

### Plan B: Pattern-Enhanced UET Migration
**File**: Claude history `2af6187340c96af6@v3`
- Timeline: 3-4 weeks
- Approach: Parallel worktrees + templates
- Risk: Medium (reduced via anti-pattern guards)
- Decision overhead: ~5 decisions per phase (90% reduction)
- Pattern integration: All 7 PRMNT patterns

---

## Key Differences

### Timeline Acceleration

| Phase | Original | Pattern-Enhanced | Speedup |
|-------|----------|------------------|---------|
| Phase 0 (Templates) | N/A | 2 days | New phase |
| Phase 1 (Foundation) | 10 days | 4 days | **2.5x faster** |
| Phase 2-5 (Remaining) | 14 days | 10 days | 1.4x faster |
| **Total** | **6-8 weeks** | **3-4 weeks** | **~2x faster** |

**How**: Parallel worktree execution (3 worktrees work simultaneously on Phase 1)

---

### Decision Elimination

**Original Plan**:
- ~250 decisions across 5 phases
- Manual planning for each step
- Ad-hoc verification

**Pattern-Enhanced Plan**:
- ~25 decisions (225 eliminated via templates)
- Pre-compiled execution templates
- Ground truth gates (programmatic verification)
- **37x potential speedup** per decision

**Example**:
```yaml
# Original: You decide what tables, write SQL, verify manually
# Pattern: Template decides, generates SQL, verifies programmatically

template: templates/migration/database_migration.template.yaml
parameters:
  tables_to_add: [uet_runs, step_attempts, run_events, patch_ledger]
  validation_query: SELECT COUNT(*) FROM sqlite_master
ground_truth_gate:
  command: sqlite3 :memory: < schema/migrations/uet_migration_001.sql
  expect_exit_code: 0
```

---

### Risk Reduction

**Original Plan**:
- Risk: HIGH
- Anti-patterns: Not addressed
- Verification: Manual review
- Rollback: Defined but untested

**Pattern-Enhanced Plan**:
- Risk: MEDIUM (reduced via 4 anti-pattern guards)
- Guards:
  1. **Hallucination of success** → Never mark complete without exit code check
  2. **Planning loop trap** → Max 2 planning iterations, then execute
  3. **Partial success amnesia** → Checkpoint after each phase
  4. **Approval loop** → No human approval for templated operations
- Verification: Ground truth gates (exit codes, file exists, tests pass)
- Rollback: Tested in worktrees before main merge

---

### Parallel Execution Strategy

**Original Plan**: Sequential phases only

**Pattern-Enhanced Plan**: Worktree parallelization
```yaml
# Phase 1 splits into 3 parallel worktrees:
wt-phase1-database:
  - Works on: schema/migrations/*
  - Produces: migration SQL

wt-phase2-dag:
  - Works on: core/engine/dag_builder.py
  - Produces: DAG scheduler

wt-phase3-patches:
  - Works on: core/engine/patch_*.py
  - Produces: Patch ledger

# All 3 work simultaneously → 2.5x speedup
```

**Control Checkout**: Single writer for global state, merges all worker patches

---

### PRMNT Pattern Integration

Pattern-enhanced plan integrates **all 7 patterns** from your PRMNT DOCS:

1. ✅ **Multi-CLI Worktree Coordination** (Phase 0)
2. ✅ **Batch Execution EXEC-001** (Phase 1)
3. ✅ **Ground Truth Verification** (All phases)
4. ✅ **Decision Elimination Templates** (Phase 0)
5. ✅ **Anti-Pattern Guards** (Phase 0)
6. ✅ **Decision Telemetry** (Phase 0)
7. ✅ **Parallel Execution Strategy** (Phase 1)

**Impact**: 2-4 week time savings, 90% decision reduction, 4 failure modes prevented

---

## Updated Recommendation Matrix

Given the **pattern-enhanced plan** exists, here's the updated recommendation:

### Option A: Pattern Automation FIRST, Legacy Orchestrator
- Cleanup (1-2 days)
- Build pattern automation on legacy orchestrator (6-8 weeks)
- **Skip** UET migration
- **Timeline**: 6-9 weeks
- **Benefit**: Auto-learning only, no speedup

### Option B: Pattern-Enhanced UET Migration FIRST
- Cleanup (1-2 days)
- Execute pattern-enhanced migration (3-4 weeks)
- Build pattern automation on UET orchestrator (6-8 weeks)
- **Timeline**: 10-13 weeks
- **Benefit**: Both auto-learning AND 4-6x speedup

### Option C: Quick Cleanup ONLY (Defer Both)
- Cleanup (1-2 days)
- Archive unused code
- **Stop** - make decision later
- **Timeline**: 2 days
- **Benefit**: Clean codebase, decision deferred

---

## New Recommendation: Option B (Pattern-Enhanced UET First)

### Why Changed From Previous Recommendation?

**Previously recommended**: Pattern automation first (Option A)
- Reasoning: De-risk by sequencing, UET migration too risky

**Now recommend**: Pattern-enhanced UET first (Option B)
- Reasoning: **Risk reduced from HIGH → MEDIUM** via pattern guards
- Timeline: **Halved from 6-8 weeks → 3-4 weeks**
- Benefits: **Better foundation for pattern automation**

### Why Pattern-Enhanced UET is Better Foundation

**UET Orchestrator Advantages for Pattern Automation**:
1. ✅ **Better event system** → `run_events` table already exists
2. ✅ **State machine architecture** → Cleaner hooks for telemetry
3. ✅ **Monitoring infrastructure** → `monitoring/run_monitor.py` ready
4. ✅ **Parallel execution** → Can capture parallel patterns
5. ✅ **Unified patch ledger** → Better pattern detection

**Legacy Orchestrator Disadvantages**:
1. ⚠️ Event system basic (only `record_event()`)
2. ⚠️ No state machine (harder to hook)
3. ⚠️ No monitoring infra (must build from scratch)
4. ⚠️ Sequential only (can't learn parallel patterns)
5. ⚠️ No patch ledger (harder pattern detection)

**Conclusion**: Building pattern automation on UET = less rework, more features

---

## Execution Strategy

### Phase 0: Cleanup + Templates (Week 1)
**Days 1-2**: Engine cleanup
- Remove 49 unused files
- Consolidate to single orchestrator
- Clean foundation

**Days 3-5**: Template library (NEW)
- Create execution templates
- Configure anti-pattern guards
- Setup worktree coordination
- Enable decision telemetry

**Deliverable**: Clean codebase + execution framework

---

### Phase 1: UET Foundation (Week 2-3)
**Parallel worktree execution**:

**wt-phase1-database** (4 days):
- Database migration SQL
- Unified DB layer
- Ground truth gates

**wt-phase2-dag** (4 days):
- DAG builder
- DAG scheduler
- Topological sort

**wt-phase3-patches** (4 days):
- Patch converter
- Patch applier
- Patch ledger

**Control merge** (1 day):
- Merge all 3 worktrees
- Run global validation
- Tag phase 1 complete

**Deliverable**: UET foundation operational

---

### Phase 2-5: UET Completion (Week 4-5)
**Phase 2** (Week 4): Parallel execution testing
**Phase 3** (Week 4): Patch management integration
**Phase 4** (Week 5, days 1-3): Integration testing
**Phase 5** (Week 5, days 4-5): Production cutover

**Deliverable**: UET in production

---

### Phase 6: Pattern Automation (Week 6-13)
Build pattern automation on **stable UET orchestrator**:
- Week 6-7: Error engine + telemetry tables
- Week 8-9: Complete 3 pattern executors
- Week 10-11: AUTO-001 through AUTO-004
- Week 12-13: AUTO-005 through AUTO-008 + testing

**Deliverable**: Auto-learning + parallel execution operational

---

## Comparison: New vs Previous Recommendation

| Factor | Previous (Pattern→Engine) | New (UET→Pattern) |
|--------|---------------------------|-------------------|
| **Week 1** | Cleanup | Cleanup + Templates |
| **Week 2-9** | Pattern automation on legacy | UET migration (pattern-enhanced) |
| **Week 10-17** | Consider UET migration (6-8 weeks) | Pattern automation on UET |
| **Total** | 17 weeks (both) | 13 weeks (both) |
| **Risk** | 2 major changes | 2 major changes |
| **Foundation** | Pattern automation on legacy (rework later) | Pattern automation on UET (no rework) |
| **Speedup** | None until week 10 | 4-6x at week 5 |
| **Decision overhead** | High (no templates) | Low (90% eliminated) |

**Winner**: New recommendation (4 weeks faster, better foundation, less rework)

---

## Final Recommendation

### **EXECUTE PATTERN-ENHANCED UET MIGRATION**

**Timeline**: 5 weeks for UET, then 8 weeks for pattern automation = **13 weeks total**

**Week-by-week**:
- **Week 1**: Cleanup + templates
- **Week 2-3**: UET foundation (parallel worktrees)
- **Week 4-5**: UET completion + cutover
- **Week 6-13**: Pattern automation on UET

**Benefits**:
1. ✅ **4-6x speedup** at week 5 (vs week 17 in old plan)
2. ✅ **Better foundation** for pattern automation
3. ✅ **No rework** (pattern automation built on final architecture)
4. ✅ **Lower risk** (anti-pattern guards, ground truth gates)
5. ✅ **4 weeks faster** than sequential approach
6. ✅ **90% fewer decisions** (templates eliminate overhead)

**First Action**: Execute `ENGINE_CLEANUP_CHECKLIST.md` (Days 1-2)

**Second Action**: Create template library (Days 3-5, from pattern-enhanced plan)

**Third Action**: Launch 3 parallel worktrees for Phase 1 (Week 2)

---

## Risk Mitigation

### Previous Concern: UET Migration Too Risky

**Addressed by Pattern-Enhanced Plan**:
- ✅ Anti-pattern guards prevent documented failure modes
- ✅ Ground truth gates prevent hallucination of success
- ✅ Worktree isolation prevents contamination
- ✅ Decision telemetry tracks progress objectively
- ✅ Rollback tested in each worktree before merge

**Result**: Risk reduced from HIGH → MEDIUM

---

### Previous Concern: Timeline Too Long (6-8 weeks)

**Addressed by Pattern-Enhanced Plan**:
- ✅ Parallel worktrees cut Phase 1 from 10 days → 4 days
- ✅ Templates eliminate decision overhead (90% reduction)
- ✅ Batch execution (EXEC-001) automates file creation
- ✅ Overall timeline halved: 6-8 weeks → 3-4 weeks

**Result**: Timeline acceptable for value delivered

---

## Documents to Use

**For Cleanup** (Days 1-2):
- `ENGINE_CLEANUP_CHECKLIST.md`

**For UET Migration** (Week 1-5):
- Claude history `2af6187340c96af6@v3` (pattern-enhanced plan)
- **NOT** `engine_migration_plan.txt` (original, slower, riskier)

**For Pattern Automation** (Week 6-13):
- `PATTERN_plan_enc.txt`
- PRMNT DOCS patterns

**For Context**:
- `ENGINE_MIGRATION_STATUS.md` (analysis)
- `CONSOLIDATED_MIGRATION_PLAN.md` (decision framework)

---

## Success Criteria

**After Week 1**:
- ✅ 49 unused files removed
- ✅ Template library created
- ✅ Worktree coordination operational
- ✅ Anti-pattern guards configured

**After Week 5**:
- ✅ UET orchestrator in production
- ✅ 4-6x speedup demonstrated
- ✅ All 46 workstreams on UET
- ✅ 337 UET tests passing

**After Week 13**:
- ✅ Pattern automation operational
- ✅ 3+ patterns auto-captured
- ✅ Error recovery learning active
- ✅ Auto-learning + parallel execution combined

---

## Questions?

**Q**: Why change recommendation from pattern automation first?  
**A**: Pattern-enhanced plan reduces UET risk (HIGH→MEDIUM) and halves timeline (6-8→3-4 weeks). Better foundation for pattern automation.

**Q**: What if UET migration fails?  
**A**: Rollback to legacy orchestrator in <15 minutes. Pattern automation can still build on legacy (original Option A).

**Q**: Can we do both simultaneously?  
**A**: No - they conflict. Pattern automation needs stable orchestrator. UET migration replaces orchestrator.

**Q**: What if we only have 1-2 weeks?  
**A**: Execute cleanup only (Option C). Defer decision on UET vs pattern automation.

---

**Status**: Final recommendation updated  
**Path**: Pattern-enhanced UET migration → Pattern automation on UET  
**Timeline**: 13 weeks total (5 UET + 8 patterns)  
**First Action**: `ENGINE_CLEANUP_CHECKLIST.md` (Days 1-2)
