#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Extract patterns from atomic-workflow-system atoms registry
    
.DESCRIPTION
    Phase 5: Migration script
    Converts atoms to UET patterns with proper naming and structure
    
.NOTES
    Source: patterns/legacy_atoms/source/atoms.registry.jsonl
    Target: patterns/legacy_atoms/converted/
#>

$ErrorActionPreference = "Stop"

Write-Host "Phase 5: Atomic Workflow Migration" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

# Paths
$sourceRegistry = "patterns\legacy_atoms\source\atoms.registry.jsonl"
$convertedDir = "patterns\legacy_atoms\converted"
$specsDir = "$convertedDir\specs"
$reportFile = "$convertedDir\reports\EXTRACTION_REPORT.md"

# Create output directories
@($specsDir, "$convertedDir\schemas", "$convertedDir\executors", "$convertedDir\examples", "$convertedDir\reports") | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
    }
}

Write-Host "`nLoading atoms registry..." -ForegroundColor Yellow
$atoms = Get-Content $sourceRegistry | ForEach-Object { $_ | ConvertFrom-Json }
Write-Host "  Total atoms: $($atoms.Count)" -ForegroundColor Green

# Analyze by role
Write-Host "`nAnalyzing atom roles..." -ForegroundColor Yellow
$roleGroups = $atoms | Group-Object -Property role | Sort-Object Count -Descending

$report = @"
# Atomic Workflow System - Extraction Report

**Generated**: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")  
**Source**: atomic-workflow-system repository  
**Total Atoms**: $($atoms.Count)

## Atom Distribution by Role

| Role | Count | Selected for Migration |
|------|-------|------------------------|
"@

$roleGroups | ForEach-Object {
    $selected = if ($_.Count -ge 10) { "✅" } else { "⬜" }
    $report += "`n| $($_.Name) | $($_.Count) | $selected |"
}

# Select top 20 atoms across key roles
$targetRoles = @('orchestrator', 'executor', 'validator', 'creator', 'modifier', 'analyzer', 'dispatcher', 'coordinator', 'monitor')
$selectedAtoms = @()

foreach ($role in $targetRoles) {
    $roleAtoms = $atoms | Where-Object { $_.role -eq $role } | Select-Object -First 5
    $selectedAtoms += $roleAtoms
}

# Also select from top overall roles
$topRoles = $roleGroups | Select-Object -First 5
foreach ($roleGroup in $topRoles) {
    $additional = $atoms | Where-Object { $_.role -eq $roleGroup.Name } | Select-Object -First 3
    $selectedAtoms += $additional
}

# Remove duplicates
$selectedAtoms = $selectedAtoms | Sort-Object atom_uid -Unique

Write-Host "  Selected atoms for migration: $($selectedAtoms.Count)" -ForegroundColor Green

$report += "`n`n## Selected Atoms for Migration`n`n"
$report += "| # | Atom UID | Title | Role | Category |`n"
$report += "|---|----------|-------|------|----------|`n"

$migrationSeq = 1
$migratedPatterns = @()

foreach ($atom in $selectedAtoms) {
    # Determine category from role
    $category = switch ($atom.role) {
        "creator" { "CLI" }
        "modifier" { "PATCH" }
        "validator" { "VERIFY" }
        "orchestrator" { "ORCHESTRATE" }
        "executor" { "EXEC" }
        "analyzer" { "ANALYZE" }
        default { "CORE" }
    }
    
    $patternId = "PAT-MIGRATED-$category-$('{0:D3}' -f $migrationSeq)"
    $patternName = "migrated_$($atom.role)_$('{0:D3}' -f $migrationSeq)"
    
    $report += "| $migrationSeq | $($atom.atom_uid) | $($atom.title) | $($atom.role) | $category |`n"
    
    # Create minimal pattern spec
    $specContent = @"
# Migrated Pattern: $($atom.title)
# Pattern ID: $patternId
# Original Atom UID: $($atom.atom_uid)
# Original Role: $($atom.role)
# Source: atomic-workflow-system
# Migrated: $(Get-Date -Format "yyyy-MM-dd")

pattern_id: "$patternId"
name: "$patternName"
version: "1.0.0"
category: "$($category.ToLower())"
status: "migrated"

metadata:
  migrated_from: "atomic-workflow-system"
  original_atom_uid: "$($atom.atom_uid)"
  original_atom_key: "$($atom.atom_key)"
  original_role: "$($atom.role)"
  source_doc: "$($atom.source_doc)"
  migration_date: "$(Get-Date -Format "yyyy-MM-dd")"
  migration_sequence: $migrationSeq

intent: |
  Migrated from: $($atom.title)
  Original atom role: $($atom.role)
  
  This pattern was automatically migrated from the atomic-workflow-system.
  Review and enhance before production use.

applicability:
  when_to_use:
    - "Refer to original atom documentation"
  when_not_to_use:
    - "Pattern requires manual review and enhancement"

inputs:
  # TO BE DEFINED based on original atom requirements
  placeholder: true

outputs:
  # TO BE DEFINED based on original atom outputs
  placeholder: true

execution_steps:
  - step_id: "S1_placeholder"
    description: "Review original atom: $($atom.atom_uid)"

compliance:
  requirements:
    - "PAT-CHECK-002"  # Migrated pattern compliance
"@
    
    # Write spec file
    $specFile = Join-Path $specsDir "$patternName.pattern.yaml"
    $specContent | Out-File -FilePath $specFile -Encoding UTF8
    
    $migratedPatterns += @{
        pattern_id = $patternId
        name = $patternName
        category = $category.ToLower()
        original_uid = $atom.atom_uid
        original_role = $atom.role
        title = $atom.title
        spec_path = "patterns/legacy_atoms/converted/specs/$patternName.pattern.yaml"
    }
    
    $migrationSeq++
}

Write-Host "`n  Created $($migratedPatterns.Count) pattern specs" -ForegroundColor Green

# Write report
$report += "`n`n## Migration Summary`n`n"
$report += "- Total atoms analyzed: $($atoms.Count)`n"
$report += "- Atoms migrated: $($migratedPatterns.Count)`n"
$report += "- Pattern specs created: $($migratedPatterns.Count)`n"
$report += "- Status: Draft (requires review)`n"
$report += "`n## Next Steps`n`n"
$report += "1. Review generated pattern specs`n"
$report += "2. Enhance with detailed inputs/outputs`n"
$report += "3. Create JSON schemas`n"
$report += "4. Implement executors for high-priority patterns`n"
$report += "5. Update pattern status from 'migrated' to 'draft' after review`n"

$report | Out-File -FilePath $reportFile -Encoding UTF8

Write-Host "`n✅ Migration complete!" -ForegroundColor Green
Write-Host "  Report: $reportFile" -ForegroundColor Cyan
Write-Host "  Specs: $specsDir" -ForegroundColor Cyan

# Output summary for registry update
$migratedPatterns | ConvertTo-Json -Depth 3 | Out-File "patterns\legacy_atoms\converted\PATTERN_INDEX_entries.json" -Encoding UTF8
Write-Host "  Registry entries: patterns\legacy_atoms\converted\PATTERN_INDEX_entries.json" -ForegroundColor Cyan

Write-Host "`nMigrated patterns ready for review and integration." -ForegroundColor Yellow
