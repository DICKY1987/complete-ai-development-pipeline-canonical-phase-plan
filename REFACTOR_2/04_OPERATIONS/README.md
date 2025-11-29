# 04_OPERATIONS - Runtime Operations & Recovery

**Failure handling, recovery procedures, and operational playbooks**

---

## 📋 Purpose

This folder contains **operational procedures** for handling runtime issues, recovering from failures, and maintaining system health during multi-agent execution.

---

## 📁 Contents

### Operational Playbooks

#### `FAILURE_RECOVERY_PLAYBOOK.md`
**Complete guide for handling system failures.**

**Covers:**
- Agent crash recovery
- Worktree corruption repair
- Network timeout handling
- Out-of-memory situations
- Partial completion scenarios
- Manual intervention procedures
- Rollback strategies

**When to use:**
- Agent process crashes mid-execution
- System resources exhausted
- Git operations fail
- Need to resume interrupted workflow

**Example scenarios:**
```
Scenario: Agent 2 crashes at 80% completion
Action: Resume from checkpoint, reuse completed work

Scenario: Disk full during execution
Action: Cleanup temp files, expand storage, resume

Scenario: Git merge fails unexpectedly
Action: Manual merge protocol, conflict resolution
```

---

#### `AGENT_FALLBACK_STRATEGIES.md`
**Tool fallback and alternative execution paths.**

**Covers:**
- Primary tool failure detection
- Automatic fallback to secondary tools
- Tool compatibility matrix
- Fallback decision tree
- Manual override procedures

**When to use:**
- Primary AI tool (Aider) unavailable
- Tool produces unexpected output
- Need to switch tools mid-execution
- Testing alternative tools

**Fallback hierarchy:**
```
1. Aider (primary)
   ↓ (if fails)
2. GitHub Copilot CLI (fallback)
   ↓ (if fails)
3. Manual execution (last resort)
```

---

#### `MERGE_CONFLICT_PROTOCOL.md`
**Merge conflict prevention and resolution.**

**Covers:**
- Why conflicts are rare with worktree isolation
- Pre-merge conflict detection
- Automatic conflict resolution strategies
- Manual conflict resolution procedures
- Post-merge validation

**When to use:**
- Unexpected merge conflicts appear
- Need to verify merge safety
- Debugging workstream independence
- Post-execution validation

**Prevention strategies:**
```
✅ Workstream file isolation verified
✅ Pre-merge conflict detection run
✅ Incremental merge (one at a time)
✅ Automatic rollback on conflict
```

---

#### `CRITICAL_FIXES_APPLIED.md`
**Log of critical fixes from Claude's review.**

**Covers:**
- Original blocking issues identified
- Fixes applied to resolve them
- Validation of fix effectiveness
- Lessons learned

**When to use:**
- Understanding system evolution
- Auditing design decisions
- Learning from past issues
- Quality assurance reviews

**Key fixes:**
1. Added explicit Aider installation check
2. Created worktree manager module
3. Implemented pre-flight validation

---

## 🎯 Operational Best Practices

### 1. Pre-Execution Validation

**Always run preflight checks:**
```powershell
python ..\03_IMPLEMENTATION\preflight_validator.py
```

**Validates:**
- Tool availability
- Repository health
- System resources
- Configuration validity

---

### 2. Monitoring During Execution

**Watch for warning signs:**
- Agent process CPU at 100% for >5 minutes (possible hang)
- Memory usage approaching system limits
- No file changes for >10 minutes (possible deadlock)
- Error messages in agent logs

**Action:** Check `FAILURE_RECOVERY_PLAYBOOK.md` for specific procedures.

---

### 3. Post-Execution Validation

**Always verify results:**
```bash
# Run tests
pytest tests/

# Validate imports
python scripts/paths_index_cli.py gate

# Check for uncommitted changes
git status
```

---

## 🚨 Common Issues & Solutions

### Issue: Agent Timeout

**Symptom:** Agent process exceeds 30-minute timeout.

**Diagnosis:**
```powershell
# Check agent logs
Get-Content logs/agent_1.log -Tail 50
```

**Solutions:**
1. Increase timeout in `config.yaml`: `timeout_minutes: 60`
2. Split workstream into smaller chunks
3. Check for network issues (if tool requires internet)

**Reference:** `FAILURE_RECOVERY_PLAYBOOK.md` → "Agent Timeout Scenarios"

---

### Issue: Merge Conflict

**Symptom:** Git reports conflicts during automatic merge.

**Diagnosis:**
```bash
git status
git diff --check
```

