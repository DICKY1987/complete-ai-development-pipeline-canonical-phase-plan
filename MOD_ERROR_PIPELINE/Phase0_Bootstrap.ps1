<# 
.SYNOPSIS
  Phase-0 Bootstrap for "PowerShell_ deterministi_factory".
  Idempotently initializes local repo, binds remote, seeds skeleton, preflight, initial push, and desktop shortcut.

.USAGE
  pwsh -NoProfile -File .\Phase0_Bootstrap.ps1 `
    -LocalRoot 'C:\PowerShell_ deterministi_factory' `
    -RemoteUrl 'https://github.com/DICKY1987/PowerShell_-deterministi_factory.git' `
    -DefaultBranch 'main' `
    -CreateDesktopShortcut:$true -Verbose

.NOTES
  Safe to re-run. Uses JSONL event logging under .runs\<RUN_ID>\events.jsonl.
#>

[CmdletBinding(SupportsShouldProcess=$true, ConfirmImpact='Medium')]
param(
  [Parameter(Mandatory=$true)]
  [ValidateNotNullOrEmpty()]
  [string]$LocalRoot,

  [Parameter(Mandatory=$true)]
  [ValidatePattern('^https?://')]
  [string]$RemoteUrl,

  [ValidateNotNullOrEmpty()]
  [string]$DefaultBranch = 'main',

  [switch]$CreateDesktopShortcut
)

# --- Strictness & globals ---
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$PSStyle.OutputRendering = 'Host'

function New-RunId {
  # ULID-like sortable ID: yyyyMMddTHHmmssZ-xxxx
  $ts = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
  $suffix = [Guid]::NewGuid().ToString('N').Substring(0,8)
  return "$ts-$suffix"
}

# Paths
$LocalRoot = [System.IO.Path]::GetFullPath($LocalRoot)
$RunId     = New-RunId
$RunsDir   = Join-Path $LocalRoot ".runs"
$RunDir    = Join-Path $RunsDir $RunId
$LogsDir   = Join-Path $RunDir  "logs"
$EventsLog = Join-Path $RunDir  "events.jsonl"

# --- Event logging (JSONL) ---
function Write-Event {
  param(
    [Parameter(Mandatory)][ValidateSet('start','ok','warn','error')][string]$Status,
    [Parameter(Mandatory)][string]$Step,
    [Parameter(Mandatory)][string]$Message,
    [hashtable]$Data
  )
  try {
    if (-not (Test-Path $RunDir)) { New-Item -ItemType Directory -Force -Path $RunDir | Out-Null }
    if (-not (Test-Path $LogsDir)) { New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null }
    $evt = [ordered]@{
      ts      = (Get-Date).ToUniversalTime().ToString('o')
      run_id  = $RunId
      step    = $Step
      status  = $Status
      message = $Message
      data    = $Data
    }
    ($evt | ConvertTo-Json -Depth 6 -Compress) | Add-Content -Path $EventsLog -Encoding UTF8
    if ($Status -eq 'error') { Write-Error "[${Step}] $Message" -ErrorAction Continue }
    elseif ($Status -eq 'warn') { Write-Warning "[${Step}] $Message" }
    else { Write-Verbose "[${Step}] $Message" }
  } catch {
    Write-Warning "Failed to write event log: $($_.Exception.Message)"
  }
}

# --- Helpers ---
function Invoke-Exe {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory)][string]$FilePath,
    [string[]]$ArgumentList,
    [string]$WorkingDirectory
  )
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = $FilePath
  if ($ArgumentList) {
    $psi.Arguments = ($ArgumentList | ForEach-Object {
      if ($_ -match '\s') { '"{0}"' -f $_.Replace('"', '\"') }
      else { $_ }
    }) -join ' '
  }
  if ($WorkingDirectory) { $psi.WorkingDirectory = $WorkingDirectory }
  $psi.RedirectStandardOutput = $true
  $psi.RedirectStandardError  = $true
  $psi.UseShellExecute = $false
  $p = New-Object System.Diagnostics.Process
  $p.StartInfo = $psi
  [void]$p.Start()
  $stdout = $p.StandardOutput.ReadToEnd()
  $stderr = $p.StandardError.ReadToEnd()
  $p.WaitForExit()
  return [pscustomobject]@{ ExitCode=$p.ExitCode; StdOut=$stdout.Trim(); StdErr=$stderr.Trim() }
}

