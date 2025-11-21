# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Critical Rules (From Parent .claude/rules/)

### DateTime Standard
**HIGHEST PRIORITY**: Always use real system datetime, never placeholders or estimates.

```bash
# Get current datetime in ISO 8601 format
date -u +"%Y-%m-%dT%H:%M:%SZ"

# Windows PowerShell
Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
```

- **Required format**: `YYYY-MM-DDTHH:MM:SSZ` (UTC with Z suffix)
- **Never use**: Placeholders like `[Current ISO date/time]` or estimates
- **Always preserve**: Original `created` dates, only update `updated` fields
- **See**: `../../.claude/rules/datetime.md` for full specification

### Path Standards
**Protect privacy and ensure portability**:

```markdown
# ✅ CORRECT - Relative paths
- `internal/auth/server.go`
- `../project-name/src/components/Button.tsx`
- `.claude/commands/pm/sync.md`

# ❌ WRONG - Absolute paths expose usernames
- `/Users/username/project/internal/auth/server.go`
- `C:\Users\username\project\cmd\server\main.go`
```

- **Always use**: Relative paths from project root
- **Never expose**: User directories or absolute local paths
- **Cross-project refs**: Use `../project-name/` format
- **See**: `../../.claude/rules/path-standards.md` for full specification

### GitHub Operations
**Repository protection required**:

```bash
# MUST CHECK before ANY GitHub write operation
remote_url=$(git remote get-url origin 2>/dev/null || echo "")
if [[ "$remote_url" == *"automazeio/ccpm"* ]]; then
  echo "❌ ERROR: Cannot modify template repository!"
  echo "Fork or create your own repo first"
  exit 1
fi
```

- **Required for**: Issue creation/editing, PR creation, comments
- **Trust gh CLI**: Don't pre-check auth, handle failures gracefully
- **Error format**: `❌ {What failed}: {Exact solution}`
- **See**: `../../.claude/rules/github-operations.md` for full specification

### Standard Patterns
**Core principles for all operations**:

1. **Fail Fast** - Check critical prerequisites, then proceed
2. **Trust the System** - Don't over-validate things that rarely fail
3. **Clear Errors** - Show exactly what failed and how to fix it
4. **Minimal Output** - Show what matters, skip decoration

```markdown
# ✅ GOOD - Concise and actionable
✅ Done: 3 files created
Failed: auth.test.js (syntax error - line 42)

# ❌ BAD - Too verbose
🎯 Starting operation...
📋 Validating prerequisites...
✅ Step 1 complete
✅ Step 2 complete
```

- **See**: `../../.claude/rules/standard-patterns.md` for full specification

### Test Execution
**Always use test-runner agent**:

- **No mocking** - Use real services for accurate results
- **Verbose output** - Capture everything for debugging
- **Check test structure first** - Before assuming code bugs
- **Cleanup after**: Kill test processes properly
- **See**: `../../.claude/rules/test-execution.md` for full specification

### Worktree Operations
**For parallel development and epic workflows**:

```bash
# Create worktree from clean main
git checkout main && git pull origin main
git worktree add ../epic-{name} -b epic/{name}

# Work in worktree
cd ../epic-{name}
git add {files}
git commit -m "Issue #{number}: {description}"
```

- **One worktree per epic** - Not per issue
- **Clean before create** - Always start from updated main
- **Commit frequently** - Small commits merge easier
- **See**: `../../.claude/rules/worktree-operations.md` for full specification

### Agent Coordination
**For parallel agent workflows in same worktree**:

1. **File-level parallelism** - Different files = no conflicts
2. **Explicit coordination** - Same file = coordinate explicitly
3. **Fail fast** - Surface conflicts immediately
4. **Human resolution** - Never auto-merge conflicts

```bash
# Before modifying shared file
git status {file}
if [[ $(git status --porcelain {file}) ]]; then
  echo "Waiting for {file} to be available..."
fi
```

- **See**: `../../.claude/rules/agent-coordination.md` for full specification

## Overview

This directory contains **Game Board Protocol** specifications - a methodology for autonomous AI development through strictly validated phases. This is a **specification repository**, not executable code. The specifications define how AI agents should execute development phases with mandatory validation gates, self-healing behavior, and patch-based isolation.

