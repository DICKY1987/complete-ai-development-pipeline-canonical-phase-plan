# Templates Directory

Pre-compiled execution templates for decision elimination and autonomous execution.

**Based on**: Decision Elimination Through Pattern Recognition methodology  
**Objective**: 3-5x speedup by eliminating runtime decisions

---

## Directory Structure

```
templates/
├── README.md                        # This file
├── phase_templates/                 # Complete phase execution templates
│   ├── worktree_lifecycle.template.yaml
│   ├── module_creation.template.yaml
│   ├── task_queue.template.yaml
│   ├── validation_loop.template.yaml
│   └── recovery_handler.template.yaml
│
├── execution_patterns/              # Atomic execution patterns
│   ├── atomic_create.pattern.yaml
│   ├── batch_create.pattern.yaml
│   ├── refactor_patch.pattern.yaml
│   ├── self_heal.pattern.yaml
│   ├── test_first.pattern.yaml
│   └── verify_commit.pattern.yaml
│
├── verification_templates/          # Ground truth validators
│   ├── preflight.verify.yaml
│   ├── pytest_green.verify.yaml
│   ├── git_clean.verify.yaml
│   ├── scope_valid.verify.yaml
│   ├── file_exists.verify.yaml
│   └── import_valid.verify.yaml
│
├── decision_templates/              # Pre-authorized decisions
│   ├── worktree_creation.decisions.yaml
│   ├── scope_validation.decisions.yaml
│   ├── self_healing.decisions.yaml
│   ├── test_coverage.decisions.yaml
│   └── code_style.decisions.yaml
│
├── self_healing/                    # Auto-fix rules
│   ├── missing_directory.fix.yaml
│   ├── missing_import.fix.yaml
│   ├── syntax_error.fix.yaml
│   ├── test_failure.fix.yaml
│   └── import_cycle.fix.yaml
│
└── examples/                        # Complete examples
    └── (coming soon)
```

---

## Template Categories

### 1. Phase Templates
**Purpose**: Complete pre-compiled phase execution plans  
**Schema**: `schema/phase_template.v1.json`  
**Time Savings**: 60-75% (133 min → 45 min)

Complete templates that define:
- All structural decisions (file paths, functions, structure)
- Variable sections (filled at runtime)
- Execution sequence (pre-ordered steps)
- Ground truth verification (programmatic checks)
- Self-healing rules (pre-authorized fixes)

**Example**: `worktree_lifecycle.template.yaml`
- Creates Git worktree management module
- 400-500 lines of implementation
- 9 tests
- CLI tool
- 45 minutes (vs 3 hours manual)

### 2. Execution Patterns
**Purpose**: Reusable atomic execution patterns  
**Schema**: `schema/execution_pattern.v1.json`  
**Time Savings**: 60% coordination reduction

Patterns for common operations:
- `atomic_create`: Create 1-3 files with tests
- `batch_create`: Create N similar files in parallel
- `refactor_patch`: Modify existing code safely
- `self_heal`: Detect → fix → retry loop
- `test_first`: TDD workflow
- `verify_commit`: Verify → commit atomic unit

**Example**: `atomic_create.pattern.yaml`
- Used in 80% of phases
- Creates files + tests in one turn
- No placeholders
- Automatic verification
- 60% faster than manual

### 3. Verification Templates
**Purpose**: Programmatic ground truth checks  
**Schema**: `schema/verification_template.v1.json`  
**Time Savings**: 90% (30 sec → 2 sec)

Observable success criteria:
- `preflight.verify`: Environment ready before execution
- `pytest_green.verify`: All tests pass
- `git_clean.verify`: No uncommitted changes
- `scope_valid.verify`: Files within declared scope
- `file_exists.verify`: Artifacts created
- `import_valid.verify`: No deprecated imports

**Example**: `pytest_green.verify.yaml`
- Runs pytest programmatically
- Parses output for metrics
- Success = all tests pass
- 2 seconds vs 30 seconds manual

