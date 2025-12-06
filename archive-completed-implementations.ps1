# DOC_LINK: DOC-SCRIPT-ARCHIVE-COMPLETED-IMPLEMENTATIONS-829
<#
.SYNOPSIS
  Archive completed implementation documents to cleanup the repository.

.DESCRIPTION
  Finds documents about completed implementations and moves them to archive.
  Looks for files with COMPLETE, COMPLETED, FINISHED, etc. in the name
  and verifies completion status in content.

.PARAMETER WhatIf
  Preview what will be archived without moving files.
#>

param([switch]$WhatIf)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$completionKeywords = @(
    "COMPLETE", "COMPLETED", "COMPLETION", "FINISHED", "DONE",
    "SUCCESS", "FINAL", "SUMMARY"
)

Write-Host "=" * 70
Write-Host "ARCHIVE COMPLETED IMPLEMENTATION DOCUMENTS"
Write-Host "=" * 70
Write-Host ""

# Find all completion documents
$allDocs = Get-ChildItem -Recurse -File | Where-Object {
    ($_.Extension -eq ".md" -or $_.Extension -eq ".txt") -and
    -not ($_.FullName -like "*archive*") -and
    -not ($_.FullName -like "*.git*") -and
    -not ($_.FullName -like "*node_modules*")
}

$completedDocs = foreach ($doc in $allDocs) {
    $matchesFilename = $false
    foreach ($kw in $completionKeywords) {
        if ($doc.BaseName -like "*$kw*") {
            $matchesFilename = $true
            break
        }
    }
    
    if ($matchesFilename) {
        $content = Get-Content $doc.FullName -TotalCount 20 -ErrorAction SilentlyContinue
        $contentText = $content -join " "
        
        $hasStatusComplete = $contentText -match "Status.*Complete|Complete.*Status|COMPLETE|✓.*COMPLETE"
        $hasImplementationDone = $contentText -match "Implementation.*complete|All.*complete|Migration.*complete"
        
        [PSCustomObject]@{
            File = $doc
            StrongIndicator = $hasStatusComplete -or $hasImplementationDone
            AgeDays = [math]::Round((New-TimeSpan -Start $doc.LastWriteTime -End (Get-Date)).TotalDays)
        }
    }
}

# Only archive strong matches (both filename and content indicate completion)
$toArchive = $completedDocs | Where-Object { $_.StrongIndicator }

Write-Host "Documents to archive: $($toArchive.Count)"
Write-Host "  (Strong completion indicators in both filename and content)"
Write-Host ""

if ($toArchive.Count -eq 0) {
    Write-Host "No documents to archive."
    exit 0
}

# Show sample
Write-Host "Sample (first 15):"
$toArchive | Select-Object -First 15 | ForEach-Object {
    $relPath = $_.File.FullName.Replace((Get-Location).Path + "\", "")
    Write-Host "  [$($_.AgeDays)d] $relPath"
}
if ($toArchive.Count -gt 15) {
    Write-Host "  ... and $($toArchive.Count - 15) more"
}
Write-Host ""

if ($WhatIf) {
    Write-Host "═══ WHAT-IF MODE ═══"
    Write-Host "Run without -WhatIf to execute archival"
    exit 0
}

# Create archive directory
$archiveDir = "archive\$($timestamp)_completed_implementations"
New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null
Write-Host "Created archive: $archiveDir"
Write-Host ""

# Archive files
$archived = 0
foreach ($item in $toArchive) {
    $file = $item.File
    $relPath = $file.FullName.Replace((Get-Location).Path + "\", "")
    $destPath = Join-Path $archiveDir $relPath
    $destDir = Split-Path $destPath -Parent
    
    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }
    
    Move-Item -LiteralPath $file.FullName -Destination $destPath
    $archived++
    
    if ($archived % 20 -eq 0) {
        Write-Host "  Archived: $archived / $($toArchive.Count)"
    }
}

# Create archive README
$readme = @"
# Completed Implementations Archive

**Date**: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Archived**: $archived documents

These documents describe completed implementations and have been archived
to reduce repository clutter.

## Selection Criteria

Documents were archived if they had BOTH:
1. Completion keywords in filename (COMPLETE, COMPLETED, FINISHED, DONE, etc.)
2. Content confirming completion (Status: Complete, Implementation complete, etc.)

## Archived Documents

"@

$toArchive | Sort-Object { $_.File.FullName } | ForEach-Object {
    $relPath = $_.File.FullName.Replace((Get-Location).Path + "\", "")
    $readme += "`n- [$($_.AgeDays) days old] $relPath"
}

$readme += @"


## Restoration

To restore a specific document:
``````powershell
Copy-Item "archive\$($timestamp)_completed_implementations\path\to\file.md" "path\to\file.md"
``````

To restore all:
``````powershell
Copy-Item -Recurse "archive\$($timestamp)_completed_implementations\*" .
``````

## Notes

These documents represent completed work and were kept for historical reference.
The actual implementations they describe remain active in the codebase.
"@

$readme | Out-File -FilePath (Join-Path $archiveDir "README.md") -Encoding UTF8

Write-Host ""
Write-Host "=" * 70
Write-Host "✓ COMPLETE"
Write-Host "=" * 70
Write-Host "Archived: $archived documents"
Write-Host "Location: $archiveDir"
Write-Host ""
Write-Host "Your repository is now cleaner!"
