# Folder Overlap Consolidation - Action Plan

**Created**: 2025-12-04
**Status**: PROPOSED
**Priority**: HIGH (Blocking Clean Development)

## Problem Statement

The repository contains **duplicate implementations** across root-level and phase-based directory structures:
- `core/planning/` (stubs) vs `phase1_planning/modules/` (full implementation)
- `core/adapters/` (minimal) vs `phase4_routing/modules/tool_adapters/` (complete)
- Multiple schema and config directories

This creates:
- Import path confusion
- Maintenance burden
- Unclear "single source of truth" (SSOT)
- Risk of editing the wrong version

## Recommended Strategy: **Option A - Phase-Based Structure Wins**

### Rationale
1. Phase implementations are **more complete** (100+ files vs 3-10 files)
2. Better **module isolation** and testing
3. Aligns with phase-based pipeline architecture (0-7)
4. Root-level stubs are incomplete/TODO-only

### Decision
- **SSOT**: Phase-based modules (`phase*_*/modules/`)
- **Archive**: Root-level stubs (`core/planning/`, `core/adapters/`)
- **Schemas**: Keep root `schema/` as global registry
- **Config**: Root `config/` = global, phase `config/` = overrides

---

## Phase 1: Planning Module Consolidation

### 1.1 Archive Root-Level Stubs
```bash
# Move to archive
mkdir -p _ARCHIVE/core_planning_stubs_2025-12-04
mv core/planning/* _ARCHIVE/core_planning_stubs_2025-12-04/

# Create deprecation notice
echo "DEPRECATED: Moved to phase1_planning/modules/ on 2025-12-04" > core/planning/README_DEPRECATED.md
```

### 1.2 Update Import Paths
**Find affected files**:
```bash
grep -r "from core\.planning" --include="*.py" .
```

**Update imports**:
```python
# OLD (deprecated)
from core.planning.planner import generate_workstream
from core.planning.ccpm_integration import integrate_ccpm

# NEW (authoritative)
from phase1_planning.modules.workstream_planner.src.planner import generate_workstream
from phase1_planning.modules.workstream_planner.src.ccpm_integration import integrate_ccpm
```

### 1.3 Update PYTHONPATH
Add to `.env` or activate script:
```bash
export PYTHONPATH="${PYTHONPATH}:./phase1_planning/modules/workstream_planner/src"
export PYTHONPATH="${PYTHONPATH}:./phase1_planning/modules/spec_parser/src"
export PYTHONPATH="${PYTHONPATH}:./phase1_planning/modules/spec_tools/src"
```

### 1.4 Update Tests
```bash
# Update test imports
sed -i 's/from core\.planning/from phase1_planning.modules.workstream_planner.src/g' tests/planning/*.py
```

---

## Phase 2: Tool Adapter Consolidation

### 2.1 Archive Root-Level Minimal Implementation
```bash
mkdir -p _ARCHIVE/core_adapters_minimal_2025-12-04
mv core/adapters/* _ARCHIVE/core_adapters_minimal_2025-12-04/

echo "DEPRECATED: Moved to phase4_routing/modules/tool_adapters/ on 2025-12-04" > core/adapters/README_DEPRECATED.md
```

### 2.2 Update Import Paths
**Find affected files**:
```bash
grep -r "from core\.adapters" --include="*.py" .
```

**Update imports**:
```python
# OLD (deprecated)
from core.adapters.base import ToolAdapter
from core.adapters.registry import AdapterRegistry
from core.adapters.subprocess_adapter import SubprocessAdapter

# NEW (authoritative)
from phase4_routing.modules.tool_adapters.src.adapters.base import ToolAdapter
from phase4_routing.modules.tool_adapters.src.adapters.registry import AdapterRegistry
from phase4_routing.modules.tool_adapters.src.adapters.subprocess_adapter import SubprocessAdapter
```

### 2.3 Update PYTHONPATH
```bash
export PYTHONPATH="${PYTHONPATH}:./phase4_routing/modules/tool_adapters/src"
export PYTHONPATH="${PYTHONPATH}:./phase4_routing/modules/aim_tools/src"
export PYTHONPATH="${PYTHONPATH}:./phase4_routing/modules/aider_integration/src"
```

### 2.4 Update Tests
```bash
sed -i 's/from core\.adapters/from phase4_routing.modules.tool_adapters.src.adapters/g' tests/adapters/*.py
```

---

## Phase 3: Schema Consolidation

### 3.1 Audit Schema Files
```bash
# Find all schemas
find . -name "*.schema.json" -o -name "*_schema.json" | sort

# Compare for duplicates
find . -name "*.schema.json" -exec md5sum {} \; | sort
```

### 3.2 Establish Hierarchy
- **Root `schema/`**: Global/shared schemas (17 files - keep as-is)
- **Phase `schemas/`**: Module-specific extensions only
- **Rule**: Phase schemas MUST NOT duplicate root schemas

### 3.3 Add Validation
Create `scripts/validate_schema_no_duplicates.py`:
```python
#!/usr/bin/env python3
"""Ensure no schema duplication between root and phase modules."""
import json
from pathlib import Path

root_schemas = set(Path("schema").glob("*.json"))
phase_schemas = set(Path(".").glob("phase*/modules/*/schemas/*.json"))

# Compare schema IDs
conflicts = []
for phase_schema in phase_schemas:
    schema_id = json.loads(phase_schema.read_text()).get("$id")
    for root_schema in root_schemas:
        if json.loads(root_schema.read_text()).get("$id") == schema_id:
            conflicts.append((phase_schema, root_schema))

if conflicts:
    print("ERROR: Schema ID conflicts found:")
    for p, r in conflicts:
        print(f"  {p} duplicates {r}")
    sys.exit(1)
```

