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

.PARAMETER PlanPath
    Path to the phase plan YAML file relative to repo root.
    Default: "plans/PHASE_PLAN.yaml"

.PARAMETER ProjectNumber
    GitHub Project number (as shown in gh project view/list).
    Required.

.PARAMETER ProjectOwner
    GitHub project owner. Use "@me" for current user or an org name.
    Default: "@me"

.PARAMETER DryRun
    If set, do not call gh or write back to the plan file.
    Shows what would be created.

.PARAMETER RequireCleanGitStatus
    If set, require that `git status --porcelain` is empty before writing.
    Prevents accidental plan modifications when working tree is dirty.

.EXAMPLE
    # Dry run to see what would be created
    .\Invoke-UetPhasePlanToGitHubProjectSync.ps1 -ProjectNumber 1 -DryRun -Verbose

.EXAMPLE
    # Actually sync phases to GitHub Project
    .\Invoke-UetPhasePlanToGitHubProjectSync.ps1 -ProjectNumber 1 -RequireCleanGitStatus -Verbose

.EXAMPLE
    # Sync to an org project
    .\Invoke-UetPhasePlanToGitHubProjectSync.ps1 `
        -ProjectNumber 3 `
        -ProjectOwner "my-org" `
        -PlanPath "workstreams/ws-pipeline-plus/PHASE_PLAN.yaml"

.NOTES
    Pattern Id: PAT_EXEC_GHPROJECT_PHASE_PLAN_SYNC_V1
    Phase Id  : PH-PLAN-GHPROJECT-SYNC
    Author    : UET / Canonical Pipeline tooling
    Version   : 1.0.0
    Created   : 2025-12-02

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

    Requirements:
      - GitHub CLI installed: gh auth status
      - GitHub CLI project scope: gh auth refresh -s project
      - PowerShell 7+ (for native YAML support)
        OR powershell-yaml module for PS 5.1

.LINK
    https://cli.github.com/manual/gh_project
    https://cli.github.com/manual/gh_project_item-create
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
        throw "Required cmdlet '$Name' is not available. On PowerShell 7+, ConvertFrom-Yaml/ConvertTo-Yaml should exist. Otherwise install powershell-yaml module."
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
    $bodyLines += "**Phase ID:** ``$($Phase.phase_id)``"
    $bodyLines += "**Workstream ID:** ``$($Phase.workstream_id)``"
    if ($Phase.phase_type) {
        $bodyLines += "**Phase Type:** $($Phase.phase_type)"
    }
    if ($Phase.estimate_hours) {
        $bodyLines += "**Estimated Hours:** $($Phase.estimate_hours)"
    }
    if ($Phase.status) {
        $bodyLines += "**Status:** $($Phase.status)"
    }
    if ($dependsOn) {
        $bodyLines += "**Depends On:** $dependsOn"
    }
    $bodyLines += ""
    $bodyLines += "## Objective"
    $bodyLines += $Phase.objective
    
    # Add acceptance criteria if present
    if ($Phase.acceptance_criteria) {
        $bodyLines += ""
        $bodyLines += "## Acceptance Criteria"
        foreach ($criterion in $Phase.acceptance_criteria) {
            $bodyLines += "- [ ] $criterion"
        }
    }

    $body = $bodyLines -join "`n"

    if ($DryRun) {
        Write-Host "[DRY-RUN] Would create GitHub project draft item for phase '$($Phase.phase_id)':" -ForegroundColor Cyan
        Write-Host "          Title: $title" -ForegroundColor Gray
        Write-Host "          Body :" -ForegroundColor Gray
        Write-Host ($body -replace "`n", "`n          ") -ForegroundColor DarkGray
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

    Write-Host "✓ Created item for phase '$($Phase.phase_id)' → gh_item_id: $($json.id)" -ForegroundColor Green
    return $json.id
}

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  UET Phase Plan → GitHub Project Sync" -ForegroundColor Cyan
Write-Host "  Pattern: PAT_EXEC_GHPROJECT_PHASE_PLAN_SYNC_V1" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

try {
    # Pre-flight checks
    Write-Verbose "Running pre-flight checks..."
    Assert-CommandAvailable -Name "gh"
    Assert-CmdletAvailable -Name "ConvertFrom-Yaml"
    Assert-CmdletAvailable -Name "ConvertTo-Yaml"
    
    # Verify GitHub CLI authentication
    $authStatus = gh auth status 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "GitHub CLI not authenticated. Run 'gh auth login' first."
    }
    
    Assert-GitCleanIfRequested -RequireClean:$RequireCleanGitStatus

    $planInfo = Load-UetPhasePlan -Path $PlanPath
    $plan     = $planInfo.Plan
    $phases   = $planInfo.Phases

    Write-Host "Loaded $($phases.Count) phase(s) from '$PlanPath'" -ForegroundColor Gray
    Write-Host ""

    $phasesNeedingItems = $phases | Where-Object {
        -not $_.PSObject.Properties.Name.Contains('gh_item_id') -or
        [string]::IsNullOrWhiteSpace($_.gh_item_id)
    }

    if ($phasesNeedingItems.Count -eq 0) {
        Write-Host "✓ All phases already have gh_item_id. Nothing to create." -ForegroundColor Green
        Write-Host ""
        return
    }

    Write-Host "$($phasesNeedingItems.Count) phase(s) will have GitHub Project items created:" -ForegroundColor Yellow
    foreach ($phase in $phasesNeedingItems) {
        Write-Host "  • $($phase.phase_id): $($phase.title)" -ForegroundColor Gray
    }
    Write-Host ""

    if ($DryRun) {
        Write-Host "[DRY-RUN MODE] No changes will be made." -ForegroundColor Cyan
        Write-Host ""
    }

    foreach ($phase in $phasesNeedingItems) {
        $newId = New-GitHubProjectDraftItemForPhase `
            -Phase $phase `
            -ProjectNumber $ProjectNumber `
            -ProjectOwner $ProjectOwner `
            -DryRun:$DryRun

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
        Write-Host ""
        Write-Host "Dry-run complete. No changes written to '$PlanPath'." -ForegroundColor Cyan
        Write-Host ""
        return
    }

    # Persist updated plan with gh_item_id back to disk
    Save-UetPhasePlan -Plan $plan -Path $PlanPath

    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host "  Sync Complete!" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
    Write-Host "✓ Updated plan written to '$PlanPath'" -ForegroundColor Green
    Write-Host "✓ Each phase now has a gh_item_id for future status syncs" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. View your project: gh project view $ProjectNumber --owner $ProjectOwner --web" -ForegroundColor Gray
    Write-Host "  2. Update phase status in the YAML as work progresses" -ForegroundColor Gray
    Write-Host "  3. Run status sync script to update GitHub Project fields" -ForegroundColor Gray
    Write-Host ""

} catch {
    Write-Host ""
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    exit 1
}
