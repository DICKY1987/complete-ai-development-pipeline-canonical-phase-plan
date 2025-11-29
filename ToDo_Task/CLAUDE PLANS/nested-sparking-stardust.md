# Module-Centric Refactor Plan with Execution Patterns

**Document ID**: PLAN-REFACTOR-MODULE-CENTRIC-001
**Date**: 2025-11-26
**Status**: Ready for Execution
**Estimated Time**: 3-5 days (vs 3-4 weeks with manual approach)
**Speedup**: 4-6x via execution patterns + anti-pattern guards

---

## TARGET SUMMARY

### Module-Centric Architecture Principles (Non-Negotiable)

Based on the "Why Module-Centric Works Better" architecture, the final state will be:

1. **Module Boundary Organization** - All related files (code, tests, schemas, docs, state) live in ONE module directory
2. **ULID-Based Identity** - Every module has a unique 6-char ULID prefix (e.g., `01JDEX`) that groups all related artifacts
3. **Atomic Context Units** - AI tools load ONE directory to get complete context (no scattered lookups)
4. **Self-Contained Modules** - Each module directory is independently cloneable, testable, and deployable
5. **Manifest-Driven** - Every module has a `module.manifest.yaml` that defines structure, dependencies, and metadata
6. **Import Safety** - Python import compatibility via hybrid approach (ULID files + clean `__init__.py` re-exports)
7. **Safe Migration** - Old structure archived, not deleted; incremental phases with Git checkpoints
8. **Execution Pattern Driven** - Use EXEC-001 (Batch Creator), EXEC-002 (Module Generator) patterns throughout

### Target Repository Structure

```
modules/
  core-state/                    # Infrastructure layer
    010003_db.py                 # ULID-prefixed implementation
    010003_crud.py
    010003_db.test.py            # Tests colocated
    010003_db.schema.json        # Schemas colocated
    010003_db.md                 # Docs colocated
    010003_module.manifest.yaml  # Module metadata
    __init__.py                  # Clean imports (no ULID in import paths)
    .state/current.json          # Module state

  core-engine/                   # Domain layer
    010001_orchestrator.py
    010001_executor.py
    [... 29 more files ...]
    010001_module.manifest.yaml
    __init__.py
    .state/

  error-plugin-python-ruff/      # UI layer
    010015_plugin.py
    010015_module.manifest.yaml
    __init__.py

legacy/
  structure_archived_2025-11-26/ # Old structure preserved
    core/
    error/
    aim/
    pm/
    specifications/
```

**Key Benefits**:
- **AI Context Loading**: `load_module("modules/core-state/")` gets everything
- **SafePatch Worktrees**: Clone just one module directory
- **Parallel Execution**: Independent modules, no bottlenecks
- **Machine-Verifiable**: ULID prefix links all related files
- **Import Compatibility**: Python imports work via `__init__.py` re-exports

---

## REPO_ANALYSIS

### Current State (Week 2 Complete)

**✅ DONE (Phase 1-2)**:
- 33 modules created in `modules/` directory
- 94 Python files migrated with ULID prefixes (m010000, m010001, etc.)
- 37 module manifests generated (YAML format)
- MODULES_INVENTORY.yaml complete
- Template system operational
- Validation framework (7 gates) passing
- Anti-pattern guards documented

**❌ BLOCKED (Critical Issue)**:
- **Import Incompatibility**: ULID-prefixed files (`m010001_db.py`) cannot be directly imported in Python
- Python syntax error: `from modules.core_state.m010001_db import X` (invalid decimal literal)
- 179 cross-module imports need rewriting
- Old structure (`core/`, `error/`, `aim/`, `pm/`, `specifications/`) still in place (dual structure)
- Tests failing due to import path changes

**⚠️ OVERLAP/DUPLICATION**:
- Original files exist in both old locations AND `modules/` (duplicated code)
- Import statements still reference old paths (`from core.state.db import`)
- Git searches return 4x duplicates (worktree contamination risk)

### Migration Progress by Layer

| Layer | Modules | Files | Manifests | Import Fix | Status |
|-------|---------|-------|-----------|------------|--------|
| **Infrastructure** | 1/1 | 7/7 | ✅ | ❌ | Blocked on imports |
| **Domain** | 5/5 | 49/49 | ✅ | ❌ | Blocked on imports |
| **API** | 6/6 | 16/16 | ✅ | ❌ | Blocked on imports |
| **UI** | 21/21 | 22/22 | ✅ | ❌ | Blocked on imports |
| **TOTAL** | **33/33** | **94/94** | **37/37** | **0/179** | **60% Complete** |

### Gaps vs Target State

1. **Import Strategy** - Need hybrid approach (ULID files + `__init__.py` wrapper)
2. **Import Rewriting** - 179 import statements need conversion
3. **Test Compatibility** - Tests reference old paths
4. **Old Structure Archival** - `core/`, `error/`, etc. not yet archived
5. **Documentation Updates** - Some docs reference old paths

---

## PHASE_PLAN

### Phase 0: Pattern Selection & Guards (1 hour)

**Goal**: Select execution patterns and enable anti-pattern guards

**Execution Pattern**: EXEC-002 (Module Generator) + Hybrid Import Pattern

