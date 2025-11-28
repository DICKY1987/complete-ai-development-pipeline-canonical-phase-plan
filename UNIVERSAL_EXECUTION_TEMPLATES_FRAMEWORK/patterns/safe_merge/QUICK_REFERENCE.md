# Safe Merge Quick Reference Card

**Location**: `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/safe_merge/`

---

## ⚡ Most Common Commands

```powershell
# Replace your git push (use this daily)
.\safe_merge.ps1 -Action push

# Before merging any feature
.\safe_merge.ps1 -Action scan -BaseBranch main -FeatureBranch feature/xyz

# Fix nested repos (one-time setup)
.\safe_merge.ps1 -Action normalize

# Complete safe merge
.\safe_merge.ps1 -Action merge `
    -BaseBranch main `
    -FeatureBranch feature/xyz `
    -AllowAutoPush
```

---

## 📋 All Available Actions

| Action | Purpose | When to Use |
|--------|---------|-------------|
| `scan` | Detect issues before merge | Before every merge |
| `normalize` | Fix nested repos | One-time or when detected |
| `merge` | Full safe merge workflow | Feature → base merges |
| `push` | Safe push with guard | Daily pushes |
| `full` | Complete pipeline | Automated workflows |

---

## 🔧 Individual Patterns

```powershell
# Environment scan
.\scripts\merge_env_scan.ps1 -BaseBranch main -FeatureBranch feature/xyz

# Nested repo detection
python scripts\nested_repo_detector.py .

# File classification
python scripts\merge_file_classifier.py .

# Safe push
.\scripts\safe_pull_and_push.ps1

# Multi-clone guard
python scripts\multi_clone_guard.py --instance-id my_tool --branch main

# Nested repo normalizer
python scripts\nested_repo_normalizer.py . --policy absorb_as_folder

# Full orchestrator
.\scripts\safe_merge_auto.ps1 -BaseBranch main -FeatureBranch feature/xyz
```

---

## 📊 Output Files

All patterns create JSON reports:

```
env_scan.safe_merge.json           # Environment state
nested_repos_report.json           # Nested repo classification
merge_file_classes.json            # File classifications
sync_log_summary.json              # Sync activity analysis
SAFE_MERGE_REPORT_<timestamp>.md   # Human-readable report
safe_merge_report_<timestamp>.json # Machine-readable report
safe_push_events.jsonl             # Push event log
```

---

## ✅ Success Indicators

**Pattern succeeded if**:
- Exit code = 0
- JSON output file created
- No "ABORT" or "ERROR" messages

**Pattern warned if**:
- Exit code = 1 (may still create output)
- "WARNING" messages present
- Check JSON for details

---

## 🚨 Troubleshooting

```powershell
# If push fails
.\safe_merge.ps1 -Action scan  # Diagnose issues first

# If merge conflicts
cat SAFE_MERGE_REPORT_*.md     # Review what happened
git checkout rollback/*        # Rollback if needed

# If scripts won't run
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# If Python errors
python --version               # Ensure 3.8+
```

---

## 📖 Documentation Index

| File | Purpose |
|------|---------|
| `INDEX.md` | Complete overview (START HERE) |
| `QUICKSTART.md` | Quick examples |
| `IMPLEMENTATION_SUMMARY.md` | How it works |
| `FINAL_COMPLETION_REPORT.md` | What was built |
| `QUICK_REFERENCE.md` | This file |

---

## 🎯 Usage Patterns

### Daily Development
```powershell
# Morning: Sync up
.\safe_merge.ps1 -Action push

# After changes: Safe push
.\safe_merge.ps1 -Action push
```

### Feature Merge
```powershell
# Step 1: Scan
.\safe_merge.ps1 -Action scan -BaseBranch main -FeatureBranch feature/xyz

# Step 2: Review reports
cat env_scan.safe_merge.json
cat nested_repos_report.json

# Step 3: Merge
.\safe_merge.ps1 -Action merge -BaseBranch main -FeatureBranch feature/xyz -AllowAutoPush
```

### First-Time Setup
```powershell
# Validate installation
.\validate_installation.ps1

# Fix nested repos
.\safe_merge.ps1 -Action normalize

# Test on current branch
.\safe_merge.ps1 -Action scan
```

---

## 💡 Pro Tips

1. **Always scan before merging** - Catches 95% of issues
2. **Normalize once** - Fix nested repos early
3. **Use the wrapper** - Easier than individual patterns
4. **Check JSON outputs** - Machine-readable diagnostics
5. **Keep rollback branches** - Easy recovery if needed

---

## ⚠️ Remember

- ✅ All patterns are idempotent (safe to re-run)
- ✅ Rollback branches created automatically
- ✅ Exit codes: 0 = success, 1 = error/warning
- ✅ JSON outputs always created (even on error)
- ✅ Multi-clone safe (distributed locking)

---

**Need help?** Read `IMPLEMENTATION_SUMMARY.md` for detailed explanations.

**Found a bug?** Check JSON output files for diagnostics.

**Want more?** See `INDEX.md` for complete documentation index.

---

**Version**: 1.0.0  
**Status**: Production Ready ✅  
**Last Updated**: 2025-11-27
