# UET Framework Complete Implementation

**Change ID**: uet-001-complete-implementation  
**Type**: Architecture Migration  
**Status**: Planning  
**Owner**: Pipeline Team  
**Estimated Duration**: 9-10 weeks  
**Effort**: 75-90 hours

---

## Problem Statement

The production pipeline is currently **~40% aligned** with the Universal Execution Templates (UET) Framework. This partial alignment creates:

1. **Inconsistent workflows**: Mix of direct file edits and patch-based approaches
2. **Limited traceability**: No comprehensive audit trail for AI-generated changes
3. **Weak validation**: Schema validation not enforced across the board
4. **Sequential execution**: No true DAG-based parallel scheduling
5. **Brittle recovery**: Limited rollback and compensation capabilities
6. **ID fragmentation**: Mix of auto-increment IDs and custom identifiers (not ULIDs)

**Current State**:
- ✅ Worker lifecycle: 80% complete (missing health checks)
- ✅ Event bus: 85% complete (missing persistence)
- ✅ Cost tracker: 75% complete (missing per-phase tracking)
- ✅ Patch manager: 50% complete (missing ledger system)
- ⚠️ Adapters: Direct file edits (not patch-first)
- ⚠️ Scheduler: Basic sequential (not DAG-based)
- ❌ ULIDs: Using auto-increment integers
- ❌ Schema validation: Not enforced

---

## Proposed Solution

**Phased migration** to full UET alignment over 9-10 weeks, maintaining backward compatibility through feature flags.

### Strategic Approach

1. **Copy, Don't Rewrite**: Leverage existing 17 UET schemas from `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/`
2. **Feature Flags**: Enable dual-mode operation during transition
3. **Incremental Migration**: Phase-by-phase with quality gates
4. **Preserve Backward Compatibility**: Existing workstreams continue functioning
5. **Test-Driven**: Each phase has comprehensive test suite

### Architecture Vision

```
┌─────────────────────────────────────────────────────────────┐
│ UET Framework (Reference) - UNIVERSAL_EXECUTION_TEMPLATES   │
│  • 17 canonical schemas                                     │
│  • 196 passing tests                                        │
│  • Clean architecture                                       │
└────────────────┬────────────────────────────────────────────┘
                 │ Copy schemas, patterns, architecture
                 ↓
┌─────────────────────────────────────────────────────────────┐
│ Production Pipeline (Target: 100% aligned)                  │
│  Phase A: Quick Wins (schemas, health, events)              │
│  Phase B: Patch System (ledger, validator, policies)        │
│  Phase C: Orchestration (DAG, merge, context)               │
│  Phase D: Adapters (patch-first refactoring)                │
│  Phase E: Resilience (compensation, review, checkpoints)    │
└─────────────────────────────────────────────────────────────┘
```

---

## Requirements

### Functional Requirements

**Core Infrastructure**:
- SHALL copy all 17 UET schemas from reference implementation to `schema/uet/`
- SHALL implement patch ledger with full state machine (created → validated → applied → verified → committed)
- SHALL create patch validator enforcing format, scope, and constraint checks
- SHALL implement patch policy engine for constraint enforcement
- MUST maintain 100% backward compatibility with existing workstreams during migration

**Execution System**:
- SHALL implement DAG-based scheduler with topological sort
- SHALL create deterministic merge orchestration strategy
- SHALL implement context manager with token estimation, pruning, and chunking
- SHALL integrate test gates with event bus for real-time notifications

**Adapters**:
- SHALL refactor all adapters (aider, codex, claude) to output unified diffs
- SHALL implement dual-mode support (patch-first vs direct-edit)
- SHALL add task mode support (prompt, patch_review, patch_apply_validate)
- MUST NOT break existing adapter configurations

**Data Management**:
- SHALL migrate database to ULID-based identification
- SHALL create `patches`, `patch_ledger_entries`, and `run_events` tables
- SHALL implement event sourcing for full audit trail
- MUST provide rollback script for database migration

**Resilience**:
- SHALL implement Saga pattern for compensation
- SHALL create human review workflow with structured escalation
- SHALL add checkpoint/restore system using git tags
- SHOULD implement security isolation (optional for MVP)

### Non-Functional Requirements

**Performance**:
- SHALL NOT increase execution time by more than 10% vs current
- Patch validation MUST complete in <500ms for 99th percentile
- DAG scheduler overhead MUST be <1 second per workstream

**Quality**:
- ALL new code SHALL have ≥80% test coverage
- ALL changes SHALL pass existing test suite (no regressions)
- ALL database migrations SHALL have validated rollback procedures

**Compatibility**:
- SHALL support Windows PowerShell as primary shell
- SHALL work with Python 3.8+
- SHALL maintain existing file structure (no major reorganization)

---

## Success Criteria

### Phase Completion Gates

**Phase A Complete** when:
- ✅ All 17 UET schemas copied to `schema/uet/`
- ✅ Worker health checks implemented and passing tests
- ✅ Events persisted to database
- ✅ Feedback loop creating fix tasks automatically

