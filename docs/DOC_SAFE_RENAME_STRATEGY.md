---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-SAFE_RENAME_STRATEGY-091
---

# Safe Rename Strategy for AI-Friendly Codebase

**Date**: 2025-11-23  
**Purpose**: Safely rename folders and files to improve AI comprehension without breaking the codebase  
**Status**: Active Guide

---

## Overview

Your codebase already has excellent infrastructure for safe renaming:
1. **Path indexing database** (`refactor_paths.db`) - tracks all hardcoded paths
2. **CI enforcement** - blocks deprecated imports via `paths_index_cli.py gate`
3. **Section-based architecture** - clear module boundaries
4. **CODEBASE_INDEX.yaml** - machine-readable structure map
5. **ai_policies.yaml** - AI-readable edit policies

This guide shows how to leverage these tools for safe, AI-friendly renames.

---

## Principles for AI-Friendly Naming

### ✅ Good Naming Patterns
```
core/state/db.py                    # Clear: "state management database"
error/plugins/python_ruff/          # Clear: "Python Ruff error plugin"
specifications/tools/indexer/       # Clear: "specification indexing tools"
scripts/validate_workstreams.py     # Clear: "validates workstreams"
tests/engine/test_executor.py       # Clear: "tests for executor"
```

### ❌ Problematic Names (AI Confusion)
```
MOD_ERROR_PIPELINE/                 # Unclear: "MOD" prefix ambiguous
src/pipeline/                       # Generic: what kind of pipeline?
aux/                                # Unclear: what auxiliary functions?
utils/                              # Too vague: what utilities?
bad excution/                       # Typo + unclear purpose
```

### Naming Guidelines for AI
1. **Use domain terminology**: `error/`, `core/`, `engine/` vs `utils/`, `helpers/`
2. **Be specific**: `validate_workstreams.py` vs `validate.py`
3. **Layer hierarchy in paths**: `core/state/crud.py` (layer → domain → function)
4. **Match documentation**: File names should echo CODEBASE_INDEX.yaml module names
5. **Avoid abbreviations**: `specifications/` vs `specs/`, `database/` vs `db/`
6. **No spaces in paths**: Use underscores or hyphens

---

## Safe Rename Process (Step-by-Step)

### Phase 1: Discovery & Planning

#### Step 1.1: Scan Current Paths
```powershell
# Scan all hardcoded paths in codebase
python scripts\paths_index_cli.py scan --root . --db refactor_paths.db --reset

# Report paths matching a pattern (e.g., finding all "utils" references)
python scripts\paths_index_cli.py report --db refactor_paths.db --pattern "utils" --limit 100
```

#### Step 1.2: Identify Rename Candidates
Use CODEBASE_INDEX.yaml to identify misaligned names:

```powershell
# Check which modules have unclear names
python -c "import yaml; idx = yaml.safe_load(open('CODEBASE_INDEX.yaml')); print([m['id'] + ' -> ' + m['path'] for m in idx['modules'] if 'legacy' not in m['id']])"
```

#### Step 1.3: Create Rename Plan
Document planned changes in a mapping file:

```yaml
# rename_plan.yaml
renames:
  - old: "error/shared/utils/"
    new: "error/shared/utilities/"
    reason: "More explicit, avoids 'utils' ambiguity"
    impact: "15 import statements"
    
  - old: "bad excution/"
    new: "quarantine/failed_runs/"
    reason: "Fix typo, clarify purpose"
    impact: "2 references in docs"
```

### Phase 2: Pre-Rename Validation

#### Step 2.1: Check All References
```powershell
# Find all occurrences of the path to rename
python scripts\paths_index_cli.py report --db refactor_paths.db --pattern "error/shared/utils" > rename_impact.txt

# Search in code
grep -r "error.shared.utils" --include="*.py"
grep -r "error/shared/utils" --include="*.py"
```

#### Step 2.2: Verify Test Coverage
```powershell
# Run tests to establish baseline
pytest -q tests/

# Check if renamed module has tests
pytest -k "shared" -v
```

### Phase 3: Execute Rename (Safe Pattern)

#### Step 3.1: Create Migration Branch
```powershell
git checkout -b rename/error-shared-utils-to-utilities
```

