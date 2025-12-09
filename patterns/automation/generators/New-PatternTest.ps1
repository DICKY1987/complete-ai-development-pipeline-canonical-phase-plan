#!/usr/bin/env pwsh
# DOC_ID: DOC-PAT-GENERATORS-NEW-PATTERN-TEST-001
<#
.SYNOPSIS
    Generate Pester test from template

.DESCRIPTION
    Implements GAP-PATREG-012: Test template generator
    Creates Pester test files from template

.PARAMETER PatternName
    Pattern name (file system format)

.PARAMETER DocID
    Pattern document ID

.PARAMETER OutputPath
    Output path for test file

.EXAMPLE
    New-PatternTest -PatternName "database_migration" -DocID "DOC-PAT-EXEC-DATABASE-001"

.NOTES
    Pattern: EXEC-009 (Meta-Execution)
    Version: 1.0.0
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$PatternName,

    [Parameter(Mandatory=$true)]
    [string]$DocID,

    [Parameter(Mandatory=$false)]
    [string]$OutputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptPath = $PSScriptRoot
$patternsDir = Split-Path (Split-Path $scriptPath -Parent) -Parent
$templatesDir = Join-Path $patternsDir "templates"
$testsDir = Join-Path $patternsDir "tests"

if (-not $OutputPath) {
    $OutputPath = Join-Path $testsDir "test_$($PatternName)_executor.ps1"
}

# Load template
$template = Get-Content "$templatesDir\pattern-test.Tests.ps1" -Raw

# Replace placeholders
$test = $template -replace '\{PATTERN_NAME\}', $PatternName
$test = $test -replace '\{DOC_ID\}', $DocID

# Write test file
New-Item -Path (Split-Path $OutputPath -Parent) -ItemType Directory -Force | Out-Null
Set-Content -Path $OutputPath -Value $test

Write-Host "✓ Generated test file: $OutputPath" -ForegroundColor Green
