<#
.SYNOPSIS
    Sync phase plan status updates to GitHub Project items.

.DESCRIPTION
    Reads a UET-style phase plan YAML and updates the Status field in GitHub
    Project items based on the phase.status value in the YAML.
    
    This is the companion to Invoke-UetPhasePlanToGitHubProjectSync.ps1.
    That script creates the initial items, this script keeps them in sync.
    
    Status mapping:
      not_started → Todo
      in_progress → In Progress
      done → Done
      blocked → Blocked

.PARAMETER PlanPath
    Path to the phase plan YAML file.
    Default: "plans/PHASE_PLAN.yaml"

.PARAMETER ProjectNumber
    GitHub Project number (same as used for initial sync).
    Required.

.PARAMETER ProjectOwner
    GitHub project owner ("@me" or org name).
    Default: "@me"

.PARAMETER StatusFieldName
    Name of the Status field in your GitHub Project.
    Default: "Status"

.PARAMETER DryRun
    If set, show what would be updated without making changes.

.PARAMETER Force
    If set, update all phases regardless of whether status changed.
    Otherwise, only updates phases where YAML status differs from last sync.

.EXAMPLE
    # Dry run to see what would be updated
    .\Invoke-UetPhasePlanStatusSync.ps1 -ProjectNumber 1 -DryRun -Verbose

.EXAMPLE
    # Sync status changes
    .\Invoke-UetPhasePlanStatusSync.ps1 -ProjectNumber 1

.EXAMPLE
    # Force update all phases (useful after field name changes)
    .\Invoke-UetPhasePlanStatusSync.ps1 -ProjectNumber 1 -Force

.NOTES
    Pattern Id: PAT_EXEC_GHPROJECT_PHASE_STATUS_SYNC_V1
    Phase Id  : PH-PLAN-GHPROJECT-STATUS-SYNC
    Author    : UET / Canonical Pipeline tooling
    Version   : 1.0.0
    Created   : 2025-12-02

    Requirements:
      - GitHub CLI with project scope (gh auth refresh -s project)
      - Phase plan must have gh_item_id values (run sync script first)
      - Project must have a Status field configured

.LINK
    https://cli.github.com/manual/gh_project_item-edit
    Invoke-UetPhasePlanToGitHubProjectSync.ps1
#>

[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory = $false)]
    [string]$PlanPath = "plans/PHASE_PLAN.yaml",

    [Parameter(Mandatory = $true)]
    [int]$ProjectNumber,

    [Parameter(Mandatory = $false)]
    [string]$ProjectOwner = "@me",

    [Parameter(Mandatory = $false)]
    [string]$StatusFieldName = "Status",

    [switch]$DryRun,
    
    [switch]$Force
)

