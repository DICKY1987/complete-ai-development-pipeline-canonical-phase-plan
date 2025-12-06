# DOC_LINK: DOC-SCRIPT-CLEANUP-ROOT-PLANNING-DOCS-837
<#
.SYNOPSIS
  Clean up root-level planning/report files by moving them to organized folders.

.DESCRIPTION
  Identifies planning/execution documents in the root and moves them to
  appropriate subdirectories (docs/, developer/, archive/)
#>

param(
    [string]$RootPath = "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan",
    [switch]$WhatIf
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# Keywords to match
$keywords = @("PLAN", "REPORT", "QUICKSTART", "SUMMARY", "COMPLETE", "COMPLETED", "CHAT", "PHASE", "PROGRESS", "STATUS", "SESSION")

# Get root-level files only
Write-Host "Scanning root-level planning documents..."
$rootFiles = Get-ChildItem -Path $RootPath -File -ErrorAction SilentlyContinue | Where-Object {
    ($_.Extension -eq ".md" -or $_.Extension -eq ".txt") -and
    ($keywords | Where-Object { $_.BaseName -like "*$_*" }).Count -gt 0
}

if ($rootFiles.Count -eq 0) {
    Write-Host "No planning documents found in root."
    exit 0
}

Write-Host "Found $($rootFiles.Count) planning/report files in root:"
$rootFiles | ForEach-Object { Write-Host "  - $($_.Name)" }
Write-Host ""

if ($WhatIf) {
    Write-Host "WHAT-IF MODE: No files will be moved."
    Write-Host ""
}

# Create destination folder
$destFolder = Join-Path $RootPath "docs\planning_archive_$timestamp"

if (-not $WhatIf) {
    New-Item -ItemType Directory -Path $destFolder -Force | Out-Null
    Write-Host "Created: $destFolder"
    Write-Host ""
}

# Move files
$moved = 0
foreach ($file in $rootFiles) {
    $dest = Join-Path $destFolder $file.Name
    
    if ($WhatIf) {
        Write-Host "Would move: $($file.Name) -> $destFolder"
    } else {
        Write-Host "Moving: $($file.Name)"
        Move-Item -LiteralPath $file.FullName -Destination $dest
        $moved++
    }
}

if (-not $WhatIf) {
    # Create README
    $readme = @"
# Planning Documents Archive

**Date**: $(Get-Date)
**Count**: $moved files

These files were moved from the root to reduce clutter.

## Files Archived

"@
    
    $rootFiles | ForEach-Object {
        $readme += "`n- $($_.Name)"
    }
    
    $readme | Out-File -FilePath (Join-Path $destFolder "README.md") -Encoding UTF8
    
    Write-Host ""
    Write-Host "✓ Moved $moved files to: $destFolder"
} else {
    Write-Host ""
    Write-Host "Run without -WhatIf to execute: .\cleanup-root-planning-docs.ps1"
}
