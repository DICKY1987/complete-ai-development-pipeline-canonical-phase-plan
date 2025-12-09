#!/usr/bin/env pwsh
# DOC_ID: DOC-PAT-AUTOMATION-REGISTER-PATTERN-BATCH-001
<#
.SYNOPSIS
    Batch pattern registration pipeline

.DESCRIPTION
    Implements GAP-PATREG-001: Batch registration workflow
    7-phase pipeline for registering 6+ patterns at once:
    1. Scan source directory
    2. Categorize patterns
    3. Generate pattern IDs
    4. Create specs from templates
    5. Create schemas from templates
    6. Create executors from templates
    7. Update registry and validate

.PARAMETER SourceDir
    Directory containing source pattern files

.PARAMETER TargetDir
    Target patterns directory (default: patterns)

.PARAMETER CategoryDefault
    Default category if not detected (default: behavioral)

.PARAMETER BatchSize
    Number of patterns to process in parallel (default: 6)

.PARAMETER Verify
    Run validation after registration (default: true)

.PARAMETER DryRun
    Show what would be done without executing

.EXAMPLE
    .\register_pattern_batch.ps1 -SourceDir ".\new_patterns" -Verify

.NOTES
    Pattern: EXEC-009 (Meta-Execution) + EXEC-HYBRID-010
    Version: 1.0.0
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$SourceDir,

    [Parameter(Mandatory=$false)]
    [string]$TargetDir = "patterns",

    [Parameter(Mandatory=$false)]
    [ValidateSet("EXEC", "BEHAVE", "ANTI", "DOC", "META", "MODULE")]
    [string]$CategoryDefault = "BEHAVE",

    [Parameter(Mandatory=$false)]
    [int]$BatchSize = 6,

    [Parameter(Mandatory=$false)]
    [switch]$Verify = $true,

    [Parameter(Mandatory=$false)]
    [switch]$DryRun = $false
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptPath = $PSScriptRoot
$patternsDir = Split-Path $scriptPath -Parent | Split-Path -Parent
$helpersDir = Join-Path $scriptPath "helpers"
$templatesDir = Join-Path $patternsDir "templates"

# Import helper scripts
. "$helpersDir\Get-NextPatternID.ps1"
. "$helpersDir\Add-PatternToRegistry.ps1"

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  BATCH PATTERN REGISTRATION PIPELINE" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Source: $SourceDir" -ForegroundColor Gray
Write-Host "  Target: $TargetDir" -ForegroundColor Gray
Write-Host "  Batch Size: $BatchSize" -ForegroundColor Gray
Write-Host "  Default Category: $CategoryDefault" -ForegroundColor Gray
Write-Host "  Dry Run: $DryRun" -ForegroundColor Gray
Write-Host ""

# Phase 1: Scan source directory
Write-Host "Phase 1/7: Scanning source directory..." -ForegroundColor Cyan
$sourcePatterns = @()
Get-ChildItem $SourceDir -File -Recurse | ForEach-Object {
    $sourcePatterns += @{
        SourceFile = $_.FullName
        Name = $_.BaseName
        Extension = $_.Extension
    }
}
Write-Host "  Found $($sourcePatterns.Count) source files" -ForegroundColor Green

# Phase 2: Categorize patterns
Write-Host ""
Write-Host "Phase 2/7: Categorizing patterns..." -ForegroundColor Cyan
foreach ($pattern in $sourcePatterns) {
    # Try to detect category from content or filename
    $content = Get-Content $pattern.SourceFile -Raw -ErrorAction SilentlyContinue

    if ($content -match 'category:\s*(EXEC|BEHAVE|ANTI|DOC|META|MODULE)') {
        $pattern.Category = $matches[1]
    } elseif ($pattern.Name -match '^(EXEC|BEHAVE|ANTI|DOC|META|MODULE)') {
        $pattern.Category = $matches[1]
    } else {
        $pattern.Category = $CategoryDefault
    }

    Write-Host "  $($pattern.Name) -> $($pattern.Category)" -ForegroundColor Gray
}

# Phase 3: Generate pattern IDs
Write-Host ""
Write-Host "Phase 3/7: Generating pattern IDs..." -ForegroundColor Cyan
foreach ($pattern in $sourcePatterns) {
    $patternName = $pattern.Name -replace '[^a-zA-Z0-9\-]', '-'
    $idInfo = & "$helpersDir\Get-NextPatternID.ps1" -Category $pattern.Category -Name $patternName

    $pattern.PatternID = $idInfo.pattern_id
    $pattern.DocID = $idInfo.doc_id
    $pattern.FileSystemName = $idInfo.file_system_name
    $pattern.SpecPath = $idInfo.spec_path
    $pattern.SchemaPath = $idInfo.schema_path
    $pattern.ExecutorPath = $idInfo.executor_path
    $pattern.TestPath = $idInfo.test_path
    $pattern.ExampleDir = $idInfo.example_dir

    Write-Host "  $($pattern.Name) -> $($pattern.PatternID)" -ForegroundColor Gray
}

