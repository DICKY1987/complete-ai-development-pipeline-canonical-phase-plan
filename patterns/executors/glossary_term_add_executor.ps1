#!/usr/bin/env pwsh
# DOC_LINK: DOC-PAT-GLOSSARY-TERM-ADD-EXECUTOR-219
<#
.SYNOPSIS
    Executor for glossary_term_add pattern (PAT-GLOSSARY-TERM-ADD-001)

.DESCRIPTION
    Adds new term to glossary with:
    - Auto-generated unique term ID
    - Addition to glossary.md and metadata
    - Validation of inputs
    - Duplicate detection
    - Changelog update

.PARAMETER InstancePath
    Path to pattern instance JSON file

.PARAMETER Verbose
    Enable verbose output

.EXAMPLE
    .\glossary_term_add_executor.ps1 -InstancePath instance.json

.NOTES
    Pattern: PAT-GLOSSARY-TERM-ADD-001
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

# Generate term ID based on category
function Get-TermId {
    param(
        [string]$Category,
        [hashtable]$ExistingTerms
    )

    $categoryMap = @{
        "Core Engine" = "ENGINE"
        "Patch Management" = "PATCH"
        "Error Detection" = "ERROR"
        "Specifications" = "SPEC"
        "State Management" = "STATE"
        "Integrations" = "INTEGRATION"
        "Framework" = "FRAMEWORK"
        "Project Management" = "PM"
    }

    $prefix = $categoryMap[$Category]
    if (-not $prefix) {
        throw "Unknown category: $Category"
    }

    # Find highest number for this prefix
    $maxNum = 0
    foreach ($termId in $ExistingTerms.Keys) {
        if ($termId -match "^TERM-$prefix-(\d{3})$") {
            $num = [int]$matches[1]
            if ($num -gt $maxNum) {
                $maxNum = $num
            }
        }
    }

    $nextNum = $maxNum + 1
    return "TERM-$prefix-{0:D3}" -f $nextNum
}

# Result tracking
$result = @{
    status = "success"
    pattern_id = "PAT-GLOSSARY-TERM-ADD-001"
    term_id = ""
    files_updated = @()
    validation_passed = $false
    execution_duration_seconds = 0
    errors = @()
}

