# Unified Pattern Implementation Plan
## Decision Elimination via Pattern System Architecture

**Created**: 2025-11-24  
**Unified From**:
- `TEMPLATE_IMPLEMENTATION_PLAN.md` (Template-driven execution)
- `complete pattern solution.txt` (4-component pattern architecture)
- `atomic-workflow-system` repository (Proven atom/workflow patterns)

**Objective**: Implement a unified pattern-based execution system to achieve **3-5x speedup** through decision elimination.

---

## Executive Summary

### The Problem (Current State)
```
Phase Execution Time Breakdown:
├─ Load spec: 30 sec (300+ lines)
├─ Analyze dependencies: 60 sec
├─ Design structure: 120 sec
├─ Plan verification: 180 sec
├─ Create execution plan: 120 sec
├─ Ask permissions: 90 sec (3× 30 sec)
├─ Execute: 7200 sec (2 hours)
├─ Manual verify: 150 sec (5× 30 sec)
└─ Total: ~8000 sec (133 minutes)

Token consumption: ~80k tokens
Human interventions: 3+ permission requests
```

### The Solution (Pattern-Driven)
```
Phase Execution Time Breakdown:
├─ Load pattern from registry: 1 sec
├─ Fill context variables: 2 sec
├─ Validate against schema: 2 sec
├─ Pre-flight verify: 5 sec (programmatic)
├─ Execute pattern steps: 2700 sec (45 minutes)
├─ Auto-verify: 10 sec (programmatic)
└─ Total: ~2720 sec (45 minutes)

Token consumption: ~5k tokens (94% reduction)
Human interventions: 0 (pre-authorized)
```

**Speedup**: 2.96x faster (133 min → 45 min)  
**Token Savings**: 94% reduction  
**Automation**: 100% (zero human intervention)

---

## Architecture Overview

### Unified Directory Structure

```
UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/
├── patterns/                            # NEW: Unified pattern system
│   ├── registry/                        # Single source of truth
│   │   ├── PATTERN_INDEX.yaml          # All patterns catalog
│   │   ├── PATTERN_INDEX.schema.json   # Registry validation
│   │   └── atoms.registry.jsonl        # Legacy: Atomic workflow atoms (from old repo)
│   │
│   ├── specs/                           # Pattern contracts (RFC 2119)
│   │   ├── atomic_create.pattern.yaml
│   │   ├── batch_create.pattern.yaml
│   │   ├── refactor_patch.pattern.yaml
│   │   ├── self_heal.pattern.yaml
│   │   ├── verify_commit.pattern.yaml
│   │   ├── worktree_lifecycle.pattern.yaml
│   │   └── module_creation.pattern.yaml
│   │
│   ├── schemas/                         # Rigid validators
│   │   ├── atomic_create.schema.json
│   │   ├── batch_create.schema.json
│   │   ├── refactor_patch.schema.json
│   │   ├── self_heal.schema.json
│   │   ├── verify_commit.schema.json
│   │   ├── worktree_lifecycle.schema.json
│   │   └── module_creation.schema.json
│   │
│   ├── executors/                       # Deterministic runners
│   │   ├── atomic_create_executor.ps1
│   │   ├── batch_create_executor.ps1
│   │   ├── refactor_patch_executor.ps1
│   │   ├── self_heal_executor.py
│   │   ├── verify_commit_executor.ps1
│   │   ├── worktree_lifecycle_executor.py
│   │   └── module_creation_executor.py
│   │
│   ├── examples/                        # Instance templates
│   │   ├── atomic_create/
│   │   │   ├── instance_minimal.json
│   │   │   └── instance_full.json
│   │   ├── batch_create/
│   │   │   ├── instance_minimal.json
│   │   │   └── instance_full.json
│   │   └── [pattern_name]/
│   │       ├── instance_minimal.json
│   │       └── instance_full.json
│   │
│   ├── tests/                           # Determinism enforcement
│   │   ├── test_atomic_create_executor.ps1
│   │   ├── test_batch_create_executor.ps1
│   │   ├── test_refactor_patch_executor.ps1
│   │   ├── test_self_heal_executor.py
│   │   ├── test_verify_commit_executor.ps1
│   │   ├── test_worktree_lifecycle_executor.py
│   │   └── test_module_creation_executor.py
│   │
│   ├── verification/                    # Ground truth validators
│   │   ├── preflight.verify.yaml
│   │   ├── pytest_green.verify.yaml
│   │   ├── git_clean.verify.yaml
│   │   ├── scope_valid.verify.yaml
│   │   ├── file_exists.verify.yaml
│   │   └── import_valid.verify.yaml
│   │
│   ├── decisions/                       # Pre-authorized decision trees
│   │   ├── worktree_creation.decisions.yaml
│   │   ├── scope_validation.decisions.yaml
│   │   ├── self_healing.decisions.yaml
│   │   ├── test_coverage.decisions.yaml
│   │   └── code_style.decisions.yaml
│   │
│   ├── self_healing/                    # Auto-fix rules
│   │   ├── missing_directory.fix.yaml
│   │   ├── missing_import.fix.yaml
│   │   ├── syntax_error.fix.yaml
│   │   ├── test_failure.fix.yaml
│   │   └── import_cycle.fix.yaml
│   │
│   ├── legacy_atoms/                    # Migrated from atomic-workflow-system
│   │   ├── source/                      # Raw cloned repositories
│   │   ├── converted/                   # Generated patterns
│   │   │   ├── specs/                   # Migrated pattern specs
│   │   │   ├── schemas/                 # Migrated schemas
│   │   │   ├── executors/               # Migrated executors
│   │   │   ├── examples/                # Migrated examples
│   │   │   ├── mapping.json             # Atom UID → Pattern ID mapping
│   │   │   └── registry_entries.yaml    # Entries to merge (bare list)
│   │   ├── reports/                     # Migration documentation
│   │   │   ├── analysis_report.md       # Pre-migration analysis
│   │   │   └── EXTRACTION_REPORT.md     # Post-migration summary
│   │   └── tools/                       # Legacy-specific helpers
│   │
│   └── README_PATTERNS.md               # AI usage guide
│
├── core/
│   └── engine/
│       ├── pattern_loader.py            # NEW: Load patterns from registry
│       ├── pattern_executor.py          # NEW: Execute pattern instances
│       ├── pattern_validator.py         # NEW: Schema validation
│       ├── verification_engine.py       # NEW: Programmatic verification
│       ├── template_extractor.py        # NEW: Extract templates from runs
│       └── orchestrator.py              # UPDATED: Use patterns
│
├── tools/
│   ├── atoms/                           # Migrated from atomic-workflow-system
│   │   ├── id_utils.py                  # ULID generation
│   │   ├── atom_validator.py            # Atom validation
│   │   ├── md2atom.py                   # Markdown → Atom converter
│   │   ├── ps2atom.py                   # PowerShell → Atom converter
│   │   ├── py2atom.py                   # Python → Atom converter
│   │   └── simple2atom.py               # JSON → Atom converter
│   │
│   └── pattern_tools.py                 # NEW: Pattern management CLI
│
├── scripts/
│   ├── validate_pattern_registry.ps1    # NEW: Registry compliance checker
│   ├── check_pattern_compliance.ps1     # NEW: PAT-CHECK-001 validator
│   ├── extract_pattern_from_ws.py       # NEW: Auto-extract from workstream
│   └── migrate_atoms_to_patterns.py     # NEW: Convert atoms to patterns
│
└── schema/
    ├── phase_template.v1.json           # Template schema
    ├── execution_pattern.v1.json        # Pattern schema
    ├── verification_template.v1.json    # Verification schema
    └── atom.v1.json                     # Atom schema (from old repo)
```

