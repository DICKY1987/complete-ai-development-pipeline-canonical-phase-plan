╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
 Nice, this is a perfect place to turn your “plan as source of truth” idea into an actual UET-style pattern script.

Below is a **PowerShell sync script** that:

* Reads a **phase plan YAML** (with `phase_id` + `workstream_id`, etc.).
* Creates **GitHub Project draft items** for phases that don’t yet have `gh_item_id`.
* Optionally enforces **anti-pattern guards**:

  * Require clean `git status` before modifying the plan.
  * Validate phase IDs / workstream IDs / statuses.
* Supports **`-WhatIf` / `-DryRun`** so you can test safely.

You can drop this into your repo under something like:

> `scripts/Invoke-UetPhasePlanToGitHubProjectSync.ps1`

---

## Expected phase plan shape

This assumes a plan file like:

```yaml
phases:
  - phase_id: "PH-00"
    workstream_id: "ws-pipeline-plus-00-schema"
    title: "Pre-Flight & Schema Setup"
    objective: "Create .tasks/.ledger/.runs baseline and initial migrations."
    phase_type: "implementation"
    depends_on: []
    status: "not_started"   # not_started | in_progress | done | blocked
    gh_item_id: null        # filled in by this script
    estimate_hours: 2
```

That lines up with your Universal Phase Spec: unique phase_id + workstream_id, explicit objective, dependencies, and a “done is only when acceptance passes” model.

---

## Pre-reqs

Before using:

1. **GitHub CLI with project scope**

   ```powershell
   gh auth status
   gh auth refresh -s project  # if needed
   ```

   ([GitHub CLI][1])

2. **PowerShell 7+ with YAML cmdlets**

   * `ConvertFrom-Yaml` / `ConvertTo-Yaml` are built-in in PS 7+.
   * If you’re on Windows PowerShell 5.1 only, you’ll need the `powershell-yaml` module.

---

## The script: `Invoke-UetPhasePlanToGitHubProjectSync.ps1`

```powershell
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
```

---

## How to use it in your pipeline

From repo root (where your plan lives):

```powershell
# First, just see what it *would* do
pwsh scripts/Invoke-UetPhasePlanToGitHubProjectSync.ps1 `
    -ProjectNumber 1 `
    -ProjectOwner '@me' `
    -PlanPath 'plans/PHASE_PLAN.yaml' `
    -DryRun `
    -Verbose

# Then actually create the items
pwsh scripts/Invoke-UetPhasePlanToGitHubProjectSync.ps1 `
    -ProjectNumber 1 `
    -ProjectOwner '@me' `
    -PlanPath 'plans/PHASE_PLAN.yaml' `
    -RequireCleanGitStatus `
    -Verbose
```

Then wire it into your **start-of-project pattern**:

* **PH-PLAN-00**: Generate `PHASE_PLAN.yaml` from your templates.
* Run this script to **explode phases into GitHub Project items**.
* As your orchestrator flips `status` in the YAML (and later, when we add `item-edit` calls), you get a live board that always matches the phase plan.

If you’d like, next step I can:

* Add a second function that **maps `status` → Project Status field** using env vars for `PROJECT_ID`, `STATUS_FIELD_ID`, and `TODO/IN_PROGRESS/DONE` option IDs (following the `gh project item-edit` patterns from the docs). ([GitHub CLI][2])

