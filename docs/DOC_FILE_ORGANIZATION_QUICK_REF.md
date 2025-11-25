# File Organization Quick Reference

> **Purpose**: Quick lookup guide for where files should go  
> **See Also**: [FILE_ORGANIZATION_SYSTEM.md](FILE_ORGANIZATION_SYSTEM.md) for complete specification

---

## Quick Decision Tree

```
Is this file...

├─ Generated at runtime (logs, cache, state)?
│  └─ ✅ Put in: .worktrees/, .runs/, .tasks/, .ledger/, logs/
│      (Git: IGNORED)
│
├─ Production code or config?
│  └─ ✅ Put in: core/, engine/, error/, scripts/, tests/, config/, schema/
│      (Git: COMMITTED, in releases)
│
├─ User-facing documentation?
│  └─ ✅ Put in: docs/ or root README.md, AGENTS.md, etc.
│      (Git: COMMITTED, in releases)
│
└─ Development artifact (planning, sessions, progress tracking)?
   └─ ✅ Put in: devdocs/phases/, devdocs/sessions/, devdocs/execution/
       (Git: COMMITTED for continuity, EXCLUDED from releases)
```

---

## File Placement by Type

| File Type | Location | Example | Git Status |
|-----------|----------|---------|------------|
| **Python module** | `core/`, `engine/`, `error/` | `core/state/db.py` | ✅ Committed |
| **Test file** | `tests/` | `tests/pipeline/test_db.py` | ✅ Committed |
| **Automation script** | `scripts/` | `scripts/bootstrap.ps1` | ✅ Committed |
| **JSON schema** | `schema/` | `schema/workstream.schema.json` | ✅ Committed |
| **Config file** | `config/` | `config/adapter-profiles.json` | ✅ Committed |
| **Example workstream** | `workstreams/` | `workstreams/single/example.json` | ✅ Committed |
| **Architecture doc** | `docs/` | `docs/ARCHITECTURE.md` | ✅ Committed |
| **API reference** | `docs/reference/` | `docs/reference/api-overview.md` | ✅ Committed |
| **Main README** | Root | `README.md`, `AGENTS.md` | ✅ Committed |
| **Phase plan** | `devdocs/phases/phase-x/` | `devdocs/phases/phase-i/PLAN.md` | ✅ Committed* |
| **Phase completion** | `devdocs/phases/phase-x/` | `devdocs/phases/phase-i/COMPLETE.md` | ✅ Committed* |
| **Session log** | `devdocs/sessions/` | `devdocs/sessions/SESSION_2025-11-22.md` | ✅ Committed* |
| **Execution summary** | `devdocs/execution/` | `devdocs/execution/PHASE_I_SUMMARY.md` | ✅ Committed* |
| **Progress report** | `devdocs/execution/` | `devdocs/execution/WS_G2_PROGRESS.md` | ✅ Committed* |
| **Analysis report** | `devdocs/analysis/` | `devdocs/analysis/METRICS_SUMMARY.md` | ✅ Committed* |
| **Handoff doc** | `devdocs/handoffs/` | `devdocs/handoffs/HANDOFF_2025-11-20.md` | ✅ Committed* |
| **Planning doc** | `devdocs/planning/` | `devdocs/planning/PHASE_ROADMAP.md` | ✅ Committed* |
| **Archived dev work** | `devdocs/archive/` | `devdocs/archive/2025-11/phase-h/` | ✅ Committed* |
| **Runtime worktree** | `.worktrees/` | `.worktrees/ws-abc-123/` | ❌ Ignored |
| **Execution run** | `.runs/` | `.runs/run_20251122_170000/` | ❌ Ignored |
| **Task queue** | `.tasks/` | `.tasks/pending/task_001.json` | ❌ Ignored |
| **Execution ledger** | `.ledger/` | `.ledger/execution.jsonl` | ❌ Ignored |
| **Log file** | `logs/` | `logs/pipeline_20251122.log` | ❌ Ignored |
| **Python cache** | `__pycache__/` | `__pycache__/db.cpython-311.pyc` | ❌ Ignored |

\* Committed for continuity, but excluded from distribution packages

---

## Naming Conventions

### System Files (Production)

```python
# Python modules
core/state/db.py                          # snake_case
engine/orchestrator.py                    # snake_case
error/plugins/python_ruff/plugin.py       # snake_case

# Tests
tests/pipeline/test_orchestrator.py       # test_*.py

# Scripts
scripts/bootstrap.ps1                     # snake_case.ps1
scripts/validate_workstreams.py           # snake_case.py

# Config
config/adapter-profiles.json              # kebab-case.json
config/circuit-breaker.yaml               # kebab-case.yaml

# Documentation (system)
docs/ARCHITECTURE.md                      # ALL_CAPS (major docs)
docs/reference/api-overview.md            # kebab-case (specific guides)
```

### Development Artifacts

