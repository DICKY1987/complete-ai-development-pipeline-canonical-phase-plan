# Folder Overlap Analysis Report
Generated: 2025-12-04 15:24:58

## Executive Summary

This analysis identifies duplicate responsibilities and deliverables across the repository structure.
The codebase shows evidence of a migration from root-level organization to phase-based containers.

## Critical Findings

### 1. DUPLICATE IMPLEMENTATIONS

#### Planning Module (Phase 1)
- **Root Location**: `core/planning/` (3 files, minimal stubs)
  - planner.py (STUB - TODO only)
  - ccpm_integration.py (partial)
  - archive.py

- **Phase Location**: `phase1_planning/modules/` (3 subdirectories, ~100+ files)
  - workstream_planner/ (full implementation with src/, tests/, docs/, schemas/)
  - spec_parser/ (full implementation)
  - spec_tools/ (full implementation)

**Status**: Phase-based implementation is MORE COMPLETE than root-level
**Recommendation**: Deprecate `core/planning/` stubs, use phase1_planning modules as SSOT

---

#### Tool Adapters (Phase 4)
- **Root Location**: `core/adapters/` (~10 files)
  - base.py
  - registry.py
  - subprocess_adapter.py
  - MISSING: Advanced pooling, cluster management

- **Phase Location**: `phase4_routing/modules/tool_adapters/` (~60+ files)
  - Full src/adapters/ implementation
  - Complete test suite (tests/)
  - Documentation (docs/)
  - Configuration (config/)
  - Schemas (schemas/)

**Status**: Phase-based implementation is SIGNIFICANTLY MORE COMPLETE
**Recommendation**: Deprecate `core/adapters/` minimal version, use phase4_routing modules as SSOT

---

### 2. IMPORT PATH CONFLICTS

#### Current Import Patterns:
- Production code uses: `from core.planning import *`
- Tests use both: `from core.adapters import *` AND `from phase4_routing.modules.tool_adapters import *`

**Issue**: Import paths point to INCOMPLETE root-level implementations while phase-based modules have full code

**Resolution Required**:
1. Update all imports to use phase-based paths
2. OR symlink/redirect root paths to phase implementations
3. OR consolidate all code into root-level (reverse migration)

---

### 3. SCHEMA DUPLICATION

Multiple schema directories exist:
- `schema/` (root, 17 JSON schemas) - Referenced in CODEBASE_INDEX
- `phase*/modules/*/schemas/` (per-module schemas)

**Analysis**: Root-level schemas appear authoritative (referenced by CI)
**Recommendation**: Keep root `schema/` as SSOT, phase schemas for module-specific extensions only

---

### 4. CONFIGURATION DUPLICATION

- `config/` (root)
- `phase0_bootstrap/config/`
- `phase1_planning/modules/*/config/`
- `phase4_routing/modules/*/config/`

**Recommendation**: Establish hierarchy:
1. Root `config/` = Global defaults
2. Phase `config/` = Phase-specific overrides
3. Module `config/` = Module-specific settings

---

## DETAILED OVERLAP MATRIX

