# Aider - Coordination Instructions

## Quick Start

**Read this first:** `docs/COORDINATION_GUIDE.md` - Complete coordination mechanisms guide

**Run this to check status:**
```bash
/run bash scripts/check_workstream_status.sh
```

## Aider-Specific Workflow

Aider works seamlessly with git worktrees and branches. Here's how to participate in the workstream coordination:

### 1. Check Current Status

**From main repository:**
```bash
# See what's been completed
/run git branch -a | grep "workstream/"

# See active worktrees
/run git worktree list

# Run automated status checker
/run bash scripts/check_workstream_status.sh
```

### 2. Start a New Workstream

**Example: Starting ws-ph02-schema**

```bash
# Create worktree and branch
/run git worktree add .worktrees/ws-ph02-schema -b workstream/ws-ph02-schema main

# Navigate to worktree (exit aider first, then restart in worktree)
cd .worktrees/ws-ph02-schema
aider

# Verify branch
/run git branch --show-current
# Should output: workstream/ws-ph02-schema
```

### 3. Working in a Workstream

**Add files you'll be working on:**
```bash
# Example for ws-ph02-schema
/add schema/schema.sql
/add docs/schema_design.md
```

**Check dependencies before starting:**
```bash
# Example: ws-ph02-schema has no dependencies, safe to start
/run cat .AI\ Development\ Pipeline\ Workstream\ Execution\ Plan*.md | grep -A 5 "ws-ph02-schema"
```

**During development:**
- Use aider normally to edit files
- Aider will auto-commit or you can use `/commit`

### 4. Completing a Workstream

**Review your changes:**
```bash
/run git status
/run git log --oneline -5
```

**Ensure proper commit message:**
```bash
/commit feat(ws-ph02-schema): implement database schema

- Created schema.sql with state machine tables
- Added indexes for performance
- Documented schema design

🤖 Generated with Aider

Co-Authored-By: Aider <aider@aider.chat>
```

**Return to main repository:**
```bash
/exit
cd .../  # Back to main repo
```

## Current Status (As of Last Check)

### ✅ Completed Workstreams

**Claude Code:**
- `ws-ph03-adapter-core` ✅ (Branch: `workstream/ws-ph03-adapter-core`)

**PH-00 Baseline (Already Done):**
- Module stubs created ✅
- `scripts/generate_spec_index.py` ✅ (ws-ph01-index-scanner equivalent)

### 📋 Ready to Start (No Dependencies)

**Aider Can Start Immediately:**
1. **ws-ph01-docs** (no dependencies) - Update documentation
2. **ws-ph02-schema** (no dependencies) ⭐ **RECOMMENDED FIRST** - Unblocks others
3. **ws-ph03-profiles** (no dependencies) - Create tool profiles JSON
4. **ws-ph03-docs** (no dependencies) - Update documentation

**Claude Can Start Immediately:**
1. ws-ph01-spec-mapping (dependency met: generate_spec_index.py exists ✅)
2. ws-ph01-tests (dependency met: generate_spec_index.py exists ✅)

**Codex Can Start Immediately:**
1. ws-ph01-docs (no dependencies)
2. ws-ph02-schema (no dependencies)
3. ws-ph03-profiles (no dependencies)
4. ws-ph03-docs (no dependencies)

### ⏳ Waiting for Dependencies

**Blocked workstreams:**
- ws-ph02-db-core → needs ws-ph02-schema ⭐ (any tool can do schema first)
- ws-ph02-scripts → needs ws-ph02-db-core
- ws-ph02-state-machine → needs ws-ph02-db-core
- ws-ph02-crud → needs ws-ph02-db-core
- And more... (see full dependency tree in COORDINATION_GUIDE.md)

## Checking Other AI's Work

### What Has Claude Code Done?
```bash
/run git show workstream/ws-ph03-adapter-core:src/pipeline/tools.py | head -20
```

### What Has Codex Done?
```bash
# List all workstream branches to see what exists
/run git branch -a | grep "workstream/"

# Check specific implementation
/run git log workstream/<ws_id> --oneline
```