**Actions**:
1. **Pattern Selection** (15 min)
   - Task: Fix imports for 33 modules
   - Pattern: EXEC-002 (N ≥ 3 modules) + HYBRID_IMPORT_EXECUTION_PATTERN
   - Time estimate: 3-4 hours with pattern (vs 12-15 hours manual)

2. **Enable Anti-Pattern Guards** (15 min)
   - Enable all 11 guards from `ANTI_PATTERN_GUARDS.md`
   - Create `.execution/anti_patterns_checklist.md`
   - Set up validation hooks

3. **Pre-Execution Decisions** (30 min)
   - Format: Python `__init__.py` with wildcard imports
   - Import style: Module-level only (`from modules.X import Y`)
   - Validation: `python -m compileall modules/ -q` must exit 0
   - Success: All 33 modules importable, zero syntax errors
   - NOT deciding: Perfect import organization, optimal performance

**Ground Truth Verification**:
```bash
# Guard checklist exists
test -f .execution/anti_patterns_checklist.md && echo "✅ GUARDS ENABLED"

# Pattern selected
grep "EXEC-002" .execution/current_pattern.txt && echo "✅ PATTERN SELECTED"
```

**Success Criteria**:
- ✅ Pattern documented in `.execution/current_pattern.txt`
- ✅ 11 guards enabled in checklist
- ✅ Pre-decisions documented

---

### Phase 1: Hybrid Import Setup (2-3 hours)

**Goal**: Fix Python import compatibility using hybrid approach

**Execution Pattern**: HYBRID_IMPORT_EXECUTION_PATTERN (EXEC-002 variant)

#### 1.1: Create `__init__.py` Generator Script (30 min)

**Script**: `scripts/create_init_files_v3.py`

**Strategy** (from HYBRID_IMPORT_EXECUTION_PATTERN.md):
```python
# For each module, generate __init__.py with:
# 1. Docstring with module metadata
# 2. Wildcard imports from ULID files: from .010003_db import *
# 3. Module metadata variables
```

**Template**:
```python
"""Module: {module_id}
ULID Prefix: {ulid_prefix}
Layer: {layer}
Files: {file_count}
"""

# Re-export all symbols from ULID-prefixed files
from .010003_db import *
from .010003_crud import *

__module_id__ = "{module_id}"
__ulid_prefix__ = "{ulid_prefix}"
__layer__ = "{layer}"
```

**Ground Truth**:
```bash
# Script exists
python scripts/create_init_files_v3.py --help && echo "✅ SCRIPT EXISTS"
```

#### 1.2: Generate All `__init__.py` Files (30 min)

**Execution**:
```bash
# Dry run first
python scripts/create_init_files_v3.py --all --dry-run

# Execute (batch of 33)
python scripts/create_init_files_v3.py --all --execute
```

**Anti-Pattern Guard Check**:
- Guard #1: Hallucination of Success - Verify programmatically
- Guard #3: Incomplete Implementation - No TODOs in generated files

**Ground Truth**:
```bash
# All 33 __init__.py files created
find modules/ -name "__init__.py" | wc -l  # Expected: 34 (33 modules + modules/)
echo "Expected: 34 files"

# All compile without errors
python -m compileall modules/*/__init__.py -q
echo $?  # Must be 0
```

**Success Criteria**:
- ✅ 34 `__init__.py` files exist (33 modules + root)
- ✅ All compile: `python -m compileall modules/*/__init__.py -q` → exit 0
- ✅ No TODOs or placeholders in generated files

#### 1.3: Create Import Rewriter Script (60 min)

**Script**: `scripts/rewrite_imports_v2.py`

**Strategy**:
- Use string replacement (proven to work, not AST)
- Convert file-level to module-level imports
- Process in batches of 10 modules
- Validate each batch before proceeding
- Rollback on failure

**Conversion Rules** (from MODULES_INVENTORY.yaml):
```yaml
core.state.* → modules.core_state
core.engine.* → modules.core_engine
core.planning.* → modules.core_planning
error.engine.* → modules.error_engine
error.plugins.* → modules.error_plugin_*
aim.environment.* → modules.aim_environment
aim.registry.* → modules.aim_registry
aim.cli.* → modules.aim_cli
pm.* → modules.pm_*
specifications.* → modules.specifications_*
```

**Ground Truth**:
```bash
# Script exists
python scripts/rewrite_imports_v2.py --help && echo "✅ SCRIPT EXISTS"
```

#### 1.4: Batch Import Rewriting (60 min)

**Execution Pattern**: EXEC-001 (Batch File Creator) - Process in batches

**Batch 1: Core modules** (15 min)
```bash
python scripts/rewrite_imports_v2.py --modules "core-*" --dry-run
python scripts/rewrite_imports_v2.py --modules "core-*" --execute
python -m compileall modules/core-* -q && echo "✅ BATCH 1 PASS"
```

**Batch 2: Error modules** (15 min)
```bash
python scripts/rewrite_imports_v2.py --modules "error-*" --dry-run
python scripts/rewrite_imports_v2.py --modules "error-*" --execute
python -m compileall modules/error-* -q && echo "✅ BATCH 2 PASS"
```

