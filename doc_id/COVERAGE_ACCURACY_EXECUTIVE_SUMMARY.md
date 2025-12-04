# Doc ID Coverage & Registry Accuracy - Executive Summary

**Generated**: 2025-12-04
**Status**: ⚠️ **REGISTRY OUT OF SYNC**

---

## Key Findings

### 1. Coverage Statistics ✅
- **Total files scanned**: 2,233
- **Files with doc_ids**: 1,307 (58.5%)
- **Unique doc_ids**: 1,154
- **Files without doc_ids**: 685 (30.7%)
- **Invalid format doc_ids**: 241 (10.8%)

### 2. Critical Issue: Duplicate doc_ids ❌
**Found 81 duplicate doc_ids across 153 files**

Top duplicates:
- `DOC-PAT-ATOMIC-CREATE-TEMPLATE-001`: **9 files** ❌
- `DOC-PAT-BATCH-FILE-CREATION-001`: **8 files** ❌
- `DOC-PAT-CREATE-TEST-COMMIT-001`: **8 files** ❌
- `DOC-PAT-VIEW-EDIT-VERIFY-003`: **8 files** ❌
- `DOC-BATCH-CREATE-001`: 4 files
- `DOC-MODULE-CREATION-001`: 4 files
- Many more with 2-3 duplicates each

**Impact**: 1,307 files share only 1,154 unique IDs = **153 duplicate assignments**

### 3. Registry Accuracy: 0.09% ❌
- **Registry entries**: 1 (test entry only)
- **Actual doc_ids in files**: 1,154 unique IDs
- **Accuracy**: 1/1154 = **0.09%**
- **Missing from registry**: 1,153 doc_ids (99.91%)

---

## Data Quality Issues

### Issue 1: Massive Duplication (153 files)
**81 doc_ids are assigned to multiple files**, violating uniqueness requirement.

**Most duplicated patterns** (8-9 files each):
```
DOC-PAT-ATOMIC-CREATE-TEMPLATE-001    (9 files)
DOC-PAT-BATCH-FILE-CREATION-001       (8 files)
DOC-PAT-CREATE-TEST-COMMIT-001        (8 files)
DOC-PAT-DECISION-ELIMINATION-BOOTSTRAP-001 (8 files)
DOC-PAT-GREP-VIEW-EDIT-002            (8 files)
DOC-PAT-MODULE-CREATION-CONVERGENCE-001 (8 files)
DOC-PAT-PREFLIGHT-VERIFY-001          (8 files)
DOC-PAT-PYTEST-GREEN-VERIFY-002       (8 files)
DOC-PAT-VIEW-EDIT-VERIFY-003          (8 files)
```

**Root cause**: Pattern files copied across multiple locations without renumbering.

### Issue 2: Invalid Format (241 files)
Scanner expects: `DOC-CATEGORY-NAME-###` (exactly 3 digits)

**Common invalid patterns**:
- 4-digit IDs: `DOC-GUIDE-CLAUDE-1095` (should be `095`)
- Dates: `DOC-SCRIPT-STATUS-TRACKER-2025-12-02`
- Missing suffix: `DOC-GUIDE-DOC-ID-SYSTEM-BUG-ANALYSIS`
- Incomplete: `DOC-TEST-` (truncated)

### Issue 3: Registry Completely Empty
- Only 1 test entry in registry
- 1,153 production doc_ids **completely untracked**
- No collision detection possible
- Auto-assigner will generate duplicates

---

## Impact Assessment

### High Risk ⚠️
1. **No collision detection** - Registry doesn't know existing IDs
2. **Auto-assigner will create duplicates** - Starts at 001 in each category
3. **No audit trail** - Can't track who assigned what, when
4. **No artifact linking** - Can't find which files use which IDs

### Medium Risk ⚠️
1. **Invalid IDs** - 241 files with non-conformant format
2. **Documentation drift** - Files and registry out of sync
3. **No validation** - Can't verify integrity

### Low Risk ℹ️
1. Coverage is reasonable (58.5%) for initial state
2. Python/YAML have excellent coverage (>89%)
3. Infrastructure is functional (scanner, assigner, registry CLI work)

---

## Required Actions

### CRITICAL: Fix Duplicates (Priority 0)
**Before importing to registry**, resolve 153 duplicate assignments:

```bash
# Find all duplicates
python -c "
import json
from collections import Counter
entries = [json.loads(line) for line in open('docs_inventory.jsonl', encoding='utf-8')]
ids = [e['doc_id'] for e in entries if e['status'] == 'registered']
dupes = {k:v for k,v in Counter(ids).items() if v > 1}
for doc_id, count in sorted(dupes.items(), key=lambda x: -x[1])[:20]:
    print(f'{doc_id}: {count} files')
" 2>&1
```

