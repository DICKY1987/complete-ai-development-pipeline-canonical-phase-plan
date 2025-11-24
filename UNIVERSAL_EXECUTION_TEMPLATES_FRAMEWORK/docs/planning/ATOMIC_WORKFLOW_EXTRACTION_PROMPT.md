# AI Agent: Extract Patterns from atomic-workflow-system

**Purpose**: Direct an agentic AI to extract proven patterns from the atomic-workflow-system repository and integrate them into the unified pattern system.

**Target Repository**: https://github.com/DICKY1987/atomic-workflow-system

**Estimated Time**: 3-4 hours

---

## Mission

Extract reusable workflow patterns from the atomic-workflow-system repository and convert them into the unified pattern format for integration into the UET framework.

---

## Phase 1: Repository Analysis (30 min)

### Step 1.1: Clone Repository
```bash
# Navigate to pattern workspace
cd patterns/legacy_atoms/

# Clone repository
git clone https://github.com/DICKY1987/atomic-workflow-system.git source/

# Explore structure
ls -R source/
```

### Step 1.2: Inventory Assets

Analyze these key files:
- `source/atoms.registry.jsonl` (534KB - contains ~1000+ atoms)
- `source/IMPLEMENTATION_SUMMARY.md` (system overview)
- `source/WORKFLOWS/README.md` (workflow catalog)
- `source/WORKFLOWS/WORKFLOW_CATALOG.md` (detailed workflows)

### Step 1.3: Identify High-Value Patterns

Focus on atoms with:
- **High reuse count** (used multiple times)
- **Clear role definitions** (well-documented purpose)
- **Well-defined inputs/outputs** (predictable interface)
- **Dependency declarations** (explicit dependencies)
- **Proven execution** (tested and working)

**Priority Categories**:
1. **CLI operations** (`source/atoms/cli/`)
2. **Core workflows** (`source/WORKFLOWS/core/`)
3. **GitHub integrations** (`source/WORKFLOWS/github/`)
4. **Validation workflows** (`source/WORKFLOWS/validation/`)
5. **Generator workflows** (`source/WORKFLOWS/generators/`)

### Deliverable 1.3: Create `analysis_report.md`

```markdown
# atomic-workflow-system Analysis Report

## Repository Statistics
- Total atoms in registry: [COUNT]
- Atoms with dependencies: [COUNT]
- Atoms with tests: [COUNT]
- Workflow categories: [LIST]

## High-Value Patterns Identified
1. **Pattern Name**: [NAME]
   - Atom UID: [UID]
   - Category: [CATEGORY]
   - Reuse count: [COUNT]
   - Complexity: [LOW|MED|HIGH]
   - Migration priority: [1-5]

[Repeat for top 20-30 patterns]

## Converter Tools Available
- `md2atom.py` - Markdown to atom
- `ps2atom.py` - PowerShell to atom
- `py2atom.py` - Python to atom
- `simple2atom.py` - JSON to atom
- `atom_validator.py` - Validation
- `id_utils.py` - ULID utilities

## Recommendations
[Migration strategy and priorities]
```

---

## Phase 2: Tool Migration (45 min)

### Step 2.1: Copy Converter Tools

```bash
# Create tools directory
mkdir -p tools/atoms/

# Copy converter suite
cp source/tools/atoms/*.py tools/atoms/

# Files to copy:
# - id_utils.py (ULID generation and validation)
# - atom_validator.py (Schema validation)
# - md2atom.py (Markdown converter)
# - ps2atom.py (PowerShell converter)
# - py2atom.py (Python converter)
# - simple2atom.py (JSON converter)
```

### Step 2.2: Test Converter Tools

```bash
# Install dependencies
pip install -r source/tools/requirements.txt

# Run tests
cd source/
pytest tests/ -v

# Expected: All 26 tests passing
```

### Step 2.3: Copy Schema Definition

```bash
# Copy atom schema
cp source/registry-template.json schema/atom.v1.json
```

### Deliverable 2.3: Verify tools work

