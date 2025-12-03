#!/usr/bin/env pwsh
# DOC_LINK: DOC-PAT-GLOSSARY-VALIDATE-EXECUTOR-220
<#
.SYNOPSIS
    Executor for glossary_validate pattern (PAT-GLOSSARY-VALIDATE-001)
    
.DESCRIPTION
    Validates glossary structure, content, and quality with:
    - Multiple validation modes (full, quick, orphans, paths)
    - Comprehensive error and warning reporting
    - Quality score calculation
    - Configurable failure thresholds
    
.PARAMETER InstancePath
    Path to pattern instance JSON file
    
.PARAMETER Verbose
    Enable verbose output
    
.EXAMPLE
    .\glossary_validate_executor.ps1 -InstancePath instance.json
    
.NOTES
    Pattern: PAT-GLOSSARY-VALIDATE-001
    Version: 1.0.0
    Requires: PowerShell 7+, Python 3+, pyyaml
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$InstancePath,
    
    [switch]$VerboseOutput
)

$ErrorActionPreference = "Stop"
$startTime = Get-Date

# Helper functions
function Write-Step { param([string]$Message) Write-Host "`n▶ $Message" -ForegroundColor Cyan }
function Write-Success { param([string]$Message) Write-Host "  ✓ $Message" -ForegroundColor Green }
function Write-Failure { param([string]$Message) Write-Host "  ✗ $Message" -ForegroundColor Red }
function Write-Info { param([string]$Message) Write-Host "  ℹ $Message" -ForegroundColor Yellow }

# Result tracking
$result = @{
    status = "success"
    pattern_id = "PAT-GLOSSARY-VALIDATE-001"
    total_terms = 0
    errors = @()
    warnings = @()
    orphaned_terms = @()
    quality_score = 0
    execution_duration_seconds = 0
}

