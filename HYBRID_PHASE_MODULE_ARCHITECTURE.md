# Hybrid Phase-Module Architecture Plan

**Date**: 2025-12-03  
**Goal**: Restructure to hybrid architecture where each phase contains self-contained modules

## Architecture Concept

```
phaseN_*/
  modules/
    module_name/
      src/        # Code
      tests/      # Module-specific tests
      docs/       # Module-specific docs
      schemas/    # Module-specific schemas
      config/     # Module-specific config
      scripts/    # Module-specific scripts
```

## Proposed Module Structure by Phase

### Phase 0 – Bootstrap & Initialization

```
phase0_bootstrap/
  modules/
    bootstrap_orchestrator/
      src/
        orchestrator.py
        discovery.py
        selector.py
        generator.py
        validator.py
      tests/
        test_orchestrator.py
        test_discovery.py
      docs/
        architecture.md
        usage.md
      schemas/
        (move from ../schema/)
      config/
        (move from ../config/)
  README.md
```

**Migration**: 
- `core/bootstrap/` → `phase0_bootstrap/modules/bootstrap_orchestrator/src/`
- `schema/` → `phase0_bootstrap/modules/bootstrap_orchestrator/schemas/`
- `config/` → `phase0_bootstrap/modules/bootstrap_orchestrator/config/`
- Split tests from `tests/bootstrap/` → module tests/

---

### Phase 1 – Planning & Spec Alignment

```
phase1_planning/
  modules/
    spec_parser/
      src/
        openspec_parser.py
        spec_index.py
      tests/
        test_parser.py
      docs/
        spec_format.md
      schemas/
        openspec.schema.json
    
    workstream_planner/
      src/
        planner.py
        ccpm_integration.py
      tests/
        test_planner.py
      docs/
        planning_guide.md
    
    spec_tools/
      src/
        (from SPEC_tools/)
      tests/
      docs/
  
  README.md
```

**Migration**:
- `core/planning/` → `phase1_planning/modules/workstream_planner/src/`
- `specifications/` → `phase1_planning/modules/spec_parser/docs/` (content)
- `SPEC_tools/` → `phase1_planning/modules/spec_tools/src/`
- `plans/` → `phase1_planning/modules/workstream_planner/docs/examples/`

---

### Phase 4 – Tool Routing & Adapter Selection

```
phase4_routing/
  modules/
    aim_tools/
      src/
        bridge/
        capabilities/
        audit.py
      tests/
        test_bridge.py
        test_capabilities.py
      docs/
        aim_architecture.md
        usage_guide.md
      schemas/
        capability.schema.json
      config/
        default_capabilities.yaml
    
    tool_adapters/
      src/
        guard/
        indexer/
        patcher/
        renderer/
        resolver/
      tests/
        test_guard.py
        test_indexer.py
      docs/
        adapter_guide.md
    
    aider_integration/
      src/
        (from aider/)
      tests/
      docs/
      config/
        aider_config.yaml
  
  README.md
```

**Migration**:
- `aim/` → `phase4_routing/modules/aim_tools/src/`
- `tools/` → `phase4_routing/modules/tool_adapters/src/`
- `aider/` → `phase4_routing/modules/aider_integration/src/`
- Split related tests from `tests/`

---

### Phase 6 – Error Analysis & Recovery

```
phase6_error_recovery/
  modules/
    error_engine/
      src/
        error_engine.py
        plugin_manager.py
        error_state_machine.py
      tests/
        test_error_engine.py
      docs/
        error_pipeline.md
      schemas/
        error_record.schema.json
    
    plugins/
      python_ruff/
        src/
          plugin.py
        tests/
          test_plugin.py
        docs/
          README.md
        config/
          ruff_config.toml
      
      python_mypy/
        src/
        tests/
        docs/
        config/
      
      # ... (21 plugins total)
  
  README.md
```

