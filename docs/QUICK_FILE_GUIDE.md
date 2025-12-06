---
doc_id: DOC-GUIDE-QUICK-FILE-GUIDE-184
---

# Quick File Placement Guide

**Where to put files in this repository**

---

## Planning Documents
📁 **Location**: `docs/planning/active/`

**Patterns**: *_PLAN.md, PHASE_*.md, *_PLANNING.md

**Examples**:
- ✅ `docs/planning/active/auth-feature-plan.md`
- ✅ `docs/planning/active/phase-5-deployment.md`
- ❌ `NEW_FEATURE_PLAN.md` (don't create in root!)

**Lifecycle**: Moved to `docs/planning/archive/` after 30 days

---

## Completion Reports
📁 **Location**: `docs/completed/current/`

**Patterns**: *_COMPLETE.md, *_FINISHED.md, *_FINAL_REPORT.md

**Examples**:
- ✅ `docs/completed/current/auth-feature-complete.md`
- ✅ `docs/completed/current/migration-finished.md`
- ❌ `FEATURE_COMPLETE.md` (don't create in root!)

**Lifecycle**: Auto-archived to `archive/` after 7 days

---

## Session Summaries
📁 **Location**: `docs/sessions/YYYY-MM-DD/`

**Patterns**: SESSION_*.md, *_SESSION.md, work logs

**Examples**:
- ✅ `docs/sessions/2025-12-01/work-summary.md`
- ✅ `docs/sessions/2025-12-01/implementation-notes.md`
- ❌ `SESSION_SUMMARY_2025-12-01.md` (don't create in root!)

**Lifecycle**: Organized by date, archived after 30 days

---

## Generated/Temporary Files
📁 **Location**: `temp/` (gitignored)

**Patterns**: *_YYYYMMDD_*.*, batch_*.json, *_output.*

**Examples**:
- ✅ `temp/generated/batch_results.json`
- ✅ `temp/reports/file_index_20251201.csv`
- ❌ `batch_results.json` (don't commit to git!)

**Lifecycle**: Cleaned weekly by maintenance script

---

## Active Documentation
📁 **Location**: Repository root or `docs/`

**Files**:
- README.md, CLAUDE.md, AGENTS.md → **Root**
- Guides, references, specs → **docs/**
- Architecture docs → **docs/architecture/**

---

## Quick Rules

### ✅ DO
- Create planning docs in `docs/planning/active/`
- Create completion reports in `docs/completed/current/`
- Create session logs in `docs/sessions/YYYY-MM-DD/`
- Output generated files to `temp/`

### ❌ DON'T
- Create planning docs in repository root
- Create completion reports in repository root
- Create timestamped files in repository root
- Commit files from `temp/` to git

---

## Automation

### Weekly Maintenance (Automated)
**Schedule**: Every Sunday at 2:00 AM  
**Script**: `scripts/weekly-maintenance.ps1`

**Actions**:
- Archives completion docs older than 7 days
- Archives planning docs older than 30 days
- Cleans `temp/` directory
- Checkpoints large database WAL files

### Monthly Health Check (Manual)
**Run**: `.\scripts\repo-health-check.ps1`

**Checks**:
- Files in wrong locations
- Large temp directory
- Large WAL files
- Timestamped files in root

---

## Examples

### Starting New Work
```powershell
# Planning phase
New-Item "docs/planning/active/user-auth-feature.md"

# During implementation
New-Item "docs/sessions/2025-12-01/auth-implementation.md"

# After completion
New-Item "docs/completed/current/user-auth-complete.md"
```

### Generated Scripts
```powershell
# Output to temp (gitignored)
$results | ConvertTo-Json | Out-File "temp/generated/results.json"

# Never do this:
$results | ConvertTo-Json | Out-File "results_20251201.json"  # ❌ Root!
```

---

## Need Help?

**Full documentation**: `docs/REPOSITORY_MAINTENANCE.md`  
**Quick setup**: `PREVENTION_QUICKSTART.md`  
**Prevention system**: `PREVENTION_SYSTEM_STATUS.md`

**Run health check**: `.\scripts\repo-health-check.ps1`  
**Run maintenance**: `.\scripts\weekly-maintenance.ps1`

---

**Golden Rule**: If a file has PLAN, COMPLETE, SESSION, or a timestamp in the name, it does NOT go in the repository root!
