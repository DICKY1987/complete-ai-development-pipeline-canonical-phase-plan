# Test Run - AI Logs Analyzer
# Quick test to verify everything is working

Write-Host @"
╔═══════════════════════════════════════════════════════╗
║     AI Logs Analyzer - Test Run                      ║
╚═══════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

Write-Host ""
Write-Host "Step 1: Checking AI tool directories..." -ForegroundColor Yellow

$tools = @{
    "Claude Code" = "$HOME\.claude\history.jsonl"
    "Codex" = "$HOME\.codex\history.jsonl"
    "Copilot" = "$HOME\.copilot\logs"
    "Aider" = "$HOME\Documents\aider-config\history\.aider.chat.history.md"
    "Gemini" = "$HOME\.gemini"
}

$foundTools = @()
foreach ($tool in $tools.GetEnumerator()) {
    if (Test-Path $tool.Value) {
        Write-Host "  ✓ $($tool.Key) - FOUND" -ForegroundColor Green
        $foundTools += $tool.Key
    } else {
        Write-Host "  ✗ $($tool.Key) - NOT FOUND" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Step 2: Checking directory structure..." -ForegroundColor Yellow

$dirs = @("aggregated", "analysis", "exports", "scripts", "config")
foreach ($dir in $dirs) {
    if (Test-Path "$HOME\ALL_AI\ai-logs-analyzer\$dir") {
        Write-Host "  ✓ $dir/" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $dir/ - MISSING" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Step 3: Testing log aggregation..." -ForegroundColor Yellow
Write-Host "  Running: ./scripts/aggregate-logs.ps1" -ForegroundColor Gray

try {
    & "$HOME\ALL_AI\ai-logs-analyzer\scripts\aggregate-logs.ps1" -ErrorAction Stop
    Write-Host "  ✓ Aggregation successful!" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Aggregation failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 4: Testing analysis..." -ForegroundColor Yellow
Write-Host "  Running: ./scripts/analyze-logs.ps1 -Type summary" -ForegroundColor Gray

try {
    & "$HOME\ALL_AI\ai-logs-analyzer\scripts\analyze-logs.ps1" -Type summary -ErrorAction Stop
    Write-Host "  ✓ Analysis successful!" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Analysis failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host @"
╔═══════════════════════════════════════════════════════╗
║     Test Complete!                                    ║
╚═══════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

Write-Host ""
Write-Host "Found and processed logs from:" -ForegroundColor Yellow
foreach ($tool in $foundTools) {
    Write-Host "  • $tool" -ForegroundColor Green
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Review aggregated logs in: .\aggregated\" -ForegroundColor Gray
Write-Host "  2. Check analysis results in: .\analysis\" -ForegroundColor Gray
Write-Host "  3. Read QUICKSTART.md for daily usage" -ForegroundColor Gray
Write-Host "  4. Set up scheduled task: .\scripts\setup-scheduled-task.ps1" -ForegroundColor Gray
Write-Host ""
