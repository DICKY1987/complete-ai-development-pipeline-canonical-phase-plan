---
doc_id: DOC-GUIDE-ADR-011-HYBRID-IMPORTS-1440
---

# ADR-011: Hybrid Import Strategy (ULID Filenames + Clean Imports)

## Context
ULID-prefixed filenames are useful for identity but cannot be imported directly in Python due to
leading digits. We need both machine identity and clean import paths.

## Decision
- Keep ULID-prefixed filenames for artifacts.
- Require `__init__.py` in each module to re-export public symbols under import-safe names.
- Optionally add alias files (e.g., `orchestrator.py`) that delegate to ULID files for readability.
- Use automated import rewrite scripts to enforce clean imports.

## Rationale
- Preserves ULID identity while maintaining Python compatibility.
- Keeps public API stable even if ULID-prefixed filenames change internally.
- Simplifies AI tooling: import paths are predictable and do not include numeric prefixes.

## Consequences
- Every module must maintain `__init__.py` exports.
- Import rewrites are part of migration and must be validated.
- Code review should reject direct imports of numeric filenames.
