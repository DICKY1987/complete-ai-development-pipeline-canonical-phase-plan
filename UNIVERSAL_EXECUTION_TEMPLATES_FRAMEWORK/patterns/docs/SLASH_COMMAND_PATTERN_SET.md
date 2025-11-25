# Slash Command Pattern Set

Slash commands are the entrypoints into the deterministic pipeline: each command maps to a fixed Phase, Workstream bundle, FILES_SCOPE, and ExecutionRequest template. Use these definitions when wiring chat surfaces, TUI buttons, or GitHub slash shortcuts so the right agent stack is invoked every time.

## AI Codebase Structure (PH-ACS)

### /acs-init
- Phase · Workstream: `PH-ACS` · `WS-ACS-INIT`
- ExecutionRequest Template: `ER-ACS-INIT`
- FILES_SCOPE: `repo_root` (writes `CODEBASE_INDEX.yaml`, `QUALITY_GATE.yaml`, `ai_policies.yaml`, `.meta\AI_GUIDANCE.md`)
- Parameters: `--branch`, `--db-path`, `--force`
- Validation: `python scripts\validate_acs_conformance.py`
- Outputs: Fresh ACS artifact set, ledger entry tagged `acs-init`

### /acs-refresh-index
- Phase · Workstream: `PH-ACS` · `WS-ACS-INDEX`
- ExecutionRequest: `ER-ACS-REFRESH-INDEX`
- FILES_SCOPE: `core/index-only`
- Parameters: `--branch`, `--include-summaries`
- Validation: `python scripts\generate_repo_summary.py`
- Outputs: Regenerated `CODEBASE_INDEX.yaml`

### /acs-refresh-policies
- Phase · Workstream: `PH-ACS` · `WS-ACS-POLICY`
- ExecutionRequest: `ER-ACS-POLICY`
- FILES_SCOPE: `config-only` (`ai_policies.yaml`, `QUALITY_GATE.yaml`)
- Parameters: `--policy-set`, `--strict`
- Validation: `python scripts\validate_acs_conformance.py --policies-only`
- Outputs: Updated policy bundle, diff summary

### /acs-guidance
- Phase · Workstream: `PH-ACS` · `WS-ACS-GUIDANCE`
- ExecutionRequest: `ER-ACS-GUIDANCE`
- FILES_SCOPE: `.meta\*`
- Parameters: `--summaries`, `--code-graph`
- Validation: `python scripts\generate_repo_summary.py` + `python scripts\generate_code_graph.py`
- Outputs: Refreshed `.meta\AI_GUIDANCE.md`, `.meta\ai_context\repo_summary.json`, `.meta\ai_context\code_graph.json`

## Restructure Control (PH-RESTRUCT)

### /restruct-plan
- Phase · Workstream: `PH-RESTRUCT` · `WS-RESTRUCT-PLAN`
- ExecutionRequest: `ER-RESTRUCT-PLAN`
- FILES_SCOPE: `planning-only` (`plans\RESTRUCTURE_CODEBASE_V1.yaml`)
- Parameters: `--branch`, `--target-area`, `--risk`
- Validation: `python scripts\validate_workstreams.py --plan RESTRUCTURE_CODEBASE_V1.yaml`
- Outputs: Updated restructure spec plus planning report

### /restruct-dryrun
- Phase · Workstream: `PH-RESTRUCT` · `WS-RESTRUCT-SIM`
- ExecutionRequest: `ER-RESTRUCT-DRYRUN`
- FILES_SCOPE: `sim-output` (`reports\restructure\*.md`)
- Parameters: `--plan`, `--branch`
- Validation: `python scripts\test.ps1 -Configuration DryRun`
- Outputs: Impact matrix, diff preview, risk score

### /restruct-apply
- Phase · Workstream: `PH-RESTRUCT` · `WS-RESTRUCT-APPLY`
- ExecutionRequest: `ER-RESTRUCT-APPLY`
- FILES_SCOPE: `plan+code` (bounded by the approved spec)
- Parameters: `--plan`, `--branch`, `--checkpoint`
- Validation: `python scripts\test.ps1` + `python scripts\validate_workstreams.py`
- Outputs: Applied patches, ledger writeback, validation logs

### /restruct-rollback
- Phase · Workstream: `PH-RESTRUCT` · `WS-RESTRUCT-ROLLBACK`
- ExecutionRequest: `ER-RESTRUCT-ROLLBACK`
- FILES_SCOPE: `git-ledger`
- Parameters: `--checkpoint`, `--branch`, `--reason`
- Validation: `git status`, `python scripts\test.ps1 --subset smoke`
- Outputs: Reverted snapshot, ledger entry with rollback reason

