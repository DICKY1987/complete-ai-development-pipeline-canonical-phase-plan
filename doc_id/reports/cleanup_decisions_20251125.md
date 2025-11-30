---
doc_id: DOC-GUIDE-CLEANUP-DECISIONS-20251125-1384
---

# DOC Cleanup Decisions – 2025-11-25

Pilot run of `DOC_DOCUMENTATION_CLEANUP_PATTERN.md` against the latest cleanup
bundle (`cleanup_report_20251125_090442.json`).

## Phase 1 – Inventory

- Baseline report: `cleanup_reports/cleanup_report_20251125_090442.json`.
- Manual queue: `cleanup_reports/cleanup_review_needed_20251125_090442.json`.
- High-confidence script (dry-run): `cleanup_reports/cleanup_high_confidence_20251125_090442.ps1`.

## Phase 2 – Classification

| Path | Source | Proposed Action | Rationale |
| --- | --- | --- | --- |
| `ccpm/ccpm/` (plus `commands/`, `rules/`, `agents/`) | High-confidence script | **DELETE** | Duplicate CLI payloads already consolidated under `pm/` + `ccpm/` modules; removing entire subtree frees ~0.45 MB. |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/pattern_extraction/` | High-confidence script | **ARCHIVE** | Contains historical extraction helpers referenced in reports; move to `archive/docs/uet_pattern_extraction/` before deletion. |
| `ai-logs-analyzer/*/.gitkeep` & `analysis/summary-report-20251124-104847.json` | High-confidence script | **KEEP (no-op)** | `.gitkeep` placeholders ensure empty dirs track; summary report provides last known metrics. Leave in place despite duplicate hash warning. |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/__init__.py` (and sibling package files) | Manual review list | **KEEP (pending refactor)** | Required to preserve namespace packages even if empty; mark for revisit only after module restructure. |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/tests/schema/test_all_schemas.py` | Manual review list | **CONSOLIDATE** | Move under `tests/schema/` root (already there) but cross-link to new schema validation harness; keep test while updating imports. |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/tools/check_doc_orphans.py` (and related doc tools) | Manual review list | **ARCHIVE** | Superseded by `scripts/doc_triage.py`; relocate to `archive/tools/` for reference. |

## Phase 3 – Execution Plan

1. **Delete duplicates**: After final confirmation, run
   `cleanup_high_confidence_20251125_090442.ps1` with `$DryRun = $false` to drop
   the redundant `ccpm/ccpm/**` subtree. Capture output in this folder.
2. **Archive pattern extraction scripts**: `git mv` the directory to
   `archive/tools/pattern_extraction/` and update references in the cleanup
   reports.
3. **Document tooling archive**: Move legacy doc tools (`check_doc_orphans.py`,
   etc.) to `archive/tools/doc_workflows/` and log the change.

## Phase 4 – Validation Checklist

- [ ] Re-run `python scripts/doc_triage.py --output doc_id/docid_reports/doc_cleanup_post_20251125.json`.
- [ ] `python doc_id/doc_id_registry_cli.py validate`.
- [ ] Markdown + link lint for affected docs.

## Phase 5 – Logging

- Record final actions (commit hashes, deleted/archived paths) in
  `docs/DOC_CLEANUP_LOG.md`.
- Attach the post-run triage report and PowerShell output to this folder to keep
  the audit trail complete.
