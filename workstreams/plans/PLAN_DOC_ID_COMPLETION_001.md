---
status: draft
doc_type: plan
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-DOC_ID_COMPLETION_001-126
---

# Phase Plan: ID Framework Completion & Integration
**Document ID**: PLAN-DOC-ID-COMPLETION-001  
**Date**: 2025-11-29  
**Status**: Ready to Execute  
**Estimated Total Time**: 3-4 hours

---

## Executive Summary

This phase plan implements the **2 real gaps** identified in the AI evaluation reality check and adds **optional enhancements** for a production-ready ID framework integrated with multi-agent orchestration.

**What This Plan Does**:
- ✅ Closes 2 critical specification gaps (lifecycle, conflict resolution)
- ✅ Adds optional safety mechanisms (orchestration.lock)
- ✅ Documents existing safeguards (scanner exclusions)
- ✅ Creates validation and enforcement tools
- ✅ Integrates ID framework with Phase 0 execution

**What This Plan Does NOT Do**:
- ❌ Implement IDCoordinator (not needed - registry already exists)
- ❌ Fix scanner race conditions (already solved)
- ❌ Add threading locks (not applicable to current design)

---

## Phase 0: Foundation (30 minutes)

**Goal**: Document existing safeguards and establish baseline

### Step 0.1: Create ID_LIFECYCLE_RULES.yaml (15 min)

**File**: `doc_id/ID_LIFECYCLE_RULES.yaml`

