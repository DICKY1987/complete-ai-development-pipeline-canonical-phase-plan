---
doc_id: DOC-PAT-CLEANUP-AUTOMATION-IMPLEMENTATION-743
---

# Cleanup Automation Implementation Guide

**Status:** ✅ Core Implementation Complete
**Version:** 1.0.0
**Date:** 2025-11-29
**Priority Patterns:** EXEC-014, EXEC-016 (ready for Week 1-2 execution)

---

## Implementation Summary

This document summarizes the cleanup automation framework implementation based on the approved plan in `C:\Users\richg\.claude\plans\sleepy-dreaming-bubble.md`.

### What Was Created

#### 1. Pattern Specifications (2 files) ✅
- **EXEC-014:** `patterns/specs/EXEC-014-exact-duplicate-eliminator.md`
  - Comprehensive 450-line specification
  - SHA256-based duplicate detection
  - Canonical file ranking algorithm
  - 95-100% confidence, auto-approved
  - Estimated 47 duplicates, 2.3 MB savings

- **EXEC-016:** `patterns/specs/EXEC-016-import-path-standardizer.md`
  - Complete 400-line specification
  - Batched import migration strategy
  - 100% confidence (deterministic regex)
  - Estimated 300+ files, 800+ import changes

#### 2. Configuration (1 file) ✅
- **Main Config:** `config/cleanup_automation_config.yaml`
  - Global settings (auto-approval threshold: 75%+)
  - Pattern-specific configuration (EXEC-014 through EXEC-020)
  - Scan paths and exclusions
  - Validation settings
  - 4-week execution schedule

#### 3. Detection Engines (2 files) ✅
- **Duplicate Detector:** `patterns/automation/detectors/duplicate_detector.py`
  - 250+ lines of production code
  - SHA256 hashing with caching
  - Canonical ranking (location, recency, imports, depth)
  - CLI interface with verification mode
  - JSON export for reporting

- **Import Analyzer:** `patterns/automation/detectors/import_pattern_analyzer.py`
  - 250+ lines of production code
  - Regex-based pattern matching
  - Migration map support
  - Deprecated import detection
  - Batching support

#### 4. Execution Runtime (1 file) ✅
- **Cleanup Executor:** `patterns/automation/runtime/cleanup_executor.py`
  - 300+ lines orchestration engine
  - Pre-execution validation (git, tests, backup)
  - Pattern-specific execution logic
  - Post-execution validation
  - Automatic rollback on failure
  - JSON result export

---

## File Structure Created

```
config/
└── cleanup_automation_config.yaml         # ✅ Main configuration

UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/
├── patterns/
│   ├── specs/
│   │   ├── EXEC-014-exact-duplicate-eliminator.md     # ✅ Priority 1
│   │   └── EXEC-016-import-path-standardizer.md       # ✅ Priority 2
│   ├── automation/
│   │   ├── detectors/
│   │   │   ├── duplicate_detector.py                  # ✅ EXEC-014 engine
│   │   │   └── import_pattern_analyzer.py             # ✅ EXEC-016 engine
│   │   └── runtime/
│   │       └── cleanup_executor.py                    # ✅ Main executor
│   └── CLEANUP_AUTOMATION_IMPLEMENTATION.md           # ✅ This file
```

---

## Quick Start Guide

### 1. Verify Installation

```bash
# Check Python version (3.9+ recommended)
python --version

# Verify files exist
ls UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/specs/
ls UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/detectors/
ls config/cleanup_automation_config.yaml

# Install dependencies (if needed)
pip install pyyaml  # For configuration loading
```

### 2. Run Discovery (Dry-Run)

#### EXEC-014: Detect Duplicates
```bash
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/detectors/duplicate_detector.py \
  --scan-paths UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/ modules/ core/ \
  --report duplicates_report.json

# Expected output:
# Duplicate Detection Results:
#   Total duplicate groups: X
#   Total duplicate files: 47 (estimated)
#   Potential space savings: 2.3 MB
```