---

## Pattern System Architecture

### The 4-Component Pattern Structure

Every reusable pattern MUST have:

#### 1. Pattern Spec (.pattern.yaml) - The Contract
**Location**: `patterns/specs/<pattern_name>.pattern.yaml`

**Contains**:
- `pattern_id` (stable ID, e.g., `PAT-ATOMIC-CREATE-001`)
- `name`, `version` (semantic versioning)
- `intent` / `applicability` (when to use)
- `inputs` + `outputs` (with types)
- `constraints` / guardrails
- `steps` → high-level A → B → C flow
- `tool_bindings` (claude_code, github_copilot_cli, etc.)
- `structural_decisions` (pre-made choices)
- `variable_sections` (what gets filled at runtime)

**Purpose**: The rigid contract + deterministic flow definition.

#### 2. Pattern Schema (.schema.json) - The Validator
**Location**: `patterns/schemas/<pattern_name>.schema.json`

**Enforces**:
- Required fields / types for inputs/params
- Allowed enum values
- Structure of steps and tool_bindings
- Version compatibility
- **Rule**: "If it doesn't validate, reject execution"

**Purpose**: Programmatic validation before execution.

#### 3. Pattern Executor (_executor.ps1|.py) - The Runner
**Location**: `patterns/executors/<pattern_name>_executor.*`

**Responsibilities**:
- Read pattern instance (e.g., `workstreams/ws-123/pattern_instance.json`)
- Validate against schema
- Execute steps from spec
- Call concrete scripts/tools
- Emit structured logs + result JSON
- Handle self-healing if enabled

**Purpose**: Deterministic execution ("If PATTERN_X, run steps A → B → C").

#### 4. Pattern Tests (test_*.ps1|.py) - The Guardrail
**Location**: `patterns/tests/test_<pattern_name>_executor.*`

**Validates**:
- Same input → same output (determinism)
- Failures on bad params
- Smoke tests for all steps
- Self-healing behavior

**Purpose**: Enforce trustworthy re-use.

---

### Global Pattern Index

**Single shared file**: `patterns/registry/PATTERN_INDEX.yaml`

**Structure**:
```yaml
version: "1.0.0"
patterns:
  - pattern_id: PAT-ATOMIC-CREATE-001
    name: atomic_create
    version: "1.0.0"
    status: active          # draft | active | deprecated
    category: file_creation
    spec_path: patterns/specs/atomic_create.pattern.yaml
    schema_path: patterns/schemas/atomic_create.schema.json
    executor_path: patterns/executors/atomic_create_executor.ps1
    test_path: patterns/tests/test_atomic_create_executor.ps1
    example_dir: patterns/examples/atomic_create/
    tool_targets:
      - claude_code
      - github_copilot_cli
    time_savings_vs_manual: "60%"
    proven_uses: 12
    
  - pattern_id: PAT-BATCH-CREATE-001
    name: batch_create
    version: "1.0.0"
    status: active
    category: file_creation
    spec_path: patterns/specs/batch_create.pattern.yaml
    schema_path: patterns/schemas/batch_create.schema.json
    executor_path: patterns/executors/batch_create_executor.ps1
    test_path: patterns/tests/test_batch_create_executor.ps1
    example_dir: patterns/examples/batch_create/
    tool_targets:
      - claude_code
    time_savings_vs_manual: "88%"
    proven_uses: 17
```

