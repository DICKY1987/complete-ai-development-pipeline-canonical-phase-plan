# UET Phase Plan → GitHub Project Sync Setup

**Pattern**: `PAT_EXEC_GHPROJECT_PHASE_PLAN_SYNC_V1`  
**Script**: `scripts/Invoke-UetPhasePlanToGitHubProjectSync.ps1`  
**Status**: Ready for use

---

## What This Does

Syncs your phase plan YAML files into GitHub Projects automatically, making the YAML the **single source of truth** for project management.

**Key Features**:
- ✅ Creates GitHub Project items from phase plan YAML
- ✅ Writes `gh_item_id` back to YAML (bidirectional sync)
- ✅ Anti-pattern guards (clean git, validation, uniqueness checks)
- ✅ Dry-run mode for safety
- ✅ PowerShell 7+ with YAML support

---

## Prerequisites

### 1. Install GitHub CLI

```bash
# Windows (winget)
winget install GitHub.cli

# Or download from https://cli.github.com/
```

### 2. Authenticate with Project Scope

```powershell
gh auth login
gh auth refresh -s project
gh auth status  # Verify 'project' scope is listed
```

### 3. PowerShell 7+

```powershell
# Check version
$PSVersionTable.PSVersion

# Install if needed (Windows)
winget install Microsoft.PowerShell

# Or download from https://github.com/PowerShell/PowerShell/releases
```

PowerShell 7+ has built-in `ConvertFrom-Yaml` and `ConvertTo-Yaml`.

---

## Phase Plan YAML Format

The script expects this structure:

```yaml
phases:
  - phase_id: "PH-WEEK2-DAY1"
    workstream_id: "ws-multi-instance-cli"
    title: "ClusterManager Core Implementation"
    objective: "Implement high-level launch_cluster() API with basic routing"
    phase_type: "implementation"
    depends_on: []
    status: "not_started"   # not_started | in_progress | done | blocked
    gh_item_id: null        # filled by script
    estimate_hours: 6
    
  - phase_id: "PH-WEEK2-DAY2"
    workstream_id: "ws-multi-instance-cli"
    title: "Routing Strategies"
    objective: "Implement round-robin, least-busy, and sticky routers"
    phase_type: "implementation"
    depends_on: ["PH-WEEK2-DAY1"]
    status: "not_started"
    gh_item_id: null
    estimate_hours: 6
```

**Required Fields**:
- `phase_id` - Unique identifier
- `workstream_id` - Workstream this belongs to
- `title` - Human-readable title
- `objective` - What this phase accomplishes
- `status` - One of: `not_started`, `in_progress`, `done`, `blocked`

**Optional Fields**:
- `phase_type` - Type of phase (implementation, planning, etc.)
- `depends_on` - Array of phase_ids this depends on
- `estimate_hours` - Estimated effort
- `gh_item_id` - GitHub Project item ID (auto-filled)

---

## Usage

### Step 1: Create GitHub Project

```powershell
# Create a new project
gh project create --owner @me --title "Multi-Instance CLI Control"

# List projects to get the number
gh project list --owner @me
```

Note the **project number** (e.g., `1`, `2`, etc.).

### Step 2: Create Phase Plan YAML

```powershell
# Create plans directory
New-Item -Path "plans" -ItemType Directory -Force

# Create your phase plan
New-Item -Path "plans\MULTI_INSTANCE_CLI_WEEK2.yaml" -ItemType File
```

Add your phases (see format above).

### Step 3: Dry Run (Test First)

```powershell
# See what would be created
pwsh scripts\Invoke-UetPhasePlanToGitHubProjectSync.ps1 `
    -ProjectNumber 1 `
    -ProjectOwner '@me' `
    -PlanPath 'plans\MULTI_INSTANCE_CLI_WEEK2.yaml' `
    -DryRun `
    -Verbose
```

### Step 4: Execute (Create Items)

```powershell
# Actually create the GitHub Project items
pwsh scripts\Invoke-UetPhasePlanToGitHubProjectSync.ps1 `
    -ProjectNumber 1 `
    -ProjectOwner '@me' `
    -PlanPath 'plans\MULTI_INSTANCE_CLI_WEEK2.yaml' `
    -RequireCleanGitStatus `
    -Verbose
```

### Step 5: Verify

```powershell
# View your project
gh project view 1 --owner @me

# Check the updated YAML
Get-Content plans\MULTI_INSTANCE_CLI_WEEK2.yaml
```

The `gh_item_id` fields should now be filled in!

---

## Example: Week 2 Plan Setup

### 1. Convert Week 2 Plan to YAML

