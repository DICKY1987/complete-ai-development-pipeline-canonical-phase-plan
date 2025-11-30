---
doc_id: DOC-GUIDE-PHASE-PLAN-PATH-REFACTORING-168
---

# Path refactoring phase plan

## Overview
Migrate the codebase from hard-coded paths and imports to the key-based path abstraction defined
in `PATH_ABSTRACTION_SPEC.md`, and use the discovery and enforcement tooling described in
`DOC_HARDCODED_PATH_INDEXER.md` to find and gate legacy patterns. The phases below are structured
for automation: scan, cluster, key definition, refactor, gate, and validate.

## Phases

### PH01_DISCOVER — Repository scan initialization
- **PHASE_ID:** PH01_DISCOVER
- **NAME:** Repository scan initialization
- **GOAL:** Produce a fresh `refactor_paths.db` that indexes all hard-coded paths/imports across
  code, configs, and docs.
- **ENTRY CONDITIONS:** Repository root available; Python env with required deps; scanner scripts
  present (`scripts/paths_index_cli.py`); working tree recorded for rollback.
- **EXIT CONDITIONS:** `refactor_paths.db` exists with non-zero occurrences; scan log captured;
  scan parameters stored for reproducibility.
- **INPUTS:** Repository root; optional existing `refactor_paths.db`; `.aiignore`/`.gitignore`
  patterns; PATH_ABSTRACTION_SPEC reference for context.
- **OUTPUTS:** Fresh `refactor_paths.db`; scan log (text/JSON); timestamped run metadata.
- **HIGH-LEVEL TASKS:**
  1. Ensure clean or recorded working tree state.
  2. Create or reset `refactor_paths.db`.
  3. Run full scan from repo root with section detection enabled.
  4. Store scan command and arguments for reproducibility.
  5. Archive scan log and db location for downstream phases.
- **MAPPED EXECUTION PATTERNS:** PAT_SCAN_REPO_FOR_PATHS, PAT_PHASE_VALIDATION_AND_LOGGING.

### PH02_CLUSTER — Occurrence summarization and batching
- **PHASE_ID:** PH02_CLUSTER
- **NAME:** Occurrence summarization and batching
- **GOAL:** Convert raw scan results into prioritized batches grouped by kind, section, and
  path similarity to drive scoped refactors.
- **ENTRY CONDITIONS:** Completed PH01 with valid `refactor_paths.db`.
- **EXIT CONDITIONS:** Machine-readable cluster report (e.g., JSON/YAML) with batches labeled by
  section/kind; prioritization rubric recorded.
- **INPUTS:** `refactor_paths.db`; repo layout metadata (sections); PATH_ABSTRACTION_SPEC for
  namespace cues.
- **OUTPUTS:** Cluster report; summary stats; shortlist of high-priority batches.
- **HIGH-LEVEL TASKS:**
  1. Run summary/export commands to get counts by kind/section.
  2. Derive clustering rules (e.g., by directory, file extension, shared prefixes).
  3. Emit batch definitions with explicit occurrence lists.
  4. Rank batches by risk/impact (e.g., code before docs, core before tests).
  5. Store reports for reuse across runs.
- **MAPPED EXECUTION PATTERNS:** PAT_SUMMARIZE_AND_CLUSTER_OCCURRENCES,
  PAT_PHASE_VALIDATION_AND_LOGGING.

### PH03_KEY_DEFINITION — Registry key creation and updates
- **PHASE_ID:** PH03_KEY_DEFINITION
- **NAME:** Registry key creation and updates
- **GOAL:** Ensure every targeted batch has stable keys in `config/path_index.yaml`, ready for
  call-site rewrites.
- **ENTRY CONDITIONS:** Cluster report with selected batch; existing or new
  `config/path_index.yaml`; resolver library available (`src/path_registry.py`).
- **EXIT CONDITIONS:** Added/updated keys committed to `config/path_index.yaml`; YAML validated;
  optional dry-run resolution proves keys resolve to expected paths.
- **INPUTS:** Batch definition; current `config/path_index.yaml`; PATH_ABSTRACTION_SPEC key format;
  repo path structure.
- **OUTPUTS:** Updated `config/path_index.yaml`; key resolution check log; change summary.
- **HIGH-LEVEL TASKS:**
  1. Identify candidate keys (namespaced, dotted) for each batch target path.
  2. Add or update entries in `config/path_index.yaml` following schema.
  3. Maintain descriptions/sections for traceability.
  4. Run YAML lint/parse and uniqueness checks.
  5. Optionally invoke resolver to validate key/path existence.
- **MAPPED EXECUTION PATTERNS:** PAT_DEFINE_OR_UPDATE_PATH_KEYS, PAT_PHASE_VALIDATION_AND_LOGGING.

