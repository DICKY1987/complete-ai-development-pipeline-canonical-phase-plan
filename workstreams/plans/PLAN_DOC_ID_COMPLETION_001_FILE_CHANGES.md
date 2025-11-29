---
status: draft
doc_type: plan
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-DOC_ID_COMPLETION_001_FILE_CHANGES-127
---

# PLAN_DOC_ID_COMPLETION_001 - File Modifications Summary

**Plan**: PLAN_DOC_ID_COMPLETION_001  
**Date**: 2025-11-29  
**Total Changes**: 12 files (7 new, 5 updates, 0 deletions)

---

## NEW FILES (7)

### 1. `doc_id/ID_LIFECYCLE_RULES.yaml`
**Size**: ~250 lines  
**Purpose**: Canonical lifecycle and conflict resolution rules  
**Content**:
```yaml
metadata:
  version: "1.0"
  last_updated: "2025-11-29"
  status: "canonical"
  doc_id: "DOC-ID-LIFECYCLE-RULES-001"

lifecycle:
  file_split: {...}
  file_merge: {...}
  file_move: {...}
  file_rename: {...}
  file_delete: {...}

conflict_resolution:
  same_file_different_ids: {...}
  different_files_same_id: {...}
  id_format_violation: {...}

validation:
  preflight_checks: {...}
  post_merge_validation: {...}

enforcement:
  REFRACTOR_GATE_001: {...}
  CI_ID_VALIDATION: {...}
```

---

### 2. `doc_id/SCANNER_EXCLUSIONS.md`
**Size**: ~100 lines  
**Purpose**: Document why .worktrees exclusion prevents race conditions  
**Content**:
- Current exclusion patterns
- Why worktrees are excluded
- Risk scenarios (if not excluded)
- Testing instructions
- Related safeguards

**Key Sections**:
```markdown
## Current Exclusions
EXCLUDE_PATTERNS = [".worktrees", ".state", ...]

## Why Worktrees Are Excluded
[Explains race condition prevention]

## Testing Exclusions
[Commands to verify exclusions work]
```

---

### 3. `scripts/orchestration_lock.py`
**Size**: ~50 lines  
**Purpose**: Lock management for orchestration  
**New Functions**:
```python
def acquire_lock(orchestrator_pid: int) -> bool
def release_lock() -> None
def is_locked() -> bool
def get_lock_info() -> dict
```

**Creates**: `.state/orchestration.lock` (JSON file)

---

### 4. `scripts/id_conflict_resolver.py`
**Size**: ~200 lines  
**Purpose**: Conflict detection and resolution utilities  
**New Functions**:
```python
def detect_conflicts(inventory_path) -> Dict
def is_valid_format(doc_id: str) -> bool
def resolve_same_file_conflict(path, doc_ids, keep_id) -> None
def generate_conflict_report(conflicts, output_path) -> None
```

**CLI Commands**:
```bash
python scripts/id_conflict_resolver.py detect
python scripts/id_conflict_resolver.py resolve-same-file --path <file> --keep <id>
```

**Generates**: `reports/id_conflicts_<timestamp>.md`

---

### 5. `docs/ID_CONFLICT_RESOLUTION_PROCEDURES.md`
**Size**: ~300 lines  
**Purpose**: Step-by-step conflict resolution procedures  
**Content**:
- When conflicts occur
- Detection methods
- Conflict types (3 types)
- Resolution steps for each type
- Prevention best practices
- CI integration
- Escalation procedures
- Examples

**Sections**:
```markdown
## Type 1: Same File, Different IDs
## Type 2: Different Files, Same ID
## Type 3: Format Violations
## Prevention
## Escalation
## Appendix: Examples
```

---

### 6. `tests/test_id_framework.py`
**Size**: ~150 lines  
**Purpose**: Validation test suite for ID framework  
**Test Classes**:
```python
class TestIDFormat:
    def test_valid_formats()
    def test_invalid_formats()

class TestConflictDetection:
    def test_no_conflicts()
    def test_same_file_different_ids()
    def test_different_files_same_id()
    def test_format_violations()

class TestScannerExclusions:
    def test_worktrees_excluded()
    def test_state_excluded()

class TestOrchestrationLock:
    def test_acquire_release()
    def test_double_acquire_fails()
```

