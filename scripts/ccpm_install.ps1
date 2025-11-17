param(
  [switch]$UseSubmodule,
  [switch]$Quiet
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Info($msg) { if (-not $Quiet) { Write-Host "[ccpm:install] $msg" } }
function Write-Ok($msg)   { if (-not $Quiet) { Write-Host "[ccpm:install] $msg" -ForegroundColor Green } }
function Write-Warn($msg) { if (-not $Quiet) { Write-Host "[ccpm:install] $msg" -ForegroundColor Yellow } }
function Write-Err($msg)  { Write-Host "[ccpm:install] $msg" -ForegroundColor Red }

try { $repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..') } catch { $repoRoot = (Get-Location).Path }
$ccpmRuntime = Join-Path $repoRoot 'ccpm'
$ccpmPmDir   = Join-Path $ccpmRuntime 'scripts/pm'

if (Test-Path -LiteralPath $ccpmPmDir) {
  Write-Ok "CCPM already present at $ccpmPmDir"
  exit 0
}

# Prefer submodule when requested and repo has .git
if ($UseSubmodule -and (Test-Path (Join-Path $repoRoot '.git'))) {
  if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Write-Err 'git not available; cannot add submodule'; exit 1 }
  Write-Info 'Adding CCPM as a git submodule'
  pushd $repoRoot | Out-Null
  try {
    if (-not (Test-Path -LiteralPath (Join-Path $repoRoot 'ccpm'))) {
      git submodule add https://github.com/automazeio/ccpm.git ccpm | Out-Null
    }
    git submodule update --init --recursive ccpm | Out-Null
  } finally { popd | Out-Null }
} else {
  # Lightweight vendor: clone to temp, then materialize runtime layout
  if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Warn 'git not found; attempting ZIP download'
    $zipUrl = 'https://codeload.github.com/automazeio/pm/zip/refs/heads/main'
    $zipPath = Join-Path $env:TEMP "ccpm.zip"
    Invoke-WebRequest -UseBasicParsing -Uri $zipUrl -OutFile $zipPath
    $tmpDir = Join-Path $env:TEMP ("ccpm_" + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $tmpDir | Out-Null
    Expand-Archive -Path $zipPath -DestinationPath $tmpDir -Force
    Remove-Item $zipPath -Force
    $extracted = Get-ChildItem $tmpDir | Where-Object { $_.PSIsContainer } | Select-Object -First 1
    $sourceRoot = $extracted.FullName
  } else {
    $sourceRoot = Join-Path $env:TEMP ("ccpm_src_" + [guid]::NewGuid().ToString('N'))
    git clone --depth 1 https://github.com/automazeio/ccpm.git $sourceRoot | Out-Null
  }

  # Ensure runtime dir exists
  if (-not (Test-Path -LiteralPath $ccpmRuntime)) {
    New-Item -ItemType Directory -Path $ccpmRuntime | Out-Null
  }

  # CCPM repo nests actual payload under /ccpm
  $nested = Join-Path $sourceRoot 'ccpm'
  if (-not (Test-Path -LiteralPath $nested)) {
    Write-Err "Unexpected repository layout. Expected '$nested' to exist."
    exit 1
  }

  # Copy selected directories into runtime path
  $dirs = 'scripts','commands','rules','agents','context','hooks','prds','epics'
  foreach ($d in $dirs) {
    $src = Join-Path $nested $d
    if (Test-Path -LiteralPath $src) {
      Copy-Item -Recurse -Force $src $ccpmRuntime
    }
  }

  # Clean up source temp if we cloned/expanded
  try { if ($sourceRoot -and (Test-Path $sourceRoot)) { Remove-Item -Recurse -Force $sourceRoot } } catch {}
}

if (Test-Path -LiteralPath $ccpmPmDir) {
  Write-Ok "Installed CCPM runtime at $ccpmPmDir"
  exit 0
} else {
  Write-Err 'CCPM install failed (pm scripts not found)'
  exit 1
}