**Resolution strategy**:
1. Keep ONE canonical assignment per doc_id
2. Renumber duplicates with new IDs
3. Update files with new IDs

### Priority 1: Import Existing IDs to Registry
After deduplication, populate registry:

```python
# Create: doc_id/tools/import_from_inventory.py
def import_to_registry():
    inventory = load_inventory()
    registry = DocIDRegistry()

    for entry in inventory:
        if entry['status'] == 'registered':
            # Parse and add to registry
            registry.add_from_inventory(entry)

    registry.save()
```

### Priority 2: Fix Invalid Format (241 files)
Options:
1. **Relax regex** - Accept 1+ digits instead of exactly 3
2. **Renumber** - Update files to conform to 3-digit format
3. **Register as-is** - Document exceptions

### Priority 3: Enable Continuous Sync
Add validation to CI/CD:
```yaml
# .github/workflows/doc_id_validation.yml
- name: Validate doc_id sync
  run: |
    python doc_id/doc_id_scanner.py scan
    python doc_id/tools/validate_registry_sync.py
```

---

## Coverage Analysis by File Type

### Excellent Coverage (>80%) ✅
| Type | Coverage | Files |
|------|----------|-------|
| YAML | 91.9% | 193/210 |
| Python | 89.3% | 533/597 |

### Good Coverage (60-80%) ✅
| Type | Coverage | Files |
|------|----------|-------|
| JSON | 73.1% | 234/320 |
| PowerShell | 65.7% | 138/210 |

### Needs Improvement (<60%) ⚠️
| Type | Coverage | Files |
|------|----------|-------|
| Text | 42.9% | 15/35 |
| YAML (yml) | 40.0% | 2/5 |
| Shell | 33.3% | 10/30 |
| **Markdown** | **22.0%** | **182/826** |

**Biggest gap**: Markdown (only 22% coverage, 644 files missing IDs)

---

## Recommended Workflow

### Phase 1: Data Cleanup (1-2 hours)
1. ✅ Identify all 153 duplicate file assignments
2. ✅ Decide canonical file for each duplicated ID
3. ✅ Renumber non-canonical files (mint new IDs)
4. ✅ Update file headers with new IDs

### Phase 2: Registry Population (30 minutes)
1. ✅ Create import script
2. ✅ Import 1,154 unique IDs to registry
3. ✅ Link each ID to its file artifacts
4. ✅ Validate no duplicates in registry

### Phase 3: Format Fixes (1 hour)
1. ✅ Decide on format: strict 3-digit or relaxed 1+ digit
2. ✅ Update scanner regex if relaxing
3. ✅ Fix or register 241 invalid IDs
4. ✅ Rescan to verify

### Phase 4: Coverage Improvement (ongoing)
1. Auto-assign to 644 markdown files
2. Auto-assign to remaining 685 files
3. Target: 90%+ coverage

---

## Success Metrics

### Current State
- Registry accuracy: **0.09%** ❌
- Coverage: **58.5%** ⚠️
- Duplicates: **81 IDs, 153 files** ❌
- Invalid IDs: **241 files** ❌

### After Cleanup (Phase 1-2)
- Registry accuracy: **100%** ✅
- Coverage: **58.5%** (unchanged)
- Duplicates: **0** ✅
- Invalid IDs: **241** (deferred) or **0** (if fixed)

### After Full Implementation (Phase 3-4)
- Registry accuracy: **100%** ✅
- Coverage: **90%+** ✅
- Duplicates: **0** ✅
- Invalid IDs: **0** ✅

---

## Bottom Line

### What's Working ✅
- Scanner finds doc_ids accurately
- 58.5% coverage is reasonable starting point
- Python/YAML have excellent coverage
- Infrastructure is functional

### What's Broken ❌
- **Registry is empty** (0.09% accuracy)
- **81 duplicate doc_ids** across 153 files
- **241 files with invalid format**
- **No sync between files and registry**

### What's Needed 🔧
1. **Deduplicate** 153 file assignments
2. **Import** 1,154 unique IDs to registry
3. **Fix** 241 invalid format IDs
4. **Sync** validation in CI/CD

**Time estimate**: 2-3 hours for Phases 1-3, ongoing for Phase 4

---

**Recommendation**: Do NOT use auto-assigner until duplicates are resolved and registry is populated. Risk of creating more duplicates is high.
