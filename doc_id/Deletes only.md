Here’s a concrete **SAFE_CLEAN_V1** pattern plus a ready-to-drop-in **PowerShell script**.

It does exactly what you asked:

* Deletes only:

  * `__pycache__` directories
  * `.pytest_cache` directories
  * `*.log` files (inside any `logs` directory)
* Ensures they’re ignored by Git via a managed block in `.gitignore`
* Emits a small, structured report with counts + bytes reclaimed

---

## 1. Pattern: `SAFE_CLEAN_V1`

You can treat this as the pattern doc the script implements.

```yaml
pattern_id: SAFE_CLEAN_V1
intent: >
  Safely clean non-source, regenerable artifacts from the repo
  (Python caches, pytest cache, log files) and prevent them from
  re-inflating the repo by adding them to .gitignore.

scope:
  root: "Git repo root (directory containing .git)"

inputs:
  - name: repo_root
    type: path
    required: false
    default: "auto-detect by walking up from current directory until .git is found"
  - name: dry_run
    type: boolean
    required: false
    default: true
    description: "If true, only report what *would* be deleted."
  - name: include_logs
    type: boolean
    required: false
    default: true
    description: "If true, delete *.log files under any 'logs' directory."

targets:
  - name: python_bytecode_caches
    description: "All __pycache__ directories and their contents."
    selector: 'directories named "__pycache__" (recursive)'
    safe_reason: "Python regenerates .pyc/.pyo on demand; no runtime dependency."
  - name: pytest_cache
    description: "All .pytest_cache directories and their contents."
    selector: 'directories named ".pytest_cache" (recursive)'
    safe_reason: "Pytest recreates its cache; not used in runtime."
  - name: log_files
    description: "All *.log files under directories named 'logs'."
    selector: 'files matching *.log under any directory named "logs" (recursive)'
    safe_reason: "Logs are historical only; no execution path depends on past logs."

steps:
  - step: detect_repo_root
    description: "Walk up from current directory until .git is found; that directory is repo_root."
  - step: scan_targets
    description: "Locate all matching directories/files for each target."
  - step: compute_stats
    description: "For each target: count files and sum bytes to be freed."
  - step: update_gitignore
    description: >
      Ensure .gitignore contains a managed SAFE_CLEAN_V1 block with patterns:
      '__pycache__/', '.pytest_cache/', '*.log'.
      If block exists, replace it; otherwise append it.
  - step: delete_artifacts
    guard: "dry_run == false"
    description: "Delete the targeted directories/files."
  - step: emit_report
    description: >
      Print a summary table:
      - files_deleted_per_target
      - bytes_freed_per_target
      - total_files_deleted
      - total_bytes_freed

outputs:
  - name: summary_report
    type: console_text
  - name: gitignore_block
    type: file_append_or_update
    path: ".gitignore"
    managed_block_id: "SAFE_CLEAN_V1"

idempotence:
  description: >
    Multiple runs are safe. After the first run, there may be
    zero targets found; .gitignore block is updated in-place.

failure_modes:
  - case: "repo_root not found (no .git)"
    behavior: "Fail with clear error message and non-zero exit code."
  - case: "permission denied on some path"
    behavior: "Warn and continue; report failures in summary."
```

---

## 2. PowerShell Implementation: `safe_clean_v1.ps1`

Place this at the repo root (or anywhere on your PATH) and run it from inside the repo.

