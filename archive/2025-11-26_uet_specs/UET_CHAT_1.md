---
doc_id: DOC-GUIDE-UET-CHAT-1-1125
---

Got it — I’ll stay in planning/architecture mode only and **won’t** start drafting any actual documents yet.

Based on the project knowledge you’ve fed in, here’s how I’d frame the *documentation suite* we should design next, plus how it ties back to what already exists.

---

## 1. What the current knowledge base is already telling us

From the files, you already have the core “org chart” for an agentic documentation system:

* **Agent Operations as the top brain**
  `AGENT_OPERATIONS_SPEC v1.0` explicitly organizes the world into four specs:

  * `PROMPT_RENDERING_SPEC`
  * `TASK_ROUTING_SPEC`
  * `PATCH_MANAGEMENT_SPEC`
  * `COOPERATION_SPEC` 
    That’s basically a ready-made skeleton for a reusable doc suite.

* **Prompt side is rich but fragmented**
  You’ve got:

  * Anthropic-style 3C + persona patterns and XML-ish structuring.
  * A massive *AI-Optimized Prompt Engineering Reference System* with TOC, schemas, and validation concepts. 
  * PRR Project Instructions (decision tree, architecture-aware, contract-first behavior). 
  * A concrete `WORKSTREAM_V1.1` template already tuned for tool-neutral prompts. 
    The missing piece is a single **PROMPT_RENDERING_SPEC** that says: “Here is the one canonical way all projects will describe prompts + workstreams, and how we validate them.”

* **Routing & orchestrator patterns are clearly defined**

  * Central router/orchestrator, app registry, routing config, task schema (`task_id`, `capabilities`, `timeouts`, etc.). 
  * Phase plans + workstreams + Git worktrees + background workers for parallel execution. 
  * `pipeline_plus` docs clarifying how section-based refactors, DeepSeek/Ollama, Autorun, and tool profiles fit into the stack. 
  * Invoke / Invoke-Build as thin outer task runners, not a new brain. 
    All this wants to live under a reusable **TASK_ROUTING_SPEC** + **COOPERATION_SPEC** family rather than scattered explanations.

* **Patch files are already your canonical change format**

  * Unified diff is the universal, language-agnostic change carrier, ideal as a tool-to-tool artifact. 
  * The integration spec shows exactly where to capture, hash, scope-check, and ledger patches (e.g., `.ledger/patches/ws-{id}-{run}.patch`). 
    This should become a formal **PATCH_MANAGEMENT_SPEC** that any project can adopt.

* **Behavioral rules and anti-patterns are already spelled out**

  * `DEVELOPMENT RULES DO and DONT` defines atomic phases, file-scope, tests-first, patch isolation, and strict prohibitions (no hallucinated success, no giant refactors, etc.). 
    That doc is essentially your **global law** for how agents should behave.

So: we’re not starting from scratch. We’re really designing a **reusable, project-agnostic shell** around these existing concepts, plus a metadata layer so agents can *validate* that the docs are correct and refuse to act when required pieces are missing.

---

## 2. Proposed documentation suite “stack” (reusable for any project/module)

Think in three layers:

### Layer 0 – Global Governance (project-agnostic)

These exist once and are shared by *all* projects:

1. **AGENT_OPERATIONS_SPEC (Global Index & Contracts)**

   * Role: Master index that defines:

     * Which sub-specs exist (`PROMPT_RENDERING_SPEC`, `TASK_ROUTING_SPEC`, `PATCH_MANAGEMENT_SPEC`, `COOPERATION_SPEC`).
     * How to map concepts into those specs (the `<MAPPING_*>` entries you already have). 
   * Machine-readable: XML/Hybrid-Markdown with stable IDs for each section and mapping entry.
   * Patch-friendly: one rule per line, stable section ordering.

2. **DEVELOPMENT_RULES (Global DO/DON’T + Anti-Patterns)**

   * Role: Global “constitution” describing:

     * Mandatory behaviors (ground truth over vibes, atomic phases, test-driven everything, worktree & patch isolation, etc.). 
     * Strict anti-patterns (hallucinated success, giant refactors, scope-violating patches).
   * Machine-readable: bullet-per-rule layout, unique rule IDs like `RULE_DEV_ATOMIC_01`.