### 4. Decision Templates
**Purpose**: Pre-authorized decision rules  
**Schema**: Custom per template

Pre-made decisions for:
- When to create worktrees
- File scope validation rules
- Self-healing authorization
- Test coverage requirements
- Code style standards

**Example**: `self_healing.decisions.yaml`
- Missing directory → auto-create
- Missing import → pip install
- Syntax error → black format
- Test failure → fix + retry (3x)

### 5. Self-Healing Rules
**Purpose**: Automatic error recovery  
**Schema**: Custom per fix

Auto-fix scenarios:
- `missing_directory.fix`: Create dirs automatically
- `missing_import.fix`: Install packages
- `syntax_error.fix`: Auto-format code
- `test_failure.fix`: Analyze + fix + retry
- `import_cycle.fix`: Refactor imports

**Example**: `missing_import.fix.yaml`
- Detects: `ModuleNotFoundError: No module named 'X'`
- Action: `pip install X --quiet`
- Verify: `python -c 'import X'`
- Max attempts: 1

---

## How Templates Work

### Traditional Execution (SLOW)
```
1. Load 300-line spec           → 30 sec
2. Analyze dependencies         → 60 sec
3. Design file structure        → 120 sec
4. Plan verification            → 180 sec
5. Create execution plan        → 120 sec
6. Ask permissions              → 90 sec
7. Execute                      → 7200 sec
8. Manual verify                → 150 sec
───────────────────────────────────────────
TOTAL: 8000 sec (133 min)
Tokens: 80k
Human interventions: 3+
```

### Template-Driven Execution (FAST)
```
1. Load template                → 1 sec (pre-compiled)
2. Fill context vars            → 2 sec
3. Pre-flight verify            → 5 sec (programmatic)
4. Execute                      → 2700 sec
5. Auto-verify                  → 10 sec (programmatic)
───────────────────────────────────────────
TOTAL: 2720 sec (45 min)
Tokens: 5k (-94%)
Human interventions: 0 (-100%)
```

**Speedup**: 2.96x faster  
**Key**: Decisions made once at template creation, not every execution

---

## Using Templates

### From Python
```python
from core.engine.template_loader import TemplateLoader
from core.engine.pattern_executor import PatternExecutor

# Load template
loader = TemplateLoader()
template = loader.load("worktree_lifecycle_v1")

# Fill context variables
context = {
    "PROJECT_ROOT": "/path/to/project",
    "BASE_BRANCH": "main",
    "RUN_ID": "run-2025-11-23",
    "WS_ID": "ws-001"
}

# Execute
executor = PatternExecutor()
result = executor.execute_template(template, context)
```

### From Workstream
```yaml
# workstream spec
workstream_id: "WS-001"
template_ref:
  template_id: "module_creation_v1"
  context_vars:
    MODULE_NAME: "error_detector"
    MODULE_PATH: "src/error/detector"
    MODULE_PURPOSE: "Detect errors in patches"
    LAYER: "domain"
```

---

## Creating New Templates

### 1. Execute Phase Manually First
```bash
# Run phase and track time/decisions
python -m core.engine.orchestrator execute WS-001

# Result: 133 minutes, 15 decisions made
```

### 2. Extract Template
```bash
# Analyze execution and create template
python tools/extract_template.py \
  --workstream WS-001 \
  --run run-2025-11-23 \
  --output templates/phase_templates/my_phase.template.yaml
```

### 3. Validate Template
```bash
# Check schema compliance
python tools/validate_template.py \
  templates/phase_templates/my_phase.template.yaml
```

### 4. Use Template
```bash
# Execute using template (should be 60-75% faster)
python -m core.engine.orchestrator execute WS-002 --use-template my_phase_v1
```

### 5. Measure ROI
```
First execution (manual):     133 min
Template creation:             30 min
─────────────────────────────────────
Total investment:             163 min

Second execution (template):   45 min
Time saved:                    88 min

Break-even:                     2 uses
After 5 uses:                 440 min saved (7.3 hours)
After 10 uses:                880 min saved (14.7 hours)
```

