---
title: Next Session Quick Start Guide
status: active
doc_id: DOC-DOCID-NEXT-SESSION-QUICKSTART-001
---

# Next Session Quick Start Guide

## Current State

**Branch**: `feature/docid-phase0-82pct-coverage`  
**Coverage**: 82.0% (2,407/2,935 files)  
**Remaining**: 528 files need doc_ids

## Quick Start (5 Minutes)

```powershell
# 1. Checkout the feature branch
git checkout feature/docid-phase0-82pct-coverage

# 2. Check current coverage
cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"
python scripts/doc_id_scanner.py stats

# 3. Review session summary
code doc_id/SESSION_COMPLETION_SUMMARY.md
code doc_id/PHASE_0_STATUS_REPORT.md
```

## Critical Issues to Fix First

### Issue 1: JSON Injection Not Working ⚠️
**File**: `scripts/doc_id_assigner.py`  
**Problem**: JSON files need doc_id as a top-level field, not a comment  
**Current**:
```json
/* DOC_ID: DOC-GUIDE-INDEX-001 */
{
  "data": "value"
}
```
**Should be**:
```json
{
  "doc_id": "DOC-GUIDE-INDEX-001",
  "data": "value"
}
```

**Fix Location**: Function `inject_doc_id()` around line 300

### Issue 2: Duplicate Doc_IDs ⚠️
**Example**: `docs/index.json` has 5 duplicate doc_ids  
**Fix**: Add check before injection:
```python
def inject_doc_id(file_path, doc_id, file_type):
    content = read_file(file_path)
    
    # NEW: Check if doc_id already exists
    if doc_id in content or "DOC_ID:" in content:
        return False, "File already has a doc_id"
    
    # ... rest of injection logic
```

### Issue 3: Markdown Injection Silent Failure ⚠️
**Problem**: 343 files "assigned" but coverage didn't improve  
**Investigation**: Check if frontmatter injection is working correctly

## Step-by-Step Fix Plan

### Step 1: Fix JSON Injection (30 mins)

```python
# In scripts/doc_id_assigner.py

def inject_doc_id_json(file_path, doc_id):
    """Inject doc_id as top-level field in JSON files."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add doc_id as first field
        data = {"doc_id": doc_id, **data}
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True, "Injected doc_id as top-level field"
    except Exception as e:
        return False, f"JSON injection failed: {e}"
```

### Step 2: Add Duplicate Detection (15 mins)

```python
def has_existing_docid(file_path, file_type):
    """Check if file already has a doc_id."""
    try:
        content = Path(file_path).read_text(encoding='utf-8', errors='ignore')
        
        # Check for various doc_id patterns
        patterns = [
            r'DOC_ID:\s*DOC-',
            r'doc_id:\s*DOC-',
            r'"doc_id":\s*"DOC-',
            r'doc_id\s*=\s*["\']DOC-'
        ]
        
        for pattern in patterns:
            if re.search(pattern, content):
                return True
        
        return False
    except Exception:
        return False

# In inject_doc_id():
if has_existing_docid(file_path, file_type):
    return False, "File already has a doc_id"
```

### Step 3: Clean Up Duplicates (15 mins)

```powershell
# Find files with duplicate doc_ids
Get-ChildItem -Recurse -Include *.json,*.md,*.py | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $matches = [regex]::Matches($content, 'DOC_ID:\s*(DOC-[A-Z0-9-]+)')
    if ($matches.Count -gt 1) {
        Write-Host "Duplicate in: $($_.FullName)" -ForegroundColor Yellow
        Write-Host "  IDs: $($matches.Value -join ', ')" -ForegroundColor Red
    }
}
```

### Step 4: Test Fixes (15 mins)

```bash
# Test JSON injection
python scripts/doc_id_assigner.py auto-assign --types json --limit 5 --dry-run

# Test duplicate detection
python scripts/doc_id_assigner.py auto-assign --types md --limit 5 --dry-run

# Verify one file manually
code docs/index.json
```

### Step 5: Complete Assignment (30 mins)