**Run**: `pytest tests/test_id_framework.py -v`

---

### 7. `doc_id/PHASE_COMPLETION_CHECKLIST.md`
**Size**: ~150 lines  
**Purpose**: Execution checklist with validation commands  
**Content**:
- Phase 0 checklist (2 steps)
- Phase 1 checklist (3 steps)
- Phase 2 checklist (2 steps)
- Phase 3 checklist (2 steps)
- Phase 4 checklist (2 steps)
- Completion criteria
- Post-completion steps

**Format**:
```markdown
- [ ] Step 0.1: Create ID_LIFECYCLE_RULES.yaml (15 min)
  - [ ] File created
  - [ ] YAML syntax validated
  - [ ] Contains all lifecycle rules
  
**Validation**:
```bash
python -c "import yaml; ..."
```
```

---

## UPDATED FILES (5)

### 1. `scripts/doc_id_scanner.py`
**Changes**: Add orchestration lock check  
**Lines Added**: ~10 lines  
**Location**: At start of `scan()` method

**Addition**:
```python
# Add at top of file
from orchestration_lock import is_locked, get_lock_info

# Add to scan() function
def scan(self):
    # Check for orchestration lock
    if is_locked():
        lock_info = get_lock_info()
        raise RuntimeError(
            f"Cannot scan during active orchestration.\n"
            f"Lock acquired at: {lock_info.get('acquired_at')}\n"
            f"Orchestrator PID: {lock_info.get('pid')}\n"
            f"Wait for orchestration to complete or remove .state/orchestration.lock"
        )
    
    # Continue with existing scan logic...
```

**Impact**: Scanner will error if run during orchestration

---

### 2. `scripts/preflight_validator.py`
**Changes**: Add ID coverage and conflict validation  
**Lines Added**: ~50 lines  
**New Methods**:
```python
def validate_id_coverage(self, threshold: float = 1.0) -> bool:
    """Validate ID coverage meets threshold."""
    from doc_id_scanner import DocIDScanner
    scanner = DocIDScanner()
    stats = scanner.get_stats()
    # Check coverage >= threshold
    # Return True/False

def validate_id_conflicts(self) -> bool:
    """Check for ID conflicts."""
    from id_conflict_resolver import detect_conflicts
    conflicts = detect_conflicts()
    # Return True if no conflicts

# Update run_preflight() to include new checks
def run_preflight(self) -> bool:
    checks = [
        ("Disk space", self.check_disk_space),
        ("Git status", self.check_git_status),
        ("Dependencies", self.check_dependencies),
        ("ID coverage", lambda: self.validate_id_coverage(threshold=1.0)),  # ← NEW
        ("ID conflicts", self.validate_id_conflicts),  # ← NEW
    ]
    # ... existing logic
```

**Impact**: Preflight now checks ID coverage and conflicts

---

### 3. `scripts/run_multi_agent_refactor.ps1`
**Changes**: Add lock, trap, preflight, post-validation  
**Lines Added**: ~80 lines  
**Sections Added**:

**At start**:
```powershell
# Acquire orchestration lock
Write-Host "🔒 Acquiring orchestration lock..." -ForegroundColor Yellow
python -c "from scripts.orchestration_lock import acquire_lock; import os; acquire_lock(os.getpid())"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to acquire lock - orchestration already running?" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Lock acquired" -ForegroundColor Green
```

