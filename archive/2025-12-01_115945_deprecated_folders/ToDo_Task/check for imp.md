---
doc_id: DOC-GUIDE-CHECK-FOR-IMP-450
---

Think of it like running a kitchen:

* You have a bunch of dishes to cook (tasks),
* Some must be prepped before others (dependencies),
* Some can be cooked at the same time (parallelism),
* Some things just simmer in the back while you do other stuff (background tasks),
* And you track all that with a plan/diagram (graph + dependency tracking).

Now let’s map that to your world and your pipeline.

---

## 1. Parallelism

**Parallelism** = running multiple tasks at the same time on different workers (threads, processes, machines).

* If you have 8 cores, you could run:

  * `ruff`, `pylint`, `mypy`, `bandit`, `semgrep`, etc. all at once on different files or projects, as long as they don’t depend on each other.
* In your plugin system, the design explicitly calls out:

  * **“DAG-based ordering (resolve dependencies)”**
  * **“Parallel execution where possible”**

So: the **graph** tells you which plugins *can* run in parallel; the **scheduler** actually runs them in parallel.

---

## 2. Background tasks

**Background tasks** = work that runs “off to the side”, without blocking the main thing the user cares about.

Examples in your ecosystem:

* A CLI that kicks off the **error pipeline** for a set of files and continues to accept other commands while validation runs.
* A script like `scripts/run_error_engine.py` that can be invoked by other tools to scan files in the background and return a non-zero exit code only if errors are found.

In practice, background tasks are usually:

* Scheduled jobs (cron, timers),
* Worker processes/threads consuming a queue,
* Or “fire-and-forget” subprocesses started by the main orchestrator.

They **may** run in parallel with foreground work, but the key is **they don’t block the main interaction loop**.

---

## 3. Graphs (especially DAGs)

A **graph** is just:

* **Nodes** = tasks / steps / plugins / workstreams
* **Edges** = “must happen before” relationships

Most pipelines use a **DAG** (Directed Acyclic Graph):

* Directed: each edge has a direction (A → B means “A before B”).
* Acyclic: no cycles, so you can always find a valid order.

You already have DAGs in at least two places:

1. **Plugin system**

   * The spec explicitly says: **“DAG-based ordering (resolve dependencies)”**.
   * You encode dependencies like:

     ````text
     python_isort_fix → python_black_fix → [ruff, pylint, mypy, pyright, bandit, safety]
     ``` :contentReference[oaicite:3]{index=3}

     ````
   * And for JS/Markdown:

     ````text
     js_prettier_fix → js_eslint
     md_mdformat_fix → md_markdownlint
     ``` :contentReference[oaicite:4]{index=4}
     ````

   That’s literally a little dependency graph of plugins.

2. **Validation pipeline & error pipeline**

   * The state flow from `S_INIT` through `S0_*`, `S1_AIDER_*`, `S2_CODEX_*`, `S3_CLAUDE_*`, then `S_SUCCESS` or `S4_QUARANTINE` is a *state graph*: a node for each state, edges for allowed transitions.

   It’s mostly linear, but it’s still a graph that encodes **what can happen next**.

---

## 4. Dependency tracking

**Dependency tracking** = keeping a record of “X can’t run until Y is finished successfully.”

This is:

* Data: dependency lists, `requires` fields, `depends_on` lists, etc.
* Behavior: the scheduler uses that data to decide when a task is **blocked**, **ready**, or **runnable**.

You have this in multiple layers:

### 4.1 Workstreams / state machine

Your run/workstream state machine has states like:

* `pending → ready → running → succeeded`
* And `pending → blocked (dependency not met) → ready → running → …`

Key bits:

* `blocked` = dependencies not met.
* The scheduler promotes to `ready` when dependencies succeed.
* Only `ready` workstreams can move to `running`.

That **is** dependency tracking at the workstream level.

### 4.2 Plugins

In the plugin world:

* Each plugin has a `Requires` field (e.g. `python_black_fix` requires `python_isort_fix`; `js_eslint` requires `js_prettier_fix`)
* The plugin engine uses that to:

  * Build a DAG,
  * Compute a topological order,
  * Run things in a valid order, and in **parallel** where possible.

### 4.3 High-level pipeline

The overall pipeline spec says:

* **EDIT → STATIC → RUNTIME → (Error Pipeline / Quarantine)**
* STATIC (plugins) must succeed before RUNTIME (tests).
* RUNTIME must succeed before you mark the workstream **done** and archive the OpenSpec change.

That’s dependency tracking between **phases**, not just individual tools.

---

## 5. How they all fit together

Putting it in one mental model:

1. **Graph / DAG**

   * Data structure: tasks (nodes) + “must happen before” (edges).
   * Examples: plugin chains, workstream dependencies, pipeline phases.

