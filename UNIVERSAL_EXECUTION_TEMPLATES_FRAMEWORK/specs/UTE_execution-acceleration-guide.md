# UET Execution Acceleration via Decision Elimination
## Applying Pattern Recognition to Autonomous Phase Execution

---

## Executive Summary

Your three documents define a sophisticated autonomous execution system:
1. **Development Rules** - Operational constraints and anti-patterns
2. **Tool Execution Spec** - Multi-workstream CLI coordination
3. **Phase 04.5 Spec** - Git worktree lifecycle implementation

The **Decision Elimination Playbook** can accelerate this system by 3-5x through:
- Pre-compiled execution templates (eliminate runtime decisions)
- Standardized verification patterns (eliminate inspection overhead)
- Automated self-healing workflows (eliminate human intervention)
- Batch-parallelizable phase patterns (eliminate sequential bottlenecks)

---

## Current State Analysis

### Bottlenecks in Current Design

**Planning Loop Trap** (from Dev Rules):
```
Problem: 80k+ tokens on planning before atomic execution
Cost: 4-5 minutes per Plan() call, no code/tests generated
Root cause: Every phase execution makes ALL decisions at runtime
```

**Permission Bottlenecks**:
```
Problem: "Would you like me to..." blocking autonomous flow
Cost: Context switches, human intervention, broken execution chains
Root cause: No pre-authorized decision templates for safe operations
```

**Verification Overhead**:
```
Problem: Manual verification of every phase output
Cost: 30+ seconds per verification × N phases
Root cause: No standardized ground truth templates
```

**Context Pollution**:
```
Problem: Loading 300+ line specs before atomic steps
Cost: Token consumption, cognitive load, decision paralysis
Root cause: Specs contain structure AND runtime decisions mixed together
```

---

## Solution: Pre-Compiled Execution Templates

### Core Principle

**Current approach (SLOW):**
```python
def execute_phase(phase_spec):
    # Read 300-line spec
    decisions = analyze_and_decide(phase_spec)  # 80k tokens
    plan = create_detailed_plan(decisions)       # 4-5 minutes
    ask_permission()                             # Human bottleneck
    execute(plan)                                # Finally
    verify_manually()                            # 30+ seconds
```

**Decision Elimination approach (FAST):**
```python
def execute_phase(phase_template):
    # Template has pre-made decisions baked in
    context = load_minimal_context()             # < 5k tokens
    execute(phase_template.fill(context))        # Immediate
    verify(phase_template.ground_truth)          # 2 seconds
```

---

## Implementation Strategy

### Phase 1: Template Library Architecture

Create a new directory structure that separates **structure** from **decisions**:

```
templates/
├── phase_templates/
│   ├── worktree_lifecycle.template.yaml      # PH-04.5 decisions baked in
│   ├── task_queue.template.yaml              # PH-05 decisions baked in
│   ├── validation_loop.template.yaml         # PH-06 decisions baked in
│   └── recovery_handler.template.yaml        # PH-06.5 decisions baked in
│
├── execution_patterns/
│   ├── atomic_create.pattern.yaml            # Single file + test pattern
│   ├── batch_create.pattern.yaml             # N similar files pattern
│   ├── refactor_patch.pattern.yaml           # Modify existing pattern
│   └── self_heal.pattern.yaml                # Detect + fix pattern
│
├── verification_templates/
│   ├── file_exists.verify.yaml               # Test-Path checks
│   ├── pytest_green.verify.yaml              # All tests pass
│   ├── git_clean.verify.yaml                 # No uncommitted changes
│   └── scope_valid.verify.yaml               # Files in declared scope
│
└── decision_templates/
    ├── worktree_creation.decisions.yaml      # Pre-answered questions
    ├── scope_validation.decisions.yaml       # Pre-defined rules
    └── self_healing.decisions.yaml           # Pre-authorized repairs
```

### Phase 2: Template Structure

#### Example: worktree_lifecycle.template.yaml

