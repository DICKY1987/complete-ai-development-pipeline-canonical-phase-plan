# MASTER_SPLINTER Process Documentation

## Overview

This directory contains comprehensive process documentation for the MASTER_SPLINTER orchestration system, providing schema-based validation and execution tracking for multi-agent phase plan workflows.

## Files Created

### 1. `MASTER_SPLINTER_PROCESS_STEPS_SCHEMA.yaml`
**Comprehensive process schema documentation** for MASTER_SPLINTER orchestration.

**Purpose:**
- Documents all 26 orchestration steps across 8 phases
- Defines state machine: INIT → DISCOVERY → CONVERSION → DAG_RESOLUTION → EXECUTION → CONSOLIDATION → SYNC → DONE
- Catalogs 5 core components and their responsibilities
- Specifies 12 operation kinds (orchestration, multi_agent_execution, github_sync, etc.)
- Maps artifact registry (phase plans, workstreams, consolidated DB, reports)
- Defines 4 guardrail checkpoints and anti-patterns

**Key Sections:**
- **Meta**: State machine, phases, transitions, NO STOP MODE enforcement
- **Operation Kinds**: Taxonomy of orchestration operations
- **Components**: run_master_splinter, phase_plan_to_workstream, multi_agent_workstream_coordinator, sync_workstreams_to_github
- **Artifact Registry**: Phase plans, workstreams, database, reports, logs
- **Phases**: 8 phases with detailed step-by-step execution
- **Guardrail Checkpoints**: Prerequisites, DAG validation, circuit breakers, fix loops
- **Anti-Patterns**: Stop-on-error, circular dependencies, missing workstreams, scope violations

**Stats:**
- 8 Phases
- 26 Steps
- 5 Components
- 12 Operation Kinds
- 4 Guardrail Checkpoints
- 6 Artifact Types

### 2. `validate_master_splinter_schema.py`
**Python validator** for MASTER_SPLINTER_PROCESS_STEPS_SCHEMA.yaml

**Features:**
- Validates required fields per step (step_id, phase, name, responsible_component, etc.)
- Checks operation_kind taxonomy compliance
- Validates component references
- Verifies state machine transitions
- Checks guardrail checkpoint structure
- Validates artifact registry references
- Reports compliance metrics and detailed errors

**Usage:**
```bash
python validate_master_splinter_schema.py
```

**Output:**
```
MASTER_SPLINTER SCHEMA VALIDATION REPORT
========================================
Schema: MASTER_SPLINTER_PROCESS_STEPS_SCHEMA.yaml
Version: 1.0.0

STATISTICS:
  Total Phases: 8
  Total Steps: 26
  Total Components: 5
  Total Operations: 12
  Total Guardrails: 4
  Total Artifacts: 6

RESULT: PASSED ✅
Schema is valid and compliant.
```

## State Machine

```
INIT
  ↓
DISCOVERY (discover phase plans)
  ↓
CONVERSION (phase plans → workstreams)
  ↓
DAG_RESOLUTION (build dependency graph)
  ↓
EXECUTION (multi-agent coordination)
  ↓
CONSOLIDATION (aggregate results to DB)
  ↓
SYNC (GitHub feature branch + commits)
  ↓
DONE
```

**Terminal States:** DONE, FAILED
**Special Rule:** Any phase can transition to FAILED

## Components

| Component | File | Role |
|-----------|------|------|
| **run_master_splinter** | `run_master_splinter.py` | Master orchestrator - 1-touch execution |
| **phase_plan_to_workstream** | `phase_plan_to_workstream.py` | Phase plan → Workstream JSON converter |
| **multi_agent_workstream_coordinator** | `multi_agent_workstream_coordinator.py` | DAG-based multi-agent executor |
| **sync_workstreams_to_github** | `sync_workstreams_to_github.py` | GitHub sync with feature branches |
| **circuit_breakers** | `config/circuit_breakers.yaml` | Guardrails and fix loop config |

## Operation Kinds

1. **orchestration** - Master coordination, state transitions
2. **phase_discovery** - YAML phase plan discovery
3. **workstream_conversion** - Phase plan transformation
4. **dag_resolution** - Dependency graph construction
5. **multi_agent_execution** - Agent task coordination
6. **result_consolidation** - Result aggregation and reporting
7. **github_sync** - Branch creation, commits, push
8. **circuit_breaker_check** - Guardrail enforcement
9. **fix_loop** - Automated error repair
10. **initialization** - Bootstrap and setup
11. **persistence** - SQLite/JSON operations
12. **event_emission** - Logging and metrics

