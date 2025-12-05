# src/ and abstraction/ Analysis Summary

**Date**: 2025-12-01
**Conclusion**: src/ is ACTIVE code - do NOT archive!

---

## Analysis Results

### ❌ src/ - DO NOT ARCHIVE

**Contains ACTIVE production code:**

1. **src/path_registry.py** (93 lines)
   - Full path registry implementation
   - Used by: `tests/test_path_registry.py`, `scripts/dev/paths_resolve_cli.py`
   - NO equivalent in UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK
   - **Status**: ACTIVE production module

2. **src/orchestrator.py** (34 lines)
   - Parallel runner test stub
   - Used by: `tests/test_parallel_orchestrator.py`, `tests/test_parallel_dependencies.py`
   - **Status**: ACTIVE test helper

3. **src/plugins/spec_validator.py**
   - Need to verify usage

**Verdict**: Keep src/ in repository - it's NOT deprecated!

---

### ✅ abstraction/ - SAFE TO ARCHIVE

**Contains outdated status scripts:**

1. **abstraction/implement_all_phases.py** (84 lines)
   - Just prints status and creates markdown
   - No imports found (not used anywhere)
   - UET has NO workstream generation (different purpose)
   - **Status**: Can be safely archived

**Verdict**: Archive abstraction/ - it's just old status tracking

---

## Corrected Cleanup Plan

### What to Archive (7 folders, ~201 files)

1. Module-Centric/ (34 files)
2. REFACTOR_2/ (39 files)
3. bring_back_docs_/ (10 files)
4. ToDo_Task/ (74 files)
5. AI_SANDBOX/ (4 files)
6. ai-logs-analyzer/ (20 files)
7. **abstraction/** (20 files) ← ADDED

**Total**: 201 files, all documentation/planning

### What to KEEP

- **src/** (3 Python files) ← ACTIVE CODE, keep in repo!

---

## Why Initial Analysis Was Wrong

❌ **Incorrect assumption**: "src/ is deprecated because it uses old import paths"

✅ **Reality**: 
- src/path_registry.py IS the path registry implementation
- Tests import FROM it because it's the actual module
- There's no "new version" in UET - this is unique functionality
- It's part of the active codebase

---

## Action Items

1. ✅ Run corrected cleanup script:
   ```bash
   python safe_cleanup_corrected.py
   ```

2. ✅ Archives 7 folders (not 8)

3. ✅ Keeps src/ in repository

4. ✅ Total archived: ~201 files (docs only)

---

## Scripts Created

1. **check_src_necessity.py** - Analysis script (this report)
2. **safe_cleanup_corrected.py** - Corrected archival script
3. **SRC_ABSTRACTION_ANALYSIS.md** - This summary

---

## Recommendation

**Run this command to archive the correct folders:**

```bash
python safe_cleanup_corrected.py
```

This will:
- Archive 7 folders (201 files of docs/planning)
- Keep src/ in repository (active code)
- Create full README in archive explaining decisions