**Content**:
```yaml
# ID Lifecycle & Conflict Resolution Rules
# Version: 1.0
# Date: 2025-11-29

metadata:
  version: "1.0"
  last_updated: "2025-11-29"
  status: "canonical"
  doc_id: "DOC-ID-LIFECYCLE-RULES-001"

# File Lifecycle Rules
lifecycle:
  
  file_split:
    # When one file becomes multiple files
    description: "Primary file retains original doc_id, derived files get new IDs"
    rules:
      primary_file:
        doc_id: "unchanged - retains original"
        metadata:
          - field: "split_into"
            value: "list of new doc_ids"
      
      derived_files:
        doc_id: "new doc_id assigned"
        metadata:
          - field: "derived_from"
            value: "original doc_id"
          - field: "split_reason"
            value: "free text explanation"
    
    example:
      before:
        file: "orchestrator.py"
        doc_id: "DOC-CORE-ORCHESTRATOR-001"
      
      after:
        - file: "orchestrator_core.py"
          doc_id: "DOC-CORE-ORCHESTRATOR-001"  # Unchanged
          metadata:
            split_into: ["DOC-CORE-ORCHESTRATOR-HELPERS-002"]
        
        - file: "orchestrator_helpers.py"
          doc_id: "DOC-CORE-ORCHESTRATOR-HELPERS-002"  # New
          metadata:
            derived_from: "DOC-CORE-ORCHESTRATOR-001"
            split_reason: "Extracted helper functions for clarity"
  
  file_merge:
    # When multiple files become one file
    description: "Merged file gets new doc_id, originals marked superseded"
    rules:
      merged_file:
        doc_id: "new doc_id assigned"
        metadata:
          - field: "supersedes"
            value: "list of original doc_ids"
          - field: "merge_reason"
            value: "free text explanation"
      
      original_files:
        status: "retired"
        metadata:
          - field: "superseded_by"
            value: "new merged doc_id"
          - field: "retired_at"
            value: "ISO 8601 timestamp"
    
    example:
      before:
        - file: "db_read.py"
          doc_id: "DOC-CORE-DB-READ-001"
        - file: "db_write.py"
          doc_id: "DOC-CORE-DB-WRITE-002"
      
      after:
        - file: "db_operations.py"
          doc_id: "DOC-CORE-DB-OPERATIONS-003"  # New
          metadata:
            supersedes: 
              - "DOC-CORE-DB-READ-001"
              - "DOC-CORE-DB-WRITE-002"
            merge_reason: "Unified database operations"
        
        # Registry entries for retired IDs:
        - doc_id: "DOC-CORE-DB-READ-001"
          status: "retired"
          superseded_by: "DOC-CORE-DB-OPERATIONS-003"
          retired_at: "2025-11-29T15:00:00Z"
  
  file_move:
    # When file changes path (module refactor)
    description: "doc_id unchanged, path updated in inventory"
    rules:
      doc_id: "unchanged - IDs are stable across moves"
      path: "updated in docs_inventory.jsonl"
      metadata:
        - field: "previous_paths"
          value: "list of historical paths"
        - field: "moved_at"
          value: "ISO 8601 timestamp"
    
    example:
      before:
        path: "core/state/db.py"
        doc_id: "DOC-CORE-STATE-DB-001"
      
      after:
        path: "modules/mod-core-state/db.py"
        doc_id: "DOC-CORE-STATE-DB-001"  # Unchanged
        metadata:
          previous_paths:
            - "core/state/db.py"
          moved_at: "2025-11-29T15:00:00Z"
  
  file_rename:
    # When file name changes but stays in same module
    description: "doc_id unchanged, path updated"
    rules:
      doc_id: "unchanged"
      path: "updated in inventory"
      metadata:
        - field: "previous_names"
          value: "list of historical names"
    
    example:
      before:
        file: "db_ops.py"
        doc_id: "DOC-CORE-DB-OPS-001"
      
      after:
        file: "database_operations.py"
        doc_id: "DOC-CORE-DB-OPS-001"  # Unchanged
        metadata:
          previous_names: ["db_ops.py"]
  
  file_delete:
    # When file is removed from codebase
    description: "doc_id marked retired in registry, not reused"
    rules:
      doc_id: "marked retired - never reused"
      status: "retired"
      metadata:
        - field: "retired_at"
          value: "ISO 8601 timestamp"
        - field: "retirement_reason"
          value: "free text explanation"
        - field: "last_known_path"
          value: "path before deletion"
    
    example:
      file: "deprecated_module.py"
      doc_id: "DOC-CORE-DEPRECATED-001"
      status: "retired"
      retired_at: "2025-11-29T15:00:00Z"
      retirement_reason: "Functionality moved to new architecture"
      last_known_path: "core/deprecated/deprecated_module.py"

# Conflict Resolution Rules
conflict_resolution:
  
  same_file_different_ids:
    # Multiple agents assign different doc_ids to same file
    description: "First-merged-wins, later IDs marked superseded"
    policy: "first-merged-wins"
    
    detection:
      - "During merge, detect doc_id field conflicts"
      - "Check docs_inventory.jsonl for duplicate path entries"
    
    resolution:
      action: "keep first-merged doc_id, mark later as superseded"
      steps:
        - "Accept first merged doc_id"
        - "Mark later doc_ids as superseded_by first"
        - "Update registry to reflect supersession"
        - "Log conflict to logs/id_conflicts.log"
        - "Generate report: reports/id_conflict_<timestamp>.md"
    
    prevention:
      - "Use central registry for ID assignment"
      - "Run scanner before orchestration to assign IDs upfront"
      - "Avoid ad-hoc ID minting in worktrees"
    
    example:
      conflict:
        file: "core/state/db.py"
        agent_1_id: "DOC-CORE-STATE-DB-001"  # Merged first
        agent_2_id: "DOC-CORE-STATE-DB-002"  # Merged later
      
      resolution:
        kept: "DOC-CORE-STATE-DB-001"
        superseded: "DOC-CORE-STATE-DB-002"
        registry_entry:
          doc_id: "DOC-CORE-STATE-DB-002"
          status: "superseded"
          superseded_by: "DOC-CORE-STATE-DB-001"
          reason: "Duplicate ID assigned during parallel execution"
  
  different_files_same_id:
    # Two different files claim same doc_id (should be impossible)
    description: "Error condition - requires manual resolution"
    policy: "error - halt and require manual intervention"
    
    detection:
      - "Registry validation detects duplicate doc_id"
      - "Two different paths reference same doc_id"
    
    resolution:
      action: "halt orchestration, generate error report, manual fix"
      steps:
        - "STOP orchestration immediately"
        - "Generate error report: reports/critical_id_error_<timestamp>.md"
        - "List conflicting files and their claims"
        - "Require human to decide which file keeps ID"
        - "Manual correction in registry + files"
        - "Restart orchestration after fix"
    
    prevention:
      - "Central registry ensures uniqueness"
      - "Validation in doc_id_registry_cli.py mint command"
      - "Preflight validation before orchestration"
    
    example:
      conflict:
        doc_id: "DOC-CORE-DB-001"
        file_1: "core/state/db.py"
        file_2: "core/database/operations.py"
      
      error_report:
        title: "CRITICAL: Duplicate doc_id across different files"
        doc_id: "DOC-CORE-DB-001"
        files:
          - "core/state/db.py"
          - "core/database/operations.py"
        required_action: "Manual resolution - choose which file keeps this ID"
  
  id_format_violation:
    # doc_id doesn't match expected format
    description: "Reject invalid IDs, log error"
    policy: "error - reject invalid format"
    
    validation:
      format: "DOC-<CATEGORY>-<NAME>-<SEQ>"
      regex: "^DOC-[A-Z]+-[A-Z0-9-]+-\\d{3}$"
    
    resolution:
      action: "reject during registry mint, generate error"
      steps:
        - "Validate format before accepting"
        - "Generate error with expected format"
        - "Suggest corrected ID"
    
    example:
      invalid: "doc-core-db-1"  # Lowercase, short seq
      valid: "DOC-CORE-DB-001"
      error: "Invalid doc_id format: must match DOC-<CAT>-<NAME>-<SEQ> with 3-digit sequence"

# Validation Rules
validation:
  
  preflight_checks:
    description: "Checks before orchestration starts"
    checks:
      - name: "ID coverage"
        rule: "All eligible files must have doc_id"
        threshold: "100% for module refactor, 95% for CI"
        enforcement: "REFRACTOR_GATE_001"
      
      - name: "ID uniqueness"
        rule: "No duplicate doc_ids in registry"
        enforcement: "Hard error - halt if duplicates found"
      
      - name: "Format compliance"
        rule: "All doc_ids match expected format"
        enforcement: "Hard error - halt if invalid format"
      
      - name: "Registry consistency"
        rule: "docs_inventory.jsonl matches registry"
        enforcement: "Warning - report discrepancies"
  
  post_merge_validation:
    description: "Checks after each worktree merge"
    checks:
      - name: "No ID conflicts introduced"
        rule: "Merged files don't create duplicate IDs"
      
      - name: "Inventory updated"
        rule: "docs_inventory.jsonl reflects merge"
      
      - name: "Retired IDs tracked"
        rule: "Deleted files marked retired in registry"

# Enforcement
enforcement:
  
  REFRACTOR_GATE_001:
    description: "Module refactor may not start unless ID coverage meets threshold"
    threshold: "100%"
    scope: "All files in modules being refactored"
    action_on_fail: "Halt refactor, generate coverage report, list missing IDs"
  
  CI_ID_VALIDATION:
    description: "CI validates ID compliance on every PR"
    checks:
      - "No duplicate doc_ids"
      - "All new files have doc_ids"
      - "Format compliance"
    action_on_fail: "Block PR merge"

# Notes
notes:
  - "IDs are immutable - once assigned, never changed or reused"
  - "Paths can change freely - IDs decouple identity from location"
  - "Lifecycle metadata enables traceability across refactors"
  - "Conflict resolution is defensive - assumes rare edge cases"
  - "Central registry is single source of truth"
```

