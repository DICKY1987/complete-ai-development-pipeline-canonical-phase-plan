Here’s the short version of what each of those three is and how they relate to each other:

---

### 1. **PRO_Phase Specification mandatory structure.md**

Think of this as the **production-grade template** for how a phase MUST be defined.

* It gives a **normative phase template** with all required fields (like `phase_id`, `workstream_id`, objective, dependencies, etc.), usually with **YAML-style examples**.
* It forces you to declare **file scope** in detail (separate lists for `create`, `modify`, and `read_only`).
* It encodes the **standard directory layout** for your system: `.tasks/`, `.ledger/patches/`, `.runs/`, etc.
* It includes an **anti-pattern blocklist** and rules for enforcement (what’s forbidden and how to catch it).

> Mental model: this is the **“golden template + rulebook”** for what a valid phase spec file must look like in production.

---

### 2. **AGENTIC_DEV_PROTOTYPE\UNIVERSAL PHASE SPECIFICATION.txt**

This is the **canonical, conceptual phase spec** for the whole Game Board / agentic system.

* It defines the **universal phase structure**: identity and metadata, core required fields like
  `phase_id`, `workstream_id`, `objective`, `file_scope`, `acceptance_tests`, `dependencies`.
* It describes **Pre-Flight checks**, the **execution loop**, and **completion gates** — basically the lifecycle a phase goes through.
* It encodes the **Operator Execution Standard**: CLI-first, self-healing behavior, worktree isolation, etc.

> Mental model: this is the **big canonical spec** that says “what a phase *is* and how execution is supposed to work” in abstract.

---

### 3. **DEVELOPMENT RULES DO and DONT.md**

This is the **behavior contract / operating rules** for any AI or operator working under this system.

* The “DO” side covers things like:

  * Use **CLI output as ground truth**
  * Keep work **atomic**
  * Use **self-healing loops**
  * Maintain **worktree isolation**
* The “DON’T” side forbids:

  * Claiming success without tests (“hallucination of success”)
  * Giant refactors without phases
  * Permission bottlenecks (“asking instead of doing” for safe actions)
  * Context pollution (loading everything before taking a small step), etc.

> Mental model: this is the **“code of conduct”** for development: what’s allowed vs forbidden in how phases are actually executed.

---

### How they fit together (one-liner)

* **UNIVERSAL PHASE SPECIFICATION.txt** → defines *what a phase is* and its lifecycle.
* **PRO_Phase Specification mandatory structure.md** → defines *exactly how to write a valid phase spec* that the system will accept.
* **DEVELOPMENT RULES DO and DONT.md** → defines *how agents must behave* when executing those phases.

Short answer:
They **don’t replace** your three core specs, but they **do improve and sharpen specific slices** of them:

* **Background_task.md** → gives a *better, concrete implementation* for execution / parallelism than anything in the current three.
* **Patch Files as Unified Diff & Optimal** → gives a *better and more nuanced* patch policy than the current “patch-first” language.
* **Comprehensive Integration Spec – Enhanced Prompt Engineering** → gives a *better canonical definition* for workstream templates, telemetry, and rollout than what’s in the existing specs.

---

## 1. Background_task.md vs your core specs

What it adds:

* A **machine-runnable phase plan format** in YAML: `phases[] -> workstreams[]` with `id`, `tool`, `repo`, `prompt_file`, `timeout_minutes`, `depends_on`, and per-phase `max_parallel_workstreams`.
* A **standard worktree pattern**: `ws/$PhaseId/$WorkstreamId` branches and `.worktrees/$PhaseId-$WorkstreamId` directories, plus a small JSON ledger mapping `task_id → branch → worktree_path`.
* A **background job executor**: `Start-WorkstreamTask` + `Invoke-PhasePlan` that:

  * Enforces `depends_on`
  * Respects `max_parallel_workstreams`
  * Captures logs and simple `task.json` metadata under `.runs/<task-id>/…`

How it compares:

* **UNIVERSAL PHASE SPEC** already says:

  * Phases must define dependencies and parallelization explicitly.
  * Work must happen in isolated worktrees, not directly on main.
* **DEVELOPMENT RULES DO and DONT** already warn against:

  * Over-broad parallelism and racing over same scopes.

But those are **principles**, not an executable pattern.

👉 **Conclusion for Background_task.md**

* It **does not replace** UNIVERSAL PHASE SPEC or DEVELOPMENT RULES.
* It **should become the canonical implementation** of:

  * “How to represent a phase plan as runnable tasks”
  * “How to safely do background tasks + parallel workstreams + worktrees”

I’d treat it as the **“Phase Execution Engine” sub-spec** referenced from:

* UNIVERSAL PHASE SPEC §1.2 / §2.4 (dependencies, execution loop)
* DEVELOPMENT RULES “Over-Broad Parallelism” anti-pattern section.

---

## 2. Patch Files as Unified Diff & Optimal vs current patch sections

What it adds:

* A **full mental model** for when and why to use patches:

  * Multi-machine / multi-agent flows, locked workstreams, review chains, cross-environment delegation.
* Clear **orchestrator responsibilities around patches**:

  * `git apply --check`, language-aware checks (ruff/PSScriptAnalyzer/pytest), file-scope guard rails, quarantine on failure.