---

## Phase 4: Configuration Consolidation

### 4.1 Establish Loading Order
Document in `config/README.md`:
```markdown
# Configuration Loading Hierarchy

1. **Root `config/`**: Global defaults (lowest priority)
2. **Phase `phase*/config/`**: Phase overrides
3. **Module `phase*/modules/*/config/`**: Module-specific settings
4. **Environment `.env`**: Runtime overrides (highest priority)

Config files cascade: Module → Phase → Root → Defaults
```

### 4.2 Implement Config Loader
Update `core/config_loader.py`:
```python
def load_config(module_path: str = None):
    """Load config with hierarchy: module > phase > root > defaults."""
    configs = [
        Path("config/defaults.yaml"),           # Base
        Path("config/settings.yaml"),           # Root
    ]

    if module_path:
        phase = extract_phase(module_path)  # e.g., "phase1_planning"
        configs.extend([
            Path(f"{phase}/config/settings.yaml"),
            Path(f"{module_path}/config/settings.yaml"),
        ])

    return merge_configs(configs)  # Later configs override earlier
```

---

## Phase 5: Update Documentation

### 5.1 Update CODEBASE_INDEX.yaml
```yaml
modules:
  - id: "core.planning"
    status: "DEPRECATED"
    deprecated_date: "2025-12-04"
    replacement: "phase1_planning.modules.workstream_planner"

  - id: "core.adapters"
    status: "DEPRECATED"
    deprecated_date: "2025-12-04"
    replacement: "phase4_routing.modules.tool_adapters"

  - id: "phase1_planning.modules.workstream_planner"
    name: "Workstream Planning"
    path: "phase1_planning/modules/workstream_planner/src/"
    layer: "domain"
    purpose: "Generate workstreams from specs, CCPM integration"
    ai_priority: "HIGH"
    edit_policy: "safe"

  - id: "phase4_routing.modules.tool_adapters"
    name: "Tool Adapters"
    path: "phase4_routing/modules/tool_adapters/src/"
    layer: "api"
    purpose: "Tool adapter interfaces and implementations"
    ai_priority: "HIGH"
    edit_policy: "safe"
```

### 5.2 Update PHASE_DIRECTORY_MAP.md
Add deprecation notices and update mappings to reference phase modules as authoritative.

### 5.3 Create Migration Guide
Create `docs/IMPORT_MIGRATION_GUIDE.md` with examples and timeline.

---

## Phase 6: CI/CD Updates

### 6.1 Update Path Validation
Update `scripts/paths_index_cli.py` to recognize phase-based imports as valid:
```python
VALID_IMPORT_PATTERNS = [
    r"^from core\.state\.",
    r"^from core\.engine\.",
    r"^from phase1_planning\.modules\.workstream_planner\.src\.",
    r"^from phase4_routing\.modules\.tool_adapters\.src\.",
    # ... etc
]

DEPRECATED_PATTERNS = [
    (r"^from core\.planning\.", "Use phase1_planning.modules.workstream_planner.src"),
    (r"^from core\.adapters\.", "Use phase4_routing.modules.tool_adapters.src"),
]
```

### 6.2 Add Pre-commit Hook
Create `.pre-commit-config.yaml` entry:
```yaml
- id: check-deprecated-imports
  name: Check for deprecated import paths
  entry: python scripts/check_deprecated_imports.py
  language: python
  types: [python]
```

---

## Validation Checklist

- [ ] All imports updated (run `grep -r "from core\.planning\|from core\.adapters" --include="*.py"`)
- [ ] Tests pass (`pytest -q tests/`)
- [ ] CI gates pass (`python scripts/paths_index_cli.py gate`)
- [ ] Documentation updated (CODEBASE_INDEX, PHASE_DIRECTORY_MAP, import guide)
- [ ] PYTHONPATH includes phase module paths
- [ ] Deprecated code moved to `_ARCHIVE/`
- [ ] Deprecation notices created
- [ ] Schema validation passes (no duplicates)
- [ ] Config hierarchy documented

---

## Rollback Plan

If issues arise:
```bash
# Restore from archive
cp -r _ARCHIVE/core_planning_stubs_2025-12-04/* core/planning/
cp -r _ARCHIVE/core_adapters_minimal_2025-12-04/* core/adapters/

# Revert imports (git)
git checkout HEAD -- $(grep -rl "from phase1_planning.modules" --include="*.py")
```

---

## Timeline

- **Day 1**: Planning consolidation (Phase 1)
- **Day 2**: Adapter consolidation (Phase 2)
- **Day 3**: Schema/config consolidation (Phases 3-4)
- **Day 4**: Documentation updates (Phase 5)
- **Day 5**: CI/CD updates and validation (Phase 6)

**Total Estimated Effort**: 5-8 hours of focused work

---

## Success Criteria

1. ✅ Zero import errors when running: `python -m pytest tests/`
2. ✅ CI path gate passes: `python scripts/paths_index_cli.py gate --db refactor_paths.db`
3. ✅ Clear SSOT documented in `CODEBASE_INDEX.yaml`
4. ✅ All deprecated code in `_ARCHIVE/` with dated folders
5. ✅ Import migration guide published in `docs/`
6. ✅ No duplicate schema IDs across root and phase directories

---

## Next Actions

**Immediate**:
1. Review and approve this plan
2. Create consolidation workstream in issue tracker
3. Branch: `feature/consolidate-phase-modules`

**Execute**:
4. Run Phases 1-6 in order
5. Validate at each step
6. Merge to main with comprehensive testing

**Follow-up**:
7. Monitor for import issues post-merge
8. Document lessons learned
9. Archive planning documents
