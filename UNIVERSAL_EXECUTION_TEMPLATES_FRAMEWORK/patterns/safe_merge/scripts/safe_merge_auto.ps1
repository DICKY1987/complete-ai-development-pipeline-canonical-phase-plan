<#
.SYNOPSIS
    MERGE-004: Safe Merge Automation (Orchestrator)

.DESCRIPTION
    Orchestrates a complete safe merge workflow with rollback capability.
    Combines all patterns into a single automated merge process.

.PARAMETER BaseBranch
    Target branch (e.g., "main")

.PARAMETER FeatureBranch
    Source branch to merge (e.g., "feature/xyz")

.PARAMETER RemoteName
    Remote name (default: "origin")

.PARAMETER BackupNamespace
    Namespace for rollback branches (default: "rollback/pre-merge")

.PARAMETER AllowAutoPush
    Whether to automatically push after successful merge

.PARAMETER ValidationGates
    Array of validation gates to run (default: @("compile", "import"))

.PARAMETER TimestampMergeMode
    Timestamp resolution mode: "off", "conservative", "lww_for_generated"

.OUTPUTS
    SAFE_MERGE_REPORT_<timestamp>.md - Merge report
    safe_merge_report_<timestamp>.json - Machine-readable report
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$BaseBranch,
    
    [Parameter(Mandatory=$true)]
    [string]$FeatureBranch,
    
    [string]$RemoteName = "origin",
    [string]$BackupNamespace = "rollback/pre-merge",
    [switch]$AllowAutoPush,
    [string[]]$ValidationGates = @("compile", "import"),
    [ValidateSet("off", "conservative", "lww_for_generated")]
    [string]$TimestampMergeMode = "off"
)

$ErrorActionPreference = "Stop"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$reportPath = "SAFE_MERGE_REPORT_$timestamp.md"
$reportJsonPath = "safe_merge_report_$timestamp.json"

function Write-MergeLog {
    param([string]$Message, [string]$Level = "INFO")
    
    $color = switch ($Level) {
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "SUCCESS" { "Green" }
        default { "White" }
    }
    
    $logLine = "[$timestamp] [$Level] $Message"
    Write-Host $logLine -ForegroundColor $color
    Add-Content -Path $reportPath -Value $logLine
}

function Invoke-ValidationGate {
    param([string]$Gate)
    
    Write-MergeLog "Running validation gate: $Gate" "INFO"
    
    switch ($Gate) {
        "compile" {
            $result = python -m compileall . -q 2>&1
            return @{
                gate = "compile"
                passed = $LASTEXITCODE -eq 0
                output = $result
            }
        }
        "import" {
            if (Test-Path "scripts\test_imports.py") {
                $result = python scripts\test_imports.py 2>&1
                return @{
                    gate = "import"
                    passed = $LASTEXITCODE -eq 0
                    output = $result
                }
            } else {
                return @{
                    gate = "import"
                    passed = $true
                    output = "No test_imports.py found - skipped"
                    skipped = $true
                }
            }
        }
        "tests" {
            $result = pytest tests/core tests/engine -q 2>&1
            return @{
                gate = "tests"
                passed = $LASTEXITCODE -eq 0
                output = $result
            }
        }
        default {
            return @{
                gate = $Gate
                passed = $true
                output = "Unknown gate - skipped"
                skipped = $true
            }
        }
    }
}

# Initialize report
Write-Host ""
Write-Host "🔄 MERGE-004: Safe Merge Automation" -ForegroundColor Cyan
Write-Host "   Base: $BaseBranch | Feature: $FeatureBranch" -ForegroundColor Gray
Write-Host ""

@"
# Safe Merge Report
**Pattern**: MERGE-004  
**Timestamp**: $timestamp  
**Base Branch**: $BaseBranch  
**Feature Branch**: $FeatureBranch  
**Remote**: $RemoteName  

---

## Execution Log

"@ | Out-File $reportPath

$mergeReport = @{
    pattern_id = "MERGE-004"
    timestamp = $timestamp
    base_branch = $BaseBranch
    feature_branch = $FeatureBranch
    remote = $RemoteName
    phases = @{}
    status = "in_progress"
}

