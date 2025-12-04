# DOC_LINK: DOC-SCRIPT-RUN-SIMPLE-EXECUTOR-068
<#
.SYNOPSIS
    Launch simple sequential workstream executor

.DESCRIPTION
    Interactive executor that processes workstreams one at a time
    with manual control over execution method

.EXAMPLE
    .\run_simple_executor.ps1
#>

$ErrorActionPreference = "Stop"

function Write-Banner {
    param([string]$Text)
    $width = 70
    $padding = [Math]::Max(0, ($width - $Text.Length - 2) / 2)
    $paddingStr = "=" * [Math]::Floor($padding)

    Write-Host ""
    Write-Host ("=" * $width) -ForegroundColor Cyan
    Write-Host ($paddingStr + " $Text " + $paddingStr) -ForegroundColor Cyan
    Write-Host ("=" * $width) -ForegroundColor Cyan
    Write-Host ""
}

# Header
Write-Banner "Simple Workstream Executor"

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+." -ForegroundColor Red
    exit 1
}

# Check workstreams directory
if (-not (Test-Path "workstreams")) {
    Write-Host "❌ Workstreams directory not found" -ForegroundColor Red
    Write-Host "   Expected: workstreams/*.json" -ForegroundColor Yellow
    exit 1
}

$wsCount = (Get-ChildItem "workstreams\ws-*.json" -ErrorAction SilentlyContinue).Count
if ($wsCount -eq 0) {
    Write-Host "❌ No workstream files found in workstreams/" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Found $wsCount workstream files" -ForegroundColor Green

# Create directories
$directories = @("logs", "reports")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "✅ Created $dir/" -ForegroundColor Green
    }
}

# Launch executor
Write-Host ""
Write-Host "🚀 Launching executor..." -ForegroundColor Cyan
Write-Host ""

python scripts\simple_workstream_executor.py

$exitCode = $LASTEXITCODE

# Summary
Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "✅ Executor completed" -ForegroundColor Green

    if (Test-Path "reports\simple_executor_results.json") {
        Write-Host ""
        Write-Host "📊 Results saved to: reports\simple_executor_results.json" -ForegroundColor Cyan
    }
} else {
    Write-Host "❌ Executor exited with errors (code: $exitCode)" -ForegroundColor Red
}

Write-Host ""
exit $exitCode
