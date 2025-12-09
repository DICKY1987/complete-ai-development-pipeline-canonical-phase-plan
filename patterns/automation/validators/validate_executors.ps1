#!/usr/bin/env pwsh
# DOC_ID: DOC-PAT-VALIDATORS-VALIDATE-EXECUTORS-001
<#
.SYNOPSIS
    Validate PowerShell executor syntax

.DESCRIPTION
    Implements GAP-PATREG-007: Executor syntax validation
    Uses PSScriptAnalyzer to check all executor scripts

.PARAMETER Severity
    Minimum severity level (Error, Warning, Information)

.EXAMPLE
    .\validate_executors.ps1 -Severity Error

.NOTES
    Pattern: EXEC-002 (Batch Validation)
    Version: 1.0.0
#>

[CmdletBinding()]
param(
    [ValidateSet("Error", "Warning", "Information")]
    [string]$Severity = "Error"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Import PSScriptAnalyzer
if (-not (Get-Module -ListAvailable -Name PSScriptAnalyzer)) {
    Write-Host "Installing PSScriptAnalyzer..." -ForegroundColor Yellow
    Install-Module -Name PSScriptAnalyzer -Force -SkipPublisherCheck -Scope CurrentUser
}

$scriptPath = $PSScriptRoot
$patternsDir = Split-Path (Split-Path $scriptPath -Parent) -Parent
$executorsDir = Join-Path $patternsDir "executors"

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  PowerShell Executor Syntax Validation" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $executorsDir)) {
    Write-Host "✓ No executors directory found - skipping" -ForegroundColor Yellow
    exit 0
}

$executors = Get-ChildItem $executorsDir -Filter "*_executor.ps1" -ErrorAction SilentlyContinue
if ($executors.Count -eq 0) {
    Write-Host "✓ No executor files found" -ForegroundColor Yellow
    exit 0
}

Write-Host "Analyzing $($executors.Count) executor files..." -ForegroundColor White
Write-Host ""

$allErrors = @()
$analyzed = 0

foreach ($executor in $executors) {
    $analyzed++
    Write-Host "[$analyzed/$($executors.Count)] Analyzing $($executor.Name)..." -ForegroundColor Gray

    $results = Invoke-ScriptAnalyzer -Path $executor.FullName -Severity $Severity

    if ($results) {
        $allErrors += @{
            File = $executor.Name
            Errors = $results
        }

        foreach ($result in $results) {
            Write-Host "  ✗ Line $($result.Line): $($result.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "  ✓ Clean" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($allErrors.Count -gt 0) {
    Write-Host "✗ Found errors in $($allErrors.Count) files" -ForegroundColor Red
    exit 1
} else {
    Write-Host "✓ All $($executors.Count) executors passed validation" -ForegroundColor Green
    exit 0
}