```bash
# Assign remaining files in batches
python scripts/doc_id_assigner.py auto-assign --types json --limit 100
python scripts/doc_id_assigner.py auto-assign --types md --limit 350
python scripts/doc_id_assigner.py auto-assign --types sh --limit 20
python scripts/doc_id_assigner.py auto-assign --types yaml yml --limit 50
python scripts/doc_id_assigner.py auto-assign --types txt ps1 py --limit 30

# Verify 100% coverage
python scripts/doc_id_scanner.py scan --output doc_id/reports/docs_inventory.jsonl
python scripts/doc_id_scanner.py stats
```

### Step 6: Validate & Commit (15 mins)

```bash
# Run preflight checks
python scripts/doc_id_preflight.py --min-coverage 1.0

# Validate registry
python doc_id/tools/doc_id_registry_cli.py validate

# Commit
git add -A
git commit -m "fix(doc_id): Achieve 100% coverage - Phase 0 complete

- Fixed JSON injection (top-level field)
- Fixed Markdown injection
- Added duplicate detection
- Cleaned up existing duplicates
- Assigned remaining 528 files
- Coverage: 100% (2,935/2,935 files)
"

# Merge to main
git checkout main
git merge feature/docid-phase0-82pct-coverage
```

## Remaining Files by Type

- **344 Markdown** - Need frontmatter injection verification
- **100 JSON** - Need field injection (not comments)
- **41 YAML** - Should be straightforward
- **17 Shell** - Need shebang + comment injection
- **13 Text** - Need header comment injection
- **9 PowerShell** - Need header comment injection
- **2 Python** - Should be straightforward
- **2 YML** - Should be straightforward

## Expected Timeline

| Task | Time | Description |
|------|------|-------------|
| Fix JSON injection | 30 min | Update inject_doc_id() for JSON |
| Add duplicate detection | 15 min | Prevent re-injection |
| Clean duplicates | 15 min | Remove existing duplicates |
| Test fixes | 15 min | Verify on sample files |
| Assign remaining | 30 min | Batch assignment of 528 files |
| Validate & commit | 15 min | Preflight + registry validation |
| **Total** | **2 hours** | **100% coverage achieved** |

## Success Criteria

- ✅ JSON files have `"doc_id": "DOC-..."` as top-level field
- ✅ No duplicate doc_ids in any file
- ✅ Coverage: 100% (2,935/2,935 files)
- ✅ Preflight passes with `--min-coverage 1.0`
- ✅ Registry validates successfully
- ✅ All changes committed and merged to main

## Files to Modify

1. `scripts/doc_id_assigner.py` - Fix injection logic
2. Files with duplicates (find with grep)
3. Registry if needed (cleanup duplicates)

## Commands Cheat Sheet

```bash
# Check status
python scripts/doc_id_scanner.py stats

# Dry-run assignment
python scripts/doc_id_assigner.py auto-assign --types json --limit 10 --dry-run

# Real assignment
python scripts/doc_id_assigner.py auto-assign --types json md yaml sh txt ps1 yml py

# Find duplicates
grep -r "DOC_ID:" --include="*.json" | grep -E "(DOC_ID.*){2,}"

# Validate
python scripts/doc_id_preflight.py --min-coverage 1.0
python doc_id/tools/doc_id_registry_cli.py validate
```

## Reference Documents

- `doc_id/SESSION_COMPLETION_SUMMARY.md` - Full session summary
- `doc_id/PHASE_0_STATUS_REPORT.md` - Detailed status report
- `doc_id/COMPLETE_PHASE_PLAN.md` - Full 6-phase plan
- `scripts/doc_id_assigner.py` - Tool to modify
- `doc_id/specs/DOC_ID_REGISTRY.yaml` - Registry (2,000+ entries)

## After 100% Coverage

Proceed to **Phase 1.5: MODULE_ID Extension**:
1. Review `doc_id/MODULE_ID_INTEGRATION_PLAN.md`
2. Create `module_map.yaml`
3. Link doc_ids to module_ids
4. Update registry with module references

---

**Ready to complete Phase 0 in ~2 hours!** 🚀
