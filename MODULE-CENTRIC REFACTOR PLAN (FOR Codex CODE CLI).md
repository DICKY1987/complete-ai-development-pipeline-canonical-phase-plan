````markdown
# MODULE-CENTRIC REFACTOR PLAN (FOR Codex CODE CLI)

## 0. Purpose of this Document

You are running inside the repository:

- `https://github.com/DICKY1987/complete-ai-development-pipeline-canonical-phase-plan`

The human owner wants to refactor this repo into a **module-centric architecture** where:

- Each **module** is the unit of ownership.
- **All artifacts belonging to a module live inside that module’s folder**:
  - Code, docs, schemas, tests, configs, scripts, examples.
- There are **no free-floating `docs/`, `tests/`, `schema/` trees** holding module-specific artifacts at the root.
- The repo already uses **ID + registry indirection** (e.g. `doc_id`, `pattern_id`, etc.), so scripts rarely hard-code paths; they call the **registry** instead.

Your job as Codex Code is to:

1. Understand this architecture and the constraints.
2. Use the existing data (data-flow docs + path summaries) to **classify folders into module categories**.
3. Help migrate the repository toward the target **module-centric layout**, **primarily by updating the registry and moving files**, not by rewriting core logic.
4. Do so **safely, incrementally, and deterministically**, in small, verifiable phases.

This doc gives you the **conceptual model** and **recommended approach**. Actual execution should use the owner’s **patterns / phase plans** where available and create new ones as needed.

---

## 1. Core Concepts

### 1.1 Module-Centric Architecture

**Definition of a module (for this repo):**

> A module is a cohesive unit of functionality (pipeline stage or feature service) that owns *all* its artifacts:
> - `src/` (code)
> - `docs/`
> - `schemas/`
> - `tests/`
> - `config/`
> - `scripts/` (module-specific helpers)
> - `examples/` (optional)

In the target state:

```text
modules/
  <module_id>/
    src/
    docs/
    schemas/
    tests/
    config/
    examples/
````

**Key rules:**

* A file that conceptually belongs to a module **should live under that module folder**, not under a root-level `docs/`, `schema/`, or `tests/`.
* Root-level `docs/`, `tests/`, `schema/` should hold **only**:

  * Global, cross-module governance (architecture, glossary, meta docs), or
  * Meta tests that touch multiple modules.

---

### 1.2 ID + Registry Abstraction

The repo already uses an **ID → registry → path** abstraction.

Typical usage pattern in code:

```python
doc = registry.load(doc_id="DOC_ULID_1234")
pattern = registry.get_pattern("PAT_EXEC_001")
config = registry.get_config("CFG_AIM_PROFILE_001")
```

The code **knows IDs**, not filesystem paths.

The registry stores something like:

```json
{
  "doc_id": "DOC_ULID_1234",
  "artifact_kind": "spec_doc",
  "path": "docs/patterns/PAT_EXEC_001_spec.md",
  "status": "active",
  "version": "1.0.0"
}
```

**For the refactor:**

* IDs remain stable (they are the API).
* **Paths will change** when we move to `modules/<module_id>/...`.
* The *main work* is:

  * Moving files.
  * Updating registry entries so they point to the new locations.
* Scripts that use IDs should not need changes, as long as the registry stays consistent.

We will also introduce:

* `module_id` — which module owns this artifact.
* `module_kind` — what *kind* of module it is (pipeline stage, feature service, infra, etc.).

Example after refactor:

```json
{
  "doc_id": "DOC_EXEC_PLAN_001",
  "artifact_kind": "exec_plan_doc",
  "module_id": "execution",
  "module_kind": "PIPELINE_STAGE_MODULE",
  "path": "modules/execution/docs/EXEC_PLAN_001.md",
  "version": "1.1.0"
}
```

---

### 1.3 Data Flows (from `DATA_FLOWS.md`)

The repo already has a **data-flow view** of the system. You should treat these flows as the **ground truth** for pipeline-stage boundaries and sub-components.

At a high level, there are at least three key flows:

1. **Workstream Execution Flow** (spec/workstream → orchestrator → tools → results)

   * Components: Validator → Orchestrator → DB → Step Executor → Tool Adapter → DB → User.
2. **Error Detection Flow**

   * Components: Error Engine → Plugin Discovery → File Scanner → Plugin Execution → Aggregation → DB → Report.
3. **Specification Resolution Flow**

   * Components: URI Resolver → Cache → Filesystem → Markdown Parser → Cross-Refs → Cache/DB.

Each of these flows defines **natural modules and submodules**:

* Pipeline stages (intake, planning, scheduling, execution, error, state, reporting).
* Feature services (AIM tools, patterns engine, spec bridge).
* Supporting subsystems (registry, observability, infra).

Use these flows to justify module boundaries (don’t invent arbitrary splits).

---

### 1.4 Path Analysis Data (`paths_summary.txt`, `paths_clusters.json`)

Two input artifacts give a **quantitative map** of how paths are used:

* `paths_summary.txt` — high-level stats over ~2,400 files:

  * Breaks down paths by **kind**:

    * `doc_link`, `code_path`, `config_path`, `fs_literal`, `code_import`.
  * Shows where root-level `docs/`, `tests/`, `engine/`, `tools/`, `gui/`, `schema/`, `state/`, `aim/`, `pm/`, `openspec/`, `ccpm/`, `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/` etc. are used.
* `paths_clusters.json` — structured mapping:

  * Each “section” (e.g. `doc_id`, `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK`, `cleanup_reports`, `developer`, `archive`, `aim`, `scripts`, `pm`, `gui`, `openspec`, `ccpm`, `registry`, `error`, etc.) has counts by `doc_link`, `config_path`, `code_path`, `fs_literal`, `code_import`.

You should use these to:

* Identify which top-level folders correspond to which **module kinds**.
* See where **path-sensitive code/tests** live (lots of `fs_literal` / `code_path`).
* Prioritize refactor order: start where risk is lowest.

---

## 2. Module Kinds (Classification Scheme)

The human wants a **finite list of module kinds** that covers almost all folders. Use this list to classify both **modules** and (optionally) individual **registry entries**.

### 2.1 Module Kind Enum

Treat this as a **canonical enum**:

```yaml
MODULE_KIND:
  - PIPELINE_STAGE_MODULE
  - FEATURE_SERVICE_MODULE
  - INTEGRATION_BRIDGE_MODULE
  - INTERFACE_MODULE
  - REGISTRY_METADATA_MODULE
  - INFRA_PLATFORM_MODULE
  - OBSERVABILITY_REPORTING_MODULE
  - GOVERNANCE_KNOWLEDGE_MODULE
  - SANDBOX_EXPERIMENTAL_MODULE
  - ARCHIVE_LEGACY_BUCKET
