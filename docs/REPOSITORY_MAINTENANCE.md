---
doc_id: DOC-GUIDE-REPOSITORY-MAINTENANCE-182
---

# Repository Maintenance - Prevention Strategy

**Purpose**: Prevent future buildup of planning docs, completion reports, and temporary files

---

## The Problem

Over time, these file types accumulated in the repository:
- 201 files in deprecated folders
- 148 completed implementation documents
- 82 phase/session/report planning docs
- 32 generated/temporary files

**Total**: 463 files that should have been archived earlier

---

## Prevention Strategy

### 1. Establish Clear File Lifecycle Rules

#### Rule 1: Completion Documents Auto-Archive After 7 Days
**Files**: *_COMPLETE.md, *_FINISHED.md, *_DONE.md, *_FINAL_REPORT.md

**Policy**:
- When implementation is complete, document goes to `docs/completed/YYYY-MM/`
- After 7 days in completed/, auto-archive to `archive/completed_implementations/`

**Automation**:
```powershell
# Run weekly (cron or Task Scheduler)
.\scripts\auto-archive-completed.ps1
```

#### Rule 2: Planning Documents Go to docs/planning/ (Not Root)
**Files**: *_PLAN.md, *_PHASE.md, PHASE_*.md

**Policy**:
- **Never create in root** - Always use `docs/planning/active/`
- When phase complete, move to `docs/planning/archive/YYYY-MM/`

**Enforcement**:
```bash
# Git pre-commit hook
.git/hooks/pre-commit
```

#### Rule 3: Session Reports in Timestamped Folders
**Files**: SESSION_*.md, *_SESSION_*.md

**Policy**:
- Create in `docs/sessions/YYYY-MM-DD/`
- Auto-archive sessions older than 30 days

#### Rule 4: Generated Files in .gitignore
**Files**: *_YYYYMMDD_*.csv, batch_*.json, *_output.json

**Policy**:
- Add to `.gitignore` - don't commit them
- Store in `temp/` directory (gitignored)
- Clear temp/ weekly

---

## Implementation

### Step 1: Create Organized Directory Structure

```powershell
# Create organized structure
$dirs = @(
    "docs/planning/active",
    "docs/planning/archive",
    "docs/completed/current",
    "docs/sessions",
    "temp/generated",
    "temp/reports"
)

foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force
    }
}
```

### Step 2: Update .gitignore

```gitignore
# Generated/temporary files
temp/
*.timestamp.csv
*_[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_*.csv
*_[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_*.json
batch_*_results.json
*_output.json
*_generated.json

# Database WAL files (checkpoint regularly instead)
*.db-wal
*.db-shm

# Backup files
*_backup.*
*_copy.*
* - Copy.*
*.bak
```

### Step 3: Create Pre-Commit Hook

Prevents committing files to wrong locations:

```bash
#!/bin/sh
# .git/hooks/pre-commit

# Check for planning docs in root
root_plans=$(git diff --cached --name-only | grep -E '^[A-Z_]+PLAN\.md$|^PHASE_.*\.md$')
if [ ! -z "$root_plans" ]; then
    echo "ERROR: Planning documents should go in docs/planning/active/, not root:"
    echo "$root_plans"
    echo ""
    echo "Move them with:"
    echo "  git mv FILE.md docs/planning/active/"
    exit 1
fi

# Check for completion docs in root
root_complete=$(git diff --cached --name-only | grep -E '^.*COMPLETE\.md$|^.*FINISHED\.md$|^.*FINAL.*REPORT\.md$')
if [ ! -z "$root_complete" ]; then
    echo "ERROR: Completion documents should go in docs/completed/current/, not root:"
    echo "$root_complete"
    echo ""
    echo "Move them with:"
    echo "  git mv FILE.md docs/completed/current/"
    exit 1
fi

exit 0
```

### Step 4: Create Weekly Maintenance Script