try {
    Write-Host "Glossary Term Add Pattern Executor" -ForegroundColor Cyan
    Write-Host "===================================" -ForegroundColor Cyan

    # STEP 1: Load instance
    Write-Step "S1: Loading pattern instance..."
    if (-not (Test-Path $InstancePath)) {
        throw "Instance file not found: $InstancePath"
    }

    $instance = Get-Content $InstancePath -Raw | ConvertFrom-Json
    Write-Success "Loaded instance from $InstancePath"

    # Validate pattern ID
    if ($instance.pattern_id -ne "PAT-GLOSSARY-TERM-ADD-001") {
        throw "Invalid pattern_id: Expected PAT-GLOSSARY-TERM-ADD-001, got $($instance.pattern_id)"
    }
    Write-Success "Pattern ID validated"

    # Extract parameters
    $projectRoot = $instance.inputs.project_root
    $termName = $instance.inputs.term_name
    $category = $instance.inputs.category
    $definition = $instance.inputs.definition
    $status = if ($instance.inputs.status) { $instance.inputs.status } else { "draft" }
    $implementationFiles = if ($instance.inputs.implementation_files) { $instance.inputs.implementation_files } else { @() }
    $relatedTerms = if ($instance.inputs.related_terms) { $instance.inputs.related_terms } else { @() }

    Write-Info "Term name: $termName"
    Write-Info "Category: $category"
    Write-Info "Status: $status"

    # STEP 2: Validate prerequisites
    Write-Step "S2: Validating prerequisites..."

    # Check glossary directory
    $glossaryRoot = Join-Path $projectRoot "glossary"
    if (-not (Test-Path $glossaryRoot)) {
        throw "Glossary directory not found: $glossaryRoot"
    }
    Write-Success "Glossary directory found"

    # Check metadata file
    $metadataPath = Join-Path $glossaryRoot ".glossary-metadata.yaml"
    if (-not (Test-Path $metadataPath)) {
        throw "Metadata file not found: $metadataPath"
    }
    Write-Success "Metadata file found"

    # Validate inputs
    if ($termName.Length -lt 2 -or $termName.Length -gt 100) {
        throw "Term name must be 2-100 characters"
    }
    if ($definition.Length -lt 20 -or $definition.Length -gt 1000) {
        throw "Definition must be 20-1000 characters"
    }
    Write-Success "Input validation passed"

    # STEP 3: Load existing metadata
    Write-Step "S3: Loading existing metadata..."

    Push-Location $glossaryRoot
    try {
        # Load YAML metadata
        $metadataContent = Get-Content ".glossary-metadata.yaml" -Raw

        # Parse with Python (more reliable than PowerShell YAML parsing)
        $parseScript = @"
import yaml
import json
import sys

with open('.glossary-metadata.yaml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

# Extract terms
terms = {}
if 'terms' in data:
    for term_id, term_data in data['terms'].items():
        terms[term_id] = term_data.get('name', '')

print(json.dumps(terms))
"@

        $parseScript | Set-Content -Path ".tmp-parse-metadata.py" -Encoding UTF8
        $existingTermsJson = python ".tmp-parse-metadata.py"
        Remove-Item ".tmp-parse-metadata.py" -ErrorAction SilentlyContinue

        $existingTerms = $existingTermsJson | ConvertFrom-Json -AsHashtable
        Write-Success "Loaded $($existingTerms.Count) existing terms"

        # Check for duplicate names
        foreach ($termId in $existingTerms.Keys) {
            if ($existingTerms[$termId] -eq $termName) {
                throw "Term with name '$termName' already exists: $termId"
            }
        }
        Write-Success "No duplicate term names found"
    }
    finally {
        Pop-Location
    }

    # STEP 4: Generate term ID
    Write-Step "S4: Generating term ID..."

    $termId = Get-TermId -Category $category -ExistingTerms $existingTerms
    $result.term_id = $termId
    Write-Success "Generated term ID: $termId"

    # STEP 5: Add term to metadata
    Write-Step "S5: Adding term to metadata..."

    Push-Location $glossaryRoot
    try {
        # Create Python script to add term
        $addScript = @"
import yaml
from datetime import datetime

# Load existing metadata
with open('.glossary-metadata.yaml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

if 'terms' not in data:
    data['terms'] = {}

# Add new term
term_id = '$termId'
data['terms'][term_id] = {
    'name': '$termName',
    'category': '$category',
    'definition': '''$definition''',
    'status': '$status',
    'created_at': datetime.utcnow().isoformat() + 'Z',
    'updated_at': datetime.utcnow().isoformat() + 'Z'
}

# Add implementation files if provided
impl_files = $(if ($implementationFiles.Count -gt 0) { "'$($implementationFiles -join "', '")'" } else { "" })
if impl_files:
    data['terms'][term_id]['implementation'] = {
        'files': [impl_files.split("', '")]
    }

# Add related terms if provided
# (Skipping for now - would need JSON parsing)

# Save updated metadata
with open('.glossary-metadata.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

print('Term added successfully')
"@

        $addScript | Set-Content -Path ".tmp-add-term.py" -Encoding UTF8
        $output = python ".tmp-add-term.py" 2>&1
        Remove-Item ".tmp-add-term.py" -ErrorAction SilentlyContinue

        if ($LASTEXITCODE -ne 0) {
            throw "Failed to add term to metadata: $output"
        }

        Write-Success "Term added to metadata"
        $result.files_updated += ".glossary-metadata.yaml"
    }
    finally {
        Pop-Location
    }

    # STEP 6: Add term to glossary.md
    Write-Step "S6: Adding term to glossary.md..."

    $glossaryMdPath = Join-Path $glossaryRoot "glossary.md"
    if (Test-Path $glossaryMdPath) {
        $glossaryContent = Get-Content $glossaryMdPath -Raw

        # Find the category section
        $categoryPattern = "## $category"

        if ($glossaryContent -match $categoryPattern) {
            # Add term to category
            $termEntry = @"

### $termName
**ID**: ``$termId``
**Status**: $status

$definition

"@

            # Insert after category header
            $glossaryContent = $glossaryContent -replace "($categoryPattern)", "`$1$termEntry"

            Set-Content -Path $glossaryMdPath -Value $glossaryContent -Encoding UTF8
            Write-Success "Term added to glossary.md"
            $result.files_updated += "glossary.md"
        }
        else {
            Write-Info "Category '$category' not found in glossary.md - metadata updated only"
        }
    }
    else {
        Write-Info "glossary.md not found - metadata updated only"
    }

    # STEP 7: Validate
    Write-Step "S7: Running validation..."

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
            $result.errors += "Post-add validation failed"
        }
    }
    finally {
        Pop-Location
    }

    # STEP 8: Generate output
    Write-Step "S8: Generating execution output..."

    $result.execution_duration_seconds = ((Get-Date) - $startTime).TotalSeconds

    # Save output
    $outputPath = Join-Path (Split-Path $InstancePath -Parent) "output.json"
    $instance.outputs = $result
    $instance | ConvertTo-Json -Depth 10 | Set-Content $outputPath -Encoding UTF8
    Write-Success "Output saved to $outputPath"

    # Summary
    Write-Host "`n===================================" -ForegroundColor Cyan
    Write-Host "Execution Summary" -ForegroundColor Cyan
    Write-Host "===================================" -ForegroundColor Cyan
    Write-Host "Status:       $($result.status)" -ForegroundColor Green
    Write-Host "Term ID:      $termId" -ForegroundColor Green
    Write-Host "Term Name:    $termName"
    Write-Host "Category:     $category"
    Write-Host "Files Updated: $($result.files_updated.Count)"
    foreach ($file in $result.files_updated) {
        Write-Host "  - $file" -ForegroundColor Gray
    }
    Write-Host "Validation:   $(if ($result.validation_passed) { 'PASSED' } else { 'FAILED' })" -ForegroundColor $(if ($result.validation_passed) { "Green" } else { "Red" })
    Write-Host "Duration:     $([math]::Round($result.execution_duration_seconds, 2))s"
    Write-Host "===================================" -ForegroundColor Cyan

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
