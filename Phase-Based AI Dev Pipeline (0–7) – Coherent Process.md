Here’s one coherent process that pulls your “random thoughts” + all the current diagrams + the Phase 0–7 pipeline into a single map you (and your CLIs) can actually use.

---

# Phase-Based AI Dev Pipeline (0–7) – Coherent Process

## Table of Contents

1. **High-Level Overview**
   1.1. Goals
   1.2. The 8 Logical Phases (0–7)
   1.3. Core System Components
2. **Master Pipeline Diagram (0–7)**
3. **Phase 0 – Bootstrap & Initialization**
4. **Phase 1 – Planning & Spec Alignment**
5. **Phase 2 – Request Building & Run Creation**
6. **Phase 3 – Scheduling & Task Graph**
7. **Phase 4 – Tool Routing & Adapter Selection**
8. **Phase 5 – Execution & Validation**
9. **Phase 6 – Error Analysis, Auto-Fix & Escalation**
10. **Phase 7 – Monitoring, Completion & Archival**
11. **Cross-Cutting Layer A – Patterns, IDs & Templates**
12. **Cross-Cutting Layer B – Files, Tasks, UI & State**
13. **Diagram Index (Where Each Existing Diagram Fits)**
14. **How You Actually Use This in Practice**

---

## 1. High-Level Overview

### 1.1 Goals

All your “random thoughts” basically converge on this:

* **Pattern-first pipeline**: patterns = *contracts* (“shape + rules”), not copy-paste files.
* **Phase-based execution**: every run is a journey through Phases 0–7.
* **Spec-driven**: OpenSpec + CCPM + phase plans drive workstreams.
* **Tool-agnostic**: Aider / Codex / custom tools are just adapters selected by profiles.
* **Self-healing**: error engine + plugins + circuit breaker + retries, not blind reruns.
* **Full observability**: SQLite state + UI/TUI/CLI dashboard for runs, workstreams, files, tools.

### 1.2 The 8 Logical Phases (0–7)

You effectively have 8 logical phases (Phase “8” in the E2E diagram is now folded into 7 for simplicity):

0. **Bootstrap & Initialization** – detect repo, pick profile, validate baseline, generate project profile/router config.
1. **Planning & Spec Alignment** – take OpenSpec + PM epics + plan docs → workstreams + phase plans.
2. **Request Building & Run Creation** – turn “run this plan” into a concrete run record + normalized execution request in DB.
3. **Scheduling & Task Graph** – build DAG, resolve dependencies, prepare task queue.
4. **Tool Routing & Adapter Selection** – match each step to a tool profile + adapter, using the tool registry.
5. **Execution & Validation** – run tools, capture output, run acceptance tests, update state.
6. **Error Analysis, Auto-Fix & Escalation** – error engine + plugins + auto-fix + circuit breakers + escalation paths.
7. **Monitoring, Completion & Archival** – live monitoring, dashboards, run completion, artifact archival, reporting.

### 1.3 Core System Components (Mapped to Phases)

From the System Architecture + Architecture Overview:

* **User Layer** (CLI / GUI / API) → used mainly in Phases 0–2 & 7
* **Core Engine** (Orchestrator, Scheduler, Executor, State Manager) → Phases 2–7
* **State & Persistence** (SQLite, Checkpoints, Worktrees) → underpin all phases
* **Error Detection & Recovery** (Error Engine, Plugins, Circuit Breaker, Retry Manager) → Phase 6 + hooks in 5/7
* **Specification Management** (OpenSpec Parser, Spec Index, Spec Resolver, Change Proposals) → Phase 1
* **Tool Adapters** (Aider, Codex, Custom, Manual) → Phase 4–5
* **External Services** (Git, Aider CLI, OpenAI, CCPM) → touched across phases, especially 1, 4, 5, 7

---

## 2. Master Pipeline Diagram (0–7)

