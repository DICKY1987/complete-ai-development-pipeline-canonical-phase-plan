---
doc_id: DOC-PAT-EXEC-017-COMPREHENSIVE-CODE-CLEANUP-862
---

# EXEC-017: Comprehensive Code Cleanup & Archival Pattern

**Pattern ID:** EXEC-017  
**Pattern Name:** Comprehensive Code Cleanup & Archival  
**Version:** 1.0.0  
**Category:** cleanup  
**Confidence:** 90%+ (Conservative)  
**Auto-Approval:** Tier 1 only (90%+ confidence)  
**Estimated Time:** 2-3 hours (implementation) + 1-2 hours (execution)  
**Priority:** P0  
**Depends On:** EXEC-013, EXEC-014, EXEC-015

---

## Purpose

Orchestrate a comprehensive 6-signal cleanup strategy to identify and archive obsolete Python code while excluding .md and .txt files. Builds on existing patterns to add entry point reachability and test coverage analysis.

---

## Problem Statement

From Code Cleanup Analysis, the repository needs:
- **90% confidence threshold** (conservative, very safe archival)
- **90-day staleness** (3 months - aggressive flagging)
- **Parallel implementation analysis** before archival decisions
- **Enhanced signals**: Entry point reachability + test coverage
- **Exclusion**: All .md and .txt files
- **Expected results**: 80-100 Tier 1 files, 100-150 Tier 2 files

---

## Solution: 6-Signal Cleanup Framework

### Signal Integration (Weighted Composite Score)

| Signal | Weight | Source Pattern | Description |
|--------|--------|----------------|-------------|
| **Duplication** | 25% | EXEC-014 | SHA-256 exact matches |
| **Staleness** | 15% | EXEC-015 | 90+ days without modification |
| **Obsolescence** | 20% | New | Deprecated patterns, version suffixes |
| **Isolation** | 15% | EXEC-013 | Not imported by active code |
| **Reachability** | 15% | **NEW** | Unreachable from entry points |
| **Test Coverage** | 10% | **NEW** | No test coverage |

**Confidence Boost:** +10 points if 3+ signals score ≥80

---

## Inputs

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `confidence_threshold` | `int` | No | `90` | Minimum confidence for archival (%) |
| `staleness_days` | `int` | No | `90` | Days threshold for staleness |
| `exclude_extensions` | `List[str]` | No | `[".md", ".txt"]` | File extensions to exclude |
| `output_dir` | `Path` | No | `cleanup_reports/` | Report output directory |
| `dry_run` | `bool` | No | `true` | If true, only generate reports |

---

## Execution Flow

### Phase 1: Enhanced Analyzer Setup (6-8 hours)

#### Step 1.1: Create Entry Point Reachability Analyzer

**File:** `scripts/entry_point_reachability.py`

**Purpose:** Identify orphaned code unreachable from any entry point

**Entry Points:**
1. Files with `if __name__ == "__main__":`
2. Test files in `./tests/`
3. CLI entry points (e.g., `./modules/aim-cli/m01001A_main.py`)
4. Scripts in `./scripts/`
5. Pytest fixtures (`conftest.py`)

**Algorithm:**
```python
def analyze_entry_point_reachability():
    """
    1. Identify all entry points
    2. Build import graph (reuse EXEC-013 logic)
    3. BFS traversal marking reachable modules
    4. Score by reachability distance
    
    Scoring:
    - 100: Not reachable + no test references
    - 85: Only reachable from other orphans
    - 70: Only via deprecated imports
    - 0: Reachable from active entry points
    """
```

**Output:** `entry_point_reachability_report.json`

**Ground Truth:** 
```bash
python scripts/entry_point_reachability.py && \
test -f cleanup_reports/entry_point_reachability_report.json && \
echo "✅ COMPLETE" || echo "❌ FAILED"
```

#### Step 1.2: Create Test Coverage Analyzer

**File:** `scripts/test_coverage_archival.py`

**Purpose:** Identify untested files (often indicates abandoned code)