```powershell
param(
    [switch]$DryRun,
    [switch]$IncludeLogs = $true
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-RepoRoot {
    param(
        [string]$StartDir = (Get-Location).Path
    )

    $dir = Get-Item -LiteralPath $StartDir
    while ($null -ne $dir) {
        if (Test-Path (Join-Path $dir.FullName ".git")) {
            return $dir.FullName
        }
        $dir = $dir.Parent
    }

    throw "SAFE_CLEAN_V1: Could not find a .git directory above '$StartDir'. Run this inside a Git repo."
}

function Get-FilesUnderDirectories {
    param(
        [System.IO.DirectoryInfo[]]$Directories
    )
    $allFiles = @()
    foreach ($d in $Directories) {
        if (-not $d.Exists) { continue }
        $allFiles += Get-ChildItem -LiteralPath $d.FullName -Recurse -File -ErrorAction SilentlyContinue
    }
    return $allFiles
}

function Get-SizeInfo {
    param(
        [System.IO.FileInfo[]]$Files
    )
    if (-not $Files -or $Files.Count -eq 0) {
        return [pscustomobject]@{
            FileCount = 0
            Bytes     = 0L
        }
    }

    $m = $Files | Measure-Object -Property Length -Sum
    return [pscustomobject]@{
        FileCount = $Files.Count
        Bytes     = [int64]$m.Sum
    }
}

function Format-Bytes {
    param(
        [int64]$Bytes
    )
    if ($Bytes -ge 1GB) {
        return ("{0:N2} GB" -f ($Bytes / 1GB))
    } elseif ($Bytes -ge 1MB) {
        return ("{0:N2} MB" -f ($Bytes / 1MB))
    } elseif ($Bytes -ge 1KB) {
        return ("{0:N2} KB" -f ($Bytes / 1KB))
    } else {
        return ("{0} B" -f $Bytes)
    }
}

function Update-GitIgnoreForSafeClean {
    param(
        [string]$RepoRoot
    )

    $gitIgnorePath = Join-Path $RepoRoot ".gitignore"
    $blockStart    = "# >>> SAFE_CLEAN_V1"
    $blockEnd      = "# <<< SAFE_CLEAN_V1"

    $blockContent = @"
$blockStart
__pycache__/
.pytest_cache/
*.log
$blockEnd
"@.Trim()

    if (Test-Path $gitIgnorePath) {
        $text = Get-Content -LiteralPath $gitIgnorePath -Raw
        if ($text -match [regex]::Escape($blockStart) -and $text -match [regex]::Escape($blockEnd)) {
            # Replace existing block
            $pattern = "(?ms)" + [regex]::Escape($blockStart) + ".*?" + [regex]::Escape($blockEnd)
            $newText = [regex]::Replace($text, $pattern, [System.Text.RegularExpressions.MatchEvaluator]{ param($m) $blockContent })
            Set-Content -LiteralPath $gitIgnorePath -Value $newText
        }
        else {
            Add-Content -LiteralPath $gitIgnorePath -Value "`n`n$blockContent`n"
        }
    }
    else {
        Set-Content -LiteralPath $gitIgnorePath -Value "$blockContent`n"
    }
}

# --------------------------
# MAIN
# --------------------------

$repoRoot = Get-RepoRoot
Write-Host "SAFE_CLEAN_V1: Repo root detected at: $repoRoot" -ForegroundColor Cyan

# 1) Discover targets
$pycacheDirs = Get-ChildItem -Path $repoRoot -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue
$pytestDirs  = Get-ChildItem -Path $repoRoot -Recurse -Directory -Filter ".pytest_cache" -ErrorAction SilentlyContinue

$logFiles = @()
if ($IncludeLogs) {
    $logDirs  = Get-ChildItem -Path $repoRoot -Recurse -Directory -Filter "logs" -ErrorAction SilentlyContinue
    foreach ($ld in $logDirs) {
        $logFiles += Get-ChildItem -LiteralPath $ld.FullName -Recurse -File -Filter "*.log" -ErrorAction SilentlyContinue
    }
}

$pycacheFiles = Get-FilesUnderDirectories -Directories $pycacheDirs
$pytestFiles  = Get-FilesUnderDirectories -Directories $pytestDirs

# 2) Compute stats
$pycacheStats = Get-SizeInfo -Files $pycacheFiles
$pytestStats  = Get-SizeInfo -Files $pytestFiles
$logStats     = Get-SizeInfo -Files $logFiles

