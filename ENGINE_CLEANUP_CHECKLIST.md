# Engine Cleanup Checklist - Quick Win Path

**Goal**: Remove unused engine code, keep only the active legacy orchestrator  
**Time**: 1-2 days  
**Risk**: Low (removing dead code)

---

## Phase 1: Remove UET Stubs (Dead Code)

### Files to Delete - UET Stubs in core/engine/
These are 2-line placeholder stubs that were never implemented:

- [ ] `core/engine/uet_orchestrator.py` - 2-line stub
- [ ] `core/engine/uet_scheduler.py` - stub
- [ ] `core/engine/uet_router.py` - stub
- [ ] `core/engine/uet_patch_ledger.py` - stub
- [ ] `core/engine/uet_state_machine.py` - stub

### Files to Delete - UET Adapter Stubs
- [ ] `core/engine/adapters/uet_base.py` - stub
- [ ] `core/engine/adapters/uet_registry.py` - stub
- [ ] `core/engine/adapters/uet_subprocess.py` - stub

**Verification**: 
```bash
# Confirm no imports (should return nothing)
grep -r "from core.engine.uet_" --include="*.py" .
```

**Total**: 8 files to remove

---

## Phase 2: Archive engine/ Directory (Experimental Code)

### Directory to Archive
- [ ] Move `engine/` → `archive/experimental_engine/`

**Contents** (24 files):
- `engine/orchestrator/orchestrator.py`
- `engine/queue/*.py` (7 files)
- `engine/adapters/*.py` (4 files)
- `engine/interfaces/*.py` (4 files)
- `engine/state_store/*.py`
- `engine/types.py`
- `engine/README.md`

### Files to Update - Scripts
Update or remove these 3 scripts that reference `engine/`:

- [ ] `scripts/test_state_store.py` - Update or remove
- [ ] `scripts/test_adapters.py` - Update or remove
- [ ] `tools/validation/validate_engine.py` - Update or remove

**Verification**:
```bash
# Check for remaining imports (should return nothing after cleanup)
grep -r "from engine\." --include="*.py" .
```

**Total**: 1 directory (24 files) to archive

---

## Phase 3: Archive UET Framework (Reference Only)

### Directory to Archive
- [ ] Move `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/` → `archive/uet_framework_reference/`

**Rationale**: 
- Contains production-ready code (337 passing tests)
- But migration never executed
- Keep as reference for future migration
- Remove from active codebase

**Size**: 17 engine files + full framework

---

## Phase 4: Investigate and Clean Variant Orchestrators

### Files to Investigate
- [ ] Review `core/engine/parallel_orchestrator.py`
  - Is it extension or replacement of legacy?
  - Still in use?
  - Decision: Keep or remove?

- [ ] Review `core/engine/pipeline_plus_orchestrator.py`
  - What is this?
  - Still in use?
  - Decision: Keep or remove?

### Files to Keep (Active Production)
- ✅ `core/engine/orchestrator.py` - **CANONICAL** (legacy)
- ✅ `core/orchestrator.py` - Re-export (keep)
- ✅ All other `core/engine/*.py` files currently in use

---

## Phase 5: Update Documentation

### Files to Update
- [ ] `ENGINE_MIGRATION_STATUS.md` - Mark as "Cleanup Complete"
- [ ] `CODEBASE_INDEX.yaml` - Remove references to:
  - `engine/` directory
  - UET stubs
  - `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/`

- [ ] `docs/DOC_ARCHITECTURE.md` - Clarify:
  - `core/engine/orchestrator.py` is canonical
  - UET migration not executed
  - Archive locations

- [ ] `README.md` - Update if needed

- [ ] `core/engine/README.md` - Document cleanup

- [ ] `developer/planning/DEPRECATION_PLAN.md` - Update status

---

## Phase 6: Verification

### Run These Checks

1. **No broken imports**:
```bash
pytest tests/ -v
python -m core.ui_cli --help
python -m core.planning.planner --help
```

2. **No references to removed code**:
```bash
# Should return empty
grep -r "from core.engine.uet_" --include="*.py" .
grep -r "from engine\." --include="*.py" . | grep -v "archive/"
grep -r "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK" --include="*.py" . | grep -v "archive/"
```

3. **Git status clean**:
```bash
git status
git log --oneline -5
```

---

## Execution Commands

