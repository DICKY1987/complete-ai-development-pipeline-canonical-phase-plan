---
doc_id: DOC-PAT-EXAMPLE-018
---

# Example: Syncing a Phase Plan to GitHub

This example demonstrates the complete GitHub sync workflow.

## Prerequisites

1. **GitHub Personal Access Token** with permissions:
   - `repo` (for Issues)
   - `project` (for Projects v2)

2. **GitHub Project v2** created with custom fields:
   - Phase ID (Text)
   - Workstream (Text)
   - Status (Single-select: planned, active, blocked, done)
   - Risk (Single-select: low, medium, high)
   - Target date (Date)
   - doc_id (Text)

3. **Python dependencies installed**:
   ```bash
   pip install pyyaml requests jsonschema
   ```

## Step 1: Create/Update Phase Plan

Edit your phase plan to include `github_integration`:

```yaml
doc_id: "DOC-PHASE-EXAMPLE-001"
template_version: 3

phase_identity:
  phase_id: "PH-001"
  workstream_id: "ws-core"
  title: "Example Phase Plan"
  summary: "This is an example phase for GitHub sync"
  objective: "Demonstrate GitHub integration"
  status: "planned"

# ... other phase plan sections ...

github_integration:
  enabled: true

  repo:
    owner: "YOUR_GITHUB_USERNAME"
    name: "YOUR_REPO_NAME"
    default_branch: "main"

  issue:
    mode: "one-per-phase"
    number: null                  # Will be filled after first sync
    title_template: "[{phase_id}] {title}"
    body_template_path: null
    labels:
      - "phase-plan"
      - "splinter"
    assignees: []

  project:
    owner: "YOUR_GITHUB_USERNAME"
    project_number: 1             # Your project number
    item_id: null                 # Will be filled after first sync

    field_mappings:
      phase_id_field: "Phase ID"
      workstream_field: "Workstream"
      status_field: "Status"
      risk_field: "Risk"
      target_date_field: "Target date"
      doc_id_field: "doc_id"

  automation:
    allow_issue_create: true
    allow_issue_update: true
    allow_project_item_create: true
    allow_project_item_update: true
    sync_direction: "yaml->github"
    on_phase_status_change_update_project: true
    on_project_status_change_update_phase: false
```

## Step 2: Validate the Phase Plan

```bash
python scripts/validate_phase_plan.py \
  --repo-root . \
  --phase-file phases/example_phase.yaml
```

Expected output:
```json
{
  "ok": true,
  "checks": [
    {"id": "STEP_1_PATTERN_REGISTRY_AND_GH_SYNC", "status": "PASS"},
    {"id": "STEP_2_SPLINTER_PHASE_SCHEMA", "status": "PASS"},
    {"id": "STEP_3_GH_SYNC_SCHEMA", "status": "PASS"}
  ]
}
```

## Step 3: Dry Run

Preview what will be synced without making changes:

```bash
export GITHUB_TOKEN="your_personal_access_token"

python scripts/splinter_sync_phase_to_github.py \
  --phase-file phases/example_phase.yaml \
  --github-repo YOUR_USERNAME/YOUR_REPO \
  --dry-run
```

Expected output:
```
Loading phase plan: phases/example_phase.yaml
Phase: PH-001 - Example Phase Plan
  Workstream: ws-core
  Status: planned
  Risk: unspecified

[DRY RUN] Would perform the following actions:
  1. Ensure issue exists for PH-001
     Repository: YOUR_USERNAME/YOUR_REPO
     Mode: one-per-phase
  2. Ensure project item in Project #1
     Field mappings: ['phase_id_field', 'workstream_field', 'status_field', ...]
```

## Step 4: Actual Sync

```bash
python scripts/splinter_sync_phase_to_github.py \
  --phase-file phases/example_phase.yaml \
  --github-repo YOUR_USERNAME/YOUR_REPO
```

Expected output:
```
Loading phase plan: phases/example_phase.yaml
Phase: PH-001 - Example Phase Plan
  Workstream: ws-core
  Status: planned
  Risk: unspecified

1. Ensuring GitHub Issue...
   ✓ Issue #42

2. Ensuring Project Item...
   ✓ Project item: PVTI_lADOABCDEF...

✓ Sync complete
```

## Step 5: Verify in GitHub

### Check the Issue
1. Go to your repository → Issues
2. Find issue #42 with title "[PH-001] Example Phase Plan"
3. Verify labels: `phase-plan`, `splinter`, `workstream:ws-core`, `phase:PH-001`

### Check the Project
1. Go to your repository → Projects → Your Project
2. Find the item for issue #42
3. Verify custom fields are populated:
   - Phase ID: `PH-001`
   - Workstream: `ws-core`
   - Status: `planned`
   - doc_id: `DOC-PHASE-EXAMPLE-001`

## Step 6: Update and Re-Sync

Edit your phase plan (e.g., change status to "active"):

```yaml
phase_identity:
  status: "active"  # Changed from "planned"
```

Re-run sync:
```bash
python scripts/splinter_sync_phase_to_github.py \
  --phase-file phases/example_phase.yaml \
  --github-repo YOUR_USERNAME/YOUR_REPO
```

The Issue and Project item will be updated automatically.

## Automatic Sync via GitHub Actions

Once you push phase YAML files to your repository, the GitHub Action will automatically sync them:

```bash
git add phases/example_phase.yaml
git commit -m "Add example phase plan"
git push
```

The workflow `.github/workflows/splinter_phase_sync.yml` will:
1. Detect the changed phase file
2. Run validation
3. Sync to GitHub Issues and Projects

## Troubleshooting

### "GraphQL error: Could not resolve to a ProjectV2"
- Verify `project_number` is correct (check project URL)
- Ensure token has `project` scope
- Check if project is user-owned or org-owned

### "Field 'Status' not found in project"
- Verify field names match exactly (case-sensitive)
- Check `field_mappings` in your phase plan
- Ensure custom fields are created in the project

### "Option 'planned' not found for single-select field"
- Verify single-select options exist in the project
- Option names must match exactly (case-insensitive matching is applied)

## Advanced: Bidirectional Sync (Future)

To enable bidirectional sync (updates flow both ways):

```yaml
automation:
  sync_direction: "bidirectional"
  on_project_status_change_update_phase: true
```

**Note**: This requires additional webhook handling and conflict resolution logic (not yet implemented).