```mermaid
graph TB
    subgraph "PHASE 0: Bootstrap & Init"
        P0_1[Detect Repo / Profile]
        P0_2[Validate Baseline Schema]
        P0_3[Generate PROJECT_PROFILE.yaml<br/>router_config.json]
        P0_1 --> P0_2 --> P0_3
    end

    subgraph "PHASE 1: Planning & Spec Alignment"
        P1_1[Load OpenSpec / Plans / PM Epics]
        P1_2[Validate Specs + Index]
        P1_3[Convert Specs → Workstreams]
        P1_4[Attach Patterns & Templates]
        P1_1 --> P1_2 --> P1_3 --> P1_4
    end

    subgraph "PHASE 2: Request Building & Run Creation"
        P2_1[User / CLI Requests Run]
        P2_2[Build Execution Request]
        P2_3[Validate Request Schema]
        P2_4[Create Run + Workstreams in DB]
        P2_1 --> P2_2 --> P2_3 --> P2_4
    end

    subgraph "PHASE 3: Scheduling"
        P3_1[Load Workstreams & Tasks]
        P3_2[Build DAG / Resolve Deps]
        P3_3[Fill Task Queue]
        P3_1 --> P3_2 --> P3_3
    end

    subgraph "PHASE 4: Tool Routing"
        P4_1[Match Task → Tool Profiles]
        P4_2[Select Adapter (Aider/Codex/Custom)]
        P4_3[Validate Tool Config]
        P4_1 --> P4_2 --> P4_3
    end

    subgraph "PHASE 5: Execution & Validation"
        P5_1[Invoke Adapter / Run Tool]
        P5_2[Capture Output + Files]
        P5_3[Run Acceptance Tests]
        P5_4[Update Task State in DB]
        P5_1 --> P5_2 --> P5_3 --> P5_4
    end

    subgraph "PHASE 6: Error Analysis & Recovery"
        P6_1[Detect Errors via Plugins]
        P6_2[Classify (Transient / Permanent)]
        P6_3[Auto-fix Attempts + Re-validate]
        P6_4[Circuit Breaker / Escalation]
        P6_1 --> P6_2 --> P6_3 --> P6_4
    end

    subgraph "PHASE 7: Monitoring & Completion"
        P7_1[Monitor Runs & Workstreams]
        P7_2[Summarize Results / Reports]
        P7_3[Archive Artifacts & State]
        P7_1 --> P7_2 --> P7_3
    end

    P0_3 --> P1_1
    P1_4 --> P2_1
    P2_4 --> P3_1
    P3_3 --> P4_1
    P4_3 --> P5_1
    P5_4 --> P6_1
    P5_4 --> P7_1
    P6_4 --> P7_1
```

This Mermaid diagram is the “single picture” that all your other diagrams zoom into from different angles.

---

## 3. Phase 0 – Bootstrap & Initialization

**What happens**

* Detect repo + environment.
* Pick correct **project profile** (patterns, tools, configs).
* Validate repo against schemas (IDs, patterns, layout, etc.).
* Generate initial **PROJECT_PROFILE.yaml** and **router_config.json** used later in routing.

**Main components**

* `core/bootstrap/orchestrator.py`, `discovery.py`, `selector.py`, `generator.py`
* `schema/` – validation for profiles, project config, routing. 

**Random-thought consolidation**

* All your “pattern vs unique file” thinking lives here as **profile + pattern selection**, not one-off hacks:

  * Repo-level patterns (layout, IDs, modules).
  * Language-level patterns (Python/PS/MQL4 shape).
  * Error-pipeline patterns (where ERR modules live).
* Phase 0 is where you decide which **pattern suite** + **execution rules** this repo uses.

---

## 4. Phase 1 – Planning & Spec Alignment

**What happens**

* Ingest **OpenSpec**, PM epics, phase docs, and workstream authoring guides.
* Validate specs & build **spec index** + dependency graph. 
* Convert accepted specs into **workstream JSON** (tasks + dependencies + metadata).
* Link specs and workstreams back to CCPM/PM issues.

**Main components**

* `core/openspec_parser.py`, `openspec_convert.py`, `spec_index.py` 
* `spec/` + `specifications/` content
* `specs_index.json`, `specs_mapping.json`, workstreams in `workstreams/`

**Random-thought consolidation**

* Your idea “plans must be machine-readable, phases must be explicit” becomes:

  * OpenSpec files + Phase Plans → **single source of truth**.
  * Each spec is **patternized**:

    * spec pattern (base/common/feature)
    * dependency DAG
    * workstream template + tasks.

---

## 5. Phase 2 – Request Building & Run Creation

**What happens**

* User/CLI selects a plan/workstream bundle and says “run this”.
* Pipeline builds a **normalized execution request** (what, where, tools, patterns, IDs).
* Validates against `request.schema.json`.
* Creates a **run** record and initial **workstream** rows in SQLite.

**Main components**

* `core/engine/execution_request_builder.py`
* `core/state/db.py`, `crud.py`, `db_sqlite.py`
* `state/pipeline_state.db` tables: `runs`, `workstreams`, `step_attempts`, `events`.

**Random-thought consolidation**

* This phase is where your “modular, composable plans” become **actual rows in DB**, not just documents.
* Your “patch-based edits” thinking is reflected as:

  * Each **task** = patch bundle with pattern_id, files_scope, acceptance tests. (visible in your execution docs inside the .docx)
  * The run request binds those patches to a specific repo state.

