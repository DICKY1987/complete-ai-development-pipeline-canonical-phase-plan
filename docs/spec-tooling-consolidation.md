# Spec tooling consolidation

This repository standardizes on OpenSpec for specifications while preserving compatibility with
the legacy SPEC_MGMT_V1 toolchain.

## Recommended (OpenSpec-first)
- Author specs in `openspec/specs/**/spec.md` and changes under `openspec/changes/<id>/`.
- Generate normalized bundles: `python -m src.pipeline.openspec_parser --change-id <id> --generate-bundle`.
- Convert to workstreams: `python scripts/generate_workstreams_from_openspec.py --change-id <id> --files-scope <path...>`.
- Validate and run: `python scripts/validate_workstreams.py` then `python scripts/run_workstream.py`.

## Legacy (SPEC_MGMT_V1)
- Tools (sidecars + suite-index) remain available under `tools/spec_*`:
  - `spec_guard/guard.py` — consistency validator
  - `spec_indexer/indexer.py` — sidecar generation and indexing
  - `spec_patcher/patcher.py` — paragraph-level patching
  - `spec_resolver/resolver.py` — ID/anchor resolution to file and ranges
  - `spec_renderer/renderer.py` — unified spec rendering

Notes:
- `spec_renderer/renderer.py` now supports OpenSpec fallback. If `docs/.index/suite-index.yaml`
  is missing, it concatenates `openspec/specs/**/spec.md` in a deterministic order.
- Prefer OpenSpec workflows for new automation. SPEC_MGMT_V1 is retained for teams relying on
  sidecar-based document management.