$totalFiles = $pycacheStats.FileCount + $pytestStats.FileCount + $logStats.FileCount
$totalBytes = $pycacheStats.Bytes     + $pytestStats.Bytes     + $logStats.Bytes

Write-Host ""
Write-Host "SAFE_CLEAN_V1: Scan summary (what WILL be deleted if not DryRun):" -ForegroundColor Yellow
$summary = @(
    [pscustomobject]@{
        Target      = "__pycache__"
        Files       = $pycacheStats.FileCount
        Size        = Format-Bytes $pycacheStats.Bytes
    }
    [pscustomobject]@{
        Target      = ".pytest_cache"
        Files       = $pytestStats.FileCount
        Size        = Format-Bytes $pytestStats.Bytes
    }
    [pscustomobject]@{
        Target      = "logs/*.log"
        Files       = $logStats.FileCount
        Size        = Format-Bytes $logStats.Bytes
    }
)

$summary | Format-Table -AutoSize

Write-Host ""
Write-Host ("Total files: {0}" -f $totalFiles)
Write-Host ("Total size:  {0}" -f (Format-Bytes $totalBytes))
Write-Host ""

# 3) Update .gitignore
Write-Host "SAFE_CLEAN_V1: Updating .gitignore with managed ignore rules..." -ForegroundColor Cyan
Update-GitIgnoreForSafeClean -RepoRoot $repoRoot
Write-Host "SAFE_CLEAN_V1: .gitignore updated." -ForegroundColor Green
Write-Host ""

if ($DryRun) {
    Write-Host "SAFE_CLEAN_V1: DRY RUN ONLY – no files were deleted." -ForegroundColor Yellow
    Write-Host "Re-run without -DryRun to apply cleanup." -ForegroundColor Yellow
    return
}

# 4) Delete artifacts
$errors = @()

Write-Host "SAFE_CLEAN_V1: Deleting artifacts..." -ForegroundColor Cyan

foreach ($d in $pycacheDirs) {
    try {
        Remove-Item -LiteralPath $d.FullName -Recurse -Force -ErrorAction Stop
    }
    catch {
        $errors += "Failed to delete __pycache__ dir: $($d.FullName) - $($_.Exception.Message)"
    }
}

foreach ($d in $pytestDirs) {
    try {
        Remove-Item -LiteralPath $d.FullName -Recurse -Force -ErrorAction Stop
    }
    catch {
        $errors += "Failed to delete .pytest_cache dir: $($d.FullName) - $($_.Exception.Message)"
    }
}

if ($IncludeLogs -and $logFiles.Count -gt 0) {
    foreach ($f in $logFiles) {
        try {
            Remove-Item -LiteralPath $f.FullName -Force -ErrorAction Stop
        }
        catch {
            $errors += "Failed to delete log file: $($f.FullName) - $($_.Exception.Message)"
        }
    }
}

Write-Host ""
Write-Host "SAFE_CLEAN_V1: Cleanup complete." -ForegroundColor Green

if ($errors.Count -gt 0) {
    Write-Host ""
    Write-Host "Some items could not be deleted:" -ForegroundColor Red
    $errors | ForEach-Object { Write-Host "  - $_" }
}

Write-Host ""
Write-Host "SAFE_CLEAN_V1: Final report" -ForegroundColor Yellow
$summary | Format-Table -AutoSize
Write-Host ("Total files deleted (attempted): {0}" -f $totalFiles)
Write-Host ("Approx. space reclaimed:       {0}" -f (Format-Bytes $totalBytes))
```

---

## 3. How to use it

From *anywhere* inside the repo:

### 1) First run as a safety check

```powershell
# From inside the repo
.\safe_clean_v1.ps1 -DryRun
```

You’ll see:

* Count + size for `__pycache__`, `.pytest_cache`, and `logs/*.log`
* `.gitignore` updated (this part always happens)

### 2) Then actually clean

```powershell
.\safe_clean_v1.ps1
```

Optional: to temporarily keep logs but still clean caches:

```powershell
.\safe_clean_v1.ps1 -IncludeLogs:$false
```

---

