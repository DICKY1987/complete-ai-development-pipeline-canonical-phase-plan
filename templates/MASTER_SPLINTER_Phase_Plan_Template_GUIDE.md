---
doc_id: DOC-GUIDE-MASTER-SPLINTER-PHASE-PLAN-TEMPLATE-527
---

# Phase Plan Template – AI Fill Guide (Decision-Elimination Ready)

Authoritative rules: follow `AI_SANDBOX\_template_sandbox\docs\DEV_RULES_CORE.md`. Use this guide when populating `MASTER_SPLINTER_Phase_Plan_Template.yml`. Ground truth over vibes: success = observable facts (files exist, commands pass, tests green), scope respected, no forbidden paths touched.

## How to Fill Each Section
- `doc_id`, `template_version`: keep existing values unless versioning the template.
- `phase_identity`: set `phase_id`, `workstream_id`, `title`, `summary`, `objective` (definition of done), `phase_type` (enum in template), `status` (`not_started|in_progress|planned|blocked|done|abandoned`), `estimate_hours`, `gh_item_id` (null until GitHub sync), `tags` (short context keywords).
- `dag_and_dependencies`: list hard `depends_on` (must be DONE), safe `may_run_parallel_with`, optional `parallel_group`, `is_critical_path` boolean.
- `scope_and_modules`: `repo_root`, `modules` (id + description), `file_scope` read/modify/create lists, and `forbidden_paths` (never touch). `worktree_strategy` mode/name_pattern/base_branch.
- `environment_and_tools`: target OS/shell/lang, python constraints, required services, config_files, AI operators, tool_profiles.
- `execution_profile`: prompt_template_id, run_mode, max_runtime, concurrency limits, retry policy.
- `pre_flight_checks`: each check needs id, description, when, command, success_pattern, on_fail.
- `execution_plan.steps`: ordered steps with id/name/operation_kind/pattern_ids/description/tool_id/inputs/expected_outputs; set `requires_human_confirmation` explicitly.
- `fix_loop_and_circuit_breakers`: enable/disable, applies_to, config ref, defaults, behavior.
- `expected_artifacts`: required patch/log/doc/db artifacts with paths and must_exist flags.
- `acceptance_tests.tests`: id, description, command, success_pattern, must_pass.
- `completion_gate`: rules booleans plus manual_override controls.
- `observability_and_metrics`: event_tags, metrics toggles.
- `governance_and_constraints`: anti_patterns_blocked, notes_for_operators.
- `extensions.custom_fields`: free-form; leave `{}` if unused.

## Decision-Elimination Rules (apply from UTE docs)
- Decide once, apply many: keep structure unchanged; only fill variable fields. Do not add new structural keys without template versioning.
- Ground truth: success only when declared artifacts exist, commands/tests match success patterns, and git scope is limited to allowed paths. No subjective approval.
- Scope enforcement: all edits constrained to `scope_and_modules.file_scope`; never write to `forbidden_paths`.
- Verification: rely on pre_flight + acceptance tests + completion_gate; if missing, add concrete commands with regex success patterns.
- Self-heal policy: prefer deterministic fixes already allowed by tools (e.g., create parents, rerun commands); do not invent new auto-fixes beyond template behavior.
- Parallelism: only use `may_run_parallel_with`/`max_parallel_steps` when scopes don’t overlap; otherwise keep sequential.
- Stop on ambiguity: if a required field is unknown, leave a clear placeholder token (e.g., `TODO-WORKSTREAM-ID`) rather than guessing.

## Quick Usage Pattern for AI/Tools
1) Load template + this guide; fill every required field above the dashed line before execution.
2) Pre-commit sanity: `git status --porcelain` (expect clean or only your template edits).
3) When adding steps/checks/tests, always include: command + success_pattern + must_pass/must_exist as appropriate.
4) When integrating with GitHub Project sync, keep `gh_item_id: null` until the sync script writes it back.
5) Validation to run after edits: `python -m jsonschema` (if schema exists), optional `python -c "import yaml,sys;yaml.safe_load(open('MASTER_SPLINTER_Phase_Plan_Template.yml'))"` to ensure YAML parses.

## Alignment with UTE Playbooks
- Mirrors Decision Elimination Playbook: pre-answer structure, verification, and scope to remove runtime choices.
- Matches Execution Acceleration Guide: treat template as pre-decided plan; fill variables only, run ground-truth checks.
- Matches Pattern Recognition writeup: reuse invariant ordering and fields; avoid per-instance structural changes.
