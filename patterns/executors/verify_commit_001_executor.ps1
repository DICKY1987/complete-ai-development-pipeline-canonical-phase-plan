# DOC_LINK: DOC-PAT-VERIFY-COMMIT-001-EXECUTOR-230
# Pattern Executor: verify_commit
# Pattern ID: PAT-VERIFY-COMMIT-001
# Auto-generated: 2025-11-27T10:14:13.686960

param(
    [Parameter(Mandatory=$true)]
    [string]$InstanceFile
)

$ErrorActionPreference = "Stop"

# Read instance
$instance = Get-Content $InstanceFile -Raw | ConvertFrom-Json

Write-Host "[EXEC] Running verify_commit..." -ForegroundColor Cyan

# Parse inputs
$inputs = $instance.pattern.inputs
$projectRoot = if ($inputs.project_root) { $inputs.project_root } else { "." }
$commitMsg = if ($inputs.commit_message) { $inputs.commit_message } else { "HEAD" }

Push-Location $projectRoot
try {
    # Validate git repository
    git status 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Not a git repository"
    }

    # Run verification checks
    $checks = @()

    # Check for uncommitted changes
    $gitStatus = git status --porcelain 2>&1
    $hasUncommitted = $gitStatus.Length -gt 0
    $checks += @{
        name = "no_uncommitted_changes"
        status = if ($hasUncommitted) { "fail" } else { "pass" }
        message = if ($hasUncommitted) { "Uncommitted changes detected" } else { "Clean working tree" }
    }

    # Verify last commit exists
    try {
        git log -1 --oneline 2>&1 | Out-Null
        $hasCommits = $LASTEXITCODE -eq 0
    } catch {
        $hasCommits = $false
    }

    $checks += @{
        name = "commit_exists"
        status = if ($hasCommits) { "pass" } else { "fail" }
        message = if ($hasCommits) { "Commits verified" } else { "No commits found" }
    }

    # Check expected files if provided
    if ($inputs.expected_files) {
        foreach ($file in $inputs.expected_files) {
            $exists = Test-Path $file
            $checks += @{
                name = "file_$file"
                status = if ($exists) { "pass" } else { "fail" }
                message = if ($exists) { "File exists: $file" } else { "Missing file: $file" }
            }
        }
    }

    $failedChecks = $checks | Where-Object { $_.status -eq "fail" }
    $overallStatus = if ($failedChecks.Count -eq 0) { "success" } else { "failure" }

    if ($overallStatus -eq "success") {
        Write-Host "[OK] Commit verification passed" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Verification failed: $($failedChecks.Count) check(s)" -ForegroundColor Red
    }
} finally {
    Pop-Location
}

Write-Host "[OK] Execution complete" -ForegroundColor Green
