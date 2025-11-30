---
doc_id: DOC-GUIDE-SECTION-REFACTOR-PLAN-1252
---

# Section refactor plan (WS‑02)

This document captures the section mapping configuration and analysis derived from the WS‑01
hardcoded path indexer. It defines the target directory structure and initial priorities for the
data‑driven refactor.

## Objectives

- Establish an authoritative section map (`config/section_map.yaml`).
- Use scan data to identify highest‑impact areas and sequencing.
- Document risks and guardrails for upcoming automated rewrites.

## Scan insights (from refactor_paths.db)

Occurrences by tracked section (descending):

- docs/: 219
- scripts/: 188
- src/: 141
- tools/: 52
- tests/: 50
- MOD_ERROR_PIPELINE: 34
- schema/: 22
- config/: 18
- workstreams/: 15
- gui/: 11
- openspec/: 9
- PHASE_DEV_DOCS: 8
- sandbox_repos/: 1

Notes:

- The majority of path‑like references are in docs and scripts. These are low‑risk refactors and
  ideal for early execution to drive down noise.
- Code imports (Python) are captured but not rewritten in WS‑02; they inform boundaries for later
  phases.

## Target directory structure

The canonical structure (no changes proposed in WS‑02; serves as normalization map):

- docs/
- scripts/
- tools/
- src/
- tests/
- config/
- schema/
- openspec/
- workstreams/
- PHASE_DEV_DOCS/
- MOD_ERROR_PIPELINE/
- gui/
- sandbox_repos/

See `config/section_map.yaml` for the machine‑readable mapping, normalization rules, and exclusions.

## Risks and guardrails

- Medium risk: `src/`, `schema/`, and `config/` due to downstream tooling expectations.
- Exclude directories per config to avoid churn: `.venv`, caches, build artifacts, logs, state.
- Prefer relative paths within sections; ban absolute local filesystem paths in shared logic.

## Sequencing recommendations

1. Normalize docs/ and scripts/ references using `mapping-rules` (low risk).
2. Validate and stage config/ and schema/ rewrites with dry‑run and diff checks.
3. Review `MOD_ERROR_PIPELINE` and `gui` references for section boundary issues.
4. Defer `src/` moves/re‑writes to WS‑03+ where import resolution and tests accompany changes.

## Next actions

- Lock `config/section_map.yaml` in the repo (PR review).
- Generate targeted reports to enumerate candidates for rewrite by section.
- Prepare automation to apply non‑destructive path normalization (dry‑run + report).
