---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-CHECKLIST_QUICK_START-052
---

# Repository Checklist - Quick Start

## What Is This?

A **machine-readable validation system** that consolidates all repository compliance, validation, and quality requirements into a single JSON spec.

## Quick Commands

### Run All Validations

```powershell
.\scripts\validate\validate_repo_checklist.ps1
```

### Run Specific Checks

```powershell
# State infrastructure only
.\scripts\validate\validate_repo_checklist.ps1 -RequirementFilter "STATE-OBS-001,STATE-OBS-002,STATE-OBS-003"

# Audit requirements
.\scripts\validate\validate_repo_checklist.ps1 -RequirementFilter "AUDIT-001,AUDIT-002"

# ACS artifacts
.\scripts\validate\validate_repo_checklist.ps1 -RequirementFilter "ACS-ARTIFACTS-001"
```

### JSON Output (for CI)

```powershell
.\scripts\validate\validate_repo_checklist.ps1 -JsonOutput
```

## Key Locations

- **Checklist Spec**: `.ai-orch/checklists/repo_checklist.json`
- **Validator Script**: `scripts/validate/validate_repo_checklist.ps1`
- **State Directory**: `.state/`
- **Documentation**: `docs/operations/REPO_CHECKLIST.md`

## Requirement IDs

### Categories

- `ACS-*` - AI Codebase Structure
- `STATE-OBS-*` - State observability
- `AUDIT-*` - Audit trail
- `WS-*` - Workstream validation
- `PATH-STD-*` - Path standards
- `TEST-*` - Test suite
- `ENGINE-*` - Engine validation
- `ERROR-*` - Error module validation
- `FOLDER-*` - Folder-level requirements

### Example Requirements

```
ACS-ARTIFACTS-001  - Core ACS files must exist
STATE-OBS-001      - .state directory layout
STATE-OBS-002      - .state/current.json validity
AUDIT-001          - Audit trail documentation
TEST-PYTEST-001    - Pytest suite passes
```

## Understanding Results

### Status Codes

- **✓ PASS** - Check passed, all good
- **✗ FAIL** - Check failed, fix required
- **⚠ SKIP** - Check skipped (not implemented or N/A)

### Exit Codes

- `0` - All checks passed
- `1` - One or more checks failed

## State Directory (`.state/`)

### What's There

```
.state/
├── current.json              # Current repo state
├── transitions.jsonl         # State change history
├── health.json              # Health status
├── indices/
│   ├── task_index.json
│   ├── workstream_index.json
│   └── capability_index.json
└── snapshots/               # (future: historical snapshots)
```

### Key Files

**`current.json`** - Current state snapshot
- `state_id`, `timestamp`, `status`, `phase`
- `current_workstreams`, `active_tasks`
- `capabilities`, `health`

**`transitions.jsonl`** - Append-only audit log
- One JSON object per line
- `transition_id`, `from_state`, `to_state`, `timestamp`
- Never modified, only appended

**`health.json`** - Repository health
- Overall status and component checks
- Metrics (transitions, snapshots, indices)
- Issues and recommendations

## Adding a New Requirement

1. Edit `.ai-orch/checklists/repo_checklist.json`
2. Add new requirement object:
   ```json
   {
     "requirement_id": "CATEGORY-DESC-NNN",
     "scope": "repo",
     "type": "check_type",
     "priority": "HIGH",
     "description": "What this checks",
     "params": { /* check-specific params */ }
   }
   ```
3. Test: `.\scripts\validate\validate_repo_checklist.ps1 -RequirementFilter "YOUR-NEW-ID"`

## Troubleshooting

### "Checklist file not found"

Run from repository root:
```powershell
cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"
.\scripts\validate\validate_repo_checklist.ps1
```

### "Unsupported check type"

Check type not yet implemented. Either:
- Implement the check type in validator script
- Or change to a supported type

### Check always fails

Run with verbose to debug:
```powershell
.\scripts\validate\validate_repo_checklist.ps1 -VerboseOutput
```

## Integration Examples

### Pre-commit Hook

```powershell
# .git/hooks/pre-commit
pwsh scripts/validate/validate_repo_checklist.ps1 -RequirementFilter "PATH-STD-001,TEST-PYTEST-001"
```

### GitHub Actions

```yaml
- name: Validate Repository
  run: |
    pwsh scripts/validate/validate_repo_checklist.ps1 -JsonOutput > results.json
```

### Local Development

```powershell
# Before pushing
.\scripts\validate\validate_repo_checklist.ps1

# If fails, fix issues and rerun
```

## More Information

- **Full Guide**: `docs/operations/REPO_CHECKLIST.md`
- **Audit Trail**: `docs/operations/AUDIT_TRAIL.md`
- **Retention Policy**: `docs/operations/AUDIT_RETENTION.md`
- **Implementation Summary**: `docs/operations/CHECKLIST_IMPLEMENTATION_SUMMARY.md`

## Quick Reference

```powershell
# All checks
.\scripts\validate\validate_repo_checklist.ps1

# Verbose
.\scripts\validate\validate_repo_checklist.ps1 -VerboseOutput

# JSON output
.\scripts\validate\validate_repo_checklist.ps1 -JsonOutput

# Specific checks
.\scripts\validate\validate_repo_checklist.ps1 -RequirementFilter "STATE-OBS-001,AUDIT-001"
```

## Version

**Quick Start Version**: 1.0.0  
**Last Updated**: 2025-11-23
