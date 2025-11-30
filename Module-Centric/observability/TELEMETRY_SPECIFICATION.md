---
doc_id: DOC-GUIDE-TELEMETRY-SPECIFICATION-1462
---

# Telemetry Specification

Defines what is logged to `.execution/telemetry.jsonl` (or similar) during migration and operations.

## Event Shape (JSONL)
- `timestamp` (ISO-8601 UTC)
- `event_type` (e.g., `dag_refresh`, `dag_validate`, `import_rewrite`, `test_run`)
- `module_id` or `pipeline_id` (optional, when scoped)
- `status` (`ok`, `warn`, `error`)
- `details` (message)
- `hashes` (optional; e.g., DAG `source_hash`)

## Required Events
- DAG refresh start/finish with status and hash
- DAG validation result
- Import rewrite result
- Manifest validation result
- Test run result (if executed as part of migration)

## Retention and Hygiene
- Rotate or archive telemetry after major migrations.
- Do not log secrets or PII.
- Keep entries concise to aid diff/grep during failures.
