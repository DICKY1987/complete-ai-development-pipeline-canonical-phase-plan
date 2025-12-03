# Phase 1 – Planning & Spec Alignment

**Purpose**: Take OpenSpec + PM epics + plan docs → workstreams + phase plans.

## Phase Contents

Located in: `phase1_planning/`

- `specifications/` - Spec content and OpenSpec files
- `SPEC_tools/` - Spec processing tools
- `plans/` - Phase plans and CCPM integration
- `README.md` - This file

## Current Components

### Specifications (`specifications/`)
- Core specs (10 production specs):
  - UET_BOOTSTRAP_SPEC.md
  - UET_COOPERATION_SPEC.md
  - UET_PHASE_SPEC_MASTER.md
  - UET_WORKSTREAM_SPEC.md
  - UET_TASK_ROUTING_SPEC.md
  - UET_PROMPT_RENDERING_SPEC.md
  - UET_PATCH_MANAGEMENT_SPEC.md
  - UET_CLI_TOOL_EXECUTION_SPEC.md
  - UTE_ID_SYSTEM_SPEC.md
  - UET_EXECUTION_KERNEL_PARALLELISM_STRATEGY_SPEC_V2.md

### Spec Tools (`SPEC_tools/`)
- Spec processing and validation utilities

### Plans (`plans/`)
- Phase plans
- CCPM integration files

### Implementation (`core/planning/`)
Located in cross-cutting `core/` directory:
- `planner.py` - Workstream planner ⚠️ (STUB - partial implementation)
- `ccpm_integration.py` - CCPM/PM integration ⚠️ (partial)
- `archive.py` - Historical archival ✅

## Main Operations
- Ingest OpenSpec, PM epics, phase docs
- Validate specs & build spec index + dependency graph
- Convert accepted specs into workstream JSON
- Link specs and workstreams back to CCPM/PM issues

## Test Coverage
0 tests (no implementation yet)

## Status
⚠️ Partial (40%) - Planner needs implementation
