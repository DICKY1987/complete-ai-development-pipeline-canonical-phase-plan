# Safe Cleanup Script - Archive Duplicates Only
# Generated: 2025-12-02 (Manually curated from analyzer output)
# Strategy: Only delete files within archive/ folders

$ErrorActionPreference = 'Stop'
$RepoRoot = 'C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan'

Write-Host '=== Safe Archive Cleanup ===' -ForegroundColor Cyan
Write-Host 'Deleting duplicate files from archive/ folders only' -ForegroundColor Green
Write-Host ''

$DryRun = $false  # EXECUTE MODE

# Count and tracking
$deleteCount = 0
$totalSize = 0

# Get all files to delete (only from archive/)
$archiveFiles = @(
    'archive\2025-11-30_060626_engine-consolidation\root-engine-init-backup.py',
    'archive\2025-11-30_060626_engine-consolidation\root-engine-jobqueue\__init__.py',
    'archive\2025-11-30_060626_engine-consolidation\root-engine-jobqueue\orchestrator\__main__.py',
    'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\context_estimator.py',
    'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\cost_tracker.py',
    'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\dag_builder.py',
    'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\execution_request_builder.py',
    'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\integration_worker.py',
    'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\patch_converter.py',
    'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\patch_ledger.py',
    'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\process_spawner.py',
    'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\prompt_engine.py',
    'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\recovery.py',
    'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\router.py',
    'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\state_machine.py',
    'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\worker_lifecycle.py',
    'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\__init__.py',
    'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\monitoring\progress_tracker.py',
    'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\monitoring\__init__.py',
    'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\circuit_breaker.py',
    'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\resilient_executor.py',
    'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\retry.py',
    'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\__init__.py',
    'archive\2025-12-01_091928_old-root-folders\core\engine\test_gate.py',
    'archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\cost_tracker.py',
    'archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\execution_request_builder.py',
    'archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\patch_converter.py',
    'archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\recovery.py',
    'archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\worker_lifecycle.py',
    'archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\circuit_breaker.py'
)

Write-Host "Files to delete: $($archiveFiles.Count)" -ForegroundColor Yellow
Write-Host ""

foreach ($file in $archiveFiles) {
    $fullPath = Join-Path $RepoRoot $file
    
    if (-not (Test-Path $fullPath)) {
        Write-Host "[SKIP] File not found: $file" -ForegroundColor DarkGray
        continue
    }
    
    $fileSize = (Get-Item $fullPath).Length
    $totalSize += $fileSize
    
    if ($DryRun) {
        Write-Host "[DRY-RUN] Would delete: $file" -ForegroundColor Yellow
    } else {
        try {
            Remove-Item -Path $fullPath -Force
            $deleteCount++
            Write-Host "[OK] Deleted: $file" -ForegroundColor Green
        } catch {
            Write-Host "[ERROR] Failed to delete: $file - $_" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "[!] DRY RUN MODE - No files were deleted" -ForegroundColor Yellow
    Write-Host "To execute: Edit this script and set `$DryRun = `$false" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Would delete: $($archiveFiles.Count) files" -ForegroundColor Yellow
    Write-Host "Would free: $([math]::Round($totalSize / 1KB, 2)) KB" -ForegroundColor Yellow
} else {
    Write-Host "[OK] Cleanup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Deleted: $deleteCount files" -ForegroundColor Green
    Write-Host "Freed: $([math]::Round($totalSize / 1KB, 2)) KB" -ForegroundColor Green
}

Write-Host ""
