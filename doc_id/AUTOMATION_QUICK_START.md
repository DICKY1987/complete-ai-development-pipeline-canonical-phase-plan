---
doc_id: DOC-GUIDE-DOC-ID-AUTOMATION-QUICK-START-008
---

# DOC_ID Automation - Quick Start Guide

**Last Updated**: 2025-12-04
**Status**: ✅ READY TO USE

---

## 🚀 30-Second Quick Start

```bash
# 1. Run full automation suite (dry-run)
.\doc_id\automation_runner.ps1 -Task all -DryRun

# 2. Check what needs fixing
python doc_id/cleanup_invalid_doc_ids.py scan
python doc_id/sync_registries.py check

# 3. Fix registry drift
python doc_id/sync_registries.py sync
```

---

## 📋 Daily Workflow

### Option A: PowerShell Orchestrator (Recommended)
```powershell
# Run everything at once
.\doc_id\automation_runner.ps1 -Task all
```

### Option B: Individual Scripts
```bash
# 1. Scan repository
python doc_id/doc_id_scanner.py scan

# 2. Generate daily report
python doc_id/scheduled_report_generator.py daily

# 3. Check for issues
python doc_id/cleanup_invalid_doc_ids.py scan

# 4. Sync registries
python doc_id/sync_registries.py check
```

---

## 🔧 Common Tasks

### Detect Invalid Doc IDs
```bash
# Scan and save report
python doc_id/cleanup_invalid_doc_ids.py scan

# View report
cat doc_id/DOC_ID_reports/cleanup_report.json
```

**Expected output**:
- Malformed: ~1,828 (don't match pattern)
- Duplicates: ~1,761 (appear in multiple files)
- Orphaned: 0

---

### Sync Registry & Inventory

**Check gap**:
```bash
python doc_id/sync_registries.py check
```

**Fix gap** (dry-run first):
```bash
python doc_id/sync_registries.py sync --dry-run
python doc_id/sync_registries.py sync
```

**Current gap**: ~1,383 doc_ids in inventory but not in registry

---

### Generate Reports

**Daily report**:
```bash
python doc_id/scheduled_report_generator.py daily
```

**Weekly report** (needs 7 days of daily reports):
```bash
python doc_id/scheduled_report_generator.py weekly
```

Reports saved to: `doc_id/DOC_ID_reports/`

---

### Validate Before Commit

**Manual check**:
```bash
python doc_id/pre_commit_hook.py
```

**Install as Git hook**:
```bash
# Copy hook
cp doc_id/pre_commit_hook.py .git/hooks/pre-commit

# Make executable (Linux/Mac)
chmod +x .git/hooks/pre-commit
```

**Bypass hook** (not recommended):
```bash
git commit --no-verify
```

---

## 📊 Current Status

Run this to see current state:
```bash
python doc_id/doc_id_scanner.py stats
```

**Expected output**:
```
Total eligible files:    2,373
Files with doc_id:       2,297 (96.8%)
Files without doc_id:    72 (3.2%)
Files with invalid ID:   4
```

---

## 🎯 Key Actions Needed

### 1. Sync Registry (High Priority)
**Why**: 1,383 doc_ids exist in files but not in registry

```bash
python doc_id/sync_registries.py sync
```

### 2. Fix Malformed IDs (High Priority)
**Why**: 1,828 doc_ids don't match canonical pattern

```bash
# First, review what's malformed
python doc_id/cleanup_invalid_doc_ids.py scan

# Then fix (with backup)
python doc_id/cleanup_invalid_doc_ids.py fix --backup
```

**Note**: Cleanup script currently only detects. Fix logic needs enhancement for auto-repair.

### 3. Audit Duplicates (Medium Priority)
**Why**: 1,761 duplicate doc_ids found

```bash
# View duplicates in report
python doc_id/cleanup_invalid_doc_ids.py scan
cat doc_id/DOC_ID_reports/cleanup_report.json | grep -A 5 '"duplicates"'
```

**Manual review required** to determine:
- Intentional cross-references (keep)
- Accidental duplicates (renumber)

### 4. Enable CI/CD (Medium Priority)
**Why**: Automate validation on every push/PR

```bash
# Workflow already created at:
.github/workflows/doc_id_validation.yml

# Just commit and push to enable
git add .github/workflows/doc_id_validation.yml
git commit -m "Enable DOC_ID validation workflow"
git push
```

---

## 🔍 Troubleshooting

### "PyYAML not installed"
```bash
pip install pyyaml
```

### "Permission denied" on pre-commit hook
```bash
# Windows: No action needed
# Linux/Mac: Make executable
chmod +x .git/hooks/pre-commit
```

### Scripts run slow (>2 minutes)
**Normal**: 2,373 files take ~60 seconds to scan

**Speedup options**:
- Exclude large directories in script (edit EXCLUDE_PATTERNS)
- Run on subset: `--limit 100` where supported

### Coverage shows 100% but should be 96.8%
**Cause**: Scanner reads from cached `docs_inventory.jsonl`

**Fix**: Delete inventory and re-scan
```bash
rm docs_inventory.jsonl
python doc_id/doc_id_scanner.py scan
```

---

## 📅 Recommended Schedule

### Daily
- Run scanner: `doc_id_scanner.py scan`
- Generate report: `scheduled_report_generator.py daily`
- Check for issues: `cleanup_invalid_doc_ids.py scan`

### Weekly
- Generate weekly report: `scheduled_report_generator.py weekly`
- Review cleanup reports
- Sync registries: `sync_registries.py sync`

### Monthly
- Audit duplicates
- Review malformed IDs
- Update documentation

---

## 🎛️ Configuration

### Modify Exclusion Patterns

**Edit in each script**:
```python
EXCLUDE_DIRS = {".git", "__pycache__", ".venv", ...}
ELIGIBLE_EXTENSIONS = {".py", ".md", ".yaml", ...}
```

### Change Coverage Baseline

**In CI workflow** (`.github/workflows/doc_id_validation.yml`):
```yaml
python doc_id/validate_doc_id_coverage.py --baseline 0.97  # Increase to 97%
```

### Customize Report Output

**All scripts support**:
- `--report <path>` - Custom report path
- `--dry-run` - Preview changes
- `--help` - Show all options

---

## 📚 Documentation

- **Full guide**: `doc_id/AUTOMATION_SUMMARY.md`
- **Test results**: `doc_id/AUTOMATION_TEST_RESULTS.md`
- **Quick reference**: `doc_id/QUICK_REFERENCE.md`
- **System status**: `doc_id/DOC_ID_SYSTEM_STATUS.md`

---

## 🆘 Getting Help

### Check script help
```bash
python doc_id/cleanup_invalid_doc_ids.py --help
python doc_id/sync_registries.py --help
python doc_id/scheduled_report_generator.py --help
```

### View latest reports
```bash
ls doc_id/DOC_ID_reports/
cat doc_id/DOC_ID_reports/daily_report_*.json
```

### Debug mode
```bash
# Add -v or --verbose if supported
python doc_id/doc_id_scanner.py scan -v
```

---

**Ready to automate?** Start with: `.\doc_id\automation_runner.ps1 -Task all -DryRun`