**Phase B Complete** when:
- ✅ Database migration executed successfully
- ✅ Patch ledger tracking full lifecycle
- ✅ Patch validator catching invalid diffs
- ✅ Rollback script tested and working

**Phase C Complete** when:
- ✅ DAG scheduler executing parallel tasks
- ✅ Merge orchestration handling conflicts
- ✅ Context manager estimating tokens accurately

**Phase D Complete** when:
- ✅ All adapters outputting patches (not direct edits)
- ✅ Dual-mode support tested with existing workstreams
- ✅ Migration test suite covering 20+ scenarios

**Phase E Complete** when:
- ✅ Compensation engine rolling back failed phases
- ✅ Human review workflow integrated
- ✅ Checkpoints created at phase boundaries

### Overall Success Metrics

- **UET Alignment**: 100% (up from 40%)
- **Schema Validation**: Enforced for all executions
- **Patch Coverage**: 100% of file changes captured as diffs
- **Test Coverage**: ≥85% for new UET components
- **Backward Compatibility**: 0 broken workstreams
- **Performance**: <10% overhead vs baseline

---

## Risks and Mitigations

### Critical Risks

**Risk 1: Adapter Refactoring Breaks Existing Workstreams**  
**Impact**: HIGH  
**Mitigation**:
- Feature flag: `patch_mode: true/false` in `PROJECT_PROFILE.yaml`
- Dual-mode support for 3 months
- Workstream-by-workstream migration
- Comprehensive regression testing
- Rollback plan: Keep old adapters in `core/engine/adapters/legacy/`

**Risk 2: DAG Scheduler Changes Execution Order**  
**Impact**: HIGH  
**Mitigation**:
- Analyze existing workstreams for implicit dependencies
- Default to sequential if no dependencies specified
- Opt-in flag: `parallel_strategy: "dag"` vs `"sequential"`
- Shadow mode: Run both schedulers, compare results
- Gradual rollout by workstream complexity

**Risk 3: Database Migration Causes Data Loss**  
**Impact**: CRITICAL  
**Mitigation**:
- **MANDATORY backup**: `cp .worktrees/pipeline_state.db .worktrees/pipeline_state.db.backup`
- Idempotent migration script (can re-run safely)
- Dual-key support (old IDs + ULIDs coexist)
- Validation queries after migration
- Rollback script: `scripts/rollback_db_migration.py`

**Risk 4: ULID Migration Breaks ID References**  
**Impact**: MEDIUM  
**Mitigation**:
- Add ULID columns, keep existing ID columns
- Update code to accept both ID types
- Populate ULIDs for all existing records
- Transition period: 1 month of dual support
- Drop old IDs only after full validation

---

## Dependencies

### External Dependencies

- **UET Framework**: `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/` (already in repo)
- **Python Packages**: `python-ulid`, `pydantic` (for schema validation)
- **Database**: SQLite 3.35+ (for better JSON support)

### Internal Dependencies

- All phases depend on **Phase A** (schemas must be copied first)
- **Phase C** depends on **Phase B** (patch system needed for DAG)
- **Phase D** depends on **Phase B** (adapters need patch ledger)
- **Phase E** depends on **Phase C** (compensation needs orchestration)

### Dependency Graph

```
Phase A (Quick Wins)
    ├──> Phase B (Patch System)
    │       ├──> Phase C (Orchestration)
    │       └──> Phase D (Adapters)
    │               └──> Phase E (Resilience)
    └──> (Independent of other phases)
```

---

## Timeline

### Estimated Schedule

| Phase | Duration | Effort | Start Week | End Week |
|-------|----------|--------|------------|----------|
| Phase A | 1-2 weeks | 18 hours | Week 1 | Week 2 |
| Phase B | 2-3 weeks | 42 hours | Week 3 | Week 5 |
| Phase C | 2-3 weeks | 30 hours | Week 5 | Week 7 |
| Phase D | 3-4 weeks | 42 hours | Week 7 | Week 10 |
| Phase E | 1-2 weeks | 40 hours | Week 10 | Week 11 |
| **Total** | **9-12 weeks** | **172 hours** | - | - |

**Fast Track** (MVP without security): 7-8 weeks, ~130 hours

---

## Related Changes

This is the **parent change** for five sub-proposals:

- `uet-001-phase-a-quick-wins` - Schema copy, worker health, events
- `uet-001-phase-b-patch-system` - Ledger, validator, database migration
- `uet-001-phase-c-orchestration` - DAG scheduler, merge orchestration
- `uet-001-phase-d-adapters` - Patch-first refactoring
- `uet-001-phase-e-resilience` - Compensation, review, checkpoints

---

## References

- **UET Integration Guide**: `UET_INTEGRATION_GUIDE.md`
- **UET Integration Plan Analysis**: `UET_INTEGRATION_PLAN_ANALYSIS.md`
- **UET Framework**: `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/`
- **UET Schemas**: `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/schema/*.json`