```powershell
# Create Week 2 plan from WEEK2_PHASE_PLAN.md
$plan = @"
phases:
  - phase_id: "PH-W2D1"
    workstream_id: "ws-cluster-manager"
    title: "ClusterManager Core"
    objective: "Implement launch_cluster() API and basic routing"
    phase_type: "implementation"
    depends_on: []
    status: "not_started"
    gh_item_id: null
    estimate_hours: 6
    
  - phase_id: "PH-W2D2"
    workstream_id: "ws-cluster-manager"
    title: "Routing Strategies"
    objective: "Implement RoundRobin, LeastBusy, Sticky routers"
    phase_type: "implementation"
    depends_on: ["PH-W2D1"]
    status: "not_started"
    gh_item_id: null
    estimate_hours: 6
    
  - phase_id: "PH-W2D3"
    workstream_id: "ws-cluster-manager"
    title: "Auto-Restart & Circuit Breaker"
    objective: "Add health monitoring and failure recovery"
    phase_type: "implementation"
    depends_on: ["PH-W2D1"]
    status: "not_started"
    gh_item_id: null
    estimate_hours: 6
    
  - phase_id: "PH-W2D4"
    workstream_id: "ws-cluster-manager"
    title: "Metrics & Monitoring"
    objective: "Track performance metrics and export APIs"
    phase_type: "implementation"
    depends_on: ["PH-W2D1", "PH-W2D2", "PH-W2D3"]
    status: "not_started"
    gh_item_id: null
    estimate_hours: 6
    
  - phase_id: "PH-W2D5"
    workstream_id: "ws-cluster-manager"
    title: "Integration & Documentation"
    objective: "Complete tests, docs, and examples"
    phase_type: "implementation"
    depends_on: ["PH-W2D1", "PH-W2D2", "PH-W2D3", "PH-W2D4"]
    status: "not_started"
    gh_item_id: null
    estimate_hours: 6
"@

$plan | Set-Content -Path "plans\WEEK2_CLUSTER_MANAGER.yaml" -Encoding UTF8
```

### 2. Sync to GitHub

```powershell
# Dry run first
pwsh scripts\Invoke-UetPhasePlanToGitHubProjectSync.ps1 `
    -ProjectNumber 1 `
    -PlanPath 'plans\WEEK2_CLUSTER_MANAGER.yaml' `
    -DryRun

# Then execute
pwsh scripts\Invoke-UetPhasePlanToGitHubProjectSync.ps1 `
    -ProjectNumber 1 `
    -PlanPath 'plans\WEEK2_CLUSTER_MANAGER.yaml'
```

---

## Anti-Pattern Guards

The script validates:

✅ **Unique phase_id** - No duplicates allowed  
✅ **Required fields** - phase_id, workstream_id, title, objective must exist  
✅ **Valid statuses** - Only `not_started`, `in_progress`, `done`, `blocked`  
✅ **Clean git** - With `-RequireCleanGitStatus`, ensures no uncommitted changes  
✅ **YAML structure** - Must have top-level `phases` array

---

## Future Enhancements

### Status Sync (Coming Next)

Add a companion script to sync status changes back:

```powershell
# Update phase status in YAML
scripts\Update-UetPhaseStatus.ps1 `
    -PlanPath 'plans\WEEK2_CLUSTER_MANAGER.yaml' `
    -PhaseId 'PH-W2D1' `
    -Status 'in_progress'

# Sync to GitHub Project (updates board)
scripts\Sync-UetPhaseStatusToGitHub.ps1 `
    -PlanPath 'plans\WEEK2_CLUSTER_MANAGER.yaml' `
    -ProjectNumber 1
```

### Integration with Execution Patterns

```powershell
# Auto-create phases when starting work
scripts\Start-UetPhase.ps1 -PhaseId 'PH-W2D1'
# → Updates status to 'in_progress'
# → Syncs to GitHub
# → Checks dependencies
# → Creates work branch
```

---

## Troubleshooting

### "Required cmdlet 'ConvertFrom-Yaml' is not available"

**Solution**: Use PowerShell 7+, not Windows PowerShell 5.1

```powershell
# Check version
$PSVersionTable.PSVersion

# If < 7.0, install PowerShell 7
winget install Microsoft.PowerShell
```

### "gh project item-create failed"

**Solution**: Ensure gh CLI has project scope

```powershell
gh auth refresh -s project
gh auth status  # Look for 'project' in scopes
```

### "Phase plan file not found"

**Solution**: Use path relative to repo root

```powershell
# Good
-PlanPath 'plans\WEEK2.yaml'

# Bad (absolute path)
-PlanPath 'C:\Users\...\plans\WEEK2.yaml'
```

---

## Integration Example

```powershell
# 1. Create plan
$plan = Get-Content WEEK2_PHASE_PLAN.md
# ... convert to YAML ...
$yaml | Set-Content plans\WEEK2.yaml

# 2. Sync to GitHub
pwsh scripts\Invoke-UetPhasePlanToGitHubProjectSync.ps1 `
    -ProjectNumber 1 `
    -PlanPath 'plans\WEEK2.yaml'

# 3. Start work on Day 1
# (future) scripts\Start-UetPhase.ps1 -PhaseId 'PH-W2D1'

# 4. Track progress in GitHub Project web UI
# Items auto-created with dependencies shown
```

---

**Status**: Ready for use  
**Next**: Create Week 2 YAML and sync to GitHub Project
