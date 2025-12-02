---
doc_id: DOC-PAT-EXEC-015-STALE-FILE-ARCHIVER-861
---

# EXEC-015: Stale File Archiver Pattern Specification

**Pattern ID:** EXEC-015  
**Version:** 1.0.0  
**Date:** 2025-11-29  
**Status:** Ready for Implementation  
**Confidence:** 85% (Auto-approved with review)  
**Priority:** P1

---

## Overview

Automatically identify and archive stale files that have not been modified or referenced recently, creating symlinks for backward compatibility during a grace period.

### Goals

1. **Identify stale files** using multi-factor staleness scoring
2. **Archive to consolidation directory** with preserved structure
3. **Create symlinks** for 30-day grace period
4. **Reduce active codebase clutter** without data loss

### Non-Goals

- Delete any files (archive only)
- Archive actively used files
- Remove files with recent commits
- Archive whitelisted critical files

---

## Staleness Scoring Algorithm

### Scoring Components (Total = 100 points)

| Component | Weight | Description | Threshold |
|-----------|--------|-------------|-----------|
| **Last Modified** | 30% | Days since last modification | ≥180 days = max |
| **Last Commit** | 20% | Days since last git commit | ≥365 days = max |
| **Reference Count** | 20% | Number of imports/references (inverted) | 0 refs = max |
| **Location Tier** | 10% | File location priority (inverted) | archive/ = max |
| **File Size** | 10% | File size (inverted) | Smaller = max |
| **Test Coverage** | 10% | Has test file (inverted) | No tests = max |

### Staleness Threshold

- **≥70 points:** File is stale → Archive
- **<70 points:** File is active → Keep

### Calculation Examples

#### Example 1: Stale Archive File
```yaml
File: archive/legacy/old_module.py
- Last modified: 250 days ago → 30 pts (180+ = max)
- Last commit: 400 days ago → 20 pts (365+ = max)
- References: 0 → 20 pts (inverted)
- Location: archive/ → 10 pts (tier 100)
- Size: 2 KB → 10 pts (small)
- Tests: None → 10 pts (inverted)
Total: 100 points → ARCHIVE ✓
```

#### Example 2: Active Core File
```yaml
File: core/engine/orchestrator.py
- Last modified: 5 days ago → 1 pt
- Last commit: 2 days ago → 0 pts
- References: 50+ → 0 pts (inverted)
- Location: core/ → 1 pt (tier 10)
- Size: 500 KB → 0 pts (large)
- Tests: Yes → 0 pts (has tests)
Total: 2 points → KEEP ✓
```

#### Example 3: Borderline File
```yaml
File: modules/deprecated/helper.py
- Last modified: 200 days ago → 30 pts
- Last commit: 300 days ago → 16 pts
- References: 2 → 16 pts
- Location: modules/ → 3 pts (tier 30)
- Size: 15 KB → 8 pts
- Tests: None → 10 pts
Total: 83 points → ARCHIVE ✓
```

---

## Implementation

### Detection Engine: `staleness_scorer.py`

**Location:** `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/detectors/staleness_scorer.py`

**Key Methods:**
```python
class StalenessScorer:
    def score_file(file_path: str) -> Dict:
        """Calculate staleness score for a file."""
        
    def scan_directory(directory: str) -> List[Dict]:
        """Scan directory and score all files."""
        
    def identify_stale_files(threshold: int = 70) -> List[str]:
        """Return list of files exceeding threshold."""
```

### Execution Workflow

1. **Discovery Phase**
   - Scan configured directories
   - Calculate staleness scores
   - Identify files ≥70 points
   - Generate report with recommendations

2. **Archive Phase**
   - Create archive structure: `archive/stale_YYYY-MM-DD/`
   - Move stale files preserving directory structure
   - Create symlinks at original locations
   - Commit in batches (20 files per batch)

3. **Grace Period** (30 days)
   - Symlinks allow backward compatibility
   - Monitor for broken imports
   - Log any access attempts

4. **Cleanup Phase** (After 30 days)
   - Remove symlinks
   - Consolidate archive
   - Update documentation

---

## Configuration