## Error Pipeline / Self-Healing (PH-ERR)

### /err-diagnose
- Phase · Workstream: `PH-ERR` · `WS-ERR-DIAGNOSE`
- ExecutionRequest: `ER-ERR-DIAG`
- FILES_SCOPE: `reports\error\*.json`
- Parameters: `--run-id`, `--log-path`, `--tests`
- Validation: `python scripts\run_error_engine.py --mode classify`
- Outputs: Error report, failing test manifest

### /err-fix
- Phase · Workstream: `PH-ERR` · `WS-ERR-FIX`
- ExecutionRequest: `ER-ERR-FIX`
- FILES_SCOPE: `bounded` (files listed in diagnosis)
- Parameters: `--run-id`, `--strategy`, `--max-patches`
- Validation: `pytest -q --maxfail=1` scoped to failing tests
- Outputs: Patch set, fix ledger, updated diagnosis report

### /err-verify
- Phase · Workstream: `PH-ERR` · `WS-ERR-VERIFY`
- ExecutionRequest: `ER-ERR-VERIFY`
- FILES_SCOPE: `tests-only`
- Parameters: `--run-id`, `--suite`, `--coverage`
- Validation: `pwsh scripts\test.ps1 --filter "{suite}"`
- Outputs: Minimal verification log, coverage delta

### /err-open-pr
- Phase · Workstream: `PH-ERR` · `WS-ERR-PR`
- ExecutionRequest: `ER-ERR-PR`
- FILES_SCOPE: `reports+patches`
- Parameters: `--run-id`, `--branch`, `--include-logs`
- Validation: `git status`, `gh pr status`
- Outputs: Draft PR with patches + error logs attached

## Repo Hygiene & Docs (PH-HYGIENE)

### /stale-scan
- Phase · Workstream: `PH-HYGIENE` · `WS-HYGIENE-STALE`
- ExecutionRequest: `ER-STALE-SCAN`
- FILES_SCOPE: `docs+examples`
- Parameters: `--older-than`, `--paths`, `--format`
- Validation: `python scripts\staleness_scan.py`
- Outputs: `reports\STALE_CONTENT_REPORT.json`

### /stale-quarantine
- Phase · Workstream: `PH-HYGIENE` · `WS-HYGIENE-QUAR`
- ExecutionRequest: `ER-STALE-QUAR`
- FILES_SCOPE: `docs-only`
- Parameters: `--report`, `--label`, `--branch`
- Validation: `python scripts\staleness_scan.py --check {report}`
- Outputs: Moves to `quarantine\`, audit log update

### /docs-index
- Phase · Workstream: `PH-HYGIENE` · `WS-HYGIENE-DOCS`
- ExecutionRequest: `ER-DOCS-INDEX`
- FILES_SCOPE: `docs\**\*.md`
- Parameters: `--paths`, `--format`
- Validation: `python scripts\build_doc_registry.py`
- Outputs: Updated docs index + manifest (feeds registry layer)

## Observability & Status (PH-OBS)

### /phase-status
- Phase · Workstream: `PH-OBS` · `WS-OBS-PHASE`
- ExecutionRequest: `ER-OBS-PHASE`
- FILES_SCOPE: `read-only`
- Parameters: `--phase`, `--detail`
- Validation: `python scripts\phase_status.py`
- Outputs: Live view of phase gates, surfaced in chat/TUI

### /ws-status
- Phase · Workstream: `PH-OBS` · `WS-OBS-WS`
- ExecutionRequest: `ER-OBS-WS`
- FILES_SCOPE: `read-only`
- Parameters: `--workstream`, `--phase`, `--limit`
- Validation: `python scripts\workstream_status.py`
- Outputs: Table of workstream states (running / blocked / complete)

### /ledger-last
- Phase · Workstream: `PH-OBS` · `WS-OBS-LEDGER`
- ExecutionRequest: `ER-OBS-LEDGER`
- FILES_SCOPE: `read-only`
- Parameters: `--count`, `--filter`
- Validation: `python scripts\ledger_cli.py --tail {count}`
- Outputs: Last N ledger entries, ready for insertion into chat thread

### /graph
- Phase · Workstream: `PH-OBS` · `WS-OBS-GRAPH`
- ExecutionRequest: `ER-OBS-GRAPH`
- FILES_SCOPE: `.meta\ai_context`
- Parameters: `--format` (`svg|json`), `--phase`
- Validation: `python scripts\generate_code_graph.py --mode phases`
- Outputs: Rendered dependency graph artifact for dashboards