**Batch 3: AIM modules** (15 min)
```bash
python scripts/rewrite_imports_v2.py --modules "aim-*" --dry-run
python scripts/rewrite_imports_v2.py --modules "aim-*" --execute
python -m compileall modules/aim-* -q && echo "✅ BATCH 3 PASS"
```

**Batch 4: PM + Specs** (15 min)
```bash
python scripts/rewrite_imports_v2.py --modules "pm-*,specifications-*" --dry-run
python scripts/rewrite_imports_v2.py --modules "pm-*,specifications-*" --execute
python -m compileall modules/pm-*,modules/specifications-* -q && echo "✅ BATCH 4 PASS"
```

**Anti-Pattern Guards**:
- Guard #3: Silent Failures - All subprocess.run() use check=True
- Guard #10: Partial Success Amnesia - Checkpoint after each batch

**Ground Truth Per Batch**:
```bash
# Exit code 0 from compileall
python -m compileall modules/<batch>/ -q
echo $?  # Must be 0

# No syntax errors
python -c "import modules.<module_name>" && echo "✅ IMPORTS"

# Checkpoint created
test -f .execution/checkpoints/batch_<N>_complete.txt && echo "✅ CHECKPOINT"
```

**Success Criteria**:
- ✅ All 4 batches complete with exit code 0
- ✅ All modules compile without syntax errors
- ✅ 4 checkpoint files created
- ✅ Import analysis shows 0 old-style imports remaining

---

### Phase 2: Validation & Testing (1 hour)

**Goal**: Verify all imports work and tests pass

**Execution Pattern**: Ground Truth Verification (from EXECUTION_PATTERNS_MANDATORY.md)

#### 2.1: Ground Truth Validation Gates (30 min)

**Gate 1: All modules compile**
```bash
python -m compileall modules/ -q
echo $?  # Must be 0
```

**Gate 2: Import resolution test**
```python
# scripts/test_imports.py
from modules.core_state import get_connection
from modules.core_engine import Orchestrator
from modules.error_engine import ErrorEngine
from modules.aim_environment import HealthMonitor
from modules.error_plugin_python_ruff import parse

print("✅ All imports successful!")
```

```bash
python scripts/test_imports.py
# Expected: "✅ All imports successful!"
```

**Gate 3: No ULID imports in code**
```bash
# Should return nothing:
grep -r "from modules\.\w\+\.0[0-9]" modules/ || echo "✅ NO ULID IMPORTS"
grep -r "import modules\.\w\+\.0[0-9]" modules/ || echo "✅ NO ULID IMPORTS"
```

**Gate 4: Import analysis verification**
```bash
python scripts/analyze_imports.py modules/ > import_analysis_after.yaml

# Compare before/after
diff import_analysis_report.yaml import_analysis_after.yaml

# Expected: old-style imports reduced to 0
```

**Anti-Pattern Guards**:
- Guard #1: Hallucination of Success - All gates use exit codes
- Guard #6: Test-Code Mismatch - Tests actually run the code

**Success Criteria**:
- ✅ All 4 validation gates pass
- ✅ Exit codes verified programmatically
- ✅ No ULID imports found in grep

#### 2.2: Test Suite Execution (30 min)

**Strategy**: Run existing 196-test suite to verify no regressions

```bash
# Run all tests
python -m pytest tests/ -v

# Expected: 196 passed (same as baseline)
```

**If tests fail**:
1. Identify failing tests
2. Check if they reference old import paths
3. Update test files with import rewriter
4. Re-run tests

**Ground Truth**:
```bash
# Tests pass
python -m pytest tests/ -q
echo $?  # Must be 0

# Coverage maintained
pytest --cov=modules --cov-report=term-missing tests/
# Expected: ≥77% (baseline coverage)
```

**Success Criteria**:
- ✅ All tests pass (196/196 or adjusted count)
- ✅ Coverage ≥77%
- ✅ No import errors in test output

---

### Phase 3: Archive Old Structure (1 hour)

**Goal**: Move old directory structure to archive, make module-centric canonical

**Execution Pattern**: EXEC-001 (Batch File Creator) for archival

#### 3.1: Create Archival Script (15 min)

**Script**: `scripts/archive_old_structure.py`

**Strategy**:
```python
# Move directories to archive with timestamp
# - core/ → archive/structure_archived_2025-11-26/core/
# - error/ → archive/structure_archived_2025-11-26/error/
# - aim/ → archive/structure_archived_2025-11-26/aim/
# - pm/ → archive/structure_archived_2025-11-26/pm/
# - specifications/ → archive/structure_archived_2025-11-26/specifications/
```

**Anti-Pattern Guard**:
- Guard #4: Framework Over-Engineering - Don't create complex archival system, simple move is enough

**Ground Truth**:
```bash
python scripts/archive_old_structure.py --help && echo "✅ SCRIPT EXISTS"
```

#### 3.2: Execute Archival (15 min)

```bash
# Dry run
python scripts/archive_old_structure.py --dry-run

# Execute
python scripts/archive_old_structure.py --execute

# Verify
test -d archive/structure_archived_2025-11-26/core/ && echo "✅ ARCHIVED"
```

