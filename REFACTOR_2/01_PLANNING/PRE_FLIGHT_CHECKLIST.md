# ✅ Pre-Flight Checklist - Before First Production Run

## 🎯 Purpose
Quick validation checklist to ensure everything is ready for first production run.

**Estimated Time**: 5 minutes  
**When to Use**: Before running `.\scripts\run_multi_agent_refactor.ps1` for the first time

---

## ☑️ **1. Documentation Review** (2 min)

- [ ] Read [COMPLETION_SUMMARY.md](./COMPLETION_SUMMARY.md) to understand what to expect
- [ ] Skim [MERGE_CONFLICT_PROTOCOL.md](./MERGE_CONFLICT_PROTOCOL.md) quick reference table
- [ ] Bookmark [FAILURE_RECOVERY_PLAYBOOK.md](./FAILURE_RECOVERY_PLAYBOOK.md) for emergencies

---

## ☑️ **2. Environment Check** (1 min)

```powershell
# Run automated validation
python scripts/preflight_validator.py
```

**Expected output**:
```
🔍 Running pre-flight validation...

✅ Git working tree is clean
✅ Git worktree support available
✅ Python packages: networkx, sqlite3 installed
✅ Found 39 workstream files
✅ Dependency graph is valid (acyclic)
✅ Disk space: 15.3 GB free

📊 Validation Summary:
   Errors: 0
   Warnings: 0

✅ ALL CHECKS PASSED - Ready to proceed!
```

**If any errors**:
- See error message for specific issue
- Fix and re-run validation
- Common fixes in [FAILURE_RECOVERY_PLAYBOOK.md](./FAILURE_RECOVERY_PLAYBOOK.md)

---

## ☑️ **3. Backup Current State** (30 sec)

```powershell
# Ensure main branch is clean
git status

# Expected: "nothing to commit, working tree clean"

# If uncommitted changes exist:
git stash push -m "pre-multi-agent-run-backup"

# Verify remote is up to date
git pull origin main
git push origin main
```

---

## ☑️ **4. Dry Run Test** (1 min)

```powershell
# Test without making any changes
.\scripts\run_multi_agent_refactor.ps1 -DryRun
```

**Expected output**:
```
╔══════════════════════════════════════════════════════════════════╗
║        Multi-Agent Workstream Orchestrator                       ║
╚══════════════════════════════════════════════════════════════════╝

⚠️  DRY RUN MODE - No actual changes will be made

Configuration:
  • Agents: 3
  • Dry Run: True

Step 1/5: Pre-Flight Validation
────────────────────────────────────────────────────────────────────
✅ ALL CHECKS PASSED

Step 2/5: Worktree Setup
────────────────────────────────────────────────────────────────────
[DRY RUN] Would create 3 worktrees in .worktrees/

[... rest of output ...]

✅ DRY RUN COMPLETE - No changes made
```

---

## ☑️ **5. Final Checks** (30 sec)

- [ ] **Disk Space**: Minimum 10 GB free (15+ GB recommended)
  ```powershell
  # Check current free space
  Get-Volume | Where-Object {$_.DriveLetter -eq 'C'} | Select-Object SizeRemaining
  ```

- [ ] **Time Available**: 3-5 days for execution (can pause/resume)

- [ ] **Monitoring Plan**: How will you check progress?
  - Option 1: Check logs periodically (`logs/orchestrator.log`)
  - Option 2: Query database for status (see below)

- [ ] **Support Access**: Know where to find help
  - Merge conflicts → [MERGE_CONFLICT_PROTOCOL.md](./MERGE_CONFLICT_PROTOCOL.md)
  - Failures → [FAILURE_RECOVERY_PLAYBOOK.md](./FAILURE_RECOVERY_PLAYBOOK.md)

---

## ☑️ **6. Progress Monitoring Setup** (Optional, 30 sec)

Save this command for checking progress:

```powershell
# Check completion status
sqlite3 .state/orchestration.db "SELECT status, COUNT(*) as count FROM workstream_status GROUP BY status"

# Expected output as system runs:
# pending|30
# running|3
# completed|6
#
# When done:
# completed|39
```

Save this command for viewing logs:

```powershell
# Tail orchestrator logs
Get-Content logs/orchestrator.log -Wait -Tail 50
```

---

## 🚀 Ready to Launch

### **If all checkboxes are checked:**

```powershell
# Launch production run
.\scripts\run_multi_agent_refactor.ps1
```

**What happens next:**
1. System creates 3 isolated worktrees
2. Launches 3 AI agents (aider processes)
3. Each agent picks available workstream and executes
4. Completed work merges to main automatically
5. Logs written to `logs/orchestrator.log`
6. Progress tracked in `.state/orchestration.db`

**You should:**
- Check progress periodically (every few hours)
- Watch for merge conflict notifications
- Don't kill the process abruptly (use Ctrl+C if needed - trap handler will clean up)

---

## ⏸️ Pause/Resume

### **To Pause**
```powershell
# Press Ctrl+C in terminal
# Trap handler will clean up worktrees
# Database state preserved
```

### **To Resume**
```powershell
# System automatically resumes from database state
.\scripts\run_multi_agent_refactor.ps1 -Resume
```

---

## 🆘 If Something Goes Wrong

### **During Execution**

| Issue | Immediate Action |
|-------|------------------|
| Merge conflict notification | See [MERGE_CONFLICT_PROTOCOL.md](./MERGE_CONFLICT_PROTOCOL.md) |
| Agent hangs >1 hour | See [FAILURE_RECOVERY_PLAYBOOK.md](./FAILURE_RECOVERY_PLAYBOOK.md) Scenario 2 |
| Orchestrator crashes | Restart with same command (auto-resumes) |
| Out of disk space | Free up space, then resume |

### **After Completion**

```powershell
# Verify all workstreams completed
sqlite3 .state/orchestration.db "SELECT * FROM workstream_status WHERE status != 'completed'"

# Should return empty (0 rows) if all successful

# Run tests to verify changes
pytest -v

# If tests fail, see FAILURE_RECOVERY_PLAYBOOK.md Scenario 4
```

---

## ✅ Success Criteria

**System completed successfully when:**
- [ ] All 39 workstreams show status "completed" in database
- [ ] No worktrees remain in `.worktrees/` directory
- [ ] All tests pass (`pytest -v`)
- [ ] Main branch has 39 new merge commits
- [ ] No errors in `logs/orchestrator.log`

---

## 📊 Expected Timeline

| Phase | Duration | What's Happening |
|-------|----------|------------------|
| Setup | 2-5 min | Worktree creation, agent spawn |
| Execution | 3-5 days | Agents working in parallel |
| Merge & Cleanup | 5-10 min | Final merges, worktree removal |
| **Total** | **3-5 days** | Mostly unattended |

**Manual Intervention**: Only if merge conflicts occur (~5-10% probability)

---

## 🎉 Ready to Go!

**All checks passed?** Run this:

```powershell
.\scripts\run_multi_agent_refactor.ps1
```

**Questions?** See [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md) for navigation.

**Good luck!** 🚀

---

**Last Updated**: 2025-11-29  
**Estimated First-Run Time**: 3-5 days (automated)  
**Manual Intervention**: Minimal (only for merge conflicts)
