# Workstream Coordination Guide
## For Claude Code & Codex CLI Collaboration

This guide explains how Claude Code and Codex CLI can coordinate their work and track each other's progress across the 17 workstreams in phases PH-01 through PH-03.

---

## Overview

**Repository:** `Complete AI Development Pipeline – Canonical Phase Plan`
**Working Method:** Git worktrees with isolated branches
**Branch Pattern:** `workstream/<ws_id>`
**Worktree Path:** `.worktrees/<ws_id>/`

**Division of Labor:**
- **Claude Code:** 8 hard/complex workstreams (state machine, CRUD, tests, tool adapter)
- **Codex CLI:** 9 easy/mechanical workstreams (stubs, schema, docs, profiles)

---

## Coordination Mechanisms

### 1. Check Active Worktrees

**Command:**
```bash
git worktree list
```

**What it shows:**
- All active worktree directories
- Which branch each worktree is on
- Current commit hash for each worktree

**Example output:**
```
C:/Users/richg/.../Complete AI Development Pipeline...    61e6aa6 [main]
C:/Users/richg/.../.worktrees/ws-ph03-adapter-core         9730936 [workstream/ws-ph03-adapter-core]
C:/Users/richg/.../.worktrees/ws-ph01-index-scanner        abc1234 [workstream/ws-ph01-index-scanner]
```

**Interpretation:**
- If `.worktrees/ws-ph01-index-scanner` exists → Codex has started ws-ph01-index-scanner
- If `.worktrees/ws-ph03-adapter-core` exists → Claude has started ws-ph03-adapter-core

---

### 2. Check All Workstream Branches

**Command:**
```bash
git branch -a
```

**What it shows:**
- All local branches including workstream branches
- Remote branches
- Current branch (marked with *)

**Example output:**
```
* main
+ workstream/ws-ph03-adapter-core
  workstream/ws-ph01-index-scanner
  workstream/ws-ph02-schema
  remotes/origin/main
```

**Interpretation:**
- `+` indicates a worktree is checked out on this branch
- Branches prefixed with `workstream/` are active workstreams
- Count workstream branches to see how many workstreams are in progress

---

### 3. View Commit History Across All Branches

**Command:**
```bash
git log --all --oneline --graph --decorate
```

**What it shows:**
- All commits across all branches
- Visual graph of branch relationships
- Which commits are on which branches

**Example output:**
```
* 9730936 (workstream/ws-ph03-adapter-core) feat(ws-ph03-adapter-core): implement core tool adapter
* abc1234 (workstream/ws-ph01-index-scanner) feat(ws-ph01-index-scanner): implement spec index tag scanner
* 61e6aa6 (HEAD -> main, origin/main) chore: initial scaffold (PH-00)
```

**Interpretation:**
- Each workstream has its own commit(s)
- Can see which workstreams are ahead of main
- Can identify which workstreams have been completed

---

### 4. Check Specific File Implementation Status

**Command (from main branch):**
```bash
# Check if file is still a stub
git show main:src/pipeline/db.py | head -20

# Check if file exists in a workstream branch
git show workstream/ws-ph02-db-core:src/pipeline/db.py | head -20

# Check specific worktree directory
cat .worktrees/ws-ph01-index-scanner/scripts/generate_spec_index.py
```

**What it shows:**
- Whether a file is still a TODO stub or has real implementation
- Contents of files in specific branches without switching

**Stub vs Implementation:**
```python
# STUB (not done):
"""Database core..."""
# TODO: Implement connection factory per ws-ph02-db-core.

# IMPLEMENTED (done):
"""Database core..."""
def get_connection():
    # actual implementation...
```

---

### 5. Check Workstream Dependencies

**Before starting a workstream, check its dependencies:**

#### Example: ws-ph01-spec-mapping (Claude Code)
**Dependency:** ws-ph01-index-scanner (Codex)

```bash
# Check if dependency workstream exists
git branch -a | grep "workstream/ws-ph01-index-scanner"

# Check if dependency file exists and is implemented
git show main:scripts/generate_spec_index.py 2>/dev/null || echo "Not merged to main yet"

# Check worktree if not merged
ls .worktrees/ws-ph01-index-scanner/scripts/generate_spec_index.py 2>/dev/null && echo "EXISTS"
```

#### Example: ws-ph02-state-machine (Claude Code)
**Dependency:** ws-ph02-db-core (Codex)

