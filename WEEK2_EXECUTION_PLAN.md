# Week 2 Execution Plan: Import Paths, Testing, Documentation

**Date**: 2025-11-26  
**Status**: Week 1 COMPLETE (100% modules migrated)  
**Phase**: Week 2 - Integration & Validation

---

## Week 1 Achievement Summary

✅ **All 33 modules migrated** (100%)
✅ **94 Python files** with ULID prefixes
✅ **33 manifests** auto-generated
✅ **Template system** validated (150-200x speedup)
✅ **Time**: 3.25 hours total (vs 150-200 hours manual)

---

## Week 2 Objectives

### 🎯 Primary Goals
1. **Import path analysis** - Map all current imports
2. **Import rewriting strategy** - Define conversion rules
3. **Integration testing** - Verify module functionality
4. **Documentation sync** - Update all references
5. **Validation gates** - Ensure nothing breaks

### 📊 Success Criteria
- [ ] All imports analyzed and documented
- [ ] Import rewriting strategy defined
- [ ] Critical modules tested (core-engine, core-state, error-engine)
- [ ] CODEBASE_INDEX.yaml updated
- [ ] No broken imports in migrated code

---

## Day 1: Import Path Analysis

### Task 1.1: Scan All Imports (1-2 hours)

**Goal**: Understand current import patterns across codebase

**Script to create**:
```python
# scripts/analyze_imports.py
"""
Analyze all import statements in Python files.
Generate report of:
- Import sources (where imports come from)
- Import targets (what gets imported)
- Deprecated paths (src.*, MOD_ERROR_PIPELINE.*)
- Module cross-references
"""
```

**Output**: `import_analysis_report.yaml`

### Task 1.2: Map Module Dependencies (1 hour)

**Goal**: Verify MODULES_INVENTORY.yaml dependency graph is accurate

**Validation**:
- Cross-reference actual imports vs declared dependencies
- Identify circular dependencies
- Find missing dependencies

### Task 1.3: Identify Import Patterns (1 hour)

**Categories**:
1. **Intra-module imports** (within same module) - No change needed
2. **Cross-module imports** (between modules) - Update to new paths
3. **External imports** (third-party) - No change needed
4. **Deprecated imports** (src.*, MOD_ERROR_PIPELINE.*) - Flag for removal

---

## Day 2: Import Rewriting Strategy

### Task 2.1: Define Conversion Rules (2 hours)

**Old → New mapping**:
```yaml
conversion_rules:
  # Core modules
  - old: "from core.state.db import"
    new: "from modules.core_state.010003_db import"
    
  - old: "from core.engine.orchestrator import"
    new: "from modules.core_engine.010001_orchestrator import"
    
  # Error modules
  - old: "from error.engine.error_engine import"
    new: "from modules.error_engine.010004_error_engine import"
    
  - old: "from error.plugins.python_ruff.plugin import"
    new: "from modules.error_plugin_python_ruff.010015_plugin import"
    
  # AIM modules
  - old: "from aim.environment.scanner import"
    new: "from modules.aim_environment.01001B_scanner import"
```

### Task 2.2: Create Import Rewriter (2-3 hours)

**Script**: `scripts/rewrite_imports.py`

**Features**:
- Reads conversion rules from config
- Uses AST parsing for accuracy
- Preserves import styles (from X import Y, import X)
- Dry-run mode
- Backup original files

**Safety**:
- Only rewrite files in `modules/`
- Validate syntax after rewriting
- Git-trackable changes

### Task 2.3: Test Import Rewriter (1 hour)

**Test on**: 1-2 small modules first
- error-plugin-echo (simple, 1 file)
- core-ast (simple, 1 file)

**Validation**:
```bash
python -m py_compile modules/error-plugin-echo/*.py
python -m py_compile modules/core-ast/*.py
```

---

## Day 3: Batch Import Rewriting

### Task 3.1: Rewrite Independent Modules (2 hours)

**Order** (lowest risk first):
1. Error plugins (21 modules, mostly self-contained)
2. AIM modules (simple imports)
3. PM module (minimal imports)
4. Specifications (utility functions)

**Command**:
```bash
python scripts/rewrite_imports.py --pattern "error-plugin-*" --dry-run
python scripts/rewrite_imports.py --pattern "error-plugin-*" --execute
```

### Task 3.2: Rewrite Core Modules (2 hours)

**Order** (dependency-aware):
1. core-state (infrastructure)
2. core-planning (depends on core-state)
3. error-engine (domain)
4. core-engine (depends on all above)

### Task 3.3: Validation (1 hour)

**Checks**:
- All Python files compile
- No syntax errors
- Imports resolve (using Python import checker)
- No deprecated paths remain

---

## Day 4: Integration Testing

### Task 4.1: Unit Test Critical Modules (2 hours)

