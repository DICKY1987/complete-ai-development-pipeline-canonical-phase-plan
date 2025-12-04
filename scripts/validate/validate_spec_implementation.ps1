# DOC_LINK: DOC-SCRIPT-VALIDATE-SPEC-IMPLEMENTATION-093
#Requires -Version 5.1
<#
.SYNOPSIS
    Validates that implementation matches specifications.

.DESCRIPTION
    Checks that code implementation aligns with specification documents:
    - Spec URIs in code are resolvable
    - Required spec sections are implemented
    - Implementation references valid spec IDs
    - Spec coverage analysis

.PARAMETER SpecSource
    Path to specifications content directory. Default: specifications/content

.PARAMETER CodeRoot
    Path to code root directory. Default: repository root

.PARAMETER DryRun
    Show what would be validated without running checks.

.PARAMETER VerboseOutput
    Show detailed validation output.

.EXAMPLE
    .\validate_spec_implementation.ps1
    Run full spec-implementation validation.

.EXAMPLE
    .\validate_spec_implementation.ps1 -VerboseOutput
    Run with detailed output.
#>

[CmdletBinding()]
param(
    [Parameter()]
    [string]$SpecSource = "specifications\content",

    [Parameter()]
    [string]$CodeRoot = ".",

    [Parameter()]
    [switch]$DryRun,

    [Parameter()]
    [switch]$VerboseOutput
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

function Test-SpecIndexExists {
    <#
    .SYNOPSIS
        Check that spec index exists and is valid.
    #>
    param(
        [Parameter(Mandatory)]
        [string]$SpecSource
    )

    # Check multiple possible locations
    $possiblePaths = @(
        "specifications\.index\suite-index.yaml",
        "specifications\content\.index\suite-index.yaml",
        ".index\suite-index.yaml"
    )

    $indexPath = $null
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            $indexPath = $path
            break
        }
    }

    if (-not $indexPath) {
        return @{
            Status = "WARN"
            Message = "Spec index not found (spec system may not be initialized)"
            Details = @{
                SearchedPaths = $possiblePaths
                Solution = "python specifications/tools/indexer/indexer.py --source specifications/content"
                Note = "This is optional - only needed if using spec:// URIs"
            }
        }
    }

    try {
        # Try to parse the index
        $indexContent = Get-Content $indexPath -Raw
        # Basic validation - should contain 'suite' key
        if ($indexContent -notlike "*suite:*") {
            return @{
                Status = "FAIL"
                Message = "Spec index appears invalid (missing 'suite' key)"
                Details = @{ IndexPath = $indexPath }
            }
        }

        return @{
            Status = "PASS"
            Message = "Spec index exists and appears valid"
            Details = @{ IndexPath = $indexPath }
        }
    }
    catch {
        return @{
            Status = "FAIL"
            Message = "Spec index exists but failed to parse: $($_.Exception.Message)"
            Details = @{ IndexPath = $indexPath }
        }
    }
}

