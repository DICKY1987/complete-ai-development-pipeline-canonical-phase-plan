# Automated Cleanup Script (High Confidence)
# Generated: 2025-12-02T17:54:55.781537+00:00
# Confidence Threshold: 90%

$ErrorActionPreference = 'Stop'
$RepoRoot = 'C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan'

Write-Host '=== High Confidence Cleanup ===' -ForegroundColor Cyan
Write-Host 'Review this script before running!' -ForegroundColor Yellow
Write-Host ''

$DryRun = $true  # Change to $false to execute

# archive\2025-11-30_060626_engine-consolidation\root-engine-init-backup.py
# Confidence: 95% | Score: 50
# Reasons: Exact duplicate of: archive\2025-11-30_060626_engine-consolidation\root-engine-jobqueue\__init__.py; Path contains 'archive'; Not imported and imports nothing (orphaned)
# Duplicate of: archive\2025-11-30_060626_engine-consolidation\root-engine-jobqueue\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-11-30_060626_engine-consolidation\root-engine-init-backup.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-11-30_060626_engine-consolidation\root-engine-init-backup.py') -Force
    Write-Host 'Deleted: archive\2025-11-30_060626_engine-consolidation\root-engine-init-backup.py' -ForegroundColor Green
}

# archive\2025-11-30_060626_engine-consolidation\root-engine-jobqueue\__init__.py
# Confidence: 95% | Score: 50
# Reasons: Exact duplicate of: archive\2025-11-30_060626_engine-consolidation\root-engine-init-backup.py; Path contains 'archive'; Not imported and imports nothing (orphaned)
# Duplicate of: archive\2025-11-30_060626_engine-consolidation\root-engine-init-backup.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-11-30_060626_engine-consolidation\root-engine-jobqueue\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-11-30_060626_engine-consolidation\root-engine-jobqueue\__init__.py') -Force
    Write-Host 'Deleted: archive\2025-11-30_060626_engine-consolidation\root-engine-jobqueue\__init__.py' -ForegroundColor Green
}

# archive\2025-11-30_060626_engine-consolidation\root-engine-jobqueue\orchestrator\__main__.py
# Confidence: 95% | Score: 46
# Reasons: Exact duplicate of: engine\orchestrator\__main__.py; Path contains 'archive'; Not imported by any file
# Duplicate of: engine\orchestrator\__main__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-11-30_060626_engine-consolidation\root-engine-jobqueue\orchestrator\__main__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-11-30_060626_engine-consolidation\root-engine-jobqueue\orchestrator\__main__.py') -Force
    Write-Host 'Deleted: archive\2025-11-30_060626_engine-consolidation\root-engine-jobqueue\orchestrator\__main__.py' -ForegroundColor Green
}

# archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\context_estimator.py
# Confidence: 95% | Score: 46
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\context_estimator.py; Path contains 'archive'; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\context_estimator.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\context_estimator.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\context_estimator.py') -Force
    Write-Host 'Deleted: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\context_estimator.py' -ForegroundColor Green
}

# archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\cost_tracker.py
# Confidence: 95% | Score: 46
# Reasons: Exact duplicate of: archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\cost_tracker.py, UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\cost_tracker.py; Path contains 'archive'; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\cost_tracker.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\cost_tracker.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\cost_tracker.py') -Force
    Write-Host 'Deleted: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\cost_tracker.py' -ForegroundColor Green
}

# archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\dag_builder.py
# Confidence: 95% | Score: 46
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\dag_builder.py; Path contains 'archive'; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\dag_builder.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\dag_builder.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\dag_builder.py') -Force
    Write-Host 'Deleted: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\dag_builder.py' -ForegroundColor Green
}

# archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\execution_request_builder.py
# Confidence: 95% | Score: 46
# Reasons: Exact duplicate of: archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\execution_request_builder.py, UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\execution_request_builder.py; Path contains 'archive'; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\execution_request_builder.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\execution_request_builder.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\execution_request_builder.py') -Force
    Write-Host 'Deleted: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\execution_request_builder.py' -ForegroundColor Green
}

# archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\integration_worker.py
# Confidence: 95% | Score: 46
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\integration_worker.py; Path contains 'archive'; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\integration_worker.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\integration_worker.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\integration_worker.py') -Force
    Write-Host 'Deleted: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\integration_worker.py' -ForegroundColor Green
}

# archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\patch_converter.py
# Confidence: 95% | Score: 46
# Reasons: Exact duplicate of: archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\patch_converter.py, UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\patch_converter.py; Path contains 'archive'; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\patch_converter.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\patch_converter.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\patch_converter.py') -Force
    Write-Host 'Deleted: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\patch_converter.py' -ForegroundColor Green
}

# archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\patch_ledger.py
# Confidence: 95% | Score: 46
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\patch_ledger.py; Path contains 'archive'; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\patch_ledger.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\patch_ledger.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\patch_ledger.py') -Force
    Write-Host 'Deleted: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\patch_ledger.py' -ForegroundColor Green
}

# archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\process_spawner.py
# Confidence: 95% | Score: 46
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\process_spawner.py; Path contains 'archive'; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\process_spawner.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\process_spawner.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\process_spawner.py') -Force
    Write-Host 'Deleted: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\process_spawner.py' -ForegroundColor Green
}

# archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\prompt_engine.py
# Confidence: 95% | Score: 46
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\prompt_engine.py; Path contains 'archive'; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\prompt_engine.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\prompt_engine.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\prompt_engine.py') -Force
    Write-Host 'Deleted: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\prompt_engine.py' -ForegroundColor Green
}

# archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\recovery.py
# Confidence: 95% | Score: 46
# Reasons: Exact duplicate of: archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\recovery.py, UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\recovery.py; Path contains 'archive'; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\recovery.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\recovery.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\recovery.py') -Force
    Write-Host 'Deleted: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\recovery.py' -ForegroundColor Green
}

# archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\router.py
# Confidence: 95% | Score: 46
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\router.py; Path contains 'archive'; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\router.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\router.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\router.py') -Force
    Write-Host 'Deleted: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\router.py' -ForegroundColor Green
}

# archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\state_machine.py
# Confidence: 95% | Score: 46
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\state_machine.py; Path contains 'archive'; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\state_machine.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\state_machine.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\state_machine.py') -Force
    Write-Host 'Deleted: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\state_machine.py' -ForegroundColor Green
}

# archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\worker_lifecycle.py
# Confidence: 95% | Score: 46
# Reasons: Exact duplicate of: archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\worker_lifecycle.py, UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\worker_lifecycle.py; Path contains 'archive'; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\worker_lifecycle.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\worker_lifecycle.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\worker_lifecycle.py') -Force
    Write-Host 'Deleted: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\worker_lifecycle.py' -ForegroundColor Green
}

# archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\__init__.py
# Confidence: 95% | Score: 50
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\__init__.py; Path contains 'archive'; Not imported and imports nothing (orphaned)
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\__init__.py') -Force
    Write-Host 'Deleted: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\__init__.py' -ForegroundColor Green
}

# archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\monitoring\progress_tracker.py
# Confidence: 95% | Score: 46
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\monitoring\progress_tracker.py; Path contains 'archive'; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\monitoring\progress_tracker.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\monitoring\progress_tracker.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\monitoring\progress_tracker.py') -Force
    Write-Host 'Deleted: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\monitoring\progress_tracker.py' -ForegroundColor Green
}

# archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\monitoring\__init__.py
# Confidence: 95% | Score: 46
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\monitoring\__init__.py; Path contains 'archive'; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\monitoring\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\monitoring\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\monitoring\__init__.py') -Force
    Write-Host 'Deleted: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\monitoring\__init__.py' -ForegroundColor Green
}

# archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\circuit_breaker.py
# Confidence: 95% | Score: 46
# Reasons: Exact duplicate of: archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\circuit_breaker.py, UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\circuit_breaker.py; Path contains 'archive'; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\circuit_breaker.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\circuit_breaker.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\circuit_breaker.py') -Force
    Write-Host 'Deleted: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\circuit_breaker.py' -ForegroundColor Green
}

# archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\resilient_executor.py
# Confidence: 95% | Score: 46
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\resilient_executor.py; Path contains 'archive'; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\resilient_executor.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\resilient_executor.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\resilient_executor.py') -Force
    Write-Host 'Deleted: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\resilient_executor.py' -ForegroundColor Green
}

# archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\retry.py
# Confidence: 95% | Score: 46
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\retry.py; Path contains 'archive'; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\retry.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\retry.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\retry.py') -Force
    Write-Host 'Deleted: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\retry.py' -ForegroundColor Green
}

# archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\__init__.py
# Confidence: 95% | Score: 46
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\__init__.py; Path contains 'archive'; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\__init__.py') -Force
    Write-Host 'Deleted: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\__init__.py' -ForegroundColor Green
}

