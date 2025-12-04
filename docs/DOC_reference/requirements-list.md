---
doc_id: DOC-GUIDE-REQUIREMENTS-LIST-858
---

# Repository Validation Requirements - Complete List

**Checklist ID**: AI-ORCH-REPO-V1.0
**Total Requirements**: 19
**Last Updated**: 2025-11-23

## Priority Legend

- 🔴 **CRITICAL** - Must pass before commit
- 🟠 **HIGH** - Should pass before merge
- 🟡 **MEDIUM** - Aim to pass, warn if not
- 🟢 **LOW** - Aspirational, info only

---

## AI CODEBASE STRUCTURE (ACS) - 7 Requirements

### 🟠 ACS-ARTIFACTS-001
**Description**: Core ACS artifacts must exist
**Type**: required_files
**Scope**: repo
**Files Required**:
- CODEBASE_INDEX.yaml
- QUALITY_GATE.yaml
- ai_policies.yaml
- .aiignore
- .meta/AI_GUIDANCE.md
- .meta/ai_context/repo_summary.json
- .meta/ai_context/code_graph.json

### 🟠 ACS-MODULE-PATHS-001
**Description**: All modules in CODEBASE_INDEX.yaml must exist on disk
**Type**: module_path_validation
**Scope**: repo
**Status**: Implementation pending

### 🟠 ACS-MODULE-DEPS-001
**Description**: All dependency references in CODEBASE_INDEX must be valid module IDs
**Type**: dependency_validation
**Scope**: repo
**Status**: Implementation pending

### 🟡 ACS-MODULE-DOCS-001
**Description**: HIGH priority modules must have MODULE.md or README.md
**Type**: module_documentation
**Scope**: repo
**Status**: Implementation pending

### 🟡 ACS-CODE-GRAPH-001
**Description**: Code graph must be consistent with CODEBASE_INDEX
**Type**: code_graph_consistency
**Scope**: repo
**Status**: Implementation pending

### 🟡 ACS-POLICY-PATHS-001
**Description**: Paths in ai_policies.yaml must be valid relative patterns
**Type**: policy_path_validation
**Scope**: repo
**Status**: Implementation pending

### 🟡 ACS-INVARIANTS-001
**Description**: All invariants in ai_policies.yaml must be well-defined
**Type**: invariant_validation
**Scope**: repo
**Status**: Implementation pending

---

## STATE OBSERVABILITY (STATE-OBS) - 5 Requirements

### 🟠 STATE-OBS-001
**Description**: .state directory must have required structure
**Type**: directory_layout
**Scope**: repo
**Status**: ✅ IMPLEMENTED
**Required Structure**:
- .state/snapshots/ (directory)
- .state/indices/ (directory)
- .state/current.json (file)
- .state/transitions.jsonl (file)
- .state/health.json (file)

### 🟠 STATE-OBS-002
**Description**: .state/current.json must be valid with required fields
**Type**: json_file
**Scope**: repo
**Status**: ✅ IMPLEMENTED
**Required Fields**:
- schema_version
- state_id
- timestamp
- project_id
- status

### 🟠 STATE-OBS-003
**Description**: .state/transitions.jsonl must be valid JSONL with required fields per line
**Type**: json_lines_file
**Scope**: repo
**Status**: ✅ IMPLEMENTED
**Required Fields Per Line**:
- transition_id
- from_state
- to_state
- timestamp
- trigger

### 🟡 STATE-OBS-004
**Description**: Required index files must exist under .state/indices
**Type**: json_index_files
**Scope**: repo
**Status**: ✅ IMPLEMENTED
**Required Indices**:
- task_index.json
- workstream_index.json
- capability_index.json

### 🟡 STATE-OBS-005
**Description**: Indices must be derivable from current.json with overlap checks
**Type**: derived_index_sanity
**Scope**: repo
**Status**: Implementation pending

---

## AUDIT TRAIL (AUDIT) - 2 Requirements

### 🟡 AUDIT-001
**Description**: Audit trail documentation must exist
**Type**: file_exists
**Scope**: repo
**Status**: ✅ IMPLEMENTED
**Required File**: docs/operations/AUDIT_TRAIL.md

### 🟡 AUDIT-002
**Description**: Audit retention policy must exist
**Type**: file_exists
**Scope**: repo
**Status**: ✅ IMPLEMENTED
**Required File**: docs/operations/AUDIT_RETENTION.md

---

## WORKSTREAM VALIDATION (WS) - 1 Requirement

### 🟠 WS-BUNDLE-001
**Description**: All workstream bundles must be valid and have no overlapping file scopes
**Type**: workstream_validation
**Scope**: repo
**Status**: ✅ IMPLEMENTED (with auto-fix partially)
**Auto-Fix**: Available via `auto_remediate.ps1`

---

