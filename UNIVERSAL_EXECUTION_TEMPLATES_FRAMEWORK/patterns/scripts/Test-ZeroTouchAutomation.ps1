# Quick Test - Zero-Touch Pattern Automation
# Runs immediate test without waiting for nightly schedule

param(
    [switch]$FullTest,    # Run full workflow
    [switch]$QuickTest    # Just test log parsing
)

$ErrorActionPreference = "Stop"

$PatternsDir = "$PSScriptRoot\.."
$PythonScript = Join-Path $PatternsDir "automation\runtime\zero_touch_workflow.py"

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Zero-Touch Pattern Automation - Quick Test                   ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Check Python
Write-Host "[1/5] Checking Python..." -ForegroundColor Yellow
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "  ❌ Python not found" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Python: $($python.Source)" -ForegroundColor Green

# Check script exists
Write-Host "`n[2/5] Checking Script..." -ForegroundColor Yellow
if (-not (Test-Path $PythonScript)) {
    Write-Host "  ❌ Script not found: $PythonScript" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Script: $PythonScript" -ForegroundColor Green

# Check log directories
Write-Host "`n[3/5] Checking Log Directories..." -ForegroundColor Yellow

$logDirs = @(
    @{Name="Claude"; Path="$env:USERPROFILE\.claude\file-history"},
    @{Name="Copilot"; Path="$env:USERPROFILE\.copilot\session-state"},
    @{Name="Codex"; Path="$env:USERPROFILE\.codex\log"}
)

$totalFiles = 0
foreach ($dir in $logDirs) {
    if (Test-Path $dir.Path) {
        $count = (Get-ChildItem $dir.Path -File -ErrorAction SilentlyContinue | Measure-Object).Count
        Write-Host "  ✓ $($dir.Name): $count files" -ForegroundColor Green
        $totalFiles += $count
    } else {
        Write-Host "  ✗ $($dir.Name): Not found" -ForegroundColor Red
    }
}

if ($totalFiles -eq 0) {
    Write-Host "`n⚠️  WARNING: No log files found!" -ForegroundColor Yellow
    Write-Host "   Use AI tools (Copilot/Codex/Claude) for a few days first." -ForegroundColor Yellow
    Write-Host "   Test will continue but won't generate patterns.`n" -ForegroundColor Yellow
    Start-Sleep -Seconds 3
}

# Quick test: Just parse logs
if ($QuickTest) {
    Write-Host "`n[4/5] Quick Test: Parsing Logs..." -ForegroundColor Yellow
    
    $testScript = @"
import sys
import os
patterns_dir = r'$($PatternsDir.Replace('\', '\\'))'
sys.path.insert(0, patterns_dir)
os.chdir(patterns_dir)

from automation.detectors.multi_ai_log_miner import MultiAILogMiner
import sqlite3

db = sqlite3.connect(':memory:')
miner = MultiAILogMiner(db)

print('\nParsing logs...')
requests = miner.mine_all_logs()

print(f'\n✓ Mined {len(requests)} requests')
print(f'  - Copilot: {len([r for r in requests if r.source == "copilot"])}')
print(f'  - Codex: {len([r for r in requests if r.source == "codex"])}')
print(f'  - Claude: {len([r for r in requests if r.source == "claude"])}')

if requests:
    print('\nSample requests:')
    for i, r in enumerate(requests[:3], 1):
        print(f'  {i}. [{r.source}] {r.user_message[:60]}...')
"@
    
    $testScript | python
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Quick Test PASSED" -ForegroundColor Green
    } else {
        Write-Host "`n❌ Quick Test FAILED" -ForegroundColor Red
        exit 1
    }
    
    exit 0
}

# Full test: Run complete workflow
Write-Host "`n[4/5] Running Full Workflow..." -ForegroundColor Yellow
Write-Host "  (This will mine logs, detect patterns, and generate specs)`n" -ForegroundColor Gray

Push-Location $PatternsDir
try {
    python $PythonScript
    $exitCode = $LASTEXITCODE
} finally {
    Pop-Location
}

Write-Host "`n[5/5] Checking Results..." -ForegroundColor Yellow

if ($exitCode -eq 0) {
    Write-Host "  ✓ Workflow completed successfully" -ForegroundColor Green
    
    # Check generated files
    $reportsDir = Join-Path $PatternsDir "reports\zero_touch"
    $draftsDir = Join-Path $PatternsDir "drafts"
    $specsDir = Join-Path $PatternsDir "specs"
    
    if (Test-Path $reportsDir) {
        $reports = Get-ChildItem $reportsDir -Filter "*.md" -ErrorAction SilentlyContinue
        if ($reports) {
            $latest = $reports | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            Write-Host "`n  📊 Report Generated:" -ForegroundColor Cyan
            Write-Host "     $($latest.Name)" -ForegroundColor White
            Write-Host "     Size: $([math]::Round($latest.Length/1KB, 1)) KB" -ForegroundColor Gray
            
            # Open report
            Write-Host "`n  Opening report..." -ForegroundColor Gray
            code $latest.FullName
        }
    }
    
    if (Test-Path "$draftsDir\AUTO-*.pattern.yaml") {
        $drafts = Get-ChildItem "$draftsDir\AUTO-*.pattern.yaml" -ErrorAction SilentlyContinue
        Write-Host "`n  📝 Pattern Drafts: $($drafts.Count)" -ForegroundColor Cyan
        $drafts | Select-Object -First 3 | ForEach-Object {
            Write-Host "     - $($_.Name)" -ForegroundColor White
        }
    }
    
    if (Test-Path "$specsDir\AUTO-*.pattern.yaml") {
        $specs = Get-ChildItem "$specsDir\AUTO-*.pattern.yaml" -ErrorAction SilentlyContinue
        Write-Host "`n  ✅ Auto-Approved Patterns: $($specs.Count)" -ForegroundColor Green
        $specs | Select-Object -First 3 | ForEach-Object {
            Write-Host "     - $($_.Name)" -ForegroundColor White
        }
    }
    
    Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║  ✅ TEST SUCCESSFUL - System Working!                          ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green
    
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "  1. Review report (opened in editor)" -ForegroundColor White
    Write-Host "  2. Install nightly task:" -ForegroundColor White
    Write-Host "     .\scripts\Schedule-ZeroTouchAutomation.ps1 -Action install" -ForegroundColor Gray
    Write-Host "  3. Check status tomorrow:" -ForegroundColor White
    Write-Host "     .\scripts\Schedule-ZeroTouchAutomation.ps1 -Action status" -ForegroundColor Gray
    
} else {
    Write-Host "  ❌ Workflow failed (exit code: $exitCode)" -ForegroundColor Red
    Write-Host "`n  Check error messages above for details." -ForegroundColor Yellow
    exit $exitCode
}