```powershell
# scripts/weekly-maintenance.ps1
<#
.SYNOPSIS
  Weekly repository maintenance - archive old files automatically.
#>

$timestamp = Get-Date -Format "yyyy-MM"

Write-Host "Weekly Repository Maintenance"
Write-Host "=" * 70
Write-Host ""

# 1. Archive completed docs older than 7 days
Write-Host "1. Archiving old completion documents..."
$cutoff = (Get-Date).AddDays(-7)
$oldCompleted = Get-ChildItem "docs/completed/current" -File -ErrorAction SilentlyContinue | 
    Where-Object { $_.LastWriteTime -lt $cutoff }

if ($oldCompleted.Count -gt 0) {
    $archiveDir = "archive/$timestamp/completed"
    New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null
    
    foreach ($file in $oldCompleted) {
        Move-Item $file.FullName -Destination $archiveDir
        Write-Host "  Archived: $($file.Name)"
    }
    Write-Host "  Total: $($oldCompleted.Count) files"
} else {
    Write-Host "  No old completion docs to archive"
}

# 2. Archive planning docs in archive folder older than 30 days
Write-Host ""
Write-Host "2. Archiving old planning documents..."
$cutoff30 = (Get-Date).AddDays(-30)
$oldPlans = Get-ChildItem "docs/planning/archive" -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -lt $cutoff30 }

if ($oldPlans.Count -gt 0) {
    $archiveDir = "archive/$timestamp/planning"
    New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null
    
    foreach ($file in $oldPlans) {
        $dest = Join-Path $archiveDir $file.Name
        Move-Item $file.FullName -Destination $dest
    }
    Write-Host "  Archived: $($oldPlans.Count) files"
} else {
    Write-Host "  No old planning docs to archive"
}

# 3. Clean temp directory
Write-Host ""
Write-Host "3. Cleaning temporary files..."
if (Test-Path "temp") {
    $tempFiles = Get-ChildItem "temp" -Recurse -File
    if ($tempFiles.Count -gt 0) {
        Remove-Item "temp/*" -Recurse -Force
        Write-Host "  Removed: $($tempFiles.Count) temp files"
    } else {
        Write-Host "  Temp directory already clean"
    }
}

# 4. Checkpoint database WAL files
Write-Host ""
Write-Host "4. Checkpointing database WAL files..."
$dbFiles = Get-ChildItem -Recurse -Filter "*.db" | Where-Object { 
    -not ($_.FullName -like "*archive*")
}

foreach ($db in $dbFiles) {
    $walFile = "$($db.FullName)-wal"
    if (Test-Path $walFile) {
        $walSize = [math]::Round((Get-Item $walFile).Length / 1MB, 2)
        if ($walSize -gt 1) {
            Write-Host "  Checkpointing $($db.Name) (WAL: ${walSize}MB)"
            python -c "import sqlite3; conn = sqlite3.connect('$($db.FullName)'); conn.execute('PRAGMA wal_checkpoint(TRUNCATE)'); conn.close()"
        }
    }
}

Write-Host ""
Write-Host "=" * 70
Write-Host "Maintenance complete!"
```

### Step 5: Document File Placement Guidelines

Create `docs/FILE_PLACEMENT_GUIDE.md`:

```markdown
# File Placement Guidelines

## Where to Put Different File Types

### Planning Documents
**Pattern**: *_PLAN.md, PHASE_*.md, *_PLANNING.md

**Location**: `docs/planning/active/`
- ✅ DO: Create in docs/planning/active/
- ❌ DON'T: Create in repository root
- When done: Move to docs/planning/archive/YYYY-MM/

### Completion Reports
**Pattern**: *_COMPLETE.md, *_FINISHED.md, *_FINAL_REPORT.md

**Location**: `docs/completed/current/`
- ✅ DO: Create in docs/completed/current/
- ❌ DON'T: Create in repository root
- Auto-archive: Moves to archive/ after 7 days

### Session Summaries
**Pattern**: SESSION_*.md, *_SESSION.md

**Location**: `docs/sessions/YYYY-MM-DD/`
- ✅ DO: Create in dated session folder
- ❌ DON'T: Create in root
- Auto-archive: After 30 days

### Generated/Temporary Files
**Pattern**: *_YYYYMMDD_*.*, batch_*.json, *_output.*

**Location**: `temp/` (gitignored)
- ✅ DO: Output to temp/ directory
- ❌ DON'T: Commit to git
- Auto-clean: Weekly maintenance removes old files

### Active Documentation
**Pattern**: README.md, CONTRIBUTING.md, guides

**Location**: Repository root or `docs/`
- README.md, CLAUDE.md, AGENTS.md → root
- Guides, references → `docs/`
```

---

## Automation Setup

### Windows Task Scheduler (Weekly Maintenance)

```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$PWD\scripts\weekly-maintenance.ps1`""

$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 2am

$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive

Register-ScheduledTask -TaskName "RepoWeeklyMaintenance" `
    -Action $action -Trigger $trigger -Principal $principal `
    -Description "Weekly repository maintenance - archive old files"
```

### Git Pre-Commit Hook

```bash
# Make hook executable
chmod +x .git/hooks/pre-commit

