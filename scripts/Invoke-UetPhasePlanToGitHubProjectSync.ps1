# DOC_LINK: DOC-SCRIPT-INVOKE-UETPHASEPLANTOGITHUBPROJECTSYNC-746
<#
.SYNOPSIS
    Sync UET Phase Plan phases into a GitHub Project as draft items.

.DESCRIPTION
    Reads a UET-style phase plan YAML file (phases[], each with phase_id and
    workstream_id), validates structure, and for any phase missing gh_item_id
    it creates a draft issue item in the configured GitHub Project.

    Once created, the script writes the returned GitHub Project item ID
    back into the phase document as gh_item_id so the plan becomes the
    single source of truth for future syncs.

    Anti-pattern guards:
      - Optional clean-git check before modifying anything.
      - Validates mandatory fields (phase_id, workstream_id, title, objective).
      - Validates that phase_id values are unique.
      - Validates phase.status is from an allowed set.

.NOTES
    Pattern Id: PAT_EXEC_GHPROJECT_PHASE_PLAN_SYNC_V1
    Phase Id  : PH-PLAN-GHPROJECT-SYNC
    Author    : UET / Canonical Pipeline tooling

    Expected YAML shape (minimal):

    phases:
      - phase_id: "PH-00"
        workstream_id: "ws-some-workstream"
        title: "Human-readable phase title"
        objective: "Phase objective..."
        phase_type: "implementation"
        depends_on: []
        status: "not_started"   # not_started | in_progress | done | blocked
        gh_item_id: null        # will be set by this script
        estimate_hours: 2
#>

[CmdletBinding(SupportsShouldProcess = $true)]
param(
    # Path to the phase plan YAML file relative to repo root.
    [Parameter(Mandatory = $false)]
    [string]$PlanPath = "plans/PHASE_PLAN.yaml",

    # GitHub Project number (as shown in gh project view/list).
    [Parameter(Mandatory = $true)]
    [int]$ProjectNumber,

    # GitHub project owner. Use "@me" for current user or an org name.
    [Parameter(Mandatory = $false)]
    [string]$ProjectOwner = "@me",

    # If set, do not call gh or write back to the plan file.
    [switch]$DryRun,

    # If set, require that `git status --porcelain` is empty before writing.
    [switch]$RequireCleanGitStatus
)

# ---------------------------------------------------------------------------
# Helper: Fail fast if required executables / cmdlets are missing
# ---------------------------------------------------------------------------
function Assert-CommandAvailable {
    param(
        [Parameter(Mandatory)]
        [string]$Name
    )
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' is not available on PATH. Install it before running this script."
    }
}

function Assert-CmdletAvailable {
    param(
        [Parameter(Mandatory)]
        [string]$Name
    )
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required cmdlet '$Name' is not available. On PowerShell 7+, ConvertFrom-Yaml/ConvertTo-Yaml should exist. Otherwise install a YAML module."
    }
}

# ---------------------------------------------------------------------------
# Helper: Optional safety guard to avoid mutating dirty repos
# ---------------------------------------------------------------------------
function Assert-GitCleanIfRequested {
    param(
        [switch]$RequireClean
    )

    if (-not $RequireClean) { return }

    Assert-CommandAvailable -Name "git"

    Write-Verbose "Checking git working tree cleanliness (RequireCleanGitStatus enabled)..."

    $status = git status --porcelain
    if ($LASTEXITCODE -ne 0) {
        throw "git status failed. Ensure you are inside a git repository and try again."
    }

    if ($status) {
        throw "Working tree is not clean. Commit/stash changes before running with -RequireCleanGitStatus."
    }
}

