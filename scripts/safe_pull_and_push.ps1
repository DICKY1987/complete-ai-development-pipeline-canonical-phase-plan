# DOC_LINK: DOC-SCRIPT-SAFE-PULL-AND-PUSH-749
# Safe pull-and-push wrapper with retry support.
param(
    [Parameter(Mandatory = $true)]
    [string]$Branch,
    [string]$RemoteName = "origin",
    [string]$RebaseMode = "rebase",
    [int]$RetryCount = 2
)

$ErrorActionPreference = "Stop"

function Invoke-WithRetry {
    param(
        [scriptblock]$Action,
        [int]$Retries = 0,
        [int]$DelaySeconds = 5
    )

    for ($i = 0; $i -le $Retries; $i++) {
        try {
            & $Action
            return $true
        } catch {
            if ($i -ge $Retries) { throw }
            Start-Sleep -Seconds $DelaySeconds
        }
    }
}

# Require lock presence to guard direct usage
$repoRoot = Split-Path -Parent $PSScriptRoot
$lockRoot = Join-Path $repoRoot ".git\locks"
$pipelineLock = Join-Path $lockRoot "merge_pipeline_$Branch.lock"
$pushLock = Join-Path $lockRoot "branch_$Branch.lock"
if (-not ((Test-Path $pipelineLock) -or (Test-Path $pushLock))) {
    Write-Error "Push guard active: no lock present for $Branch (expected $pipelineLock or $pushLock)"
    exit 2
}

# If pattern script exists, delegate to it for consistency.
$patternScript = Join-Path $PSScriptRoot "..\patterns\safe_merge\scripts\safe_pull_and_push.ps1"
if (Test-Path $patternScript) {
    & $patternScript -Branch $Branch -RemoteName $RemoteName -RebaseMode $RebaseMode
    exit $LASTEXITCODE
}

Invoke-WithRetry -Retries $RetryCount -Action {
    git fetch $RemoteName $Branch
}

if ($RebaseMode -eq "rebase") {
    Invoke-WithRetry -Retries $RetryCount -Action {
        git pull --rebase $RemoteName $Branch
    }
} else {
    Invoke-WithRetry -Retries $RetryCount -Action {
        git pull --ff-only $RemoteName $Branch
    }
}

Invoke-WithRetry -Retries $RetryCount -Action {
    git push $RemoteName $Branch
}

Write-Host "OK: Safe pull and push completed for $Branch"
exit 0
