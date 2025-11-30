---
doc_id: DOC-GUIDE-REMAINING-MODULE-CENTRIC-PLAN-429
---

# Module-Centric Refactor Plan (Remaining Steps Only)

Document ID: PLAN-REFACTOR-MODULE-CENTRIC-001-REMAINING  
Date: 2025-11-27  
Status: In Progress (Phase 2-4 pending)  

## Phase 2: Validation & Testing
- Gate 1: Compile modules — `python -m compileall modules/ -q` (must exit 0).
- Gate 2: Import resolution — run `python scripts/test_imports.py` (expect “All imports successful!”).
- Gate 3: No ULID path usage — `rg "modules\\.\\w+\\.0[0-9]" modules/` should return nothing.
- Gate 4: Import analysis diff — `python scripts/analyze_imports.py modules/ > import_analysis_after.yaml` then diff vs `import_analysis_report.yaml`.
- Test suite: `pytest -q` (expect all passing; baseline 196 tests). Coverage target ≥77%.

## Phase 3: Archive Old Structure
- Script: `python scripts/archive_old_structure.py --dry-run` then `--execute`.
- Verify archive: `archive/structure_archived_2025-11-26/{core,error,aim,pm,specifications}` exist; original dirs absent in root.
- Docs/indices update:
  - `CODEBASE_INDEX.yaml` references only `modules/`.
  - `README.md` import examples use `modules.*`.
  - `docs/MODULE_CENTRIC_MIGRATION_GUIDE.md` marked complete.
  - `MIGRATION_FINAL_STATUS.md` updated with completion status.

## Phase 4: Final Validation & Cleanup
- Validation suite:
  - `python scripts/validate_modules.py --all`
  - `python scripts/paths_index_cli.py gate --db refactor_paths.db`
  - `pytest -q`
  - `python -m compileall modules/ -q`
  - `python scripts/validate_all_schemas.py`
  - `python scripts/enforce_guards.py`
- Anti-pattern scorecard: all 11 guards zero violations; no TODOs/placeholders.
- Cleanup: remove temporary checkpoints/worktrees and `__pycache__` under modules/.
- Commit packaging: include modules/, archive output, scripts/, updated docs/indices; ensure clean `git status`.
