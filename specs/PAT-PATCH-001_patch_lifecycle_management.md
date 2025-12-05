---
doc_id: DOC-PAT-PAT-PATCH-001-PATCH-LIFECYCLE-MANAGEMENT-865
---

# PAT-PATCH-001: Patch Lifecycle Management

## Pattern ID
**PAT-PATCH-001**

## Pattern Name
Patch Lifecycle Management (Check, Apply, Archive)

## Category
Infrastructure / DevOps

## Intent
Automatically detect patch application status, apply unapplied patches, and archive completed patches to maintain a clean, auditable patch workflow.

## Problem
- Patch files accumulate without clear status
- No automated way to know if a patch has been applied
- Applied patches remain in active directories causing clutter
- Risk of re-applying patches or losing patch history

## Solution
A three-stage automated workflow:
1. **Check**: Detect if patch is already applied
2. **Apply**: Apply unapplied patches with validation
3. **Archive**: Move successfully applied patches to timestamped archive

## Structure

### Directory Layout
```
patches/
├── active/              # Pending patches to be applied
├── archive/            # Successfully applied patches
│   └── YYYY-MM-DD/    # Date-based folders
└── failed/            # Patches that failed to apply
```

### Patch Naming Convention
```
{ID}-{description}.patch
Examples:
- 001-config-integration.patch
- 002-error-handler-fix.patch
- WS-002-database-migration.patch
```

## Implementation

### Detection Logic
```python
def is_patch_applied(patch_file: str, repo_path: str = ".") -> bool:
    """
    Check if a patch has been applied by attempting a dry-run.

    Returns:
        True if patch is already applied
        False if patch can be applied
    Raises:
        PatchConflictError if patch conflicts
    """
    result = subprocess.run(
        ["git", "apply", "--check", "--reverse", patch_file],
        cwd=repo_path,
        capture_output=True,
        text=True
    )

    # Exit code 0 means patch IS applied (reverse succeeds)
    # Exit code 1 means patch is NOT applied (reverse fails)
    return result.returncode == 0
```

### Application Logic
```python
def apply_patch(patch_file: str, repo_path: str = ".") -> dict:
    """
    Apply a patch file with validation.

    Returns:
        {
            "success": bool,
            "patch": str,
            "message": str,
            "output": str
        }
    """
    # Check if already applied
    if is_patch_applied(patch_file, repo_path):
        return {
            "success": True,
            "patch": patch_file,
            "message": "Already applied",
            "output": ""
        }

    # Attempt to apply
    result = subprocess.run(
        ["git", "apply", "--3way", patch_file],
        cwd=repo_path,
        capture_output=True,
        text=True
    )

    return {
        "success": result.returncode == 0,
        "patch": patch_file,
        "message": "Applied successfully" if result.returncode == 0 else "Failed to apply",
        "output": result.stdout + result.stderr
    }
```

### Archive Logic
```python
from pathlib import Path
from datetime import datetime
import shutil

def archive_patch(patch_file: str, archive_base: str = "patches/archive") -> str:
    """
    Move applied patch to dated archive folder.

    Returns:
        Path to archived file
    """
    patch_path = Path(patch_file)
    date_folder = datetime.now().strftime("%Y-%m-%d")
    archive_dir = Path(archive_base) / date_folder
    archive_dir.mkdir(parents=True, exist_ok=True)

    archive_path = archive_dir / patch_path.name
    shutil.move(str(patch_path), str(archive_path))

    return str(archive_path)
```

### Orchestration
```python
def process_patches(patch_dir: str = "patches/active", repo_path: str = ".") -> dict:
    """
    Process all patches: check, apply, archive.

    Returns:
        {
            "applied": [],
            "already_applied": [],
            "failed": [],
            "archived": []
        }
    """
    results = {
        "applied": [],
        "already_applied": [],
        "failed": [],
        "archived": []
    }

    patch_files = sorted(Path(patch_dir).glob("*.patch"))

    for patch_file in patch_files:
        patch_str = str(patch_file)

        # Check status
        already_applied = is_patch_applied(patch_str, repo_path)

        if already_applied:
            results["already_applied"].append(patch_str)
            # Archive already-applied patches
            archived = archive_patch(patch_str)
            results["archived"].append(archived)
            continue

        # Apply patch
        apply_result = apply_patch(patch_str, repo_path)

        if apply_result["success"]:
            results["applied"].append(patch_str)
            # Archive successfully applied
            archived = archive_patch(patch_str)
            results["archived"].append(archived)
        else:
            results["failed"].append({
                "patch": patch_str,
                "error": apply_result["output"]
            })
            # Move to failed directory
            failed_dir = Path("patches/failed")
            failed_dir.mkdir(exist_ok=True)
            shutil.move(patch_str, str(failed_dir / Path(patch_str).name))

    return results
```

## Usage

### CLI Tool
```bash
# Process all patches in active directory
python scripts/process_patches.py

# Check specific patch
python scripts/process_patches.py --check patches/active/001-fix.patch

# Apply specific patch
python scripts/process_patches.py --apply patches/active/001-fix.patch

# Dry run (no changes)
python scripts/process_patches.py --dry-run
```

### Script Output
```
Patch Processing Report
=======================
Patches Applied: 2
  ✓ 001-config-integration.patch
  ✓ 003-error-handler-fix.patch

Already Applied: 1
  ○ 002-database-migration.patch

Failed: 0

Archived: 3
  → patches/archive/2025-11-24/001-config-integration.patch
  → patches/archive/2025-11-24/002-database-migration.patch
  → patches/archive/2025-11-24/003-error-handler-fix.patch
```

## Integration Points

### Pre-commit Hook
```bash
# .git/hooks/pre-commit
python scripts/process_patches.py --check-only
```

### CI/CD Pipeline
```yaml
- name: Process Patches
  run: |
    python scripts/process_patches.py
    git add .
    git commit -m "Auto-archive applied patches" || true
```

### Quality Gate
Add to `QUALITY_GATE.yaml`:
```yaml
patch_management:
  command: python scripts/process_patches.py --validate
  required: true
  description: Ensure all patches are processed
```

## Success Criteria
- ✅ No unapplied patches in active directory
- ✅ All applied patches archived with timestamps
- ✅ Failed patches isolated in failed directory
- ✅ Audit trail maintained in archive
- ✅ Zero manual intervention required

## Anti-Patterns
❌ Deleting patches without archiving
❌ Applying patches without checking status first
❌ Mixed applied/unapplied patches in same directory
❌ No timestamping in archive
❌ Manual patch management

## Related Patterns
- **PAT-GIT-001**: Git Workflow Standards
- **PAT-CI-001**: Continuous Integration Pipeline
- **PAT-AUDIT-001**: Change Audit Trail

## References
- Git apply documentation: https://git-scm.com/docs/git-apply
- Patch-first pipeline philosophy (UET)
- `QUALITY_GATE.yaml` - Validation standards

## Metadata
- **Created**: 2025-11-24
- **Version**: 1.0.0
- **Status**: Active
- **Compliance**: UET, ACS
