# Template Implementation Plan
## Decision Elimination via Pre-Compiled Execution Templates

**Created**: 2025-11-23  
**Based on**:
- `uet-execution-acceleration-guide.md` (Decision Elimination Theory)
- `Decision Elimination Through Pattern Recognition6.md` (17 Manifests in 12 Hours Case Study)
- `UET_WORKSTREAM_SPEC.md` (Workstream Architecture)

**Objective**: Implement template-driven execution to achieve **3-5x speedup** by eliminating runtime decisions.

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

### The Solution (Template-Driven)
```
Phase Execution Time Breakdown:
├─ Load template: 1 sec (pre-compiled)
├─ Fill context: 2 sec (variables only)
├─ Pre-flight verify: 5 sec (programmatic)
├─ Execute: 2700 sec (45 minutes)
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

### Template Directory Structure

```
UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/
├── templates/                           # NEW: Template library
│   ├── phase_templates/                 # Pre-compiled phase templates
│   │   ├── worktree_lifecycle.template.yaml
│   │   ├── module_creation.template.yaml
│   │   ├── task_queue.template.yaml
│   │   ├── validation_loop.template.yaml
│   │   └── recovery_handler.template.yaml
│   │
│   ├── execution_patterns/              # Atomic execution patterns
│   │   ├── atomic_create.pattern.yaml
│   │   ├── batch_create.pattern.yaml
│   │   ├── refactor_patch.pattern.yaml
│   │   ├── self_heal.pattern.yaml
│   │   ├── test_first.pattern.yaml
│   │   └── verify_commit.pattern.yaml
│   │
│   ├── verification_templates/          # Ground truth validators
│   │   ├── preflight.verify.yaml
│   │   ├── pytest_green.verify.yaml
│   │   ├── git_clean.verify.yaml
│   │   ├── scope_valid.verify.yaml
│   │   ├── file_exists.verify.yaml
│   │   └── import_valid.verify.yaml
│   │
│   ├── decision_templates/              # Pre-authorized decisions
│   │   ├── worktree_creation.decisions.yaml
│   │   ├── scope_validation.decisions.yaml
│   │   ├── self_healing.decisions.yaml
│   │   ├── test_coverage.decisions.yaml
│   │   └── code_style.decisions.yaml
│   │
│   └── self_healing/                    # Auto-fix rules
│       ├── missing_directory.fix.yaml
│       ├── missing_import.fix.yaml
│       ├── syntax_error.fix.yaml
│       ├── test_failure.fix.yaml
│       └── import_cycle.fix.yaml
│
├── core/
│   └── engine/
│       ├── template_loader.py           # NEW: Load and fill templates
│       ├── pattern_executor.py          # NEW: Execute patterns
│       └── verification_engine.py       # NEW: Programmatic verification
│
└── schema/
    ├── phase_template.v1.json           # NEW: Phase template schema
    ├── execution_pattern.v1.json        # NEW: Pattern schema
    └── verification_template.v1.json    # NEW: Verification schema
```

---

## Phase 1: Core Template Infrastructure (Week 1)

### Objective
Build the 4 highest-impact templates that provide **80% of speedup**.

### Deliverables

#### 1. `atomic_create.pattern.yaml` (Day 1-2)
**Impact**: Used in 80% of phases  
**Time Savings**: 60% coordination reduction

```yaml
# Pattern: Atomic Create
# USE_CASE: Creating 1-3 files with tests
# TIME_SAVINGS: 60% (30 min -> 12 min)

pattern_id: "atomic_create_v1"
category: "file_creation"

structural_decisions:
  max_files_per_phase: 3
  always_include_tests: true
  test_ratio: "1 test file per implementation file"
  