2. **Dependency tracking**

   * The system stores “A requires B” and uses state (`blocked`, `ready`, `running`) to reflect that.
   * When all prerequisites are `succeeded`, a node becomes `ready`.

3. **Parallelism**

   * The scheduler looks at the graph and says:

     * “These N nodes are **ready** and have no remaining unmet deps → run them at the same time on different workers.”
   * For example:

     * For a Python file, you run `ruff`, `pylint`, `mypy`, `bandit`, `safety`, `codespell`, `semgrep`, `gitleaks` all in parallel **after** the `isort` + `black` fixes.

4. **Background tasks**

   * Many of these tasks can be launched as background jobs:

     * A “validation run” that scans the repo while you keep working.
     * A scheduled CI job that triggers your plugin test suite (`pytest`, Pester, etc.) using the tool profiles JSON.
   * They obey the same graph + dependency rules; they just run outside the foreground interaction.

---

## 6. Super simple summary

* **Graphs/DAGs**: the *map* of everything that must happen, and in what order.
* **Dependency tracking**: the *rules* and *state* that say what’s blocked vs ready.
* **Parallelism**: the *execution strategy* that runs multiple *ready* tasks simultaneously.
* **Background tasks**: *where* some of that work runs (off to the side) so it doesn’t block your main flow.

If you’d like, next step we can take one concrete slice of your system (like “run static checks + tests for a repo”) and draw the exact graph and show where you’d put parallel workers and background jobs.


---



You’re thinking about it in exactly the right way: “how many things can we safely do at once *at each level* of the system, without breaking determinism?”

Let me break it into two parts:

1. **What these concepts are & how they relate**
2. **Where the extra parallelism opportunities hide in your phase/workstream world**

---

## 1. Concepts & how they fit together

### Parallelism

* **What:** Running multiple tasks *at the same time* (multiple cores/agents/CLIs actually working simultaneously).
* **In your world:**

  * Multiple **workstreams** executing at once.
  * Multiple **phases** in different workstreams running concurrently, as long as their dependencies don’t clash.

### Background tasks

* **What:** Tasks that run “off to the side” and don’t block the main flow.
* **In your world:**

  * Linting, docs generation, test matrix, indexing, metadata extraction, repo scans.
  * Long-running checks that can be kicked off and monitored, but don’t need a human in the loop.

Think: *“Anything that doesn’t affect the current decision but improves safety/quality/state can be a background task.”*

### Graphs (usually DAGs)

* **What:** A graph of nodes (tasks) with edges (dependencies: “B depends on A”).
* In practice you almost always want a **DAG** (Directed Acyclic Graph) so you never get circular dependencies.
* **In your world:**

  * A **Phase Plan** is naturally a small DAG.
  * A **Project** is a bigger DAG composed of many phase DAGs.
  * A **Pipeline** is just a DAG + an execution engine.

### Dependency tracking

* **What:** The bookkeeping layer that says:

  * “Task X can’t start until A and B are done.”
  * “Task Y must not run at the same time as Z because they touch the same files.”
* **In your world:**

  * For each phase/workstream you already have: `depends_on`, `files_scope`, `constraints`, `acceptance`.
  * A dependency tracker uses that metadata to decide:

    * what can be run **now**,
    * what must **wait**,
    * what can be kicked to **background**.

**Relationship in one sentence:**

> You define tasks + dependencies → build a DAG → the scheduler uses that DAG to run as many tasks in parallel as possible, pushing non-blocking ones into background, while dependency tracking guarantees safety and determinism.

---

## 2. Where are the *other* parallelism opportunities?

You already spotted two levels:

1. **Project level:**

   * Different sections/modules of the project can be developed in parallel.
2. **Inside a section’s Phase Plan:**

   * Different steps/blocks of the phase (spec writing, test skeletons, scaffolding, etc.) can sometimes be done in parallel.

There are several **more layers** you can exploit.

### A. Parallelism across *concerns* for the same module

For a single module `M`, you can split workstreams by concern:

* **API / interface design**
* **Core implementation**
* **Tests and fixtures**
* **Docs / examples**
* **Infra / CI wiring (Dockerfile, workflows, Makefile, scripts)**

Some rules:

* As soon as **API contract** is at least draft-stable,

  * tests and docs can start in parallel.
* Infra/CI wiring can often start in parallel as soon as you know:

  * language/runtime,
  * entrypoints,
  * repo structure.

So for a single module, instead of:

> PH-01 spec → PH-02 impl → PH-03 tests → PH-04 docs → PH-05 CI

You can do:

* **PH-SPEC-01:** Draft API + acceptance criteria
* Then in parallel:

  * **WS-IMPL:** core code
  * **WS-TEST:** test scaffolding + sample cases
  * **WS-DOC:** user docs / readme / usage examples
  * **WS-CI:** pipeline config & hooks

