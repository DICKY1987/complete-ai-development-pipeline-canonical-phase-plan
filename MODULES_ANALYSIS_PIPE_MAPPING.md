# modules/ Folder Analysis & PIPE Mapping

## Executive Summary

**modules/ CANNOT BE REMOVED** - It contains 243 active files that are heavily imported across the entire codebase.

However, there are **potential candidates for removal/archival**:
- `engine/` (27 files) - Hybrid GUI/TUI architecture experiment
- `src/` (3 files) - Legacy orchestrator stubs

---

## 1. What's in modules/ and Why It Must Stay

### File Count by Module (Top 10)

| Module | Files | Purpose | PIPE Module |
|--------|-------|---------|-------------|
| **core-engine** | 37 | Orchestrator, scheduler, executor, workers | PIPE-14, 15, 17 |
| **core-state** | 16 | DB, state management, bundles, DAG | PIPE-12, 22 |
| **error-engine** | 14 | Error detection engine, state machine | PIPE-20, 21 |
| **aim-environment** | 11 | Tool installation, health checks, VC | PIPE-17 |
| **specifications-tools** | 9 | Spec indexer, resolver, patcher | PIPE-02, 08 |
| **core-ast** | 8 | AST parsing for Python/JS | PIPE-18 |
| **core-planning** | 8 | Parallelism detection, DAG planning | PIPE-09, 11 |
| **error-shared** | 7 | Shared error utilities | PIPE-19-21 |
| **error-plugin-python-ruff** | 6 | Ruff linter plugin | PIPE-19 |
| **20 other error plugins** | 5 each | Various linters/formatters | PIPE-19 |

### Import Dependencies

**Heavily imported by**:
- `tests/` - 100+ test files
- `engine/` - 27 files (legacy, but still active)
- `tools/` - validation, spec tools
- `scripts/` - 30+ automation scripts

**Cross-module dependencies**:
```python
modules/core-engine → modules/core-state
modules/core-engine → modules/aim-environment
modules/error-engine → modules/error-shared
modules/core-planning → modules/core-state
```

---

## 2. PIPE Module Mapping for modules/

Based on the virtual tree classification:

### Core Domain (PIPE-09 to PIPE-17, 22)

| modules/ Directory | PIPE Module | Rationale |
|-------------------|-------------|-----------|
| `core-planning/` | PIPE-09, 11 | Pattern specialization, DAG building |
| `core-state/` | PIPE-12, 22 | Persist plan in state, commit results |
| `core-engine/` | PIPE-14, 15, 17 | Queue, priority, execution |
| `core-ast/` | PIPE-18 | Post-exec validation (AST checks) |

### Error Domain (PIPE-19 to PIPE-21)

| modules/ Directory | PIPE Module | Rationale |
|-------------------|-------------|-----------|
| `error-engine/` | PIPE-20 | Error classification engine |
| `error-shared/` | PIPE-19-21 | Shared utilities |
| `error-plugin-*` (20 plugins) | PIPE-19 | Error detection plugins |

### AIM Domain (PIPE-07, 17)

| modules/ Directory | PIPE Module | Rationale |
|-------------------|-------------|-----------|
| `aim-registry/` | PIPE-07 | Capabilities & registry |
| `aim-environment/` | PIPE-17 | Tool execution environment |
| `aim-services/` | PIPE-17 | Tool adapter services |
| `aim-cli/` | PIPE-07 | Registry CLI |
| `aim-tests/` | PIPE-18 | Testing |

### Other (PIPE-01, 02)

| modules/ Directory | PIPE Module | Rationale |
|-------------------|-------------|-----------|
| `pm-integrations/` | PIPE-01 | PM intake |
| `specifications-tools/` | PIPE-02 | Spec discovery |

---

## 3. What CAN Be Removed

### 3.1. engine/ (27 files) - **Candidate for Archival**

**Purpose**: Experimental "Hybrid GUI/TUI" architecture
**Status**: Legacy/superseded by `modules/core-engine/`

**Evidence it's superseded**:
```python
# engine/README.md says:
"This directory implements the **hybrid GUI/Terminal/TUI architecture**"
"Phase 1 (Current): engine/ is standalone with minimal dependencies"
"Phase 2: Integrate with core/state/ for persistence"

# But modules/core-engine/ is the actual implementation
modules/core-engine/  # 37 files - ACTIVE
engine/orchestrator/  # Thin wrapper
```

