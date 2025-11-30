# DOC_LINK: DOC-SCRIPT-CLEANUP-HIGH-CONFIDENCE-20251125-090442-048
# Automated Cleanup Script (High Confidence)
# Generated: 2025-11-25T15:04:42.565071+00:00
# Confidence Threshold: 85%

$ErrorActionPreference = 'Stop'
$RepoRoot = 'C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan'

Write-Host '=== High Confidence Cleanup ===' -ForegroundColor Cyan
Write-Host 'Review this script before running!' -ForegroundColor Yellow
Write-Host ''

$DryRun = $false  # Execute deletions

function Invoke-Removal {
    param(
        [string]$RelativePath,
        [switch]$Directory
    )

    $fullPath = Join-Path $RepoRoot $RelativePath
    if (-not (Test-Path $fullPath)) {
        Write-Host "Skip (not found): $RelativePath" -ForegroundColor DarkGray
        return
    }

    if ($Directory) {
        Remove-Item -Path $fullPath -Recurse -Force
    } else {
        Remove-Item -Path $fullPath -Force
    }

    Write-Host "Deleted: $RelativePath" -ForegroundColor Green
}

# CCPM commands duplicated (Confidence: 95%)
# Note: Deleting parent directory ccpm/ccpm/ covers all subdirectories
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: ccpm/ccpm/' -ForegroundColor Yellow
} else {
    Invoke-Removal 'ccpm/ccpm/' -Directory
}

# Pattern extraction tools duplicated (Confidence: 90%)
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/pattern_extraction/' -ForegroundColor Yellow
} else {
    Invoke-Removal 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/pattern_extraction/' -Directory
}

# ai-logs-analyzer\aggregated\.gitkeep
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ai-logs-analyzer\analysis\summary-report-20251124-104847.json, aim\registry\__init__.py, aim\tests\registry\__init__.py
# Duplicate of: aim\registry\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: ai-logs-analyzer\aggregated\.gitkeep' -ForegroundColor Yellow
} else {
    Invoke-Removal 'ai-logs-analyzer\aggregated\.gitkeep'
}

# ai-logs-analyzer\analysis\.gitkeep
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ai-logs-analyzer\analysis\summary-report-20251124-104847.json, aim\registry\__init__.py, aim\tests\registry\__init__.py
# Duplicate of: aim\registry\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: ai-logs-analyzer\analysis\.gitkeep' -ForegroundColor Yellow
} else {
    Invoke-Removal 'ai-logs-analyzer\analysis\.gitkeep'
}

# ai-logs-analyzer\analysis\summary-report-20251124-104847.json
# Confidence: 95% | Score: 43
# Reasons: Exact duplicate of: aim\registry\__init__.py, aim\tests\registry\__init__.py, engine\queue\__init__.py; Filename indicates versioning/backup
# Duplicate of: aim\registry\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: ai-logs-analyzer\analysis\summary-report-20251124-104847.json' -ForegroundColor Yellow
} else {
    Invoke-Removal 'ai-logs-analyzer\analysis\summary-report-20251124-104847.json'
}

# ai-logs-analyzer\exports\.gitkeep
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ai-logs-analyzer\analysis\summary-report-20251124-104847.json, aim\registry\__init__.py, aim\tests\registry\__init__.py
# Duplicate of: aim\registry\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: ai-logs-analyzer\exports\.gitkeep' -ForegroundColor Yellow
} else {
    Invoke-Removal 'ai-logs-analyzer\exports\.gitkeep'
}

# aim\.AIM_ai-tools-registry\logs\error.log
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ai-logs-analyzer\analysis\summary-report-20251124-104847.json, aim\registry\__init__.py, aim\tests\registry\__init__.py
# Duplicate of: aim\registry\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: aim\.AIM_ai-tools-registry\logs\error.log' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'aim\.AIM_ai-tools-registry\logs\error.log') -Force
    Write-Host 'Deleted: aim\.AIM_ai-tools-registry\logs\error.log' -ForegroundColor Green
}

# aim\.AIM_ai-tools-registry\logs\interactions.log
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ai-logs-analyzer\analysis\summary-report-20251124-104847.json, aim\registry\__init__.py, aim\tests\registry\__init__.py
# Duplicate of: aim\registry\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: aim\.AIM_ai-tools-registry\logs\interactions.log' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'aim\.AIM_ai-tools-registry\logs\interactions.log') -Force
    Write-Host 'Deleted: aim\.AIM_ai-tools-registry\logs\interactions.log' -ForegroundColor Green
}

# aim\registry\__init__.py
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ai-logs-analyzer\analysis\summary-report-20251124-104847.json, aim\tests\registry\__init__.py, engine\queue\__init__.py
# Duplicate of: aim\tests\registry\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: aim\registry\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'aim\registry\__init__.py') -Force
    Write-Host 'Deleted: aim\registry\__init__.py' -ForegroundColor Green
}

# aim\tests\registry\__init__.py
# Confidence: 95% | Score: 42
# Reasons: Exact duplicate of: ai-logs-analyzer\analysis\summary-report-20251124-104847.json, aim\registry\__init__.py, engine\queue\__init__.py; Superseded by canonical module in tools
# Duplicate of: aim\registry\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: aim\tests\registry\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'aim\tests\registry\__init__.py') -Force
    Write-Host 'Deleted: aim\tests\registry\__init__.py' -ForegroundColor Green
}

# ccpm\ccpm\scripts\check-path-standards.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: pm\scripts\check-path-standards.sh, scripts\check-path-standards.sh
# Duplicate of: pm\scripts\check-path-standards.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: ccpm\ccpm\scripts\check-path-standards.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'ccpm\ccpm\scripts\check-path-standards.sh') -Force
    Write-Host 'Deleted: ccpm\ccpm\scripts\check-path-standards.sh' -ForegroundColor Green
}