# archive\2025-12-01_091928_old-root-folders\core\engine\test_gate.py
# Confidence: 95% | Score: 46
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\test_gate.py; Path contains 'archive'; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\test_gate.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-12-01_091928_old-root-folders\core\engine\test_gate.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-12-01_091928_old-root-folders\core\engine\test_gate.py') -Force
    Write-Host 'Deleted: archive\2025-12-01_091928_old-root-folders\core\engine\test_gate.py' -ForegroundColor Green
}

# archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\cost_tracker.py
# Confidence: 95% | Score: 46
# Reasons: Exact duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\cost_tracker.py, UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\cost_tracker.py; Path contains 'archive'; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\cost_tracker.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\cost_tracker.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\cost_tracker.py') -Force
    Write-Host 'Deleted: archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\cost_tracker.py' -ForegroundColor Green
}

# archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\execution_request_builder.py
# Confidence: 95% | Score: 46
# Reasons: Exact duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\execution_request_builder.py, UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\execution_request_builder.py; Path contains 'archive'; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\execution_request_builder.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\execution_request_builder.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\execution_request_builder.py') -Force
    Write-Host 'Deleted: archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\execution_request_builder.py' -ForegroundColor Green
}

# archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\patch_converter.py
# Confidence: 95% | Score: 46
# Reasons: Exact duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\patch_converter.py, UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\patch_converter.py; Path contains 'archive'; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\patch_converter.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\patch_converter.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\patch_converter.py') -Force
    Write-Host 'Deleted: archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\patch_converter.py' -ForegroundColor Green
}

# archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\recovery.py
# Confidence: 95% | Score: 46
# Reasons: Exact duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\recovery.py, UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\recovery.py; Path contains 'archive'; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\recovery.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\recovery.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\recovery.py') -Force
    Write-Host 'Deleted: archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\recovery.py' -ForegroundColor Green
}

# archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\worker_lifecycle.py
# Confidence: 95% | Score: 46
# Reasons: Exact duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\worker_lifecycle.py, UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\worker_lifecycle.py; Path contains 'archive'; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\worker_lifecycle.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\worker_lifecycle.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\worker_lifecycle.py') -Force
    Write-Host 'Deleted: archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\worker_lifecycle.py' -ForegroundColor Green
}

# archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\circuit_breaker.py
# Confidence: 95% | Score: 46
# Reasons: Exact duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\circuit_breaker.py, UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\circuit_breaker.py; Path contains 'archive'; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\circuit_breaker.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\circuit_breaker.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\circuit_breaker.py') -Force
    Write-Host 'Deleted: archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\circuit_breaker.py' -ForegroundColor Green
}

# engine\orchestrator\__main__.py
# Confidence: 95% | Score: 34
# Reasons: Exact duplicate of: archive\2025-11-30_060626_engine-consolidation\root-engine-jobqueue\orchestrator\__main__.py; Not imported by any file
# Duplicate of: archive\2025-11-30_060626_engine-consolidation\root-engine-jobqueue\orchestrator\__main__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: engine\orchestrator\__main__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'engine\orchestrator\__main__.py') -Force
    Write-Host 'Deleted: engine\orchestrator\__main__.py' -ForegroundColor Green
}

# REFACTOR_2\comprehensive_archival_analyzer.py
# Confidence: 95% | Score: 34
# Reasons: Exact duplicate of: scripts\comprehensive_archival_analyzer.py; Not imported by any file
# Duplicate of: scripts\comprehensive_archival_analyzer.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: REFACTOR_2\comprehensive_archival_analyzer.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'REFACTOR_2\comprehensive_archival_analyzer.py') -Force
    Write-Host 'Deleted: REFACTOR_2\comprehensive_archival_analyzer.py' -ForegroundColor Green
}

# REFACTOR_2\detect_parallel_implementations.py
# Confidence: 95% | Score: 34
# Reasons: Exact duplicate of: scripts\detect_parallel_implementations.py; Not imported by any file
# Duplicate of: scripts\detect_parallel_implementations.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: REFACTOR_2\detect_parallel_implementations.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'REFACTOR_2\detect_parallel_implementations.py') -Force
    Write-Host 'Deleted: REFACTOR_2\detect_parallel_implementations.py' -ForegroundColor Green
}

# REFACTOR_2\entry_point_reachability.py
# Confidence: 95% | Score: 34
# Reasons: Exact duplicate of: scripts\entry_point_reachability.py; Not imported by any file
# Duplicate of: scripts\entry_point_reachability.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: REFACTOR_2\entry_point_reachability.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'REFACTOR_2\entry_point_reachability.py') -Force
    Write-Host 'Deleted: REFACTOR_2\entry_point_reachability.py' -ForegroundColor Green
}

