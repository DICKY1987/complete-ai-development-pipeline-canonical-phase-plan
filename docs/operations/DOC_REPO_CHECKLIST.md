---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-REPO_CHECKLIST-053
---

# Repository Checklist System

## Overview

This repository uses a **machine-readable, patch-friendly checklist system** to consolidate all validation, compliance, and quality requirements into a single source of truth.

## Architecture

### Core Components

1. **`.ai-orch/checklists/repo_checklist.json`** - Main checklist specification
2. **`.folder_checklist.json` files** (optional) - Folder-specific rules  
3. **`scripts/validate/validate_repo_checklist.ps1`** - Generic validator
4. **`.state/` directory** - Repository state tracking

## Quick Start

### Running the Validator

```powershell
# Run all checks
.\scripts\validate\validate_repo_checklist.ps1

# JSON output (for automation)
.\scripts\validate\validate_repo_checklist.ps1 -JsonOutput

# Specific requirements only
.\scripts\validate\validate_repo_checklist.ps1 -RequirementFilter "ACS-ARTIFACTS-001,STATE-OBS-001"

# Verbose mode
.\scripts\validate\validate_repo_checklist.ps1 -VerboseOutput
```

**Exit Codes:**
- `0` - All checks passed
- `1` - One or more checks failed

## Requirement IDs

### Naming Conventions

- **`ACS-*`** - AI Codebase Structure requirements
- **`STATE-OBS-*`** - State observability requirements
- **`AUDIT-*`** - Audit trail requirements
- **`WS-*`** - Workstream requirements
- **`PATH-STD-*`** - Path standards (CI enforced)
- **`TEST-*`** - Test suite requirements
- **`ENGINE-*`** - Engine validation
- **`ERROR-*`** - Error module requirements
- **`FOLDER-*`** - Folder-level requirements

### Current Requirements

See `.ai-orch/checklists/repo_checklist.json` for complete list.

## State Directory

The `.state/` directory tracks repository state:

```
.state/
├── current.json           # Current state snapshot
├── transitions.jsonl      # State transition history
├── health.json           # Repository health status
├── indices/
│   ├── task_index.json
│   ├── workstream_index.json
│   └── capability_index.json
└── snapshots/            # Historical snapshots
```

## Extending the System

### Add New Requirement

1. Edit `.ai-orch/checklists/repo_checklist.json`
2. Add requirement with unique ID
3. Test with validator

### Add New Check Type

1. Edit `scripts/validate/validate_repo_checklist.ps1`
2. Add case to `Invoke-Check` function
3. Update documentation

## Integration

### CI/CD

```yaml
# .github/workflows/validation.yml
- run: pwsh scripts/validate/validate_repo_checklist.ps1 -JsonOutput
```

### Pre-commit Hook

```powershell
pwsh scripts/validate/validate_repo_checklist.ps1 -RequirementFilter "PATH-STD-001,TEST-PYTEST-001"
```

## References

- **QUALITY_GATE.yaml** - Quality gates
- **ai_policies.yaml** - Edit policies
- **CODEBASE_INDEX.yaml** - Module structure