```bash
# Test conversion
python tools/atoms/simple2atom.py source/examples/test.json > /tmp/test_atom.json
python tools/atoms/atom_validator.py /tmp/test_atom.json

# Should output: "✓ Valid atom"
```

---

## Phase 3: Pattern Extraction (90 min)

### Step 3.1: Create Extraction Script

Create `scripts/migrate_atoms_to_patterns.py`:

```python
#!/usr/bin/env python3
"""
Migrate atoms from atomic-workflow-system to unified patterns.

Usage:
    python scripts/migrate_atoms_to_patterns.py --registry source/atoms.registry.jsonl
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List
import yaml

def load_atom_registry(registry_path: str) -> List[Dict]:
    """Load atoms from JSONL registry"""
    atoms = []
    with open(registry_path) as f:
        for line in f:
            if line.strip():
                atoms.append(json.loads(line))
    return atoms

def calculate_priority(atom: Dict) -> int:
    """Calculate migration priority (1=highest, 5=lowest)"""
    priority = 3  # Default medium
    
    # High priority: Has dependencies (proves reuse)
    if atom.get('depends_on'):
        priority -= 1
    
    # High priority: Well-documented
    if len(atom.get('description', '')) > 100:
        priority -= 1
    
    # High priority: Has explicit inputs/outputs
    if atom.get('inputs') and atom.get('outputs'):
        priority -= 1
    
    # Low priority: Missing critical metadata
    if not atom.get('role'):
        priority += 1
    
    return max(1, min(5, priority))

def convert_atom_to_pattern(atom: Dict) -> Dict:
    """Convert atom format to pattern spec format"""
    
    # Extract atom_key components for pattern name
    atom_key = atom.get('atom_key', 'unknown/unknown/v1/ph0/ln0/000')
    name_part = atom_key.split('/')[-1].split('-')[0]  # Get seq part, remove variants
    
    pattern = {
        'pattern_id': f"PAT-MIGRATED-{atom['atom_uid'][:8].upper()}",
        'name': f"migrated_{name_part}",
        'version': '1.0.0',
        'category': atom.get('role', 'general'),
        
        'meta': {
            'migrated_from': 'atomic-workflow-system',
            'original_atom_uid': atom['atom_uid'],
            'original_atom_key': atom.get('atom_key'),
            'migration_date': '2025-11-24',
            'status': 'draft'  # Until tested
        },
        
        'intent': atom.get('description', 'Migrated from atomic-workflow-system'),
        
        'inputs': {
            inp: {'type': 'string', 'description': f'Input: {inp}'}
            for inp in atom.get('inputs', [])
        },
        
        'outputs': {
            out: {'type': 'string', 'description': f'Output: {out}'}
            for out in atom.get('outputs', [])
        },
        
        'dependencies': [
            {'pattern_id': f"PAT-MIGRATED-{dep[:8].upper()}"}
            for dep in atom.get('depends_on', [])
        ],
        
        'execution_steps': [
            {
                'id': 'execute_atom_logic',
                'description': 'Execute migrated atom logic',
                'note': 'TODO: Implement based on original atom behavior'
            }
        ],
        
        'tool_bindings': {
            'claude_code': {
                'invoke': f"pattern {pattern['name']} --instance ${{instance_path}}"
            }
        }
    }
    
    return pattern

def generate_pattern_schema(pattern: Dict) -> Dict:
    """Generate JSON schema for pattern"""
    
    input_properties = {
        name: {
            'type': meta.get('type', 'string'),
            'description': meta.get('description', '')
        }
        for name, meta in pattern.get('inputs', {}).items()
    }
    
    schema = {
        '$schema': 'http://json-schema.org/draft-07/schema#',
        'type': 'object',
        'required': ['pattern_id', 'inputs'],
        'properties': {
            'pattern_id': {
                'type': 'string',
                'pattern': '^PAT-MIGRATED-[A-Z0-9]{8}$'
            },
            'inputs': {
                'type': 'object',
                'properties': input_properties,
                'required': list(input_properties.keys())
            }
        }
    }
    
    return schema

def generate_executor_stub(pattern: Dict) -> str:
    """Generate Python executor stub"""
    
    executor = f'''#!/usr/bin/env python3
"""
Executor for {pattern['name']}

Migrated from atomic-workflow-system
Original atom UID: {pattern['meta']['original_atom_uid']}
Original atom key: {pattern['meta']['original_atom_key']}

Status: {pattern['meta']['status'].upper()}
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

def execute(instance: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute pattern instance.
    
    TODO: Implement execution logic based on original atom behavior.
    Review original atom at:
    https://github.com/DICKY1987/atomic-workflow-system
    """
    
    # Validate inputs
    required_inputs = {list(pattern.get('inputs', {}).keys())}
    for inp in required_inputs:
        if inp not in instance.get('inputs', {{}}):
            raise ValueError(f"Missing required input: {{inp}}")
    
    # TODO: Implement atom logic here
    print(f"Executing {pattern['name']}...")
    print(f"Inputs: {{json.dumps(instance['inputs'], indent=2)}}")
    
    # Placeholder result
    result = {{
        'status': 'success',
        'message': 'Pattern executed (stub implementation)',
        'migrated': True,
        'original_atom': '{pattern['meta']['original_atom_uid']}',
        'outputs': {{
            # TODO: Generate actual outputs
        }}
    }}
    
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: {pattern['name']}_executor.py <instance.json>")
        sys.exit(1)
    
    instance_path = sys.argv[1]
    
    with open(instance_path) as f:
        instance = json.load(f)
    
    result = execute(instance)
    
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
'''
    
    return executor

def save_pattern(pattern: Dict, output_dir: Path):
    """Save pattern spec, schema, and executor"""
    
    name = pattern['name']
    
    # Save spec
    spec_path = output_dir / 'specs' / f'{name}.pattern.yaml'
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    with open(spec_path, 'w') as f:
        yaml.dump(pattern, f, default_flow_style=False, sort_keys=False)
    
    # Save schema
    schema = generate_pattern_schema(pattern)
    schema_path = output_dir / 'schemas' / f'{name}.schema.json'
    schema_path.parent.mkdir(parents=True, exist_ok=True)
    with open(schema_path, 'w') as f:
        json.dump(schema, f, indent=2)
    
    # Save executor
    executor = generate_executor_stub(pattern)
    executor_path = output_dir / 'executors' / f'{name}_executor.py'
    executor_path.parent.mkdir(parents=True, exist_ok=True)
    with open(executor_path, 'w') as f:
        f.write(executor)
    executor_path.chmod(0o755)  # Make executable
    
    # Create examples directory
    examples_dir = output_dir / 'examples' / name
    examples_dir.mkdir(parents=True, exist_ok=True)
    
    # Create minimal instance example
    minimal_instance = {
        'pattern_id': pattern['pattern_id'],
        'inputs': {
            inp: f'<value_for_{inp}>'
            for inp in pattern.get('inputs', {}).keys()
        }
    }
    with open(examples_dir / 'instance_minimal.json', 'w') as f:
        json.dump(minimal_instance, f, indent=2)
    
    return {
        'spec': str(spec_path),
        'schema': str(schema_path),
        'executor': str(executor_path),
        'examples': str(examples_dir)
    }

def main():
    parser = argparse.ArgumentParser(description='Migrate atoms to patterns')
    parser.add_argument('--registry', required=True, help='Path to atoms.registry.jsonl')
    parser.add_argument('--output', default='patterns/legacy_atoms/converted', help='Output directory')
    parser.add_argument('--limit', type=int, default=20, help='Max patterns to migrate')
    parser.add_argument('--min-priority', type=int, default=3, help='Minimum priority (1-5)')
    
    args = parser.parse_args()
    
    # Load atoms
    print(f"Loading atoms from {args.registry}...")
    atoms = load_atom_registry(args.registry)
    print(f"Found {len(atoms)} atoms")
    
    # Calculate priorities
    print("Calculating migration priorities...")
    prioritized = [
        (calculate_priority(atom), atom)
        for atom in atoms
    ]
    prioritized.sort()  # Sort by priority (1=highest)
    
    # Filter by priority threshold
    to_migrate = [
        atom for priority, atom in prioritized
        if priority <= args.min_priority
    ][:args.limit]
    
    print(f"Migrating {len(to_migrate)} high-priority atoms...")
    
    # Convert and save
    output_dir = Path(args.output)
    migrated = []
    
    for atom in to_migrate:
        try:
            pattern = convert_atom_to_pattern(atom)
            paths = save_pattern(pattern, output_dir)
            
            migrated.append({
                'pattern_id': pattern['pattern_id'],
                'pattern_name': pattern['name'],
                'original_atom_uid': atom['atom_uid'],
                'original_atom_key': atom.get('atom_key'),
                'category': pattern['category'],
                'files': paths
            })
            
            print(f"  ✓ {pattern['name']} ({pattern['pattern_id']})")
        
        except Exception as e:
            print(f"  ✗ Failed to migrate {atom.get('atom_uid', 'unknown')}: {e}")
    
    # Save mapping
    mapping_path = output_dir / 'mapping.json'
    with open(mapping_path, 'w') as f:
        json.dump(migrated, f, indent=2)
    
    print(f"\nMigration complete!")
    print(f"  Patterns migrated: {len(migrated)}")
    print(f"  Mapping saved to: {mapping_path}")
    
    # Generate registry entries
    registry_entries = []
    for m in migrated:
        registry_entries.append({
            'pattern_id': m['pattern_id'],
            'name': m['pattern_name'],
            'version': '1.0.0',
            'status': 'draft',
            'category': m['category'],
            'spec_path': m['files']['spec'],
            'schema_path': m['files']['schema'],
            'executor_path': m['files']['executor'],
            'example_dir': m['files']['examples'],
            'migrated_from': 'atomic-workflow-system',
            'original_atom_uid': m['original_atom_uid']
        })
    
    registry_path = output_dir / 'PATTERN_INDEX_entries.yaml'
    with open(registry_path, 'w') as f:
        yaml.dump({'patterns': registry_entries}, f, default_flow_style=False)
    
    print(f"  Registry entries saved to: {registry_path}")
    print(f"\nNext steps:")
    print(f"  1. Review generated patterns in {output_dir}")
    print(f"  2. Implement executor logic (marked with TODO)")
    print(f"  3. Create tests for each pattern")
    print(f"  4. Merge registry entries into patterns/registry/PATTERN_INDEX.yaml")

if __name__ == '__main__':
    main()
```