```yaml
# TEMPLATE: Git Worktree Lifecycle Management
# PHASE_ID: PH-04.5
# DECISIONS_MADE_AT: 2025-11-22 (template creation)
# PROVEN_USES: 0 (initial version)

meta:
  template_id: "worktree_lifecycle_v1"
  category: "infrastructure"
  estimated_time_minutes: 45
  time_savings_vs_manual: "75%"  # 45 min vs 3 hours
  
structural_decisions:
  # These NEVER change - decided once at template creation
  file_format: "python"
  module_location: "src/pipeline/worktree.py"
  test_location: "tests/pipeline/test_worktree.py"
  cli_location: "scripts/worktrees.py"
  doc_updates:
    - "docs/ARCHITECTURE.md::Git Worktree Lifecycle"
    - "docs/PHASE_PLAN.md::PH-04.5"
  
  # Standard architecture (from Dev Rules #8)
  directory_structure:
    - ".worktrees/"
    - ".ledger/patches/"
    - ".tasks/inbox/"
    - ".tasks/running/"
    - ".tasks/done/"
    - ".tasks/failed/"
  
  # Function signatures (from Phase 04.5 spec)
  required_functions:
    - "get_repo_root() -> Path"
    - "get_worktree_root() -> Path"
    - "get_base_branch() -> str"
    - "create_worktree_for_ws(run_id: str, ws_id: str) -> WorktreeInfo"
    - "validate_scope(ws_id: str, files_scope: list, files_create: list) -> dict"
    # ... (all 13 functions)

variable_sections:
  # These change per execution - but structure is fixed
  project_root: "${PROJECT_ROOT}"
  base_branch: "${BASE_BRANCH:-main}"
  run_id: "${RUN_ID}"
  ws_id: "${WS_ID}"

ground_truth_verification:
  # Observable success criteria (from Dev Rules #1)
  pre_flight:
    - cmd: "Test-Path ${PROJECT_ROOT}"
      expect: "True"
      fail_msg: "Project root does not exist - run PH-00 first"
    
    - cmd: "git status --porcelain"
      expect: ""
      fail_msg: "Base repo not clean - commit or stash changes"
  
  post_execution:
    - cmd: "Test-Path src/pipeline/worktree.py"
      expect: "True"
      
    - cmd: "Test-Path scripts/worktrees.py"
      expect: "True"
      
    - cmd: "python -m pytest tests/pipeline/test_worktree.py -q"
      expect: ".*passed.*"
      fail_msg: "Tests failed - review output"
      
    - cmd: "git status --porcelain"
      expect_pattern: "^[AM]\\s+(src/pipeline/worktree\\.py|scripts/worktrees\\.py|tests/.*|docs/.*)"
      fail_msg: "Unexpected files modified - scope violation"
  
  success_criteria:
    # ALL must pass before marking complete
    - "All post_execution checks green"
    - "No files touched outside declared scope"
    - "Git commit created with message pattern: 'PH-04.5:.*'"

execution_sequence:
  # Atomic steps - no decisions needed at runtime
  steps:
    - id: "preflight"
      pattern: "verification"
      template: "verification_templates/preflight.verify.yaml"
      on_fail: "stop"  # Never proceed with dirty base
    
    - id: "implement_module"
      pattern: "atomic_create"
      template: "execution_patterns/atomic_create.pattern.yaml"
      files:
        - path: "src/pipeline/worktree.py"
          type: "implementation"
          lines: 400-500
          sections:
            - "Module docstring"
            - "Imports"
            - "WorktreeInfo dataclass"
            - "Helper functions (1-3)"
            - "Lifecycle functions (4-10)"
            - "Scope enforcement (11)"
            - "Orphan cleanup (12-13)"
    
    - id: "implement_cli"
      pattern: "atomic_create"
      files:
        - path: "scripts/worktrees.py"
          type: "cli_tool"
          lines: 200-300
          subcommands: ["init", "list", "status", "validate-scope", "cleanup-orphans"]
    
    - id: "implement_tests"
      pattern: "atomic_create"
      files:
        - path: "tests/pipeline/test_worktree.py"
          type: "test_suite"
          test_count: 9
          coverage_target: "core_functions_only"
    
    - id: "update_docs"
      pattern: "batch_create"
      files:
        - path: "docs/ARCHITECTURE.md"
          section: "Git Worktree Lifecycle & Scope Enforcement"
          append_mode: true
        - path: "docs/PHASE_PLAN.md"
          section: "PH-04.5"
          update_mode: true
    
    - id: "verify_and_commit"
      pattern: "verification_commit"
      template: "execution_patterns/verify_commit.pattern.yaml"

parallelism:
  # Can these steps run in parallel? (from Kernel Parallelism Spec)
  parallel_eligible: false  # Sequential dependencies
  reasons:
    - "Tests depend on module implementation"
    - "Docs reference module APIs"
    - "CLI imports module functions"
  
  # But WITHIN steps, can parallelize:
  step_internal_parallelism:
    implement_tests:
      can_batch: true
      max_batch_size: 3  # Create 3 test functions per LLM turn
    update_docs:
      can_batch: true
      max_batch_size: 2  # Both doc files in one turn

self_healing:
  # Pre-authorized repairs (from Dev Rules #4)
  auto_fix_scenarios:
    - condition: "Parent directory does not exist"
      action: "create_directory"
      requires_permission: false
      
    - condition: "Import error - module not found"
      action: "install_from_requirements"
      requires_permission: false
      
    - condition: "Test failure - assertion error"
      action: "fix_and_retry"
      max_attempts: 3
      requires_permission: false
      
    - condition: "Git worktree already exists"
      action: "remove_and_recreate"
      requires_permission: true  # Destructive
      
    - condition: "Base branch does not exist"
      action: "stop_with_error"
      requires_permission: false  # Cannot auto-fix

anti_patterns:
  # From Dev Rules - what NOT to do
  forbidden_actions:
    - "Declare success without observable test output"
    - "Create 20+ file refactor in single phase"
    - "Ask permission for obvious safe actions"
    - "Load full spec before executing atomic step"
    - "Verify manually instead of programmatically"

operator_instructions:
  # For AI agent executing this template
  mindset: "operator"  # Not code generator
  
  decision_policy:
    - "NO runtime decisions - all decisions in template"
    - "If template ambiguous, fail fast with error"
    - "Document assumptions in code comments only"
  
  execution_policy:
    - "Execute atomically - one step completes before next"
    - "Verify at every step boundary"
    - "Self-heal without asking if in auto_fix_scenarios"
    - "Stop immediately on unexpected failure"
  
  communication_policy:
    - "Report observable facts only (test results, file counts)"
    - "No 'this looks right' - only ground truth"
    - "Success = all verification checks green"
```