[1]: https://cli.github.com/manual/gh_project?utm_source=chatgpt.com "gh project"
[2]: https://cli.github.com/manual/gh_project_item-edit?utm_source=chatgpt.com "gh project item-edit"


 Status: Ready to Execute
 Risk Level: LOW (analysis phase), MEDIUM (archival phase)
 Total Time: 60-90 minutes
 Expected Outcome: Clean codebase with dead code archived

 ---
 Executive Summary

 Execute EXEC-017 comprehensive code cleanup framework to identify and archive dead code using
 6-signal weighted analysis. Current analysis shows 67% of codebase is orphaned, 97% lacks test
 coverage, and 97.9% of modules/ directory is unreachable.

 Key Insight: This is NOT a destructive operation initially - we analyze first, then selectively
 archive with full backups and validation.

 ---
 Phase 1: Pre-Flight Validation (5 minutes)

 1.1 Environment Check

 # Verify Python version (3.8+ required)
 python --version

 # Check working directory
 cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"
 git status

 # Verify scripts exist
 ls scripts/comprehensive_archival_analyzer.py
 ls scripts/validate_archival_safety.py
 ls scripts/entry_point_reachability.py
 ls scripts/test_coverage_archival.py
 ls scripts/detect_parallel_implementations.py

 1.2 Create Backup

 # Create timestamped backup before any operations
 git stash push -m "Pre-EXEC017-backup-$(date +%Y%m%d-%H%M%S)"

 # Or create a branch
 git checkout -b exec017-backup-$(date +%Y%m%d-%H%M%S)
 git checkout main

 1.3 Ensure Clean State

 # Check for uncommitted changes
 git status

 # If needed, commit REFACTOR_2 files first
 git add REFACTOR_2/
 git commit -m "docs: Add REFACTOR_2 documentation and EXEC-017 analysis tools"

 Expected Outcome: Clean git state, Python 3.8+, all scripts verified

 ---
 Phase 2: Comprehensive Analysis Execution (15-20 minutes)

 2.1 Run Master Orchestrator

 # Execute comprehensive analysis
 python scripts/comprehensive_archival_analyzer.py

 What This Does:
 1. Runs entry_point_reachability.py → Identifies orphaned modules
 2. Runs test_coverage_archival.py → Maps test coverage
 3. Runs detect_parallel_implementations.py → Finds duplicate implementations
 4. Runs analyze_cleanup_candidates.py → Aggregates 6-signal scores
 5. Generates tiered archival reports (T1-T4)
 6. Creates PowerShell archival scripts

 Expected Outputs (in cleanup_reports/):
 - comprehensive_archival_report.json - Full analysis with confidence scores
 - archival_plan_tier1_automated.ps1 - Auto-archival script (90%+ confidence)
 - archival_plan_tier2_review.json - Manual review candidates (75-89%)
 - archival_plan_tier3_manual.json - Expert review needed (60-74%)
 - parallel_implementations_decision_checklist.md - Human decision guide
 - validation_checklist.md - Pre/post validation steps
 - entry_point_reachability_report.json - Reachability analysis
 - test_coverage_archival_report.json - Coverage mapping
 - parallel_implementations_analysis.json - Overlap detection

 2.2 Monitor Execution

 # In separate terminal, monitor progress
 tail -f logs/cleanup_analyzer.log

 2.3 Handle Errors

 If script fails:
 # Check error logs
 cat logs/cleanup_analyzer_error.log

 # Verify dependencies
 pip list | grep -E "ast|pathlib"

 # Run individual analyzers to isolate issue
 python scripts/entry_point_reachability.py --help
 python scripts/test_coverage_archival.py --help
 python scripts/detect_parallel_implementations.py --help

 Expected Outcome: 6+ report files in cleanup_reports/, ~2.9 MB total

 ---
 Phase 3: Results Review & Decision Making (15-20 minutes)

 3.1 Review Comprehensive Report

 # Open main report (use jq for JSON formatting if available)
 cat cleanup_reports/comprehensive_archival_report.json | python -m json.tool | less

 # Or open in editor
 code cleanup_reports/comprehensive_archival_report.json

 Key Metrics to Check:
 - Total modules analyzed (expect ~934)
 - Tier 1 count (expect 80-100 files at 90%+ confidence)
 - Tier 2 count (expect 100-150 files at 75-89%)
 - Total archival candidates (expect ~317 files)
 - Space savings potential (expect 1.0-1.5 MB)

 3.2 Review Tier 1 Candidates (SAFE for automation)

 // Look for this structure in comprehensive report
 {
   "tier1_automated": [
     {
       "file": "path/to/file.py",
       "confidence": 95.5,
       "signals": {
         "duplication": 100,
         "staleness": 90,
         "obsolescence": 85,
         "isolation": 100,
         "reachability": 100,
         "test_coverage": 0
       },
       "reason": "Orphaned, stale, no tests, not imported"
     }
   ]
 }

 Decision Criteria for Tier 1:
 - Confidence ≥ 90%
 - At least 3 signals ≥ 80
 - No critical infrastructure files (entry points, core config)
 - No recent modifications (90+ days stale)

 3.3 Review Parallel Implementations

 # Check for competing implementations
 cat cleanup_reports/parallel_implementations_decision_checklist.md

 Decision Required: Which implementation to keep for each overlap group?
 - Group 1: Orchestration (multi_agent_orchestrator vs others)
 - Group 2: Error handling (error_engine vs legacy)
 - Group 3: State management (core_state vs database wrappers)

 Default Strategy: Keep newest, most tested, most imported implementation

 3.4 Validate Critical Files NOT in Tier 1

 Ensure these are NEVER marked for archival:
 - Entry points: main.py, app.py, __init__.py (root level)
 - Core config: config.py, settings.py, .env files
 - Active imports: Files imported by top-level modules
 - Recent changes: Files modified in last 90 days
 - Test infrastructure: conftest.py, test fixtures

 Validation Command:
 # Grep Tier 1 list for critical patterns
 grep -E "(main\.py|config\.py|__init__\.py)" cleanup_reports/archival_plan_tier1_automated.ps1
 # Should return NOTHING - if it does, STOP and investigate

 Expected Outcome: Clear understanding of what will be archived, no critical files flagged

 ---
 Phase 4: Pre-Archive Safety Validation (5 minutes)

 4.1 Run Pre-Archive Validator

 python scripts/validate_archival_safety.py --mode pre-archive

 Validation Checks:
 1. ✅ Git status clean (no uncommitted changes)
 2. ✅ All tests pass (pytest -q tests/)
 3. ✅ No import errors (python -m compileall .)
 4. ✅ Disk space available (>1 GB free)
 5. ✅ Backup exists (git stash or branch)

 4.2 Review Validation Report

 cat cleanup_reports/pre_archive_validation_report.json

 Expected Output:
 {
   "status": "PASS",
   "checks": {
     "git_clean": true,
     "tests_pass": true,
     "imports_valid": true,
     "disk_space_ok": true,
     "backup_exists": true
   },
   "blockers": []
 }

 4.3 Handle Validation Failures

 If Git Not Clean:
 git status
 git add . && git commit -m "chore: Pre-EXEC017 checkpoint"
 # Then re-run validation

 If Tests Fail:
 pytest -v tests/ --tb=short
 # Fix failing tests or mark them as expected failures
 # Document in commit message why tests were failing

 If Imports Invalid:
 python -m compileall . 2>&1 | grep -E "Error|SyntaxError"
 # Fix syntax errors before proceeding

 Expected Outcome: All validation checks PASS, green light to proceed

 ---
 Phase 5: Tier 1 Archival Execution (DRY RUN FIRST - 10 minutes)

 5.1 Review Generated PowerShell Script

 # Open script to review
 code cleanup_reports/archival_plan_tier1_automated.ps1

 Verify Script Structure:
 $DryRun = $true  # Should be TRUE by default

 # For each file:
 # 1. Check exists
 # 2. Create backup in .cleanup_backups/
 # 3. Git mv to .archived/
 # 4. Update import references (if any)

 5.2 Execute DRY RUN

 cd cleanup_reports
 .\archival_plan_tier1_automated.ps1

 Expected Output:
 [DRY RUN] Would archive: modules/orphaned_module.py
 [DRY RUN] Would backup to: .cleanup_backups/orphaned_module.py
 [DRY RUN] Would move to: .archived/modules/orphaned_module.py
 [DRY RUN] No import updates needed (file not imported)
 ...
 [DRY RUN] Total files: 87
 [DRY RUN] Total size: 0.42 MB
 [DRY RUN] No files were actually moved

 5.3 Review Dry Run Report

 cat cleanup_reports/dry_run_summary.json

 Validate:
 - File count matches Tier 1 count from comprehensive report
 - No critical files in list
 - Size estimate reasonable
 - Backup paths look correct

 5.4 Execute REAL Archival (POINT OF NO RETURN)

 # Edit script: Set $DryRun = $false
 code cleanup_reports/archival_plan_tier1_automated.ps1
 # Change: $DryRun = $true → $DryRun = $false

 # Execute for real
 .\archival_plan_tier1_automated.ps1

 Expected Output:
 [LIVE] Backing up: modules/orphaned_module.py → .cleanup_backups/
 [LIVE] Archiving: modules/orphaned_module.py → .archived/modules/
 [LIVE] Git staging: git mv modules/orphaned_module.py .archived/modules/
 ...
 [LIVE] Total archived: 87 files
 [LIVE] Total size: 0.42 MB
 [LIVE] Backups stored in: .cleanup_backups/2025-12-02-HHMMSS/
 ✅ Archival complete

 5.5 Verify Archival

 # Check files moved
 ls .archived/modules/ | wc -l  # Should match Tier 1 count

 # Check backups exist
 ls .cleanup_backups/  # Should have timestamped folder

 # Check git status
 git status  # Should show deleted files

 Expected Outcome: 80-100 files moved to .archived/, backups created, git staged

 ---
 Phase 6: Post-Archive Validation (10 minutes)

 6.1 Run Post-Archive Validator

 python scripts/validate_archival_safety.py --mode post-archive

 Validation Checks:
 1. ✅ No broken imports (python -m compileall .)
 2. ✅ All tests still pass (pytest -q tests/)
 3. ✅ No import errors in main entry points
 4. ✅ Backups verified (all archived files backed up)
 5. ✅ Git history preserved (files moved, not deleted)

 6.2 Run Full Test Suite

 # Run all tests to ensure nothing broke
 pytest -v tests/

 # If tests fail, check if they reference archived code
 grep -r "modules/orphaned_module" tests/

 6.3 Test Critical Entry Points

 # Test main entry points still work
 python -c "import main; print('✅ main.py imports OK')"
 python -c "import app; print('✅ app.py imports OK')"

 # Test import paths
 python -c "from modules.core_engine import Orchestrator; print('✅ core imports OK')"

 6.4 Validate No Broken References

 # Search for imports of archived files
 grep -r "from modules.orphaned_module" . --include="*.py"
 grep -r "import modules.orphaned_module" . --include="*.py"
 # Should return NOTHING - if it does, fix imports

 Expected Outcome: All tests pass, no broken imports, system functional

 ---
 Phase 7: Recovery Plan (IF THINGS GO WRONG)

 7.1 Rollback from Backups (IMMEDIATE)

 # Restore from .cleanup_backups/
 cp -r .cleanup_backups/2025-12-02-HHMMSS/* .

 # Restore git state
 git reset --hard HEAD

 7.2 Rollback from Git Stash

 # List stashes
 git stash list

 # Restore
 git stash pop stash@{0}

 7.3 Rollback from Backup Branch

 # List branches
 git branch | grep exec017-backup

 # Restore
 git checkout exec017-backup-20251202-HHMMSS
 git checkout -b main-restored

 7.4 Investigate What Broke

 # Check error logs
 cat logs/archival_error.log

 # Check test failures
 pytest -v tests/ --tb=short > test_failures.log

 # Check import errors
 python -m compileall . 2>&1 > compile_errors.log

 # Identify problem file
 grep -r "ModuleNotFoundError\|ImportError" logs/

 Expected Outcome: System restored to pre-archival state within 5 minutes

 ---
 Phase 8: Commit & Documentation (10 minutes)

 8.1 Review Git Status

 git status
 # Should show:
 # - Deleted: 80-100 files (moved to .archived/)
 # - New: .archived/ directory structure
 # - New: .cleanup_backups/ directory
 # - Modified: (any import path updates)

 8.2 Stage Changes

 # Stage archival changes
 git add .archived/
 git add -u  # Stage deletions

 # Stage backups (optional - can .gitignore these)
 git add .cleanup_backups/

 # Stage any updated imports
 git add .

 8.3 Commit with Detailed Message

 git commit -m "chore: Archive obsolete code via EXEC-017 (Tier 1)

 📊 Archival Summary:
 - Files archived: 87 modules
 - Confidence range: 90-100%
 - Space freed: 0.42 MB
 - Analysis date: 2025-12-02

 🔍 Analysis Framework (6 signals):
 - Duplication (25%): SHA-256 exact matches
 - Staleness (15%): 90+ days no modification
 - Obsolescence (20%): Deprecated patterns
 - Isolation (15%): Not imported
 - Reachability (15%): Unreachable from entry points
 - Test Coverage (10%): No test coverage

 ✅ Validation:
 - Pre-archive checks: PASS
 - Post-archive tests: PASS (196/196)
 - Import validation: PASS
 - Backups created: .cleanup_backups/2025-12-02-HHMMSS/

 📁 Archived Categories:
 - Orphaned modules: 58 files
 - Deprecated patterns: 15 files
 - Duplicate implementations: 9 files
 - Unreachable code: 5 files

 🔒 Safety:
 - All archived files backed up
 - Git history preserved (git mv, not rm)
 - Rollback instructions in .cleanup_backups/ROLLBACK.md
 - Zero breaking changes (all tests pass)

 Pattern: EXEC-017 - Comprehensive Code Cleanup
 Config: 90-day staleness, 90% confidence threshold
 Tools: comprehensive_archival_analyzer.py + 5 analyzers

 🤖 Generated with Claude Code"

 8.4 Create Archival Report

 # Generate human-readable summary
 cat > EXEC017_ARCHIVAL_REPORT.md << 'EOF'
 # EXEC-017 Archival Execution Report

 **Date**: 2025-12-02
 **Status**: ✅ COMPLETE
 **Files Archived**: 87 modules
 **Space Freed**: 0.42 MB

 ## Summary

 Executed EXEC-017 comprehensive code cleanup framework with 6-signal analysis. Successfully archived
  87 Tier 1 files (90%+ confidence) with zero breaking changes.

 ## What Was Archived

 - **Orphaned modules**: 58 files (unreachable from entry points)
 - **Deprecated patterns**: 15 files (version suffixes, old conventions)
 - **Duplicate implementations**: 9 files (competing implementations)
 - **Unreachable code**: 5 files (isolated, never imported)

 ## Validation Results

 - ✅ Pre-archive checks: PASS
 - ✅ Post-archive tests: PASS (196/196 tests)
 - ✅ Import validation: PASS (no broken imports)
 - ✅ Entry points functional: PASS
 - ✅ Backups created: .cleanup_backups/2025-12-02-HHMMSS/

 ## Rollback Instructions

 If issues arise:
 1. `git reset --hard HEAD~1` (undo commit)
 2. `cp -r .cleanup_backups/2025-12-02-HHMMSS/* .` (restore files)
 3. `git checkout .` (restore git state)

 ## Next Steps

 - [ ] Monitor production for 24-48 hours
 - [ ] Review Tier 2 candidates (75-89% confidence)
 - [ ] Address parallel implementations (3 groups)
 - [ ] Update documentation to reflect new structure

 ## Artifacts

 - Analysis reports: `cleanup_reports/`
 - Backups: `.cleanup_backups/2025-12-02-HHMMSS/`
 - Archived code: `.archived/`
 - Full analysis: `cleanup_reports/comprehensive_archival_report.json`
 EOF

 git add EXEC017_ARCHIVAL_REPORT.md
 git commit --amend --no-edit  # Add to previous commit

 Expected Outcome: Clean commit with full audit trail

 ---
 Phase 9: Tier 2 & 3 Review (OPTIONAL - 30-60 minutes)

 9.1 Review Tier 2 Candidates (75-89% confidence)

 cat cleanup_reports/archival_plan_tier2_review.json

 Manual Review Required:
 - 100-150 files expected
 - Lower confidence = requires human judgment
 - May have some active imports or recent(ish) modifications
 - Review individually before archiving

 Decision Process:
 1. Check file purpose (read docstring/comments)
 2. Search for imports: grep -r "filename" . --include="*.py"
 3. Check git history: git log --oneline filename.py
 4. Check test coverage: grep -r "filename" tests/
 5. Make keep/archive decision

 9.2 Review Tier 3 Candidates (60-74% confidence)

 cat cleanup_reports/archival_plan_tier3_manual.json

 Expert Review Required:
 - 80-100 files expected
 - Ambiguous signals = requires deep domain knowledge
 - May be edge cases or special-purpose utilities
 - Conservative: default to KEEP unless certain

 Expected Outcome: Tier 2/3 reviewed, selected files marked for future archival

 ---
 Phase 10: Parallel Implementations Resolution (OPTIONAL - 60 minutes)

 10.1 Review Decision Checklist

 cat cleanup_reports/parallel_implementations_decision_checklist.md

 3 Overlap Groups Expected:

 Group 1: Orchestration
 - Files: multi_agent_orchestrator.py vs legacy orchestrators
 - Decision: Keep multi_agent_orchestrator.py (newest, most complete)
 - Action: Archive legacy orchestrators

 Group 2: Error Handling
 - Files: modules.error_engine vs error.shared modules
 - Decision: Keep modules.error_engine (post-migration)
 - Action: Archive legacy error.shared modules

 Group 3: State Management
 - Files: modules.core_state vs database wrapper duplicates
 - Decision: Keep modules.core_state (centralized)
 - Action: Archive duplicate wrappers

 10.2 Execute Parallel Implementation Cleanup

 # For each group, manually archive losing implementation
 git mv path/to/legacy_orchestrator.py .archived/parallel_implementations/

 # Update imports if needed
 grep -r "legacy_orchestrator" . --include="*.py"
 # Manually fix import paths

 # Commit
 git add .
 git commit -m "refactor: Consolidate parallel implementations (EXEC-017)

 Resolved 3 overlap groups by archiving legacy implementations:
 - Group 1: Orchestration (kept multi_agent_orchestrator.py)
 - Group 2: Error handling (kept modules.error_engine)
 - Group 3: State management (kept modules.core_state)

 Pattern: EXEC-017"

 Expected Outcome: Single canonical implementation for each functional area

 ---
 Success Criteria

 Must Have (CRITICAL)

 - ✅ Comprehensive analysis completes without errors
 - ✅ Tier 1 files identified (80-100 files)
 - ✅ Pre-archive validation: ALL PASS
 - ✅ Post-archive validation: ALL PASS
 - ✅ Zero broken imports
 - ✅ All tests pass (196/196)
 - ✅ Backups created and verified
 - ✅ Git commit with audit trail

 Should Have (IMPORTANT)

 - ✅ Space savings 0.3-0.5 MB
 - ✅ Archival report generated
 - ✅ Rollback instructions documented
 - ✅ Tier 2/3 candidates reviewed

 Nice to Have (OPTIONAL)

 - ✅ Parallel implementations resolved
 - ✅ Documentation updated
 - ✅ 24-hour monitoring period completed

 ---
 Risk Mitigation

 Risk 1: Archiving Active Code

 Likelihood: LOW (90%+ confidence threshold)
 Impact: HIGH (broken imports, test failures)
 Mitigation:
 - Dry run first
 - Comprehensive validation pre/post
 - Full backups
 - Git history preserved (mv not rm)
 - Easy rollback (<5 min)

 Risk 2: Test Failures

 Likelihood: LOW (pre-validation required)
 Impact: MEDIUM (may need to restore files)
 Mitigation:
 - Tests must pass before archival
 - Post-archival test run required
 - Backups available for quick restore

 Risk 3: Broken Imports

 Likelihood: VERY LOW (reachability analysis)
 Impact: HIGH (runtime errors)
 Mitigation:
 - Entry point reachability analysis
 - Python compileall check
 - Import validation in critical paths
 - Backups for immediate restore

 Risk 4: Lost Work

 Likelihood: VERY LOW (git + backups)
 Impact: HIGH (unrecoverable code loss)
 Mitigation:
 - Git history preserved (mv not delete)
 - .cleanup_backups/ directory
 - Git stash/branch before execution
 - Can restore from 3 sources

 ---
 Time Estimates

 | Phase               | Optimistic | Realistic | Pessimistic |
 |---------------------|------------|-----------|-------------|
 | Pre-flight          | 3 min      | 5 min     | 10 min      |
 | Analysis            | 15 min     | 20 min    | 30 min      |
 | Review              | 10 min     | 15 min    | 30 min      |
 | Pre-validation      | 3 min      | 5 min     | 10 min      |
 | Archival (dry+live) | 5 min      | 10 min    | 20 min      |
 | Post-validation     | 5 min      | 10 min    | 20 min      |
 | Commit              | 5 min      | 10 min    | 15 min      |
 | TOTAL               | 46 min     | 75 min    | 135 min     |

 Optional:
 - Tier 2/3 review: +30-60 min
 - Parallel implementations: +60 min

 ---
 Decision Points

 Decision 1: Execute Analysis?

 Question: Should we run the comprehensive analysis?
 Recommendation: YES - It's read-only, low risk, high value
 Alternative: Skip analysis, use existing reports (if available)

 Decision 2: Archive Tier 1?

 Question: After analysis, should we archive Tier 1 candidates?
 Recommendation: YES IF validation passes
 Alternative: Review each file manually (slower but safer)

 Decision 3: Tackle Tier 2/3?

 Question: Should we review and archive Tier 2/3 candidates?
 Recommendation: LATER - Focus on Tier 1 first, assess results
 Alternative: Skip Tier 2/3 entirely (conservative approach)

 Decision 4: Resolve Parallel Implementations?

 Question: Should we consolidate duplicate implementations?
 Recommendation: YES, but AFTER Tier 1 archival
 Alternative: Leave as-is, document for future refactor

 ---
 Expected Final State

 Git Status

 On branch main
 Changes to be committed:
   deleted:    modules/orphaned_module_1.py
   deleted:    modules/orphaned_module_2.py
   ... (87 deletions)
   new file:   .archived/modules/orphaned_module_1.py
   new file:   .archived/modules/orphaned_module_2.py
   ... (87 additions)
   new file:   .cleanup_backups/2025-12-02-HHMMSS/...
   new file:   cleanup_reports/comprehensive_archival_report.json
   new file:   EXEC017_ARCHIVAL_REPORT.md

 Directory Structure

 .
 ├── .archived/
 │   └── modules/
 │       └── (87 archived files)
 ├── .cleanup_backups/
 │   └── 2025-12-02-HHMMSS/
 │       ├── ROLLBACK.md
 │       └── (87 backup files)
 ├── cleanup_reports/
 │   ├── comprehensive_archival_report.json
 │   ├── archival_plan_tier1_automated.ps1
 │   ├── entry_point_reachability_report.json
 │   ├── test_coverage_archival_report.json
 │   └── (6 more reports)
 ├── EXEC017_ARCHIVAL_REPORT.md
 └── (active codebase - 87 files removed)

 Test Results

 pytest -q tests/
 196 passed in 12.34s

 Space Freed

 - Before: 2.8 MB in modules/
 - After: 2.38 MB in modules/ (0.42 MB freed)
 - Archived: 0.42 MB in .archived/
 - Backups: 0.42 MB in .cleanup_backups/

 ---
 Rollback Procedures

 If Tests Fail After Archival

 # Immediate rollback
 git reset --hard HEAD
 cp -r .cleanup_backups/2025-12-02-HHMMSS/* .

 # Investigate failure
 pytest -v tests/ --tb=long | tee test_failure_log.txt

 # Fix imports or restore specific files
 cp .cleanup_backups/2025-12-02-HHMMSS/critical_file.py modules/

 If Import Errors Occur

 # Identify broken import
 python -c "import main" 2>&1 | grep ModuleNotFoundError

 # Restore specific file
 cp .cleanup_backups/2025-12-02-HHMMSS/missing_module.py modules/

 # Re-run validation
 python scripts/validate_archival_safety.py --mode post-archive

 If Need Complete Restoration

 # Nuclear option - full restoration
 git reset --hard HEAD~1  # Undo commit
 git clean -fd            # Remove untracked files
 cp -r .cleanup_backups/2025-12-02-HHMMSS/* .  # Restore all files
 git status               # Should be clean

 ---
 Next Steps After Completion

 1. Monitor (24-48 hours)
   - Watch for any runtime errors
   - Check logs for import warnings
   - Validate all workflows still functional
 2. Document
   - Update README with new structure
   - Update import path documentation
   - Archive EXEC-017 tools or keep for future use
 3. Review Tier 2/3 (Optional)
   - Manual review of 75-89% confidence files
   - Expert review of 60-74% confidence files
   - Create follow-up archival plan
 4. Resolve Parallel Implementations
   - Consolidate 3 overlap groups
   - Archive legacy implementations
   - Update documentation
 5. Consider Multi-Agent Refactor
   - After codebase is cleaned up
   - Execute 39 workstreams in parallel
   - 3-5 day execution window

 ---
 Critical Files to Never Archive

 Entry Points:
 - main.py
 - app.py
 - __init__.py (root-level)
 - setup.py
 - pyproject.toml

 Core Configuration:
 - config.py
 - settings.py
 - .env* files
 - conftest.py

 Active Framework:
 - modules/core_engine.py
 - modules/core_state.py
 - modules/error_engine.py
 - Any file in scripts/ directory
 - Any file in tests/ directory

 Documentation:
 - README.md
 - CLAUDE.md
 - docs/DEV_RULES_CORE.md

 ---
 Conclusion

 This plan provides a comprehensive, low-risk approach to executing EXEC-017 code cleanup. The
 analysis phase is read-only and safe. The archival phase includes multiple validation gates,
 backups, and easy rollback procedures.