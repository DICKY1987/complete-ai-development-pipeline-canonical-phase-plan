---
doc_id: DOC-GUIDE-MODULE-ID-INTEGRATION-PLAN-412
---

# Integration Plan: MODULE_ID Extension into Phase Plan

**Date**: 2025-11-30  
**Purpose**: Integrate MODULE_ID_EXTENSION spec into the complete phase plan

---

## Executive Summary

### What is MODULE_ID_EXTENSION_AND_MODULE_MAP_SPEC_V1.md?

**Purpose**: Extends the doc_id system with `module_id` field to enable module-centric repository organization.

**Scope**: 
- Adds `module_id` to every doc in `DOC_ID_REGISTRY.yaml`
- Infers module ownership from paths/categories
- Creates `modules/MODULE_DOC_MAP.yaml` for module-centric view
- Prepares for future physical file reorganization

**Status**: **Phase 1.5 work** (between Phase 1 and Phase 2)

---

## Where This Fits in the Complete Phase Plan

### Current Phase Plan Structure:
```
✅ Phase 3 (Nov 29)    Documentation Governance      COMPLETE
⏳ Phase 0 (Nov 30)    Universal Coverage           60% COMPLETE
🔜 Phase 1             CI/CD Integration            NOT STARTED
🔜 Phase 2             Production Hardening         NOT STARTED
🔜 Phase 3.5           Documentation Consolidation  NOT STARTED
```

### **NEW: Insert Phase 1.5 - Module ID Extension**

```
✅ Phase 3 (Nov 29)    Documentation Governance      COMPLETE
⏳ Phase 0 (Nov 30)    Universal Coverage           60% COMPLETE
🔜 Phase 1             CI/CD Integration            NOT STARTED
🔜 Phase 1.5           MODULE_ID Extension          NOT STARTED  ← NEW
🔜 Phase 2             Production Hardening         NOT STARTED
🔜 Phase 3.5           Documentation Consolidation  NOT STARTED
```

---

## Rationale: Why Phase 1.5?

### Dependencies:
**Requires** (from Phase 0):
- ✅ 100% doc_id coverage
- ✅ Complete registry (~3,160 docs)
- ✅ Validated paths in `DOC_ID_REGISTRY.yaml`

**Blocks** (for future phases):
- 🔜 Physical module reorganization
- 🔜 Module-centric refactoring
- 🔜 Automated import path updates

### Logical Position:
1. **After Phase 0**: Need complete doc_id coverage first
2. **After Phase 1**: CI/CD gates ensure registry stability
3. **Before Phase 2**: Module boundaries inform hardening
4. **Before Phase 3.5**: Module map drives doc consolidation

### **Revised Position: Between Phase 1 and Phase 2**

This gives us:
- Stable registry (Phase 0 complete)
- CI/CD protection (Phase 1 gates)
- Module foundation for hardening (Phase 2)

---

## Phase 1.5: MODULE_ID Extension - Detailed Plan

### Goal
Add `module_id` to every doc entry in registry and create module-centric mapping.

### Prerequisites
- [ ] Phase 0 complete (100% coverage)
- [ ] Phase 1 complete (CI/CD gates active)
- [ ] Registry validates with 0 errors
- [ ] All 2,894 docs have doc_ids

### Inputs
- `doc_id/specs/DOC_ID_REGISTRY.yaml` (~3,160 docs)
- `doc_id/reports/docs_inventory.jsonl`
- `MODULE_ID_EXTENSION_AND_MODULE_MAP_SPEC_V1.md` (specification)

### Outputs
1. Updated `DOC_ID_REGISTRY.yaml` with `module_id` fields
2. New `module_taxonomy` section in registry
3. `modules/MODULE_DOC_MAP.yaml` (module-centric view)
4. `doc_id/reports/MODULE_ID_ASSIGNMENT_DRY_RUN.md`
5. `doc_id/reports/MODULE_ID_ASSIGNMENT_FINAL.json`
6. `doc_id/reports/MODULE_ID_UNASSIGNED.jsonl` (if any)

---

## Phase 1.5 Tasks Breakdown

### Task 1.5.1: Create Module Assignment Script (60 min)

**File**: `scripts/module_id_assigner.py`

**Features**:
- Parse DOC_ID_REGISTRY.yaml
- Implement path-based inference rules (from spec section 3.2)
- Support dry-run mode
- Generate assignment reports