**Add trap**:
```powershell
# Add trap for cleanup
trap {
    Write-Host "`n🛑 Orchestration interrupted!" -ForegroundColor Red
    Write-Host "🧹 Cleaning up..." -ForegroundColor Yellow
    
    # Release lock
    python -c "from scripts.orchestration_lock import release_lock; release_lock()"
    
    # Clean worktrees
    Write-Host "Removing worktrees..." -ForegroundColor Yellow
    git worktree list --porcelain | Select-String "worktree.*\.worktrees" | ForEach-Object {
        $path = ($_ -replace "worktree ", "").Trim()
        if (Test-Path $path) {
            git worktree remove $path --force
            Write-Host "  Removed: $path" -ForegroundColor Gray
        }
    }
    
    Write-Host "✅ Cleanup complete" -ForegroundColor Green
    exit 1
}
```

**Add preflight**:
```powershell
# Run preflight validation
Write-Host "`n🔍 Running preflight validation..." -ForegroundColor Cyan
python scripts/preflight_validator.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Preflight validation failed" -ForegroundColor Red
    python -c "from scripts.orchestration_lock import release_lock; release_lock()"
    exit 1
}

Write-Host "✅ Preflight passed" -ForegroundColor Green
```

**At end**:
```powershell
# Release orchestration lock
Write-Host "`n🔓 Releasing orchestration lock..." -ForegroundColor Yellow
python -c "from scripts.orchestration_lock import release_lock; release_lock()"
Write-Host "✅ Lock released" -ForegroundColor Green

# Post-orchestration validation
Write-Host "`n🔍 Post-orchestration validation..." -ForegroundColor Cyan
python scripts/id_conflict_resolver.py detect

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  ID conflicts detected - check reports/" -ForegroundColor Yellow
}

# Update inventory
Write-Host "`n📊 Updating inventory..." -ForegroundColor Cyan
python scripts/doc_id_scanner.py scan
python scripts/doc_id_scanner.py report

Write-Host "`n✅ Orchestration complete" -ForegroundColor Green
```

**Impact**: Orchestration now has lock, cleanup, validation

---

### 4. `workstreams/WORKSTREAM_TEMPLATE.json`
**Changes**: Add files_to_edit and files_to_create fields  
**Lines Added**: ~10 lines  

**Addition**:
```json
{
  "id": "ws-XXX",
  "name": "Workstream Name",
  "description": "What this workstream does",
  "depends_on": [],
  "estimated_hours": 1,
  "tool": "aider",
  
  "files_to_edit": [           // ← NEW
    "path/to/file1.py",
    "path/to/file2.py"
  ],
  
  "files_to_create": [         // ← NEW
    "path/to/new_file.md"
  ],
  
  "validation": {
    "run_tests": true,
    "test_pattern": "tests/path/test_*.py"
  }
}
```

**Impact**: Workstreams now declare file dependencies

**Note**: Also update `scripts/validate_workstreams.py` to validate these fields:
```python
def validate_workstream_files(ws_data: dict) -> List[str]:
    """Validate files_to_edit exist or can be created."""
    errors = []
    
    # Check files_to_edit exist
    for file_path in ws_data.get("files_to_edit", []):
        if not Path(file_path).exists():
            errors.append(f"File to edit does not exist: {file_path}")
    
    # Check files_to_create don't already exist
    for file_path in ws_data.get("files_to_create", []):
        if Path(file_path).exists():
            errors.append(f"File to create already exists: {file_path}")
    
    return errors
```

---

### 5. `README.md`
**Changes**: Add ID Framework section  
**Lines Added**: ~40 lines  
**Location**: Add new section

**Addition**:
```markdown
## ID Framework

**Status**: Production-ready (v1.0)  
**Coverage**: See `DOC_ID_COVERAGE_REPORT.md`

### Quick Start

```bash
# Scan repository for doc_ids
python scripts/doc_id_scanner.py scan

# Check coverage
python scripts/doc_id_scanner.py stats

# Detect conflicts
python scripts/id_conflict_resolver.py detect

# Mint new doc_id
python doc_id/doc_id_registry_cli.py mint --category CORE --name MY-MODULE
```

### Key Files

- `doc_id/ID_LIFECYCLE_RULES.yaml` - Lifecycle & conflict resolution policies
- `doc_id/DOC_ID_FRAMEWORK.md` - Complete specification
- `doc_id/DOC_ID_REGISTRY.yaml` - Central registry
- `docs_inventory.jsonl` - Current inventory
- `DOC_ID_COVERAGE_REPORT.md` - Coverage statistics

