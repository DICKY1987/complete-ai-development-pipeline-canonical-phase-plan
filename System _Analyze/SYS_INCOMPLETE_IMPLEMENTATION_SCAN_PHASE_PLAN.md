# Phase 5X - Incomplete Implementation Scanner Execution Plan

**Objective**: Implement and operationalize the incomplete implementation scanner described in `incomplete_implementation_scan_spec.json` and `INCOMPLETE_IMPLEMENTATION_RULES.md`, closing identified gaps and shipping a repeatable execution pattern with CI gates.

## Scope
- Codebase-wide scan for stubs, empty structures, dangling references, and orphan modules.
- Outputs: inventories, findings (JSONL), classified summary (JSON/MD), CI gate status.
- Excludes: language support beyond Python/TS/JS for this phase (log as info).

## Milestones (ordered)
1) Config + wiring
2) Inventory (files/dirs)
3) Stub detection
4) Structure/reference checks
5) Dependency graph + orphans
6) Severity/classification
7) Reports + UX
8) Allowlist + quality gates
9) CI/pre-commit integration

## Execution Patterns per Milestone

### 1) Config + Wiring
- Single config object: `root`, `ignored_paths`, `tiny_file_line_threshold`, `severity_rules`, `allowlist_markers`, `entrypoints`.
- CLI shape: `python tools/scan_incomplete_implementation.py --root . --output .state/incomplete_scan_summary.json --inventory .state/file_inventory.jsonl`.
- Persist defaults alongside spec; fail fast on missing root or write locations.

### 2) Inventory
- Walk `root`, skip `ignored_paths`.
- Emit `file_inventory.jsonl`: `{kind:"file", path, ext, size_bytes, num_lines}`; `dir_inventory.jsonl`: `{kind:"dir", path, num_files, num_subdirs}`.
- Flag empties/tiny files inline: attach `reason` when `num_lines <= tiny_file_line_threshold`.
- Cache support (mtime/hash) optional; log when skipped due to cache hit.

### 3) Stub Detection (language-aware)
- Regex scan for TODO/FIXME/WIP/XXX/STUB markers.
- Per-language no-op detection:
  - Python: `pass`, `...`, `raise NotImplementedError`, `return None` w/ TODO.
  - TS/JS: `throw new Error("Not implemented")`, empty body `{}` with TODO.
- Optional Python AST pass to catch empty functions/classes; include `line` and `symbol`.
- Output: `stub_candidates.jsonl` with `kind`, `path`, `symbol`, `line`, `reason`, `language`.

### 4) Structure + References
- Parse ABC/interface requirements vs. concrete implementations; emit missing overrides.
- Parse configs/routes/entrypoints/tests for referenced symbols (pyproject entrypoints, Flask/FastAPI/Click/Typer patterns, YAML/JSON plugin registries).
- Cross-check references against inventory + stub list; emit `missing_reference` and `abstract_vs_concrete` findings.
- Outputs: `missing_reference_findings.jsonl`, `abstract_vs_concrete_findings.jsonl`.

### 5) Dependency Graph + Orphans
- Extract imports per file (Python import/From, TS/JS import/require).
- Build adjacency and inbound counts; mark entrypoints (main guards, CLI files, route registries) to avoid false orphans.
- Emit `dependency_graph.json`, `orphan_module_findings.jsonl` with reason (no inbound, not entrypoint, tiny body).

### 6) Severity + Classification
- Merge findings; apply severity rules:
  - Critical: missing implementation referenced by config/tests; stubs in core/public API.
  - Major: stubs in used modules; abstract methods unimplemented.
  - Minor/Info: experimental/archive paths, tiny harmless files.
- Apply path multipliers (core/engine/error x3; public/cli x2; experiments/archive x0.1/x0.01).
- Output: `classified_findings.jsonl` with context (module/package/group).

### 7) Reports + UX
- JSON summary: counts by kind/severity, top critical items, stats (stub_functions, stub_classes, missing_refs, empty_dirs).
- Markdown summary (optional) with top N critical/major items and remediation hints.
- Clear exit codes: 0=pass,1=gate fail,2=config/environment error.

### 8) Allowlist + Quality Gates
- Load `incomplete_allowlist.yaml`; honor inline markers `# INCOMPLETE_OK`, `# STUB_ALLOWED`.
- Downgrade to `allowed_stub` and exclude from gates; include reason.
- Gates: `max_critical=0`, `max_major=10`, `prevent_regressions=true`.
- Output: `final_findings.jsonl`; gate status in summary.

### 9) CI / Pre-Commit Integration
- CI job: `python tools/scan_incomplete_implementation.py --root . --output .state/incomplete_scan_summary.json --fail-on-gate`.
- Optional pre-commit: lightweight run on changed files (reuse inventory cache).
- PR comment hook (optional): post top critical/major deltas.

## Gap Closures & Improvements
- Add language registry and log unsupported files as `info`.
- Normalize thresholds in one config block to avoid drift between doc and code.
- Expand config parsers: pyproject entrypoints, FastAPI/Flask routes, Click/Typer CLIs, YAML plugin registries.
- Add caching layer (mtime/hash) to speed repeated scans.
- Tests: fixtures for stubs, allowlist markers, missing references, orphan detection; mirror under `tests/` with markers; add new suites to `tests/TEST_INDEX.yaml` if created.
- Documentation: README for scanner CLI with examples; sample outputs mirroring spec; list exit codes.

## Acceptance Criteria
- All pipeline outputs written to `.state/` (or configured path) with schema fidelity.
- Gate enforcement matches spec: critical=0, major<=10, allowlist ignored by gates.
- Classified findings include `kind`, `path`, `severity`, `reason`, `language|null`, `line|null`, `context`.
- Tests cover: inventory tiny-file detection, stub detection per language, allowlist handling, missing reference detection, orphan detection, severity scoring.

## Runbook (happy path)
1) `python tools/scan_incomplete_implementation.py --root . --output .state/incomplete_scan_summary.json`
2) Inspect `.state/incomplete_scan_summary.json` (and `.md` if enabled) for critical/major items.
3) Remediate or allowlist with justification; rerun until gates pass.
4) CI enforces gates on PRs; failures block merge until fixed or allowed.
