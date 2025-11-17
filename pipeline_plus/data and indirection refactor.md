At a high level, those four docs are basically saying:

* **“Use data and indirection to do the scary refactor, not raw AI brute-force.”**

  1. Build a **Hardcoded Path Indexer + DB** (WS-01) and use it as ground truth for *all* risky path edits.
  2. Define **sections + section map**, then do a **Section-Aware repo refactor** in ordered workstreams.
  3. Add a **Path Registry + Resolver** (PATH_ABSTRACTION) so scripts use keys like `phase_docs.ph02_state_layer_spec` instead of raw paths.
  4. Drive execution via **workstreams** (WS-01..WS-17) with explicit dependencies so you can parallelize safely.

Given your tool limits (Codex / Copilot / Gemini capped, Aider uncapped but needs guardrails), the best plan is:

> **Use the pipeline + indexer to carry most of the weight, and spend your expensive models on designing tools, not doing the bulk edits.**

Below is a concrete, lightweight strategy broken down by: **execution order, scripts vs custom agent, orchestrator, GitHub/CCPM integration, and tool assignments.**

---

## 1. Execution Order: What to Do First (and Why)

The docs already give you a dependency graph; we’ll respect that.

**Stage 0 – Safety + Baseline**

* Snapshot current repo state; run `pytest`, linters, etc.
* Generate a quick “before” report:

  * `python scripts/validate_workstreams.py --json` (ensure existing bundles are OK).
  * Run your spec tools (`spec_indexer`, etc.) so you can compare later.

**Stage 1 – WS-01: Hardcoded Path Indexer (foundation)**

Implement Part B of the spec: scanner + SQLite DB `refactor_paths.db`, CLI, docs.

Artifacts:

* `tools/hardcoded_path_indexer.py` (scanner).
* `scripts/paths_index_cli.py` with commands like `paths-index scan / summary`.
* DB tables: `path_patterns`, `files`, `occurrences`, etc.
* `docs/HARDCODED_PATH_INDEXER.md`.

This gives you a *data-driven map* of every `"PHASE_DEV_DOCS"`, `"src/pipeline"`, `MOD_ERROR_PIPELINE`, etc.

**Stage 2 – WS-02: Section Map + Refactor Plan**

Populate `config/section_map.yaml` + `docs/SECTION_REFACTOR_PLAN.md`, making heavy use of indexer reports.

* Decide where each directory goes (`core/`, `error/`, `spec/`, `pm/`, `aim/`, `aider/`, `gui/`, `infra/`, `meta/`).
* Capture **old → new path mapping** as structured data for later.

**Stage 3 – Path Registry & Resolver (PATH_ABSTRACTION)**

Implement the **Path Registry** and **Resolver**:

* `config/path_index.yaml` — keys → paths + section, description, flags.
* `src/path_registry.py` with `resolve_path(key)` and `list_paths(section=None)`.
* CLI wrapper: `scripts/paths_resolve_cli.py` (`paths-resolve`, `paths-list`, `paths-debug`).
* Docs: `docs/PATH_ABSTRACTION_SPEC.md` and updated `docs/PATH_INDEX_SPEC.md`.

This is your **indirection layer**; it turns future refactors into “update YAML” instead of “hunt through the repo.”

**Stage 4 – Section Refactor Workstreams (WS-03..WS-16)**

Use the existing Section-Aware Workstream Plan + dependency table to create actual workstreams:

* For each WS (e.g., `WS-03 Refactor Meta`, `WS-04 Refactor GUI`, `WS-05 Refactor Infra`…):

  * Define **files_scope** and **files_create**.
  * Set `depends_on` matching the table.
  * Choose a `tool` (`aider`, `manual`, `custom-script`) based on risk & quota.
* Convert each into `workstreams/ws-0x-*.json` obeying `workstream.schema.json`.

You can run `python scripts/validate_workstreams.py` to check for overlap / cycles and optionally sync to DB.

