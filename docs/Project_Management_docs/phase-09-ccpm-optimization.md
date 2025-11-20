# Phase 09: CCPM integration optimization plan

## Objectives
- Fully integrate CCPM capabilities (PRD → epic → task → issue → code) into the pipeline.
- Wire GitHub Issues synchronization for status, comments, labels, and relationships.
- Enable parallel execution with per‑task worktrees and agent guidance.
- Align local scripts and plugins with canonical CCPM rules and outputs.
- Provide end‑to‑end tests, docs, and Windows‑first tooling.

## Scope
- In scope: CCPM installation/wiring, GitHub sync hooks, parallel orchestrator, worktree ops,
  script alignment, tests, and documentation updates.
- Out of scope: Major refactors to unrelated pipeline modules, non‑GitHub issue trackers.

## Key decisions
- Installation strategy: add CCPM to repo at `pm/` (vendored or submodule). This makes
  `.claude/commands/pm/*.md` references like `bash pm/scripts/pm/...` immediately executable.
- Windows‑first: add thin PowerShell wrappers in `scripts/` that call CCPM bash scripts via WSL
  when needed; core logic in Python.
- GitHub integration: prefer `gh` CLI for simplicity; fall back to REST API via PyGithub when
  `gh` is unavailable. All network calls are optional and controlled via config flags.

## Phase breakdown

### Phase 09.1 — Install CCPM and wire commands
- Tasks
  - Add `pm/` directory via submodule or vendored copy (scripts, commands, rules kept intact).
  - Update `scripts/bootstrap.ps1` to optionally install/update CCPM:
    - Detect `pm/`; if missing, offer to `git submodule add` or clone.
    - Verify `.claude/` contents exist; ensure `.claude/commands/pm/*` paths resolve.
  - Add `scripts/ccpm_install.ps1` and `scripts/ccpm_update.ps1` for one‑shot setup/update.
  - Ensure `.gitignore` excludes CCPM ephemeral dirs (e.g., `.claude/epics/`).
- Deliverables
  - `pm/` present and callable; updated bootstrap script; install/update automation.
- Acceptance criteria
  - `pwsh ./scripts/bootstrap.ps1` reports CCPM ready; `.claude/commands/pm/epic-status.md`
    runs its underlying script without path errors.

### Phase 09.2 — GitHub Issues integration hooks
- Tasks
  - Add `src/integrations/github_sync.py` with functions:
    - `ensure_epic(epic_name, labels, body) -> issue_number`
    - `create_or_update_issue(epic_number, task_title, labels, body)`
    - `comment(issue_number, text)`
    - `set_status(issue_number, state, labels)`
    - Implement via `gh` CLI; fallback to REST with PAT from env.
  - Add `scripts/gh_issue_update.py` and `scripts/gh_epic_sync.py` thin CLIs.
  - Configuration: `config/github.yaml` + `.env.example` for `GITHUB_TOKEN`, repo owner/name,
    and `ENABLE_GH_SYNC=true|false`.
  - Hook pipeline events:
    - Update `scripts/run_workstream.py` to emit lifecycle events (started, stage transitions,
      success/failure) and call `github_sync.comment` when `ENABLE_GH_SYNC` and `ccpm_issue` set.
    - Extend `src/pipeline/bundles.py` emitted metadata to include `ccpm_issue` in event payloads.
- Deliverables
  - GitHub sync module, CLIs, config, and pipeline hooks.
- Acceptance criteria
  - Dry‑run mode posts to a test repo with mocked credentials in CI; local runs no‑op when disabled.

### Phase 09.3 — Parallel execution and worktrees
- Tasks
  - Add `src/orchestrator/parallel.py`:
    - Plan: map bundle tasks to workers; respect dependencies.
    - Execute: spawn per‑task subprocesses (Python) with controlled concurrency.
    - Emit events for start/finish/progress (to GitHub when enabled).
  - Add `scripts/worktree_start.ps1` and `scripts/worktree_merge.ps1`:
    - `worktree_start`: `git worktree add ../epic-<name> -b epic/<name>`; sync required files.
    - `worktree_merge`: fast‑forward or merge back; handle conflicts; cleanup.
  - Provide WSL/bash parity scripts (`.sh`) where useful.
  - Align with `.claude/agents/parallel-worker.md` guidance for worker responsibilities.
