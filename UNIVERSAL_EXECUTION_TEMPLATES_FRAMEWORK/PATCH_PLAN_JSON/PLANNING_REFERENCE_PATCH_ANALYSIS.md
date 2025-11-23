# Planning & Reference Documentation Patch Analysis

**Generated**: 2025-11-23T11:16:48Z  
**Purpose**: Analyze planning and reference docs for master plan patches  
**Status**: CRITICAL - Complete phase plans and error catalog identified

---

## Executive Summary

**13 files analyzed** - **6 contain CRITICAL implementation details**:

| File | Priority | Content | Impact |
|------|----------|---------|--------|
| **PHASE_UET_INTEGRATION.md** | CRITICAL | Complete 9-10 week phase plan | Full implementation roadmap |
| **PHASE_UET_CHECKLIST.md** | CRITICAL | Detailed checklist with hour estimates | Execution tracking |
| **workstream-style-prompt-structure.md** | HIGH | Universal workstream prompt template | Tool-agnostic execution |
| **DATA_FLOWS.md** | HIGH | Request/response flows | Data transformation understanding |
| **DEPENDENCIES.md** | MEDIUM | Module coupling analysis | Change impact analysis |
| **ERROR_CATALOG.md** | HIGH | 25 common errors + recovery | Error handling procedures |

**Total New Information**: Complete UET integration plan + operational procedures

---

## Critical Findings

### 1. PHASE_UET_INTEGRATION.md - CRITICAL

**Complete 9-10 Week Implementation Plan**:

#### Phase Breakdown
- **Phase A**: Quick Wins (Week 1-2, 26 hours)
  - WS-UET-A1: Schema Foundation (2h)
  - WS-UET-A2: Worker Health Checks (4h)
  - WS-UET-A3: Event Persistence (4h)
  - WS-UET-A4: ULID Migration (8h)
  - WS-UET-A5: Cost Tracking Enhancements (8h)

- **Phase B**: Patch System (Week 3-4, 42 hours)
  - Database migration
  - Patch ledger state machine
  - Patch validator
  - Patch policy engine

- **Phases C-F**: Workers, Gates, Orchestration, Testing (Week 5-10, ~80 hours)

**Current State**: ~40% UET-aligned
- ✅ Worker lifecycle: 80% (has states, needs health checks)
- ✅ Event bus: 85% (has events, needs persistence)  
- ✅ Patch manager: 50% (basic parsing, needs ledger)
- ✅ Cost tracker: 75% (needs per-phase tracking)
- ❌ Adapters: Direct edits (needs patch-first refactor)

**Impact**: This is the ACTUAL implementation plan with hours and workstreams!

---

### 2. PHASE_UET_CHECKLIST.md - CRITICAL

**Detailed Execution Checklist**:

```markdown
| Phase | Workstreams | Status | Duration (Est) | % Complete |
|-------|-------------|--------|----------------|------------|
| Phase A | 5 | ⬜ Not Started | 26h | 0% |
| Phase B | 4 | ⬜ Not Started | 42h | 0% |
| Phase C-F | TBD | ⬜ Not Started | ~80h | 0% |
| TOTAL | 9+ | ⬜ Not Started | ~148h | 0% |
```

**Per-Workstream Checklists**:
- [ ] Files created/modified
- [ ] Commands to run
- [ ] Success criteria
- [ ] Dependencies
- [ ] Actual hours tracking

**Impact**: Ready-to-execute checklist with validation!

---

### 3. workstream-style-prompt-structure.md - HIGH

**Universal Workstream Prompt Template** (works with ALL tools):

```text
[ROLE] Senior software engineer
[WORKSTREAM_META] id, goal, priority
[REPO_CONTEXT] tech_stack, entry_points
[FILE_SCOPE] files_scope, files_may_create
[TASKS] concrete, checkable steps
[CONSTRAINTS] minimal changes, preserve behavior
[TESTS_AND_VALIDATION] required_checks, acceptance_criteria
[EXECUTION_GUIDANCE] plan first, wait for confirmation
[OUTPUT_FORMAT] PLAN → CHANGES → TESTS → NEXT_STEPS
```

**Tool Compatibility**:
- ✅ Aider: Use `--message-file`
- ✅ Ollama Code: Paste as first message
- ✅ Codex CLI: First user message
- ✅ Claude Code CLI: Initial prompt

**Impact**: Standardized prompt structure for all AI tools!

---

### 4. DATA_FLOWS.md - HIGH

**Data Transformation Pipeline**:

```
User Input (JSON Bundle)
  ↓ [Validator] → Validated Workstream Object
  ↓ [Orchestrator] → Execution Plan
  ↓ [Database] ← Store Initial State (S_PENDING)
  ↓ [Step Executor] → For Each Step:
      ├─ Load Step Context
      ├─ [Tool Adapter] → Execute Tool
      ├─ [Database] ← Store Step Result
      └─ State Transition (S_SUCCESS/S_FAILED)
  ↓ [Database] ← Final Workstream State
  ↓ User Output (Execution Result)
```

**State Flow Through Database**:
- T0: Workstream Created (S_PENDING)
- T1: Step 1 Running (S_RUNNING)
- T2: Step 1 Complete (S_SUCCESS)
- T3: Final State (S_SUCCESS/S_FAILED)

**Impact**: Critical for understanding data lifecycle!

---

### 5. DEPENDENCIES.md - MEDIUM

**4-Layer Architecture**:

```
Layer 4: User Interface (scripts)
  ↓ depends on
Layer 3: Orchestration (core.engine, error.engine)
  ↓ depends on
Layer 2: Domain Logic (core.state, error.plugins)
  ↓ depends on
Layer 1: Infrastructure (core.state.db, file_cache)
  ↓ depends on
Layer 0: Standard Library (sqlite3, subprocess)
```

**Rules**:
- ✅ Layer N can depend on Layer N-1 or below
- ❌ No upward dependencies
- ❌ No circular dependencies

**Impact**: Enforces clean architecture!

---

### 6. ERROR_CATALOG.md - HIGH

**25 Common Errors with Recovery**:

#### Categories
1. **Database Errors** (6): Locked, schema mismatch, constraint violation
2. **Workstream Errors** (5): Dependency cycles, timeouts, conflicts
3. **Plugin Errors** (4): Manifest issues, execution failures
4. **Spec Errors** (3): Not found, circular refs
5. **Tool Errors** (4): Circuit breaker, timeout, not found
6. **Config Errors** (3): Missing files, invalid syntax

**Example**:
```
ERR-DB-01: Database Locked
Root Cause: Another process has exclusive write lock
Recovery:
  1. Check for other processes: ps aux | grep python
  2. Kill stale processes: kill <pid>
  3. Restore backup: cp pipeline_state.db.backup
  4. Set busy timeout: PRAGMA busy_timeout = 5000
Prevention: Keep transactions <100ms, use WAL mode
```

**Impact**: Critical error handling procedures!

---

## Required Patches

### Patch 004: Complete Phase Plan

```json
[
  {
    "op": "add",
    "path": "/meta/complete_phase_plan",
    "value": {
      "spec_ref": "docs/planning/PHASE_UET_INTEGRATION.md",
      "total_duration_hours": 148,
      "total_duration_weeks": 10,
      "mvp_milestone_weeks": 4,
      "current_alignment_percentage": 40,
      "phases": {
        "Phase_A": {
          "name": "Quick Wins",
          "weeks": "1-2",
          "duration_hours": 26,
          "workstreams": 5,
          "priority": "CRITICAL"
        },
        "Phase_B": {
          "name": "Patch System",
          "weeks": "3-4",
          "duration_hours": 42,
          "workstreams": 4,
          "priority": "CRITICAL"
        },
        "Phase_C_F": {
          "name": "Workers, Gates, Orchestration, Testing",
          "weeks": "5-10",
          "duration_hours": 80,
          "workstreams": "TBD",
          "priority": "HIGH"
        }
      }
    }
  },
  {
    "op": "add",
    "path": "/phases/PH-002/workstreams/WS-002-001",
    "value": {
      "workstream_id": "WS-UET-A1",
      "name": "Schema Foundation",
      "priority": "CRITICAL",
      "estimated_duration_hours": 2,
      "risk": "LOW",
      "tasks": {
        "TSK-002-001-001": {
          "name": "Copy UET Schemas",
          "command": "Copy-Item UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\\schema\\*.json schema\\uet\\",
          "validation": "Test-Path schema/uet/*.json (17 files expected)"
        }
      }
    }
  }
]
```

### Patch 005: Workstream Prompt Template

```json
[
  {
    "op": "add",
    "path": "/meta/workstream_prompt_template",
    "value": {
      "spec_ref": "docs/reference/workstream-style-prompt-structure.md",
      "structure": {
        "role": "Senior software engineer in existing codebase",
        "sections": ["WORKSTREAM_META", "REPO_CONTEXT", "FILE_SCOPE", "TASKS", "CONSTRAINTS", "TESTS_AND_VALIDATION", "EXECUTION_GUIDANCE", "OUTPUT_FORMAT"],
        "output_format": ["PLAN", "CHANGES", "TESTS", "NEXT_STEPS"]
      },
      "tool_compatibility": {
        "aider": "--message-file",
        "ollama_code": "First message",
        "codex_cli": "First user message",
        "claude_code": "Initial prompt"
      }
    }
  }
]
```