---

## 6. Phase 3 – Scheduling & Task Graph

**What happens**

* Load workstream + tasks.
* Build a **DAG** based on dependencies (spec-driven + author-defined).
* Determine what can run **in parallel** vs **must be sequential**.
* Populate the **task queue** with PENDING tasks.

**Main components**

* `core/engine/scheduler.py` – DAG resolution & queue building.
* Workstream definitions (`workstreams/*.json`) with `depends_on`.
* Task lifecycle states: `PENDING → IN_PROGRESS → VALIDATING → COMPLETED/FAILED/...`. 

**Random-thought consolidation**

* Your “multi-workstream / DAG workstreams” idea is here: scheduler slices DAG into **independent workstreams** for parallelism.
* Your “Final 20% verification library” is expressible as **post-phase verification tasks** that hang off the DAG end nodes.

---

## 7. Phase 4 – Tool Routing & Adapter Selection

**What happens**

* For each scheduled step, consult **Tool Registry + Tool Profiles**:

  * Match by language, task type, environment, etc.
* Select the best tool adapter (aider / Codex / custom / manual) with fallbacks.
* Validate adapter configuration (commands, paths, env, timeouts). 

**Main components**

* `Tool Registry`, `config/tool_profiles.json`
* `core/engine/tools.py`, adapter implementations.
* Multi-instance pool / cluster control for Aider/Codex (ToolProcessPool + ClusterManager). 

**Random-thought consolidation**

* Your “Copilot CLI controlling 3–5 Aider instances” is not separate; it’s **one routing mode**:

  * ToolProcessPool manages N aider processes. 
  * ClusterManager / launch_cluster(`"aider"`) adds routing strategies (RR, least-busy, sticky).
* Your “tool selection based on pattern + environment” is exactly the **Tool Selection Decision Tree + Profile Matching Algorithm**. 

---

## 8. Phase 5 – Execution & Validation

**What happens**

* Executor pulls next task from queue.
* Invokes correct adapter: spawn process / call API / manual instructions.
* Streams output, tracks duration, captures files changed.
* Runs **acceptance tests** (linting, unit tests, import checks, etc.).
* Updates task state (`IN_PROGRESS → VALIDATING → COMPLETED/FAILED/TIMEOUT/...`). 

**Main components**

* `core/engine/executor.py`, `circuit_breakers.py`, `recovery.py`.
* Error plugins invoked as part of validation (ruff/mypy/pytest/etc).
* Task Lifecycle state machine diagram. 

**Random-thought consolidation**

* All your detailed “final 20%” patterns (boundary scans, state transitions, temporal checks, etc.) plug in here as:

  * **Verification patterns** bound to tasks.
  * Each pattern defines *what to validate* and *which tools to use*.
* Your idea “every change has acceptance tests baked into the plan” is literally this Phase.

---

## 9. Phase 6 – Error Analysis, Auto-Fix & Escalation

**What happens**

* On FAILED/TIMEOUT/etc, error engine:

  * Collects outputs/logs.
  * Runs configured **error plugins** (ruff, mypy, pytest, semgrep, etc.).
  * Classifies error (transient vs permanent vs unknown).
* For auto-fixable errors:

  * Plugins generate patches / suggestions.
  * System applies patch, re-runs validation.
* Circuit breaker:

  * Protects from runaway retries; transitions to `CIRCUIT_OPEN / HALF_OPEN`.
* Escalation:

  * Marked for manual intervention, PM/CCPM link, or higher-tier AI.

**Main components**

* `error/engine/error_engine.py`, `plugin_manager.py`, `error_state_machine.py`.
* `error/plugins/*` – per-language and cross-cutting plugins. 
* Error Escalation diagrams.

**Random-thought consolidation**

* Your “error pipeline” and “self-healing gate” live here as **formal states + plugins**:

  * Error states: NEW → ANALYZED → FIXED/VERIFIED/etc.
  * Escalation rules = patterns (ERR-EXEC, ERR-PIPE, etc.).
* The patterns you described for **“pattern-based bug detection”** map directly into plugin behavior and validation sequences.

---

## 10. Phase 7 – Monitoring, Completion & Archival

**What happens**

* While phases 3–6 run, monitoring components:

  * Show runs/workstreams/tasks status in CLI dashboard, UI, or JSON.
  * Surface tool health metrics and error counts.
* When DAG is exhausted:

  * Mark run as **COMPLETED / FAILED / PARTIAL**.
  * Archive artifacts, logs, final DB snapshot (or compress).

**Main components**

