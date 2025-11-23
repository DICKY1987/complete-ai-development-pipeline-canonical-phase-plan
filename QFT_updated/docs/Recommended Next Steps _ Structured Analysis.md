Recommended Next Steps _ Structured Analysis
/plan/README.md (Checklist)
Description of the Step

Inline your 10-step planning loop with gates into /plan/README.md, and require /plan/file-map.yaml and /plan/rtm.yaml to exist before any execution.

Purpose

Make the plan self-contained and executable so every contributor knows the minimum artifacts and gates before work starts.

Outcome/Value Delivered

A single canonical checklist that prevents “plan drift,” enforces prerequisites, and accelerates onboarding and reviews.

Epics (one per plugin type)
Description of the Step

Create one Epic per plugin category with a shared scaffold (tests + docs deliverables) and use the template’s steps as tasks.

Purpose

Standardize how different plugins are planned and built, ensuring consistent quality and traceability across streams.

Outcome/Value Delivered

Uniform Epics that speed planning, reduce rework, and let CI apply the same gates across all plugin efforts.

CI (L0–L5 tiers, trace gaps auto-fail, docs from contracts, OTel at each gate)
Description of the Step

Implement multi-tier CI checks; fail builds on traceability gaps; build docs from the same contracts; emit OTel traces at each gate.

Purpose

Turn governance into code so quality and documentation are verifiable on every change.

Outcome/Value Delivered

Predictable builds, auditable pipelines, and living documentation generated from authoritative specs.

DoR/DoD (Repository Policy)
Description of the Step

Enforce Definition-of-Ready and Definition-of-Done checklists for every plugin/workstream.

Purpose

Ensure work only starts when it’s well-scoped and only finishes when evidence proves acceptance.

Outcome/Value Delivered

Fewer partially-baked tasks, cleaner merges, and consistent “done” criteria across teams.

Plan Schema + Examples
Description of the Step

Ship PlanFile.schema.json, include YAML/JSON examples in /schemas with tests, and declare the 5-concurrency rule.

Purpose

Validate plans before execution and codify orchestration constraints (e.g., max concurrency).

Outcome/Value Delivered

Schema-checked plans, earlier error detection, and safer orchestrations aligned with platform limits.

Governance (CHANGE_SPEC + GitHub CLI wiring)
Description of the Step

Add CHANGE_SPEC.yaml to the Release section (flag, non-goals, rollback) and wire gh requirements where auto-PRs are planned.

Purpose

Control risky features behind flags and make rollback explicit; ensure automation can authenticate and open PRs.

Outcome/Value Delivered

Lower blast radius for changes, faster recovery on regressions, and reliable repo automation.

Projects Board & Commits
Description of the Step

Create board columns and adopt the Aider commit prefix now; reflect this in contribution guidelines and PR templates.

Purpose

Align planning signals (boards/labels) with commit semantics for better status tracking and review.

Outcome/Value Delivered

Clearer project visibility and searchable commit history tied to workflow states.

Make Acceptance-Criteria (AC) Blocks Mandatory
Description of the Step

Require an AC block in every issue; add a one-liner in ISSUE_TEMPLATE pointing to the AC pattern.

Purpose

Force testable, objective “done” conditions up front.

Outcome/Value Delivered

Less ambiguity, faster review cycles, and stronger CI enforcement against vague tasks.

Standardize Board Columns Across Projects
Description of the Step

Adopt a common set of columns; include an “AI Proposed” column to flag AI-authored PRs.

Purpose

Enable cross-project reporting and consistent automation rules on column changes.

Outcome/Value Delivered

Comparable dashboards and easier portfolio-level analytics.

Codify Aider Session Flow in docs/USING_AIDER.md
Description of the Step

Document the slash-command flow and embed tables/examples in a repo-local guide.

Purpose

Give contributors an authoritative, repeatable playbook for session setup and safe edits.

Outcome/Value Delivered

Fewer session mistakes, safer large changes, and faster onboarding to Aider workflows.

Portfolio README
Description of the Step

Create a top-level README describing the portfolio structure (e.g., Docs-v2 Migration + Next Project) and link both plans.

Purpose

Clarify scope and relationships between projects under one governance model.

Outcome/Value Delivered

A clear entry point for stakeholders that reduces confusion and duplication.

Single ISSUE_TEMPLATE with AC Scaffold + “Suggested Aider Prompt”
Description of the Step

Unify to one issue template that enforces AC and includes a “Suggested Aider Prompt” field.

Purpose

Standardize issue quality and encourage prompt patterns that map directly to CI gates.

Outcome/Value Delivered

Higher-quality issues and more deterministic AI edits aligned with acceptance.

Add Slash-Command Cheat-Sheet to docs/USING_AIDER.md
Description of the Step

Include the quick-reference slash-commands and reference them from both plans.

Purpose

Reduce context-switching and errors during interactive sessions.

Outcome/Value Delivered

Faster execution and fewer misuse errors when operating Aider.

Create a Real Plan at plan/phase_plan.yaml (with at least one dependsOn)
Description of the Step

Author a minimal but real plan file and include at least one dependency edge.

Purpose

Move from concept to execution with a schema-valid plan that exercises dependency handling.

Outcome/Value Delivered

A runnable plan that unblocks orchestrator tests and exposes graph/ordering issues early.

Run the Orchestrator to Validate Plumbing
Description of the Step

Execute:
Import-Module .\src\Application\Orchestrator.ps1 -Force; Start-Orchestration -PlanPath .\plan\phase_plan.yaml -Concurrency 5 -Verbose.

Purpose

Smoke-test end-to-end orchestration (schema validation, worktrees, concurrency, logging).

Outcome/Value Delivered

Proof that the pipeline runs on your machine, with actionable logs for any failures.

Add CHANGE_SPEC to CI (Feature Flag Default=Off + Rollback Path)
Description of the Step

Wire CHANGE_SPEC.yaml into CI so the orchestrator is behind a feature flag until tests pass; define rollback.

Purpose

Reduce risk while rolling out new orchestration by gating it behind automated verification.

Outcome/Value Delivered

Safe, reversible activation with explicit criteria for enabling/disabling in production CI.