## Execution Modes

### 1. One-Touch (Full Pipeline)
```bash
python run_master_splinter.py
```
Runs all phases: INIT → DISCOVERY → CONVERSION → DAG_RESOLUTION → EXECUTION → CONSOLIDATION → SYNC → DONE

**NO STOP MODE:** Continues through all tasks even on errors

### 2. Conversion Only
```bash
python phase_plan_to_workstream.py
```
Converts phase plans to workstreams without execution

### 3. Multi-Agent Only
```bash
python multi_agent_workstream_coordinator.py
```
Executes existing workstreams without conversion or sync

### 4. GitHub Sync Only
```bash
python sync_workstreams_to_github.py
```
Syncs workstreams to GitHub without execution

## Artifacts

| Artifact | Path | Format | Description |
|----------|------|--------|-------------|
| **Phase Plans** | `plans/phases/*.yml` | YAML | Phase plan templates with execution steps |
| **Workstreams** | `workstreams/*.json` | JSON | Executable workstream definitions |
| **Consolidated DB** | `.state/multi_agent_consolidated.db` | SQLite | All execution results from all agents |
| **Master Report** | `reports/master_run_*.json` | JSON | Master orchestrator summary |
| **Sync Report** | `reports/sync_summary_*.json` | JSON | GitHub sync summary |
| **Logs** | `logs/*.log` | TEXT | Execution logs per component |

## Guardrail Checkpoints

1. **GC-MS-PREREQ** (INIT) - Validate prerequisites exist
2. **GC-MS-DAG** (DAG_RESOLUTION) - No circular dependencies
3. **GC-MS-CIRCUIT** (EXECUTION) - Circuit breaker enforcement
4. **GC-MS-FIX** (EXECUTION) - Fix loop attempt limits

## Anti-Patterns Blocked

1. **ANTI-STOP-ON-ERROR** - Stopping execution on first error (violates NO STOP MODE)
2. **ANTI-CIRCULAR-DEPS** - Circular dependencies in phase plan DAG
3. **ANTI-MISSING-WORKSTREAM** - depends_on references non-existent workstream
4. **ANTI-SCOPE-VIOLATION** - Modifying forbidden_paths

## Integration with ACMS/MINI_PIPE

MASTER_SPLINTER orchestration can integrate with ACMS/MINI_PIPE:

- **Phase Plans** can invoke ACMS gap discovery and planning
- **Workstreams** can execute via MINI_PIPE scheduler
- **Circuit Breakers** shared configuration between systems
- **Artifact Registry** cross-references for dependency tracking

## Comparison with PROCESS_STEPS_SCHEMA.yaml

| Aspect | MASTER_SPLINTER | ACMS/MINI_PIPE |
|--------|----------------|----------------|
| **Focus** | Multi-agent orchestration | Gap-driven autonomous code modification |
| **Phases** | 8 (INIT → SYNC → DONE) | 7 (INIT → SUMMARY → DONE) |
| **Steps** | 26 orchestration steps | 35+ execution steps |
| **Components** | 5 orchestration tools | 8+ ACMS components |
| **Operations** | 12 kinds | 10 kinds |
| **Special Mode** | NO STOP MODE | Guardrail enforcement |

Both schemas follow the same structure:
- Required fields per step
- State machine definitions
- Component registry
- Operation taxonomy
- Artifact tracking
- Guardrail checkpoints

## Validation

Run validator to check schema compliance:

```bash
python validate_master_splinter_schema.py
```

Expected output:
- ✅ All 26 steps validated
- ✅ All components documented
- ✅ All operation kinds defined
- ✅ State machine transitions valid
- ✅ Guardrail checkpoints complete

## Next Steps

1. **Use schema for tooling generation**: Auto-generate DAG visualizations, execution trackers
2. **Integrate with GitHub Projects**: Sync phase plans to GitHub Project items
3. **Add step-level metrics**: Track execution time, resource usage per step
4. **Create execution templates**: Reference templates in step.execution_templates
5. **Build schema validator CI/CD**: Run validation on phase plan commits

## Related Documentation

- `MASTER_SPLINTER_Phase_Plan_Template.yml` - Phase plan template
- `config/circuit_breakers.yaml` - Circuit breaker configuration
- `../prompts/PROCESS_STEPS_SCHEMA.yaml` - ACMS/MINI_PIPE schema (sibling system)
- `../prompts/validate_process_steps_schema.py` - ACMS validator (reference)

---

**Created:** 2025-12-09
**Version:** 1.0.0
**Status:** ✅ Validated and Complete
