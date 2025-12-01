<#
.SYNOPSIS
  Weekly repository maintenance - archive old files automatically.

.DESCRIPTION
  Archives completion documents older than 7 days, planning docs older than 30 days,
  cleans temp directory, and checkpoints database WAL files.
#>

$timestamp = Get-Date -Format "yyyy-MM"

Write-Host "=" * 70
Write-Host "WEEKLY REPOSITORY MAINTENANCE"
Write-Host "=" * 70
Write-Host "Started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

$totalArchived = 0
$totalCleaned = 0

# 1. Archive completed docs older than 7 days
Write-Host "1. Checking completion documents..."
$cutoff7 = (Get-Date).AddDays(-7)

if (Test-Path "docs/completed/current") {
    $oldCompleted = Get-ChildItem "docs/completed/current" -File -ErrorAction SilentlyContinue | 
        Where-Object { $_.LastWriteTime -lt $cutoff7 }

    if ($oldCompleted.Count -gt 0) {
        $archiveDir = "archive/$timestamp/completed"
        New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null
        
        foreach ($file in $oldCompleted) {
            Move-Item $file.FullName -Destination $archiveDir -ErrorAction SilentlyContinue
            Write-Host "   Archived: $($file.Name)"
            $totalArchived++
        }
        Write-Host "   Total: $($oldCompleted.Count) completion docs archived"
    } else {
        Write-Host "   No old completion docs (all < 7 days old)"
    }
} else {
    Write-Host "   docs/completed/current/ does not exist yet"
}

# 2. Archive planning docs older than 30 days
Write-Host ""
Write-Host "2. Checking planning documents..."
$cutoff30 = (Get-Date).AddDays(-30)

if (Test-Path "docs/planning/archive") {
    $oldPlans = Get-ChildItem "docs/planning/archive" -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.LastWriteTime -lt $cutoff30 }

    if ($oldPlans.Count -gt 0) {
        $archiveDir = "archive/$timestamp/planning"
        New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null
        
        foreach ($file in $oldPlans) {
            $dest = Join-Path $archiveDir $file.Name
            Move-Item $file.FullName -Destination $dest -ErrorAction SilentlyContinue
            $totalArchived++
        }
        Write-Host "   Archived: $($oldPlans.Count) planning docs"
    } else {
        Write-Host "   No old planning docs (all < 30 days old)"
    }
} else {
    Write-Host "   docs/planning/archive/ does not exist yet"
}

# 3. Clean temp directory
Write-Host ""
Write-Host "3. Cleaning temporary files..."
if (Test-Path "temp") {
    $tempFiles = Get-ChildItem "temp" -Recurse -File -ErrorAction SilentlyContinue
    if ($tempFiles.Count -gt 0) {
        Remove-Item "temp/*" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "   Removed: $($tempFiles.Count) temp files"
        $totalCleaned += $tempFiles.Count
    } else {
        Write-Host "   Temp directory already clean"
    }
} else {
    Write-Host "   temp/ directory does not exist yet"
}

# 4. Checkpoint database WAL files
Write-Host ""
Write-Host "4. Checkpointing database WAL files..."
$dbFiles = Get-ChildItem -Recurse -Filter "*.db" -ErrorAction SilentlyContinue | 
    Where-Object { -not ($_.FullName -like "*archive*") }

$checkpointed = 0
foreach ($db in $dbFiles) {
    $walFile = "$($db.FullName)-wal"
    if (Test-Path $walFile) {
        $walSize = [math]::Round((Get-Item $walFile).Length / 1MB, 2)
        if ($walSize -gt 1) {
            Write-Host "   Checkpointing $($db.Name) (WAL: ${walSize}MB)..."
            try {
                python -c "import sqlite3; conn = sqlite3.connect('$($db.FullName)'); conn.execute('PRAGMA wal_checkpoint(TRUNCATE)'); conn.close()"
                $checkpointed++
            } catch {
                Write-Host "   Warning: Could not checkpoint $($db.Name)"
            }
        }
    }
}

if ($checkpointed -gt 0) {
    Write-Host "   Checkpointed: $checkpointed database(s)"
} else {
    Write-Host "   No large WAL files to checkpoint"
}

# Summary
Write-Host ""
Write-Host "=" * 70
Write-Host "MAINTENANCE COMPLETE"
Write-Host "=" * 70
Write-Host "Documents archived: $totalArchived"
Write-Host "Temp files cleaned: $totalCleaned"
Write-Host "Databases checkpointed: $checkpointed"
Write-Host "Finished: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

# Create log entry
$logDir = "logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

$logEntry = @"
$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Weekly Maintenance
  Archived: $totalArchived docs
  Cleaned: $totalCleaned temp files
  Checkpointed: $checkpointed databases
"@

Add-Content -Path "$logDir/maintenance.log" -Value $logEntry