#### Step 3.2: Rename Directories/Files
```powershell
# Use git mv to preserve history
git mv error\shared\utils error\shared\utilities
```

#### Step 3.3: Update All Imports (Automated)
Create a migration script:

```python
# scripts/migrate_imports.py
"""Update imports after renaming error/shared/utils to error/shared/utilities"""
import re
from pathlib import Path

OLD_IMPORT = "from error.shared.utils"
NEW_IMPORT = "from error.shared.utilities"

OLD_PATH = "error/shared/utils"
NEW_PATH = "error/shared/utilities"

def migrate_file(file_path: Path) -> bool:
    content = file_path.read_text(encoding='utf-8')
    original = content
    
    # Update imports
    content = content.replace(OLD_IMPORT, NEW_IMPORT)
    content = content.replace(OLD_PATH, NEW_PATH)
    
    if content != original:
        file_path.write_text(content, encoding='utf-8')
        return True
    return False

if __name__ == "__main__":
    root = Path(__file__).parent.parent
    changed = 0
    
    # Update Python files
    for py_file in root.rglob("*.py"):
        if "legacy" in py_file.parts or ".venv" in py_file.parts:
            continue
        if migrate_file(py_file):
            changed += 1
            print(f"Updated: {py_file}")
    
    print(f"\nTotal files updated: {changed}")
```

Run the migration:
```powershell
python scripts\migrate_imports.py
```

#### Step 3.4: Update Documentation
Update these files to reflect new paths:
- `CODEBASE_INDEX.yaml` (module path)
- `docs/SECTION_REFACTOR_MAPPING.md` (add to mapping table)
- `ai_policies.yaml` (if edit zones changed)
- `README.md` / `QUICK_START.md` (if user-facing)

#### Step 3.5: Rescan Path Index
```powershell
# Rescan to update path database
python scripts\paths_index_cli.py scan --root . --db refactor_paths.db --reset

# Verify old path no longer exists in code
python scripts\paths_index_cli.py gate --db refactor_paths.db --regex "error/shared/utils"
```

### Phase 4: Validation

#### Step 4.1: Run CI Gates
```powershell
# Check for deprecated paths
python scripts\paths_index_cli.py gate --db refactor_paths.db --regex "src/pipeline|MOD_ERROR_PIPELINE"

# Run tests
pytest -q tests/

# Validate workstreams
python scripts\validate_workstreams.py
```

#### Step 4.2: Verify Imports
```powershell
# Try importing the renamed module
python -c "from error.shared.utilities.hashing import hash_file; print('OK')"
```

#### Step 4.3: Check Documentation
```powershell
# Validate CODEBASE_INDEX
python -c "import yaml; yaml.safe_load(open('CODEBASE_INDEX.yaml')); print('CODEBASE_INDEX.yaml is valid')"

# Check for broken links in markdown
grep -r "error/shared/utils" docs/
```

### Phase 5: Commit & Cleanup

#### Step 5.1: Stage Changes
```powershell
git add -A
git status  # Review all changes
```

#### Step 5.2: Commit with Clear Message
```powershell
git commit -m "refactor: rename error/shared/utils to error/shared/utilities

- Improves AI comprehension with explicit naming
- Updates all 15 import statements across codebase
- Updates CODEBASE_INDEX.yaml and documentation
- All tests passing, CI gates pass
- See docs/SECTION_REFACTOR_MAPPING.md for full mapping"
```

#### Step 5.3: Update Mapping Log
Add entry to `docs/SECTION_REFACTOR_MAPPING.md`:

```markdown
### Error Shared Utils Rename (2025-11-23)
| Old Path | New Path | Notes |
|----------|----------|-------|
| `error/shared/utils/` | `error/shared/utilities/` | Explicit naming for AI clarity |
```

---

## Common Rename Scenarios

### Scenario 1: Rename Single File
**Example**: `scripts/validate.py` → `scripts/validate_workstreams.py`

```powershell
# 1. Rename file
git mv scripts\validate.py scripts\validate_workstreams.py

# 2. Find and update references
grep -r "validate.py" --include="*.py" --include="*.md"

# 3. Update imports (if any)
# from scripts.validate → from scripts.validate_workstreams

# 4. Update QUALITY_GATE.yaml if it's a validation script

# 5. Test and commit
pytest -q
git commit -m "refactor: rename validate.py to validate_workstreams.py for clarity"
```

