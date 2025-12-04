#!/usr/bin/env pwsh
# DOC_LINK: DOC-SCRIPT-VALIDATE-COMPLIANCE-089
<#
.SYNOPSIS
    Validate All Orchestration Specification Requirements

.DESCRIPTION
    Master validation script that runs all individual validators and
    provides a comprehensive compliance report.

.PARAMETER StateDir
    Directory containing state files (default: .state)

.PARAMETER TasksDir
    Directory containing task definitions (default: tasks)

.PARAMETER DocsDir
    Base documentation directory (default: docs)

.PARAMETER Verbose
    Enable verbose output

.EXAMPLE
    ./validate_compliance.ps1

.EXAMPLE
    ./validate_compliance.ps1 -StateDir .state -TasksDir tasks -Verbose
#>

[CmdletBinding()]
param(
    [Parameter()]
    [string]$StateDir = ".state",

    [Parameter()]
    [string]$TasksDir = "tasks",

    [Parameter()]
    [string]$DocsDir = "docs",

    [Parameter()]
    [switch]$VerboseOutput
)

$ErrorActionPreference = "Stop"
$script:TotalChecks = 0
$script:PassedChecks = 0
$script:FailedChecks = 0

function Write-Section {
    param([string]$Title)
    Write-Host "`n$('=' * 80)" -ForegroundColor Cyan
    Write-Host $Title -ForegroundColor Cyan
    Write-Host $('=' * 80) -ForegroundColor Cyan
}

function Run-Validator {
    param(
        [string]$Name,
        [string]$ScriptPath,
        [hashtable]$Parameters
    )

    Write-Section "Running: $Name"

    if (-not (Test-Path $ScriptPath)) {
        Write-Host "ERROR: Validator not found: $ScriptPath" -ForegroundColor Red
        $script:FailedChecks++
        return $false
    }

    try {
        $params = @{}
        foreach ($key in $Parameters.Keys) {
            $params[$key] = $Parameters[$key]
        }

        if ($VerboseOutput) {
            $params['VerboseOutput'] = $true
        }

        & $ScriptPath @params

        if ($LASTEXITCODE -eq 0) {
            $script:PassedChecks++
            return $true
        } else {
            $script:FailedChecks++
            return $false
        }
    } catch {
        Write-Host "ERROR: Validator crashed: $($_.Exception.Message)" -ForegroundColor Red
        $script:FailedChecks++
        return $false
    }
}

# Store script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Section "Orchestration Specification Compliance Validation"
Write-Host "Started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Gray
Write-Host "  State Directory: $StateDir" -ForegroundColor Gray
Write-Host "  Tasks Directory: $TasksDir" -ForegroundColor Gray
Write-Host "  Docs Directory: $DocsDir" -ForegroundColor Gray
Write-Host ""

# Track individual validator results
$results = @{}

# 1. Validate State Observability (STATE-OBS-*)
$script:TotalChecks++
$results['State Observability'] = Run-Validator `
    -Name "State Observability (STATE-OBS-*)" `
    -ScriptPath (Join-Path $scriptDir "validate_state_obs.ps1") `
    -Parameters @{ StateDir = $StateDir }

# 2. Validate Task Definitions (TASK-DEF-*)
$script:TotalChecks++
$results['Task Definitions'] = Run-Validator `
    -Name "Task Definitions (TASK-DEF-*)" `
    -ScriptPath (Join-Path $scriptDir "validate_task_defs.ps1") `
    -Parameters @{ TasksDir = $TasksDir }

# 3. Validate DAG Structure (DAG-VIEW-*)
$script:TotalChecks++
$results['DAG Structure'] = Run-Validator `
    -Name "DAG Structure (DAG-VIEW-*)" `
    -ScriptPath (Join-Path $scriptDir "validate_dag_structure.ps1") `
    -Parameters @{ StateDir = $StateDir }

# 4. Validate Failure Modes (ERR-FM-*)
$script:TotalChecks++
$failureModesDir = Join-Path $DocsDir "failure_modes"
$results['Failure Modes'] = Run-Validator `
    -Name "Failure Modes (ERR-FM-*)" `
    -ScriptPath (Join-Path $scriptDir "validate_failure_modes.ps1") `
    -Parameters @{ DocsDir = $failureModesDir }

# 5. Validate Documentation Structure
Write-Section "Documentation Structure Validation"