**Inference Rules** (from spec):
```python
def infer_module_id(doc_entry):
    """Infer module_id from artifact paths and category."""
    path = get_primary_artifact_path(doc_entry)
    
    # Rule 1: Core modules
    if path.startswith('core/engine/') or path.startswith('tests/engine/'):
        return 'core.engine'
    if path.startswith('core/state/') or path.startswith('tests/state/'):
        return 'core.state'
    if path.startswith('error/'):
        return 'core.error'
    
    # Rule 2: AIM
    if path.startswith('aim/adapters/'):
        return 'aim.adapters'
    if path.startswith('aim/core/'):
        return 'aim.core'
    if path.startswith('aim/'):
        return 'aim.misc'
    
    # Rule 3: PM
    if path.startswith('pm/cli/'):
        return 'pm.cli'
    if path.startswith('pm/'):
        return 'pm.misc'
    
    # Rule 4: Patterns
    if 'patterns/specs/' in path:
        return 'patterns.specs'
    if 'patterns/executors/' in path:
        return 'patterns.executors'
    if 'patterns/examples/' in path:
        return 'patterns.examples'
    
    # Rule 5: Docs/Guides
    if path.startswith('doc_id/') or path.startswith('docs/'):
        return 'docs.guides'
    
    # Rule 6: ADR
    if path.startswith('adr/'):
        return 'adr.architecture'
    
    # Rule 7: Config/Infra
    if path.startswith('config/'):
        return 'config.global'
    if path.startswith('infra/') or path.startswith('.github/'):
        return 'infra.ci'
    
    # Rule 8: Tests (inherit from source module)
    if path.startswith('tests/'):
        return infer_from_test_path(path, doc_entry)
    
    # Fallback
    return 'unassigned'
```

**Commands**:
```bash
# Dry-run mode
python scripts/module_id_assigner.py --dry-run

# Apply mode
python scripts/module_id_assigner.py --apply

# Generate reports only
python scripts/module_id_assigner.py --report-only
```

---

### Task 1.5.2: Create Module Taxonomy (30 min)

**File**: `doc_id/specs/module_taxonomy.yaml`

Define canonical modules:
```yaml
module_taxonomy:
  core.engine:
    description: Core execution engine components (orchestrator, scheduler, executor)
    root_paths:
      - core/engine
      - tests/engine
    
  core.state:
    description: State management, persistence, snapshots
    root_paths:
      - core/state
      - tests/state
  
  core.error:
    description: Error detection, reporting, and recovery
    root_paths:
      - error
      - tests/error
  
  aim.adapters:
    description: AIM adapters, tool bridges, and integrations
    root_paths:
      - aim/adapters
  
  aim.core:
    description: AIM core functionality
    root_paths:
      - aim/core
  
  pm.cli:
    description: Project management CLI tools
    root_paths:
      - pm/cli
  
  patterns.specs:
    description: UET pattern specifications
    root_paths:
      - UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/specs
  
  patterns.executors:
    description: UET pattern executors
    root_paths:
      - UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/executors
  
  docs.guides:
    description: High-level framework and user guides
    root_paths:
      - doc_id
      - docs
  
  adr.architecture:
    description: Architecture decision records
    root_paths:
      - adr
  
  config.global:
    description: Global configuration files
    root_paths:
      - config
  
  infra.ci:
    description: CI/CD infrastructure
    root_paths:
      - infra
      - .github/workflows
```

---

### Task 1.5.3: Dry-Run Assignment (15 min)

```bash
# Step 1: Run dry-run
python scripts/module_id_assigner.py --dry-run

# Step 2: Review report
cat doc_id/reports/MODULE_ID_ASSIGNMENT_DRY_RUN.md

# Step 3: Check for unassigned
cat doc_id/reports/MODULE_ID_UNASSIGNED.jsonl | wc -l

# Step 4: Review samples per module
cat doc_id/reports/MODULE_ID_ASSIGNMENT_DRY_RUN.md | grep -A 3 "Module:"
```

**Expected Output**:
```markdown
# Module ID Assignment Dry-Run Report

**Generated**: 2025-11-30

## Summary
- Total docs: 3,160
- Modules assigned: 12
- Unassigned: 47

## Distribution by Module

### core.engine (234 docs)
- DOC-CORE-ORCHESTRATOR-001
- DOC-CORE-SCHEDULER-002
- DOC-TEST-ENGINE-045
...

### docs.guides (178 docs)
- DOC-GUIDE-DOC-ID-FRAMEWORK-001
- DOC-GUIDE-AGENTS-106
...

### unassigned (47 docs)
- DOC-LEGACY-MODULE-001 (reason: no matching rule)
...
```

---

### Task 1.5.4: Apply Module ID Assignment (30 min)

