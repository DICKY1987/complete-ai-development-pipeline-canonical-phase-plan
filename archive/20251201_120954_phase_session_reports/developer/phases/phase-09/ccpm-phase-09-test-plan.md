---
doc_id: DOC-GUIDE-CCPM-PHASE-09-TEST-PLAN-1266
---

# CCPM Phase 09 — Test Plan and Matrix

This document lists existing tests and proposed tests to validate the CCPM
integration (install/wiring, GitHub sync, parallel orchestration, lifecycle
hooks, and script/plugin alignment). Unit tests run by default in CI; integration
and environment‑dependent tests remain opt‑in or skipped by default.

## Legend
- Type: unit | integration | e2e
- Status: existing | planned
- Platform: cross | posix | windows
- CI: included | optional | skipped

## Existing tests
- tests/test_ccpm_openspec_integration.py — Verify CCPM components exist (agents, rules, scripts)
  - Type: unit, Platform: cross, CI: included, Status: existing
- tests/test_github_sync.py — Ensure disabled sync is no‑op; epic lookup via mocked gh
  - Type: unit, Platform: cross, CI: included, Status: existing
- tests/test_github_sync_cli_path.py — Stub gh on PATH to exercise CLI path
  - Type: unit, Platform: posix, CI: included (Ubuntu), Status: existing
- tests/test_parallel_orchestrator.py — Run two workstreams in dry‑run via parallel orchestrator
  - Type: unit, Platform: cross, CI: included, Status: existing
- tests/test_parallel_dependencies.py — Ensure dependency ordering (depends_on) respected
  - Type: unit, Platform: cross, CI: included, Status: existing
- tests/test_orchestrator_lifecycle_sync.py — Lifecycle start/end comments emitted when enabled
  - Type: unit, Platform: cross, CI: included, Status: existing
- tests/test_path_standardizer.py — Parse path violations with file/line; Windows path normalization
  - Type: unit, Platform: cross, CI: included, Status: existing

## Planned tests (to be added)
- tests/test_test_runner_plugin.py — Validate pytest summary parsing and count extraction
  - Covers: count_tests, count_passed, count_failed, parse_test_output
  - Type: unit, Platform: cross, CI: included, Status: planned
- tests/test_test_and_log_script.sh (or Python wrapper) — Assert CCPM_TEST_SUMMARY marker emitted
  - Use a small fake pytest output file; no real test execution required
  - Type: unit (script), Platform: posix, CI: optional, Status: planned
- tests/windows/test_worktree_scripts.ps1 — Smoke test PowerShell worktree scripts (mock git)
  - Use PowerShell -NoProfile with mocked git in PATH
  - Type: unit (script), Platform: windows, CI: optional, Status: planned
- tests/integration/test_parallel_worktrees.py — Parallel tasks with real git worktree in a temp repo
  - Validate branch creation and merge behavior (skip in CI by default)
  - Type: integration, Platform: cross, CI: skipped, Status: planned
- tests/integration/test_github_sync_end_to_end.py — Dry‑run flow posting to a test repo (token via env)
  - Gate on env RUN_GH_E2E=true and presence of GITHUB_TOKEN
  - Type: integration, Platform: cross, CI: optional, Status: planned

## Notes
- Integration tests must avoid real network by default; require explicit env flags.
- Keep mocks deterministic; prefer PATH shims for CLI behavior.
- Windows‑first policy: provide PowerShell coverage where scripts differ.

## How to run (local)
- Unit tests only: pytest -q
- Skip integration: pytest -q --ignore=tests/integration
- Run POSIX script tests on Windows via WSL if needed.