**Validation**:
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('doc_id/ID_LIFECYCLE_RULES.yaml'))"
```

---

### Step 0.2: Document Scanner Exclusions (15 min)

**File**: `doc_id/SCANNER_EXCLUSIONS.md`

**Content**:
```markdown
# Doc ID Scanner Exclusions - Implementation Notes

**Purpose**: Document why `.worktrees/` exclusion prevents race conditions  
**Date**: 2025-11-29  
**Status**: Canonical reference

---

## Current Exclusions

From `scripts/doc_id_scanner.py`:

```python
EXCLUDE_PATTERNS = [
    ".venv",
    "__pycache__",
    ".git",
    "node_modules",
    ".pytest_cache",
    ".worktrees",      # ← Prevents worktree race condition
    "legacy",
    ".state",
    "refactor_paths.db",
    "*.db-shm",
    "*.db-wal",
]
```

---

## Why Worktrees Are Excluded

### The Risk (If Not Excluded)

During multi-agent orchestration:

```
main branch:           core/state/db.py (no doc_id yet)
.worktrees/agent-1/:   core/state/db.py (doc_id: DOC-001)
.worktrees/agent-2/:   core/state/db.py (doc_id: DOC-002)
```

If scanner ran during orchestration WITHOUT exclusion:
1. Finds 3 versions of `core/state/db.py`
2. Creates 3 entries in `docs_inventory.jsonl`
3. Registry corruption - which is truth?

### The Solution (Already Implemented)

✅ `.worktrees` in `EXCLUDE_PATTERNS`:
- Scanner never enters worktree directories
- Only scans main branch
- Single source of truth maintained

### Additional Safety

See `ID_LIFECYCLE_RULES.yaml` for:
- `conflict_resolution.same_file_different_ids` - handles edge cases
- `validation.preflight_checks` - validates before orchestration

---

## When Scanner Runs

### Safe Times ✅
- Before orchestration (no worktrees exist)
- After orchestration completes (worktrees cleaned up)
- During development (no orchestration active)

### Unsafe Times ❌
- During active orchestration (worktrees exist, agents working)
  
**Protection**: Optional `orchestration.lock` file (see Phase 1)

---

## Testing Exclusions

```bash
# Create test worktree
git worktree add .worktrees/test-wt main

# Run scanner
python scripts/doc_id_scanner.py scan

# Verify worktree files NOT in inventory
grep ".worktrees" docs_inventory.jsonl
# Should return nothing

# Cleanup
git worktree remove .worktrees/test-wt
```

---

## Related Safeguards

1. **Central Registry**: `doc_id_registry_cli.py` ensures unique IDs
2. **Phase 3 Plan**: IDs assigned BEFORE worktrees created
3. **Conflict Resolution**: Rules for edge cases (ID_LIFECYCLE_RULES.yaml)

---

## Conclusion

✅ Scanner exclusion ALREADY prevents worktree race conditions  
✅ No additional code changes needed  
✅ This document explains WHY it works

**Status**: SOLVED - documented for future reference
```

**Validation**:
```bash
# Verify exclusions work
python scripts/doc_id_scanner.py scan --verbose 2>&1 | grep "Excluding"
```

---

## Phase 1: Safety Mechanisms (1 hour)

**Goal**: Add optional safety belts and validation

### Step 1.1: Add Orchestration Lock (15 min)

**Purpose**: Prevent scanner from running during active orchestration

**File 1**: `scripts/orchestration_lock.py` (NEW)

```python
"""Orchestration lock management."""
from pathlib import Path
from datetime import datetime
import json

LOCK_FILE = Path(".state/orchestration.lock")

def acquire_lock(orchestrator_pid: int) -> bool:
    """Acquire orchestration lock. Returns True if acquired."""
    if LOCK_FILE.exists():
        # Check if stale (process not running)
        lock_data = json.loads(LOCK_FILE.read_text())
        # Optional: check if PID still running
        return False
    
    # Create lock
    lock_data = {
        "acquired_at": datetime.utcnow().isoformat(),
        "pid": orchestrator_pid,
        "status": "active"
    }
    LOCK_FILE.write_text(json.dumps(lock_data, indent=2))
    return True

def release_lock() -> None:
    """Release orchestration lock."""
    if LOCK_FILE.exists():
        LOCK_FILE.unlink()

def is_locked() -> bool:
    """Check if orchestration is active."""
    return LOCK_FILE.exists()

def get_lock_info() -> dict:
    """Get lock information."""
    if LOCK_FILE.exists():
        return json.loads(LOCK_FILE.read_text())
    return {}
```

**File 2**: Update `scripts/doc_id_scanner.py`

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
    
    # Continue with scan...
```

**Validation**:
```bash
# Test lock
python -c "from scripts.orchestration_lock import acquire_lock, is_locked; acquire_lock(1234); print(is_locked())"

# Test scanner with lock
python scripts/doc_id_scanner.py scan
# Should error: "Cannot scan during active orchestration"

# Cleanup
rm .state/orchestration.lock
```

---

### Step 1.2: Add Conflict Resolution Utilities (30 min)

**File**: `scripts/id_conflict_resolver.py` (NEW)

