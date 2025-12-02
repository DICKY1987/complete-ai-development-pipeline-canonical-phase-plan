# Workstream Sync - Quick Reference Card

## ONE-LINE COMMANDS

```powershell
# SYNC ALL WORKSTREAMS (NO STOP MODE)
python scripts/sync_workstreams_to_github.py

# PREVIEW ONLY (DRY RUN)
python scripts/sync_workstreams_to_github.py --dry-run

# CUSTOM BRANCH
python scripts/sync_workstreams_to_github.py --branch feature/my-sync
```

---

## WHAT IT DOES

1. ✅ Creates feature branch (`feature/ws-sync-YYYYMMDD-HHMMSS`)
2. ✅ Commits each workstream separately
3. ✅ Continues through ALL tasks (NO STOP MODE)
4. ✅ Pushes to remote (origin)
5. ✅ Generates summary report

---

## NO STOP MODE

**CRITICAL FEATURE**: Never stops on errors

✅ Processes ALL workstreams  
✅ Collects ALL errors  
✅ Tracks ALL successes  
✅ Always generates final report  

**Result**: Complete execution picture, not just first failure

---

## FILES

| Type | Location |
|------|----------|
| **Script** | `scripts/sync_workstreams_to_github.py` |
| **Template** | `templates/workstream_summary_report.md` |
| **Report** | `reports/workstream_sync_*.md` (generated) |
| **Guide** | `docs/WORKSTREAM_SYNC_GUIDE.md` |

---

## AFTER SYNC

```powershell
# 1. Review report
code reports/workstream_sync_*.md

# 2. Check commits
git log --oneline feature/ws-sync-*

# 3. Create PR
gh pr create --base main --head feature/ws-sync-* --title "Sync workstreams"
```

---

## TEMPLATE VARIABLES

When using `templates/workstream_summary_report.md`:

- `${TIMESTAMP}` → Report time
- `${FEATURE_BRANCH}` → Branch name  
- `${TOTAL_WORKSTREAMS}` → Total count
- `${SUCCESS_COUNT}` → Successes
- `${FAILED_COUNT}` → Failures
- `${COMMITS_CREATED}` → Git commits
- `${ERROR_LOG}` → Error details

---

## CONFIGURATION

In `MASTER_SPLINTER_Phase_Plan_Template.yml`:

```yaml
extensions:
  custom_fields:
    workstream_sync:
      enabled: true
      no_stop_mode: true
    execution_resilience:
      continue_on_error: true
```

---

## DOCUMENTATION

📖 **Full Guide**: `docs/WORKSTREAM_SYNC_GUIDE.md`  
📋 **Completion Summary**: `WORKSTREAM_SYNC_COMPLETION.md`  
🎯 **MASTER_SPLINTER Docs**: `C:\Users\richg\Downloads\PRMNT DOCS\`

---

**READY TO USE** - All 54 workstreams ready for sync
