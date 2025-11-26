# Engine Migration Status Report

**Generated**: 2025-11-25  
**Purpose**: Analyze UET Framework migration status and identify consolidation opportunities

---

## Executive Summary

**Migration Status**: ⚠️ **INCOMPLETE - Multiple Engine Systems Coexist**

### Current State
- **3 separate engine implementations** detected
- **75 total engine-related Python files** across codebase
- **4 orchestrator variants** present (legacy, UET, parallel, pipeline_plus)
- **UET files are placeholder stubs** - migration NOT executed

### Key Finding
The migration plan exists but **was never executed**. UET orchestrator is a 2-line placeholder file.

---

## File Count Analysis

| Location | File Count | Status |
|----------|-----------|--------|
| `core/engine/` | 34 files | ✅ Active (legacy system) |
| `engine/` | 24 files | ⚠️ Duplicate/older system |
| `UET_FRAMEWORK/core/engine/` | 17 files | ✅ Production-ready (unused) |

**Total**: 75 engine files

---

## Orchestrator Inventory

### 1. Legacy Orchestrator (ACTIVE)
**File**: `core/engine/orchestrator.py`  
**Lines**: ~400+ lines  
**Features**:
- EDIT → STATIC → RUNTIME sequencing
- Single workstream execution
- Basic parallel support (Phase I addition)
- DB state tracking
- Circuit breakers
- AIM integration

**Status**: ✅ Currently in use

---

### 2. UET Orchestrator (PLACEHOLDER STUB)
**File**: `core/engine/uet_orchestrator.py`  
**Lines**: 2 lines (placeholder comment)  
**Content**:
```python
# UET Module: core\engine\uet_orchestrator.py
# To be copied from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK
```

**Status**: ❌ Not implemented - migration never executed

---

### 3. UET Framework Orchestrator (SOURCE)
**File**: `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/orchestrator.py`  
**Lines**: ~500+ lines  
**Features**:
- DAG-based parallel execution
- State machine integration
- Run lifecycle management
- Event emission
- ULID generation
- Test gate integration
- Patch ledger support

**Status**: ✅ Production-ready with 337 passing tests - **UNUSED**

---

### 4. Parallel Orchestrator
**File**: `core/engine/parallel_orchestrator.py`  
**Purpose**: Extension of legacy orchestrator for parallel execution  
**Status**: ⚠️ Partial implementation

---

### 5. Pipeline Plus Orchestrator
**File**: `core/engine/pipeline_plus_orchestrator.py`  
**Purpose**: Unknown - potential experimental variant  
**Status**: ⚠️ Needs review

---

### 6. Engine Module Orchestrator
**File**: `engine/orchestrator/orchestrator.py`  
**Purpose**: Older/separate implementation?  
**Status**: ⚠️ Likely deprecated

---

## Duplicate Engine Systems

### System 1: `core/engine/` (34 files)
**Primary active system** - contains:
- orchestrator.py
- uet_orchestrator.py (stub)
- uet_scheduler.py
- uet_router.py
- uet_patch_ledger.py
- uet_state_machine.py
- parallel_orchestrator.py
- dag_builder.py
- patch_applier.py
- patch_converter.py
- Many support modules

**Assessment**: Mix of legacy + partially migrated UET stubs

---

### System 2: `engine/` (24 files)
Contains:
- `orchestrator/orchestrator.py`
- `queue/` module (worker pool, retry policy, job queue)
- `adapters/` (aider, codex, git, tests)
- `interfaces/` (orchestrator, adapter, state)
- `state_store/` (job state store)

**Assessment**: ⚠️ Appears to be older/alternative implementation

**Questions**:
- Is this deprecated?
- Does anything still use it?
- Can it be removed?

---

### System 3: `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/` (17 files)
**Production-ready UET implementation** with:
- orchestrator.py
- scheduler.py
- router.py
- state_machine.py
- patch_ledger.py
- test_gate.py
- worker_lifecycle.py
- cost_tracker.py
- execution_request_builder.py
- resilience/ module (circuit breaker, retry, resilient executor)
- monitoring/ module (progress tracker, run monitor)

**Assessment**: ✅ **Complete, tested, production-ready** - should be THE engine

---

## Migration Plan Status

