---
decision_id: DECISION-DATABASE_STRATEGY-001
date: 2025-12-03
status: proposed
author: AI Development Team
---

# Decision: Database Unification Strategy

## Context


The codebase currently has two separate database systems:
- core/state/db.py → .ledger/framework.db (runs, step_attempts tables)
- gui/tui_app/core/sqlite_state_backend.py → .worktrees/pipeline_state.db (uet_executions, patch_ledger tables)

The headless CLI supervision feature needs to add tool_runs and approvals tables.
We must decide which database to use and how to handle the schema divergence.


## Problem Statement

Two separate databases with different schemas create maintenance burden and data consistency issues

## Options Considered


### Option 1: unified_db

**Description**: Merge both databases into single schema at .worktrees/pipeline_state.db

**Pros**:

- Single source of truth - no data sync issues

- Atomic transactions across all tables

- Simpler code - one connection, one schema

- Easier to maintain and evolve


**Cons**:

- Significant migration effort required

- Potential breaking changes to existing code

- Risk during migration (need rollback plan)


**Recommendation**: RECOMMENDED - Long-term cleanest solution


### Option 2: dual_db_with_sync

**Description**: Keep separate databases, sync tool_runs/approvals between them

**Pros**:

- Less disruptive to existing code

- Gradual migration path possible

- Lower immediate risk


**Cons**:

- Data consistency issues (sync lag, conflicts)

- Increased complexity (sync daemon required)

- Two schemas to maintain forever


**Recommendation**: Acceptable fallback if migration too risky


### Option 3: supervisor_writes_both

**Description**: cli_supervisor writes tool_runs/approvals to both databases

**Pros**:

- Quick implementation - no migration needed

- Works with existing architecture immediately


**Cons**:

- Technical debt - double writes error-prone

- Complex failure handling (what if one write fails?)

- Performance overhead

- Still need to unify eventually


**Recommendation**: AVOID - Creates more problems than it solves



## Decision

**Chosen Option**: TBD - Team decision required

**Rationale**: Decision pending team discussion of migration effort vs long-term benefits

## Consequences

### Positive

- TBD after decision


### Negative

- TBD after decision


### Risks

- TBD after decision


## Implementation Notes


If unified_db chosen:
1. Create migration script to merge schemas
2. Back up both databases before migration
3. Test migration on copy of production data
4. Create rollback procedure
5. Update all code to use unified schema

If dual_db_with_sync chosen:
1. Create sync daemon
2. Define sync protocol (eventual consistency)
3. Handle conflict resolution
4. Monitor sync lag


## Timeline

- **Decision Date**: 2025-12-03
- **Implementation Start**: TBD
- **Expected Completion**: TBD

## Related Decisions



## References


- gui/HEADLESS_CLI_SUPERVISION_PLAN.json - Phase 1 tasks

- gui/HEADLESS_CLI_SUPERVISION_GAP_ANALYSIS.md - Gap #3
