# Merge Conflict Resolution Protocol

## 🎯 Purpose

Defines the exact steps when a workstream merge fails due to conflicts, ensuring:
- Dependent workstreams are properly blocked
- Clear resolution instructions for users
- State tracking remains consistent
- Orchestrator can resume after manual intervention

---

## 🔍 Detection & Notification

### 1. **Orchestrator Detects Conflict**

When `git merge` returns non-zero exit code:

```python
# In multi_agent_orchestrator.py
result = subprocess.run(
    ["git", "merge", branch_name, "--no-edit"],
    cwd=self.repo_root,
    capture_output=True
)

if result.returncode != 0:
    # CONFLICT DETECTED
    self._handle_merge_conflict(workstream_id, branch_name, result.stderr)
```

### 2. **Automatic Logging**

Orchestrator immediately logs to multiple locations:

**A. Console Output**
```
⚠️  MERGE CONFLICT: ws-22
   Branch: ws/ws-22/agent-1
   Files: core/state/db_operations.py, core/engine/executor.py
   
   📝 Detailed report: reports/conflict_ws-22.md
   🔄 Dependent workstreams paused: ws-24, ws-26
```

**B. Conflict Log File** (`logs/conflicts.log`)
```
2025-11-29 08:15:23 | ws-22 | ws/ws-22/agent-1 | core/state/db_operations.py, core/engine/executor.py
```

**C. Conflict Report** (`reports/conflict_ws-22.md`)
```markdown
# Merge Conflict: ws-22

**Status**: ⚠️ Requires Manual Resolution  
**Detected**: 2025-11-29 08:15:23  
**Branch**: ws/ws-22/agent-1  

## Conflicting Files
- `core/state/db_operations.py` (lines 45-67)
- `core/engine/executor.py` (lines 123-145)

## Branches Involved
- **Source**: ws/ws-22/agent-1
- **Target**: main (commit abc123f)

## Dependent Workstreams Blocked
- ws-24 (depends on ws-22)
- ws-26 (depends on ws-22)

## Resolution Instructions
[See section below]
```

### 3. **Database State Update**

```sql
-- Mark workstream as conflicted
UPDATE workstream_status 
SET status = 'conflict', 
    error_message = 'Merge conflict in: core/state/db_operations.py, core/engine/executor.py',
    updated_at = CURRENT_TIMESTAMP
WHERE workstream_id = 'ws-22';

-- Pause dependent workstreams
UPDATE workstream_status
SET status = 'blocked',
    blocked_by = 'ws-22',
    updated_at = CURRENT_TIMESTAMP
WHERE workstream_id IN ('ws-24', 'ws-26');
```

---

## 🛑 Pause Dependent Workstreams

### Dependency Graph Query

```python
def get_dependents(workstream_id: str) -> list[str]:
    """Find all workstreams that depend on the given one."""
    conn = sqlite3.connect('.state/orchestration.db')
    cursor = conn.cursor()
    
    # Recursive CTE to find all downstream dependencies
    cursor.execute("""
        WITH RECURSIVE dependents AS (
            -- Base: direct dependents
            SELECT ws.id as dependent_id
            FROM workstreams ws
            WHERE ws.depends_on LIKE '%' || ? || '%'
            
            UNION
            
            -- Recursive: dependents of dependents
            SELECT ws.id as dependent_id
            FROM workstreams ws
            INNER JOIN dependents d ON ws.depends_on LIKE '%' || d.dependent_id || '%'
        )
        SELECT dependent_id FROM dependents
    """, (workstream_id,))
    
    return [row[0] for row in cursor.fetchall()]
```

### Pause Logic

```python
def pause_dependents(conflicted_ws_id: str):
    """Pause all workstreams that depend on the conflicted one."""
    dependents = get_dependents(conflicted_ws_id)
    
    for ws_id in dependents:
        logger.warning(f"Pausing {ws_id} (blocked by {conflicted_ws_id})")
        
        # Update database
        conn.execute("""
            UPDATE workstream_status
            SET status = 'blocked',
                blocked_by = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE workstream_id = ?
        """, (conflicted_ws_id, ws_id))
        
        # If agent is currently running this, terminate it
        # (Orchestrator will check status before starting new workstreams)
```

---

## 👤 Human Intervention Required

### Step-by-Step Resolution

#### **Option A: Manual Merge (Recommended)**

```powershell
# 1. Navigate to repository root
cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"

# 2. Ensure you're on main branch
git checkout main

# 3. Attempt merge (will show conflicts)
git merge ws/ws-22/agent-1 --no-commit

# Expected output:
# Auto-merging core/state/db_operations.py
# CONFLICT (content): Merge conflict in core/state/db_operations.py
# Automatic merge failed; fix conflicts and then commit the result.

# 4. Open conflicting files in editor
code core/state/db_operations.py
code core/engine/executor.py

# 5. Resolve conflicts (remove <<<<<<, ======, >>>>>> markers)
#    Choose correct version or combine both

# 6. Test changes (critical!)
pytest tests/core/state/test_db_operations.py -v
pytest tests/engine/test_executor.py -v

# 7. Stage resolved files
git add core/state/db_operations.py
git add core/engine/executor.py

# 8. Complete merge with descriptive message
git commit -m "resolve: merge ws-22 (database operations refactor)

- Merged changes from ws/ws-22/agent-1
- Resolved conflicts in db_operations.py (kept new transaction handling)
- Resolved conflicts in executor.py (combined retry logic)
- Tests passing: test_db_operations.py, test_executor.py"

# 9. Update orchestrator database to mark as resolved
python -c "
import sqlite3
conn = sqlite3.connect('.state/orchestration.db')
conn.execute(\"UPDATE workstream_status SET status='completed', error_message=NULL WHERE workstream_id='ws-22'\")
conn.commit()
"

# 10. Resume orchestrator (it will unblock dependents)
.\scripts\run_multi_agent_refactor.ps1 -Resume
```

