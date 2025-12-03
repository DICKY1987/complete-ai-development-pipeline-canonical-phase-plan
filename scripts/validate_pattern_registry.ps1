#!/usr/bin/env pwsh
# DOC_LINK: DOC-SCRIPT-VALIDATE-PATTERN-REGISTRY-114
<#
.SYNOPSIS
    Validate PATTERN_INDEX.yaml against schema and check compliance
    
.DESCRIPTION
    Validates the pattern registry for:
    - YAML syntax correctness
    - JSON Schema compliance
    - File path existence
    - Naming convention adherence
    - PAT-CHECK-001 and PAT-CHECK-002 compliance
    
.PARAMETER RegistryPath
    Path to PATTERN_INDEX.yaml (default: patterns/registry/PATTERN_INDEX.yaml)
    
.PARAMETER SchemaPath
    Path to schema file (default: patterns/registry/PATTERN_INDEX.schema.json)
    
.PARAMETER Strict
    Enable strict mode (fail on warnings)
    
.EXAMPLE
    .\validate_pattern_registry.ps1
    
.EXAMPLE
    .\validate_pattern_registry.ps1 -Strict
    
.NOTES
    Requirement: PAT-CHECK-001, PAT-CHECK-002
    Version: 1.0.0
    Created: 2025-11-24
#>

param(
    [string]$RegistryPath = "patterns\registry\PATTERN_INDEX.yaml",
    [string]$SchemaPath = "patterns\registry\PATTERN_INDEX.schema.json",
    [switch]$Strict
)

$ErrorActionPreference = "Stop"

# Color helper functions
function Write-Success { param([string]$Message) Write-Host "  ✓ $Message" -ForegroundColor Green }
function Write-Failure { param([string]$Message) Write-Host "  ✗ $Message" -ForegroundColor Red }
function Write-Warning { param([string]$Message) Write-Host "  ⚠ $Message" -ForegroundColor Yellow }
function Write-Section { param([string]$Message) Write-Host "`n$Message" -ForegroundColor Cyan }

# Validation results
$script:Errors = @()
$script:Warnings = @()
$script:Checks = 0
$script:Passed = 0

function Add-Error {
    param([string]$Message)
    $script:Errors += $Message
    Write-Failure $Message
}

function Add-Warning {
    param([string]$Message)
    $script:Warnings += $Message
    Write-Warning $Message
}

function Test-Check {
    param(
        [string]$Name,
        [scriptblock]$Test,
        [string]$SuccessMessage,
        [string]$FailureMessage,
        [switch]$Warning
    )
    
    $script:Checks++
    
    try {
        $result = & $Test
        if ($result) {
            $script:Passed++
            Write-Success ($SuccessMessage -replace '\{result\}', $result)
        } else {
            if ($Warning) {
                Add-Warning $FailureMessage
            } else {
                Add-Error $FailureMessage
            }
        }
    } catch {
        if ($Warning) {
            Add-Warning "$FailureMessage : $_"
        } else {
            Add-Error "$FailureMessage : $_"
        }
    }
}

# Main validation
Write-Host "Pattern Registry Validation" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan

# Check 1: Registry file exists
Write-Section "Checking registry file..."
Test-Check -Name "Registry exists" -Test {
    Test-Path $RegistryPath
} -SuccessMessage "Registry file found: $RegistryPath" `
  -FailureMessage "Registry file not found: $RegistryPath"

if (-not (Test-Path $RegistryPath)) {
    Write-Host "`n❌ Cannot continue without registry file" -ForegroundColor Red
    exit 1
}

