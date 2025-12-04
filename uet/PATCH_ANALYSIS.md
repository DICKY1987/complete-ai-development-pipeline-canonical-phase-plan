---
doc_id: DOC-GUIDE-PATCH-ANALYSIS-754
---

# Patch Analysis - Configuration Files Impact on UET V2 Master Plan

**Generated**: 2025-11-23T11:01:12.785Z
**Purpose**: Analyze configuration files for required patches to `copiolt plan_uv2.json`
**Status**: CRITICAL - Multiple high-priority patches identified

---

## Executive Summary

**5 configuration files** contain **critical information** that MUST be patched into the master plan:

| File | Priority | Impact | Patches Needed |
|------|----------|--------|----------------|
| **CODEBASE_INDEX.yaml** | CRITICAL | Module structure, dependencies, 3 engines | 15+ patches |
| **ai_policies.yaml** | CRITICAL | Edit zones, invariants, validation | 10+ patches |
| **QUALITY_GATE.yaml** | HIGH | 30+ quality gates, CI enforcement | 8+ patches |
| **PROJECT_PROFILE.yaml** | MEDIUM | Project metadata, constraints | 5 patches |
| **PRO_Phase Specification.md** | CRITICAL | Phase structure requirements | 12+ patches |

**Total Patches Required**: 50+ operations

---

## 1. CODEBASE_INDEX.yaml - CRITICAL

### What It Reveals

**Architecture**: 4-layer modular architecture
```yaml
layers:
  - infra: "Database, state, schemas, config"
  - domain: "Core business logic and orchestration"
  - api: "External tool integrations"
  - ui: "CLI, GUI, user-facing tools"
```

**Modules**: 12+ modules with explicit dependencies
- `core.state` (no dependencies)
- `core.engine` (depends on: core.state, config)
- `engine` (separate job execution engine!)
- `error.engine` (domain layer)

### Critical Finding: THREE Execution Engines

```yaml
modules:
  - id: "core.engine"
    path: "core/engine/"
    model: "Workstream → EDIT → STATIC → RUNTIME"

  - id: "engine"  # SEPARATE!
    path: "engine/"
    model: "Job JSON → Adapter → Subprocess"
    notes: "Separate from core/engine/ - uses job JSON pattern"

  - id: "uet_framework"  # IMPLICIT
    path: "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/"
    model: "Bootstrap → Profile → Task Routing"
```

### Required Patches

```json
[
  {
    "op": "add",
    "path": "/meta/architecture",
    "value": {
      "layers": ["infra", "domain", "api", "ui"],
      "layer_enforcement": true,
      "dependency_graph_location": "CODEBASE_INDEX.yaml",
      "layered_architecture_doc": "docs/ARCHITECTURE.md"
    }
  },
  {
    "op": "add",
    "path": "/meta/modules",
    "value": {
      "total_modules": 12,
      "module_index": "CODEBASE_INDEX.yaml",
      "dependency_validation": "required",
      "circular_dependency_check": true
    }
  },
  {
    "op": "add",
    "path": "/meta/three_engine_problem",
    "value": {
      "core_engine": {
        "location": "core/engine/",
        "model": "Workstream-based orchestration",
        "state": "SQLite pipeline_state.db",
        "priority": "primary"
      },
      "job_engine": {
        "location": "engine/",
        "model": "Job JSON pattern",
        "state": "JobStateStore protocol",
        "priority": "secondary"
      },
      "uet_framework": {
        "location": "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/",
        "model": "Bootstrap + Profile + Task Router",
        "state": "Minimal (portable)",
        "priority": "reference"
      },
      "unification_needed": true
    }
  },
  {
    "op": "add",
    "path": "/phases/PH-007",
    "value": {
      "phase_id": "PH-007",
      "phase_ulid": "01JDK6XWQP8PH007UNIFY00001",
      "name": "Engine Unification",
      "description": "Unify three execution engines into coherent architecture",
      "priority": "CRITICAL",
      "status": "ready",
      "estimated_duration_hours": 24,
      "dependencies": ["PH-002", "PH-003"],
      "workstreams": {
        "WS-007-001": {
          "workstream_id": "WS-007-001",
          "name": "State Layer Unification",
          "estimated_duration_hours": 8,
          "tasks": {
            "TSK-007-001-001": {
              "name": "Create unified state adapter",
              "description": "Bridge core.state.db ↔ JobStateStore ↔ UET state"
            }
          }
        },
        "WS-007-002": {
          "workstream_id": "WS-007-002",
          "name": "Execution Model Reconciliation",
          "estimated_duration_hours": 12,
          "tasks": {
            "TSK-007-002-001": {
              "name": "Define canonical execution flow",
              "description": "Reconcile workstream vs job vs UET task models"
            }
          }
        }
      }
    }
  }
]
```

