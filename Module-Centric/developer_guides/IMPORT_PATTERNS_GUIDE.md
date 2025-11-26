# Import Patterns Guide (Hybrid ULID Strategy)

Goal: keep ULID-prefixed filenames for identity while preserving Python-import-safe names for code.

## Rules
- Files may start with ULID prefix (e.g., `010001_orchestrator.py`) but are not imported directly.
- Each module folder MUST have `__init__.py` exporting import-safe symbols (no leading digits).
- Public imports use clean names (`from modules.core_engine import orchestrator`), not ULID filenames.

## Patterns
- Re-export in `__init__.py`:
  ```python
  from .010001_orchestrator import Orchestrator  # noqa: F401
  ```
- Optional alias module for readability:
  ```python
  # modules/core-engine/orchestrator.py
  from .010001_orchestrator import Orchestrator  # noqa: F401
  ```
- Avoid numeric module names in imports; never `import modules.core-engine.010001_orchestrator`.

## Migration Steps
1) Ensure every module has `__init__.py` with re-exports for ULID-prefixed files.
2) Run `python scripts/create_init_files_v3.py` to generate missing re-exports.
3) Run `python scripts/rewrite_imports.py` to point imports to clean names.
4) Validate: `python -m py_compile $(rg --files -g '*.py')`.

## Anti-Patterns (do not)
- Import by numeric filename.
- Cross-module relative imports that bypass the module boundary.
- Divergent aliases: keep the same public symbol names as exposed in `__init__.py`.