# ccpm\ccpm\scripts\fix-path-standards.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: pm\scripts\fix-path-standards.sh, scripts\fix-path-standards.sh
# Duplicate of: pm\scripts\fix-path-standards.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: ccpm\ccpm\scripts\fix-path-standards.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'ccpm\ccpm\scripts\fix-path-standards.sh') -Force
    Write-Host 'Deleted: ccpm\ccpm\scripts\fix-path-standards.sh' -ForegroundColor Green
}

# ccpm\ccpm\scripts\test-and-log.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: pm\scripts\test-and-log.sh
# Duplicate of: pm\scripts\test-and-log.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: ccpm\ccpm\scripts\test-and-log.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'ccpm\ccpm\scripts\test-and-log.sh') -Force
    Write-Host 'Deleted: ccpm\ccpm\scripts\test-and-log.sh' -ForegroundColor Green
}

# ccpm\ccpm\scripts\pm\blocked.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: pm\scripts\pm\blocked.sh
# Duplicate of: pm\scripts\pm\blocked.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: ccpm\ccpm\scripts\pm\blocked.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'ccpm\ccpm\scripts\pm\blocked.sh') -Force
    Write-Host 'Deleted: ccpm\ccpm\scripts\pm\blocked.sh' -ForegroundColor Green
}

# ccpm\ccpm\scripts\pm\epic-list.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: pm\scripts\pm\epic-list.sh
# Duplicate of: pm\scripts\pm\epic-list.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: ccpm\ccpm\scripts\pm\epic-list.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'ccpm\ccpm\scripts\pm\epic-list.sh') -Force
    Write-Host 'Deleted: ccpm\ccpm\scripts\pm\epic-list.sh' -ForegroundColor Green
}

# ccpm\ccpm\scripts\pm\epic-show.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: pm\scripts\pm\epic-show.sh
# Duplicate of: pm\scripts\pm\epic-show.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: ccpm\ccpm\scripts\pm\epic-show.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'ccpm\ccpm\scripts\pm\epic-show.sh') -Force
    Write-Host 'Deleted: ccpm\ccpm\scripts\pm\epic-show.sh' -ForegroundColor Green
}

# ccpm\ccpm\scripts\pm\epic-status.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: pm\scripts\pm\epic-status.sh
# Duplicate of: pm\scripts\pm\epic-status.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: ccpm\ccpm\scripts\pm\epic-status.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'ccpm\ccpm\scripts\pm\epic-status.sh') -Force
    Write-Host 'Deleted: ccpm\ccpm\scripts\pm\epic-status.sh' -ForegroundColor Green
}

# ccpm\ccpm\scripts\pm\help.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: pm\scripts\pm\help.sh
# Duplicate of: pm\scripts\pm\help.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: ccpm\ccpm\scripts\pm\help.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'ccpm\ccpm\scripts\pm\help.sh') -Force
    Write-Host 'Deleted: ccpm\ccpm\scripts\pm\help.sh' -ForegroundColor Green
}

# ccpm\ccpm\scripts\pm\in-progress.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: pm\scripts\pm\in-progress.sh
# Duplicate of: pm\scripts\pm\in-progress.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: ccpm\ccpm\scripts\pm\in-progress.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'ccpm\ccpm\scripts\pm\in-progress.sh') -Force
    Write-Host 'Deleted: ccpm\ccpm\scripts\pm\in-progress.sh' -ForegroundColor Green
}

# ccpm\ccpm\scripts\pm\init.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: pm\scripts\pm\init.sh
# Duplicate of: pm\scripts\pm\init.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: ccpm\ccpm\scripts\pm\init.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'ccpm\ccpm\scripts\pm\init.sh') -Force
    Write-Host 'Deleted: ccpm\ccpm\scripts\pm\init.sh' -ForegroundColor Green
}

# ccpm\ccpm\scripts\pm\next.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: pm\scripts\pm\next.sh
# Duplicate of: pm\scripts\pm\next.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: ccpm\ccpm\scripts\pm\next.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'ccpm\ccpm\scripts\pm\next.sh') -Force
    Write-Host 'Deleted: ccpm\ccpm\scripts\pm\next.sh' -ForegroundColor Green
}

# ccpm\ccpm\scripts\pm\prd-list.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: pm\scripts\pm\prd-list.sh
# Duplicate of: pm\scripts\pm\prd-list.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: ccpm\ccpm\scripts\pm\prd-list.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'ccpm\ccpm\scripts\pm\prd-list.sh') -Force
    Write-Host 'Deleted: ccpm\ccpm\scripts\pm\prd-list.sh' -ForegroundColor Green
}

# ccpm\ccpm\scripts\pm\prd-status.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: pm\scripts\pm\prd-status.sh
# Duplicate of: pm\scripts\pm\prd-status.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: ccpm\ccpm\scripts\pm\prd-status.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'ccpm\ccpm\scripts\pm\prd-status.sh') -Force
    Write-Host 'Deleted: ccpm\ccpm\scripts\pm\prd-status.sh' -ForegroundColor Green
}

# ccpm\ccpm\scripts\pm\search.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: pm\scripts\pm\search.sh
# Duplicate of: pm\scripts\pm\search.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: ccpm\ccpm\scripts\pm\search.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'ccpm\ccpm\scripts\pm\search.sh') -Force
    Write-Host 'Deleted: ccpm\ccpm\scripts\pm\search.sh' -ForegroundColor Green
}

# ccpm\ccpm\scripts\pm\standup.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: pm\scripts\pm\standup.sh
# Duplicate of: pm\scripts\pm\standup.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: ccpm\ccpm\scripts\pm\standup.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'ccpm\ccpm\scripts\pm\standup.sh') -Force
    Write-Host 'Deleted: ccpm\ccpm\scripts\pm\standup.sh' -ForegroundColor Green
}

