---
doc_id: DOC-CORE-UTE-ID-SYSTEM-SPEC-200
---

# ID_SYSTEM_SPEC.md
Version: 1.0.0
Status: DRAFT
Spec ID: ID-SYSTEM-SPEC-V1

## 0. Purpose & Scope

This specification defines the **ID system** used to link documentation, code, and supporting artifacts in a deterministic, machine-friendly way.

The ID system is intentionally minimal:

- There is **one primary identifier type** for cross-artifact linkage: `doc_id`.
- `doc_id` is used to connect:
  - Documentation units (specs, design docs)
  - Code files (scripts, modules, tests)
  - Non-code artifacts (schemas, configs, diagrams, binaries)

This spec uses RFC 2119 keywords (MUST, SHOULD, MAY) in a normative sense.

---

## 1. Core Principles

### ID-SYS-001 – Single Linking ID (MUST)

- The system **MUST** use a **single primary ID type** for linking docs, code, and artifacts: `doc_id`.
- `doc_id` **MUST** be the only cross-artifact identifier used for:
  - Documentation frontmatter
  - Code file `DOC_LINK` headers
  - Non-code sidecar metadata
  - Optional central indexes

Domain-specific identifiers (e.g., `pattern_id`, `PAT-CHECK-001`, `TASK-001`) **MAY** exist within documents and data structures but **MUST NOT** replace `doc_id` as the cross-artifact join key.

### ID-SYS-002 – Human-Readable and Stable (MUST)

- `doc_id` **MUST** be:
  - Short
  - Human-readable
  - Stable across routine edits to content
- `doc_id` **MUST** describe a logical documentation unit (spec, design, contract), not a single file revision.

---

## 2. `doc_id` Specification

### ID-SYS-101 – Format (MUST)

- `doc_id` **MUST** match the following pattern:

  ```text
  [A-Z0-9]+(-[A-Z0-9]+)*