#### **Option B: Auto-Retry with Rebase**

```powershell
# 1. Rebase conflicting branch onto current main
git checkout ws/ws-22/agent-1
git rebase main

# 2. If rebase succeeds, merge again
git checkout main
git merge ws/ws-22/agent-1 --no-edit

# 3. If rebase fails, fall back to Option A (manual resolution)
```

#### **Option C: Discard Workstream (Last Resort)**

```powershell
# 1. Delete conflicting branch
git branch -D ws/ws-22/agent-1

# 2. Mark as failed in database
python -c "
import sqlite3
conn = sqlite3.connect('.state/orchestration.db')
conn.execute(\"UPDATE workstream_status SET status='discarded', error_message='Merge conflicts unresolvable - manual implementation required' WHERE workstream_id='ws-22'\")
conn.commit()
"

# 3. Implement workstream manually (outside orchestrator)

# 4. Mark dependent workstreams as unblocked
python -c "
import sqlite3
conn = sqlite3.connect('.state/orchestration.db')
conn.execute(\"UPDATE workstream_status SET status='pending', blocked_by=NULL WHERE blocked_by='ws-22'\")
conn.commit()
"
```

---

## 🔄 Resuming Orchestrator

### After Conflict Resolution

```powershell
# Resume orchestrator (uses existing database state)
.\scripts\run_multi_agent_refactor.ps1 -Resume

# Or if you want to see what will run first:
.\scripts\run_multi_agent_refactor.ps1 -Resume -DryRun
```

### Orchestrator Resume Logic

```python
# In multi_agent_orchestrator.py
def resume_from_database(self):
    """Resume orchestration from existing state."""
    
    # Unblock any workstreams that were blocked by now-completed ones
    cursor.execute("""
        UPDATE workstream_status
        SET status = 'pending',
            blocked_by = NULL
        WHERE blocked_by IN (
            SELECT workstream_id FROM workstream_status WHERE status = 'completed'
        )
    """)
    
    # Get next batch of workstreams to execute
    cursor.execute("""
        SELECT workstream_id FROM workstream_status
        WHERE status = 'pending'
        AND (blocked_by IS NULL OR blocked_by = '')
        ORDER BY priority DESC
        LIMIT ?
    """, (self.num_agents,))
```

---

## 📊 Conflict Statistics

Track conflict rates to identify problematic workstreams:

```sql
-- Get conflict rate by workstream
SELECT 
    workstream_id,
    COUNT(*) as total_attempts,
    SUM(CASE WHEN status = 'conflict' THEN 1 ELSE 0 END) as conflicts,
    ROUND(100.0 * SUM(CASE WHEN status = 'conflict' THEN 1 ELSE 0 END) / COUNT(*), 1) as conflict_rate_pct
FROM workstream_status_history
GROUP BY workstream_id
HAVING conflicts > 0
ORDER BY conflict_rate_pct DESC;
```

---

## ⚡ Quick Reference

| Situation | Command |
|-----------|---------|
| **View conflict details** | `cat reports/conflict_ws-<ID>.md` |
| **See which workstreams are blocked** | `sqlite3 .state/orchestration.db "SELECT * FROM workstream_status WHERE status='blocked'"` |
| **Manually resolve** | `git merge ws/<ID>/<agent> --no-commit` → fix → `git commit` |
| **Mark as resolved** | `sqlite3 .state/orchestration.db "UPDATE workstream_status SET status='completed' WHERE workstream_id='ws-<ID>'"` |
| **Resume orchestrator** | `.\scripts\run_multi_agent_refactor.ps1 -Resume` |
| **Skip workstream entirely** | `sqlite3 .state/orchestration.db "UPDATE workstream_status SET status='discarded' WHERE workstream_id='ws-<ID>'"` |

---

## 🎓 Best Practices

### Minimize Conflicts
1. **Better workstream decomposition** - Avoid overlapping file changes
2. **Merge frequently** - Don't let main get too far ahead
3. **Review dependency graph** - Ensure proper ordering

### Faster Resolution
1. **Always test after resolving** - Don't just remove markers blindly
2. **Use git mergetool** - Configure VS Code or Beyond Compare
3. **Document resolution reasoning** - Future you will thank you

### When to Get Help
- **Multiple files in conflict** - May indicate bad decomposition
- **Can't understand conflicting changes** - Review original workstream spec
- **Tests fail after resolution** - May need to rethink approach

---

**Last Updated**: 2025-11-29  
**Owner**: GitHub Copilot CLI  
**Related**: `FAILURE_RECOVERY_PLAYBOOK.md`, `ONE_TOUCH_IMPLEMENTATION_COMPLETE.md`
