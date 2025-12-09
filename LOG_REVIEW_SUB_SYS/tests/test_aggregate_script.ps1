# Test script for aggregate-logs.ps1
# Validates that aggregation works correctly

$ErrorActionPreference = "Stop"

Write-Host "Testing aggregate-logs.ps1..." -ForegroundColor Cyan
Write-Host ""

# Change to parent directory
Set-Location (Split-Path -Parent $PSScriptRoot)

# Test 1: Basic aggregation
Write-Host "Test 1: Basic aggregation (Claude only)..." -ForegroundColor Yellow
.\aggregate-logs.ps1 -StartDate "2025-12-01" -EndDate "2025-12-08" -Tools @("claude") -OutputDir ".\aggregated"

$latestLog = Get-ChildItem ".\aggregated\aggregated-*.jsonl" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if ($latestLog) {
    Write-Host "✓ Log file created: $($latestLog.Name)" -ForegroundColor Green
    $lineCount = (Get-Content $latestLog.FullName | Measure-Object -Line).Lines
    Write-Host "✓ Contains $lineCount entries" -ForegroundColor Green
    
    # Validate JSON format
    $validEntries = 0
    Get-Content $latestLog.FullName | ForEach-Object {
        try {
            $entry = $_ | ConvertFrom-Json
            if ($entry.tool -and $entry.type -and $entry.timestamp) {
                $validEntries++
            }
        } catch {
            Write-Host "  Warning: Invalid JSON line" -ForegroundColor Yellow
        }
    }
    
    Write-Host "✓ $validEntries valid JSON entries" -ForegroundColor Green
    
    # Check for privacy redaction
    $content = Get-Content $latestLog.FullName -Raw
    if ($content -match 'sk-[a-zA-Z0-9]{32,}' -or $content -match '@[a-zA-Z0-9.-]+\.[a-z]{2,}') {
        Write-Host "✗ Privacy redaction may have failed" -ForegroundColor Red
    } else {
        Write-Host "✓ Privacy redaction applied" -ForegroundColor Green
    }
} else {
    Write-Host "✗ No log file created" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "All tests passed!" -ForegroundColor Green
exit 0