$docChecks = @{
    "Execution Model OVERVIEW.md" = (Join-Path $DocsDir "execution_model/OVERVIEW.md")
    "Execution Model STATE_MACHINE.md" = (Join-Path $DocsDir "execution_model/STATE_MACHINE.md")
    "Execution Model RECOVERY.md" = (Join-Path $DocsDir "execution_model/RECOVERY.md")
    "State Machine task_lifecycle.yaml" = (Join-Path $DocsDir "state_machines/task_lifecycle.yaml")
    "State Machine workstream_lifecycle.yaml" = (Join-Path $DocsDir "state_machines/workstream_lifecycle.yaml")
    "State Machine worker_lifecycle.yaml" = (Join-Path $DocsDir "state_machines/worker_lifecycle.yaml")
    "Operations AUDIT_RETENTION.md" = (Join-Path $DocsDir "operations/AUDIT_RETENTION.md")
    "Failure Modes CATALOG.md" = (Join-Path $DocsDir "failure_modes/CATALOG.md")
}

$docChecksPassed = 0
$docChecksFailed = 0

foreach ($check in $docChecks.GetEnumerator()) {
    $script:TotalChecks++
    if (Test-Path $check.Value) {
        Write-Host "[✓] $($check.Key)" -ForegroundColor Green
        $docChecksPassed++
        $script:PassedChecks++
    } else {
        Write-Host "[✗] $($check.Key) - NOT FOUND" -ForegroundColor Red
        $docChecksFailed++
        $script:FailedChecks++
    }
}

$results['Documentation Structure'] = ($docChecksFailed -eq 0)

# 6. Validate Capability Registry
Write-Section "Capability Registry Validation"

$capabilityChecks = @{
    "Capability Registry (registry.psd1)" = "capabilities/registry.psd1"
    "Resource Registry (resources.psd1)" = "capabilities/resources.psd1"
}

$capChecksPassed = 0
$capChecksFailed = 0

foreach ($check in $capabilityChecks.GetEnumerator()) {
    $script:TotalChecks++
    if (Test-Path $check.Value) {
        # Try to parse PowerShell data file
        try {
            $content = Get-Content $check.Value -Raw
            if ($content -match '@\(') {
                Write-Host "[✓] $($check.Key)" -ForegroundColor Green
                $capChecksPassed++
                $script:PassedChecks++
            } else {
                Write-Host "[✗] $($check.Key) - INVALID FORMAT" -ForegroundColor Red
                $capChecksFailed++
                $script:FailedChecks++
            }
        } catch {
            Write-Host "[✗] $($check.Key) - PARSE ERROR" -ForegroundColor Red
            $capChecksFailed++
            $script:FailedChecks++
        }
    } else {
        Write-Host "[✗] $($check.Key) - NOT FOUND" -ForegroundColor Red
        $capChecksFailed++
        $script:FailedChecks++
    }
}

$results['Capability Registry'] = ($capChecksFailed -eq 0)

# Final Summary
Write-Section "Compliance Validation Summary"

Write-Host "`nValidator Results:" -ForegroundColor Yellow
foreach ($result in $results.GetEnumerator()) {
    $status = if ($result.Value) { "PASS" } else { "FAIL" }
    $color = if ($result.Value) { "Green" } else { "Red" }
    $symbol = if ($result.Value) { "✓" } else { "✗" }

    Write-Host "  [$symbol] $($result.Key): " -NoNewline
    Write-Host $status -ForegroundColor $color
}

Write-Host "`nOverall Statistics:" -ForegroundColor Yellow
Write-Host "  Total Checks: $script:TotalChecks" -ForegroundColor Gray
Write-Host "  Passed: $script:PassedChecks" -ForegroundColor Green
Write-Host "  Failed: $script:FailedChecks" -ForegroundColor $(if ($script:FailedChecks -gt 0) { "Red" } else { "Green" })

$successRate = if ($script:TotalChecks -gt 0) {
    [Math]::Round(($script:PassedChecks / $script:TotalChecks) * 100, 1)
} else {
    0
}
Write-Host "  Success Rate: $successRate%" -ForegroundColor $(if ($successRate -eq 100) { "Green" } elseif ($successRate -gt 75) { "Yellow" } else { "Red" })

Write-Host "`nCompleted: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray

if ($script:FailedChecks -gt 0) {
    Write-Host "`n✗ COMPLIANCE VALIDATION FAILED" -ForegroundColor Red
    Write-Host "  Review errors above and fix compliance issues." -ForegroundColor Red
    exit 1
} else {
    Write-Host "`n✓ COMPLIANCE VALIDATION PASSED" -ForegroundColor Green
    Write-Host "  All orchestration specification requirements met." -ForegroundColor Green
    exit 0
}
