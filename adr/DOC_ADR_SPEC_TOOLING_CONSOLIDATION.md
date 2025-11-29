---
status: canonical
doc_type: adr
module_refs: []
script_refs: []
doc_id: DOC-ARCH-ADR_SPEC_TOOLING_CONSOLIDATION-009
---

# ADR-0005: Spec tooling consolidation

## Status
Accepted

## Context
We have two parallel approaches for managing specifications:

1. SPEC_MGMT_V1 (sidecars + suite-index): implemented via tools under `tools/spec_*`
   (renderer, guard, resolver, indexer, patcher). These rely on `docs/.index/suite-index.yaml`
   and paragraph-level sidecar files.

2. OpenSpec (source-of-truth in `openspec/specs/` plus `openspec/changes/`), which aligns
   with spec-driven development for AI coding assistants and integrates well with our pipeline
   via a change→bundle→workstream flow.

Maintaining both increases drift and complexity.

## Decision
- Treat `openspec/specs/` as the primary source of truth for specifications.
- Keep SPEC_MGMT_V1 tools available but do not expand them. Prefer OpenSpec-centric flows.
- Adapt `tools/spec_renderer/renderer.py` to render from OpenSpec when a suite-index
  is not present (fallback mode). This provides a single rendering entry point without
  requiring sidecars.
- Document SPEC_MGMT_V1 tools as legacy/optional; teams may continue using them for
  paragraph-level workflows, but new automation should prefer OpenSpec.

## Consequences
- Reduced duplication and drift; single canonical spec location under `openspec/specs/`.
- Minimal code changes (renderer fallback) to keep compatibility while guiding new usage.
- Future automation and validators should operate on OpenSpec (e.g., `openspec/specs` and
  `openspec/changes`).

## Migration
- Existing flows using suite-index/sidecars continue to work unchanged.
- For OpenSpec-only projects, `tools/spec_renderer/renderer.py` now renders specs by scanning
  `openspec/specs/**/spec.md`.