- Deliverables
  - Parallel orchestrator module and worktree scripts.
- Acceptance criteria
  - Run two independent tasks in parallel with isolated worktrees; results merged without conflict.

### Phase 09.4 — Align scripts with CCPM rules
- Tasks
  - Review and adopt CCPM canonical scripts for testing and path standards where they diverge.
  - Normalize `scripts/test-and-log.sh` output to a stable format parsed by
    `src/plugins/test_runner/plugin.py` (exit code, summary lines).
  - Update `src/plugins/path_standardizer/plugin.py` to:
    - Return Operating Contract errors with file/line when detectable.
    - Support Windows paths consistently; avoid false positives; honor `.claude/rules/path-standards.md`.
- Deliverables
  - Updated scripts and plugins aligned with CCPM documentation and rules.
- Acceptance criteria
  - Plugins produce deterministic outputs across platforms; unit tests cover common cases.

### Phase 09.5 — End‑to‑end tests
- Tasks
  - Expand `tests/test_ccpm_openspec_integration.py`:
    - Mock `gh` (shim script ahead of PATH) and assert calls: epic creation, status comments,
      label updates.
    - Validate that pipeline lifecycle emits expected GitHub updates when `ENABLE_GH_SYNC=true`.
  - Add tests for parallel orchestrator:
    - Simulate two tasks with independent file scopes; assert no overlap; assert merge script calls.
  - Add tests for path/test plugins against sample files.
- Deliverables
  - Deterministic tests with no real network; CI‑friendly.
- Acceptance criteria
  - `pytest -q` passes locally and in CI; tests are skipped when prerequisites are missing.

### Phase 09.6 — Documentation and developer UX
- Tasks
  - Update `docs/ccpm-openspec-workflow.md` to match actual entrypoints
    (replace placeholders like `src.orchestrator.main` with concrete commands).
  - Add `docs/ccpm-github-setup.md` for `gh` install/auth, scopes, test repo usage.
  - Update `README`/quickstart snippets and `scripts/test.ps1` to include new tests.
  - Provide troubleshooting matrix (auth, PATH, WSL, submodule checkout).
- Deliverables
  - Up‑to‑date documentation and quick starts.
- Acceptance criteria
  - A new contributor can bootstrap CCPM, run a sample workstream, and see GH updates.

### Phase 09.7 — Hardening and CI
- Tasks
  - Add CI jobs to run unit tests and CCPM integration tests in dry‑run mode.
  - Add feature flags: `ENABLE_PARALLEL`, `ENABLE_WORKTREES`, `ENABLE_GH_SYNC` in config.
  - Add telemetry/debug logging for orchestrator and sync actions.
- Deliverables
  - CI pipelines and feature‑flagged configuration.
- Acceptance criteria
  - CI green on PRs; flags allow selective enabling per environment.

## Milestones and timeline (indicative)
- M1 (Week 1): Phase 09.1 complete; CCPM installed and wired.
- M2 (Week 2): Phase 09.2 complete; GH sync hooks operational behind a flag.
- M3 (Week 3): Phase 09.3 complete; basic parallel execution with worktrees.
- M4 (Week 4): Phase 09.4–09.5 complete; scripts aligned and E2E tests stable.
- M5 (Week 5): Phase 09.6–09.7 complete; docs/CI hardened; flags tuned.

## Risks and mitigations
- GitHub rate limits or auth failures → mock `gh` in tests; exponential backoff; dry‑run mode.
- Worktree merge conflicts → enforce file‑scope separation; pre‑merge checks; clear rollback.
- Cross‑platform quirks → Windows‑first wrappers; rely on Python for core logic; WSL fallback.
- Submodule friction → provide vendored fallback and install scripts; document both paths.

## Acceptance summary (exit criteria)
- CCPM commands run from this repo without path errors.
- Pipeline emits GitHub issue updates for workstream lifecycle when enabled.
- Parallel tasks run in isolated worktrees and merge cleanly in a demo scenario.
- Tests pass locally and in CI without network dependency by default.
- Docs enable a new user to bootstrap and verify the integration end‑to‑end.