function New-Directory {
  [CmdletBinding(SupportsShouldProcess=$true)]
  param([Parameter(Mandatory)][string]$Path)
  if (-not (Test-Path $Path)) {
    if ($PSCmdlet.ShouldProcess($Path,'Create directory')) {
      New-Item -ItemType Directory -Force -Path $Path | Out-Null
    }
  }
}

function Write-Placeholder {
  [CmdletBinding(SupportsShouldProcess=$true)]
  param([Parameter(Mandatory)][string]$FilePath,[string]$Content = "")
  if (-not (Test-Path $FilePath)) {
    if ($PSCmdlet.ShouldProcess($FilePath,'Create placeholder')) {
      $dir = Split-Path -Parent $FilePath
      if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
      Set-Content -Path $FilePath -Value $Content -Encoding UTF8
    }
  }
}

# --- Step 1: Preflight directories & event log ---
Write-Event -Status start -Step 'bootstrap' -Message "Starting Phase-0 bootstrap into $LocalRoot" -Data @{ remote=$RemoteUrl; branch=$DefaultBranch; run_dir=$RunDir }
New-Directory -Path $LocalRoot
New-Directory -Path $RunsDir
New-Directory -Path $RunDir
New-Directory -Path $LogsDir
Write-Event -Status ok -Step 'bootstrap' -Message "Filesystem prepared" -Data @{ localRoot=$LocalRoot }

# --- Step 2: Preflight tools ---
function Get-ToolVersion {
  param([string]$Exe,[string[]]$ToolArgs=@('--version'))
  try {
    $res = Invoke-Exe -FilePath $Exe -ArgumentList $ToolArgs
    if ($res.ExitCode -eq 0) { return $res.StdOut }
    return $null
  } catch { return $null }
}
$toolReport = [ordered]@{
  powershell = $PSVersionTable.PSVersion.ToString()
  git        = Get-ToolVersion -Exe 'git'
  gh         = Get-ToolVersion -Exe 'gh' -ToolArgs @('version')
  pester     = (Get-Module -ListAvailable Pester | Select-Object -First 1).Version.ToString()
  psscriptanalyzer = (Get-Module -ListAvailable PSScriptAnalyzer | Select-Object -First 1).Version.ToString()
}
$preflightPath = Join-Path $LogsDir 'preflight.json'
$toolReport | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 -Path $preflightPath
Write-Event -Status ok -Step 'preflight' -Message "Tool versions captured" -Data $toolReport

if (-not $toolReport.git) {
  Write-Event -Status error -Step 'preflight' -Message "Git not found in PATH. Install Git and re-run." -Data @{}
  throw "Missing dependency: Git"
}

# --- Step 3: Initialize Git repo (idempotent) ---
$gitDir = Join-Path $LocalRoot '.git'
$repoInitialized = Test-Path $gitDir
if (-not $repoInitialized) {
  if ($PSCmdlet.ShouldProcess($LocalRoot,"git init -b $DefaultBranch")) {
    $res = Invoke-Exe -FilePath 'git' -ArgumentList @('init','-b',$DefaultBranch) -WorkingDirectory $LocalRoot
    if ($res.ExitCode -ne 0) {
      # fallback for older git lacking -b
      $res2 = Invoke-Exe -FilePath 'git' -ArgumentList @('init') -WorkingDirectory $LocalRoot
      if ($res2.ExitCode -ne 0) { Write-Event -Status error -Step 'git' -Message "git init failed: $($res2.StdErr)" -Data @{}; throw "git init failed" }
      Invoke-Exe -FilePath 'git' -ArgumentList @('symbolic-ref','HEAD',"refs/heads/$DefaultBranch") -WorkingDirectory $LocalRoot | Out-Null
    }
    Write-Event -Status ok -Step 'git' -Message "Repository initialized" -Data @{ branch=$DefaultBranch }
  }
} else {
  Write-Event -Status ok -Step 'git' -Message "Repository already initialized" -Data @{ branch=$DefaultBranch }
}