### Scenario 2: Rename Directory (Shallow)
**Example**: `error/shared/utils/` → `error/shared/utilities/`

See Phase 3 above for full workflow.

### Scenario 3: Rename Section (Deep)
**Example**: `MOD_ERROR_PIPELINE/` → `error/` (already done)

This is documented in `docs/SECTION_REFACTOR_MAPPING.md` - follow that pattern.

### Scenario 4: Split Large Module
**Example**: `core/engine/orchestrator.py` (800 lines) → Split into smaller files

```powershell
# 1. Create new structure
mkdir core\engine\orchestration
git mv core\engine\orchestrator.py core\engine\orchestration\main_orchestrator.py

# 2. Extract components
# Create core/engine/orchestration/__init__.py
# Create core/engine/orchestration/scheduler_integration.py
# Create core/engine/orchestration/recovery_handler.py

# 3. Update imports to use new structure
# from core.engine.orchestrator → from core.engine.orchestration

# 4. Update CODEBASE_INDEX.yaml

# 5. Test thoroughly (this is a complex change)
pytest tests/engine/ -v
```

---

## AI-Optimized Naming Conventions

### Directory Naming
```
✅ Good:
core/state/              # Layer + domain
error/plugins/           # Domain + type
specifications/tools/    # Domain + purpose
tests/integration/       # Purpose + scope

❌ Avoid:
utils/                   # Too vague
misc/                    # Unclear purpose
tmp/                     # Temporary what?
old/                     # Use legacy/ and date it
```

### File Naming
```
✅ Good:
validate_workstreams.py      # Action + target
db_sqlite.py                 # Technology + implementation
error_state_machine.py       # Domain + pattern
test_executor_retry.py       # Test + component + aspect

❌ Avoid:
utils.py                     # Too generic
helpers.py                   # What kind of help?
main.py                      # Main what?
temp.py                      # Should be deleted
```

### Module Naming (in CODEBASE_INDEX.yaml)
```yaml
✅ Good:
- id: "error.plugins"
  name: "Error Detection Plugins"
  purpose: "Language-specific error detection plugins"

❌ Avoid:
- id: "utils"
  name: "Utilities"
  purpose: "Various utility functions"
```

---

## Incremental Rename Strategy

Rather than a big-bang rename, use **incremental renames** aligned with development phases:

### Phase K: Current State (Baseline)
- ✅ Core sections established (`core/`, `error/`, `engine/`)
- ✅ Legacy clearly marked (`legacy/`)
- ⚠️ Some ambiguous names remain (`bad excution/`, scattered utils)

### Phase K+1: Clarify Top-Level
```yaml
Renames:
  - "bad excution/" → "quarantine/failed_runs/"
  - "What's working so well in `fastdev.md`/" → "docs/retrospectives/fastdev_analysis/"
  - "PROCESS_DEEP_DIVE_OPTOMIZE/" → "meta/process_optimization/"
  - "QFT_updated/" → "tools/qft_quality_framework/"
```

### Phase K+2: Clarify Nested Utilities
```yaml
Renames:
  - "error/shared/utils/" → "error/shared/utilities/"
  - "core/shared/utils/" → "core/shared/common/" (if exists)
```

### Phase K+3: Consolidate Documentation
```yaml
Renames:
  - "devdocs/" → "docs/development/"
  - "Prompt/" → "docs/prompts/" or "aider/prompts/"
```

---

## Automation Helpers

### Script: Bulk Rename with Validation
```python
# scripts/safe_rename.py
"""Safe bulk rename with validation"""
import subprocess
from pathlib import Path
from typing import List, Tuple

def safe_rename(old_path: str, new_path: str, dry_run: bool = True) -> bool:
    """Safely rename path with validation."""
    old = Path(old_path)
    new = Path(new_path)
    
    if not old.exists():
        print(f"❌ Source does not exist: {old}")
        return False
    
    if new.exists():
        print(f"❌ Target already exists: {new}")
        return False
    
    # Check git status
    result = subprocess.run(
        ["git", "status", "--porcelain", str(old)],
        capture_output=True,
        text=True
    )
    if result.stdout.strip():
        print(f"⚠️ Uncommitted changes in: {old}")
        print(result.stdout)
        return False
    
    if dry_run:
        print(f"🔍 DRY RUN: Would rename {old} → {new}")
        return True
    
    # Execute rename
    new.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "mv", str(old), str(new)], check=True)
    print(f"✅ Renamed: {old} → {new}")
    return True

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("old", help="Old path")
    parser.add_argument("new", help="New path")
    parser.add_argument("--execute", action="store_true", help="Execute rename (default: dry run)")
    args = parser.parse_args()
    
    safe_rename(args.old, args.new, dry_run=not args.execute)
```

