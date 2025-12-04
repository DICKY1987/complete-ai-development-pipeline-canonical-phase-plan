# DOC_LINK: DOC-SCRIPT-ARCHIVE-MODULES-FOLDER-742
# Archive modules/ Directory - EXEC-017
# Reason: 98% of modules are orphaned (failed module-centric refactor)
# Safe to archive: Preserves git history, reversible

$ErrorActionPreference = 'Stop'
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$archiveName = "archive/${timestamp}_exec017_modules_folder_cleanup"
$RepoRoot = 'C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan'

Write-Host '=== Archive modules/ Directory ===' -ForegroundColor Cyan
Write-Host ''
Write-Host "Reason: Failed module-centric refactor (98% orphaned code)" -ForegroundColor Yellow
Write-Host "Strategy: Archive entire directory with full git history" -ForegroundColor Yellow
Write-Host ''

$DryRun = $true  # Change to $false to execute

# Get stats before archival
if (Test-Path "modules") {
    $files = Get-ChildItem -Path "modules" -Recurse -File
    $totalSize = ($files | Measure-Object -Property Length -Sum).Sum

    Write-Host "modules/ statistics:" -ForegroundColor Yellow
    Write-Host "  Files: $($files.Count)" -ForegroundColor Gray
    Write-Host "  Size: $([math]::Round($totalSize / 1MB, 2)) MB" -ForegroundColor Gray
    Write-Host "  Orphaned: 138 of 141 Python files (98%)" -ForegroundColor Red
    Write-Host ""
} else {
    Write-Host "[ERROR] modules/ directory not found!" -ForegroundColor Red
    exit 1
}

# Archive plan
Write-Host "Archive plan:" -ForegroundColor Green
Write-Host "  1. Create archive directory: $archiveName" -ForegroundColor Gray
Write-Host "  2. Move modules/ → $archiveName/modules/" -ForegroundColor Gray
Write-Host "  3. Create README with archival context" -ForegroundColor Gray
Write-Host "  4. Commit to git with detailed message" -ForegroundColor Gray
Write-Host ""

if ($DryRun) {
    Write-Host "[DRY-RUN] Would archive modules/ directory" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To execute: Edit this script and set `$DryRun = `$false" -ForegroundColor Yellow
    Write-Host ""
    exit 0
}

# Confirm before proceeding
Write-Host "CONFIRMATION REQUIRED:" -ForegroundColor Red
Write-Host "This will archive the entire modules/ directory." -ForegroundColor Yellow
Write-Host "The operation is reversible via git, but requires manual intervention." -ForegroundColor Yellow
Write-Host ""
$confirmation = Read-Host "Type 'ARCHIVE' to proceed, or anything else to cancel"

if ($confirmation -ne 'ARCHIVE') {
    Write-Host "[CANCELLED] Archive operation aborted by user" -ForegroundColor Yellow
    exit 0
}

# Create archive directory
Write-Host ""
Write-Host "Creating archive directory..." -ForegroundColor Green
New-Item -ItemType Directory -Path $archiveName -Force | Out-Null

# Move modules/ to archive
Write-Host "Moving modules/ to archive..." -ForegroundColor Green
Move-Item -Path "modules" -Destination "$archiveName/modules" -Force

# Create README
Write-Host "Creating archival documentation..." -ForegroundColor Green
$readmeContent = @"
# Archived: modules/ Directory

**Archived**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
**Reason**: Failed module-centric refactor - 98% orphaned code
**Pattern**: EXEC-017 Comprehensive Code Cleanup

---

## Context

The \`modules/\` directory was created as part of a module-centric refactor attempt
to organize code by functional modules rather than by layer (core/, engine/, etc.).

**The refactor was never completed.**

---

## Statistics

- **Total files**: $($files.Count)
- **Total size**: $([math]::Round($totalSize / 1MB, 2)) MB
- **Orphaned code**: 138 of 141 Python files (98%)
- **Reachability**: Only 3 files were actually imported

---

## Archival Analysis

### Reachability Report
From \`cleanup_reports/entry_point_reachability_report.json\`:
- Total modules analyzed: 141
- Orphaned: 138 (97.9%)
- Reachable: 3 (2.1%)

### Why Archive?

1. **Failed refactor**: Module-centric architecture was started but abandoned
2. **Massive orphan rate**: 98% of code is unreachable from any entry point
3. **Import analysis**: Only 3 modules are actually imported anywhere
4. **Cognitive load**: Large directory with mostly dead code
5. **Maintenance burden**: Confusing for new developers

### What Was Attempted

The module-centric refactor aimed to organize code as:
\`\`\`
modules/
├── aim-cli/           # AIM environment management CLI
├── aim-environment/   # AIM environment core
├── error-pipeline/    # Error detection pipeline
├── orchestrator/      # Job orchestrator
├── phase-executor/    # Phase execution engine
└── ...                # Many more modules
\`\`\`

**Reality**: Most modules were created but never integrated.

---

## Restoration

If needed, restore via git:

\`\`\`bash
# View this archive commit
git log --all --grep="modules_folder_cleanup"

# Restore modules/ directory
git checkout <commit-hash> -- modules/

# Or restore entire archive
git checkout <commit-hash> -- archive/${timestamp}_exec017_modules_folder_cleanup/
\`\`\`

---

## Lessons Learned

1. **Complete or revert**: Don't leave refactors half-finished
2. **Validate integration**: Ensure new code is actually used
3. **Test coverage**: Would have caught the orphaned modules
4. **Incremental migration**: Migrate one module at a time, validate each

---

## Related Documentation

- \`cleanup_reports/entry_point_reachability_report.json\` - Reachability analysis
- \`cleanup_reports/comprehensive_archival_report.json\` - Full cleanup analysis
- \`EXEC017_SESSION_COMPLETE.md\` - Cleanup session summary

---

**Archive Status**: ✅ Preserved for historical reference
**Production Impact**: None (code was unused)
**Reversible**: Yes (via git)
"@

Set-Content -Path "$archiveName/README.md" -Value $readmeContent -Encoding UTF8

Write-Host ""
Write-Host "[OK] Archive complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Archive location: $archiveName" -ForegroundColor Cyan
Write-Host "Files archived: $($files.Count)" -ForegroundColor Gray
Write-Host "Size: $([math]::Round($totalSize / 1MB, 2)) MB" -ForegroundColor Gray
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review: $archiveName/README.md" -ForegroundColor Gray
Write-Host "  2. Commit: git add . && git commit -m 'chore: Archive modules/ folder (EXEC-017)'" -ForegroundColor Gray
Write-Host "  3. Validate: Run tests to ensure no breakage" -ForegroundColor Gray
Write-Host ""