### Step 3.2: Run Migration

```bash
# Migrate top 20 high-priority atoms
python scripts/migrate_atoms_to_patterns.py \
    --registry patterns/legacy_atoms/source/atoms.registry.jsonl \
    --output patterns/legacy_atoms/converted \
    --limit 20 \
    --min-priority 3

# Review output
ls -R patterns/legacy_atoms/converted/
```

### Deliverable 3.2: Migrated Patterns

Expected output structure:
```
patterns/legacy_atoms/converted/
├── specs/
│   ├── migrated_000.pattern.yaml
│   ├── migrated_001.pattern.yaml
│   └── ...
├── schemas/
│   ├── migrated_000.schema.json
│   ├── migrated_001.schema.json
│   └── ...
├── executors/
│   ├── migrated_000_executor.py
│   ├── migrated_001_executor.py
│   └── ...
├── examples/
│   ├── migrated_000/
│   │   └── instance_minimal.json
│   └── ...
├── mapping.json
└── PATTERN_INDEX_entries.yaml
```

---

## Phase 4: Workflow Extraction (60 min)

### Step 4.1: Analyze Workflow Compositions

Review these workflow directories:
- `source/WORKFLOWS/core/` - Core workflow patterns
- `source/WORKFLOWS/github/` - GitHub integration patterns
- `source/WORKFLOWS/validation/` - Validation patterns
- `source/WORKFLOWS/generators/` - Generator patterns