---

## Execution Pattern Templates

### Pattern: atomic_create.pattern.yaml

```yaml
# PATTERN: Atomic Create
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
    strategy: "sequential"  # Implementation before tests
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

### Pattern: self_heal.pattern.yaml

```yaml
# PATTERN: Self-Healing Execution Loop
# USE_CASE: Run → Inspect → Fix → Re-verify
# ELIMINATES: Permission bottlenecks, manual intervention

pattern_id: "self_heal_v1"
category: "error_recovery"

pre_authorized_fixes:
  # These can execute without asking (from Dev Rules #4)
  
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
    tool: "black"  # Auto-formatter
    verify: "python -m py_compile ${file_path}"
    max_auto_attempts: 2
  
  test_failure_assertion:
    detection: "AssertionError|assert .* == .*"
    action: "analyze_and_fix_test"
    verify: "pytest ${test_file} -q"
    max_auto_attempts: 3
  
  import_cycle:
    detection: "ImportError.*circular import"
    action: "refactor_imports"
    verify: "python -m py_compile ${file_path}"
    max_auto_attempts: 1

requires_human_intervention:
  # These STOP and ask (safety critical)
  
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
  
  destructive_operation_collision:
    detection: "worktree already exists"
    action: "stop_and_ask"
    reason: "May contain uncommitted work"

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
        - "If unknown error → stop and report"
    
    4_apply_fix:
      if: "fix_authorized"
      action: "${fix.action}"
      log: "Applied auto-fix: ${fix.action}"
    
    5_re_verify:
      action: "Re-run original command"
      if_success: "break_loop"
      if_fail: "increment_iteration"
    
  loop_exit_conditions:
    success: "All checks pass"
    max_iterations_exceeded: "Report unrecoverable failure"
    human_intervention_required: "Report specific blocker"
```

---

## Verification Template System

### verification_templates/preflight.verify.yaml

```yaml
# VERIFICATION: Pre-Flight Checks
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
  