### Integration with Orchestration

The ID framework integrates with multi-agent orchestration:

1. **Before orchestration**: Scanner assigns IDs to all files
2. **During orchestration**: Worktrees operate on files with existing IDs
3. **After orchestration**: Validator checks for conflicts

See `ID_LIFECYCLE_RULES.yaml` for complete policies.

### Conflict Resolution

If conflicts detected:

```bash
# Generate report
python scripts/id_conflict_resolver.py detect

# Review
cat reports/id_conflicts_*.md

# Resolve
# See: docs/ID_CONFLICT_RESOLUTION_PROCEDURES.md
```
```

**Impact**: README now documents ID framework

---

## DELETED FILES (0)

**No files are deleted** by this plan.

---

## GENERATED FILES (Runtime)

These files are created during execution, not by the plan:

### 1. `.state/orchestration.lock`
**Created by**: `scripts/orchestration_lock.py`  
**When**: During orchestration  
**Auto-deleted**: Yes (at end or on interrupt)  
**Format**: JSON
```json
{
  "acquired_at": "2025-11-29T15:00:00.000Z",
  "pid": 12345,
  "status": "active"
}
```

### 2. `reports/id_conflicts_<timestamp>.md`
**Created by**: `scripts/id_conflict_resolver.py`  
**When**: If conflicts detected  
**Auto-deleted**: No (kept for review)  
**Format**: Markdown report

---

## MODIFICATION SUMMARY

### By File Type

**YAML**: 1 new  
- `doc_id/ID_LIFECYCLE_RULES.yaml`

**Python**: 3 new, 3 updated  
- NEW: `scripts/orchestration_lock.py`
- NEW: `scripts/id_conflict_resolver.py`
- NEW: `tests/test_id_framework.py`
- UPDATE: `scripts/doc_id_scanner.py`
- UPDATE: `scripts/preflight_validator.py`
- UPDATE: `scripts/validate_workstreams.py`

**Markdown**: 3 new, 1 updated  
- NEW: `doc_id/SCANNER_EXCLUSIONS.md`
- NEW: `docs/ID_CONFLICT_RESOLUTION_PROCEDURES.md`
- NEW: `doc_id/PHASE_COMPLETION_CHECKLIST.md`
- UPDATE: `README.md`

**PowerShell**: 1 updated  
- UPDATE: `scripts/run_multi_agent_refactor.ps1`

**JSON**: 1 updated  
- UPDATE: `workstreams/WORKSTREAM_TEMPLATE.json`

---

### By Impact Area

**Core Framework**:
- `doc_id/ID_LIFECYCLE_RULES.yaml` (NEW)
- `doc_id/SCANNER_EXCLUSIONS.md` (NEW)

**Safety & Validation**:
- `scripts/orchestration_lock.py` (NEW)
- `scripts/id_conflict_resolver.py` (NEW)
- `scripts/doc_id_scanner.py` (UPDATE)
- `scripts/preflight_validator.py` (UPDATE)

**Orchestration**:
- `scripts/run_multi_agent_refactor.ps1` (UPDATE)
- `workstreams/WORKSTREAM_TEMPLATE.json` (UPDATE)
- `scripts/validate_workstreams.py` (UPDATE)

**Documentation**:
- `docs/ID_CONFLICT_RESOLUTION_PROCEDURES.md` (NEW)
- `doc_id/PHASE_COMPLETION_CHECKLIST.md` (NEW)
- `README.md` (UPDATE)

**Testing**:
- `tests/test_id_framework.py` (NEW)

---

## DEPENDENCIES ADDED

### Python Imports (New)

**In `scripts/doc_id_scanner.py`**:
```python
from orchestration_lock import is_locked, get_lock_info
```

**In `scripts/preflight_validator.py`**:
```python
from doc_id_scanner import DocIDScanner
from id_conflict_resolver import detect_conflicts
```

**In `scripts/id_conflict_resolver.py`**:
```python
from pathlib import Path
from datetime import datetime
import json
import re
from typing import List, Dict, Tuple
```

**In `tests/test_id_framework.py`**:
```python
import pytest
from pathlib import Path
import json
import tempfile
import shutil
from scripts.id_conflict_resolver import (
    detect_conflicts,
    is_valid_format,
)
from scripts.doc_id_scanner import DocIDScanner
from scripts.orchestration_lock import acquire_lock, release_lock, is_locked
```

### External Dependencies (None)

No new external packages required. Uses only Python stdlib.

---

## SIZE IMPACT

**Total Lines Added**: ~1,300 lines  
**Total Lines Modified**: ~100 lines  
**Total Lines Deleted**: 0 lines  

**Breakdown**:
- New documentation: ~650 lines
- New code: ~400 lines
- New tests: ~150 lines
- Updates to existing: ~100 lines

**Disk Space**: ~200 KB (text files only)

---

## BEHAVIORAL CHANGES

### 1. Scanner Behavior
**Before**: Runs anytime  
**After**: Errors if orchestration active (lock exists)

### 2. Preflight Validation
**Before**: Checks disk, git, dependencies  
**After**: Also checks ID coverage (100%) and conflicts

### 3. Orchestration Script
**Before**: No lock, no cleanup on interrupt  
**After**: 
- Acquires lock at start
- Cleanup trap on Ctrl+C
- Preflight validation
- Post-execution conflict check
- Inventory update

### 4. Workstream Validation
**Before**: Validates structure only  
**After**: Also validates `files_to_edit` exist, `files_to_create` don't exist

---

## BREAKING CHANGES

**None**. All changes are additive:
- New files don't conflict with existing
- Updates to existing files add functionality
- No API changes to existing functions
- No removed functionality

**Backward Compatible**: Yes, fully

---

## ROLLBACK STRATEGY

If needed, rollback is simple:

```bash
# Remove new files
rm doc_id/ID_LIFECYCLE_RULES.yaml
rm doc_id/SCANNER_EXCLUSIONS.md
rm doc_id/PHASE_COMPLETION_CHECKLIST.md
rm scripts/orchestration_lock.py
rm scripts/id_conflict_resolver.py
rm docs/ID_CONFLICT_RESOLUTION_PROCEDURES.md
rm tests/test_id_framework.py