All gated by:

* “spec is in `DRAFT-STABLE` state” and
* “files_scope” conflict rules (e.g., tests and docs don’t edit the same files as core implementation).

---

### B. Parallelism inside a *single phase*

Even one phase can often be split into **micro-tasks** that don’t conflict:

Example: Phase “Implement new endpoint”

* Subtasks that can be parallel:

  * “Generate types / DTOs”
  * “Write handler skeleton”
  * “Write initial unit test cases”
  * “Update OpenAPI spec”
* Dependencies:

  * All require a stable **endpoint contract** (name, URL, request, response).
  * Tests don’t need final implementation; they just need the contract.

So your phase spec could explicitly list:

```yaml
subtasks:
  - id: ST-API-CONTRACT
    kind: design
    outputs: [api_contract.yml]
  - id: ST-HANDLER-SKELETON
    depends_on: [ST-API-CONTRACT]
  - id: ST-TYPES
    depends_on: [ST-API-CONTRACT]
  - id: ST-TEST-SKELETON
    depends_on: [ST-API-CONTRACT]
  - id: ST-DOC-UPDATE
    depends_on: [ST-API-CONTRACT]
```

Then a scheduler can run all post-contract subtasks in parallel.

---

### C. Cross-cutting background work

You can define **recurring background workstreams** that run whenever the graph sees “dirty state”:

* **BG-LINT:** run linters/formatters on changed files.
* **BG-METRICS:** gather complexity metrics, coverage, TODO counts, etc.
* **BG-DOC-INDEX:** rebuild search index / summary docs after doc changes.
* **BG-REF-AUDIT:** scan for unused files, dead code, outdated docs.

Rules:

* They depend on “some code changed”, not on specific phases.
* They write only to:

  * logs,
  * a `.ledger/` directory,
  * or a `build/` directory — not core source files.
    That keeps them **safe** to run in parallel.

---

### D. Parallelism across *pipelines* (multi-agent, multi-tool)

Given your environment (Claude Code, Codex CLI, Aider, Copilot, etc.), you can:

* Run different **tools** on different **worktrees / sandboxes** in parallel:

  * Aider handling refactor on worktree A.
  * Codex running test-fix loop on worktree B.
  * Claude doing spec/docs in a docs-only sandbox.
* As long as:

  * Each tool has a **non-overlapping files_scope** (or its own clone/worktree).
  * All changes get merged back through a **single, serialized “patch intake” phase** (your error-pipeline / patch-management spec world).

So your framework can say:

* “Parallelism between tools is allowed, but **all writes to the mainline branch must pass through a deterministic Patch Intake Phase**.”

---

### E. CI / validation as a graph

The CI/test side is another layer:

* For a given commit or patch bundle, you can run in parallel:

  * `lint`
  * `unit_tests`
  * `integration_tests`
  * `schema_checks`
  * `security_scan`
* Dependency graph:

  * `deploy` depends on **all** of the above passing.
  * Some expensive tests (e2e) might depend on unit/integration passing first.

You don’t need to invent this from scratch; your PHASE/WORKSTREAM spec can simply say:

```yaml
phase_id: PH-CI-CORE
tasks:
  - id: T-LINT
  - id: T-UNIT
  - id: T-INTEGRATION
  - id: T-SECURITY
  - id: T-DEPLOY
    depends_on: [T-LINT, T-UNIT, T-INTEGRATION, T-SECURITY]
```

---

## 3. How to keep it deterministic while doing “as much as possible”

The core guardrails for your framework:

1. **Everything is a node in a DAG**

   * Project → phases → workstreams → tasks/subtasks.
   * Each one has:

     * `depends_on`
     * `files_scope` (read/write)
     * `acceptance` (how we know it’s done)
     * `id` (ULID / IDX)

2. **Scheduler rule:**

   * “At any moment, run all **ready** nodes where:

     * all dependencies are complete,
     * and their `files_scope.write` sets don’t overlap.”

3. **Background tasks tag**

   * Nodes with `priority: background`:

     * can run whenever resources are free,
     * must not write to the same files as any active foreground node,
     * usually write to `.ledger/`, `build/`, or logs only.

4. **Patch-based writes**

   * Tools and agents don’t free-write into mainline:

     * They produce **patches or PRs**.
     * A dedicated **Patch Intake Phase**:

       * checks those patches,
       * runs validations,
       * then applies them in a **single, serialized path**.

5. **State machine per node**

   * Each node has states like:

     * `PENDING`, `READY`, `RUNNING`, `SUCCEEDED`, `FAILED`, `CANCELLED`.
   * Deterministic rules for transitions:

     * E.g., “only move to READY when all dependencies are SUCCEEDED.”

If you wire that into your phase/workstream spec system, you get exactly what you described:

> “Do as much as we can safely at once, but always in a way we can replay, audit, and get the same result again.”

---

If you want, next step I can sketch:

* a **tiny YAML schema** for “task nodes” (phase/workstream/subtask),
* and a **scheduling rule set** written in plain English that your agents must follow when deciding what to run in parallel.


---


Nice, this is the fun part of your system: pretend we’ve got an infinite-core monster box and ask, “How do we turn **more CLI windows** into **more finished work**, without losing determinism?”

The trick is to stop thinking “more windows = more chaos” and instead treat each CLI instance as:

> **A worker in a controlled factory** with a clear *job*, *scope*, and *sandbox*.

---

## 1. Mental model: each CLI instance = 1 worker in a job queue

Right now you’re doing:

* Open 2–3 Kodex / Claude Code windows
* Manually decide: “this one works on X, that one on Y”

Let’s formalize that:

* Each **window/instance** gets:

  * a **role** (what kind of tasks it takes),
  * a **files_scope** (what it’s allowed to touch),
  * a **task queue** (phase/workstream tasks assigned to it),
  * optional **background jobs** it’s allowed to run.

Then your **Phase Plans + Workstreams** become a **job queue**, and the CLI instances are just workers pulling from that queue.

With infinite hardware, your speed is limited by:

* how well you split work into independent tasks, and
* how well you avoid conflicting edits / duplicated effort.

That’s where more instances can shine *if* you add structure.

---

## 2. Ways more instances can actually make you faster

### Pattern 1 – Parallel features / modules (multi-sandbox)

Use **one sandbox per feature**, and bind each CLI instance to a sandbox:

* `sandbox-A` → feature A (new module)
* `sandbox-B` → feature B (refactor)
* `sandbox-C` → infra/CI changes

Each sandbox is:

* a **separate branch** or **git worktree** of the same repo,
* or even a separate clone.

Then:

* Instance 1 (Claude Code) → owns `sandbox-A`
* Instance 2 (Codex) → owns `sandbox-B`
* Instance 3 (Claude Code or Aider) → owns `sandbox-C`

All three run **at the same time** because they never touch the same working tree.

**Win:**
You get true parallelism on different parts of the project, with **zero conflict risk** until you merge via your patch/PR intake process.

---

### Pattern 2 – Parallel concerns on *one* feature

For a single feature, split work by concern, not just by file:

* **Spec + design**
* **Implementation**
* **Tests**
* **Docs & examples**

Then map them to instances:

* **Instance A – “Spec & Docs” worker**

  * Writes/updates: spec docs, diagrams, README, comments.
* **Instance B – “Implementation” worker**

  * Focuses on the core code changes.
* **Instance C – “Testing & Validation” worker**

  * Writes tests, runs test suites, tunes test data.

All three can work **from the same Phase Plan**, just with different `files_scope`:

* A: `/docs`, `/specs`, comments only
* B: `/src`
* C: `/tests`, `/ci`, `/scripts`

**Win:**
You’re moving spec, code, tests, and docs forward together, instead of waiting for one to fully finish before starting the others.

---

### Pattern 3 – Dedicated background workers

Spin up one or more **permanent “background” CLI instances** whose *only* job is to run queued background tasks:

Examples:

* **BG-VALIDATION worker**

  * Watches for “task done” events.
  * Runs linters, static analysis, quick tests on changed files.
* **BG-REVIEW worker**

  * Takes patch bundles, runs extra quality checks, suggests improvements.
* **BG-DOC-INDEX worker**

  * Regenerates documentation indexes or summaries after changes.

Your foreground coding instances don’t waste cycles on this; they just **enqueue jobs**:

```text
Instance B (impl) finishes task → enqueue:
  - BG-VALIDATION(task_id, files_changed)
  - BG-DOC-INDEX(if docs touched)
```

**Win:**
You keep the coding windows focused on “move the design/code forward” while background instances quietly enforce quality and maintain meta-structure.

---

### Pattern 4 – Sweeper / refactor bots

Have one or more instances whose role is **“sweeper/refactor”**:

* They never start new features.
* They only:

  * apply systematic refactors,
  * improve naming,
  * simplify code,
  * update style to match standards.

Process:

1. Foreground instances produce the initial implementation.
2. When a module stabilizes, you enqueue a **“SWEEP”** workstream:

   * `WS-SWEEP-001: refactor module X for readability and consistency`
3. Sweeper instance grabs that job, works in its own branch/worktree, and emits a patch.

Because it works in its own sandbox, it can run in parallel without stepping on active feature work.

**Win:**
You keep forward momentum and still get the “second pass of polish” without pausing main development.

---

### Pattern 5 – Experiment sandboxes / spike workers

Use dedicated instances for **“spikes”** / experiments:

* “Try approach A vs B for this algorithm”
* “Generate 3 alternative designs for this API”
* “Explore performance optimizations”

Each experiment:

* runs in a short-lived branch or temp worktree,
* never writes directly to the main branch,
* emits a **comparison report** + patches.

You can run several of these at once:

* Instance E1: spike on library choice
* Instance E2: spike on schema design
* Instance E3: spike on deployment strategy

**Win:**
You explore multiple options in parallel, then pick the best path *without* contaminating the mainline until you decide.

---

## 3. Guardrails so “more instances” doesn’t mean “more chaos”

To keep it deterministic and safe:

### 3.1 Separate sandboxes / branches

* **Rule:** An instance either:

  * has its own branch/worktree, **or**
  * shares a branch but has a strict `files_scope` that doesn’t overlap with other active instances.

Default safest pattern:

> “If two instances may edit the same logical area, give them different worktrees.”

### 3.2 Task contracts instead of “vibes”

Every task in your Phase/Workstream Plan should have:

* `id`
* `files_scope`
* `depends_on`
* `tool_preference` (e.g., “prefer Codex”, “prefer Claude Code”)
* `priority` (foreground vs background)

Then your job as operator is just:

* Start N instances.
* Assign each a **role** + **queue filter** (“I take all `tool_preference: codex` tasks with `priority: foreground` on modules A/B”).

### 3.3 Patch/PR intake as **single merge gate**

No matter how many instances you have:

* **Only one deterministic intake phase** is allowed to merge into:

  * main branch or
  * canonical repo.

That intake phase:

1. Collects patches from each instance.
2. Validates them (tests, lint, constraints).
3. Applies them in a controlled order.
4. Logs everything to a ledger.

So parallelism happens **before** merge; merging stays **serial and governed**.

---

## 4. Net effect: how this makes you faster

Assuming infinite hardware, this architecture gives you:

* **Horizontal scaling of AI work**

  * Add more windows/instances = add more workers.
* **Multi-level parallelism**

  * Across features
  * Across concerns (spec/impl/tests/docs)
  * Across experiments
  * Across background tasks
* **Deterministic control**

  * Because every instance is bound to:

    * a sandbox/branch,
    * a role,
    * a queue of well-specified tasks,
    * and merges go through one intake gate.

If you want, next step I can sketch a **“SESSION_SPEC”** format like:

```yaml
session_id: S-CODEX-01
tool: codex
role: implementation
sandbox: worktrees/feature-A
task_filters:
  priority: [foreground]
  kinds: [impl, small-refactor]
  modules: [file_alchemist.core, file_alchemist.adapters]
background_allowed:
  - run_local_tests
  - quick_lint
forbidden:
  - edit_docs
  - edit_ci
```

…so that every new CLI window you open has a **machine-readable contract** for what it’s allowed to do.


---

Exactly—what you’re describing is a **parallelism-aware phase plan**: the plan itself *knows* where concurrency is safe, and your orchestrator just follows it.

Let me show you how to bake that into the spec *before* any code is written.

---

## 1. What the “complete phase plan” needs to contain

For each project/section, your **Phase Plan** should define *at planning time*:

For each phase / workstream / task node:

* `id` – stable ID
* `kind` – design / impl / test / docs / infra / refactor / spike / bg
* `depends_on: [...]` – other nodes
* `files_scope`:

  * `reads: [...]`
  * `writes: [...]`
* `concurrency_hint`:

  * `parallel_ok: true|false`
  * `conflict_group: <string>` (all nodes in same group cannot run together)
* `tool_preference` – which CLI tools are best
* `priority` – foreground vs background

That’s the **minimum** for a deterministic parallel scheduler.

Your “guardrail files” are basically schemas + validators that enforce:

* every node has these fields,
* no missing dependencies,
* no obviously overlapping `files_scope.writes` for nodes marked parallel.

---

## 2. Pre-computing where parallelism is possible

Because the whole plan exists up front, you can compute a **parallelism profile** of the project before coding:

### 2.1 Build the DAG

* Nodes = all phase/workstream tasks.
* Edges = `depends_on`.

Then:

* Topologically sort the DAG.
* For each “layer” of the sort, find nodes whose:

  * dependencies are already satisfied **and**
  * `parallel_ok == true`.

That gives you:

> At “time slice” k, we have N nodes that *could* be run in parallel, subject to file scopes.

### 2.2 Filter by file_scope

From that set:

* Only run nodes in parallel whose `files_scope.writes` don’t overlap **and** don’t conflict via `conflict_group`.

What’s left is your **effective parallel set** for that slice.

From this you can compute:

* `max_parallelism_per_slice` – how many tasks are safely parallel at each point.
* `parallel_windows` – contiguous ranges of the plan where there’s “lots of parallel work” vs “serial bottlenecks”.

---

## 3. Using this to *trigger* new CLI instances

