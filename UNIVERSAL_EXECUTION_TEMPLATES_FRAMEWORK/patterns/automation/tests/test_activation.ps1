# Pattern Automation Activation Test
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path "$PSScriptRoot/../..").Path
Set-Location $repoRoot

Write-Host "`nTesting Pattern Automation Activation" -ForegroundColor Cyan

$dbPath = Join-Path $repoRoot "metrics/pattern_automation.db"
$configPath = Join-Path $repoRoot "automation/config/detection_config.yaml"

# Test 1: Database tables exist
Write-Host "`n[1/5] Checking database tables..."
if (-not (Test-Path $dbPath)) {
    throw "Database not found: $dbPath"
}

$tableCheck = @"
import sqlite3, sys
from pathlib import Path

db_path = Path(r"$dbPath")
conn = sqlite3.connect(db_path)
expected = {"execution_logs", "pattern_candidates", "anti_patterns"}
present = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
missing = expected - present
if missing:
    sys.exit("Missing tables: " + ", ".join(sorted(missing)))
print("OK")
"@
$tableCheck | python -
if ($LASTEXITCODE -ne 0) {
    throw "Missing expected tables"
}
Write-Host "  Tables present" -ForegroundColor Green

# Test 2: Configuration loads
Write-Host "`n[2/5] Checking configuration..."
if (-not (Test-Path $configPath)) {
    throw "Config not found: $configPath"
}
python -c "import yaml; yaml.safe_load(open(r'$configPath')); print('OK')"
if ($LASTEXITCODE -ne 0) {
    throw "Failed to load configuration"
}
Write-Host "  Configuration loads" -ForegroundColor Green

# Test 3: Integration module imports
Write-Host "`n[3/5] Checking Python imports..."
python -c "from automation.integration.orchestrator_hooks import get_hooks; print('OK')"
if ($LASTEXITCODE -ne 0) {
    throw "Failed to import orchestrator_hooks"
}
Write-Host "  Import successful" -ForegroundColor Green

# Test 4: Simulate execution logging
Write-Host "`n[4/5] Testing execution logging..."
$logScript = @"
from automation.integration.orchestrator_hooks import PatternAutomationHooks

hooks = PatternAutomationHooks(r"$dbPath")
task = {"operation_kind": "activation-test", "inputs": {"file": "demo.txt"}}
result = {"success": True, "outputs": {"file": "demo.txt"}}
context = hooks.on_task_start(task)
hooks.on_task_complete(task, result, context)
print("OK")
"@
$logScript | python -
if ($LASTEXITCODE -ne 0) {
    throw "Failed to log execution"
}
Write-Host "  Execution logging works" -ForegroundColor Green

# Test 5: Verify log entry
Write-Host "`n[5/5] Verifying database entry..."
$countScript = @"
import sqlite3
from pathlib import Path

db_path = Path(r"$dbPath")
conn = sqlite3.connect(db_path)
count = conn.execute("SELECT COUNT(*) FROM execution_logs;").fetchone()[0]
print(count)
"@
$count = $countScript | python -
if ($LASTEXITCODE -ne 0) {
    throw "Failed to read execution_logs count"
}
$countValue = [int]$count[0]
if ($countValue -lt 1) {
    throw "No execution logs found"
}
Write-Host "  Found $countValue execution log(s)" -ForegroundColor Green

Write-Host "`nAll tests passed. Pattern automation is active." -ForegroundColor Green