output_format:
  success: |
    ✅ Pre-flight checks passed (${passed_count}/${total_count})
  
  failure: |
    ❌ Pre-flight checks failed (${failed_count}/${total_count})
    
    Blockers:
    ${blocker_list}
    
    Fixes:
    ${fix_hints}
```

### verification_templates/pytest_green.verify.yaml

```yaml
# VERIFICATION: All Tests Pass
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
  # From Dev Rules: "all tests green" is ONLY success criterion
  - "exit_code == 0"
  - "Match success_patterns"
  - "No match failure_patterns"
  - "Output contains test count (e.g., '118/118 passed')"

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
    
    Error summary:
    ${error_summary}
```

---

## Boss Program Integration

### How Templates Accelerate Orchestration

**Before (Current UET_EXECUTION_KERNEL):**

```python
def execute_phase(phase_spec: dict):
    """
    Problem: Makes all decisions at runtime
    - Loads 300-line spec
    - Analyzes dependencies
    - Plans file structure
    - Decides verification strategy
    - Creates execution plan
    Cost: 80k tokens, 4-5 minutes
    """
    context = load_full_spec(phase_spec)  # 300+ lines
    dependencies = analyze_dag(context)   # 20k tokens
    plan = create_execution_plan(context) # 40k tokens
    validation = design_tests(context)    # 20k tokens
    
    # THEN finally execute
    result = execute_with_tool(plan)
    
    # And then figure out how to verify
    verify_manually(result)
```

**After (Template-Driven):**

```python
def execute_phase(template_id: str, context: dict):
    """
    Solution: All decisions pre-made in template
    - Template has structure baked in
    - Verification steps pre-defined
    - Self-healing rules pre-authorized
    - Only fill in variables
    Cost: < 5k tokens, < 30 seconds
    """
    template = load_template(template_id)  # Pre-compiled decisions
    
    # Verify environment (< 5 sec)
    run_verification(template.ground_truth.pre_flight)
    
    # Execute steps (decisions already made)
    for step in template.execution_sequence.steps:
        pattern = load_pattern(step.pattern)
        result = execute_pattern(pattern, context)
        
        # Auto-verify with pre-defined checks
        if not verify_step(step.ground_truth):
            if can_auto_heal(result.error):
                heal_and_retry(step)
            else:
                fail_fast(result.error)
    
    # Final verification (programmatic)
    run_verification(template.ground_truth.post_execution)
    
    return "complete"  # Only if ALL verifications pass
```

### Decision Elimination Metrics

```
Time Savings:
  Planning overhead: 4-5 min → 0 sec (template pre-compiled)
  Permission asking: 30+ sec × N → 0 sec (pre-authorized)
  Manual verification: 30+ sec × N → 2 sec × N (programmatic)
  Context loading: 300+ lines → < 50 lines (minimal context)
  
Token Savings:
  Planning: 80k tokens → < 5k tokens (95% reduction)
  Spec loading: 300+ lines → template ID (99% reduction)
  
Execution Savings:
  Phase 04.5 example: 3 hours → 45 minutes (75% faster)
  Self-healing: Manual → Automatic (100% automation)
```

---

## Template Creation Workflow

### Step 1: Extract Pattern from First Execution

When executing PH-04.5 for the first time:

```yaml
# Document decisions made during execution
decisions_log:
  - question: "What file structure?"
    answer: "src/pipeline/worktree.py + scripts/worktrees.py + tests/"
    decision_time: "2 minutes"
    
  - question: "How detailed should functions be?"
    answer: "Complete implementation, 400-500 lines total"
    decision_time: "3 minutes"
    
  - question: "What verification strategy?"
    answer: "pytest -v, check all files exist, git status clean"
    decision_time: "5 minutes"
    
  - question: "How to handle missing directories?"
    answer: "Auto-create with -Force, don't ask"
    decision_time: "2 minutes"
    
  - question: "When is phase complete?"
    answer: "All tests pass + files exist + git commit created"
    decision_time: "1 minute"

total_decision_time: 13 minutes
execution_time: 120 minutes
total_time: 133 minutes
```

### Step 2: Convert to Template

Extract decisions into reusable template:

```yaml
# Now these 13 minutes of decisions are FREE for future phases
template: "worktree_lifecycle.template.yaml"
decisions_eliminated: 5
decision_time_saved: 13 minutes

