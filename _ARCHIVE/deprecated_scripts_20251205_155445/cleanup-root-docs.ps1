# DOC_LINK: DOC-SCRIPT-CLEANUP-ROOT-DOCS-838
<#
.SYNOPSIS
  Clean up root-level planning/report files by moving them to organized folders.
#>

param(
    [string]$RootPath = ".",
    [switch]$WhatIf
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$keywords = @("PLAN", "REPORT", "QUICKSTART", "SUMMARY", "COMPLETE", "COMPLETED", "CHAT", "PHASE", "PROGRESS", "STATUS", "SESSION", "EXECUTION")

Write-Host "Scanning root-level planning documents..."

# Get root-level files
$rootFiles = Get-ChildItem -Path $RootPath -File | Where-Object {
    # Must be .md or .txt
    if ($_.Extension -ne ".md" -and $_.Extension -ne ".txt") {
        return $false
    }
    
    # Must match at least one keyword
    $name = $_.BaseName
    foreach ($kw in $keywords) {
        if ($name -like "*$kw*") {
            return $true
        }
    }
    return $false
}

if ($rootFiles.Count -eq 0) {
    Write-Host "No planning documents found in root."
    exit 0
}

Write-Host "Found $($rootFiles.Count) planning/report files in root:`n"
$rootFiles | Sort-Object Name | ForEach-Object { Write-Host "  - $($_.Name)" }
Write-Host ""

if ($WhatIf) {
    Write-Host "═══ WHAT-IF MODE ═══"
    Write-Host "No files will be moved. Remove -WhatIf to execute.`n"
} else {
    # Create destination folder
    $destFolder = Join-Path $RootPath "docs\planning_archive_$timestamp"
    New-Item -ItemType Directory -Path $destFolder -Force | Out-Null
    Write-Host "Created archive: $destFolder`n"
}

# Process files
$moved = 0
foreach ($file in $rootFiles) {
    if ($WhatIf) {
        Write-Host "[WOULD MOVE] $($file.Name)"
    } else {
        $dest = Join-Path $destFolder $file.Name
        Move-Item -LiteralPath $file.FullName -Destination $dest
        Write-Host "[MOVED] $($file.Name)"
        $moved++
    }
}

if (-not $WhatIf) {
    # Create README
    $readme = @"
# Planning Documents Archive

**Date**: $(Get-Date)
**Archived**: $moved files

These files were moved from the root to reduce clutter.

## Archived Files

"@
    
    $rootFiles | Sort-Object Name | ForEach-Object {
        $readme += "`n- $($_.Name)"
    }
    
    $readme += @"


## Restoration

To restore a file:
``````powershell
Copy-Item "docs\planning_archive_$timestamp\filename.md" .
``````
"@
    
    $readme | Out-File -FilePath (Join-Path $destFolder "README.md") -Encoding UTF8
    
    Write-Host ""
    Write-Host "✓ COMPLETE: Moved $moved files"
    Write-Host "  Location: $destFolder"
} else {
    Write-Host ""
    Write-Host "To execute: .\cleanup-root-docs.ps1"
}
