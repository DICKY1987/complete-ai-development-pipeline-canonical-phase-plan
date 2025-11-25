# Safe Cleanup Script - Individual Files Only
# Generated: 2025-11-25
# Skips already-deleted items

$ErrorActionPreference = 'Continue'
$RepoRoot = 'C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan'

Write-Host "`n=== Cleaning Individual Files ===" -ForegroundColor Cyan
$DeletedCount = 0
$SkippedCount = 0

# List of individual files to delete
$FilesToDelete = @(
    'ai-logs-analyzer\aggregated\.gitkeep',
    'ai-logs-analyzer\analysis\.gitkeep',
    'ai-logs-analyzer\analysis\summary-report-20251124-104847.json',
    'ai-logs-analyzer\exports\.gitkeep',
    'aim\.AIM_ai-tools-registry\logs\error.log',
    'aim\.AIM_ai-tools-registry\logs\interactions.log',
    'logs\error.log',
    'logs\interactions.log',
    'DICKY1987-ORCH-CLAUDE-AIDER-V2\logs\interactions.log',
    'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\base_plan.json',
    'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\.meta\archive\patches\001-config-integration.json',
    'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\master_plan\base_plan.json',
    'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\master_plan\UET_V2_MASTER_PLAN.json',
    'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\master_plan\archive\UET_V2_MASTER_PLAN_backup_20251124_025411.json',
    'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\patches\001-config-integration.json',
    'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\patterns\scripts\pattern_cli.ps1',
    'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_cli.ps1',
    'workstreams\phase-k-plus-bundle.json.backup',
    'workstreams\.deferred\phase-k-plus-bundle.json',
    'tests\test.py',
    'ToDo_Task\Phase_K_Plus_Complete_2025-11-22_142319\phase-k-plus-bundle.json',
    'bootstrap_report.json',
    'core_modules_analysis.json',
    'pattern_analysis.json',
    'processwalk.txt',
    'triage_full_report.txt',
    'WORKTREE1_SESSION_REPORT.md',
    'GLOSSARY_REORGANIZATION_SUMMARY.md'
)

foreach ($File in $FilesToDelete) {
    $FullPath = Join-Path $RepoRoot $File
    
    if (Test-Path $FullPath) {
        try {
            Remove-Item -Path $FullPath -Force
            Write-Host "✓ Deleted: $File" -ForegroundColor Green
            $DeletedCount++
        } catch {
            Write-Host "✗ Failed: $File - $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "⊘ Skipped: $File (already gone)" -ForegroundColor Gray
        $SkippedCount++
    }
}

Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "Deleted: $DeletedCount files" -ForegroundColor Green
Write-Host "Skipped: $SkippedCount files (already deleted)" -ForegroundColor Gray
Write-Host "Total processed: $($FilesToDelete.Count) files"