---

## 2. ai_policies.yaml - CRITICAL

### What It Reveals

**Edit Zones**: Machine-readable permissions for AI agents
```yaml
zones:
  safe_to_modify:
    - "core/**/*.py"
    - "tests/**/*.py"
    conditions:
      - "All tests must pass after changes"

  review_required:
    - "schema/**"
    - "config/**"
    - "CODEBASE_INDEX.yaml"

  read_only:
    - "legacy/**"
    - "src/pipeline/**"  # DEPRECATED
    - "MOD_ERROR_PIPELINE/**"  # DEPRECATED
```

**Invariants**: CI-enforced rules
```yaml
invariants:
  - id: "INV-SECTION-IMPORTS"
    enforcement: "ci"
    forbidden:
      - "from src.pipeline.db import init_db"  # ❌
    correct:
      - "from core.state.db import init_db"  # ✅
```

### Required Patches

```json
[
  {
    "op": "add",
    "path": "/meta/ai_policies",
    "value": {
      "policy_file": "ai_policies.yaml",
      "zones": {
        "safe_to_modify": ["core/**", "engine/**", "error/**", "tests/**", "scripts/**"],
        "review_required": ["schema/**", "config/**", "docs/canonical/**"],
        "read_only": ["legacy/**", "src/pipeline/**", "MOD_ERROR_PIPELINE/**"]
      },
      "validation_on_patch": true
    }
  },
  {
    "op": "add",
    "path": "/validation/ai_policy_compliance",
    "value": {
      "check_edit_zones": true,
      "check_invariants": true,
      "forbidden_imports": [
        "from src.pipeline.*",
        "from MOD_ERROR_PIPELINE.*",
        "from legacy.*"
      ],
      "validation_script": "scripts/check_deprecated_paths.py"
    }
  },
  {
    "op": "add",
    "path": "/phases/PH-000/constraints",
    "value": {
      "edit_zones": "safe_to_modify",
      "must_pass_tests": true,
      "no_deprecated_imports": true,
      "policy_ref": "ai_policies.yaml"
    }
  }
]
```

### Impact on All Tasks

**Every task must now include**:
```json
{
  "constraints": {
    "edit_zone": "safe_to_modify",
    "forbidden_imports": ["src.pipeline.*", "MOD_ERROR_PIPELINE.*"],
    "must_pass_tests": true
  }
}
```

---

## 3. QUALITY_GATE.yaml - HIGH PRIORITY

### What It Reveals

**30+ Quality Gates** grouped by category:
- Testing (4 gates)
- CI Enforcement (2 gates) - **BLOCKING**
- Linting (2 gates)
- Error Detection (2 gates)
- Spec Validation (2 gates)
- Engine Validation (3 gates)
- Database (2 gates)
- Documentation (2 gates)

**CI-Enforced Gates** (BLOCKING):
```yaml
- id: "ci.path_standards"
  required: true
  failure_action: "block"
  command: "python scripts/paths_index_cli.py gate --db refactor_paths.db --regex 'src/pipeline|MOD_ERROR_PIPELINE'"
```

### Required Patches

