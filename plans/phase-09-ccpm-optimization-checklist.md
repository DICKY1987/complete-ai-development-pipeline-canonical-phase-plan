# Phase 09 – CCPM optimization checklist

## M1 — Install CCPM and wire commands
- [ ] Add `ccpm/` (submodule or vendored) with scripts and commands
- [ ] Update `scripts/bootstrap.ps1` to install/update CCPM
- [ ] Add `scripts/ccpm_install.ps1`, `scripts/ccpm_update.ps1`
- [ ] Verify `.claude/commands/pm/*` resolve to `ccpm/scripts/pm/*`

## M2 — GitHub issues integration hooks
- [ ] Add `src/integrations/github_sync.py` (gh first, API fallback)
- [ ] Add `scripts/gh_issue_update.py`, `scripts/gh_epic_sync.py`
- [ ] Add `config/github.yaml` and `.env.example` vars
- [ ] Call GitHub sync from `scripts/run_workstream.py` lifecycle events

## M3 — Parallel execution and worktrees
- [ ] Add `src/orchestrator/parallel.py` (concurrency, events)
- [ ] Add `scripts/worktree_start.ps1`, `scripts/worktree_merge.ps1` (+ `.sh` parity)
- [ ] Demo: two parallel tasks, isolated scopes, successful merge

## M4 — Align scripts and plugins
- [ ] Normalize `scripts/test-and-log.sh` output format
- [ ] Improve `src/plugins/test_runner/plugin.py` parsing and summary
- [ ] Improve `src/plugins/path_standardizer/plugin.py` (Windows paths, file/line)

## M5 — End‑to‑end tests
- [ ] Expand `tests/test_ccpm_openspec_integration.py` with mocked `gh`
- [ ] Add tests for parallel orchestrator and worktree scripts
- [ ] Add plugin tests for path and test runner

## M6 — Docs and developer UX
- [ ] Update `docs/ccpm-openspec-workflow.md` entrypoints
- [ ] Add `docs/ccpm-github-setup.md`
- [ ] Update quickstart and `scripts/test.ps1`

## M7 — Hardening and CI
- [ ] Add CI jobs (dry‑run) for CCPM flows
- [ ] Add feature flags (`ENABLE_PARALLEL`, `ENABLE_WORKTREES`, `ENABLE_GH_SYNC`)
- [ ] Add structured logging and diagnostics

