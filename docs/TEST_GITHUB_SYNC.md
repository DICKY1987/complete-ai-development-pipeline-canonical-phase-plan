# Test Example: GitHub Project Sync

**Purpose**: Validate the UET Phase Plan → GitHub Project sync pattern with a minimal 2-phase example.

---

## Test Plan YAML

File: `plans/TEST_SYNC.yaml`

Contains 2 simple test phases to verify:
- ✅ YAML → GitHub item creation
- ✅ `gh_item_id` written back to YAML
- ✅ Status sync (YAML → GitHub)
- ✅ Validation and error handling

---

## Step-by-Step Test (Option C)

### Prerequisites Check

```powershell
# 1. Verify GitHub CLI installed
gh --version

# 2. Verify authenticated
gh auth status

# 3. Verify project scope
gh auth status | Select-String "project"

# If no project scope:
gh auth refresh -s project

# 4. Verify PowerShell 7+
$PSVersionTable.PSVersion
# Should be 7.x or higher
```

---

### Test 1: Dry Run (See What Would Happen)

```powershell
# Dry run - no actual changes
pwsh scripts/Invoke-UetPhasePlanToGitHubProjectSync.ps1 `
    -ProjectNumber 1 `
    -ProjectOwner '@me' `
    -PlanPath 'plans/TEST_SYNC.yaml' `
    -DryRun `
    -Verbose
```

**Expected Output**:
```
[DRY-RUN] Would create GitHub project draft item for phase 'PH-TEST-01':
          Title: [PH-TEST-01] Test Phase 1 - Setup
          Body :
          Phase ID: PH-TEST-01
          Workstream ID: ws-github-sync-test
          ...

[DRY-RUN] Would create GitHub project draft item for phase 'PH-TEST-02':
          Title: [PH-TEST-02] Test Phase 2 - Validation
          ...

Dry-run complete. No changes written to 'plans/TEST_SYNC.yaml'.
```

---

### Test 2: Create GitHub Items

**First, create a test project** (if you don't have one):

```powershell
# Create project
gh project create --owner @me --title "UET Sync Test"

# List to get number
gh project list --owner @me
# Note the number (e.g., 1, 2, 3...)
```

**Now sync the phases**:

```powershell
# Replace with your project number
$projectNum = 1

# Execute sync
pwsh scripts/Invoke-UetPhasePlanToGitHubProjectSync.ps1 `
    -ProjectNumber $projectNum `
    -ProjectOwner '@me' `
    -PlanPath 'plans/TEST_SYNC.yaml' `
    -Verbose
```

**Expected Output**:
```
2 phase(s) will have GitHub Project items created.
Phase 'PH-TEST-01' mapped to GitHub item id 'PVTI_lADO...'
Phase 'PH-TEST-02' mapped to GitHub item id 'PVTI_lADO...'
Sync complete. Updated plan written to 'plans/TEST_SYNC.yaml'.
Each phase now has a gh_item_id that can be used for future status syncs.
```

---

### Test 3: Verify GitHub Items Created

```powershell
# View project in web browser
gh project view $projectNum --owner @me --web

# Or view in terminal
gh project view $projectNum --owner @me
```

**You should see**:
- ✅ Two items in the project
- ✅ Titles: `[PH-TEST-01] Test Phase 1 - Setup` and `[PH-TEST-02] Test Phase 2 - Validation`
- ✅ Bodies contain phase details

---

### Test 4: Verify YAML Updated

```powershell
# Check the updated YAML
Get-Content plans/TEST_SYNC.yaml
```

**Look for `gh_item_id` filled in**:
```yaml
phases:
  - phase_id: "PH-TEST-01"
    ...
    gh_item_id: "PVTI_lADOABC123..."  # ← Should be filled in
    
  - phase_id: "PH-TEST-02"
    ...
    gh_item_id: "PVTI_lADODEF456..."  # ← Should be filled in
```

---

### Test 5: Get GitHub Project Field IDs

```powershell
# Discover field IDs for status sync
pwsh scripts/Get-GitHubProjectFieldIds.ps1 `
    -ProjectNumber $projectNum `
    -Owner '@me'
```

**Expected Output**:
```
✓ Project ID: PVT_kwDOABC123
  Title: UET Sync Test

✓ Status Field ID: PVTSSF_lADOABC123
  Options:
    - Todo: 47fc9ee4
    - In Progress: f75ad846
    - Done: 98ec6ea7

