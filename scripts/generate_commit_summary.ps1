<#
.SYNOPSIS
    Generate a commit summary for the last 6 hours (or custom time window)

.DESCRIPTION
    Collects git commits from the specified time window, analyzes them by phase
    and subsystem, and generates a structured commit summary using the template.

    Designed to be run every 6 hours by automation or on-demand.

.PARAMETER Hours
    Number of hours to look back (default: 6)

.PARAMETER Branches
    Comma-separated list of branches to analyze (default: current branch)

.PARAMETER OutputDir
    Directory to write the summary (default: docs/commit_summaries)

.PARAMETER Mode
    Generation mode: auto_6h or on_demand (default: on_demand)

.EXAMPLE
    .\generate_commit_summary.ps1
    Generate summary for last 6 hours on current branch

.EXAMPLE
    .\generate_commit_summary.ps1 -Hours 12 -Branches "main,feature/x"
    Generate summary for last 12 hours across multiple branches

.EXAMPLE
    .\generate_commit_summary.ps1 -Mode auto_6h
    Run in automated 6-hour mode
#>

param(
    [int]$Hours = 6,
    [string]$Branches = "",
    [string]$OutputDir = "docs\commit_summaries",
    [string]$Mode = "on_demand"
)

$ErrorActionPreference = "Stop"

# Ensure we're in a git repo
if (-not (Test-Path .git)) {
    Write-Error "Not in a git repository root"
    exit 1
}

# Create output directory if needed
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# Calculate time window
$EndTime = Get-Date
$StartTime = $EndTime.AddHours(-$Hours)
$EndTimeStr = $EndTime.ToString("yyyy-MM-ddTHH:mm:sszzz")
$StartTimeStr = $StartTime.ToString("yyyy-MM-ddTHH:mm:sszzz")

# Determine branches to analyze
if ([string]::IsNullOrWhiteSpace($Branches)) {
    $BranchList = @((git rev-parse --abbrev-ref HEAD).Trim())
} else {
    $BranchList = $Branches -split ',' | ForEach-Object { $_.Trim() }
}

Write-Host "Analyzing commits from $StartTimeStr to $EndTimeStr"
Write-Host "Branches: $($BranchList -join ', ')"

# Get repo info
$RepoName = (git remote get-url origin 2>$null) -replace '.*[:/]([^/]+/[^/]+?)(\.git)?$', '$1'
if ([string]::IsNullOrWhiteSpace($RepoName)) {
    $RepoName = Split-Path -Leaf (Get-Location)
}
$DefaultBranch = (git symbolic-ref refs/remotes/origin/HEAD 2>$null) -replace 'refs/remotes/origin/', ''
if ([string]::IsNullOrWhiteSpace($DefaultBranch)) {
    $DefaultBranch = "main"
}