# ---------------------------------------------------------------------------
# Helper: Fail fast if required executables / cmdlets are missing
# ---------------------------------------------------------------------------
function Assert-CommandAvailable {
    param([Parameter(Mandatory)][string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' is not available. Install it before running."
    }
}

function Assert-CmdletAvailable {
    param([Parameter(Mandatory)][string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required cmdlet '$Name' is not available. Use PowerShell 7+ or install powershell-yaml module."
    }
}

# ---------------------------------------------------------------------------
# Helper: Load phase plan YAML
# ---------------------------------------------------------------------------
function Load-UetPhasePlan {
    param([Parameter(Mandatory)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Phase plan file not found: $Path"
    }

    Assert-CmdletAvailable -Name "ConvertFrom-Yaml"

    Write-Verbose "Loading phase plan from '$Path'..."
    $raw = Get-Content -LiteralPath $Path -Raw
    $plan = $raw | ConvertFrom-Yaml

    if (-not $plan -or -not $plan.phases) {
        throw "Invalid phase plan: missing 'phases' collection"
    }

    return [PSCustomObject]@{
        Plan   = $plan
        Phases = @($plan.phases)
    }
}

# ---------------------------------------------------------------------------
# Helper: Get GitHub Project field metadata
# ---------------------------------------------------------------------------
function Get-GitHubProjectFields {
    param(
        [Parameter(Mandatory)][int]$ProjectNumber,
        [Parameter(Mandatory)][string]$ProjectOwner
    )

    Assert-CommandAvailable -Name "gh"

    Write-Verbose "Fetching project field metadata..."
    
    # Get project fields using GraphQL
    $query = @"
{
  user(login: "$ProjectOwner") {
    projectV2(number: $ProjectNumber) {
      fields(first: 20) {
        nodes {
          ... on ProjectV2SingleSelectField {
            id
            name
            options {
              id
              name
            }
          }
        }
      }
    }
  }
}
"@

    $output = gh api graphql -f query=$query 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to fetch project fields. Output: $output"
    }

    try {
        $result = $output | ConvertFrom-Json
        return $result.data.user.projectV2.fields.nodes
    } catch {
        throw "Failed to parse project fields response: $_"
    }
}

# ---------------------------------------------------------------------------
# Helper: Find status field and option IDs
# ---------------------------------------------------------------------------
function Get-StatusFieldInfo {
    param(
        [Parameter(Mandatory)][array]$Fields,
        [Parameter(Mandatory)][string]$FieldName
    )

    $statusField = $Fields | Where-Object { $_.name -eq $FieldName }
    
    if (-not $statusField) {
        throw "Status field '$FieldName' not found in project. Available fields: $($Fields.name -join ', ')"
    }

    if (-not $statusField.options) {
        throw "Field '$FieldName' exists but has no options. Is it a single-select field?"
    }

    # Build mapping: status value -> option ID
    $mapping = @{}
    foreach ($option in $statusField.options) {
        $mapping[$option.name] = $option.id
    }

    return [PSCustomObject]@{
        FieldId = $statusField.id
        OptionIds = $mapping
    }
}

# ---------------------------------------------------------------------------
# Helper: Map phase status to GitHub Project option
# ---------------------------------------------------------------------------
function Get-GitHubStatusOption {
    param(
        [Parameter(Mandatory)][string]$PhaseStatus,
        [Parameter(Mandatory)][hashtable]$OptionIds
    )

    # Standard mapping
    $mapping = @{
        'not_started' = 'Todo'
        'in_progress' = 'In Progress'
        'done' = 'Done'
        'blocked' = 'Blocked'
    }

    $targetOption = $mapping[$PhaseStatus]
    if (-not $targetOption) {
        Write-Warning "Unknown phase status '$PhaseStatus'. Defaulting to 'Todo'."
        $targetOption = 'Todo'
    }

    if (-not $OptionIds.ContainsKey($targetOption)) {
        throw "Status option '$targetOption' not found in project. Available: $($OptionIds.Keys -join ', ')"
    }

    return $OptionIds[$targetOption]
}

# ---------------------------------------------------------------------------
# Helper: Update phase status in GitHub Project
# ---------------------------------------------------------------------------
function Update-GitHubProjectItemStatus {
    param(
        [Parameter(Mandatory)][object]$Phase,
        [Parameter(Mandatory)][int]$ProjectNumber,
        [Parameter(Mandatory)][string]$ProjectOwner,
        [Parameter(Mandatory)][string]$FieldId,
        [Parameter(Mandatory)][string]$OptionId,
        [switch]$DryRun
    )

    Assert-CommandAvailable -Name "gh"

    $itemId = $Phase.gh_item_id
    $phaseId = $Phase.phase_id
    $status = $Phase.status

    if ([string]::IsNullOrWhiteSpace($itemId)) {
        Write-Warning "Phase '$phaseId' has no gh_item_id. Run sync script first."
        return $false
    }

    if ($DryRun) {
        Write-Host "[DRY-RUN] Would update phase '$phaseId' → status '$status'" -ForegroundColor Cyan
        return $true
    }

    if (-not $PSCmdlet.ShouldProcess("Phase '$phaseId' (item $itemId)", "Update status to '$status'")) {
        return $false
    }

    Write-Verbose "Updating phase '$phaseId' (item $itemId) → status '$status'..."

    # Use gh project item-edit
    $output = gh project item-edit `
        --id $itemId `
        --project-id $ProjectNumber `
        --field-id $FieldId `
        --option-id $OptionId `
        2>&1

    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to update phase '$phaseId'. Output: $output"
        return $false
    }

    Write-Host "✓ Updated phase '$phaseId' → status '$status'" -ForegroundColor Green
    return $true
}

# ---------------------------------------------------------------------------
# Helper: Load last sync state (to detect changes)
# ---------------------------------------------------------------------------
function Get-LastSyncState {
    param([Parameter(Mandatory)][string]$PlanPath)

    $stateFile = "$PlanPath.sync_state.json"
    
    if (-not (Test-Path $stateFile)) {
        Write-Verbose "No previous sync state found. Will update all phases."
        return @{}
    }

    try {
        $state = Get-Content $stateFile -Raw | ConvertFrom-Json -AsHashtable
        Write-Verbose "Loaded previous sync state: $($state.Keys.Count) phases"
        return $state
    } catch {
        Write-Warning "Failed to load sync state: $_. Will update all phases."
        return @{}
    }
}

# ---------------------------------------------------------------------------
# Helper: Save current sync state
# ---------------------------------------------------------------------------
function Save-SyncState {
    param(
        [Parameter(Mandatory)][string]$PlanPath,
        [Parameter(Mandatory)][array]$Phases
    )

    $stateFile = "$PlanPath.sync_state.json"
    
    $state = @{}
    foreach ($phase in $Phases) {
        $state[$phase.phase_id] = @{
            status = $phase.status
            gh_item_id = $phase.gh_item_id
            last_sync = (Get-Date).ToString('o')
        }
    }

    $state | ConvertTo-Json -Depth 10 | Set-Content $stateFile -Encoding UTF8
    Write-Verbose "Saved sync state to '$stateFile'"
}

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  UET Phase Plan Status → GitHub Project Sync" -ForegroundColor Cyan
Write-Host "  Pattern: PAT_EXEC_GHPROJECT_PHASE_STATUS_SYNC_V1" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

try {
    # Pre-flight checks
    Write-Verbose "Running pre-flight checks..."
    Assert-CommandAvailable -Name "gh"
    Assert-CmdletAvailable -Name "ConvertFrom-Yaml"
    
    # Verify GitHub CLI authentication
    $authStatus = gh auth status 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "GitHub CLI not authenticated. Run 'gh auth login' first."
    }

    # Load phase plan
    $planInfo = Load-UetPhasePlan -Path $PlanPath
    $plan = $planInfo.Plan
    $phases = $planInfo.Phases

    Write-Host "Loaded $($phases.Count) phase(s) from '$PlanPath'" -ForegroundColor Gray
    Write-Host ""

    # Get project field metadata
    Write-Host "Fetching GitHub Project field configuration..." -ForegroundColor Gray
    $fields = Get-GitHubProjectFields -ProjectNumber $ProjectNumber -ProjectOwner $ProjectOwner
    $statusField = Get-StatusFieldInfo -Fields $fields -FieldName $StatusFieldName

    Write-Host "✓ Found status field '$StatusFieldName' with $($statusField.OptionIds.Count) options" -ForegroundColor Green
    Write-Host "  Available statuses: $($statusField.OptionIds.Keys -join ', ')" -ForegroundColor Gray
    Write-Host ""

    # Load last sync state
    $lastState = Get-LastSyncState -PlanPath $PlanPath

    # Determine which phases need updates
    $phasesToUpdate = @()
    
    foreach ($phase in $phases) {
        if (-not $phase.gh_item_id) {
            Write-Warning "Phase '$($phase.phase_id)' has no gh_item_id. Skipping."
            continue
        }

        # Check if status changed since last sync
        $needsUpdate = $Force
        
        if (-not $Force) {
            $lastStatus = $lastState[$phase.phase_id]?.status
            if ($lastStatus -ne $phase.status) {
                $needsUpdate = $true
                Write-Verbose "Phase '$($phase.phase_id)' status changed: $lastStatus → $($phase.status)"
            }
        }

        if ($needsUpdate) {
            $phasesToUpdate += $phase
        }
    }

    if ($phasesToUpdate.Count -eq 0) {
        Write-Host "✓ All phases are up-to-date. No changes needed." -ForegroundColor Green
        Write-Host ""
        Write-Host "Tip: Use -Force to update all phases regardless of changes." -ForegroundColor Gray
        Write-Host ""
        return
    }

    Write-Host "$($phasesToUpdate.Count) phase(s) will be updated:" -ForegroundColor Yellow
    foreach ($phase in $phasesToUpdate) {
        $lastStatus = $lastState[$phase.phase_id]?.status
        $changeIndicator = if ($lastStatus) { "($lastStatus → $($phase.status))" } else { "(new)" }
        Write-Host "  • $($phase.phase_id): $($phase.title) $changeIndicator" -ForegroundColor Gray
    }
    Write-Host ""

    if ($DryRun) {
        Write-Host "[DRY-RUN MODE] No changes will be made." -ForegroundColor Cyan
        Write-Host ""
    }

    # Update each phase
    $successCount = 0
    $failCount = 0

    foreach ($phase in $phasesToUpdate) {
        try {
            $optionId = Get-GitHubStatusOption -PhaseStatus $phase.status -OptionIds $statusField.OptionIds
            
            $success = Update-GitHubProjectItemStatus `
                -Phase $phase `
                -ProjectNumber $ProjectNumber `
                -ProjectOwner $ProjectOwner `
                -FieldId $statusField.FieldId `
                -OptionId $optionId `
                -DryRun:$DryRun

            if ($success) {
                $successCount++
            } else {
                $failCount++
            }
        } catch {
            Write-Error "Failed to update phase '$($phase.phase_id)': $_"
            $failCount++
        }
    }

    if (-not $DryRun) {
        # Save sync state
        Save-SyncState -PlanPath $PlanPath -Phases $phases
    }

    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host "  Status Sync Complete!" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
    
    if ($DryRun) {
        Write-Host "Dry-run complete. No changes were made." -ForegroundColor Cyan
    } else {
        Write-Host "✓ Updated: $successCount phase(s)" -ForegroundColor Green
        if ($failCount -gt 0) {
            Write-Host "✗ Failed: $failCount phase(s)" -ForegroundColor Red
        }
        Write-Host ""
        Write-Host "Sync state saved to: $PlanPath.sync_state.json" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. View your project: gh project view $ProjectNumber --owner $ProjectOwner --web" -ForegroundColor Gray
    Write-Host "  2. Update phase status in YAML as work progresses" -ForegroundColor Gray
    Write-Host "  3. Re-run this script to sync status changes" -ForegroundColor Gray
    Write-Host ""

} catch {
    Write-Host ""
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    exit 1
}
