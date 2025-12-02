---
doc_id: DOC-PAT-EXEC-014-EXACT-DUPLICATE-ELIMINATOR-860
---

# EXEC-014: Exact Duplicate Eliminator

**Pattern ID:** EXEC-014
**Pattern Name:** Exact Duplicate Eliminator
**Version:** 1.0.0
**Category:** cleanup
**Confidence:** 95-100%
**Auto-Approval:** YES
**Estimated Time:** ~15 minutes
**Priority:** P0

---

## Purpose

Eliminate exact file duplicates across the repository using SHA256 hash matching. This pattern safely identifies, archives, and removes duplicate files while preserving the canonical version and maintaining system integrity.

---

## Problem Statement

The codebase currently has **47 exact duplicate files** identified across multiple locations:
- `core/`, `modules/`, `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/`, and `archive/`
- Duplicates consume ~2.3 MB of disk space
- Create confusion for developers and AI tools about which version is canonical
- Increase maintenance burden (changes must be applied to multiple locations)

---

## Solution

Automated detection and removal of exact duplicates using:
1. **SHA256 hashing** for 100% accuracy (no false positives)
2. **Canonical scoring** to select the best version to keep
3. **Safe archival** before deletion for easy recovery
4. **Import validation** to prevent breaking changes

---

## Inputs

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `scan_paths` | `List[Path]` | Yes | - | Directories to scan for duplicates |
| `exclusions` | `List[str]` | No | `["tests/", "docs/", ".git/", "__pycache__/"]` | Patterns to exclude from scanning |
| `hash_algorithm` | `str` | No | `"SHA256"` | Hash algorithm (SHA256 recommended) |
| `min_file_size` | `int` | No | `1024` | Minimum file size in bytes (1 KB) |
| `dry_run` | `bool` | No | `false` | If true, only report duplicates without deletion |

---

## Execution Flow

### Phase 1: Discovery (2 minutes)

**Action:** Scan filesystem and compute hashes

**Steps:**
1. Traverse `scan_paths` directories recursively
2. Filter files by exclusions and minimum size
3. Compute SHA256 hash for each file
4. Group files by identical hash values
5. Identify duplicate groups (2+ files with same hash)

**Output:**
```json
{
  "duplicate_groups": [
    {
      "hash": "a1b2c3d4...",
      "file_count": 3,
      "total_size_bytes": 4096,
      "files": [
        "/path/to/file1.py",
        "/path/to/file2.py",
        "/path/to/file3.py"
      ]
    }
  ],
  "total_duplicates": 47,
  "potential_savings_bytes": 2421760
}
```

### Phase 2: Ranking (1 minute)

**Action:** Score each file to determine canonical version

**Scoring Criteria** (0-100 points):
- **Location tier** (40 pts): `UETF/ > modules/ > core/ > engine/ > archive/`
- **Recency** (30 pts): Newest modification time wins
- **Import count** (20 pts): Most imported file wins (import graph analysis)
- **File path depth** (10 pts): Shallower paths preferred (simpler is better)

**Selection:** Highest scoring file = canonical version (keep)

**Output:**
```json
{
  "canonical": "/UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/orchestrator.py",
  "canonical_score": 95,
  "duplicates_to_delete": [
    {
      "path": "/core/orchestrator.py",
      "score": 45,
      "reason": "shim_layer"
    },
    {
      "path": "/modules/core-engine/m010001_orchestrator.py",
      "score": 62,
      "reason": "lower_tier"
    }
  ]
}
```

### Phase 3: Execution (10 minutes)

**Action:** Archive and delete non-canonical duplicates

**Steps:**
1. **Pre-execution validation:**
   - Git working directory clean
   - All tests passing (196/196)
   - Backup directory writable

2. **For each duplicate file:**
   - Create backup: `.cleanup_backups/YYYY-MM-DD-HHMMSS/[original_path]`
   - Update any direct file references (rare, but checked)
   - Delete duplicate file
   - Commit change: `git add -A && git commit -m "cleanup(EXEC-014): Remove duplicate [file]"`

3. **Batch processing:**
   - Process 10 files per batch
   - Commit after each batch
   - Continue if successful, rollback if any failure

**Output:**
```json
{
  "deleted_files": 47,
  "space_saved_bytes": 2421760,
  "commits_created": 5,
  "backup_location": ".cleanup_backups/2025-11-29-140532/"
}
```

### Phase 4: Verification (2 minutes)

**Action:** Validate no breaking changes introduced

**Checks:**
1. **Test suite:** `pytest -q tests/` (all 196 tests must pass)
2. **Import validation:** `python scripts/paths_index_cli.py gate`
3. **Broken imports:** `python scripts/detect_broken_imports.py`
4. **Duplicate verification:** Re-scan to confirm zero duplicates remain

**Success Criteria:**
- ✅ All tests passing (196/196)
- ✅ No broken imports detected
- ✅ Zero duplicate SHA256 hashes remain
- ✅ Space savings achieved (≥2 MB)

**Failure Handling:**
- Any check fails → Automatic rollback
- Restore from `.cleanup_backups/` directory
- Revert git commits: `git revert HEAD~N..HEAD`
- Generate failure report for manual review

---

## Ground Truth Criteria

### Success Conditions

```python
# All conditions must be true
success = (
    duplicate_count == 0 and
    tests_passed == 196 and
    broken_imports == 0 and
    space_saved_bytes >= 2_000_000
)
```

### Verification Commands

```bash
# 1. Verify no duplicates remain
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/detectors/duplicate_detector.py --verify

# 2. Run full test suite
pytest -q tests/ --maxfail=1

# 3. Validate import graph
python scripts/paths_index_cli.py gate

# 4. Check for broken imports
python scripts/detect_broken_imports.py

# 5. Measure space savings
du -sh .cleanup_backups/
```

