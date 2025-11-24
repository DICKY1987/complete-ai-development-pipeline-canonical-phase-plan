# Pattern System Guide

**Version**: 1.0.0  
**Created**: 2025-11-24  
**Status**: Infrastructure Phase (Phase 0 Complete)

---

## Quick Start

This directory contains the **Universal Execution Templates (UET) Pattern System** - a library of pre-compiled, decision-eliminated execution patterns designed to achieve **3-5x speedup** through template-driven execution.

### For AI Tools

**Primary Entry Point**: `registry/PATTERN_INDEX.yaml`

```yaml
# Load pattern registry first
patterns:
  - pattern_id: PAT-ATOMIC-CREATE-001
    name: atomic_create
    spec_path: patterns/specs/atomic_create.pattern.yaml
    schema_path: patterns/schemas/atomic_create.schema.json
    executor_path: patterns/executors/atomic_create_executor.ps1
    # ... more metadata
```

### Pattern Invocation Workflow

1. **Load Registry**: Read `registry/PATTERN_INDEX.yaml`
2. **Select Pattern**: By `pattern_id` or `name`
3. **Read Spec**: Load pattern spec from `spec_path`
4. **Validate Instance**: Validate your instance against `schema_path`
5. **Execute**: Run executor at `executor_path` with instance
6. **Verify**: Check results against `ground_truth` criteria

---

## Directory Structure

```
patterns/
├── registry/                   # Single source of truth
│   ├── PATTERN_INDEX.yaml     # All patterns catalog
│   └── PATTERN_INDEX.schema.json
│
├── specs/                      # Pattern contracts (YAML)
│   └── <pattern_name>.pattern.yaml
│
├── schemas/                    # JSON Schema validators
│   └── <pattern_name>.schema.json
│
├── executors/                  # Deterministic runners
│   └── <pattern_name>_executor.(ps1|py)
│
├── examples/                   # Instance templates
│   └── <pattern_name>/
│       ├── instance_minimal.json
│       └── instance_full.json
│
├── tests/                      # Determinism enforcement
│   └── test_<pattern_name>_executor.*
│
├── verification/               # Ground truth validators
│   ├── preflight.verify.yaml
│   ├── pytest_green.verify.yaml
│   └── ...
│
├── decisions/                  # Pre-authorized decision trees
│   ├── worktree_creation.decisions.yaml
│   └── ...
│
├── self_healing/               # Auto-fix rules
│   ├── missing_directory.fix.yaml
│   └── ...
│
└── legacy_atoms/               # Migrated patterns
    ├── source/                 # Cloned repositories
    ├── converted/              # Generated patterns
    ├── reports/                # Migration documentation
    └── tools/                  # Legacy-specific helpers
```

---

## Pattern Naming Conventions

### Core Patterns (PAT-NAME-001)
- **Format**: `PAT-<CATEGORY>-<NAME>-<SEQ>`
- **Examples**: 
  - `PAT-ATOMIC-CREATE-001` (file creation)
  - `PAT-BATCH-CREATE-001` (bulk operations)
  - `PAT-WORKTREE-LIFECYCLE-001` (infrastructure)

### Migrated Patterns (PAT-NAME-002)
- **Format**: `PAT-MIGRATED-<CATEGORY>-<SEQ>`
- **Examples**:
  - `PAT-MIGRATED-CLI-001`
  - `PAT-MIGRATED-GITHUB-002`
- **Metadata Required**:
  - `migrated_from: atomic-workflow-system`
  - `original_atom_uid: <uid>`
  - `status: draft` (until tested)

---

## Available Patterns

### Core Patterns (Status: Planned)

**File Creation**:
- `atomic_create` - Create 1-3 files with tests (60% faster)
- `batch_create` - Create 6+ similar files (88% faster)

**Code Modification**:
- `refactor_patch` - Modify existing files with patches (70% faster)

**Error Recovery**:
- `self_heal` - Auto-fix common errors (90% faster, eliminates permissions)

**Verification**:
- `verify_commit` - Ground truth verification + git commit (85% faster)

**Infrastructure**:
- `worktree_lifecycle` - Git worktree management (75% faster, PH-04.5)

**Module Setup**:
- `module_creation` - Create module + tests + manifest (88% faster)

### Migrated Patterns (Status: Not Yet Migrated)

See `legacy_atoms/reports/EXTRACTION_REPORT.md` once migration complete.

---

## Usage Examples

### Example 1: Using atomic_create Pattern

```bash
# 1. Create instance file
cat > instance.json << 'EOF'
{
  "pattern_id": "PAT-ATOMIC-CREATE-001",
  "project_root": "C:\\MyProject",
  "files_to_create": [
    {
      "path": "src/utils/helper.py",
      "type": "implementation"
    },
    {
      "path": "tests/test_helper.py",
      "type": "test"
    }
  ]
}
EOF

# 2. Validate instance
python tools/pattern_tools.py validate-instance instance.json atomic_create

# 3. Execute pattern
powershell patterns/executors/atomic_create_executor.ps1 -InstancePath instance.json
```