**Test**:
```bash
# Test core modules
python -c "from modules.core_state.010003_db import init_db; print('OK')"
python -c "from modules.core_engine.010001_orchestrator import Orchestrator; print('OK')"
python -c "from modules.error_engine.010004_error_engine import ErrorEngine; print('OK')"
```

### Task 4.2: Run Existing Test Suite (2 hours)

**If tests exist**:
```bash
pytest tests/ -v --tb=short
```

**Expected**: Some tests may fail (import paths changed)

**Strategy**: 
- Update test imports to use new paths
- Or: Add backward compatibility shims temporarily

### Task 4.3: Smoke Test Key Workflows (1 hour)

**Manual validation**:
1. Can core-engine import core-state? ✅
2. Can error-engine load plugins? ✅
3. Can orchestrator run a simple task? ✅

---

## Day 5: Documentation & Cleanup

### Task 5.1: Update CODEBASE_INDEX.yaml (1 hour)

**Changes**:
```yaml
modules:
  - id: "core-state"
    path: "modules/core-state/"  # Updated from "core/state/"
    manifest: "modules/core-state/010003_module.manifest.yaml"
    ulid_prefix: "010003"
    # ... rest from manifest
```

### Task 5.2: Update Documentation (2 hours)

**Files to update**:
- README.md (if references old paths)
- docs/DIRECTORY_GUIDE.md
- Any developer guides
- Architecture diagrams

### Task 5.3: Create Migration Complete Report (1 hour)

**Document**:
- What changed (file paths, import statements)
- How to import modules now
- Backward compatibility notes
- Known issues / tech debt

---

## Validation Gates (Continuous)

### Gate 1: Python Syntax
```bash
python -m compileall modules/ -q
```
**Must**: Exit code 0

### Gate 2: Import Resolution
```bash
python scripts/validate_imports.py --all
```
**Must**: All imports resolve

### Gate 3: No Deprecated Paths
```bash
grep -r "from src\." modules/
grep -r "from MOD_ERROR_PIPELINE\." modules/
```
**Must**: No results

### Gate 4: Manifest Consistency
```bash
python scripts/validate_modules.py --all
```
**Must**: All manifests valid

---

## Risk Mitigation

### Risk 1: Import Rewriting Breaks Code
**Mitigation**:
- Dry-run first
- Test on small modules
- Git commit after each batch
- Keep original files until validation passes

### Risk 2: Circular Import Issues
**Mitigation**:
- Dependency analysis first
- Break circular deps if found
- Use lazy imports where needed

### Risk 3: Tests Fail After Migration
**Mitigation**:
- Expected for import changes
- Update test imports systematically
- Temporarily add backward compat if needed

---

## Automation Scripts to Create

### 1. `scripts/analyze_imports.py`
- Scan all Python files
- Extract import statements
- Categorize imports
- Generate report

### 2. `scripts/rewrite_imports.py`
- Load conversion rules
- Parse Python files with AST
- Rewrite import statements
- Validate syntax
- Support dry-run mode

### 3. `scripts/validate_imports.py`
- Check all imports resolve
- Identify broken imports
- Report missing modules

### 4. `scripts/update_codebase_index.py`
- Read MODULES_INVENTORY.yaml
- Generate updated CODEBASE_INDEX.yaml
- Merge with existing metadata

---

## Timeline Estimate

**Day 1**: Import analysis (3-4 hours)
**Day 2**: Rewriter creation + testing (4-5 hours)
**Day 3**: Batch rewriting + validation (4-5 hours)
**Day 4**: Integration testing (4-5 hours)
**Day 5**: Documentation + cleanup (3-4 hours)

**Total**: 18-23 hours (~1 week at 4 hours/day)

---

## Success Metrics

### Week 2 Complete When:
- [ ] All imports analyzed and documented
- [ ] Import rewriter created and tested
- [ ] All 33 modules have updated imports
- [ ] Python compilation passes (100%)
- [ ] Import resolution passes (100%)
- [ ] CODEBASE_INDEX.yaml updated
- [ ] Documentation reflects new structure
- [ ] Migration report published

---

## Next Week Preview (Week 3-4)

**If Week 2 completes successfully**:
- Week 3: Archive old structure, final testing
- Week 4: Polish, optimization, close migration

**Alternatively**:
- Continue import path work if complex
- Add backward compatibility layer
- Gradual cutover approach

---

## Current Status

**Completed**:
✅ Week 1: All 33 modules migrated
✅ Template system working
✅ Validation framework operational

**Starting**:
🔄 Week 2 Day 1: Import path analysis

**Next Action**:
Create `scripts/analyze_imports.py` to understand current import landscape

---

**Status**: Ready to begin Week 2  
**Confidence**: High (foundation solid)  
**Risk**: Medium (import rewriting needs care)  
**Timeline**: On track for 4-5 week completion