# Phase 4-6: Generate artifacts in batches
Write-Host ""
Write-Host "Phase 4-6/7: Generating artifacts (batches of $BatchSize)..." -ForegroundColor Cyan

$batches = [Math]::Ceiling($sourcePatterns.Count / $BatchSize)
for ($batchNum = 0; $batchNum -lt $batches; $batchNum++) {
    $start = $batchNum * $BatchSize
    $end = [Math]::Min(($batchNum + 1) * $BatchSize - 1, $sourcePatterns.Count - 1)
    $batch = $sourcePatterns[$start..$end]

    Write-Host "  Processing batch $($batchNum + 1)/$batches ($($batch.Count) patterns)..." -ForegroundColor Yellow

    foreach ($pattern in $batch) {
        $patternName = $pattern.FileSystemName

        # Load templates
        $specTemplate = Get-Content "$templatesDir\pattern-spec.yaml" -Raw
        $schemaTemplate = Get-Content "$templatesDir\pattern-schema.json" -Raw
        $executorTemplate = Get-Content "$templatesDir\pattern-executor.ps1" -Raw

        # Replace placeholders
        $spec = $specTemplate -replace '\{PATTERN_ID\}', $pattern.PatternID
        $spec = $spec -replace '\{DOC_ID\}', $pattern.DocID
        $spec = $spec -replace '\{PATTERN_NAME\}', $patternName
        $spec = $spec -replace '\{CATEGORY\}', $pattern.Category
        $spec = $spec -replace '\{CREATED_DATE\}', (Get-Date -Format 'yyyy-MM-dd')
        $spec = $spec -replace '\{DESCRIPTION\}', "Pattern description for $patternName"
        $spec = $spec -replace '\{TIME_SAVINGS\}', '25'

        $schema = $schemaTemplate -replace '\{PATTERN_ID\}', $pattern.PatternID
        $schema = $schema -replace '\{PATTERN_NAME\}', $patternName
        $schema = $schema -replace '\{DESCRIPTION\}', "Schema for $patternName"

        $executor = $executorTemplate -replace '\{PATTERN_ID\}', $pattern.PatternID
        $executor = $executor -replace '\{DOC_ID\}', $pattern.DocID
        $executor = $executor -replace '\{PATTERN_NAME\}', $patternName
        $executor = $executor -replace '\{DESCRIPTION\}', "Executor for $patternName"
        $executor = $executor -replace '\{CREATED_DATE\}', (Get-Date -Format 'yyyy-MM-dd')

        if (-not $DryRun) {
            # Create spec
            $specFullPath = Join-Path (Split-Path $patternsDir -Parent) $pattern.SpecPath
            New-Item -Path (Split-Path $specFullPath -Parent) -ItemType Directory -Force | Out-Null
            Set-Content -Path $specFullPath -Value $spec

            # Create schema
            $schemaFullPath = Join-Path (Split-Path $patternsDir -Parent) $pattern.SchemaPath
            New-Item -Path (Split-Path $schemaFullPath -Parent) -ItemType Directory -Force | Out-Null
            Set-Content -Path $schemaFullPath -Value $schema

            # Create executor
            $executorFullPath = Join-Path (Split-Path $patternsDir -Parent) $pattern.ExecutorPath
            New-Item -Path (Split-Path $executorFullPath -Parent) -ItemType Directory -Force | Out-Null
            Set-Content -Path $executorFullPath -Value $executor

            Write-Host "    ✓ $patternName (spec, schema, executor)" -ForegroundColor Green
        } else {
            Write-Host "    [DRY RUN] Would create $patternName" -ForegroundColor Yellow
        }
    }
}

# Phase 7: Update registry and validate
Write-Host ""
Write-Host "Phase 7/7: Updating registry..." -ForegroundColor Cyan
foreach ($pattern in $sourcePatterns) {
    if (-not $DryRun) {
        & "$helpersDir\Add-PatternToRegistry.ps1" `
            -PatternID $pattern.PatternID `
            -Name $pattern.FileSystemName `
            -Category $pattern.Category `
            -SpecPath $pattern.SpecPath `
            -SchemaPath $pattern.SchemaPath `
            -ExecutorPath $pattern.ExecutorPath

        Write-Host "  ✓ Registered $($pattern.PatternID)" -ForegroundColor Green
    } else {
        Write-Host "  [DRY RUN] Would register $($pattern.PatternID)" -ForegroundColor Yellow
    }
}

# Validation
if ($Verify -and -not $DryRun) {
    Write-Host ""
    Write-Host "Running validation..." -ForegroundColor Cyan

    # Update metadata
    & "$helpersDir\Update-PatternMetadata.ps1"

    # Run validators
    python "$patternsDir\automation\validators\registry_validator.py"
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  BATCH REGISTRATION COMPLETE" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "  Patterns processed: $($sourcePatterns.Count)" -ForegroundColor White
Write-Host "  Batches: $batches" -ForegroundColor White
Write-Host "  Files created: $($sourcePatterns.Count * 3)" -ForegroundColor White
Write-Host ""