execution_steps:
  1_verify_parent_dirs:
    checks:
      - "Parent directories exist"
      - "No conflicting files"
    on_fail: "create_parents_auto"
  
  2_create_files:
    strategy: "sequential"
    order:
      - "implementation_files"
      - "test_files"
    
    implementation_files:
      approach: "complete_file_in_one_turn"
      no_placeholders: true
      include_docstrings: true
      include_type_hints: true
    
    test_files:
      approach: "complete_test_suite"
      min_test_count: 3
      test_types:
        - "happy_path"
        - "error_cases"
        - "edge_cases"
  
  3_verify_creation:
    checks:
      - cmd: "Test-Path ${file_path}"
        for_each: "created_files"
      - cmd: "python -m py_compile ${file_path}"
        for_each: "python_files"
  
  4_run_tests:
    cmd: "python -m pytest ${test_file} -v"
    expect: ".*passed.*0 failed.*"
    on_fail: "enter_fix_loop"
  
  5_git_status:
    cmd: "git status --porcelain"
    expect_count: "${created_files.length}"
    expect_pattern: "^\\?\\?\\s+.*"

ground_truth:
  success_criteria:
    - "All files exist"
    - "All files compile/parse"
    - "All tests pass"
    - "Git status shows only expected new files"
```

**Implementation**:
```python
# core/engine/pattern_executor.py
class PatternExecutor:
    def execute_pattern(self, pattern_id: str, context: dict):
        """Execute pre-compiled pattern with context variables"""
        pattern = self.load_pattern(pattern_id)
        
        for step in pattern['execution_steps']:
            result = self.execute_step(step, context)
            if not self.verify_step(step, result):
                if step.get('on_fail') == 'enter_fix_loop':
                    self.self_heal(result, pattern)
                else:
                    raise ExecutionError(f"Step {step['id']} failed")
        
        return self.verify_ground_truth(pattern['ground_truth'], context)
```

#### 2. `pytest_green.verify.yaml` (Day 2)
**Impact**: Eliminates manual verification  
**Time Savings**: 30 sec → 2 sec per verification

```yaml
# Verification: All Tests Pass
# PURPOSE: Ground truth verification (from Dev Rules #1)
# TIME: Variable (depends on test count)

verification_id: "pytest_green_v1"
category: "testing"

command: "python -m pytest ${test_path} -v --tb=short"

success_patterns:
  - ".*passed.*"
  - ".*0 failed.*"
  - ".*0 errors.*"

failure_patterns:
  - "FAILED"
  - "ERROR"
  - ".*[1-9][0-9]* failed.*"

ground_truth_criteria:
  - "exit_code == 0"
  - "Match success_patterns"
  - "No match failure_patterns"
  - "Output contains test count"

parsing:
  extract_metrics:
    - pattern: "(\\d+) passed"
      capture: "passed_count"
    - pattern: "(\\d+) failed"
      capture: "failed_count"
    - pattern: "(\\d+) errors"
      capture: "error_count"

reporting:
  on_success: |
    ✅ Tests passed: ${passed_count}/${passed_count}
  
  on_failure: |
    ❌ Tests failed: ${passed_count}/${passed_count + failed_count}
    
    Failed tests:
    ${failed_test_list}
```

**Implementation**:
```python
# core/engine/verification_engine.py
class VerificationEngine:
    def verify(self, verification_id: str, context: dict) -> VerificationResult:
        """Run programmatic verification"""
        template = self.load_verification(verification_id)
        
        # Execute command
        result = subprocess.run(
            template['command'].format(**context),
            capture_output=True,
            text=True
        )
        
        # Check ground truth
        for criterion in template['ground_truth_criteria']:
            if not self.evaluate_criterion(criterion, result):
                return VerificationResult(
                    success=False,
                    message=template['reporting']['on_failure'].format(**context)
                )
        
        return VerificationResult(
            success=True,
            message=template['reporting']['on_success'].format(**context)
        )