**Migration**:
- `error/engine/` → `phase6_error_recovery/modules/error_engine/src/`
- `error/plugins/python_ruff/` → `phase6_error_recovery/modules/plugins/python_ruff/src/`
- Each plugin becomes a self-contained module

---

### Phase 7 – Monitoring & Completion

```
phase7_monitoring/
  modules/
    gui_components/
      src/
        textual/
        tui_app/
      tests/
        test_ui_components.py
      docs/
        ui_architecture.md
      config/
        tui_config.yaml
    
    state_manager/
      src/
        (from state/)
      tests/
      docs/
      schemas/
        state.schema.json
  
  README.md
```

**Migration**:
- `gui/` → `phase7_monitoring/modules/gui_components/src/`
- `state/` → `phase7_monitoring/modules/state_manager/src/`

---

## Cross-Cutting at Root (Shared Infrastructure)

These stay at root because they're used by ALL phases:

```
core/                    # Orchestrator that RUNS all phases
  engine/
  state/
  adapters/

patterns/                # Pattern library (Layer A)
tests/integration/       # Integration tests ACROSS modules
scripts/                 # Repo-wide automation
docs/                    # Repo-wide architecture docs
uet/                     # Framework workspace
UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/
```

---

## Migration Strategy

### Phase 1: Create Module Structure (No File Moves)

For each phase, create the `modules/` structure:

```bash
# Example for phase4_routing
mkdir -p phase4_routing/modules/aim_tools/{src,tests,docs,schemas,config}
mkdir -p phase4_routing/modules/tool_adapters/{src,tests,docs,schemas}
mkdir -p phase4_routing/modules/aider_integration/{src,tests,docs,config}
```

### Phase 2: Move Files into Modules

Move folders into their module homes:

```bash
# Phase 4 example
mv phase4_routing/aim phase4_routing/modules/aim_tools/src/
mv phase4_routing/tools phase4_routing/modules/tool_adapters/src/
mv phase4_routing/aider phase4_routing/modules/aider_integration/src/
```

### Phase 3: Extract Module-Specific Tests

From the global `tests/` directory, move module-specific tests:

```bash
# Extract AIM tests
mv tests/aim/* phase4_routing/modules/aim_tools/tests/

# Extract tool adapter tests  
mv tests/adapters/* phase4_routing/modules/tool_adapters/tests/
```

### Phase 4: Add Module README Files

Each module gets a README.md:

```markdown
# Module: aim_tools

**Phase**: 4 (Tool Routing & Adapter Selection)  
**Layer**: API  
**Purpose**: AI tool capability matching and selection

## Structure

- `src/` - Source code
- `tests/` - Module tests
- `docs/` - Module documentation
- `schemas/` - JSON schemas
- `config/` - Configuration files

## Dependencies

- None (pure Python)

## Usage

See `docs/usage_guide.md`
```

---

## Benefits of Hybrid Approach

1. **Phase Organization** - Still organized by pipeline flow (0-7)
2. **Module Ownership** - Everything for a module in one place
3. **AI Context Loading** - Load one module directory = complete context
4. **Parallel Development** - Different teams can own different modules
5. **Clear Boundaries** - Modules are atomic, testable units
6. **Import Simplicity** - `from phase4_routing.modules.aim_tools.src import X`

---

## Next Steps

1. Create module structure in each phase
2. Move existing folders into module src/
3. Extract module-specific tests from tests/
4. Add module README files
5. Update import paths
6. Update documentation

---

## File Count Estimates

- Phase 0: 1 module (bootstrap_orchestrator) - 78 files
- Phase 1: 3 modules (spec_parser, workstream_planner, spec_tools) - 341 files
- Phase 4: 3 modules (aim_tools, tool_adapters, aider_integration) - 171 files
- Phase 6: 22 modules (error_engine + 21 plugins) - 231 files
- Phase 7: 2 modules (gui_components, state_manager) - 88 files

**Total**: ~31 modules across 5 phases (phases 2, 3, 5 have no folders yet)