**Algorithm:**
```python
def analyze_test_coverage_for_archival():
    """
    1. Scan ./tests/ and UETF/tests/
    2. Extract imports and test targets (AST)
    3. Build mapping: module -> [test_files]
    4. Cross-reference with staleness + isolation
    
    Scoring:
    - 95: No tests + 90+ days stale + not imported
    - 80: No tests + deprecated naming
    - 70: No tests + only imported by untested code
    - 0: Has test coverage
    """
```

**Output:** `test_coverage_archival_report.json`

**Ground Truth:**
```bash
python scripts/test_coverage_archival.py && \
test -f cleanup_reports/test_coverage_archival_report.json && \
echo "✅ COMPLETE" || echo "❌ FAILED"
```

#### Step 1.3: Enhance Main Cleanup Analyzer

**File:** `scripts/analyze_cleanup_candidates.py`

**Modifications:**
1. Update constants:
   ```python
   STALENESS_DAYS = 90  # Changed from 180
   CONFIDENCE_THRESHOLD = 90  # Changed from 85
   ```

2. Add fields to `FileScore` dataclass:
   ```python
   @dataclass
   class FileScore:
       # Existing fields...
       reachability_score: int = 0  # NEW
       test_coverage_score: int = 0  # NEW
   ```

3. Update composite scoring:
   ```python
   total = (
       dup_score * 0.25 +      # Duplication: 25%
       stale_score * 0.15 +    # Staleness: 15%
       obs_score * 0.20 +      # Obsolescence: 20%
       iso_score * 0.15 +      # Isolation: 15%
       reach_score * 0.15 +    # Reachability: 15% (NEW)
       test_score * 0.10       # Test coverage: 10% (NEW)
   )
   ```

4. Add file filtering:
   ```python
   def should_analyze_file(self, filepath: Path) -> bool:
       ext = filepath.suffix.lower()
       if ext in {'.md', '.txt'}:
           return False
       return ext in CODE_EXTENSIONS | CONFIG_EXTENSIONS
   ```

**Ground Truth:**
```bash
python scripts/analyze_cleanup_candidates.py \
  --confidence-threshold 90 \
  --staleness-days 90 \
  --exclude-extensions .md,.txt && \
echo "✅ COMPLETE" || echo "❌ FAILED"
```

### Phase 2: Parallel Implementation Analysis (3-4 hours)

#### Step 2.1: Create Parallel Implementation Detector

**File:** `scripts/detect_parallel_implementations.py`

**Purpose:** Detailed comparison of competing implementations

**Overlap Groups:**
- Orchestration: `./modules/core-engine/` vs `./engine/`
- Error systems: `./modules/error-engine/` vs `./UETF/error/`
- State management: `./modules/core-state/` vs `./state/` vs `./engine/state_store/`

**Scoring Criteria (200 points max):**
- CODEBASE_INDEX.yaml canonical path: +50 pts
- ULID-prefixed files (m010001_*): +40 pts
- Most recent git activity: +30 pts
- Higher import reference count: +25 pts
- Test coverage percentage: +25 pts
- Documentation quality: +15 pts
- Code size (prefer smaller/cleaner): +15 pts

**Output:** `parallel_implementations_analysis.json`

**Report Structure:**
```json
{
  "overlap_groups": [
    {
      "group_id": "orchestration_engines",
      "purpose": "Workstream orchestration",
      "implementations": [
        {
          "path": "modules/core-engine/",
          "score": 185,
          "ranking": 1,
          "status": "PRIMARY - KEEP",
          "strengths": ["Canonical", "ULID", "Recent commits"]
        },
        {
          "path": "engine/",
          "score": 120,
          "ranking": 2,
          "status": "SECONDARY - REVIEW FOR ARCHIVAL",
          "recommendation": "ANALYZE: Check for unique job queue functionality"
        }
      ]
    }
  ]
}
```

**Ground Truth:**
```bash
python scripts/detect_parallel_implementations.py && \
test -f cleanup_reports/parallel_implementations_analysis.json && \
echo "✅ COMPLETE" || echo "❌ FAILED"
```

### Phase 3: Master Orchestration (2-3 hours)

#### Step 3.1: Create Comprehensive Analyzer

