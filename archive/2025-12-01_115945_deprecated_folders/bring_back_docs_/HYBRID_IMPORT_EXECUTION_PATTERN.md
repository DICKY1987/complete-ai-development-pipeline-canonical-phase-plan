---
doc_id: DOC-GUIDE-HYBRID-IMPORT-EXECUTION-PATTERN-234
---

# Hybrid Import Strategy - Execution Pattern

**Date**: 2025-11-26  
**Pattern**: EXEC-002 (Code Module Generator) + EXEC-001 (Batch File Creator)  
**Goal**: Fix Python import compatibility for ULID-prefixed modules  
**Time Estimate**: 3-4 hours (vs 12-15 hours manual)

---

## Pre-Decisions (Made Once, Applied N Times)

### Structural Decisions ✅
- **Approach**: Hybrid (ULID files + clean `__init__.py` imports)
- **Import style**: Module-level only (`from modules.X import Y`)
- **File handling**: Keep ULID files, `__init__.py` re-exports ALL symbols
- **Validation**: `python -m compileall modules/ -q` must exit 0
- **Success metric**: All 33 modules importable, zero syntax errors

### Format Decisions ✅
- **__init__.py format**: Python with docstring + wildcard imports
- **Import rewrite**: String-based (not AST)
- **Ground truth**: File compiles + imports resolve

### NOT Decisions (Don't Waste Time) ❌
- Perfect import organization
- Optimal performance
- Future-proof design
- Comprehensive testing of every function
- Documentation updates (do after imports work)

---

## The 4-Phase Pattern

### PHASE 1: DISCOVERY (Already Done ✅)

**Status**: Complete from Week 2 analysis
- 33 modules with ULID files
- 179 cross-module imports identified
- Import patterns analyzed

---

### PHASE 2: TEMPLATE (30 minutes)

#### 2.1 Create `__init__.py` Template

**Template**: `templates/module_init.py.template`

```python
"""Module: {module_id}

ULID Prefix: {ulid_prefix}
Layer: {layer}
Files: {file_count}

This module re-exports all symbols from ULID-prefixed files.
"""

# Re-export all symbols from ULID-prefixed files
{import_statements}

# Module metadata
__module_id__ = "{module_id}"
__ulid_prefix__ = "{ulid_prefix}"
__layer__ = "{layer}"
```

**Variables**:
- `{module_id}`: e.g., "core-state"
- `{ulid_prefix}`: e.g., "010003"
- `{layer}`: e.g., "infrastructure"
- `{file_count}`: Number of Python files
- `{import_statements}`: Generated from file list

#### 2.2 Create Import Rewrite Template

**Pattern**: Replace old module paths with new module paths

```python
# OLD:
from core.state.db import get_connection
from error.engine.error_engine import ErrorEngine

# NEW:
from modules.core_state import get_connection
from modules.error_engine import ErrorEngine
```

**Decision**: Module-level imports only (not file-level)

---

### PHASE 3: BATCH (2-3 hours)

#### 3.1 Regenerate `__init__.py` Files (30 min)

**Script**: `scripts/create_init_files_v2.py`

```python
"""
Generate proper __init__.py files that import from ULID files.

Strategy:
1. For each module, find all {ULID}_*.py files
2. Generate: from .{ULID}_filename import *
3. Validate: Imports resolve correctly
"""
```

**Execution**:
```bash
python scripts/create_init_files_v2.py --all --execute
```

**Ground Truth**:
- 33 `__init__.py` files created
- Each contains `from .{ULID}_* import *` statements
- All compile without syntax errors

#### 3.2 Rewrite Import Statements (90 min)

**Script**: `scripts/rewrite_imports_v2.py`

**Strategy**:
1. Use simple string replacement (proven to work)
2. Convert file-level to module-level imports
3. Process in batches of 10 modules
4. Validate each batch before proceeding

**Conversion Rules** (from MODULES_INVENTORY.yaml):
```yaml
# Core modules
core.state.* → modules.core_state
core.engine.* → modules.core_engine
core.planning.* → modules.core_planning

# Error modules
error.engine.* → modules.error_engine
error.plugins.* → modules.error_plugin_*

# AIM modules
aim.environment.* → modules.aim_environment
aim.registry.* → modules.aim_registry
aim.cli.* → modules.aim_cli

# PM modules
pm.* → modules.pm_*

# Specifications
specifications.* → modules.specifications_*
```

**Execution Pattern**:
```bash
# Batch 1: Core modules (highest dependency)
python scripts/rewrite_imports_v2.py --modules "core-*" --execute

# Validate batch 1
python -m compileall modules/core-* -q

# Batch 2: Error modules
python scripts/rewrite_imports_v2.py --modules "error-*" --execute
python -m compileall modules/error-* -q

# Batch 3: AIM modules
python scripts/rewrite_imports_v2.py --modules "aim-*" --execute
python -m compileall modules/aim-* -q

# Batch 4: PM + Specs
python scripts/rewrite_imports_v2.py --modules "pm-*,specifications-*" --execute
python -m compileall modules/pm-*,modules/specifications-* -q
```

**Ground Truth per Batch**:
- Exit code 0 from compileall
- No syntax errors
- Imports resolve (manual spot check 2 files)

#### 3.3 Create modules/__init__.py (15 min)

**File**: `modules/__init__.py`