# Ensure default branch exists (in case repo existed with different HEAD)
try {
  $rev = Invoke-Exe -FilePath 'git' -ArgumentList @('rev-parse','--abbrev-ref','HEAD') -WorkingDirectory $LocalRoot
  if ($rev.ExitCode -eq 0 -and $rev.StdOut -ne $DefaultBranch) {
    if ($PSCmdlet.ShouldProcess($LocalRoot,"Switch to $DefaultBranch (or create)")) {
      $chk = Invoke-Exe -FilePath 'git' -ArgumentList @('show-ref',"refs/heads/$DefaultBranch") -WorkingDirectory $LocalRoot
      if ($chk.ExitCode -eq 0) {
        Invoke-Exe -FilePath 'git' -ArgumentList @('checkout',$DefaultBranch) -WorkingDirectory $LocalRoot | Out-Null
      } else {
        Invoke-Exe -FilePath 'git' -ArgumentList @('checkout','-b',$DefaultBranch) -WorkingDirectory $LocalRoot | Out-Null
      }
    }
  }
} catch { }

# --- Step 4: Set or update remote 'origin' ---
$remoteUrlCurrent = $null
try {
  $q = Invoke-Exe -FilePath 'git' -ArgumentList @('remote','get-url','origin') -WorkingDirectory $LocalRoot
  if ($q.ExitCode -eq 0) { $remoteUrlCurrent = $q.StdOut }
} catch { }

if ($remoteUrlCurrent) {
  if ($remoteUrlCurrent -ne $RemoteUrl) {
    if ($PSCmdlet.ShouldProcess($LocalRoot,"git remote set-url origin $RemoteUrl")) {
      $s = Invoke-Exe -FilePath 'git' -ArgumentList @('remote','set-url','origin',$RemoteUrl) -WorkingDirectory $LocalRoot
      if ($s.ExitCode -ne 0) { Write-Event -Status error -Step 'git' -Message "Failed to set remote: $($s.StdErr)" -Data @{}; throw "git remote set-url failed" }
    }
    Write-Event -Status ok -Step 'git' -Message "Remote 'origin' updated" -Data @{ origin=$RemoteUrl }
  } else {
    Write-Event -Status ok -Step 'git' -Message "Remote 'origin' already set" -Data @{ origin=$RemoteUrlCurrent }
  }
} else {
  if ($PSCmdlet.ShouldProcess($LocalRoot,"git remote add origin $RemoteUrl")) {
    $a = Invoke-Exe -FilePath 'git' -ArgumentList @('remote','add','origin',$RemoteUrl) -WorkingDirectory $LocalRoot
    if ($a.ExitCode -ne 0) { Write-Event -Status error -Step 'git' -Message "Failed to add remote: $($a.StdErr)" -Data @{}; throw "git remote add failed" }
  }
  Write-Event -Status ok -Step 'git' -Message "Remote 'origin' added" -Data @{ origin=$RemoteUrl }
}

# --- Step 5: Deterministic skeleton (folders + placeholders) ---
$Skeleton = @(
  'docs',
  'config',
  'scripts',
  'modules',
  '.runs',
  'worktrees',
  '.gate\incoming',
  '.gate\approved',
  '.gate\rejected',
  '.stage\10-bootstrap\out',
  '.stage\20-config\out',
  '.stage\30-plan\out',
  '.stage\40-worktrees\out',
  '.stage\80-validate\out',
  '.stage\90-gate\out',
  '.stage\99-archive\out'
)
foreach ($rel in $Skeleton) {
  New-Directory -Path (Join-Path $LocalRoot $rel)
  Write-Placeholder -FilePath (Join-Path $LocalRoot (Join-Path $rel '.gitkeep')) -Content ''
}

# Basic repo files (placeholders, created only if missing)
Write-Placeholder -FilePath (Join-Path $LocalRoot '.gitignore') -Content @'
# OS / tooling
.DS_Store
Thumbs.db
*.log
*.tmp
# Runs & artifacts
.runs/
worktrees/
# VSCode
.vscode/
'@
Write-Placeholder -FilePath (Join-Path $LocalRoot 'README.md') -Content "# PowerShell_ deterministi_factory`n`nPhase-0 baseline initialized on $(Get-Date -Format s)."
Write-Placeholder -FilePath (Join-Path $LocalRoot 'config\file_router.config.json') -Content @'
{
  "$schema": "inline",
  "version": "v1.0.0",
  "projects": {
    "PowerShell_deterministi_factory": {
      "aliases": {
        "docs": "docs/",
        "scripts": "scripts/",
        "modules": "modules/"
      }
    }
  },
  "conflictPolicy": "dedupe-or-quarantine",
  "fileStableMs": 1500
}
'@

Write-Event -Status ok -Step 'skeleton' -Message "Skeleton laid down" -Data @{ count=$Skeleton.Count }