Usage:
```powershell
# Dry run
python scripts\safe_rename.py "bad excution" "quarantine\failed_runs"

# Execute
python scripts\safe_rename.py "bad excution" "quarantine\failed_runs" --execute
```

---

## Checklist: Before Any Rename

- [ ] **Scan** current path usage: `paths_index_cli.py scan`
- [ ] **Report** all references: `paths_index_cli.py report --pattern "old/path"`
- [ ] **Check** imports: `grep -r "old.path" --include="*.py"`
- [ ] **Baseline** tests: `pytest -q` (should pass)
- [ ] **Create** migration branch: `git checkout -b rename/descriptive-name`
- [ ] **Document** plan: Update rename plan with impact assessment

## Checklist: After Any Rename

- [ ] **Update** imports: Run migration script or manual search-replace
- [ ] **Update** CODEBASE_INDEX.yaml: Change module paths
- [ ] **Update** ai_policies.yaml: If edit zones changed
- [ ] **Update** docs: SECTION_REFACTOR_MAPPING.md, README.md, etc.
- [ ] **Rescan** paths: `paths_index_cli.py scan --reset`
- [ ] **Gate check**: `paths_index_cli.py gate --regex "old/path"`
- [ ] **Run tests**: `pytest -q`
- [ ] **Validate workstreams**: `python scripts\validate_workstreams.py`
- [ ] **Commit** with clear message and link to this guide

---

## Quick Reference Commands

```powershell
# Discovery
python scripts\paths_index_cli.py scan --root . --db refactor_paths.db --reset
python scripts\paths_index_cli.py report --db refactor_paths.db --pattern "utils"
grep -r "pattern" --include="*.py"

# Rename
git mv old\path new\path

# Update imports (create migration script)
python scripts\migrate_imports.py

# Validate
python scripts\paths_index_cli.py gate --db refactor_paths.db --regex "deprecated/path"
pytest -q tests/
python scripts\validate_workstreams.py

# Commit
git add -A
git commit -m "refactor: rename description"
```

---

## When NOT to Rename

❌ **Don't rename if**:
- It's in `legacy/` (already archived, don't touch)
- It's a well-known convention (`tests/`, `docs/`, `scripts/`)
- It's part of external tool config (`.github/`, `pyproject.toml` sections)
- Rename would break published APIs or external integrations
- You're unsure of impact (scan and report first)

✅ **DO rename if**:
- Name is misleading or has typos
- Name is too generic (`utils/`, `misc/`)
- Name doesn't match CODEBASE_INDEX.yaml module purpose
- Name would confuse AI tools (e.g., `MOD_ERROR_PIPELINE`)
- You've validated impact and have migration plan

---

## Summary

Your codebase has **excellent rename infrastructure**:
1. Use `paths_index_cli.py` to track hardcoded paths
2. Follow **section-based architecture** (core/, error/, engine/, etc.)
3. Keep **CODEBASE_INDEX.yaml** in sync
4. Use **git mv** to preserve history
5. **Automate** import updates with migration scripts
6. **Validate** with CI gates before committing

**Key insight**: Rename **incrementally** and **purposefully**. Each rename should make the codebase more obvious to both humans and AI. Document every change in `SECTION_REFACTOR_MAPPING.md`.

---

## See Also

- `docs/SECTION_REFACTOR_MAPPING.md` - Historical renames
- `CODEBASE_INDEX.yaml` - Current module structure
- `ai_policies.yaml` - AI edit policies
- `DIRECTORY_GUIDE.md` - Directory explanations
- `scripts/paths_index_cli.py` - Path tracking tool