# Revert updated files
git checkout scripts/doc_id_scanner.py
git checkout scripts/preflight_validator.py
git checkout scripts/run_multi_agent_refactor.ps1
git checkout scripts/validate_workstreams.py
git checkout workstreams/WORKSTREAM_TEMPLATE.json
git checkout README.md

# Remove generated files
rm .state/orchestration.lock
rm reports/id_conflicts_*.md
```

---

## VALIDATION COMMANDS

After all changes:

```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('doc_id/ID_LIFECYCLE_RULES.yaml'))"

# Run tests
pytest tests/test_id_framework.py -v

# Check preflight
python scripts/preflight_validator.py

# Detect conflicts
python scripts/id_conflict_resolver.py detect

# Test lock
python -c "from scripts.orchestration_lock import acquire_lock, is_locked; acquire_lock(1234); print(is_locked())"
```

---

## SUMMARY TABLE

| Category | New | Updated | Deleted | Total |
|----------|-----|---------|---------|-------|
| **Files** | 7 | 5 | 0 | 12 |
| **Lines** | ~1,300 | ~100 | 0 | ~1,400 |
| **Python** | 3 | 3 | 0 | 6 |
| **Markdown** | 3 | 1 | 0 | 4 |
| **YAML** | 1 | 0 | 0 | 1 |
| **PowerShell** | 0 | 1 | 0 | 1 |
| **JSON** | 0 | 1 | 0 | 1 |

---

**Status**: Complete file modification list  
**Breaking Changes**: None  
**Backward Compatible**: Yes  
**Rollback**: Simple (delete new, revert updated)

