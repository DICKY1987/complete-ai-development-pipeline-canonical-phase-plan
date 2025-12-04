---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-DOC-DOCUMENTATION-CLEANUP-PATTERN-819
---

# DOC Documentation Cleanup Pattern

Reusable workflow for pruning, consolidating, and archiving repository
documentation without losing auditability.

## Purpose

- Keep guidance accurate by flagging stale/duplicated docs early.
- Provide a deterministic loop for merging overlapping guides and archiving
  historical notes.
- Ensure DOC_ID registry, guide indexes, and cleanup reports stay aligned.

## When to Run

| Trigger | Examples |
| --- | --- |
| Scheduled hygiene | Monthly or before a major release |
| Signal from cleanup reports | New `cleanup_report_*` JSON/PS1 bundle |
| Structural change | Large migration (e.g., doc_id re-org, spec merge) |

## Inputs & Tools

- `scripts/doc_triage.py` (or equivalent) to produce baseline metadata.
- Cleanup bundles (`cleanup_reports/*.json` and `.ps1`) for duplicates/staleness.
- DOC registries (`doc_id/DOC_ID_REGISTRY.yaml`, `docs/GUIDE_INDEX.yaml`).
- Markdown & link lint (`pwsh ./scripts/test.ps1`, `npm run lint:md` if enabled).

## Workflow

| Phase | Actions | Owner | Outputs |
| --- | --- | --- | --- |
| 1. Inventory | Run triage: `python scripts/doc_triage.py --output doc_id/docid_reports/doc_cleanup_<ts>.json`. Export last-modified, size, doc_id, tags. | Maintainer | `doc_cleanup_<ts>.json`, updated `docid_reports/` summary |
| 2. Classification | Join triage data with cleanup reports. Label each doc as `KEEP`, `ARCHIVE`, `CONSOLIDATE`, or `DELETE`. Capture rationale in `doc_id/docid_reports/cleanup_decisions_<ts>.md`. | Maintainer + SMEs | Decision log |
| 3. Execution | For each label: <br>• **Consolidate** – merge content into canonical doc, remove duplicates with `git mv`.<br>• **Archive** – move to `archive/docs/<year>/` or add “Archived” banner.<br>• **Delete** – only when doc is superseded *and* logged.<br>Update DOC_ID registry/artifact paths after every move. | Maintainer | Git commits w/ doc moves/edits |
| 4. Validation | Re-run doc triage, Markdown/link lint, and `python doc_id/doc_id_registry_cli.py validate`. Ensure guide indexes list the new locations. | QA/Docs | Clean validation reports |
| 5. Logging | Append summary to `docs/DOC_CLEANUP_LOG.md` (date, actions, links to commits). Store generated cleanup artifacts under `doc_id/docid_reports/`. | Maintainer | Audit trail |

## Consolidation Guidelines

- **Group by focus**: cluster docs sharing a DOC_ID, product area, or plan. Merge
  overlapping sections and keep historical context in an appendix.
- **Preserve IDs**: when two documents share a DOC_ID, select a primary file and
  note the redirect/merge in the registry’s `migration_queue`.
- **Archive, don’t erase**: move superseded narratives into `archive/docs/` or
  add an “Archived” front matter block with the retirement date.
- **Link updates**: use `rg -n "<old filename>"` to find references; update or
  remove them as part of the same commit.

## Automation Hooks

- **High-confidence cleanup script**: review the generated
  `cleanup_reports/cleanup_high_confidence_<ts>.ps1`, flip `$DryRun = $false`
  only after manual verification, and track the run in the cleanup log.
- **Manual review queue**: Triagers own the
  `cleanup_review_needed_<ts>.json` list. Schedule pairing sessions to decide on
  low-confidence files and feed decisions back into the next batch.

## Success Criteria

- All docs in scope have current DOC_ID entries & correct paths.
- No lint/link failures after consolidation.
- Cleanup log records what moved, what merged, and why.
- Future triage runs show the candidate list shrinking (signals trending down).
