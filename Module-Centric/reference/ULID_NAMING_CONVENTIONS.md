---
doc_id: DOC-GUIDE-ULID-NAMING-CONVENTIONS-1466
---

# ULID Naming Conventions

Consistent ULID prefixes let tools verify related artifacts across code, tests, schemas, and docs.

## Prefix and Shape
- Filename prefix: 6-char ULID prefix (e.g., `01JDEX`) + `_` + descriptive slug.
- Full ULIDs (26 chars) may be stored in manifests; filenames keep the 6-char prefix for brevity.
- Examples:
  - `01JDEX_orchestrator.py`
  - `01JDEX_orchestrator.test.py`
  - `01JDEX_orchestrator.schema.json`
  - `01JDEX_module.manifest.json`

## Rules
- One ULID prefix per module; all module artifacts share it.
- Manifests list all ULID artifacts and their paths.
- Avoid collisions: regenerate ULID prefix only when creating a new module, not per file.
- Keep suffixes descriptive and import-safe (no leading digits after the prefix separator).

## Validation
- Manifest check: `ulid_prefix` must match all listed artifacts.
- Repo scan: `rg --files -g '??000?_*.py' modules` (adapt prefix pattern) to spot drift.
- DAG source hash: include ULID-named files when computing DAG `source_hash`.

## Generation Tips
- Use existing ULID generator; avoid timestamps in filenames.
- Do not embed semantic meaning in the ULID; semantics live in manifest fields.
