#!/usr/bin/env pwsh
# DOC_LINK: DOC-SCRIPT-VALIDATE-FAILURE-MODES-091
<#
.SYNOPSIS
    Validate Failure Mode Documentation (ERR-FM-*)

.DESCRIPTION
    Validates that failure mode documentation meets all requirements
    defined in the orchestration specification.

.PARAMETER DocsDir
    Directory containing failure mode docs (default: docs/failure_modes)

.EXAMPLE
    ./validate_failure_modes.ps1 -DocsDir docs/failure_modes
#>

[CmdletBinding()]
param(
    [Parameter()]
    [string]$DocsDir = "docs/failure_modes",

    [Parameter()]
    [switch]$VerboseOutput
)

$ErrorActionPreference = "Stop"
$script:FailureCount = 0
$script:PassCount = 0

function Write-Result {
    param(
        [string]$RequirementId,
        [string]$Status,
        [string]$Message
    )

    $statusSymbol = if ($Status -eq "PASS") { "✓" } else { "✗" }
    $color = if ($Status -eq "PASS") { "Green" } else { "Red" }

    Write-Host "[$statusSymbol] $RequirementId : " -NoNewline
    Write-Host $Message -ForegroundColor $color

    if ($Status -eq "PASS") {
        $script:PassCount++
    } else {
        $script:FailureCount++
    }
}

function Test-FailureModeDoc {
    param([string]$DocPath)

    $errors = @()
    $content = Get-Content $DocPath -Raw

    # Required sections
    $requiredSections = @(
        "Detection",
        "Probability",
        "Impact",
        "Manifestation",
        "Automatic Recovery",
        "Manual Intervention"
    )

    foreach ($section in $requiredSections) {
        if ($content -notmatch "\*\*$section\*\*") {
            $errors += "Missing required section: **$section**"
        }
    }

    # Check for Related Failures section (optional but recommended)
    if ($content -notmatch "\*\*Related Failures\*\*") {
        $errors += "Warning: Missing recommended section: **Related Failures**"
    }

    # Check for structured format
    if ($content -notmatch "##\s+") {
        $errors += "Document should use markdown headers (##)"
    }

    return $errors
}

Write-Host "`n=== Validating Failure Mode Requirements ===" -ForegroundColor Cyan
Write-Host "Documentation Directory: $DocsDir`n" -ForegroundColor Gray

# ERR-FM-001: Failure Mode Documentation
Write-Host "`nERR-FM-001: Failure Mode Documentation" -ForegroundColor Yellow

if (-not (Test-Path $DocsDir)) {
    Write-Result "ERR-FM-001" "FAIL" "Failure modes directory not found: $DocsDir"
} else {
    $failureModeFiles = Get-ChildItem -Path $DocsDir -Filter "*.md" | Where-Object { $_.Name -ne "CATALOG.md" }

    if ($failureModeFiles.Count -eq 0) {
        Write-Host "  No failure mode documentation files found" -ForegroundColor Yellow
        Write-Result "ERR-FM-001" "PASS" "Failure modes directory exists (0 documented modes)"
    } else {
        $allDocsValid = $true
        $docsWithErrors = 0
        $warningCount = 0

        foreach ($docFile in $failureModeFiles) {
            $errors = Test-FailureModeDoc $docFile.FullName

            # Count warnings vs errors
            $actualErrors = $errors | Where-Object { $_ -notlike "Warning:*" }
            $warnings = $errors | Where-Object { $_ -like "Warning:*" }
            $warningCount += $warnings.Count

            if ($actualErrors.Count -gt 0) {
                $allDocsValid = $false
                $docsWithErrors++

                Write-Host "  Errors in $($docFile.Name):" -ForegroundColor Red
                foreach ($error in $actualErrors) {
                    Write-Host "    - $error" -ForegroundColor Red
                }
            }

            if ($warnings.Count -gt 0 -and $VerboseOutput) {
                foreach ($warning in $warnings) {
                    Write-Host "  $warning" -ForegroundColor Yellow
                }
            } elseif ($actualErrors.Count -eq 0 -and $VerboseOutput) {
                Write-Host "  ✓ $($docFile.Name)" -ForegroundColor Gray
            }
        }

        $validCount = $failureModeFiles.Count - $docsWithErrors
        $message = "Failure mode documentation: $validCount/$($failureModeFiles.Count) files valid"
        if ($warningCount -gt 0) {
            $message += " ($warningCount warnings)"
        }

        Write-Result "ERR-FM-001" $(if ($allDocsValid) { "PASS" } else { "FAIL" }) $message
    }
}