```python
"""
Modules package - Module-centric architecture.

All 33 modules are organized here with ULID-based file naming.
Import from module level, not file level:

    from modules.core_state import get_connection  # ✅
    from modules.core_state.010003_db import get_connection  # ❌
"""

# Make modules discoverable
__all__ = [
    'core_state',
    'core_engine',
    'core_planning',
    'core_ast',
    'error_engine',
    # ... all 33 modules
]
```

**Execution**:
```bash
python scripts/create_modules_root_init.py
```

---

### PHASE 4: TRUST (30 minutes)

#### 4.1 Ground Truth Validation

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

print("All imports successful!")
```

```bash
python scripts/test_imports.py
# Expected: "All imports successful!"
```

**Gate 3: No ULID imports in code**
```bash
# Should return nothing:
grep -r "from modules\.\w\+\.0[0-9]" modules/ 

# Should return nothing:
grep -r "import modules\.\w\+\.0[0-9]" modules/
```

#### 4.2 Spot Check (5 modules)

Manually verify:
1. `modules/core-state/__init__.py` - Has all imports
2. `modules/core-engine/010001_orchestrator.py` - Uses module-level imports
3. `modules/error-engine/010004_error_engine.py` - Uses module-level imports
4. `modules/aim-environment/01001B_health.py` - Uses module-level imports
5. `modules/error-plugin-python-ruff/010015_plugin.py` - Clean (no cross-module imports)

#### 4.3 Final Validation

```bash
# Run full import analysis again
python scripts/analyze_imports.py modules/ > import_analysis_after.yaml

# Compare before/after
diff import_analysis_report.yaml import_analysis_after.yaml

# Expected: project_* imports reduced to 0, modules.* imports increased
```

---

## Execution Scripts to Create

### 1. `scripts/create_init_files_v2.py`

**Purpose**: Generate proper `__init__.py` with wildcard imports from ULID files

**Key features**:
- Read MODULES_INVENTORY.yaml
- For each module, find all `{ULID}_*.py` files
- Generate `from .{ULID}_filename import *`
- Validate imports resolve

**Time**: 30 min to create, 2 min to run

### 2. `scripts/rewrite_imports_v2.py`

**Purpose**: Rewrite old imports to module-level

**Key features**:
- Load conversion rules from MODULES_INVENTORY.yaml
- Use string replacement (not AST)
- Process in batches
- Validate each batch
- Rollback on failure

**Time**: 60 min to create, 10 min to run

### 3. `scripts/create_modules_root_init.py`

**Purpose**: Create `modules/__init__.py` with all module names

**Time**: 15 min to create, 1 min to run

### 4. `scripts/test_imports.py`

**Purpose**: Test that key imports resolve correctly

**Time**: 10 min to create, 5 sec to run

---

## Batch Execution Plan

### Hour 1: Template Creation
- [ ] Create `create_init_files_v2.py` (30 min)
- [ ] Create `rewrite_imports_v2.py` (30 min)

### Hour 2: First Execution Pass
- [ ] Run `create_init_files_v2.py --all --dry-run` (2 min)
- [ ] Review output, fix issues (10 min)
- [ ] Run `create_init_files_v2.py --all --execute` (2 min)
- [ ] Validate: `python -m compileall modules/*/__ init__.py -q` (1 min)
- [ ] Create `rewrite_imports_v2.py` (30 min if not done in Hour 1)
- [ ] Test on one module (15 min)

### Hour 3: Batch Import Rewriting
- [ ] Batch 1: Core modules (15 min)
- [ ] Batch 2: Error modules (15 min)
- [ ] Batch 3: AIM modules (10 min)
- [ ] Batch 4: PM + Specs (10 min)
- [ ] Create modules root init (10 min)

### Hour 4: Validation & Testing
- [ ] Run all validation gates (15 min)
- [ ] Spot check 5 modules (15 min)
- [ ] Run import test script (5 min)
- [ ] Re-run import analysis (5 min)
- [ ] Commit and document (20 min)

---

## Success Criteria (Ground Truth)

### Must Have ✅
1. All 33 modules compile: `python -m compileall modules/ -q` → exit 0
2. Key imports work: `python scripts/test_imports.py` → "All imports successful!"
3. No ULID in import paths: `grep` returns nothing
4. Import analysis shows 0 `project_*` imports

### Nice to Have 📋
1. Documentation updated
2. Tests run (if they exist)
3. Original files archived

### Don't Need ❌
1. Perfect import organization
2. Optimal performance testing
3. Comprehensive documentation updates
4. Test coverage improvements

---

## Rollback Plan

If any batch fails:
1. Restore from git: `git checkout modules/`
2. Re-run that batch with `--dry-run`
3. Fix conversion rules
4. Try again

---

## Time Savings Calculation

**Manual approach** (no patterns):
- 33 modules × 20 min/module = 11 hours
- Import debugging: 4 hours
- Testing: 2 hours
- **Total: 17 hours**

**Pattern approach**:
- Template creation: 1 hour
- Batch execution: 2 hours
- Validation: 1 hour
- **Total: 4 hours**

**Savings: 76% (13 hours saved)**

---

## Next Action

Start with Hour 1: Create the two main scripts following the template patterns.

**Command to begin**:
```bash
# Create the script skeletons
python scripts/create_init_files_v2.py --help  # Should exist after creation
python scripts/rewrite_imports_v2.py --help     # Should exist after creation
```
