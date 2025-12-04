# Safe Merge Orchestrator Phase Plan (jsonplan.json)

Anchors the safe-merge workflow to `jsonplan.json` and adds practical execution patterns plus gap-closure tasks.

## Entrypoints & Execution Patterns
- Full run (human/AI): `pwsh ./scripts/safe_merge_orchestrator.ps1 --branch <branch>`
- CI run: `pwsh ./scripts/safe_merge_orchestrator.ps1 --branch ${{ github.ref_name }} --mode ci`
- Debug flags: `--from-phase <n>` / `--to-phase <n>` to slice execution; `--phases 2,3,4` to run a set; `--dryrun` to only log planned actions.
- Phase-by-phase debug (reuse state in `.state/safe_merge/`):
  1) `pwsh ./scripts/merge_env_scan.ps1 --branch <branch> --OutputPath .state/safe_merge/env_scan_<branch>.json`
  2) `python ./scripts/sync_log_summary.py --output .state/safe_merge/sync_summary_<branch>.json`
  3) `python ./scripts/nested_repo_detector.py --output .state/safe_merge/nested_repos_<branch>.json`
     `python ./scripts/nested_repo_normalizer.py --input .state/safe_merge/nested_repos_<branch>.json --policy auto --default <nested_repo_default_policy>`
  4) `python ./scripts/merge_file_classifier.py --policy config/merge_policy.yaml --output .state/safe_merge/merge_file_classes_<branch>.json`
  5) `git fetch origin <branch>`; `git merge --no-ff origin/<branch> || echo "merge_conflicts" > .state/safe_merge/conflicts_<branch>.flag`
     `python ./scripts/merge_timestamp_resolver.py --input .state/safe_merge/merge_file_classes_<branch>.json --branch <branch> --restrict-classes`
     `python ./scripts/ai_conflict_resolver.py --branch <branch> --file-classes .state/safe_merge/merge_file_classes_<branch>.json --max-files 20`
  6) `python ./scripts/multi_clone_guard.py --lock-type pipeline --branch <branch> --command "pwsh ./scripts/safe_pull_and_push.ps1 -Branch <branch>"`
  7) `python ./scripts/safe_merge_emit_event.py --branch <branch> --status success --events-file .state/safe_merge/merge_events.jsonl`
- Recovery loop: inspect `.state/safe_merge/` artifacts (env scan, sync summary, nested repos, file classes, conflicts flag), remediate, then rerun from phase 0 to re-acquire locks.
- Lock hygiene: clean stale locks under `.git/locks/` per policy; pipeline lock `merge_pipeline_<branch>` for phases 0–6, push lock `branch_<branch>` for phase 5 only.

## Phase Objectives, Checks, and Outputs
- 0 environment_scan: clean working tree; outputs `.state/safe_merge/env_scan_<branch>.json`; abort if rebase/merge in progress.
- 1 sync_health_gate: analyze sync logs; outputs `.state/safe_merge/sync_summary_<branch>.json`; blocks if error/high-activity thresholds hit.
- 2 nested_repo_gate: detect/normalize stray repos; outputs `.state/safe_merge/nested_repos_<branch>.json`; blocks unless stray count is 0.
- 3 file_classification: classify files; outputs `.state/safe_merge/merge_file_classes_<branch>.json`; enforces timestamp-safe/forbidden classes.
- 4 local_merge_and_resolution: fetch/merge, timestamp resolution, AI/manual conflicts; writes conflicts flag and resolved trees; blocks on unresolved conflicts.
- 5 guarded_pull_and_push: branch-level lock via multi_clone_guard wrapping `safe_pull_and_push.ps1`; requires lock + successful push.
- 6 metrics_and_event_append: append success/failed events to `.state/safe_merge/merge_events.jsonl`; log-only on failure.

## Gap Closures & Improvements (actionable)
- Add missing script declarations to `required_scripts`: `ai_conflict_resolver.py`, `safe_merge_emit_event.py`, and the orchestrator itself for parity validation.
- Implement a `--phase` / `--from-phase` or `--dry-run` option in `safe_merge_orchestrator.ps1` for targeted debugging while still obeying locks.
- Add retry/backoff around network steps (`git fetch`, guarded push) with bounded attempts and clear error surfaces.
- Guard entrypoint by blocking direct `git merge/push` when pipeline lock is absent; validate presence of `config/merge_policy.yaml`, `.state/safe_merge/`, and `.git/locks/` on startup.
- Extend metrics/events to capture per-phase duration, lock wait times, and surface a summarized report in `logs/` (plus CI step output).
- Enforce policy clarity: when sync/nested/file-classification checks block, emit the reason_code and a user-facing hint.

## Quick Usage
- Fresh merge attempt: `pwsh ./scripts/safe_merge_orchestrator.ps1 --branch <branch>`
- Investigate a failure: check `.state/safe_merge/*_<branch>.json` and `.git/locks/`, clean up issues, rerun from phase 0 to re-acquire locks and revalidate gates.
