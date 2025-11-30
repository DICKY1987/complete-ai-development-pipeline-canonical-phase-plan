---
doc_id: DOC-GUIDE-PATH-TO-100-PERCENT-COVERAGE-1741
---

# Path to 100% Coverage - Doc ID Assignment Strategy

**Current Status**: 81.8% coverage (based on scanner stats for eligible types)  
**Actual Inventory Status**: 2,360 files still missing doc_id  
**Assignable Files**: 2,344 files (excluding git/venv/pycache)

---

## 🎯 Goal: Achieve 100% Coverage

### Strategy Overview

We have **2,344 assignable files** remaining. These are NOT in ignored directories - they're legitimate source files that the auto-assigner skipped for various reasons.

---

## 📊 Gap Analysis

### Missing Files by Type (From Inventory)
```
Markdown:     1,027 files
Python:         677 files  
JSON:           251 files
YAML:           169 files
PowerShell:     122 files
Text:            81 files
Shell:           29 files
YML:              4 files
────────────────────────
TOTAL:        2,360 files
```

### Missing Files by Directory (Top 15)
```
UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK:  516 files
modules:                                   208 files
developer:                                 162 files
archive:                                   155 files
scripts:                                   126 files
docs:                                      123 files
ToDo_Task:                                 109 files
pm:                                         99 files
tests:                                      84 files
error:                                      79 files
aim:                                        69 files
<root>:                                     53 files
workstreams:                                48 files
tools:                                      43 files
gui:                                        41 files
```

### Why Were These Skipped?

The auto-assigner likely skipped these due to:
1. **Name sanitization failures** - Special characters in paths
2. **Category inference failures** - Couldn't map to a valid category
3. **Validation failures** - Names that don't pass registry validation
4. **Silent errors** - Exceptions during processing

---

## 🛠️ Solution: 3-Phase Approach

### **Phase A: Fix Auto-Assigner Issues** (30 min)

**Goal**: Make auto-assigner handle ALL file patterns

**Tasks**:
1. Add debug logging to identify why files are skipped
2. Enhance category inference with fallback logic
3. Improve name sanitization for edge cases
4. Add special handling for:
   - `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/` → category: `pattern`
   - `modules/` → category: `core`
   - `developer/` → category: `guide`
   - `archive/` → category: `legacy` (new category)
   - `ToDo_Task/` → category: `task` (new category)
5. Re-run with enhanced logic

**Expected Result**: Reduce missing from 2,344 → ~500

---

### **Phase B: Batch Processing by Directory** (45 min)

**Goal**: Process remaining files in targeted batches

**Strategy**: Directory-based batches with explicit category mapping

```bash
# Batch 1: UET Patterns (516 files)
python scripts/doc_id_assigner.py auto-assign \
  --category pattern \
  --path-filter "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK" \
  --limit 300

# Batch 2: Modules (208 files)
python scripts/doc_id_assigner.py auto-assign \
  --category core \
  --path-filter "modules" \
  --limit 250

# Batch 3: Developer Docs (162 files)
python scripts/doc_id_assigner.py auto-assign \
  --category guide \
  --path-filter "developer" \
  --limit 200

# Batch 4: Archive (155 files)
python scripts/doc_id_assigner.py auto-assign \
  --category legacy \
  --path-filter "archive" \
  --limit 200

# Batch 5: Scripts (126 files)
python scripts/doc_id_assigner.py auto-assign \
  --category script \
  --path-filter "scripts" \
  --limit 150

# Continue for remaining directories...
```

**Expected Result**: Reduce missing from ~500 → ~100

---

### **Phase C: Manual Review & Edge Cases** (30 min)

**Goal**: Handle the final 100 files that need special attention

**Process**:
1. Export list of remaining missing files
2. Categorize into:
   - **Legitimate files** → Assign manually or fix auto-assigner
   - **Generated files** → Add to scanner ignore list
   - **External code** → Add to scanner ignore list
   - **Deprecated** → Move to archive or mark as legacy
3. Handle each category appropriately

**Expected Result**: 100% coverage or documented exceptions

---

## 🚀 Implementation Plan

### **Option 1: Automated Sweep (Fastest - 60 min)**

Run enhanced auto-assigner with aggressive fallback logic:

```bash
# 1. Update auto-assigner with enhanced logic
# 2. Run full assignment with fallback categories
python scripts/doc_id_assigner.py auto-assign \
  --types py md json yaml yml ps1 sh txt \
  --use-fallback-categories \
  --aggressive-mode

# 3. Scan and validate
python scripts/doc_id_scanner.py scan
python scripts/doc_id_scanner.py stats
python scripts/doc_id_preflight.py --min-coverage 1.0
```

**Pros**: Fastest path to 100%  
**Cons**: May create suboptimal category assignments

---

### **Option 2: Controlled Batches (Recommended - 90 min)**

Process files in controlled batches by directory:

```bash
# Phase A: Enhance assigner (30 min)
# - Add directory → category mapping
# - Add new categories (legacy, task)
# - Improve error handling

# Phase B: Process by directory (45 min)
# - UET patterns → pattern category
# - Modules → core category  
# - Developer → guide category
# - Archive → legacy category
# - ToDo_Task → task category
# - Scripts → script category
# - Tests → test category
# - Docs → guide category
# - Error → error category
# - AIM → aim category
# - PM → pm category
# - Tools → script category
# - GUI → guide category
# - Workstreams → guide category
# - Root files → guide category (default)

# Phase C: Manual review (15 min)
# - Review final 50-100 files
# - Assign or document exceptions
```