# Collect commits
$AllCommits = @()
foreach ($Branch in $BranchList) {
    $GitLog = git log $Branch --since="$StartTimeStr" --until="$EndTimeStr" `
        --pretty=format:"%H|%h|%an <%ae>|%aI|$Branch|%s" 2>$null

    if ($GitLog) {
        $AllCommits += $GitLog | ForEach-Object {
            $Parts = $_ -split '\|', 6
            [PSCustomObject]@{
                Hash = $Parts[0]
                ShortHash = $Parts[1]
                Author = $Parts[2]
                Timestamp = $Parts[3]
                Branch = $Parts[4]
                Summary = $Parts[5]
            }
        }
    }
}

# Deduplicate by hash (commits may appear on multiple branches)
$UniqueCommits = $AllCommits | Sort-Object -Property Hash -Unique | Sort-Object -Property Timestamp

Write-Host "Found $($UniqueCommits.Count) unique commits"

# Phase mapping (file path patterns → phase)
$PhasePatterns = @{
    'phase0_' = 'Phase 0'
    'phase1_' = 'Phase 1'
    'phase2_' = 'Phase 2'
    'phase3_' = 'Phase 3'
    'phase4_' = 'Phase 4'
    'phase5_' = 'Phase 5'
    'phase6_' = 'Phase 6'
    'phase7_' = 'Phase 7'
    'core/engine/' = 'Phase 5'
    'core/state/' = 'Phase 0'
    'error/' = 'Phase 6'
}

# Subsystem mapping
$SubsystemPatterns = @{
    'core/engine/' = 'core_engine'
    'core/state/' = 'core_engine'
    'error/engine/' = 'error_engine'
    'error/plugins/' = 'error_engine'
    'specifications/' = 'spec_bridge'
    'schema/' = 'spec_bridge'
    'aim/' = 'tool_adapters'
    'config/tool_profiles' = 'tool_adapters'
    '.state/' = 'state_persistence'
    'gui/' = 'gui_pm'
    'pm/' = 'gui_pm'
    'docs/' = 'docs_schemas'
}

# Analyze each commit
$CommitDetails = @()
$TotalFiles = 0
$TotalTests = 0
$TotalPipelines = 0
$Authors = @{}

foreach ($Commit in $UniqueCommits) {
    # Get files changed
    $FilesChanged = git diff-tree --no-commit-id --name-only -r $Commit.Hash
    $Files = @($FilesChanged)
    $TestFiles = @($Files | Where-Object { $_ -match '^tests/' })
    $PipelineFiles = @($Files | Where-Object { $_ -match '\.github/|\.yml$|\.yaml$|Jenkinsfile|\.gitlab-ci' })

    $TotalFiles += $Files.Count
    $TotalTests += $TestFiles.Count
    $TotalPipelines += $PipelineFiles.Count
    $Authors[$Commit.Author] = $true

    # Determine phases touched
    $PhasesTouched = @()
    foreach ($File in $Files) {
        foreach ($Pattern in $PhasePatterns.Keys) {
            if ($File -like "*$Pattern*") {
                $Phase = $PhasePatterns[$Pattern]
                if ($PhasesTouched -notcontains $Phase) {
                    $PhasesTouched += $Phase
                }
            }
        }
    }
    if ($PhasesTouched.Count -eq 0) { $PhasesTouched = @('UNKNOWN') }

    # Determine subsystems touched
    $SubsystemsTouched = @()
    foreach ($File in $Files) {
        foreach ($Pattern in $SubsystemPatterns.Keys) {
            if ($File -like "*$Pattern*") {
                $Subsystem = $SubsystemPatterns[$Pattern]
                if ($SubsystemsTouched -notcontains $Subsystem) {
                    $SubsystemsTouched += $Subsystem
                }
            }
        }
    }
    if ($SubsystemsTouched.Count -eq 0) { $SubsystemsTouched = @('UNKNOWN') }

    # Simple risk heuristic
    $Risk = "LOW"
    if ($Files.Count -gt 10 -or $TestFiles.Count -eq 0 -and $Files.Count -gt 3) {
        $Risk = "MEDIUM"
    }
    if ($PipelineFiles.Count -gt 0 -or $Files.Count -gt 20) {
        $Risk = "HIGH"
    }

    # Simple automation impact heuristic
    $AutomationImpact = "NEUTRAL"
    if ($TestFiles.Count -gt 0) { $AutomationImpact = "STRENGTHENED" }

    $CommitDetails += [PSCustomObject]@{
        hash = $Commit.Hash
        short_hash = $Commit.ShortHash
        author = $Commit.Author
        timestamp = $Commit.Timestamp
        branch = $Commit.Branch
        summary = $Commit.Summary
        phases_touched = $PhasesTouched
        subsystems_touched = $SubsystemsTouched
        files_changed = $Files
        tests_changed = $TestFiles
        risk = $Risk
        automation_impact = $AutomationImpact
        notes = ""
    }
}

# Overall risk
$OverallRisk = "LOW"
if ($CommitDetails | Where-Object { $_.risk -eq "HIGH" }) {
    $OverallRisk = "HIGH"
} elseif ($CommitDetails | Where-Object { $_.risk -eq "MEDIUM" }) {
    $OverallRisk = "MEDIUM"
}

# Generate focus signal
$FocusSignal = "TBD"
$PhaseFreq = @{}
foreach ($Commit in $CommitDetails) {
    foreach ($Phase in $Commit.phases_touched) {
        if ($Phase -ne "UNKNOWN") {
            $PhaseFreq[$Phase] = ($PhaseFreq[$Phase] ?? 0) + 1
        }
    }
}
if ($PhaseFreq.Count -gt 0) {
    $TopPhase = ($PhaseFreq.GetEnumerator() | Sort-Object -Property Value -Descending | Select-Object -First 1).Name
    $FocusSignal = "$TopPhase activity"
}

# Generate run ID
$RunId = "RUN-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

# Generate doc_id
$DocId = "COMMIT-SUMMARY-$(Get-Date -Format 'yyyyMMdd-HHmm')"

# Generate filename
$FileName = "COMMIT_SUMMARY_$(Get-Date -Format 'yyyyMMdd_HHmm').md"
$OutputPath = Join-Path $OutputDir $FileName

# Load template
$TemplatePath = "templates\COMMIT_SUMMARY_TEMPLATE.md"
if (-not (Test-Path $TemplatePath)) {
    Write-Error "Template not found: $TemplatePath"
    exit 1
}

$Template = Get-Content $TemplatePath -Raw

# Replace placeholders in frontmatter
$Output = $Template -replace 'doc_id: COMMIT-SUMMARY-PLACEHOLDER', "doc_id: $DocId"
$Output = $Output -replace 'run_id: RUN-PLACEHOLDER', "run_id: $RunId"
$Output = $Output -replace 'mode: auto_6h', "mode: $Mode"
$Output = $Output -replace 'start: 2025-01-01T00:00:00-06:00', "start: $StartTimeStr"
$Output = $Output -replace 'end:   2025-01-01T06:00:00-06:00', "end:   $EndTimeStr"
$Output = $Output -replace 'name: complete-ai-development-pipeline-canonical-phase-plan', "name: $RepoName"
$Output = $Output -replace 'default_branch: main', "default_branch: $DefaultBranch"
$Output = $Output -replace 'branches_analyzed:\s+- main\s+- feature/example', "branches_analyzed:`n$(($BranchList | ForEach-Object { "  - $_" }) -join "`n")"
$Output = $Output -replace 'commit_count: 0', "commit_count: $($UniqueCommits.Count)"
$Output = $Output -replace 'authors_count: 0', "authors_count: $($Authors.Count)"
$Output = $Output -replace 'files_changed: 0', "files_changed: $TotalFiles"
$Output = $Output -replace 'tests_changed: 0', "tests_changed: $TotalTests"
$Output = $Output -replace 'pipelines_touched: 0', "pipelines_touched: $TotalPipelines"
$Output = $Output -replace 'risk_overall: TBD', "risk_overall: $OverallRisk"
$Output = $Output -replace 'focus_signal: TBD', "focus_signal: $FocusSignal"

# Replace template placeholders in body
$Output = $Output -replace '\{\{commit_count\}\}', "$($UniqueCommits.Count)"
$Output = $Output -replace '\{\{files_changed\}\}', "$TotalFiles"
$Output = $Output -replace '\{\{tests_changed\}\}', "$TotalTests"
$Output = $Output -replace '\{\{pipelines_touched\}\}', "$TotalPipelines"

# Generate JSON commit inventory
$CommitJson = [PSCustomObject]@{
    time_window = @{
        start = $StartTimeStr
        end = $EndTimeStr
    }
    commits = $CommitDetails
} | ConvertTo-Json -Depth 10 -Compress:$false

# Replace JSON section
$Output = $Output -replace '(?s)```json.*?```', "``````json`n$CommitJson`n``````"

# Write output
$Output | Set-Content -Path $OutputPath -Encoding UTF8

Write-Host "✓ Commit summary generated: $OutputPath"
Write-Host "  Commits: $($UniqueCommits.Count)"
Write-Host "  Authors: $($Authors.Count)"
Write-Host "  Files: $TotalFiles"
Write-Host "  Risk: $OverallRisk"
Write-Host "  Focus: $FocusSignal"

exit 0