### Layer 1 – Core Spec Families (reused across projects)

These define *how the system works*, not a particular project.

3. **PROMPT_RENDERING_SPEC**

   * Encodes:

     * Canonical prompt template family (e.g., `WORKSTREAM_V1.1`) with required sections `[HEADER]`, `[OBJECTIVE]`, `[CONTEXT]`, `[CONSTRAINTS]`, `[FILE_SCOPE]`, `[OUTPUT_FORMAT]`, `[VALIDATION]`, etc.
     * 3C + persona rules (Clarity, Context, Constraints + ROLE line).
     * Classification rules (complexity, quality, domain) and reasoning mode selection.
     * Tool-neutral vs tool-specific views (Aider view, Codex view, etc.), with the core template always tool-neutral.
   * Machine-readable:

     * YAML/JSON schema describing valid prompt sections.
     * Per-section constraints (e.g., `[HEADER]` must contain `WORKSTREAM_ID`, `CALLING_APP`, `TARGET_APP`).
   * Validation:

     * If a prompt is missing mandatory sections or fields, agent must **refuse to execute** and emit a structured “prompt_invalid” error.

4. **TASK_ROUTING_SPEC**

   * Encodes:

     * Task object schema (task_id, source_app, capabilities, constraints, timeouts, routing_state, retry_state, metadata). 
     * Router configuration schema (`router.config.yaml` apps + routing + global rules).
     * Classification-driven routing (e.g., complexity/domain from prompts controlling timeouts and tool selection).
   * Machine-readable:

     * JSON Schema for tasks; YAML schema for router config.
   * Validation:

     * Pre-flight: any task missing required fields or violating schema is rejected before hitting any tool.

5. **PATCH_MANAGEMENT_SPEC**

   * Encodes:

     * Unified diff as canonical change artifact (creation, application, conflict behavior). 
     * Patch lifecycle: capture → ledger → scope validation → tests → apply → commit → rollback plan.
     * Ledger layout (`.ledger/patches/` naming, diff hashes, oscillation detection).
   * Machine-readable:

     * Patch metadata JSON schema (patch_id, ws_id, run_id, diff_hash, files_modified, line_count, etc.).
   * Validation:

     * Rules for rejecting patches that:

       * touch files outside declared `files_scope`.
       * repeat the same diff hash more than `N` times (oscillation).
       * exceed line-count or file-count limits for a given phase.

6. **COOPERATION_SPEC**

   * Encodes:

     * Orchestrator state model and DB schema (runs, workstreams, events, step_attempts, errors). 
     * Queue contract (`.tasks/inbox/running/done/failed`) and background worker behavior.
     * EDIT → STATIC → RUNTIME pipeline and error/fix loops.
     * Rules for cross-agent collaboration, escalation (Aider → Codex → Claude), and prohibited behaviors (cross-scope edits, unlogged changes).
   * Machine-readable:

     * State transition table (JSON).
     * Event types and payload schemas.

### Layer 2 – Project/Module-Specific Instantiations

These are the *per-project* or *per-module* documents that plug into the global specs.

7. **PROJECT_PROFILE_SPEC**

   * Defines project-level constants:

     * `project_id`, repo locations, runtime environments (Windows/WSL), default tools, CI entrypoints.
     * Which global versions of PROMPT_RENDERING_SPEC, TASK_ROUTING_SPEC, etc. this project follows (like SemVer pinning).
   * Machine-readable:

     * YAML with strict schema so agents know exactly which stack to assume.

8. **PHASE_SPEC_MASTER + PHASE_SPEC_INSTANCE**

   * Master:

     * Reusable spec describing a Phase: ID, objective, allowed workstreams, dependencies, entry/exit conditions.
     * Aligns with your Universal Phase Spec + PRO_Phase mandatory structure (all phases must define objective, file scope, acceptance tests, etc.). 
   * Instances:

     * Per-phase docs: `PH-XX_<name>.md` or `.yaml` that fill those required fields for a specific project.
   * Machine-readable:

     * JSON Schema for phase definition, plus stable section IDs (e.g., `PHASE_METADATA`, `DEPENDENCIES`, `ACCEPTANCE_TESTS`).

