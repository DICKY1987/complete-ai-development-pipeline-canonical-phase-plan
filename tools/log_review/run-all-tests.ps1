# Master Test Runner
# Runs all tests for LOG_REVIEW_SUB_SYS

param(
    [switch]$PythonOnly,
    [switch]$PowerShellOnly,
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"

Write-Host "`n╔═══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         LOG_REVIEW_SUB_SYS - Master Test Runner                  ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$startTime = Get-Date
$totalTests = 0
$totalPassed = 0
$totalFailed = 0

# Run Python tests
if (-not $PowerShellOnly) {
    Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host "PYTHON UNIT TESTS" -ForegroundColor Yellow
    Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host ""
    
    # Check if pytest is installed
    $pytestInstalled = python -c "import pytest; print('installed')" 2>$null
    
    if ($pytestInstalled -ne "installed") {
        Write-Host "Installing pytest..." -ForegroundColor Yellow
        python -m pip install pytest --quiet
    }
    
    # Run pytest
    Set-Location tests
    
    if ($Verbose) {
        python -m pytest -v --tb=short
    } else {
        python -m pytest --tb=line
    }
    
    $pythonExitCode = $LASTEXITCODE
    
    Set-Location ..
    
    if ($pythonExitCode -eq 0) {
        Write-Host "`n✓ Python tests passed" -ForegroundColor Green
    } else {
        Write-Host "`n✗ Python tests failed (exit code: $pythonExitCode)" -ForegroundColor Red
    }
    
    Write-Host ""
}

# Run PowerShell tests
if (-not $PythonOnly) {
    Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host "POWERSHELL INTEGRATION TESTS" -ForegroundColor Yellow
    Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host ""
    
    Set-Location tests
    
    if ($Verbose) {
        .\test_powershell_integration.ps1 -Verbose
    } else {
        .\test_powershell_integration.ps1
    }
    
    $psExitCode = $LASTEXITCODE
    
    Set-Location ..
    
    if ($psExitCode -eq 0) {
        Write-Host "`n✓ PowerShell tests passed" -ForegroundColor Green
    } else {
        Write-Host "`n✗ PowerShell tests failed (exit code: $psExitCode)" -ForegroundColor Red
    }
    
    Write-Host ""
}

# Run aggregation test
if (-not $PythonOnly -and -not $PowerShellOnly) {
    Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host "AGGREGATION WORKFLOW TEST" -ForegroundColor Yellow
    Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host ""
    
    Set-Location tests
    .\test_aggregate_script.ps1
    $aggExitCode = $LASTEXITCODE
    Set-Location ..
    
    if ($aggExitCode -eq 0) {
        Write-Host "`n✓ Aggregation workflow test passed" -ForegroundColor Green
    } else {
        Write-Host "`n✗ Aggregation workflow test failed" -ForegroundColor Red
    }
    
    Write-Host ""
}

# Summary
$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Gray
Write-Host "TEST SUMMARY" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Gray
Write-Host ""

if (-not $PowerShellOnly) {
    Write-Host "Python Tests:       " -NoNewline
    if ($pythonExitCode -eq 0) {
        Write-Host "PASSED ✓" -ForegroundColor Green
    } else {
        Write-Host "FAILED ✗" -ForegroundColor Red
    }
}

if (-not $PythonOnly) {
    Write-Host "PowerShell Tests:   " -NoNewline
    if ($psExitCode -eq 0) {
        Write-Host "PASSED ✓" -ForegroundColor Green
    } else {
        Write-Host "FAILED ✗" -ForegroundColor Red
    }
}

if (-not $PythonOnly -and -not $PowerShellOnly) {
    Write-Host "Aggregation Test:   " -NoNewline
    if ($aggExitCode -eq 0) {
        Write-Host "PASSED ✓" -ForegroundColor Green
    } else {
        Write-Host "FAILED ✗" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Duration: $($duration.TotalSeconds) seconds" -ForegroundColor Gray
Write-Host ""

# Determine overall result
$overallSuccess = $true
if (-not $PowerShellOnly -and $pythonExitCode -ne 0) { $overallSuccess = $false }
if (-not $PythonOnly -and $psExitCode -ne 0) { $overallSuccess = $false }
if (-not $PythonOnly -and -not $PowerShellOnly -and $aggExitCode -ne 0) { $overallSuccess = $false }

if ($overallSuccess) {
    Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host "✓ ALL TESTS PASSED" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Green
    exit 0
} else {
    Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Red
    Write-Host "✗ SOME TESTS FAILED" -ForegroundColor Red
    Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Red
    exit 1
}
