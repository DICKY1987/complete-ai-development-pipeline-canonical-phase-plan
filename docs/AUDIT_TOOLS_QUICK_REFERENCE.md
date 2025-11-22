# Codebase Audit Tools - Quick Reference

This repository includes comprehensive tools for auditing, identifying, and safely removing deprecated, obsolete, and duplicative files.

## Tools Overview

### 1. Codebase Auditor (`tools/codebase_auditor.py`)
Systematically scans the repository to identify problematic files.

**Run full audit:**
```bash
python tools/codebase_auditor.py
```

**Output:**
- `codebase_audit.json` - Machine-readable results
- `CODEBASE_AUDIT_REPORT.md` - Human-readable report

**Filter by category:**
```bash
python tools/codebase_auditor.py --category deprecated
python tools/codebase_auditor.py --category temporary
python tools/codebase_auditor.py --category duplicative
```

**JSON output only:**
```bash
python tools/codebase_auditor.py --json
```

### 2. Safe Archival Script (`scripts/archive_audited_files.py`)
Safely archives files with rollback capability.

**Dry run (preview):**
```bash
python scripts/archive_audited_files.py --dry-run
python scripts/archive_audited_files.py --dry-run --category temporary
```

**Archive temporary files:**
```bash
python scripts/archive_audited_files.py --category temporary
```

**Archive large directories:**
```bash
python scripts/archive_audited_files.py --category archive_candidates
```

**Rollback if needed:**
```bash
python scripts/archive_audited_files.py --rollback docs/archive/audit-2025-11-22/
```

### 3. Deprecated Usage Checker (`scripts/check_deprecated_usage.py`)
Scans for old import patterns.

```bash
python scripts/check_deprecated_usage.py
python scripts/check_deprecated_usage.py --strict  # Exit 1 if found
python scripts/check_deprecated_usage.py --json
```

## Categories Detected

| Category | Description | Count | Priority |
|----------|-------------|-------|----------|
| **Archive Candidates** | Large dirs (PROTOTYPE, BACKUP, etc.) | 8 dirs (4.5 MB) | Medium |
| **Temporary Files** | *.bak, __tmp_*, *_backup_* | 2 files | High |
| **Duplicates** | Same filename in different locations | 37 files | Low |
| **Outdated Docs** | References to src.pipeline.* | 27 files | Medium |
| **Obsolete Files** | No import references | 41 files | Low (review) |

## Quick Start Workflow

### Step 1: Run Audit
```bash
python tools/codebase_auditor.py
```

### Step 2: Review Reports
1. Open `CODEBASE_AUDIT_REPORT.md` for findings
2. Open `CODEBASE_AUDIT_RECOMMENDATIONS.md` for action plan

### Step 3: Safe Cleanup (Priority 1)
```bash
# Dry run first
python scripts/archive_audited_files.py --dry-run --category temporary

# If looks good, execute
python scripts/archive_audited_files.py --category temporary

# Verify nothing broke
python -m pytest tests/test_codebase_auditor.py -v
```

### Step 4: Review Archive Candidates
```bash
# Check what would be archived
python scripts/archive_audited_files.py --dry-run --category archive_candidates

# Review each directory individually before archiving
```

### Step 5: Update Outdated Documentation
```bash
# Check for deprecated imports in docs
python scripts/check_deprecated_usage.py

# Use automated migration tool
python scripts/auto_migrate_imports.py --docs-only
```

## Safety Features

All tools include:
- ✅ **Dry-run mode** - Preview changes before execution
- ✅ **Archive, not delete** - Files moved to `docs/archive/` first
- ✅ **Rollback capability** - Easy restoration if needed
- ✅ **Manifest generation** - Tracking of what was archived
- ✅ **Metadata preservation** - Why files were archived

## Validation Steps

After any archival operation:

```bash
# 1. Run tests
python -m pytest tests/test_codebase_auditor.py -v

# 2. Check for broken imports
python scripts/check_deprecated_usage.py --strict

# 3. Verify builds
pwsh ./scripts/test.ps1

# 4. Check git status
git status
```

## Archive Structure

