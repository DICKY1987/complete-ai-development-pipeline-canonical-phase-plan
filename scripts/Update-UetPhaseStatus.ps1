<#
.SYNOPSIS
    Update phase status in YAML file.

.DESCRIPTION
    Updates the 'status' field of a phase in a UET phase plan YAML file.
    Validates status value and provides option to auto-sync to GitHub.

.EXAMPLE
    # Update one phase
    pwsh scripts/Update-UetPhaseStatus.ps1 `
        -PlanPath 'plans/WEEK2.yaml' `
        -PhaseId 'PH-W2D1' `
        -Status 'in_progress'

.EXAMPLE
    # Update and immediately sync to GitHub
    pwsh scripts/Update-UetPhaseStatus.ps1 `
        -PlanPath 'plans/WEEK2.yaml' `
        -PhaseId 'PH-W2D1' `
        -Status 'done' `
        -SyncToGitHub
#>

[CmdletBinding(SupportsShouldProcess = $true)]
param(
    # Path to phase plan YAML
    [Parameter(Mandatory = $true)]
    [string]$PlanPath,

    # Phase ID to update
    [Parameter(Mandatory = $true)]
    [string]$PhaseId,

    # New status value
    [Parameter(Mandatory = $true)]
    [ValidateSet('not_started', 'in_progress', 'done', 'blocked')]
    [string]$Status,

    # If set, automatically sync to GitHub after updating
    [switch]$SyncToGitHub,

    # Git commit message (if not set, no commit)
    [Parameter(Mandatory = $false)]
    [string]$CommitMessage
)

# Load YAML module check
if (-not (Get-Command ConvertFrom-Yaml -ErrorAction SilentlyContinue)) {
    throw "ConvertFrom-Yaml not available. Use PowerShell 7+ or install powershell-yaml module."
}

if (-not (Get-Command ConvertTo-Yaml -ErrorAction SilentlyContinue)) {
    throw "ConvertTo-Yaml not available. Use PowerShell 7+ or install powershell-yaml module."
}

# Load plan
if (-not (Test-Path -LiteralPath $PlanPath)) {
    throw "Phase plan not found: $PlanPath"
}

Write-Verbose "Loading phase plan from '$PlanPath'..."
$raw = Get-Content -LiteralPath $PlanPath -Raw
$plan = $raw | ConvertFrom-Yaml

if (-not $plan.phases) {
    throw "Phase plan missing 'phases' collection"
}

# Find the phase
$phase = $plan.phases | Where-Object { $_.phase_id -eq $PhaseId }

if (-not $phase) {
    throw "Phase '$PhaseId' not found in plan. Available phases: $($plan.phases.phase_id -join ', ')"
}

$oldStatus = $phase.status ?? 'not_started'

if ($oldStatus -eq $Status) {
    Write-Host "Phase '$PhaseId' already has status '$Status', no change needed."
    exit 0
}

if (-not $PSCmdlet.ShouldProcess("Phase $PhaseId in $PlanPath", "Update status from '$oldStatus' to '$Status'")) {
    exit 0
}

# Update status
Write-Host "Updating phase '$PhaseId': '$oldStatus' → '$Status'"

if ($phase.PSObject.Properties.Name -contains 'status') {
    $phase.status = $Status
} else {
    $phase | Add-Member -NotePropertyName 'status' -NotePropertyValue $Status
}

# Save back to file
Write-Verbose "Saving updated plan to '$PlanPath'..."
$yaml = $plan | ConvertTo-Yaml
$yaml | Set-Content -LiteralPath $PlanPath -Encoding UTF8

Write-Host "✓ Phase status updated in YAML"

# Optional: Commit
if ($CommitMessage) {
    Write-Verbose "Committing change..."
    git add $PlanPath
    git commit -m $CommitMessage
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Changes committed"
    } else {
        Write-Warning "Git commit failed (may already be staged)"
    }
}

# Optional: Sync to GitHub
if ($SyncToGitHub) {
    Write-Host "`nSyncing status to GitHub Project..."

    $syncScript = Join-Path $PSScriptRoot "Sync-UetPhaseStatusToGitHub.ps1"
    if (-not (Test-Path $syncScript)) {
        Write-Warning "Sync script not found at '$syncScript', skipping GitHub sync"
    } else {
        & $syncScript -PlanPath $PlanPath -PhaseId $PhaseId -Verbose:$VerbosePreference
    }
}

Write-Host "`n✓ Complete!"