## PATH STANDARDS (PATH-STD) - 1 Requirement

### 🔴 PATH-STD-001
**Description**: No deprecated import paths allowed (CI enforced)
**Type**: import_path_standards
**Scope**: repo
**Status**: Implementation pending
**Forbidden Patterns**:
- `from src.pipeline` → use `from core.*`
- `from MOD_ERROR_PIPELINE` → use `from error.*`
- `from legacy.` → Do not import legacy code

---

## TEST SUITE (TEST) - 1 Requirement

### 🔴 TEST-PYTEST-001
**Description**: All pytest tests must pass
**Type**: test_suite
**Scope**: repo
**Status**: ✅ IMPLEMENTED
**Auto-Fix**: Available - fixes import conflicts
**Command**: `python -m pytest -q tests`

---

## ENGINE VALIDATION (ENGINE) - 1 Requirement

### 🟠 ENGINE-VALIDATE-001
**Description**: Engine components must be valid and importable
**Type**: engine_validation
**Scope**: repo
**Status**: Implementation pending
**Validates**:
- schema/jobs/job.schema.json
- schema/jobs/examples/aider_job.json
- engine.types, engine.interfaces, engine.adapters, engine.orchestrator

---

## ERROR MODULE (ERROR) - 1 Requirement

### 🟠 ERROR-IMPORTS-001
**Description**: Error module imports must follow section standards
**Type**: error_module_imports
**Scope**: repo
**Status**: Implementation pending
**Expected Pattern**: `from error.`

---

## FOLDER TEMPLATES - 3 Templates

### 📁 FOLDER-DOCS-001
**Description**: Code folders must have basic documentation
**Applies To**: core/**, engine/**, error/**, aim/**, pm/**, scripts/**, tools/**
**Rules**:
- README.md should exist (can be in parent)

### 📁 FOLDER-STATE-001
**Description**: Code folders must not mix dev and system files
**Applies To**: core/**, engine/**, error/**, aim/**, pm/**
**Forbidden Patterns**:
- phase_plan*.md
- execution_summary*.md
- temp_*.py
- scratch_*.py

### 📁 FOLDER-TESTS-001
**Description**: Module folders should have corresponding tests
**Applies To**: core/**, engine/**, error/**, aim/**, pm/**
**Rules**:
- Require 50% test coverage ratio
- Test patterns: test_*.py, *_test.py

---

## Summary by Priority

| Priority | Count | Description |
|----------|-------|-------------|
| 🔴 CRITICAL | 2 | Must pass before commit |
| 🟠 HIGH | 9 | Should pass before merge |
| 🟡 MEDIUM | 7 | Aim to pass, warn if not |
| 🟢 LOW | 1 | Aspirational, info only |

## Implementation Status

| Status | Count | Description |
|--------|-------|-------------|
| ✅ Implemented | 7 | Fully working with validator |
| 🔧 Partial | 1 | Working but needs refinement |
| 📝 Pending | 11 | Documented, not yet coded |

## Auto-Remediation Support

| Requirement | Auto-Fix Available |
|-------------|-------------------|
| TEST-PYTEST-001 | ✅ Yes (renames tests/ast) |
| WS-BUNDLE-001 | 🔧 Partial (schema migration) |
| Others | ❌ Not yet |

## Quick Commands

```powershell
# Validate all requirements
.\scripts\validate\validate_repo_checklist.ps1

# Auto-fix failures
.\scripts\validate\auto_remediate.ps1

# Check specific requirement
.\scripts\validate\validate_repo_checklist.ps1 -RequirementFilter "STATE-OBS-001"

# List all requirements
cat .ai-orch\checklists\repo_checklist.json | ConvertFrom-Json | Select-Object -ExpandProperty rules | Format-Table requirement_id, priority, description
```

## Adding New Requirements

1. Edit `.ai-orch/checklists/repo_checklist.json`
2. Add new requirement object:
   ```json
   {
     "requirement_id": "CATEGORY-DESC-NNN",
     "scope": "repo",
     "type": "check_type",
     "priority": "HIGH",
     "description": "What this checks",
     "params": { }
   }
   ```
3. Test: `.\scripts\validate\validate_repo_checklist.ps1 -RequirementFilter "YOUR-ID"`

## References

- **Checklist Spec**: `.ai-orch/checklists/repo_checklist.json`
- **Validator**: `scripts/validate/validate_repo_checklist.ps1`
- **Auto-Fix**: `scripts/validate/auto_remediate.ps1`
- **Documentation**: `docs/operations/REPO_CHECKLIST.md`
- **Quick Start**: `docs/operations/CHECKLIST_QUICK_START.md`
- **Auto-Fix Guide**: `docs/operations/AUTO_REMEDIATION.md`

---

**Version**: 1.0.0
**Generated**: 2025-11-23