```json
[
  {
    "op": "add",
    "path": "/validation/quality_gates",
    "value": {
      "gate_file": "QUALITY_GATE.yaml",
      "total_gates": 30,
      "required_gates": [
        "test.pytest",
        "test.workstream_validation",
        "ci.path_standards",
        "error.import_validation"
      ],
      "blocking_gates": [
        "test.pytest",
        "ci.path_standards",
        "error.import_validation"
      ]
    }
  },
  {
    "op": "add",
    "path": "/validation/execution_order",
    "value": {
      "pre_commit_checks": {
        "gates": ["test.pytest", "test.workstream_validation", "ci.path_standards"],
        "parallel": true,
        "required": true
      },
      "full_validation": {
        "gates": ["lint.markdown", "error.engine_run", "spec.index_generation"],
        "parallel": true,
        "required": false
      }
    }
  },
  {
    "op": "add",
    "path": "/meta/ci_enforcement",
    "value": {
      "path_standards_enforced": true,
      "import_validation_enforced": true,
      "test_coverage_required": true,
      "workstream_schema_validation": true
    }
  }
]
```

### Impact on Tasks

**Every task completion requires**:
```json
{
  "postconditions": [
    "test.pytest passes",
    "ci.path_standards passes",
    "error.import_validation passes"
  ],
  "validation_commands": [
    "python -m pytest -q tests",
    "python scripts/paths_index_cli.py gate --db refactor_paths.db",
    "python scripts/validate_error_imports.py"
  ]
}
```

---

## 4. PROJECT_PROFILE.yaml - MEDIUM PRIORITY

### What It Reveals

**Project Configuration**:
```yaml
project_id: "PRJ-COMPLETE_AI_DEVELOPMENT_PIPELINE_–_CANONICAL_PHASE_PLAN"
project_name: "Complete AI Development Pipeline – Canonical Phase Plan"
profile_id: "generic"
domain: "mixed"

constraints:
  max_lines_changed: 500
  patch_only: true

framework_paths:
  worktrees_dir: ".worktrees/"
  ledger_dir: ".ledger/"
  tasks_dir: ".tasks/"
  quarantine_dir: ".quarantine/"
```

### Required Patches

```json
[
  {
    "op": "add",
    "path": "/meta/project",
    "value": {
      "project_id": "PRJ-COMPLETE_AI_DEVELOPMENT_PIPELINE_–_CANONICAL_PHASE_PLAN",
      "project_name": "Complete AI Development Pipeline – Canonical Phase Plan",
      "profile_id": "generic",
      "domain": "mixed",
      "profile_file": "PROJECT_PROFILE.yaml"
    }
  },
  {
    "op": "add",
    "path": "/meta/constraints",
    "value": {
      "max_lines_changed_per_patch": 500,
      "patch_only_mode": true,
      "no_direct_file_edits": true
    }
  },
  {
    "op": "add",
    "path": "/meta/framework_paths",
    "value": {
      "worktrees_dir": ".worktrees/",
      "ledger_dir": ".ledger/",
      "tasks_dir": ".tasks/",
      "quarantine_dir": ".quarantine/",
      "state_dir": ".state/"
    }
  }
]
```

---

## 5. PRO_Phase Specification.md - CRITICAL

### What It Reveals

**Mandatory Phase Structure**:
```markdown
Every Phase MUST contain:
1. Phase ID (human: "Phase 1A") + Workstream ID (machine: "ws-pipeline-plus-1a-task-queue")
2. Objective (single, tight goal)
3. File Scope (create, modify, read_only)
4. Programmatic Acceptance Tests (PowerShell + pytest)
5. Dependencies (must_follow, may_run_parallel_with)
6. Pre-Flight checks (verify prerequisites)
```

**Phase Naming Pattern**:
```
Phase ID: "Phase 0", "Phase 1A", "Phase 1B", "Phase 2"
Workstream ID: "ws-{project}-{phase}-{slug}"
Example: "ws-pipeline-plus-1a-task-queue"
```

**File Scope Enforcement**:
```yaml
file_scope:
  create: ["core/state/task_queue.py"]
  modify: ["core/state/__init__.py"]
  read_only: ["config/router.config.yaml"]
```

