# Test specifications for plugin suite (to be implemented)

This document defines the test cases another AI should implement for the newly added plugins.
Focus on deterministic parsing, graceful skip when tools are absent, and minimal external deps.

## General guidelines

- Use `pytest` and mark tests with `pytest.mark.skipif(shutil.which(tool) is None, ...)` for live smoke tests.
- Prefer parser unit tests by feeding saved tool JSON outputs to parser helpers or by monkeypatching `subprocess.run` to return canned stdout/stderr.
- Avoid network access; do not install tools inside tests. Tests should pass even if tools are not installed by skipping live runs.
- Keep tests fast (< 2s each). Use temp files via `tmp_path`.

## Python — isort (fix)

Cases:
- Given a Python file with unsorted imports, running the plugin produces a modified temp file (validated output differs from input) and no issues.
- Non-Python file is ignored by the plugin filter.
- If `isort` missing, plugin is skipped by discovery.

Assertions:
- `PluginResult.success is True` when command exit code is 0.
- Engine recheck uses validated outputs after mechanical autofix step.

## Python — Black (fix)

Cases:
- Given poorly formatted Python, running the plugin modifies the temp file; no issues emitted.

Assertions:
- Success on exit code 0; no issues created by this plugin.

## Python — Ruff (lint)

Cases:
- Parse sample Ruff JSON with a few warnings; normalized issues: `tool=ruff`, `category=style`, `severity=warning`.
- Exit code 1 counts as success; exit codes other than 0/1 should mark success=False.

Assertions:
- Aggregation counts by tool and category reflect parsed issues.

## Python — Pylint (lint)

Cases:
- Provide sample Pylint JSON containing `error`, `warning`, `convention`, `refactor` messages; verify category/severity mapping:
  - `error`/`fatal` → `category=syntax`, `severity=error`.
  - `warning` → `category=style`, `severity=warning`.
  - `convention`/`refactor` → `category=style`, `severity=info`.
- Return code handling: values with bit 32 set (usage error) → `success=False`; others (with bits 1|2|4|8|16) → `success=True`.

Assertions:
- Normalized fields set; paths and line/column propagated.

## Python — mypy (type)

Cases:
- Parse typical mypy JSON records; each becomes a normalized issue `category=type`; `severity` per item.
- Exit codes 0 or 1 treated as success; others as failure.

Assertions:
- Totals by category include all parsed items under `type`.

## Python — Pyright (type)

Cases:
- Provide sample `--outputjson` diagnostics; map 0-based positions to 1-based line/column.
- Exit codes 0 or 1 treated as success; others as failure.

Assertions:
- Normalized issues present; message, rule/code, severity mapped; category `type`.

## Engine orchestration (integration-lite)

Cases:
- Baseline → mechanical autofix → recheck path:
  - Start with a Python file needing only formatting/import sort.
  - After `S0_MECHANICAL_AUTOFIX`, the `ctx.python_files` list is replaced with validated outputs.
  - Recheck runs and yields zero issues if only formatting was needed.

Assertions:
- FSM transitions as expected; final state either `S_SUCCESS` or escalates when real lint/type issues remain.
## Python — Bandit (security)

Cases:
- Parse sample Bandit JSON with results at varying severities (LOW/MEDIUM/HIGH) and ensure mapping:
  - HIGH → severity=error; MEDIUM → warning; LOW → info; category=security.
- Single-file run produces path and line numbers correctly.

Assertions:
- Normalized fields (tool, path, line, code, category, severity, message) set.
- Success when return code in {0,1}; others mark failure.

## Python — Safety (dependencies/security)

Cases:
- Provide sample Safety JSON lists/objects from different versions; parse into normalized issues with `path=requirements*.txt`.
- When no `requirements*.txt` is present, plugin returns success with zero issues.
- If tool outputs non-JSON (e.g., missing license/db), parser returns success with zero issues.

Assertions:
- Issues have `category=security` and severity mapped by `critical/high/medium/low`.
- Engine aggregation includes Safety issues under `security` category when present.

