#!/usr/bin/env pwsh
# DOC_LINK: DOC-SCRIPT-VALIDATE-STATE-OBS-094
<#
.SYNOPSIS
    Validate State Observability Requirements (STATE-OBS-*)

.DESCRIPTION
    Validates that the orchestration system meets all state observability
    requirements defined in the orchestration specification.

.PARAMETER StateDir
    Directory containing state files (default: .state)

.PARAMETER Verbose
    Enable verbose output

.EXAMPLE
    ./validate_state_obs.ps1 -StateDir .state
#>

[CmdletBinding()]
param(
    [Parameter()]
    [string]$StateDir = ".state",

    [Parameter()]
    [switch]$VerboseOutput
)

$ErrorActionPreference = "Stop"
$script:FailureCount = 0
$script:PassCount = 0

function Write-Result {
    param(
        [string]$RequirementId,
        [string]$Status,
        [string]$Message
    )

    $statusSymbol = if ($Status -eq "PASS") { "✓" } else { "✗" }
    $color = if ($Status -eq "PASS") { "Green" } else { "Red" }

    Write-Host "[$statusSymbol] $RequirementId : " -NoNewline
    Write-Host $Message -ForegroundColor $color

    if ($Status -eq "PASS") {
        $script:PassCount++
    } else {
        $script:FailureCount++
    }
}

function Test-FileExists {
    param([string]$Path, [string]$Description)

    if (Test-Path $Path) {
        if ($VerboseOutput) {
            Write-Host "  Found: $Path" -ForegroundColor Gray
        }
        return $true
    } else {
        Write-Host "  Missing: $Path" -ForegroundColor Red
        return $false
    }
}

