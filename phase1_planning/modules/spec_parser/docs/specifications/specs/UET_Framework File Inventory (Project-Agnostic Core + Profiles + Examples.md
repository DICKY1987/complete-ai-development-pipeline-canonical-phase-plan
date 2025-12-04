---
doc_id: DOC-GUIDE-UET-FRAMEWORK-FILE-INVENTORY-PROJECT-885
---

Here’s a single document you can drop into the repo as your **“what files belong in the framework”** map.

I’ll keep it project-agnostic and call out where things are:

* **Core (generic, re-usable everywhere)**
* **Profiles (software-dev flavored, optional)**
* **Examples (error-pipeline etc., clearly non-core)**

You can rename paths, but this gives you a concrete file set.

---

# Framework File Inventory (Project-Agnostic Core + Profiles + Examples)

## 0. Top-Level Layout

Recommended high-level structure:

```text
/framework
  /specs            # All schema & spec files (core + profiles)
  /guides           # Human-readable guides for operators/maintainers
  /registry         # Registries & ledgers (JSONL/YAML)
  /examples         # Non-core, domain-specific examples (e.g., error pipeline)
  /tools            # Helper scripts/CLIs used by the framework
```

---

## 1. Core Spec Files (Project-Agnostic)

These are the things that should exist for **any** project/module that uses the framework.

### 1.1 Meta & Shared Types

**Purpose:** give every document and artifact a consistent, machine-readable header and shared structural types.

* `specs/core/doc_meta.schema.json`

  * JSON Schema for doc meta frontmatter (doc_type, doc_layer, version, owner, tags, etc.).
  * Used by *all* spec/guide docs.

* `specs/core/check_definition.schema.json`

  * Generic definition of an “acceptance check”:

    * `id`, `type`, `description`, `required`, `severity`, `condition`/`command`, etc.
  * Shared by phase/workstream/task acceptance blocks.

* `specs/core/policy_block.schema.json` (optional)

  * Generic shape for constraint/policy blocks:

    * `name`, `scope`, `rules[]`, `tightening_only` flags.

---

### 1.2 Prompt Rendering (PROMPT_RENDERING_SPEC)

**Core (project-agnostic):**

* `specs/core/prompt_instance.schema.json`

  * Defines the generic `PromptInstance` object:

    * `prompt_instance_id`
    * `template_id`
    * `target_tool`
    * `kind` (open enum)
    * `sections` (OBJECTIVE, CONTEXT, CONSTRAINTS, OUTPUT_SPEC, etc.)
  * No code-specific assumptions; “kind” is generic.

* `specs/core/prompt_rendering_spec.md`

  * Framework-level description of:

    * Required sections,
    * How templates + overrides produce a `PromptInstance`,
    * How tools consume it.
  * Written for agentic AI; highly structured, but project-agnostic.

**Software-dev profile (optional):**

* `specs/profiles/software_dev/prompt_profiles.md`

  * Describes dev-centric prompt patterns (code_edit, code_review, etc.).
  * Includes how to express FILES_SCOPE and patch expectations in prompts.

---

### 1.3 Task Routing (TASK_ROUTING_SPEC)

**Core routing:**

* `specs/core/execution_request.schema.json`

  * Generic “unit of work” schema:

    * `request_id`, `project_id`, `phase_id`, `workstream_id`
    * `task_kind` (open enum)
    * `origin` (who/what created it)
    * `classification` (complexity, risk_tier, domain, priority)
    * `resource_scope` (generic, not “files”)
    * `constraints` (generic validation/behavior fields)
    * `prompt_spec` (link to `PromptInstance` template)
    * `routing` (strategy, allowed_tools, max_attempts, timeout)
    * `telemetry` (correlation_id, trace_flags)

* `specs/core/router_config.schema.json`

  * Schema for routing configuration:

    * `apps` (tool registry: capabilities, limits)
    * `rules` (match conditions and routing strategies)
    * `defaults` (fallback behavior)
    * `guard_rules` (simple pre-routing guards).

* `specs/core/task_routing_spec.md`

  * Describes how:

    * ExecutionRequests are created from workstreams/tasks,
    * RouterConfig is applied,
    * Phase and resource constraints are enforced before routing.

**Software-dev profile (optional):**

* `specs/profiles/software_dev/execution_request.dev_profile.md`

  * Documents how `resource_scope` is specialized into `files_scope` for dev projects.
  * Adds conventions for test requirements, patch-only, etc.

---

### 1.4 Cooperation & Orchestration (COOPERATION_SPEC)

**Core (project-agnostic):**

* `specs/core/run_record.schema.json`

  * Schema for `RunRecord`:

    * `run_id`, `project_id`, `phase_id`, `workstream_id`,
    * timestamps, `state`, `state_reason`, `origin`, `counters`.

* `specs/core/step_attempt.schema.json`

  * Schema for `StepAttempt`:

    * per-tool invocation details,
    * `state`, `state_reason`, `outputs` (generic).

* `specs/core/run_event.schema.json`

  * Schema for `RunEvent`:

    * `event_id`, `run_id`, optional `step_attempt_id`,
    * `ts`, `kind` (enumerated, but generic: `run_created`, `tool_call_started`, etc.),
    * `payload` (arbitrary object).

* `specs/core/cooperation_spec.md`

  * Defines:

    * Worker & queue model (Router Worker, Tool Worker, etc.),
    * Zone model (STATIC / EDIT / RUNTIME, conceptually),
    * Run state machine and allowed transitions,
    * Requirements for emitting RunEvents.

**Profiles (optional):**

* `specs/profiles/software_dev/cooperation.dev_profile.md`

  * Explains how EDIT zone maps to Git worktrees, tests, etc. for dev projects.

---

### 1.5 Phase Specification (PHASE_SPEC_MASTER)

**Core phase spec:**

* `specs/core/phase_spec.schema.json`

  * Generic phase definition:

    * `phase_id`, `name`, `category`, `description`.
    * `resource_scope` (not hardcoded to files).
    * `constraints` (behavioral + verification; generic types).
    * `acceptance`:

      * `mode` (“all/any/custom”)
      * `checks[]` (using `check_definition.schema.json`)
      * `post_actions[]` (generic action descriptors).

* `specs/core/phase_spec_master.md`

  * Explains:

    * What a phase is in the framework,
    * How `resource_scope` and `constraints` act as contracts,
    * How `acceptance` ties into Run success criteria.

**Software-dev profile (optional):**

* `specs/profiles/software_dev/phase_spec.dev_profile.schema.json`

  * Extends phase spec with dev-centric fields:

    * `files_scope` (read/write/create/forbidden + strict overrides),
    * `constraints.patch` (max_lines_changed, max_files_changed, patch_required, etc.),
    * `constraints.tests` (tests_must_run, tests_must_pass, test_command).

* `specs/profiles/software_dev/phase_spec.dev_profile.md`

  * Narrative: how to define dev phases with file scopes, patch constraints, tests.

---

### 1.6 Workstream & Task Specification (WORKSTREAM_SPEC)

**Core workstream spec:**

* `specs/core/workstream_spec.schema.json`

  * Workstream instance:

    * `workstream_id`, `project_id`, `phase_id`
    * `name`, `objective`, `tags`
    * optional `resource_scope` (narrower than phase)
    * optional `constraints` (tighten phase constraints)
    * `concurrency`, `error_handling`, `acceptance` (using shared check schema)
    * `tasks[]` (`TaskSpec` refs).

* `specs/core/task_spec.schema.json`

  * Task specification:

    * `task_id`, `name`, `kind` (open enum)
    * `depends_on`, `allow_parallel`
    * `classification` (complexity, risk_tier, domain, priority)
    * optional `resource_scope_delta` (task-level narrowing)
    * optional `constraints_delta` (task-level tightening)
    * `execution` (max_attempts, timeout, retry_strategy, background)
    * `prompt_template_ref`, `prompt_overrides`
    * `execution_request_template` (for building ExecutionRequest)
    * `error_handling` (what to do on failure)
    * `acceptance` (task-local checks).

* `specs/core/workstream_spec.md`

  * Explains:

    * Relationship between Phase → Workstream → Tasks,
    * How ExecutionRequests are generated,
    * How task dependency & concurrency are interpreted.

**Profiles:**

* `specs/profiles/software_dev/workstream.dev_profile.md`

  * Usage patterns for code workstreams (refactor, migration, error handling, etc.).

---

### 1.7 Change / Patch Management (generic core + dev profile)

**Core change management:**

* `specs/core/change_artifact.schema.json`

  * Generic change representation:

    * `change_id`, `kind` (e.g. `file_patch`, `config_update`, `db_migration`),
    * `format` (e.g. `unified_diff`, `json_patch`, `sql_script`),
    * `target_resource` (generic),
    * `origin`, `summary`, optional `scope` metrics,
    * `payload` (format-specific).

* `specs/core/change_ledger_entry.schema.json`

  * Generic ledger entry:

    * `ledger_id`, `change_id`, `project_id`, `phase_id`, `workstream_id`, `state`, `state_history[]`, `validation`, `apply`, `relations`.

* `specs/core/change_policy.schema.json`

  * Generic policy for changes:

    * `scope` (global/project/phase/doc),
    * `constraints` (allowed formats, validation requirements, approvals, etc.).

* `specs/core/change_management_spec.md`

  * Describes:

    * Change lifecycle states,
    * Invariants (change artifacts must be ledgered, state transitions, policy enforcement),
    * Relationship with phases/workstreams.

**Software-dev patch profile:**

* `specs/profiles/software_dev/file_patch_artifact.schema.json`

  * Specialization of `change_artifact` where:

    * `kind = "file_patch"`, `format = "unified_diff"`,
    * `scope.files_touched`, `line_insertions`, `line_deletions`, `hunks`,
    * `diff_text`.

* `specs/profiles/software_dev/file_patch_ledger_entry.schema.json`

  * Specialization of `change_ledger_entry` for file patches:

    * `validation` fields: `format_ok`, `scope_ok`, `constraints_ok`, `tests_ran`, `tests_passed`.

* `specs/profiles/software_dev/patch_policy.schema.json`

  * Dev-specific constraints:

    * `patch_required`, `max_lines_changed`, `max_files_changed`,
    * `forbid_binary_patches`, `forbid_touching_paths`, `require_tests_for_paths`, etc.

* `specs/profiles/software_dev/patch_management_spec.md`

  * Narrative of patch lifecycle (created → validated → queued → applied → verified → committed / quarantined),
  * How it ties into tests and CI.

---

## 2. Framework Guides (Project-Agnostic)

These are higher-level “how to use the framework” docs. They should all have doc meta and be written for agents *and* humans.

* `guides/framework_overview.md`

  * High-level map explaining all core specs:

    * Phases, workstreams, tasks, prompts, routing, runs, change management.

* `guides/doc_meta_usage.md`

  * How to apply `doc_meta` to every spec/guide/instance file.
  * Conventions for `doc_type`, `doc_layer`, semantic versioning, etc.

* `guides/coordination_guide.md`

  * Generic version of the coordination guide:

    * Worker roles,
    * Queues,
    * State diagrams,
    * How multiple tools are orchestrated via Runs/StepAttempts/Events.

* `guides/profiles_software_dev.md`

  * Explains the **software-dev profile**:

    * How it specializes resource_scope → files_scope,
    * How tests/patches are treated,
    * How to adopt/ignore the profile for a given project.

---

## 3. Registry & Ledger Files

**Note:** For the framework itself, you’ll probably just define *schemas* and “example entries.” Actual per-project registries live in each project.

Framework-level examples:

* `registry/examples/doc.registry.example.yaml`

  * Example of a docs registry (key → doc meta).

* `registry/examples/change.registry.example.yaml`

  * Example change registry mapping `change_id` → metadata.

* `registry/examples/run.registry.example.jsonl`

  * Example run ledger/registry (one RunRecord per line).

---

## 4. Tools (Generic Helpers)

These aren’t required for the spec to exist, but they’re part of the **framework implementation**.

* `tools/validate_specs.py`

  * Validates all spec and instance files against the JSON Schemas.

* `tools/render_prompt_instance.py`

  * Renders a `PromptInstance` from a template + overrides.

* `tools/build_execution_request.py`

  * Given a Workstream + Task + Phase instance, produces an `ExecutionRequest` JSON.

* `tools/check_acceptance.py`

  * Evaluates `acceptance.checks` for phases/workstreams/tasks against Run/Change/CI data.

(You can add dev-profile-specific tools under `tools/dev/` without polluting the core.)

---

## 5. Profiles & Integrations for Software-Dev (Optional Layer)

These are **not** part of the strict core, but are reusable across *many* dev projects.

* `specs/profiles/software_dev/path_abstraction_spec.md`

  * Generalized version of your PATH_ABSTRACTION_SPEC:

    * Key → path mapping,
    * Resolution rules,
    * CLI/SDK expectations.

* `specs/profiles/software_dev/path_indexer_spec.md`

  * Spec for a path/index analysis tool (like your hardcoded path indexer):

    * Inputs/outputs,
    * Section classification,
    * How results feed into constraints/acceptance.

* `specs/profiles/software_dev/ci_path_standards.md`

  * Template for describing path/module standards enforced by CI:

    * Deprecated modules,
    * Forbidden directories,
    * required abstractions.

* `guides/dev_ci_integration.md`

  * How to integrate the dev profile with CI:

    * Run validation / path indexer,
    * Evaluate phase/workstream acceptance in CI.

---

## 6. Examples (Non-Core, Domain-Specific)

Everything under `/examples` is **explicitly non-core** and may be project-specific. For clarity, you’d keep your error-pipeline material here.

Example structure:

```text
/examples
  /error_pipeline
    PH-ERR-01.phase.yaml
    PH-ERR-02.phase.yaml
    WS-ERR-01A.workstream.yaml
    WS-ERR-02A.workstream.yaml
    README.md               # explains this as a reference implementation
```

These reference implementations:

* Show how to instantiate Phase/Workstream/Task/Change specs,
* Are intentionally *not* treated as framework “musts”.

---

## 7. Summary

If you want a one-liner view:

* **Core** → everything under `specs/core` + generic `guides/`
* **Profiles (software-dev)** → `specs/profiles/software_dev` + dev-specific guides/tools
* **Registries & Tools** → `registry/examples` + `tools/` (helper scripts)
* **Examples (modules)** → `examples/<module_name>/...`

This document itself can live as:

* `guides/framework_file_inventory.md`

and act as the authoritative list of “what files belong in the framework” for both humans and agentic tools.