**File:** `scripts/comprehensive_archival_analyzer.py`

**Purpose:** Orchestrate all analyzers and generate unified reports

**Execution Flow:**
```python
def run_comprehensive_analysis():
    """
    Step 1: Run analyzers in sequence
    - analyze_cleanup_candidates.py (enhanced)
    - entry_point_reachability.py
    - test_coverage_archival.py
    - detect_parallel_implementations.py
    - analyze_imports.py (deprecated tracking)
    
    Step 2: Aggregate results with 6-signal scoring
    
    Step 3: Generate tiered reports
    - TIER_1 (90-100%): Auto-archival safe
    - TIER_2 (75-89%): Review recommended
    - TIER_3 (60-74%): Manual expert review
    - TIER_4 (<60%): Keep
    
    Step 4: Generate execution artifacts
    - archival_plan_tier1_automated.ps1
    - archival_plan_tier2_review.json
    - parallel_implementations_decision_checklist.md
    - validation_checklist.md
    """
```

**Command:**
```bash
python scripts/comprehensive_archival_analyzer.py \
  --confidence-threshold 90 \
  --staleness-days 90 \
  --exclude-extensions .md,.txt \
  --output-dir cleanup_reports/
```

**Outputs:**
1. `comprehensive_archival_report.json` - Full analysis
2. `archival_plan_tier1_automated.ps1` - 90%+ confidence script
3. `archival_plan_tier2_review.json` - 75-89% review list
4. `archival_plan_tier3_manual.json` - 60-74% expert review
5. `parallel_implementations_decision_checklist.md` - Human decision aid
6. `validation_checklist.md` - Pre/post validation steps

**Ground Truth:**
```bash
ls cleanup_reports/*.{json,ps1,md} | wc -l | grep -q "6" && \
echo "✅ ALL OUTPUTS GENERATED" || echo "❌ MISSING OUTPUTS"
```

### Phase 4: Validation Framework (2-3 hours)

#### Step 4.1: Create Validation Script

**File:** `scripts/validate_archival_safety.py`

**Pre-Archive Validation:**
1. Import validation (no active imports to archived files)
2. Test suite validation (dry-run with files moved)
3. Entry point validation (all __main__ blocks accessible)
4. Git status check (no uncommitted changes)
5. Canonical path validation (CODEBASE_INDEX.yaml integrity)

**Post-Archive Validation:**
1. Test suite: All 458 valid tests pass
2. Import check: No new import errors
3. Entry points: All functional
4. Functionality: No regression detected

**Usage:**
```bash
# Before archival
python scripts/validate_archival_safety.py \
  --mode pre-archive \
  --files-list tier1_files.json

# After archival
python scripts/validate_archival_safety.py \
  --mode post-archive
```

**Ground Truth:**
```bash
python scripts/validate_archival_safety.py --mode pre-archive && \
echo "✅ PRE-ARCHIVE VALIDATION PASSED" || echo "❌ BLOCKERS FOUND"
```

### Phase 5: Execution Workflow (1-2 hours)

#### Recommended Steps

**Step 1: Run Analysis** (15-20 min)
```bash
python scripts/comprehensive_archival_analyzer.py \
  --confidence-threshold 90 \
  --staleness-days 90 \
  --exclude-extensions .md,.txt \
  --output-dir cleanup_reports/
```

**Step 2: Review Parallel Implementations** (30-60 min)
```bash
code cleanup_reports/parallel_implementations_decision_checklist.md
```

**Step 3: Review Tier 1 Candidates** (10-15 min)
```bash
python -c "import json; print(json.dumps(json.load(open('cleanup_reports/comprehensive_archival_report.json'))['tier_1_summary'], indent=2))"
```

**Step 4: Pre-Archive Validation** (5 min)
```bash
python scripts/validate_archival_safety.py --mode pre-archive
```

**Step 5: Execute Tier 1 Archival (DRY RUN FIRST)**
```powershell
cd cleanup_reports
.\archival_plan_tier1_automated.ps1  # $DryRun = $true by default

# Review output, then execute:
# Edit script: Set $DryRun = $false
.\archival_plan_tier1_automated.ps1
```

