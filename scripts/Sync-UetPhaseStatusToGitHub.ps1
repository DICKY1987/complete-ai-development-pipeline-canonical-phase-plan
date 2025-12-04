# DOC_LINK: DOC-SCRIPT-SYNC-UETPHASESTATUSTOGITHUB-750
<#
.SYNOPSIS
    Sync phase status changes from YAML to GitHub Project.

.DESCRIPTION
    Reads a UET phase plan YAML and syncs the 'status' field of each phase
    to its corresponding GitHub Project item (identified by gh_item_id).

    Uses gh project item-edit to update the Status field based on environment
    variables that map to your project's field IDs and option IDs.

.NOTES
    Pattern Id: PAT_EXEC_GHPROJECT_STATUS_SYNC_V1
    Phase Id  : PH-PLAN-STATUS-SYNC
    Author    : UET / Canonical Pipeline tooling

    Required Environment Variables (or parameters):
    - PROJECT_ID: GitHub Project node ID (from gh api graphql query)
    - STATUS_FIELD_ID: Field ID for Status field
    - STATUS_TODO_ID: Option ID for "Todo" / "Not Started"
    - STATUS_IN_PROGRESS_ID: Option ID for "In Progress"
    - STATUS_DONE_ID: Option ID for "Done"
    - STATUS_BLOCKED_ID: Option ID for "Blocked" (optional)

.EXAMPLE
    # Set up environment (one-time setup per project)
    $env:PROJECT_ID = "PVT_kwDOABC123"
    $env:STATUS_FIELD_ID = "PVTSSF_lADOABC123"
    $env:STATUS_TODO_ID = "todo-option-id"
    $env:STATUS_IN_PROGRESS_ID = "in-progress-option-id"
    $env:STATUS_DONE_ID = "done-option-id"

    # Sync all phases
    pwsh scripts/Sync-UetPhaseStatusToGitHub.ps1 -PlanPath 'plans/WEEK2.yaml'

.EXAMPLE
    # Sync only one phase
    pwsh scripts/Sync-UetPhaseStatusToGitHub.ps1 `
        -PlanPath 'plans/WEEK2.yaml' `
        -PhaseId 'PH-W2D1'
#>

[CmdletBinding(SupportsShouldProcess = $true)]
param(
    # Path to phase plan YAML
    [Parameter(Mandatory = $true)]
    [string]$PlanPath,

    # Optional: sync only this phase_id
    [Parameter(Mandatory = $false)]
    [string]$PhaseId,

    # GitHub Project node ID (e.g., PVT_kwDOABC123)
    # If not provided, reads from $env:PROJECT_ID
    [Parameter(Mandatory = $false)]
    [string]$ProjectId,

    # Status field ID (e.g., PVTSSF_lADOABC123)
    # If not provided, reads from $env:STATUS_FIELD_ID
    [Parameter(Mandatory = $false)]
    [string]$StatusFieldId,

    # If set, only show what would be done
    [switch]$DryRun
)

# ---------------------------------------------------------------------------
# Helper: Get configuration from params or environment
# ---------------------------------------------------------------------------
function Get-ProjectConfig {
    param(
        [string]$ProjectId,
        [string]$StatusFieldId
    )

    $config = @{
        ProjectId = $ProjectId ?? $env:PROJECT_ID
        StatusFieldId = $StatusFieldId ?? $env:STATUS_FIELD_ID
        StatusTodoId = $env:STATUS_TODO_ID
        StatusInProgressId = $env:STATUS_IN_PROGRESS_ID
        StatusDoneId = $env:STATUS_DONE_ID
        StatusBlockedId = $env:STATUS_BLOCKED_ID
    }

    # Validate required fields
    if (-not $config.ProjectId) {
        throw "PROJECT_ID not set. Provide -ProjectId parameter or set `$env:PROJECT_ID"
    }
    if (-not $config.StatusFieldId) {
        throw "STATUS_FIELD_ID not set. Provide -StatusFieldId parameter or set `$env:STATUS_FIELD_ID"
    }
    if (-not $config.StatusTodoId) {
        throw "STATUS_TODO_ID not set. Set `$env:STATUS_TODO_ID to your 'Todo' option ID"
    }
    if (-not $config.StatusInProgressId) {
        throw "STATUS_IN_PROGRESS_ID not set. Set `$env:STATUS_IN_PROGRESS_ID"
    }
    if (-not $config.StatusDoneId) {
        throw "STATUS_DONE_ID not set. Set `$env:STATUS_DONE_ID"
    }

    return $config
}

