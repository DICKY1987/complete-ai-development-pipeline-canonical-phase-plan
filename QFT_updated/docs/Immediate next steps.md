Concrete downstream updates (add these to your plan today)

/plan/README.md (Checklist) – Inline the 10-step loop with gates; require /plan/file-map.yaml and /plan/rtm.yaml before execution.

Epics – One per plugin type with the shared scaffold + tests + docs deliverables, using the template steps as tasks.

CI – Implement L0–L5 tiers, auto-fail on trace gaps, docs build from the same contract/manifest, and OTel traces emitted for each gate.

DoR/DoD (repo policy) – Enforce the ready/done checklists for every plugin/workstream.

Plan schema + examples – Ship PlanFile.schema.json, include the YAML/JSON examples in /schemas with tests, and declare the 5-concurrency rule.

Governance – Add CHANGE_SPEC.yaml to the plan’s Release section (flag, non-goals, rollback) and wire GitHub CLI requirements where auto-PRs are planned.

Projects board & commits – Create the board columns and adopt the Aider commit prefix now; reflect in contribution guidelines and PR templates.



Minor gaps & quick fixes

Make acceptance-criteria blocks mandatory in every issue (template suggests; playbook shows how). Add a one-liner to your ISSUE_TEMPLATE pointing to the “AC pattern”.

Standardize board columns across projects (use the template’s “AI Proposed” column to flag AI-authored PRs).

Codify the session flow in a repo-local docs/USING_AIDER.md that embeds the slash-flow tables & examples.

Recommended unification (1-hour tidy-up)

Create a portfolio README: “This portfolio contains Project A: Docs-v2 Migration (IMP_PLAN_3) and Project B: <Your Next>. Both follow the Aider Planning Template.” Link to each plan.

Add a single ISSUE_TEMPLATE with the same AC scaffold + “Suggested Aider Prompt” field from the template.

Drop the slash-command cheat-sheet into docs/USING_AIDER.md and reference it from both plans.


What’s missing (and worth adding)

Formal schemas in-repo
You refer to PlanFile.schema.json, DependencyFile.schema.json, and tui.module.schema.json; make sure they exist and are enforced in CI (PlanValidator already expects them).

Observability + health
Emit a machine log of orchestrator lifecycle and a periodic worktree status JSON (matches your schema) for the TUI and for a GitHub Projects data ingestion job.

End-to-end Project wiring
Auto-open/update GitHub issues for each workstream; annotate dependencies (dependsOn) into tasklists (or parent/child where used), and update progress fields when a workstream/job finishes.

Prompt assets + gates
Store each promptFile + acceptance criteria alongside tests; reuse your “issue seeds/epics” library so Aider tasks are always scoped, testable, and traceable.

Safer rollout
Respect enable_qft_orchestrator in a tiny bootstrap. Add a “dry-run plan” path (no edits, only generate per-workstream intent + diffs), then flip the flag after Pester/pytest gates pass.

Concrete expansion plan (phased, low-risk)

Phase A — Contracts & CI (foundation)

Add the three JSON Schemas; update PlanValidator tests to enforce them in CI.

Add a docs-guard workflow and scheduled validation (weekly) per your planning notes.

Phase B — Orchestrator hardening

Emit worktree_status.json on each tick conforming to your schema; include statistics and operations to feed the TUI.

Add “dry-run” mode that only spawns Aider intent (no writes), plus structured logs at logs/<ws-id>.log.

Phase C — GitHub Projects integration

On Start-Orchestration, create/ensure issues per workstream, link dependsOn via tasklists, and update status fields/labels on completion.

Gate PR creation to “green workstreams only” (tests pass), reusing your gh hooks.

Phase D — TUI modules

Build worktrees_ui to render the status schema and expose per-worktree actions (prune/repair/lock). Use the plugin manifest and versioned merge rules already defined.

Add a ledger_view module for run history and error rates (enables the 5% rollback trigger visibility).

Phase E — Prompt & seed library

Turn the “Issue Seeds / Epics” docs into a reusable prompt pack consumed by promptFile—small, file-scoped tasks with acceptance criteria + tests.

Immediate next steps (do these now)

Create a real plan at plan/phase_plan.yaml using your examples; include at least one dependsOn.

Run the orchestrator exactly as documented to validate plumbing:
Import-Module .\src\Application\Orchestrator.ps1 -Force; Start-Orchestration -PlanPath .\plan\phase_plan.yaml -Concurrency 5 -Verbose

Add CHANGE_SPEC to CI: enforce feature flag default=off until Pester passes; enable rollback path.

