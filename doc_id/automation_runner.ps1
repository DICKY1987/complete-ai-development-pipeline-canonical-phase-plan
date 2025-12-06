# DOC_LINK: DOC-SCRIPT-DOC-ID-AUTOMATION-RUNNER-005
<#
.SYNOPSIS
    DOC_ID System Automation Runner

.DESCRIPTION
    Orchestrates all doc_id automation tasks: scanning, validation, reporting, cleanup

.PARAMETER Task
    Task to run: scan, validate, cleanup, report, sync, all

.PARAMETER DryRun
    Preview changes without applying

.EXAMPLE
    .\doc_id\automation_runner.ps1 -Task scan
    .\doc_id\automation_runner.ps1 -Task all -DryRun
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('scan', 'validate', 'cleanup', 'report', 'sync', 'all')]
    [string]$Task,

    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot
$DocIdDir = Join-Path $RepoRoot "doc_id"

function Write-TaskHeader {
    param([string]$Title)
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host " $Title" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
}

function Invoke-Scanner {
    Write-TaskHeader "Running DOC_ID Scanner"
    & python "$DocIdDir\doc_id_scanner.py" scan
    & python "$DocIdDir\doc_id_scanner.py" stats
}

function Invoke-Validation {
    Write-TaskHeader "Running Coverage Validation"
    & python "$DocIdDir\validate_doc_id_coverage.py" --baseline 0.55
}

function Invoke-Cleanup {
    Write-TaskHeader "Running Cleanup Check"
    & python "$DocIdDir\cleanup_invalid_doc_ids.py" scan
    if (-not $DryRun) {
        # PATTERN: EXEC-004 - Use --auto-approve for automation
        & python "$DocIdDir\cleanup_invalid_doc_ids.py" fix --backup --auto-approve
    }
}

function Invoke-Reporting {
    Write-TaskHeader "Generating Reports"
    & python "$DocIdDir\scheduled_report_generator.py" daily
}

function Invoke-Sync {
    Write-TaskHeader "Syncing Registries"
    $dryRunFlag = if ($DryRun) { "--dry-run" } else { "" }
    if ($DryRun) {
        & python "$DocIdDir\sync_registries.py" check
    } else {
        & python "$DocIdDir\sync_registries.py" sync
    }
}

# Main execution
try {
    Write-Host "DOC_ID Automation Runner" -ForegroundColor Green
    Write-Host "Repository: $RepoRoot" -ForegroundColor Gray
    if ($DryRun) {
        Write-Host "Mode: DRY RUN (preview only)" -ForegroundColor Yellow
    }

    switch ($Task) {
        'scan' { Invoke-Scanner }
        'validate' { Invoke-Validation }
        'cleanup' { Invoke-Cleanup }
        'report' { Invoke-Reporting }
        'sync' { Invoke-Sync }
        'all' {
            Invoke-Scanner
            Invoke-Validation
            Invoke-Cleanup
            Invoke-Reporting
            Invoke-Sync
        }
    }

    Write-Host "`n✅ Task completed successfully" -ForegroundColor Green
    exit 0

} catch {
    Write-Host "`n❌ Error: $_" -ForegroundColor Red
    exit 1
}
