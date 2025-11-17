Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "[bootstrap] Initializing repository skeleton..."

"docs","plans","scripts","tests","assets" | ForEach-Object {
  if (-not (Test-Path -LiteralPath $_)) {
    New-Item -ItemType Directory -Path $_ -Force | Out-Null
    Write-Host "[bootstrap] Created ./$_"
  }
}

Write-Host "[bootstrap] Environment checks (optional)"
if (Get-Command python -ErrorAction SilentlyContinue) {
  Write-Host "  - Python found: $(python --version 2>$null)"
} else {
  Write-Host "  - Python not found (skip)"
}

if (Get-Command node -ErrorAction SilentlyContinue) {
  Write-Host "  - Node.js found: $(node --version)"
} else {
  Write-Host "  - Node.js not found (skip)"
}

Write-Host "[bootstrap] Done. See AGENTS.md for workflow details."

# CCPM presence check and optional auto-install
try {
  $repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
} catch { $repoRoot = (Get-Location).Path }

$ccpmPmDir = Join-Path $repoRoot 'ccpm/scripts/pm'
if (-not (Test-Path -LiteralPath $ccpmPmDir)) {
  Write-Host "[bootstrap] CCPM not found (missing 'ccpm/scripts/pm'). Attempting install..."
  $installer = Join-Path $repoRoot 'scripts/ccpm_install.ps1'
  if (Test-Path -LiteralPath $installer) {
    & $installer -Quiet | Write-Host
  } else {
    Write-Host "[bootstrap] Installer missing at scripts/ccpm_install.ps1"
  }
  if (Test-Path -LiteralPath $ccpmPmDir) {
    Write-Host "[bootstrap] CCPM installed ✔"
  } else {
    Write-Host "[bootstrap] CCPM install did not complete. See docs/phase-09-ccpm-optimization.md"
  }
} else {
  Write-Host "[bootstrap] CCPM found: $ccpmPmDir"
}