**Stage 5 – Gradual Script Refactor to Keys**

Now use the indexer + path registry to *incrementally* replace hardcoded paths in scripts:

* Target paths like `PHASE_DEV_DOCS`, `AIDER_PROMNT_HELP`, `MOD_ERROR_PIPELINE`, etc.
* Replace with `resolve_path("phase_docs.ph02_state_layer_spec")`–style keys in small batches.
* Re-scan with `paths-index`, mark occurrences as `updated` in DB.

**Stage 6 – CI / Enforcement**

* Add CI jobs that run `paths-index` and fail if forbidden old patterns appear.
* Optionally enforce “no new hardcoded paths” for key patterns via lints/tests.

---

## 2. How to Use Scripts vs “Custom Agent” vs Orchestrator

You already have:

* **Workstream bundles + schema** (`schema/workstream.schema.json`, `src/pipeline/bundles.py`).
* **SQLite state store** (`schema.sql` with runs/workstreams/errors/events).
* **Orchestrator** that runs EDIT → STATIC → RUNTIME with FIX loops and scope validation.

So instead of building a huge new “agent framework”, I’d:

### 2.1. Use Dumb Scripts for Heavy Lifting

Let scripts handle **repetitive, high-volume work**:

* `paths-index scan` / `paths-index summary` – scanning & reporting.
* `paths-resolve` – key→path resolution.
* `section_refactor.py` – uses `config/section_map.yaml` + `refactor_paths.db` to:

  * `git mv` files from old→new sections.
  * Update imports, maybe using regex or AST transforms.
* `paths-enforce` – optional script invoked in CI to check for new deprecated patterns.

These don’t consume model tokens at all once authored.

### 2.2. Let the Existing Orchestrator be the “Agent Brain”

Use `src/pipeline/orchestrator.py` as your **lightweight autonomous runner**:

* Encode each WS-0x as a bundle (`workstreams/ws-0x-*.json`).

* For each WS:

  ```bash
  python scripts/run_workstream.py --ws-id ws-xx-something
  ```

* Orchestrator will:

  * Call EDIT step (AI tool via `prompts.run_aider_*`).
  * Run STATIC tools (linters, indexer checks) via `tools.run_tool`.
  * Run RUNTIME tests.
  * Use circuit breakers & FIX loops to avoid infinite AI retries.
  * Validate that changes stay within `files_scope` (no repo-wide accidental damage).

This gives you “autonomy” with strong guardrails, but no fancy agent framework.

### 2.3. A Thin “Refactor Agent” Script on Top

If you want a single command:

* `scripts/refactor_sections.py`:

  * Reads the **dependency table** from `dependency-aware path.md` or a CSV version.

  * Filters for WS’s you’ve marked as “enabled”.

  * For each WS whose dependencies are done, calls:

    ```bash
    python scripts/run_workstream.py --ws-id <ws-id>
    ```

  * Stops if any WS fails, so you don’t cascade broken states.

That’s “custom agent” without complexity: just a loop on top of your orchestrator.

---

## 3. Tool Strategy: Aider vs Codex vs Copilot vs Gemini

Your constraints:

* **Aider** – unlimited-ish, local, already integrated (tool profile + Aider contract).
* **Codex / Copilot / Gemini** – powerful, but usage-capped.

Best approach:

### 3.1. Use Expensive Models for Designing Tools & First Passes

* **WS-01 (Index DB)** & **Path Registry / Resolver** are *perfect* candidates:

  * Ask Codex or Gemini to *write the initial implementation* of:

    * `tools/hardcoded_path_indexer.py`
    * `scripts/paths_index_cli.py`
    * `src/path_registry.py`
    * `scripts/paths_resolve_cli.py`
  * Use very focused prompts: paste the relevant spec sections only.
* Once those exist, 99% of the work they do later is **non-AI**.

### 3.2. Use Aider for Local, Scoped Refactors

