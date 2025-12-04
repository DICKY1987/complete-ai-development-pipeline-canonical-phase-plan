# Workstream Sync to GitHub Project Manager

Complete automation for syncing workstreams to GitHub with no-stop execution.

## Quick Start

```powershell
# Sync all workstreams to GitHub PM
python scripts/sync_workstreams_to_github.py

# Preview what will be synced (no changes)
python scripts/sync_workstreams_to_github.py --dry-run

# Use custom branch name
python scripts/sync_workstreams_to_github.py --branch feature/my-sync
```

## What It Does

### 1. Feature Branch Creation
- Auto-generates branch name: `feature/ws-sync-YYYYMMDD-HHMMSS`
- Creates new branch from current HEAD
- Switches to feature branch for all operations

### 2. Workstream Processing (NO STOP MODE)
- Processes **ALL** workstreams in `workstreams/ws-*.json`
- Creates **separate commit** for each workstream
- **Continues through errors** - never stops mid-execution
- Collects all successes and failures

### 3. Git Operations
Each workstream gets its own commit with metadata:
```
sync: ws-01-hardcoded-path-index

Workstream: ws-01-hardcoded-path-index
Doc ID: DOC-CONFIG-WS-01-HARDCODED-PATH-INDEX-141
Tool: codex
Gate: 1
```

### 4. Remote Push
- Pushes feature branch to `origin`
- Sets upstream tracking automatically

### 5. Summary Report
- Generated at: `reports/workstream_sync_YYYYMMDD_HHMMSS.md`
- Uses template: `templates/workstream_summary_report.md`
- Includes: successes, errors, timeline, recommendations

## Critical Feature: NO STOP MODE

### Why It Matters
Traditional batch processing stops on first error. This wastes time and hides downstream issues.

**NO STOP MODE** solves this by:
- ✅ Processing **every** workstream regardless of individual failures
- ✅ Collecting **all** errors for comprehensive analysis
- ✅ Generating **complete** reports showing full execution picture
- ✅ Providing **actionable** data for bulk fixes

### Implementation Pattern
```python
errors = []
successes = []

for workstream in all_workstreams:
    try:
        process_workstream(workstream)
        successes.append(workstream)
    except Exception as e:
        errors.append({"workstream": workstream, "error": str(e)})
        # CRITICAL: Continue to next workstream, don't break

# Always generate final report
generate_summary_report(successes, errors)
```

## Files Created

### Scripts
- `scripts/sync_workstreams_to_github.py` - Main sync engine

### Templates
- `templates/workstream_summary_report.md` - Report template with variables

### Reports (Generated)
- `reports/workstream_sync_YYYYMMDD_HHMMSS.md` - Execution summary

## Configuration

### In Phase Plan Template
Location: `MASTER_SPLINTER_Phase_Plan_Template.yml`

```yaml
extensions:
  custom_fields:
    workstream_sync:
      enabled: true
      auto_commit: true
      feature_branch_pattern: "feature/ws-sync-${timestamp}"
      github_project_integration: true
      no_stop_mode: true
      summary_report_template: "templates/workstream_summary_report.md"
      sync_script: "scripts/sync_workstreams_to_github.py"

    execution_resilience:
      continue_on_error: true          # Never stop on errors
      error_collection_mode: true      # Collect all errors
      final_report_on_completion: true # Always generate report
```

## Report Template Variables

Template: `templates/workstream_summary_report.md`

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `${TIMESTAMP}` | Report generation time | `2024-12-02T18:57:00Z` |
| `${FEATURE_BRANCH}` | Git branch used | `feature/ws-sync-20241202-185700` |
| `${TOTAL_WORKSTREAMS}` | Total workstream count | `54` |
| `${PROCESSED_COUNT}` | Number processed | `54` |
| `${SUCCESS_COUNT}` | Successful operations | `52` |
| `${FAILED_COUNT}` | Failed operations | `2` |
| `${COMMITS_CREATED}` | Git commits made | `52` |
| `${SYNC_STATUS}` | Overall status | `✅ Complete` or `⚠️ Partial` |
| `${ERROR_LOG}` | Detailed error list | Error details with context |
| `${SUCCESS_LIST}` | List of successful items | Success details |
| `${RECOMMENDATIONS}` | Next steps | Action items |

