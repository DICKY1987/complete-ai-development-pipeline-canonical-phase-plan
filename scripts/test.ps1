Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "[test] Running repository checks..."
$exit = 0

# Run pytest if available and tests exist
$hasTests = (Test-Path -LiteralPath 'tests' -PathType Container) -and ($null -ne (Get-ChildItem -Path 'tests' -Recurse -Include 'test_*.py','*_test.py' -File | Select-Object -First 1))
if ($hasTests) {
  Write-Host "[test] python -m pytest -q"
  python -m pytest -q
  if ($LASTEXITCODE -ne 0) { $exit = $LASTEXITCODE }
} else {
  Write-Host "[test] No Python tests detected - skipping."
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

# OpenSpec flow smoke checks (non-fatal)
try {
  if (Test-Path -LiteralPath 'openspec/changes/test-001' -PathType Container) {
    Write-Host "[test] openspec: generate bundle from change-id"
    python -m src.pipeline.openspec_parser --change-id test-001 --generate-bundle | Out-Null
    if ($LASTEXITCODE -ne 0) { $exit = $LASTEXITCODE }

    Write-Host "[test] openspec: convert to workstream (explicit files_scope)"
    python scripts/generate_workstreams_from_openspec.py --change-id test-001 --files-scope src/pipeline/openspec_parser.py | Out-Null
    if ($LASTEXITCODE -ne 0) { $exit = $LASTEXITCODE }

    Write-Host "[test] validate workstreams"
    python scripts/validate_workstreams.py | Out-Null
    if ($LASTEXITCODE -ne 0) { $exit = $LASTEXITCODE }
  }
}
catch {
  Write-Warning "[test] OpenSpec flow smoke check failed: $($_.Exception.Message)"
}

Write-Host "[test] Completed with exit code $exit"
exit $exit
