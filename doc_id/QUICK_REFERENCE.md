---
doc_id: DOC-GUIDE-QUICK-REFERENCE-487
---

# Doc ID System - Quick Reference Card

**Status**: ✅ FULLY OPERATIONAL
**Coverage**: 58.6% (1,307/2,230 files)
**Last Updated**: 2025-12-04

---

## Quick Commands

### Scan & Report
```bash
# Scan all files
python doc_id\doc_id_scanner.py scan

# View statistics
python doc_id\doc_id_scanner.py stats

# Generate coverage report
python doc_id\doc_id_scanner.py report --format markdown
```

### Manage Registry
```bash
# View registry stats
python doc_id\tools\doc_id_registry_cli.py stats

# Mint new doc_id
python doc_id\tools\doc_id_registry_cli.py mint \
  --category core \
  --name my-component \
  --title "My Component"

# List all doc_ids
python doc_id\tools\doc_id_registry_cli.py list

# Validate registry
python doc_id\tools\doc_id_registry_cli.py validate
```

### Auto-Assign
```bash
# Preview assignments (dry-run)
python doc_id\doc_id_assigner.py auto-assign --dry-run --limit 10

# Assign to specific file types
python doc_id\doc_id_assigner.py auto-assign --types md --dry-run

# Batch assign (careful!)
python doc_id\doc_id_assigner.py auto-assign --limit 50
```

---

## Directory Structure

```
doc_id/
├── DOC_ID_REGISTRY.yaml         # Central registry
├── tools/
│   └── doc_id_registry_cli.py   # Registry implementation
├── doc_id_registry_cli.py       # CLI wrapper
├── doc_id_scanner.py            # Repository scanner
├── doc_id_assigner.py           # Auto-assigner
└── doc_id_coverage_trend.py     # Trend tracker
```

---

## Current Coverage

| Type | Coverage | Files |
|------|----------|-------|
| Python | 89.3% | 533/597 ✅ |
| YAML | 91.9% | 193/210 ✅ |
| JSON | 73.1% | 234/320 ✅ |
| PS1 | 65.7% | 138/210 ✅ |
| Markdown | 22.1% | 182/823 ⚠️ |
| Shell | 33.3% | 10/30 ⚠️ |
| Text | 42.9% | 15/35 ⚠️ |

**Total**: 1,307/2,230 files (58.6%)

---

## doc_id Format

```
DOC-{CATEGORY}-{NAME}-{NUMBER}
```

**Examples**:
- `DOC-CORE-SCHEDULER-001`
- `DOC-ERROR-PYTHON-RUFF-002`
- `DOC-GUIDE-QUICK-START-003`

---

## Categories (14 total)

- `core` - Core system components
- `error` - Error detection/recovery
- `patterns` - Execution patterns
- `guide` - Documentation
- `spec` - Specifications
- `test` - Test files
- `script` - Automation scripts
- `config` - Configuration
- `legacy` - Archived code
- `task` - Workstream definitions
- `infra` - Infrastructure
- `aim` - AIM environment
- `pm` - Project management
- `engine` - Job execution

---

## Files Created/Fixed

### Created ✅
- `doc_id/DOC_ID_REGISTRY.yaml` - Registry data
- `doc_id/__init__.py` - Package marker
- `doc_id/tools/__init__.py` - Submodule marker
- `doc_id/DOC_ID_SYSTEM_FIX_SUMMARY.md` - Fix report

### Fixed ✅
- `doc_id/doc_id_registry_cli.py` - Wrapper (circular import)
- `doc_id/tools/doc_id_registry_cli.py` - Registry path
- `doc_id/doc_id_assigner.py` - Dataclass bugs (2 fixes)

### Moved ✅
- Renamed "doc_id_registry_cli - Copy.py" → `tools/doc_id_registry_cli.py`

---

## All Bugs Fixed ✅

1. ✅ Missing `DOC_ID_REGISTRY.yaml` - Created
2. ✅ Circular import in wrapper - Fixed
3. ✅ Wrong registry path - Fixed
4. ✅ InventoryEntry dataclass bug - Fixed
5. ✅ AssignmentResult dataclass bug - Fixed
6. ✅ Missing `doc_id/tools/` directory - Created

---

## Validation Status

- ✅ Scanner working (2,230 files scanned)
- ✅ Registry CLI operational
- ✅ Minting new doc_ids working
- ✅ Auto-assigner working
- ✅ Coverage reporting working
- ✅ All dataclasses fixed

---

## Next Actions (Optional)

1. **Fix 241 invalid doc_ids** - Run validation
2. **Improve Markdown coverage** - Currently 22.1%, target 80%
3. **Auto-assign remaining 682 files** - Use assigner
4. **Set up trend tracking** - Monitor coverage over time

---

## Documentation

- 📄 `DOC_ID_SYSTEM_FIX_SUMMARY.md` - Complete fix report
- 📄 `DOC_ID_SYSTEM_BUG_ANALYSIS.md` - Original bug analysis
- 📄 `DOC_ID_SYSTEM_STATUS.md` - System status
- 📄 `UTE_ID_SYSTEM_SPEC.md` - Specification
- 📄 `DOC_ID_COVERAGE_REPORT.md` - Latest coverage report

---

**System Status**: Fully operational and ready for production use! 🎉