```

**High-level meanings:**

1. **PIPELINE_STAGE_MODULE**

   * Core sections of the end-to-end pipeline:

     * Intake → Planning → Scheduling → Execution → Error Handling → State Persistence → Reporting.
   * Example candidates in current repo:

     * `core/`, `engine/`, `state/`, `pipeline/`, parts of `workstreams/`.

2. **FEATURE_SERVICE_MODULE**

   * Big cross-cutting capabilities the pipeline uses.
   * Examples:

     * `aim/` (tool registry/selection).
     * `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/` (patterns engine).
     * `ai-logs-analyzer/`.

3. **INTEGRATION_BRIDGE_MODULE**

   * Bridges to external systems.
   * Examples:

     * `openspec/`, `ccpm/`, `pm/`, `tools/` (external CLIs, when not purely internal helpers).

4. **INTERFACE_MODULE**

   * User-facing entrypoints & interfaces.
   * Examples:

     * `gui/`, `tui_app/`.
     * CLI flows or prompt orchestration layers.

5. **REGISTRY_METADATA_MODULE**

   * ID systems, registries, schemas that describe artifacts.
   * Examples:

     * `registry/`, `doc_id/`, some parts of `schema/`.

6. **INFRA_PLATFORM_MODULE**

   * CI, environment bootstrap, tool configs, generic scripts.
   * Examples:

     * `.github/`, `infra/`, `.ai/`, `.Codex/`, `.execution/`, `.state/`, `scripts/`, `environment/`, `aider/`, sandbox templates.

7. **OBSERVABILITY_REPORTING_MODULE**

   * Logs, reports, metrics, result summaries.
   * Examples:

     * `reports/`, `cleanup_reports/`, log analysis tools.

8. **GOVERNANCE_KNOWLEDGE_MODULE**

   * Global docs, ADRs, glossaries, capability catalogs.
   * Examples:

     * `adr/`, `docs/`, `glossary/`, `capabilities/`, high-level architecture docs at root.

9. **SANDBOX_EXPERIMENTAL_MODULE**

   * Experimental or sandbox areas (not canonical).
   * Examples:

     * `AI_SANDBOX/`, ad-hoc template sandboxes, experimental prototypes.

10. **ARCHIVE_LEGACY_BUCKET**

    * Historical, non-active code/docs kept for reference.
    * Examples:

      * `archive/` and its dated subfolders.

> **Important:** By default, treat `SANDBOX_EXPERIMENTAL_MODULE` and `ARCHIVE_LEGACY_BUCKET` as **read-only** during refactor. Do not move or mutate them unless explicitly asked.

---

### 2.2 Module vs Submodule vs Helpers

Within each `modules/<module_id>/` folder, you will still see internal structure:

* `src/domain/`      → domain logic submodule.
* `src/adapters/`    → integration adapters submodule.
* `src/utils/`       → utilities/helpers submodule.
* `src/cli/`         → CLI interface submodule.
* `docs/`            → documentation submodule.
* `tests/`           → tests submodule.
* `schemas/`         → schemas submodule.

You **do not** need extra `MODULE_KIND` values for these; they are **submodules** of the same module. If helpful, you can annotate:

```json
"submodule_role": "domain" | "adapter" | "utility" | "cli" | "doc" | "schema" | "test"
```

but the **owning module** is still the same `module_id`.

---

## 3. Target Module Set (Conceptual)

The exact mapping will be refined by reading the repo, but conceptually, the system wants modules like:

### 3.1 Pipeline Stage Modules

* `intake_spec/`

  * OpenSpec + CCPM → workstreams.
* `planning/`

  * Decompose workstreams into tasks; build DAG.
* `scheduling/`

  * Dependency resolution; concurrency and queues.
* `execution/`

  * Orchestrate tasks; call tools; run tests.
* `error_recovery/`

  * Error capture; classification; retries; escalation.
* `state_lifecycle/`

  * Runs, tasks, file lifecycle; DB schemas; state machines.
* `reporting/`

  * Reports, summaries, exports.

### 3.2 Feature Service Modules

* `aim_tools/`

  * Tool registry, profiles, selection, health.
* `patterns_engine/`

  * UET patterns, pattern doc suites, pattern registry.
* `spec_bridge/`

  * OpenSpec + CCPM → internal workstreams; URI resolution.
* `registry_core/`

  * Generic doc_id/pattern_id/module_id registry and APIs.
* `gui_shell/` and/or `tui_shell/`

  * GUI/TUI shells over the engine.
* `observability/`

  * Live metrics, dashboards, advanced log analysis.

These correspond fairly directly to existing folders like `aim/`, `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/`, `openspec/`, `ccpm/`, `pm/`, `gui/`, `registry/`, `reports/`, etc.

Your job is to:

* Map **existing folders** to **module_ids** and **module_kinds**.
* Help create the new `modules/` layout that reflects this conceptual map.

---

## 4. Recommended Refactor Strategy (Phased)

You must treat this as a **multi-phase, reversible refactor**. Use small, validated steps. Avoid large, one-shot moves.

### Phase 0 – Safety & Discovery

1. **Confirm clean working tree**:

   * `git status` should be clean or changes explicitly staged/committed before structural refactors.
2. **Backup registry & path mapping data**:

   * Copy existing registry DB / JSON / YAML files to a safe location (e.g. `archive/registry_snapshots/` with timestamp).
   * Keep `DATA_FLOWS.md`, `paths_summary.txt`, `paths_clusters.json` unchanged as reference inputs.
3. **Scan for hard-coded paths**:

   * Use ripgrep/grep to identify usages of `docs/`, `tests/`, `schema/`, etc. in code:

     * Flag ones *not* going through the registry or a path helper.
   * This will inform later repairs.

> Behavior: DO NOT move any files in this phase. Only analysis and snapshots.

---

### Phase 1 – Define & Annotate Modules (Logical Only)

Goal: Introduce module metadata **without moving files yet**.

Steps:

1. **Define module IDs and kinds**:

   * Create a central config (e.g. `modules/MODULES_INVENTORY.yaml`) listing:

     * `module_id`
     * `module_kind`
     * brief description
     * initial guess for legacy root paths (e.g. `engine/`, `aim/`, etc.).
2. **Use `paths_clusters.json` to auto-suggest module_kind**:

   * For each top-level “section” in `paths_clusters.json`:

     * If it’s dominated by `code_path`/`code_import` and under `engine/`, `core/`, `pipeline/`, `workstreams/`, classify as `PIPELINE_STAGE_MODULE`.
     * If under `aim/`, `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/`, classify as `FEATURE_SERVICE_MODULE`.
     * If under `openspec/`, `ccpm/`, `pm/`, classify as `INTEGRATION_BRIDGE_MODULE`.
     * If under `gui/`, `tui_app/`, classify as `INTERFACE_MODULE`.
     * If under `registry/`, `doc_id/`, classify as `REGISTRY_METADATA_MODULE`.
     * If under `reports/`, `cleanup_reports/`, `ai-logs-analyzer/`, classify as `OBSERVABILITY_REPORTING_MODULE`.
     * If under `docs/`, `adr/`, `glossary/`, classify as `GOVERNANCE_KNOWLEDGE_MODULE`.
     * If under `AI_SANDBOX/` or clearly experimental, classify as `SANDBOX_EXPERIMENTAL_MODULE`.
     * If under `archive/`, classify as `ARCHIVE_LEGACY_BUCKET`.
3. **Extend registry schema (logical only)**:

   * Add nullable fields:

     * `module_id`
     * `module_kind`
   * Backfill approximate values per registry row based on its current `path`.

Again, **no physical moves yet**—only adding metadata and ensuring the registry structure supports module-aware operations.

---

### Phase 2 – Extend Registry and Link Artifacts

Goal: Make the registry the single source of truth for module ownership.

1. **For each registry row**:

   * Infer `module_id` (from path → section → module).
   * Infer `module_kind` (from module inventory).
   * Ensure `artifact_kind` is set (e.g. `spec_doc`, `pattern_doc`, `schema`, `unit_test`, `integration_test`, `code_module`, etc.).

2. **Write a validation script**:

   * For every row:

     * Does `path` currently exist on disk?
   * For every *non-archive* file:

     * Is there a registry row?
   * Emit:

     * `missing_files` list.
     * `unregistered_files` list.

3. **Fix obvious gaps** (registrations, not moves):

   * Register files that should be in registry but aren’t.
   * Mark clearly dead/legacy rows for later cleanup (don’t delete yet).

---

### Phase 3 – Introduce `modules/` Skeleton (Still Non-Destructive)

Goal: Create empty module folders with internal structure, to prepare for migration.

For each `module_id` from the inventory:

```text
modules/
  <module_id>/
    src/
    docs/
    schemas/
    tests/
    config/
    examples/