# Check 2: Valid YAML syntax
Write-Section "Validating YAML syntax..."
$registryContent = $null
Test-Check -Name "YAML syntax" -Test {
    try {
        # PowerShell 7+ has ConvertFrom-Yaml, fallback to manual parsing
        if (Get-Command ConvertFrom-Yaml -ErrorAction SilentlyContinue) {
            $script:registryContent = Get-Content $RegistryPath -Raw | ConvertFrom-Yaml
        } else {
            # Install powershell-yaml if not available
            if (-not (Get-Module -ListAvailable -Name powershell-yaml)) {
                Install-Module powershell-yaml -Force -Scope CurrentUser
            }
            Import-Module powershell-yaml
            $script:registryContent = Get-Content $RegistryPath -Raw | ConvertFrom-Yaml
        }
        $true
    } catch {
        $false
    }
} -SuccessMessage "YAML syntax valid" `
  -FailureMessage "YAML syntax invalid"

# Check 3: Schema validation (if Python available)
Write-Section "Validating against JSON Schema..."
if (Get-Command python -ErrorAction SilentlyContinue) {
    Test-Check -Name "Schema validation" -Test {
        # Create temp Python script for validation
        $validatorScript = @"
import json
import yaml
import sys
try:
    from jsonschema import validate, ValidationError
    
    with open('$RegistryPath') as f:
        registry = yaml.safe_load(f)
    
    with open('$SchemaPath') as f:
        schema = json.load(f)
    
    validate(instance=registry, schema=schema)
    print("VALID")
    sys.exit(0)
except ValidationError as e:
    print(f"INVALID: {e.message}")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(2)
"@
        
        $tempScript = [System.IO.Path]::GetTempFileName() + ".py"
        $validatorScript | Out-File $tempScript -Encoding UTF8
        
        try {
            $result = python $tempScript 2>&1
            $result -match "VALID"
        } finally {
            Remove-Item $tempScript -ErrorAction SilentlyContinue
        }
    } -SuccessMessage "Schema validation passed" `
      -FailureMessage "Schema validation failed" `
      -Warning
} else {
    Add-Warning "Python not available, skipping schema validation"
}

# Check 4: Pattern entries validation
Write-Section "Validating pattern entries..."

if ($registryContent -and $registryContent.patterns) {
    $patternCount = $registryContent.patterns.Count
    Write-Success "Found $patternCount registered patterns"
    
    foreach ($pattern in $registryContent.patterns) {
        $patternId = $pattern.pattern_id
        
        # Check naming convention
        if ($patternId -match '^PAT-MIGRATED-') {
            # Migrated pattern (PAT-CHECK-002)
            Test-Check -Name "$patternId naming" -Test {
                $patternId -match '^PAT-MIGRATED-[A-Z]+-\d{3}$'
            } -SuccessMessage "$patternId follows migrated naming (PAT-MIGRATED-<CATEGORY>-<SEQ>)" `
              -FailureMessage "$patternId violates migrated naming convention"
            
            # Check required migrated fields
            Test-Check -Name "$patternId metadata" -Test {
                $pattern.migrated_from -eq 'atomic-workflow-system' -and
                $pattern.original_atom_uid
            } -SuccessMessage "$patternId has required migration metadata" `
              -FailureMessage "$patternId missing required migration metadata"
              
        } else {
            # Core pattern (PAT-CHECK-001)
            Test-Check -Name "$patternId naming" -Test {
                $patternId -match '^PAT-[A-Z]+-[A-Z]+-\d{3}$'
            } -SuccessMessage "$patternId follows core naming (PAT-<CATEGORY>-<NAME>-<SEQ>)" `
              -FailureMessage "$patternId violates core naming convention"
        }
        
        # Check file paths exist
        $pathsToCheck = @(
            @{Name = "spec"; Path = $pattern.spec_path},
            @{Name = "schema"; Path = $pattern.schema_path},
            @{Name = "executor"; Path = $pattern.executor_path}
        )
        
        foreach ($pathCheck in $pathsToCheck) {
            if ($pathCheck.Path) {
                Test-Check -Name "$patternId $($pathCheck.Name) file" -Test {
                    Test-Path $pathCheck.Path
                } -SuccessMessage "$patternId $($pathCheck.Name) exists: $($pathCheck.Path)" `
                  -FailureMessage "$patternId $($pathCheck.Name) not found: $($pathCheck.Path)" `
                  -Warning
            }
        }
    }
} else {
    Write-Warning "No patterns registered yet (registry empty)"
}

# Check 5: Directory structure compliance
Write-Section "Checking directory structure (PAT-CHECK-001)..."

$requiredDirs = @(
    "patterns\registry",
    "patterns\specs",
    "patterns\schemas",
    "patterns\executors",
    "patterns\examples",
    "patterns\tests",
    "patterns\verification",
    "patterns\decisions",
    "patterns\self_healing",
    "patterns\legacy_atoms"
)

foreach ($dir in $requiredDirs) {
    Test-Check -Name "Directory $dir" -Test {
        Test-Path $dir
    } -SuccessMessage "Required directory exists: $dir" `
      -FailureMessage "Required directory missing: $dir"
}

# Final report
Write-Section "Validation Summary"

Write-Host "  Total checks: $script:Checks" -ForegroundColor White
Write-Host "  Passed: $script:Passed" -ForegroundColor Green
Write-Host "  Errors: $($script:Errors.Count)" -ForegroundColor $(if ($script:Errors.Count -eq 0) { "Green" } else { "Red" })
Write-Host "  Warnings: $($script:Warnings.Count)" -ForegroundColor $(if ($script:Warnings.Count -eq 0) { "Green" } else { "Yellow" })

if ($script:Errors.Count -gt 0) {
    Write-Host "`n❌ VALIDATION FAILED" -ForegroundColor Red
    Write-Host "`nErrors:" -ForegroundColor Red
    $script:Errors | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    exit 1
}

if ($script:Warnings.Count -gt 0 -and $Strict) {
    Write-Host "`n⚠️  VALIDATION FAILED (Strict Mode)" -ForegroundColor Yellow
    Write-Host "`nWarnings:" -ForegroundColor Yellow
    $script:Warnings | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
    exit 1
}

if ($script:Warnings.Count -gt 0) {
    Write-Host "`n✓ VALIDATION PASSED (with warnings)" -ForegroundColor Yellow
    Write-Host "`nWarnings:" -ForegroundColor Yellow
    $script:Warnings | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
} else {
    Write-Host "`n✅ VALIDATION PASSED" -ForegroundColor Green
}

exit 0