**Ground Truth**:
```bash
# Old directories moved
test ! -d core/ && echo "✅ core/ ARCHIVED"
test ! -d error/ && echo "✅ error/ ARCHIVED"
test ! -d aim/ && echo "✅ aim/ ARCHIVED"
test ! -d pm/ && echo "✅ pm/ ARCHIVED"
test ! -d specifications/ && echo "✅ specifications/ ARCHIVED"

# Archive exists
test -d archive/structure_archived_2025-11-26/ && echo "✅ ARCHIVE EXISTS"
ls archive/structure_archived_2025-11-26/ | wc -l  # Expected: 5 directories
```

**Success Criteria**:
- ✅ 5 old directories moved to archive
- ✅ Archive directory created with timestamp
- ✅ Original directories no longer exist in root

#### 3.3: Update Documentation (30 min)

**Files to Update**:
1. `CODEBASE_INDEX.yaml` - Remove old paths, keep only `modules/` references
2. `README.md` - Update import examples
3. `docs/MODULE_CENTRIC_MIGRATION_GUIDE.md` - Mark Phase 4 complete
4. `MIGRATION_FINAL_STATUS.md` - Update with completion status

**Ground Truth**:
```bash
# CODEBASE_INDEX has no old paths
grep "core/" CODEBASE_INDEX.yaml && echo "❌ OLD PATHS REMAIN" || echo "✅ CLEAN"
grep "modules/" CODEBASE_INDEX.yaml && echo "✅ NEW PATHS PRESENT"

# README updated
grep "from modules." README.md && echo "✅ IMPORT EXAMPLES UPDATED"
```

**Success Criteria**:
- ✅ CODEBASE_INDEX.yaml references only `modules/`
- ✅ README has module-centric import examples
- ✅ Migration guide marked complete
- ✅ Final status document updated

---

### Phase 4: Final Validation & Cleanup (1 hour)

**Goal**: Run complete validation suite and clean up temporary files

**Execution Pattern**: Ground Truth Gates (Final Verification)

#### 4.1: Complete Validation Suite (30 min)

**Run All Quality Gates**:
```bash
# 1. Module validation
python scripts/validate_modules.py --all

# 2. Import validation
python scripts/paths_index_cli.py gate --db refactor_paths.db

# 3. Test suite
python -m pytest tests/ -q

# 4. Compilation check
python -m compileall modules/ -q

# 5. Schema validation
python scripts/validate_all_schemas.py

# 6. Anti-pattern guard check
python scripts/enforce_guards.py
```

**Ground Truth**:
```bash
# All scripts exit 0
python scripts/validate_modules.py --all
echo $?  # Must be 0

python scripts/paths_index_cli.py gate --db refactor_paths.db
echo $?  # Must be 0

python -m pytest tests/ -q
echo $?  # Must be 0
```

**Anti-Pattern Guard Scorecard**:
```yaml
✅ hallucination_of_success: 0 violations (saved 12h)
✅ incomplete_implementation: 0 TODOs (saved 5h)
✅ silent_failures: All subprocess.run(check=True) (saved 4h)
✅ framework_over_engineering: No unused infrastructure (saved 10h)
✅ planning_loop_trap: Max 2 iterations (saved 16h)
✅ test_code_mismatch: Tests cover code (saved 6h)
✅ worktree_contamination: No duplicate searches (saved 10h)
✅ configuration_drift: Config classes used (saved 3h)
✅ module_integration_gap: Integration tests pass (saved 2h)
✅ documentation_lies: Types match (saved 3h)
✅ partial_success_amnesia: All checkpoints recorded (saved 12h)

Total waste prevented: 83h
```

**Success Criteria**:
- ✅ All 6 validation scripts pass with exit code 0
- ✅ All 11 anti-pattern guards show 0 violations
- ✅ No TODOs or placeholders in committed code

#### 4.2: Cleanup & Git Commit (30 min)

**Cleanup Actions**:
```bash
# Remove temporary worktrees (Guard #11)
git worktree list
git worktree remove .worktrees/<name>  # For any unused worktrees

# Clean up execution artifacts
rm -rf .execution/checkpoints/  # Temporary checkpoints

# Clean Python cache
find modules/ -type d -name "__pycache__" -exec rm -rf {} +
```

**Git Commit**:
```bash
git add modules/
git add archive/structure_archived_2025-11-26/
git add scripts/
git add CODEBASE_INDEX.yaml README.md docs/

git commit -m "$(cat <<'EOF'
refactor: Complete module-centric migration (Phase 1-4)

- Hybrid import strategy: ULID files + clean __init__.py
- All 33 modules with working imports
- 94 Python files migrated
- 179 import statements rewritten
- Old structure archived to archive/structure_archived_2025-11-26/
- All 196 tests passing
- All validation gates passing

Anti-pattern waste prevented: 83h
Time savings: 4-6x faster than manual migration

Pattern: EXEC-002 (Module Generator) + HYBRID_IMPORT_EXECUTION_PATTERN

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Ground Truth**:
```bash
# Commit succeeded
git log -1 --oneline | grep "module-centric migration" && echo "✅ COMMITTED"

# No untracked files (except intentional)
git status --short | grep "^??" && echo "⚠️ UNTRACKED FILES" || echo "✅ CLEAN"