```python
"""ID conflict detection and resolution utilities."""
from pathlib import Path
from datetime import datetime
import json
from typing import List, Dict, Tuple

def detect_conflicts(inventory_path: Path = Path("docs_inventory.jsonl")) -> Dict:
    """Detect ID conflicts in inventory.
    
    Returns:
        {
            "same_file_different_ids": [...],
            "different_files_same_id": [...],
            "format_violations": [...]
        }
    """
    conflicts = {
        "same_file_different_ids": [],
        "different_files_same_id": [],
        "format_violations": []
    }
    
    if not inventory_path.exists():
        return conflicts
    
    # Build maps
    path_to_ids = {}  # path -> list of doc_ids
    id_to_paths = {}  # doc_id -> list of paths
    
    for line in inventory_path.read_text().strip().split("\n"):
        entry = json.loads(line)
        path = entry.get("path")
        doc_id = entry.get("doc_id")
        
        if not doc_id:
            continue
        
        # Check format
        if not is_valid_format(doc_id):
            conflicts["format_violations"].append({
                "path": path,
                "doc_id": doc_id,
                "reason": "Does not match DOC-<CAT>-<NAME>-<SEQ> format"
            })
        
        # Track path -> IDs
        if path not in path_to_ids:
            path_to_ids[path] = []
        path_to_ids[path].append(doc_id)
        
        # Track ID -> paths
        if doc_id not in id_to_paths:
            id_to_paths[doc_id] = []
        id_to_paths[doc_id].append(path)
    
    # Detect same_file_different_ids
    for path, doc_ids in path_to_ids.items():
        if len(doc_ids) > 1:
            conflicts["same_file_different_ids"].append({
                "path": path,
                "doc_ids": doc_ids
            })
    
    # Detect different_files_same_id
    for doc_id, paths in id_to_paths.items():
        if len(paths) > 1:
            conflicts["different_files_same_id"].append({
                "doc_id": doc_id,
                "paths": paths
            })
    
    return conflicts

def is_valid_format(doc_id: str) -> bool:
    """Validate doc_id format: DOC-<CAT>-<NAME>-<SEQ>"""
    import re
    pattern = r"^DOC-[A-Z]+-[A-Z0-9-]+-\d{3}$"
    return bool(re.match(pattern, doc_id))

def resolve_same_file_conflict(path: str, doc_ids: List[str], keep_id: str) -> None:
    """Resolve same_file_different_ids conflict.
    
    Implements first-merged-wins policy:
    - Keep specified doc_id
    - Mark others as superseded
    """
    from doc_id_registry_cli import mark_superseded
    
    for doc_id in doc_ids:
        if doc_id != keep_id:
            mark_superseded(
                doc_id=doc_id,
                superseded_by=keep_id,
                reason=f"Conflict resolution: same file multiple IDs"
            )
    
    print(f"✅ Resolved conflict for {path}")
    print(f"   Kept: {keep_id}")
    print(f"   Superseded: {[id for id in doc_ids if id != keep_id]}")

def generate_conflict_report(conflicts: Dict, output_path: Path) -> None:
    """Generate human-readable conflict report."""
    timestamp = datetime.utcnow().isoformat()
    
    report = f"""# ID Conflict Report
**Generated**: {timestamp}
**Total Conflicts**: {sum(len(v) for v in conflicts.values())}

---

## Same File, Different IDs

{len(conflicts['same_file_different_ids'])} conflicts found.

"""
    
    for conflict in conflicts["same_file_different_ids"]:
        report += f"""
### {conflict['path']}

**Conflicting IDs**:
{chr(10).join(f'- {id}' for id in conflict['doc_ids'])}

**Resolution**: Choose one ID to keep, others will be marked superseded.

```bash
python scripts/id_conflict_resolver.py resolve-same-file \\
  --path "{conflict['path']}" \\
  --keep "DOC-..." 
```

---
"""
    
    report += f"""
## Different Files, Same ID

{len(conflicts['different_files_same_id'])} conflicts found.

"""
    
    for conflict in conflicts["different_files_same_id"]:
        report += f"""
### {conflict['doc_id']}

**Conflicting Paths**:
{chr(10).join(f'- {path}' for path in conflict['paths'])}

**Resolution**: CRITICAL - Manual intervention required. Choose which file keeps this ID.

---
"""
    
    report += f"""
## Format Violations

{len(conflicts['format_violations'])} violations found.

"""
    
    for violation in conflicts["format_violations"]:
        report += f"""
### {violation['path']}

**Invalid ID**: `{violation['doc_id']}`  
**Reason**: {violation['reason']}

**Expected Format**: `DOC-<CATEGORY>-<NAME>-<SEQ>`  
**Example**: `DOC-CORE-STATE-001`

---
"""
    
    output_path.write_text(report)
    print(f"✅ Conflict report: {output_path}")

# CLI
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ID conflict detection and resolution")
    parser.add_argument("command", choices=["detect", "resolve-same-file"])
    parser.add_argument("--path", help="File path for resolution")
    parser.add_argument("--keep", help="doc_id to keep")
    
    args = parser.parse_args()
    
    if args.command == "detect":
        conflicts = detect_conflicts()
        if any(conflicts.values()):
            report_path = Path(f"reports/id_conflicts_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md")
            report_path.parent.mkdir(exist_ok=True)
            generate_conflict_report(conflicts, report_path)
            exit(1)
        else:
            print("✅ No conflicts detected")
            exit(0)
    
    elif args.command == "resolve-same-file":
        # Implementation for resolution
        pass
```

**Validation**:
```bash
# Test conflict detection
python scripts/id_conflict_resolver.py detect
```

---

### Step 1.3: Add Preflight Validator (15 min)

**File**: Update `scripts/preflight_validator.py`

