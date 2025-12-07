---
doc_id: DOC-PAT-EXEC-016-IMPORT-PATH-STANDARDIZER-862
---

# EXEC-016: Import Path Standardizer

**Pattern ID:** EXEC-016
**Pattern Name:** Import Path Standardizer
**Version:** 1.0.0
**Category:** migration
**Confidence:** 100%
**Auto-Approval:** YES
**Estimated Time:** ~45 minutes
**Priority:** P0

---

## Purpose

Systematically update all Python imports to use canonical paths pointing to `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/`. This eliminates import ambiguity, improves AI navigation clarity, and establishes a single source of truth for all modules.

---

## Problem Statement

The codebase currently has **multiple import patterns** for the same functionality:

```python
# Problem: 4 different ways to import the same orchestrator
from core.orchestrator import Orchestrator              # Shim layer
from modules.core_engine import Orchestrator            # ULID module
from modules.core_engine.m010001_orchestrator import *  # ULID file
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine import Orchestrator  # Canonical
```

**Impact:**
- AI tools confused about which import to use
- Developers unsure which path is canonical
- Import graph complexity (4x paths for same module)
- 300+ files need standardization

---

## Solution

Automated, batched migration of all imports to canonical `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/` paths using:
1. **Migration mapping** (old path → new path)
2. **Dependency ordering** (leaf modules → root modules)
3. **Batched execution** (25 files per commit for safety)
4. **Per-batch testing** (ensure no breakage)
5. **Shim preservation** (30-day compatibility window)

---

## Inputs

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `migration_map_file` | `Path` | Yes | `config/import_migration_map.yaml` | Mapping of old → new import paths |
| `batch_size` | `int` | No | `25` | Files per batch/commit |
| `dry_run` | `bool` | No | `false` | Report only, no modifications |
| `preserve_shims` | `bool` | No | `true` | Keep compatibility shims for 30 days |
| `test_after_batch` | `bool` | No | `true` | Run tests after each batch |

---

## Migration Map

```yaml
# config/import_migration_map.yaml
migrations:
  # Core engine imports
  - old_pattern: "^from core\\.orchestrator import"
    new_pattern: "from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine import"
    confidence: 100

  - old_pattern: "^from core\\.executor import"
    new_pattern: "from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine import"
    confidence: 100

  - old_pattern: "^from core\\.scheduler import"
    new_pattern: "from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine import"
    confidence: 100

  # Error engine imports
  - old_pattern: "^from error\\.engine import"
    new_pattern: "from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.engine import"
    confidence: 100

  - old_pattern: "^from error\\.shared\\.utils import"
    new_pattern: "from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.shared.utils import"
    confidence: 100

  # Module imports (ULID-prefixed)
  - old_pattern: "^from modules\\.core_engine import"
    new_pattern: "from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine import"
    confidence: 100

  - old_pattern: "^from modules\\.error_shared import"
    new_pattern: "from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.shared.utils import"
    confidence: 100

  # Deprecated patterns (block these)
  - old_pattern: "^from src\\.pipeline"
    action: "block"
    message: "Deprecated: use UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core"

  - old_pattern: "^from MOD_ERROR_PIPELINE"
    action: "block"
    message: "Deprecated: use UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error"
```

---

## Execution Flow

### Phase 1: Discovery & Analysis (5 minutes)

**Action:** Identify all files needing import updates

**Steps:**
1. Scan Python files for import statements
2. Match against `migration_map` patterns
3. Build dependency graph (which files import which)
4. Determine execution order (leaf-first topology sort)
5. Group files into batches (25 files each)

**Output:**
```json
{
  "files_to_update": 312,
  "total_import_changes": 847,
  "batches": [
    {
      "batch_id": 1,
      "files": ["tests/test_orchestrator.py", ...],
      "import_count": 34,
      "dependency_level": 0
    },
    ...
  ],
  "estimated_commits": 13
}
```

### Phase 2: Batched Migration (30 minutes)

