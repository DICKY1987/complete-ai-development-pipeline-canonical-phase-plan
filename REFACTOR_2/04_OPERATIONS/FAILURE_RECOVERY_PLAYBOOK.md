# Failure Recovery Playbook

## 🎯 Purpose

Comprehensive guide for recovering from common failure scenarios during multi-agent orchestration. Each scenario includes symptoms, root causes, and step-by-step recovery procedures.

---

## 📋 Quick Triage

| Symptoms | Likely Scenario | Jump To |
|----------|----------------|---------|
| Python crash, worktrees remain | [Scenario 1: Orchestrator Crash](#scenario-1-orchestrator-crashes-mid-execution) |
| Workstream stuck "running" >1 hour | [Scenario 2: Agent Hangs](#scenario-2-agent-hangs-for-1-hour) |
| "not a valid path" errors | [Scenario 3: Worktree Corruption](#scenario-3-git-worktree-corruption) |
| Tests fail after merge | [Scenario 4: Bad Merge](#scenario-4-tests-fail-after-merge) |
| Database locked errors | [Scenario 5: Database Lock](#scenario-5-database-lock-errors) |
| All agents stuck at 0% | [Scenario 6: Dependency Deadlock](#scenario-6-dependency-deadlock) |

---

## Scenario 1: Orchestrator Crashes Mid-Execution

### 🔍 Symptoms
- Python process terminated unexpectedly
- Multiple worktrees still exist in `.worktrees/`
- Database shows some workstreams with status "running"
- Error message like "KeyboardInterrupt", "MemoryError", or exception traceback

### 🎯 Root Causes
- User pressed Ctrl+C
- Out of memory (too many agents)
- Unhandled exception in orchestrator code
- System crash or power loss

### ✅ Recovery Steps

#### **Step 1: Assess Database State**

```powershell
# Check which workstreams were running
sqlite3 .state/orchestration.db "SELECT workstream_id, status, agent_id, started_at FROM workstream_status WHERE status='running'"

# Example output:
# ws-15|running|agent-1|2025-11-29 08:05:12
# ws-22|running|agent-2|2025-11-29 08:05:15
# ws-31|running|agent-3|2025-11-29 08:05:18
```

#### **Step 2: Check Each Running Workstream**

For each workstream ID:

```powershell
# Check if agent made any commits
git log ws/<ws-id>/<agent-id> --oneline -5

# Check current state of branch
git show ws/<ws-id>/<agent-id>:path/to/changed/file.py

# See what files were modified
git diff main..ws/<ws-id>/<agent-id> --name-only
```

**Decision Tree:**

```
Has commits AND changes look correct?
├─ YES → Proceed to Step 3 (manual merge)
└─ NO  → Proceed to Step 4 (mark as failed)
```

#### **Step 3: Manual Merge (If Work is Valid)**

```powershell
# For each workstream with valid work
git checkout main
git merge ws/<ws-id>/<agent-id> --no-edit

# If merge succeeds:
git push origin main

# Update database to mark as completed
sqlite3 .state/orchestration.db "UPDATE workstream_status SET status='completed', completed_at=datetime('now') WHERE workstream_id='<ws-id>'"

# If merge conflicts occur:
# See MERGE_CONFLICT_PROTOCOL.md for resolution steps
```

#### **Step 4: Mark Failed Workstreams**

```powershell
# For workstreams with no commits or bad work
sqlite3 .state/orchestration.db "UPDATE workstream_status SET status='failed', error_message='Orchestrator crash - no valid work found' WHERE workstream_id='<ws-id>'"
```

#### **Step 5: Clean Up Worktrees**

```powershell
# List all worktrees
git worktree list

# Remove each agent worktree
git worktree list | Select-String ".worktrees" | ForEach-Object {
    $path = ($_ -split '\s+')[0]
    Write-Host "Removing: $path"
    git worktree remove $path --force
}

# Prune any orphaned references
git worktree prune
```

#### **Step 6: Restart Orchestrator**

```powershell
# Orchestrator will:
# - Skip completed workstreams
# - Retry failed workstreams
# - Resume from current state
.\scripts\run_multi_agent_refactor.ps1 -Resume
```

---

## Scenario 2: Agent Hangs for >1 Hour

### 🔍 Symptoms
- One workstream shows status "running" for >60 minutes
- No recent commits on the workstream branch
- Aider process appears frozen (high CPU or no activity)
- Other agents have completed their work

### 🎯 Root Causes
- Aider stuck waiting for user input
- Infinite loop in agent code
- Network timeout connecting to API
- Very large file causing processing hang

### ✅ Recovery Steps

#### **Step 1: Identify Hung Process**

```powershell
# Find aider processes
Get-Process aider | Format-Table Id, CPU, StartTime, WorkingSet -AutoSize

# Find which worktree it's working on
Get-Process aider | ForEach-Object {
    $proc = $_
    Write-Host "PID $($proc.Id): $(Get-ItemProperty -Path $proc.Path).DirectoryName"
}
```

#### **Step 2: Check Partial Work**

```powershell
# Navigate to agent's worktree
cd .worktrees/agent-<N>-ws-<ID>

# See uncommitted changes
git status
git diff

# See if any commits were made
git log --oneline -5
```

**Decision: Is there valuable work?**

```
Has meaningful changes or commits?
├─ YES → Step 3 (save work)
└─ NO  → Step 4 (abandon and retry)
```

#### **Step 3: Save Valuable Work**

```powershell
# If uncommitted changes exist, commit them
git add .
git commit -m "WIP: Partial work before agent timeout"

# Push branch
git push origin ws/<ws-id>/agent-<N>

# Manually merge or mark for human review
git checkout main
git merge ws/<ws-id>/agent-<N> --no-edit  # Or handle conflicts

# Update database
sqlite3 .state/orchestration.db "UPDATE workstream_status SET status='completed', completed_at=datetime('now'), notes='Completed manually after agent timeout' WHERE workstream_id='ws-<ID>'"
```

#### **Step 4: Abandon and Retry**

```powershell
# Kill hung process
Get-Process aider | Where-Object { $_.Id -eq <PID> } | Stop-Process -Force

# Clean worktree
cd ../../..  # Back to repo root
git worktree remove .worktrees/agent-<N>-ws-<ID> --force

# Delete branch (work was not valuable)
git branch -D ws/<ws-id>/agent-<N>

# Mark as failed to trigger retry
sqlite3 .state/orchestration.db "UPDATE workstream_status SET status='failed', error_message='Agent timeout - abandoned and will retry', started_at=NULL WHERE workstream_id='ws-<ID>'"

# Restart orchestrator (will pick up failed workstream)
.\scripts\run_multi_agent_refactor.ps1 -Resume
```

---

## Scenario 3: Git Worktree Corruption

### 🔍 Symptoms
- `git worktree list` shows "prunable" entries
- Error: "fatal: '.worktrees/agent-1-ws-22' is not a valid path"
- Cannot remove worktree with standard commands
- `.git/worktrees/` directory has orphaned folders

### 🎯 Root Causes
- Worktree directory deleted without `git worktree remove`
- File system corruption
- Improper cleanup after crash
- Manual deletion of `.git/worktrees/` entries

### ✅ Recovery Steps

#### **Step 1: Prune Invalid Entries**

```powershell
# Git's built-in cleanup
git worktree prune -v

# Check if issue is resolved
git worktree list
```

#### **Step 2: Manual Cleanup (If Prune Fails)**

```powershell
# List problematic worktree admin directories
Get-ChildItem .git/worktrees/

# For each orphaned entry:
# 1. Check if directory still exists
Test-Path ".worktrees/agent-1-ws-22"  # If False, it's orphaned

# 2. Forcibly remove admin entry
Remove-Item .git/worktrees/agent-1-ws-22 -Recurse -Force

# 3. Repeat for all orphaned entries
```

#### **Step 3: Rebuild Worktree Metadata**

```powershell
# Attempt to repair
git worktree repair

# Verify clean state
git worktree list

# Should now only show main worktree (repository root)
```

#### **Step 4: Clean Physical Directories**

```powershell
# Remove any remaining .worktrees directories
if (Test-Path ".worktrees") {
    Get-ChildItem .worktrees | ForEach-Object {
        Write-Host "Removing orphaned directory: $($_.Name)"
        Remove-Item $_.FullName -Recurse -Force
    }
}
```

#### **Step 5: Reset Database State**

```powershell
# Mark any "running" workstreams as failed
sqlite3 .state/orchestration.db "UPDATE workstream_status SET status='failed', error_message='Worktree corruption - will retry' WHERE status='running'"
```

---

## Scenario 4: Tests Fail After Merge

### 🔍 Symptoms
- Workstream merged successfully (no conflicts)
- CI pipeline fails
- `pytest` shows failing tests
- Tests were passing before merge

### 🎯 Root Causes
- Agent made logically incorrect changes
- Integration issue between workstreams
- Test assumptions invalidated by refactor
- Missing dependency update

### ✅ Recovery Steps

#### **Step 1: Identify Failing Tests**

```powershell
# Run full test suite
pytest -v --tb=short

# Example output:
# FAILED tests/core/state/test_db_operations.py::test_transaction_rollback
# FAILED tests/engine/test_executor.py::test_retry_logic
```

#### **Step 2: Bisect to Find Culprit**

```powershell
# Find which merge introduced the failure
git log --oneline main -10

# Example:
# abc123f resolve: merge ws-22
# def456g resolve: merge ws-15
# ...

# Test each merge
git checkout def456g
pytest tests/core/state/test_db_operations.py  # Pass or fail?

git checkout abc123f
pytest tests/core/state/test_db_operations.py  # Pass or fail?
```

#### **Step 3: Revert Bad Merge**

```powershell
# If merge abc123f caused the failure
git revert abc123f --no-edit

# Push fix
git push origin main

# Update database
sqlite3 .state/orchestration.db "UPDATE workstream_status SET status='reverted', error_message='Tests failed after merge - needs rework' WHERE workstream_id='ws-22'"
```

#### **Step 4: Rework Workstream**

```powershell
# Option A: Manually fix the issue
# 1. Understand what agent changed
git show abc123f

# 2. Fix the code
code core/state/db_operations.py

# 3. Test and commit
pytest tests/core/state/test_db_operations.py
git add .
git commit -m "fix: correct transaction rollback logic from ws-22"

# Option B: Re-run agent with better instructions
# 1. Update workstream spec with additional context
code workstreams/ws-22.json
# Add: "CRITICAL: Ensure transaction rollback handles nested transactions"

# 2. Reset workstream status
sqlite3 .state/orchestration.db "UPDATE workstream_status SET status='pending' WHERE workstream_id='ws-22'"

# 3. Re-run orchestrator for just this workstream
.\scripts\run_multi_agent_refactor.ps1 -Workstreams ws-22
```

---

## Scenario 5: Database Lock Errors

### 🔍 Symptoms
- Error: "database is locked"
- SQLite errors during orchestration
- Multiple processes trying to access `.state/orchestration.db`

### 🎯 Root Causes
- Multiple orchestrator instances running
- Long-running transaction not committed
- File system locking issue (NFS, network drive)

### ✅ Recovery Steps

#### **Step 1: Check for Multiple Processes**

```powershell
# Find all Python processes
Get-Process python | Format-Table Id, Path, StartTime -AutoSize

# Kill duplicate orchestrators
Get-Process python | Where-Object { $_.Path -like "*multi_agent_orchestrator*" } | Stop-Process
```

#### **Step 2: Clear Lock File**

```powershell
# Remove SQLite lock files
Remove-Item .state/orchestration.db-shm -ErrorAction SilentlyContinue
Remove-Item .state/orchestration.db-wal -ErrorAction SilentlyContinue

# Vacuum database to clean up
sqlite3 .state/orchestration.db "VACUUM;"
```

#### **Step 3: Enable WAL Mode (Prevention)**

```powershell
# Better concurrency for SQLite
sqlite3 .state/orchestration.db "PRAGMA journal_mode=WAL;"
sqlite3 .state/orchestration.db "PRAGMA busy_timeout=5000;"
```

---

## Scenario 6: Dependency Deadlock

### 🔍 Symptoms
- All agents stuck at 0% progress
- Database shows all workstreams as "blocked"
- No errors in logs
- Orchestrator appears to be running but doing nothing

### 🎯 Root Causes
- Circular dependency in workstream graph (A depends on B depends on A)
- Invalid dependency reference (depends on non-existent workstream)

### ✅ Recovery Steps

#### **Step 1: Check Blocking Graph**

```powershell
# See what's blocking what
sqlite3 .state/orchestration.db "SELECT workstream_id, status, blocked_by FROM workstream_status WHERE status='blocked'"

# Example output:
# ws-22|blocked|ws-15
# ws-15|blocked|ws-22  # CIRCULAR!
```

#### **Step 2: Detect Cycle**

```powershell
# Run preflight validator's dependency check
python scripts/preflight_validator.py

# Will output:
# ❌ Dependency cycle detected: ws-15 -> ws-22 -> ws-15
```

#### **Step 3: Break the Cycle**

```powershell
# Option A: Remove dependency from workstream spec
code workstreams/ws-22.json
# Change: "depends_on": ["ws-15"] → "depends_on": []

# Option B: Force unblock one workstream
sqlite3 .state/orchestration.db "UPDATE workstream_status SET blocked_by=NULL WHERE workstream_id='ws-22'"

# Restart orchestrator
.\scripts\run_multi_agent_refactor.ps1 -Resume
```

---

## 🛡️ Prevention Best Practices

### Before Running Orchestrator
1. ✅ **Always run preflight validation**
   ```powershell
   python scripts/preflight_validator.py
   ```

2. ✅ **Commit or stash uncommitted changes**
   ```powershell
   git status --porcelain
   ```

3. ✅ **Ensure sufficient disk space** (10+ GB free)

### During Execution
1. ✅ **Monitor logs in real-time**
   ```powershell
   Get-Content logs/orchestrator.log -Wait -Tail 50
   ```

2. ✅ **Check progress periodically**
   ```powershell
   sqlite3 .state/orchestration.db "SELECT status, COUNT(*) FROM workstream_status GROUP BY status"
   ```

3. ✅ **Don't kill abruptly** - Use Ctrl+C (trap handler will clean up)

### After Completion
1. ✅ **Verify all workstreams completed**
   ```powershell
   sqlite3 .state/orchestration.db "SELECT * FROM workstream_status WHERE status != 'completed'"
   ```

2. ✅ **Run full test suite**
   ```powershell
   pytest -v
   ```

3. ✅ **Clean up worktrees**
   ```powershell
   git worktree prune
   ```

---

## 📞 Escalation

### When to Seek Help

If recovery steps don't work after 2 attempts:
- [ ] Document exact symptoms in `logs/failure_<timestamp>.md`
- [ ] Capture database state: `sqlite3 .state/orchestration.db .dump > state_dump.sql`
- [ ] Collect logs: `tar -czf logs_<timestamp>.tar.gz logs/`
- [ ] Open issue with details

### Emergency Reset (Nuclear Option)

⚠️ **WARNING**: This will lose all orchestration state!

```powershell
# Stop everything
Get-Process python | Stop-Process
Get-Process aider | Stop-Process

# Remove all state
Remove-Item .state/orchestration.db
Remove-Item .worktrees -Recurse -Force
Remove-Item logs/* -Force

# Prune git references
git worktree prune

# Delete all agent branches
git branch | Select-String "ws/" | ForEach-Object {
    $branch = $_.ToString().Trim()
    git branch -D $branch
}

# Start fresh
.\scripts\run_multi_agent_refactor.ps1
```

---

**Last Updated**: 2025-11-29  
**Owner**: GitHub Copilot CLI  
**Related**: `MERGE_CONFLICT_PROTOCOL.md`, `ONE_TOUCH_IMPLEMENTATION_COMPLETE.md`
