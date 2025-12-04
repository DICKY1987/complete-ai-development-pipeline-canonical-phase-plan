---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-DOC-FOLDER-VERSION-SCORING-SPEC-789
---

# Folder Version Scoring Specification

**Version**: 2.0
**Date**: 2025-11-25
**Status**: CANONICAL

---

## Purpose

Define explicit, deterministic rules for scoring folder versions to identify:
1. Which folder is **canonical** (KEEP)
2. Which folders are **outdated** (DELETE/ARCHIVE)
3. Which folders need **manual review** (REVIEW)

---

## Core Principle

**Score is necessary but NOT sufficient for deletion.**
A folder can only be deleted if:
- Low score AND
- Zero active usage AND
- Not in governance system

---

## 1. Similarity Metrics (Prerequisite)

Before scoring, compute **exact similarity percentages**:

### 1.1 Content Similarity (Hash-Based)
```
content_similarity = (shared_file_hashes / union_file_hashes) × 100
```

**Interpretation**:
- `≥ 90%` → Same content family (versions of each other)
- `80-89%` → Closely related (partial refactor/evolution)
- `50-79%` → Related but diverged
- `< 50%` → Different purposes (same name by coincidence)

### 1.2 Strict Similarity (Name + Hash Match)
```
strict_similarity = (matched_filename_hashes / max(files_A, files_B)) × 100
```

Only count files where **both filename AND hash match**.

**Interpretation**:
- `≥ 95%` → Exact copy (possibly relocated/renamed folder)
- `90-94%` → Near-exact with minor edits
- `< 90%` → Significant differences

### 1.3 When to Apply Similarity
- Only compare folders when `content_similarity ≥ 50%`
- Otherwise treat as "different purposes" → both KEEP

---

## 2. Six-Factor Scoring System (0-100 points)

### Factor 1: Content (0-25 points)

**Definition**: File completeness relative to sibling folders with same name.

**Scoring**:
```
content_score = (file_count / max_file_count_in_group) × 25
```

**Example**:
- `core/engine/` has 27 files (max) → 25 points
- `engine/` has 5 files → (5/27) × 25 = 4.6 ≈ 5 points

---

### Factor 2: Recency (0-20 points)

**Definition**: How recently the folder was modified (maintenance signal).

**Scoring**:
```python
newest_in_group = max(newest_file_date for all folders)
age_months = (newest_in_group - this_folder.newest_file_date).days / 30

recency_score = max(0, 20 - age_months)  # Lose 1 point per month
```

**Decay Cap**:
- If **no changes in > 12 months**, cap at 5 points even if still "newer" than others
- Rationale: Unmaintained code shouldn't win on recency alone

---

### Factor 3: Completeness (0-15 points)

**Definition**: Markers of being a "real module" vs. abandoned fragment.

**Scoring** (additive):
- Has `README.md` or `readme.md`: **+5**
- Has `__init__.py` (Python) or module entrypoint: **+5**
- Has pattern spec/schema/executor (repo-specific): **+3**
- Has tests in `tests/<folder_name>/`: **+2**

**Maximum**: 15 points

---

### Factor 4: History (0-15 points)

**Definition**: Which folder is the "original" vs. later copy.

**Scoring**:
```python
earliest_creation = min(git_created_date for all folders)

if git_created_date == earliest_creation:
    history_score = 15  # Original
else:
    months_after = (git_created_date - earliest_creation).days / 30
    history_score = max(0, 15 - months_after)  # Lose 1 point per month delay
```

**Tie-Breaker**:
- If `strict_similarity ≥ 80%` AND newer folder has **more files**, treat newer as "evolved original"
- Subtract 5 points from older folder's history score

**Commit Count Bonus** (max +3):
- Add `min(3, commit_count / 10)` to history score

---

### Factor 5: Usage (0-15 points)

**Definition**: Is this folder actively referenced by the system?

**MUST check ALL of these** (not just Python imports):

#### 5.1 Python Imports (0-8 points)
```python
if is_imported:
    usage_score += 8
```

#### 5.2 Broader Usage Signals (0-7 points)
Check for references in:
- **PowerShell scripts**: `.\path\to\folder` or `Import-Module`
- **YAML/TOML configs**: Pattern executors, workflow definitions
- **Pattern registry**: `patterns/registry/*.yaml`
- **DOC_ID registry**: `doc_id/DOC_ID_REGISTRY.yaml`
- **CODEBASE_INDEX.yaml**: Listed as canonical module
- **Tests**: Referenced in `tests/` directory