```yaml
# config/cleanup_automation_config.yaml

EXEC-015:
  name: "Stale File Archiver"
  enabled: true
  confidence: 85
  auto_approve: true  # Single review required
  priority: 1
  
  staleness_threshold_score: 70
  grace_period_days: 30
  
  # Scoring weights
  scoring:
    last_modified_days: 30  # ≥180 days = max
    last_commit_days: 20    # ≥365 days = max
    reference_count: 20     # 0 refs = max (inverted)
    location_tier: 10       # archive/ = max (inverted)
    file_size: 10           # Smaller = max (inverted)
    test_coverage: 10       # No tests = max (inverted)
  
  # Whitelist (never archive)
  whitelist_files:
    - "doc_id/**/*"
    - "CODEBASE_INDEX.md"
    - "*.schema.json"
    - "README.md"
    - "LICENSE"
  
  # Scan paths
  scan_paths:
    - "modules/"
    - "scripts/"
    - "archive/"  # Re-evaluate existing archive
    - "REFACTOR_2/"
    - "ToDo_Task/"
  
  # Exclusions
  exclude_patterns:
    - "__pycache__"
    - ".git"
    - "node_modules"
    - ".venv"
    - ".cleanup_backups"
```

---

## Safety Mechanisms

### Pre-Execution

- ✅ **Whitelist check:** Never archive critical files
- ✅ **Git status:** Working directory clean
- ✅ **Backup:** Full backup before archival
- ✅ **Dry-run:** Preview mode available

### During Execution

- ✅ **Symlink creation:** Maintain backward compatibility
- ✅ **Batch commits:** 20 files per commit
- ✅ **Structure preservation:** Mirror original directory layout
- ✅ **Git tracking:** All moves tracked in git

### Post-Execution

- ✅ **Symlink validation:** All symlinks functional
- ✅ **Import validation:** No broken imports
- ✅ **Test suite:** All tests passing
- ✅ **Rollback:** Automatic on failure

---

## CLI Usage

### Discovery

```bash
# Scan for stale files
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/detectors/staleness_scorer.py \
  --scan-paths modules/ scripts/ archive/ \
  --threshold 70 \
  --report staleness_report.json \
  --top 50 \
  --verbose

# Output:
# 🔍 EXEC-015: Stale File Analysis
# Threshold: 70 points (≥70 = stale)
# Scan paths: modules/, scripts/, archive/
# 
# 📊 Analysis Results:
#   Total files scanned: 1,234
#   Stale files found: 87 (≥70 points)
#   Active files: 1,147
# 
# 🔝 Top 50 Stale Files:
# 1. archive/legacy/old_module.py (Score: 100)
# 2. modules/deprecated/helper.py (Score: 83)
# ...
```

### Execution (Manual Approach)

```bash
# Review report
cat staleness_report.json | jq '.stale_file_details | length'

# Archive stale files (batch by batch)
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/runtime/stale_file_archiver.py \
  --input staleness_report.json \
  --archive-dir archive/stale_2025-11-29/ \
  --create-symlinks \
  --batch-size 20
```

---

## Expected Results

### Baseline Estimate

Based on current codebase analysis:

| Metric | Estimated |
|--------|-----------|
| **Files Scanned** | ~1,500 |
| **Stale Files** | ~100-150 |
| **Archive Size** | ~2-3 MB |
| **Symlinks Created** | ~100-150 |
| **Batches** | ~6-8 |
| **Execution Time** | ~20 minutes |

### Success Criteria

- [ ] 100+ stale files archived
- [ ] ~2-3 MB space organized
- [ ] All symlinks functional
- [ ] Zero broken imports
- [ ] 196/196 tests passing
- [ ] Zero rollback incidents

---

## Location Tier Scoring

Location tiers determine archival priority (inverted scoring):

| Location | Tier Score | Archival Priority |
|----------|------------|-------------------|
| `archive/` | 100 | Highest (already archived) |
| `legacy/` | 90 | Very High |
| `deprecated/` | 80 | High |
| `ToDo_Task/` | 70 | Medium-High |
| `REFACTOR_2/` | 60 | Medium |
| `modules/` | 30 | Low |
| `core/` | 10 | Very Low |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/` | 0 | Lowest (never archive) |

---

## Archival Structure

```
archive/
└── stale_2025-11-29/
    ├── modules/
    │   └── deprecated/
    │       └── helper.py          # Original file moved here
    ├── scripts/
    │   └── old_tool.py
    └── README.md                  # Archive manifest
