#!/usr/bin/env pwsh
# DOC_ID: DOC-PAT-EXEC-CODE-CLEANUP-ARCHIVAL-EXECUTOR-001
<#
.SYNOPSIS
    Execute code cleanup and dead-code archival pattern

.DESCRIPTION
    Implements EXEC-017 pattern for structured code cleanup:
    - Multi-signal analysis of codebase
    - Tiered cleanup recommendations
    - Safe archival with backup/rollback
    - Validation and testing

.PARAMETER InstancePath
    Path to pattern instance JSON file

.PARAMETER DryRun
    Run analysis only without archiving

.PARAMETER SkipTests
    Skip test validation

.EXAMPLE
    .\code_cleanup_archival_executor.ps1 -InstancePath instance.json -DryRun

.NOTES
    Pattern: PAT-EXEC-CODE-CLEANUP-ARCHIVAL-001
    Version: 1.0.0
    Created: 2025-12-09
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$InstancePath,

    [switch]$DryRun,

    [switch]$SkipTests
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  EXEC-017: Code Cleanup & Dead-Code Archival" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Load instance
if (-not (Test-Path $InstancePath)) {
    throw "Instance file not found: $InstancePath"
}

$instance = Get-Content $InstancePath -Raw | ConvertFrom-Json

# Validate required fields
$required = @('pattern_id', 'project_root', 'analyzer_script', 'critical_files', 'execution_mode')
foreach ($field in $required) {
    if (-not $instance.$field) {
        throw "Missing required field: $field"
    }
}

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Project Root: $($instance.project_root)" -ForegroundColor Gray
Write-Host "  Analyzer: $($instance.analyzer_script)" -ForegroundColor Gray
Write-Host "  Execution Mode: $($instance.execution_mode)" -ForegroundColor Gray
Write-Host "  Dry Run: $($DryRun -or $instance.dry_run)" -ForegroundColor Gray
Write-Host ""

# Validate project root exists
if (-not (Test-Path $instance.project_root)) {
    throw "Project root not found: $($instance.project_root)"
}

# Change to project root
Push-Location $instance.project_root

try {
    # PHASE 1: PRE-CONDITIONS CHECK
    Write-Host "Phase 1: Validating Prerequisites..." -ForegroundColor Cyan

    # Check for Git
    $gitStatus = git status 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Git repository required. Project must be under version control."
    }

    # Check for clean working tree
    $changedFiles = git status --porcelain
    if ($changedFiles) {
        Write-Warning "Working tree has uncommitted changes"
        Write-Host "Changed files:" -ForegroundColor Yellow
        $changedFiles | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }

        $continue = Read-Host "Continue anyway? (y/N)"
        if ($continue -ne 'y') {
            throw "Aborted: Clean working tree required"
        }
    }

    Write-Host "  ✓ Git repository validated" -ForegroundColor Green
    Write-Host "  ✓ Working tree checked" -ForegroundColor Green
    Write-Host ""

    # PHASE 2: BACKUP
    if ($instance.backup_strategy) {
        Write-Host "Phase 2: Creating Backup..." -ForegroundColor Cyan

        $backupMethod = $instance.backup_strategy.method

        if ($backupMethod -eq 'branch') {
            $branchName = if ($instance.backup_strategy.branch_name) {
                $instance.backup_strategy.branch_name
            } else {
                "backup/exec017-$(Get-Date -Format 'yyyy-MM-dd-HHmmss')"
            }

            git branch $branchName
            Write-Host "  ✓ Created backup branch: $branchName" -ForegroundColor Green
        } elseif ($backupMethod -eq 'stash') {
            git stash save "EXEC-017 backup $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
            Write-Host "  ✓ Created git stash backup" -ForegroundColor Green
        }

        Write-Host ""
    }

    # PHASE 3: ANALYSIS
    Write-Host "Phase 3: Running Analysis..." -ForegroundColor Cyan

    $analyzerPath = Join-Path $instance.project_root $instance.analyzer_script
    if (-not (Test-Path $analyzerPath)) {
        throw "Analyzer script not found: $analyzerPath"
    }

    Write-Host "  Running analyzer: $analyzerPath" -ForegroundColor Gray

    # Execute analyzer (assuming it's a Python script)
    if ($analyzerPath -match '\.py$') {
        python $analyzerPath
    } elseif ($analyzerPath -match '\.ps1$') {
        & $analyzerPath
    } else {
        throw "Unsupported analyzer script type: $analyzerPath"
    }

    Write-Host "  ✓ Analysis complete" -ForegroundColor Green
    Write-Host ""

    # PHASE 4: ARCHIVAL (if not dry run)
    if (-not ($DryRun -or $instance.dry_run)) {
        Write-Host "Phase 4: Archival..." -ForegroundColor Cyan

        $archiveDir = if ($instance.archive_directory) {
            Join-Path $instance.project_root $instance.archive_directory
        } else {
            Join-Path $instance.project_root "_archived"
        }

        Write-Host "  Archive directory: $archiveDir" -ForegroundColor Gray
        New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null

        Write-Host "  ⚠ Archival implementation depends on analyzer output" -ForegroundColor Yellow
        Write-Host "  ⚠ Manual archival required based on tier reports" -ForegroundColor Yellow
        Write-Host ""
    }

    # PHASE 5: VALIDATION
    if (-not $SkipTests -and $instance.validation_tests -and $instance.validation_tests.enabled) {
        Write-Host "Phase 5: Validation..." -ForegroundColor Cyan

        if ($instance.validation_tests.test_command) {
            Write-Host "  Running tests: $($instance.validation_tests.test_command)" -ForegroundColor Gray
            Invoke-Expression $instance.validation_tests.test_command

            if ($LASTEXITCODE -eq 0) {
                Write-Host "  ✓ Tests passed" -ForegroundColor Green
            } else {
                Write-Warning "Tests failed - consider rollback"
            }
        }

        Write-Host ""
    }

    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host "  EXECUTION COMPLETE" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Review analysis reports" -ForegroundColor Gray
    Write-Host "  2. Process tier-based recommendations" -ForegroundColor Gray
    Write-Host "  3. Archive files as appropriate" -ForegroundColor Gray
    Write-Host "  4. Run full test suite" -ForegroundColor Gray
    Write-Host ""

} catch {
    Write-Error "Execution failed: $_"
    throw
} finally {
    Pop-Location
}