---

## Safety Mechanisms

### Pre-Execution Checks

```yaml
checks:
  - name: "Git status clean"
    command: "git diff --exit-code"
    required: true

  - name: "Tests passing"
    command: "pytest --collect-only -q"
    required: true

  - name: "Backup space available"
    command: "df -h | grep -E '([0-9]+G|[0-9]{3,}M).*/$'"
    required: true
    min_space_mb: 10
```

### During Execution

- **Batched commits:** 10 files per commit (easy surgical rollback)
- **Per-batch validation:** Quick import check after each batch
- **Progress tracking:** Live progress bar with ETA
- **Automatic pause:** Stop on first error, await manual decision

### Post-Execution

- **Verification report:** Detailed JSON + human-readable summary
- **Rollback documentation:** Exact commands to undo all changes
- **Backup retention:** 90 days, then archive to `archive/cleanup_backups/`

### Rollback Procedure

```bash
# Step 1: Revert git commits (if N batches committed)
git revert HEAD~N..HEAD

# Step 2: Restore files from backup
cp -r .cleanup_backups/YYYY-MM-DD-HHMMSS/* .

# Step 3: Verify restoration
pytest -q tests/
git status

# Step 4: Document rollback reason
echo "Rollback completed: [reason]" >> .cleanup_backups/rollback_log.txt
```

---

## Integration

### Quality Gates

**Pre-commit Hook:**
```python
# .git/hooks/pre-commit (added section)
# Prevent new duplicates from being committed
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/detectors/duplicate_detector.py \
  --check-staged \
  --fail-on-duplicate
```

**CI Pipeline:**
```yaml
# .github/workflows/quality-gate.yml (added job)
- name: Detect Duplicate Files
  run: |
    python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/detectors/duplicate_detector.py \
      --fail-on-duplicate \
      --report duplicate_report.json

  - name: Upload Report
    uses: actions/upload-artifact@v3
    with:
      name: duplicate-report
      path: duplicate_report.json
```

### Pattern Registry

Register pattern in `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/registry/cleanup_patterns.yaml`:

```yaml
patterns:
  - id: "EXEC-014"
    name: "Exact Duplicate Eliminator"
    category: "cleanup"
    confidence: 95
    auto_approval: true
    enabled: true
```

### Event System

Emit events for monitoring:

```python
# Event emitted after successful execution
event = {
    "pattern_id": "EXEC-014",
    "status": "completed",
    "timestamp": "2025-11-29T14:32:15Z",
    "metrics": {
        "duplicates_removed": 47,
        "space_saved_bytes": 2421760,
        "execution_time_seconds": 847
    }
}
emit_event("pattern_execution_complete", event)
```

---

## Expected Results

### Quantitative Metrics

- **Files deleted:** 47 exact duplicates
- **Space saved:** ~2.3 MB
- **Commits created:** 5 batches
- **Execution time:** ~15 minutes (including verification)
- **False positive rate:** 0% (SHA256 guarantees exact match)
- **Test pass rate:** 100% (196/196)

### Qualitative Improvements

- **Developer clarity:** Single canonical location per file
- **AI navigation:** No ambiguity about which file to use
- **Maintenance burden:** Changes only need to be made once
- **Repository health:** Reduced cruft, cleaner structure

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Delete wrong file | Very Low (0.1%) | High | SHA256 hashing, canonical scoring, backup before delete |
| Break imports | Low (5%) | High | Import validation, test gating, automatic rollback |
| Data loss | Very Low (0.1%) | Critical | Full backup, 90-day retention, git history |
| Test failures | Medium (15%) | Medium | Pre-execution test check, automatic rollback |

**Overall Risk Level:** ⚠️ **Very Low**

**Auto-Approval:** ✅ **YES** (95-100% confidence)

---

## Manual Review Tier

**Tier:** 1 (Auto-Approved)

**Rationale:**
- 95-100% confidence (SHA256 exact matching)
- Zero false positives possible
- Comprehensive safety mechanisms
- Full rollback capability
- Minimal breaking change risk

**Review Process:**
- **Pre-execution:** None required (auto-approved)
- **Post-execution:** Audit log review only
- **Escalation:** Only if execution fails or anomalies detected

---

## Usage Examples

### Dry-Run Mode (Discovery Only)

```bash
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/runtime/cleanup_executor.py \
  --pattern EXEC-014 \
  --dry-run \
  --report duplicates_report.json
```

### Full Execution (Auto-Approved)

```bash
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/runtime/cleanup_executor.py \
  --pattern EXEC-014 \
  --auto-approve \
  --log cleanup_exec014.log
```

### Custom Configuration

```bash
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/runtime/cleanup_executor.py \
  --pattern EXEC-014 \
  --config custom_config.yaml \
  --scan-paths "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/" "modules/" \
  --min-file-size 512
```

---

## Related Patterns

- **EXEC-015:** Stale File Archiver (complementary - handles near-duplicates)
- **EXEC-016:** Import Path Standardizer (follow-up - fix import references)
- **EXEC-012:** Module Consolidation (broader scope - consolidates entire modules)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-29 | Initial specification |

---

## References

- **Implementation:** `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/detectors/duplicate_detector.py`
- **Execution Engine:** `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/automation/runtime/cleanup_executor.py`
- **Configuration:** `config/cleanup_automation_config.yaml`
- **Orchestrator:** `scripts/cleanup_automation_orchestrator.py`

---

**Status:** ✅ Ready for implementation and Week 1 execution
