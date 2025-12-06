---
doc_id: DOC-GUIDE-GAP-ANA-239
---

Executive Summary

  - Total gaps: 7 (Critical: 1, High: 4, Medium: 2)
  - High-impact quick wins: 3
  - Potential time savings: ~84 hours/month
  - Estimated effort to implement: ~47 hours

  Gap Inventory

  - GAP-001 | Manual Workflow | Critical | 24 h/mo | 10 h
  - GAP-002 | Missing Validation | High | 12 h/mo | 6 h
  - GAP-003 | Manual Workflow | High | 20 h/mo | 8 h
  - GAP-004 | Missing Validation | High | 10 h/mo | 3 h
  - GAP-005 | Missing Monitoring | High | 8 h/mo | 8 h
  - GAP-006 | Dependency Hygiene | Medium | 4 h/mo | 2 h
  - GAP-007 | Data Ops | Medium | 6 h/mo | 10 h

  Detailed Recommendations

  GAP-001
  Priority: Critical
  RECOMMENDATION: Automate staged releases

  - Solution: Add GitHub Actions workflows for staging on main and
    production on tagged releases.
      - Tool/Technology: GitHub Actions + existing Python scripts
        (deploy hooks can use orchestrator).
      - Implementation:
          1. Create .github/workflows/deploy-staging.yml triggered
             on push to main; steps: checkout → pip install -r
             requirements.txt → run smoke tests → deploy script.
          2. Create .github/workflows/deploy-prod.yml triggered on
             release tags; steps: checkout → build artifact (zip/
             docker) → run scripts/verify_* → promote.
          3. Upload deployment metadata to .state/deployments.jsonl
             for traceability.
      - Integration point: new workflows under .github/workflows/.
  - Effort: 10 h
  - Expected Benefits: Time saved 24 h/mo; Error reduction: removes
    manual push mistakes; Quality: consistent promotion path.
  - Implementation Steps:
      1. Author staging workflow with smoke-test step.
      2. Author prod workflow gated on releases.
      3. Add rollback/verification job (health check script).
  - Dependencies: Deployment script/targets accessible from CI
    secrets.
  - Quick Win Potential: Yes—small workflows close the release
    gap immediately.

  GAP-002
  Priority: High
  RECOMMENDATION: Fix CI install/test reproducibility

  - Solution: Make CI installable and deterministic.
      - Tool/Technology: Python packaging metadata + GitHub
        Actions.
      - Implementation:
          1. Add minimal pyproject.toml build-system or setup.cfg
             so pip install -e . in .github/workflows/quality-
             gates.yml succeeds (currently no installable package;
             only pytest config).
          2. Align test discovery to one config (drop duplicate
             roots between pyproject.toml and pytest.ini or
             standardize to one).
          3. Cache .venv/pip to shorten reruns.
      - Integration point: .github/workflows/quality-gates.yml,
        repo root packaging files.
  - Effort: 6 h
  - Expected Benefits: Time saved 12 h/mo (failed CI spins); Error
    reduction: CI actually runs tests; Quality: deterministic env.
  - Implementation Steps:
      1. Add build-system section with setuptools and package
         layout (or remove editable install and set PYTHONPATH=.).
      2. Update workflow install step to pip install -r
         requirements.txt + pip install -e . once package exists.
      3. Consolidate pytest config to a single source.
  - Dependencies: None.
  - Quick Win Potential: Yes—unblocks existing CI jobs.

  GAP-003
  Priority: High
  RECOMMENDATION: Standardize non-interactive CLI execution

  - Solution: Add orchestrated, non-interactive path for scripts.
      - Tool/Technology: Existing orchestrator + argparse wrappers.
      - Implementation:
          1. Introduce scripts/lib/cli_runner.py that wraps
             commands with timeouts/state logging.
          2. Add --non-interactive / --assume-yes flags
             to scripts with prompts (scripts/agents/
             workstream_generator.py lines 255-271; scripts/
             exec017_quick_cleanup.py:56; PowerShell prompts like
             scripts/consolidate_archives.ps1:72).
          3. Provide a single entrypoint (python -m
             scripts.run_workstream ...) that records runs
             to .state/run_events.
      - Integration point: scripts/ and orchestrator hooks.
  - Effort: 8 h
  - Expected Benefits: Time saved 20 h/mo; Error reduction: fewer
    hung jobs; Quality: traceable CLI executions.
  - Implementation Steps:
      1. Ship shared runner with timeout/heartbeat.
      2. Migrate top 10 high-usage scripts to new runner.
      3. Add CI check to forbid input()/Read-Host when --non-
         interactive set.
  - Dependencies: None beyond existing orchestrator.

  GAP-004
  Priority: High
  RECOMMENDATION: Enforce lint/type/test gates in CI

  - Solution: Remove soft-fail linting and optional checks.
      - Tool/Technology: GitHub Actions + pre-commit.
      - Implementation:
          1. In .github/workflows/quality-gates.yml, remove || true
             from the Ruff step so failures break the build.
          2. In .pre-commit-config.yaml, drop || true from mypy/
             pytest hooks or mark them mandatory with platform-safe
             shells (replace bash -c with python -m pytest ...).
          3. Add a lightweight pre-commit job in CI to mirror local
             hooks.
      - Integration point: .github/workflows/quality-
        gates.yml, .pre-commit-config.yaml.
  - Effort: 3 h
  - Expected Benefits: Time saved 10 h/mo (less back-and-forth on
    broken lint); Error reduction: prevents regressions; Quality:
    consistent coding standards.
  - Implementation Steps:
      1. Edit workflow to fail on Ruff violations.
      2. Make mypy/pytest hooks blocking.
      3. Add pre-commit run --all-files job to CI.
  - Dependencies: None.

  GAP-005
  Priority: High
  RECOMMENDATION: Add alerting to event bus/CI failures

  - Solution: Connect core/events/event_bus.py to outbound
    notifications.
      - Tool/Technology: Webhook/Slack/email + GitHub Actions
        status notifications.
      - Implementation:
          1. Add subscriber that forwards EventSeverity.ERROR/
             CRITICAL to a webhook (Slack/Teams) and persists to a
             rolling alert log.
          2. Add a scheduled workflow to summarize last 24h
             critical events and CI failures.
          3. Expose a minimal dashboard artifact (JSON → Markdown)
             uploaded by CI.
      - Integration point: core/events/event_bus.py, new .github/
        workflows/alerts.yml.
  - Effort: 8 h
  - Expected Benefits: Time saved 8 h/mo; Error reduction: faster
    MTTR; Quality: visibility into failures.
  - Implementation Steps:
      1. Implement webhook sender and register subscriber.
      2. Create scheduled job to pull .state/run_events and post
         digest.
      3. Add alert output to Actions summary/artifact.
  - Dependencies: Webhook credentials.

  GAP-006
  Priority: Medium
  RECOMMENDATION: Automate dependency updates and security checks

  - Solution: Enable Dependabot/Renovate and pip auditing.
      - Tool/Technology: Dependabot config + pip-audit/pip index.
      - Implementation:
          1. Add .github/dependabot.yml for pip and GitHub Actions.
          2. Add a CI step pip install pip-audit && pip-audit
             (after install).
          3. Pin dev tools via a requirements-dev.txt lock or pip-
             compile.
      - Integration point: new Dependabot config, quality-gates
        job.
  - Effort: 2 h
  - Expected Benefits: Time saved 4 h/mo; Error reduction: fewer
    vuln surprises; Quality: up-to-date toolchain.
  - Implementation Steps:
      1. Commit Dependabot config with weekly cadence.
      2. Add pip-audit step to CI.
      3. Generate locked dev requirements.
  - Dependencies: None.

  GAP-007
  Priority: Medium
  RECOMMENDATION: Automate DB schema migrations/backups

  - Solution: Introduce migration tooling and scheduled backups
    for .state SQLite DBs.
      - Tool/Technology: Alembic (or simple migration scripts) +
        GitHub Actions artifacts.
      - Implementation:
          1. Define migrations for .state/orchestration.db
             (currently inspected manually by scripts/
             check_db_schema.py).
          2. Add migration step to CI (validate schema) and to
             startup scripts.
          3. Add nightly backup workflow to artifact/Storage, with
             retention policy.
      - Integration point: scripts/check_db_schema.py → migration
        runner; new .github/workflows/state-backup.yml.
  - Effort: 10 h
  - Expected Benefits: Time saved 6 h/mo; Error reduction: prevents
    schema drift/data loss; Quality: reproducible state.
  - Implementation Steps:
      1. Initialize Alembic migrations.
      2. Add CI job to run alembic upgrade head and fail on pending
         migrations.
      3. Add scheduled backup workflow for .state/*.db.
  - Dependencies: Storage for backups.

  Implementation Roadmap

  - Phase 1 (Week 1-2, Quick Wins): GAP-002 (CI install), GAP-004
    (fail lint), GAP-006 (Dependabot) — unlocks reliable CI and
    hygiene fast.
  - Phase 2 (Month 1, High Impact): GAP-001 (deploy pipelines),
    GAP-003 (non-interactive CLIs), GAP-005 (alerting) — closes
    major automation holes.
  - Phase 3 (Quarter 1, Long-term): GAP-007 (migrations/backups) —
    stabilizes stateful components and resilience.

  Appendix (Key Evidence)

  - CI install fails without package: .github/workflows/quality-
    gates.yml installs with pip install -e . but repo has no
    setup.py/setup.cfg/build-system (only pytest settings in
    pyproject.toml), so tests don’t actually run.
  - Duplicate/loose test config: pyproject.toml and pytest.ini both
    declare different testpaths.
  - Interactive/manual scripts: scripts/agents/
    workstream_generator.py:255-271 (input prompts), scripts/
    exec017_quick_cleanup.py:56 (input()), PowerShell prompts
    such as scripts/consolidate_archives.ps1:72 and scripts/
    execute_safe_merge.ps1:66.
  - Lint soft-fail: ruff check ... || true in .github/workflows/
    quality-gates.yml; mypy/pytest hooks in .pre-commit-config.yaml
    wrapped with || true.
  - Monitoring limited to local DB: core/events/event_bus.py only
    persists to SQLite and dispatches in-process; no webhook/alert
    subscribers present.
  - No dependency automation: no dependabot.yml under .github/;
    requirements are version-ranged but unlocked.
  - Manual DB checks: scripts/check_db_schema.py prints schema
    from .state/orchestration.db with no migration or backup
    automation.