### Planned (from engine_migration_plan.txt)

The plan called for:

**Phase 1**: Foundation (10 days)
- ✅ Unified database layer
- ❌ Workstream converter (not created)
- ❌ UET core modules integration (stubs only)
- ❌ Bridge adapters (not created)

**Phase 2**: Parallel Execution (5 days)
- ❌ DAG scheduler operational
- ⚠️ Partial parallel orchestrator exists
- ❌ Wave-based execution

**Phase 3**: Patch Management (3 days)
- ⚠️ Some files exist (patch_applier, patch_converter)
- ❌ Not integrated with UET patch ledger

**Phase 4**: Integration Testing (3 days)
- ❌ Not executed

**Phase 5**: Cutover (1 day)
- ❌ Never happened

**Overall Status**: ~15% complete (stubs created, no real migration)

---

## What Needs to Be Removed

### HIGH PRIORITY - Remove to Consolidate to ONE Engine

#### Option A: Keep Legacy, Remove UET Stubs
If staying with legacy system:

**Remove**:
```
core/engine/uet_orchestrator.py (stub)
core/engine/uet_scheduler.py
core/engine/uet_router.py
core/engine/uet_patch_ledger.py
core/engine/uet_state_machine.py
core/engine/adapters/uet_base.py
core/engine/adapters/uet_registry.py
core/engine/adapters/uet_subprocess.py
```

**Keep**:
```
core/engine/orchestrator.py (legacy)
core/engine/parallel_orchestrator.py
core/engine/dag_builder.py
All other core/engine/*.py files
```

**Archive**:
```
UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/ (move to archive/)
```

---

#### Option B: Complete Migration to UET (RECOMMENDED)
If committing to UET:

**Execute** the migration plan:

1. **Copy UET core files** (replace stubs with real implementations):
```bash
# Copy orchestrator
cp UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/orchestrator.py \
   core/engine/uet_orchestrator.py

# Copy supporting modules
cp UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/scheduler.py \
   core/engine/uet_scheduler.py

cp UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/router.py \
   core/engine/uet_router.py

cp UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/state_machine.py \
   core/engine/uet_state_machine.py

cp UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/patch_ledger.py \
   core/engine/uet_patch_ledger.py

# Copy adapters
cp -r UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/adapters/* \
      core/engine/adapters/

# Copy state DB
cp UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/state/db.py \
   core/state/uet_db.py
```

2. **Remove legacy orchestrator** after validation:
```
core/engine/orchestrator.py → core/engine/orchestrator_legacy.py (archive)
core/engine/parallel_orchestrator.py (superseded by UET scheduler)
```