### Step 1: Remove UET Stubs
```powershell
# Remove UET stub files
Remove-Item core\engine\uet_orchestrator.py
Remove-Item core\engine\uet_scheduler.py
Remove-Item core\engine\uet_router.py
Remove-Item core\engine\uet_patch_ledger.py
Remove-Item core\engine\uet_state_machine.py

# Remove UET adapter stubs
Remove-Item core\engine\adapters\uet_base.py
Remove-Item core\engine\adapters\uet_registry.py
Remove-Item core\engine\adapters\uet_subprocess.py
```

### Step 2: Archive engine/ Directory
```powershell
# Create archive location
New-Item -ItemType Directory -Force -Path archive\experimental_engine

# Move directory
Move-Item engine archive\experimental_engine\

# Update or remove dependent scripts
# (Manual review required)
```

### Step 3: Archive UET Framework
```powershell
# Create archive location
New-Item -ItemType Directory -Force -Path archive\uet_framework_reference

# Move directory
Move-Item UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK archive\uet_framework_reference\
```

### Step 4: Commit Changes
```bash
git add -A
git commit -m "cleanup: Remove unused engine code

- Remove 8 UET stub files (dead code)
- Archive engine/ directory (experimental, unused)
- Archive UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK (reference only)
- Update documentation

Consolidate to single production orchestrator: core/engine/orchestrator.py"
```

---

## Success Criteria

- [ ] ✅ All tests passing
- [ ] ✅ CLI commands work
- [ ] ✅ No broken imports
- [ ] ✅ Documentation updated
- [ ] ✅ Git committed
- [ ] ✅ Codebase simpler (75 → ~45 engine files)
- [ ] ✅ One canonical orchestrator clearly identified

---

## Rollback Plan

If something breaks:

```bash
# Restore from git
git reset --hard HEAD~1

# Or restore individual directories
git restore engine/
git restore UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/
git restore core/engine/uet_*.py
git restore core/engine/adapters/uet_*.py
```

---

## Post-Cleanup State

### Active Engine Files (core/engine/)
~26 files (down from 34):
- `orchestrator.py` ← **CANONICAL**
- `parallel_orchestrator.py` (if kept)
- `dag_builder.py`
- `executor.py`
- `scheduler.py`
- `tools.py`
- `adapters/*.py` (non-UET)
- All other supporting modules

### Archived
- `archive/experimental_engine/` (24 files)
- `archive/uet_framework_reference/` (full framework)

### Removed
- 8 UET stub files (dead code)

---

## Timeline

**Day 1 Morning**: 
- Remove UET stubs (Phase 1)
- Test verification

**Day 1 Afternoon**:
- Archive engine/ directory (Phase 2)
- Update scripts
- Test verification

**Day 2 Morning**:
- Archive UET framework (Phase 3)
- Update documentation (Phase 5)

**Day 2 Afternoon**:
- Final verification (Phase 6)
- Git commit
- Report completion

---

## Notes

- **Keep migration plan doc**: `engine_migration_plan.txt` → for future reference
- **Keep status report**: `ENGINE_MIGRATION_STATUS.md` → for future decisions
- **Archive, don't delete**: UET framework has 337 passing tests - valuable reference

---

## Completion Report Template

After cleanup, fill in:

```markdown
# Engine Cleanup Complete - [DATE]

## Actions Taken
- ✅ Removed 8 UET stub files
- ✅ Archived engine/ directory (24 files)
- ✅ Archived UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK
- ✅ Updated documentation
- ✅ Verified all tests passing

## Current State
- **Canonical Orchestrator**: core/engine/orchestrator.py
- **Total Engine Files**: 26 (down from 75)
- **Archives**: 
  - archive/experimental_engine/
  - archive/uet_framework_reference/

## Verification Results
- Tests: [PASS/FAIL]
- CLI: [PASS/FAIL]
- Imports: [CLEAN/ISSUES]

## Future Decisions
- [ ] Decide on parallel_orchestrator.py (keep/remove)
- [ ] Decide on pipeline_plus_orchestrator.py (keep/remove)
- [ ] Consider UET migration for long-term (6-8 weeks)

## Contacts
- Engineer: [NAME]
- Date: [DATE]
- Commit: [SHA]
```

---

**Ready to Execute**: Yes, all steps are actionable  
**Risk Level**: Low (removing unused code, archiving for safety)  
**Estimated Time**: 1-2 days
