---
doc_id: DOC-GUIDE-VALIDATION-CHECKLIST-1460
---

# Validation Checklist (Module-Centric Migration)

Run these checks after each phase and before commit.

## Manifests and ULIDs
- [ ] Each module has `module.manifest.json|yaml` per spec.
- [ ] `ulid_prefix` matches all listed artifacts.
- [ ] `python scripts/validate_modules.py modules` passes.

## DAGs (Derived State)
- [ ] `python scripts/refresh_repo_dag.py --force` succeeds.
- [ ] `python scripts/validate_dag_freshness.py` exits 0.
- [ ] `.state/dag/repo_modules.dag.json` exists and lists all inventory modules.
- [ ] `modules/*/.state/module_tasks.dag.json` exist where modules have manifests.
- [ ] `.state/dag/pipelines/*.dag.json` exist (if pipeline specs present).

## Imports (Hybrid Strategy)
- [ ] Each module has `__init__.py` re-exporting ULID files.
- [ ] `python scripts/rewrite_imports.py` run without errors.
- [ ] `python -m py_compile $(rg --files -g '*.py')` passes.

## Tests
- [ ] Targeted tests or `pytest -q` pass (if test suite present).
- [ ] No skipped critical tests related to migration.

## Git Hygiene
- [ ] `git status -sb` is clean or only shows intended changes.
- [ ] Large generated files (DAGs) reviewed for expected diffs only.

## Post-Migration Spot Checks
- [ ] One module opened in isolation contains code/tests/schemas/docs/state.
- [ ] Importing a representative module works in a Python shell.
- [ ] DAG reverse-edge query answers “who depends on X?” correctly for at least one module.