### Step 4.2: Extract Workflow Patterns

For complex workflows that compose multiple atoms, create workflow compositions:

```yaml
# patterns/compositions/github_pr_workflow.composition.yaml

composition_id: "COMP-GITHUB-PR-001"
name: "github_pr_workflow"
version: "1.0.0"
category: "github_integration"

description: |
  Complete GitHub PR workflow: create branch, make changes, run tests, create PR.
  
migrated_from: "atomic-workflow-system/WORKFLOWS/github/"

patterns_used:
  - pattern_id: "PAT-MIGRATED-<UID1>"
    step: "create_branch"
    
  - pattern_id: "PAT-MIGRATED-<UID2>"
    step: "apply_changes"
    
  - pattern_id: "PAT-MIGRATED-<UID3>"
    step: "run_tests"
    
  - pattern_id: "PAT-MIGRATED-<UID4>"
    step: "create_pr"

execution_flow:
  1_create_branch:
    pattern: "create_branch"
    inputs:
      base_branch: "${BASE_BRANCH}"
      new_branch: "${FEATURE_BRANCH}"
  
  2_apply_changes:
    pattern: "apply_changes"
    depends_on: "1_create_branch"
    inputs:
      files: "${FILES_TO_CHANGE}"
  
  3_run_tests:
    pattern: "run_tests"
    depends_on: "2_apply_changes"
    inputs:
      test_suite: "all"
  
  4_create_pr:
    pattern: "create_pr"
    depends_on: "3_run_tests"
    inputs:
      title: "${PR_TITLE}"
      body: "${PR_BODY}"
```

