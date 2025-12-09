#!/usr/bin/env pwsh
# DOC_ID: DOC-PAT-GENERATORS-UPDATE-PATTERN-DOCS-001
<#
.SYNOPSIS
    Auto-update pattern documentation

.DESCRIPTION
    Implements GAP-PATREG-013: Documentation auto-updater
    Updates pattern counts in documentation files

.PARAMETER DocsDir
    Directory containing documentation files

.EXAMPLE
    Update-PatternDocs

.NOTES
    Pattern: EXEC-004 (Atomic Operations)
    Version: 1.0.0
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$DocsDir
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptPath = $PSScriptRoot
$patternsDir = Split-Path (Split-Path $scriptPath -Parent) -Parent

if (-not $DocsDir) {
    $DocsDir = $patternsDir
}

# Get pattern count from registry
& "$patternsDir\automation\helpers\Update-PatternMetadata.ps1" -WhatIf | Out-Null

$registryPath = Join-Path $patternsDir "registry\PATTERN_INDEX.yaml"
$registryContent = Get-Content $registryPath -Raw

if ($registryContent -match 'total_patterns:\s*(\d+)') {
    $totalPatterns = [int]$matches[1]
} else {
    $totalPatterns = 0
}

Write-Host "Updating documentation with pattern count: $totalPatterns" -ForegroundColor Cyan

# Update README files
Get-ChildItem $DocsDir -Filter "*.md" -Recurse | ForEach-Object {
    $content = Get-Content $_.FullName -Raw

    # Replace various pattern count placeholders
    $updated = $content -replace 'Total Patterns:\s*\d+', "Total Patterns: $totalPatterns"
    $updated = $updated -replace 'total_patterns:\s*\d+', "total_patterns: $totalPatterns"
    $updated = $updated -replace '\d+\s*patterns?(\s+registered)?', "$totalPatterns patterns"

    if ($updated -ne $content) {
        Set-Content -Path $_.FullName -Value $updated
        Write-Host "  ✓ Updated $($_.Name)" -ForegroundColor Green
    }
}

Write-Host "✓ Documentation update complete" -ForegroundColor Green
