---
status: canonical
doc_type: adr
module_refs: []
script_refs: []
doc_id: DOC-ARCH-ADR_0008_DATABASE_LOCATION_WORKTREE-008
---

# ADR-0008: Database Location in Worktree

**Status:** Accepted  
**Date:** 2025-11-22  
**Deciders:** System Architecture Team  
**Context:** Need to determine where to store the SQLite database file for pipeline state

---

## Decision

The SQLite database will be stored at **`.worktrees/pipeline_state.db`** by default, configurable via the `PIPELINE_DB_PATH` environment variable.

---

## Rationale

### Requirements for Database Location

The database location must:
1. Be **git-ignored** - State should not be committed to version control
2. Be **discoverable** - Scripts and tools must find it reliably
3. Support **multiple worktrees** - Each git worktree should have independent state
4. Be **predictable** - Users and tools know where to look
5. Allow **override** - Power users can specify custom location

### Why `.worktrees/` Directory

1. **Semantic Meaning:** Name clearly indicates worktree-specific data
2. **Git Ignored by Default:** `.worktrees/` is in `.gitignore`
3. **Worktree Isolation:** Each worktree directory gets its own `.worktrees/` subfolder
4. **Discoverable:** Standard location relative to repository root
5. **Future Expansion:** Can store other worktree-specific data here

### Why Not Other Locations

**Not repository root:**
- Clutters root directory
- Easy to accidentally commit

**Not user home directory:**
- Loses association with repository
- Harder to back up with project
- Conflicts with multiple clones

**Not system temp directory:**
- Survives across sessions
- Harder to find and debug

---

## Consequences

### Positive

- **Clean Repository:** Database never accidentally committed
- **Worktree Independence:** Multiple worktrees don't interfere with each other
- **Easy Backup:** Backup `.worktrees/` to preserve state
- **Predictable Location:** Always `$(git rev-parse --show-toplevel)/.worktrees/pipeline_state.db`
- **Configuration Override:** Set `PIPELINE_DB_PATH` for custom location

### Negative

- **Not Obvious to New Users:** Must document the location
- **Manual Cleanup:** `.worktrees/` not cleaned automatically on worktree delete
- **Backup Required:** State not backed up by default

### Neutral

- **Environment Variable:** Users can override location if needed
- **Directory Creation:** Scripts must create `.worktrees/` if it doesn't exist

---

## Alternatives Considered

### Alternative 1: Repository Root (`pipeline_state.db`)

**Pros:**
- Very easy to find
- Obvious location

**Rejected because:**
- Easy to accidentally commit (despite .gitignore)
- Clutters repository root
- Name conflicts possible

### Alternative 2: XDG Base Directory (`~/.local/share/pipeline/`)

**Pros:**
- Follows XDG standard on Linux
- System-wide location

**Rejected because:**
- Not discoverable from repository
- Hard to backup with project
- Doesn't work for multiple repository clones
- XDG is Linux-only (doesn't help Windows/macOS users)

### Alternative 3: Hidden Directory (`.pipeline/state.db`)

**Pros:**
- Hidden from normal directory listings
- At repository root

**Rejected because:**
- `.pipeline/` could contain other things (config, cache)
- Not specific to worktree concept
- Still clutters root with hidden dirs

### Alternative 4: Temp Directory (`/tmp/pipeline_*.db`)

**Pros:**
- Automatically cleaned by OS
- Doesn't pollute repository

**Rejected because:**
- State lost on reboot (undesirable for long-running workflows)
- Hard to find for debugging
- Multiple users/processes could conflict

---

## Related Decisions

- [ADR-0003: SQLite State Storage](0003-sqlite-state-storage.md) - What we're storing
- [ADR-0001: Workstream Model Choice](0001-workstream-model-choice.md) - What state represents

---

## References

- **Database Module:** `core/state/db.py`
- **Environment Variable:** `PIPELINE_DB_PATH`
- **Default Path:** `.worktrees/pipeline_state.db`
- **Gitignore Entry:** `.gitignore` includes `.worktrees/`

---

## Notes

### Environment Variable Override

Users can specify custom location:

```bash
# Linux/macOS
export PIPELINE_DB_PATH="/path/to/custom/location.db"

# Windows PowerShell
$env:PIPELINE_DB_PATH = "C:\custom\location.db"

# One-time override
PIPELINE_DB_PATH=/tmp/test.db python scripts/run_workstream.py bundle.json
```

### Database Initialization

Scripts initialize database as needed:

```python
from core.state.db import init_db
import os

# Get database path (respects PIPELINE_DB_PATH)
db_path = os.getenv("PIPELINE_DB_PATH", ".worktrees/pipeline_state.db")

# Create directory if needed
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Initialize database
conn = init_db(db_path)
```

### Git Worktree Behavior

With git worktrees, each worktree gets its own `.worktrees/` directory:

```
repo/
├── .worktrees/
│   └── pipeline_state.db  # Main worktree state
└── .git/

repo-worktree-feature/
├── .worktrees/
│   └── pipeline_state.db  # Feature worktree state (independent!)
└── .git -> ../repo/.git/worktrees/feature/
```

This ensures:
- Feature branches can run workflows without affecting main
- Concurrent executions in different worktrees don't conflict
- State is isolated per worktree

### Backup Strategy

To backup pipeline state:

```bash
# Backup before risky operation
cp .worktrees/pipeline_state.db .worktrees/pipeline_state.db.backup

# Restore if needed
cp .worktrees/pipeline_state.db.backup .worktrees/pipeline_state.db
```

### Cleanup on Worktree Deletion

When deleting a worktree:

```bash
# Git worktree delete doesn't remove .worktrees/
git worktree remove feature-branch

# Manual cleanup if desired
rm -rf ../repo-worktree-feature/.worktrees/
```

Consider adding to `.git/hooks/post-worktree-delete` for automatic cleanup.

### Multiple Users on Same Machine

Each user gets their own state because:
- Repository is typically cloned per-user
- Each clone has its own `.worktrees/` directory
- File permissions prevent cross-user access

For shared repositories (rare), use `PIPELINE_DB_PATH` to specify user-specific location.

---

## Revision History

| Date | Change | Author |
|------|--------|--------|
| 2025-11-22 | Initial ADR created as part of Phase K+ | GitHub Copilot |
