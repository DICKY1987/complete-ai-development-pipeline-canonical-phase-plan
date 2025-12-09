#!/usr/bin/env pwsh
# DOC_ID: DOC-PAT-HELPERS-GET-NEXT-PATTERN-ID-001
<#
.SYNOPSIS
    Generate next available pattern ID with collision detection

.DESCRIPTION
    Implements automated pattern ID generation (GAP-PATREG-002)
    - Reads PATTERN_INDEX.yaml to find existing IDs
    - Scans specs/ directory for orphaned patterns
    - Generates unique pattern_id and doc_id
    - Validates against all sources to prevent collisions
    - Supports standard categories: EXEC, BEHAVE, ANTI, DOC, META, MODULE

.PARAMETER Category
    Pattern category (EXEC, BEHAVE, ANTI, DOC, META, MODULE)

.PARAMETER Name
    Pattern name (e.g., "DATABASE-MIGRATION", "ATOMIC-CREATE")

.PARAMETER Force
    Skip collision checks (use with caution)

.EXAMPLE
    Get-NextPatternID -Category "EXEC" -Name "DATABASE-MIGRATION"

    Returns:
    @{
        pattern_id = "PAT-EXEC-DATABASE-MIGRATION-015"
        doc_id = "DOC-PAT-EXEC-DATABASE-MIGRATION-015"
        number = 15
        category = "EXEC"
        name = "DATABASE-MIGRATION"
        spec_path = "patterns/specs/database_migration.pattern.yaml"
        schema_path = "patterns/schemas/database_migration.schema.json"
        executor_path = "patterns/executors/database_migration_executor.ps1"
    }

.NOTES
    Pattern: EXEC-004 (Atomic Operations)
    Version: 1.0.0
    Created: 2025-12-09
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("EXEC", "BEHAVE", "ANTI", "DOC", "META", "MODULE")]
    [string]$Category,

    [Parameter(Mandatory=$true)]
    [ValidatePattern('^[A-Z][A-Z0-9\-]+$')]
    [string]$Name,

    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

#region Helper Functions

function Get-PatternsDirectory {
    $scriptPath = $PSScriptRoot
    # Navigate up from automation/helpers/ to patterns/
    return Split-Path (Split-Path $scriptPath -Parent) -Parent
}

function Get-ExistingPatternNumbers {
    param(
        [string]$Category,
        [string]$PatternsDir
    )

    $numbers = @()

    # Check registry
    $registryPath = Join-Path $PatternsDir "registry\PATTERN_INDEX.yaml"
    if (Test-Path $registryPath) {
        $registryContent = Get-Content $registryPath -Raw
        $pattern = "pattern_id:\s*PAT-$Category-.+-(\d+)"
        $matches = [regex]::Matches($registryContent, $pattern)
        foreach ($match in $matches) {
            $numbers += [int]$match.Groups[1].Value
        }
    }

    # Check specs directory for orphaned patterns
    $specsDir = Join-Path $PatternsDir "specs"
    if (Test-Path $specsDir) {
        Get-ChildItem $specsDir -Filter "*.pattern.yaml" | ForEach-Object {
            $content = Get-Content $_.FullName -Raw
            if ($content -match "pattern_id:\s*`"?PAT-$Category-.+-(\d+)`"?") {
                $numbers += [int]$matches[1]
            }
        }
    }

    return $numbers | Sort-Object -Unique
}

function Test-PatternIDUnique {
    param(
        [string]$PatternID,
        [string]$PatternsDir
    )

    # Check registry
    $registryPath = Join-Path $PatternsDir "registry\PATTERN_INDEX.yaml"
    if (Test-Path $registryPath) {
        $registryContent = Get-Content $registryPath -Raw
        if ($registryContent -match "pattern_id:\s*`"?$PatternID`"?") {
            return $false
        }
    }

    # Check specs directory
    $specsDir = Join-Path $PatternsDir "specs"
    if (Test-Path $specsDir) {
        Get-ChildItem $specsDir -Filter "*.pattern.yaml" | ForEach-Object {
            $content = Get-Content $_.FullName -Raw
            if ($content -match "pattern_id:\s*`"?$PatternID`"?") {
                return $false
            }
        }
    }

    return $true
}

function Format-PatternName {
    param([string]$Name)

    # Ensure uppercase and valid characters
    $formatted = $Name.ToUpper() -replace '[^A-Z0-9\-]', '-'

    # Remove duplicate hyphens
    $formatted = $formatted -replace '\-+', '-'

    # Remove leading/trailing hyphens
    $formatted = $formatted.Trim('-')

    return $formatted
}

function ConvertTo-FileSystemName {
    param([string]$Name)

    # Convert to lowercase with underscores (e.g., DATABASE-MIGRATION -> database_migration)
    return $Name.ToLower() -replace '\-', '_'
}

#endregion

#region Main Logic

$patternsDir = Get-PatternsDirectory

Write-Verbose "Patterns directory: $patternsDir"
Write-Verbose "Category: $Category"
Write-Verbose "Name: $Name"

# Format name
$formattedName = Format-PatternName -Name $Name
Write-Verbose "Formatted name: $formattedName"

# Get existing numbers for this category
$existingNumbers = @(Get-ExistingPatternNumbers -Category $Category -PatternsDir $patternsDir)
if ($null -eq $existingNumbers) { $existingNumbers = @() }
Write-Verbose "Found $($existingNumbers.Count) existing patterns in category $Category"

# Find next available number (fill gaps first, then increment)
$nextNumber = 1
if ($existingNumbers.Count -gt 0) {
    # Look for gaps in the sequence
    $sortedNumbers = $existingNumbers | Sort-Object
    $foundGap = $false

    for ($i = 1; $i -le 999; $i++) {
        if ($i -notin $existingNumbers) {
            $nextNumber = $i
            $foundGap = $true
            Write-Verbose "Found gap at number $nextNumber"
            break
        }
    }

    if (-not $foundGap) {
        throw "Category $Category has exhausted the number range (001-999). Consider creating a new category."
    }
}

# Generate IDs
$patternID = "PAT-$Category-$formattedName-$($nextNumber.ToString('000'))"
$docID = "DOC-$patternID"

Write-Verbose "Generated pattern_id: $patternID"
Write-Verbose "Generated doc_id: $docID"

# Validate uniqueness
if (-not $Force) {
    $isUnique = Test-PatternIDUnique -PatternID $patternID -PatternsDir $patternsDir
    if (-not $isUnique) {
        throw "Pattern ID '$patternID' already exists. Use -Force to override (not recommended)."
    }
    Write-Verbose "✓ Pattern ID is unique"
}

# Generate file paths
$fileSystemName = ConvertTo-FileSystemName -Name $formattedName
$result = @{
    pattern_id = $patternID
    doc_id = $docID
    number = $nextNumber
    category = $Category
    name = $formattedName
    file_system_name = $fileSystemName
    spec_path = "patterns/specs/$fileSystemName.pattern.yaml"
    schema_path = "patterns/schemas/$fileSystemName.schema.json"
    executor_path = "patterns/executors/$($fileSystemName)_executor.ps1"
    test_path = "patterns/tests/test_$($fileSystemName)_executor.ps1"
    example_dir = "patterns/examples/$fileSystemName/"
}

# Return structured object
return [PSCustomObject]$result

#endregion