**Purpose**: Single source of truth for all patterns. AI tools read this first.

---

## Implementation Phases

### PHASE 0: Infrastructure Setup (30 min)

**Pattern**: Infrastructure First

**Deliverables**:
1. Create `patterns/` root directory
2. Create 9 subdirectories:
   - `registry/`
   - `specs/`
   - `schemas/`
   - `executors/`
   - `examples/`
   - `tests/`
   - `verification/`
   - `decisions/`
   - `self_healing/`
   - `legacy_atoms/`
3. Create placeholder `README_PATTERNS.md`

**Success Criteria**:
- [ ] All directories exist
- [ ] Structure matches specification
- [ ] No files yet, just structure

**Files Created**: 10 directories, 1 README

---

### PHASE 1: Pattern Registry Foundation (45 min)

**Pattern**: Template-Based Creation

**Deliverables**:
1. `patterns/registry/PATTERN_INDEX.yaml` with schema definition
2. `patterns/registry/PATTERN_INDEX.schema.json` for validation
3. Comprehensive `README_PATTERNS.md` for AI tools
4. `scripts/validate_pattern_registry.ps1` validation script

**Success Criteria**:
- [ ] PATTERN_INDEX.yaml is valid YAML
- [ ] README explains: where to start, how to add pattern, how to invoke
- [ ] Validation script checks registry compliance
- [ ] Follows naming conventions (PAT-INDEX-001 through PAT-INDEX-012)

**Files Created**: 4 files

---

### PHASE 2A: First Pattern - Atomic Create (Spec & Schema) (60 min)

**Pattern**: Template Extraction

**Deliverables**:
1. Extract decisions from completed UET phases (e.g., PH-04.5)
2. `patterns/specs/atomic_create.pattern.yaml`
3. `patterns/schemas/atomic_create.schema.json`
4. Example instances:
   - `patterns/examples/atomic_create/instance_minimal.json`
   - `patterns/examples/atomic_create/instance_full.json`

**Spec Contents**:
```yaml
# Pattern: Atomic Create
# USE_CASE: Creating 1-3 files with tests
# TIME_SAVINGS: 60% (30 min -> 12 min)

pattern_id: "PAT-ATOMIC-CREATE-001"
name: "atomic_create"
version: "1.0.0"
category: "file_creation"

intent: |
  Create 1-3 implementation files with corresponding tests.
  Used when adding small, isolated functionality.

applicability:
  max_files: 3
  always_include_tests: true
  test_ratio: "1 test file per implementation file"

inputs:
  files_to_create:
    type: "array"
    items:
      path: "string"
      type: "enum[implementation, test]"
      content_template: "string (optional)"
  project_root:
    type: "string"
    required: true

outputs:
  created_files:
    type: "array"
    items: "string (file paths)"
  test_results:
    type: "object"
    fields: [passed, failed, duration]

structural_decisions:
  max_files_per_phase: 3
  always_include_tests: true
  approach: "complete_file_in_one_turn"
  no_placeholders: true
  include_docstrings: true
  include_type_hints: true

execution_steps:
  - id: "verify_parent_dirs"
    checks:
      - "Parent directories exist"
      - "No conflicting files"
    on_fail: "create_parents_auto"
  
  - id: "create_files"
    strategy: "sequential"
    order: ["implementation_files", "test_files"]
  
  - id: "verify_creation"
    checks:
      - cmd: "Test-Path ${file_path}"
        for_each: "created_files"
      - cmd: "python -m py_compile ${file_path}"
        for_each: "python_files"
  
  - id: "run_tests"
    cmd: "python -m pytest ${test_file} -v"
    expect: ".*passed.*0 failed.*"
    on_fail: "enter_fix_loop"
  
  - id: "git_status"
    cmd: "git status --porcelain"
    expect_count: "${created_files.length}"

ground_truth:
  success_criteria:
    - "All files exist"
    - "All files compile/parse"
    - "All tests pass"
    - "Git status shows only expected new files"

tool_bindings:
  claude_code:
    invoke: "pattern atomic_create --instance ${instance_path}"
  github_copilot_cli:
    invoke: "gh copilot pattern atomic_create ${instance_path}"
```

**Success Criteria**:
- [ ] Spec includes all required fields
- [ ] Schema validates both example instances
- [ ] Follows PAT-SPEC-001 through PAT-SPEC-004
- [ ] Follows PAT-SCHEMA-001 through PAT-SCHEMA-004

**Files Created**: 4 files

---

### PHASE 2B: First Pattern - Atomic Create (Executor & Tests) (90 min)

**Pattern**: Atomic Creation + Self-Healing

**Deliverables**:
1. `patterns/executors/atomic_create_executor.ps1`
2. Implements: Read instance → Validate → Execute → Emit logs
3. `patterns/tests/test_atomic_create_executor.ps1`
4. Add entry to `PATTERN_INDEX.yaml`

