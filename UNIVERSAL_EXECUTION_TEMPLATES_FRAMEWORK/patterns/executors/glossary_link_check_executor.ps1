#!/usr/bin/env pwsh
# DOC_LINK: DOC-PAT-GLOSSARY-LINK-CHECK-EXECUTOR-216
<#
.SYNOPSIS
    Executor for glossary_link_check pattern (PAT-GLOSSARY-LINK-CHECK-001)
    
.DESCRIPTION
    Validates cross-references and links in glossary:
    - Check term_id cross-references
    - Verify implementation file paths exist
    - Validate schema file references
    - Check related term links
    - Find broken links
    
.PARAMETER InstancePath
    Path to pattern instance JSON file
    
.PARAMETER VerboseOutput
    Enable verbose output
    
.EXAMPLE
    .\glossary_link_check_executor.ps1 -InstancePath instance.json
    
.NOTES
    Pattern: PAT-GLOSSARY-LINK-CHECK-001
    Version: 1.0.0
    Requires: PowerShell 7+, Python 3+
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
    pattern_id = "PAT-GLOSSARY-LINK-CHECK-001"
    total_links_checked = 0
    broken_links = @()
    warnings = @()
    execution_duration_seconds = 0
    errors = @()
}

try {
    Write-Host "Glossary Link Check Pattern Executor" -ForegroundColor Cyan
    Write-Host "====================================" -ForegroundColor Cyan
    
    # STEP 1: Load instance
    Write-Step "S1: Loading pattern instance..."
    if (-not (Test-Path $InstancePath)) {
        throw "Instance file not found: $InstancePath"
    }
    
    $instance = Get-Content $InstancePath -Raw | ConvertFrom-Json
    Write-Success "Loaded instance from $InstancePath"
    
    # Validate pattern ID
    if ($instance.pattern_id -ne "PAT-GLOSSARY-LINK-CHECK-001") {
        throw "Invalid pattern_id: Expected PAT-GLOSSARY-LINK-CHECK-001, got $($instance.pattern_id)"
    }
    Write-Success "Pattern ID validated"
    
    # Extract parameters
    $projectRoot = $instance.inputs.project_root
    $checkTermRefs = if ($null -ne $instance.inputs.check_term_references) { $instance.inputs.check_term_references } else { $true }
    $checkFilePaths = if ($null -ne $instance.inputs.check_file_paths) { $instance.inputs.check_file_paths } else { $true }
    $checkSchemaRefs = if ($null -ne $instance.inputs.check_schema_refs) { $instance.inputs.check_schema_refs } else { $true }
    $checkRelatedTerms = if ($null -ne $instance.inputs.check_related_terms) { $instance.inputs.check_related_terms } else { $true }
    $failOnBrokenLinks = if ($null -ne $instance.inputs.fail_on_broken_links) { $instance.inputs.fail_on_broken_links } else { $false }
    
    Write-Info "Project root: $projectRoot"
    Write-Info "Check term references: $checkTermRefs"
    Write-Info "Check file paths: $checkFilePaths"
    Write-Info "Check schema refs: $checkSchemaRefs"
    Write-Info "Check related terms: $checkRelatedTerms"
    
    # STEP 2: Validate prerequisites
    Write-Step "S2: Validating prerequisites..."
    
    if (-not (Test-Path $projectRoot)) {
        throw "Project root not found: $projectRoot"
    }
    Write-Success "Project root found"
    
    $glossaryRoot = Join-Path $projectRoot "glossary"
    if (-not (Test-Path $glossaryRoot)) {
        throw "Glossary directory not found: $glossaryRoot"
    }
    Write-Success "Glossary directory found"
    
    $metadataPath = Join-Path $glossaryRoot ".glossary-metadata.yaml"
    if (-not (Test-Path $metadataPath)) {
        throw "Metadata file not found: $metadataPath"
    }
    Write-Success "Metadata file found"
    
    # STEP 3: Load glossary metadata
    Write-Step "S3: Loading glossary metadata..."
    
    Push-Location $glossaryRoot
    try {
        # Load metadata using Python
        $loadScript = @"
import yaml
import json

with open('.glossary-metadata.yaml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

terms = data.get('terms', {})
print(json.dumps({
    'term_count': len(terms),
    'terms': terms
}, default=str))
"@
        
        $loadScript | Set-Content -Path ".tmp-load.py" -Encoding UTF8
        $metadataJson = python ".tmp-load.py" 2>&1
        Remove-Item ".tmp-load.py" -ErrorAction SilentlyContinue
        
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to load metadata: $metadataJson"
        }
        
        $metadata = $metadataJson | ConvertFrom-Json
        Write-Success "Loaded $($metadata.term_count) terms from metadata"
    }
    finally {
        Pop-Location
    }
    
    # STEP 4: Check term ID cross-references
    if ($checkTermRefs) {
        Write-Step "S4: Checking term ID cross-references..."
        
        $termIds = $metadata.terms.PSObject.Properties.Name
        $linksChecked = 0
        
        foreach ($termId in $termIds) {
            $termData = $metadata.terms.$termId
            
            # Check if term_id follows pattern
            if ($termId -notmatch '^TERM-[A-Z]+-\d{3}$') {
                $result.warnings += "Term ID '$termId' does not follow standard pattern TERM-XXX-NNN"
            }
            $linksChecked++
        }
        
        $result.total_links_checked += $linksChecked
        Write-Success "Checked $linksChecked term IDs"
    }
    
    # STEP 5: Check implementation file paths
    if ($checkFilePaths) {
        Write-Step "S5: Checking implementation file paths..."
        
        $pathsChecked = 0
        
        foreach ($termId in $metadata.terms.PSObject.Properties.Name) {
            $termData = $metadata.terms.$termId
            $implFiles = $termData.implementation
            
            if ($implFiles) {
                foreach ($implFile in $implFiles) {
                    $pathsChecked++
                    $fullPath = Join-Path $projectRoot $implFile
                    
                    if (-not (Test-Path $fullPath)) {
                        $result.broken_links += @{
                            term_id = $termId
                            link_type = "implementation_file"
                            target = $implFile
                            error = "File not found: $fullPath"
                        }
                    }
                }
            }
        }
        
        $result.total_links_checked += $pathsChecked
        Write-Success "Checked $pathsChecked implementation file paths"
    }
    
    # STEP 6: Check schema references
    if ($checkSchemaRefs) {
        Write-Step "S6: Checking schema references..."
        
        $schemaRefsChecked = 0
        
        foreach ($termId in $metadata.terms.PSObject.Properties.Name) {
            $termData = $metadata.terms.$termId
            $schemaRefs = $termData.schema_refs
            
            if ($schemaRefs) {
                foreach ($schemaRef in $schemaRefs) {
                    $schemaRefsChecked++
                    $fullPath = Join-Path $projectRoot $schemaRef
                    
                    if (-not (Test-Path $fullPath)) {
                        $result.broken_links += @{
                            term_id = $termId
                            link_type = "schema_reference"
                            target = $schemaRef
                            error = "Schema file not found: $fullPath"
                        }
                    }
                }
            }
        }
        
        $result.total_links_checked += $schemaRefsChecked
        Write-Success "Checked $schemaRefsChecked schema references"
    }
    
    # STEP 7: Check related terms
    if ($checkRelatedTerms) {
        Write-Step "S7: Checking related term links..."
        
        $relatedTermsChecked = 0
        $validTermIds = $metadata.terms.PSObject.Properties.Name
        
        foreach ($termId in $validTermIds) {
            $termData = $metadata.terms.$termId
            $relatedTerms = $termData.related_terms
            
            if ($relatedTerms) {
                foreach ($relatedTermId in $relatedTerms) {
                    $relatedTermsChecked++
                    
                    if ($relatedTermId -notin $validTermIds) {
                        $result.broken_links += @{
                            term_id = $termId
                            link_type = "related_term"
                            target = $relatedTermId
                            error = "Related term not found in glossary"
                        }
                    }
                }
            }
        }
        
        $result.total_links_checked += $relatedTermsChecked
        Write-Success "Checked $relatedTermsChecked related term links"
    }
    
    # STEP 8: Check for orphaned terms
    Write-Step "S8: Checking for orphaned terms..."
    
    $orphanCount = 0
    $validTermIds = $metadata.terms.PSObject.Properties.Name
    
    foreach ($termId in $validTermIds) {
        $termData = $metadata.terms.$termId
        $relatedTerms = if ($termData.related_terms) { $termData.related_terms } else { @() }
        
        # Check if term has no related terms and is not referenced by others
        $isReferenced = $false
        foreach ($otherTermId in $validTermIds) {
            if ($otherTermId -eq $termId) { continue }
            $otherTermData = $metadata.terms.$otherTermId
            $otherRelatedTerms = if ($otherTermData.related_terms) { $otherTermData.related_terms } else { @() }
            
            if ($termId -in $otherRelatedTerms) {
                $isReferenced = $true
                break
            }
        }
        
        if ($relatedTerms.Count -eq 0 -and -not $isReferenced) {
            $orphanCount++
            $result.warnings += "Term '$termId' ($($termData.name)) has no related terms and is not referenced by other terms"
        }
    }
    
    if ($orphanCount -gt 0) {
        Write-Info "Found $orphanCount orphaned terms"
    } else {
        Write-Success "No orphaned terms found"
    }
    
    # STEP 9: Determine final status
    Write-Step "S9: Generating link check report..."
    
    if ($result.broken_links.Count -gt 0) {
        if ($failOnBrokenLinks) {
            $result.status = "failure"
        } else {
            $result.status = "warnings"
        }
    }
    
    if ($result.warnings.Count -gt 0 -and $result.status -eq "success") {
        $result.status = "warnings"
    }
    
    # STEP 10: Save output
    Write-Step "S10: Saving execution output..."
    
    $result.execution_duration_seconds = ((Get-Date) - $startTime).TotalSeconds
    
    $outputJsonPath = Join-Path (Split-Path $InstancePath -Parent) "output.json"
    $instance.outputs = $result
    $instance | ConvertTo-Json -Depth 10 | Set-Content $outputJsonPath -Encoding UTF8
    Write-Success "Output saved to $outputJsonPath"
    
    # STEP 11: Display summary
    Write-Host "`n====================================" -ForegroundColor Cyan
    Write-Host "Link Check Report Summary" -ForegroundColor Cyan
    Write-Host "====================================" -ForegroundColor Cyan
    Write-Host "Status:            $($result.status)" -ForegroundColor $(
        switch ($result.status) {
            "success" { "Green" }
            "warnings" { "Yellow" }
            "failure" { "Red" }
        }
    )
    Write-Host "Total Links Checked: $($result.total_links_checked)"
    Write-Host "Broken Links:        $($result.broken_links.Count)" -ForegroundColor $(if ($result.broken_links.Count -gt 0) { "Red" } else { "Green" })
    Write-Host "Warnings:            $($result.warnings.Count)" -ForegroundColor $(if ($result.warnings.Count -gt 0) { "Yellow" } else { "Green" })
    Write-Host ""
    
    if ($result.broken_links.Count -gt 0) {
        Write-Host "❌ Broken Links Found: $($result.broken_links.Count)" -ForegroundColor Red
        foreach ($link in $result.broken_links | Select-Object -First 10) {
            Write-Host "  - [$($link.term_id)] $($link.link_type): $($link.target)" -ForegroundColor Red
            Write-Host "    Error: $($link.error)" -ForegroundColor Gray
        }
        if ($result.broken_links.Count -gt 10) {
            Write-Host "  ... and $($result.broken_links.Count - 10) more broken links" -ForegroundColor Gray
        }
        Write-Host ""
    }
    
    if ($result.warnings.Count -gt 0) {
        Write-Host "⚠ Warnings: $($result.warnings.Count)" -ForegroundColor Yellow
        foreach ($warning in $result.warnings | Select-Object -First 5) {
            Write-Host "  - $warning" -ForegroundColor Yellow
        }
        if ($result.warnings.Count -gt 5) {
            Write-Host "  ... and $($result.warnings.Count - 5) more warnings" -ForegroundColor Gray
        }
        Write-Host ""
    }
    
    Write-Host "Duration: $([math]::Round($result.execution_duration_seconds, 2))s"
    Write-Host "====================================" -ForegroundColor Cyan
    
    if ($result.status -eq "failure") {
        Write-Host "`n✗ Link check failed. Found $($result.broken_links.Count) broken links." -ForegroundColor Red
        exit 1
    }
    elseif ($result.status -eq "warnings") {
        Write-Host "`n⚠ Link check completed with warnings." -ForegroundColor Yellow
        exit 0
    }
    else {
        Write-Host "`n✓ All links validated successfully!" -ForegroundColor Green
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