======================================================================
COPY AND PASTE THESE ENVIRONMENT VARIABLES:
======================================================================

# PowerShell
$env:PROJECT_ID = 'PVT_kwDOABC123'
$env:STATUS_FIELD_ID = 'PVTSSF_lADOABC123'
$env:STATUS_TODO_ID = '47fc9ee4'
$env:STATUS_IN_PROGRESS_ID = 'f75ad846'
$env:STATUS_DONE_ID = '98ec6ea7'
```

**Copy those environment variables** and run them in your PowerShell session.

---

### Test 6: Update Phase Status (YAML only)

```powershell
# Update status in YAML
pwsh scripts/Update-UetPhaseStatus.ps1 `
    -PlanPath 'plans/TEST_SYNC.yaml' `
    -PhaseId 'PH-TEST-01' `
    -Status 'in_progress'
```

**Expected Output**:
```
Updating phase 'PH-TEST-01': 'not_started' → 'in_progress'
✓ Phase status updated in YAML
✓ Complete!
```

**Verify**:
```powershell
Get-Content plans/TEST_SYNC.yaml | Select-String -Pattern "PH-TEST-01" -Context 0,5
```

Should show `status: "in_progress"`.

---

### Test 7: Sync Status to GitHub (Dry Run First)

```powershell
# Dry run status sync
pwsh scripts/Sync-UetPhaseStatusToGitHub.ps1 `
    -PlanPath 'plans/TEST_SYNC.yaml' `
    -PhaseId 'PH-TEST-01' `
    -DryRun
```

**Expected Output**:
```
[DRY-RUN] Would update phase 'PH-TEST-01':
          Item ID: PVTI_lADO...
          Status: in_progress → Option ID: f75ad846

[DRY-RUN] No changes were made to GitHub Project
```

---

### Test 8: Actually Sync Status to GitHub

```powershell
# Actually sync (requires env vars from Test 5)
pwsh scripts/Sync-UetPhaseStatusToGitHub.ps1 `
    -PlanPath 'plans/TEST_SYNC.yaml' `
    -PhaseId 'PH-TEST-01'
```

**Expected Output**:
```
Syncing 1 phase(s) to GitHub Project...
✓ Updated phase 'PH-TEST-01' to 'in_progress'

Sync complete:
  Updated: 1
  Skipped: 0
  Failed:  0
```

**Verify in GitHub**:
```powershell
gh project view $projectNum --owner @me --web
```

The first item should now show **"In Progress"** status!

---

### Test 9: Full Workflow (Update + Sync in One Command)

```powershell
# Update YAML and sync to GitHub in one command
pwsh scripts/Update-UetPhaseStatus.ps1 `
    -PlanPath 'plans/TEST_SYNC.yaml' `
    -PhaseId 'PH-TEST-01' `
    -Status 'done' `
    -SyncToGitHub
```

**Expected Output**:
```
Updating phase 'PH-TEST-01': 'in_progress' → 'done'
✓ Phase status updated in YAML

Syncing status to GitHub Project...
✓ Updated phase 'PH-TEST-01' to 'done'

✓ Complete!
```

**Verify**: Item should now show **"Done"** in GitHub Project!

---

## Success Criteria

After completing all tests, you should have:

✅ **Test 1-2**: Created 2 GitHub Project items from YAML  
✅ **Test 3-4**: Verified items in GitHub and `gh_item_id` in YAML  
✅ **Test 5**: Obtained GitHub field/option IDs  
✅ **Test 6**: Updated phase status in YAML  
✅ **Test 7-8**: Synced status to GitHub Project  
✅ **Test 9**: Full workflow (update + sync)

---

## Troubleshooting

### "Required cmdlet 'ConvertFrom-Yaml' is not available"
→ Use PowerShell 7+: `winget install Microsoft.PowerShell`

### "gh project item-create failed"
→ Ensure project scope: `gh auth refresh -s project`

### "PROJECT_ID not set"
→ Run Test 5 and set environment variables

### "Phase has no gh_item_id"
→ Run Test 2 first to create GitHub items

---

## Cleanup (Optional)

```powershell
# Delete test project
gh project delete $projectNum --owner @me

# Remove test plan
Remove-Item plans/TEST_SYNC.yaml
```

---

**Status**: Ready to test!  
**Next**: Once validated, proceed to Option A (Week 2 setup)