# ccpm\ccpm\scripts\pm\status.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: pm\scripts\pm\status.sh
# Duplicate of: pm\scripts\pm\status.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: ccpm\ccpm\scripts\pm\status.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'ccpm\ccpm\scripts\pm\status.sh') -Force
    Write-Host 'Deleted: ccpm\ccpm\scripts\pm\status.sh' -ForegroundColor Green
}

# ccpm\ccpm\scripts\pm\validate.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: pm\scripts\pm\validate.sh
# Duplicate of: pm\scripts\pm\validate.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: ccpm\ccpm\scripts\pm\validate.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'ccpm\ccpm\scripts\pm\validate.sh') -Force
    Write-Host 'Deleted: ccpm\ccpm\scripts\pm\validate.sh' -ForegroundColor Green
}

# DICKY1987-ORCH-CLAUDE-AIDER-V2\logs\interactions.log
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ai-logs-analyzer\analysis\summary-report-20251124-104847.json, aim\registry\__init__.py, aim\tests\registry\__init__.py
# Duplicate of: aim\registry\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: DICKY1987-ORCH-CLAUDE-AIDER-V2\logs\interactions.log' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'DICKY1987-ORCH-CLAUDE-AIDER-V2\logs\interactions.log') -Force
    Write-Host 'Deleted: DICKY1987-ORCH-CLAUDE-AIDER-V2\logs\interactions.log' -ForegroundColor Green
}

# engine\queue\__init__.py
# Confidence: 95% | Score: 47
# Reasons: Exact duplicate of: ai-logs-analyzer\analysis\summary-report-20251124-104847.json, aim\registry\__init__.py, aim\tests\registry\__init__.py; Not imported and imports nothing (orphaned)
# Duplicate of: aim\registry\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: engine\queue\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'engine\queue\__init__.py') -Force
    Write-Host 'Deleted: engine\queue\__init__.py' -ForegroundColor Green
}

# error\plugins\codespell\__init__.py
# Confidence: 95% | Score: 47
# Reasons: Exact duplicate of: ai-logs-analyzer\analysis\summary-report-20251124-104847.json, aim\registry\__init__.py, aim\tests\registry\__init__.py; Not imported and imports nothing (orphaned)
# Duplicate of: aim\registry\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: error\plugins\codespell\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'error\plugins\codespell\__init__.py') -Force
    Write-Host 'Deleted: error\plugins\codespell\__init__.py' -ForegroundColor Green
}

# error\plugins\gitleaks\__init__.py
# Confidence: 95% | Score: 47
# Reasons: Exact duplicate of: ai-logs-analyzer\analysis\summary-report-20251124-104847.json, aim\registry\__init__.py, aim\tests\registry\__init__.py; Not imported and imports nothing (orphaned)
# Duplicate of: aim\registry\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: error\plugins\gitleaks\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'error\plugins\gitleaks\__init__.py') -Force
    Write-Host 'Deleted: error\plugins\gitleaks\__init__.py' -ForegroundColor Green
}

# error\plugins\json_jq\__init__.py
# Confidence: 95% | Score: 47
# Reasons: Exact duplicate of: ai-logs-analyzer\analysis\summary-report-20251124-104847.json, aim\registry\__init__.py, aim\tests\registry\__init__.py; Not imported and imports nothing (orphaned)
# Duplicate of: aim\registry\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: error\plugins\json_jq\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'error\plugins\json_jq\__init__.py') -Force
    Write-Host 'Deleted: error\plugins\json_jq\__init__.py' -ForegroundColor Green
}

# error\plugins\js_eslint\__init__.py
# Confidence: 95% | Score: 47
# Reasons: Exact duplicate of: ai-logs-analyzer\analysis\summary-report-20251124-104847.json, aim\registry\__init__.py, aim\tests\registry\__init__.py; Not imported and imports nothing (orphaned)
# Duplicate of: aim\registry\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: error\plugins\js_eslint\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'error\plugins\js_eslint\__init__.py') -Force
    Write-Host 'Deleted: error\plugins\js_eslint\__init__.py' -ForegroundColor Green
}

# error\plugins\js_prettier_fix\__init__.py
# Confidence: 95% | Score: 47
# Reasons: Exact duplicate of: ai-logs-analyzer\analysis\summary-report-20251124-104847.json, aim\registry\__init__.py, aim\tests\registry\__init__.py; Not imported and imports nothing (orphaned)
# Duplicate of: aim\registry\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: error\plugins\js_prettier_fix\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'error\plugins\js_prettier_fix\__init__.py') -Force
    Write-Host 'Deleted: error\plugins\js_prettier_fix\__init__.py' -ForegroundColor Green
}

# error\plugins\md_markdownlint\__init__.py
# Confidence: 95% | Score: 47
# Reasons: Exact duplicate of: ai-logs-analyzer\analysis\summary-report-20251124-104847.json, aim\registry\__init__.py, aim\tests\registry\__init__.py; Not imported and imports nothing (orphaned)
# Duplicate of: aim\registry\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: error\plugins\md_markdownlint\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'error\plugins\md_markdownlint\__init__.py') -Force
    Write-Host 'Deleted: error\plugins\md_markdownlint\__init__.py' -ForegroundColor Green
}

# error\plugins\md_mdformat_fix\__init__.py
# Confidence: 95% | Score: 47
# Reasons: Exact duplicate of: ai-logs-analyzer\analysis\summary-report-20251124-104847.json, aim\registry\__init__.py, aim\tests\registry\__init__.py; Not imported and imports nothing (orphaned)
# Duplicate of: aim\registry\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: error\plugins\md_mdformat_fix\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'error\plugins\md_mdformat_fix\__init__.py') -Force
    Write-Host 'Deleted: error\plugins\md_mdformat_fix\__init__.py' -ForegroundColor Green
}