**Executor Implementation**:
```powershell
# patterns/executors/atomic_create_executor.ps1

param(
    [Parameter(Mandatory=$true)]
    [string]$InstancePath
)

$ErrorActionPreference = "Stop"

# Load pattern spec
$specPath = "patterns/specs/atomic_create.pattern.yaml"
$spec = ConvertFrom-Yaml (Get-Content $specPath -Raw)

# Load instance
$instance = Get-Content $InstancePath | ConvertFrom-Json

# Validate against schema
$schemaPath = "patterns/schemas/atomic_create.schema.json"
if (-not (Test-JsonSchema -Instance $instance -SchemaPath $schemaPath)) {
    throw "Instance validation failed"
}

# Execute steps
foreach ($step in $spec.execution_steps) {
    Write-StructuredLog -Event "step_start" -StepId $step.id
    
    switch ($step.id) {
        "verify_parent_dirs" {
            # Implementation
        }
        "create_files" {
            # Implementation
        }
        "verify_creation" {
            # Implementation
        }
        "run_tests" {
            # Implementation
        }
        "git_status" {
            # Implementation
        }
    }
    
    Write-StructuredLog -Event "step_complete" -StepId $step.id
}

# Emit result
$result = @{
    status = "success"
    created_files = $createdFiles
    test_results = $testResults
    duration_seconds = (Get-Date) - $startTime
}

$result | ConvertTo-Json -Depth 10 | Out-File "result.json"
```