### Deliverable 4.2: Workflow Compositions

Create at least 5 high-value workflow compositions.

---

## Phase 5: Integration & Documentation (45 min)

### Step 5.1: Merge Registry Entries

```bash
# Append to main pattern registry
cat patterns/legacy_atoms/converted/PATTERN_INDEX_entries.yaml >> patterns/registry/PATTERN_INDEX.yaml

# Validate registry
python scripts/validate_pattern_registry.ps1
```

### Step 5.2: Create Extraction Report

Create `patterns/legacy_atoms/EXTRACTION_REPORT.md`:

```markdown
# atomic-workflow-system Extraction Report

**Date**: 2025-11-24  
**Source**: https://github.com/DICKY1987/atomic-workflow-system  
**Commit**: [SHA]

## Summary

- **Total atoms analyzed**: [COUNT]
- **Patterns extracted**: [COUNT]
- **Workflow compositions created**: [COUNT]
- **Converter tools migrated**: 6 tools

## Extracted Patterns

### High Priority (Priority 1-2)

1. **migrated_000** (`PAT-MIGRATED-XXXXXXXX`)
   - Original: `[atom_key]`
   - Category: [category]
   - Status: Draft - needs implementation
   - Complexity: [LOW|MED|HIGH]

[List all patterns]

## Workflow Compositions

1. **github_pr_workflow** (`COMP-GITHUB-PR-001`)
   - Composes: 4 patterns
   - Purpose: Complete GitHub PR creation flow

[List all compositions]

## Converter Tools Migrated

1. **id_utils.py** - ULID generation (26 tests passing)
2. **atom_validator.py** - Schema validation (tests passing)
3. **md2atom.py** - Markdown converter (3 tests passing)
4. **ps2atom.py** - PowerShell converter (4 tests passing)
5. **py2atom.py** - Python converter (4 tests passing)
6. **simple2atom.py** - JSON converter (3 tests passing)

**Total test coverage**: 22 unit tests + 4 system tests = 26 tests ✓

## Implementation Status

### Complete ✓
- [x] Pattern specs generated
- [x] Schemas generated
- [x] Executor stubs created
- [x] Example instances created
- [x] Registry entries created
- [x] Converter tools copied

### TODO ⚠️
- [ ] Implement executor logic (marked with TODO comments)
- [ ] Create tests for each pattern
- [ ] Validate patterns work end-to-end
- [ ] Update pattern status from 'draft' to 'active'
- [ ] Create documentation for each pattern

## Recommendations

### Immediate Actions
1. Review generated patterns in `patterns/legacy_atoms/converted/`
2. Prioritize implementing executors for top 5 patterns
3. Create tests following the pattern test template
4. Validate migrated patterns work with UET orchestrator

### Long-term Actions
1. Consider creating meta-patterns for common atom combinations
2. Build pattern composition engine for workflows
3. Create converter tools for other formats (YAML, etc.)
4. Establish pattern contribution guidelines

## Mapping

Complete atom UID → pattern ID mapping available in:
`patterns/legacy_atoms/converted/mapping.json`

## Issues Encountered

[Document any problems during extraction]

## Lessons Learned

[Document insights for future migrations]
```