## Core Concepts

### Game Board Protocol
A framework that enforces deterministic, verifiable development through:
- **Phases**: Atomic development units with unique IDs (e.g., Phase 0, Phase 1A, Phase 1B)
- **Workstreams**: Machine-readable phase definitions with `ws-{project}-{phase}-{slug}` naming
- **Acceptance Tests**: CLI-based programmatic validation (never "vibes" or conversational claims)
- **Isolation**: Git worktrees and patch files for all changes
- **Self-Healing**: Autonomous detection and repair of tool failures

### Ground Truth Principle
**CLI outputs are the sole source of truth.** Never declare success without:
- Exit code 0 from test commands
- Observable test output (e.g., "44/44 passed")
- Filesystem verification via `Test-Path` or equivalent
- Git status matching expectations

## Key Documents

### Specification Files

**UNIVERSAL PHASE SPECIFICATION.txt** - Canonical phase structure definition:
- Phase identity and metadata requirements
- Mandatory fields: `phase_id`, `workstream_id`, `objective`, `file_scope`, `acceptance_tests`, `dependencies`
- Pre-flight checks, execution loop, completion gates
- Operator execution standard (CLI-first, self-healing, worktree isolation)

**ExecutionReque_Validator_Orchestrator_ Game Board protocol.md** - System architecture:
- ExecutionRequest validation engine design
- Prompt renderer for strict-mode AI instructions
- Orchestrator pattern for tool dispatch
- Phase breakdown: PH-00 through PH-06

**DEVELOPMENT RULES DO and DONT.md** - Operational rules:
- DO: Ground truth via CLI, atomic execution, self-healing loops, worktree isolation
- DON'T: Hallucinate success, giant refactors, permission bottlenecks, context pollution

**2025- ANTI-PATTERN FORENSICS.md** - Historical failure analysis:
- Hallucination of success (claiming "Complete" without test output)
- Planning loop trap (80k+ token plans without atomic execution)
- Permission bottlenecks (asking instead of doing)
- Context pollution (huge specs before any atomic step)

**PRO_Phase Specification mandatory structure.md** - Normative phase template:
- Required phase fields with YAML examples
- File scope declaration (create/modify/read_only)
- Standard directory layout (.tasks/, .ledger/patches/, .runs/)
- Anti-pattern blocklist with enforcement rules

**PRO_fastdev.md** - Working example of successful phase execution:
- Shows Phase 0 through Phase 2 implementation
- Demonstrates self-healing (detecting Aider under-delivery, creating files directly)
- Test-driven validation (30/30 tests passing → 44/44 tests passing)
- Patch management implementation with full test coverage

## Mandatory Architecture

All projects following this protocol must have:

```
.tasks/
  inbox/      # New tasks as JSON
  running/    # Tasks being executed
  done/       # Successfully completed
  failed/     # Failed tasks
.ledger/
  patches/    # All patch files
.runs/        # Execution logs, run IDs
schema/
  migrations/ # Database migrations (e.g., 001_add_patches_table.sql)
config/
  router.config.yaml  # Tool routing rules
```

## Phase Structure (Mandatory)

Every phase MUST include:

1. **Identity**: `phase_id` and `workstream_id`
2. **Objective**: Single, tight goal
3. **File Scope**: Explicit `create`, `modify`, `read_only` lists
4. **Dependencies**: `must_follow` and `may_run_parallel_with`
5. **Pre-Flight**: Environment and prerequisite checks
6. **Acceptance Tests**: Programmatic PowerShell/pytest commands
7. **Success Criteria**: Observable state, all tests green

## Execution Workflow (Golden Path)

```
1. Pre-Flight Check
   ↓ Verify prerequisites exist
   ↓ If fail → repair & retry

2. Execute Atomic Phase
   ↓ Run workstream command (e.g., python scripts/run_workstream.py --ws-id ...)
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
   ↓ All tests green?

6. ✅ ONLY THEN: Mark Complete
```

## Strictly Forbidden Anti-Patterns