```

#### 3. `preflight.verify.yaml` (Day 3)
**Impact**: Catches environment issues before execution  
**Time Savings**: Prevents 15-30 min debugging sessions

```yaml
# Verification: Pre-Flight Checks
# PURPOSE: Ensure environment ready before phase execution
# TIME: < 5 seconds

verification_id: "preflight_v1"
category: "environment"

checks:
  project_root_exists:
    cmd: "Test-Path ${PROJECT_ROOT}"
    expect: "True"
    criticality: "blocker"
    fix_hint: "Create project with PH-00 first"
  
  git_repo_initialized:
    cmd: "Test-Path ${PROJECT_ROOT}/.git"
    expect: "True"
    criticality: "blocker"
    fix_hint: "Run 'git init' in project root"
  
  base_repo_clean:
    cmd: "git status --porcelain"
    expect: ""
    criticality: "blocker"
    fix_hint: "Commit or stash changes before creating worktree"
  
  python_available:
    cmd: "python --version"
    expect_pattern: "Python 3\\.(1[2-9]|[2-9][0-9]).*"
    criticality: "blocker"
    fix_hint: "Install Python 3.12+"
  
  pytest_available:
    cmd: "python -m pytest --version"
    expect_pattern: "pytest.*"
    criticality: "blocker"
    fix_hint: "pip install pytest"
  
  required_directories:
    cmd: "Test-Path ${dir}"
    for_each:
      - "src/pipeline"
      - "tests/pipeline"
      - "docs"
      - "scripts"
    expect: "True"
    criticality: "warning"
    auto_fix: "create_directory"

execution:
  run_all: true
  stop_on_first_blocker: true
  report_warnings: true
```

#### 4. `self_heal.pattern.yaml` (Day 4-5)
**Impact**: Removes permission bottlenecks  
**Time Savings**: 90 sec → 0 sec (automated fixes)

```yaml
# Pattern: Self-Healing Execution Loop
# USE_CASE: Run → Inspect → Fix → Re-verify
# ELIMINATES: Permission bottlenecks, manual intervention

pattern_id: "self_heal_v1"
category: "error_recovery"

pre_authorized_fixes:
  # These can execute without asking
  
  missing_directory:
    detection: "FileNotFoundError.*No such file or directory"
    action: |
      New-Item -ItemType Directory -Path ${missing_path} -Force
    verify: "Test-Path ${missing_path}"
    max_auto_attempts: 1
  
  missing_import:
    detection: "ModuleNotFoundError: No module named '(.*)'"
    action: |
      pip install ${module_name} --quiet
    verify: "python -c 'import ${module_name}'"
    max_auto_attempts: 1
  
  syntax_error:
    detection: "SyntaxError|IndentationError"
    action: "fix_code_with_linter"
    tool: "black"
    verify: "python -m py_compile ${file_path}"
    max_auto_attempts: 2
  
  test_failure_assertion:
    detection: "AssertionError|assert .* == .*"
    action: "analyze_and_fix_test"
    verify: "pytest ${test_file} -q"
    max_auto_attempts: 3

requires_human_intervention:
  # These STOP and ask
  
  git_conflict:
    detection: "CONFLICT.*Merge conflict"
    action: "stop_and_report"
    reason: "Manual merge required"
  
  base_repo_dirty:
    detection: "git status --porcelain.*[AM] .*"
    action: "stop_and_report"
    reason: "Base must be clean before worktree creation"
  
  out_of_scope_changes:
    detection: "out_of_scope_files.*length > 0"
    action: "stop_and_report"
    reason: "Scope violation - manual review needed"

execution_loop:
  max_iterations: 5
  
  flow:
    1_execute:
      action: "run_command_or_tool"
      capture: ["stdout", "stderr", "exit_code"]
    
    2_inspect:
      checks:
        - "exit_code == 0"
        - "expected_artifacts_exist"
        - "no_error_patterns_in_output"
    
    3_classify_failure:
      if_any_check_failed:
        - "Match against pre_authorized_fixes patterns"
        - "If match → apply fix"
        - "If no match → check requires_human_intervention"
        - "If human needed → stop and report"
    
    4_apply_fix:
      if: "fix_authorized"
      action: "${fix.action}"
      log: "Applied auto-fix: ${fix.action}"
    
    5_re_verify:
      action: "Re-run original command"
      if_success: "break_loop"
      if_fail: "increment_iteration"
