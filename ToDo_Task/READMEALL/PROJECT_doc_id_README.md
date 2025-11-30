---
doc_id: DOC-GUIDE-PROJECT-DOC-ID-README-1585
---

# DOC ID Module

This module centralizes every artifact that defines, documents, or operates the
repository-wide document identifier system.

## Contents

- `DOC_ID_REGISTRY.yaml` – canonical list of minted identifiers plus migration
  queue metadata.
- `DOC_ID_FRAMEWORK.md`, `DOC_ID_EXECUTION_PLAN.md`,
  `DOC_ID_PARALLEL_EXECUTION_GUIDE.md`,
  `DOC_ID_PROJECT_PHASE*.md`, `DOC_ID_PROJECT_SESSION_REPORT.md` – reference
  documentation for the doc_id framework, execution strategy, and project
  reports.
- `docid_batches/`, `docid_deltas/`, `docid_reports/` – operational data used by
  the CLI (batch specs, delta JSONL files, dry-run + merge reports, inventory
  exports).
- `doc_id_registry_cli.py` – Python CLI for minting, searching, validating, and
  indexing doc_ids.
- `create_docid_worktrees.ps1` – PowerShell helper that provisions dedicated
  worktrees for large-scale registry work.
- `PLAN_DOC_ID_PHASE3_EXECUTION__v1.md` – current expansion plan for the doc_id
  system.

Wrapper scripts remain under `scripts/` so existing commands keep working:
`scripts/doc_id_registry_cli.py` forwards to this module, and
`scripts/create_docid_worktrees.ps1` dispatches to the module script.