**Step 6: Post-Archive Validation** (5 min)
```bash
python scripts/validate_archival_safety.py --mode post-archive
pytest -q tests/
git status
```

**Step 7: Commit** (if validation passes)
```bash
$Timestamp = Get-Date -Format 'yyyy-MM-dd_HHmmss'

git add .
git commit -m "chore: Archive obsolete Python code (Tier 1 - 90%+ confidence)

Archived N files based on comprehensive 6-signal analysis:
- Duplication: SHA-256 exact matches
- Staleness: 90+ days without modification
- Obsolescence: Superseded by canonical modules
- Isolation: Not imported by active code
- Reachability: Unreachable from entry points
- Test coverage: No test coverage

Archive: archive/${Timestamp}_python-code-cleanup/
Confidence: 90-100% safe to archive
Configuration: 90-day staleness, 90% threshold

All validation checks passed:
✓ Tests passing (458/458)
✓ No import errors
✓ Entry points functional
✓ Git history preserved

Pattern: EXEC-017
"
```

---

## Expected Outcomes

### By Signal

| Signal | Threshold | Est. Files Flagged | Rationale |
|--------|-----------|-------------------|-----------|
| Duplication | SHA-256 match | 10-15 | Exact duplicates |
| Staleness | 90+ days | 200-250 | Aggressive 3-month threshold |
| Obsolescence | Deprecated patterns | 60-70 | Archive dirs, version suffixes |
| Isolation | Not imported | 40-50 | Orphaned modules |
| Reachability | Unreachable | 50-60 | Dead code paths |
| Test Coverage | No tests + stale | 120-150 | Untested + old = abandoned |

### By Tier

- **Tier 1 (90-100%)**: 80-100 files - Automated archival safe
  - Exact duplicates: ~15 files
  - Stale + not imported + no tests: ~40 files
  - In archive directories: ~10 files
  - Superseded by canonical modules: ~25 files

- **Tier 2 (75-89%)**: 100-150 files - Review recommended
  - Stale + deprecated patterns: ~50 files
  - Parallel implementation secondaries: ~30 files
  - Orphaned unclear purpose: ~40 files

- **Tier 3 (60-74%)**: 80-100 files - Manual expert review

- **Tier 4 (<60%)**: 600-700 files - Keep

### Space Savings

- Tier 1: 0.3-0.5 MB
- Tier 2 (if processed): 1.0-1.5 MB
- **Primary benefit**: Clarity and reduced cognitive load

---

## Archive Structure

```
./archive/2025-12-02_HHMMSS_python-code-cleanup/
├── ARCHIVE_MANIFEST.json           # Metadata and restoration
├── ARCHIVAL_ANALYSIS_REPORT.json   # Full analysis with all signals
├── README.md                        # Human-readable summary
├── modules/                         # Preserved directory structure
├── engine/                          # If archived
└── scripts/
```

**Manifest Format:**
```json
{
  "archive_metadata": {
    "timestamp": "2025-12-02T14:30:22Z",
    "confidence_tier": "TIER_1_SAFE_ARCHIVE",
    "created_by": "comprehensive_archival_analyzer.py v1.0",
    "user_config": {
      "confidence_threshold": 90,
      "staleness_days": 90,
      "excluded_extensions": [".md", ".txt"]
    }
  },
  "statistics": {
    "files_archived": 87,
    "total_size_bytes": 245760
  },
  "validation": {
    "pre_archive_tests_passed": true,
    "post_archive_tests_passed": true
  },
  "signals_summary": {
    "avg_duplication_score": 45,
    "avg_staleness_score": 92,
    "avg_obsolescence_score": 78,
    "avg_isolation_score": 85,
    "avg_reachability_score": 88,
    "avg_test_coverage_score": 90
  }
}
```

---

## Ground Truth Verification

### Success Criteria

✅ All files in `scripts/` created  
✅ `cleanup_reports/` contains 6 output files  
✅ Pre-archive validation passes  
✅ Post-archive validation passes  
✅ All 458 valid tests passing  
✅ Git history fully preserved

### Verification Commands