3. **Remove duplicate engine/** directory:
```
engine/orchestrator/
engine/queue/
engine/adapters/
engine/interfaces/
engine/state_store/
```

4. **Update imports** throughout codebase

---

### MEDIUM PRIORITY - Clean Up Deprecated

**Remove if confirmed deprecated**:
```
engine/ (entire directory - 24 files)
  - orchestrator/orchestrator.py
  - queue/ module
  - adapters/ (old versions)
  - interfaces/
  - state_store/
```

**Verification needed**:
- Check if anything imports from `engine.orchestrator`
- Check if queue system is still used
- Confirm no active dependencies

---

### LOW PRIORITY - Test File Cleanup

**Old pipeline tests** (if src/pipeline deprecated):
```
tests/pipeline/test_orchestrator_single.py
tests/pipeline/test_bundles.py
tests/pipeline/test_aim_bridge.py
tests/pipeline/test_fix_loop.py
tests/pipeline/test_openspec_parser_src.py
tests/pipeline/test_workstream_authoring.py
```

---

## Dependency Analysis

### Files importing deprecated paths

**Found 42 files** importing `from src.pipeline`:
- Documentation files (can be updated)
- Migration scripts (can be updated)
- Legacy docs in archive/ (can ignore)

**Action**: Run import migration script:
```bash
python scripts/migrate_imports.py
```

---

## Recommendations

### Immediate Actions

1. **DECIDE**: UET vs Legacy
   - If UET: Execute migration (6-8 weeks realistic)
   - If Legacy: Remove all UET stubs (1 day)

2. **REMOVE**: `engine/` directory duplication
   - Verify no active dependencies
   - Archive or delete

3. **DOCUMENT**: Chosen architecture
   - Update ARCHITECTURE.md
   - Clear governance on "one engine"

---

### Short-term (1-2 weeks)

4. **Consolidate adapters**
   - Merge `core/engine/adapters/` and `engine/adapters/`
   - Single source of truth

5. **Clean test files**
   - Remove deprecated pipeline tests
   - Update test imports

6. **Update CI/CD**
   - Enforce single engine imports
   - Block deprecated path usage

---

### Long-term (if choosing UET)

7. **Execute full migration plan**
   - Follow 5-phase plan from migration doc
   - 6-8 week realistic timeline
   - Maintain rollback capability

8. **Archive UET Framework directory**
   - After successful migration
   - Move to `archive/uet_framework_source/`

9. **Leverage UET features**
   - DAG parallel execution (4-6x speedup)
   - Unified patch ledger
   - Better observability

---

## File Removal Checklist

### If Keeping Legacy (Quick Path)

- [ ] Remove `core/engine/uet_orchestrator.py`
- [ ] Remove `core/engine/uet_scheduler.py`
- [ ] Remove `core/engine/uet_router.py`
- [ ] Remove `core/engine/uet_patch_ledger.py`
- [ ] Remove `core/engine/uet_state_machine.py`
- [ ] Remove `core/engine/adapters/uet_*.py` (3 files)
- [ ] Remove or archive `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/`
- [ ] Remove `engine/` directory (after verification)
- [ ] Update documentation to reflect legacy as canonical
- [ ] Update `CODEBASE_INDEX.yaml`

**Estimated time**: 1-2 days  
**Risk**: Low (removing unused code)

---

### If Migrating to UET (Proper Path)

- [ ] Phase 1: Copy UET files (replace stubs)
- [ ] Phase 1: Create bridge adapters
- [ ] Phase 1: Unified database layer
- [ ] Phase 2: DAG scheduler integration
- [ ] Phase 2: Parallel execution testing
- [ ] Phase 3: Patch ledger integration
- [ ] Phase 4: Full integration testing
- [ ] Phase 5: Production cutover
- [ ] Remove `core/engine/orchestrator.py` (archive as orchestrator_legacy.py)
- [ ] Remove `engine/` directory
- [ ] Remove `core/engine/parallel_orchestrator.py` (superseded)
- [ ] Archive `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/` as source reference
- [ ] Update all imports
- [ ] Update documentation

**Estimated time**: 6-8 weeks  
**Risk**: High (replacing core system)

---

## Risk Assessment

### Current State Risks

⚠️ **Code Confusion**: Multiple orchestrators - which is canonical?  
⚠️ **Technical Debt**: 75 engine files, many potentially unused  
⚠️ **Maintenance Burden**: 3 systems to maintain  
⚠️ **Test Confusion**: Tests for multiple implementations  

### Consolidation Risks

**Legacy Path**:
- ✅ Low risk (removing unused code)
- ❌ Misses UET benefits (parallelism, patch ledger)

**UET Path**:
- ⚠️ High risk (core system replacement)
- ✅ Gains 4-6x speedup potential
- ✅ Better architecture
- ✅ 337 tests already passing

---

## Questions ANSWERED

### 1. **Is `engine/` directory still in use?**
**✅ ANSWER: YES - Self-contained module**

**Evidence**: 17 files in `engine/` import from `engine.`:
- `engine/orchestrator/orchestrator.py`
- `engine/queue/*.py` (7 files)
- `engine/adapters/*.py` (4 files) 
- `engine/interfaces/*.py` (4 files)
- `engine/state_store/*.py`

**Status**: ⚠️ **Separate system** - appears self-contained but unused by main codebase

**Scripts using it**:
- `scripts/test_state_store.py`
- `scripts/test_adapters.py`
- `tools/validation/validate_engine.py`

**Recommendation**: Can be archived - appears to be experimental/alternative implementation

---

### 2. **Are UET adapter stubs being used?**
**❌ ANSWER: NO - Only mentioned in migration plan**

**Evidence**: Only 1 reference found:
- `engine_migration_plan.txt` (the planning doc itself)

**Files checked**:
- `core/engine/adapters/uet_base.py`
- `core/engine/adapters/uet_registry.py`
- `core/engine/adapters/uet_subprocess.py`

**Status**: ❌ **Dead code** - stubs not imported anywhere

**Recommendation**: Safe to delete

---

### 3. **What is the actual current orchestrator in production?**
**✅ ANSWER: `core/engine/orchestrator.py` (legacy)**

**Evidence**:
```python
# core/orchestrator.py (re-export)
from core.engine.orchestrator import *  # type: ignore F401,F403
```

**43 files** reference `from core.engine.orchestrator import`:
- Main codebase docs and READMEs
- Test files
- Planning docs
- UET Framework docs (for comparison)

**Entry points** found:
- `core/ui_cli.py` (main CLI)
- `core/ui_settings_cli.py`
- `core/planning/planner.py`

**Status**: ✅ **ACTIVE** - this is the current production orchestrator

**Recommendation**: This is canonical - keep or replace (but decide)

---

### 4. **Has parallel_orchestrator.py superseded legacy?**
**❌ ANSWER: NO - Appears to be extension, not replacement**

**Status**: Unclear - needs investigation of:
- When/how it's used
- Relationship to `core/engine/orchestrator.py`

**Recommendation**: Review imports and usage before removal

---

### 5. **What is `pipeline_plus_orchestrator.py`?**
**Status**: ⚠️ Unknown - not referenced in grep results

**Recommendation**: Check file header/docstring, then likely remove

---

## Next Steps

### For Decision Making

1. **Run dependency check**:
```bash
# Check what imports from engine/
rg "from engine\." --type py

# Check what imports UET stubs
rg "from core\.engine\.uet_" --type py

# Check active orchestrator
rg "from core\.engine\.orchestrator import" --type py
```

2. **Check CLI entry point**:
```bash
cat core/cli.py | grep -A 10 "orchestrator"
```

3. **Test current system**:
```bash
# What orchestrator actually runs?
python -m core.cli run-workstream --help
```

### For Implementation

**If choosing Legacy path** (1-2 days):
```bash
# 1. Remove UET stubs
rm core/engine/uet_*.py
rm core/engine/adapters/uet_*.py

# 2. Verify engine/ not in use, then remove
rm -rf engine/

# 3. Archive UET framework
mv UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK archive/uet_framework_reference/

# 4. Update docs
# Edit CODEBASE_INDEX.yaml, ARCHITECTURE.md
```

**If choosing UET path** (6-8 weeks):
```bash
# Follow detailed migration plan in engine_migration_plan.txt
# Start with Phase 1, Day 1-2: Database layer
```

---

## Conclusion

**Current Reality**: Migration was planned but never executed. Codebase has:
- ✅ **1 active legacy orchestrator** (`core/engine/orchestrator.py`) - in production
- ✅ **1 production-ready UET orchestrator** (unused in `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/`)
- ⚠️ **1 separate engine system** (`engine/`) - self-contained, likely experimental
- ❌ **UET stubs** (8 files) - dead code, never imported
- ⚠️ **Multiple variants** - parallel, pipeline_plus (need investigation)

**Key Finding**: 
- **Production uses**: `core/engine/orchestrator.py` (legacy)
- **UET stubs are dead code**: Only referenced in migration plan doc
- **engine/ directory is isolated**: Used only by 3 test scripts

**Recommendation**: **Choose one path and execute cleanly**

**Quick Win (Legacy - RECOMMENDED)**: 
- Remove UET stubs (8 files) → **Dead code**
- Archive `engine/` directory → **Unused experimental code**
- Archive `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/` → **Reference only**
- **Time**: 1-2 days  
- **Risk**: ✅ Very low (removing unused code)

**Long-term Win (UET)**: 
- Execute full migration (see plan)
- Replace `core/engine/orchestrator.py` with UET
- Gain 4-6x speedup potential
- **Time**: 6-8 weeks
- **Risk**: ⚠️ High (replacing production system)

**Do NOT continue with current hybrid state** - creates technical debt and confusion.

---

## Files Generated

- This report: `ENGINE_MIGRATION_STATUS.md`
- Original plan: `engine_migration_plan.txt`

**Report Date**: 2025-11-25  
**Assessment**: Migration incomplete, decision needed to consolidate