```markdown
# Phase documentation
devdocs/phases/phase-i/PLAN.md                      # PHASE_<ID>_PLAN.md
devdocs/phases/phase-i/EXECUTION_SUMMARY.md         # PHASE_<ID>_EXECUTION_SUMMARY.md
devdocs/phases/phase-i/COMPLETE.md                  # PHASE_<ID>_COMPLETE.md

# Session logs
devdocs/sessions/SESSION_2025-11-22_ERROR_PIPELINE.md    # SESSION_<DATE>_<DESC>.md

# Execution tracking
devdocs/execution/WORKSTREAM_G2_PROGRESS.md         # <CONTEXT>_PROGRESS.md
devdocs/execution/PHASE_I_EXECUTION_SUMMARY.md      # <CONTEXT>_EXECUTION_SUMMARY.md

# Analysis
devdocs/analysis/DUPLICATE_ANALYSIS.md              # <TYPE>_ANALYSIS.md
devdocs/analysis/METRICS_SUMMARY_20251120.md        # METRICS_SUMMARY_<DATE>.md

# Handoffs
devdocs/handoffs/HANDOFF_2025-11-20_UET.md          # HANDOFF_<DATE>_<DESC>.md
```

---

## Common Scenarios

### "I'm starting a new phase"

1. Create directory: `devdocs/phases/phase-k/`
2. Create plan: `devdocs/phases/phase-k/PLAN.md`
3. Track progress: `devdocs/execution/PHASE_K_PROGRESS.md` (optional)
4. When done: `devdocs/phases/phase-k/COMPLETE.md`

### "I finished a work session"

1. Create log: `devdocs/sessions/SESSION_YYYY-MM-DD_<SHORT_DESC>.md`
2. Include: what was done, decisions made, next steps
3. Commit to preserve continuity

### "I'm analyzing code or metrics"

1. Create report: `devdocs/analysis/<TYPE>_ANALYSIS.md`
2. Or dated: `devdocs/analysis/METRICS_SUMMARY_YYYYMMDD.md`

### "I'm handing off work to another session"

1. Create: `devdocs/handoffs/HANDOFF_YYYY-MM-DD_<CONTEXT>.md`
2. Include: current state, blockers, next steps, references

### "The phase is complete and I want to clean up"

1. Review: `devdocs/phases/phase-x/` - ensure COMPLETE.md exists
2. Archive: Move to `devdocs/archive/YYYY-MM/phase-x/`
3. Update: `devdocs/archive/YYYY-MM/ARCHIVE_SUMMARY.md` with what was moved

### "I'm writing production code"

1. Python module → `core/`, `engine/`, `error/` (appropriate subdirectory)
2. Test → `tests/` (mirror the structure: `tests/core/state/test_db.py`)
3. Script → `scripts/`
4. Config → `config/`
5. Schema → `schema/`

### "I'm documenting the system"

1. Architecture / major doc → `docs/ARCHITECTURE.md` (ALL_CAPS)
2. User guide / reference → `docs/reference/guide-name.md` (kebab-case)
3. API doc → `docs/reference/api-overview.md`
4. Main README → Root level

---

## Migration Helpers

### Moving Phase Documentation

**Before**:
```
docs/PHASE_I_PLAN.md
docs/PHASE_I_EXECUTION_SUMMARY.md
docs/PHASE_I_COMPLETE.md
```

**After**:
```
devdocs/phases/phase-i/PLAN.md
devdocs/phases/phase-i/EXECUTION_SUMMARY.md
devdocs/phases/phase-i/COMPLETE.md
```

**Command**:
```powershell
# Create phase directory
New-Item -ItemType Directory -Path "devdocs\phases\phase-i"

# Move files
Move-Item "docs\PHASE_I_PLAN.md" "devdocs\phases\phase-i\PLAN.md"
Move-Item "docs\PHASE_I_EXECUTION_SUMMARY.md" "devdocs\phases\phase-i\EXECUTION_SUMMARY.md"
Move-Item "docs\PHASE_I_COMPLETE.md" "devdocs\phases\phase-i\COMPLETE.md"
```

### Moving Session Logs

**Before**:
```
docs/sessions/SESSION_SUMMARY_2025-11-19.md
UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/SESSION_SUMMARY_2025-11-20_MEGA_SESSION.md
```

**After**:
```
devdocs/sessions/SESSION_2025-11-19_SUMMARY.md
devdocs/sessions/uet/SESSION_2025-11-20_MEGA_SESSION.md
```

---

## Anti-Patterns (What NOT to Do)

❌ **DON'T** put phase plans in `docs/`
```
docs/PHASE_K_PLAN.md          # ❌ Wrong
devdocs/phases/phase-k/PLAN.md  # ✅ Correct
```

❌ **DON'T** put session logs in root or random directories
```
SESSION_2025-11-22.md                        # ❌ Wrong
some_feature/SESSION_LOG.md                  # ❌ Wrong
devdocs/sessions/SESSION_2025-11-22.md       # ✅ Correct
```

❌ **DON'T** put production code in development directories
```
devdocs/new_feature/orchestrator.py          # ❌ Wrong
core/engine/orchestrator.py                  # ✅ Correct
```

❌ **DON'T** commit runtime artifacts
```
.worktrees/ws-123/file.py                    # ❌ Should be gitignored
logs/pipeline_20251122.log                   # ❌ Should be gitignored
```

❌ **DON'T** mix file naming conventions
```
core/state/DatabaseManager.py                # ❌ Wrong (PascalCase)
core/state/db.py                             # ✅ Correct (snake_case)
```

---

## Quick Links

- **Full Specification**: [FILE_ORGANIZATION_SYSTEM.md](FILE_ORGANIZATION_SYSTEM.md)
- **Repository Guide**: [DIRECTORY_GUIDE.md](../DIRECTORY_GUIDE.md)
- **Development Guidelines**: [AGENTS.md](../AGENTS.md)
- **Architecture Overview**: [ARCHITECTURE.md](ARCHITECTURE.md)

---

**END OF QUICK REFERENCE**
