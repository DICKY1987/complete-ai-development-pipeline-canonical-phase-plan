---
doc_id: DOC-GUIDE-ADR-010-ULID-IDENTITY-1395
---

# ADR-010: ULID Identity System

## Context
Modules need machine-verifiable linkage across code, tests, schemas, and docs. Human-friendly names
alone are insufficient for automation and AI context scoping.

## Decision
- Assign each module a ULID prefix (6 chars) used in all artifact filenames.
- Store full ULIDs (26 chars) in manifests as canonical identity.
- Manifests enumerate all ULID-prefixed artifacts; validators enforce prefix consistency.

## Rationale
- Verifiable grouping: all files sharing the prefix belong to the same module.
- Hashable provenance: ULIDs feed DAG `source_hash` to detect staleness.
- Portability: modules can move without losing identity.

## Consequences
- File creation must include the module ULID prefix.
- Validation scripts must reject mismatched prefixes.
- Renaming ULIDs requires coordinated manifest and DAG refresh.