# Archive exists in git
git ls-files archive/structure_archived_2025-11-26/ | wc -l
# Expected: >50 files
```

**Success Criteria**:
- ✅ Git commit created with descriptive message
- ✅ Archive included in commit
- ✅ No accidental untracked files
- ✅ Worktrees cleaned up

---

## IMPORT_STRATEGY

### Hybrid Approach (RECOMMENDED)

**Problem**: Python cannot import files starting with digits (`from modules.core_state.010003_db` is SyntaxError)

**Solution**: Keep ULID files for identity, use `__init__.py` for clean imports

### File Structure

```
modules/core-state/
  010003_db.py              # ULID implementation file (for identity)
  010003_crud.py            # ULID implementation file
  010003_db.test.py         # ULID test file
  010003_module.manifest.yaml
  __init__.py               # Clean import wrapper (see below)
  .state/current.json
```

### `__init__.py` Pattern

```python
"""Module: core-state
ULID Prefix: 010003
Layer: infrastructure
Files: 2
"""

# Re-export all symbols from ULID-prefixed files
from .010003_db import *
from .010003_crud import *

# Module metadata
__module_id__ = "core-state"
__ulid_prefix__ = "010003"
__layer__ = "infrastructure"
```

### Import Examples

**✅ Correct (Module-Level)**:
```python
# Import from module (no ULID in path)
from modules.core_state import get_connection, init_db
from modules.core_engine import Orchestrator
from modules.error_engine import ErrorEngine
```

**❌ Incorrect (File-Level with ULID)**:
```python
# This causes SyntaxError
from modules.core_state.010003_db import get_connection  # ❌ INVALID
```

### Mapping: Old → New

| Old Import Path | New Import Path |
|----------------|-----------------|
| `from core.state.db import X` | `from modules.core_state import X` |
| `from core.engine.orchestrator import Y` | `from modules.core_engine import Y` |
| `from error.engine.error_engine import Z` | `from modules.error_engine import Z` |
| `from aim.environment.health import A` | `from modules.aim_environment import A` |
| `from error.plugins.python_ruff.plugin import B` | `from modules.error_plugin_python_ruff import B` |

### Benefits of Hybrid Approach

1. **ULID Identity Preserved** - Files keep ULID names for human/AI recognition
2. **Python Compatibility** - Imports use clean module names (no syntax errors)
3. **AI Context Loading** - ULID prefix still groups related files visually
4. **Simple Migration** - String replacement for import rewriting
5. **Backwards Compatible** - Can support both styles during transition

---

## AUTOMATION_PLAN

### Scripts to Create

#### 1. `scripts/create_init_files_v3.py`

**Purpose**: Generate `__init__.py` files with wildcard imports from ULID files

**Input**: MODULES_INVENTORY.yaml

**Output**: 34 `__init__.py` files (33 modules + root)

**Key Features**:
- Read module inventory
- For each module, find all `{ULID}_*.py` files
- Generate `from .{ULID}_filename import *` statements
- Add module metadata variables
- Validate imports resolve

**Time**: 30 min to create, 2 min to run

**Ground Truth**: `python -m compileall modules/*/__init__.py -q` → exit 0

#### 2. `scripts/rewrite_imports_v2.py`

**Purpose**: Rewrite old import paths to module-level imports

**Input**: Conversion rules from MODULES_INVENTORY.yaml

**Output**: Updated Python files with new imports

**Key Features**:
- Load conversion rules from inventory
- Use string replacement (not AST - proven reliable)
- Process in batches of 10 modules
- Validate each batch before proceeding
- Rollback on failure (Git restore)
- Create checkpoint after each batch

**Time**: 60 min to create, 10 min to run (4 batches × 2.5 min)

**Ground Truth**: `python -m compileall modules/<batch>/ -q` → exit 0 per batch

#### 3. `scripts/create_modules_root_init.py`

**Purpose**: Create `modules/__init__.py` with all module names

**Input**: MODULES_INVENTORY.yaml

**Output**: `modules/__init__.py`

**Key Features**:
- List all 33 modules in `__all__`
- Add package docstring
- Include import guidelines

**Time**: 15 min to create, 1 min to run

**Ground Truth**: File exists and imports work

#### 4. `scripts/test_imports.py`

**Purpose**: Test that key imports resolve correctly

**Input**: None (hardcoded test imports)

**Output**: Success message or import errors

**Key Features**:
- Import from 5-10 representative modules
- Cover all layers (infra, domain, api, ui)
- Print clear success/failure message

**Time**: 10 min to create, 5 sec to run

**Ground Truth**: Prints "✅ All imports successful!" and exits 0

#### 5. `scripts/archive_old_structure.py`

**Purpose**: Move old directory structure to archive

**Input**: List of directories to archive

**Output**: Moved directories in `archive/structure_archived_<date>/`

**Key Features**:
- Create timestamped archive directory
- Move (not copy) old directories
- Verify move completed
- Print summary

**Time**: 15 min to create, 30 sec to run

**Ground Truth**: Old directories gone, archive exists with 5 subdirectories

#### 6. `scripts/validate_migration_complete.py`

**Purpose**: Run all validation gates in sequence

**Input**: None

**Output**: Pass/fail status for each gate

**Key Features**:
- Run 6 validation scripts
- Collect exit codes
- Print scorecard
- Exit 0 if all pass, exit 1 if any fail

**Time**: 20 min to create, 2 min to run

**Ground Truth**: Exits 0, prints "✅ ALL GATES PASSED"

---

## RISKS_AND_ANTIPATTERNS

### Top 10 Risks

#### 1. **Import Rewriting Breaks Code** (HIGH)
- **Risk**: String replacement changes unintended code
- **Mitigation**: Batch processing with validation gates per batch
- **Rollback**: `git restore modules/<batch>/` if batch fails
- **Detection**: Compilation errors in batch validation

#### 2. **Tests Fail After Import Changes** (HIGH)
- **Risk**: Tests still reference old import paths
- **Mitigation**: Run import rewriter on test files too
- **Rollback**: Restore test files from Git
- **Detection**: pytest exit code ≠ 0

#### 3. **Partial Migration State** (MEDIUM)
- **Risk**: Some modules work, others broken (Guard #10)
- **Mitigation**: Checkpoint after each batch, validate before next
- **Rollback**: Restore from last checkpoint
- **Detection**: Compilation fails for some but not all modules

#### 4. **Worktree Contamination** (MEDIUM - Guard #7)
- **Risk**: Git searches return 4x duplicates, slow performance
- **Mitigation**: Clean up worktrees after Phase 4 completion
- **Rollback**: `git worktree remove <name>`
- **Detection**: `git worktree list` shows unused worktrees

#### 5. **Archive Corruption** (MEDIUM)
- **Risk**: Old files accidentally deleted instead of moved
- **Mitigation**: Use move (not delete), verify archive before removing originals
- **Rollback**: Restore from archive/
- **Detection**: Old directories missing, archive incomplete

#### 6. **Hallucination of Success** (HIGH - Guard #1)
- **Risk**: Marking complete without programmatic verification
- **Mitigation**: All validation uses exit codes, no subjective "looks good"
- **Detection**: Manual review of validation scripts for `check=True`

#### 7. **Silent Import Failures** (MEDIUM - Guard #3)
- **Risk**: Code compiles but imports fail at runtime
- **Mitigation**: Run import test script that actually imports modules
- **Detection**: `scripts/test_imports.py` catches runtime import errors

#### 8. **Configuration Drift** (LOW - Guard #8)
- **Risk**: Hardcoded paths in scripts break on different machines
- **Mitigation**: Use Path objects, load config from MODULES_INVENTORY.yaml
- **Detection**: Script fails on different developer machine

#### 9. **Documentation Out of Sync** (LOW - Guard #9)
- **Risk**: Docs still reference old paths after migration
- **Mitigation**: Grep docs for old paths, update in Phase 3.3
- **Detection**: `grep "from core\." docs/*.md`

#### 10. **Incomplete Implementation** (MEDIUM - Guard #2)
- **Risk**: Scripts have TODO placeholders, don't actually work
- **Mitigation**: No TODOs allowed in committed code, test all scripts before use
- **Detection**: `grep "# TODO" scripts/*.py`

### Anti-Patterns to Avoid

#### ❌ **Planning Loop Trap** (Guard #5)
- **Anti-Pattern**: Spending hours planning perfect import strategy
- **Correct Pattern**: Make decision once (hybrid approach), execute in batches
- **Time Saved**: 16h

#### ❌ **Sequential Execution**
- **Anti-Pattern**: Migrating modules one at a time with verification per module
- **Correct Pattern**: Batch of 10 modules → validate batch → next batch
- **Time Saved**: 4x faster

#### ❌ **Framework Over-Engineering** (Guard #4)
- **Anti-Pattern**: Creating complex import rewriting AST parser
- **Correct Pattern**: Simple string replacement (proven to work)
- **Time Saved**: 10h

#### ❌ **Approval Loop**
- **Anti-Pattern**: Ask user approval for each script before running
- **Correct Pattern**: Dry-run first, then execute with validation gates
- **Time Saved**: 12h

#### ❌ **Perfectionist Imports**
- **Anti-Pattern**: Organizing imports alphabetically, removing unused, etc.
- **Correct Pattern**: Just make them work (module-level), optimize later
- **Time Saved**: 5h

#### ❌ **Test-Code Mismatch** (Guard #6)
- **Anti-Pattern**: Tests that only check `assert result is not None`
- **Correct Pattern**: Tests actually import modules and use functions
- **Time Saved**: 6h

#### ❌ **No Checkpoints** (Guard #10)
- **Anti-Pattern**: Running all 4 batches without intermediate validation
- **Correct Pattern**: Checkpoint after each batch, validate before next
- **Time Saved**: 12h

#### ❌ **Manual Import Updates**
- **Anti-Pattern**: Editing import statements by hand across 94 files
- **Correct Pattern**: Use import rewriter script with batch processing
- **Time Saved**: 12h

#### ❌ **Ignoring Guard Violations**
- **Anti-Pattern**: Skipping guard enforcement script
- **Correct Pattern**: Run `enforce_guards.py` before final commit
- **Time Saved**: 43h total waste prevention

#### ❌ **Duplicating Old and New Structure**
- **Anti-Pattern**: Leaving both old and new structures in place indefinitely
- **Correct Pattern**: Archive old structure once migration validated
- **Time Saved**: Prevents ongoing confusion and maintenance burden

---

## NEXT_ACTIONS

### First 3 Concrete Steps (START TODAY)

#### Step 1: Enable Anti-Pattern Guards (15 minutes)

**Action**: Create guard checklist and enable enforcement

```bash
# Create execution directory
mkdir -p .execution/checkpoints

# Create guard checklist
cat > .execution/anti_patterns_checklist.md <<'EOF'
# Anti-Pattern Guard Checklist

## Before Each Commit
- [ ] No TODOs in committed code
- [ ] All subprocess.run() use check=True
- [ ] All scripts have been tested
- [ ] Exit codes verified programmatically

## Before Batch Execution
- [ ] Checkpoint created after each batch
- [ ] Validation gate passes before next batch
- [ ] Dry-run completed first

## Before Final Commit
- [ ] All 11 guards passing
- [ ] No duplicate files in searches
- [ ] Worktrees cleaned up
- [ ] Documentation updated
EOF

# Document pattern selection
echo "EXEC-002 (Module Generator) + HYBRID_IMPORT_EXECUTION_PATTERN" > .execution/current_pattern.txt

# Verify
test -f .execution/anti_patterns_checklist.md && echo "✅ GUARDS ENABLED"
test -f .execution/current_pattern.txt && echo "✅ PATTERN SELECTED"
```

**Ground Truth**: Both files exist

**Time**: 15 minutes

#### Step 2: Create `__init__.py` Generator Script (30 minutes)

**Action**: Implement `scripts/create_init_files_v3.py` using template pattern

```bash
# Create script skeleton
python scripts/create_init_files_v3.py --help

# Expected output: Usage message with --all, --dry-run, --execute options
```

**Implementation Checklist**:
- [ ] Load MODULES_INVENTORY.yaml
- [ ] For each module, find ULID-prefixed `.py` files
- [ ] Generate `from .{ULID}_filename import *` statements
- [ ] Create docstring with module metadata
- [ ] Add `__module_id__`, `__ulid_prefix__`, `__layer__` variables
- [ ] Support `--dry-run` and `--execute` modes
- [ ] Use `subprocess.run(check=True)` for validation (Guard #1)

**Ground Truth**:
```bash
# Script exists
test -f scripts/create_init_files_v3.py && echo "✅ SCRIPT EXISTS"

# Help works
python scripts/create_init_files_v3.py --help && echo "✅ HELP WORKS"

# Dry-run works
python scripts/create_init_files_v3.py --all --dry-run && echo "✅ DRY-RUN WORKS"
```

**Time**: 30 minutes

#### Step 3: Generate `__init__.py` Files (30 minutes)

**Action**: Execute generator script and validate output

```bash
# Dry-run first (Guard #11: No approval loop, but verify first)
python scripts/create_init_files_v3.py --all --dry-run

# Review output (should show 34 files to be created)

# Execute
python scripts/create_init_files_v3.py --all --execute

# Validate (Guard #1: Programmatic verification)
find modules/ -name "__init__.py" | wc -l  # Expected: 34
python -m compileall modules/*/__init__.py -q
echo $?  # Must be 0

