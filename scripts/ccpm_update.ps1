# DOC_LINK: DOC-SCRIPT-CCPM-UPDATE-054
param(
  [switch]$Quiet
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Info($msg) { if (-not $Quiet) { Write-Host "[pm:update] $msg" } }
function Write-Ok($msg)   { if (-not $Quiet) { Write-Host "[pm:update] $msg" -ForegroundColor Green } }
function Write-Err($msg)  { Write-Host "[pm:update] $msg" -ForegroundColor Red }

try { $repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..') } catch { $repoRoot = (Get-Location).Path }
$pmRuntime = Join-Path $repoRoot 'pm'
$pmPmDir   = Join-Path $pmRuntime 'scripts/pm'

if (-not (Test-Path -LiteralPath $pmRuntime)) {
  Write-Info 'PM not present; installing instead of updating'
  & (Join-Path $repoRoot 'scripts/ccpm_install.ps1') -Quiet
  exit $LASTEXITCODE
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Write-Info 'git not found; re-installing from ZIP'
  & (Join-Path $repoRoot 'scripts/ccpm_install.ps1') -Quiet
  exit $LASTEXITCODE
}

# Refresh from upstream and re-materialize runtime layout
$sourceRoot = Join-Path $env:TEMP ("ccpm_src_" + [guid]::NewGuid().ToString('N'))
git clone --depth 1 https://github.com/automazeio/ccpm.git $sourceRoot | Out-Null

$nested = Join-Path $sourceRoot 'ccpm'
if (-not (Test-Path -LiteralPath $nested)) {
  Write-Err "Unexpected repository layout. Expected '$nested' to exist."
  exit 1
}

$dirs = 'scripts','commands','rules','agents','context','hooks','prds','epics'
foreach ($d in $dirs) {
  $src = Join-Path $nested $d
  if (Test-Path -LiteralPath $src) {
    Copy-Item -Recurse -Force $src $pmRuntime
  }
}

try { if ($sourceRoot -and (Test-Path $sourceRoot)) { Remove-Item -Recurse -Force $sourceRoot } } catch {}

if (Test-Path -LiteralPath $pmPmDir) {
  Write-Ok "PM updated at $pmPmDir"
  exit 0
} else {
  Write-Err 'PM update failed (pm scripts not found)'
  exit 1
}
