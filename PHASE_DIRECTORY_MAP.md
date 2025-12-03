# Phase Directory Mapping

This document maps the repository structure to the Phase-Based AI Dev Pipeline (0-7).

## Phase-Aligned Directories

### Phase 0 – Bootstrap & Initialization
- `phase0_bootstrap/` - **Phase container**
  - `config/` - Configuration files
  - `schema/` - Validation schemas (17 JSON schemas)
  - `README.md` - Phase documentation
- Related in `core/`: `core/bootstrap/` - Bootstrap orchestrator ✅ Complete (100%)

### Phase 1 – Planning & Spec Alignment  
- `phase1_planning/` - **Phase container**
  - `specifications/` - Spec content and files
  - `SPEC_tools/` - Spec processing tools
  - `plans/` - Phase plans and CCPM integration
  - `README.md` - Phase documentation
- Related in `core/`: `core/planning/` - Workstream planner ⚠️ Partial (40%)

### Phase 2 – Request Building & Run Creation
- `phase2_request_building/` - **Phase container**
  - `README.md` - Phase documentation
- Related in `core/`: 
  - `core/state/` - State management ✅ Complete (100%)
  - `core/engine/execution_request_builder.py` - Request builder ✅

### Phase 3 – Scheduling & Task Graph
- `phase3_scheduling/` - **Phase container**
  - `README.md` - Phase documentation
- Related in `core/`:
  - `core/engine/scheduler.py` - DAG scheduler ✅ Complete (100%)
  - `core/engine/dag_builder.py` - DAG construction ✅
  - `core/state/dag_utils.py` - DAG utilities ✅

### Phase 4 – Tool Routing & Adapter Selection
- `phase4_routing/` - **Phase container**
  - `tools/` - Tool implementations (guard, indexer, patcher, renderer, resolver)
  - `aider/` - Aider adapter configuration
  - `aim/` - AIM environment manager and tool capability matching
  - `README.md` - Phase documentation
- Related in `core/`:
  - `core/engine/router.py` - Task routing ⚠️ Partial (60%)
  - `core/adapters/` - Tool adapters ⚠️ Partial (60%)

### Phase 5 – Execution & Validation
- `phase5_execution/` - **Phase container**
  - `README.md` - Phase documentation
- Related in `core/`:
  - `core/engine/executor.py` - Main executor ⚠️ STUB (needs implementation)
  - `core/engine/resilience/` - Circuit breaker, retry ✅ Complete (100%)
  - `core/engine/monitoring/` - Progress tracking ✅ Complete (100%)

### Phase 6 – Error Analysis, Auto-Fix & Escalation
- `phase6_error_recovery/` - **Phase container**
  - `error/` - Error engine and 21 plugins
    - `error/engine/` - Error engine ⚠️ Partial (60%)
    - `error/plugins/` - 21 error plugins ✅ Complete (100%)
  - `README.md` - Phase documentation

### Phase 7 – Monitoring, Completion & Archival
- `phase7_monitoring/` - **Phase container**
  - `gui/` - UI components and dashboards
  - `state/` - State persistence
  - `README.md` - Phase documentation
- Related in `core/`:
  - `core/ui_cli.py` - CLI dashboard ⚠️ Partial (30%)
  - `core/engine/monitoring/` - Run monitoring ✅ Complete (100%)

## Cross-Cutting Directories (Not Phase-Specific)

These directories support multiple phases and should NOT be forced into 0-7:

- `core/` - Core engine (orchestrator, scheduler, executor) - used across phases 2-7
- `patterns/` - Cross-cutting patterns layer (Layer A)
- `modules/` - Module system
- `tests/` - Testing infrastructure
- `scripts/` - Utility scripts
- `docs/` - Documentation
- `glossary/` - Terminology
- `assets/` - Static assets
- `uet/` - Universal Execution Templates
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/` - UET framework

## Archive and System Directories

- `_ARCHIVE/` - Archived content
  - `_ARCHIVE/modules_legacy_m-prefix_implementation/` - ⚠️ **DEPRECATED** duplicate module-based implementation (moved 2025-12-03)
    - Contained 152 files with m010001_, m010002_, etc. prefixes
    - Duplicated functionality from core/, error/, aim/ with module ID system
    - Archived because core/ is the authoritative implementation
- `__pycache__/` - Python cache
- `.*/` - Hidden system directories

## Usage Notes

1. **Phase directories are containers** - Each `phaseN_*/` directory contains the folders relevant to that phase
2. **Core engine orchestrates** - `core/` contains the orchestrator, scheduler, executor that tie all phases together
3. **Cross-cutting remains separate** - `patterns/`, `tests/`, `scripts/`, `docs/`, `uet/` support all phases
4. **Import paths unchanged** - Code still imports from `core.*`, `error.*`, etc. (now under phase directories)
5. **Phase isolation** - Each phase is self-contained with its specific tools and configurations
6. **Archived modules/** - Legacy m-prefix implementation moved to `_ARCHIVE/modules_legacy_m-prefix_implementation/` (2025-12-03)

## Reference

See `Phase-Based AI Dev Pipeline (0–7) – Coherent Process.md` for full pipeline description.