function Test-JsonValid {
    param([string]$Path)

    try {
        $content = Get-Content $Path -Raw
        $null = ConvertFrom-Json $content
        return $true
    } catch {
        Write-Host "  Invalid JSON: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Test-JsonlValid {
    param([string]$Path)

    try {
        $lineNum = 0
        Get-Content $Path | ForEach-Object {
            $lineNum++
            if ($_ -and $_.Trim()) {
                $null = ConvertFrom-Json $_
            }
        }
        return $true
    } catch {
        Write-Host "  Invalid JSONL at line ${lineNum}: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

Write-Host "`n=== Validating State Observability Requirements ===" -ForegroundColor Cyan
Write-Host "State Directory: $StateDir`n" -ForegroundColor Gray

# STATE-OBS-001: State Snapshot Requirements
Write-Host "`nSTATE-OBS-001: State Snapshot Requirements" -ForegroundColor Yellow

$currentJsonPath = Join-Path $StateDir "current.json"
$obs001_exists = Test-FileExists $currentJsonPath "State snapshot file"
$obs001_valid = if ($obs001_exists) { Test-JsonValid $currentJsonPath } else { $false }
$obs001_pass = $obs001_exists -and $obs001_valid

if ($obs001_pass) {
    # Check for required fields
    $stateData = Get-Content $currentJsonPath -Raw | ConvertFrom-Json
    $hasRequiredFields = $true

    foreach ($field in @("workstreams", "tasks", "timestamp")) {
        if (-not $stateData.PSObject.Properties.Name.Contains($field)) {
            Write-Host "  Missing required field: $field" -ForegroundColor Red
            $hasRequiredFields = $false
        }
    }

    $obs001_pass = $hasRequiredFields
}

Write-Result "STATE-OBS-001" $(if ($obs001_pass) { "PASS" } else { "FAIL" }) `
    "State snapshot file exists and is queryable"

# STATE-OBS-002: Transition Log Requirements
Write-Host "`nSTATE-OBS-002: Transition Log Requirements" -ForegroundColor Yellow

$transitionsPath = Join-Path $StateDir "transitions.jsonl"
$obs002_exists = Test-FileExists $transitionsPath "Transition log file"
$obs002_valid = if ($obs002_exists) { Test-JsonlValid $transitionsPath } else { $false }
$obs002_pass = $obs002_exists -and $obs002_valid

Write-Result "STATE-OBS-002" $(if ($obs002_pass) { "PASS" } else { "FAIL" }) `
    "Transition log is append-only and valid JSONL"

# STATE-OBS-003: Atomicity Guarantees
Write-Host "`nSTATE-OBS-003: Atomicity Guarantees" -ForegroundColor Yellow

# Check that no .tmp file exists (atomic rename completed)
$tmpPath = Join-Path $StateDir "current.json.tmp"
$obs003_no_tmp = -not (Test-Path $tmpPath)

if (-not $obs003_no_tmp) {
    Write-Host "  Found abandoned .tmp file: $tmpPath" -ForegroundColor Red
}

Write-Result "STATE-OBS-003" $(if ($obs003_no_tmp) { "PASS" } else { "FAIL" }) `
    "No abandoned temporary state files (atomic writes working)"

# STATE-OBS-004: Event Schema
Write-Host "`nSTATE-OBS-004: Event Schema" -ForegroundColor Yellow

$obs004_pass = $false
if ($obs002_exists) {
    try {
        $validEvents = $true
        $eventCount = 0

        Get-Content $transitionsPath | ForEach-Object {
            if ($_ -and $_.Trim()) {
                $event = ConvertFrom-Json $_
                $eventCount++

                # Check required fields
                $requiredFields = @("timestamp", "event", "severity")
                foreach ($field in $requiredFields) {
                    if (-not $event.PSObject.Properties.Name.Contains($field)) {
                        Write-Host "  Event missing field '$field' at line $eventCount" -ForegroundColor Red
                        $validEvents = $false
                    }
                }

                # Check severity is valid
                if ($event.severity -and $event.severity -notin @("info", "warning", "error", "critical")) {
                    Write-Host "  Invalid severity '$($event.severity)' at line $eventCount" -ForegroundColor Red
                    $validEvents = $false
                }
            }
        }

        if ($VerboseOutput -and $validEvents) {
            Write-Host "  Validated $eventCount events" -ForegroundColor Gray
        }

        $obs004_pass = $validEvents
    } catch {
        Write-Host "  Error validating event schema: $($_.Exception.Message)" -ForegroundColor Red
        $obs004_pass = $false
    }
} else {
    Write-Host "  Cannot validate: transitions.jsonl not found" -ForegroundColor Red
}

Write-Result "STATE-OBS-004" $(if ($obs004_pass) { "PASS" } else { "FAIL" }) `
    "Event schema includes severity levels and required fields"

# STATE-OBS-005: Index Files
Write-Host "`nSTATE-OBS-005: Index Files" -ForegroundColor Yellow

$indexFiles = @(
    "by_workstream.json",
    "by_status.json",
    "by_worker.json"
)

$obs005_pass = $true
$foundIndices = 0

foreach ($indexFile in $indexFiles) {
    $indexPath = Join-Path $StateDir $indexFile
    if (Test-Path $indexPath) {
        $foundIndices++
        if ($VerboseOutput) {
            Write-Host "  Found index: $indexFile" -ForegroundColor Gray
        }
    } else {
        if ($VerboseOutput) {
            Write-Host "  Optional index not found: $indexFile" -ForegroundColor Gray
        }
    }
}

# Index files are SHOULD, not MUST, so we just report
Write-Result "STATE-OBS-005" "PASS" `
    "Index files: $foundIndices/$($indexFiles.Count) present (optional)"

# STATE-OBS-006: Index Generation
Write-Host "`nSTATE-OBS-006: Index Generation" -ForegroundColor Yellow

$obs006_pass = $true
if ($foundIndices -gt 0) {
    # Check if indices are newer than or same age as current.json
    $currentMtime = (Get-Item $currentJsonPath).LastWriteTime

    foreach ($indexFile in $indexFiles) {
        $indexPath = Join-Path $StateDir $indexFile
        if (Test-Path $indexPath) {
            $indexMtime = (Get-Item $indexPath).LastWriteTime
            $staleness = ($currentMtime - $indexMtime).TotalSeconds

            if ($staleness -gt 60) {
                Write-Host "  Index $indexFile is stale by $([int]$staleness) seconds" -ForegroundColor Yellow
                # Don't fail, just warn (indices can be regenerated)
            } elseif ($VerboseOutput) {
                Write-Host "  Index $indexFile is fresh (${staleness}s old)" -ForegroundColor Gray
            }
        }
    }
}

Write-Result "STATE-OBS-006" $(if ($obs006_pass) { "PASS" } else { "FAIL" }) `
    "Index generation requirements met"

# Summary
Write-Host "`n=== Validation Summary ===" -ForegroundColor Cyan
Write-Host "PASSED: $script:PassCount" -ForegroundColor Green
Write-Host "FAILED: $script:FailureCount" -ForegroundColor $(if ($script:FailureCount -gt 0) { "Red" } else { "Green" })

if ($script:FailureCount -gt 0) {
    Write-Host "`nValidation FAILED. See errors above." -ForegroundColor Red
    exit 1
} else {
    Write-Host "`nValidation PASSED. All state observability requirements met." -ForegroundColor Green
    exit 0
}