**Imports from engine/**:
- 27 files import from `engine/` (mostly tests)
- Most are in `tests/` and can be updated

**Recommendation**: 
✅ **Archive to `archive/legacy-engine/`**
- Keep for reference
- Update imports to use `modules/core-engine/` instead
- ~27 files to update

---

### 3.2. src/ (3 files) - **Candidate for Removal**

**Purpose**: Legacy orchestrator stubs
**Status**: Minimal, mostly empty

**Contents**:
```
src/
├── orchestrator.py  (30 lines - stub/shim)
├── path_registry.py
└── plugins/
```

**Imports from src/**:
- None found in active code

**Recommendation**:
✅ **Delete entirely** (after verification)
- Only 3 files
- No active imports
- Appears to be leftover from old structure

---

### 3.3. Other Candidates

Check these for redundancy:

| Folder | Files | Status | Recommendation |
|--------|-------|--------|----------------|
| `legacy/` | ? | Explicitly marked legacy | ✅ Archive if not already |
| `MOD_ERROR_PIPELINE/` | ? | Deprecated error module | ✅ Archive (superseded by modules/error-*) |
| `src/pipeline/` | ? | Old pipeline impl | ✅ Archive (superseded by modules/core-*) |

---

## 4. Improved PIPE Mapping Configuration

The current `pipe_mapping_config.yaml` needs refinement for `modules/`:

### Current Issue

```yaml
# Currently modules/core-engine maps to PIPE-14 (queue admission)
# But it also contains PIPE-15 (priority) and PIPE-17 (execution) code
```

### Proposed Fix

Update `pipe_mapping_config.yaml` with more granular rules:

```yaml
rules:
  # Split core-engine by file patterns
  - name: execution_core
    pipe_id: PIPE-17_EXECUTE_TOOL_AND_CAPTURE_OUTPUT
    match:
      file_glob:
        - "modules/core-engine/*orchestrator*.py"
        - "modules/core-engine/*executor*.py"
        - "modules/core-engine/*aim_integration*.py"
  
  - name: scheduling_priority
    pipe_id: PIPE-15_ASSIGN_PRIORITIES_AND_SLOTS
    match:
      file_glob:
        - "modules/core-engine/*scheduler*.py"
        - "modules/core-engine/*priority*.py"
  
  - name: queue_admission
    pipe_id: PIPE-14_ADMIT_READY_TASKS_TO_QUEUE
    match:
      file_glob:
        - "modules/core-engine/*queue*.py"
        - "modules/core-engine/*worker*.py"
  
  # Error plugins - be specific
  - name: error_plugins_detection
    pipe_id: PIPE-19_RUN_ERROR_PLUGINS_PIPELINE
    match:
      path_prefix:
        - "modules/error-plugin-"
        - "modules/error-shared/"
  
  - name: error_engine_classify
    pipe_id: PIPE-20_CLASSIFY_ERRORS_AND_CHOOSE_ACTION
    match:
      file_glob:
        - "modules/error-engine/*error_engine*.py"
        - "modules/error-engine/*classifier*.py"
  
  - name: error_engine_autofix
    pipe_id: PIPE-21_APPLY_AUTOFIX_RETRY_AND_CIRCUIT_CONTROL
    match:
      file_glob:
        - "modules/error-engine/*recovery*.py"
        - "modules/error-engine/*autofix*.py"
        - "modules/error-engine/*circuit*.py"
  
  # State - split by responsibility
  - name: state_planning
    pipe_id: PIPE-12_PERSIST_PLAN_IN_STATE
    match:
      file_glob:
        - "modules/core-state/*db*.py"
        - "modules/core-state/*bundles*.py"
        - "modules/core-state/*dag*.py"
  
  - name: state_results
    pipe_id: PIPE-22_COMMIT_TASK_RESULTS_TO_STATE_AND_MODULES
    match:
      file_glob:
        - "modules/core-state/*crud*.py"
        - "modules/core-state/*audit*.py"
        - "modules/core-state/*metrics*.py"
```

---

## 5. Action Plan

### Immediate Actions (Safe)

1. ✅ **Keep modules/** - It's the active implementation
2. ✅ **Update PIPE mapping** - Refine rules for better classification
3. ✅ **Document module purposes** - Add to each module's README

### Short-Term (Validation Required)

1. ⬜ **Analyze engine/ usage**
   ```bash
   grep -r "from engine\." --include="*.py" | grep -v "test" | wc -l
   ```
2. ⬜ **Verify src/ is unused**
   ```bash
   grep -r "from src\." --include="*.py" | wc -l
   ```
3. ⬜ **Create archival plan** if confirmed unused

### Medium-Term (After Validation)

1. ⬜ **Archive engine/** → `archive/legacy-engine/`
2. ⬜ **Delete src/** (if truly unused)
3. ⬜ **Update imports** in affected files
4. ⬜ **Re-run tests** to ensure nothing breaks

### Long-Term (Optional)

1. ⬜ **Restructure modules/** to match PIPE-XX physically
2. ⬜ **Create per-module manifests**
3. ⬜ **Gradual migration** to pipeline/ structure

---

## 6. Comparison: modules/ vs engine/ vs src/

| Aspect | modules/ | engine/ | src/ |
|--------|----------|---------|------|
| **Files** | 243 | 27 | 3 |
| **Status** | ✅ Active | ⚠️ Legacy experiment | ❌ Stub/empty |
| **Imports** | 100+ references | 27 references | 0 references |
| **Purpose** | Module-centric impl | GUI/TUI experiment | Old orchestrator |
| **Action** | **KEEP** | Archive | Delete |

---

## 7. Summary

### Do NOT Remove
- ✅ **modules/** (243 files, heavily used)

### Safe to Archive/Remove (After Verification)
- ⚠️ **engine/** (27 files) → Archive to `archive/legacy-engine/`
- ✅ **src/** (3 files) → Delete entirely
- ⚠️ **legacy/**, **MOD_ERROR_PIPELINE/**, **src/pipeline/** → Archive if exist

### Update Required
- 📝 **pipe_mapping_config.yaml** - More granular rules for modules/
- 📝 **Import statements** - Update references from engine/ to modules/

---

**Created**: 2025-12-02
**Analysis**: modules/ folder structure vs PIPE-01 to PIPE-26
**Recommendation**: Keep modules/, archive engine/, delete src/