```

**Original locations get symlinks:**
```
modules/deprecated/helper.py → ../../archive/stale_2025-11-29/modules/deprecated/helper.py
```

---

## Grace Period Management

### During Grace Period (30 days)

1. **Monitor access:** Log any imports/references to symlinks
2. **Track usage:** Record if archived files still needed
3. **Quick restore:** Symlinks allow instant access
4. **Review threshold:** Adjust scoring if needed

### After Grace Period

1. **Remove symlinks:** Clean original locations
2. **Consolidate archive:** Merge into main archive
3. **Update docs:** Document archived files
4. **Final report:** Summary of archival results

---

## Rollback Plan

If issues arise:

```bash
# Option 1: Restore from symlinks (during grace period)
# Files still accessible via symlinks - no action needed

# Option 2: Restore specific files
cp archive/stale_2025-11-29/path/to/file.py path/to/file.py
git add path/to/file.py
git commit -m "chore: Restore file from archive"

# Option 3: Full rollback
git revert <archival_commit>
```

---

## Integration with EXEC-014

EXEC-015 builds on EXEC-014 success:

1. **No duplicates:** EXEC-014 removed all duplicates first
2. **Clean baseline:** Staleness scoring on deduplicated codebase
3. **Canonical files:** Only canonical files evaluated for staleness
4. **Complementary:** Different criteria (duplicates vs. staleness)

---

## Risk Assessment

### Risk Level: **MEDIUM** ⚠️

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Archiving needed file | Low | Medium | Whitelist + grace period + symlinks |
| Broken imports | Low | Medium | Symlinks + import validation |
| Incorrect scoring | Medium | Low | Manual review + dry-run |
| Symlink issues (Windows) | Medium | Low | Test on Windows first |

### Mitigation Strategies

1. **Whitelist critical files:** Never archive doc_id/, schemas, READMEs
2. **Grace period:** 30-day symlinks for safety
3. **Batch processing:** Easy rollback per batch
4. **Import validation:** Test suite runs after each batch
5. **Manual review:** 85% confidence requires review

---

## Week 1 Execution Plan

### Day 3: Discovery & Review (2 hours)

```bash
# 1. Run staleness analysis
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/detectors/staleness_scorer.py \
  --scan-paths modules/ scripts/ archive/ REFACTOR_2/ ToDo_Task/ \
  --threshold 70 \
  --report staleness_report.json \
  --verbose

# 2. Review top stale files
cat staleness_report.json | jq '.stale_file_details[:20]'

# 3. Verify whitelist
# Check no critical files in stale list
```

### Day 4: Execution (2-3 hours)

```bash
# 1. Archive stale files (first batch)
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/runtime/stale_file_archiver.py \
  --input staleness_report.json \
  --archive-dir archive/stale_2025-11-29/ \
  --create-symlinks \
  --batch-size 20 \
  --dry-run  # Preview first

# 2. Execute (after review)
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/runtime/stale_file_archiver.py \
  --input staleness_report.json \
  --archive-dir archive/stale_2025-11-29/ \
  --create-symlinks \
  --batch-size 20

# 3. Validate
pytest -q tests/
python scripts/paths_index_cli.py gate
```

### Day 5: Week 1 Summary

- Generate Week 1 completion report
- Document EXEC-014 + EXEC-015 results
- Prepare for Week 2 (EXEC-016)

---

## Future Enhancements

1. **ML-based scoring:** Train model on archival decisions
2. **Usage tracking:** Monitor actual file access patterns
3. **Auto-adjustment:** Dynamic threshold based on codebase size
4. **Archive compression:** Compress old archives automatically
5. **Restoration UI:** Interactive tool to restore archived files

---

## Files Created

### Implementation
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/detectors/staleness_scorer.py`
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/runtime/stale_file_archiver.py` (to be created)

### Specification
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/specs/EXEC-015-stale-file-archiver.md` (this file)

### Reports
- `staleness_report.json` (discovery output)
- `exec015_results.json` (execution results)

---

**Status:** ✅ Specification Complete, Implementation Ready  
**Next:** Run discovery phase, review results, execute archival  
**Dependency:** None (EXEC-014 complete)  
**Estimated Time:** 4-5 hours total (discovery + execution)

🗂️ **Ready to organize the codebase by archiving ~100-150 stale files!**
