---
doc_id: DOC-GUIDE-EXECUTION-CHECKPOINTS-GUIDE-1461
---

# Execution Checkpoints Guide

`.execution/checkpoints/` tracks progress across migration and pipeline runs.

## Purpose
- Persist step-wise progress for resumability.
- Provide audit trail for CI/local runs.

## Location and Format
- Files under `.execution/checkpoints/` (JSONL or JSON, append-only where possible).
- Typical fields: `timestamp`, `step`, `status`, `details`, `hashes` (optional).

## Usage During Migration
- Record completion of major phases (manifests ready, DAGs refreshed, imports rewritten).
- Include `source_hash` from DAG validation when relevant.

## Good Practices
- Append, don’t overwrite.
- Avoid storing secrets; keep entries minimal.
- Prune only after archiving or once a migration is fully signed off.
