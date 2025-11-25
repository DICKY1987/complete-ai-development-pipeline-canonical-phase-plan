# Hardcoded Path Indexer

This tool scans the repository to index hardcoded paths, Python imports, and path-like references across code, configs, and docs. Results persist in a SQLite database for planning section-aware refactors.

## Features

- Scans code (`.py`, `.ps1`, `.psm1`, `.sh`, `.bat`, `.cmd`), configs (`.yml/.yaml`, `.json`, `.ini/.cfg/.toml`), and docs (`.md`, `.txt`).
- Classifies occurrences by kind: `code_import`, `fs_literal`, `code_path`, `config_path`, `doc_link`.
- Tracks section patterns (e.g., `src/`, `tests/`, `docs/`, `tools/`, `config/`, `schema/`, `openspec/`, `PHASE_DEV_DOCS`, `MOD_ERROR_PIPELINE`, `gui`).
- Persists results to `refactor_paths.db` (SQLite) with `files` and `occurrences` tables.
- CLI provides `scan`, `report`, `summary`, and `export` commands.
- CI gate: `gate` command fails on matching legacy patterns.

## Quick Start

1. Install dependencies (from repo root):

   - `python -m venv .venv && . ./.venv/Scripts/Activate.ps1`
   - `pip install -r requirements.txt`

2. Run a fresh scan (from repo root):

   - `python ./scripts/paths_index_cli.py scan --root . --db refactor_paths.db --reset`

3. View a summary:

   - `python ./scripts/paths_index_cli.py summary --db refactor_paths.db`

4. Export results to JSON or CSV:

   - `python ./scripts/paths_index_cli.py export --db refactor_paths.db --format json --out paths.json`

5. CI gate example:

   - `python ./scripts/paths_index_cli.py gate --db refactor_paths.db --regex "src/pipeline|MOD_ERROR_PIPELINE|PHASE_DEV_DOCS"`

## Database Schema

- `files(file_path, ext, size, mtime, scanned_at)`
- `occurrences(id, file_path, line_no, kind, pattern, value, context, ext)`

## Notes

- The indexer is best-effort and conservative. It avoids URLs and binary files and prunes common build/test caches.
- For YAML parsing it uses `PyYAML` if available; otherwise falls back to text matching.
- You can include hidden files and folders with `--include-hidden`.