# error\plugins\powershell_pssa\__init__.py
# Confidence: 95% | Score: 47
# Reasons: Exact duplicate of: ai-logs-analyzer\analysis\summary-report-20251124-104847.json, aim\registry\__init__.py, aim\tests\registry\__init__.py; Not imported and imports nothing (orphaned)
# Duplicate of: aim\registry\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: error\plugins\powershell_pssa\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'error\plugins\powershell_pssa\__init__.py') -Force
    Write-Host 'Deleted: error\plugins\powershell_pssa\__init__.py' -ForegroundColor Green
}

# error\plugins\semgrep\__init__.py
# Confidence: 95% | Score: 47
# Reasons: Exact duplicate of: ai-logs-analyzer\analysis\summary-report-20251124-104847.json, aim\registry\__init__.py, aim\tests\registry\__init__.py; Not imported and imports nothing (orphaned)
# Duplicate of: aim\registry\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: error\plugins\semgrep\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'error\plugins\semgrep\__init__.py') -Force
    Write-Host 'Deleted: error\plugins\semgrep\__init__.py' -ForegroundColor Green
}

# error\plugins\yaml_yamllint\__init__.py
# Confidence: 95% | Score: 47
# Reasons: Exact duplicate of: ai-logs-analyzer\analysis\summary-report-20251124-104847.json, aim\registry\__init__.py, aim\tests\registry\__init__.py; Not imported and imports nothing (orphaned)
# Duplicate of: aim\registry\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: error\plugins\yaml_yamllint\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'error\plugins\yaml_yamllint\__init__.py') -Force
    Write-Host 'Deleted: error\plugins\yaml_yamllint\__init__.py' -ForegroundColor Green
}

# logs\error.log
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ai-logs-analyzer\analysis\summary-report-20251124-104847.json, aim\registry\__init__.py, aim\tests\registry\__init__.py
# Duplicate of: aim\registry\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: logs\error.log' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'logs\error.log') -Force
    Write-Host 'Deleted: logs\error.log' -ForegroundColor Green
}

# logs\interactions.log
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ai-logs-analyzer\analysis\summary-report-20251124-104847.json, aim\registry\__init__.py, aim\tests\registry\__init__.py
# Duplicate of: aim\registry\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: logs\interactions.log' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'logs\interactions.log') -Force
    Write-Host 'Deleted: logs\interactions.log' -ForegroundColor Green
}

# pm\scripts\check-path-standards.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ccpm\ccpm\scripts\check-path-standards.sh, scripts\check-path-standards.sh
# Duplicate of: scripts\check-path-standards.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: pm\scripts\check-path-standards.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'pm\scripts\check-path-standards.sh') -Force
    Write-Host 'Deleted: pm\scripts\check-path-standards.sh' -ForegroundColor Green
}

# pm\scripts\fix-path-standards.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ccpm\ccpm\scripts\fix-path-standards.sh, scripts\fix-path-standards.sh
# Duplicate of: scripts\fix-path-standards.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: pm\scripts\fix-path-standards.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'pm\scripts\fix-path-standards.sh') -Force
    Write-Host 'Deleted: pm\scripts\fix-path-standards.sh' -ForegroundColor Green
}

# pm\scripts\test-and-log.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ccpm\ccpm\scripts\test-and-log.sh
# Duplicate of: ccpm\ccpm\scripts\test-and-log.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: pm\scripts\test-and-log.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'pm\scripts\test-and-log.sh') -Force
    Write-Host 'Deleted: pm\scripts\test-and-log.sh' -ForegroundColor Green
}

# pm\scripts\pm\blocked.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ccpm\ccpm\scripts\pm\blocked.sh
# Duplicate of: ccpm\ccpm\scripts\pm\blocked.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: pm\scripts\pm\blocked.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'pm\scripts\pm\blocked.sh') -Force
    Write-Host 'Deleted: pm\scripts\pm\blocked.sh' -ForegroundColor Green
}

# pm\scripts\pm\epic-list.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ccpm\ccpm\scripts\pm\epic-list.sh
# Duplicate of: ccpm\ccpm\scripts\pm\epic-list.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: pm\scripts\pm\epic-list.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'pm\scripts\pm\epic-list.sh') -Force
    Write-Host 'Deleted: pm\scripts\pm\epic-list.sh' -ForegroundColor Green
}

# pm\scripts\pm\epic-show.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ccpm\ccpm\scripts\pm\epic-show.sh
# Duplicate of: ccpm\ccpm\scripts\pm\epic-show.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: pm\scripts\pm\epic-show.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'pm\scripts\pm\epic-show.sh') -Force
    Write-Host 'Deleted: pm\scripts\pm\epic-show.sh' -ForegroundColor Green
}

# pm\scripts\pm\epic-status.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ccpm\ccpm\scripts\pm\epic-status.sh
# Duplicate of: ccpm\ccpm\scripts\pm\epic-status.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: pm\scripts\pm\epic-status.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'pm\scripts\pm\epic-status.sh') -Force
    Write-Host 'Deleted: pm\scripts\pm\epic-status.sh' -ForegroundColor Green
}

# pm\scripts\pm\help.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ccpm\ccpm\scripts\pm\help.sh
# Duplicate of: ccpm\ccpm\scripts\pm\help.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: pm\scripts\pm\help.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'pm\scripts\pm\help.sh') -Force
    Write-Host 'Deleted: pm\scripts\pm\help.sh' -ForegroundColor Green
}

# pm\scripts\pm\in-progress.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ccpm\ccpm\scripts\pm\in-progress.sh
# Duplicate of: ccpm\ccpm\scripts\pm\in-progress.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: pm\scripts\pm\in-progress.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'pm\scripts\pm\in-progress.sh') -Force
    Write-Host 'Deleted: pm\scripts\pm\in-progress.sh' -ForegroundColor Green
}