* A **decision guide**: when patches are optimal vs when they are *not* (high-level design, huge exploratory refactors, volatile files, etc.).

Your current specs:

* **UNIVERSAL PHASE SPEC** already says:

  * Every non-trivial change must be represented as a patch in `.ledger/patches/{ws_id}-{run_id}.patch`.
  * Handoffs between tools in multi-tool flows MUST use patch transport.
* **PRO_Phase / DEVELOPMENT RULES** already:

  * Enforce patch-first editing and forbid whole-file rewrites when small diffs would do.

What’s different / better in Patch Files doc:

* It **adds nuance** the existing docs lack:

  * Don’t force patches for *analysis / planning* tasks or giant reorganizations.
  * Use **workstream prompt + file_scope** for editing; treat patches as the **transport/audit layer**, not necessarily the in-memory editing format.
* It **fully spells out** multi-agent flows and circuit breaker integration that the core specs only hint at.

👉 **Conclusion for Patch Files doc**

* It **should override / refine** the “Patch-First Change Representation” sections in:

  * UNIVERSAL PHASE SPEC §2.3.2
  * PRO_Phase’s “Patch-First Editing is MANDATORY” paragraphs.
* Keep the **MUST have a patch artifact per workstream run**, but adopt this doc’s more nuanced stance on:

  * *When* patches are the primary handoff vs when they are “final audit + transport”.
* So: treat **Patch Files as Unified Diff & Optimal** as the **authoritative patch-policy sub-spec** the other docs point to.

---

## 3. Comprehensive Integration Spec – Enhanced Prompt Engineering

What it adds:

1. **Workstream_V1.1 template** (ASCII, section-based, tool-agnostic) with:

   * Header (IDs, apps, repo, entry files)
   * ROLE line, CLASSIFICATION (complexity/quality/domain)
   * OBJECTIVE, CONTEXT, CONSTRAINTS, TASK_BREAKDOWN
   * FILE_SCOPE, ACCEPTANCE_TESTS, CIRCUIT_BREAKER, metadata.

2. A concrete **SQLite state schema**: `runs`, `workstreams`, `events`, `step_attempts`, `errors`.

3. A staged **integration plan with quality gates and success metrics** for rolling out v1.1 prompts and patch capture:

   * Week-by-week phases and gates (e.g., patch capture must not add >5% overhead; oscillation detection must have no false positives, etc.).

How it compares:

* **UNIVERSAL PHASE SPEC** defines a **phase record** (phase_id, workstream_id, objective, phase_type, file_scope, acceptance, etc.) but doesn’t standardize the **runtime workstream prompt** that goes to Aider/Codex/etc.
* **PRO_Phase** defines mandatory structure for the spec documents, not the **per-run prompt wrapper**.
* **DEVELOPMENT RULES** define behaviors (operator mindset, anti-patterns), but not:

  * DB schema
  * Template versioning
  * Metrics / A/B analysis.

👉 **Conclusion for Comprehensive Integration Spec**

* For **prompt engineering / workstream prompt structure**:

  * This **is better** than anything in the existing three.
  * It should be referenced as the **canonical WORKSTREAM_V1.1 prompt format** when a phase executes through a tool.
* For **pipeline state & metrics**:

  * It extends UNIVERSAL PHASE’s “tests and acceptance” with *system-level* metrics (success rate, fix attempts, oscillation frequency, etc.).
  * I’d treat it as the **“Orchestrator State & Metrics” sub-spec**.

It doesn’t replace:

* The high-level **what is a phase + gates** in UNIVERSAL PHASE SPEC.
* The **behavioral rules / anti-patterns** in DEVELOPMENT RULES.

It **implements and tightens** them.

---

## 4. Practical “spec stack” after this comparison

If you want a clean mental model:

1. **Top layer – What & Behavior (unchanged core):**

   * **UNIVERSAL PHASE SPECIFICATION.txt** → Phase contract & lifecycle.
   * **DEVELOPMENT RULES DO and DONT.md** → Behavior / anti-pattern contract.

2. **Middle layer – Structure of specs:**

   * **PRO_Phase Specification mandatory structure.md**

     * Still defines *how to write* a phase spec.
     * Should **reference**:

       * WORKSTREAM_V1.1 for “how to wrap this into a tool prompt”.
       * Patch Files doc for detailed patch policy.

3. **Implementation sub-specs (these three become canonical here):**

   * **Background_task.md** → Canonical pattern for:

     * Encoding phase plans → workstreams → background workers → worktrees.
   * **Patch Files as Unified Diff & Optimal** → Canonical patch policy:

     * When to use patches, how orchestrators validate them, and when *not* to.
   * **Comprehensive Integration Spec – Enhanced Prompt Engineering** → Canonical:

     * Workstream prompt format (V1.1)
     * Orchestrator DB schema
     * Quality gates & rollout of template + patch capture.

So:

* **Whole documents?** The three new ones don’t replace your core trio.
* **Sections?** Yes:

  * Anywhere the old docs talk about **patch workflows**, **prompt structure**, or **parallel execution mechanics**, these three provide **strictly better / more complete solutions** and should be treated as the authoritative sub-specs those sections point to.