# ---------------------------------------------------------------------------
# Helper: Map phase status to GitHub option ID
# ---------------------------------------------------------------------------
function Get-GitHubStatusOptionId {
    param(
        [Parameter(Mandatory)]
        [string]$PhaseStatus,
        [Parameter(Mandatory)]
        [hashtable]$Config
    )

    switch ($PhaseStatus) {
        'not_started' { return $Config.StatusTodoId }
        'in_progress' { return $Config.StatusInProgressId }
        'done'        { return $Config.StatusDoneId }
        'blocked'     {
            if ($Config.StatusBlockedId) {
                return $Config.StatusBlockedId
            } else {
                Write-Warning "No STATUS_BLOCKED_ID configured, using TODO instead"
                return $Config.StatusTodoId
            }
        }
        default {
            throw "Unknown phase status: $PhaseStatus"
        }
    }
}

# ---------------------------------------------------------------------------
# Helper: Load phase plan
# ---------------------------------------------------------------------------
function Load-PhasePlan {
    param(
        [Parameter(Mandatory)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Phase plan not found: $Path"
    }

    if (-not (Get-Command ConvertFrom-Yaml -ErrorAction SilentlyContinue)) {
        throw "ConvertFrom-Yaml cmdlet not available. Use PowerShell 7+ or install powershell-yaml module."
    }

    $raw = Get-Content -LiteralPath $Path -Raw
    $plan = $raw | ConvertFrom-Yaml

    if (-not $plan.phases) {
        throw "Phase plan missing 'phases' collection"
    }

    return $plan.phases
}

# ---------------------------------------------------------------------------
# Helper: Update GitHub Project item status
# ---------------------------------------------------------------------------
function Update-GitHubProjectItemStatus {
    param(
        [Parameter(Mandatory)]
        [object]$Phase,
        [Parameter(Mandatory)]
        [hashtable]$Config,
        [switch]$DryRun
    )

    if (-not $Phase.gh_item_id) {
        Write-Warning "Phase '$($Phase.phase_id)' has no gh_item_id, skipping"
        return $false
    }

    $optionId = Get-GitHubStatusOptionId -PhaseStatus $Phase.status -Config $Config

    if ($DryRun) {
        Write-Host "[DRY-RUN] Would update phase '$($Phase.phase_id)':"
        Write-Host "          Item ID: $($Phase.gh_item_id)"
        Write-Host "          Status: $($Phase.status) → Option ID: $optionId"
        return $true
    }

    if (-not $PSCmdlet.ShouldProcess("GitHub item $($Phase.gh_item_id)", "Update status to $($Phase.status)")) {
        return $false
    }

    Write-Verbose "Updating phase '$($Phase.phase_id)' (item: $($Phase.gh_item_id)) to status '$($Phase.status)'"

    $args = @(
        'project', 'item-edit',
        '--id', $Phase.gh_item_id,
        '--project-id', $Config.ProjectId,
        '--field-id', $Config.StatusFieldId,
        '--option-id', $optionId
    )

    $output = & gh @args 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to update phase '$($Phase.phase_id)': $output"
        return $false
    }

    Write-Host "✓ Updated phase '$($Phase.phase_id)' to '$($Phase.status)'"
    return $true
}

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

try {
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        throw "GitHub CLI (gh) not found. Install from https://cli.github.com/"
    }

    $config = Get-ProjectConfig -ProjectId $ProjectId -StatusFieldId $StatusFieldId

    Write-Verbose "Loading phase plan from '$PlanPath'..."
    $phases = Load-PhasePlan -Path $PlanPath

    # Filter to single phase if requested
    if ($PhaseId) {
        $phases = $phases | Where-Object { $_.phase_id -eq $PhaseId }
        if (-not $phases) {
            throw "Phase '$PhaseId' not found in plan"
        }
        if ($phases -is [array]) {
            $phases = @($phases)
        } else {
            $phases = @($phases)
        }
    }

    Write-Host "Syncing $($phases.Count) phase(s) to GitHub Project..."

    $updated = 0
    $skipped = 0
    $failed = 0

    foreach ($phase in $phases) {
        if (-not $phase.status) {
            Write-Warning "Phase '$($phase.phase_id)' has no status field, skipping"
            $skipped++
            continue
        }

        $result = Update-GitHubProjectItemStatus -Phase $phase -Config $config -DryRun:$DryRun
        if ($result) {
            $updated++
        } else {
            $failed++
        }
    }

    Write-Host "`nSync complete:"
    Write-Host "  Updated: $updated"
    Write-Host "  Skipped: $skipped"
    Write-Host "  Failed:  $failed"

    if ($DryRun) {
        Write-Host "`n[DRY-RUN] No changes were made to GitHub Project"
    }

} catch {
    Write-Error $_.Exception.Message
    exit 1
}