# REFACTOR_2\test_coverage_archival.py
# Confidence: 95% | Score: 34
# Reasons: Exact duplicate of: scripts\test_coverage_archival.py; Not imported by any file
# Duplicate of: scripts\test_coverage_archival.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: REFACTOR_2\test_coverage_archival.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'REFACTOR_2\test_coverage_archival.py') -Force
    Write-Host 'Deleted: REFACTOR_2\test_coverage_archival.py' -ForegroundColor Green
}

# REFACTOR_2\validate_archival_safety.py
# Confidence: 95% | Score: 34
# Reasons: Exact duplicate of: scripts\validate_archival_safety.py; Not imported by any file
# Duplicate of: scripts\validate_archival_safety.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: REFACTOR_2\validate_archival_safety.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'REFACTOR_2\validate_archival_safety.py') -Force
    Write-Host 'Deleted: REFACTOR_2\validate_archival_safety.py' -ForegroundColor Green
}

# scripts\comprehensive_archival_analyzer.py
# Confidence: 95% | Score: 34
# Reasons: Exact duplicate of: REFACTOR_2\comprehensive_archival_analyzer.py; Not imported by any file
# Duplicate of: REFACTOR_2\comprehensive_archival_analyzer.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: scripts\comprehensive_archival_analyzer.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'scripts\comprehensive_archival_analyzer.py') -Force
    Write-Host 'Deleted: scripts\comprehensive_archival_analyzer.py' -ForegroundColor Green
}

# scripts\detect_parallel_implementations.py
# Confidence: 95% | Score: 34
# Reasons: Exact duplicate of: REFACTOR_2\detect_parallel_implementations.py; Not imported by any file
# Duplicate of: REFACTOR_2\detect_parallel_implementations.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: scripts\detect_parallel_implementations.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'scripts\detect_parallel_implementations.py') -Force
    Write-Host 'Deleted: scripts\detect_parallel_implementations.py' -ForegroundColor Green
}

# scripts\entry_point_reachability.py
# Confidence: 95% | Score: 34
# Reasons: Exact duplicate of: REFACTOR_2\entry_point_reachability.py; Not imported by any file
# Duplicate of: REFACTOR_2\entry_point_reachability.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: scripts\entry_point_reachability.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'scripts\entry_point_reachability.py') -Force
    Write-Host 'Deleted: scripts\entry_point_reachability.py' -ForegroundColor Green
}

# scripts\test_coverage_archival.py
# Confidence: 95% | Score: 34
# Reasons: Exact duplicate of: REFACTOR_2\test_coverage_archival.py; Not imported by any file
# Duplicate of: REFACTOR_2\test_coverage_archival.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: scripts\test_coverage_archival.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'scripts\test_coverage_archival.py') -Force
    Write-Host 'Deleted: scripts\test_coverage_archival.py' -ForegroundColor Green
}

# scripts\validate_archival_safety.py
# Confidence: 95% | Score: 34
# Reasons: Exact duplicate of: REFACTOR_2\validate_archival_safety.py; Not imported by any file
# Duplicate of: REFACTOR_2\validate_archival_safety.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: scripts\validate_archival_safety.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'scripts\validate_archival_safety.py') -Force
    Write-Host 'Deleted: scripts\validate_archival_safety.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\context_estimator.py