# Next similar phase (e.g., PH-05 task queue):
# - Load template: 30 seconds
# - Fill variables: 2 minutes
# - Execute: 45 minutes
# Total: 47 minutes (vs 133 minutes)
# Savings: 86 minutes (65% faster)
```

### Step 3: Generalize Pattern

Extract reusable execution pattern:

```yaml
# atomic_create.pattern.yaml
# Now ANY "create small module" phase uses this
# - PH-04.5: worktree module
# - PH-05: task queue module
# - PH-06: validator module
# - PH-06.5: recovery module

pattern_reuse_count: 4
time_saved_per_reuse: 13 minutes
total_time_saved: 52 minutes (after 4 uses)
```

---

## Batch Parallelism Integration

### Identifying Parallelizable Phases

From your Kernel Parallelism Spec, phases can run in parallel if:
- No file scope conflicts
- No sequential dependencies
- Independent ground truth verification

**Template Enhancement for Parallelism:**

```yaml
# phase_bundle.template.yaml

bundle_id: "infrastructure_foundation"
phases:
  - phase_id: "PH-04.5"
    template_id: "worktree_lifecycle"
    file_scope: ["src/pipeline/worktree.py", "scripts/worktrees.py"]
    
  - phase_id: "PH-05.1"
    template_id: "task_queue"
    file_scope: ["src/pipeline/queue.py", "scripts/task_queue.py"]
    
  - phase_id: "PH-05.2"
    template_id: "audit_logger"
    file_scope: ["src/pipeline/audit.py", "tests/test_audit.py"]

parallelism_analysis:
  # Automated conflict detection
  file_conflicts: []  # No overlapping file_scope
  dependency_conflicts: []  # No phase depends on another
  
  execution_strategy:
    parallel_eligible: true
    max_parallel: 3
    estimated_time_sequential: 135 minutes
    estimated_time_parallel: 50 minutes
    speedup: "2.7x"

execution_plan:
  batch_1:
    phases: ["PH-04.5", "PH-05.1", "PH-05.2"]
    tool_assignment:
      - tool: "claude_code_cli_1"
        phases: ["PH-04.5"]
        worktree: ".worktrees/ws-ph-04-5/"
      
      - tool: "claude_code_cli_2"
        phases: ["PH-05.1"]
        worktree: ".worktrees/ws-ph-05-1/"
      
      - tool: "claude_code_cli_3"
        phases: ["PH-05.2"]
        worktree: ".worktrees/ws-ph-05-2/"
    
    verification:
      strategy: "barrier_sync"
      wait_for: "all_phases_complete"
      then: "merge_worktrees_sequentially"
```

---

## Self-Healing Automation

### Template-Driven Auto-Fixes

**Current problem:** AI stops and asks when tools fail

**Solution:** Pre-authorize common fixes in template

```yaml
# Example from worktree_lifecycle.template.yaml

execution_steps:
  - id: "create_worktree"
    cmd: "git worktree add -B ${branch} ${path} ${base_branch}"
    
    expected_failures:
      - pattern: "fatal: '${path}' already exists"
        auto_fix:
          condition: "path_exists_but_not_worktree"
          actions:
            - "Remove-Item -Path ${path} -Recurse -Force"
            - "Retry: git worktree add -B ${branch} ${path} ${base_branch}"
          requires_permission: false
        
      - pattern: "fatal: invalid reference: ${base_branch}"
        auto_fix:
          condition: "base_branch_missing"
          actions:
            - "Report error: Base branch '${base_branch}' does not exist"
            - "Available branches:"
            - "git branch -a"
          requires_permission: false
          auto_recoverable: false
        
      - pattern: "fatal: '${path}' is not empty"
        auto_fix:
          condition: "directory_has_contents"
          actions:
            - "Backup existing content to .worktrees/.backup/${timestamp}/"
            - "Remove directory"
            - "Retry creation"
          requires_permission: true  # Potentially destructive