### Is a Specific File Implemented?
```bash
# Example: Check if db.py is still a stub
/run git show main:src/pipeline/db.py | grep -E "(TODO|pass|NotImplemented)"

# If output shows TODO/pass/NotImplemented → still a stub ❌
# If no output → likely implemented ✅
```

## Aider-Specific Tips

### Using /run for Coordination
Aider's `/run` command is perfect for checking coordination status:
```bash
/run bash scripts/check_workstream_status.sh
/run git worktree list
/run git branch -a | grep workstream
```

### Auto-commit vs Manual Commit
Aider can auto-commit changes. To ensure proper workstream attribution:
```bash
# Option 1: Let aider auto-commit (it will use default message)
# Then amend the commit message:
/run git commit --amend -m "feat(ws-ph02-schema): your message here

🤖 Generated with Aider

Co-Authored-By: Aider <aider@aider.chat>"

# Option 2: Use /commit with full message
/commit feat(ws-ph02-schema): your detailed message here
```

### Working Across Multiple Files
```bash
# Add all relevant files to aider's context
/add src/pipeline/db.py
/add schema/schema.sql
/add tests/test_db.py

# Aider can now edit all of them consistently
```

### Testing Your Changes
```bash
# Run tests from within aider
/run pytest tests/

# Run specific test file
/run pytest tests/test_db.py -v

# Run the test script
/run bash scripts/test.ps1
```

## Recommended Workstream for Aider to Start

### 🎯 ws-ph02-schema (HIGHEST PRIORITY)

**Why this one?**
- No dependencies - can start immediately
- Unblocks 5+ other workstreams for all AI tools
- Clear, contained task - create SQL schema file
- High impact on overall progress

**What to do:**
```bash
# 1. Create worktree
/run git worktree add .worktrees/ws-ph02-schema -b workstream/ws-ph02-schema main

# 2. Exit and restart aider in worktree
/exit
cd .worktrees/ws-ph02-schema
aider

# 3. Add files
/add schema/schema.sql

# 4. Implement schema (ask aider to create it based on state machine requirements)
# "Create a SQLite schema for the pipeline state machine with tables for:
#  - pipeline_runs (id, name, status, created_at, updated_at)
#  - run_states (id, run_id, state, entered_at, exited_at)
#  - run_context (id, run_id, key, value)
#  Include proper indexes and foreign keys"

# 5. Commit when done
/commit feat(ws-ph02-schema): implement pipeline state machine schema

🤖 Generated with Aider

Co-Authored-By: Aider <aider@aider.chat>
```

## Communication Protocol

### When You Complete a Workstream:
1. ✅ Commit to your `workstream/<ws_id>` branch
2. ✅ Claude Code and Codex will detect it via `git branch -a`
3. ✅ No manual notification needed - git is the source of truth

### When You Need to Check Progress:
```bash
# Quick overview
/run bash scripts/check_workstream_status.sh

# Detailed check
/run git branch -a | grep workstream
/run git log --all --oneline --graph | head -30
```

### Avoiding Conflicts:
- Each AI works in separate worktree
- Each AI commits to separate branch
- No conflicts possible during development
- Integration happens later via merge

## Key Files Reference

| File | Purpose |
|------|---------|
| `docs/COORDINATION_GUIDE.md` | Full coordination mechanisms |
| `scripts/check_workstream_status.sh` | Automated status checker |
| `CODEX_COORDINATION_INSTRUCTIONS.md` | Instructions for Codex CLI |
| `AIDER_COORDINATION_INSTRUCTIONS.md` | This file - for Aider |
| `AI Development Pipeline Workstream Execution Plan (PH-01 to PH-03).md` | Full workstream definitions |

## Summary

✅ **Aider is fully compatible with the coordination system**
✅ **Use `/run` for all git and status checks**
✅ **Work in worktrees to avoid conflicts**
✅ **Start with ws-ph02-schema for maximum impact**
✅ **Git state is the single source of truth**

## Next Steps

1. Run status checker: `/run bash scripts/check_workstream_status.sh`
2. Pick a workstream from "Ready to Start" list
3. Create worktree and branch
4. Implement the workstream
5. Commit with proper attribution
6. Other AIs will see your work automatically

🚀 **Ready to contribute to parallel development!**