Once you have the above, your orchestrator can have simple rules like:

> **Rule A** – Spawn worker instances based on “ready, parallelizable work”
>
> * Let `R` = number of READY nodes (all deps satisfied, parallel_ok, non-conflicting file scopes).
> * Let `W` = current number of running CLI instances.
> * If `R > α·W` (e.g., 2× or 3×), and below some hard max, spawn another instance.

> **Rule B** – Retire workers when parallelism drops
>
> * If `R` stays below some threshold for N cycles, you let some instances finish their current task and then idle/close.

> **Rule C** – Assign tasks to instances by role
>
> * Implementation worker gets impl/refactor nodes.
> * Test worker gets test/validation nodes.
> * Docs/spec worker gets docs/spec nodes.
> * Background worker gets kind=bg nodes.

Because the plan includes `kind`, `files_scope`, and `tool_preference`, assigning tasks to the right CLI and sandbox is deterministic.

---

## 4. Helper functions you’ll want (conceptually)

These can be just scripts (Python/PowerShell) that work *only off the phase plan JSON/YAML*:

1. **`parse_phase_plan()`**

   * Load the plan.
   * Validate against schema.
   * Build DAG structure in memory.

2. **`compute_ready_nodes(current_state)`**

   * Inputs:

     * node states (PENDING / READY / RUNNING / DONE / FAILED)
   * Output:

     * list of nodes that:

       * all deps are DONE,
       * not yet RUNNING or DONE,
       * `parallel_ok == true`,
       * no scope conflicts with currently RUNNING.

3. **`estimate_parallelism_profile()`**

   * Run a simulation from scratch:

     * assume each node takes one “tick”.
     * at each tick, run `compute_ready_nodes()` and record `len(ready_nodes)`.
   * Output:

     * profile over time: at which ticks parallelism spikes or dips.

4. **`suggest_instance_count()`**

   * Based on the profile, compute:

     * recommended number of CLI workers overall
     * when to consider spinning more up.

You don’t have to make this perfect at first – even a simple “count ready nodes” per slice is enough to get useful signals.

---

## 5. Making “parallel opportunities” explicit in the plan

You can even make this visible in the plan itself with a couple of fields:

```yaml
phase_id: PH-FEATURE-X
parallel_profile:
  expected_max_parallelism: 5
  recommended_workers:
    min: 2
    max: 4
tasks:
  - id: T-SPEC-API
    kind: design
    parallel_ok: false        # must be done alone
  - id: T-IMPL-CORE
    depends_on: [T-SPEC-API]
    parallel_ok: true
    conflict_group: impl-core
  - id: T-TESTS
    depends_on: [T-SPEC-API]
    parallel_ok: true
    conflict_group: tests
  - id: T-DOCS
    depends_on: [T-SPEC-API]
    parallel_ok: true
    conflict_group: docs
  - id: T-CI
    depends_on: [T-SPEC-API]
    parallel_ok: true
    conflict_group: ci
```

From this, your orchestrator can see:

* After `T-SPEC-API`, there are **four** tasks that can run in parallel with disjoint conflict groups → *great time to spin up extra instances.*

Later, when you hit a phase that is inherently sequential (e.g., complex integration tests / deployment), the ready set shrinks → orchestrator naturally stops scaling out.

---

## 6. Big picture: what you just designed

You’re essentially saying:

* **We never “discover” parallelism at runtime by accident.**
* We **declare** it in the phase plan and guardrail docs.
* We compute a **parallelism map** of the project before coding.
* A small orchestration layer watches:

  * node states,
  * DAG structure,
  * file scopes,
  * and uses that to decide:

    * when to open more CLAUDE/CODEX instances,
    * which tasks to feed them,
    * when to let instances wind down.

That gives you exactly what you want:

> “Do as much as we can at once, but in a deterministic, repeatable, auditable way.”

If you’d like, next I can draft a **mini PHASE_PLAN schema** (in YAML) that includes these parallelism fields, ready to drop into your existing framework.


---


These are *exactly* the right instincts. Let’s treat what you wrote as requirements and wire them into the framework, instead of leaving them as vibes.

I’ll break it into four pieces:

1. Using the **parallelism chart** to control tools, background tests, and MCP servers
2. A **“development blackout”** mode for Windows + circuit breakers
3. A **kernel-level error + self-healing pipeline** for dev hiccups
4. How to **encode all of this in the phase plan** so it stays deterministic

---

## 1. Parallelism chart as the “master dial” for tools, background tests, MCP servers

You already have:

* A **parallelism profile** per project/section:
  “At this slice of the plan, N tasks are safely parallel; at this other slice, only 1–2.”

Your new idea:

> Use that same profile to decide:
>
> * how many CLI tools to spin up,
> * how many background tests to run,
> * how many MCP servers to keep online.

