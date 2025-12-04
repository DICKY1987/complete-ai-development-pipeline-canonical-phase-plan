#!/usr/bin/env pwsh
# DOC_LINK: DOC-PAT-GLOSSARY-EXPORT-EXECUTOR-215
<#
.SYNOPSIS
    Executor for glossary_export pattern (PAT-GLOSSARY-EXPORT-001)

.DESCRIPTION
    Exports glossary to various formats:
    - JSON (for APIs and programmatic access)
    - Markdown (for documentation sites)
    - CSV (for spreadsheets)
    - HTML (for web viewing)
    - YAML (for configuration)

.PARAMETER InstancePath
    Path to pattern instance JSON file

.PARAMETER Verbose
    Enable verbose output

.EXAMPLE
    .\glossary_export_executor.ps1 -InstancePath instance.json

.NOTES
    Pattern: PAT-GLOSSARY-EXPORT-001
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
    pattern_id = "PAT-GLOSSARY-EXPORT-001"
    output_file = ""
    terms_exported = 0
    file_size_bytes = 0
    execution_duration_seconds = 0
    errors = @()
}

try {
    Write-Host "Glossary Export Pattern Executor" -ForegroundColor Cyan
    Write-Host "=================================" -ForegroundColor Cyan

    # STEP 1: Load instance
    Write-Step "S1: Loading pattern instance..."
    if (-not (Test-Path $InstancePath)) {
        throw "Instance file not found: $InstancePath"
    }

    $instance = Get-Content $InstancePath -Raw | ConvertFrom-Json
    Write-Success "Loaded instance from $InstancePath"

    # Validate pattern ID
    if ($instance.pattern_id -ne "PAT-GLOSSARY-EXPORT-001") {
        throw "Invalid pattern_id: Expected PAT-GLOSSARY-EXPORT-001, got $($instance.pattern_id)"
    }
    Write-Success "Pattern ID validated"

    # Extract parameters
    $projectRoot = $instance.inputs.project_root
    $outputFormat = $instance.inputs.output_format
    $outputPath = $instance.inputs.output_path
    $includeMetadata = if ($null -ne $instance.inputs.include_metadata) { $instance.inputs.include_metadata } else { $true }
    $filterByCategory = if ($instance.inputs.filter_by_category) { $instance.inputs.filter_by_category } else { @() }
    $filterByStatus = if ($instance.inputs.filter_by_status) { $instance.inputs.filter_by_status } else { @() }

    Write-Info "Output format: $outputFormat"
    Write-Info "Output path: $outputPath"

    # STEP 2: Validate prerequisites
    Write-Step "S2: Validating prerequisites..."

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

    # STEP 3: Load and filter glossary data
    Write-Step "S3: Loading glossary data..."

    Push-Location $glossaryRoot
    try {
        # Create Python export script
        $exportScript = @"
import yaml
import json
import csv
from datetime import datetime

# Load metadata
with open('.glossary-metadata.yaml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

terms = data.get('terms', {})
output_format = '$outputFormat'
output_path = '$outputPath'
include_metadata = $includeMetadata
filter_categories = $(if ($filterByCategory.Count -gt 0) { "['$($filterByCategory -join "','")']" } else { "[]" })
filter_statuses = $(if ($filterByStatus.Count -gt 0) { "['$($filterByStatus -join "','")']" } else { "[]" })

# Filter terms
filtered_terms = {}
for term_id, term_data in terms.items():
    # Category filter
    if filter_categories and term_data.get('category') not in filter_categories:
        continue
    # Status filter
    if filter_statuses and term_data.get('status') not in filter_statuses:
        continue
    filtered_terms[term_id] = term_data

print(f'Filtered to {len(filtered_terms)} terms')

# Export based on format
if output_format == 'json':
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(filtered_terms, f, indent=2, ensure_ascii=False)

elif output_format == 'yaml':
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(filtered_terms, f, default_flow_style=False, allow_unicode=True)

elif output_format == 'csv':
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Term ID', 'Name', 'Category', 'Definition', 'Status'])
        for term_id, term_data in filtered_terms.items():
            writer.writerow([
                term_id,
                term_data.get('name', ''),
                term_data.get('category', ''),
                term_data.get('definition', ''),
                term_data.get('status', '')
            ])

elif output_format == 'markdown':
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('# Glossary\\n\\n')
        f.write(f'**Generated**: {datetime.utcnow().isoformat()}Z\\n\\n')
        f.write(f'**Total Terms**: {len(filtered_terms)}\\n\\n')

        # Group by category
        by_category = {}
        for term_id, term_data in filtered_terms.items():
            cat = term_data.get('category', 'Uncategorized')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append((term_id, term_data))

        # Write each category
        for category in sorted(by_category.keys()):
            f.write(f'## {category}\\n\\n')
            for term_id, term_data in sorted(by_category[category], key=lambda x: x[1].get('name', '')):
                f.write(f'### {term_data.get("name", "Unknown")}\\n')
                f.write(f'**ID**: ``{term_id}``  \\n')
                f.write(f'**Status**: {term_data.get("status", "unknown")}\\n\\n')
                f.write(f'{term_data.get("definition", "No definition provided.")}\\n\\n')

elif output_format == 'html':
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE html>\\n<html>\\n<head>\\n')
        f.write('<meta charset="UTF-8">\\n')
        f.write('<title>Glossary</title>\\n')
        f.write('<style>\\n')
        f.write('body { font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; }\\n')
        f.write('h1 { color: #333; border-bottom: 3px solid #007acc; padding-bottom: 10px; }\\n')
        f.write('h2 { color: #007acc; margin-top: 30px; }\\n')
        f.write('h3 { color: #555; }\\n')
        f.write('.term { margin-bottom: 20px; padding: 15px; background: #f9f9f9; border-left: 4px solid #007acc; }\\n')
        f.write('.term-id { font-family: monospace; background: #e0e0e0; padding: 2px 6px; border-radius: 3px; }\\n')
        f.write('.status { display: inline-block; padding: 2px 8px; border-radius: 3px; font-size: 0.9em; }\\n')
        f.write('.status-active { background: #4caf50; color: white; }\\n')
        f.write('.status-draft { background: #ff9800; color: white; }\\n')
        f.write('</style>\\n</head>\\n<body>\\n')
        f.write('<h1>Glossary</h1>\\n')
        f.write(f'<p><strong>Generated</strong>: {datetime.utcnow().isoformat()}Z</p>\\n')
        f.write(f'<p><strong>Total Terms</strong>: {len(filtered_terms)}</p>\\n')

        # Group by category
        by_category = {}
        for term_id, term_data in filtered_terms.items():
            cat = term_data.get('category', 'Uncategorized')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append((term_id, term_data))

        # Write each category
        for category in sorted(by_category.keys()):
            f.write(f'<h2>{category}</h2>\\n')
            for term_id, term_data in sorted(by_category[category], key=lambda x: x[1].get('name', '')):
                status = term_data.get('status', 'unknown')
                f.write(f'<div class="term">\\n')
                f.write(f'<h3>{term_data.get("name", "Unknown")}</h3>\\n')
                f.write(f'<p><strong>ID</strong>: <span class="term-id">{term_id}</span> ')
                f.write(f'<span class="status status-{status}">{status}</span></p>\\n')
                f.write(f'<p>{term_data.get("definition", "No definition provided.")}</p>\\n')
                f.write(f'</div>\\n')

        f.write('</body>\\n</html>\\n')

print(f'Exported {len(filtered_terms)} terms to {output_path}')
"@

        $exportScript | Set-Content -Path ".tmp-export.py" -Encoding UTF8
        $output = python ".tmp-export.py" 2>&1
        Remove-Item ".tmp-export.py" -ErrorAction SilentlyContinue

        if ($LASTEXITCODE -ne 0) {
            throw "Export failed: $output"
        }

        # Parse output for term count
        if ($output -match 'Exported (\d+) terms') {
            $result.terms_exported = [int]$matches[1]
        }

        Write-Success "Export completed: $output"
    }
    finally {
        Pop-Location
    }

    # STEP 4: Get file size
    Write-Step "S4: Verifying output file..."

    $fullOutputPath = if ([System.IO.Path]::IsPathRooted($outputPath)) {
        $outputPath
    } else {
        Join-Path $glossaryRoot $outputPath
    }

    if (Test-Path $fullOutputPath) {
        $fileInfo = Get-Item $fullOutputPath
        $result.output_file = $fullOutputPath
        $result.file_size_bytes = $fileInfo.Length
        Write-Success "Output file: $fullOutputPath ($($fileInfo.Length) bytes)"
    }
    else {
        throw "Output file not found: $fullOutputPath"
    }

    # STEP 5: Generate output
    Write-Step "S5: Generating execution output..."

    $result.execution_duration_seconds = ((Get-Date) - $startTime).TotalSeconds

    # Save output
    $outputJsonPath = Join-Path (Split-Path $InstancePath -Parent) "output.json"
    $instance.outputs = $result
    $instance | ConvertTo-Json -Depth 10 | Set-Content $outputJsonPath -Encoding UTF8
    Write-Success "Output saved to $outputJsonPath"

    # Summary
    Write-Host "`n=================================" -ForegroundColor Cyan
    Write-Host "Export Summary" -ForegroundColor Cyan
    Write-Host "=================================" -ForegroundColor Cyan
    Write-Host "Status:         $($result.status)" -ForegroundColor Green
    Write-Host "Format:         $outputFormat"
    Write-Host "Terms Exported: $($result.terms_exported)"
    Write-Host "Output File:    $($result.output_file)"
    Write-Host "File Size:      $($result.file_size_bytes) bytes"
    Write-Host "Duration:       $([math]::Round($result.execution_duration_seconds, 2))s"
    Write-Host "=================================" -ForegroundColor Cyan

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
