#Requires -Version 5.1
<#
.SYNOPSIS
    Renders all .drawio diagram source files to PNG/PDF using draw.io CLI.

.DESCRIPTION
    Scans docs/diagrams/source/ for .drawio files and exports them to
    docs/diagrams/exports/png/ and optionally PDF.

    Uses C:\Tools\drawio-cli.ps1 wrapper for consistent CLI access.

.PARAMETER Format
    Export format(s): png, pdf, svg (comma-separated)

.PARAMETER SourceDir
    Source directory containing .drawio files (default: docs/diagrams/source)

.PARAMETER OutputDir
    Output directory for exports (default: docs/diagrams/exports)

.PARAMETER Scale
    Scale factor for export (default: 2.5 for high quality)

.EXAMPLE
    .\scripts\render_diagrams.ps1

.EXAMPLE
    .\scripts\render_diagrams.ps1 -Format "png,pdf" -Scale 3.0
#>

param(
    [string]$Format = "png",
    [string]$SourceDir = "docs\diagrams\source",
    [string]$OutputDir = "docs\diagrams\exports",
    [decimal]$Scale = 2.5
)

$ErrorActionPreference = "Stop"

# Resolve paths relative to repo root
$repoRoot = Split-Path -Parent $PSScriptRoot
$sourceDir = Join-Path $repoRoot $SourceDir
$outputDir = Join-Path $repoRoot $OutputDir

# Verify source directory exists
if (-not (Test-Path $sourceDir)) {
    Write-Error "Source directory not found: $sourceDir"
    exit 1
}

# Verify draw.io CLI wrapper exists
$drawioCliPath = "C:\Tools\drawio-cli.ps1"
if (-not (Test-Path $drawioCliPath)) {
    Write-Error "draw.io CLI wrapper not found: $drawioCliPath"
    Write-Host "Run setup to create C:\Tools\drawio-cli.ps1"
    exit 1
}

# Parse formats
$formats = $Format.Split(",") | ForEach-Object { $_.Trim() }

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Diagram Rendering Pipeline" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Source Dir: $sourceDir"
Write-Host "Output Dir: $outputDir"
Write-Host "Formats:    $($formats -join ', ')"
Write-Host "Scale:      $Scale"
Write-Host ""

# Find all .drawio files
$diagramFiles = Get-ChildItem -Path $sourceDir -Filter "*.drawio" -Recurse

if ($diagramFiles.Count -eq 0) {
    Write-Warning "No .drawio files found in $sourceDir"
    exit 0
}

Write-Host "Found $($diagramFiles.Count) diagram(s) to render" -ForegroundColor Green
Write-Host ""

$successCount = 0
$failCount = 0

foreach ($file in $diagramFiles) {
    # Get relative path from source dir
    $relativePath = $file.FullName.Substring($sourceDir.Length + 1)
    $relativeDir = Split-Path -Parent $relativePath
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)

    Write-Host "Processing: $relativePath" -ForegroundColor Yellow

    foreach ($fmt in $formats) {
        # Determine output directory
        $targetDir = Join-Path $outputDir $fmt
        if ($relativeDir) {
            $targetDir = Join-Path $targetDir $relativeDir
        }

        # Create output directory
        New-Item -ItemType Directory -Force -Path $targetDir | Out-Null

        # Output file path
        $outputFile = Join-Path $targetDir "$baseName.$fmt"

        Write-Host "  → Exporting $fmt to: $outputFile"

        # Build extra args
        $extraArgs = "--scale $Scale"

        # Call draw.io CLI wrapper
        $result = & pwsh -File $drawioCliPath `
            -Export `
            -Format $fmt `
            -InputPath $file.FullName `
            -OutputPath $outputFile `
            -ExtraArgs $extraArgs

        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Success" -ForegroundColor Green
            $successCount++
        } else {
            Write-Host "  ✗ Failed (exit code: $LASTEXITCODE)" -ForegroundColor Red
            $failCount++
        }
    }

    Write-Host ""
}

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Rendering Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Total Diagrams:  $($diagramFiles.Count)"
Write-Host "Successful:      $successCount" -ForegroundColor Green
Write-Host "Failed:          $failCount" -ForegroundColor $(if ($failCount -gt 0) { "Red" } else { "Gray" })
Write-Host ""

if ($failCount -gt 0) {
    exit 1
}

exit 0