**Scoring**:
```python
reference_count = count_all_reference_types()
usage_score = min(7, reference_count)  # Cap at 7
```

**Total**: 8 (imports) + 7 (other) = 15 points max

---

### Factor 6: Location (0-10 points)

**Definition**: Blessed locations score higher (repo-specific hierarchy).

**Tier System** for this repository:

#### Tier 1 (10 points): Canonical Locations
- `core/`
- `engine/`
- `error/`
- `scripts/`
- `pm/`
- `specifications/`
- `docs/`
- `.claude/`

#### Tier 2 (7 points): Module Libraries
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/`
- `aim/`
- `tools/`
- `glossary/`

#### Tier 3 (4 points): Experimental/Utilities
- `examples/`
- `developer/`
- `infra/`

#### Tier 4 (0 points): Graveyards
- `legacy/`
- `archive/`
- `old/`
- `tmp/`
- `backup/`
- Any path containing `deprecated`, `_old`, `.bak`

**Scoring**:
```python
for tier, score in tiers:
    if folder_path.startswith(tier):
        location_score = score
        break
```

---

## 3. Total Score Calculation

```python
total_score = (
    content_score +      # 0-25
    recency_score +      # 0-20
    completeness_score + # 0-15
    history_score +      # 0-15
    usage_score +        # 0-15
    location_score       # 0-10
)  # Maximum: 100 points
```

---

## 4. Verdict Bands (with HARD Guardrails)

### 4.1 KEEP (Score ≥ 80)

**Automatic KEEP if ANY of**:
- Score ≥ 80
- `usage_score > 0` (actively referenced)
- In Tier 1 location
- Listed in `CODEBASE_INDEX.yaml`
- Has `doc_id` in `DOC_ID_REGISTRY.yaml`

**Action**: No changes

---

### 4.2 REVIEW (Score 50-79)

**Manual review required**

**Possible actions**:
- **CONSOLIDATE**: Merge with canonical version
- **RENAME**: Clarify purpose (e.g., `engine/` → `job_engine/`)
- **MOVE**: Relocate to better location
- **ARCHIVE**: Move to `archive/` with date stamp

**Do NOT auto-delete**

---

### 4.3 DELETE-CANDIDATE (Score < 50)

**MUST meet ALL these conditions** for deletion:

```python
can_delete = (
    total_score < 50 AND
    usage_score == 0 AND  # Zero references
    not in_pattern_registry AND
    not has_doc_id AND
    not has_doc_link AND
    location_score == 0  # In graveyard location
)
```

**If `can_delete == True`**:
- Add to deletion queue
- Generate `git rm -r` command
- Log in `docs/DOC_CLEANUP_LOG.md`

**If `can_delete == False`**:
- Move to REVIEW queue despite low score

---

## 5. Special Cases

### 5.1 Folders with Same Name, Different Purposes

**Example**: `engine/` (job system) vs `core/engine/` (orchestrator)

**Detection**:
- `content_similarity < 50%`
- Different file types (`.py` vs `.ps1` vs `.md`)

**Action**: Both KEEP with verdict `DIFFERENT_PURPOSE`

---

### 5.2 Exact Copies (Relocated Folders)

**Detection**:
- `strict_similarity ≥ 95%`
- One folder created later in git history

**Action**:
- KEEP: Higher-scoring folder (usually newer location)
- DELETE: Lower-scoring folder (usually old location)
- Document as "relocated" in cleanup log

---

### 5.3 Evolved Versions

**Detection**:
- `content_similarity 80-90%`
- Newer folder has **more files** or **higher usage_score**

**Action**:
- KEEP: Evolved version (newer, more complete)
- ARCHIVE: Original version (move to `archive/<year>/`)

---

## 6. File-Level Scoring (Extension)

Apply same 6-factor system to **individual files** within a folder:

### When to Use File-Level Scoring:
- Multiple versions of same script (e.g., `deploy.py`, `deploy_v2.py`, `deploy_old.py`)
- Duplicate files across folders

### Adaptations:
- **Content**: Lines of code vs. other versions
- **Recency**: Last commit touching the file
- **Completeness**: Docstring, arg parsing, logging
- **History**: First appearance in git
- **Usage**: Direct imports/executions
- **Location**: Same tier system

---

## 7. Integration with Governance Systems

### 7.1 DOC_ID System Override
If a file/folder has a `doc_id`:
- Minimum score = 60 (moves to REVIEW tier)
- Cannot be auto-deleted
- Must update registry if consolidated/moved

### 7.2 Pattern Registry Override
If referenced in `patterns/registry/*.yaml`:
- Minimum score = 70
- Usage score = 15 (maximum)

### 7.3 CODEBASE_INDEX.yaml Override
If listed as canonical module:
- Minimum score = 85 (automatic KEEP)
- Location score = 10 (maximum)

---

## 8. Execution Flow

```
1. Scan repository
   ↓
2. Group folders by normalized name
   ↓
3. For each group:
   a. Compute similarity metrics
   b. If content_similarity < 50% → Mark DIFFERENT_PURPOSE, skip scoring
   c. Else: Score all 6 factors
   d. Apply guardrails
   e. Assign verdict
   ↓
4. Generate reports:
   - DELETE candidates (score < 50 + all guardrails pass)
   - REVIEW candidates (50-79 or failed guardrails)
   - KEEP (80+ or overrides)
   ↓
5. Human review DELETE + REVIEW queues
   ↓
6. Execute approved deletions
   ↓
7. Log in DOC_CLEANUP_LOG.md
```

---

## 9. Examples

### Example 1: `core/engine/` vs `engine/`

| Metric | core/engine/ | engine/ |
|--------|-------------|---------|
| Content | 25 (27 files) | 5 (5 files) |
| Recency | 20 (recent) | 20 (recent) |
| Completeness | 15 (README, __init__) | 6 (no README) |
| History | 15 (original) | 10 (2 months later) |
| Usage | 15 (heavily imported) | 14 (imported) |
| Location | 10 (Tier 1) | 10 (Tier 1) |
| **TOTAL** | **100** | **65** |
| **Verdict** | **KEEP** | **REVIEW** |

**Recommendation**: Both serve different purposes (similarity: 35%). Keep both.

---

### Example 2: `pm/scripts/` vs `scripts/`

| Metric | scripts/ | pm/scripts/ |
|--------|----------|-------------|
| Content | 25 (65 files) | 2 (4 files) |
| Recency | 20 | 20 |
| Completeness | 13 (README) | 0 (no README) |
| History | 15 (original) | 12 |
| Usage | 15 (imported) | 0 (never used) |
| Location | 10 (Tier 1) | 7 (Tier 1/pm) |
| **TOTAL** | **98** | **41** |
| **Verdict** | **KEEP** | **DELETE** |

**Guardrail Check**:
- Score: 41 < 50 ✓
- Usage: 0 ✓
- Not in registry ✓
- Not in CODEBASE_INDEX ✓
- Not in graveyard (so location = 7, not 0) ✗

**Final Verdict**: REVIEW (failed guardrail, needs manual check)

---

## 10. Validation & Testing

### 10.1 Test Cases
Create test scenarios:
- Exact copies (should detect with strict_similarity ≥ 95%)
- Evolved versions (similarity 80-90%, newer has more files)
- Different purposes (similarity < 50%)
- Graveyard folders (location_score = 0, should delete if unused)

### 10.2 Dry-Run Mode
Always run with `--dry-run` first:
- Generate deletion candidates
- Show scores and reasons
- Require manual approval before executing

---

## 11. Future Enhancements

1. **Machine learning**: Train on past cleanup decisions
2. **Cross-repo analysis**: Detect patterns across multiple repos
3. **Automated migration**: Generate git commands to consolidate folders
4. **Dashboard**: Visual scoring interface for review queue

---

## Appendix A: Formulas Quick Reference

```python
# Similarity
content_similarity = (shared_hashes / union_hashes) × 100
strict_similarity = (matched_filename_hashes / max(files_A, files_B)) × 100

# Scoring
content_score = (file_count / max_in_group) × 25
recency_score = max(0, 20 - age_months)
completeness_score = sum(markers) up to 15
history_score = 15 if original else max(0, 15 - months_after_original)
usage_score = 8 (if imported) + min(7, reference_count)
location_score = tier_value (0, 4, 7, or 10)

# Guardrails
can_delete = (
    total_score < 50 AND
    usage_score == 0 AND
    not in_registry AND
    not has_doc_id AND
    location_score == 0
)
```

---

**END OF SPECIFICATION**

_This is a living document. Update as scoring rules evolve._