#### EXEC-016: Detect Import Violations
```bash
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/detectors/import_pattern_analyzer.py \
  --scan-paths . \
  --check-all \
  --report import_violations.json

# Expected output:
# Import Pattern Analysis Results:
#   Files to update: 300+ (estimated)
#   Total import changes: 800+
#   Estimated batches: 12-15
```

### 3. Execute Pattern (Full Run)

#### EXEC-014: Remove Duplicates
```bash
# Dry-run first (highly recommended)
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/runtime/cleanup_executor.py \
  --pattern EXEC-014 \
  --dry-run

# Full execution (auto-approved at 95%+ confidence)
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/runtime/cleanup_executor.py \
  --pattern EXEC-014 \
  --auto-approve \
  --report exec014_results.json
```

---

## Configuration Reference

### Auto-Approval Thresholds (User Selected: Balanced)

```yaml
# config/cleanup_automation_config.yaml

global:
  auto_approval_threshold: 75  # User preference: Balanced
  require_manual_review_below: 75

patterns:
  EXEC-014:
    confidence: 95
    auto_approve: true   # ✅ Auto-approved (95% ≥ 75%)

  EXEC-016:
    confidence: 100
    auto_approve: true   # ✅ Auto-approved (100% ≥ 75%)

  EXEC-015:
    confidence: 85
    auto_approve: true   # ⚠️ Single review required (85% tier)

  EXEC-018:
    confidence: 80
    auto_approve: false  # ❌ Manual review (below 90%)
```

### Scan Paths & Exclusions

```yaml
scan_paths:
  - "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/"
  - "modules/"
  - "core/"
  - "error/"
  - "scripts/"
  - "tests/"

exclusions:
  directories:
    - ".git/"
    - "__pycache__/"
    - "archive/"  # Already archived
    - ".cleanup_backups/"  # Our own backups
```

---

## Safety Mechanisms

### Pre-Execution Checks

All patterns verify:
- ✅ Git working directory clean
- ✅ Tests passing (196/196 baseline)
- ✅ Backup directory writable
- ✅ Sufficient disk space

### During Execution

- **Batched commits:** 10-25 files per commit
- **Progress tracking:** Live updates
- **Test gating:** Tests run after each batch
- **Auto-pause:** Stop on first error

### Post-Execution

- **Full test suite:** All 196 tests must pass
- **Import validation:** No broken imports
- **Rollback:** Automatic on any failure

---

## Week 1 Execution Plan

### Day 1-2: EXEC-014 (Exact Duplicates)

```bash
# 1. Discovery
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/detectors/duplicate_detector.py \
  --scan-paths . \
  --report duplicates_discovery.json

# 2. Review report (auto-approved, but good to check)
cat duplicates_discovery.json | jq '.duplicate_groups | length'

# 3. Execute
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/runtime/cleanup_executor.py \
  --pattern EXEC-014 \
  --auto-approve \
  --log exec014.log

# 4. Verify
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/detectors/duplicate_detector.py \
  --verify
```

**Expected Results:**
- 47 exact duplicates removed
- ~2.3 MB space saved
- 5 batched commits
- 100% test pass rate

### Day 3-4: EXEC-015 (Stale Files)

*Implementation pending - requires staleness_scorer.py*

### Day 5: Validation & Documentation

```bash
# Full test suite
pytest -q tests/

# Import validation
python scripts/paths_index_cli.py gate

# Generate metrics
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/runtime/cleanup_executor.py \
  --pattern EXEC-014 \
  --report week1_summary.json
```

---

## Week 2 Execution Plan

### Day 6-11: EXEC-016 (Import Standardization)

```bash
# 1. Discovery
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/detectors/import_pattern_analyzer.py \
  --scan-paths . \
  --check-all \
  --report import_plan.json

# 2. Review migration plan
cat import_plan.json | jq '.batches | length'

# 3. Execute (batched)
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/runtime/cleanup_executor.py \
  --pattern EXEC-016 \
  --auto-approve \
  --log exec016.log

# 4. Verify
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/detectors/import_pattern_analyzer.py \
  --check-deprecated \
  --fail-on-violation
```