```

### Decision Tree for Error Handling

```yaml
error_handling_decision_tree:
  # Pre-compiled decision tree (no runtime thinking)
  
  on_error:
    1_classify:
      - "Match against known_error_patterns"
      - "Extract error_type and error_details"
    
    2_check_authorization:
      - "Is error in pre_authorized_fixes?"
      - "If yes → proceed to fix"
      - "If no → check requires_human"
    
    3_apply_fix:
      - "If auto_fix_enabled and not requires_permission:"
      - "  Execute fix.actions"
      - "  Verify fix.verify_cmd"
      - "  If verify passes → retry original"
      - "  If verify fails → escalate"
      - "Else:"
      - "  Stop and report"
    
    4_retry:
      - "Re-execute original step"
      - "If success → continue"
      - "If fail → check max_attempts"
      - "If max_attempts exceeded → fail phase"

# No runtime decisions needed - just execute decision tree
```

---

## Integration with Tool Execution Spec

### Mapping Templates to ToolWorkItems

Your Tool Execution Spec defines how work is queued and executed. Templates integrate seamlessly:

```yaml
# Enhanced ToolWorkItem structure

ToolWorkItem:
  item_id: "ITEM-001"
  workstream_id: "ws-ph-04-5-worktree"
  
  # NEW: Template reference (eliminates planning overhead)
  template_ref:
    template_id: "worktree_lifecycle_v1"
    template_path: "templates/phase_templates/worktree_lifecycle.template.yaml"
    context_vars:
      PROJECT_ROOT: "C:/Users/richg/ALL_AI/AI_Dev_Pipeline"
      BASE_BRANCH: "main"
      RUN_ID: "RUN-2025-11-22"
      WS_ID: "ws-ph-04-5-worktree"
  
  # Execution profile (from template)
  estimated_time_seconds: 2700  # 45 minutes (from template metadata)
  max_runtime_seconds: 3600     # 1 hour limit
  
  # Ground truth (from template)
  verification_steps: [
    "preflight_checks",
    "post_execution_checks",
    "pytest_green"
  ]
  
  # Self-healing (from template)
  auto_heal_enabled: true
  max_auto_heal_attempts: 3
```

### Worker Execution Flow

```python
class ToolWorker:
    """Enhanced with template support"""
    
    def execute_work_item(self, item: ToolWorkItem):
        # Load pre-compiled template (< 1 second)
        template = self.template_loader.load(item.template_ref.template_id)
        
        # Fill context variables (< 1 second)
        context = self.fill_context(template, item.template_ref.context_vars)
        
        # Execute without planning overhead
        result = self.execute_template(template, context)
        
        return result
    
    def execute_template(self, template, context):
        # Pre-flight verification (< 5 seconds)
        self.verify(template.ground_truth.pre_flight, context)
        
        # Execute steps (decisions already made)
        for step in template.execution_sequence.steps:
            pattern = self.load_pattern(step.pattern)
            
            try:
                step_result = self.execute_step(pattern, context)
                self.verify_step(step.ground_truth, step_result)
            
            except ExecutionError as e:
                # Template-driven self-healing
                if self.can_auto_heal(e, template.self_healing):
                    self.heal_and_retry(step, e, template.self_healing)
                else:
                    raise
        
        # Post-execution verification
        self.verify(template.ground_truth.post_execution, context)
        
        return ExecutionResult(status="complete")
```

---

## Metrics and ROI

### Speed Comparison

**Without Templates (Current):**
```
Phase PH-04.5 execution:
├─ Load spec: 30 seconds (300+ lines)
├─ Analyze dependencies: 60 seconds
├─ Design file structure: 120 seconds (2 min)
├─ Plan verification: 180 seconds (3 min)
├─ Create execution plan: 120 seconds (2 min)
├─ Ask permissions: 30 seconds × 3 = 90 seconds
├─ Execute: 2 hours (7200 seconds)
├─ Manual verify: 30 seconds × 5 = 150 seconds
└─ Total: ~8000 seconds (133 minutes)

Token consumption: ~80k tokens
Human interventions: 3
```

**With Templates:**
```
Phase PH-04.5 execution:
├─ Load template: 1 second (pre-compiled)
├─ Fill context: 2 seconds (just variables)
├─ Pre-flight verify: 5 seconds (programmatic)
├─ Execute: 45 minutes (2700 seconds)
├─ Auto-verify: 2 seconds × 5 = 10 seconds
└─ Total: ~2720 seconds (45 minutes)