# ERR-FM-002: Failure Mode Catalog
Write-Host "`nERR-FM-002: Failure Mode Catalog" -ForegroundColor Yellow

$catalogPath = Join-Path $DocsDir "CATALOG.md"
if (-not (Test-Path $catalogPath)) {
    Write-Result "ERR-FM-002" "FAIL" "Failure mode catalog not found: CATALOG.md"
} else {
    $catalogContent = Get-Content $catalogPath -Raw

    # Check for required sections
    $hasTaskFailures = $catalogContent -match "##\s+Task Failures"
    $hasWorkerFailures = $catalogContent -match "##\s+Worker Failures"
    $hasSystemFailures = $catalogContent -match "##\s+System Failures"

    $catalogValid = $hasTaskFailures -and $hasWorkerFailures -and $hasSystemFailures

    if (-not $hasTaskFailures) {
        Write-Host "  Missing section: ## Task Failures" -ForegroundColor Red
    }
    if (-not $hasWorkerFailures) {
        Write-Host "  Missing section: ## Worker Failures" -ForegroundColor Red
    }
    if (-not $hasSystemFailures) {
        Write-Host "  Missing section: ## System Failures" -ForegroundColor Red
    }

    # Check if catalog lists documented failure modes
    if (Test-Path $DocsDir) {
        $failureModeFiles = Get-ChildItem -Path $DocsDir -Filter "*.md" | Where-Object { $_.Name -ne "CATALOG.md" }
        $listedModes = 0

        foreach ($docFile in $failureModeFiles) {
            $modeName = $docFile.BaseName
            if ($catalogContent -match $modeName) {
                $listedModes++
            } else {
                Write-Host "  Warning: Mode '$modeName' not listed in catalog" -ForegroundColor Yellow
            }
        }

        if ($VerboseOutput) {
            Write-Host "  Catalog lists $listedModes/$($failureModeFiles.Count) documented modes" -ForegroundColor Gray
        }
    }

    Write-Result "ERR-FM-002" $(if ($catalogValid) { "PASS" } else { "FAIL" }) `
        "Failure mode catalog exists and has required sections"
}

# ERR-FM-003: Recovery Decision Trees
Write-Host "`nERR-FM-003: Recovery Decision Trees" -ForegroundColor Yellow

# Check if catalog or individual docs contain decision trees
$hasDecisionTrees = $false
$decisionTreeCount = 0

if (Test-Path $catalogPath) {
    $catalogContent = Get-Content $catalogPath -Raw
    if ($catalogContent -match "Decision Tree|Recovery Decision") {
        $hasDecisionTrees = $true
        $decisionTreeCount++
    }
}

if (Test-Path $DocsDir) {
    $allDocs = Get-ChildItem -Path $DocsDir -Filter "*.md"
    foreach ($doc in $allDocs) {
        $content = Get-Content $doc.FullName -Raw
        if ($content -match "Decision Tree|Recovery Decision") {
            $hasDecisionTrees = $true
            $decisionTreeCount++
        }
    }
}

if ($hasDecisionTrees) {
    Write-Result "ERR-FM-003" "PASS" `
        "Recovery decision trees found in $decisionTreeCount documents"
} else {
    Write-Host "  No decision trees found in failure mode documentation" -ForegroundColor Yellow
    Write-Result "ERR-FM-003" "PASS" `
        "Recovery decision trees are optional (SHOULD, not MUST)"
}

# Summary
Write-Host "`n=== Validation Summary ===" -ForegroundColor Cyan
Write-Host "PASSED: $script:PassCount" -ForegroundColor Green
Write-Host "FAILED: $script:FailureCount" -ForegroundColor $(if ($script:FailureCount -gt 0) { "Red" } else { "Green" })

if ($script:FailureCount -gt 0) {
    Write-Host "`nValidation FAILED. See errors above." -ForegroundColor Red
    exit 1
} else {
    Write-Host "`nValidation PASSED. All failure mode requirements met." -ForegroundColor Green
    exit 0
}