### Example 2: AI Tool Invocation

```python
# From AI code execution context
from core.engine.pattern_loader import PatternLoader
from core.engine.pattern_executor import PatternExecutor

# Load pattern
loader = PatternLoader('patterns/registry/PATTERN_INDEX.yaml')
pattern = loader.load_pattern('PAT-ATOMIC-CREATE-001')

# Create instance
instance = {
    'pattern_id': 'PAT-ATOMIC-CREATE-001',
    'project_root': project_root,
    'files_to_create': [...]
}

# Execute
executor = PatternExecutor()
result = executor.execute(pattern, instance)

# Result contains:
# - status: 'success' | 'failed'
# - created_files: [...]
# - test_results: {...}
# - duration_seconds: 123
```

---

## Migrated Patterns from atomic-workflow-system

**Status**: Infrastructure ready, migration pending (Phase 5)

20+ proven patterns will be migrated from the atomic-workflow-system repository. These patterns are marked with `migrated_from: atomic-workflow-system` in their metadata.

See complete extraction procedure in:
`docs/planning/ATOMIC_WORKFLOW_EXTRACTION_PROMPT.md`

### Available Converter Tools

The following atom converter tools are ready in `tools/atoms/`:
- `md2atom.py` - Convert Markdown to atom/pattern
- `ps2atom.py` - Convert PowerShell to atom/pattern  
- `py2atom.py` - Convert Python to atom/pattern
- `simple2atom.py` - Convert simple JSON to atom/pattern
- `atom_validator.py` - Validate atom/pattern structure
- `id_utils.py` - ULID generation and validation

Usage:
```bash
# Convert Markdown file to pattern
python tools/atoms/md2atom.py my_workflow.md > pattern.json

# Validate pattern
python tools/atoms/atom_validator.py pattern.json
```

---

## Implementation Status

### Phase 0: Infrastructure Setup ✅ COMPLETE
- [x] Directory structure created (10 subdirectories)
- [x] README_PATTERNS.md created
- [x] Ready for Phase 1

### Phase 1: Pattern Registry Foundation (Next)
- [ ] Create PATTERN_INDEX.yaml with schema
- [ ] Create PATTERN_INDEX.schema.json
- [ ] Create validation script
- [ ] Document registry structure

### Phase 2: First Pattern (atomic_create)
- [ ] Extract from existing UET phases
- [ ] Create pattern spec
- [ ] Create schema
- [ ] Create executor
- [ ] Create tests
- [ ] Add to registry

### Phases 3-9: See Implementation Plan
Refer to: `docs/planning/UNIFIED_PATTERN_IMPLEMENTATION_PLAN.md`

---

## Performance Targets

- **Execution Time**: 60-75% reduction
- **Token Usage**: 94% reduction (80k → 5k tokens)
- **Human Interventions**: 95% reduction  
- **Automation**: 100% (zero permission prompts)
- **ROI**: 112% return after break-even (2.4 uses per pattern)

---

## Compliance

### Pattern Requirements (PAT-CHECK-001)
Every pattern **MUST** have:
1. Pattern spec (`.pattern.yaml`)
2. JSON schema (`.schema.json`)
3. Executor (`.ps1` or `.py`)
4. Tests (`test_*_executor.*`)
5. Examples (`instance_minimal.json`, `instance_full.json`)
6. Registry entry

### Migrated Pattern Exception (PAT-CHECK-002)
Migrated patterns:
- **MAY** use `PAT-MIGRATED-<CATEGORY>-<SEQ>` format
- **MUST** include `migrated_from` metadata
- **MUST** have `status: draft` until tested
- **SHOULD** be refactored to standard naming once validated

---

## Contributing Patterns

See: `docs/planning/UNIFIED_PATTERN_IMPLEMENTATION_PLAN.md` section "Phase 4: Template Extraction & Tools"

Quick summary:
1. Execute workstream successfully
2. Document decisions made
3. Run `scripts/extract_pattern_from_ws.py --ws-id <id> --run-id <id>`
4. Review generated pattern
5. Add tests
6. Submit for inclusion

---

## References

- **Implementation Plan**: `docs/planning/UNIFIED_PATTERN_IMPLEMENTATION_PLAN.md`
- **Extraction Guide**: `docs/planning/ATOMIC_WORKFLOW_EXTRACTION_PROMPT.md`
- **Pattern Theory**: `EVERYTHING_PATTERNS/decision-elimination-playbook.md`
- **Case Study**: `EVERYTHING_PATTERNS/Decision Elimination Through Pattern Recognition6.md`
- **Architecture Spec**: `EVERYTHING_PATTERNS/Every_reusable_pattern.md`

---

**Next Step**: Proceed to Phase 1 - Create pattern registry and validation infrastructure.