Perfect. That’s just a policy layer on top of the DAG.

### 1.1. Conceptual loop

At runtime, for the current project/phase:

1. Compute `R_active` = number of **READY, parallel-safe tasks**.
2. Compute `I_active` = number of **running CLI instances** bound to this project.
3. Compute `M_active` = number of **MCP services** actually needed by those tasks.

Then:

* If `R_active` is high → **scale out**:

  * Start more CLI instances (Claude Code / Codex / Aider), each with its own scope.
  * Enable extra MCP services that those tasks require.
  * Allow more background test jobs (up to limits).

* If `R_active` drops → **scale in**:

  * Let some CLI instances finish their current task and then idle/shutdown.
  * Stop MCP services not used by any READY/RUNNING task.
  * Throttle or pause background test jobs.

So the **parallelism chart** isn’t just “how many tasks”; it becomes a **target concurrency level** that everything else obeys.

### 1.2. Phase plan knobs

For each phase or workstream, add fields like:

```yaml
parallelism_policy:
  max_cli_workers: 4
  max_bg_jobs: 3
  mcp_profiles:
    required:
      - fs
      - github
    optional:
      - jira
  mcp_auto_shutdown: true   # allowed to turn off when no tasks need them
```

Now your orchestrator can say:

* “For this slice, parallelism chart says 5 tasks are safely parallel → spin up to `max_cli_workers` and `max_bg_jobs` but no further.”
* “No active tasks require `jira` MCP → shut it down.”

---

## 2. “Development blackout” mode + circuit breakers

You’re also right that **the rest of Windows** matters: browsers, games, OneDrive sync, antivirus scans, etc.

You’re basically describing:

> A **Focus Mode / Dev Blackout** that reconfigures the OS around the pipeline, plus **circuit breakers** that keep you from overloading the box.

### 2.1. Dev blackout modes

Think in terms of **operating modes**:

* `OS_MODE_NORMAL` – everything allowed.
* `OS_MODE_FOCUS_DEV` – heavy non-essential stuff paused, lighter background load.
* `OS_MODE_CRITICAL_PIPELINE` – only essential services + pipeline.

On Windows, this could be implemented (later) via PowerShell scripts, Task Scheduler, and a list of “apps/services to suspend/stop” – but for now, conceptually:

Each phase/workstream in your plan can declare:

```yaml
os_profile:
  mode: FOCUS_DEV | CRITICAL_PIPELINE | NORMAL
  blackout_reason: "Long-running integration tests"
  forbidden_apps:
    - "steam.exe"
    - "gamebar.exe"
    - "dropbox.exe"
  allowed_background_services:
    - "defender"
    - "necessary vpn"
```

Then your orchestrator:

* Sees a phase that declares `CRITICAL_PIPELINE` →
  triggers your OS script that:

  * closes certain apps,
  * stops specific services,
  * maybe sets a high-performance power plan, etc.

When the phase finishes, you restore the previous mode.

### 2.2. Circuit breakers on system usage

Now add **live telemetry** from the OS:

* `CPU_usage`, `RAM_usage`, `Disk_IO`, maybe `GPU_usage`.

Circuit-breaker rules (configurable, per project):

```yaml
resource_limits:
  cpu_percent_soft: 70
  cpu_percent_hard: 85
  ram_percent_soft: 70
  ram_percent_hard: 90
  io_wait_soft_ms: 200
  actions:
    on_soft_limit:
      - "stop_spinning_up_more_cli_workers"
      - "throttle_bg_jobs"
    on_hard_limit:
      - "pause_new_tasks"
      - "gracefully shutdown lowest_priority_instances"
```

So at runtime:

* If below soft limits → normal behavior.
* Above soft, below hard → **stop scaling out**; let the system catch up.
* Above hard → **fail fast but safe**:

  * Don’t crash the machine; instead:

    * stop starting new tasks,
    * optionally cancel low-priority background jobs,
    * log a “RESOURCE_LIMIT_EXCEEDED” event into your ledger.

This is exactly the **circuit breaker** pattern but applied to system resources.

---

## 3. “Kernel-level” error detection + self-healing pipeline

You also said:

> “Additionally, when something breaks, we need to have an extremely sophisticated system of identifying it as far as the system kernel is concerned.”

In your architecture, “kernel” really means the **core orchestrator layer** – the thing that knows about:

* phase plans,
* workstreams,
* tools,
* MCP servers,
* OS modes,
* resource limits.

So we want a **deterministic error pipeline** for *execution hiccups*, similar to your file error module.

### 3.1. Error classes for execution

Define a small, fixed set of **execution error types**:

* `E_TOOL_FAILURE` – CLI tool crashed, bad exit code, or hung.
* `E_MCP_FAILURE` – MCP server unresponsive or returning structured errors.
* `E_RESOURCE_LIMIT` – circuit breaker tripped (CPU/RAM/etc).
* `E_OS_MODE_FAILURE` – couldn’t enter requested blackout mode (permissions, etc).
* `E_PLAN_CONSISTENCY` – plan says a node is READY but deps/states are inconsistent.
* `E_UNKNOWN` – everything else.

Each time something breaks, the orchestrator turns that into:

```yaml
error_event:
  id: ERR-ULID
  type: E_TOOL_FAILURE
  phase_id: PH-FOO-01
  task_id: T-IMPL-123
  tool: "codex"
  description: "codex timed out after 300s running tests"
  context:
    exit_code: 124
    last_stdout: "... truncated ..."
    last_stderr: "... truncated ..."
  timestamp: ...
```

### 3.2. Deterministic self-healing path (ERR-EXEC pipeline)

Then you define a **mini state machine** for these errors, e.g.:

1. `ERR-EXEC-01: Auto Retry`

   * Try rerunning with:

     * same tool + slightly adjusted timeout, **or**
     * a different tool (e.g., Claude instead of Codex).
2. `ERR-EXEC-02: Context Repair`

   * Re-read phase plan, regenerate the prompt for that task,
   * check file state (no partial writes / revert if needed),
   * try again.
3. `ERR-EXEC-03: Agent Review`

   * A more powerful agent (or different model) analyzes:

     * the error_event,
     * the task spec,
     * recent logs.
   * It may:

     * re-plan the task,
     * split it into smaller pieces,
     * adjust constraints.
4. `ERR-EXEC-04: Human Escalation`

   * If after N cycles of self-healing it still fails,
   * create a **HUMAN_REVIEW** work item with:

     * all attempts,
     * logs,
     * recommended next steps,
     * minimal surface area for the human to inspect.
5. Terminal states:

   * `RESOLVED_AUTO` – self-healed.
   * `RESOLVED_HUMAN` – human fixed and it passed.
   * `QUARANTINED` – permanently parked and excluded from future runs until explicitly revived.

This is the **same shape** as your file error module, but at the **execution/orchestration** level.

### 3.3. Goal: avoid human intervention unless absolutely necessary

Your priority order is:

1. **Self-heal with context + tools adjustments**
2. **Escalate to a stronger/more expensive agent**
3. **Only then bother the human**

So for each `error_event`, you attach a **policy**:

```yaml
self_heal_policy:
  max_attempts: 3
  retry_strategies:
    - "rerun_same_tool"
    - "switch_to_claude"
    - "split_task_into_subtasks"
  escalation:
    on_fail: HUMAN_REVIEW
```

The kernel/orchestrator just follows the script.

---

## 4. How to encode all of this in the phase plan (so it stays deterministic)

To tie it all together, each **phase/workstream/task** in your spec can have four new sections:

```yaml
phase_id: PH-SECTION-01
# 1) how many workers / MCP / bg jobs
parallelism_policy:
  max_cli_workers: 3
  max_bg_jobs: 2
  mcp_profiles:
    required: [fs, github]
    optional: [jira]
  mcp_auto_shutdown: true

# 2) OS blackout / resource guards
os_profile:
  mode: FOCUS_DEV
  blackout_reason: "Running heavy linters and tests"
  forbidden_apps: ["steam.exe", "onedrive.exe"]
resource_limits:
  cpu_percent_soft: 70
  cpu_percent_hard: 85
  ram_percent_soft: 70
  ram_percent_hard: 90

# 3) Error handling policy
error_policy:
  pipeline_id: ERR-EXEC-V1
  self_heal_policy:
    max_attempts: 3
    retry_strategies:
      - rerun_same_tool
      - switch_tool_to: "claude"
      - split_task
    escalation: HUMAN_REVIEW

# 4) Task graph still has its usual deps / files_scope / etc.
tasks:
  - id: T-IMPL-API
    depends_on: [T-SPEC-API]
    files_scope:
      writes: ["src/api/*.py"]
    parallel_ok: true
  - id: T-TEST-API
    depends_on: [T-SPEC-API]
    files_scope:
      writes: ["tests/api/*.py"]
    parallel_ok: true
```

Then your **kernel/orchestrator** doesn’t improvise:

* It reads the plan,
* Computes parallelism windows,
* Starts/stops CLI tools + MCP servers according to the policy,
* Adjusts OS mode when needed,
* Watches resource limits and trips circuit breakers deterministically,
* And uses a defined ERR-EXEC pipeline to self-heal execution hiccups.

---

If you want, next step we can:

* draft one **“EXECUTION_KERNEL_SPEC.md”** or YAML schema that defines these fields globally,
* then do a **concrete example** for one small feature (PH + WS + error path + OS blackout + parallelism policy) so you can drop it straight into your docs.
