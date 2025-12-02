# EXEC-017 Tier 2 Cleanup - Archive Cruft & Auto-Generated Drafts
# Safe to delete: Files already in archive/ + auto-generated versioned backups

$ErrorActionPreference = 'Stop'
$RepoRoot = 'C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan'

Write-Host '=== EXEC-017 Tier 2 Cleanup ===' -ForegroundColor Cyan
Write-Host 'Removing low-value files from archive/ and auto-generated drafts' -ForegroundColor Yellow
Write-Host ''

$DryRun = $false  # EXECUTE MODE

# Load the review-needed report
$reviewNeeded = Get-Content "$RepoRoot\cleanup_reports\cleanup_review_needed_20251202_115455.json" | ConvertFrom-Json

# Tier 1: Files already in archive/ (duplicates, cruft)
$archiveFiles = $reviewNeeded.items | Where-Object { $_.path -like "archive\*" }

# Tier 2: Auto-generated draft files (AUTO-YYYYMMDD-###)
$autoFiles = $reviewNeeded.items | Where-Object { $_.path -match 'AUTO-\d{8}-\d{3}' }

# Combine (remove duplicates)
$allFiles = @($archiveFiles) + @($autoFiles) | Select-Object -Unique -Property path

Write-Host "Files to delete:" -ForegroundColor Yellow
Write-Host "  Archive/* cruft: $($archiveFiles.Count)" -ForegroundColor Gray
Write-Host "  AUTO-* drafts: $($autoFiles.Count)" -ForegroundColor Gray
Write-Host "  Total unique: $($allFiles.Count)" -ForegroundColor White
Write-Host ""

# Stats
$deleteCount = 0
$totalSize = 0
$errors = @()

# Group by archive folder for reporting
$byFolder = $archiveFiles | ForEach-Object {
    if ($_.path -match '^archive\\([^\\]+)') {
        [PSCustomObject]@{ 
            Folder = $matches[1]
            Path = $_.path
        }
    }
} | Group-Object Folder | Sort-Object Count -Descending

Write-Host "Archive folders being cleaned:" -ForegroundColor Cyan
$byFolder | ForEach-Object {
    Write-Host ("  {0}: {1} files" -f $_.Name, $_.Count) -ForegroundColor Gray
}
Write-Host ""

if ($DryRun) {
    Write-Host "[DRY-RUN] Preview of deletions:" -ForegroundColor Yellow
    Write-Host ""
    
    # Show sample files
    Write-Host "Sample files to delete:" -ForegroundColor Cyan
    $allFiles | Select-Object -First 20 | ForEach-Object {
        $fullPath = Join-Path $RepoRoot $_.path
        if (Test-Path $fullPath) {
            $size = (Get-Item $fullPath).Length
            $totalSize += $size
            Write-Host ("  [DRY-RUN] {0} ({1} bytes)" -f $_.path, $size) -ForegroundColor DarkGray
        } else {
            Write-Host ("  [SKIP] File not found: {0}" -f $_.path) -ForegroundColor DarkYellow
        }
    }
    
    if ($allFiles.Count -gt 20) {
        Write-Host ("  ... and {0} more files" -f ($allFiles.Count - 20)) -ForegroundColor DarkGray
    }
    
    Write-Host ""
    Write-Host "[DRY-RUN] Summary:" -ForegroundColor Yellow
    Write-Host ("  Would delete: {0} files" -f $allFiles.Count) -ForegroundColor Gray
    Write-Host ("  Estimated size: {0} KB" -f [math]::Round($totalSize / 1KB, 2)) -ForegroundColor Gray
    Write-Host ""
    Write-Host "To execute: Edit this script and set `$DryRun = `$false" -ForegroundColor Cyan
    exit 0
}

# Confirm before proceeding
Write-Host "CONFIRMATION REQUIRED:" -ForegroundColor Red
Write-Host "This will delete $($allFiles.Count) files from archive/ and AUTO-* drafts." -ForegroundColor Yellow
Write-Host "These are low-value duplicates and auto-generated backups." -ForegroundColor Yellow
Write-Host ""
$confirmation = Read-Host "Type 'DELETE' to proceed, or anything else to cancel"

if ($confirmation -ne 'DELETE') {
    Write-Host "[CANCELLED] Cleanup aborted by user" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Deleting files..." -ForegroundColor Green

foreach ($item in $allFiles) {
    $fullPath = Join-Path $RepoRoot $item.path
    
    if (-not (Test-Path $fullPath)) {
        Write-Host ("[SKIP] File not found: {0}" -f $item.path) -ForegroundColor DarkYellow
        continue
    }
    
    try {
        $fileSize = (Get-Item $fullPath).Length
        $totalSize += $fileSize
        
        Remove-Item -Path $fullPath -Force
        $deleteCount++
        
        if ($deleteCount % 25 -eq 0) {
            Write-Host ("[OK] Deleted $deleteCount files..." -f $deleteCount) -ForegroundColor Green
        }
    } catch {
        $errors += [PSCustomObject]@{
            Path = $item.path
            Error = $_.Exception.Message
        }
        Write-Host ("[ERROR] Failed to delete: {0} - {1}" -f $item.path, $_.Exception.Message) -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== Cleanup Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Successfully deleted: $deleteCount files" -ForegroundColor Green
Write-Host "Total size freed: $([math]::Round($totalSize / 1KB, 2)) KB" -ForegroundColor Green

if ($errors.Count -gt 0) {
    Write-Host ""
    Write-Host "Errors encountered: $($errors.Count)" -ForegroundColor Red
    $errors | ForEach-Object {
        Write-Host ("  {0}: {1}" -f $_.Path, $_.Error) -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Breakdown:" -ForegroundColor Yellow
Write-Host "  Archive/* cruft: $($archiveFiles.Count)" -ForegroundColor Gray
Write-Host "  AUTO-* drafts: $($autoFiles.Count)" -ForegroundColor Gray
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Commit: git add . && git commit -m 'chore: Delete archive cruft (EXEC-017 Tier 2)'" -ForegroundColor Gray
Write-Host "  2. Review: Remaining 42 files in UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/" -ForegroundColor Gray
Write-Host ""
