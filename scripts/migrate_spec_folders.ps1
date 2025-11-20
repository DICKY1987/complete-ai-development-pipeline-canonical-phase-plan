#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Migrate openspec/ and spec/ into unified specifications/ directory.

.DESCRIPTION
    This script wraps the Python migration script to provide a native
    PowerShell experience for Windows users.

.PARAMETER DryRun
    Show what would be done without making changes

.PARAMETER Backup
    Create backup of old directories before migration

.EXAMPLE
    .\scripts\migrate_spec_folders.ps1 -DryRun
    Show what would be migrated without making changes

.EXAMPLE
    .\scripts\migrate_spec_folders.ps1 -Backup
    Perform migration with backup of old directories

.EXAMPLE
    .\scripts\migrate_spec_folders.ps1
    Perform migration without backup
#>

param(
    [switch]$DryRun,
    [switch]$Backup
)

$ErrorActionPreference = "Stop"

# Get script directory and repository root
$ScriptDir = Split-Path -Parent $PSCommandPath
$RepoRoot = Split-Path -Parent $ScriptDir

# Build Python command
$PythonScript = Join-Path $ScriptDir "migrate_spec_folders.py"
$PythonArgs = @()

if ($DryRun) {
    $PythonArgs += "--dry-run"
}

if ($Backup) {
    $PythonArgs += "--backup"
}

# Check if Python script exists
if (-not (Test-Path $PythonScript)) {
    Write-Error "Python script not found: $PythonScript"
    exit 1
}

# Run Python script
Write-Host "Running migration script..." -ForegroundColor Cyan
Write-Host "Repository: $RepoRoot" -ForegroundColor Gray
Write-Host ""

try {
    if ($PythonArgs.Count -gt 0) {
        & python $PythonScript $PythonArgs
    } else {
        & python $PythonScript
    }
    
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -eq 0) {
        Write-Host ""
        Write-Host "✓ Script completed successfully" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "✗ Script failed with exit code: $exitCode" -ForegroundColor Red
        exit $exitCode
    }
}
catch {
    Write-Error "Failed to run migration script: $_"
    exit 1
}