```

### Week 1 Success Metrics
- [ ] 4 templates created and validated
- [ ] Template loader implemented
- [ ] Pattern executor implemented
- [ ] Verification engine implemented
- [ ] Test suite for template system (20+ tests)
- [ ] Demo: Create simple module using `atomic_create` pattern

---

## Phase 2: Phase Template Library (Week 2)

### Objective
Create 3 high-value phase templates based on real UET phases.

### Deliverables

#### 5. `worktree_lifecycle.template.yaml` (Day 6-7)
**Impact**: PH-04.5 from 3 hours → 45 minutes  
**Time Savings**: 75% reduction

Based on actual Git worktree lifecycle requirements from UET framework.

```yaml
# TEMPLATE: Git Worktree Lifecycle Management
# PHASE_ID: PH-04.5
# DECISIONS_MADE_AT: 2025-11-23 (template creation)
# PROVEN_USES: 0 (initial version)

meta:
  template_id: "worktree_lifecycle_v1"
  category: "infrastructure"
  estimated_time_minutes: 45
  time_savings_vs_manual: "75%"
  
structural_decisions:
  file_format: "python"
  module_location: "src/pipeline/worktree.py"
  test_location: "tests/pipeline/test_worktree.py"
  cli_location: "scripts/worktrees.py"
  
  directory_structure:
    - ".worktrees/"
    - ".ledger/patches/"
    - ".tasks/inbox/"
    - ".tasks/running/"
    - ".tasks/done/"
    - ".tasks/failed/"
  
  required_functions:
    - "get_repo_root() -> Path"
    - "get_worktree_root() -> Path"
    - "get_base_branch() -> str"
    - "create_worktree_for_ws(run_id: str, ws_id: str) -> WorktreeInfo"
    - "validate_scope(ws_id: str, files_scope: list, files_create: list) -> dict"
    - "cleanup_orphaned_worktrees() -> list"

variable_sections:
  project_root: "${PROJECT_ROOT}"
  base_branch: "${BASE_BRANCH:-main}"
  run_id: "${RUN_ID}"
  ws_id: "${WS_ID}"

ground_truth_verification:
  pre_flight:
    - cmd: "Test-Path ${PROJECT_ROOT}"
      expect: "True"
      fail_msg: "Project root does not exist"
    
    - cmd: "git status --porcelain"
      expect: ""
      fail_msg: "Base repo not clean"
  
  post_execution:
    - cmd: "Test-Path src/pipeline/worktree.py"
      expect: "True"
      
    - cmd: "python -m pytest tests/pipeline/test_worktree.py -q"
      expect: ".*passed.*"
      
    - cmd: "git status --porcelain"
      expect_pattern: "^[AM]\\s+(src/pipeline/worktree\\.py|scripts/worktrees\\.py|tests/.*)"

execution_sequence:
  steps:
    - id: "preflight"
      pattern: "verification"
      template: "verification_templates/preflight.verify.yaml"
      on_fail: "stop"
    
    - id: "implement_module"
      pattern: "atomic_create"
      files:
        - path: "src/pipeline/worktree.py"
          type: "implementation"
          lines: 400-500
    
    - id: "implement_tests"
      pattern: "atomic_create"
      files:
        - path: "tests/pipeline/test_worktree.py"
          type: "test_suite"
          test_count: 9
    
    - id: "verify_and_commit"
      pattern: "verification_commit"

