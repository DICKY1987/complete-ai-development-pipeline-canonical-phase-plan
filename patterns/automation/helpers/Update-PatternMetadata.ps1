#!/usr/bin/env pwsh
# DOC_ID: DOC-PAT-HELPERS-UPDATE-PATTERN-METADATA-001
<#
.SYNOPSIS
    Auto-update pattern metadata counts in PATTERN_INDEX.yaml

.DESCRIPTION
    Implements GAP-PATREG-009: Pattern Count Auto-Update
    - Counts actual patterns in registry
    - Updates metadata.total_patterns
    - Updates metadata.total_categories
    - Updates metadata.last_updated timestamp

.EXAMPLE
    Update-PatternMetadata
    Updates counts in PATTERN_INDEX.yaml

.NOTES
    Pattern: EXEC-004 (Atomic Operations)
    Version: 1.0.0
#>

[CmdletBinding()]
param(
    [switch]$WhatIf
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptPath = $PSScriptRoot
$patternsDir = Split-Path (Split-Path $scriptPath -Parent) -Parent
$registryPath = Join-Path $patternsDir "registry\PATTERN_INDEX.yaml"

if (-not (Test-Path $registryPath)) {
    throw "Registry file not found: $registryPath"
}

Write-Verbose "Loading registry from: $registryPath"

# Read registry (simple YAML parsing for metadata update)
$registryContent = Get-Content $registryPath -Raw

# Count patterns
$patternMatches = [regex]::Matches($registryContent, '(?m)^- pattern_id:')
$totalPatterns = $patternMatches.Count

# Count categories
$categoryMatches = [regex]::Matches($registryContent, '(?m)^\s+category:\s+(.+)$')
$categories = @{}
foreach ($match in $categoryMatches) {
    $category = $match.Groups[1].Value.Trim()
    $categories[$category] = $true
}
$totalCategories = $categories.Count

# Get current date
$currentDate = Get-Date -Format "yyyy-MM-dd"

Write-Host "Pattern Statistics:" -ForegroundColor White
Write-Host "  Total Patterns: $totalPatterns" -ForegroundColor Gray
Write-Host "  Total Categories: $totalCategories" -ForegroundColor Gray
Write-Host "  Last Updated: $currentDate" -ForegroundColor Gray
Write-Host ""

if ($WhatIf) {
    Write-Host "WHATIF: Would update metadata in $registryPath" -ForegroundColor Yellow
    return
}

# Update metadata counts using regex replacement
$updatedContent = $registryContent -replace '(?m)^(\s*total_patterns:)\s*\d+', "`$1 $totalPatterns"
$updatedContent = $updatedContent -replace '(?m)^(\s*total_categories:)\s*\d+', "`$1 $totalCategories"
$updatedContent = $updatedContent -replace "(?m)^(\s*last_updated:)\s*'.+'", "`$1 '$currentDate'"

# Write back to file
Set-Content -Path $registryPath -Value $updatedContent -NoNewline

Write-Host "✓ Updated pattern metadata in PATTERN_INDEX.yaml" -ForegroundColor Green
Write-Host "  - total_patterns: $totalPatterns" -ForegroundColor Gray
Write-Host "  - total_categories: $totalCategories" -ForegroundColor Gray
Write-Host "  - last_updated: $currentDate" -ForegroundColor Gray