### PH04_REFACTOR — Call-site rewrites to key-based resolution
- **PHASE_ID:** PH04_REFACTOR
- **NAME:** Call-site rewrites to key-based resolution
- **GOAL:** Replace hard-coded paths/imports in the selected batch with registry-driven lookups
  while preserving behavior.
- **ENTRY CONDITIONS:** Keys for batch paths exist; occurrence list for batch is available; tests
  runnable for affected areas.
- **EXIT CONDITIONS:** Batch occurrences updated to use `src/path_registry.py` or CLI; configs/docs
  updated accordingly; code/config parse cleanly; local checks pass for touched areas.
- **INPUTS:** Batch occurrence list; updated `config/path_index.yaml`; resolver API/CLI; source
  files per occurrence.
- **OUTPUTS:** Refactored files; mapping of old literal -> new key; before/after occurrence counts.
- **HIGH-LEVEL TASKS:**
  1. Map each literal/import to a registry key from PH03.
  2. Rewrite code to call `resolve_path(key)` or equivalent CLI usage.
  3. Adjust configs/docs to reference keys or resolved paths via scripts where applicable.
  4. Keep changes atomic per batch to simplify review.
  5. Run syntax/lint checks and targeted tests for touched modules.
- **MAPPED EXECUTION PATTERNS:** PAT_REWRITE_CALL_SITES_TO_KEYS,
  PAT_PHASE_VALIDATION_AND_LOGGING.

### PH05_GATING — Regression gate configuration
- **PHASE_ID:** PH05_GATING
- **NAME:** Regression gate configuration
- **GOAL:** Enforce that banned hard-coded patterns do not reappear by wiring the indexer gate into
  CI and local workflows.
- **ENTRY CONDITIONS:** Updated registry and refactors applied for at least one batch; gate
  patterns defined or derivable from DOC_HARDCODED_PATH_INDEXER.md.
- **EXIT CONDITIONS:** Gate command defined and runnable; CI/local scripts updated; failing gate
  output is actionable.
- **INPUTS:** `refactor_paths.db`; gate regex list; CI configuration hooks; PATH_ABSTRACTION_SPEC
  for allowed usage.
- **OUTPUTS:** Gate configuration (command snippets, scripts); gate run log; documented failure
  handling instructions.
- **HIGH-LEVEL TASKS:**
  1. Define regex filters for legacy paths/imports per DOC_HARDCODED_PATH_INDEXER.md.
  2. Run `gate` against the latest `refactor_paths.db`.
  3. Wire gate into CI/local scripts (e.g., test pipeline) with clear failure messaging.
  4. Store gate logs and thresholds for future runs.
  5. Document how to refresh the DB before gate runs.
- **MAPPED EXECUTION PATTERNS:** PAT_RUN_GATE_AND_ENFORCE_NO_REGRESSIONS,
  PAT_PHASE_VALIDATION_AND_LOGGING.

### PH06_VALIDATION — Consolidated validation and reporting
- **PHASE_ID:** PH06_VALIDATION
- **NAME:** Consolidated validation and reporting
- **GOAL:** Provide end-of-cycle validation that keys resolve, gates pass, and regression risk is
  minimized, with structured logs for auditability.
- **ENTRY CONDITIONS:** Refactor batches completed; gate configured; tests runnable.
- **EXIT CONDITIONS:** Tests/gates executed; key resolution spot-checks logged; structured phase
  report emitted with before/after metrics.
- **INPUTS:** Updated code/config/docs; `config/path_index.yaml`; `refactor_paths.db`; validation
  scripts.
- **OUTPUTS:** Validation log (JSON/YAML/Markdown); metrics on occurrences reduction; list of
  remaining debt, if any.
- **HIGH-LEVEL TASKS:**
  1. Run targeted or full test suite relevant to touched areas.
  2. Execute gate in strict mode to confirm no regressions.
  3. Perform key resolution sanity checks across representative keys.
  4. Compare occurrence counts before vs after and note residual debt.
  5. Publish structured validation report for archiving.
- **MAPPED EXECUTION PATTERNS:** PAT_PHASE_VALIDATION_AND_LOGGING,
  PAT_RUN_GATE_AND_ENFORCE_NO_REGRESSIONS.

## Phase ordering and parallelism
- PH01 through PH03 are sequential because downstream phases depend on the scan, clustering, and
  key availability.
- PH04 can run in parallel per batch once PH03 defines the required keys; isolate batches by
  section (e.g., `src/`, `tests/`, `docs/`) to parallelize safely.
- PH05 should follow at least one successful PH04 batch; expanding gate patterns can be iterative
  but must run after each batch when new literals are removed.
- PH06 runs after each batch for incremental assurance and again after the final batch.
- Guardrails: no key renames without dedicated review; keep refactor batches small with passing
  tests before proceeding; always refresh `refactor_paths.db` before gate runs to keep results
  aligned with code state.
