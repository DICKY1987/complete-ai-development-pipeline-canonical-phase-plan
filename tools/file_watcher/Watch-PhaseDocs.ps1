# DOC_LINK: DOC-SCRIPT-WATCH-PHASEDOCS-740
<#
.SYNOPSIS
  Watch a directory tree for .md/.txt files whose names contain certain
  keywords, and move them into a DEVELOPMENT_TEMP_FILES folder.

.DESCRIPTION
  - Runs an initial scan to move all matching files.
  - Rescans every 6 hours to catch any new matching files.
  - Between scans, watches for file events (Created/Changed/Renamed).
  - Overwrites existing files in TargetPath with the latest version.

  Press Ctrl+C to stop the watcher.
#>

param(
    [string]$RootPath   = "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan",
    [string]$TargetPath = "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\DEVELOPMENT_TEMP_FILES",
    [string[]]$Extensions = @(".md", ".txt"),
    [string[]]$NameKeywords = @(
        "PLAN",
        "REPORT",
        "QUICKSTART",
        "SUMMARY",
        "COMPLETE",
        "COMPLETED",
        "CHAT",
        "PHASE"
    ),
    [switch]$SkipInitialScan,
    [int]$ScanIntervalHours = 6
)

function Test-MatchingFile {
    param(
        [Parameter(Mandatory)]
        [System.IO.FileInfo]$File
    )

    # extension check
    if ($Extensions -notcontains $File.Extension) {
        return $false
    }

    # filename keyword check (BaseName = filename without extension)
    $name = $File.BaseName
    foreach ($kw in $NameKeywords) {
        if ($name -like "*$kw*") {  # case-insensitive
            return $true
        }
    }

    return $false
}

function Move-MatchingFile {
    param(
        [Parameter(Mandatory)]
        [string]$FullPath
    )

    if (-not (Test-Path -LiteralPath $FullPath)) {
        return
    }

    try {
        $file = Get-Item -LiteralPath $FullPath -ErrorAction Stop

        if (-not (Test-MatchingFile -File $file)) {
            return
        }

        # Find the LAST keyword match in the filename
        $matchedKeyword = $null
        $lastPosition = -1
        $name = $file.BaseName

        foreach ($kw in $NameKeywords) {
            $pos = $name.LastIndexOf($kw, [System.StringComparison]::OrdinalIgnoreCase)
            if ($pos -gt $lastPosition) {
                $lastPosition = $pos
                $matchedKeyword = $kw
            }
        }

        if (-not $matchedKeyword) {
            return
        }

        # Create keyword-specific subdirectory
        $keywordFolder = Join-Path -Path $TargetPath -ChildPath $matchedKeyword
        if (-not (Test-Path -LiteralPath $keywordFolder)) {
            New-Item -ItemType Directory -Path $keywordFolder -Force | Out-Null
        }

        $destPath = Join-Path -Path $keywordFolder -ChildPath $file.Name

        Move-Item -LiteralPath $file.FullName -Destination $destPath -Force
        Write-Host "Moved: $($file.FullName) -> $destPath"
    }
    catch {
        Write-Warning "Failed to move '$FullPath': $($_.Exception.Message)"
    }
}

# --- Setup & validation ---

if (-not (Test-Path -LiteralPath $RootPath)) {
    Write-Error "RootPath does not exist: $RootPath"
    exit 1
}

if (-not (Test-Path -LiteralPath $TargetPath)) {
    Write-Host "Creating target folder: $TargetPath"
    New-Item -ItemType Directory -Path $TargetPath -Force | Out-Null
}

# Create keyword folders
Write-Host "Creating keyword folders..."
foreach ($kw in $NameKeywords) {
    $kwFolder = Join-Path -Path $TargetPath -ChildPath $kw
    if (-not (Test-Path -LiteralPath $kwFolder)) {
        New-Item -ItemType Directory -Path $kwFolder -Force | Out-Null
        Write-Host "  Created: $kwFolder"
    }
}

Write-Host "RootPath:   $RootPath"
Write-Host "TargetPath: $TargetPath"
Write-Host "Extensions: $($Extensions -join ', ')"
Write-Host "Keywords:   $($NameKeywords -join ', ')"
Write-Host ""

# --- Scan function ---

function Invoke-FileScan {
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Running file scan..."
    $count = 0
    Get-ChildItem -LiteralPath $RootPath -Recurse -File -ErrorAction SilentlyContinue |
        ForEach-Object {
            $beforeCount = $count
            Move-MatchingFile -FullPath $_.FullName
            if ((Test-Path -LiteralPath (Join-Path -Path $TargetPath -ChildPath $_.Name))) {
                $count++
            }
        }
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Scan complete. Files processed: $count"
    Write-Host ""
}

# --- Initial scan (optional) ---

if (-not $SkipInitialScan) {
    Invoke-FileScan
}

$script:lastScanTime = Get-Date

# --- Set up FileSystemWatcher ---

$fsw = New-Object System.IO.FileSystemWatcher
$fsw.Path = $RootPath
$fsw.IncludeSubdirectories = $true
$fsw.Filter = "*.*"
$fsw.EnableRaisingEvents = $true

# Action for Created / Changed
$action = {
    param($source, $eventArgs)

    # Small delay so the file is fully written
    Start-Sleep -Milliseconds 250

    Move-MatchingFile -FullPath $eventArgs.FullPath
}

# Action for Renamed (only new name matters)
$renameAction = {
    param($source, $eventArgs)

    Start-Sleep -Milliseconds 250

    Move-MatchingFile -FullPath $eventArgs.FullPath
}

Register-ObjectEvent -InputObject $fsw -EventName Created -SourceIdentifier "PhaseDocsCreated" -Action $action | Out-Null
Register-ObjectEvent -InputObject $fsw -EventName Changed -SourceIdentifier "PhaseDocsChanged" -Action $action | Out-Null
Register-ObjectEvent -InputObject $fsw -EventName Renamed -SourceIdentifier "PhaseDocsRenamed" -Action $renameAction | Out-Null

Write-Host "Watching for matching .md/.txt files under:"
Write-Host "  $RootPath"
Write-Host "Matching files are moved into:"
Write-Host "  $TargetPath"
Write-Host "Rescanning every $ScanIntervalHours hours"
Write-Host ""
Write-Host "Press Ctrl+C to stop the watcher."

# Keep script alive, process events, and run periodic scans
while ($true) {
    Wait-Event -Timeout 5 | Out-Null

    # Check if it's time for another scan
    $timeSinceLastScan = (Get-Date) - $script:lastScanTime
    if ($timeSinceLastScan.TotalHours -ge $ScanIntervalHours) {
        Invoke-FileScan
        $script:lastScanTime = Get-Date
    }
}