```bash
# Phase 1: Scripts exist
test -f scripts/entry_point_reachability.py && \
test -f scripts/test_coverage_archival.py && \
test -f scripts/detect_parallel_implementations.py && \
test -f scripts/comprehensive_archival_analyzer.py && \
test -f scripts/validate_archival_safety.py && \
echo "✅ ALL SCRIPTS CREATED" || echo "❌ MISSING SCRIPTS"

# Phase 3: Reports generated
ls cleanup_reports/*.{json,ps1,md} | wc -l | grep -q "6" && \
echo "✅ ALL REPORTS GENERATED" || echo "❌ MISSING REPORTS"

# Phase 4: Validation passes
python scripts/validate_archival_safety.py --mode pre-archive && \
echo "✅ PRE-ARCHIVE SAFE" || echo "❌ BLOCKERS FOUND"

# Phase 5: Tests pass
pytest -q tests/ && \
echo "✅ TESTS PASS" || echo "❌ TESTS FAIL"
```

---

## Risk Mitigation

### Safety Mechanisms

1. **Conservative Threshold (90%+)** - Only archive overwhelming evidence
2. **Multi-Signal Convergence** - Require 3+ signals at 80+ for high confidence
3. **Dry-Run Mode** - All scripts default to `$DryRun = $true`
4. **Validation Gates** - Pre/post-archive blocking checks
5. **Git Preservation** - Files moved (not deleted), full history intact
6. **Tiered Approach** - Process Tier 1 first, validate, then decide on Tier 2

### Rollback Procedure

```bash
# Option 1: Git revert
git revert HEAD

# Option 2: Restore from archive
python scripts/restore_from_archive.py \
  --archive-id 2025-12-02_143022_python-code-cleanup
```

---

## Integration with Existing Patterns

| Pattern | Role | Integration Point |
|---------|------|-------------------|
| EXEC-013 | Dependency Mapper | Import graph analysis for isolation scoring |
| EXEC-014 | Duplicate Eliminator | Duplication signal (25% weight) |
| EXEC-015 | Stale File Archiver | Staleness signal (15% weight) |

---

## Time Estimate

- Phase 1 (Enhance analyzer): **6-8 hours**
  - Entry point reachability: 2-3 hours
  - Test coverage analysis: 2-3 hours
  - Modify main analyzer: 2 hours

- Phase 2 (Parallel impl detector): **3-4 hours**

- Phase 3 (Master orchestrator): **2-3 hours**

- Phase 4 (Validation): **2-3 hours**

- Phase 5 (Execution & Review): **1-2 hours**

**Total Effort**: 14-20 hours implementation + 1-2 hours execution

---

## Next Steps After Approval

1. Create `scripts/entry_point_reachability.py`
2. Create `scripts/test_coverage_archival.py`
3. Modify `scripts/analyze_cleanup_candidates.py`
4. Create `scripts/detect_parallel_implementations.py`
5. Create `scripts/comprehensive_archival_analyzer.py`
6. Create `scripts/validate_archival_safety.py`
7. Run comprehensive analysis
8. Review parallel implementation decisions
9. Execute Tier 1 archival with validation
10. Commit results

---

## Anti-Pattern Guards

### Enabled Guards (from EXECUTION_PATTERNS_MANDATORY.md)

1. ✅ **Hallucination of Success** - Require exit code verification
2. ✅ **Planning Loop Trap** - Max 2 planning iterations
3. ✅ **Incomplete Implementation** - No TODO/pass placeholders
4. ✅ **Silent Failures** - Explicit error handling required
5. ✅ **Approval Loop** - No human approval for 90%+ confidence

### Decision Elimination

**Structural decisions (made once, apply N times):**
- ✅ Format: Python scripts + JSON/PowerShell outputs
- ✅ Verification: File exists + exit code == 0
- ✅ Completion: All 6 signals implemented + reports generated

---

**Pattern Status**: Ready for Implementation  
**Confidence**: 90% (Conservative - Safe for execution)  
**Pattern Authors**: Based on Code Cleanup Analysis + Existing EXEC-013/014/015  
**Last Updated**: 2025-12-02