```bash
# Check if db.py has get_connection() implemented
git show main:src/pipeline/db.py | grep -A 5 "def get_connection"

# Or check the worktree
cat .worktrees/ws-ph02-db-core/src/pipeline/db.py | grep "def get_connection"
```

---

## Standard Workflow for Both Tools

### Before Starting a Workstream

```bash
# 1. Check if your workstream has dependencies
# (Refer to workstream plan document)

# 2. For each dependency, verify it's complete:
git worktree list | grep <dependency_ws_id>
git branch -a | grep "workstream/<dependency_ws_id>"

# 3. Check specific files that should exist
ls .worktrees/<dependency_ws_id>/<expected_file_path>
# OR
git show workstream/<dependency_ws_id>:<expected_file_path> | head -20

# 4. If dependency is complete, proceed. If not, wait or ask.
```

### After Completing a Workstream

```bash
# 1. Verify all acceptance criteria met
# 2. Commit to your workstream branch
git add <files>
git commit -m "feat(<ws_id>): <description>"

# 3. The other tool can now detect your work via:
#    - git worktree list
#    - git branch -a
#    - git log --all
```

---

## Quick Reference: Workstream Status Check

### Check All Workstream Status at Once

```bash
#!/bin/bash
# Save this as scripts/check_workstream_status.sh

echo "=== WORKSTREAM STATUS ==="
echo ""

# List all workstream branches
echo "Active Workstream Branches:"
git branch -a | grep "workstream/" | sed 's/^[+ *]*/  /'
echo ""

# List all worktrees
echo "Active Worktrees:"
git worktree list | grep "ws-ph" || echo "  None"
echo ""

# Check specific files for key workstreams
echo "Key File Implementation Status:"

# PH-01
echo "  [PH-01] scripts/generate_spec_index.py:"
test -f scripts/generate_spec_index.py && echo "    ✅ EXISTS" || \
  (git show main:scripts/generate_spec_index.py &>/dev/null && echo "    ✅ EXISTS in main") || \
  echo "    ❌ NOT FOUND"

echo "  [PH-01] docs/spec/spec_index_map.md:"
test -f docs/spec/spec_index_map.md && echo "    ✅ EXISTS" || \
  (git show main:docs/spec/spec_index_map.md &>/dev/null && echo "    ✅ EXISTS in main") || \
  echo "    ❌ NOT FOUND"

# PH-02
echo "  [PH-02] schema/schema.sql:"
test -f schema/schema.sql && echo "    ✅ EXISTS" || \
  (git show main:schema/schema.sql &>/dev/null && echo "    ✅ EXISTS in main") || \
  echo "    ❌ NOT FOUND"

echo "  [PH-02] src/pipeline/db.py (implemented):"
if grep -q "def get_connection" src/pipeline/db.py 2>/dev/null; then
  echo "    ✅ IMPLEMENTED"
elif git show main:src/pipeline/db.py 2>/dev/null | grep -q "def get_connection"; then
  echo "    ✅ IMPLEMENTED in main"
else
  echo "    ❌ STUB ONLY"
fi

# PH-03
echo "  [PH-03] config/tool_profiles.json:"
test -f config/tool_profiles.json && echo "    ✅ EXISTS" || \
  (git show main:config/tool_profiles.json &>/dev/null && echo "    ✅ EXISTS in main") || \
  echo "    ❌ NOT FOUND"

echo "  [PH-03] src/pipeline/tools.py (implemented):"
if grep -q "def run_tool" src/pipeline/tools.py 2>/dev/null; then
  echo "    ✅ IMPLEMENTED"
elif git show main:src/pipeline/tools.py 2>/dev/null | grep -q "def run_tool"; then
  echo "    ✅ IMPLEMENTED in main"
else
  echo "    ❌ STUB ONLY"
fi

echo ""
echo "=== END STATUS ==="
```

### Run the status check:
```bash
bash scripts/check_workstream_status.sh
```

---

## Dependency Matrix

### Claude Code Workstreams → Dependencies

| Workstream | Dependencies | Check Command |
|------------|--------------|---------------|
| ws-ph01-spec-mapping | ws-ph01-index-scanner (Codex) | `ls .worktrees/ws-ph01-index-scanner/scripts/generate_spec_index.py` |
| ws-ph01-tests | ws-ph01-index-scanner (Codex) | Same as above |
| ws-ph02-state-machine | ws-ph02-db-core (Codex) | `grep "def get_connection" .worktrees/ws-ph02-db-core/src/pipeline/db.py` |
| ws-ph02-crud | ws-ph02-db-core (Codex) | Same as above |
| ws-ph02-tests | ws-ph02-state-machine, ws-ph02-crud (both Claude) | Check both workstream branches exist |
| ws-ph03-adapter-core | None | Can start immediately ✅ |
| ws-ph03-db-integration | ws-ph03-adapter-core (Claude), ws-ph02-crud (Claude) | Check both branches |
| ws-ph03-tests | ws-ph03-adapter-core, ws-ph03-db-integration (both Claude) | Check both branches |