try {
    Write-Host "Glossary Validate Pattern Executor" -ForegroundColor Cyan
    Write-Host "===================================" -ForegroundColor Cyan
    
    # STEP 1: Load instance
    Write-Step "S1: Loading pattern instance..."
    if (-not (Test-Path $InstancePath)) {
        throw "Instance file not found: $InstancePath"
    }
    
    $instance = Get-Content $InstancePath -Raw | ConvertFrom-Json
    Write-Success "Loaded instance from $InstancePath"
    
    # Validate pattern ID
    if ($instance.pattern_id -ne "PAT-GLOSSARY-VALIDATE-001") {
        throw "Invalid pattern_id: Expected PAT-GLOSSARY-VALIDATE-001, got $($instance.pattern_id)"
    }
    Write-Success "Pattern ID validated"
    
    # Extract parameters
    $projectRoot = $instance.inputs.project_root
    $validationMode = if ($instance.inputs.validation_mode) { $instance.inputs.validation_mode } else { "full" }
    $failOnWarnings = if ($null -ne $instance.inputs.fail_on_warnings) { $instance.inputs.fail_on_warnings } else { $false }
    
    Write-Info "Project root: $projectRoot"
    Write-Info "Validation mode: $validationMode"
    Write-Info "Fail on warnings: $failOnWarnings"
    
    # STEP 2: Validate prerequisites
    Write-Step "S2: Validating prerequisites..."
    
    # Check glossary directory
    $glossaryRoot = Join-Path $projectRoot "glossary"
    if (-not (Test-Path $glossaryRoot)) {
        throw "Glossary directory not found: $glossaryRoot"
    }
    Write-Success "Glossary directory found"
    
    # Check validation script
    $validatorScript = Join-Path $glossaryRoot "scripts" "validate_glossary.py"
    if (-not (Test-Path $validatorScript)) {
        throw "Validation script not found: $validatorScript"
    }
    Write-Success "Validation script found"
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Success "Python available: $pythonVersion"
    }
    catch {
        throw "Python not found. Please install Python 3+"
    }
    
    # STEP 3: Run validation
    Write-Step "S3: Running validation (mode: $validationMode)..."
    
    Push-Location $glossaryRoot
    try {
        $validateArgs = @("scripts/validate_glossary.py")
        
        switch ($validationMode) {
            "quick" { $validateArgs += "--quick" }
            "orphans" { $validateArgs += "--check-orphans" }
            "paths" { $validateArgs += "--check-paths" }
            "full" { <# default, no extra args #> }
        }
        
        $output = python $validateArgs 2>&1
        $exitCode = $LASTEXITCODE
        
        $outputText = $output | Out-String
        
        if ($VerboseOutput) {
            Write-Host $outputText
        }
        
        # Parse output
        # Extract term count
        if ($outputText -match 'Found (\d+) terms') {
            $result.total_terms = [int]$matches[1]
            Write-Info "Total terms: $($result.total_terms)"
        }
        
        # Extract errors
        $errorMatches = [regex]::Matches($outputText, '❌.+')
        foreach ($match in $errorMatches) {
            $result.errors += $match.Value -replace '❌\s*', ''
        }
        
        # Extract warnings
        $warningMatches = [regex]::Matches($outputText, '⚠️.+')
        foreach ($match in $warningMatches) {
            $result.warnings += $match.Value -replace '⚠️\s*', ''
        }
        
        # Extract orphaned terms (if checking orphans)
        if ($validationMode -eq "orphans" -or $validationMode -eq "full") {
            if ($outputText -match 'Found (\d+) orphaned terms:') {
                $orphanCount = [int]$matches[1]
                if ($orphanCount -gt 0) {
                    $orphanSection = $outputText -split 'orphaned terms:' | Select-Object -Last 1
                    $orphanMatches = [regex]::Matches($orphanSection, '^\s*-\s*(.+)$', [System.Text.RegularExpressions.RegexOptions]::Multiline)
                    foreach ($match in $orphanMatches) {
                        $result.orphaned_terms += $match.Groups[1].Value.Trim()
                    }
                }
            }
        }
        
        # Determine status
        if ($result.errors.Count -gt 0) {
            $result.status = "failure"
            Write-Failure "$($result.errors.Count) errors found"
        }
        elseif ($result.warnings.Count -gt 0) {
            if ($failOnWarnings) {
                $result.status = "failure"
                Write-Failure "$($result.warnings.Count) warnings found (treating as errors)"
            }
            else {
                $result.status = "warnings"
                Write-Info "$($result.warnings.Count) warnings found"
            }
        }
        else {
            $result.status = "success"
            Write-Success "No errors or warnings found"
        }
        
        # Calculate quality score
        $result.quality_score = 100
        if ($result.errors.Count -gt 0) {
            $result.quality_score -= ($result.errors.Count * 10)
        }
        if ($result.warnings.Count -gt 0) {
            $result.quality_score -= ($result.warnings.Count * 2)
        }
        if ($result.orphaned_terms.Count -gt 0) {
            $result.quality_score -= ($result.orphaned_terms.Count * 1)
        }
        $result.quality_score = [Math]::Max(0, $result.quality_score)
        
        Write-Info "Quality score: $($result.quality_score)/100"
    }
    finally {
        Pop-Location
    }
    
    # STEP 4: Generate output
    Write-Step "S4: Generating execution output..."
    
    $result.execution_duration_seconds = ((Get-Date) - $startTime).TotalSeconds
    
    # Save output
    $outputPath = Join-Path (Split-Path $InstancePath -Parent) "output.json"
    $instance.outputs = $result
    $instance | ConvertTo-Json -Depth 10 | Set-Content $outputPath -Encoding UTF8
    Write-Success "Output saved to $outputPath"
    
    # Summary
    Write-Host "`n===================================" -ForegroundColor Cyan
    Write-Host "Validation Summary" -ForegroundColor Cyan
    Write-Host "===================================" -ForegroundColor Cyan
    Write-Host "Status:         $($result.status)" -ForegroundColor $(
        switch ($result.status) {
            "success" { "Green" }
            "warnings" { "Yellow" }
            "failure" { "Red" }
        }
    )
    Write-Host "Total Terms:    $($result.total_terms)"
    Write-Host "Errors:         $($result.errors.Count)" -ForegroundColor $(if ($result.errors.Count -gt 0) { "Red" } else { "Green" })
    Write-Host "Warnings:       $($result.warnings.Count)" -ForegroundColor $(if ($result.warnings.Count -gt 0) { "Yellow" } else { "Green" })
    Write-Host "Orphaned Terms: $($result.orphaned_terms.Count)" -ForegroundColor $(if ($result.orphaned_terms.Count -gt 0) { "Yellow" } else { "Green" })
    Write-Host "Quality Score:  $($result.quality_score)/100"
    Write-Host "Duration:       $([math]::Round($result.execution_duration_seconds, 2))s"
    Write-Host "===================================" -ForegroundColor Cyan
    
    if ($result.status -eq "failure") {
        exit 1
    }
    else {
        exit 0
    }
}
catch {
    $result.status = "failure"
    $result.errors += $_.Exception.Message
    $result.execution_duration_seconds = ((Get-Date) - $startTime).TotalSeconds
    
    Write-Failure "Execution failed: $($_.Exception.Message)"
    
    # Save error output
    $outputPath = Join-Path (Split-Path $InstancePath -Parent) "output.json"
    $instance.outputs = $result
    $instance | ConvertTo-Json -Depth 10 | Set-Content $outputPath -Encoding UTF8
    
    Write-Host "`nError details saved to $outputPath" -ForegroundColor Red
    exit 1
}