# pm\scripts\pm\init.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ccpm\ccpm\scripts\pm\init.sh
# Duplicate of: ccpm\ccpm\scripts\pm\init.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: pm\scripts\pm\init.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'pm\scripts\pm\init.sh') -Force
    Write-Host 'Deleted: pm\scripts\pm\init.sh' -ForegroundColor Green
}

# pm\scripts\pm\next.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ccpm\ccpm\scripts\pm\next.sh
# Duplicate of: ccpm\ccpm\scripts\pm\next.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: pm\scripts\pm\next.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'pm\scripts\pm\next.sh') -Force
    Write-Host 'Deleted: pm\scripts\pm\next.sh' -ForegroundColor Green
}

# pm\scripts\pm\prd-list.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ccpm\ccpm\scripts\pm\prd-list.sh
# Duplicate of: ccpm\ccpm\scripts\pm\prd-list.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: pm\scripts\pm\prd-list.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'pm\scripts\pm\prd-list.sh') -Force
    Write-Host 'Deleted: pm\scripts\pm\prd-list.sh' -ForegroundColor Green
}

# pm\scripts\pm\prd-status.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ccpm\ccpm\scripts\pm\prd-status.sh
# Duplicate of: ccpm\ccpm\scripts\pm\prd-status.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: pm\scripts\pm\prd-status.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'pm\scripts\pm\prd-status.sh') -Force
    Write-Host 'Deleted: pm\scripts\pm\prd-status.sh' -ForegroundColor Green
}

# pm\scripts\pm\search.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ccpm\ccpm\scripts\pm\search.sh
# Duplicate of: ccpm\ccpm\scripts\pm\search.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: pm\scripts\pm\search.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'pm\scripts\pm\search.sh') -Force
    Write-Host 'Deleted: pm\scripts\pm\search.sh' -ForegroundColor Green
}

# pm\scripts\pm\standup.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ccpm\ccpm\scripts\pm\standup.sh
# Duplicate of: ccpm\ccpm\scripts\pm\standup.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: pm\scripts\pm\standup.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'pm\scripts\pm\standup.sh') -Force
    Write-Host 'Deleted: pm\scripts\pm\standup.sh' -ForegroundColor Green
}

# pm\scripts\pm\status.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ccpm\ccpm\scripts\pm\status.sh
# Duplicate of: ccpm\ccpm\scripts\pm\status.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: pm\scripts\pm\status.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'pm\scripts\pm\status.sh') -Force
    Write-Host 'Deleted: pm\scripts\pm\status.sh' -ForegroundColor Green
}

# pm\scripts\pm\validate.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ccpm\ccpm\scripts\pm\validate.sh
# Duplicate of: ccpm\ccpm\scripts\pm\validate.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: pm\scripts\pm\validate.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'pm\scripts\pm\validate.sh') -Force
    Write-Host 'Deleted: pm\scripts\pm\validate.sh' -ForegroundColor Green
}

# scripts\check-path-standards.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ccpm\ccpm\scripts\check-path-standards.sh, pm\scripts\check-path-standards.sh
# Duplicate of: pm\scripts\check-path-standards.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: scripts\check-path-standards.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'scripts\check-path-standards.sh') -Force
    Write-Host 'Deleted: scripts\check-path-standards.sh' -ForegroundColor Green
}

# scripts\fix-path-standards.sh
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ccpm\ccpm\scripts\fix-path-standards.sh, pm\scripts\fix-path-standards.sh
# Duplicate of: pm\scripts\fix-path-standards.sh
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: scripts\fix-path-standards.sh' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'scripts\fix-path-standards.sh') -Force
    Write-Host 'Deleted: scripts\fix-path-standards.sh' -ForegroundColor Green
}

# specifications\tools\__init__.py
# Confidence: 95% | Score: 47
# Reasons: Exact duplicate of: specifications\tools\guard\__init__.py, specifications\tools\indexer\__init__.py, specifications\tools\patcher\__init__.py; Not imported and imports nothing (orphaned)
# Duplicate of: specifications\tools\guard\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: specifications\tools\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'specifications\tools\__init__.py') -Force
    Write-Host 'Deleted: specifications\tools\__init__.py' -ForegroundColor Green
}

# specifications\tools\guard\__init__.py
# Confidence: 95% | Score: 47
# Reasons: Exact duplicate of: specifications\tools\__init__.py, specifications\tools\indexer\__init__.py, specifications\tools\patcher\__init__.py; Not imported and imports nothing (orphaned)
# Duplicate of: specifications\tools\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: specifications\tools\guard\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'specifications\tools\guard\__init__.py') -Force
    Write-Host 'Deleted: specifications\tools\guard\__init__.py' -ForegroundColor Green
}

# specifications\tools\indexer\__init__.py
# Confidence: 95% | Score: 47
# Reasons: Exact duplicate of: specifications\tools\__init__.py, specifications\tools\guard\__init__.py, specifications\tools\patcher\__init__.py; Not imported and imports nothing (orphaned)
# Duplicate of: specifications\tools\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: specifications\tools\indexer\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'specifications\tools\indexer\__init__.py') -Force
    Write-Host 'Deleted: specifications\tools\indexer\__init__.py' -ForegroundColor Green
}

# specifications\tools\patcher\__init__.py
# Confidence: 95% | Score: 47
# Reasons: Exact duplicate of: specifications\tools\__init__.py, specifications\tools\guard\__init__.py, specifications\tools\indexer\__init__.py; Not imported and imports nothing (orphaned)
# Duplicate of: specifications\tools\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: specifications\tools\patcher\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'specifications\tools\patcher\__init__.py') -Force
    Write-Host 'Deleted: specifications\tools\patcher\__init__.py' -ForegroundColor Green
}

