<#
.SYNOPSIS
  Find all completion/tracking files across the entire repository.

.DESCRIPTION
  Searches for files matching completion/tracking patterns:
  - COMPLETE, COMPLETED, COMPLETION
  - SESSION reports and summaries
  - FINAL reports
  - PROGRESS, STATUS reports
  - IMPLEMENTATION/EXECUTION summaries
  - DAY/WEEK tracking
  - MIGRATION tracking
  - DISCOVERY/ANALYSIS results

.PARAMETER OutputCSV
  Path to output CSV file with results

.PARAMETER WhatIf
  Show what would be found without writing to file
#>

param(
    [string]$OutputCSV = "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\completion_files_inventory.csv",
    [switch]$WhatIf
)

$rootPath = "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"

Write-Host "Scanning: $rootPath"
Write-Host ""

# Exclusion patterns for directories
$excludeDirs = @('node_modules', '.git', '__pycache__', '.pytest_cache', '.venv', 'legacy', 'aider')

# Filename patterns that indicate completion/tracking files
$completionPatterns = @(
    'COMPLETE\.md$',
    'COMPLETED\.md$',
    'COMPLETION.*\.md$',
    'SESSION.*REPORT.*\.md$',
    'SESSION.*SUMMARY.*\.md$',
    'FINAL.*REPORT.*\.md$',
    'FINAL.*SUMMARY.*\.md$',
    'PROGRESS.*\.md$',
    'STATUS.*REPORT.*\.md$',
    'IMPLEMENTATION.*SUMMARY.*\.md$',
    'IMPLEMENTATION.*COMPLETE.*\.md$',
    'EXECUTION.*SUMMARY.*\.md$',
    'DAY\d+.*COMPLETE.*\.md$',
    'WEEK\d+.*COMPLETE.*\.md$',
    'WEEK\d+.*FINAL.*\.md$',
    'MIGRATION.*SUCCESS.*\.md$',
    'MIGRATION.*COMPLETE.*\.md$',
    'CLEANUP.*COMPLETE.*\.md$',
    'OVERLAP.*REPORT.*\.md$',
    'VALIDATION.*REPORT.*\.md$',
    'DISCOVERY.*RESULTS.*\.md$',
    'ANALYSIS.*RESULTS.*\.md$',
    'MERGE.*COMPLETE.*\.md$',
    'REFACTOR.*COMPLETE.*\.md$',
    '.*_COMPLETION_.*\.md$',
    '.*_SESSION_.*\.md$',
    'TEST.*COMPLETE.*\.md$',
    'FIXES.*COMPLETE.*\.md$',
    'CHECKPOINT.*FINAL.*\.md$',
    'EXECUTION_SUMMARY\.txt$',
    'TASK_EXECUTION_SUMMARY\.txt$',
    'WEEK\d+_COMPLETION.*\.txt$'
)

# Get all .md and .txt files
$allFiles = Get-ChildItem -Path $rootPath -Recurse -File -Include "*.md","*.txt" -ErrorAction SilentlyContinue

# Filter out excluded directories
$candidateFiles = $allFiles | Where-Object {
    $path = $_.FullName
    $inExcludedDir = $false
    foreach ($dir in $excludeDirs) {
        if ($path -like "*\$dir\*") {
            $inExcludedDir = $true
            break
        }
    }
    return -not $inExcludedDir
}

# Match against completion patterns
$completionFiles = $candidateFiles | Where-Object {
    $name = $_.Name
    $matches = $false
    foreach ($pattern in $completionPatterns) {
        if ($name -match $pattern) {
            $matches = $true
            break
        }
    }
    return $matches
}

# Group by directory for analysis
$grouped = $completionFiles | Group-Object {Split-Path $_.FullName -Parent} | Sort-Object Count -Descending

Write-Host "=== COMPLETION FILES INVENTORY ==="
Write-Host "Total files scanned:     $($candidateFiles.Count)"
Write-Host "Completion files found:  $($completionFiles.Count)"
Write-Host ""
Write-Host "Top directories:"
$grouped | Select-Object Count, Name -First 15 | Format-Table -AutoSize

# Prepare output
$results = $completionFiles | Select-Object `
    @{N='FullPath'; E={$_.FullName}},
    @{N='FileName'; E={$_.Name}},
    @{N='Directory'; E={Split-Path $_.FullName -Parent}},
    @{N='LastModified'; E={$_.LastWriteTime}},
    @{N='SizeKB'; E={[math]::Round($_.Length/1KB,2)}}

if (-not $WhatIf) {
    $results | Export-Csv -Path $OutputCSV -NoTypeInformation -Encoding UTF8
    Write-Host ""
    Write-Host "Results written to: $OutputCSV"
} else {
    Write-Host ""
    Write-Host "[WhatIf] Would write $($results.Count) files to: $OutputCSV"
}

# Summary by category
Write-Host ""
Write-Host "=== BY CATEGORY ==="
@{
    'Session Reports' = ($completionFiles | Where-Object {$_.Name -match 'SESSION'}).Count
    'Completion Markers' = ($completionFiles | Where-Object {$_.Name -match 'COMPLETE|COMPLETION'}).Count
    'Progress Tracking' = ($completionFiles | Where-Object {$_.Name -match 'PROGRESS|STATUS'}).Count
    'Final Reports' = ($completionFiles | Where-Object {$_.Name -match 'FINAL'}).Count
    'Implementation' = ($completionFiles | Where-Object {$_.Name -match 'IMPLEMENTATION.*SUMMARY|EXECUTION.*SUMMARY'}).Count
    'Migration/Cleanup' = ($completionFiles | Where-Object {$_.Name -match 'MIGRATION|CLEANUP'}).Count
    'Day/Week Tracking' = ($completionFiles | Where-Object {$_.Name -match 'DAY\d+|WEEK\d+'}).Count
    'Analysis/Discovery' = ($completionFiles | Where-Object {$_.Name -match 'ANALYSIS.*RESULTS|DISCOVERY'}).Count
}.GetEnumerator() | Sort-Object Value -Descending | Format-Table -AutoSize