# Create checkpoint (Guard #10: Partial Success Amnesia)
echo "Phase 1.2 Complete: All __init__.py files created" > .execution/checkpoints/init_files_complete.txt
date >> .execution/checkpoints/init_files_complete.txt
```

**Ground Truth**:
```bash
# Files created
test $(find modules/ -name "__init__.py" | wc -l) -eq 34 && echo "✅ 34 FILES CREATED"

# All compile
python -m compileall modules/*/__init__.py -q && echo "✅ ALL COMPILE"

# Checkpoint exists
test -f .execution/checkpoints/init_files_complete.txt && echo "✅ CHECKPOINT"
```

**Time**: 30 minutes

---

## EXECUTION_PATTERNS_INTEGRATION

### Pattern: EXEC-002 (Module Generator)

**Applied To**: All 33 modules import fix

**Phases**:
1. **Discovery** (already done) - MODULES_INVENTORY.yaml exists
2. **Template** (30 min) - Create `__init__.py` template
3. **Batch** (2-3 hours) - Generate all files + rewrite imports in batches
4. **Verification** (30 min) - Ground truth validation gates

### Pattern: HYBRID_IMPORT_EXECUTION_PATTERN

**Applied To**: Import compatibility fix

**Pre-Decisions**:
- ✅ Approach: Hybrid (ULID files + clean `__init__.py`)
- ✅ Import style: Module-level only
- ✅ File handling: Keep ULID files, `__init__.py` re-exports
- ✅ Validation: `python -m compileall modules/ -q` exit 0
- ✅ Success: All 33 modules importable, zero syntax errors

**NOT Decisions**:
- ❌ Perfect import organization
- ❌ Optimal performance
- ❌ Future-proof design
- ❌ Comprehensive testing of every function
- ❌ Documentation updates (do after imports work)

### Pattern: EXEC-001 (Batch File Creator)

**Applied To**: Import rewriting across 94 Python files

**Batch Size**: 10 modules per batch (4 batches total)

**Execution**:
1. Load template ONCE (conversion rules)
2. Load ALL context UPFRONT (no mid-batch lookups)
3. Generate batch of 10 module updates in SINGLE operation
4. Verify ALL items at END (batch verification)
5. Move to next batch

### Anti-Pattern Guards (11 Guards Active)

**Tier 1 Critical** (Save 21h):
1. Hallucination of Success (12h saved)
2. Incomplete Implementation (5h saved)
3. Silent Failures (4h saved)

**Tier 2 High Priority** (Save 22h):
4. Framework Over-Engineering (10h saved)
5. Planning Loop Trap (16h saved) - Max 2 iterations
6. Test-Code Mismatch (6h saved)

**Tier 3 Medium Priority** (Save 40h):
7. Worktree Contamination (10h saved)
8. Configuration Drift (3h saved)
9. Module Integration Gap (2h saved)
10. Documentation Lies (3h saved)
11. Partial Success Amnesia (12h saved)

**Total Waste Prevented**: 83 hours

---

## SUCCESS_METRICS

### Completion Criteria

**Phase 1: Hybrid Import Setup**
- ✅ 34 `__init__.py` files created
- ✅ All compile: `python -m compileall modules/*/__init__.py -q` → exit 0
- ✅ Import rewriter script created and tested
- ✅ All 4 batches complete with exit code 0
- ✅ 4 checkpoints created

**Phase 2: Validation & Testing**
- ✅ All 4 validation gates pass
- ✅ All tests pass (196/196 or adjusted)
- ✅ Coverage ≥77%
- ✅ No ULID imports in code

**Phase 3: Archive Old Structure**
- ✅ 5 old directories moved to archive
- ✅ CODEBASE_INDEX.yaml references only `modules/`
- ✅ Documentation updated (4 files)

**Phase 4: Final Validation**
- ✅ All 6 validation scripts pass with exit code 0
- ✅ All 11 anti-pattern guards show 0 violations
- ✅ Git commit created
- ✅ Worktrees cleaned up

### Time Savings Calculation

**Manual Approach** (no patterns):
- 33 modules × 20 min/module = 11 hours
- Import debugging: 4 hours
- Testing: 2 hours
- Archive old structure: 2 hours
- Documentation: 2 hours
- **Total: 21 hours**

**Pattern Approach**:
- Guard setup: 1 hour
- Template creation: 1 hour
- Batch execution: 3 hours
- Validation: 1 hour
- Archive & docs: 1 hour
- **Total: 7 hours**

**Speedup**: 3x faster (14 hours saved)

**Anti-Pattern Waste Prevented**: 83 hours

**Combined Total Savings**: 97 hours

---

## ROLLBACK_STRATEGY

### Per-Phase Rollback

**Phase 1: Import Setup**
- **If init file generation fails**: Delete `modules/*/__init__.py`, restore from Git
- **If batch N fails**: `git restore modules/<batch>/`, fix conversion rules, retry
- **Restore point**: `.execution/checkpoints/batch_<N-1>_complete.txt`

**Phase 2: Validation**
- **If tests fail**: Restore test files from Git, fix import paths in tests
- **If validation gates fail**: Review gate output, fix specific issues
- **Restore point**: `.execution/checkpoints/init_files_complete.txt`

**Phase 3: Archive**
- **If archive fails**: Restore old directories from `archive/structure_archived_*/`
- **If documentation update breaks**: `git restore docs/ README.md CODEBASE_INDEX.yaml`
- **Restore point**: Git commit before Phase 3

**Phase 4: Final**
- **If validation fails**: Review all phases, identify regression
- **If commit issues**: Amend commit or create fixup commit
- **Restore point**: Git commit before Phase 4

### Complete Rollback (Emergency)

```bash
# Restore entire repo to pre-migration state
git reset --hard <commit_before_migration>

