# DOC_ID Execution Plan - Session 2025-11-24

**Generated**: 2025-11-24 17:45:08  
**Status**: Ready to Execute  
**Strategy**: 4-way parallel execution using git worktrees

---

## 📊 Current State

**Registry Status:**
- Total registered: 29 documents
- Categories populated: 5 (core, error, script, patterns, guide)
- Registry validation: ⚠️ Minor issues (non-blocking)

**Worktrees Status:**
- ✅ 4 worktrees created and ready
- ✅ All branches isolated
- ✅ No conflicts detected

**File Discovery:**
- Specs & Config: 10 files
- Scripts: 25 files  
- Tests & Docs: 90 files
- Remaining Modules: 100 files
- **Total to process: 225 files**

---

## 🎯 Execution Plan

### Phase 1: Parallel Registration (Estimated: 1.5 hours)

#### Worktree 1: Specifications & Config
**Branch**: `feature/docid-specs`  
**Path**: `.worktrees/wt-docid-specs`  
**Files**: 10 (8 schemas + 2 configs)  
**Estimated time**: 20 minutes

**Files to register:**
```
schema/
  - workstream.schema.json
  - step.schema.json
  - error.schema.json
  - run.schema.json
  - event.schema.json
  - tool-profile.schema.json
  - config.schema.json
  - quality-gate.schema.json

config/
  - orchestrator.yaml
  - executor.yaml
```

**Actions:**
1. Register 8 schemas with DOC-SPEC-* prefix
2. Register 2 configs with DOC-CONFIG-* prefix
3. Create specifications/SPEC_INDEX.yaml
4. Commit to feature/docid-specs

**Pattern**: EXEC-009, EXEC-010

---

#### Worktree 2: Scripts & Tools
**Branch**: `feature/docid-scripts`  
**Path**: `.worktrees/wt-docid-scripts`  
**Files**: 25 Python scripts  
**Estimated time**: 30 minutes

**Files to register:**
```
scripts/
  - doc_id_registry_cli.py (DOC-SCRIPT-DOC-ID-REGISTRY-CLI-001 ✅)
  - batch_file_creator.py (DOC-SCRIPT-BATCH-FILE-CREATOR-002 ✅)
  - pattern_discovery.py (DOC-SCRIPT-PATTERN-DISCOVERY-003 ✅)
  - validate_workstreams.py (DOC-SCRIPT-VALIDATE-WORKSTREAMS-004 ✅)
  - create_docid_worktrees.ps1 (needs registration)
  - ... (21 more scripts)
```

**Actions:**
1. Register remaining 21 scripts with DOC-SCRIPT-* prefix
2. Create scripts/SCRIPT_INDEX.yaml
3. Group by function (validation, generation, analysis)
4. Commit to feature/docid-scripts

**Pattern**: EXEC-009, EXEC-010

---

#### Worktree 3: Tests & Documentation
**Branch**: `feature/docid-tests-docs`  
**Path**: `.worktrees/wt-docid-tests-docs`  
**Files**: 90 (80 tests + 10 docs)  
**Estimated time**: 45 minutes

**Files to register:**
```
tests/
  - state/test_*.py (7 files)
  - engine/test_*.py (18 files)
  - error/test_*.py (40 files)
  - planning/test_*.py (15 files)

docs/
  - QUICK_START.md
  - README.md
  - ARCHITECTURE.md
  - ... (7 more guides)
```

**Actions:**
1. Register 80 test files with DOC-TEST-* prefix
2. Register 10 guide files with DOC-GUIDE-* prefix
3. Create tests/TEST_INDEX.yaml
4. Create docs/GUIDE_INDEX.yaml
5. Commit to feature/docid-tests-docs

**Pattern**: EXEC-009, EXEC-010

---

#### Worktree 4: Remaining Modules
**Branch**: `feature/docid-modules`  
**Path**: `.worktrees/wt-docid-modules`  
**Files**: 100 (64 core + 28 aim + 8 pm)  
**Estimated time**: 60 minutes

**Files to register:**
```
core/ (64 files - excluding already registered state/engine)
  - planning/*.py (15 files)
  - ast/*.py (12 files)
  - utils/*.py (10 files)
  - adapters/*.py (8 files)
  - ... (19 more)

aim/ (28 files)
  - bridge.py
  - tool_manager.py
  - environment_manager.py
  - ... (25 more)

pm/ (8 files)
  - workstream_manager.py
  - step_executor.py
  - bundle_loader.py
  - ... (5 more)
```

