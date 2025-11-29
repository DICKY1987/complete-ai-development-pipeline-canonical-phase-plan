---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-SPEC_MANAGEMENT_CONTRACT-042
---

# Specification Management Contract (SPEC_MGMT_V1)

This document defines the contract for multi‑document versioning and specification management in this repository. It standardizes how documents are identified, versioned, linked, and validated so both humans and AI agents can operate deterministically.

## Goals
- Deterministic, auditable document versioning via sidecar metadata files.
- Cross‑document linking with stable IDs and resolvable URIs.
- Unified suite index for rendering, patching, and validation.
- Agent‑friendly tools to index, resolve, patch, render, and guard.

## Sidecar Metadata Format (.sidecar.yaml)
Each Markdown file under `docs/source/` (or designated source root) has a sibling sidecar YAML with combined document and paragraph metadata. Required top‑level fields:
- `document_id` (string): stable identifier (e.g., `01-architecture/00-overview`).
- `title` (string): human‑readable title.
- `version` (string): semver string (e.g., `1.0.0`).
- `category` (string): folder category (e.g., `01-architecture`).
- `last_updated` (string): ISO‑8601 timestamp.
- `authors` (array[string]): list of author names/IDs.

Optional fields:
- `tags` (array[string])
- `depends_on` (array[string])
- `status` (string): one of `draft|review|approved|deprecated`.
- `checksum` (string): SHA‑256 of Markdown file contents.

Paragraph tracking fields coexist in the same file for deterministic patching:
- `file` (string): relative Markdown path.
- `mfid` (string): SHA‑256 of entire file.
- `paragraphs` (array): entries with `anchor`, `start_line`, `end_line`, `mfid`, `id`.

See `schema/sidecar_metadata.schema.yaml` for full schema and validation rules.

## Document Categories
Document categories follow the directory structure under `docs/source/`:
- `01-architecture`
- `02-operating-contract`
- `05-process`, `06-conformance`, `08-ci-cd-gates`, `09-observability-slos`, `10-reference`, `11-developer-experience`, `12-security-supply-chain`

## Cross‑Document Linking
Use resolvable URIs:
- `spec://<VOLUME_KEY>/<SECTION_KEY>[#p-N]` (e.g., `spec://01-architecture/00-overview#p-2`).
- `specid://<ID>` where `<ID>` is a stable paragraph or section ID.

Tools resolve these using `docs/.index/suite-index.yaml` and sidecars.

## Versioning Scheme
- Semver for documents (e.g., `1.2.0`).
- Bump `version` on substantive changes; update `last_updated` and `checksum` automatically via indexer.
- Status transitions: `draft → review → approved → deprecated`.

## Tooling Overview
- `tools/spec_indexer/indexer.py`
  - Scans source, (re)generates/augments sidecars, validates against schema, builds `docs/index.json` and `docs/.index/suite-index.yaml`.
- `tools/spec_resolver/resolver.py`
  - Resolves `spec://` and `specid://` to file paths and paragraph ranges.
- `tools/spec_patcher/patcher.py`
  - Patches a paragraph by ID, updates sidecar and suite index.
- `tools/spec_renderer/renderer.py`
  - Renders unified spec view using `suite-index.yaml` ordering.
- `tools/spec_guard/guard.py`
  - Validates consistency across index, sidecars, and files.

## Contract Version
- CONTRACT_VERSION: SPEC_MGMT_V1

## Usage
- Index & validate: `python tools/spec_indexer/indexer.py --source "docs/source" --output docs/index.json`
- Render combined view: `python tools/spec_renderer/renderer.py --output build/spec.md`
- Resolve link: `python tools/spec_resolver/resolver.py spec://01-architecture/00-overview#p-2`
- Patch paragraph: `python tools/spec_patcher/patcher.py --id <ID> --text "New paragraph"`
- Guard: `python tools/spec_guard/guard.py`
