# DOC_LINK: DOC-SCRIPT-PATTERN-DIR-CHECK-111
# PATTERN_DIR_CHECK.ps1
# Validates patterns/ directory against PAT-CHECK-001 compliance
# Version: 1.0.0

param([switch]$Verbose)

$ErrorActionPreference = "Continue"
$baseDir = Split-Path $PSScriptRoot -Parent
$patternsDir = Join-Path $baseDir "patterns"

$results = @{}
$passed = 0
$failed = 0

Write-Host "=== PAT-CHECK-001 COMPLIANCE VALIDATION ===" -ForegroundColor Cyan

# PAT-CHECK-001-001: patterns/ directory exists
$check = "PAT-CHECK-001-001"
$results[$check] = Test-Path $patternsDir
if ($results[$check]) {
    Write-Host "✓ $check`: patterns/ directory exists" -ForegroundColor Green
    $passed++
} else {
    Write-Host "✗ $check`: patterns/ directory missing" -ForegroundColor Red
    $failed++
}

# PAT-CHECK-001-002: Required subdirectories exist
$requiredDirs = @("registry", "specs", "schemas", "executors", "examples", "tests")
foreach ($dir in $requiredDirs) {
    $check = "PAT-CHECK-001-002-$dir"
    $results[$check] = Test-Path (Join-Path $patternsDir $dir)
    if ($results[$check]) {
        Write-Host "✓ $check`: $dir/ exists" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "✗ $check`: $dir/ missing" -ForegroundColor Red
        $failed++
    }
}

# PAT-CHECK-001-010: PATTERN_INDEX.yaml exists
$check = "PAT-CHECK-001-010"
$indexPath = Join-Path $patternsDir "registry\PATTERN_INDEX.yaml"
$results[$check] = Test-Path $indexPath
if ($results[$check]) {
    Write-Host "✓ $check`: PATTERN_INDEX.yaml exists" -ForegroundColor Green
    $passed++
} else {
    Write-Host "✗ $check`: PATTERN_INDEX.yaml missing" -ForegroundColor Red
    $failed++
}

# PAT-CHECK-001-011: Pattern entries have required fields
if ($results["PAT-CHECK-001-010"]) {
    $check = "PAT-CHECK-001-011"
    $content = Get-Content $indexPath -Raw
    $hasDocId = $content -match "doc_id:"
    $hasPatternId = $content -match "pattern_id:"
    $hasName = $content -match "name:"

    $results[$check] = $hasDocId -and $hasPatternId -and $hasName
    if ($results[$check]) {
        Write-Host "✓ $check`: Pattern entries have required fields" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "✗ $check`: Missing required fields in pattern entries" -ForegroundColor Red
        $failed++
    }
}

# Summary
Write-Host "`n=== SUMMARY ===" -ForegroundColor Cyan
Write-Host "Passed: $passed" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor $(if ($failed -eq 0) { 'Green' } else { 'Red' })

if ($failed -eq 0) {
    Write-Host "`n✓ FULL COMPLIANCE" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n✗ COMPLIANCE FAILURES" -ForegroundColor Red
    exit 1
}
