#!/usr/bin/env pwsh
# DOC_LINK: DOC-PAT-GLOSSARY-SYNC-EXECUTOR-218
<#
.SYNOPSIS
    Executor for glossary_sync pattern (PAT-GLOSSARY-SYNC-001)

.DESCRIPTION
    Syncs glossary with codebase by:
    - Scanning code for term usage
    - Detecting missing terms (referenced but not defined)
    - Finding stale terms (implementation deleted)
    - Suggesting new terms from docstrings
    - Verifying implementation paths exist

.PARAMETER InstancePath
    Path to pattern instance JSON file

.PARAMETER VerboseOutput
    Enable verbose output

.EXAMPLE
    .\glossary_sync_executor.ps1 -InstancePath instance.json

.NOTES
    Pattern: PAT-GLOSSARY-SYNC-001
    Version: 1.0.0
    Requires: PowerShell 7+, Python 3+, ripgrep (rg)
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
function Write-Warning { param([string]$Message) Write-Host "  ⚠ $Message" -ForegroundColor Yellow }

# Result tracking
$result = @{
    status = "success"
    pattern_id = "PAT-GLOSSARY-SYNC-001"
    missing_terms = @()
    stale_terms = @()
    suggested_terms = @()
    invalid_paths = @()
    files_scanned = 0
    execution_duration_seconds = 0
    errors = @()
}

