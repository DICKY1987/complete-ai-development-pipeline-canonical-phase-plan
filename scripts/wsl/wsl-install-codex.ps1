# DOC_LINK: DOC-SCRIPT-WSL-INSTALL-CODEX-104
#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$src = Join-Path $repoRoot 'Migrate Codex & adier WSL2 on Windows\WSL-Install-Step5-Codex.ps1'

if (-not (Test-Path $src)) {
  Write-Error "Source script not found: $src"
  exit 1
}

& $src @args