```bash
# Step 1: Backup registry
cp doc_id/specs/DOC_ID_REGISTRY.yaml \
   doc_id/specs/DOC_ID_REGISTRY.backup.$(date +%Y%m%d_%H%M).yaml

# Step 2: Apply assignment
python scripts/module_id_assigner.py --apply

# Step 3: Validate registry
python doc_id/tools/doc_id_registry_cli.py validate

# Step 4: Check final stats
cat doc_id/reports/MODULE_ID_ASSIGNMENT_FINAL.json

# Step 5: Commit
git add doc_id/specs/DOC_ID_REGISTRY.yaml
git add doc_id/reports/MODULE_ID_*
git commit -m "feat: Add module_id to all docs in registry

- Assigned module_id to 3,160 docs
- 12 modules defined
- 47 docs marked as unassigned (pending review)
- Generated module taxonomy
- Reports: DRY_RUN, FINAL, UNASSIGNED"
```

---

### Task 1.5.5: Create Module Map (30 min)

**Script**: `scripts/build_module_map.py`

```python
#!/usr/bin/env python3
"""Build MODULE_DOC_MAP.yaml from DOC_ID_REGISTRY.yaml"""

import yaml
from datetime import datetime

def build_module_map(registry_path, output_path):
    with open(registry_path) as f:
        registry = yaml.safe_load(f)
    
    # Group docs by module_id
    modules = {}
    for doc in registry['docs']:
        module_id = doc.get('module_id', 'unassigned')
        if module_id not in modules:
            modules[module_id] = []
        
        # Extract minimal info for map
        modules[module_id].append({
            'doc_id': doc['doc_id'],
            'category': doc['category'],
            'kind': infer_kind(doc),
            'path': get_primary_path(doc)
        })
    
    # Build output structure
    module_map = {
        'metadata': {
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'source_registry': registry_path,
            'total_modules': len(modules),
            'total_docs': len(registry['docs'])
        },
        'modules': {}
    }
    
    # Add module descriptions from taxonomy
    for module_id, docs in sorted(modules.items()):
        module_map['modules'][module_id] = {
            'description': get_module_description(module_id, registry),
            'docs': docs
        }
    
    # Write output
    with open(output_path, 'w') as f:
        yaml.dump(module_map, f, default_flow_style=False, sort_keys=False)
```

**Usage**:
```bash
# Generate module map
python scripts/build_module_map.py

# Verify output
cat modules/MODULE_DOC_MAP.yaml | head -50

# Commit
git add modules/MODULE_DOC_MAP.yaml
git commit -m "feat: Create module-centric documentation map

- Generated from DOC_ID_REGISTRY.yaml
- 12 modules mapped
- 3,160 docs organized by module
- Enables module-centric refactoring"
```

---

### Task 1.5.6: Extend Registry CLI (Optional, 45 min)

Add two new commands to `doc_id/tools/doc_id_registry_cli.py`:

```python
@cli.command()
@click.option('--dry-run', is_flag=True)
@click.option('--apply', is_flag=True)
def module_assign(dry_run, apply):
    """Assign module_id to all docs in registry."""
    # Implementation calls module_id_assigner.py logic
    pass

@cli.command()
@click.option('--module-id', help='Filter to specific module')
def build_module_map(module_id):
    """Build MODULE_DOC_MAP.yaml from registry."""
    # Implementation calls build_module_map.py logic
    pass
```

**Usage**:
```bash
# New CLI commands
python doc_id/tools/doc_id_registry_cli.py module-assign --dry-run
python doc_id/tools/doc_id_registry_cli.py module-assign --apply
python doc_id/tools/doc_id_registry_cli.py build-module-map
python doc_id/tools/doc_id_registry_cli.py build-module-map --module-id core.engine
```

---

### Task 1.5.7: Final Validation (15 min)

```bash
# Validate all module_ids are assigned
python scripts/validate_module_ids.py

# Check taxonomy coverage
python scripts/check_module_taxonomy_coverage.py

# Generate summary
python scripts/module_id_summary.py > doc_id/reports/MODULE_ID_SUMMARY.md

# Final scan
python scripts/doc_id_scanner.py scan
python scripts/doc_id_scanner.py stats
```

---

## Phase 1.5 Success Criteria

- [ ] Every doc in registry has `module_id` field
- [ ] `module_taxonomy` section exists in registry
- [ ] MODULE_DOC_MAP.yaml created in `modules/`
- [ ] ≤ 5% docs marked as `unassigned`
- [ ] Registry validates with 0 errors
- [ ] All reports generated
- [ ] Changes committed to feature branch

---

## Execution Pattern for Phase 1.5

### Pattern Spec: `module_id_assignment.pattern.yaml`

