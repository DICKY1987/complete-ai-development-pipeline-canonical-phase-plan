# Plugin suite expansion plan

This plan adds a complete, deterministic plugin suite across Python, PowerShell, JS/TS,
markup (Markdown/YAML/JSON), and security/secrets tools. It conforms to the Operating
Contract, architecture docs, and the existing engine and state-machine service.

## Objectives

- Provide comprehensive validators and formatters with normalized issue output.
- Maintain determinism: stable ordering, temp-dir isolation, env scrubbing, timeouts.
- Support auto-fix where safe; recheck on validated outputs (non-destructive).
- Ensure minimal external assumptions; degrade gracefully if a tool is missing.

## Scope

- Implement and register plugins with manifests under `src/plugins/<tool>/`.
- Standardize parsing, category/severity mapping, and success-code handling.
- Define DAG ordering for fix-before-check chains within each language.
- Add focused tests per plugin (parse fixtures; skip if tool not installed).

Out-of-scope:
- Full tool installation automation and CI caching (tracked separately).
- Advanced per-repo configuration beyond `manifest.json` conventions.

## References

- Operating Contract: `MOD_ERROR_PIPELINE/ERROR_Operating Contract.txt:1`
- Architecture: `MOD_ERROR_PIPELINE/ARCHITECTURE.md:1`
- Engine: `MOD_ERROR_PIPELINE/pipeline_engine.py:1`
- Service/State machine: `src/pipeline/*.py`

## Target plugin matrix

- Python
  - Lint/format/type: Ruff, Black (fix), isort (fix), Pylint, mypy, pyright
  - Security: Bandit
  - Dependencies: Safety (optional offline DB or allow network opt-out)
  - Optional: pyupgrade (fix)
- PowerShell
  - Static analysis: PSScriptAnalyzer
  - Tests: Pester (report-only integration, optional)
- JavaScript/TypeScript
  - Lint/format: ESLint, Prettier (fix)
- Markup / data
  - YAML: yamllint
  - Markdown: markdownlint-cli, mdformat (fix)
  - JSON: `jq` validation (syntax-only)
- Cross-cutting
  - Spelling: codespell
  - Security (multi-language): Semgrep
  - Secrets: Gitleaks

## Ordering (DAG guidelines)

- Python
  1) isort (fix)
  2) black (fix)
  3) ruff
  4) pylint
  5) mypy / pyright (parallel in concept; ordered deterministically)
  6) bandit
  7) safety (per `requirements*.txt` when available)
- JS/TS
  1) prettier (fix)
  2) eslint
- Markdown
  1) mdformat (fix)
  2) markdownlint-cli
- YAML/JSON: yamllint before downstream schema validation (future); `jq` for syntax
- Cross-cutting: codespell then semgrep, gitleaks last

## Manifest conventions (update across plugins)

- Fields
  - `plugin_id`, `name`, `file_extensions`, `requires`, `tool.success_codes`
- Optional
  - `tool.fix_args` for fix-capable tools (where CLI supports it)
  - `patterns` (globs) to refine applicability beyond extension
- Success codes
  - Use tool docs: ruff `[0,1]`; eslint `[0,1]`; others `[0]`

## Normalization rules

- Issue fields: `tool,path,line,column,code,category,severity,message`
- Category mapping
  - Ruff/eslint/yamllint/markdownlint: `style`
  - Black/isort/mdformat/prettier: no issues on success; treat failures as `formatting`
  - Pylint: `style` for C/R/W; `other` for refactors; map E/F to `syntax`
  - mypy/pyright: `type`
  - PSScriptAnalyzer: map rules to `style`/`syntax` based on severity/category
  - Bandit/Safety/Semgrep: `security`
  - Gitleaks: `security` (secrets)
  - codespell: `style` (spelling)
- Severity mapping
  - Tool “error”/“warning” → `error`/`warning`; rest → `info`

## Milestones

- M1: Python baseline
  - isort (fix), black (fix) — already added black; add isort
  - ruff — already added; ensure conflict-free with black/isort
  - pylint, mypy, pyright parsers
- M2: Python security and deps
  - bandit parser
  - safety (optional network; add offline/skip mode)
- M3: PowerShell
  - PSScriptAnalyzer parser; Pester summary collector (optional)
- M4: JS/TS
  - prettier (fix), eslint parser
- M5: Markup/data
  - yamllint, markdownlint-cli, mdformat (fix), jq (JSON syntax)
- M6: Cross-cutting
  - codespell, semgrep, gitleaks parsers
- M7: Test coverage & docs
  - Parsing fixtures; skip tests when tools missing
  - Update README with tool matrix and ordering

## Tasks per plugin (repeatable template)

1) Add `src/plugins/<id>/manifest.json` with `file_extensions`, `requires`, `tool.success_codes`.
2) Implement `plugin.py`:
   - `check_tool_available()` via `shutil.which`
   - `build_command(file_path)` with JSON output if supported
   - `execute()` with `scrub_env()`, `timeout`, `cwd=file_path.parent`, `shell=False`
   - Parse stdout/stderr → normalized issues; map categories/severity
3) Add unit tests
   - Given sample JSON output, parser produces expected issues
   - Mark `pytest.mark.skipif` when tool not available; otherwise smoke-run on temp file

## Acceptance criteria

- Engine discovers and runs new plugins with stable DAG ordering.
- For each plugin, at least one parsing test passes locally.
- Auto-fix tools modify temp copies; recheck uses validated outputs; originals untouched.
- Normalized issues obey category/severity mapping and aggregate correctly in reports.
- Missing tools cause graceful skip; presence triggers execution without errors.
- Documentation lists supported tools, ordering, and known limitations.

## Risks & mitigations

- Tool availability and network constraints
  - Skip when absent; provide local fixtures for parsing tests; avoid network by default.
- Output format drift across tool versions
  - Keep parsers robust to optional fields; add version detection in metadata later.
- Determinism risks from concurrent writes
  - Maintain sequential execution and atomic writes; JSONL rotation already tail-preserving.

## Timeline (indicative)

- Week 1: M1–M2 (Python suite)
- Week 2: M3 (PowerShell), M4 (JS/TS)
- Week 3: M5 (Markup/data), M6 (Cross-cutting)
- Week 4: M7 (tests/docs hardening)