**Expected Results:**
- 300+ files updated
- 800+ import statements migrated
- 12-15 batched commits
- 0% import ambiguity remaining

---

## Troubleshooting

### Issue: Pre-execution validation fails

```bash
# Check git status
git status

# Run tests manually
pytest -q tests/

# Check backup directory
ls -la .cleanup_backups/
```

### Issue: Pattern execution fails

```bash
# Check execution log
cat exec014.log

# Manual rollback if needed
git log --oneline | head -5
git revert HEAD  # Revert last commit

# Restore from backup
cp -r .cleanup_backups/[timestamp]/* .
```

### Issue: Import errors after migration

```bash
# Verify import paths
python scripts/paths_index_cli.py gate

# Check for broken imports
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/detectors/import_pattern_analyzer.py \
  --check-deprecated

# Fix specific file
python -m py_compile [file.py]
```

---

## Next Steps

### Immediate (Ready Now)
1. ✅ **Test basic imports:**
   ```bash
   python -c "from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.patterns.automation.detectors.duplicate_detector import DuplicateDetector; print('✓ Import successful')"
   ```

2. ✅ **Run discovery on your codebase:**
   ```bash
   python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/detectors/duplicate_detector.py \
     --scan-paths . --report my_duplicates.json
   ```

3. ✅ **Review configuration:**
   - Edit `config/cleanup_automation_config.yaml` if needed
   - Adjust scan_paths, exclusions, thresholds

### Week 1 Preparation
1. **Create import migration map:**
   - File: `config/import_migration_map.yaml`
   - Based on your specific import patterns

2. **Setup backup infrastructure:**
   ```bash
   mkdir -p .cleanup_backups
   echo ".cleanup_backups/" >> .gitignore
   ```

3. **Baseline metrics:**
   - Run discovery for EXEC-014 and EXEC-016
   - Document current state (duplicates, import patterns)

### Future Enhancements

**Remaining Pattern Specs (Week 3-4):**
- EXEC-015: Stale File Archiver
- EXEC-017: Archive Consolidator
- EXEC-018: Orphaned Module Detector
- EXEC-019: Shim Removal Automation
- EXEC-020: Directory Structure Optimizer

**Additional Implementation Files:**
- `staleness_scorer.py` (for EXEC-015)
- `orphan_analyzer.py` (for EXEC-018)
- `batch_processor.py` (batching utility)
- `rollback_manager.py` (rollback coordination)
- Main orchestrator script

**Integration:**
- Pre-commit hooks
- CI/CD pipeline integration
- Automated scheduling

---

## Success Criteria

### Week 1 Success (EXEC-014 + EXEC-015)
- [ ] 47 exact duplicates removed
- [ ] ~3 MB total space saved
- [ ] 196/196 tests passing
- [ ] Zero rollback incidents

### Week 2 Success (EXEC-016)
- [ ] 300+ files with canonical imports
- [ ] 0% import ambiguity
- [ ] 12-15 batched commits
- [ ] Import graph acyclic

### Overall Success (Week 4)
- [ ] <10% duplication (down from 67%)
- [ ] 5-7 MB space saved
- [ ] Single canonical structure
- [ ] 90+ AI navigation clarity score

---

## Support & Documentation

- **Plan File:** `C:\Users\richg\.claude\plans\sleepy-dreaming-bubble.md`
- **Configuration:** `config/cleanup_automation_config.yaml`
- **Pattern Specs:** `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/specs/`
- **Implementation:** This file

**Questions or Issues:**
- Check troubleshooting section above
- Review pattern specifications for details
- Run in dry-run mode first to preview changes

---

**Status:** ✅ Ready for Week 1 execution (EXEC-014)
**Next Action:** Run discovery phase for EXEC-014 to get baseline metrics