| Component | Root Location | Phase Location | Root Status | Phase Status | Authoritative |
|-----------|---------------|----------------|-------------|--------------|---------------|
| Workstream Planner | core/planning/planner.py | phase1_planning/modules/workstream_planner/ | STUB (0%) | FULL (100%) | **Phase** |
| CCPM Integration | core/planning/ccpm_integration.py | phase1_planning/modules/workstream_planner/src/ | Partial (40%) | FULL (100%) | **Phase** |
| Spec Parser | ❌ Missing | phase1_planning/modules/spec_parser/ | N/A | FULL (100%) | **Phase** |
| Tool Adapters | core/adapters/ | phase4_routing/modules/tool_adapters/ | Basic (30%) | FULL (100%) | **Phase** |
| AIM Bridge | aim/ | phase4_routing/modules/aim_tools/ | FULL (100%) | Duplicate | **Root** |
| Error Engine | error/engine/ | phase6_error_recovery/ (container) | FULL (100%) | Container only | **Root** |
| Bootstrap | core/bootstrap/ | phase0_bootstrap/ (container) | FULL (100%) | Container only | **Root** |
| State Management | core/state/ | ❌ No duplicate | FULL (100%) | N/A | **Root** |
| Schemas | schema/ | phase*/modules/*/schemas/ | FULL (100%) | Module-specific | **Root** |

---

## MIGRATION STATUS

### Completed Migrations (to Archive):
- ✅ `modules/` (m-prefix implementation) → `_ARCHIVE/` (2025-12-03)
- ✅ Large archive content → External storage (2025-12-02)
- ✅ `_ARCHIVE/phase0_bootstrap_orchestrator_duplicate/`
- ✅ `_ARCHIVE/phase1_ccpm_integration_duplicate/`
- ✅ `_ARCHIVE/phase4_tool_adapters_duplicate/`

### Pending Consolidation:
- ⚠️ `core/planning/` vs `phase1_planning/modules/`
- ⚠️ `core/adapters/` vs `phase4_routing/modules/tool_adapters/`
- ⚠️ Multiple config/ and schema/ directories

---

## RECOMMENDED ACTIONS

### HIGH PRIORITY (Blocking Development)

1. **Establish Single Source of Truth (SSOT)**
   - Decision: Root-level OR phase-based?
   - Update CODEBASE_INDEX.yaml accordingly
   - Document in DIRECTORY_GUIDE.md

2. **Fix Import Paths**
   - If Phase-based wins: Update all `from core.planning` → `from phase1_planning.modules.workstream_planner`
   - If Root wins: Move all phase module code to root locations
   - Run: `python scripts/paths_index_cli.py gate` to validate

3. **Archive Stubs**
   - Move `core/planning/` to `_ARCHIVE/core_planning_stubs/`
   - Move `core/adapters/` to `_ARCHIVE/core_adapters_basic/`
   - Update deprecation notices

### MEDIUM PRIORITY (Technical Debt)

4. **Schema Consolidation**
   - Audit all schema files for duplicates
   - Centralize in root `schema/`
   - Document module-specific schema extensions

5. **Configuration Hierarchy**
   - Document config precedence order
   - Create config loading cascade
   - Validate with tests

6. **Test Coverage**
   - Ensure tests reference authoritative implementation
   - Remove tests for deprecated code
   - Update test imports

### LOW PRIORITY (Documentation)

7. **Update Documentation**
   - PHASE_DIRECTORY_MAP.md (mark deprecated paths)
   - Folder Structure to Phase Mapping.md (clarify SSOT)
   - CODEBASE_INDEX.yaml (remove deprecated modules)

8. **Add Migration Guide**
   - Document why phase-based structure exists
   - Provide import migration examples
   - Timeline for deprecation removal

---

## DECISION TREE

### Option A: Phase-Based Structure Wins
**Pros**:
- More complete implementations
- Better module isolation
- Clearer phase boundaries

**Cons**:
- Longer import paths
- More directory nesting
- Requires widespread import updates

**Action**:
1. Move `core/planning/` → `_ARCHIVE/`
2. Move `core/adapters/` → `_ARCHIVE/`
3. Update all imports to phase paths
4. Update PYTHONPATH to include phase directories

---

### Option B: Root-Level Structure Wins
**Pros**:
- Shorter import paths
- Matches CODEBASE_INDEX.yaml
- Less nesting

**Cons**:
- Loses phase isolation benefits
- Requires moving lots of code
- May break existing phase tooling

**Action**:
1. Move `phase1_planning/modules/workstream_planner/src/*` → `core/planning/`
2. Move `phase4_routing/modules/tool_adapters/src/*` → `core/adapters/`
3. Keep phase directories as containers/docs only
4. Update tests to use root imports

---

### Option C: Hybrid (Current Mess - Not Recommended)
**Status**: Current state with dual implementations
**Outcome**: Continued confusion, import errors, maintenance burden

---

## IMPACT ASSESSMENT

### Files Affected by Consolidation:
- Import statements: ~50-100 files (est.)
- Tests: ~30 test files
- Documentation: ~10 docs
- CI/CD: 2-3 workflow files

### Estimated Effort:
- Option A (Phase wins): 4-6 hours
- Option B (Root wins): 8-12 hours
- Option C (Do nothing): Infinite ongoing confusion

### Risk Level:
- **Option A**: Low (phase code already more complete)
- **Option B**: Medium (requires code movement)
- **Option C**: High (continued tech debt accumulation)

---

## NEXT STEPS

1. **Choose SSOT Strategy** (Option A or B)
2. **Create Consolidation Workstream**
3. **Run Import Path Audit**: `grep -r "from core\\.planning\\|from core\\.adapters" --include="*.py"`
4. **Execute Migration**
5. **Update CI Gates**
6. **Archive Deprecated Code**

---

## APPENDIX: File Counts

### Root Structure:
- `core/planning/`: 3 files
- `core/adapters/`: 10 files
- `schema/`: 17 schemas
- `config/`: ~5 config files

### Phase Structure:
- `phase1_planning/modules/`: 100+ files
- `phase4_routing/modules/`: 100+ files
- Phase schemas: ~20+ schema files
- Phase configs: ~15+ config files

**Total Duplication**: ~50-100 files with overlapping responsibilities