self_healing:
  auto_fix_scenarios:
    - condition: "Parent directory does not exist"
      action: "create_directory"
      requires_permission: false
    
    - condition: "Import error - module not found"
      action: "install_from_requirements"
      requires_permission: false
```

#### 6. `module_creation.template.yaml` (Day 8-9)
**Impact**: Used 17+ times in manifest creation case study  
**Time Savings**: 88% (42 min → 5 min per manifest)

Based on the "Decision Elimination Through Pattern Recognition" case study.

```yaml
# TEMPLATE: Module Creation with Manifest
# USE_CASE: Create Python module + tests + .ai-module-manifest
# TIME_SAVINGS: 88% (42 min -> 5 min)

meta:
  template_id: "module_creation_v1"
  category: "module_setup"
  estimated_time_minutes: 5
  time_savings_vs_manual: "88%"
  based_on: "17 manifests created in 12 hours case study"

structural_decisions:
  always_create:
    - "${module_path}/__init__.py"
    - "${module_path}/.ai-module-manifest"
    - "tests/${module_name}/test_${module_name}.py"
  
  manifest_template:
    sections:
      - "module"
      - "purpose"
      - "layer"
      - "entry_points"
      - "key_patterns"
      - "common_tasks"
      - "gotchas"
      - "dependencies"
      - "status"
      - "ai_quick_reference"
  
  manifest_size_target: "50-100 lines"
  
  test_structure:
    min_tests: 3
    test_categories:
      - "happy_path"
      - "error_cases"
      - "integration"

variable_sections:
  module_name: "${MODULE_NAME}"
  module_path: "${MODULE_PATH}"
  purpose: "${MODULE_PURPOSE}"
  layer: "${LAYER}"  # infra, domain, api, ui

execution_sequence:
  steps:
    - id: "create_module_structure"
      pattern: "atomic_create"
      files:
        - path: "${module_path}/__init__.py"
          content: "module_init_template"
        
        - path: "${module_path}/.ai-module-manifest"
          content: "manifest_template"
          fill_sections: true
    
    - id: "create_tests"
      pattern: "atomic_create"
      files:
        - path: "tests/${module_name}/test_${module_name}.py"
          content: "test_template"
    
    - id: "verify_manifest"
      checks:
        - "Manifest is 50-100 lines"
        - "All required sections present"
        - "No placeholder text (TODO, FIXME)"

ground_truth:
  success_criteria:
    - "3 files created"
    - "Manifest validates against template"
    - "Tests pass (even if empty)"
    - "Module importable"
```

#### 7. `scope_valid.verify.yaml` (Day 10)
**Impact**: Prevents scope violations (security)  
**Time Savings**: Catches errors before execution

```yaml
# Verification: Scope Validation
# PURPOSE: Ensure files touched are within declared scope
# TIME: < 2 seconds

verification_id: "scope_valid_v1"
category: "security"

inputs:
  files_scope:
    read: []
    write: []
    create: []
    forbidden: []
  
  actual_files_touched: []

validation_logic:
  1_check_forbidden:
    for_each: "actual_files_touched"
    check: "file not in files_scope.forbidden"
    on_fail: "SCOPE_VIOLATION_CRITICAL"
  
  2_check_write:
    for_each: "files_modified"
    check: "file matches glob in files_scope.write"
    on_fail: "SCOPE_VIOLATION_WRITE"
  
  3_check_create:
    for_each: "files_created"
    check: "file matches glob in files_scope.create"
    on_fail: "SCOPE_VIOLATION_CREATE"

reporting:
  on_success: |
    ✅ Scope validation passed
    Files touched: ${actual_files_touched.length}
    All within scope: ${files_scope}
  
  on_failure: |
    ❌ SCOPE VIOLATION DETECTED
    
    Out of scope files:
    ${out_of_scope_files}
    
    Declared scope:
    ${files_scope}
    
    ACTION REQUIRED: Manual review before proceeding