```python
# Add to existing preflight checks

def validate_id_coverage(self, threshold: float = 1.0) -> bool:
    """Validate ID coverage meets threshold.
    
    Args:
        threshold: 0.0-1.0 (default 1.0 = 100%)
    
    Returns:
        True if coverage >= threshold
    """
    from doc_id_scanner import DocIDScanner
    
    scanner = DocIDScanner()
    stats = scanner.get_stats()
    
    total = stats["total_files"]
    with_id = stats["files_with_id"]
    coverage = with_id / total if total > 0 else 0
    
    print(f"📊 ID Coverage: {coverage*100:.1f}% ({with_id}/{total})")
    
    if coverage < threshold:
        print(f"❌ Coverage {coverage*100:.1f}% below threshold {threshold*100:.1f}%")
        print(f"   Missing IDs: {total - with_id} files")
        print(f"   Run: python scripts/doc_id_scanner.py report")
        return False
    
    print(f"✅ ID coverage meets threshold")
    return True

def validate_id_conflicts(self) -> bool:
    """Check for ID conflicts."""
    from id_conflict_resolver import detect_conflicts
    
    conflicts = detect_conflicts()
    
    if any(conflicts.values()):
        print("❌ ID conflicts detected:")
        for conflict_type, items in conflicts.items():
            if items:
                print(f"   {conflict_type}: {len(items)}")
        print("   Run: python scripts/id_conflict_resolver.py detect")
        return False
    
    print("✅ No ID conflicts")
    return True

# Add to main preflight check
def run_preflight(self) -> bool:
    """Run all preflight checks."""
    checks = [
        ("Disk space", self.check_disk_space),
        ("Git status", self.check_git_status),
        ("Dependencies", self.check_dependencies),
        ("ID coverage", lambda: self.validate_id_coverage(threshold=1.0)),  # ← NEW
        ("ID conflicts", self.validate_id_conflicts),  # ← NEW
    ]
    
    results = []
    for name, check_fn in checks:
        print(f"\n🔍 Checking: {name}...")
        result = check_fn()
        results.append((name, result))
    
    # Summary
    print("\n" + "="*60)
    print("PREFLIGHT SUMMARY")
    print("="*60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} | {name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n✅ All preflight checks passed - ready to execute")
    else:
        print("\n❌ Some preflight checks failed - fix before proceeding")
    
    return all_passed
```

**Validation**:
```bash
# Run preflight
python scripts/preflight_validator.py

# Should check:
# - Disk space
# - Git status  
# - Dependencies
# - ID coverage (100%)
# - ID conflicts (none)
```

---

## Phase 2: Integration with Orchestration (1 hour)

**Goal**: Integrate ID framework with multi-agent orchestration workflow

### Step 2.1: Update Orchestration Script (30 min)

**File**: Update `scripts/run_multi_agent_refactor.ps1`

```powershell
# At start of script
Write-Host "🔒 Acquiring orchestration lock..." -ForegroundColor Yellow
python -c "from scripts.orchestration_lock import acquire_lock; import os; acquire_lock(os.getpid())"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to acquire lock - orchestration already running?" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Lock acquired" -ForegroundColor Green

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

# Run preflight validation
Write-Host "`n🔍 Running preflight validation..." -ForegroundColor Cyan
python scripts/preflight_validator.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Preflight validation failed" -ForegroundColor Red
    python -c "from scripts.orchestration_lock import release_lock; release_lock()"
    exit 1
}

Write-Host "✅ Preflight passed" -ForegroundColor Green

# ... (existing orchestration code) ...

# At end of successful execution
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

---

### Step 2.2: Verify Workstream File Mappings (30 min)

**Task**: Check if workstream JSONs have `files_to_edit` field

```bash
# Check sample workstream
cat workstreams/ws-22.json | jq '.files_to_edit'

# If null/missing, add template
```

**If missing, add to workstream template**:

**File**: `workstreams/WORKSTREAM_TEMPLATE.json`

```json
{
  "id": "ws-XXX",
  "name": "Workstream Name",
  "description": "What this workstream does",
  "depends_on": [],
  "estimated_hours": 1,
  "tool": "aider",
  
  "files_to_edit": [
    "path/to/file1.py",
    "path/to/file2.py"
  ],
  
  "files_to_create": [
    "path/to/new_file.md"
  ],
  
  "validation": {
    "run_tests": true,
    "test_pattern": "tests/path/test_*.py"
  }
}
```

**Validation Script**: `scripts/validate_workstreams.py` (update)

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

## Phase 3: Documentation & Validation (1 hour)

**Goal**: Complete documentation and create validation suite

### Step 3.1: Create Conflict Resolution Procedures (30 min)

**File**: `docs/ID_CONFLICT_RESOLUTION_PROCEDURES.md`

```markdown
# ID Conflict Resolution Procedures

**Purpose**: Step-by-step procedures for resolving ID conflicts  
**Audience**: Developers, orchestrator maintainers  
**Date**: 2025-11-29

---

## When Conflicts Occur

ID conflicts are **rare** if following best practices:
- ✅ Central registry used for minting
- ✅ Scanner runs before orchestration
- ✅ Worktrees operate on files with existing IDs

However, edge cases can occur during:
- Manual edits during orchestration
- Interrupted orchestration with partial merges
- Parallel development without coordination

---

## Detection

Run conflict detector:

```bash
python scripts/id_conflict_resolver.py detect
```

Outputs:
- `reports/id_conflicts_<timestamp>.md` (if conflicts found)
- Exit code 0 (no conflicts) or 1 (conflicts)

---

## Conflict Types & Resolutions

### Type 1: Same File, Different IDs

**Scenario**: One file has multiple doc_ids assigned

Example:
```
File: core/state/db.py
IDs:  DOC-CORE-STATE-DB-001 (agent 1)
      DOC-CORE-STATE-DB-002 (agent 2)
