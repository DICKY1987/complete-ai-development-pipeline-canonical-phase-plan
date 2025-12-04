# Doc ID Coverage & Registry Accuracy Report

**Generated**: 2025-12-04 04:26:00 UTC
**Inventory File**: `docs_inventory.jsonl`
**Registry File**: `doc_id/DOC_ID_REGISTRY.yaml`

---

## Executive Summary

### Critical Finding: Registry vs. File Discrepancy ⚠️

- **Files with doc_ids**: 1,307 files (58.5% of 2,233 eligible files)
- **IDs in registry**: 1 entry (test entry only)
- **Discrepancy**: **1,306 doc_ids exist in files but are NOT in the central registry**

**Root Cause**: The system has two separate doc_id sources:
1. **Embedded doc_ids** - IDs written directly in file headers/frontmatter (1,307 files)
2. **Registry entries** - IDs tracked in `DOC_ID_REGISTRY.yaml` (1 entry)

**These are NOT synchronized!**

---

## Coverage Breakdown

### Overall Statistics
| Metric | Count | Percentage |
|--------|-------|------------|
| **Total eligible files** | 2,233 | 100% |
| **Files with valid doc_id** | 1,307 | 58.5% |
| **Files with invalid doc_id** | 241 | 10.8% |
| **Files without doc_id** | 685 | 30.7% |

### Coverage by File Type
| Type | With doc_id | Total | Coverage |
|------|-------------|-------|----------|
| YAML | 193 | 210 | 91.9% ✅ |
| Python | 533 | 597 | 89.3% ✅ |
| JSON | 234 | 320 | 73.1% ✅ |
| PowerShell | 138 | 210 | 65.7% ✅ |
| Text | 15 | 35 | 42.9% ⚠️ |
| YAML (yml) | 2 | 5 | 40.0% ⚠️ |
| Shell | 10 | 30 | 33.3% ⚠️ |
| Markdown | 182 | 826 | 22.0% ⚠️ |

---

## Invalid doc_ids Analysis (241 files)

### Invalid Format Patterns

The scanner validates against this regex:
```regex
^DOC-[A-Z0-9]+-[A-Z0-9]+(-[A-Z0-9]+)*-[0-9]{3}$
```

**Expected format**: `DOC-CATEGORY-NAME-###` (exactly 3 digits)

### Common Invalid Formats Found

#### 1. Four-digit sequences (most common)
```
DOC-GUIDE-CLAUDE-1095                    # Expected: DOC-GUIDE-CLAUDE-095
DOC-GUIDE-README-1096                    # Expected: DOC-GUIDE-README-096
DOC-GUIDE-UET-ABSTRACTION-GUIDELINES-1002
```
**Issue**: 4 digits instead of 3

#### 2. Date-based suffixes
```
DOC-SCRIPT-EXECUTE-NEXT-WORKSTREAMS-2025-12-02
DOC-SCRIPT-STATUS-TRACKER-2025-12-02
```
**Issue**: Date format instead of numeric ID

#### 3. Missing number suffix
```
DOC-GUIDE-DOC-ID-SYSTEM-BUG-ANALYSIS  # Missing -XXX
DOC-TEST-                              # Truncated/incomplete
```
**Issue**: No trailing digits

#### 4. Non-standard delimiters or characters
```
DOC-GUIDE-SESSION-TRANSCRIPT-PH-011-1625  # Mixed format
```

### Recommendation: Relax Regex
Many "invalid" IDs are actually usable, just not 3-digit format. Consider:
```regex
^DOC-[A-Z0-9]+-[A-Z0-9]+(-[A-Z0-9]+)*-[0-9]+$
```
This accepts any number of digits (1+), which would validate most of the 241 "invalid" IDs.

---

## Registry Accuracy Analysis

### Current Registry State
```yaml
Total docs in registry: 1
Categories defined: 14
Last updated: 2025-12-03
```

### Sample Embedded doc_ids NOT in Registry
```
DOC-PAT-BATCH-MINT-337
DOC-CORE-CONFTEST-317
DOC-CORE-CORE-UI-CLI-127
DOC-CORE-CORE-UI-MODELS-128
DOC-SCRIPT-SCRIPTS-DOC-ID-ASSIGNER-204
DOC-SCRIPT-DOC-ID-SCANNER-046
DOC-TEST-PATTERNS-TEST-DOC-ID-COMPLIANCE-184
DOC-PAT-WRITE-DOC-IDS-TO-FILES-349
DOC-GUI-VALIDATION-600
DOC-PAT-PATTERNS-VALIDATE-AUTOMATION-655
```

**All 1,307 doc_ids** found by the scanner exist **only in file headers**, not in the central registry.

---

## System Architecture Issue

### Two Parallel ID Systems

#### System 1: Embedded doc_ids (Current State)
- **Location**: File headers (`DOC_LINK:` comments, YAML frontmatter)
- **Count**: 1,307 files
- **Management**: Manual assignment
- **Validation**: Scanner checks format only
- **No central tracking**

#### System 2: Registry-based (Intended Design)
- **Location**: `doc_id/DOC_ID_REGISTRY.yaml`
- **Count**: 1 entry (fresh registry)
- **Management**: CLI tools (`mint`, `assign`, `validate`)
- **Validation**: Registry tracks all assignments
- **Central tracking**: Yes