**Action:** Execute migration batch by batch with testing

**For each batch:**

1. **Update imports:**
   ```python
   for file in batch.files:
       for old_pattern, new_pattern in migration_map:
           content = file.read()
           updated = regex.sub(old_pattern, new_pattern, content)
           file.write(updated)
   ```

2. **Git commit:**
   ```bash
   git add [batch files]
   git commit -m "refactor(EXEC-016): Standardize imports batch $N/$TOTAL

   Updated imports in $(count) files:
   - old pattern → new canonical pattern

   Batch: $N/$TOTAL
   Files: $(file list)

   🤖 Generated with Claude Code
   Co-Authored-By: Claude <noreply@anthropic.com>"
   ```

3. **Validation:**
   ```bash
   # Quick import validation
   python -m py_compile [batch files]

   # Full test suite
   pytest -q tests/ --maxfail=3

   # Import graph check
   python scripts/paths_index_cli.py gate
   ```

4. **Success/Failure:**
   - ✅ **Success:** Continue to next batch
   - ❌ **Failure:** Rollback batch, log error, stop execution

**Progress Tracking:**
```
Batch 1/13: ████████████████████ 100% (25/25 files) ✓ Tests passed
Batch 2/13: ████████████████████ 100% (25/25 files) ✓ Tests passed
Batch 3/13: ██████████░░░░░░░░░░  50% (13/25 files) ...
```

### Phase 3: Shim Update (5 minutes)

**Action:** Update shim files to point to canonical paths

**Steps:**
1. Identify all shim files (`core/*.py`, forwarding imports)
2. Update shims to import from `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/`
3. Add deprecation warnings:
   ```python
   import warnings
   warnings.warn(
       "Importing from core.orchestrator is deprecated. "
       "Use: from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine import Orchestrator",
       DeprecationWarning,
       stacklevel=2
   )
   from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine import *
   ```

### Phase 4: Verification (5 minutes)

**Action:** Comprehensive validation of all changes

**Checks:**
1. **Full test suite:** All 196 tests must pass
2. **Import validation:** No deprecated patterns detected
3. **Import graph:** Verify acyclic structure
4. **Static analysis:** No circular imports
5. **Type checking:** mypy validation passes

**Success Criteria:**
- ✅ All tests passing (196/196)
- ✅ Zero deprecated imports detected
- ✅ Import graph acyclic
- ✅ 300+ files updated
- ✅ 12-15 commits created

---

## Ground Truth Criteria

### Success Conditions

```python
success = (
    tests_passed == 196 and
    deprecated_imports == 0 and
    import_graph_acyclic == True and
    files_updated >= 300 and
    all_batches_committed == True
)
```

### Verification Commands

```bash
# 1. Verify no deprecated imports
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/detectors/import_pattern_analyzer.py \
  --check-deprecated \
  --fail-on-violation

# 2. Full test suite
pytest -q tests/ --maxfail=1

# 3. Import graph validation
python scripts/paths_index_cli.py gate --strict

# 4. Static analysis
python scripts/detect_circular_imports.py

# 5. Type checking
mypy --config-file pyproject.toml modules/ UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/
```

---

## Safety Mechanisms

### Pre-Execution Validation

```yaml
checks:
  - name: "Git clean"
    command: "git diff --exit-code"

  - name: "Tests passing baseline"
    command: "pytest -q tests/"

  - name: "Import map valid"
    command: "python scripts/validate_migration_map.py"
```

### Batched Execution Strategy

**Why batches?**
- Surgical rollback if any batch fails
- Gradual migration reduces risk
- Per-batch testing catches issues early
- Progress tracking and checkpointing

**Batch ordering:**
1. **Leaf modules** (no dependencies) first
2. **Mid-tier modules** (some dependencies)
3. **Root modules** (many dependencies) last

This ensures imports are updated before they're referenced.

### Automatic Rollback