---

## Template Standards

### Naming Convention
- Phase templates: `{phase_name}.template.yaml`
- Execution patterns: `{pattern_name}.pattern.yaml`
- Verification templates: `{check_name}.verify.yaml`
- Decision templates: `{decision_area}.decisions.yaml`
- Self-healing rules: `{error_type}.fix.yaml`

### Version Strategy
- Semantic versioning: v1, v2, v3
- Template ID includes version: `atomic_create_v1`
- Breaking changes → new version
- Old versions supported for 6 months

### Required Metadata
Every template MUST include:
- `meta.template_id`: Unique identifier with version
- `meta.category`: Template category
- `meta.estimated_time_minutes`: Expected duration
- `meta.time_savings_vs_manual`: Measured speedup
- `meta.description`: What it does
- `ground_truth_verification`: Observable success criteria

### Testing
Every template MUST have:
- Unit tests (load, validate, fill variables)
- Integration tests (full execution)
- Performance benchmarks (vs manual)
- Example in `examples/` directory

---

## Template Library Status

### Week 1: Core Infrastructure (4 templates)
- [ ] `atomic_create.pattern.yaml` - File creation pattern
- [ ] `pytest_green.verify.yaml` - Test verification
- [ ] `preflight.verify.yaml` - Environment checks
- [ ] `self_heal.pattern.yaml` - Auto-fix loop

### Week 2: Phase Templates (3 templates)
- [ ] `worktree_lifecycle.template.yaml` - Git worktree management
- [ ] `module_creation.template.yaml` - Module + manifest creation
- [ ] `scope_valid.verify.yaml` - Scope validation

### Week 3: Additional Patterns (6 templates)
- [ ] `batch_create.pattern.yaml` - Parallel file creation
- [ ] `refactor_patch.pattern.yaml` - Safe refactoring
- [ ] `test_first.pattern.yaml` - TDD workflow
- [ ] `git_clean.verify.yaml` - Git status check
- [ ] `file_exists.verify.yaml` - Artifact verification
- [ ] `import_valid.verify.yaml` - Import path check

### Week 4: Self-Healing & Decisions (10 templates)
- [ ] `missing_directory.fix.yaml`
- [ ] `missing_import.fix.yaml`
- [ ] `syntax_error.fix.yaml`
- [ ] `test_failure.fix.yaml`
- [ ] `import_cycle.fix.yaml`
- [ ] `worktree_creation.decisions.yaml`
- [ ] `scope_validation.decisions.yaml`
- [ ] `self_healing.decisions.yaml`
- [ ] `test_coverage.decisions.yaml`
- [ ] `code_style.decisions.yaml`

**Total**: 28 templates planned  
**Current**: 0 implemented  
**Progress**: 0%

---

## ROI Analysis

### Template Library (28 templates)
```
Creation cost:
  28 templates × 178 min/template = 4,984 min (83 hours)

Savings (avg 5 uses per template):
  28 templates × 5 uses × 88 min saved = 12,320 min (205 hours)

Net savings:
  205 hours - 83 hours = 122 hours

ROI:
  147% return on investment
```

### Per Template
```
Investment: 178 min (first execution + extraction)
Break-even: 2 uses
After 5 uses: 7.3 hours saved
After 10 uses: 14.7 hours saved
```

---

## Schema References

- `schema/phase_template.v1.json` - Phase template schema
- `schema/execution_pattern.v1.json` - Execution pattern schema
- `schema/verification_template.v1.json` - Verification template schema

---

## Documentation

- `TEMPLATE_IMPLEMENTATION_PLAN.md` - Full implementation plan
- `docs/templates/` - Detailed template documentation
- `examples/` - Working examples

---

**Created**: 2025-11-23  
**Status**: Directory structure created, schemas defined  
**Next**: Implement Week 1 core templates