Token consumption: ~5k tokens (94% reduction)
Human interventions: 0
```

**Speedup: 2.96x faster (133 min → 45 min)**

### Template Creation ROI

```
Template Creation Cost (One-Time):
├─ Execute phase first time: 133 minutes
├─ Document decisions: 15 minutes
├─ Create template: 30 minutes
└─ Total investment: 178 minutes

Break-Even Analysis:
├─ Time saved per use: 88 minutes
├─ Break-even point: 2 uses
├─ After 5 uses: 440 minutes saved (7.3 hours)
├─ After 10 uses: 880 minutes saved (14.7 hours)
```

### Batch Parallelism ROI

```
Sequential Execution (3 similar phases):
├─ Phase 1: 45 minutes
├─ Phase 2: 45 minutes
├─ Phase 3: 45 minutes
└─ Total: 135 minutes

Parallel Execution (with templates):
├─ All 3 phases: 50 minutes (slight overhead for coordination)
└─ Speedup: 2.7x faster
```

---

## Migration Path

### Phase 1: Template Pilot (Week 1)

Create templates for 2-3 completed phases:

```
Priority targets:
1. PH-04.5 (Git Worktree Lifecycle) - just completed
   - Extract actual decisions made
   - Document execution sequence
   - Create verification checklist

2. PH-03.5 (Aider Integration) - similar pattern
   - Tool integration phase
   - CLI + module + tests structure

3. PH-05 (Task Queue) - upcoming
   - Use template from day 1
   - Measure actual speedup
```

### Phase 2: Pattern Library (Week 2)

Extract reusable patterns:

```
Patterns to extract:
1. atomic_create - 1 module + tests + CLI
2. tool_integration - adapt external tool
3. infrastructure_setup - directories + config
4. validation_module - validators + error handling
```

### Phase 3: Verification System (Week 3)

Standardize ground truth checks:

```
Verification templates:
1. preflight.verify - environment checks
2. pytest_green.verify - test passing
3. git_clean.verify - scope validation
4. file_exists.verify - artifact creation
```

### Phase 4: Self-Healing (Week 4)

Pre-authorize common fixes:

```
Auto-fix scenarios:
1. Missing directories → create
2. Missing imports → pip install
3. Syntax errors → auto-format
4. Test failures → fix and retry (3 attempts)
```

### Phase 5: Parallel Execution (Week 5)

Enable batch parallelism:

```
Bundle similar phases:
1. Infrastructure modules (PH-04.5, PH-05.1, PH-05.2)
2. Validation modules (PH-06.x series)
3. Recovery modules (PH-06.5.x series)
```

---

## Success Metrics

### Speed Metrics
- [ ] Phase execution time reduced by 60-75%
- [ ] Planning overhead reduced by 90% (< 5k tokens)
- [ ] Verification time reduced by 90% (programmatic)
- [ ] Human interventions reduced by 95%

### Quality Metrics
- [ ] All phases pass ground truth verification
- [ ] No scope violations (files touched outside declared scope)
- [ ] Zero "hallucinated success" incidents
- [ ] Self-healing success rate > 80%

### Automation Metrics
- [ ] 90% of phases execute without human input
- [ ] 80% of errors auto-healed
- [ ] 100% of phases use templates after pilot

---

## Conclusion

Your three documents define a sophisticated autonomous execution system that's currently bottlenecked by runtime decision-making. By applying Decision Elimination principles:

**What Changes:**
1. **Templates replace planning** - 13 minutes of decisions → 2 seconds to fill template
2. **Patterns replace thinking** - Pre-defined execution sequences
3. **Programmatic verification** - 30+ seconds manual → 2 seconds automated
4. **Pre-authorized self-healing** - No permission bottlenecks
5. **Batch parallelism** - 3 phases in 50 minutes vs 135 minutes sequential

**What Stays the Same:**
- All safety guarantees (scope enforcement, ground truth)
- All quality gates (tests must pass, git must be clean)
- All architectural principles (atomic phases, worktree isolation)

**The Result:**
- 3x faster phase execution
- 94% reduction in token consumption
- 95% reduction in human intervention
- 100% maintained safety and quality

The key insight: **Speed doesn't come from better AI or faster tools. It comes from eliminating decisions through pattern recognition and ruthless template application.**

Your system already has the infrastructure. Now layer on decision elimination templates and watch execution time collapse.