```

### Week 2 Success Metrics
- [ ] 3 phase templates created
- [ ] Integration with workstream_spec.v1.json
- [ ] Demo: Execute worktree lifecycle from template
- [ ] Documentation: Template creation guide

---

## Phase 3: Integration with Workstream System (Week 3)

### Objective
Connect templates to existing UET workstream architecture.

### Workstream Template Enhancement

Enhance existing `workstream_spec.v1.json` with template support:

```yaml
# Enhanced WorkstreamSpec with template support

workstream_id: "WS-TEMPLATE-01"
project_id: "PRJ-UET"
phase_id: "PH-CORE-01"

name: "Template-Driven Module Creation"
category: "template_execution"

# NEW: Template reference
template_ref:
  template_id: "module_creation_v1"
  template_path: "templates/phase_templates/module_creation.template.yaml"
  context_vars:
    MODULE_NAME: "error_detector"
    MODULE_PATH: "src/error/detector"
    MODULE_PURPOSE: "Detect errors in patch execution"
    LAYER: "domain"

# Execution profile (from template)
estimated_time_seconds: 300  # 5 minutes (from template metadata)
max_runtime_seconds: 600

# Ground truth (from template)
verification_steps:
  - "preflight_checks"
  - "post_execution_checks"
  - "scope_validation"

# Self-healing (from template)
auto_heal_enabled: true
max_auto_heal_attempts: 3

tasks:
  - task_id: "T-001"
    type: "template_execution"
    template_pattern: "atomic_create"
    # ... rest of task spec
```

### Template Executor Integration

```python
# core/engine/template_executor.py

class TemplateExecutor:
    """Execute workstreams using pre-compiled templates"""
    
    def __init__(self, template_loader, pattern_executor, verification_engine):
        self.template_loader = template_loader
        self.pattern_executor = pattern_executor
        self.verification_engine = verification_engine
    
    def execute_workstream(self, workstream: WorkstreamSpec) -> ExecutionResult:
        """Execute workstream with template-driven approach"""
        
        # Load template if specified
        if workstream.template_ref:
            template = self.template_loader.load(workstream.template_ref.template_id)
            context = workstream.template_ref.context_vars
        else:
            # Fallback to traditional execution
            return self.execute_traditional(workstream)
        
        # Pre-flight verification (< 5 sec)
        self.verification_engine.verify(
            template.ground_truth.pre_flight, 
            context
        )
        
        # Execute steps (decisions already made)
        for step in template.execution_sequence.steps:
            pattern = self.pattern_executor.load_pattern(step.pattern)
            
            try:
                step_result = self.pattern_executor.execute_step(pattern, context)
                self.verification_engine.verify_step(step.ground_truth, step_result)
            
            except ExecutionError as e:
                # Template-driven self-healing
                if self.can_auto_heal(e, template.self_healing):
                    self.heal_and_retry(step, e, template.self_healing)
                else:
                    raise
        
        # Post-execution verification
        self.verification_engine.verify(
            template.ground_truth.post_execution,
            context
        )
        
        return ExecutionResult(
            status="complete",
            time_seconds=time.time() - start_time,
            template_used=template.meta.template_id
        )
```

### Week 3 Success Metrics
- [ ] Enhanced workstream schema with template support
- [ ] Template executor implemented
- [ ] Integration tests with existing workstreams
- [ ] Demo: Execute real workstream with template
- [ ] Performance comparison: template vs traditional

---

## Phase 4: Template Creation Workflow (Week 4)

### Objective
Automate the creation of new templates from executed workstreams.

### Template Extraction Tool

```python
# tools/extract_template.py