```yaml
doc_id: "DOC-PAT-MODULE-ID-ASSIGNMENT-001"
pattern_id: "PAT-MODULE-ID-ASSIGNMENT-001"
name: "module_id_assignment"
version: "1.0.0"
category: "sequential"
status: "draft"

metadata:
  created: "2025-11-30"
  purpose: "Extend registry with module_id for all docs"
  related_docs:
    - "doc_id/MODULE_ID_EXTENSION_AND_MODULE_MAP_SPEC_V1.md"
    - "doc_id/COMPLETE_PHASE_PLAN.md"

intent: |
  Extend DOC_ID_REGISTRY.yaml with module_id field for every doc entry.
  Infer module ownership from paths and categories.
  Create module-centric mapping for future refactoring.

preconditions:
  - name: "Phase 0 complete"
    check: "python scripts/doc_id_scanner.py stats | grep '100.0%'"
  - name: "Registry valid"
    check: "python doc_id/tools/doc_id_registry_cli.py validate"

steps:
  - id: "step_1"
    name: "Create module_id_assigner.py"
    action: "create"
    # ... script content
    
  - id: "step_2"
    name: "Create module_taxonomy.yaml"
    action: "create"
    # ... taxonomy content
    
  - id: "step_3"
    name: "Dry-run assignment"
    command: "python scripts/module_id_assigner.py --dry-run"
    
  - id: "step_4"
    name: "Review unassigned docs"
    action: "manual_review"
    # ... review UNASSIGNED.jsonl
    
  - id: "step_5"
    name: "Apply assignment"
    command: "python scripts/module_id_assigner.py --apply"
    
  - id: "step_6"
    name: "Build module map"
    command: "python scripts/build_module_map.py"
    
  - id: "step_7"
    name: "Validate and commit"
    commands:
      - "python doc_id/tools/doc_id_registry_cli.py validate"
      - "git add doc_id/specs/ modules/ doc_id/reports/"
      - "git commit -m 'feat: Phase 1.5 - Module ID extension complete'"

postconditions:
  - name: "All docs have module_id"
    check: "python scripts/validate_module_ids.py"
  - name: "Module map exists"
    check: "test -f modules/MODULE_DOC_MAP.yaml"

estimated_time: "3 hours"
```

---

## Integration with Complete Phase Plan

### Updated Timeline

```
Phase 0 (Current)    ████████░░░░░░░░░░ 60%    3 hours remaining
                              ↓
Phase 1 (CI/CD)      ░░░░░░░░░░░░░░░░░░ 0%     2 hours
                              ↓
Phase 1.5 (Module)   ░░░░░░░░░░░░░░░░░░ 0%     3 hours  ← NEW
                              ↓
Phase 2 (Hardening)  ░░░░░░░░░░░░░░░░░░ 0%     2.5 hours
                              ↓
Phase 3.5 (Docs)     ░░░░░░░░░░░░░░░░░░ 0%     4 hours
```

**New Total Time**: 14.5 hours (was 11.5 hours)

---

## Benefits of Phase 1.5

### Immediate Benefits:
1. **Module ownership clarity** - Know which module owns each doc
2. **Module-centric queries** - `MODULE_DOC_MAP.yaml` enables filtering by module
3. **Refactor preparation** - Foundation for physical reorganization
4. **Test-source linkage** - Tests inherit module_id from source files

### Future Benefits:
1. **Automated refactoring** - Module map drives file moves
2. **Import path updates** - Module boundaries guide import rewrites
3. **Ownership tracking** - Clear responsibility per module
4. **Documentation generation** - Module-specific doc generation

---

## Recommendation

### ✅ **Integrate as Phase 1.5**

**Position**: Between Phase 1 (CI/CD) and Phase 2 (Hardening)

**Rationale**:
1. Builds on stable Phase 0 foundation (100% coverage)
2. Protected by Phase 1 CI/CD gates
3. Informs Phase 2 hardening decisions
4. Enables Phase 3.5 module-specific documentation

**Action Items**:
1. Update `COMPLETE_PHASE_PLAN.md` to include Phase 1.5
2. Create execution pattern `module_id_assignment.pattern.yaml`
3. Schedule Phase 1.5 after Phase 1 completion
4. Document dependencies in phase plan

---

## Summary

**MODULE_ID_EXTENSION_AND_MODULE_MAP_SPEC_V1.md** should be integrated as:

- **Phase 1.5** in the complete phase plan
- **3 hours** estimated time
- **7 tasks** with clear success criteria
- **Execution pattern** ready for automation
- **Positioned** between CI/CD (Phase 1) and Hardening (Phase 2)

This gives us a **complete 5-phase plan**:
- Phase 0: Universal Coverage (current)
- Phase 1: CI/CD Integration
- **Phase 1.5: Module ID Extension** ← NEW
- Phase 2: Production Hardening
- Phase 3.5: Documentation Consolidation

**Total Project Time**: 14.5 hours (1.8 workdays)