# Verify old structure exists
test -d core/ && echo "✅ RESTORED"
test -d modules/ && echo "⚠️ NEW STRUCTURE STILL EXISTS" || echo "✅ CLEAN"

# Remove modules/ if needed
rm -rf modules/
```

---

## FINAL_NOTES

### Execution Pattern Benefits

1. **Decision Elimination** - Make structural decisions once (hybrid approach), apply 33 times
2. **Batch Processing** - 4 batches of 10 modules vs 33 individual migrations
3. **Ground Truth Verification** - Exit codes and programmatic checks, no subjective quality
4. **Anti-Pattern Guards** - 83 hours waste prevention
5. **Template-Driven** - Consistent output across all modules

### Critical Success Factors

1. **Follow Execution Patterns** - EXEC-002, HYBRID_IMPORT, EXEC-001
2. **Enable All Guards** - 11 guards prevent 83h waste
3. **Batch with Validation** - Validate each batch before proceeding
4. **Trust Ground Truth** - Exit codes over "looks good"
5. **Checkpoint Progress** - Guard #10: Partial Success Amnesia

### Estimated Timeline

- **Day 1**: Phase 0-1 (Guards + Import Setup) - 3 hours
- **Day 2**: Phase 2 (Validation + Testing) - 2 hours
- **Day 3**: Phase 3 (Archive + Docs) - 2 hours
- **Day 4**: Phase 4 (Final Validation) - 1 hour

**Total**: 3-4 days (vs 3-4 weeks manual)

**Speedup**: 4-6x faster

---

**STATUS**: Ready for execution
**NEXT**: Execute Step 1 (Enable Guards) - 15 minutes
**PATTERN**: EXEC-002 + HYBRID_IMPORT_EXECUTION_PATTERN
**GUARDS**: All 11 enabled