```
docs/archive/
├── audit-2025-11-22/           # Current audit
│   ├── prototypes/             # AGENTIC_DEV_PROTOTYPE
│   ├── analysis/               # PROCESS_DEEP_DIVE_OPTOMIZE
│   ├── frameworks/             # UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK
│   ├── temp-files/             # Temporary files
│   ├── backups/                # Migration backups
│   ├── MANIFEST.md             # What was archived
│   └── */ARCHIVE_NOTE.md       # Why archived
└── phase-h-legacy/             # Previous archives
    └── ...
```

## Common Use Cases

### Use Case 1: Clean Up Temporary Files
```bash
# Find temporary files
python tools/codebase_auditor.py --category temporary --json

# Archive them
python scripts/archive_audited_files.py --category temporary
```

### Use Case 2: Review Duplicate Implementations
```bash
# Generate report
python tools/codebase_auditor.py

# Review duplicates section in CODEBASE_AUDIT_REPORT.md
# Manually consolidate or document purpose
```

### Use Case 3: Archive Old Prototypes
```bash
# Review what will be archived
python scripts/archive_audited_files.py --dry-run --category archive_candidates

# Archive specific directory
# (Currently archives all in category - enhance script for individual selection)
```

### Use Case 4: Update Documentation
```bash
# Find outdated docs
python tools/codebase_auditor.py --category outdated_docs

# Review CODEBASE_AUDIT_REPORT.md
# Manually update or use auto_migrate_imports.py
```

## Troubleshooting

### "File not found" during archival
The file was already removed or moved. Re-run audit to get current state:
```bash
python tools/codebase_auditor.py
```

### Want to undo archival
Use rollback feature:
```bash
python scripts/archive_audited_files.py --rollback docs/archive/audit-2025-11-22/
```

### Tests fail after archival
Rollback changes and investigate:
```bash
python scripts/archive_audited_files.py --rollback docs/archive/audit-2025-11-22/
python -m pytest tests/ -v --tb=short
```

## Integration with CI/CD

The audit can be integrated into CI pipelines:

```yaml
# .github/workflows/audit.yml
- name: Run codebase audit
  run: |
    python tools/codebase_auditor.py --json > audit.json
    # Fail if temporary files found
    if [ $(jq '.summary.temporary_files' audit.json) -gt 0 ]; then
      echo "Temporary files found - cleanup needed"
      exit 1
    fi
```

## Advanced Usage

### Custom Audit Criteria
Modify `tools/codebase_auditor.py`:
- Add patterns to `TEMP_PATTERNS`
- Add directories to `POTENTIAL_ARCHIVE_DIRS`
- Customize `OUTDATED_DOC_PATTERNS`

### Automated Cleanup
Create scheduled task:
```bash
# Weekly audit
0 0 * * 0 cd /path/to/repo && python tools/codebase_auditor.py
```

## Next Steps

1. ✅ Run initial audit
2. ✅ Review CODEBASE_AUDIT_RECOMMENDATIONS.md
3. ⏳ Clean up temporary files (Priority 1)
4. ⏳ Review archive candidates (Priority 2)
5. ⏳ Update outdated documentation (Priority 4)
6. ⏳ Review duplicates and obsolete files (Priority 3 & 5)

## Related Documentation

- `CODEBASE_AUDIT_REPORT.md` - Latest audit findings
- `CODEBASE_AUDIT_RECOMMENDATIONS.md` - Detailed cleanup plan
- `docs/DEPRECATION_PLAN.md` - Legacy shim removal timeline
- `docs/LEGACY_ARCHIVE_CANDIDATES.md` - Previous analysis
- `docs/CORE_DUPLICATE_ANALYSIS.md` - Duplicate analysis

## Support

For issues or questions:
1. Check `CODEBASE_AUDIT_RECOMMENDATIONS.md` for guidance
2. Review test output: `python -m pytest tests/test_codebase_auditor.py -v`
3. Run with verbose output to debug issues

---

**Last Updated:** 2025-11-22
**Tools Version:** 1.0.0
**Test Coverage:** 14/14 tests passing (100%)