* `core/ui_cli.py`, GUI/TUI pipelines.
* DB views: `runs`, `workstreams`, `file_lifecycle`, `tool_health_metrics`, `error_records`.
* Visual dashboards driven by these tables.

**Random-thought consolidation**

* Your “mission control board” and “module-in-a-panel” ideas hang here.
* All the ID/pattern metadata you keep insisting on is the **bridge** between:

  * DB rows (runs/tasks/files)
  * Module-centric docs and visual dashboards.

---

## 11. Cross-Cutting Layer A – Patterns, IDs & Templates

Across all phases, your core mental model is:

* **Patterns = contracts**, not clones.
* **doc_id / pattern_id / module_id** = primary keys to tie code, docs, tests, diagrams together.
* **Templates** (OpenSpec, workstreams, prompt templates, error pipelines) = *pattern instances*.

Where they matter by phase:

* Phase 0–1: pattern families, IDs, and schemas decide **what shapes** are allowed.
* Phase 2–3: workstream templates + task patterns decide **what gets scheduled**.
* Phase 4–5: tool profiles + execution patterns decide **how to run**.
* Phase 6: error patterns and recovery templates decide **how to self-heal**.
* Phase 7: reporting templates decide **how to summarize and archive**.

Your long .docx is essentially a **pattern bible**; this doc gives it a **spine** (0–7) so it stops feeling random.

---

## 12. Cross-Cutting Layer B – Files, Tasks, UI & State

You already have focused diagrams that zoom into specific “axes”:

* **Task Lifecycle** – full state machine for a *task* (PENDING → IN_PROGRESS → VALIDATING → COMPLETED/FAILED/etc). 
* **File Lifecycle** – how an individual *file* moves through DISCOVERED → CLASSIFIED → PROCESSING → IN_FLIGHT → QUARANTINED/REVIEW → COMMITTED.
* **UI Flow** – how the user interacts with CLI dashboard and how it queries the DB.
* **Data & Module Diagrams** – end-to-end flows + module dependency hierarchy.

These are *projections* of the same 0–7 pipeline:

* Task Lifecycle sits mostly in Phases 3–6.
* File Lifecycle sits mostly in Phases 2–6.
* UI Flow & Data Model sits mostly in Phase 7 (but observes 2–6).

---

## 13. Diagram Index (Where Each Existing Diagram Fits)

Using your Visual Architecture Guide as the index:

* **SYSTEM_ARCHITECTURE.md** – overview of all subsystems; aligns with Phases 0–7 as the *big picture map*.
* **TASK_LIFECYCLE_DIAGRAM.md** – detailed task state machine; primarily Phases 3–6.
* **DOC_ERROR_ESCALATION_DIAGRAM.md** – error pipeline + escalation; Phase 6.
* **DOC_TOOL_SELECTION_DIAGRAM.md** – tool selection / routing logic; Phase 4 + part of 5.
* **DOC_SPEC_INTEGRATION_DIAGRAM.md** – OpenSpec → workstream converter; Phase 1.
* **DOC_FILE_LIFECYCLE_DIAGRAM.md** – file lifecycle; spans Phases 2–6.
* **DOC_UI_FLOW_DIAGRAM.md** – CLI / UI command tree & data model; Phase 7’s front-door.
* **E2E_PROCESS_VISUAL_DIAGRAM.md** – existing 0–8 process; our new 0–7 view is essentially a cleaned-up version of this.
* **SYSTEM_VISUAL_DIAGRAMS.md / VISUAL_ARCHITECTURE_GUIDE.md** – meta-index + conventions + validation script.

---

## 14. How You Actually Use This in Practice

When you feel like you’re drowning in random ideas, use this as your **operational spine**:

1. **Decide which Phase you’re working on**

   * “I’m designing the error pipeline” → Phase 6.
   * “I’m fixing how tools are selected” → Phase 4.
   * “I’m making a new plan/spec” → Phase 1.

2. **Attach work to a Phase + Pattern**

   * Phase N → pick the relevant diagrams & modules above.
   * Bind work to a pattern_id / doc_id so it plugs into the system instead of being a one-off.

3. **Encode as Workstreams + Specs**

   * Use OpenSpec + workstream templates so future AI runs can reuse it.

4. **Let the Pipeline Do the Rest**

   * Once you’ve encoded it, the 0–7 pipeline handles:

     * state, retries, error handling, monitoring, multi-tool orchestration.

If you want, next step I can:

* Turn this into a **repo-ready Markdown doc** with a minimal front-matter block and explicit section IDs, or
* Slice it into **separate phase docs** (PH-00…PH-07) that your orchestrator can execute one at a time.
