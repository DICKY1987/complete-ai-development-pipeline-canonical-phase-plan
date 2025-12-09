#!/usr/bin/env pwsh
# DOC_ID: DOC-PAT-HELPERS-UNDO-PATTERN-REGISTRATION-001
<#
.SYNOPSIS
    Rollback pattern registration

.DESCRIPTION
    Implements GAP-PATREG-016: Rollback capability
    Removes pattern from registry and optionally deletes files

.PARAMETER PatternID
    Pattern ID to remove

.PARAMETER DeleteFiles
    Also delete associated files

.EXAMPLE
    Undo-PatternRegistration -PatternID "PAT-EXEC-TEST-001" -DeleteFiles

.NOTES
    Pattern: EXEC-004 (Atomic Operations)
    Version: 1.0.0
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$PatternID,

    [switch]$DeleteFiles
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptPath = $PSScriptRoot
$patternsDir = Split-Path (Split-Path $scriptPath -Parent) -Parent
$repoRoot = Split-Path $patternsDir -Parent
$registryPath = Join-Path $patternsDir "registry\PATTERN_INDEX.yaml"

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "  ROLLBACK PATTERN REGISTRATION" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host ""
Write-Host "Pattern ID: $PatternID" -ForegroundColor White
Write-Host "Delete Files: $DeleteFiles" -ForegroundColor White
Write-Host ""

# Backup registry
$backupPath = "$registryPath.rollback_backup"
Copy-Item $registryPath $backupPath -Force
Write-Host "✓ Created backup: $backupPath" -ForegroundColor Green

try {
    # Load registry
    $registryContent = Get-Content $registryPath -Raw

    # Find pattern entry
    $lines = $registryContent -split "`n"
    $patternStart = -1
    $patternEnd = -1

    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match "pattern_id:\s*$PatternID") {
            $patternStart = $i - 1  # Include the "- " line

            # Find end of this entry (next "- " or end of file)
            for ($j = $i + 1; $j -lt $lines.Count; $j++) {
                if ($lines[$j] -match "^- pattern_id:") {
                    $patternEnd = $j - 1
                    break
                }
            }
            if ($patternEnd -eq -1) {
                $patternEnd = $lines.Count - 1
            }
            break
        }
    }

    if ($patternStart -eq -1) {
        throw "Pattern $PatternID not found in registry"
    }

    # Get file paths before removing
    $filesToDelete = @()
    if ($DeleteFiles) {
        for ($i = $patternStart; $i -le $patternEnd; $i++) {
            if ($lines[$i] -match '(spec|schema|executor)_path:\s*(.+)') {
                $relPath = $matches[2].Trim("'`"")
                $fullPath = Join-Path $repoRoot $relPath
                if (Test-Path $fullPath) {
                    $filesToDelete += $fullPath
                }
            }
        }
    }

    # Remove entry from registry
    $newLines = @()
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($i -lt $patternStart -or $i -gt $patternEnd) {
            $newLines += $lines[$i]
        }
    }

    $updatedContent = $newLines -join "`n"
    Set-Content -Path $registryPath -Value $updatedContent -NoNewline

    Write-Host "✓ Removed $PatternID from registry" -ForegroundColor Green

    # Delete files if requested
    if ($DeleteFiles) {
        foreach ($file in $filesToDelete) {
            Remove-Item $file -Force
            Write-Host "  ✓ Deleted $file" -ForegroundColor Gray
        }
    }

    # Update metadata
    & "$patternsDir\automation\helpers\Update-PatternMetadata.ps1"

    Write-Host ""
    Write-Host "✓ Rollback complete" -ForegroundColor Green

    # Remove backup
    Remove-Item $backupPath -Force

} catch {
    Write-Error "Rollback failed: $_"

    # Restore from backup
    if (Test-Path $backupPath) {
        Copy-Item $backupPath $registryPath -Force
        Remove-Item $backupPath -Force
        Write-Host "✓ Restored registry from backup" -ForegroundColor Yellow
    }

    throw
}