try {
    # ===== PHASE 1: Environment Scan =====
    Write-Host "📋 Phase 1: Environment Scan" -ForegroundColor Yellow
    Write-MergeLog "Running MERGE-001 (Environment Scan)" "INFO"
    
    $envScanScript = Join-Path $PSScriptRoot "merge_env_scan.ps1"
    & $envScanScript -BaseBranch $BaseBranch -FeatureBranch $FeatureBranch -RemoteName $RemoteName
    
    if ($LASTEXITCODE -ne 0) {
        Write-MergeLog "Environment scan detected abort conditions" "ERROR"
        throw "ABORT: Environment scan failed. See env_scan.safe_merge.json for details."
    }
    
    $envScan = Get-Content "env_scan.safe_merge.json" | ConvertFrom-Json
    $mergeReport.phases.env_scan = @{
        status = "passed"
        ahead = $envScan.branches.feature.ahead
        behind = $envScan.branches.feature.behind
        diverged = $envScan.branches.feature.diverged
    }
    
    Write-MergeLog "Environment scan passed" "SUCCESS"
    Write-Host ""
    
    # ===== PHASE 2: Nested Repo Detection =====
    Write-Host "🔍 Phase 2: Nested Repo Detection" -ForegroundColor Yellow
    Write-MergeLog "Running MERGE-003 (Nested Repo Detector)" "INFO"
    
    $nestedRepoScript = Join-Path $PSScriptRoot "nested_repo_detector.py"
    python $nestedRepoScript . --output nested_repos_report.json
    
    $nestedRepos = Get-Content "nested_repos_report.json" | ConvertFrom-Json
    $mergeReport.phases.nested_repos = @{
        total = $nestedRepos.summary.total
        stray_count = $nestedRepos.summary.stray_count
    }
    
    if ($nestedRepos.summary.stray_count -gt 0) {
        Write-MergeLog "WARNING: Found $($nestedRepos.summary.stray_count) stray nested repo(s)" "WARN"
        Write-MergeLog "These will be handled in Phase 3" "INFO"
    } else {
        Write-MergeLog "No nested repo issues detected" "SUCCESS"
    }
    Write-Host ""
    
    # ===== PHASE 3: File Classification =====
    Write-Host "📁 Phase 3: File Classification" -ForegroundColor Yellow
    Write-MergeLog "Running MERGE-008 (File Classifier)" "INFO"
    
    $classifierScript = Join-Path $PSScriptRoot "merge_file_classifier.py"
    python $classifierScript . --output merge_file_classes.json
    
    $fileClasses = Get-Content "merge_file_classes.json" | ConvertFrom-Json
    $mergeReport.phases.file_classification = @{
        total_files = ($fileClasses.summary.PSObject.Properties | Measure-Object -Property Value -Sum).Sum
        classes = $fileClasses.summary
    }
    
    Write-MergeLog "Classified $($mergeReport.phases.file_classification.total_files) files" "SUCCESS"
    Write-Host ""
    
    # ===== PHASE 4: Create Rollback Point =====
    Write-Host "💾 Phase 4: Create Rollback Point" -ForegroundColor Yellow
    Write-MergeLog "Creating rollback branch: $BackupNamespace-$timestamp" "INFO"
    
    # Tag current HEAD
    $tagName = "pre-merge-$timestamp"
    git tag -a $tagName -m "Pre-merge snapshot before merging $FeatureBranch to $BaseBranch"
    
    # Create rollback branch
    $rollbackBranch = "$BackupNamespace-$timestamp"
    git branch $rollbackBranch HEAD
    
    Write-MergeLog "Rollback point created: $rollbackBranch (tag: $tagName)" "SUCCESS"
    
    $mergeReport.phases.rollback = @{
        branch = $rollbackBranch
        tag = $tagName
        commit = (git rev-parse HEAD)
    }
    Write-Host ""
    
    # ===== PHASE 5: Sync Base Branch =====
    Write-Host "🔄 Phase 5: Sync Base Branch" -ForegroundColor Yellow
    Write-MergeLog "Checking out $BaseBranch" "INFO"
    
    git checkout $BaseBranch
    
    Write-MergeLog "Pulling latest from $RemoteName/$BaseBranch" "INFO"
    git pull --ff-only $RemoteName $BaseBranch
    
    if ($LASTEXITCODE -ne 0) {
        Write-MergeLog "Cannot fast-forward base branch - manual intervention required" "ERROR"
        throw "ABORT: Base branch cannot be fast-forwarded"
    }
    
    Write-MergeLog "Base branch synced successfully" "SUCCESS"
    Write-Host ""
    
    # ===== PHASE 6: Perform Merge =====
    Write-Host "🔀 Phase 6: Merge Feature Branch" -ForegroundColor Yellow
    Write-MergeLog "Merging $FeatureBranch into $BaseBranch" "INFO"
    
    $mergeMessage = @"
Merge $FeatureBranch into $BaseBranch

Safe Merge Automation (MERGE-004)
- Pattern ID: MERGE-004
- Timestamp: $timestamp
- Rollback: $rollbackBranch
- Validation: $($ValidationGates -join ', ')

Automated by Safe Merge Pattern Library
"@
    
    git merge --no-ff $FeatureBranch -m $mergeMessage
    
    if ($LASTEXITCODE -ne 0) {
        Write-MergeLog "Merge conflicts detected" "WARN"
        
        # Get conflicted files
        $conflicted = git diff --name-only --diff-filter=U
        
        Write-MergeLog "Conflicted files: $($conflicted.Count)" "WARN"
        
        $mergeReport.phases.merge = @{
            status = "conflicts"
            conflicted_files = $conflicted
            resolution = "manual_required"
        }
        
        Write-MergeLog "ABORT: Merge has conflicts - rolling back" "ERROR"
        git merge --abort
        git checkout $rollbackBranch
        
        throw "Merge conflicts detected. Manual resolution required."
    }
    
    Write-MergeLog "Merge completed successfully" "SUCCESS"
    $mergeReport.phases.merge = @{
        status = "success"
        conflicted_files = @()
    }
    Write-Host ""
    
    # ===== PHASE 7: Validation Gates =====
    Write-Host "✅ Phase 7: Validation Gates" -ForegroundColor Yellow
    
    $validationResults = @()
    $allPassed = $true
    
    foreach ($gate in $ValidationGates) {
        $result = Invoke-ValidationGate -Gate $gate
        $validationResults += $result
        
        if (-not $result.passed -and -not $result.skipped) {
            Write-MergeLog "Gate FAILED: $gate" "ERROR"
            $allPassed = $false
        } elseif ($result.skipped) {
            Write-MergeLog "Gate SKIPPED: $gate" "WARN"
        } else {
            Write-MergeLog "Gate PASSED: $gate" "SUCCESS"
        }
    }
    
    $mergeReport.phases.validation = @{
        gates = $validationResults
        all_passed = $allPassed
    }
    
    if (-not $allPassed) {
        Write-MergeLog "ABORT: Validation gates failed - rolling back" "ERROR"
        git reset --hard $rollbackBranch
        throw "Validation gates failed. Merge rolled back."
    }
    
    Write-MergeLog "All validation gates passed" "SUCCESS"
    Write-Host ""
    
    # ===== PHASE 8: Push (if enabled) =====
    if ($AllowAutoPush) {
        Write-Host "📤 Phase 8: Push to Remote" -ForegroundColor Yellow
        Write-MergeLog "Pushing $BaseBranch to $RemoteName" "INFO"
        
        git push $RemoteName $BaseBranch
        
        if ($LASTEXITCODE -eq 0) {
            Write-MergeLog "Push successful" "SUCCESS"
            $mergeReport.phases.push = @{
                status = "success"
                remote = $RemoteName
                branch = $BaseBranch
            }
        } else {
            Write-MergeLog "Push failed" "ERROR"
            $mergeReport.phases.push = @{
                status = "failed"
            }
            throw "Push to remote failed"
        }
    } else {
        Write-Host "⏸️  Phase 8: Push Skipped (AllowAutoPush = false)" -ForegroundColor Yellow
        Write-MergeLog "Auto-push disabled - manual push required" "WARN"
        $mergeReport.phases.push = @{
            status = "skipped"
            reason = "AllowAutoPush = false"
        }
    }
    Write-Host ""
    
    # ===== SUCCESS =====
    $mergeReport.status = "success"
    Write-Host "✅ MERGE SUCCESSFUL" -ForegroundColor Green
    Write-MergeLog "Safe merge completed successfully" "SUCCESS"
    
} catch {
    # ===== FAILURE =====
    $mergeReport.status = "failed"
    $mergeReport.error = $_.Exception.Message
    
    Write-Host ""
    Write-Host "❌ MERGE FAILED" -ForegroundColor Red
    Write-MergeLog "Error: $($_.Exception.Message)" "ERROR"
    
    Write-Host ""
    Write-Host "🔄 Rollback Options:" -ForegroundColor Yellow
    Write-Host "   1. Hard reset: git reset --hard $rollbackBranch" -ForegroundColor Gray
    Write-Host "   2. Checkout rollback: git checkout $rollbackBranch" -ForegroundColor Gray
    Write-Host "   3. Review report: cat $reportPath" -ForegroundColor Gray
    
    # Save error report
    $mergeReport | ConvertTo-Json -Depth 10 | Out-File $reportJsonPath
    
    exit 1
}

# ===== FINALIZE =====
Write-Host ""
Write-Host "📊 Merge Summary:" -ForegroundColor Cyan
Write-Host "   Status: $($mergeReport.status)" -ForegroundColor Green
Write-Host "   Ahead: $($mergeReport.phases.env_scan.ahead) commits" -ForegroundColor Gray
Write-Host "   Behind: $($mergeReport.phases.env_scan.behind) commits" -ForegroundColor Gray
Write-Host "   Rollback: $($mergeReport.phases.rollback.branch)" -ForegroundColor Gray
Write-Host "   Validation: $($validationResults.Count) gates, all passed" -ForegroundColor Gray
Write-Host ""

Write-Host "📄 Reports:" -ForegroundColor Cyan
Write-Host "   Markdown: $reportPath" -ForegroundColor Gray
Write-Host "   JSON: $reportJsonPath" -ForegroundColor Gray
Write-Host ""

# Save JSON report
$mergeReport | ConvertTo-Json -Depth 10 | Out-File $reportJsonPath

Write-Host "✅ Safe Merge Automation Complete" -ForegroundColor Green
exit 0