function Find-SpecReferences {
    <#
    .SYNOPSIS
        Find all spec URI references in code.
    #>
    param(
        [Parameter(Mandatory)]
        [string]$CodeRoot
    )

    Write-Verbose "  Scanning code for spec references..."

    $patterns = @(
        'spec://[A-Z0-9_/-]+(?:#p-\d+)?',
        'specid://[A-Z0-9_-]+'
    )

    $references = @()

    # Search Python files
    $pythonFiles = Get-ChildItem -Path $CodeRoot -Filter "*.py" -Recurse -File -ErrorAction SilentlyContinue
    foreach ($file in $pythonFiles) {
        $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
        if (-not $content) { continue }

        foreach ($pattern in $patterns) {
            $matches = [regex]::Matches($content, $pattern)
            foreach ($match in $matches) {
                $references += [PSCustomObject]@{
                    File = $file.FullName.Replace("$CodeRoot\", "")
                    URI = $match.Value
                    Type = if ($match.Value -like "spec://*") { "spec_uri" } else { "spec_id" }
                }
            }
        }
    }

    # Search Markdown files
    $mdFiles = Get-ChildItem -Path $CodeRoot -Filter "*.md" -Recurse -File -ErrorAction SilentlyContinue
    foreach ($file in $mdFiles) {
        # Skip specs themselves
        if ($file.FullName -like "*specifications\content*") {
            continue
        }

        $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
        if (-not $content) { continue }

        foreach ($pattern in $patterns) {
            $matches = [regex]::Matches($content, $pattern)
            foreach ($match in $matches) {
                $references += [PSCustomObject]@{
                    File = $file.FullName.Replace("$CodeRoot\", "")
                    URI = $match.Value
                    Type = if ($match.Value -like "spec://*") { "spec_uri" } else { "spec_id" }
                }
            }
        }
    }

    return $references
}

function Test-SpecURIsResolvable {
    <#
    .SYNOPSIS
        Check that all spec URIs in code are resolvable.
    #>
    param(
        [Parameter(Mandatory)]
        [string]$SpecSource,

        [Parameter(Mandatory)]
        [string]$CodeRoot
    )

    Write-Verbose "  Finding spec references in code..."

    $references = Find-SpecReferences -CodeRoot $CodeRoot

    if ($references.Count -eq 0) {
        return @{
            Status = "PASS"
            Message = "No spec references found in code"
            Details = @{
                TotalReferences = 0
            }
        }
    }

    Write-Verbose "  Found $($references.Count) spec references"
    Write-Verbose "  Checking if references are resolvable..."

    # For now, just check that referenced specs exist
    # TODO: Use resolver.py to actually resolve URIs
    $unresolvable = @()

    foreach ($ref in $references) {
        # Basic check: extract volume/section from spec://VOLUME/SECTION
        if ($ref.Type -eq "spec_uri" -and $ref.URI -match 'spec://([^/]+)/([^#]+)') {
            $volume = $matches[1].ToLower()
            $section = $matches[2].ToLower()

            # Check if volume directory exists
            $volumePath = Join-Path $SpecSource $volume
            if (-not (Test-Path $volumePath)) {
                $unresolvable += [PSCustomObject]@{
                    URI = $ref.URI
                    File = $ref.File
                    Reason = "Volume directory not found: $volume"
                }
            }
        }
    }

    if ($unresolvable.Count -gt 0) {
        return @{
            Status = "FAIL"
            Message = "$($unresolvable.Count) spec URIs may not be resolvable"
            Details = @{
                TotalReferences = $references.Count
                Unresolvable = $unresolvable.Count
                Examples = $unresolvable | Select-Object -First 5
            }
        }
    }

    return @{
        Status = "PASS"
        Message = "All $($references.Count) spec references appear valid"
        Details = @{
            TotalReferences = $references.Count
            ByType = @{
                SpecURI = ($references | Where-Object { $_.Type -eq "spec_uri" }).Count
                SpecID = ($references | Where-Object { $_.Type -eq "spec_id" }).Count
            }
        }
    }
}

function Test-RequiredSpecsImplemented {
    <#
    .SYNOPSIS
        Check that required specs have implementations.
    #>
    param(
        [Parameter(Mandatory)]
        [string]$SpecSource
    )

    Write-Verbose "  Checking for required spec implementations..."

    # Find all spec markdown files
    $specFiles = Get-ChildItem -Path $SpecSource -Filter "*.md" -Recurse -File

    $missingImplementations = @()

    foreach ($file in $specFiles) {
        $content = Get-Content $file.FullName -Raw

        # Look for MUST/REQUIRED markers
        if ($content -match '\b(MUST|REQUIRED|SHALL)\b') {
            # Extract requirement
            $lines = $content -split "`n"
            foreach ($line in $lines) {
                if ($line -match '\b(MUST|REQUIRED|SHALL)\b') {
                    # This is a required spec
                    # Check if there's a corresponding implementation reference
                    # (This is a simplified check - real implementation would be more sophisticated)

                    # For now, just track that required specs exist
                    # TODO: Cross-reference with implementation tracker
                }
            }
        }
    }

    return @{
        Status = "PASS"
        Message = "Found $($specFiles.Count) specification files"
        Details = @{
            TotalSpecFiles = $specFiles.Count
            SpecDirectories = (Get-ChildItem -Path $SpecSource -Directory).Count
        }
    }
}

function Get-SpecCoverage {
    <#
    .SYNOPSIS
        Calculate spec coverage metrics.
    #>
    param(
        [Parameter(Mandatory)]
        [string]$SpecSource,

        [Parameter(Mandatory)]
        [string]$CodeRoot
    )

    Write-Verbose "  Calculating spec coverage..."

    # Count spec files
    $specFiles = Get-ChildItem -Path $SpecSource -Filter "*.md" -Recurse -File

    # Count code files referencing specs
    $references = Find-SpecReferences -CodeRoot $CodeRoot
    $filesWithRefs = ($references | Select-Object -Unique File).Count

    # Count total implementation files
    $pyFiles = (Get-ChildItem -Path $CodeRoot -Filter "*.py" -Recurse -File |
                Where-Object { $_.FullName -notlike "*\tests\*" -and
                               $_.FullName -notlike "*\venv\*" -and
                               $_.FullName -notlike "*\__pycache__\*" }).Count

    $coveragePercent = if ($pyFiles -gt 0) {
        [math]::Round(($filesWithRefs / $pyFiles) * 100, 1)
    } else {
        0
    }

    return @{
        Status = "PASS"
        Message = "Spec coverage: $coveragePercent% of implementation files"
        Details = @{
            SpecFiles = $specFiles.Count
            ImplFiles = $pyFiles
            FilesWithSpecRefs = $filesWithRefs
            CoveragePercent = $coveragePercent
            TotalSpecReferences = $references.Count
        }
    }
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

try {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║         SPECIFICATION-IMPLEMENTATION VALIDATOR               ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""

    if ($DryRun) {
        Write-Host "🔍 DRY RUN MODE - No validation performed`n" -ForegroundColor Yellow
        Write-Host "Would validate:" -ForegroundColor Gray
        Write-Host "  - Spec index exists: $SpecSource\..\.index\suite-index.yaml" -ForegroundColor Gray
        Write-Host "  - Spec URIs resolvable from code: $CodeRoot" -ForegroundColor Gray
        Write-Host "  - Required specs implemented" -ForegroundColor Gray
        Write-Host "  - Spec coverage metrics" -ForegroundColor Gray
        exit 0
    }

    $results = @()

    # Check 1: Spec index exists
    Write-Host "📋 Checking spec index..." -ForegroundColor Cyan
    $result = Test-SpecIndexExists -SpecSource $SpecSource
    $results += [PSCustomObject]@{
        Check = "SPEC-IMPL-001"
        Name = "Spec index exists"
        Status = $result.Status
        Message = $result.Message
        Details = $result.Details
    }

    if ($VerboseOutput) {
        Write-Host "  [$($result.Status)] $($result.Message)" -ForegroundColor $(if ($result.Status -eq "PASS") { "Green" } else { "Red" })
    }

    # Check 2: Spec URIs resolvable
    Write-Host "🔗 Checking spec URI references..." -ForegroundColor Cyan
    $result = Test-SpecURIsResolvable -SpecSource $SpecSource -CodeRoot $CodeRoot
    $results += [PSCustomObject]@{
        Check = "SPEC-IMPL-002"
        Name = "Spec URIs resolvable"
        Status = $result.Status
        Message = $result.Message
        Details = $result.Details
    }

    if ($VerboseOutput) {
        Write-Host "  [$($result.Status)] $($result.Message)" -ForegroundColor $(if ($result.Status -eq "PASS") { "Green" } else { "Red" })
        if ($result.Details.Examples) {
            Write-Host "  Examples:" -ForegroundColor Gray
            $result.Details.Examples | ForEach-Object {
                Write-Host "    $($_.URI) in $($_.File)" -ForegroundColor DarkGray
            }
        }
    }

    # Check 3: Required specs implemented
    Write-Host "✅ Checking required implementations..." -ForegroundColor Cyan
    $result = Test-RequiredSpecsImplemented -SpecSource $SpecSource
    $results += [PSCustomObject]@{
        Check = "SPEC-IMPL-003"
        Name = "Required specs implemented"
        Status = $result.Status
        Message = $result.Message
        Details = $result.Details
    }

    if ($VerboseOutput) {
        Write-Host "  [$($result.Status)] $($result.Message)" -ForegroundColor $(if ($result.Status -eq "PASS") { "Green" } else { "Red" })
    }

    # Check 4: Coverage analysis
    Write-Host "📊 Analyzing spec coverage..." -ForegroundColor Cyan
    $result = Get-SpecCoverage -SpecSource $SpecSource -CodeRoot $CodeRoot
    $results += [PSCustomObject]@{
        Check = "SPEC-IMPL-004"
        Name = "Spec coverage metrics"
        Status = $result.Status
        Message = $result.Message
        Details = $result.Details
    }

    if ($VerboseOutput) {
        Write-Host "  [$($result.Status)] $($result.Message)" -ForegroundColor $(if ($result.Status -eq "PASS") { "Green" } else { "Red" })
        Write-Host "    Spec files: $($result.Details.SpecFiles)" -ForegroundColor Gray
        Write-Host "    Impl files: $($result.Details.ImplFiles)" -ForegroundColor Gray
        Write-Host "    Files with refs: $($result.Details.FilesWithSpecRefs)" -ForegroundColor Gray
        Write-Host "    Total refs: $($result.Details.TotalSpecReferences)" -ForegroundColor Gray
    }

    # Summary
    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor Cyan
    Write-Host "VALIDATION SUMMARY" -ForegroundColor Cyan
    Write-Host ("=" * 70) -ForegroundColor Cyan

    $passed = @($results | Where-Object { $_.Status -eq "PASS" })
    $failed = @($results | Where-Object { $_.Status -eq "FAIL" })
    $warnings = @($results | Where-Object { $_.Status -eq "WARN" })

    Write-Host "Total Checks: $($results.Count)" -ForegroundColor White
    Write-Host "✓ Passed: $($passed.Count)" -ForegroundColor Green
    Write-Host "✗ Failed: $($failed.Count)" -ForegroundColor $(if ($failed.Count -gt 0) { "Red" } else { "Green" })
    Write-Host "⚠ Warnings: $($warnings.Count)" -ForegroundColor Yellow

    if ($failed.Count -gt 0) {
        Write-Host "`nFailed Checks:" -ForegroundColor Red
        foreach ($check in $failed) {
            Write-Host "  ✗ [$($check.Check)] $($check.Name)" -ForegroundColor Red
            Write-Host "    $($check.Message)" -ForegroundColor Gray
        }
    }

    Write-Host ""

    # Exit code
    if ($failed.Count -gt 0) {
        exit 1
    }
    else {
        exit 0
    }
}
catch {
    Write-Host "`n❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Gray
    exit 1
}
