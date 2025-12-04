<#
.SYNOPSIS
  Filter CSV to remove all completed implementation/development tracking files,
  keeping only active planning documents.

.DESCRIPTION
  Removes files that match patterns indicating they are:
  - Completed work (COMPLETE, COMPLETED, COMPLETION)
  - Implementation tracking (IMPLEMENTATION, EXECUTION, SESSION reports)
  - Progress/status reports (PROGRESS, STATUS, SUMMARY)
  - Final reports (FINAL_REPORT, FINAL_SESSION)
  - Development artifacts from specific phases/workstreams

  Keeps files that are:
  - Active plans (PLAN that's not a completion report)
  - Quick references (QUICKSTART, QUICK_REF)
  - Current guidance (GUIDE, ROADMAP)
  - Specifications (spec.md, README.md)

.PARAMETER InputCSV
  Path to the input CSV file (default: file_index_20251201_092302.csv)

.PARAMETER OutputCSV
  Path to the output filtered CSV file
#>

param(
    [string]$InputCSV = "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\file_index_20251201_092302.csv",
    [string]$OutputCSV = "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\active_plans_filtered.csv"
)

if (-not (Test-Path -LiteralPath $InputCSV)) {
    Write-Error "Input CSV not found: $InputCSV"
    exit 1
}

Write-Host "Reading from: $InputCSV"

# Import the CSV
$allFiles = Import-Csv -Path $InputCSV

Write-Host "Total files in CSV: $($allFiles.Count)"

# Define exclusion patterns (files to REMOVE)
$excludePatterns = @(
    # Completion markers
    '*COMPLETE.md',
    '*COMPLETED.md',
    '*COMPLETION*.md',

    # Implementation/execution tracking
    '*IMPLEMENTATION*.md',
    '*EXECUTION*.md',

    # Session reports and summaries
    '*SESSION*.md',
    '*SUMMARY*.md',
    '*REPORT.md',
    '*FINAL*.md',

    # Progress tracking
    '*PROGRESS*.md',
    '*STATUS*.md',

    # Specific development folders
    '*\developer\*',
    '*\doc_id\session_reports\*',
    '*\doc_id\reports\*REPORT*.md',
    '*\doc_id\analysis\*',
    '*\doc_id\batches\*',
    '*\doc_id\deltas\*',
    '*\infra\sync\*COMPLETE*.md',
    '*\infra\sync\*INSTALLATION*.md',
    '*\infra\sync\*SETUP*.md',
    '*\infra\sync\*TEST*.md',

    # Day/Week tracking
    '*DAY*.md',
    '*WEEK*.md',

    # Migration tracking
    '*MIGRATION*COMPLETE*.md',
    '*MIGRATION*SUCCESS*.md',
    '*MIGRATION*EXECUTION*.md',

    # Cleanup reports
    '*CLEANUP*COMPLETE*.md',
    '*CLEANUP*REPORT*.md',

    # Specific historical docs
    '*COMMITS_LAST*.md',
    '*REFACTOR*STATUS*.md',
    '*OVERLAP*REPORT*.md',

    # OpenSpec changes (completed proposals)
    '*\openspec\changes\uet-001-complete-implementation\*',

    # Example/template reports
    '*EXAMPLE_GOOD_SESSION*.md',

    # Module READMEs (auto-generated stubs)
    '*\modules\*\*_README.md',

    # Sync logs
    '*.sync-log.txt',

    # Analysis text dumps
    '*import_migration_analysis.txt',
    '*module_refactor_attempt*.txt',
    '*just need to create*.txt',
    '*repo_tree.txt',

    # Response files
    'response_*.md',

    # Glossary completion tracking
    '*\glossary\*COMPLETE*.md',
    '*\glossary\updates\*COMPLETE*.md',

    # GUI implementation tracking
    '*\gui\docs\*IMPLEMENTATION*.md',
    '*\gui\docs\*COMPLETION*.md',
    '*\gui\docs\*SUMMARY*.md',

    # Template examples (not templates themselves)
    '*TEMPLATE_EXPANSION_PHASE_PLAN.md',

    # Speed demon implementation
    '*\tools\speed_demon\IMPLEMENTATION_COMPLETE.md',

    # Test cache
    '*.pytest_cache\*',

    # AIDER tracking
    '*AIDER*FIXES*.md',
    '*AIDER*ANALYSIS*.md',
    '*AIDER*TEST*.md',
    '*AIDER*SETUP*.md',

    # Specific one-off files
    '*5_Phase Completion Plan*.md',
    '*AGENT_SUMMARY.txt',
    '*Code Cleanup Analysis.txt',
    '*comprehensive machine-readable*.txt',
    '*GUI is a hybrid*.txt',
    '*asafterthemoverepo.txt'
)

# Files to explicitly KEEP (override exclusions if needed)
$keepPatterns = @(
    # Core planning
    '*PHASE_PLAN.md',
    '*\plans\PLAN_*.md',

    # Quick starts and guides
    '*QUICKSTART*.md',
    '*QUICK_REF*.md',
    '*GUIDE.md',
    '*ROADMAP.md',

    # Specifications
    '*\specs\*.md',
    '*\specifications\content\*\spec.md',

    # README files (documentation hubs)
    'README.md',

    # Reference documentation
    '*\docs\reference\*',

    # Active OpenSpec proposals (not complete)
    '*\openspec\changes\uet-001-phase-*.md',
    '*\openspec\specs\*.md'
)

# Filter logic
$filteredFiles = $allFiles | Where-Object {
    $filePath = $_.FullPath

    # Check if explicitly kept
    $isKept = $false
    foreach ($keepPattern in $keepPatterns) {
        if ($filePath -like $keepPattern) {
            $isKept = $true
            break
        }
    }

    # If explicitly kept, include it
    if ($isKept) {
        return $true
    }

    # Check if excluded
    $isExcluded = $false
    foreach ($excludePattern in $excludePatterns) {
        if ($filePath -like $excludePattern) {
            $isExcluded = $true
            break
        }
    }

    # Keep if NOT excluded
    return -not $isExcluded
}

# Export filtered results
$filteredFiles | Export-Csv -Path $OutputCSV -NoTypeInformation -Encoding UTF8

Write-Host ""
Write-Host "=== FILTERING RESULTS ==="
Write-Host "Original count:  $($allFiles.Count)"
Write-Host "Filtered count:  $($filteredFiles.Count)"
Write-Host "Removed:         $($allFiles.Count - $filteredFiles.Count)"
Write-Host ""
Write-Host "Output written to: $OutputCSV"
