#!/usr/bin/env pwsh
# Quick registration script for PATTERN_52 files

param(
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$patternsDir = $PSScriptRoot

# Read the source directory
$sourceDir = "C:\Users\richg\ALL_AI\DOCUMENTS\PATTERN_52"
$sourceFiles = Get-ChildItem $sourceDir -Filter "*.md" | Select-Object -ExpandProperty Name

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  PATTERN_52 BATCH REGISTRATION" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Found $($sourceFiles.Count) pattern files to register" -ForegroundColor Green
Write-Host ""

# Track registered patterns
$registered = @()

foreach ($file in $sourceFiles) {
    $basename = [System.IO.Path]::GetFileNameWithoutExtension($file)

    # Determine category from filename
    $category = "DOC"
    if ($basename -match '^EXECUTION') { $category = "EXEC" }
    elseif ($basename -match '^PATTERN-\d+') { $category = "EXEC" }
    elseif ($basename -match 'ANTI') { $category = "ANTI" }
    elseif ($basename -match '^DOC_') { $category = "DOC" }
    elseif ($basename -match '^META_') { $category = "META" }
    elseif ($basename -match '^MODULE_') { $category = "MODULE" }
    elseif ($basename -match '^GUI_|^GLOSSARY_') { $category = "DOC" }

    # Clean up name for pattern ID
    $cleanName = $basename -replace '^DOC_', '' -replace '^EXECUTION_', '' -replace '^PATTERN_', 'EXEC-'
    $cleanName = $cleanName -replace '[^A-Za-z0-9\-]', '-'
    $cleanName = $cleanName -replace '\-+', '-'
    $cleanName = $cleanName -replace '^\-|\-$', ''
    $cleanName = $cleanName.ToUpper()

    # Generate pattern ID (using incrementing number)
    $number = "{0:D3}" -f ($registered.Count + 1)
    $patternId = "PAT-$category-$cleanName-$number"
    $docId = "DOC-$patternId"

    # File system name (lowercase with underscores)
    $fsName = $cleanName.ToLower() -replace '\-', '_'

    $patternInfo = @{
        SourceFile = $file
        PatternID = $patternId
        DocID = $docId
        Category = $category
        Name = $cleanName
        FileSystemName = $fsName
        SpecPath = "patterns\specs\$fsName.pattern.yaml"
        SchemaPath = "patterns\schemas\$fsName.schema.json"
        ExecutorPath = "patterns\executors\${fsName}_executor.ps1"
    }

    $registered += $patternInfo

    Write-Host "  $file" -ForegroundColor Gray
    Write-Host "    -> $patternId ($category)" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  Summary: $($registered.Count) patterns prepared" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

# Export to JSON for review
$outputPath = Join-Path $patternsDir "pattern_52_registration_plan.json"
$registered | ConvertTo-Json -Depth 10 | Set-Content $outputPath
Write-Host "Registration plan saved to: $outputPath" -ForegroundColor Yellow
Write-Host ""
Write-Host "To proceed with registration, review the plan and run with -Execute flag" -ForegroundColor Yellow