### The Problem
These systems are **not synchronized**. When you:
1. Scan → Finds 1,307 IDs in files
2. Check registry → Shows only 1 entry
3. Validate → Registry says "all valid" (because it only knows about 1 ID)

---

## Data Integrity Issues

### Issue 1: No Collision Detection
Without registry tracking, duplicate doc_ids could exist:
```bash
# Are there duplicates among the 1,307 IDs?
# Unknown - registry isn't tracking them
```

### Issue 2: No Assignment Tracking
Registry doesn't know:
- Which files use which doc_ids
- When IDs were assigned
- Who assigned them
- What the next available ID is per category

### Issue 3: Auto-Assigner Risk
The auto-assigner will:
- Generate new doc_ids starting from 001 in each category
- Potentially create **duplicates** of existing embedded IDs
- No collision detection since registry is empty

---

## Recommended Actions

### Priority 1: Populate Registry from Existing IDs (CRITICAL)
Create a migration script to:
1. Read all 1,307 embedded doc_ids from files
2. Parse and validate each one
3. Add valid ones to registry with artifact paths
4. Report any duplicates found
5. Fix invalid formats (241 files)

**Command**:
```bash
# Theoretical command - needs implementation
python doc_id/tools/doc_id_registry_cli.py batch-import-from-files
```

### Priority 2: Fix Invalid doc_ids (241 files)
Options:
1. **Relax regex** to accept 4-digit IDs (quick fix)
2. **Renumber** to 3-digit format (requires file updates)
3. **Document exceptions** for special cases (dates, etc.)

### Priority 3: Enable Registry Validation
Once registry is populated, add validation that checks:
- File doc_id matches registry entry
- No orphaned registry entries
- No unregistered doc_ids in files

### Priority 4: Prevent Future Drift
Add pre-commit hook or CI check:
```bash
# Ensure all doc_ids in files are in registry
python doc_id/validate_doc_id_consistency.ps1
```

---

## Migration Plan: Sync Files → Registry

### Step 1: Extract All Embedded doc_ids
```bash
python doc_id/doc_id_scanner.py scan  # Already done
```

### Step 2: Create Batch Import Script
```python
# Pseudo-code
def batch_import_from_inventory():
    inventory = load_inventory("docs_inventory.jsonl")
    registry = DocIDRegistry()

    for entry in inventory:
        if entry['status'] == 'registered':  # Valid format
            doc_id = entry['doc_id']
            path = entry['path']

            # Parse doc_id: DOC-CATEGORY-NAME-NUM
            category, name, num = parse_doc_id(doc_id)

            # Add to registry
            registry.add_existing(
                doc_id=doc_id,
                category=category,
                name=name,
                artifacts=[{"type": "source", "path": path}],
                status="active"
            )

    registry.save()
```

### Step 3: Handle Invalid IDs
```bash
# Fix 241 invalid IDs - either:
# A) Update regex to be more permissive
# B) Renumber them to conform
# C) Register as exceptions
```

### Step 4: Verify Sync
```bash
python doc_id/tools/doc_id_registry_cli.py validate
# Should now show 1,307+ entries (or 1,548 if invalid ones are fixed)
```

---

## Coverage Goals

### Current State
- **Total coverage**: 58.5% (1,307/2,233)
- **Valid format**: 58.5%
- **Invalid format**: 10.8%
- **No doc_id**: 30.7%

### Target State (After Fixes)
- **Total coverage**: 69.3% (1,548/2,233 if invalid IDs fixed)
- **Valid format**: 69.3%
- **Invalid format**: 0%
- **No doc_id**: 30.7%

### Stretch Goal
- **Total coverage**: 90%+ (auto-assign remaining 685 files)

---

## Key Metrics Summary

| Metric | Current | After Sync | After Auto-Assign |
|--------|---------|------------|-------------------|
| Registry entries | 1 | 1,307 | 2,000+ |
| Files with IDs | 1,307 | 1,548 | 2,000+ |
| Coverage % | 58.5% | 69.3% | 90%+ |
| Invalid IDs | 241 | 0 | 0 |
| Registry accuracy | 0.08% | 100% | 100% |

---

## Conclusion

### ✅ What's Working
- Scanner successfully finds doc_ids in files
- Registry CLI can mint new IDs
- Auto-assigner can generate IDs
- Format validation is implemented

### ❌ What's Broken
- **Registry is empty** (only 1 test entry)
- **1,307 doc_ids are untracked** in registry
- **241 doc_ids have invalid format** (mostly 4-digit IDs)
- **No synchronization** between files and registry
- **Duplicate detection is disabled** (registry doesn't know existing IDs)

### 🔧 What's Needed
1. **Batch import tool** to populate registry from existing file IDs
2. **Fix or relax validation** for 241 "invalid" IDs
3. **Sync validation** to ensure files ↔ registry consistency
4. **CI/CD integration** to prevent future drift

---

**Bottom Line**: The doc_id system infrastructure is solid, but the **registry is essentially empty** despite 1,307 IDs already being assigned in files. You need a **migration/sync step** before the registry can be considered accurate or authoritative.
