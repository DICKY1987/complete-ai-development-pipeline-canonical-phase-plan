---
doc_id: DOC-GUIDE-PREVENTION-QUICKSTART-236
---

# Repository Cleanup Prevention - Quick Implementation

**Run these steps to prevent future file buildup**

---

## 1. Create Directory Structure (2 minutes)

```powershell
# Create organized folders
$dirs = @(
    "docs/planning/active",
    "docs/planning/archive", 
    "docs/completed/current",
    "docs/sessions",
    "temp/generated",
    "temp/reports"
)

foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
    Write-Host "Created: $dir"
}

Write-Host "`n✓ Directory structure created"
```

---

## 2. Update .gitignore (1 minute)

Add these lines to `.gitignore`:

```gitignore
# Temporary and generated files
temp/
*_[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_*.csv
*_[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_*.json
*_[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_*.txt
batch_*_results.json
*_output.json
*_generated.*

# Database WAL files
*.db-wal
*.db-shm

# Backup files  
*_backup.*
*_copy.*
* - Copy.*
*.bak
```

---

## 3. Create Weekly Maintenance Script (2 minutes)

Save as `scripts/weekly-maintenance.ps1`:

```powershell
# Weekly automatic cleanup
$timestamp = Get-Date -Format "yyyy-MM"

Write-Host "Weekly Maintenance - $(Get-Date)"

# 1. Archive completed docs older than 7 days
$cutoff = (Get-Date).AddDays(-7)
$oldCompleted = Get-ChildItem "docs/completed/current" -File -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -lt $cutoff }

if ($oldCompleted) {
    $archiveDir = "archive/$timestamp/completed"
    New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null
    $oldCompleted | ForEach-Object { Move-Item $_.FullName -Destination $archiveDir }
    Write-Host "✓ Archived $($oldCompleted.Count) completed docs"
}

# 2. Clean temp directory
if (Test-Path "temp") {
    $tempFiles = Get-ChildItem "temp" -Recurse -File
    if ($tempFiles) {
        Remove-Item "temp/*" -Recurse -Force
        Write-Host "✓ Cleaned $($tempFiles.Count) temp files"
    }
}

# 3. Checkpoint large WAL files
Get-ChildItem -Recurse -Filter "*.db-wal" | Where-Object { $_.Length -gt 5MB } | ForEach-Object {
    $dbPath = $_.FullName -replace '-wal$', ''
    python -c "import sqlite3; conn = sqlite3.connect('$dbPath'); conn.execute('PRAGMA wal_checkpoint(TRUNCATE)'); conn.close()"
    Write-Host "✓ Checkpointed $(Split-Path $dbPath -Leaf)"
}

Write-Host "`n✓ Maintenance complete"
```

---

## 4. Set Up Automated Weekly Run (3 minutes)

```powershell
# Schedule weekly maintenance for Sunday 2am
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$PWD\scripts\weekly-maintenance.ps1`""

$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 2am

$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive

Register-ScheduledTask -TaskName "RepoWeeklyMaintenance" `
    -Action $action -Trigger $trigger -Principal $principal `
    -Description "Weekly repository maintenance"

Write-Host "✓ Scheduled task created (runs Sundays at 2am)"
```

---

## 5. Create Quick Reference (1 minute)

Save as `docs/QUICK_FILE_GUIDE.md`:

```markdown
# Where to Put Files

## Planning Documents
📁 `docs/planning/active/` - Active phase/planning docs
- PHASE_*.md, *_PLAN.md
- Moved to archive/ after 30 days

## Completion Reports  
📁 `docs/completed/current/` - Finished work summaries
- *_COMPLETE.md, *_FINAL_REPORT.md
- Auto-archived after 7 days

## Session Summaries
📁 `docs/sessions/YYYY-MM-DD/` - Daily work logs
- SESSION_*.md
- Organized by date

## Generated/Temp Files
📁 `temp/` - Automated outputs (gitignored)
- *_20251201_*.csv, batch_*.json
- Auto-cleaned weekly

**Rule**: Never create planning/completion docs in root!
```

---

## 6. Create Health Check Script (2 minutes)

Save as `scripts/repo-health-check.ps1`:

```powershell
# Check repository health
Write-Host "Repository Health Check`n"

$issues = 0

# Check for misplaced files
$rootPlans = Get-ChildItem -File | Where-Object { $_.Name -match 'PLAN|PHASE' -and $_.Extension -eq '.md' }
if ($rootPlans) {
    Write-Host "⚠ $($rootPlans.Count) planning docs in root (move to docs/planning/active/)"
    $issues++
}

$rootComplete = Get-ChildItem -File | Where-Object { $_.Name -match 'COMPLETE|FINISHED|FINAL.*REPORT' }
if ($rootComplete) {
    Write-Host "⚠ $($rootComplete.Count) completion docs in root (move to docs/completed/current/)"
    $issues++
}

if (Test-Path "temp") {
    $tempSize = (Get-ChildItem "temp" -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    if ($tempSize -gt 10MB) {
        Write-Host "⚠ temp/ is $([math]::Round($tempSize/1MB))MB (run weekly-maintenance.ps1)"
        $issues++
    }
}

$largeWALs = Get-ChildItem -Recurse -Filter "*.db-wal" -ErrorAction SilentlyContinue | Where-Object { $_.Length -gt 5MB }
if ($largeWALs) {
    Write-Host "⚠ $($largeWALs.Count) large WAL files (run weekly-maintenance.ps1)"
    $issues++
}

if ($issues -eq 0) {
    Write-Host "✓ Repository is healthy!"
} else {
    Write-Host "`nRun: .\scripts\weekly-maintenance.ps1"
}
```

---

## 7. New Workflow

### Creating Files (Follow This!)

**Planning Document**:
```powershell
# ✓ CORRECT
New-Item "docs/planning/active/auth-feature-plan.md"

# ✗ WRONG
New-Item "AUTH_PHASE_PLAN.md"  # Don't create in root!
```

**Completion Report**:
```powershell
# ✓ CORRECT
New-Item "docs/completed/current/auth-feature-complete.md"

# ✗ WRONG
New-Item "AUTH_FEATURE_COMPLETE.md"  # Don't create in root!
```

**Session Summary**:
```powershell
# ✓ CORRECT
New-Item "docs/sessions/2025-12-01/work-summary.md"

# ✗ WRONG  
New-Item "SESSION_SUMMARY_2025-12-01.md"  # Don't create in root!
```

---

## 8. Monthly Check

Run this monthly:

```powershell
.\scripts\repo-health-check.ps1
```

If issues found, fix them:

```powershell
# Move misplaced files
Move-Item *_PLAN.md docs/planning/active/
Move-Item *_COMPLETE.md docs/completed/current/

# Run maintenance
.\scripts\weekly-maintenance.ps1
```

---

## Implementation Checklist

- [ ] Create directory structure
- [ ] Update .gitignore
- [ ] Create weekly-maintenance.ps1
- [ ] Schedule weekly task
- [ ] Create QUICK_FILE_GUIDE.md
- [ ] Create repo-health-check.ps1
- [ ] Test: Create file in docs/completed/current/ and verify it archives
- [ ] Add reminder to workflow documentation

**Time**: 11 minutes total
**Result**: Automated prevention of file buildup

---

## Test It Works

```powershell
# 1. Create test file
"# Test" | Out-File "docs/completed/current/test-complete.md"

# 2. Change date to 8 days ago (simulate old file)
(Get-Item "docs/completed/current/test-complete.md").LastWriteTime = (Get-Date).AddDays(-8)

# 3. Run maintenance
.\scripts\weekly-maintenance.ps1

# 4. Verify it was archived
Test-Path "archive/*/completed/test-complete.md"  # Should be True
```

---

**Golden Rule**: If a file has PLAN, COMPLETE, SESSION, or a timestamp in the name, it does NOT go in the repository root!