```bash
# If batch N fails:
1. Revert batch N commit: git revert HEAD
2. Log failure: echo "Batch $N failed: $ERROR" >> migration_log.txt
3. Stop execution: exit 1
4. Manual review required before retry
```

---

## Integration

### Quality Gates

**Pre-commit Hook:**
```python
# Prevent deprecated import patterns from being committed
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/detectors/import_pattern_analyzer.py \
  --check-staged \
  --fail-on-deprecated
```

**CI/CD Pipeline:**
```yaml
- name: Validate Import Patterns
  run: |
    python scripts/paths_index_cli.py gate --strict
    python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/detectors/import_pattern_analyzer.py \
      --check-all \
      --report import_violations.json
```

---

## Expected Results

### Quantitative Metrics

- **Files updated:** 300+
- **Import statements changed:** 800+
- **Commits created:** 12-15 batches
- **Execution time:** ~45 minutes
- **Import ambiguity:** 100% → 0% (complete elimination)
- **Test pass rate:** 100% (196/196)

### Qualitative Improvements

**Before:**
```python
# Developer confusion: which import should I use?
from core.orchestrator import Orchestrator              # Option 1
from modules.core_engine import Orchestrator            # Option 2
from modules.core_engine.m010001_orchestrator import *  # Option 3
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine import Orchestrator  # Option 4
```

**After:**
```python
# Single canonical import - no confusion
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine import Orchestrator
```

**AI Navigation Clarity:**
- Before: "Found 4 import patterns, which should I use?"
- After: "Single canonical pattern identified"

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Breaking imports | Low (10%) | High | Per-batch testing, automatic rollback |
| Circular imports | Very Low (2%) | Medium | Dependency ordering, graph validation |
| Test failures | Medium (20%) | Medium | Pre-execution baseline, batch isolation |
| Incomplete migration | Very Low (1%) | Low | Verification phase checks all files |

**Overall Risk Level:** ⚠️ **Very Low**

**Auto-Approval:** ✅ **YES** (100% confidence - deterministic regex replacement)

---

## Manual Review Tier

**Tier:** 1 (Auto-Approved)

**Rationale:**
- 100% confidence (deterministic regex)
- Batched execution with per-batch validation
- Automatic rollback on any failure
- Full test coverage verification

**Review Process:**
- **Pre-execution:** None required
- **Post-execution:** Audit log review
- **Escalation:** Only if execution fails

---

## Usage Examples

### Dry-Run (Discovery Only)

```bash
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/runtime/cleanup_executor.py \
  --pattern EXEC-016 \
  --dry-run \
  --report import_migration_plan.json
```

### Full Execution (Auto-Approved)

```bash
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/runtime/cleanup_executor.py \
  --pattern EXEC-016 \
  --auto-approve \
  --batch-size 25 \
  --log import_migration.log
```

### Custom Migration Map

```bash
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/runtime/cleanup_executor.py \
  --pattern EXEC-016 \
  --migration-map custom_map.yaml \
  --batch-size 10 \
  --test-after-batch
```

---

## Related Patterns

- **EXEC-014:** Exact Duplicate Eliminator (prerequisite - removes duplicate implementations)
- **EXEC-019:** Shim Removal Automation (follow-up - removes old import paths after grace period)
- **EXEC-020:** Directory Structure Optimizer (broader scope - full repository restructure)

---

## Standard Import Aliases

After migration, enforce these standard aliases:

```python
# Standard alias for framework
import UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK as UETF

# Component-specific imports (preferred)
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine import Orchestrator, Executor
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.engine import ErrorEngine

# Avoid wildcard imports
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine import *  # ❌ Avoid
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-29 | Initial specification |

---

## References

- **Implementation:** `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/detectors/import_pattern_analyzer.py`
- **Execution Engine:** `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/runtime/cleanup_executor.py`
- **Migration Map:** `config/import_migration_map.yaml`
- **Batch Processor:** `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/runtime/batch_processor.py`

---

**Status:** ✅ Ready for Week 2 execution (after EXEC-014 completes)