### Codex Workstreams → Dependencies

| Workstream | Dependencies | Check Command |
|------------|--------------|---------------|
| ws-ph01-module-stubs | None | Can start immediately ✅ |
| ws-ph01-index-scanner | None | Can start immediately ✅ |
| ws-ph01-docs | None | Can start immediately ✅ |
| ws-ph02-schema | None | Can start immediately ✅ |
| ws-ph02-db-core | ws-ph02-schema (Codex) | `ls schema/schema.sql` |
| ws-ph02-scripts | ws-ph02-db-core (Codex) | `grep "def init_db" src/pipeline/db.py` |
| ws-ph02-docs | ws-ph02-state-machine (Claude) | `git branch -a \| grep ws-ph02-state-machine` |
| ws-ph03-profiles | None | Can start immediately ✅ |
| ws-ph03-docs | None | Can start immediately ✅ |

---

## Communication Examples

### Example 1: Codex Checking if Claude is Done

**Scenario:** Codex needs to write ws-ph02-docs, which depends on Claude's ws-ph02-state-machine

```bash
# Check if Claude completed state machine workstream
git branch -a | grep "workstream/ws-ph02-state-machine"
# Output: workstream/ws-ph02-state-machine  ✅ EXISTS

# Verify implementation exists
git show workstream/ws-ph02-state-machine:src/pipeline/db.py | grep "def validate_state_transition"
# Output: def validate_state_transition(...)  ✅ IMPLEMENTED

# CONCLUSION: Safe to proceed with ws-ph02-docs
```

### Example 2: Claude Checking if Codex is Done

**Scenario:** Claude needs to start ws-ph02-crud, which depends on Codex's ws-ph02-db-core

```bash
# Check if Codex completed db-core workstream
git worktree list | grep "ws-ph02-db-core"
# Output: .worktrees/ws-ph02-db-core  9abc123 [workstream/ws-ph02-db-core]  ✅ EXISTS

# Verify get_connection() implemented
cat .worktrees/ws-ph02-db-core/src/pipeline/db.py | grep -A 10 "def get_connection"
# Output: Shows full implementation  ✅ IMPLEMENTED

# CONCLUSION: Safe to proceed with ws-ph02-crud
```

---

## Best Practices

### ✅ DO:
- Check dependencies before starting a workstream
- Use `git worktree list` and `git branch -a` regularly
- Verify file implementation (not just existence)
- Commit frequently with clear messages
- Follow the commit message pattern: `feat(<ws_id>): description`

### ❌ DON'T:
- Start a workstream without checking dependencies
- Modify files outside your workstream's file scope
- Delete other worktrees
- Force-push or rewrite history
- Assume a file exists without verifying

---

## Troubleshooting

### "I can't find the dependency file"

```bash
# Check all possible locations:
# 1. In main branch
git show main:path/to/file

# 2. In dependency's worktree
cat .worktrees/<dependency_ws_id>/path/to/file

# 3. In dependency's branch
git show workstream/<dependency_ws_id>:path/to/file

# 4. List all branches to see what exists
git branch -a
```

### "How do I know if a workstream is truly complete?"

```bash
# 1. Check commit message
git log workstream/<ws_id> --oneline -1
# Should say "feat(<ws_id>): ..." with completion message

# 2. Check acceptance criteria from workstream plan
# (Read the file, verify functions exist, run tests if applicable)

# 3. Check for TODO comments
git show workstream/<ws_id>:src/pipeline/file.py | grep "TODO"
# Should have no TODOs in implemented code
```

---

## Summary

**Key Commands:**
```bash
git worktree list              # See active workstreams
git branch -a                  # See all branches
git log --all --graph          # See commit history
git show <branch>:<file>       # View file in branch
bash scripts/check_workstream_status.sh  # Check all status
```

**Coordination Flow:**
1. Check dependencies before starting
2. Verify implementation (not just existence)
3. Commit when done
4. Other tool detects via git commands

**Both tools can always coordinate by inspecting git state!** 🚀