```

**Policy**: **First-merged-wins**

**Resolution Steps**:

1. **Identify which ID merged first**:
   ```bash
   git log --all --oneline --grep="DOC-CORE-STATE-DB-001"
   git log --all --oneline --grep="DOC-CORE-STATE-DB-002"
   ```

2. **Keep first-merged ID**:
   ```bash
   python scripts/id_conflict_resolver.py resolve-same-file \
     --path "core/state/db.py" \
     --keep "DOC-CORE-STATE-DB-001"
   ```

3. **Verify resolution**:
   ```bash
   python scripts/id_conflict_resolver.py detect
   ```

4. **Update registry**:
   - `DOC-CORE-STATE-DB-001`: status="active"
   - `DOC-CORE-STATE-DB-002`: status="superseded", superseded_by="DOC-CORE-STATE-DB-001"

---

### Type 2: Different Files, Same ID

**Scenario**: Two files claim same doc_id

Example:
```
ID:  DOC-CORE-DB-001
Files: core/state/db.py
       core/database/operations.py
```

**Policy**: **ERROR - Manual resolution required**

**Resolution Steps**:

1. **STOP orchestration** (if running)

2. **Investigate**:
   ```bash
   # Check both files
   head -20 core/state/db.py
   head -20 core/database/operations.py
   
   # Check git history
   git log --all -- core/state/db.py
   git log --all -- core/database/operations.py
   ```

3. **Decide which file keeps ID**:
   - Consider: which file is "primary"?
   - Check: which was created first?
   - Consult: module ownership

4. **Manual correction**:
   ```bash
   # Option A: Assign new ID to one file
   python doc_id/doc_id_registry_cli.py mint \
     --category CORE \
     --name DB-OPERATIONS
   
   # Edit file header to new ID
   # Update docs_inventory.jsonl
   
   # Option B: Retire one file's ID
   python scripts/id_conflict_resolver.py retire \
     --doc-id "DOC-CORE-DB-001" \
     --file "core/database/operations.py" \
     --reason "Duplicate ID - reassigned"
   ```

5. **Validate fix**:
   ```bash
   python scripts/id_conflict_resolver.py detect
   ```

6. **Resume orchestration**

---

### Type 3: Format Violations

**Scenario**: doc_id doesn't match expected format

Example:
```
Invalid: doc-core-db-1
Valid:   DOC-CORE-DB-001
```

**Policy**: **Reject and correct**

**Resolution Steps**:

1. **Identify violations**:
   ```bash
   python scripts/id_conflict_resolver.py detect
   # Check "Format Violations" section
   ```

2. **Correct format**:
   ```bash
   # Edit file to correct format
   # Pattern: DOC-<CATEGORY>-<NAME>-<SEQ>
   # SEQ must be 3 digits: 001, 002, etc.
   ```

3. **Update registry**:
   ```bash
   python doc_id/doc_id_registry_cli.py validate
   ```

---

## Prevention

### Best Practices

1. **Always use central registry**:
   ```bash
   python doc_id/doc_id_registry_cli.py mint ...
   ```

2. **Run scanner before orchestration**:
   ```bash
   python scripts/doc_id_scanner.py scan
   ```

3. **Validate before committing**:
   ```bash
   python scripts/id_conflict_resolver.py detect
   ```

4. **Use preflight checks**:
   ```bash
   python scripts/preflight_validator.py
   ```

### CI Integration

Add to `.github/workflows/validate-ids.yml`:

```yaml
name: Validate Doc IDs
on: [pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Detect ID conflicts
        run: python scripts/id_conflict_resolver.py detect
```

---

## Escalation

If conflict cannot be resolved:

1. **Document the conflict** in `reports/critical_id_conflict_<date>.md`
2. **Tag issue** with `critical-id-conflict`
3. **Notify** repository maintainers
4. **Halt refactor** until resolved

---

## Appendix: Conflict Examples

### Example 1: Parallel agents assign different IDs

**Timeline**:
- 10:00 - Agent 1 starts WS-22, file has no doc_id
- 10:05 - Agent 1 assigns DOC-CORE-DB-001
- 10:06 - Agent 2 starts WS-03, same file still has no doc_id (branch diverged)
- 10:10 - Agent 2 assigns DOC-CORE-DB-002
- 10:15 - Agent 1 merges (DOC-CORE-DB-001 in main)
- 10:20 - Agent 2 tries to merge → CONFLICT

**Resolution**: Keep DOC-CORE-DB-001 (first merged)

**Prevention**: Use central ID coordinator OR assign IDs before worktrees created

---

### Example 2: Manual edit introduces duplicate

**Timeline**:
- File A has DOC-CORE-001
- Developer copies File A → File B
- Forgets to update doc_id in File B
- File B still has DOC-CORE-001 → CONFLICT

**Resolution**: Assign new ID to File B

**Prevention**: Linters check for duplicate IDs in pre-commit hook

---

## See Also

- `ID_LIFECYCLE_RULES.yaml` - Lifecycle policies
- `SCANNER_EXCLUSIONS.md` - Why worktrees are safe
- `scripts/id_conflict_resolver.py` - Detection tool
```

---

### Step 3.2: Create Validation Test Suite (30 min)

**File**: `tests/test_id_framework.py`

```python
"""Test suite for ID framework."""
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

class TestIDFormat:
    """Test ID format validation."""
    
    def test_valid_formats(self):
        """Valid doc_id formats should pass."""
        valid_ids = [
            "DOC-CORE-STATE-001",
            "DOC-ERROR-PLUGIN-002",
            "DOC-SPEC-SCHEMA-003",
            "DOC-PATTERN-EXEC-APPLY-004",
        ]
        for doc_id in valid_ids:
            assert is_valid_format(doc_id), f"{doc_id} should be valid"
    
    def test_invalid_formats(self):
        """Invalid doc_id formats should fail."""
        invalid_ids = [
            "doc-core-state-001",  # Lowercase
            "DOC-CORE-STATE-1",    # Short sequence
            "CORE-STATE-001",      # Missing DOC prefix
            "DOC_CORE_STATE_001",  # Underscores
            "DOC-CORE-STATE",      # Missing sequence
        ]
        for doc_id in invalid_ids:
            assert not is_valid_format(doc_id), f"{doc_id} should be invalid"

class TestConflictDetection:
    """Test conflict detection."""
    
    @pytest.fixture
    def temp_inventory(self):
        """Create temporary inventory file."""
        temp_dir = tempfile.mkdtemp()
        inventory_path = Path(temp_dir) / "test_inventory.jsonl"
        yield inventory_path
        shutil.rmtree(temp_dir)
    
    def test_no_conflicts(self, temp_inventory):
        """No conflicts in clean inventory."""
        entries = [
            {"path": "file1.py", "doc_id": "DOC-CORE-001"},
            {"path": "file2.py", "doc_id": "DOC-CORE-002"},
        ]
        temp_inventory.write_text("\n".join(json.dumps(e) for e in entries))
        
        conflicts = detect_conflicts(temp_inventory)
        assert not any(conflicts.values())
    
    def test_same_file_different_ids(self, temp_inventory):
        """Detect same file with different IDs."""
        entries = [
            {"path": "file1.py", "doc_id": "DOC-CORE-001"},
            {"path": "file1.py", "doc_id": "DOC-CORE-002"},
        ]
        temp_inventory.write_text("\n".join(json.dumps(e) for e in entries))
        
        conflicts = detect_conflicts(temp_inventory)
        assert len(conflicts["same_file_different_ids"]) == 1
        assert conflicts["same_file_different_ids"][0]["path"] == "file1.py"
    
    def test_different_files_same_id(self, temp_inventory):
        """Detect different files with same ID."""
        entries = [
            {"path": "file1.py", "doc_id": "DOC-CORE-001"},
            {"path": "file2.py", "doc_id": "DOC-CORE-001"},
        ]
        temp_inventory.write_text("\n".join(json.dumps(e) for e in entries))
        
        conflicts = detect_conflicts(temp_inventory)
        assert len(conflicts["different_files_same_id"]) == 1
        assert conflicts["different_files_same_id"][0]["doc_id"] == "DOC-CORE-001"
    
    def test_format_violations(self, temp_inventory):
        """Detect format violations."""
        entries = [
            {"path": "file1.py", "doc_id": "DOC-CORE-001"},
            {"path": "file2.py", "doc_id": "invalid-format"},
        ]
        temp_inventory.write_text("\n".join(json.dumps(e) for e in entries))
        
        conflicts = detect_conflicts(temp_inventory)
        assert len(conflicts["format_violations"]) == 1

class TestScannerExclusions:
    """Test scanner exclusions."""
    
    def test_worktrees_excluded(self):
        """Verify .worktrees is in exclusions."""
        from scripts.doc_id_scanner import EXCLUDE_PATTERNS
        assert ".worktrees" in EXCLUDE_PATTERNS
    
    def test_state_excluded(self):
        """Verify .state is in exclusions."""
        from scripts.doc_id_scanner import EXCLUDE_PATTERNS
        assert ".state" in EXCLUDE_PATTERNS

class TestOrchestrationLock:
    """Test orchestration lock mechanism."""
    
    def test_acquire_release(self):
        """Test lock acquisition and release."""
        from scripts.orchestration_lock import acquire_lock, release_lock, is_locked
        
        # Initially unlocked
        release_lock()  # Ensure clean state
        assert not is_locked()
        
        # Acquire lock
        assert acquire_lock(12345)
        assert is_locked()
        
        # Release lock
        release_lock()
        assert not is_locked()
    
    def test_double_acquire_fails(self):
        """Cannot acquire lock twice."""
        from scripts.orchestration_lock import acquire_lock, release_lock
        
        release_lock()  # Clean state
        assert acquire_lock(12345)
        assert not acquire_lock(67890)  # Should fail
        
        release_lock()  # Cleanup

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**Validation**:
```bash
# Run test suite
pytest tests/test_id_framework.py -v

# Should pass all tests
```

---

## Phase 4: Final Integration & Documentation (30 min)

**Goal**: Update main documentation and create execution checklist

### Step 4.1: Update Main README (15 min)

**File**: Update `README.md` (ID Framework section)

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

---

### Step 4.2: Create Execution Checklist (15 min)

**File**: `doc_id/PHASE_COMPLETION_CHECKLIST.md`

```markdown
# ID Framework Completion - Execution Checklist

**Phase Plan**: PLAN-DOC-ID-COMPLETION-001  
**Estimated Time**: 3-4 hours  
**Date**: 2025-11-29

---

## Phase 0: Foundation (30 min)

- [ ] **Step 0.1**: Create ID_LIFECYCLE_RULES.yaml (15 min)
  - [ ] File created in `doc_id/ID_LIFECYCLE_RULES.yaml`
  - [ ] YAML syntax validated
  - [ ] Contains all lifecycle rules (split, merge, move, rename, delete)
  - [ ] Contains conflict resolution policies
  - [ ] Contains validation rules

- [ ] **Step 0.2**: Document Scanner Exclusions (15 min)
  - [ ] File created: `doc_id/SCANNER_EXCLUSIONS.md`
  - [ ] Documents why `.worktrees` excluded
  - [ ] Includes testing instructions
  - [ ] Explains safety mechanisms

**Validation**:
```bash
python -c "import yaml; yaml.safe_load(open('doc_id/ID_LIFECYCLE_RULES.yaml'))"
python scripts/doc_id_scanner.py scan --verbose 2>&1 | grep "Excluding"
```

---

## Phase 1: Safety Mechanisms (1 hour)

- [ ] **Step 1.1**: Add Orchestration Lock (15 min)
  - [ ] Created `scripts/orchestration_lock.py`
  - [ ] Updated `scripts/doc_id_scanner.py` to check lock
  - [ ] Tested lock acquire/release
  - [ ] Tested scanner error when locked

- [ ] **Step 1.2**: Add Conflict Resolution Utilities (30 min)
  - [ ] Created `scripts/id_conflict_resolver.py`
  - [ ] Implements `detect_conflicts()`
  - [ ] Implements `is_valid_format()`
  - [ ] Implements `generate_conflict_report()`
  - [ ] CLI works: `python scripts/id_conflict_resolver.py detect`

- [ ] **Step 1.3**: Add Preflight Validator (15 min)
  - [ ] Updated `scripts/preflight_validator.py`
  - [ ] Added `validate_id_coverage()`
  - [ ] Added `validate_id_conflicts()`
  - [ ] Integrated into main preflight check
  - [ ] Tested: `python scripts/preflight_validator.py`

**Validation**:
```bash
python scripts/orchestration_lock.py
python scripts/id_conflict_resolver.py detect
python scripts/preflight_validator.py
```

---

## Phase 2: Orchestration Integration (1 hour)

- [ ] **Step 2.1**: Update Orchestration Script (30 min)
  - [ ] Updated `scripts/run_multi_agent_refactor.ps1`
  - [ ] Acquires lock at start
  - [ ] Added trap for cleanup on interrupt
  - [ ] Runs preflight validation
  - [ ] Releases lock at end
  - [ ] Post-orchestration conflict check

- [ ] **Step 2.2**: Verify Workstream File Mappings (30 min)
  - [ ] Checked sample workstreams for `files_to_edit`
  - [ ] Created `WORKSTREAM_TEMPLATE.json` if missing
  - [ ] Updated `scripts/validate_workstreams.py`
  - [ ] Tested workstream validation

**Validation**:
```bash
# Test orchestration script (dry-run)
./scripts/run_multi_agent_refactor.ps1 --dry-run

# Check workstream
cat workstreams/ws-22.json | jq '.files_to_edit'
```

---

## Phase 3: Documentation & Validation (1 hour)

- [ ] **Step 3.1**: Create Conflict Resolution Procedures (30 min)
  - [ ] Created `docs/ID_CONFLICT_RESOLUTION_PROCEDURES.md`
  - [ ] Documents all conflict types
  - [ ] Step-by-step resolution procedures
  - [ ] Includes prevention best practices
  - [ ] Examples included

- [ ] **Step 3.2**: Create Validation Test Suite (30 min)
  - [ ] Created `tests/test_id_framework.py`
  - [ ] Tests ID format validation
  - [ ] Tests conflict detection
  - [ ] Tests scanner exclusions
  - [ ] Tests orchestration lock
  - [ ] All tests passing

**Validation**:
```bash
pytest tests/test_id_framework.py -v
```

---

## Phase 4: Final Integration (30 min)

- [ ] **Step 4.1**: Update Main README (15 min)
  - [ ] Added ID Framework section to README.md
  - [ ] Quick start commands
  - [ ] Key files listed
  - [ ] Integration explained

- [ ] **Step 4.2**: Create Execution Checklist (15 min)
  - [ ] Created this file
  - [ ] All steps documented
  - [ ] Validation commands included

**Final Validation**:
```bash
# Full validation suite
python scripts/preflight_validator.py
pytest tests/test_id_framework.py -v
python scripts/id_conflict_resolver.py detect
python scripts/doc_id_scanner.py stats
```

---

## Completion Criteria

All items checked ✅ AND:

- [ ] **Coverage**: 100% ID coverage (or documented exceptions)
- [ ] **Conflicts**: Zero ID conflicts detected
- [ ] **Tests**: All tests passing
- [ ] **Documentation**: All files created and reviewed
- [ ] **Integration**: Orchestration script updated and tested

---

## Post-Completion

- [ ] Commit all changes:
  ```bash
  git add .
  git commit -m "feat: complete ID framework integration (PLAN-DOC-ID-COMPLETION-001)"
  ```

- [ ] Generate final report:
  ```bash
  python scripts/doc_id_scanner.py report
  cp DOC_ID_COVERAGE_REPORT.md reports/id_coverage_final_$(date +%Y%m%d).md
  ```

- [ ] Tag release:
  ```bash
  git tag -a id-framework-v1.0 -m "ID Framework v1.0 - Production Ready"
  ```

---

**Status**: Ready to execute  
**Estimated Time**: 3-4 hours  
**Priority**: Complete before module refactor
```

---

## Summary

This phase plan creates a **production-ready ID framework** that:

✅ **Closes Real Gaps**:
- ID lifecycle rules (split, merge, delete)
- Conflict resolution policies
- Validation and enforcement

✅ **Adds Safety**:
- Orchestration lock
- Conflict detection
- Preflight validation

✅ **Integrates with Orchestration**:
- Updates orchestration script
- Cleanup on interrupt
- Post-execution validation

✅ **Documents Everything**:
- Lifecycle rules
- Conflict procedures
- Scanner exclusions

**Total Time**: 3-4 hours  
**Deliverables**: 12 new/updated files  
**Status**: Ready to execute

---

**Next Step**: Execute Phase 0 (30 min) to create foundation files.