**Acceptance Tests**:
```yaml
acceptance_tests:
  powershell_block: |
    Test-Path .tasks
    Test-Path .ledger/patches
  python_block: |
    pytest -q tests/test_task_queue.py
```

### Required Patches

```json
[
  {
    "op": "add",
    "path": "/meta/phase_specification",
    "value": {
      "spec_file": "PRO_Phase Specification mandatory structure.md",
      "version": "1.0.0",
      "enforcement": "mandatory",
      "all_phases_must_comply": true
    }
  },
  {
    "op": "add",
    "path": "/meta/phase_requirements",
    "value": {
      "required_fields": [
        "phase_id",
        "workstream_id",
        "objective",
        "file_scope",
        "acceptance_tests",
        "dependencies",
        "pre_flight_checks"
      ],
      "workstream_id_pattern": "ws-{project}-{phase}-{slug}",
      "acceptance_test_types": ["powershell", "pytest"]
    }
  },
  {
    "op": "replace",
    "path": "/phases/PH-000/workstreams/WS-000-001",
    "value": {
      "workstream_id": "ws-pipeline-plus-00-state-infra",
      "phase_id": "Phase 0",
      "objective": "Create state observability infrastructure with validation",
      "file_scope": {
        "create": [
          ".state/current.json",
          ".state/transitions.jsonl",
          "scripts/validate/validate_state.ps1"
        ],
        "modify": [],
        "read_only": []
      },
      "acceptance_tests": {
        "powershell": "Test-Path .state; Test-Path .state/current.json",
        "pytest": "pytest -q tests/state/test_infrastructure.py"
      },
      "pre_flight_checks": {
        "python_version": ">=3.8",
        "powershell_version": ">=7.0"
      }
    }
  }
]
```

### Impact on ALL Phases

**Every phase must be restructured** to include:
1. ✅ Workstream ID following pattern
2. ✅ File scope (create/modify/read_only)
3. ✅ Acceptance tests (PowerShell + pytest)
4. ✅ Pre-flight checks
5. ✅ Dependencies (must_follow/may_run_parallel_with)

---

## Summary: Critical Patches Required

### Priority 1: IMMEDIATE (Before Any Execution)

1. **Add Three-Engine Problem** (from CODEBASE_INDEX.yaml)
   - Add Phase 7: Engine Unification
   - Document architectural complexity
   - ~24 hours additional work

2. **Add AI Policy Compliance** (from ai_policies.yaml)
   - Edit zone validation
   - Import path enforcement
   - Blocking CI gates

3. **Add Quality Gate Enforcement** (from QUALITY_GATE.yaml)
   - 30+ gates defined
   - CI enforcement on path standards
   - Test coverage requirements

4. **Restructure ALL Phases** (from PRO_Phase Specification.md)
   - Add file_scope to every phase
   - Add acceptance_tests to every phase
   - Add pre_flight_checks to every phase
   - Update workstream IDs to pattern

### Priority 2: HIGH (First Week)

5. **Add Project Metadata** (from PROJECT_PROFILE.yaml)
   - Project constraints
   - Framework paths
   - Patch-only enforcement

6. **Add Architecture Metadata** (from CODEBASE_INDEX.yaml)
   - 4-layer architecture
   - Module dependencies
   - Circular dependency prevention

### Timeline Impact

**Original Estimate**: 280 hours (7 weeks)
**With Existing Components**: 168 hours (40% already done)
**With Engine Unification**: 192 hours (7.5 weeks)
**With Compliance Overhead**: 200 hours (8 weeks realistic)

---

## Next Steps

1. **Generate Complete Patch File**: `patches/001-config-integration.json`
   - All 50+ operations
   - RFC 6902 compliant
   - Validation rules included

2. **Apply Patches to Master Plan**
   - Merge with `copiolt plan_uv2.json`
   - Create `UET_V2_MASTER_PLAN.json`

3. **Validate Result**
   - Check all ULID identifiers unique
   - Verify dependency graph acyclic
   - Validate against PRO_Phase Specification

**Ready to generate the complete patch file?**
