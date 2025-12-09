#!/usr/bin/env pwsh
# DOC_ID: DOC-PAT-HELPERS-ADD-PATTERN-TO-REGISTRY-001
<#
.SYNOPSIS
    Add pattern entry to PATTERN_INDEX.yaml

.DESCRIPTION
    Implements GAP-PATREG-005: Automated registry updates
    - Loads PATTERN_INDEX.yaml
    - Appends new pattern entry
    - Updates metadata counts
    - Validates paths exist
    - Atomic operation with rollback

.PARAMETER PatternID
    Pattern ID (e.g., PAT-EXEC-DATABASE-001)

.PARAMETER Name
    Pattern name

.PARAMETER Category
    Pattern category

.PARAMETER SpecPath
    Path to pattern spec file (relative to repo root)

.PARAMETER SchemaPath
    Path to schema file (optional)

.PARAMETER ExecutorPath
    Path to executor file (optional)

.PARAMETER AdditionalFields
    Hashtable of additional fields to include

.PARAMETER DryRun
    Show what would be done without executing

.EXAMPLE
    Add-PatternToRegistry -PatternID "PAT-EXEC-TEST-001" -Name "test_pattern" `
        -Category "EXEC" -SpecPath "patterns/specs/test_pattern.pattern.yaml"

.NOTES
    Pattern: EXEC-004 (Atomic Operations)
    Version: 1.0.0
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$PatternID,

    [Parameter(Mandatory=$true)]
    [string]$Name,

    [Parameter(Mandatory=$true)]
    [ValidateSet("EXEC", "BEHAVE", "ANTI", "DOC", "META", "MODULE")]
    [string]$Category,

    [Parameter(Mandatory=$true)]
    [string]$SpecPath,

    [Parameter(Mandatory=$false)]
    [string]$SchemaPath,

    [Parameter(Mandatory=$false)]
    [string]$ExecutorPath,

    [Parameter(Mandatory=$false)]
    [hashtable]$AdditionalFields = @{},

    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptPath = $PSScriptRoot
$patternsDir = Split-Path (Split-Path $scriptPath -Parent) -Parent
$repoRoot = Split-Path $patternsDir -Parent
$registryPath = Join-Path $patternsDir "registry\PATTERN_INDEX.yaml"

# Validate registry exists
if (-not (Test-Path $registryPath)) {
    throw "Registry file not found: $registryPath"
}

# Validate spec file exists
$fullSpecPath = Join-Path $repoRoot $SpecPath
if (-not (Test-Path $fullSpecPath)) {
    throw "Spec file not found: $fullSpecPath"
}

Write-Verbose "Registry: $registryPath"
Write-Verbose "Pattern ID: $PatternID"
Write-Verbose "Spec Path: $SpecPath"

# Backup registry
$backupPath = "$registryPath.backup"
Copy-Item $registryPath $backupPath -Force
Write-Verbose "Created backup: $backupPath"

try {
    # Read registry
    $registryContent = Get-Content $registryPath -Raw

    # Check for duplicate pattern_id
    if ($registryContent -match "pattern_id:\s*$PatternID") {
        throw "Pattern ID '$PatternID' already exists in registry"
    }

    # Build entry
    $entry = @"

- pattern_id: $PatternID
  name: $Name
  version: 1.0.0
  status: draft
  category: $Category
  spec_path: $SpecPath
  created: '$(Get-Date -Format 'yyyy-MM-dd')'
"@

    if ($SchemaPath) {
        $entry += "`n  schema_path: $SchemaPath"
    }

    if ($ExecutorPath) {
        $entry += "`n  executor_path: $ExecutorPath"
    }

    # Add additional fields
    foreach ($key in $AdditionalFields.Keys) {
        $value = $AdditionalFields[$key]
        if ($value -is [string]) {
            $entry += "`n  $($key): '$value'"
        } else {
            $entry += "`n  $($key): $value"
        }
    }

    if ($DryRun) {
        Write-Host "DRY RUN: Would add to registry:" -ForegroundColor Yellow
        Write-Host $entry -ForegroundColor Gray
        Remove-Item $backupPath -Force
        return
    }

    # Append entry to registry (before the last line if it's a newline)
    $updatedContent = $registryContent.TrimEnd() + $entry + "`n"

    # Write back
    Set-Content -Path $registryPath -Value $updatedContent -NoNewline

    # Update metadata counts
    & "$scriptPath\Update-PatternMetadata.ps1"

    Write-Host "✓ Added pattern $PatternID to registry" -ForegroundColor Green

    # Remove backup on success
    Remove-Item $backupPath -Force

} catch {
    # Rollback on error
    Write-Error "Failed to add pattern to registry: $_"
    if (Test-Path $backupPath) {
        Copy-Item $backupPath $registryPath -Force
        Remove-Item $backupPath -Force
        Write-Host "✓ Rolled back registry to backup" -ForegroundColor Yellow
    }
    throw
}