### Patch 006: Data Flows & Dependencies

```json
[
  {
    "op": "add",
    "path": "/meta/data_flows",
    "value": {
      "spec_ref": "docs/reference/DATA_FLOWS.md",
      "workstream_execution_flow": [
        "User Input (JSON Bundle)",
        "Validator → Validated Workstream Object",
        "Orchestrator → Execution Plan",
        "Database ← Store Initial State",
        "Step Executor → Execute Steps",
        "Database ← Store Results",
        "User Output"
      ],
      "state_transitions": {
        "S_PENDING": "Initial state",
        "S_RUNNING": "Execution in progress",
        "S_SUCCESS": "Completed successfully",
        "S_FAILED": "Failed with errors"
      }
    }
  },
  {
    "op": "add",
    "path": "/meta/layer_architecture",
    "value": {
      "spec_ref": "docs/reference/DEPENDENCIES.md",
      "layers": {
        "layer_4": {"name": "User Interface", "modules": ["scripts"]},
        "layer_3": {"name": "Orchestration", "modules": ["core.engine", "error.engine"]},
        "layer_2": {"name": "Domain Logic", "modules": ["core.state", "error.plugins"]},
        "layer_1": {"name": "Infrastructure", "modules": ["core.state.db", "file_cache"]},
        "layer_0": {"name": "Standard Library", "modules": ["stdlib"]}
      },
      "rules": [
        "Layer N can depend on Layer N-1 or below",
        "No upward dependencies allowed",
        "No circular dependencies"
      ]
    }
  }
]
```

### Patch 007: Error Catalog

```json
[
  {
    "op": "add",
    "path": "/meta/error_catalog",
    "value": {
      "spec_ref": "docs/reference/ERROR_CATALOG.md",
      "total_errors": 25,
      "categories": {
        "database": 6,
        "workstream": 5,
        "plugin": 4,
        "specification": 3,
        "tool_adapter": 4,
        "configuration": 3
      },
      "critical_errors": [
        {
          "id": "ERR-DB-01",
          "name": "Database Locked",
          "symptoms": "sqlite3.OperationalError: database is locked",
          "root_cause": "Another process has exclusive write lock",
          "recovery": [
            "Check for other processes: ps aux | grep python",
            "Kill stale processes if safe",
            "Restore backup if corrupted",
            "Set busy timeout: PRAGMA busy_timeout = 5000"
          ],
          "prevention": "Keep transactions <100ms, use WAL mode"
        }
      ]
    }
  },
  {
    "op": "add",
    "path": "/validation/error_handling",
    "value": {
      "catalog_ref": "docs/reference/ERROR_CATALOG.md",
      "recovery_procedures_documented": true,
      "prevention_strategies_defined": true,
      "total_documented_errors": 25
    }
  }
]
```

---

## Summary

### Must Patch Immediately (Priority 1)

1. **Complete Phase Plan** (Patch 004)
   - Full 148-hour plan with 5 phases
   - Per-workstream hour estimates
   - 40% current completion noted

2. **Workstream Prompt Template** (Patch 005)
   - Universal prompt structure
   - Tool compatibility matrix
   - Output format standardization

3. **Data Flows & Architecture** (Patch 006)
   - Request/response flows
   - 4-layer architecture
   - Dependency rules

4. **Error Catalog** (Patch 007)
   - 25 documented errors
   - Recovery procedures
   - Prevention strategies

---

## Impact on Master Plan

### New Metadata Sections
- `complete_phase_plan` - Full 10-week roadmap
- `workstream_prompt_template` - Universal AI tool prompt
- `data_flows` - Data transformation pipeline
- `layer_architecture` - 4-layer dependency model
- `error_catalog` - 25 errors + recovery

### Expanded Phases

**Phase 2 (Patch System)** needs breakdown into:
- WS-UET-B1: Database Migration (12h)
- WS-UET-B2: Patch Ledger (16h)
- WS-UET-B3: Patch Validator (8h)
- WS-UET-B4: Patch Policy Engine (6h)

**Phases 3-6** need similar detailed breakdown from planning docs

### New Validation
- Error recovery procedure validation
- Layer dependency compliance
- Data flow integrity checks

---

**These documents contain the EXECUTION ROADMAP!**

All detailed task breakdowns and hour estimates are here.