# Or use pre-commit framework
pip install pre-commit
# Create .pre-commit-config.yaml with custom hooks
```

---

## Developer Workflow Changes

### Creating Planning Documents

**Old (Bad)**:
```bash
# Creates in root - will accumulate!
echo "# Phase Plan" > NEW_PHASE_PLAN.md
```

**New (Good)**:
```bash
# Creates in organized location
echo "# Phase Plan" > docs/planning/active/phase-auth-system.md
```

### Completing Implementation

**Old (Bad)**:
```bash
# Completion doc stays in root forever
echo "# Complete" > FEATURE_COMPLETE.md
```

**New (Good)**:
```bash
# Goes to completed/, auto-archives after 7 days
echo "# Complete" > docs/completed/current/auth-system-complete.md
```

### Session Summaries

**Old (Bad)**:
```bash
# Creates in root
echo "# Session" > SESSION_SUMMARY_2025-12-01.md
```

**New (Good)**:
```bash
# Creates in dated folder
mkdir -p docs/sessions/2025-12-01
echo "# Session" > docs/sessions/2025-12-01/implementation-summary.md
```

---

## Monitoring & Alerts

### Monthly Health Check

Create `scripts/repo-health-check.ps1`:

```powershell
# Check for files in wrong places
Write-Host "Repository Health Check"
Write-Host "=" * 70

$issues = @()

# Check for planning docs in root
$rootPlans = Get-ChildItem -File | Where-Object { 
    $_.Name -match 'PLAN|PHASE' -and $_.Extension -eq '.md'
}
if ($rootPlans.Count -gt 0) {
    $issues += "⚠ $($rootPlans.Count) planning docs in root (should be in docs/planning/)"
}

# Check for completion docs in root
$rootComplete = Get-ChildItem -File | Where-Object {
    $_.Name -match 'COMPLETE|FINISHED|FINAL.*REPORT'
}
if ($rootComplete.Count -gt 0) {
    $issues += "⚠ $($rootComplete.Count) completion docs in root (should be in docs/completed/)"
}

# Check temp directory size
if (Test-Path "temp") {
    $tempSize = (Get-ChildItem "temp" -Recurse -File | Measure-Object -Property Length -Sum).Sum
    if ($tempSize -gt 10MB) {
        $issues += "⚠ temp/ directory is $([math]::Round($tempSize/1MB, 2))MB (should clean)"
    }
}

# Check for large WAL files
$largeWALs = Get-ChildItem -Recurse -Filter "*.db-wal" | Where-Object { $_.Length -gt 5MB }
if ($largeWALs.Count -gt 0) {
    $issues += "⚠ $($largeWALs.Count) large WAL files (need checkpointing)"
}

if ($issues.Count -eq 0) {
    Write-Host "✅ Repository is healthy!"
} else {
    Write-Host "Issues found:"
    $issues | ForEach-Object { Write-Host "  $_" }
    Write-Host ""
    Write-Host "Run: .\scripts\weekly-maintenance.ps1"
}
```

---

## Quick Reference Card

Save as `docs/QUICK_FILE_GUIDE.md`:

```markdown
# Quick File Placement Guide

| File Type | Goes In | Example |
|-----------|---------|---------|
| Planning docs | `docs/planning/active/` | phase-feature-x.md |
| Completion reports | `docs/completed/current/` | feature-x-complete.md |
| Session summaries | `docs/sessions/YYYY-MM-DD/` | 2025-12-01-work.md |
| Generated outputs | `temp/` (gitignored) | batch_results.json |
| Active docs | `docs/` or root | README.md, guides |

**Golden Rule**: Never create planning/completion docs in repository root!

**Maintenance**: Runs automatically every Sunday 2am (archives old files)

**Check health**: `.\scripts\repo-health-check.ps1`
```

---

## Implementation Checklist

- [ ] Create organized directory structure (docs/planning/, docs/completed/, etc.)
- [ ] Update .gitignore with temp files and generated outputs
- [ ] Create pre-commit hook to enforce file placement
- [ ] Create weekly-maintenance.ps1 script
- [ ] Set up Windows Task Scheduler for weekly maintenance
- [ ] Create repo-health-check.ps1 monitoring script
- [ ] Document guidelines in FILE_PLACEMENT_GUIDE.md
- [ ] Create QUICK_FILE_GUIDE.md reference
- [ ] Train team on new workflow
- [ ] Add to onboarding documentation

---

## Success Metrics

After 1 month, measure:
- ✅ Zero planning docs in root
- ✅ Zero completion docs in root
- ✅ temp/ directory < 10 MB
- ✅ WAL files < 5 MB
- ✅ Auto-archive runs successfully weekly

**Goal**: Never need manual cleanup again!
