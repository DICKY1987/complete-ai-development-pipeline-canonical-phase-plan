# DOC_LINK: DOC-SCRIPT-CLEANUP-PLANNING-DOCS-839
<#
.SYNOPSIS
  Enhanced cleanup script for planning and execution documents with analysis and archival.

.DESCRIPTION
  1. Scans for .md/.txt files with keywords (PLAN, REPORT, SUMMARY, etc.)
  2. Categorizes files by age and location
  3. Generates analysis report
  4. Optionally archives old files to cleanup archive

.PARAMETER RootPath
  Root directory to scan.

.PARAMETER AnalyzeOnly
  If present, only generates report without archiving.

.PARAMETER ArchiveOlderThanDays
  Archive files older than this many days (default: 30).

.PARAMETER SkipArchive
  Skip archiving folders (like archive/, docs/)
#>

param(
    [string]$RootPath = "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan",
    [switch]$AnalyzeOnly,
    [int]$ArchiveOlderThanDays = 30,
    [string[]]$SkipFolders = @("archive", ".git", "node_modules", "__pycache__")
)

# Validate root path
if (-not (Test-Path -LiteralPath $RootPath)) {
    Write-Error "RootPath does not exist: $RootPath"
    exit 1
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$reportPath = "planning_docs_analysis_$timestamp.txt"
$csvPath = "planning_docs_index_$timestamp.csv"

Write-Host "=" * 70
Write-Host "PLANNING & EXECUTION DOCUMENTS CLEANUP"
Write-Host "=" * 70
Write-Host ""
Write-Host "Root Path: $RootPath"
Write-Host "Age Threshold: $ArchiveOlderThanDays days"
Write-Host "Mode: $(if ($AnalyzeOnly) { 'ANALYZE ONLY' } else { 'ANALYZE + ARCHIVE' })"
Write-Host ""

# File matching criteria
$extensions = @(".md", ".txt")
$nameKeywords = @(
    "PLAN", "REPORT", "QUICKSTART", "SUMMARY", 
    "COMPLETE", "COMPLETED", "CHAT", "PHASE",
    "PROGRESS", "STATUS", "SESSION", "EXECUTION"
)

# Get all files
Write-Host "Scanning files..."
$allFiles = Get-ChildItem -LiteralPath $RootPath -Recurse -File -ErrorAction SilentlyContinue

# Filter by extension and filename
$matchingFiles = $allFiles | Where-Object {
    # Check if in skip folder
    $inSkipFolder = $false
    foreach ($skip in $SkipFolders) {
        if ($_.FullName -like "*\$skip\*") {
            $inSkipFolder = $true
            break
        }
    }
    if ($inSkipFolder) { return $false }
    
    # Check extension
    $hasValidExtension = $extensions -contains $_.Extension
    if (-not $hasValidExtension) { return $false }

    # Check filename for keywords
    $name = $_.BaseName
    $matchesKeyword = $false
    foreach ($kw in $nameKeywords) {
        if ($name -like "*$kw*") {
            $matchesKeyword = $true
            break
        }
    }
    return $matchesKeyword
}

Write-Host "Found: $($matchingFiles.Count) files"
Write-Host ""

# Categorize by age
$cutoffDate = (Get-Date).AddDays(-$ArchiveOlderThanDays)
$oldFiles = $matchingFiles | Where-Object { $_.LastWriteTime -lt $cutoffDate }
$recentFiles = $matchingFiles | Where-Object { $_.LastWriteTime -ge $cutoffDate }

# Categorize by location
$rootFiles = $matchingFiles | Where-Object { 
    $relPath = $_.FullName.Replace($RootPath, "")
    ($relPath -split "\\").Count -eq 2  # Only one level deep (root)
}

# Generate analysis
$analysis = @"
PLANNING & EXECUTION DOCUMENTS ANALYSIS
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Root: $RootPath

========================================
SUMMARY
========================================
Total Files Found: $($matchingFiles.Count)
  - Old (>$ArchiveOlderThanDays days): $($oldFiles.Count)
  - Recent (≤$ArchiveOlderThanDays days): $($recentFiles.Count)
  - In Root: $($rootFiles.Count)

========================================
BREAKDOWN BY KEYWORD
========================================
"@

foreach ($kw in $nameKeywords) {
    $count = ($matchingFiles | Where-Object { $_.BaseName -like "*$kw*" }).Count
    $analysis += "`n  $kw`: $count files"
}

$analysis += @"


========================================
OLD FILES (>$ArchiveOlderThanDays days) - $($oldFiles.Count) files
========================================
"@

if ($oldFiles.Count -gt 0) {
    $oldFiles | Sort-Object LastWriteTime | ForEach-Object {
        $relPath = $_.FullName.Replace($RootPath + "\", "")
        $age = [math]::Round((New-TimeSpan -Start $_.LastWriteTime -End (Get-Date)).TotalDays)
        $analysis += "`n  [$age days] $relPath"
    }
} else {
    $analysis += "`n  (none)"
}

$analysis += @"


========================================
ROOT-LEVEL FILES - $($rootFiles.Count) files
========================================
"@

if ($rootFiles.Count -gt 0) {
    $rootFiles | Sort-Object LastWriteTime -Descending | ForEach-Object {
        $age = [math]::Round((New-TimeSpan -Start $_.LastWriteTime -End (Get-Date)).TotalDays)
        $analysis += "`n  [$age days] $($_.Name)"
    }
} else {
    $analysis += "`n  (none)"
}

$analysis += @"


========================================
RECOMMENDATIONS
========================================
"@

if ($oldFiles.Count -gt 0) {
    $analysis += "`n✓ Archive $($oldFiles.Count) old files (>$ArchiveOlderThanDays days)"
}

if ($rootFiles.Count -gt 10) {
    $analysis += "`n✓ Move $($rootFiles.Count) root-level docs to organized folders"
}

$analysis += @"


========================================
NEXT STEPS
========================================
1. Review this analysis: $reportPath
2. Check CSV details: $csvPath
3. Re-run with archival:
   .\cleanup-planning-docs.ps1

4. Or archive older files:
   .\cleanup-planning-docs.ps1 -ArchiveOlderThanDays 60
"@

# Write analysis report
$analysis | Out-File -FilePath $reportPath -Encoding UTF8
Write-Host "Analysis Report: $reportPath"

# Export CSV
$csvData = $matchingFiles | Select-Object `
    @{ Name = 'FullPath'; Expression = { $_.FullName } },
    @{ Name = 'RelativePath'; Expression = { $_.FullName.Replace($RootPath + "\", "") } },
    @{ Name = 'FileName'; Expression = { $_.Name } },
    @{ Name = 'LastModified'; Expression = { $_.LastWriteTime } },
    @{ Name = 'AgeDays'; Expression = { [math]::Round((New-TimeSpan -Start $_.LastWriteTime -End (Get-Date)).TotalDays) } },
    @{ Name = 'SizeBytes'; Expression = { $_.Length } },
    @{ Name = 'Category'; Expression = { 
        if ($_.LastWriteTime -lt $cutoffDate) { "OLD" } else { "RECENT" }
    }}

$csvData | Sort-Object LastModified | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8
Write-Host "CSV Index: $csvPath"

# Display summary
Write-Host ""
Write-Host "=" * 70
Write-Host "ANALYSIS COMPLETE"
Write-Host "=" * 70
Write-Host "Total Files: $($matchingFiles.Count)"
Write-Host "  Old (>$ArchiveOlderThanDays days): $($oldFiles.Count)"
Write-Host "  Recent: $($recentFiles.Count)"
Write-Host "  Root-level: $($rootFiles.Count)"
Write-Host ""

# Archive if requested
if (-not $AnalyzeOnly -and $oldFiles.Count -gt 0) {
    Write-Host "ARCHIVING OLD FILES..."
    
    $archiveDir = Join-Path $RootPath "archive\$($timestamp)_old_planning_docs"
    New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null
    
    $archived = 0
    foreach ($file in $oldFiles) {
        $relPath = $file.FullName.Replace($RootPath + "\", "")
        $destPath = Join-Path $archiveDir $relPath
        $destDir = Split-Path $destPath -Parent
        
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        
        Move-Item -LiteralPath $file.FullName -Destination $destPath
        $archived++
        
        if ($archived % 10 -eq 0) {
            Write-Host "  Archived: $archived / $($oldFiles.Count)"
        }
    }
    
    # Create archive README
    $archiveReadme = @"
# Old Planning Documents Archive

**Date**: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Threshold**: Files older than $ArchiveOlderThanDays days

## Archived Files: $archived

These files were automatically archived based on age.

## Restoration

To restore a file:
``````powershell
Copy-Item "archive\$($timestamp)_old_planning_docs\path\to\file.md" "path\to\file.md"
``````

## Original Analysis

See: $reportPath
"@
    
    $archiveReadme | Out-File -FilePath (Join-Path $archiveDir "README.md") -Encoding UTF8
    
    Write-Host ""
    Write-Host "✓ Archived $archived files to: $archiveDir"
}

Write-Host ""
Write-Host "Done! Review $reportPath for details."
