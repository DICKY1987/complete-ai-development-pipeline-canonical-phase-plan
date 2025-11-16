# Codex CLI - Coordination Instructions

## Quick Start

**Read this first:** `docs/COORDINATION_GUIDE.md` - Complete coordination mechanisms guide

**Run this to check status:**
```bash
bash scripts/check_workstream_status.sh
```

## How to Check What Claude Code Has Done

### 1. List All Workstream Branches
```bash
git branch -a | grep "workstream/"
```

### 2. See Active Worktrees
```bash
git worktree list
```

### 3. Check Specific File Implementation
```bash
# Example: Check if Claude completed ws-ph03-adapter-core
git show workstream/ws-ph03-adapter-core:src/pipeline/tools.py | grep "def run_tool"
```

## Current Status (As of Last Check)

### ✅ Completed Workstreams

**Claude Code:**
- `ws-ph03-adapter-core` ✅ (Branch: `workstream/ws-ph03-adapter-core`)

**PH-00 Baseline (Already Done):**
- Module stubs created ✅
- `scripts/generate_spec_index.py` ✅ (ws-ph01-index-scanner equivalent)

### 📋 Ready to Start (No Dependencies)

**Codex Can Start Immediately:**
1. ws-ph01-docs (no dependencies)
2. ws-ph02-schema (no dependencies)
3. ws-ph03-profiles (no dependencies)
4. ws-ph03-docs (no dependencies)

**Claude Can Start Immediately:**
1. ws-ph01-spec-mapping (dependency met: generate_spec_index.py exists ✅)
2. ws-ph01-tests (dependency met: generate_spec_index.py exists ✅)

### ⏳ Waiting for Dependencies

**Codex workstreams blocked:**
- ws-ph02-db-core → needs ws-ph02-schema (Codex)
- ws-ph02-scripts → needs ws-ph02-db-core (Codex)
- ws-ph02-docs → needs ws-ph02-state-machine (Claude)

**Claude workstreams blocked:**
- ws-ph02-state-machine → needs ws-ph02-db-core (Codex)
- ws-ph02-crud → needs ws-ph02-db-core (Codex)
- ws-ph02-tests → needs ws-ph02-state-machine + ws-ph02-crud (both Claude)
- ws-ph03-db-integration → needs ws-ph02-crud (Claude)
- ws-ph03-tests → needs ws-ph03-db-integration (Claude)

## Next Steps for Codex

### Recommended Order:
1. **ws-ph02-schema** (creates schema/schema.sql) - Unblocks ws-ph02-db-core
2. **ws-ph02-db-core** (implements db.py) - Unblocks Claude's PH-02 work
3. **ws-ph03-profiles** (creates config/tool_profiles.json)
4. **ws-ph01-docs** (updates documentation)
5. **ws-ph03-docs** (updates documentation)
6. **ws-ph02-scripts** (needs ws-ph02-db-core)
7. **ws-ph02-docs** (needs Claude's ws-ph02-state-machine)

## Before Starting Any Workstream

```bash
# 1. Check dependencies (see COORDINATION_GUIDE.md)
# 2. Create worktree
git worktree add .worktrees/<ws_id> -b workstream/<ws_id> main

# 3. Navigate to worktree
cd .worktrees/<ws_id>

# 4. Verify you're on correct branch
git branch --show-current
# Should output: workstream/<ws_id>

# 5. Do your work...

# 6. Commit when done
git add <files>
git commit -m "feat(<ws_id>): <description>

<details>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Communication Protocol

### When You Complete a Workstream:
1. Commit to your `workstream/<ws_id>` branch ✅
2. Claude Code will detect it via `git branch -a` or `git worktree list`
3. No need to notify manually - git state is the source of truth

### When You Need to Check Claude's Progress:
```bash
# Quick check
bash scripts/check_workstream_status.sh

# Detailed check of specific workstream
git log workstream/<ws_id> --oneline
git show workstream/<ws_id>:path/to/file.py
```

## Key Files

- **Coordination Guide:** `docs/COORDINATION_GUIDE.md`
- **Status Checker:** `scripts/check_workstream_status.sh`
- **Workstream Plan:** `AI Development Pipeline Workstream Execution Plan (PH-01 to PH-03) .md`

## Summary

✅ **Coordination mechanism is in place**
✅ **Both tools can track each other via git commands**
✅ **Automated status checker available**
✅ **Dependencies clearly documented**

🚀 **Ready to start parallel development!**
