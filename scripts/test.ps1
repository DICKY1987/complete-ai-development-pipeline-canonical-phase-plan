Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "[test] Running repository checks..."
$exit = 0

# Run pytest if available and tests exist
$hasTests = (Test-Path -LiteralPath 'tests' -PathType Container) -and ($null -ne (Get-ChildItem -Path 'tests' -Recurse -Include 'test_*.py','*_test.py' -File | Select-Object -First 1))
if ($hasTests -and (Get-Command pytest -ErrorAction SilentlyContinue)) {
  Write-Host "[test] pytest -q"
  pytest -q
  if ($LASTEXITCODE -ne 0) { $exit = $LASTEXITCODE }
} else {
  Write-Host "[test] No Python tests detected or pytest unavailable — skipping."
}

# Optional: markdownlint if installed
$mdFiles = Get-ChildItem -Recurse -Include *.md -File
if ($mdFiles) {
  $mdl = Get-Command markdownlint -ErrorAction SilentlyContinue
  if ($mdl) {
    Write-Host "[test] markdownlint <md files>"
    & $mdl.Source @($mdFiles.FullName)
    if ($LASTEXITCODE -ne 0) { $exit = $LASTEXITCODE }
  } else {
    Write-Host "[test] markdownlint not found — skipping Markdown lint."
  }
}

Write-Host "[test] Completed with exit code $exit"
exit $exit
