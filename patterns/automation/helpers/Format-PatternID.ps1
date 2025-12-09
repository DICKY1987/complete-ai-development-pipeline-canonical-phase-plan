#!/usr/bin/env pwsh
# DOC_ID: DOC-PAT-HELPERS-FORMAT-PATTERN-ID-001
<#
.SYNOPSIS
    Format and validate pattern ID structure

.DESCRIPTION
    Validates pattern ID format and returns normalized version
    Expected format: PAT-{CATEGORY}-{NAME}-{NUMBER}
    - CATEGORY: EXEC, BEHAVE, ANTI, DOC, META, MODULE
    - NAME: Uppercase with hyphens
    - NUMBER: 001-999

.PARAMETER PatternID
    The pattern ID to format

.PARAMETER Strict
    Throw error on invalid format (default: return $null)

.EXAMPLE
    Format-PatternID -PatternID "pat-exec-database-migration-15"
    Returns: PAT-EXEC-DATABASE-MIGRATION-015

.NOTES
    Pattern: EXEC-001 (Type-Safe Operations)
    Version: 1.0.0
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true, ValueFromPipeline=$true)]
    [string]$PatternID,

    [switch]$Strict
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Validate format
if ($PatternID -notmatch '^PAT-([A-Z]+)-(.+)-(\d+)$') {
    if ($Strict) {
        throw "Invalid pattern ID format: '$PatternID'. Expected: PAT-{CATEGORY}-{NAME}-{NUMBER}"
    }
    return $null
}

$category = $matches[1]
$name = $matches[2]
$number = [int]$matches[3]

# Validate category
$validCategories = @("EXEC", "BEHAVE", "ANTI", "DOC", "META", "MODULE")
if ($category -notin $validCategories) {
    if ($Strict) {
        throw "Invalid category: '$category'. Must be one of: $($validCategories -join ', ')"
    }
    return $null
}

# Validate number range
if ($number -lt 1 -or $number -gt 999) {
    if ($Strict) {
        throw "Invalid number: '$number'. Must be between 001 and 999"
    }
    return $null
}

# Normalize format
$formattedID = "PAT-$category-$name-$($number.ToString('000'))"

return $formattedID