class TemplateExtractor:
    """Extract reusable template from executed workstream"""
    
    def extract_from_workstream(self, workstream_id: str, run_id: str):
        """
        Analyze completed workstream execution and generate template
        
        Process:
        1. Load execution history from run database
        2. Extract decisions made during execution
        3. Identify reusable patterns
        4. Generate template YAML
        5. Calculate time savings
        """
        
        # Load execution data
        run_data = self.load_run_data(run_id)
        workstream = self.load_workstream(workstream_id)
        
        # Extract decisions
        decisions = self.extract_decisions(run_data)
        
        # Generate template
        template = {
            'meta': {
                'template_id': f"{workstream_id.lower()}_v1",
                'category': workstream.category,
                'estimated_time_minutes': run_data.duration_minutes,
                'time_savings_vs_manual': self.calculate_savings(run_data),
                'created_from': run_id,
                'created_at': datetime.now().isoformat()
            },
            'structural_decisions': decisions['structural'],
            'variable_sections': decisions['variable'],
            'execution_sequence': self.extract_sequence(run_data),
            'ground_truth_verification': self.extract_verifications(run_data),
            'self_healing': self.extract_fixes(run_data)
        }
        
        # Save template
        output_path = f"templates/phase_templates/{template['meta']['template_id']}.yaml"
        self.save_template(template, output_path)
        
        return template
```

### Template Validation Tool

```python
# tools/validate_template.py

class TemplateValidator:
    """Validate template structure and completeness"""
    
    def validate(self, template_path: str) -> ValidationReport:
        """
        Validate template against schema and best practices
        
        Checks:
        - Schema compliance
        - All required sections present
        - Ground truth criteria defined
        - Self-healing rules complete
        - Variable substitution valid
        - Estimated time reasonable
        """
        
        template = self.load_template(template_path)
        issues = []
        
        # Schema validation
        schema = self.load_schema('schema/phase_template.v1.json')
        schema_issues = jsonschema.validate(template, schema)
        issues.extend(schema_issues)
        
        # Best practices
        if not template.get('ground_truth_verification'):
            issues.append(ValidationIssue(
                severity='error',
                message='Missing ground_truth_verification section'
            ))
        
        if template['meta']['estimated_time_minutes'] > 120:
            issues.append(ValidationIssue(
                severity='warning',
                message='Phase > 2 hours, consider splitting'
            ))
        
        return ValidationReport(
            valid=len([i for i in issues if i.severity == 'error']) == 0,
            issues=issues
        )
```

### Week 4 Success Metrics
- [ ] Template extraction tool implemented
- [ ] Template validation tool implemented
- [ ] CLI commands for template management
- [ ] Documentation: "How to Create Templates"
- [ ] Demo: Extract template from completed workstream

---

## Success Metrics & ROI

### Speed Metrics (Target)
- [ ] Phase execution time reduced by **60-75%**
- [ ] Planning overhead reduced by **90%** (< 5k tokens)
- [ ] Verification time reduced by **90%** (programmatic)
- [ ] Human interventions reduced by **95%**

### Quality Metrics (Target)
- [ ] **100%** of phases pass ground truth verification
- [ ] **0** scope violations (files touched outside declared scope)
- [ ] **0** "hallucinated success" incidents
- [ ] Self-healing success rate > **80%**

### Automation Metrics (Target)
- [ ] **90%** of phases execute without human input
- [ ] **80%** of errors auto-healed
- [ ] **100%** of phases use templates after pilot

### Template Library Metrics
- [ ] **28** templates created (5 phase, 6 pattern, 6 verification, 5 decision, 5 self-healing, 1 scope)
- [ ] **10+** workstreams converted to templates
- [ ] **5+** templates with proven reuse (>3 uses)

### ROI Calculation

```
Template Creation Cost (One-Time per template):
├─ Execute phase first time: 133 minutes
├─ Document decisions: 15 minutes
├─ Create template: 30 minutes
└─ Total investment: 178 minutes

Break-Even Analysis:
├─ Time saved per use: 88 minutes
├─ Break-even point: 2 uses
├─ After 5 uses: 440 minutes saved (7.3 hours)
├─ After 10 uses: 880 minutes saved (14.7 hours)