**Pros**: Better category accuracy, controlled process  
**Cons**: Takes longer

---

### **Option 3: Hybrid (Balanced - 75 min)**

Automated for most, manual for edge cases:

```bash
# 1. Add directory mapping to assigner (15 min)
# 2. Run auto-assign with directory hints (30 min)
# 3. Manual review of failures (30 min)
```

**Pros**: Balance of speed and accuracy  
**Cons**: Requires some manual intervention

---

## 🔧 Technical Implementation

### Step 1: Enhance Auto-Assigner

Add to `scripts/doc_id_assigner.py`:

```python
# Directory → Category mapping
DIRECTORY_CATEGORY_MAP = {
    'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK': 'pattern',
    'modules': 'core',
    'developer': 'guide',
    'archive': 'legacy',
    'ToDo_Task': 'task',
    'scripts': 'script',
    'tests': 'test',
    'docs': 'guide',
    'error': 'error',
    'aim': 'aim',
    'pm': 'pm',
    'tools': 'script',
    'gui': 'guide',
    'workstreams': 'guide',
    'core': 'core',
    'engine': 'core',
    'infra': 'infra',
    'config': 'config',
}

def infer_category_enhanced(path):
    """Enhanced category inference with directory mapping."""
    parts = Path(path).parts
    
    # Check first directory
    if len(parts) > 0:
        first_dir = parts[0]
        if first_dir in DIRECTORY_CATEGORY_MAP:
            return DIRECTORY_CATEGORY_MAP[first_dir]
    
    # Fallback to original logic
    return infer_category_original(path) or 'guide'  # guide as ultimate fallback
```

### Step 2: Add New Categories to Registry

Add to `DOC_ID_REGISTRY.yaml`:

```yaml
categories:
  # ... existing categories ...
  
  legacy:
    prefix: LEGACY
    description: Archived and deprecated content
    next_id: 1
    
  task:
    prefix: TASK
    description: Task tracking and todo items
    next_id: 1
```

### Step 3: Run Enhanced Assignment

```bash
# Dry-run first
python scripts/doc_id_assigner.py auto-assign \
  --dry-run \
  --limit 50

# If looks good, run full
python scripts/doc_id_assigner.py auto-assign
```

---

## 📈 Expected Timeline

### Option 1: Automated Sweep
- **Time**: 60 minutes
- **Coverage**: ~98-100%
- **Effort**: Low
- **Risk**: Medium (suboptimal categories)

### Option 2: Controlled Batches (RECOMMENDED)
- **Time**: 90 minutes
- **Coverage**: 100% (or documented exceptions)
- **Effort**: Medium
- **Risk**: Low (high quality assignments)

### Option 3: Hybrid
- **Time**: 75 minutes
- **Coverage**: ~99%
- **Effort**: Medium
- **Risk**: Low

---

## ✅ Success Criteria

- [ ] Coverage ≥ 99% (or 100% excluding documented exceptions)
- [ ] All Python files have doc_id (100%)
- [ ] All YAML/JSON config files have doc_id (100%)
- [ ] All scripts have doc_id (100%)
- [ ] Registry validates with 0 errors
- [ ] Preflight passes with `--min-coverage 1.0`
- [ ] All categories have appropriate docs

---

## 🎯 Recommendation

**Use Option 2: Controlled Batches**

**Rationale**:
1. High-quality category assignments
2. Controlled, verifiable process
3. Only 90 minutes additional time
4. Results in clean, maintainable registry
5. Sets foundation for Phase 1.5 (Module IDs)

**Execution**:
1. Add directory mapping (15 min)
2. Add new categories to registry (5 min)
3. Process batches by directory (50 min)
4. Manual review final files (20 min)
5. **Result**: 100% coverage with accurate categories

---

## 📊 Post-100% Validation

After reaching 100%, run full validation suite:

```bash
# 1. Scan
python scripts/doc_id_scanner.py scan

# 2. Stats (should show 100%)
python scripts/doc_id_scanner.py stats

# 3. Registry validation
python doc_id/tools/doc_id_registry_cli.py validate

# 4. Preflight (strict)
python scripts/doc_id_preflight.py --min-coverage 1.0

# 5. Generate reports
python scripts/doc_id_scanner.py coverage-report
```

Expected output:
```
Total eligible files:      ~5,200
Files with doc_id:         ~5,200 (100%)
Files missing doc_id:          0 (  0%)
```

---

## 🚀 Next Steps

1. **Choose Option** (Recommend Option 2)
2. **Implement enhancements** to auto-assigner
3. **Add new categories** to registry
4. **Execute batches** by directory
5. **Validate 100% coverage**
6. **Commit and tag** as `v1.0.0-docid-100-percent`
7. **Proceed to Phase 1** (CI/CD Integration)

---

**Current Status**: Phase 0 Complete (81.8%)  
**Next Goal**: 100% Coverage  
**Estimated Time**: 90 minutes (Option 2)  
**Ready to Execute**: ✅

---

*End of 100% Coverage Strategy*