Because you’re worried about Aider going “too big”, lean on your pipeline:

* Define **small files_scope** in the bundle.
* Let orchestrator create a **worktree** and validate scope after each WS.
* Have Aider only edit within that worktree and that section (e.g., “update imports for `core/` only”).

So Aider becomes a surgical tool, not a repo-wide wrecking ball.

### 3.3. Reserve Codex/Copilot/Gemini for “Spikes”

Examples:

* Designing the **section layout** (reviewing `config/section_map.yaml`).
* Complex refactor steps around **core state machine**, where logic is subtle.
* Generating one-off migration scripts you’ll then run repeatedly.

You can represent these as:

* `tool: "manual"` or `"codex"` in some workstreams, and treat them as “human/AI assisted” tasks where the orchestrator logs that they’re complete but doesn’t run them automatically.

---

## 4. GitHub Project Management + CCPM + OpenSpec

You already have hooks:

* Workstream schema has `ccpm_issue` to link a workstream to an issue/epic.
* Orchestrator has optional `github_sync` integration that posts lifecycle comments as WS progresses.
* `openspec_parser.py` can generate a CCPM/GitHub epic payload via `--create-epic`.

**Recommended pattern:**

1. **OpenSpec change → Epic + Workstreams**

   * Author an OpenSpec change for “Section-Aware Repo Refactor” in your `openspec/changes` dir (see Fission-AI/OpenSpec on GitHub for shape).

   * Run:

     ```bash
     python -m src.pipeline.openspec_parser --change-id OS-SECTION-REF --generate-bundle --create-epic
     ```

   * Use the `--create-epic` JSON to create a GitHub issue / CCPM epic (CCPM repo: `automazeio/ccpm` on GitHub).

   * Use the generated bundle as seed for your `workstreams/*.json` (fill in `files_scope`, `depends_on` based on your dependency table).

2. **GitHub / CCPM as “source of truth” for status**

   * One issue per workstream (WS-01..WS-17).
   * Store the issue number in `ccpm_issue` in the bundle.
   * Let orchestrator’s `github_sync` comment on those issues as steps complete.

3. **Claude Code Project Management (CCPM)**

   * You can also have CCPM manage the same tasks:

     * Create CCPM tasks for each WS ID.
     * Use the CCPM CLI / MCP integration from Claude Code to show progress or trigger `scripts/run_workstream.py` from inside Claude Code sessions.
   * The dependency table in `dependency-aware path.md` is already in a CCPM-friendly format (WS ID + dependencies).

Net effect: **OpenSpec → CCPM/GitHub → Workstreams → Orchestrator** is one continuous chain.

---

## 5. Concrete “Next Steps” That Are Lightweight

If you want a very short actionable list:

1. **Implement WS-01 Hardcoded Path Indexer** using Codex/Gemini for the code, then run it locally for free afterwards.
2. **Implement PATH Registry + Resolver** per `PATH ABSTRACTION & INDIRECTION LAYER.md` (YAML + Python + CLI).
3. **Turn `dependency-aware path.md` into `workstreams/*.json`**:

   * One bundle per WS.
   * Fill `depends_on`, `files_scope`, `tool`, `ccpm_issue`.
4. **Wire those workstreams into orchestrator** and test one low-risk section (e.g., `meta/`, `gui/`) end-to-end with Aider as the tool.
5. **Create matching GitHub/CCPM issues** for each WS and add the IDs to `ccpm_issue`.
6. Once that loop is solid for 1–2 sections, **expand to the rest** (error/spec/core) in order, using indexer + path registry + orchestrator to keep changes safe and reviewable.

If you’d like, next step I can help you:

* Sketch the actual `workstreams/ws-01-hardcoded-path-index.json` and `ws-02-section-map.json`, including which tool to use and acceptance tests.
* Or write a prompt template for Codex/Gemini to implement `hardcoded_path_indexer.py` exactly to your spec so you only burn one or two “expensive” calls.