# specifications\tools\renderer\__init__.py
# Confidence: 95% | Score: 47
# Reasons: Exact duplicate of: specifications\tools\__init__.py, specifications\tools\guard\__init__.py, specifications\tools\indexer\__init__.py; Not imported and imports nothing (orphaned)
# Duplicate of: specifications\tools\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: specifications\tools\renderer\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'specifications\tools\renderer\__init__.py') -Force
    Write-Host 'Deleted: specifications\tools\renderer\__init__.py' -ForegroundColor Green
}

# specifications\tools\resolver\__init__.py
# Confidence: 95% | Score: 47
# Reasons: Exact duplicate of: specifications\tools\__init__.py, specifications\tools\guard\__init__.py, specifications\tools\indexer\__init__.py; Not imported and imports nothing (orphaned)
# Duplicate of: specifications\tools\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: specifications\tools\resolver\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'specifications\tools\resolver\__init__.py') -Force
    Write-Host 'Deleted: specifications\tools\resolver\__init__.py' -ForegroundColor Green
}

# tests\test.py
# Confidence: 95% | Score: 47
# Reasons: Exact duplicate of: ai-logs-analyzer\analysis\summary-report-20251124-104847.json, aim\registry\__init__.py, aim\tests\registry\__init__.py; Not imported and imports nothing (orphaned)
# Duplicate of: aim\registry\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: tests\test.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'tests\test.py') -Force
    Write-Host 'Deleted: tests\test.py' -ForegroundColor Green
}

# ToDo_Task\Phase_K_Plus_Complete_2025-11-22_142319\phase-k-plus-bundle.json
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: workstreams\.deferred\phase-k-plus-bundle.json
# Duplicate of: workstreams\.deferred\phase-k-plus-bundle.json
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: ToDo_Task\Phase_K_Plus_Complete_2025-11-22_142319\phase-k-plus-bundle.json' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'ToDo_Task\Phase_K_Plus_Complete_2025-11-22_142319\phase-k-plus-bundle.json') -Force
    Write-Host 'Deleted: ToDo_Task\Phase_K_Plus_Complete_2025-11-22_142319\phase-k-plus-bundle.json' -ForegroundColor Green
}

# tools\hardcoded_path_indexer.py
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: tools\legacy\hardcoded_path_indexer.py
# Duplicate of: tools\legacy\hardcoded_path_indexer.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: tools\hardcoded_path_indexer.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'tools\hardcoded_path_indexer.py') -Force
    Write-Host 'Deleted: tools\hardcoded_path_indexer.py' -ForegroundColor Green
}

# tools\legacy\hardcoded_path_indexer.py
# Confidence: 95% | Score: 77
# Reasons: Exact duplicate of: tools\hardcoded_path_indexer.py; Path contains 'legacy'; Superseded by canonical module in tools; Not imported by any file
# Duplicate of: tools\hardcoded_path_indexer.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: tools\legacy\hardcoded_path_indexer.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'tools\legacy\hardcoded_path_indexer.py') -Force
    Write-Host 'Deleted: tools\legacy\hardcoded_path_indexer.py' -ForegroundColor Green
}

# tools\pattern-extraction\__init__.py
# Confidence: 95% | Score: 47
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\__init__.py; Not imported and imports nothing (orphaned)
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: tools\pattern-extraction\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'tools\pattern-extraction\__init__.py') -Force
    Write-Host 'Deleted: tools\pattern-extraction\__init__.py' -ForegroundColor Green
}

# tools\pattern-extraction\detectors\base_detector.py
# Confidence: 95% | Score: 40
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\base_detector.py; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\base_detector.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: tools\pattern-extraction\detectors\base_detector.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'tools\pattern-extraction\detectors\base_detector.py') -Force
    Write-Host 'Deleted: tools\pattern-extraction\detectors\base_detector.py' -ForegroundColor Green
}

# tools\pattern-extraction\detectors\parallel_detector.py
# Confidence: 95% | Score: 40
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\parallel_detector.py; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\parallel_detector.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: tools\pattern-extraction\detectors\parallel_detector.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'tools\pattern-extraction\detectors\parallel_detector.py') -Force
    Write-Host 'Deleted: tools\pattern-extraction\detectors\parallel_detector.py' -ForegroundColor Green
}

# tools\pattern-extraction\detectors\sequential_detector.py
# Confidence: 95% | Score: 40
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\sequential_detector.py; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\sequential_detector.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: tools\pattern-extraction\detectors\sequential_detector.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'tools\pattern-extraction\detectors\sequential_detector.py') -Force
    Write-Host 'Deleted: tools\pattern-extraction\detectors\sequential_detector.py' -ForegroundColor Green
}

# tools\pattern-extraction\detectors\template_detector.py
# Confidence: 95% | Score: 60
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\template_detector.py; Path contains 'temp'; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\template_detector.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: tools\pattern-extraction\detectors\template_detector.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'tools\pattern-extraction\detectors\template_detector.py') -Force
    Write-Host 'Deleted: tools\pattern-extraction\detectors\template_detector.py' -ForegroundColor Green
}

# tools\pattern-extraction\detectors\__init__.py
# Confidence: 95% | Score: 40
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\__init__.py; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: tools\pattern-extraction\detectors\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'tools\pattern-extraction\detectors\__init__.py') -Force
    Write-Host 'Deleted: tools\pattern-extraction\detectors\__init__.py' -ForegroundColor Green
}

# tools\pattern-extraction\generators\yaml_template_generator.py
# Confidence: 95% | Score: 60
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\generators\yaml_template_generator.py; Path contains 'temp'; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\generators\yaml_template_generator.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: tools\pattern-extraction\generators\yaml_template_generator.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'tools\pattern-extraction\generators\yaml_template_generator.py') -Force
    Write-Host 'Deleted: tools\pattern-extraction\generators\yaml_template_generator.py' -ForegroundColor Green
}

