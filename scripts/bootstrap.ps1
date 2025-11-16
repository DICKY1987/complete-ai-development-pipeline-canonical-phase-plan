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