1. **Hallucination of Success**: Declaring "Complete" without observable CLI proof
2. **Planning Loop Trap**: 50k+ token plans without atomic execution
3. **Permission Bottlenecks**: Asking "Would you like me to..." for obvious safe actions
4. **Context Pollution**: Loading huge specs before any atomic step
5. **Giant Refactors**: 20+ file changes without phase breakdown and worktree isolation
6. **Trusting Tools Blindly**: Assuming Aider/Codex created files without verification
7. **Completing Without Tests**: No phase is done unless all tests pass
8. **Editing Outside Scope**: Touching files not in declared `file_scope`

## Working with These Specifications

### When Reading/Modifying Specs

These are **normative documents** - they define how AI agents must behave. When editing:

- Maintain the strict MUST/MUST NOT language
- Keep examples concrete and CLI-based
- Any new rule should have a corresponding anti-pattern example
- Preserve the phase structure template

### When Implementing Systems Based on These Specs

Reference the canonical phase template in PRO_Phase Specification mandatory structure.md. Every implementation phase should:

1. Start with Pre-Flight checks
2. Use the Run → Inspect → Fix → Re-verify loop
3. Store patches in .ledger/patches/
4. Record outcomes in .runs/ or database
5. Only mark complete when all acceptance tests pass

### Testing Philosophy

- Tests created WITH the implementation (not after)
- Deterministic CLI commands only
- Coverage for: task queue, audit logging, patch manager, validators, adapters
- Success = "N/N tests passed" observable in output
- Failure = any test fails, any required file missing, any scope violation

## Self-Healing Behavior

When tools under-deliver (Aider doesn't create files, tests fail, dirs missing):

1. **Detect** via CLI verification (Test-Path, git status, pytest)
2. **Repair** directly (New-Item, Set-Content, python -c writes)
3. **Re-verify** acceptance tests
4. **Never ask permission** for obvious fixes

Example from PRO_fastdev.md:
```powershell
# Aider was told to create dirs but didn't
# AI detects and repairs:
$dirs = @('.tasks\inbox', '.tasks\running', '.tasks\done', '.tasks\failed')
foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    New-Item -ItemType File -Force -Path "$dir\.gitkeep" | Out-Null
}
```

## Key Success Patterns (from PRO_fastdev.md)

- Phase 0: Bootstrap (dirs, schema, config) → 9 acceptance checks pass
- Phase 1A & 1B: Parallel execution (task queue + audit logger) → 30/30 tests pass
- Phase 2: Patch manager → 14/14 tests pass
- Total: 44/44 tests passing = objective completion proof

Each phase:
- Detected tool under-delivery (Aider didn't create files)
- Created implementation directly
- Fixed datetime/ULID/lock file bugs
- Re-ran tests until all green
- Only then marked complete

## Machine Readability Principles (how to optimized for machine readability.md)

When authoring specifications:
- Use structured delimiters: [SECTION_NAME]
- Explicit state enums: `pending | running | completed | failed`
- File scope declarations before task lists
- Programmatic acceptance blocks (PowerShell/pytest)
- Avoid narrative fluff, prefer deterministic commands

## Common Pitfalls to Avoid

1. **Running tests in background without capturing output** - Always wait for exit code
2. **Assuming tool success without git diff check** - Verify actual file changes
3. **Creating multi-file plans without Phase 0 execution** - Execute one atomic phase first
4. **Bundling scripts + 4+ docs in one phase** - Keep phases focused and small
5. **Copying files once and declaring complete** - Run acceptance tests afterward

## When Working in This Repository

This is a **specification repository**. When asked to implement features:

1. **Don't write code here** - These are design documents
2. **Reference existing specs** - Use them as normative sources
3. **Maintain consistency** - New specs should follow existing structure
4. **Update anti-patterns** - Add forensics when new failure patterns emerge
5. **Keep examples concrete** - Show actual CLI commands, not pseudo-code

## Integration with Parent Pipeline

These specifications define the methodology implemented in the parent `pipeline_plus/` directory:
- `core/state/` - Task queue, audit logger (Phase 1A/1B implementations)
- `core/engine/` - Patch manager, orchestrator (Phase 2+ implementations)
- `scripts/` - Workstream runners and validators
- `schema/` - Database migrations and validation schemas

See parent CLAUDE.md for executable architecture details.
