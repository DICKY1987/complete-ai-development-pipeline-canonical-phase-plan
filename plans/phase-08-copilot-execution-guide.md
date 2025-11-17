## Copilot execution guide: complete the error pipeline

This guide instructs GitHub Copilot (or a similar AI coding assistant) to finish the
remaining work for the error pipeline, aligned with the Operating Contract, state-machine
spec, and architecture in `MOD_ERROR_PIPELINE`.

### Objectives

- Finish plugin coverage across Python, PowerShell, JS/TS, Markdown/YAML/JSON, and cross-cutting tools.
- Maintain determinism, temp-dir isolation, stable ordering, and scrubbed environments.
- Ensure mechanical autofix path is effective (fix → recheck) without mutating originals.
- Provide robust parsing into normalized issues and correct aggregation/reporting.
- Add test specs alignment and minimal smoke scaffolding (separate executor implements tests).

### References (treat as authoritative)

- `MOD_ERROR_PIPELINE/ERROR_Operating Contract.txt:1`
- `MOD_ERROR_PIPELINE/state-machine specification.txt:1`
- `MOD_ERROR_PIPELINE/WS-ERROR-ENGINE-CORE.md:1`
- `MOD_ERROR_PIPELINE/ARCHITECTURE.md:1`
- Existing code under:
  - `MOD_ERROR_PIPELINE/*.py`
  - `src/utils/*`, `src/pipeline/*`, `src/plugins/*`
  - Plans: `plans/phase-07-plugin-suite-expansion.md:1`, `plans/test-specs-plugins.md:1`

### Working rules for Copilot

- Respect non-destructive constraints: originals are never modified; fixes occur in temp dir and outputs are copied to validated files.
- Prefer deterministic behavior: stable plugin discovery and topological ordering via `requires` in `manifest.json`.
- Use `scrub_env()` and `shell=False` for all subprocess calls; apply timeouts (120–180s) and `cwd=file_path.parent`.
- Parse tool outputs to normalized issues: `tool,path,line,column,code,category,severity,message`.
- Treat tool absence as a graceful skip (plugin `check_tool_available()` returns False → not registered).
- Keep edits minimal and focused; follow existing style; do not refactor unrelated areas.

### Environment & commands

- Run scripts: `python scripts/run_error_engine.py <files>`
- State-machine tick: `python src/pipeline/error_pipeline_cli.py --run-id RUN --ws-id WS --py file.py`
- Use SQLite by setting `ERROR_PIPELINE_DB=.state/pipeline.db` (optional).
- Install tools locally as needed (developer workstation), not in code.

### Milestones & deliverables

- M1 Python baseline (DONE)
  - isort (fix), Black (fix), Ruff (lint), Pylint (lint), mypy/Pyright (types)
- M2 Python security/deps (DONE)
  - Bandit, Safety
- M3 PowerShell
  - PSScriptAnalyzer plugin; optional Pester summary collector
- M4 JS/TS
  - Prettier (fix), ESLint (lint)
- M5 Markup/data
  - yamllint (YAML), markdownlint-cli (lint), mdformat (fix), jq (JSON syntax)
- M6 Cross-cutting
  - codespell (spelling), Semgrep (security patterns), Gitleaks (secrets)
- M7 Testing & docs handoff
  - Ensure plan and test-specs cover all tools; minor smoke scaffolding if needed

### Detailed tasks per milestone

- PowerShell (M3)
  - PSScriptAnalyzer
    - Path: `src/plugins/powershell_pssa/{manifest.json, plugin.py}`
    - Extensions: `ps1, psm1`
    - Command: `pwsh -NoProfile -Command Invoke-ScriptAnalyzer -Path <file> -Recurse -Severity Error,Warning,Information | ConvertTo-Json -Depth 5`
    - Parse: Severity→severity; RuleName→code; category `style` (parse errors→`syntax`). Success on 0.
  - Pester (optional): collect failures as `test_failure` issues; do not fail plugin.

- JS/TS (M4)
  - Prettier (fix)
    - Path: `src/plugins/js_prettier_fix/*`; Extensions: `js,jsx,ts,tsx,json,md,yml,yaml`
    - Command: `prettier --write <file>`; no issues; success 0.
  - ESLint (lint)
    - Path: `src/plugins/js_eslint/*`; Extensions: `js,jsx,ts,tsx`
    - Command: `eslint -f json <file>`; severities 2→`error`, 1→`warning`; category `style`.
    - Success 0/1; parse list into normalized issues.

- Markup/data (M5)
  - yamllint: `yamllint -f parsable <file>`; category `style`; parser errors→`syntax`; success 0/1.
  - markdownlint-cli: `markdownlint -j <file>` or parse text; category `style`; success 0/1.
  - mdformat (fix): `mdformat <file>`; no issues; success 0.
  - jq (JSON syntax): `jq empty <file>`; stderr→single `syntax/error` issue on failure.

- Cross-cutting (M6)
  - codespell: parse stdout to `style/warning` issues.
  - Semgrep: `semgrep --json --quiet --include <file>`; map severities; `security`.
  - Gitleaks: `gitleaks detect --no-git --no-banner --report-format json --source <dir>`; filter to file; `security/error`.

### Manifest & ordering

- Enforce fix-before-check via `requires` in `manifest.json`.
- Python: `python_isort_fix` → `python_black_fix` → `python_ruff|python_pylint|python_mypy|python_pyright|python_bandit|python_safety`.
- JS/TS: `js_prettier_fix` → `js_eslint`.
- Markdown: `md_mdformat_fix` → `md_markdownlint`.
- Cross-cutting run after language-specific tools.

### Normalization mapping (quick reference)

- Python: Ruff/Pylint → `style`; mypy/Pyright → `type`; Bandit/Safety → `security`; Black/isort/mdformat/prettier → none.
- PowerShell: PSScriptAnalyzer → `style` (parse errors → `syntax`).
- JS/TS: ESLint → `style`.
- Data/markup: yamllint/markdownlint → `style`; jq → `syntax`.
- Cross-cutting: codespell → `style`; Semgrep/Gitleaks → `security`.

### Testing handoff

- Do not add tests here; implement per `plans/test-specs-plugins.md:1` separately.
- Keep parsers tolerant to optional fields and version differences.

### Acceptance criteria

- Engine discovers and orders plugins via `requires` deterministically.
- Tools absent → plugin skipped; tools present → execution with normalized issues.
- Fixers never emit issues and only modify temp copies.
- Mechanical autofix updates `ctx.python_files` to validated outputs before recheck.
- Reports aggregate by tool and category; JSONL rotation remains intact.
- Docs list supported tools and ordering.

### Risks & mitigations

- Output format drift: tolerant parsing; detect optional fields.
- Slow/hanging tools: enforce timeouts, avoid network.
- Windows path quirks: use `Path`, avoid `shell=True`.

### Definition of done

- All milestone plugins implemented with manifests and parsers/fixers.
- Ordering enforced; mechanical autofix verified by manual smoke.
- `plans/test-specs-plugins.md` covers all tools for a test executor.
- README/docs note tool matrix and ordering.

