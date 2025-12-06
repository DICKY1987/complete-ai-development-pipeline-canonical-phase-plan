# DOC_LINK: DOC-SCRIPT-REPO-HEALTH-CHECK-834
<#
.SYNOPSIS
  Repository health check - detect files in wrong locations.

.DESCRIPTION
  Checks for planning docs, completion reports, and other files that should
  be in organized folders but are in the repository root.
#>

Write-Host "=" * 70
Write-Host "REPOSITORY HEALTH CHECK"
Write-Host "=" * 70
Write-Host "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

$issues = @()
$warnings = @()

# Check for planning docs in root
$rootPlans = Get-ChildItem -File -ErrorAction SilentlyContinue | 
    Where-Object { 
        ($_.Name -match 'PLAN|PHASE') -and 
        $_.Extension -eq '.md' -and
        $_.Name -notin @('README.md', 'CLAUDE.md', 'AGENTS.md')
    }

if ($rootPlans.Count -gt 0) {
    $issues += "Planning docs in root: $($rootPlans.Count)"
    Write-Host "⚠ ISSUE: $($rootPlans.Count) planning docs found in root"
    Write-Host "   Should be in: docs/planning/active/"
    $rootPlans | ForEach-Object { Write-Host "     - $($_.Name)" }
    Write-Host ""
}

# Check for completion docs in root
$rootComplete = Get-ChildItem -File -ErrorAction SilentlyContinue |
    Where-Object {
        ($_.Name -match 'COMPLETE|FINISHED|FINAL.*REPORT') -and
        $_.Extension -in @('.md', '.txt')
    }

if ($rootComplete.Count -gt 0) {
    $issues += "Completion docs in root: $($rootComplete.Count)"
    Write-Host "⚠ ISSUE: $($rootComplete.Count) completion docs found in root"
    Write-Host "   Should be in: docs/completed/current/"
    $rootComplete | ForEach-Object { Write-Host "     - $($_.Name)" }
    Write-Host ""
}

# Check for session summaries in root
$rootSessions = Get-ChildItem -File -ErrorAction SilentlyContinue |
    Where-Object {
        ($_.Name -match 'SESSION') -and
        $_.Extension -eq '.md'
    }

if ($rootSessions.Count -gt 0) {
    $issues += "Session docs in root: $($rootSessions.Count)"
    Write-Host "⚠ ISSUE: $($rootSessions.Count) session docs found in root"
    Write-Host "   Should be in: docs/sessions/YYYY-MM-DD/"
    $rootSessions | ForEach-Object { Write-Host "     - $($_.Name)" }
    Write-Host ""
}

# Check temp directory size
if (Test-Path "temp") {
    $tempSize = (Get-ChildItem "temp" -Recurse -File -ErrorAction SilentlyContinue | 
        Measure-Object -Property Length -Sum).Sum
    
    if ($tempSize -gt 10MB) {
        $warnings += "Large temp directory: $([math]::Round($tempSize/1MB, 2))MB"
        Write-Host "⚠ WARNING: temp/ directory is $([math]::Round($tempSize/1MB, 2))MB"
        Write-Host "   Recommended: Run weekly-maintenance.ps1 to clean"
        Write-Host ""
    }
}

# Check for large WAL files
$largeWALs = Get-ChildItem -Recurse -Filter "*.db-wal" -ErrorAction SilentlyContinue | 
    Where-Object { $_.Length -gt 5MB }

if ($largeWALs.Count -gt 0) {
    $warnings += "Large WAL files: $($largeWALs.Count)"
    Write-Host "⚠ WARNING: $($largeWALs.Count) large WAL file(s)"
    $largeWALs | ForEach-Object {
        $size = [math]::Round($_.Length/1MB, 2)
        Write-Host "     - $($_.Name): ${size}MB"
    }
    Write-Host "   Recommended: Run weekly-maintenance.ps1 to checkpoint"
    Write-Host ""
}

# Check for timestamped files in root
$timestampedFiles = Get-ChildItem -File -ErrorAction SilentlyContinue |
    Where-Object { $_.BaseName -match '\d{8}(_\d{6})?$' }

if ($timestampedFiles.Count -gt 0) {
    $warnings += "Timestamped files in root: $($timestampedFiles.Count)"
    Write-Host "⚠ WARNING: $($timestampedFiles.Count) timestamped files in root"
    Write-Host "   These are likely generated reports/indexes"
    $timestampedFiles | Select-Object -First 5 | ForEach-Object { 
        Write-Host "     - $($_.Name)" 
    }
    if ($timestampedFiles.Count -gt 5) {
        Write-Host "     ... and $($timestampedFiles.Count - 5) more"
    }
    Write-Host ""
}

# Summary
Write-Host "=" * 70
Write-Host "HEALTH CHECK SUMMARY"
Write-Host "=" * 70

if ($issues.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "✓ Repository is healthy!"
    Write-Host "  No issues or warnings found."
} else {
    if ($issues.Count -gt 0) {
        Write-Host "Issues found: $($issues.Count)"
        $issues | ForEach-Object { Write-Host "  - $_" }
        Write-Host ""
    }
    
    if ($warnings.Count -gt 0) {
        Write-Host "Warnings: $($warnings.Count)"
        $warnings | ForEach-Object { Write-Host "  - $_" }
        Write-Host ""
    }
    
    Write-Host "Recommended actions:"
    if ($issues.Count -gt 0) {
        Write-Host "  1. Move misplaced files to correct locations"
        Write-Host "     - Planning docs → docs/planning/active/"
        Write-Host "     - Completion docs → docs/completed/current/"
        Write-Host "     - Session docs → docs/sessions/YYYY-MM-DD/"
    }
    Write-Host "  2. Run maintenance: .\scripts\weekly-maintenance.ps1"
}

Write-Host ""