```

* Do **not** move any existing file into these yet.
* This gives a stable target structure for subsequent moves.

---

### Phase 4 – Module-by-Module Migration (Physical Moves)

Now migrate **one module at a time** to keep change sets small and rollback easy.

For each module:

1. **Select legacy paths for this module**:

   * Based on `MODULES_INVENTORY.yaml`, `paths_clusters.json`, and human intention.
   * Example: `aim_tools` pulls from `aim/`, associated docs in `docs/` related to AIM, relevant schemas/tests.

2. **Plan move mapping**:

   * For each file to move:

     * Determine target path under `modules/<module_id>/...`.
   * Example:

     * `aim/config/profiles.yaml` → `modules/aim_tools/config/profiles.yaml`
     * `docs/aim/TOOL_SELECTION.md` → `modules/aim_tools/docs/TOOL_SELECTION.md`
     * `tests/aim/test_profiles.py` → `modules/aim_tools/tests/test_profiles.py`

3. **Perform move (atomic group)**:

   * Use filesystem operations (`git mv` ideally) to move the files.
   * Keep move operations grouped per module for easy rollback.

4. **Update registry paths**:

   * For all rows with `module_id = <module_id>`:

     * Update `path` to point to the new location under `modules/<module_id>/...`.

5. **Run validation script** (for this module only):

   * Every registry row with this `module_id` → file exists.
   * Every file under `modules/<module_id>` → registry row exists.

6. **Run tests**:

   * Preferably run only tests for this module:

     * E.g. discover tests under `modules/<module_id>/tests/`.
   * Fix any path assumptions (e.g. tests importing from old locations).

7. **Commit with clear message**:

   * E.g. `refactor: move AIM module under modules/aim_tools/` plus updated registry snapshot.

Repeat for the next module.

> **Critical behavior:** Always avoid touching `SANDBOX_EXPERIMENTAL_MODULE` and `ARCHIVE_LEGACY_BUCKET` in automatic moves. Only operate on active modules.

---

### Phase 5 – Root Cleanup & Global Docs

After most modules are migrated:

1. **Clean up root-level `docs/`, `schema/`, `tests/`**:

   * Move any remaining module-owned files into their module folders.
   * Leave only:

     * Global ADRs/architecture docs.
     * Glossary.
     * Cross-module governance docs.
     * Global integration/e2e tests.

2. **Update any scripts/test runners**:

   * If they assumed `tests/` at the root:

     * Either:

       * Update them to discover `modules/**/tests/`, or
       * Create a small aggregator under `tests/` that imports module tests.

3. **Regenerate indexes**:

   * Create or update:

     * `docs/MODULE_INDEX.md` linking to `modules/*/docs/`.
     * Optional `modules/README.md` summarizing each module’s purpose.

---

## 5. Operational Guidelines for Codex Code

When acting on this repo, you should:

1. **Prefer registry-based reasoning**:

   * If you need to know where something lives:

     * Ask: “What does the registry say for this `doc_id` / `pattern_id` / `module_id`?”
   * Avoid inventing new hard-coded paths.

2. **Treat module metadata as source of truth**:

   * `module_id` + `module_kind` + `artifact_kind` + `path` is the canonical record.
   * If a file’s module assignment doesn’t match its location, that’s a refactor candidate.

3. **Operate in small, reversible steps**:

   * One module at a time.
   * Use `git mv` and commit frequently with tight scope.

4. **Avoid destructive changes**:

   * Don’t delete files by default.
   * For legacy/unused entries, prefer:

     * Mark as `status: "deprecated"` in registry.
     * Move to `archive/` with a clear date stamp if truly obsolete.

5. **Respect sandbox and archive**:

   * Do not auto-refactor:

     * `SANDBOX_EXPERIMENTAL_MODULE` folders.
     * `ARCHIVE_LEGACY_BUCKET` folders.
   * Treat them as read-only, unless explicitly instructed otherwise by the user.

6. **Use patterns / phase plans where available**:

   * The repo already has pattern specs (UET / pattern doc suites).
   * When possible, create or use patterns like:

     * `REGISTRY_MODULE_CLASSIFICATION_V1`
     * `REGISTRY_REFACTOR_V1`
     * `MODULE_REHOME_<MODULE_ID>_V1`
   * Each pattern should:

     * Declare inputs (e.g., `paths_clusters.json`, registry DB).
     * Declare outputs (e.g., updated registry, files moved).
     * Declare validation steps and rollback plan.

7. **Always produce human-readable reports**:

   * After each module migration, generate:

     * A short report summarizing:

       * Files moved.
       * Registry rows updated.
       * Tests run and results.
   * Store these under a suitable reporting area (e.g. `reports/module_migrations/`).

---

## 6. What You Should Do First (Minimal Starting Plan)

If you need an immediate starting action list:

1. **Read**:

   * `DATA_FLOWS.md`
   * `paths_summary.txt`
   * `paths_clusters.json`
   * Any existing `MODULES_INVENTORY` or registry schema docs.

2. **Create** (if not present):

   * `modules/MODULES_INVENTORY.yaml` with:

     * `module_id`
     * `module_kind`
     * description
     * legacy path hints.
   * A tiny design doc:

     * `docs/MODULE_CENTRIC_ARCHITECTURE_OVERVIEW.md` (you can adapt this doc).

3. **Extend the registry schema** to add `module_id` and `module_kind`.

4. **Write and run a “classification” script/pattern**:

   * Use `paths_clusters.json` + legacy paths to assign `module_kind` and tentative `module_id` to all registry rows.

5. **Stop there and produce a report**:

   * Don’t move any files yet.
   * Present the owner with:

     * The inventory of modules.
     * How many artifacts are in each.
     * Proposed migration order (e.g., start with AIM, then patterns, then execution, etc.).

Once the owner confirms the plan or orders, proceed into Phase 4’s **module-by-module migration**.

---

**End of document.**

This document is intended to be checked into the repo (e.g., as
`docs/Codex_CODE_MODULE_REFACTOR_GUIDE.md`) and used as a reference whenever you (Codex Code CLI) are asked to help reorganize or refactor the repository structure.

```
::contentReference[oaicite:0]{index=0}
```
