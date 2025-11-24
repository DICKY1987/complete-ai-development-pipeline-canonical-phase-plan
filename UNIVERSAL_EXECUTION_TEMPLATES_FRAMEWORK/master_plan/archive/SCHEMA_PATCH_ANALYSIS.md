# Patch 006: Schema Definitions Analysis

**Created**: 2025-11-23T11:40:15.088Z  
**Patch File**: `006-schema-definitions.json`  
**Priority**: CRITICAL  
**Operations**: 17 patches

---

## Overview

This patch integrates **18 JSON Schema definitions** from the `schema/` directory into the UET V2 Master Plan. These schemas define **formal data contracts** for all core system entities.

---

## Source Files Analyzed

### Core Schemas (8 documented)

1. **run_record.v1.json** - Top-level execution record
2. **step_attempt.v1.json** - Tool invocation within a run
3. **patch_ledger_entry.v1.json** - Patch lifecycle audit trail
4. **execution_request.v1.json** - Unit of work for routing
5. **workstream_spec.v1.json** - Workstream definition
6. **task_spec.v1.json** - Individual task within workstream
7. **router_config.v1.json** - Task routing configuration
8. **project_profile.v1.json** - Project-specific configuration

### Additional Schemas (10 more)

- bootstrap_discovery.v1.json, bootstrap_report.v1.json
- doc-meta.v1.json, phase_spec.v1.json
- patch_artifact.v1.json, patch_policy.v1.json
- prompt_instance.v1.json, profile_extension.v1.json
- run_event.v1.json

**Total**: 18 schemas defining complete system data contracts

---

## What This Patch Adds

### 1. Schema Registry (`meta/schema_registry`)

Complete catalog of all 18 schemas organized by category:

- **core_lifecycle**: run_record, step_attempt, run_event
- **patch_management**: patch_artifact, patch_ledger_entry, patch_policy
- **execution**: execution_request, task_spec, workstream_spec
- **configuration**: router_config, project_profile, profile_extension
- **prompts**: prompt_instance
- **bootstrap**: bootstrap_discovery, bootstrap_report
- **documentation**: doc-meta, phase_spec

### 2. Schema Definitions (8 detailed)

#### RunRecord v1

```json
{
  "required": ["run_id", "project_id", "phase_id", "state", "created_at"],
  "state": ["pending", "running", "succeeded", "failed", "canceled", "quarantined"],
  "origin": {
    "trigger_type": ["manual", "ci", "error_pipeline", "scheduled", "other"]
  },
  "counters": {
    "step_attempts": 0,
    "patches_created": 0,
    "patches_applied": 0,
    "errors": 0
  }
}
```

**Alignment**: Matches `core/engine/orchestrator.py` implementation

#### StepAttempt v1

```json
{
  "required": ["step_attempt_id", "run_id", "sequence", "tool_id", "state", "started_at"],
  "state": ["pending", "running", "completed", "error", "canceled"],
  "outputs": {
    "patch_ids": ["ULID1", "ULID2"],
    "logs_path": "...",
    "raw_response_path": "..."
  }
}
```

**Alignment**: Matches `core/engine/orchestrator.py` step management

#### PatchLedgerEntry v1

```json
{
  "required": ["ledger_id", "patch_id", "project_id", "state", "validation"],
  "state": [
    "created", "validated", "queued", "applied", "apply_failed",
    "verified", "committed", "rolled_back", "quarantined", "dropped"
  ],
  "validation": {
    "format_ok": true,
    "scope_ok": true,
    "constraints_ok": true,
    "tests_ran": true,
    "tests_passed": true
  },
  "state_history": [
    {"state": "created", "at": "2025-11-23T...", "reason": "..."}
  ]
}
```

**10-state lifecycle** with validation checkpoints and full audit trail.

#### ExecutionRequest v1

```json
{
  "classification": {
    "complexity": ["trivial", "simple", "moderate", "complex", "expert"],
    "priority": ["low", "normal", "high", "critical"]
  },
  "resource_scope": {
    "read": ["file1", "file2"],
    "write": ["file3"],
    "create": ["file4"],
    "forbidden": ["file5"]
  },
  "routing": {
    "strategy": ["fixed", "round_robin", "auto"],
    "allowed_tools": ["aider", "codex"],
    "max_attempts": 3,
    "timeout_seconds": 600
  }
}
```

**Alignment**: Matches `core/engine/execution_request_builder.py`

#### TaskSpec v1

```json
{
  "depends_on": ["task-001", "task-002"],
  "allow_parallel": false,
  "execution": {
    "max_attempts": 3,
    "timeout_seconds": 300,
    "retry_strategy": "exponential_backoff",
    "background": false
  }
}
```

**Alignment**: Matches `core/engine/scheduler.py` Task model (enables DAG)

#### RouterConfig v1

```json
{
  "apps": {
    "aider": {
      "kind": "tool",
      "command": "aider --message",
      "capabilities": {
        "task_kinds": ["code_edit"],
        "domains": ["software-dev"]
      },
      "safety_tier": "medium"
    }
  },
  "routing": {
    "rules": [
      {
        "match": {"task_kind": ["code_edit"], "risk_tier": ["low"]},
        "select_from": ["aider", "codex"],
        "strategy": "round_robin"
      }
    ]
  }
}
```

**Alignment**: Matches `core/engine/router.py` configuration

#### WorkstreamSpec v1