**Solutions:**
1. Follow `MERGE_CONFLICT_PROTOCOL.md` step-by-step
2. Verify workstream independence (should be rare)
3. Manual merge if automatic resolution fails

**Reference:** `MERGE_CONFLICT_PROTOCOL.md` → "Resolution Procedures"

---

### Issue: Tool Fallback Triggered

**Symptom:** Orchestrator switches from Aider to Copilot.

**Diagnosis:**
```bash
# Check why primary tool failed
cat logs/tool_fallback.log
```

**Solutions:**
1. Verify tool installation: `which aider`
2. Check tool configuration in `config.yaml`
3. Test tool manually: `aider --version`

**Reference:** `AGENT_FALLBACK_STRATEGIES.md` → "Fallback Decision Tree"

---

### Issue: Disk Space Exhausted

**Symptom:** "No space left on device" error.

**Diagnosis:**
```bash
df -h  # Check disk usage
du -sh .worktrees/*  # Check worktree sizes
```

**Solutions:**
1. Clean up old worktrees: `git worktree prune`
2. Remove temp files: `rm -rf /tmp/aider_*`
3. Expand disk if needed

**Reference:** `FAILURE_RECOVERY_PLAYBOOK.md` → "Resource Exhaustion"

---

## 🔄 Recovery Procedures

### Procedure: Resume After Crash

**Scenario:** Orchestrator crashed mid-execution.

**Steps:**
1. Identify which agents completed:
   ```bash
   git branch --list "workstream-*"
   git log --oneline workstream-1
   ```

2. Check worktree status:
   ```bash
   git worktree list
   ```

3. Resume incomplete workstreams:
   ```bash
   # Edit config.yaml, comment out completed workstreams
   .\run_multi_agent_refactor.ps1
   ```

**Reference:** `FAILURE_RECOVERY_PLAYBOOK.md` → "Partial Completion Recovery"

---

### Procedure: Rollback Completed Work

**Scenario:** Need to undo merged changes.

**Steps:**
1. Identify last safe commit:
   ```bash
   git log --oneline -10
   ```

2. Reset to before merge:
   ```bash
   git reset --hard <commit-hash>
   ```

3. Clean up worktrees:
   ```bash
   git worktree prune
   ```

**Reference:** `FAILURE_RECOVERY_PLAYBOOK.md` → "Complete Rollback"

---

## 📊 Health Monitoring

### Real-Time Monitoring

**Watch these metrics during execution:**

| Metric | Normal Range | Warning Threshold | Critical Threshold |
|--------|--------------|-------------------|-------------------|
| **Agent CPU** | 30-70% | >80% for >5 min | 100% for >10 min |
| **Memory** | <50% system | >70% system | >90% system |
| **Disk I/O** | <50 MB/s | >100 MB/s sustained | Disk full |
| **File changes/min** | 5-20 files | <2 files | 0 files for >10 min |

---

### Log Analysis

**Key log files:**
```
logs/
├── orchestrator.log       # Main orchestration events
├── agent_1.log           # Workstream 1 execution
├── agent_2.log           # Workstream 2 execution
├── agent_3.log           # Workstream 3 execution
└── worktree_manager.log  # Git worktree operations
```

**Watch for patterns:**
```bash
# Find errors
grep -i "error" logs/*.log

# Find warnings
grep -i "warn" logs/*.log

# Check completion
grep "COMPLETE" logs/agent_*.log
```

---

## 🛠️ Maintenance

### Regular Cleanup

**After each execution:**
```bash
# Remove stale worktrees
git worktree prune

# Clean temp files
rm -rf /tmp/aider_* /tmp/worktree_*

# Archive logs
mv logs/ logs_$(date +%Y%m%d)/
```

---

### System Health Check

**Weekly validation:**
```bash
# Check Git repository
git fsck

# Validate configuration
python preflight_validator.py

# Test tool availability
aider --version
gh copilot --version
```

---

## 📝 Operational Status

- ✅ **FAILURE_RECOVERY_PLAYBOOK.md** - Complete, validated
- ✅ **AGENT_FALLBACK_STRATEGIES.md** - Complete, validated
- ✅ **MERGE_CONFLICT_PROTOCOL.md** - Complete, validated
- ✅ **CRITICAL_FIXES_APPLIED.md** - Complete, documented

---

## 🔗 Related Documentation

- **Planning** → `../01_PLANNING/` (execution strategy)
- **Architecture** → `../02_ARCHITECTURE/` (system design)
- **Implementation** → `../03_IMPLEMENTATION/` (code to run)

---

**Need help?** → Start with `FAILURE_RECOVERY_PLAYBOOK.md` for most issues.
