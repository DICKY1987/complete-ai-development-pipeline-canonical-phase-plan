# Pattern Detection Demo (optional)
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path "$PSScriptRoot/../..").Path
Set-Location $repoRoot
$dbPath = Join-Path $repoRoot "metrics/pattern_automation.db"

Write-Host "Running pattern detection demo" -ForegroundColor Cyan

$logScript = @"
from automation.integration.orchestrator_hooks import PatternAutomationHooks
from pathlib import Path

db_path = Path(r"$dbPath")
hooks = PatternAutomationHooks(str(db_path))

for i in range(1, 4):
    task = {
        "operation_kind": "file_creation",
        "name": f"create_test_file_{i}",
        "inputs": {"filename": f"test_{i}.txt", "content": f"Test content {i}"},
    }
    result = {"success": True, "outputs": {"file_created": f"test_{i}.txt"}}
    ctx = hooks.on_task_start(task)
    hooks.on_task_complete(task, result, ctx)
    print(f"Logged execution {i}")
"@
$logScript | python -
if ($LASTEXITCODE -ne 0) {
    Write-Host "Logging phase encountered errors (see output above)." -ForegroundColor Yellow
}

$candidateScript = @"
import sqlite3, sys
from pathlib import Path

db_path = Path(r"$dbPath")
try:
    conn = sqlite3.connect(db_path)
except Exception as exc:
    sys.exit(f"DB open failed: {exc}")

count = conn.execute("SELECT COUNT(*) FROM pattern_candidates;").fetchone()[0]
print(count)
drafts = list(Path("patterns/drafts").glob("AUTO-*.yaml"))
for draft in drafts:
    print(draft.name)
"@
$candidateOutput = $candidateScript | python -
if ($LASTEXITCODE -ne 0 -or -not $candidateOutput) {
    Write-Host "`nUnable to read pattern candidates (see previous output)." -ForegroundColor Yellow
    return
}

$candidateCount = [int]$candidateOutput[0]

Write-Host "`nPattern candidates found: $candidateCount" -ForegroundColor Yellow
if ($candidateOutput.Length -gt 1) {
    Write-Host "Draft patterns:" -ForegroundColor Cyan
    $candidateOutput[1..($candidateOutput.Length - 1)] | ForEach-Object { Write-Host "  $_" }
} else {
    Write-Host "No draft patterns detected yet." -ForegroundColor Yellow
}
