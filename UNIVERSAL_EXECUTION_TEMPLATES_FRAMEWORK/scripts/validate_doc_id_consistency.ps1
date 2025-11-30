# DOC_LINK: DOC-SCRIPT-VALIDATE-DOC-ID-CONSISTENCY-113
# validate_doc_id_consistency.ps1
# Validates doc_id consistency across all artifacts
# Per ID-SYSTEM-SPEC-V1

param([switch]$Verbose)

$ErrorActionPreference = "Continue"
$baseDir = Split-Path $PSScriptRoot -Parent
$patternsDir = Join-Path $baseDir "patterns"

Write-Host "=== DOC_ID CONSISTENCY VALIDATION ===" -ForegroundColor Cyan

$passed = 0
$failed = 0

# Check 1: doc_id format compliance (ID-SYS-101)
Write-Host "`n[Check 1] doc_id Format Compliance" -ForegroundColor Yellow

$indexPath = Join-Path $patternsDir "registry\PATTERN_INDEX.yaml"
if (Test-Path $indexPath) {
    $content = Get-Content $indexPath -Raw
    $docIds = [regex]::Matches($content, 'doc_id:\s+([A-Z0-9-]+)')
    
    foreach ($match in $docIds) {
        $docId = $match.Groups[1].Value
        if ($docId -match '^[A-Z0-9]+(-[A-Z0-9]+)*$') {
            Write-Host "  ✓ $docId (valid format)" -ForegroundColor Green
            $passed++
        } else {
            Write-Host "  ✗ $docId (invalid format)" -ForegroundColor Red
            $failed++
        }
    }
}

# Check 2: doc_id uniqueness
Write-Host "`n[Check 2] doc_id Uniqueness" -ForegroundColor Yellow

$docIdList = @($docIds | ForEach-Object { $_.Groups[1].Value })
$duplicates = $docIdList | Group-Object | Where-Object { $_.Count -gt 1 }

if ($duplicates) {
    foreach ($dup in $duplicates) {
        Write-Host "  ✗ Duplicate doc_id: $($dup.Name)" -ForegroundColor Red
        $failed++
    }
} else {
    Write-Host "  ✓ All doc_id values are unique" -ForegroundColor Green
    $passed++
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
