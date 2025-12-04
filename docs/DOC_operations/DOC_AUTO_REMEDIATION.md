---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-DOC-AUTO-REMEDIATION-813
---

# Auto-Remediation System

## Overview

The auto-remediation engine **automatically fixes validation failures** detected by the checklist system. It analyzes failures, applies fixes, logs all actions to the audit trail, and updates repository state.

## Quick Start

### Run Auto-Remediation

```powershell
# Auto-fix all failures
.\scripts\validate\auto_remediate.ps1

# Dry-run (show what would be fixed)
.\scripts\validate\auto_remediate.ps1 -DryRun

# Interactive mode (confirm each fix)
.\scripts\validate\auto_remediate.ps1 -Interactive

# Fix specific requirements only
.\scripts\validate\auto_remediate.ps1 -RequirementFilter "WS-BUNDLE-001,TEST-PYTEST-001"
```

## How It Works

### 1. Detection
- Runs validator to identify failures
- Parses validation results JSON
- Filters by requirement ID if specified

### 2. Analysis
- Maps each failure to a fix function
- Determines if auto-fix is available
- Checks if fix is safe to apply

### 3. Remediation
- Applies fixes based on requirement type
- Creates backups before modifying files
- Validates fixes were applied correctly

### 4. Logging
- Logs all fixes to `.state/transitions.jsonl`
- Updates state to `STATE-REMEDIATED-001`
- Records what was fixed and when

## Currently Supported Fixes

### ✅ TEST-PYTEST-001: Pytest Import Conflicts

**Problem**: `tests/ast` directory conflicts with Python stdlib `ast` module

**Fix**:
- Renames `tests/ast` → `tests/syntax_analysis`
- Updates all import statements in test files
- No data loss, fully automated

**Usage**:
```powershell
.\scripts\validate\auto_remediate.ps1 -RequirementFilter "TEST-PYTEST-001"
```

### 🔧 WS-BUNDLE-001: Workstream Schema Migration

**Problem**: Old workstream bundle schema with deprecated fields

**Fix**:
- Migrates bundles to new schema format
- Creates `.backup` files before modification
- Preserves all essential data

**Status**: Implemented but needs schema refinement

**Usage**:
```powershell
.\scripts\validate\auto_remediate.ps1 -RequirementFilter "WS-BUNDLE-001"
```

### 🔧 Missing Files (Future)

**Problem**: Required files don't exist

**Fix**:
- Creates missing files with default content
- Sets up directory structure if needed
- Adds timestamped placeholders

**Status**: Framework implemented, needs mapping

## Workflow Integration

### Before Commit Workflow

```powershell
# 1. Run validation
.\scripts\validate\validate_repo_checklist.ps1

# 2. If failures, try auto-fix
.\scripts\validate\auto_remediate.ps1

# 3. Verify fixes
.\scripts\validate\validate_repo_checklist.ps1

# 4. Commit
git add .
git commit -m "fix: Auto-remediation applied"
```

### CI/CD Integration

```yaml
# .github/workflows/auto-fix.yml
- name: Validate Repository
  run: pwsh scripts/validate/validate_repo_checklist.ps1
  continue-on-error: true

- name: Auto-Remediate Failures
  if: failure()
  run: pwsh scripts/validate/auto_remediate.ps1

- name: Commit Fixes
  if: success()
  run: |
    git config user.name "Auto-Remediation Bot"
    git config user.email "bot@example.com"
    git add .
    git commit -m "fix: Auto-remediation applied [skip ci]"
    git push
```

### Pre-commit Hook

```powershell
# .git/hooks/pre-commit
# Run validator
pwsh scripts/validate/validate_repo_checklist.ps1

# If failures, try auto-fix
if ($LASTEXITCODE -ne 0) {
    pwsh scripts/validate/auto_remediate.ps1

    # Re-validate
    pwsh scripts/validate/validate_repo_checklist.ps1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "Auto-fixes applied - please review changes" -ForegroundColor Yellow
        exit 0
    }
}
```

## Adding New Auto-Fixes

### 1. Identify the Requirement

Find the requirement ID that needs auto-fix (e.g., `PATH-STD-001`)

### 2. Create Fix Function

```powershell
function Fix-YourRequirement {
    param(
        [Parameter(Mandatory)]
        [string]$RepoRoot,

        [Parameter()]
        [switch]$DryRun
    )

    Write-Host "  🔧 Analyzing your issue..." -ForegroundColor Yellow

    # Your fix logic here

    if (-not $DryRun) {
        # Apply actual fix
        # Create backups
        # Modify files
    }

    return @{
        Success = $true
        Message = "Description of what was fixed"
        Fixes = @("List", "Of", "Changes")
    }
}
```

### 3. Add to Dispatcher

In `Invoke-AutoRemediation`, add a case:

```powershell
switch ($requirement.requirement_id) {
    "YOUR-REQ-ID" {
        if ($Interactive) {
            $response = Read-Host "  Fix your issue? (y/n)"
            if ($response -ne 'y') { continue }
        }
        $fixResult = Fix-YourRequirement -RepoRoot $RepoRoot -DryRun:$DryRun
    }
}
```

### 4. Test

```powershell
# Dry-run first
.\scripts\validate\auto_remediate.ps1 -DryRun -RequirementFilter "YOUR-REQ-ID"

# Then apply
.\scripts\validate\auto_remediate.ps1 -RequirementFilter "YOUR-REQ-ID"
```

## Safety Features

### Backups
- All file modifications create `.backup` files
- Backups timestamped for recovery
- Never overwrites existing backups

### Dry-Run Mode
- Preview all changes before applying
- No modifications to repository
- Safe to run anytime

### Interactive Mode
- Prompts for confirmation on each fix
- User controls what gets fixed
- Can skip problematic fixes

### Audit Trail
- Every fix logged to `.state/transitions.jsonl`
- Includes what was fixed and when
- Full forensic trail

### State Tracking
- State transitions recorded
- Can trace back to before auto-fix
- Enables rollback if needed

## Troubleshooting

### "No auto-fix available"

The requirement has no automated fix yet. Either:
1. Fix manually
2. Implement auto-fix function
3. Skip this requirement

### "Fix failed"

The auto-fix couldn't complete. Check:
1. Error message in output
2. File permissions
3. Backup files created
4. Manual intervention needed

### "Validation still fails after fix"

The fix worked but exposed another issue. Either:
1. Run auto-remediate again (fixes new issue)
2. Fix remaining issues manually
3. Check `.backup` files if rollback needed

## Audit Trail Format

Auto-remediation logs transitions like:

```json
{
  "transition_id": "TRANS-REMED-20251123104530",
  "from_state": "STATE-VALIDATED-001",
  "to_state": "STATE-REMEDIATED-001",
  "timestamp": "2025-11-23T16:45:30.123Z",
  "trigger": "auto_remediation",
  "actor": "auto_remediation_engine",
  "metadata": {
    "reason": "Auto-fixed validation failures",
    "fixes_applied": 2,
    "requirements_fixed": ["TEST-PYTEST-001", "WS-BUNDLE-001"]
  }
}
```

## Future Enhancements

### Planned Auto-Fixes

- **PATH-STD-001**: Auto-update import paths
- **ACS-MODULE-DOCS-001**: Generate missing MODULE.md files
- **ENGINE-VALIDATE-001**: Fix engine schema issues
- **FOLDER-DOC-001**: Generate missing README.md files

### Smart Fixes

- **AI-powered fixes**: Use LLM to suggest complex fixes
- **Multi-step fixes**: Chain fixes for related issues
- **Conflict resolution**: Auto-resolve merge conflicts
- **Dependency fixes**: Fix broken dependencies

### Safety Improvements

- **Rollback command**: One-command undo
- **Snapshot before fix**: Auto-snapshot before changes
- **Verification tests**: Run tests after each fix
- **Diff preview**: Show exact changes before applying

## Examples

### Example 1: Fix Pytest Imports

```powershell
PS> .\scripts\validate\auto_remediate.ps1 -RequirementFilter "TEST-PYTEST-001"

╔══════════════════════════════════════════════════════════════════╗
║              AUTO-REMEDIATION ENGINE                         ║
╚══════════════════════════════════════════════════════════════════╝

🔍 Analyzing: [TEST-PYTEST-001] Test suite failed (exit code: 2)
  🔧 Analyzing pytest import conflicts...
  ✅ Fix applied:
    • Renamed directory: tests\ast → tests\syntax_analysis
    • Updated imports in test files

✅ Logged remediation to audit trail

======================================================================
REMEDIATION SUMMARY
======================================================================
Total Requirements: 1
✓ Fixed:   1
```

### Example 2: Dry-Run All Fixes

```powershell
PS> .\scripts\validate\auto_remediate.ps1 -DryRun

🔍 DRY RUN MODE - No changes will be made

Found 2 failed requirement(s)

🔧 Starting auto-remediation...

🔍 Analyzing: [WS-BUNDLE-001] ...
  ✅ Fix applied:
    • [DRY RUN] Would migrate 2 bundles to new schema

🔍 Analyzing: [TEST-PYTEST-001] ...
  ✅ Fix applied:
    • [DRY RUN] Would rename tests\ast directory

Total Requirements: 2
✓ Would Fix: 2
```

## References

- **Validator**: `scripts/validate/validate_repo_checklist.ps1`
- **Checklist Spec**: `.ai-orch/checklists/repo_checklist.json`
- **Audit Trail**: `.state/transitions.jsonl`
- **State Files**: `.state/current.json`

## Version

**Auto-Remediation Version**: 1.0.0
**Last Updated**: 2025-11-23