**Test Implementation**:
```powershell
# patterns/tests/test_atomic_create_executor.ps1

Describe "Atomic Create Executor" {
    It "Should create files from minimal instance" {
        $result = & patterns/executors/atomic_create_executor.ps1 `
            -InstancePath patterns/examples/atomic_create/instance_minimal.json
        
        $result.status | Should -Be "success"
        $result.created_files | Should -HaveCount 2
    }
    
    It "Should enforce determinism (same input = same output)" {
        # Run twice with same input
        $result1 = & patterns/executors/atomic_create_executor.ps1 `
            -InstancePath patterns/examples/atomic_create/instance_minimal.json
        
        $result2 = & patterns/executors/atomic_create_executor.ps1 `
            -InstancePath patterns/examples/atomic_create/instance_minimal.json
        
        $result1.created_files | Should -Be $result2.created_files
    }
    
    It "Should fail on invalid instance" {
        { & patterns/executors/atomic_create_executor.ps1 `
            -InstancePath patterns/examples/atomic_create/invalid.json
        } | Should -Throw "validation failed"
    }
}
```

**Success Criteria**:
- [ ] Executor runs both example instances successfully
- [ ] Tests verify determinism
- [ ] Tests verify failure handling
- [ ] Pattern listed in PATTERN_INDEX.yaml
- [ ] Follows PAT-EXEC-001 through PAT-EXEC-004

**Files Created**: 2 files, 1 updated

---

### PHASE 3: Core Pattern Library (4-6 hours)

**Pattern**: Batch Production

**Deliverables**: 6 additional patterns (7 total)

For each pattern:
- Spec: `patterns/specs/<name>.pattern.yaml`
- Schema: `patterns/schemas/<name>.schema.json`
- Executor: `patterns/executors/<name>_executor.*`
- Examples: `patterns/examples/<name>/instance_{minimal,full}.json`
- Tests: `patterns/tests/test_<name>_executor.*`
- Index entry in `PATTERN_INDEX.yaml`

**Patterns to Create**:

1. **batch_create** - Create 6+ similar files at once
   - Category: file_creation
   - Time savings: 88% (from 17 manifests case study)
   - Based on: "Decision Elimination Through Pattern Recognition"

2. **refactor_patch** - Modify existing files with patches
   - Category: code_modification
   - Time savings: 70%
   - Self-healing enabled

3. **self_heal** - Auto-fix common errors (pre-authorized)
   - Category: error_recovery
   - Time savings: 90% (eliminates permission bottlenecks)
   - Includes rules from `patterns/self_healing/*.fix.yaml`

4. **verify_commit** - Ground truth verification + git commit
   - Category: verification
   - Time savings: 85%
   - Uses verifications from `patterns/verification/*.verify.yaml`

5. **worktree_lifecycle** - Git worktree management (PH-04.5)
   - Category: infrastructure
   - Time savings: 75% (3 hours → 45 min)
   - Based on actual UET requirements

6. **module_creation** - Create module + tests + manifest
   - Category: module_setup
   - Time savings: 88% (42 min → 5 min)
   - Based on 17 manifests case study

**Success Criteria**:
- [ ] All 6 patterns follow naming conventions (PAT-NAME-001 to PAT-NAME-003)
- [ ] All tests pass (determinism verified)
- [ ] All patterns registered in PATTERN_INDEX.yaml
- [ ] Each pattern has working examples

**Files Created**: 36 files (6 per pattern × 6), 6 updates to index

---

### PHASE 4: Verification & Decision Templates (2 hours)

**Pattern**: Ground Truth + Pre-Authorization

**Deliverables**:

#### Verification Templates (6 files):

1. `patterns/verification/preflight.verify.yaml`
   - Pre-flight environment checks
   - Prevents 15-30 min debugging sessions

2. `patterns/verification/pytest_green.verify.yaml`
   - All tests pass verification
   - 30 sec → 2 sec per check

3. `patterns/verification/git_clean.verify.yaml`
   - Clean working directory check

4. `patterns/verification/scope_valid.verify.yaml`
   - Scope violation detection
   - Security enforcement

5. `patterns/verification/file_exists.verify.yaml`
   - File existence checks

6. `patterns/verification/import_valid.verify.yaml`
   - Import path validation

#### Decision Templates (5 files):

1. `patterns/decisions/worktree_creation.decisions.yaml`
   - Pre-authorized worktree decisions

2. `patterns/decisions/scope_validation.decisions.yaml`
   - Scope checking rules

3. `patterns/decisions/self_healing.decisions.yaml`
   - Auto-fix decision tree

4. `patterns/decisions/test_coverage.decisions.yaml`
   - Test requirements

5. `patterns/decisions/code_style.decisions.yaml`
   - Code formatting rules

#### Self-Healing Rules (5 files):

1. `patterns/self_healing/missing_directory.fix.yaml`
2. `patterns/self_healing/missing_import.fix.yaml`
3. `patterns/self_healing/syntax_error.fix.yaml`
4. `patterns/self_healing/test_failure.fix.yaml`
5. `patterns/self_healing/import_cycle.fix.yaml`

**Success Criteria**:
- [ ] All verification templates have programmatic checks
- [ ] All decision templates have clear pre-authorization rules
- [ ] Self-healing rules have max_attempts limits
- [ ] Integration tests verify template usage

**Files Created**: 16 files

---

### PHASE 5: Migration from atomic-workflow-system (3 hours)

**Pattern**: Legacy Integration

**Objective**: Migrate proven atoms from old repository into new pattern system.

**Deliverables**:

1. **Download atomic-workflow-system patterns**:
   ```bash
   # Create migration workspace
   mkdir -p patterns/legacy_atoms/source
   cd patterns/legacy_atoms/source
   
   # Clone repo
   git clone https://github.com/DICKY1987/atomic-workflow-system.git
   ```

2. **Migrate converter tools**:
   - Copy `tools/atoms/*.py` to `tools/atoms/`
   - Files: `id_utils.py`, `atom_validator.py`, `md2atom.py`, `ps2atom.py`, `py2atom.py`, `simple2atom.py`

3. **Convert atoms to patterns** using `scripts/migrate_atoms_to_patterns.py`:
   ```python
   # scripts/migrate_atoms_to_patterns.py
   
   def convert_atom_to_pattern(atom_jsonl_entry):
       """Convert old atom format to new pattern format"""
       atom = json.loads(atom_jsonl_entry)
       
       pattern = {
           'pattern_id': f"PAT-MIGRATED-{atom['atom_uid'][:8]}",
           'name': atom.get('atom_key', 'unknown').split('/')[-1],
           'version': '1.0.0',
           'category': atom.get('role', 'general'),
           'intent': atom.get('description', ''),
           'inputs': atom.get('inputs', []),
           'outputs': atom.get('outputs', []),
           'dependencies': atom.get('depends_on', []),
           'migrated_from': 'atomic-workflow-system',
           'original_atom_uid': atom['atom_uid']
       }
       
       return pattern
   ```

4. **Create pattern specs from atoms**:
   - Parse `atoms.registry.jsonl` (534KB, ~1000+ atoms)
   - Convert to pattern specs
   - Generate schemas
   - Create minimal executors

5. **Integrate workflows**:
   - Review `WORKFLOWS/` directory structure
   - Map workflows to pattern compositions
   - Create high-level workflow patterns

**Patterns to Extract** (High-Value):
- CLI atoms (from `atoms/cli/`)
- Core workflow atoms (from `WORKFLOWS/core/`)
- GitHub integration atoms (from `WORKFLOWS/github/`)
- Validation atoms (from `WORKFLOWS/validation/`)

**Success Criteria**:
- [ ] Converter tools integrated into `tools/atoms/`
- [ ] At least 20 high-value atoms converted to patterns
- [ ] All converted patterns validate against schemas
- [ ] Migration script tested and documented
- [ ] Migrated patterns added to PATTERN_INDEX.yaml

**Files Created**: ~25+ patterns, 1 migration script, converter tools

---

### PHASE 6: UET Orchestrator Integration (2-3 hours)

**Pattern**: Integration + Self-Healing

**Deliverables**:

1. **Pattern Loader**: `core/engine/pattern_loader.py`
   ```python
   class PatternLoader:
       """Load patterns from PATTERN_INDEX.yaml"""
       
       def __init__(self, registry_path: str):
           self.registry_path = registry_path
           self.patterns = self._load_registry()
       
       def load_pattern(self, pattern_id: str) -> Pattern:
           """Load pattern by ID"""
           entry = self.patterns.get(pattern_id)
           if not entry:
               raise PatternNotFoundError(pattern_id)
           
           spec = self._load_yaml(entry['spec_path'])
           schema = self._load_json(entry['schema_path'])
           
           return Pattern(
               id=pattern_id,
               spec=spec,
               schema=schema,
               executor_path=entry['executor_path']
           )
   ```

2. **Pattern Executor**: `core/engine/pattern_executor.py`
   ```python
   class PatternExecutor:
       """Execute pattern instances"""
       
       def execute(self, pattern: Pattern, instance: dict) -> ExecutionResult:
           """Execute pattern with instance variables"""
           
           # Validate instance against schema
           self.validator.validate(instance, pattern.schema)
           
           # Execute pattern steps
           for step in pattern.spec['execution_steps']:
               result = self._execute_step(step, instance)
               
               if not result.success:
                   if self._can_auto_heal(result, pattern):
                       self._heal_and_retry(step, instance, pattern)
                   else:
                       raise ExecutionError(step, result)
           
           return ExecutionResult(status='success')
   ```

3. **Pattern Validator**: `core/engine/pattern_validator.py`
   ```python
   class PatternValidator:
       """Validate instances against schemas"""
       
       def validate(self, instance: dict, schema: dict) -> ValidationResult:
           """Validate using jsonschema"""
           try:
               jsonschema.validate(instance, schema)
               return ValidationResult(valid=True)
           except jsonschema.ValidationError as e:
               return ValidationResult(
                   valid=False,
                   errors=[str(e)]
               )
   ```

4. **Verification Engine**: `core/engine/verification_engine.py`
   ```python
   class VerificationEngine:
       """Execute programmatic verifications"""
       
       def verify(self, verification_id: str, context: dict) -> VerificationResult:
           """Run ground truth verification"""
           template = self.load_verification(verification_id)
           
           result = subprocess.run(
               template['command'].format(**context),
               capture_output=True,
               text=True
           )
           
           for criterion in template['ground_truth_criteria']:
               if not self.evaluate_criterion(criterion, result):
                   return VerificationResult(
                       success=False,
                       message=template['reporting']['on_failure']
                   )
           
           return VerificationResult(success=True)
   ```

5. **Update Orchestrator**: `core/engine/orchestrator.py`
   - Add pattern loading
   - Replace ad-hoc logic with pattern execution
   - Maintain backward compatibility

**Success Criteria**:
- [ ] Pattern loader reads PATTERN_INDEX.yaml
- [ ] Pattern executor handles all 7 core patterns
- [ ] Validation rejects invalid instances
- [ ] Orchestrator uses patterns for new workstreams
- [ ] All 196 existing tests still pass
- [ ] New integration tests for pattern system

**Files Created**: 4 new files, 2 updated files

---

### PHASE 7: Template Extraction & Tools (90 min)

**Pattern**: Automation

**Deliverables**:

1. **Template Extractor**: `core/engine/template_extractor.py`
   ```python
   class TemplateExtractor:
       """Extract reusable pattern from executed workstream"""
       
       def extract_from_workstream(self, ws_id: str, run_id: str):
           """Generate pattern from completed execution"""
           
           # Load execution history
           run_data = self.load_run_data(run_id)
           workstream = self.load_workstream(ws_id)
           
           # Extract decisions made
           decisions = self.extract_decisions(run_data)
           
           # Generate pattern spec
           pattern = {
               'pattern_id': f"PAT-EXTRACTED-{uuid4().hex[:8].upper()}",
               'name': workstream.name.lower().replace(' ', '_'),
               'version': '1.0.0',
               'category': workstream.category,
               'structural_decisions': decisions['structural'],
               'variable_sections': decisions['variable'],
               'execution_steps': self.extract_sequence(run_data),
               'ground_truth': self.extract_verifications(run_data),
               'meta': {
                   'extracted_from': run_id,
                   'estimated_time_minutes': run_data.duration_minutes,
                   'time_savings_vs_manual': self.calculate_savings(run_data)
               }
           }
           
           # Save pattern
           self.save_pattern(pattern)
           return pattern
   ```

2. **Pattern Management CLI**: `tools/pattern_tools.py`
   ```python
   import typer
   
   app = typer.Typer()
   
   @app.command()
   def create(name: str, category: str):
       """Create new pattern scaffolding"""
       # Generate spec, schema, executor, test templates
       
   @app.command()
   def validate(pattern_id: str):
       """Validate pattern compliance"""
       # Check PAT-* requirements
       
   @app.command()
   def extract(ws_id: str, run_id: str):
       """Extract pattern from workstream execution"""
       extractor = TemplateExtractor()
       pattern = extractor.extract_from_workstream(ws_id, run_id)
       typer.echo(f"Pattern created: {pattern['pattern_id']}")
   
   @app.command()
   def migrate_atom(atom_uid: str):
       """Migrate atom from legacy registry"""
       # Convert atom to pattern
   ```

3. **Compliance Checker**: `scripts/check_pattern_compliance.ps1`
   - Validates PAT-CHECK-001 requirements
   - Checks all 4 components exist
   - Verifies naming conventions
   - Ensures registry consistency

**Success Criteria**:
- [ ] Can extract pattern from any completed workstream
- [ ] CLI tools simplify pattern creation
- [ ] Compliance checker catches violations
- [ ] Documentation for pattern creation workflow

**Files Created**: 3 files

---

### PHASE 8: Validation & Compliance (90 min)

**Pattern**: Ground Truth Verification

**Deliverables**:

1. `scripts/validate_pattern_registry.ps1`
   - Validate PATTERN_INDEX.yaml structure
   - Check all referenced files exist
   - Verify pattern naming conventions

2. `tests/test_pattern_system.py`
   - System-level integration tests
   - Pattern loading tests
   - Execution tests
   - Validation tests

3. `docs/PATTERN_SYSTEM_GUIDE.md`
   - Complete usage documentation
   - Pattern creation guide
   - AI tool integration guide
   - Best practices

4. Run all tests and generate compliance report

**Success Criteria**:
- [ ] All pattern tests pass (determinism verified)
- [ ] System tests verify orchestrator integration
- [ ] Compliance report shows 100% adherence
- [ ] Documentation complete for AI and humans

**Files Created**: 3 files, 1 report

---

### PHASE 9: Performance Measurement & Iteration (2 hours)

**Pattern**: Ground Truth Metrics

**Deliverables**:

1. `scripts/measure_execution_speed.ps1` - Benchmark tool
2. Baseline measurements (without patterns)
3. Pattern-based measurements
4. Speedup report comparing:
   - Token consumption (target: 94% reduction)
   - Execution time (target: 3-5x speedup)
   - Human interventions (target: 95% reduction)
5. Actual ROI documentation

**Metrics to Capture**:
- Time per phase (before/after)
- Token usage per phase (before/after)
- Number of permission requests (before/after)
- Self-healing success rate
- Pattern reuse count

**Success Criteria**:
- [ ] Measurements show 3x+ speedup on representative phases
- [ ] Token usage < 10k (vs 80k baseline)
- [ ] Zero permission prompts during pattern execution
- [ ] Report validates claims from source documents

**Files Created**: 2 files, 1 benchmark report

---

## AI Agent Pattern Extraction (Phase 5 Implementation)

**See**: `ATOMIC_WORKFLOW_EXTRACTION_PROMPT.md` for the complete extraction procedure.

This document contains:
- Detailed 5-phase extraction process
- Complete migration script (`migrate_atoms_to_patterns.py`)
- Converter tool integration steps
- Success criteria and deliverables checklist
- Estimated time: 3-4 hours

**Quick Reference**:
```bash
# Run extraction (from repo root)
cd patterns/legacy_atoms/
git clone https://github.com/DICKY1987/atomic-workflow-system.git source/

# Run migration script
python ../../scripts/migrate_atoms_to_patterns.py \
    --registry source/atoms.registry.jsonl \
    --output converted/ \
    --limit 20 \
    --min-priority 3

# Merge registry entries
cat converted/registry_entries.yaml >> ../registry/PATTERN_INDEX.yaml
```

**Output Structure** (standardized):
```
patterns/legacy_atoms/
├── source/                     # Cloned repositories
├── converted/                  # Generated patterns
│   ├── specs/
│   ├── schemas/
│   ├── executors/
│   ├── examples/
│   ├── mapping.json
│   └── registry_entries.yaml   # Bare list for merging
├── reports/
│   ├── analysis_report.md
│   └── EXTRACTION_REPORT.md
└── tools/                      # Legacy-specific helpers
```

---

## Success Metrics & ROI

### Speed Metrics (Target)
- [ ] Phase execution time reduced by **60-75%**
- [ ] Planning overhead reduced by **90%** (< 5k tokens)
- [ ] Verification time reduced by **90%** (programmatic)
- [ ] Human interventions reduced by **95%**

### Quality Metrics (Target)
- [ ] **100%** of phases pass ground truth verification
- [ ] **0** scope violations
- [ ] **0** "hallucinated success" incidents
- [ ] Self-healing success rate > **80%**

### Automation Metrics (Target)
- [ ] **90%** of phases execute without human input
- [ ] **80%** of errors auto-healed
- [ ] **100%** of phases use patterns after pilot

### Pattern Library Metrics
- [ ] **7** core patterns created
- [ ] **16** verification/decision/self-healing templates
- [ ] **20+** patterns migrated from atomic-workflow-system
- [ ] **10+** workstreams converted to patterns
- [ ] **5+** patterns with proven reuse (>3 uses)

### ROI Calculation

```
Pattern Creation Cost (One-Time):
├─ Execute phase first time: 133 minutes
├─ Document decisions: 15 minutes
├─ Create pattern (spec+schema+executor+tests): 60 minutes
└─ Total investment: 208 minutes (~3.5 hours)

Break-Even Analysis:
├─ Time saved per use: 88 minutes (avg)
├─ Break-even point: 2.4 uses (~3 uses)
├─ After 5 uses: 440 minutes saved (7.3 hours)
├─ After 10 uses: 880 minutes saved (14.7 hours)

For 43 patterns (7 core + 16 templates + 20 migrated) with avg 5 uses each:
Total time invested: 43 × 208 = 8,944 minutes (149 hours)
Total time saved: 43 × 5 × 88 = 18,920 minutes (315 hours)
Net savings: 315 - 149 = 166 hours
ROI: 112% return on investment
```

---

## Naming Conventions (RFC 2119)

### Pattern IDs (PAT-NAME-001)
- **MUST** use format: `PAT-<CATEGORY>-<NAME>-<SEQ>`
- **MUST** use uppercase for ID
- Examples: `PAT-ATOMIC-CREATE-001`, `PAT-BATCH-CREATE-001`

### Migrated Pattern IDs (PAT-NAME-002)
**Exception for Legacy Imports**:
- Patterns migrated from atomic-workflow-system **MAY** use: `PAT-MIGRATED-<CATEGORY>-<SEQ>`
- **MUST** preserve traceability to original atom UID in metadata
- **MUST** include `migrated_from: atomic-workflow-system` field
- Examples: `PAT-MIGRATED-CLI-001`, `PAT-MIGRATED-GITHUB-002`
- **SHOULD** be refactored to standard naming once tested and validated

### Pattern Names
- **MUST** use `snake_case`
- **MUST** be `[a-z0-9_]` only (no spaces, hyphens in names)
- **MUST** match across all 4 components
- Examples: `atomic_create`, `worktree_lifecycle`

### File Naming
- Specs: `<pattern_name>.pattern.yaml`
- Schemas: `<pattern_name>.schema.json`
- Executors: `<pattern_name>_executor.(ps1|py)`
- Tests: `test_<pattern_name>_executor.(ps1|py)`

### Directory Structure
- **MUST** have all 9 subdirectories under `patterns/`
- **MUST** organize by type (specs/, schemas/, executors/, etc.)
- **MUST NOT** nest patterns within subdirectories

---

## Integration with Workstream System

### Enhanced WorkstreamSpec

```yaml
workstream_id: "WS-PATTERN-01"
project_id: "PRJ-UET"
phase_id: "PH-CORE-01"

name: "Pattern-Driven Module Creation"
category: "template_execution"

# NEW: Pattern reference
pattern_ref:
  pattern_id: "PAT-MODULE-CREATION-001"
  pattern_name: "module_creation"
  version: "1.0.0"
  instance_vars:
    MODULE_NAME: "error_detector"
    MODULE_PATH: "src/error/detector"
    MODULE_PURPOSE: "Detect errors in patch execution"
    LAYER: "domain"

# Execution profile (from pattern metadata)
estimated_time_seconds: 300  # 5 minutes
max_runtime_seconds: 600

# Ground truth (from pattern)
verification_steps:
  - "preflight_checks"
  - "post_execution_checks"
  - "scope_validation"

# Self-healing (from pattern)
auto_heal_enabled: true
max_auto_heal_attempts: 3

tasks:
  - task_id: "T-001"
    type: "pattern_execution"
    pattern_id: "PAT-MODULE-CREATION-001"
    # Tasks inherit from pattern spec
```

---

## Timeline Summary

### Week 1: Foundation (Phases 0-2B)
- **Days 1-2**: Infrastructure + Registry (Phases 0-1)
- **Days 3-4**: First Pattern Spec/Schema (Phase 2A)
- **Day 5**: First Pattern Executor/Tests (Phase 2B)
- **Deliverable**: 1 working pattern (atomic_create)

### Week 2: Core Library (Phases 3-4)
- **Days 1-4**: 6 Additional Patterns (Phase 3)
- **Day 5**: Verification/Decision Templates (Phase 4)
- **Deliverable**: 7 core patterns + 16 templates

### Week 3: Integration (Phases 5-6)
- **Days 1-2**: Migrate from atomic-workflow-system (Phase 5)
- **Days 3-5**: UET Orchestrator Integration (Phase 6)
- **Deliverable**: 20+ migrated patterns, integrated orchestrator

### Week 4: Tooling & Validation (Phases 7-9)
- **Days 1-2**: Template Extraction & CLI Tools (Phase 7)
- **Day 3**: Compliance & Documentation (Phase 8)
- **Days 4-5**: Performance Measurement (Phase 9)
- **Deliverable**: Complete pattern system, validated and benchmarked

**Total Duration**: 4 weeks (20 working days)

---

## Compliance Checklist (PAT-CHECK-001)

Pattern System Compliance:
- [ ] `patterns/` directory exists
- [ ] All 10 subdirectories exist (registry, specs, schemas, executors, examples, tests, verification, decisions, self_healing, legacy_atoms)
- [ ] `PATTERN_INDEX.yaml` is valid YAML with `patterns:` list
- [ ] Every core pattern (non-migrated) has all 4 required components
- [ ] All referenced files in registry exist
- [ ] Core pattern naming follows conventions (`PAT-<CATEGORY>-<NAME>-<SEQ>`)
- [ ] Migrated pattern naming follows exception (`PAT-MIGRATED-<CATEGORY>-<SEQ>`)
- [ ] All patterns have working examples
- [ ] All patterns have passing tests
- [ ] README_PATTERNS.md exists and is complete
- [ ] Schemas validate all example instances

### Migrated Pattern Exception (PAT-CHECK-002)

Patterns migrated from atomic-workflow-system:
- [ ] **MAY** use `PAT-MIGRATED-<CATEGORY>-<SEQ>` format
- [ ] **MUST** include `migrated_from: atomic-workflow-system` in metadata
- [ ] **MUST** include `original_atom_uid` in metadata
- [ ] **MUST** have status: "draft" until tested
- [ ] **SHOULD** be refactored to standard naming once validated
- [ ] **MUST** validate against migration-aware schemas

---

## References

1. **TEMPLATE_IMPLEMENTATION_PLAN.md** - Template-driven execution strategy
2. **complete pattern solution.txt** - 4-component pattern architecture
3. **atomic-workflow-system** - Proven atom/workflow patterns
4. **Every_reusable_pattern.md** - Pattern specification details
5. **uet-execution-acceleration-guide.md** - Decision elimination theory
6. **Decision Elimination Through Pattern Recognition6.md** - 17 manifests case study
7. **UET_WORKSTREAM_SPEC.md** - Workstream architecture
8. **ai_policies.yaml** - AI editing policies
9. **CODEBASE_INDEX.yaml** - Module structure

---

**Document Status**: Unified Plan v1.0  
**Last Updated**: 2025-11-24  
**Owner**: UET Framework Team  
**Next Review**: After Phase 2B completion (first working pattern)

---

## Quick Start

To begin implementation immediately:

```bash
# Phase 0: Create structure (5 min)
mkdir -p patterns/{registry,specs,schemas,executors,examples,tests,verification,decisions,self_healing,legacy_atoms}

# Phase 1: Initialize registry (10 min)
touch patterns/registry/PATTERN_INDEX.yaml
touch patterns/README_PATTERNS.md

# Phase 2A: Start first pattern (30 min)
touch patterns/specs/atomic_create.pattern.yaml
touch patterns/schemas/atomic_create.schema.json
mkdir patterns/examples/atomic_create

# Ready to implement!
```

**First Goal**: Get one pattern working end-to-end (atomic_create) before scaling to others.