# --- Step 6: Baseline commit (if repo has no commits or there are new files) ---
$needCommit = $false
try {
  $status = Invoke-Exe -FilePath 'git' -ArgumentList @('status','--porcelain') -WorkingDirectory $LocalRoot
  if ($status.ExitCode -eq 0 -and $status.StdOut) { $needCommit = $true }
} catch { $needCommit = $true }

if ($needCommit) {
  if ($PSCmdlet.ShouldProcess($LocalRoot,'git add & commit baseline')) {
    Invoke-Exe -FilePath 'git' -ArgumentList @('add','-A') -WorkingDirectory $LocalRoot | Out-Null
    $c = Invoke-Exe -FilePath 'git' -ArgumentList @('commit','-m',"chore(bootstrap): baseline skeleton [skip ci]") -WorkingDirectory $LocalRoot
    if ($c.ExitCode -ne 0) { Write-Event -Status error -Step 'git' -Message "Commit failed: $($c.StdErr)" -Data @{}; throw "git commit failed" }
    Write-Event -Status ok -Step 'git' -Message "Baseline commit created" -Data @{}
  }
} else {
  Write-Event -Status ok -Step 'git' -Message "No changes to commit" -Data @{}
}

# --- Step 7: Push to remote (creates main on remote if empty) ---
try {
  if ($PSCmdlet.ShouldProcess($RemoteUrl,'git push -u origin <branch>')) {
    $p = Invoke-Exe -FilePath 'git' -ArgumentList @('push','-u','origin',$DefaultBranch) -WorkingDirectory $LocalRoot
    if ($p.ExitCode -ne 0) {
      Write-Event -Status warn -Step 'git' -Message "Push failed (likely auth or remote protection). Manual auth may be required." -Data @{ exit=$p.ExitCode; err=$p.StdErr }
    } else {
      Write-Event -Status ok -Step 'git' -Message "Pushed to remote" -Data @{ origin=$RemoteUrl; branch=$DefaultBranch }
    }
  }
} catch {
  Write-Event -Status warn -Step 'git' -Message "Push threw exception: $($_.Exception.Message)" -Data @{}
}

# --- Step 8: Desktop shortcut (optional) ---
if ($CreateDesktopShortcut.IsPresent) {
  try {
    $desktop = [Environment]::GetFolderPath('Desktop')
    $lnk = Join-Path $desktop 'Deterministi-Factory.lnk'
    if ($PSCmdlet.ShouldProcess($lnk,'Create desktop shortcut')) {
      $wsh = New-Object -ComObject WScript.Shell
      $sc = $wsh.CreateShortcut($lnk)
      # Prefer Windows Terminal if present
      $wtPath = (Get-Command wt.exe -ErrorAction SilentlyContinue)?.Source
      if ($wtPath) {
        $sc.TargetPath = $wtPath
        $sc.Arguments  = "-d `"$LocalRoot`""
      } else {
        $pwshExe = (Get-Command pwsh -ErrorAction SilentlyContinue)?.Source
        if (-not $pwshExe) { $pwshExe = (Get-Command powershell -ErrorAction SilentlyContinue)?.Source }
        $sc.TargetPath = $pwshExe
        $sc.Arguments  = "-NoExit -NoLogo -Command Set-Location -LiteralPath `"$LocalRoot`""
      }
      $sc.WorkingDirectory = $LocalRoot
      $sc.IconLocation     = "$env:SystemRoot\System32\shell32.dll,167"
      $sc.Description      = "Open Deterministi Factory workspace at $LocalRoot"
      $sc.Save()
      Write-Event -Status ok -Step 'shortcut' -Message "Desktop shortcut created" -Data @{ path=$lnk }
    }
  } catch {
    Write-Event -Status warn -Step 'shortcut' -Message "Failed to create desktop shortcut: $($_.Exception.Message)" -Data @{}
  }
}

Write-Event -Status ok -Step 'bootstrap' -Message "Phase-0 bootstrap complete" -Data @{ local=$LocalRoot; origin=$RemoteUrl; branch=$DefaultBranch }
Write-Host ""
Write-Host "✅ Phase-0 complete. Run ID: $RunId" -ForegroundColor Green
Write-Host "Repo: $LocalRoot  ↔  $RemoteUrl"
Write-Host "Events log: $EventsLog"
if ($CreateDesktopShortcut) { Write-Host "Shortcut created on Desktop: Deterministi-Factory.lnk" }
