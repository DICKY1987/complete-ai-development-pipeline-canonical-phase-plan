# Phase Directory Mapping

This document maps the repository structure to the Phase-Based AI Dev Pipeline (0-7).

## Phase-Aligned Directories

### Phase 0 – Bootstrap & Initialization
- `phase0_bootstrap/` - Phase-specific work
- `core/bootstrap/` - Bootstrap orchestrator ✅ Complete (100%)
- `config/` - Configuration files (existing)
- `schema/` - Validation schemas (existing)

### Phase 1 – Planning & Spec Alignment  
- `phase1_planning/` - Phase-specific work
- `core/planning/` - Workstream planner ⚠️ Partial (40%)
- `specifications/` - Spec content (existing)
- `SPEC_tools/` - Spec processing tools (existing)
- `plans/` - Phase plans (existing)

### Phase 2 – Request Building & Run Creation
- `phase2_request_building/` - Phase-specific work
- `core/state/` - State management ✅ Complete (100%)
- `core/engine/execution_request_builder.py` - Request builder ✅

### Phase 3 – Scheduling & Task Graph
- `phase3_scheduling/` - Phase-specific work
- `core/engine/scheduler.py` - DAG scheduler ✅ Complete (100%)
- `core/engine/dag_builder.py` - DAG construction ✅
- `core/state/dag_utils.py` - DAG utilities ✅

### Phase 4 – Tool Routing & Adapter Selection
- `phase4_routing/` - Phase-specific work
- `core/engine/router.py` - Task routing ⚠️ Partial (60%)
- `core/adapters/` - Tool adapters ⚠️ Partial (60%)
- `tools/` - Tool implementations (existing)
- `aider/` - Aider adapter (existing)
- `aim/` - AIM environment manager (existing)

### Phase 5 – Execution & Validation
- `phase5_execution/` - Phase-specific work
- `core/engine/executor.py` - Main executor ⚠️ STUB (needs implementation)
- `core/engine/resilience/` - Circuit breaker, retry ✅ Complete (100%)
- `core/engine/monitoring/` - Progress tracking ✅ Complete (100%)

### Phase 6 – Error Analysis, Auto-Fix & Escalation
- `phase6_error_recovery/` - Phase-specific work
- `error/engine/` - Error engine ⚠️ Partial (60%)
- `error/plugins/` - 21 error plugins ✅ Complete (100%)

### Phase 7 – Monitoring, Completion & Archival
- `phase7_monitoring/` - Phase-specific work
- `core/ui_cli.py` - CLI dashboard ⚠️ Partial (30%)
- `core/engine/monitoring/` - Run monitoring ✅ Complete (100%)
- `gui/` - UI components (existing)
- `state/` - State persistence (existing)

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

1. **Don't force everything into phases** - Some components are cross-cutting by design
2. **Phase directories** (`phase0_bootstrap/`, etc.) are for phase-specific planning and documentation
3. **Implementation lives in core/, error/, etc.** - Phase directories reference the actual code locations
4. **Core engine** (`core/`) orchestrates all phases - it's the spine, not a phase itself
5. **Patterns** are Layer A (cross-cutting), not bound to specific phases
6. **Archived modules/** - Legacy m-prefix implementation moved to `_ARCHIVE/modules_legacy_m-prefix_implementation/` (2025-12-03)

## Reference

See `Phase-Based AI Dev Pipeline (0–7) – Coherent Process.md` for full pipeline description.