### Step 5.3: Update Main Documentation

Add section to `patterns/README_PATTERNS.md`:

```markdown
## Migrated Patterns from atomic-workflow-system

20+ proven patterns have been migrated from the atomic-workflow-system 
repository. These patterns are marked with `migrated_from: atomic-workflow-system`
in their metadata.

**Status**: Draft (requires implementation and testing)

See `legacy_atoms/EXTRACTION_REPORT.md` for complete migration details.

### Available Converter Tools

The following atom converter tools are available in `tools/atoms/`:
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
```

---

## Success Criteria

**Phase 1 Complete**:
- [ ] Repository cloned
- [ ] Analysis report created
- [ ] High-value patterns identified (20+)

**Phase 2 Complete**:
- [ ] 6 converter tools copied to `tools/atoms/`
- [ ] Tools tested (26 tests passing)
- [ ] Atom schema copied to `schema/atom.v1.json`

**Phase 3 Complete**:
- [ ] Migration script created and working
- [ ] 20+ patterns extracted
- [ ] Pattern specs, schemas, executors generated
- [ ] Example instances created
- [ ] Mapping file created

**Phase 4 Complete**:
- [ ] 5+ workflow compositions created
- [ ] Compositions documented

**Phase 5 Complete**:
- [ ] Registry entries merged
- [ ] Extraction report complete
- [ ] Documentation updated
- [ ] Ready for implementation phase

---

## Deliverables Checklist

Files to create:
- [ ] `patterns/legacy_atoms/source/` (cloned repo)
- [ ] `patterns/legacy_atoms/analysis_report.md`
- [ ] `tools/atoms/*.py` (6 converter tools)
- [ ] `schema/atom.v1.json`
- [ ] `scripts/migrate_atoms_to_patterns.py`
- [ ] `patterns/legacy_atoms/converted/specs/*.pattern.yaml` (20+ files)
- [ ] `patterns/legacy_atoms/converted/schemas/*.schema.json` (20+ files)
- [ ] `patterns/legacy_atoms/converted/executors/*_executor.py` (20+ files)
- [ ] `patterns/legacy_atoms/converted/examples/*/instance_minimal.json` (20+ files)
- [ ] `patterns/legacy_atoms/converted/mapping.json`
- [ ] `patterns/legacy_atoms/converted/PATTERN_INDEX_entries.yaml`
- [ ] `patterns/compositions/*.composition.yaml` (5+ files)
- [ ] `patterns/legacy_atoms/EXTRACTION_REPORT.md`
- [ ] Updated `patterns/README_PATTERNS.md`
- [ ] Updated `patterns/registry/PATTERN_INDEX.yaml`

---

## Next Steps After Extraction

Once extraction is complete:

1. **Implementation Phase**: Implement executor logic for top 5 patterns
2. **Testing Phase**: Create tests for each implemented pattern
3. **Validation Phase**: Run patterns through UET orchestrator
4. **Documentation Phase**: Create usage docs for each pattern
5. **Activation Phase**: Change status from 'draft' to 'active'

---

## Notes

- Focus on quality over quantity (20 proven patterns > 100 untested)
- Preserve original atom UIDs for traceability
- Mark all migrated patterns as "draft" until fully tested
- Document any assumptions or missing information
- The migration script is idempotent (safe to re-run)

**Estimated Total Time**: 3-4 hours for complete extraction