try {
    Write-Host "Glossary Sync Pattern Executor" -ForegroundColor Cyan
    Write-Host "==============================" -ForegroundColor Cyan

    # STEP 1: Load instance
    Write-Step "S1: Loading pattern instance..."
    if (-not (Test-Path $InstancePath)) {
        throw "Instance file not found: $InstancePath"
    }

    $instance = Get-Content $InstancePath -Raw | ConvertFrom-Json
    Write-Success "Loaded instance from $InstancePath"

    # Validate pattern ID
    if ($instance.pattern_id -ne "PAT-GLOSSARY-SYNC-001") {
        throw "Invalid pattern_id: Expected PAT-GLOSSARY-SYNC-001, got $($instance.pattern_id)"
    }
    Write-Success "Pattern ID validated"

    # Extract parameters
    $projectRoot = $instance.inputs.project_root
    $scanPaths = if ($instance.inputs.scan_paths) { $instance.inputs.scan_paths } else { @("core", "engine", "error", "aim", "pm") }
    $excludePatterns = if ($instance.inputs.exclude_patterns) { $instance.inputs.exclude_patterns } else { @("tests/", "__pycache__/", ".venv/", "node_modules/", "*.pyc") }
    $suggestNewTerms = if ($null -ne $instance.inputs.suggest_new_terms) { $instance.inputs.suggest_new_terms } else { $true }
    $checkImplementationPaths = if ($null -ne $instance.inputs.check_implementation_paths) { $instance.inputs.check_implementation_paths } else { $true }

    Write-Info "Project root: $projectRoot"
    Write-Info "Scan paths: $($scanPaths -join ', ')"

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

    # Check for ripgrep
    $rgAvailable = $null -ne (Get-Command rg -ErrorAction SilentlyContinue)
    if (-not $rgAvailable) {
        Write-Warning "ripgrep (rg) not found, using slower grep alternative"
    }

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
    'terms': {
        term_id: {
            'name': term_data.get('name', ''),
            'category': term_data.get('category', ''),
            'implementation': term_data.get('implementation', [])
        }
        for term_id, term_data in terms.items()
    }
}))
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

    # STEP 4: Scan codebase for term references
    Write-Step "S4: Scanning codebase for term usage..."

    Push-Location $projectRoot
    try {
        $fileCount = 0
        $termReferences = @{}

        # Build exclude pattern
        $excludeArgs = @()
        foreach ($pattern in $excludePatterns) {
            $excludeArgs += "--glob"
            $excludeArgs += "!$pattern"
        }

        # Scan each path
        foreach ($scanPath in $scanPaths) {
            if (-not (Test-Path $scanPath)) {
                Write-Warning "Scan path not found: $scanPath"
                continue
            }

            Write-Info "Scanning $scanPath..."

            # Count files
            $files = Get-ChildItem -Path $scanPath -Recurse -File -Include "*.py","*.ps1","*.md","*.yaml","*.json" -ErrorAction SilentlyContinue
            $fileCount += $files.Count

            # Search for each term
            foreach ($termId in $metadata.terms.PSObject.Properties.Name) {
                $termData = $metadata.terms.$termId
                $termName = $termData.name

                if ([string]::IsNullOrWhiteSpace($termName)) { continue }

                # Search for term name in code/docs
                if ($rgAvailable) {
                    $matches = rg -i --no-heading --line-number $termName $scanPath @excludeArgs 2>$null
                } else {
                    $matches = Get-ChildItem -Path $scanPath -Recurse -File -Include "*.py","*.ps1","*.md" -ErrorAction SilentlyContinue |
                        Select-String -Pattern $termName -SimpleMatch |
                        Select-Object -ExpandProperty Path -Unique
                }

                if ($matches) {
                    if (-not $termReferences.ContainsKey($termId)) {
                        $termReferences[$termId] = @()
                    }
                    $termReferences[$termId] += $matches
                }
            }
        }

        $result.files_scanned = $fileCount
        Write-Success "Scanned $fileCount files across $($scanPaths.Count) paths"
        Write-Success "Found references to $($termReferences.Count) terms"
    }
    finally {
        Pop-Location
    }

    # STEP 5: Detect stale terms
    Write-Step "S5: Detecting stale terms..."

    if ($checkImplementationPaths) {
        foreach ($termId in $metadata.terms.PSObject.Properties.Name) {
            $termData = $metadata.terms.$termId
            # Fix: Access implementation.files array, not the implementation dict itself
            $implFiles = if ($termData.implementation -is [hashtable] -or $termData.implementation.files) {
                $termData.implementation.files
            } else {
                $termData.implementation
            }

            if ($implFiles -and $implFiles.Count -gt 0) {
                $allMissing = $true
                foreach ($implFile in $implFiles) {
                    $fullPath = Join-Path $projectRoot $implFile
                    if (Test-Path $fullPath) {
                        $allMissing = $false
                        break
                    }
                }

                # If all implementation files are missing, term might be stale
                if ($allMissing) {
                    # Check if term is still referenced
                    if (-not $termReferences.ContainsKey($termId)) {
                        $result.stale_terms += @{
                            term_id = $termId
                            name = $termData.name
                            reason = "Implementation files missing and no code references found"
                        }
                    } else {
                        $result.invalid_paths += @{
                            term_id = $termId
                            path = $implFiles -join ", "
                        }
                    }
                }
            } else {
                # No implementation files specified, check references
                if (-not $termReferences.ContainsKey($termId)) {
                    $result.stale_terms += @{
                        term_id = $termId
                        name = $termData.name
                        reason = "No implementation files and no code references found"
                    }
                }
            }
        }

        Write-Success "Found $($result.stale_terms.Count) potentially stale terms"
        Write-Success "Found $($result.invalid_paths.Count) terms with invalid paths"
    }

    # STEP 6: Suggest new terms from docstrings
    Write-Step "S6: Analyzing code for new term suggestions..."

    if ($suggestNewTerms) {
        Push-Location $projectRoot
        try {
            # Create Python script to extract potential terms from docstrings
            $extractScript = @"
import os
import re
import ast
import json
from pathlib import Path

def extract_from_docstrings(root_paths, exclude_patterns):
    suggestions = []
    seen = set()

    for root_path in root_paths:
        if not os.path.exists(root_path):
            continue

        for py_file in Path(root_path).rglob('*.py'):
            # Check exclusions
            skip = False
            for pattern in exclude_patterns:
                if pattern.rstrip('/') in str(py_file):
                    skip = True
                    break
            if skip:
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Look for class/function definitions with docstrings
                # Pattern: """Term Name - description"""
                pattern = r'\"\"\"([A-Z][A-Za-z\s]+)\s*[-–]\s*([^\"]{20,200})\"\"\"'
                matches = re.finditer(pattern, content)

                for match in matches:
                    name = match.group(1).strip()
                    definition = match.group(2).strip()

                    # Skip if too generic or already seen
                    if len(name.split()) > 5 or name in seen:
                        continue

                    seen.add(name)
                    suggestions.append({
                        'name': name,
                        'definition': definition,
                        'source_file': str(py_file),
                        'confidence': 0.7
                    })

            except Exception:
                continue

    return suggestions[:10]  # Top 10 suggestions

root_paths = $(($scanPaths | ForEach-Object { "'$_'" }) -join ',')
exclude_patterns = $(($excludePatterns | ForEach-Object { "'$_'" }) -join ',')

suggestions = extract_from_docstrings([$root_paths], [$exclude_patterns])
print(json.dumps(suggestions))
"@

            $extractScript | Set-Content -Path ".tmp-extract.py" -Encoding UTF8
            $suggestionsJson = python ".tmp-extract.py" 2>&1
            Remove-Item ".tmp-extract.py" -ErrorAction SilentlyContinue

            if ($LASTEXITCODE -eq 0 -and $suggestionsJson) {
                $suggestions = $suggestionsJson | ConvertFrom-Json
                $result.suggested_terms = $suggestions
                Write-Success "Found $($suggestions.Count) term suggestions from docstrings"
            } else {
                Write-Info "No new term suggestions found"
            }
        }
        finally {
            Pop-Location
        }
    }

    # STEP 7: Determine status
    Write-Step "S7: Generating sync report..."

    if ($result.stale_terms.Count -gt 0 -or $result.invalid_paths.Count -gt 0) {
        $result.status = "warnings"
    }

    if ($result.errors.Count -gt 0) {
        $result.status = "failure"
    }

    # STEP 8: Save output
    Write-Step "S8: Saving execution output..."

    $result.execution_duration_seconds = ((Get-Date) - $startTime).TotalSeconds

    $outputJsonPath = Join-Path (Split-Path $InstancePath -Parent) "output.json"
    $instance.outputs = $result
    $instance | ConvertTo-Json -Depth 10 | Set-Content $outputJsonPath -Encoding UTF8
    Write-Success "Output saved to $outputJsonPath"

    # STEP 9: Display summary
    Write-Host "`n==============================" -ForegroundColor Cyan
    Write-Host "Sync Report Summary" -ForegroundColor Cyan
    Write-Host "==============================" -ForegroundColor Cyan
    Write-Host "Status:         $($result.status)" -ForegroundColor $(if ($result.status -eq "success") { "Green" } else { "Yellow" })
    Write-Host "Files Scanned:  $($result.files_scanned)"
    Write-Host "Terms in Glossary: $($metadata.term_count)"
    Write-Host "Terms Referenced: $($termReferences.Count)"
    Write-Host ""

    if ($result.stale_terms.Count -gt 0) {
        Write-Host "⚠ Potentially Stale Terms: $($result.stale_terms.Count)" -ForegroundColor Yellow
        foreach ($term in $result.stale_terms | Select-Object -First 5) {
            Write-Host "  - $($term.term_id): $($term.name)" -ForegroundColor Yellow
            Write-Host "    Reason: $($term.reason)" -ForegroundColor Gray
        }
        if ($result.stale_terms.Count -gt 5) {
            Write-Host "  ... and $($result.stale_terms.Count - 5) more" -ForegroundColor Gray
        }
        Write-Host ""
    }

    if ($result.invalid_paths.Count -gt 0) {
        Write-Host "⚠ Invalid Implementation Paths: $($result.invalid_paths.Count)" -ForegroundColor Yellow
        foreach ($item in $result.invalid_paths | Select-Object -First 5) {
            Write-Host "  - $($item.term_id): $($item.path)" -ForegroundColor Yellow
        }
        if ($result.invalid_paths.Count -gt 5) {
            Write-Host "  ... and $($result.invalid_paths.Count - 5) more" -ForegroundColor Gray
        }
        Write-Host ""
    }

    if ($result.suggested_terms.Count -gt 0) {
        Write-Host "💡 Suggested New Terms: $($result.suggested_terms.Count)" -ForegroundColor Green
        foreach ($suggestion in $result.suggested_terms | Select-Object -First 3) {
            Write-Host "  - $($suggestion.name)" -ForegroundColor Green
            Write-Host "    Definition: $($suggestion.definition.Substring(0, [Math]::Min(80, $suggestion.definition.Length)))..." -ForegroundColor Gray
            Write-Host "    Source: $($suggestion.source_file)" -ForegroundColor Gray
        }
        if ($result.suggested_terms.Count -gt 3) {
            Write-Host "  ... and $($result.suggested_terms.Count - 3) more" -ForegroundColor Gray
        }
        Write-Host ""
    }

    Write-Host "Duration: $([math]::Round($result.execution_duration_seconds, 2))s"
    Write-Host "==============================" -ForegroundColor Cyan

    if ($result.status -eq "warnings") {
        Write-Host "`n⚠ Sync completed with warnings. Review the output for details." -ForegroundColor Yellow
        exit 0
    } else {
        Write-Host "`n✓ Sync completed successfully!" -ForegroundColor Green
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
