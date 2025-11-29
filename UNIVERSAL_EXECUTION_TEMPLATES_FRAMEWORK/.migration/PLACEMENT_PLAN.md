# Placement plan for staged batches WS-001–WS-020

Scope: staged copies live under `.migration/stage/WS-*/` on branch `ai-sandbox/codex/uet-batch-staging`. This plan maps each staged file set to its canonical UET target and notes shim/validation steps before moving originals.

## Mapping rules (targets)
- Core state (WS-001, WS-002): `modules/core-state/m010003_<name>.py` → `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/state/<name>.py` (drop `m010003_` prefix).
- Core AST (WS-003): `modules/core-ast/m010000_extractors.py` → `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/ast/extractors.py`.
- Core planning (WS-004): `modules/core-planning/m010002_<name>.py` → `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/planning/<name>.py`.
- Core engine (WS-005–WS-007): `modules/core-engine/m010001_<name>.py` → `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/<name>.py`; existing UET engine files in WS-006/WS-007 stay in place (router, scheduler, patch_ledger, state_machine) and only need import updates if required.
- Error shared (WS-008): `modules/error-shared/m010021_<name>.py` → `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error/shared/utils/<name>.py`.
- Error engine (WS-009): `modules/error-engine/m010004_<name>.py` → `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error/engine/<name>.py`.
- AIM (WS-010): `modules/aim-environment/m01001B_<name>.py` → `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/aim/<name>.py`; tests under `modules/aim-tests/` map to `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/tests/aim/`.
- PM (WS-011): `modules/pm-integrations/m01001F_github_sync.py` → `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/pm/github_sync.py`.
- Specifications tools (WS-012): `modules/specifications-tools/m010020_<name>.py` → `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/specifications/tools/<name>.py`; keep `specifications/tools/__init__.py`.
- Error plugins (WS-013–WS-016): `modules/error-plugin-*/m0100**_plugin.py` → `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error/plugins/<plugin>/<plugin>.py` (rename to `plugin.py` per existing plugin pattern).
- UI/CLI (WS-013, WS-015, WS-016): move `core/ui_settings_cli.py`, `core/ui_cli.py`, `core/ui_settings.py`, `core/ui_models.py` into `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/` keeping filenames; ensure imports align with canonical `core.ui_*`.
- Scripts and utilities (WS-016, WS-017, WS-019): move staged `scripts/*.py` into `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/` preserving names.
- Patterns (WS-017, WS-019): keep under `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/...` preserving relative structure.
- Legacy/archives (WS-017–WS-020): keep under `archive/...` in `.migration/stage` until formally archived; do not overwrite active code.
- GUI items (WS-019, WS-020): place under `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/gui/` preserving names.

## Shim and import adjustments
- For each moved module, leave a thin shim in the old `modules/...` location that imports from the new UET path and raises `DeprecationWarning`.
- Update any intra-module imports in moved files to use `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.<section>...` paths (no `modules.` prefixes).
- Plugins: ensure each plugin folder has `__init__.py` if required; standardize entry filename to `plugin.py` and adjust references.

## Execution steps
1) For each batch, copy from `.migration/stage/WS-XX/` into the target directories above (non-destructive; originals remain).
2) Add shims under `modules/...` mirroring original names that redirect to UET imports.
3) Update import paths inside moved files; run a quick grep to confirm no `from modules.` or `import modules.` remains inside UET tree.
4) Record actions and target paths in `.migration/migration_log.yaml` (add status, dest paths, and notes on shims).

## Validation checklist
- Import checks (representative):
  - `python - <<'PY'\nimport UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine.state_machine\nimport UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.engine.error_engine\nimport UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.aim.exceptions\nimport UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.pm.github_sync\nPY`
- Plugins: smoke import for a few plugins, e.g., `python -c "import UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.plugins.python_pyright.plugin"`.
- Tests: `pytest UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/tests/ -q` (or narrower if only AIM/tests touched).
- Legacy import scan: `rg "from modules\\.|import modules\\." UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK`.
- Update `.migration/migration_log.yaml` with validation results (exit codes, date, scope).

## PR notes
- Branch: `ai-sandbox/codex/uet-batch-staging`.
- After placement and validations, push updates and open PR for review/merge. Include mapping summary and validation commands in the PR description.