For 28 templates with average 5 uses each:
Total time invested: 28 × 178 = 4,984 minutes (83 hours)
Total time saved: 28 × 5 × 88 = 12,320 minutes (205 hours)
Net savings: 205 - 83 = 122 hours
ROI: 147% return on investment
```

---

## Implementation Timeline

### Week 1: Core Infrastructure (Nov 25-29)
- Day 1-2: `atomic_create.pattern.yaml` + pattern_executor.py
- Day 2: `pytest_green.verify.yaml` + verification_engine.py
- Day 3: `preflight.verify.yaml`
- Day 4-5: `self_heal.pattern.yaml` + template_loader.py
- Day 5: Integration testing

### Week 2: Phase Templates (Dec 2-6)
- Day 6-7: `worktree_lifecycle.template.yaml`
- Day 8-9: `module_creation.template.yaml`
- Day 10: `scope_valid.verify.yaml`
- Day 10: Integration with workstream system

### Week 3: Workstream Integration (Dec 9-13)
- Day 11-12: Enhance workstream_spec.v1.json
- Day 12-13: template_executor.py implementation
- Day 14-15: Integration testing with real workstreams

### Week 4: Tooling & Automation (Dec 16-20)
- Day 16-17: Template extraction tool
- Day 18-19: Template validation tool
- Day 20: Documentation & examples

### Week 5: Pilot & Refinement (Dec 23-27)
- Execute 3-5 real phases using templates
- Measure actual speedup vs baseline
- Refine templates based on learnings
- Update documentation

---

## Next Steps

### Immediate Actions (This Week)
1. ✅ Create `templates/` directory structure
2. ✅ Define `phase_template.v1.json` schema
3. ✅ Define `execution_pattern.v1.json` schema
4. ✅ Define `verification_template.v1.json` schema
5. ✅ Create first template: `atomic_create.pattern.yaml`
6. ✅ Implement `pattern_executor.py` (basic version)
7. ✅ Write tests for pattern execution
8. ✅ Demo: Create a file using template

### Medium-Term (Weeks 2-3)
- Build out complete template library
- Integrate with existing workstream system
- Performance testing and optimization

### Long-Term (Month 2+)
- Template marketplace/sharing
- AI-assisted template creation
- Template versioning and migration
- Advanced self-healing strategies

---

## Appendix: Template Standards

### Template Naming Convention
- Phase templates: `{phase_name}.template.yaml`
- Execution patterns: `{pattern_name}.pattern.yaml`
- Verification templates: `{check_name}.verify.yaml`
- Decision templates: `{decision_area}.decisions.yaml`
- Self-healing rules: `{error_type}.fix.yaml`

### Template Versioning
- Semantic versioning: v1.0.0
- Breaking changes increment major version
- Template ID includes version: `atomic_create_v1`
- Migrations provided for breaking changes

### Template Documentation
Each template MUST include:
- `meta.description`: What the template does
- `meta.use_case`: When to use it
- `meta.time_savings`: Measured speedup
- `meta.proven_uses`: Number of successful executions
- `examples/`: At least 1 complete example

### Template Testing
Each template MUST have:
- Unit tests for template loader
- Integration tests for execution
- Performance benchmarks
- Example execution in CI/CD

---

**End of Implementation Plan**

---

## References

1. **uet-execution-acceleration-guide.md** - Theoretical foundation for decision elimination
2. **Decision Elimination Through Pattern Recognition6.md** - Real-world case study (17 manifests in 12 hours)
3. **UET_WORKSTREAM_SPEC.md** - Workstream architecture specification
4. **ai_policies.yaml** - AI editing policies and safe zones
5. **CODEBASE_INDEX.yaml** - Module structure and dependencies

---

**Document Status**: Draft v1.0  
**Last Updated**: 2025-11-23  
**Owner**: UET Framework Team  
**Next Review**: After Week 1 completion