# ---------------------------------------------------------------------------
# Helper: Load + validate the UET phase plan YAML
# ---------------------------------------------------------------------------
function Load-UetPhasePlan {
    param(
        [Parameter(Mandatory)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Phase plan file not found: $Path"
    }

    Assert-CmdletAvailable -Name "ConvertFrom-Yaml"

    Write-Verbose "Loading phase plan from '$Path'..."
    $raw = Get-Content -LiteralPath $Path -Raw
    $plan = $raw | ConvertFrom-Yaml

    if (-not $plan) {
        throw "Phase plan YAML appears empty or invalid: $Path"
    }

    if (-not $plan.phases) {
        throw "Phase plan is missing top-level 'phases' collection. This violates the mandatory structure."
    }

    $phases = @($plan.phases)

    if ($phases.Count -eq 0) {
        throw "Phase plan contains an empty 'phases' collection. Nothing to sync."
    }

    # Ensure unique phase_id
    $dupes = $phases | Group-Object phase_id | Where-Object { $_.Count -gt 1 }
    if ($dupes) {
        $ids = $dupes | ForEach-Object { $_.Name }
        throw "Duplicate phase_id values detected in plan: $($ids -join ', '). Fix before syncing."
    }

    # Validate required properties + allowed statuses
    $allowedStatuses = @('not_started', 'in_progress', 'done', 'blocked')

    foreach ($phase in $phases) {
        if (-not $phase.phase_id) {
            throw "A phase is missing 'phase_id'. Every phase MUST have a unique phase_id."
        }
        if (-not $phase.workstream_id) {
            throw "Phase '$($phase.phase_id)' is missing 'workstream_id'."
        }
        if (-not $phase.title) {
            throw "Phase '$($phase.phase_id)' is missing 'title'."
        }
        if (-not $phase.objective) {
            throw "Phase '$($phase.phase_id)' is missing 'objective'."
        }

        if ($phase.status) {
            if ($allowedStatuses -notcontains $phase.status) {
                throw "Phase '$($phase.phase_id)' has invalid status '$($phase.status)'. Allowed: $($allowedStatuses -join ', ')."
            }
        } else {
            # Default unknown statuses to not_started
            $phase | Add-Member -NotePropertyName status -NotePropertyValue 'not_started' -Force
        }
    }

    return [PSCustomObject]@{
        Plan   = $plan
        Phases = $phases
    }
}

# ---------------------------------------------------------------------------
# Helper: Save the updated plan back to YAML
# ---------------------------------------------------------------------------
function Save-UetPhasePlan {
    param(
        [Parameter(Mandatory)]
        [object]$Plan,
        [Parameter(Mandatory)]
        [string]$Path
    )

    Assert-CmdletAvailable -Name "ConvertTo-Yaml"

    Write-Verbose "Serializing updated phase plan back to '$Path'..."
    $yaml = $Plan | ConvertTo-Yaml

    # Preserve UTF-8, no BOM
    $yaml | Set-Content -LiteralPath $Path -Encoding UTF8
}

# ---------------------------------------------------------------------------
# Helper: Create GitHub Project draft item for a phase
# ---------------------------------------------------------------------------
function New-GitHubProjectDraftItemForPhase {
    param(
        [Parameter(Mandatory)]
        [object]$Phase,

        [Parameter(Mandatory)]
        [int]$ProjectNumber,

        [Parameter(Mandatory)]
        [string]$ProjectOwner,

        [switch]$DryRun
    )

    Assert-CommandAvailable -Name "gh"

    $title = "[{0}] {1}" -f $Phase.phase_id, $Phase.title

    $dependsOn = $null
    if ($Phase.depends_on) {
        $dependsOn = @($Phase.depends_on) -join ", "
    }

    $bodyLines = @()
    $bodyLines += "Phase ID: $($Phase.phase_id)"
    $bodyLines += "Workstream ID: $($Phase.workstream_id)"
    if ($Phase.phase_type) {
        $bodyLines += "Phase Type: $($Phase.phase_type)"
    }
    if ($Phase.estimate_hours) {
        $bodyLines += "Estimated Hours: $($Phase.estimate_hours)"
    }
    if ($dependsOn) {
        $bodyLines += "Depends On: $dependsOn"
    }
    $bodyLines += ""
    $bodyLines += "Objective:"
    $bodyLines += $Phase.objective

    $body = $bodyLines -join "`n"

    if ($DryRun) {
        Write-Host "[DRY-RUN] Would create GitHub project draft item for phase '$($Phase.phase_id)':"
        Write-Host "          Title: $title"
        Write-Host "          Body :"
        Write-Host ($body -replace "`n", "`n          ")
        return $null
    }

    if (-not $PSCmdlet.ShouldProcess("GitHub Project $ProjectNumber (owner: $ProjectOwner)", "Create draft item for phase '$($Phase.phase_id)'")) {
        return $null
    }

    Write-Verbose "Creating GitHub project draft item for phase '$($Phase.phase_id)'..."
    $args = @(
        'project', 'item-create', $ProjectNumber.ToString(),
        '--owner', $ProjectOwner,
        '--title', $title,
        '--body', $body,
        '--format', 'json'
    )

    $output = & gh @args 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "gh project item-create failed for phase '$($Phase.phase_id)'. Output:`n$output"
    }

    try {
        $json = $output | ConvertFrom-Json
    } catch {
        throw "Failed to parse gh project item-create JSON output for phase '$($Phase.phase_id)'. Raw output:`n$output"
    }

    if (-not $json.id) {
        throw "gh project item-create did not return an 'id' for phase '$($Phase.phase_id)'. Raw output:`n$output"
    }

    Write-Verbose "Phase '$($Phase.phase_id)' mapped to GitHub item id '$($json.id)'."
    return $json.id
}

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

try {
    Assert-GitCleanIfRequested -RequireClean:$RequireCleanGitStatus

    $planInfo = Load-UetPhasePlan -Path $PlanPath
    $plan     = $planInfo.Plan
    $phases   = $planInfo.Phases

    Write-Verbose ("Loaded {0} phase(s) from plan." -f $phases.Count)

    $phasesNeedingItems = $phases | Where-Object {
        -not $_.PSObject.Properties.Name.Contains('gh_item_id') -or
        [string]::IsNullOrWhiteSpace($_.gh_item_id)
    }

    if ($phasesNeedingItems.Count -eq 0) {
        Write-Host "All phases already have gh_item_id. Nothing to create."
        return
    }

    Write-Host ("{0} phase(s) will have GitHub Project items created." -f $phasesNeedingItems.Count)

    foreach ($phase in $phasesNeedingItems) {
        $newId = New-GitHubProjectDraftItemForPhase -Phase $phase -ProjectNumber $ProjectNumber -ProjectOwner $ProjectOwner -DryRun:$DryRun

        if (-not $DryRun -and $newId) {
            # Attach gh_item_id to the phase object in memory
            if ($phase.PSObject.Properties.Name -contains 'gh_item_id') {
                $phase.gh_item_id = $newId
            } else {
                $phase | Add-Member -NotePropertyName 'gh_item_id' -NotePropertyValue $newId
            }
        }
    }

    if ($DryRun) {
        Write-Host "Dry-run complete. No changes written to '$PlanPath'."
        return
    }

    # Persist updated plan with gh_item_id back to disk
    Save-UetPhasePlan -Plan $plan -Path $PlanPath

    Write-Host "Sync complete. Updated plan written to '$PlanPath'."
    Write-Host "Each phase now has a gh_item_id that can be used for future status syncs."

} catch {
    Write-Error $_.Exception.Message
    exit 1
}