# tools\pattern-extraction\generators\__init__.py
# Confidence: 95% | Score: 40
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\generators\__init__.py; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\generators\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: tools\pattern-extraction\generators\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'tools\pattern-extraction\generators\__init__.py') -Force
    Write-Host 'Deleted: tools\pattern-extraction\generators\__init__.py' -ForegroundColor Green
}

# tools\pattern-extraction\parsers\base_parser.py
# Confidence: 95% | Score: 40
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\parsers\base_parser.py; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\parsers\base_parser.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: tools\pattern-extraction\parsers\base_parser.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'tools\pattern-extraction\parsers\base_parser.py') -Force
    Write-Host 'Deleted: tools\pattern-extraction\parsers\base_parser.py' -ForegroundColor Green
}

# tools\pattern-extraction\parsers\claude_parser.py
# Confidence: 95% | Score: 40
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\parsers\claude_parser.py; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\parsers\claude_parser.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: tools\pattern-extraction\parsers\claude_parser.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'tools\pattern-extraction\parsers\claude_parser.py') -Force
    Write-Host 'Deleted: tools\pattern-extraction\parsers\claude_parser.py' -ForegroundColor Green
}

# tools\pattern-extraction\parsers\copilot_parser.py
# Confidence: 95% | Score: 40
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\parsers\copilot_parser.py; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\parsers\copilot_parser.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: tools\pattern-extraction\parsers\copilot_parser.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'tools\pattern-extraction\parsers\copilot_parser.py') -Force
    Write-Host 'Deleted: tools\pattern-extraction\parsers\copilot_parser.py' -ForegroundColor Green
}

# tools\pattern-extraction\parsers\__init__.py
# Confidence: 95% | Score: 40
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\parsers\__init__.py; Not imported by any file
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\parsers\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: tools\pattern-extraction\parsers\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'tools\pattern-extraction\parsers\__init__.py') -Force
    Write-Host 'Deleted: tools\pattern-extraction\parsers\__init__.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\base_plan.json
# Confidence: 95% | Score: 45
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\master_plan\base_plan.json; Path contains 'temp'
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\master_plan\base_plan.json
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\base_plan.json' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\base_plan.json') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\base_plan.json' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\.meta\archive\patches\001-config-integration.json
# Confidence: 95% | Score: 45
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\patches\001-config-integration.json; Path contains 'archive'
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\patches\001-config-integration.json
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\.meta\archive\patches\001-config-integration.json' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\.meta\archive\patches\001-config-integration.json') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\.meta\archive\patches\001-config-integration.json' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\bootstrap\__init__.py
# Confidence: 95% | Score: 85
# Reasons: Exact duplicate of: ai-logs-analyzer\analysis\summary-report-20251124-104847.json, aim\registry\__init__.py, aim\tests\registry\__init__.py; Path contains 'temp'; Superseded by canonical module in tools; Not imported and imports nothing (orphaned)
# Duplicate of: aim\registry\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\bootstrap\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\bootstrap\__init__.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\bootstrap\__init__.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\master_plan\base_plan.json
# Confidence: 95% | Score: 45
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\base_plan.json; Path contains 'temp'
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\base_plan.json
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\master_plan\base_plan.json' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\master_plan\base_plan.json') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\master_plan\base_plan.json' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\master_plan\UET_V2_MASTER_PLAN.json
# Confidence: 95% | Score: 45
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\master_plan\archive\UET_V2_MASTER_PLAN_backup_20251124_025411.json; Path contains 'temp'
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\master_plan\archive\UET_V2_MASTER_PLAN_backup_20251124_025411.json
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\master_plan\UET_V2_MASTER_PLAN.json' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\master_plan\UET_V2_MASTER_PLAN.json') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\master_plan\UET_V2_MASTER_PLAN.json' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\master_plan\archive\UET_V2_MASTER_PLAN_backup_20251124_025411.json
# Confidence: 95% | Score: 63
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\master_plan\UET_V2_MASTER_PLAN.json; Path contains 'archive'; Filename indicates versioning/backup
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\master_plan\UET_V2_MASTER_PLAN.json
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\master_plan\archive\UET_V2_MASTER_PLAN_backup_20251124_025411.json' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\master_plan\archive\UET_V2_MASTER_PLAN_backup_20251124_025411.json') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\master_plan\archive\UET_V2_MASTER_PLAN_backup_20251124_025411.json' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\patches\001-config-integration.json
# Confidence: 95% | Score: 45
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\.meta\archive\patches\001-config-integration.json; Path contains 'temp'
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\.meta\archive\patches\001-config-integration.json
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\patches\001-config-integration.json' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\patches\001-config-integration.json') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\patches\001-config-integration.json' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\patterns\scripts\pattern_cli.ps1
# Confidence: 95% | Score: 45
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_cli.ps1; Path contains 'temp'
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_cli.ps1
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\patterns\scripts\pattern_cli.ps1' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\patterns\scripts\pattern_cli.ps1') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\patterns\scripts\pattern_cli.ps1' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_cli.ps1
# Confidence: 95% | Score: 45
# Reasons: Exact duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\patterns\scripts\pattern_cli.ps1; Path contains 'temp'
# Duplicate of: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\patterns\scripts\pattern_cli.ps1
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_cli.ps1' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_cli.ps1') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_cli.ps1' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\__init__.py
# Confidence: 95% | Score: 85
# Reasons: Exact duplicate of: tools\pattern-extraction\__init__.py; Path contains 'temp'; Superseded by canonical module in tools; Not imported and imports nothing (orphaned)
# Duplicate of: tools\pattern-extraction\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\__init__.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\__init__.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\base_detector.py
# Confidence: 95% | Score: 77
# Reasons: Exact duplicate of: tools\pattern-extraction\detectors\base_detector.py; Path contains 'temp'; Superseded by canonical module in tools; Not imported by any file
# Duplicate of: tools\pattern-extraction\detectors\base_detector.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\base_detector.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\base_detector.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\base_detector.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\parallel_detector.py
# Confidence: 95% | Score: 77
# Reasons: Exact duplicate of: tools\pattern-extraction\detectors\parallel_detector.py; Path contains 'temp'; Superseded by canonical module in tools; Not imported by any file
# Duplicate of: tools\pattern-extraction\detectors\parallel_detector.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\parallel_detector.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\parallel_detector.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\parallel_detector.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\sequential_detector.py
# Confidence: 95% | Score: 77
# Reasons: Exact duplicate of: tools\pattern-extraction\detectors\sequential_detector.py; Path contains 'temp'; Superseded by canonical module in tools; Not imported by any file
# Duplicate of: tools\pattern-extraction\detectors\sequential_detector.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\sequential_detector.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\sequential_detector.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\sequential_detector.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\template_detector.py
# Confidence: 95% | Score: 77
# Reasons: Exact duplicate of: tools\pattern-extraction\detectors\template_detector.py; Path contains 'temp'; Superseded by canonical module in tools; Not imported by any file
# Duplicate of: tools\pattern-extraction\detectors\template_detector.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\template_detector.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\template_detector.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\template_detector.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\__init__.py
# Confidence: 95% | Score: 77
# Reasons: Exact duplicate of: tools\pattern-extraction\detectors\__init__.py; Path contains 'temp'; Superseded by canonical module in tools; Not imported by any file
# Duplicate of: tools\pattern-extraction\detectors\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\__init__.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\detectors\__init__.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\generators\yaml_template_generator.py
# Confidence: 95% | Score: 77
# Reasons: Exact duplicate of: tools\pattern-extraction\generators\yaml_template_generator.py; Path contains 'temp'; Superseded by canonical module in tools; Not imported by any file
# Duplicate of: tools\pattern-extraction\generators\yaml_template_generator.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\generators\yaml_template_generator.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\generators\yaml_template_generator.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\generators\yaml_template_generator.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\generators\__init__.py
# Confidence: 95% | Score: 77
# Reasons: Exact duplicate of: tools\pattern-extraction\generators\__init__.py; Path contains 'temp'; Superseded by canonical module in tools; Not imported by any file
# Duplicate of: tools\pattern-extraction\generators\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\generators\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\generators\__init__.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\generators\__init__.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\parsers\base_parser.py
# Confidence: 95% | Score: 77
# Reasons: Exact duplicate of: tools\pattern-extraction\parsers\base_parser.py; Path contains 'temp'; Superseded by canonical module in tools; Not imported by any file
# Duplicate of: tools\pattern-extraction\parsers\base_parser.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\parsers\base_parser.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\parsers\base_parser.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\parsers\base_parser.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\parsers\claude_parser.py
# Confidence: 95% | Score: 77
# Reasons: Exact duplicate of: tools\pattern-extraction\parsers\claude_parser.py; Path contains 'temp'; Superseded by canonical module in tools; Not imported by any file
# Duplicate of: tools\pattern-extraction\parsers\claude_parser.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\parsers\claude_parser.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\parsers\claude_parser.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\parsers\claude_parser.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\parsers\copilot_parser.py
# Confidence: 95% | Score: 77
# Reasons: Exact duplicate of: tools\pattern-extraction\parsers\copilot_parser.py; Path contains 'temp'; Superseded by canonical module in tools; Not imported by any file
# Duplicate of: tools\pattern-extraction\parsers\copilot_parser.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\parsers\copilot_parser.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\parsers\copilot_parser.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\parsers\copilot_parser.py' -ForegroundColor Green
}

# UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\parsers\__init__.py
# Confidence: 95% | Score: 77
# Reasons: Exact duplicate of: tools\pattern-extraction\parsers\__init__.py; Path contains 'temp'; Superseded by canonical module in tools; Not imported by any file
# Duplicate of: tools\pattern-extraction\parsers\__init__.py
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\parsers\__init__.py' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\parsers\__init__.py') -Force
    Write-Host 'Deleted: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\scripts\pattern_extraction\parsers\__init__.py' -ForegroundColor Green
}

# workstreams\phase-k-plus-bundle.json.backup
# Confidence: 95% | Score: 45
# Reasons: Exact duplicate of: ToDo_Task\Phase_K_Plus_Complete_2025-11-22_142319\phase-k-plus-bundle.json, workstreams\.deferred\phase-k-plus-bundle.json; Path contains 'backup'
# Duplicate of: workstreams\.deferred\phase-k-plus-bundle.json
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: workstreams\phase-k-plus-bundle.json.backup' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'workstreams\phase-k-plus-bundle.json.backup') -Force
    Write-Host 'Deleted: workstreams\phase-k-plus-bundle.json.backup' -ForegroundColor Green
}

# workstreams\.deferred\phase-k-plus-bundle.json
# Confidence: 95% | Score: 25
# Reasons: Exact duplicate of: ToDo_Task\Phase_K_Plus_Complete_2025-11-22_142319\phase-k-plus-bundle.json
# Duplicate of: ToDo_Task\Phase_K_Plus_Complete_2025-11-22_142319\phase-k-plus-bundle.json
if ($DryRun) {
    Write-Host '[DRY-RUN] Would delete: workstreams\.deferred\phase-k-plus-bundle.json' -ForegroundColor Yellow
} else {
    Remove-Item -Path (Join-Path $RepoRoot 'workstreams\.deferred\phase-k-plus-bundle.json') -Force
    Write-Host 'Deleted: workstreams\.deferred\phase-k-plus-bundle.json' -ForegroundColor Green
}


Write-Host ''
Write-Host 'Summary:' -ForegroundColor Cyan
Write-Host '  Items to delete: 108'
Write-Host '  Space to save: 1,051,415 bytes (1.00 MB)'
