---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-UET_DEVELOPMENT_RULES-072
---

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   📋 DEVELOPMENT RULES: DO's and DON'Ts

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   ✅ MUST DO - Mandatory Practices

   1. Ground Truth Over Vibes

   DO:

     - ✅ Always verify with CLI commands (git status, pytest, Test-Path)
     - ✅ Base decisions ONLY on observable outputs (exit codes, test results, file existence)
     - ✅ Treat "all tests passed" (e.g., 118/118 passed) as the ONLY success criterion

   DON'T:

     - ❌ Declare success based on "this looks right" or internal confidence
     - ❌ Assume tools did their job without verification
     - ❌ Mark phases "complete" without observable test output

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   2. Atomic Execution & Small Phases

   DO:

     - ✅ Break work into small, verifiable phases (e.g., Phase 1A: Task Queue only)
     - ✅ Each phase creates 1-3 modules max with tests
     - ✅ Use patch-style minimal diffs (+1/-1 changes)
     - ✅ Execute one phase completely before moving to next

   DON'T:

     - ❌ Create giant refactors touching 20+ files
     - ❌ Spend 80k+ tokens on planning without executing atomic steps
     - ❌ Bundle script creation + 4+ docs into one phase
     - ❌ Whole-file rewrites when patches will do

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   3. Mandatory Phase Structure

   DO: Every phase MUST have:

     - ✅ Phase ID & Workstream ID (e.g., ws-pipeline-plus-1a-task-queue)
     - ✅ Objective - Single tight goal
     - ✅ File Scope - Explicit create, modify, read_only lists
     - ✅ Dependencies - What must complete first, what can run parallel
     - ✅ Programmatic Acceptance Tests - PowerShell + pytest checks
     - ✅ Pre-Flight Checks - Verify prerequisites exist before starting

   DON'T:

     - ❌ Start phases without explicit workstream IDs
     - ❌ Proceed without file scope declarations
     - ❌ Skip acceptance test definitions
     - ❌ Ignore dependency ordering

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   4. Self-Healing Execution

   DO:

     - ✅ Run → Inspect → Fix → Re-verify loop
     - ✅ Detect when tools under-deliver (missing files/dirs)
     - ✅ Autonomously repair environment (create missing dirs, files)
     - ✅ Re-run tests after fixes
     - ✅ Only declare success after verification passes

   DON'T:

     - ❌ Stop and wait for humans to fix tool failures
     - ❌ Skip verification after tool execution
     - ❌ Assume success without re-running tests
     - ❌ Ask permission to fix obvious failures (syntax errors, test failures)

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   5. Worktree & Patch Isolation

   DO:

     - ✅ Every workstream in isolated git worktree (.worktrees/ws-*)
     - ✅ All edits captured as unified diff patches
     - ✅ Store patches in .ledger/patches/
     - ✅ Validate patches only touch files in declared scope
     - ✅ Detect oscillation (same diff hash repeating)

   DON'T:

     - ❌ Work in main worktree without isolation
     - ❌ Apply patches touching files outside scope
     - ❌ Skip patch metadata tracking
     - ❌ Ignore oscillation detection

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   6. Operator Mindset

   DO:

     - ✅ Behave like an operator: run commands, inspect outputs, fix environment
     - ✅ Proceed with obvious next safe action (don't ask permission)
     - ✅ Make decisions based on CLI output, not assumptions
     - ✅ Use Get-ChildItem, git status to discover actual state

   DON'T:

     - ❌ Act as passive code generator
     - ❌ Ask "Would you like me to..." for obvious next steps
     - ❌ Create permission bottlenecks
     - ❌ Hallucinate file structure without verifying on disk

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   7. Test-Driven Everything

   DO:

     - ✅ Tests MUST exist before or be created as part of phase
     - ✅ Run deterministic CLI commands (python -m pytest -q tests/test_*.py)
     - ✅ Only accept "all tests green" as completion
     - ✅ Cover core subsystems: task queue, audit, patch manager, validators, adapters

   DON'T:

     - ❌ Complete phases without tests
     - ❌ Skip pytest or filesystem validation
     - ❌ Use conversational reasoning as basis for completion
     - ❌ Declare "tested & verified" without observable test output

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   8. Standard Architecture Layout

   DO: Required directories (Phase 0 creates these):

     - ✅ .tasks/inbox/, .tasks/running/, .tasks/done/, .tasks/failed/
     - ✅ .ledger/patches/
     - ✅ .runs/
     - ✅ schema/migrations/001_add_patches_table.sql
     - ✅ config/router.config.yaml

   DON'T:

     - ❌ Invent new architecture on the fly
     - ❌ Create ad-hoc root-level subsystems
     - ❌ Contradict established queue/ledger/runs structure

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   ❌ ANTI-PATTERNS - Strictly Forbidden

   1. Hallucination of Success

   What Happened:

     - AI declared "Complete ✅" and "Tested & Verified" while pytest was still running
     - No observable exit code or test output, but claimed specific behaviors passed

   Rule Violated: Ground Truth over Vibes

   Fix: Always wait for test completion, inspect exit codes, verify output

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   2. Planning Loop Trap

   What Happened:

     - 80k+ token planning sessions with no atomic execution
     - Multiple heavyweight Plan() calls consuming 4-5 minutes each
     - No pytest, git worktree, or patch generation

   Rule Violated: Atomic Execution

   Fix: Execute Phase 0 immediately (create one file + test), then iterate

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   3. Permission Bottlenecks

   What Happened:

     - AI repeatedly asked "Would you like me to..."
     - Paused for user input when next step was obvious

   Rule Violated: Operator Mindset

   Fix: Proceed autonomously with obvious safe actions

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   4. Context Pollution

   What Happened:

     - Loading 300+ line specs before any atomic step
     - Designing 20+ workstream plans without executing one
     - Giant refactor intent touching 65+ files

   Rule Violated: Strict Isolation & Atomic Phasing

   Fix: Start with single test fixture, modify one module, validate, iterate

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   5. Trusting Tools Without Verification

   What Happened:

     - Aider told to create dirs/files but didn't
     - AI assumed success without checking filesystem

   Rule Violated: CLI-First, Never Vibes

   Fix: Always verify artifacts exist after tool execution, self-heal if missing

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   6. Declaring Complete Without Programmatic Acceptance

   What Happened:

     - Copied files once, marked "✅ COMPLETED"
     - No git status, no tests, no validation

   Rule Violated: Test-Driven Everything

   Fix: Run acceptance tests, verify all checks pass before completion

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   🎯 THE GOLDEN WORKFLOW

     1. Pre-Flight Check
        ↓ Verify prerequisites exist
        ↓ If fail → repair & retry

     2. Execute Atomic Phase
        ↓ Run workstream command (--ws-id)
        ↓ Isolated git worktree
        ↓ Small patch-style changes

     3. Inspect Reality
        ↓ git status
        ↓ Test-Path for required files
        ↓ pytest -q tests/test_*.py

     4. Self-Heal if Needed
        ↓ Detect missing artifacts
        ↓ Create dirs/files directly
        ↓ Fix test failures

     5. Re-Verify
        ↓ Run acceptance tests again
        ↓ All tests green? (e.g., 118/118)

     6. ✅ ONLY THEN: Mark Complete

   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

   📊 Success Metrics

   A phase is ONLY complete when:

     - ✅ All programmatic tests pass (observable output like 118/118 passed)
     - ✅ All required files/dirs exist (verified via CLI)
     - ✅ Git status is clean or matches expected changes
     - ✅ Patches stored in ledger with metadata
     - ✅ No files touched outside declared scope