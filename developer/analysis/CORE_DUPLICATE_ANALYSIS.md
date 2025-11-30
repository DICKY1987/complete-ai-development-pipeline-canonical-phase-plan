---
doc_id: DOC-GUIDE-CORE-DUPLICATE-ANALYSIS-1189
---

# Core Duplicate Analysis

**Date:** 2025-11-21  
**Phase:** H2.1 - Audit Root-Level Core Duplicates  
**Status:** Complete

## Executive Summary

Two root-level directories duplicate functionality from the `core/` section:
- `engine/` - Standalone engine implementation (DIFFERENT from core/engine/)
- `state/` - Database file only (should be in core/state/)

## Detailed Analysis

### engine/ (Root) vs core/engine/

**Status:** DIFFERENT IMPLEMENTATIONS - NOT duplicates

#### Root engine/ Structure:
```
engine/
├── interfaces/          # Protocol definitions
├── adapters/           # Tool adapters (aider, codex, git, tests)
├── orchestrator/       # Job orchestration
├── queue/             # Job queue system
├── state_store/       # State persistence
├── types.py           # Shared types
└── README.md          # Implementation docs
```

**Key Files:**
- Job-based execution system
- Adapter pattern for CLI tools
- Queue management and worker pools
- Standalone orchestrator implementation

#### core/engine/ Structure:
```
core/engine/
├── adapters/                    # Different adapter implementations
├── orchestrator.py              # Core orchestrator
├── scheduler.py                 # Scheduling logic
├── executor.py                  # Execution logic
├── recovery.py                  # Recovery strategies
├── circuit_breakers.py          # Circuit breaker patterns
├── tools.py                     # Tool adapters
├── aim_integration.py           # AIM integration
├── pipeline_plus_orchestrator.py
├── patch_manager.py
├── prompt_engine.py
└── ... (20+ specialized modules)
```

**Analysis:**
- **Different architectures**: Root `engine/` uses job-based pattern; `core/engine/` uses step-based workstream pattern
- **Different purposes**: 
  - `engine/` = Standalone hybrid GUI/Terminal/TUI architecture (per engine/README.md)
  - `core/engine/` = Workstream execution engine integrated with core pipeline
- **Different import patterns**: 22 files import from `engine.*` (not `core.engine.*`)
- **Active development**: Both are actively maintained

**Imports Referencing `engine.*`:**
```
engine\state_store\job_state_store.py
engine\queue\__main__.py
engine\queue\worker_pool.py
engine\queue\queue_manager.py
engine\queue\job_queue.py
engine\queue\escalation.py
engine\orchestrator\__main__.py
engine\orchestrator\orchestrator.py
engine\interfaces\__init__.py
engine\interfaces\state_interface.py
engine\interfaces\orchestrator_interface.py
engine\interfaces\adapter_interface.py
engine\adapters\tests_adapter.py
engine\adapters\git_adapter.py
engine\adapters\codex_adapter.py
engine\adapters\aider_adapter.py
tests\test_escalation.py
tests\test_job_queue.py
tests\test_job_wrapper.py
tests\test_queue_manager.py
tests\test_retry_policy.py
tests\test_worker_pool.py
```

**Disposition:** KEEP - This is a separate engine implementation, not a duplicate

**Recommendation:** Document relationship in AGENTS.md as:
- `engine/` = Job-based execution engine (standalone)
- `core/engine/` = Workstream execution engine (integrated)

### state/ (Root) vs core/state/

**Status:** DATABASE FILE ONLY - Should be relocated

#### Root state/ Contents:
```
state/
└── pipeline_state.db    (348 KB)
```

**Analysis:**
- Contains ONLY the database file
- No Python code
- No imports reference `state.*` module
- Database should be managed by `core/state/` module

#### core/state/ Structure:
```
core/state/
├── __init__.py
├── db.py                # Database initialization
├── db_sqlite.py         # SQLite backend
├── crud.py              # CRUD operations
├── bundles.py           # Bundle management
├── worktree.py          # Worktree management
├── task_queue.py        # Task queue
└── audit_logger.py      # Audit logging
```

**Analysis:**
- Complete state management system
- `core/state/db.py` handles database initialization
- Should be the canonical location for database files

**Disposition:** RELOCATE - Move database file to canonical location

**Recommended Actions:**
1. Move `state/pipeline_state.db` → `core/state/pipeline_state.db` OR `.worktrees/pipeline_state.db`
2. Update `core/state/db.py` to use new path
3. Update `.gitignore` for new database location
4. Remove empty `state/` directory

## Import Dependency Summary

### engine/ imports: 22 files
All references use `from engine.*` pattern, NOT `from core.engine.*`

### state/ imports: 0 files
No code imports from `state.*` module

## Consolidation Decisions

### engine/ → KEEP AS-IS
**Rationale:**
- Separate implementation with different architecture
- Active development with test coverage
- Used by different execution model (jobs vs workstreams)
- 22 files depend on `engine.*` import path
- Documented in engine/README.md as standalone system

**Required Actions:**
1. Update AGENTS.md to document both engine implementations
2. Add clear documentation distinguishing:
   - `engine/` - Job-based standalone execution
   - `core/engine/` - Workstream-based integrated execution
3. Consider future consolidation in later phase if patterns converge

### state/ → RELOCATE DATABASE
**Rationale:**
- Only contains database file (no code)
- No dependencies on `state.*` path
- `core/state/` is the proper module for state management
- Simpler to move single file than refactor module

**Recommended Location:**
**Option A:** `core/state/pipeline_state.db`
- Co-located with state management code
- Clear ownership

**Option B:** `.worktrees/pipeline_state.db`
- Keeps runtime data separate from code
- Already gitignored location
- Similar to how `.ledger`, `.runs`, `.tasks` are handled

**Recommendation:** Use **Option B** - `.worktrees/pipeline_state.db`
- Aligns with runtime data pattern
- Cleaner code directory
- Already in `.gitignore` patterns

## Risk Assessment

### engine/ - NO CHANGES
**Risk Level:** NONE
- Keeping as-is, no migration needed
- Documentation clarification only

### state/ - DATABASE RELOCATION  
**Risk Level:** LOW

**Potential Impact:**
- Database initialization code may hardcode "state/pipeline_state.db" path
- Need to update path references in `core/state/db.py`

**Mitigation:**
- Check `core/state/db.py` for hardcoded paths
- Update database path configuration
- Test database initialization after move
- Backup database before move

## File Mapping

### state/ Relocation:
```
state/pipeline_state.db  →  .worktrees/pipeline_state.db
```

### Code Updates Required:
```
core/state/db.py         - Update DEFAULT_DB_PATH
core/state/db_sqlite.py  - Verify path handling
scripts/db_inspect.py    - Update path if hardcoded
.gitignore               - Verify .worktrees/*.db is ignored
```

## Next Steps (Phase H2.2-H2.3)

### H2.2: Document engine/ Dual Implementation ✅
1. Update AGENTS.md with engine/ section
2. Create cross-reference in docs/ARCHITECTURE.md
3. No code changes needed

### H2.3: Relocate state/ Database
1. Create .worktrees/ directory if not exists
2. Copy state/pipeline_state.db → .worktrees/pipeline_state.db (keep backup)
3. Update core/state/db.py DEFAULT_DB_PATH
4. Test database access: `python scripts/db_inspect.py`
5. Remove state/ directory
6. Update documentation

---

**Analysis Complete:** 2025-11-21  
**Recommendation:** Clarify engine/ documentation, relocate state/ database  
**Approved for Next Phase:** Yes
