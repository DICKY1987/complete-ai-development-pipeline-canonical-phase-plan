#!/usr/bin/env pwsh
# DOC_LINK: DOC-PAT-GLOSSARY-PATCH-APPLY-EXECUTOR-217
<#
.SYNOPSIS
    Executor for glossary_patch_apply pattern (PAT-GLOSSARY-PATCH-APPLY-001)
    
.DESCRIPTION
    Applies patch specifications to glossary metadata with:
    - Pre-flight validation of patch spec
    - Dry-run preview mode
    - Atomic application (all or nothing)
    - Automatic changelog updates
    - Post-apply validation
    
.PARAMETER InstancePath
    Path to pattern instance JSON file
    
.PARAMETER Verbose
    Enable verbose output
    
.EXAMPLE
    .\glossary_patch_apply_executor.ps1 -InstancePath instance.json
    
.NOTES
    Pattern: PAT-GLOSSARY-PATCH-APPLY-001
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
    pattern_id = "PAT-GLOSSARY-PATCH-APPLY-001"
    patch_id = ""
    terms_updated = 0
    changes_made = @()
    validation_passed = $false
    execution_duration_seconds = 0
    errors = @()
}

try {
    Write-Host "Glossary Patch Apply Pattern Executor" -ForegroundColor Cyan
    Write-Host "=====================================" -ForegroundColor Cyan
    
    # STEP 1: Load instance
    Write-Step "S1: Loading pattern instance..."
    if (-not (Test-Path $InstancePath)) {
        throw "Instance file not found: $InstancePath"
    }
    
    $instance = Get-Content $InstancePath -Raw | ConvertFrom-Json
    Write-Success "Loaded instance from $InstancePath"
    
    # Validate pattern ID
    if ($instance.pattern_id -ne "PAT-GLOSSARY-PATCH-APPLY-001") {
        throw "Invalid pattern_id: Expected PAT-GLOSSARY-PATCH-APPLY-001, got $($instance.pattern_id)"
    }
    Write-Success "Pattern ID validated"
    
    # Extract parameters
    $projectRoot = $instance.inputs.project_root
    $patchSpecPath = $instance.inputs.patch_spec_path
    $dryRun = $instance.inputs.dry_run
    $validateAfter = if ($null -ne $instance.inputs.validate_after) { $instance.inputs.validate_after } else { $true }
    $updateChangelog = if ($null -ne $instance.inputs.update_changelog) { $instance.inputs.update_changelog } else { $true }
    
    Write-Info "Project root: $projectRoot"
    Write-Info "Patch spec: $patchSpecPath"
    Write-Info "Dry run: $dryRun"
    
    # STEP 2: Validate prerequisites
    Write-Step "S2: Validating prerequisites..."
    
    # Check project structure
    $glossaryRoot = Join-Path $projectRoot "glossary"
    if (-not (Test-Path $glossaryRoot)) {
        throw "Glossary directory not found: $glossaryRoot"
    }
    Write-Success "Glossary directory found"
    
    # Check patch spec file
    $fullPatchPath = Join-Path $glossaryRoot "updates" $patchSpecPath
    if (-not (Test-Path $fullPatchPath)) {
        throw "Patch specification not found: $fullPatchPath"
    }
    Write-Success "Patch specification found"
    
    # Check Python and required modules
    try {
        $pythonVersion = python --version 2>&1
        Write-Success "Python available: $pythonVersion"
    }
    catch {
        throw "Python not found. Please install Python 3+"
    }
    
    try {
        python -c "import yaml" 2>&1 | Out-Null
        Write-Success "pyyaml module available"
    }
    catch {
        throw "pyyaml module not found. Install with: pip install pyyaml"
    }
    
    # STEP 3: Apply patch
    Write-Step "S3: Applying patch specification..."
    
    Push-Location $glossaryRoot
    try {
        $applyArgs = @(
            "scripts/update_term.py",
            "--spec", $patchSpecPath
        )
        
        if ($dryRun) {
            $applyArgs += "--dry-run"
            Write-Info "Running in DRY RUN mode - no changes will be saved"
        }
        else {
            $applyArgs += "--apply"
        }
        
        if ($validateAfter -and -not $dryRun) {
            $applyArgs += "--validate"
        }
        
        $output = python $applyArgs 2>&1
        $exitCode = $LASTEXITCODE
        
        if ($VerboseOutput) {
            Write-Host $output
        }
        
        if ($exitCode -ne 0) {
            throw "Patch application failed with exit code $exitCode`n$output"
        }
        
        # Parse output for results
        $outputText = $output | Out-String
        
        # Extract patch ID
        if ($outputText -match 'Applying patch: ([A-Za-z0-9]+)') {
            $result.patch_id = $matches[1]
            Write-Success "Patch ID: $($result.patch_id)"
        }
        
        # Extract term count
        if ($outputText -match 'Updated (\d+) terms') {
            $result.terms_updated = [int]$matches[1]
            Write-Success "Terms updated: $($result.terms_updated)"
        }
        
        if ($dryRun) {
            $result.status = "dry_run_complete"
            Write-Info "Dry run completed - review changes above"
        }
        else {
            Write-Success "Patch applied successfully"
        }
    }
    finally {
        Pop-Location
    }
    
    # STEP 4: Post-apply validation (if enabled and not dry run)
    if ($validateAfter -and -not $dryRun) {
        Write-Step "S4: Running post-apply validation..."
        
        Push-Location $glossaryRoot
        try {
            $validateOutput = python scripts/validate_glossary.py --quick 2>&1
            $validateExitCode = $LASTEXITCODE
            
            if ($VerboseOutput) {
                Write-Host $validateOutput
            }
            
            if ($validateExitCode -eq 0) {
                $result.validation_passed = $true
                Write-Success "Validation passed"
            }
            else {
                $result.validation_passed = $false
                Write-Failure "Validation failed"
                $result.errors += "Post-apply validation failed"
            }
        }
        finally {
            Pop-Location
        }
    }
    
    # STEP 5: Generate output
    Write-Step "S5: Generating execution output..."
    
    $result.execution_duration_seconds = ((Get-Date) - $startTime).TotalSeconds
    
    # Save output
    $outputPath = Join-Path (Split-Path $InstancePath -Parent) "output.json"
    $instance.outputs = $result
    $instance | ConvertTo-Json -Depth 10 | Set-Content $outputPath -Encoding UTF8
    Write-Success "Output saved to $outputPath"
    
    # Summary
    Write-Host "`n=====================================" -ForegroundColor Cyan
    Write-Host "Execution Summary" -ForegroundColor Cyan
    Write-Host "=====================================" -ForegroundColor Cyan
    Write-Host "Status:        $($result.status)" -ForegroundColor $(if ($result.status -eq "success") { "Green" } else { "Yellow" })
    Write-Host "Patch ID:      $($result.patch_id)"
    Write-Host "Terms Updated: $($result.terms_updated)"
    Write-Host "Duration:      $([math]::Round($result.execution_duration_seconds, 2))s"
    if ($validateAfter -and -not $dryRun) {
        Write-Host "Validation:    $(if ($result.validation_passed) { 'PASSED' } else { 'FAILED' })" -ForegroundColor $(if ($result.validation_passed) { "Green" } else { "Red" })
    }
    Write-Host "=====================================" -ForegroundColor Cyan
    
    exit 0
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
