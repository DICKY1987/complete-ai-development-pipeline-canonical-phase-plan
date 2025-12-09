#!/usr/bin/env pwsh
# DOC_ID: DOC-PAT-HELPERS-TEST-PATTERN-ID-UNIQUE-001
<#
.SYNOPSIS
    Test if a pattern ID is unique across all sources

.DESCRIPTION
    Validates pattern ID uniqueness by checking:
    - PATTERN_INDEX.yaml registry
    - All spec files in specs/
    - Prevents ID collisions

.PARAMETER PatternID
    The pattern ID to test (e.g., "PAT-EXEC-DATABASE-001")

.EXAMPLE
    Test-PatternIDUnique -PatternID "PAT-EXEC-DATABASE-001"
    Returns $true if unique, $false if collision detected

.NOTES
    Pattern: EXEC-002 (Batch Validation)
    Version: 1.0.0
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true, ValueFromPipeline=$true)]
    [string]$PatternID
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptPath = $PSScriptRoot
$patternsDir = Split-Path (Split-Path $scriptPath -Parent) -Parent

$collisions = @()

# Check registry
$registryPath = Join-Path $patternsDir "registry\PATTERN_INDEX.yaml"
if (Test-Path $registryPath) {
    $registryContent = Get-Content $registryPath -Raw
    if ($registryContent -match "pattern_id:\s*`"?$PatternID`"?") {
        $collisions += "registry/PATTERN_INDEX.yaml"
    }
}

# Check specs directory
$specsDir = Join-Path $patternsDir "specs"
if (Test-Path $specsDir) {
    Get-ChildItem $specsDir -Filter "*.pattern.yaml" | ForEach-Object {
        $content = Get-Content $_.FullName -Raw
        if ($content -match "pattern_id:\s*`"?$PatternID`"?") {
            $collisions += "specs/$($_.Name)"
        }
    }
}

if ($collisions.Count -gt 0) {
    Write-Warning "Pattern ID '$PatternID' collision detected in:"
    $collisions | ForEach-Object { Write-Warning "  - $_" }
    return $false
}

return $true
