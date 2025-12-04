# DOC_LINK: DOC-SCRIPT-TEST-368
# DOC_LINK: DOC-SCRIPT-TEST-348
# DOC_LINK: DOC-SCRIPT-TEST-344
# DOC_LINK: DOC-SCRIPT-TEST-074
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "[test] Running repository checks..."
$exit = 0

# Run pytest if available and tests exist
$hasTests = (Test-Path -LiteralPath 'tests' -PathType Container) -and ($null -ne (Get-ChildItem -Path 'tests' -Recurse -Include 'test_*.py','*_test.py' -File | Select-Object -First 1))
if ($hasTests) {
  Write-Host "[test] python -m pytest -q tests"
  $env:PYTHONPATH = "$PWD"
  python -m pytest -q tests
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
    Write-Host "[test] openspec: import parser module"
    python -c "import core.openspec_parser; print('ok')" | Out-Null
    if ($LASTEXITCODE -ne 0) { $exit = $LASTEXITCODE }

    Write-Host "[test] openspec: convert to workstream (explicit files_scope)"
    python scripts/generate_workstreams_from_openspec.py --change-id test-001 --files-scope core/openspec_parser.py | Out-Null
    if ($LASTEXITCODE -ne 0) { $exit = $LASTEXITCODE }

    Write-Host "[test] validate workstreams"
    python scripts/validate_workstreams.py | Out-Null
    if ($LASTEXITCODE -ne 0) { $exit = $LASTEXITCODE }
  }
}
catch {
  Write-Warning "[test] OpenSpec flow smoke check failed: $($_.Exception.Message)"
}

# Hardcoded path gate (code+config only). Enable with LEGACY_PATH_GATE=1
if ($env:LEGACY_PATH_GATE -and ($env:LEGACY_PATH_GATE -in @('1','true','True'))) {
  # Resolve registry-backed paths for the CLI and database
  $pathsResolveCli = "scripts/dev/paths_resolve_cli.py"
  $pathsIndexCliKey = "scripts.dev__paths_index_cli_py"
  $pathsIndexCli = python $pathsResolveCli resolve $pathsIndexCliKey | Select-Object -Last 1
  $pathsIndexCli = $pathsIndexCli.Trim()

  $pathDbKey = "root.refactor_paths_db"
  $pathDb = python $pathsResolveCli resolve $pathDbKey | Select-Object -Last 1
  $pathDb = $pathDb.Trim()

  try {
    Write-Host "[test] Path index scan"
    python $pathsIndexCli scan --root . --db $pathDb --reset | Out-Null

    Write-Host "[test] Gate: fail on legacy paths (code+config)"
    $legacyRegex = ('src' + '/pipeline') + '|MOD_' + 'ERROR_PIPELINE|PHASE_DEV_DOCS'
    python $pathsIndexCli gate --db $pathDb --regex $legacyRegex
    if ($LASTEXITCODE -ne 0) { $exit = $LASTEXITCODE }
  }
  catch {
    Write-Warning "[test] Path gate failed: $($_.Exception.Message)"
    if ($exit -eq 0) { $exit = 2 }
  }
} else {
  Write-Host "[test] Legacy path gate disabled (set LEGACY_PATH_GATE=1 to enable)."
}

Write-Host "[test] Completed with exit code $exit"
exit $exit