9. **WORKSTREAM_SPEC (Bundle/Task Schema)**

   * Essentially your `workstream.schema.json` and `PHASE_PLAN.yaml` semantics generalized:

     * `id`, `tasks`, `files_scope`, `files_create`, `acceptance_tests`, `depends_on`, `tool`, `circuit_breaker`, etc.
   * Machine-readable:

     * JSON Schema (project-agnostic).
   * Validation:

     * Orchestrator only accepts workstreams that pass this schema and are consistent with the project’s PHASE_SPEC.

10. **ERROR_PIPELINE_SPEC (PH-ERR-XX family)**

    * Defines:

      * All possible deterministic paths a file can take after an error: retry, escalate, quarantine, GitHub-save (as you described).
      * Triggers for entering error pipeline (test failure, scope violations, patch validation failures).
      * Exit conditions and required artifacts (patch in quarantine folder, issue opened, etc.).
    * Machine-readable:

      * State machine table for error flows; classification of error types; mapping from error signatures to escalation strategies.

11. **TOOL_PROFILE_SPEC & CAPABILITY_CARD_SPEC**

    * Tool profiles:

      * Aider, Codex, Claude, Ollama-Code, etc. with `cmd_template`, capabilities, timeouts, delegation rules.
    * Capability cards:

      * Machine-readable records of what each tool is good at and constraints (for routing decisions).

---

## 3. Cross-cutting design rules for machine-readability & patch-friendliness

For *every* doc type in the suite, we should enforce:

1. **Strict frontmatter + stable IDs**

   * YAML frontmatter with:

     * `doc_id`, `doc_type`, `version`, `status`, `schema_ref`, `ulid`.
   * Each section has a stable identifier (e.g., `## [PRINCIPLE_PRECISION_PRINCIPLE]`) so:

     * Agents can target sections deterministically.
     * Patch files can safely modify a specific block without reflowing everything.

2. **One-concept-per-line where possible**

   * Rules, requirements, and constraints written as:

     * One bullet per rule.
     * No multi-sentence paragraphs that span many lines.
   * This keeps unified diffs tiny and legible for agents.

3. **ASCII-only, no “clever” formatting in core specs**

   * Already mandated in AGENT_OPERATIONS_SPEC (`ascii_only` principle). 
   * Emojis, odd Unicode, auto-numbered lists: reserved for human-facing docs, not for the machine-optimized suite.

4. **Schema-first validation**

   * Each doc type has a companion JSON/YAML schema in `/schema/…`.
   * Agents:

     * **Must validate** docs against schemas before execution.
     * **Must refuse** to run if docs fail validation (and emit structured error).

5. **Patch-first change model**

   * All edits to docs:

     * Are expected to be delivered as unified diffs.
     * Are recorded in `.ledger/patches/` with metadata, same as code patches.
   * The docs themselves discourage “rewrite the whole file” operations unless performing a controlled schema migration.

---

## 4. Where we can go next (without drafting yet)

Staying in planning mode, the next concrete steps *could* be:

1. **Define the “Doc Meta Schema” once**
   A tiny, universal schema used by *all* docs in the suite (`doc_id`, `doc_type`, `version`, `schema_ref`, etc.).

2. **Lock in the four core spec families**
   Sketch the *fields and sections* for:

   * `PROMPT_RENDERING_SPEC`
   * `TASK_ROUTING_SPEC`
   * `PATCH_MANAGEMENT_SPEC`
   * `COOPERATION_SPEC`
     …without writing their full prose yet.

3. **Choose one project-specific doc type to formalize first**
   Most leverage probably comes from:

   * `PHASE_SPEC_MASTER` + `PHASE_SPEC_INSTANCE`, or
   * `WORKSTREAM_SPEC` (since it feeds router, prompts, and patch flow).

When you’re ready for the *next task*, we can pick one of those (or a different starting point you prefer) and design the *schema + outline* for that doc type first—still staying schema/structure-level rather than full narrative.