**Actions:**
1. Register 64 remaining core modules with DOC-CORE-* prefix
2. Register 28 AIM modules with DOC-AIM-* prefix
3. Register 8 PM modules with DOC-PM-* prefix
4. Update core/CORE_MODULE_INDEX.yaml
5. Create aim/AIM_INDEX.yaml
6. Create pm/PM_INDEX.yaml
7. Commit to feature/docid-modules

**Pattern**: EXEC-009, EXEC-010

---

### Phase 2: Sequential Merge (Estimated: 20 minutes)

**Order** (following EXEC-011):
1. Merge `feature/docid-specs` → main (5 min)
2. Merge `feature/docid-scripts` → main (5 min)
3. Merge `feature/docid-tests-docs` → main (5 min)
4. Merge `feature/docid-modules` → main (5 min)

**Validation after each merge:**
- Run `python scripts/doc_id_registry_cli.py validate`
- Check for conflicts (resolve if any)
- Verify counts incrementing correctly

---

### Phase 3: Cleanup & Verification (Estimated: 5 minutes)

**Actions:**
1. Remove all 4 worktrees
2. Delete feature branches
3. Final registry validation
4. Generate completion report
5. Commit final state

**Expected final state:**
```
Total docs: 254 (29 current + 225 new)
By category:
  core: 74
  error: 10
  spec: 8
  config: 2
  script: 29
  test: 80
  guide: 11
  aim: 28
  pm: 8
  patterns: 4
```

---

## ⏱️ Time Budget

| Phase | Worktree/Task | Time | Status |
|-------|--------------|------|--------|
| **Phase 1** | **Parallel Execution** | **1.5 hours** | Pending |
| | Worktree 1: Specs | 20 min | ⏳ |
| | Worktree 2: Scripts | 30 min | ⏳ |
| | Worktree 3: Tests/Docs | 45 min | ⏳ |
| | Worktree 4: Modules | 60 min | ⏳ |
| **Phase 2** | **Sequential Merge** | **20 min** | Pending |
| | Merge specs | 5 min | ⏳ |
| | Merge scripts | 5 min | ⏳ |
| | Merge tests/docs | 5 min | ⏳ |
| | Merge modules | 5 min | ⏳ |
| **Phase 3** | **Cleanup** | **5 min** | Pending |
| **TOTAL** | | **~2 hours** | |

---

## 🚀 Execution Commands

### Start Worktree 1 (Terminal 1)
```powershell
cd .worktrees/wt-docid-specs
# Follow DOC_ID_PARALLEL_EXECUTION_GUIDE.md > Worktree 1 section
```

### Start Worktree 2 (Terminal 2)
```powershell
cd .worktrees/wt-docid-scripts
# Follow DOC_ID_PARALLEL_EXECUTION_GUIDE.md > Worktree 2 section
```

### Start Worktree 3 (Terminal 3)
```powershell
cd .worktrees/wt-docid-tests-docs
# Follow DOC_ID_PARALLEL_EXECUTION_GUIDE.md > Worktree 3 section
```

### Start Worktree 4 (Terminal 4)
```powershell
cd .worktrees/wt-docid-modules
# Follow DOC_ID_PARALLEL_EXECUTION_GUIDE.md > Worktree 4 section
```

---

## ✅ Success Criteria

- [ ] All 225 files registered
- [ ] 6 new index files created (SPEC, SCRIPT, TEST, GUIDE, AIM, PM)
- [ ] Registry validates without errors
- [ ] No merge conflicts
- [ ] Total time < 2.5 hours
- [ ] 100% repository coverage achieved

---

## 📋 Pre-Flight Checklist

- [x] Worktrees created
- [x] Registry validated
- [x] File counts verified
- [x] Patterns reviewed (EXEC-009, EXEC-010, EXEC-011)
- [x] Execution guide available
- [ ] 4 terminal windows open
- [ ] Ready to begin parallel execution

---

## 🎯 Next Action

**OPTION 1: Single-session execution (if you have 2 hours now)**
- Open 4 terminals
- Execute all worktrees in parallel
- Complete in one session

**OPTION 2: Phased execution (recommended)**
- Execute Worktree 1 now (20 min)
- Verify and merge
- Continue with remaining worktrees in subsequent sessions

**OPTION 3: Delegate to AI instances**
- Assign each worktree to separate AI instance
- Monitor progress
- Merge when all complete

---

**Status**: ✅ Plan Ready for Execution  
**Recommendation**: Start with Worktree 1 (smallest, 20 min) to validate approach

**Command to begin:**
```powershell
cd .worktrees/wt-docid-specs
# Execute Worktree 1 commands from guide
```
