# Development Rules v1.0 - DO's and DON'Ts

**Document ID:** DEV_RULES_V1  
**Version:** 1.0.0  
**Last Updated:** 2025-11-20  
**Status:** Canonical  

---

## DR-001: Overview {#DR-001}

This document defines **mandatory practices** (DO) and **strictly forbidden anti-patterns** (DON'T) for AI-driven development in the Game Board Protocol system.

**Enforcement:** These rules are enforced by the Guard Rules Engine (Phase 2B) and Validation Gateway (Phase 2C).

---

# PART I: MANDATORY PRACTICES (DO)

---

## DR-DO-001: Ground Truth Over Vibes {#DR-DO-001}

**Principle:** Base all decisions on observable CLI output, never on internal confidence or assumptions.

### DR-DO-001.1: Always Verify with CLI Commands {#DR-DO-001-1}

**DO:**
- ✅ Run `git status`, `pytest`, `Test-Path` after operations
- ✅ Inspect exit codes and stdout/stderr
- ✅ Parse test output for actual pass/fail counts
- ✅ Verify filesystem state with directory listings

**Example:**
```powershell
# Correct verification
$testResult = python -m pytest -q tests/
if ($LASTEXITCODE -ne 0) { throw "Tests failed" }
```

### DR-DO-001.2: Observable Outputs Only {#DR-DO-001-2}

**DO:**
- ✅ Base decisions **ONLY** on observable outputs (exit codes, test results, file existence)
- ✅ Treat "all tests passed" (e.g., `118/118 passed`) as the **ONLY** success criterion

**DON'T:**
- ❌ Declare success based on "this looks right" or internal confidence
- ❌ Assume tools did their job without verification
- ❌ Mark phases "complete" without observable test output

---

## DR-DO-002: Atomic Execution & Small Phases {#DR-DO-002}

**Principle:** Break work into small, verifiable, independently testable phases.

### DR-DO-002.1: Phase Atomicity {#DR-DO-002-1}

**DO:**
- ✅ Break work into small phases (1-3 modules max per phase)
- ✅ Each phase creates/modifies 1-3 files with tests
- ✅ Use patch-style minimal diffs (`+1 -1` changes)
- ✅ Execute one phase completely before moving to next

**Example Pattern:**
```
Phase 1A: Task Queue only (task_queue.py + test_task_queue.py)
Phase 1B: Audit Logger only (audit_logger.py + test_audit_logger.py)
```

### DR-DO-002.2: Sequential Completion {#DR-DO-002-2}

**DO:**
- ✅ Complete Phase N fully (all tests green) before starting Phase N+1
- ✅ Validate artifacts exist before declaring phase done

**DON'T:**
- ❌ Create giant refactors touching 20+ files
- ❌ Spend 80k+ tokens on planning without executing atomic steps
- ❌ Bundle script creation + 4+ docs into one phase
- ❌ Whole-file rewrites when patches will do

---

## DR-DO-003: Mandatory Phase Structure {#DR-DO-003}

**Principle:** Every phase must follow the universal structure specification.

### DR-DO-003.1: Required Fields {#DR-DO-003-1}

Every phase **MUST** have:

- ✅ **Phase ID & Workstream ID** (e.g., `PH-1A`, `ws-pipeline-plus-1a-task-queue`)
- ✅ **Objective** - Single tight goal
- ✅ **File Scope** - Explicit `create`, `modify`, `read_only` lists
- ✅ **Dependencies** - What must complete first, what can run parallel
- ✅ **Programmatic Acceptance Tests** - PowerShell + pytest checks
- ✅ **Pre-Flight Checks** - Verify prerequisites exist before starting

### DR-DO-003.2: Validation Requirements {#DR-DO-003-2}

**DON'T:**
- ❌ Start phases without explicit workstream IDs
- ❌ Proceed without file scope declarations
- ❌ Skip acceptance test definitions
- ❌ Ignore dependency ordering

---

## DR-DO-004: Self-Healing Execution {#DR-DO-004}

**Principle:** Autonomously detect and repair environment issues without human intervention.

### DR-DO-004.1: Self-Healing Loop {#DR-DO-004-1}

**DO:**
- ✅ Implement Run → Inspect → Fix → Re-verify loop
- ✅ Detect when tools under-deliver (missing files/dirs)
- ✅ Autonomously repair environment (create missing dirs, files)
- ✅ Re-run tests after fixes
- ✅ Only declare success after verification passes

**Workflow:**
```
1. Run command/tool
2. Inspect filesystem and outputs
3. Detect failures/missing artifacts
4. Apply targeted fix
5. Re-run validation
6. Repeat until success or max attempts
```

### DR-DO-004.2: Autonomous Repair {#DR-DO-004-2}

**DO:**
- ✅ Create missing directories with `.gitkeep` files
- ✅ Install missing dependencies (`pip install`, `npm install`)
- ✅ Fix syntax errors autonomously
- ✅ Regenerate corrupted config files

**DON'T:**
- ❌ Stop and wait for humans to fix tool failures
- ❌ Skip verification after tool execution
- ❌ Assume success without re-running tests
- ❌ Ask permission to fix obvious failures (syntax errors, test failures)

---

## DR-DO-005: Worktree & Patch Isolation {#DR-DO-005}

**Principle:** Every workstream operates in isolation with patch-based change tracking.

### DR-DO-005.1: Worktree Isolation {#DR-DO-005-1}

**DO:**
- ✅ Every workstream in isolated git worktree (`.worktrees/ws-*`)
- ✅ All edits captured as unified diff patches
- ✅ Store patches in `.ledger/patches/`
- ✅ Validate patches only touch files in declared scope
- ✅ Detect oscillation (same diff hash repeating)

**Pattern:**
```bash
git worktree add .worktrees/ws-pipeline-plus-1a-task-queue
cd .worktrees/ws-pipeline-plus-1a-task-queue
# ... make changes ...
git diff > .ledger/patches/ws-pipeline-plus-1a-{run_id}.patch
```

### DR-DO-005.2: Scope Enforcement {#DR-DO-005-2}

**DON'T:**
- ❌ Work in main worktree without isolation
- ❌ Apply patches touching files outside scope
- ❌ Skip patch metadata tracking
- ❌ Ignore oscillation detection

---

## DR-DO-006: Operator Mindset {#DR-DO-006}

**Principle:** Behave as an autonomous operator, not a passive code generator.

### DR-DO-006.1: Autonomous Operation {#DR-DO-006-1}

**DO:**
- ✅ Behave like an operator: run commands, inspect outputs, fix environment
- ✅ Proceed with obvious next safe action (don't ask permission)
- ✅ Make decisions based on CLI output, not assumptions
- ✅ Use `Get-ChildItem`, `git status` to discover actual state

**Example:**
```
# Good: Autonomous
Tests failed → Inspect error → Fix code → Re-run tests

# Bad: Passive
Tests failed → Ask "Would you like me to fix the tests?"
```

### DR-DO-006.2: Discovery Over Assumption {#DR-DO-006-2}

**DON'T:**
- ❌ Act as passive code generator
- ❌ Ask "Would you like me to..." for obvious next steps
- ❌ Create permission bottlenecks
- ❌ Hallucinate file structure without verifying on disk

---

## DR-DO-007: Test-Driven Everything {#DR-DO-007}

**Principle:** Tests are mandatory, not optional. No phase completes without passing tests.

### DR-DO-007.1: Test Requirements {#DR-DO-007-1}

**DO:**
- ✅ Tests **MUST** exist before or be created as part of phase
- ✅ Run deterministic CLI commands (`python -m pytest -q tests/test_*.py`)
- ✅ Only accept "all tests green" as completion
- ✅ Cover core subsystems: task queue, audit, patch manager, validators, adapters

**Coverage Requirements:**
- Filesystem structure validation (`Test-Path`)
- Unit tests for modules (`pytest`)
- Integration tests for workflows
- Schema validation

### DR-DO-007.2: Test Verification {#DR-DO-007-2}

**DON'T:**
- ❌ Complete phases without tests
- ❌ Skip pytest or filesystem validation
- ❌ Use conversational reasoning as basis for completion
- ❌ Declare "tested & verified" without observable test output

---

## DR-DO-008: Standard Architecture Layout {#DR-DO-008}

**Principle:** Follow the established architecture created by Phase 0.

### DR-DO-008.1: Required Directories {#DR-DO-008-1}

**DO:** Phase 0 creates these (all subsequent phases depend on them):

- ✅ `.tasks/queued/`, `.tasks/running/`, `.tasks/complete/`, `.tasks/failed/`
- ✅ `.ledger/`
- ✅ `.runs/`
- ✅ `config/schema.json`
- ✅ `config/validation_rules.json`

**Verification:**
```powershell
@('.tasks\queued', '.tasks\running', '.tasks\complete', '.tasks\failed', 
  '.ledger', '.runs') | ForEach-Object { 
    if (-not (Test-Path $_)) { throw "Missing $_" }
}
```

### DR-DO-008.2: Architecture Consistency {#DR-DO-008-2}

**DON'T:**
- ❌ Invent new architecture on the fly
- ❌ Create ad-hoc root-level subsystems
- ❌ Contradict established queue/ledger/runs structure

---

# PART II: ANTI-PATTERNS (DON'T)

---

## DR-DONT-001: Hallucination of Success {#DR-DONT-001}

**Anti-Pattern:** Declaring completion without waiting for observable verification.

### DR-DONT-001.1: What Happened {#DR-DONT-001-1}

- AI declared "Complete ✅" and "Tested & Verified" while pytest was still running
- No observable exit code or test output, but claimed specific behaviors passed

### DR-DONT-001.2: Rule Violated {#DR-DONT-001-2}

**Violated:** DR-DO-001 (Ground Truth Over Vibes)

### DR-DONT-001.3: Fix {#DR-DONT-001-3}

**Always:**
- Wait for test completion
- Inspect exit codes (`$LASTEXITCODE`, `$?`)
- Verify output contains expected success patterns
- Never declare success based on assumptions

---

## DR-DONT-002: Planning Loop Trap {#DR-DONT-002}

**Anti-Pattern:** Endless planning without atomic execution.

### DR-DONT-002.1: What Happened {#DR-DONT-002-1}

- 80k+ token planning sessions with no atomic execution
- Multiple heavyweight `Plan()` calls consuming 4-5 minutes each
- No pytest, git worktree, or patch generation

### DR-DONT-002.2: Rule Violated {#DR-DONT-002-2}

**Violated:** DR-DO-002 (Atomic Execution)

### DR-DONT-002.3: Fix {#DR-DONT-002-3}

**Instead:**
- Execute Phase 0 immediately (create one file + test)
- Then iterate with small phases
- Plan → Execute → Verify → Next Phase

---

## DR-DONT-003: Permission Bottlenecks {#DR-DONT-003}

**Anti-Pattern:** Asking for permission on obvious next steps.

### DR-DONT-003.1: What Happened {#DR-DONT-003-1}

- AI repeatedly asked "Would you like me to..."
- Paused for user input when next step was obvious

### DR-DONT-003.2: Rule Violated {#DR-DONT-003-2}

**Violated:** DR-DO-006 (Operator Mindset)

### DR-DONT-003.3: Fix {#DR-DONT-003-3}

**Proceed autonomously with:**
- Creating missing directories
- Installing dependencies
- Fixing syntax errors
- Re-running tests after fixes

---

## DR-DONT-004: Context Pollution {#DR-DONT-004}

**Anti-Pattern:** Loading massive context without executing atomic steps.

### DR-DONT-004.1: What Happened {#DR-DONT-004-1}

- Loading 300+ line specs before any atomic step
- Designing 20+ workstream plans without executing one
- Giant refactor intent touching 65+ files

### DR-DONT-004.2: Rule Violated {#DR-DONT-004-2}

**Violated:** DR-DO-005 (Strict Isolation) & DR-DO-002 (Atomic Phasing)

### DR-DONT-004.3: Fix {#DR-DONT-004-3}

**Instead:**
- Start with single test fixture
- Modify one module
- Validate
- Iterate

---

## DR-DONT-005: Trusting Tools Without Verification {#DR-DONT-005}

**Anti-Pattern:** Assuming tools succeeded without checking filesystem.

### DR-DONT-005.1: What Happened {#DR-DONT-005-1}

- Aider told to create dirs/files but didn't
- AI assumed success without checking filesystem

### DR-DONT-005.2: Rule Violated {#DR-DONT-005-2}

**Violated:** DR-DO-001 (CLI-First, Never Vibes)

### DR-DONT-005.3: Fix {#DR-DONT-005-3}

**Always:**
- Verify artifacts exist after tool execution (`Test-Path`, `ls`)
- Self-heal if missing
- Re-run validation

---

## DR-DONT-006: Declaring Complete Without Programmatic Acceptance {#DR-DONT-006}

**Anti-Pattern:** Marking phases complete without running acceptance tests.

### DR-DONT-006.1: What Happened {#DR-DONT-006-1}

- Copied files once, marked "✅ COMPLETED"
- No `git status`, no tests, no validation

### DR-DONT-006.2: Rule Violated {#DR-DONT-006-2}

**Violated:** DR-DO-007 (Test-Driven Everything)

### DR-DONT-006.3: Fix {#DR-DONT-006-3}

**Required:**
- Run acceptance tests
- Verify all checks pass
- Inspect test output
- Only then mark complete

---

# PART III: THE GOLDEN WORKFLOW

---

## DR-GOLD-001: Standard Execution Workflow {#DR-GOLD-001}

Every phase **MUST** follow this workflow:

### Step 1: Pre-Flight Check {#DR-GOLD-001-1}

- Verify prerequisites exist
- If fail → repair & retry
- Do not proceed if blocked

### Step 2: Execute Atomic Phase {#DR-GOLD-001-2}

- Run workstream command (`--ws-id`)
- Isolated git worktree
- Small patch-style changes

### Step 3: Inspect Reality {#DR-GOLD-001-3}

- `git status`
- `Test-Path` for required files
- `pytest -q tests/test_*.py`

### Step 4: Self-Heal if Needed {#DR-GOLD-001-4}

- Detect missing artifacts
- Create dirs/files directly
- Fix test failures

### Step 5: Re-Verify {#DR-GOLD-001-5}

- Run acceptance tests again
- All tests green? (e.g., `118/118`)

### Step 6: ✅ ONLY THEN: Mark Complete {#DR-GOLD-001-6}

- Document completion in ledger
- Update phase state
- Unblock dependent phases

---

## DR-GOLD-002: Success Metrics {#DR-GOLD-002}

A phase is **ONLY** complete when:

- ✅ All programmatic tests pass (observable output like `118/118 passed`)
- ✅ All required files/dirs exist (verified via CLI)
- ✅ Git status is clean or matches expected changes
- ✅ Patches stored in ledger with metadata
- ✅ No files touched outside declared scope

**Formula:**
```
Complete = Tests_Pass AND Files_Exist AND Scope_Valid AND Patches_Stored
```

---

## DR-999: Cross-References {#DR-999}

This specification is enforced by:

**Related Specifications:**
- **UPS-*** - Universal Phase Specification
- **PPS-*** - PRO Phase Specification

**Enforcement Components:**
- Guard Rules Engine (Phase 2B)
- Validation Gateway (Phase 2C)
- Patch Manager (Phase 4A)

---

## DR-1000: Version History {#DR-1000}

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2025-11-20 | Initial machine-readable version with stable IDs | Game Board Protocol |

---

**END OF SPECIFICATION**
