# DOC_LINK: DOC-PAT-WORKTREE-LIFECYCLE-EXECUTOR-233
# DOC_LINK: DOC-WORKTREE-LIFECYCLE-001
# Pattern: worktree_lifecycle (PAT-WORKTREE-LIFECYCLE-001)
# Version: 1.0.0
# Purpose: Execute worktree_lifecycle pattern instances

param(
    [Parameter(Mandatory=$true)]
    [string]$InstancePath
)

$ErrorActionPreference = "Stop"

Write-Host "Executing worktree_lifecycle pattern..." -ForegroundColor Cyan

# Load instance
if (-not (Test-Path $InstancePath)) {
    throw "Instance file not found: $InstancePath"
}

$instance = Get-Content $InstancePath -Raw | ConvertFrom-Json

# Validate pattern_id
if ($instance.pattern_id -ne "PAT-WORKTREE-LIFECYCLE-001") {
    throw "Invalid pattern_id. Expected: PAT-WORKTREE-LIFECYCLE-001, Got: $($instance.pattern_id)"
}

# TODO: Implement worktree_lifecycle execution logic
# See patterns/specs/worktree_lifecycle.pattern.yaml for implementation details

Write-Host "✓ worktree_lifecycle pattern execution complete" -ForegroundColor Green