# Confidence: 95% | Score: 37
# Reasons: Exact duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\context_estimator.py; Path contains 'temp'
# Duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\context_estimator.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\context_estimator.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\context_estimator.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\context_estimator.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\cost_tracker.py
# Confidence: 95% | Score: 37
# Reasons: Exact duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\cost_tracker.py, archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\cost_tracker.py; Path contains 'temp'
# Duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\cost_tracker.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\cost_tracker.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\cost_tracker.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\cost_tracker.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\dag_builder.py
# Confidence: 95% | Score: 37
# Reasons: Exact duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\dag_builder.py; Path contains 'temp'
# Duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\dag_builder.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\dag_builder.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\dag_builder.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\dag_builder.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\execution_request_builder.py
# Confidence: 95% | Score: 37
# Reasons: Exact duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\execution_request_builder.py, archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\execution_request_builder.py; Path contains 'temp'
# Duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\execution_request_builder.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\execution_request_builder.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\execution_request_builder.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\execution_request_builder.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\integration_worker.py
# Confidence: 95% | Score: 37
# Reasons: Exact duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\integration_worker.py; Path contains 'temp'
# Duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\integration_worker.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\integration_worker.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\integration_worker.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\integration_worker.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\patch_converter.py
# Confidence: 95% | Score: 37
# Reasons: Exact duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\patch_converter.py, archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\patch_converter.py; Path contains 'temp'
# Duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\patch_converter.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\patch_converter.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\patch_converter.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\patch_converter.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\patch_ledger.py
# Confidence: 95% | Score: 37
# Reasons: Exact duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\patch_ledger.py; Path contains 'temp'
# Duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\patch_ledger.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\patch_ledger.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\patch_ledger.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\patch_ledger.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\process_spawner.py
# Confidence: 95% | Score: 37
# Reasons: Exact duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\process_spawner.py; Path contains 'temp'
# Duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\process_spawner.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\process_spawner.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\process_spawner.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\process_spawner.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\prompt_engine.py
# Confidence: 95% | Score: 37
# Reasons: Exact duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\prompt_engine.py; Path contains 'temp'
# Duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\prompt_engine.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\prompt_engine.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\prompt_engine.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\prompt_engine.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\recovery.py
# Confidence: 95% | Score: 37
# Reasons: Exact duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\recovery.py, archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\recovery.py; Path contains 'temp'
# Duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\recovery.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\recovery.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\recovery.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\recovery.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\router.py
# Confidence: 95% | Score: 37
# Reasons: Exact duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\router.py; Path contains 'temp'
# Duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\router.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\router.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\router.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\router.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\state_machine.py
# Confidence: 95% | Score: 37
# Reasons: Exact duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\state_machine.py; Path contains 'temp'
# Duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\state_machine.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\state_machine.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\state_machine.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\state_machine.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\test_gate.py
# Confidence: 95% | Score: 37
# Reasons: Exact duplicate of: archive\2025-12-01_091928_old-root-folders\core\engine\test_gate.py; Path contains 'temp'
# Duplicate of: archive\2025-12-01_091928_old-root-folders\core\engine\test_gate.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\test_gate.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\test_gate.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\test_gate.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\worker_lifecycle.py
# Confidence: 95% | Score: 37
# Reasons: Exact duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\worker_lifecycle.py, archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\worker_lifecycle.py; Path contains 'temp'
# Duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\worker_lifecycle.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\worker_lifecycle.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\worker_lifecycle.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\worker_lifecycle.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\__init__.py
# Confidence: 95% | Score: 37
# Reasons: Exact duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\__init__.py; Path contains 'temp'
# Duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\__init__.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\__init__.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\monitoring\progress_tracker.py
# Confidence: 95% | Score: 37
# Reasons: Exact duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\monitoring\progress_tracker.py; Path contains 'temp'
# Duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\monitoring\progress_tracker.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\monitoring\progress_tracker.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\monitoring\progress_tracker.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\monitoring\progress_tracker.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\monitoring\__init__.py
# Confidence: 95% | Score: 37
# Reasons: Exact duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\monitoring\__init__.py; Path contains 'temp'
# Duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\monitoring\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\monitoring\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\monitoring\__init__.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\monitoring\__init__.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\circuit_breaker.py
# Confidence: 95% | Score: 37
# Reasons: Exact duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\circuit_breaker.py, archive\2025-12-02_111954_exec017_migration_cleanup\uet_migration_stage\WS-001\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\circuit_breaker.py; Path contains 'temp'
# Duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\circuit_breaker.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\circuit_breaker.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\circuit_breaker.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\circuit_breaker.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\resilient_executor.py
# Confidence: 95% | Score: 37
# Reasons: Exact duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\resilient_executor.py; Path contains 'temp'
# Duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\resilient_executor.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\resilient_executor.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\resilient_executor.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\resilient_executor.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\retry.py
# Confidence: 95% | Score: 37
# Reasons: Exact duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\retry.py; Path contains 'temp'
# Duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\retry.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\retry.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\retry.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\retry.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\__init__.py
# Confidence: 95% | Score: 37
# Reasons: Exact duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\__init__.py; Path contains 'temp'
# Duplicate of: archive\2025-12-01_090348_root-core-engine-cleanup\core\engine\resilience\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\__init__.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\engine\resilience\__init__.py' -ForegroundColor Green
}


Write-Host ''
Write-Host 'Summary:' -ForegroundColor Cyan
Write-Host '  Items to delete: 62'
Write-Host '  Space to save: 469,007 bytes (0.45 MB)'