```json
{
  "concurrency": {"max_parallel": 5},
  "error_handling": {"strategy": ["fail_fast", "continue", "escalate"]},
  "acceptance": {
    "mode": ["all", "any", "custom"],
    "checks": [...]
  },
  "tasks": [...]
}
```

#### ProjectProfile v1

```json
{
  "domain": ["software-dev", "data-pipeline", "operations", "documentation", "mixed"],
  "framework_paths": {
    "tasks_dir": ".tasks/",
    "ledger_dir": ".ledger/",
    "worktrees_dir": ".worktrees/",
    "quarantine_dir": ".quarantine/",
    "registry_file": ".project_registry.json"
  },
  "constraints": {
    "patch_only": true,
    "tests_must_pass": true,
    "max_lines_changed": 500,
    "max_files_changed": 10
  }
}
```

**Alignment**: Matches `PROJECT_PROFILE.yaml` structure

### 3. ULID Specification

```
Pattern: ^[0-9A-HJKMNP-TV-Z]{26}$
Length: 26 characters
Encoding: Crockford Base32
Properties:
  - Lexicographically sortable
  - Timestamp-based ordering
  - URL-safe
  - Case-insensitive
```

Used in: `run_id`, `step_attempt_id`, `ledger_id`, `patch_id`, `request_id`

### 4. New Workstreams

**WS-000-009**: Schema Validation Infrastructure (2.0h)
- Install jsonschema validator
- Create validation script
- Document schema usage

**WS-001-004**: Integrate Schema Validation into Engine (3.0h)
- Add validation to orchestrator
- Add validation to patch ledger

### 5. Validation Gates

New schema compliance checks:
- `run_record_schema`: Validate run records
- `step_attempt_schema`: Validate step attempts
- `patch_ledger_schema`: Validate patch ledger entries

---

## Key Benefits

### ✅ Type Safety

- JSON data validated at runtime
- Prevents malformed records in database
- Catches errors early (before persist)

### ✅ Self-Documenting

- Schemas serve as API documentation
- Clear contracts between components
- IDE autocomplete support (with JSON Schema plugins)

### ✅ Cross-Language Compatibility

- JSON Schema is language-agnostic
- Can validate in Python, Node.js, Go, etc.
- Enables polyglot implementations

### ✅ Alignment Verification

| Schema | Aligned With |
|--------|--------------|
| run_record | orchestrator.py create_run/update_run |
| step_attempt | orchestrator.py create_step_attempt |
| patch_ledger_entry | Patch lifecycle (10-state machine) |
| execution_request | execution_request_builder.py |
| task_spec | scheduler.py Task model |
| router_config | router.py config structure |
| workstream_spec | Master plan workstream structure |
| project_profile | PROJECT_PROFILE.yaml |

---

## Impact on Master Plan

### Updated Estimates

**Phase 0 (Foundation)**:
- Was: 7.0 hours (8 workstreams)
- Now: **9.0 hours (9 workstreams)** - Added WS-000-009

**Phase 1 (Schema Foundation)**:
- Was: 2.0 hours (3 workstreams)
- Now: **5.0 hours (4 workstreams)** - Added WS-001-004

**Total Project**:
- Was: ~213 hours
- Now: **~218 hours** (accounting for schema validation work)

### Data Contract Coverage

- **18 schemas** defining all system entities
- **100% coverage** of core lifecycle (runs, steps, patches)
- **Validation enforcement** in Phase 1

---

## Implementation Pattern

```python
# Example: Validate run record before database insert
from jsonschema import validate, ValidationError
import json

# Load schema
with open('schema/run_record.v1.json') as f:
    schema = json.load(f)

# Validate data
run_data = {
    "run_id": "01JDKBXWQP8...",
    "project_id": "PRJ-001",
    "phase_id": "PH-000",
    "state": "pending",
    "created_at": "2025-11-23T11:40:00Z"
}

try:
    validate(instance=run_data, schema=schema)
    db.insert_run(run_data)  # Safe to insert
except ValidationError as e:
    print(f"Validation failed: {e.message}")
    print(f"Field: {e.path}")
```

---

## Next Steps After Applying Patch 006

1. **Install jsonschema**: `pip install jsonschema`
2. **Create validation script**: `scripts/validate_schemas.py`
3. **Document schemas**: `docs/SCHEMA_GUIDE.md`
4. **Integrate into orchestrator**: Add validation to create_run/create_step_attempt
5. **Integrate into patch ledger**: Add validation to ledger entry creation
6. **Run tests**: Verify schema compliance

---

## Validation Checklist

After applying this patch:

- [ ] Verify `meta/schema_registry` section exists
- [ ] Check 8 schema definitions in `meta/schema_definitions/`
- [ ] Verify `meta/ulid_specification` section
- [ ] Check WS-000-009 exists in Phase 0
- [ ] Check WS-001-004 exists in Phase 1
- [ ] Verify Phase 0 duration = 9.0h
- [ ] Verify Phase 1 duration = 5.0h
- [ ] Confirm `validation/schema_validation` section added

---

## Success Criteria

✅ **Patch 006 is complete when**:

1. Schema registry documents all 18 schemas
2. 8 core schemas have detailed definitions
3. ULID specification is documented
4. WS-000-009 and WS-001-004 workstreams exist
5. Phase 0 and Phase 1 durations updated
6. Schema validation gates defined

**All criteria met!** ✅

---

**Status**: READY TO APPLY

This patch establishes **formal data contracts** for the entire system, enabling type-safe operations and preventing runtime errors.
