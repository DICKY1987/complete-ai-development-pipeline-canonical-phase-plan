#!/usr/bin/env pwsh
# DOC_ID: DOC-PAT-HELPERS-NEW-PATTERN-COMMIT-MESSAGE-001
<#
.SYNOPSIS
    Generate structured commit message for pattern registration

.DESCRIPTION
    Implements GAP-PATREG-008: Commit message generator
    Creates standardized commit messages and copies to clipboard

.PARAMETER PatternName
    Pattern name

.PARAMETER PatternID
    Pattern ID

.PARAMETER Action
    Action performed (add, update, remove)

.PARAMETER Category
    Pattern category

.PARAMETER TimeSavings
    Estimated time savings

.PARAMETER ExampleCount
    Number of example instances

.EXAMPLE
    New-PatternCommitMessage -PatternName "database-migration" -PatternID "PAT-EXEC-DATABASE-001" -Category "EXEC"

.NOTES
    Pattern: EXEC-004 (Atomic Operations)
    Version: 1.0.0
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$PatternName,

    [Parameter(Mandatory=$true)]
    [string]$PatternID,

    [Parameter(Mandatory=$false)]
    [ValidateSet("add", "update", "remove")]
    [string]$Action = "add",

    [Parameter(Mandatory=$false)]
    [string]$Category,

    [Parameter(Mandatory=$false)]
    [string]$TimeSavings = "25%",

    [Parameter(Mandatory=$false)]
    [int]$ExampleCount = 3
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$actionVerbs = @{
    add = "Add"
    update = "Update"
    remove = "Remove"
}

$verb = $actionVerbs[$Action]

$message = @"
feat: $verb $PatternName pattern ($PatternID)

"@

if ($Action -eq "add") {
    $message += @"
- Added pattern specification
- Created JSON schema
- Implemented PowerShell executor
- Added $ExampleCount example instances
- Created Pester tests
- Updated pattern registry

"@
} elseif ($Action -eq "update") {
    $message += @"
- Updated pattern specification
- Updated executor implementation
- Updated tests
- Registry synchronized

"@
} else {
    $message += @"
- Removed pattern specification
- Removed schema and executor
- Updated pattern registry

"@
}

if ($Category) {
    $message += "Category: $Category`n"
}

$message += @"
Time savings: $TimeSavings
Status: draft
Pattern: $PatternID
"@

# Copy to clipboard
$message | Set-Clipboard

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  COMMIT MESSAGE GENERATED" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host $message -ForegroundColor Yellow
Write-Host ""
Write-Host "✓ Copied to clipboard" -ForegroundColor Green
Write-Host ""

return $message