## Usage Examples

### Standard Sync
```powershell
cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"
python scripts/sync_workstreams_to_github.py
```

### Dry Run (Preview Only)
```powershell
python scripts/sync_workstreams_to_github.py --dry-run
```

### Custom Branch Name
```powershell
python scripts/sync_workstreams_to_github.py --branch feature/sprint-23-workstreams
```

## Post-Sync Workflow

### 1. Review Summary Report
```powershell
# Open the generated report
code reports/workstream_sync_*.md
```

### 2. Check Git Status
```powershell
# View commits on feature branch
git log --oneline origin/main..HEAD

# See what changed
git diff origin/main..HEAD --stat
```

### 3. Create Pull Request
```powershell
# Using GitHub CLI
gh pr create --base main --head feature/ws-sync-* --title "Sync workstreams to GitHub PM" --body "Automated sync of all workstreams"

# Or manually on GitHub
# https://github.com/your-org/your-repo/compare/main...feature/ws-sync-*
```

### 4. Verify GitHub Project
- Check GitHub Projects dashboard
- Verify workstream items are created/updated
- Confirm doc_id linking is correct

## Error Handling

### Common Errors and Solutions

**Error**: `Branch already exists`
- **Solution**: Use `--branch` flag with different name or delete existing branch

**Error**: `Nothing to commit`
- **Solution**: Normal - workstream hasn't changed since last sync

**Error**: `Push failed`
- **Solution**: Check remote permissions, ensure origin is configured

**Error**: `Invalid JSON in workstream file`
- **Solution**: Fix JSON syntax in the specific workstream file

### Error Collection
All errors are:
1. Logged to stderr with context
2. Collected in errors list
3. Included in final summary report
4. **Never stop execution** - other workstreams still process

## Advanced Usage

### Filtering Workstreams
Currently processes all `workstreams/ws-*.json` files. To filter:

```python
# Modify in sync script
ws_files = sorted(WORKSTREAMS_DIR.glob("ws-next-*.json"))  # Only next workstreams
ws_files = sorted(WORKSTREAMS_DIR.glob("ws-[0-2]*.json"))  # Only ws-01 through ws-29
```

### Custom Commit Messages
Edit `commit_workstream()` method in sync script:

```python
commit_msg = f"feat(workstreams): sync {ws_id}\n\n"
commit_msg += f"- Workstream: {ws_data.get('id')}\n"
commit_msg += f"- Category: {ws_data.get('category', 'N/A')}\n"
# Add your custom fields
```

## Documentation References

- **Template**: `MASTER_SPLINTER_Phase_Plan_Template.yml`
- **Guide**: `MASTER_SPLINTER_Phase_Plan_Template_GUIDE.md`
- **Quick Reference**: `MASTER_SPLINTER_paste_dir.md`

## Execution Principles

### Decision Elimination
- Pre-configured workflow: no runtime decisions needed
- Template-driven: consistent execution every time
- Ground truth: success = files exist, commits made, tests pass

### Resilience First
- Continue through errors
- Comprehensive error collection
- Always generate final report
- No silent failures

### Verification Over Trust
- Check git status before and after
- Verify commits are created
- Confirm push succeeded
- Validate report generation

## Next Steps

After running sync:

1. ✅ Review `reports/workstream_sync_*.md` for execution summary
2. ✅ Check feature branch commits: `git log --oneline`
3. ✅ Create PR for review
4. ✅ Merge to main after approval
5. ✅ Verify GitHub Project items are synced

---

**Script**: `scripts/sync_workstreams_to_github.py`
**Template**: `templates/workstream_summary_report.md`
**Mode**: NO STOP - Continues through all tasks
