# Section-Aware Repo Refactor

## Execution Order & Parallelization Guide

This document turns the **Section-Aware Repo Refactor Workstream Plan** into a concrete execution order: what runs first, what can run in parallel, and what must stay strictly sequential.

It’s written so a human or an agentic CLI app (scheduler) can follow it directly.

---

## 0. Global Rules

1. **WS-01 must be first.**
   The **Hardcoded Path Index System** is the foundation; every later decision depends on its scan results.

2. **Phase order is strict.**
   Phases run in order **1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9**, but some phases contain *parallel groups*.

3. **Within a phase:**

   * Some workstreams can run **in parallel**, as explicitly noted.
   * Others are **strictly sequential** (e.g., WS-09 → WS-10 → WS-11).

4. **“ALL previous sections/workstreams” means:**

   * **Sections** = prior *section families* (Meta, GUI, Infra, Spec, Error, Core, etc.).
   * **Workstreams** = all WS with a lower number in earlier phases.

5. **Tests & CI come near the end.**
   WS-19 (Test suite updates) and WS-21 (CI gate) enforce the final structure and should not run early.

---

## 1. High-Level Timeline (Bird’s-Eye View)

Here’s the full chain in dependency order, with parallel groups called out:

1. **WS-01** – Hardcoded Path Index System

2. **WS-02** – Section Mapping Configuration (depends on WS-01)

3. **Phase 3 – Parallel Group 1 (after WS-02):**

   * **WS-03** – Refactor Meta Section
   * **WS-04** – Refactor GUI Section
   * **WS-05** – Refactor Infra Section – CI Foundation
     👉 **Run WS-03, WS-04, WS-05 in parallel** once WS-02 is done.

4. **Phase 4 – Parallel Group 2 (after WS-03/04/05):**

   * **WS-06** – Refactor AIM Section
   * **WS-07** – Refactor PM Section – CCPM
   * **WS-08** – Refactor Aider Section
     👉 **Run WS-06, WS-07, WS-08 in parallel** once Phase 3 completes.

5. **Phase 5 – Spec Tooling (strictly sequential):**

   * **WS-09** → **WS-10** → **WS-11**
     👉 **No parallelization** within this phase.

6. **Phase 6 – Error Pipeline (strictly sequential):**

   * **WS-12** → **WS-13** → **WS-14**
     👉 **No parallelization** within this phase.

7. **Phase 7 – Core Pipeline (strictly sequential, highest risk):**

   * **WS-15** → **WS-16** → **WS-17**
     👉 **No parallelization** within this phase.

8. **Phase 8 – Integration Layer (can partially overlap):**

   * **WS-18** – Update Infrastructure Scripts
   * **WS-19** – Test Suite Updates
     👉 **WS-18 and WS-19 both depend on ALL previous workstreams.**
     They *can partially overlap* if you manage file conflicts carefully (e.g., different subtrees / branches).

9. **Phase 9 – Documentation & Enforcement:**

   * **WS-20** – Final Documentation & Mapping (depends on ALL workstreams)
   * **WS-21** – CI Gate for Path Standards (Optional)

     * Depends on **WS-01 + all refactor workstreams (WS-03–WS-19)**.

---

## 2. Phase-by-Phase Detail

### Phase 1 – Foundation (Indexer Implementation)

**Must run first. No parallelization.**

* **WS-01 – Hardcoded Path Index System**

  * Builds:

    * `tools/hardcoded_path_indexer.py`
    * `scripts/paths_index_cli.py`
    * `refactor_paths.db`
    * `docs/HARDCODED_PATH_INDEXER.md`
  * Purpose: Scan for hardcoded paths across code, configs, CI, and docs.
  * **Dependencies:** none.
  * **Blocking:** WS-02; indirectly everything else.

---

### Phase 2 – Planning & Configuration

**Runs after Phase 1. No parallelization.**

* **WS-02 – Section Mapping Configuration**

  * Builds:

    * `config/section_map.yaml` (authoritative section mapping)
    * `docs/SECTION_REFACTOR_PLAN.md`
  * Uses WS-01 scan results to:

    * Identify high-impact patterns.
    * Flag cross-section violations and circular dependencies.
  * **Dependencies:** WS-01.
  * **Blocking:** WS-03, WS-04, WS-05 (Phase 3).

---

### Phase 3 – Isolated Sections (Parallel Group 1)

**Can fully parallelize within the phase, but only after WS-02.**

* **Entry condition:** WS-02 complete.

**Parallel Group 1:**
Run **WS-03, WS-04, WS-05 in parallel.**

* **WS-03 – Refactor Meta Section**

  * Targets: `meta/ ← PHASE_DEV_DOCS/, plans/, Coordination Mechanisms/`
  * Refactors: primarily docs and meta files.
  * **Dependencies:** WS-02.

* **WS-04 – Refactor GUI Section**

  * Targets: `gui/ ← GUI_PIPELINE/, GUI docs`
  * Refactors: GUI planning / doc structure.
  * **Dependencies:** WS-02.

* **WS-05 – Refactor Infra Section – CI Foundation**

  * Targets: `infra/ci/ ← .github/workflows/, pytest.ini, requirements.txt, sandbox_repos/`
  * Refactors: CI configs and paths, but still relatively isolated.
  * **Dependencies:** WS-02.

**Constraint:** Do not start Phase 4 until WS-03, WS-04, and WS-05 are all complete.

---

### Phase 4 – Moderately Isolated Sections (Parallel Group 2)

**Can fully parallelize within the phase, but only after Phase 3 (WS-03–05).**

* **Entry condition:** WS-03, WS-04, WS-05 complete.

**Parallel Group 2:**
Run **WS-06, WS-07, WS-08 in parallel.**

* **WS-06 – Refactor AIM Section**

  * Targets: `aim/ ← src/pipeline/aim_bridge.py, .AIM_ai-tools-registry/`
  * Refactors: AIM bridge locations, adapters, registry references.
  * **Dependencies:** WS-03–WS-05 (Phase 3 complete).

* **WS-07 – Refactor PM Section – CCPM**

  * Targets: PM/CCPM-related files and instructions.
  * Refactors: project management integration paths.
  * **Dependencies:** WS-03–WS-05.

* **WS-08 – Refactor Aider Section**

  * Targets: `aider/ ← src/pipeline/prompts.py, templates/, AIDER_PROMNT_HELP/`
  * Refactors: Aider prompts & templates into a clean section.
  * **Dependencies:** WS-03–WS-05.

**Constraint:** Do not start Phase 5 until WS-06, WS-07, and WS-08 are all complete.

---

### Phase 5 – Spec Tooling (Strictly Sequential)

**No parallelization inside this phase. Internal dependencies are strong.**

* **Entry condition:** Phases 1–4 complete (WS-01–WS-08).

**Order:**
**WS-09 → WS-10 → WS-11**

* **WS-09 – Refactor Spec Section – Tools Foundation**

  * Moves spec tools into `spec/tools/` (indexer, resolver, renderer, patcher, guard).
  * **Dependencies:** all prior section refactors; this is implied but not cross-linked by ID.
  * **Blocking:** WS-10.

* **WS-10 – Refactor Spec Section – OpenSpec Integration**

  * Targets: OpenSpec parser/converter, `openspec/`, `bundles/`.
  * **Dependencies:** WS-09.

* **WS-11 – Refactor Spec Section – Documentation**

  * Targets: `spec/docs/` (multi-doc versioning suite).
  * **Dependencies:** WS-10.

**Constraint:** The spec section must be internally coherent; do not reorder WS-09/10/11.

---

### Phase 6 – Error Pipeline (Strictly Sequential)

**No parallelization inside this phase. This is a high-risk refactor.**

* **Entry condition:** Phase 5 complete (WS-09–WS-11).

**Order:**
**WS-12 → WS-13 → WS-14**

* **WS-12 – Refactor Error Section – Shared Utilities**

  * Targets: `shared/utils/` *or* `error/shared/utils/ ← src/utils/`
  * Critical decision: whether to keep utilities as shared or fully isolate into error section.
  * **Dependencies:** all previous phases (because these utilities are widely used).
  * **Blocking:** WS-13, WS-14.

* **WS-13 – Refactor Error Section – Plugins**

  * Targets: `error/plugins/ ← src/plugins/`
  * **Dependencies:** WS-12 (utils path must be stable first).

* **WS-14 – Refactor Error Section – Engine Consolidation**

  * Targets: `error/engine/ ← MOD_ERROR_PIPELINE/, src/pipeline/error_*.py`
  * **Dependencies:** WS-12 and WS-13.

**Constraint:** Do not start Core refactors (Phase 7) until WS-12–WS-14 are done and stable.

---

### Phase 7 – Core Pipeline (Strictly Sequential, Highest Risk)

**No parallelization inside this phase. This is the heart of the system.**

* **Entry condition:** Phases 1–6 complete (WS-01–WS-14).

**Order:**
**WS-15 → WS-16 → WS-17**

* **WS-15 – Refactor Core Section – State & Data**

  * Targets: `core/state/ ← DB, bundles, worktree modules`
  * **Dependencies:** ALL previous sections (Meta, GUI, Infra, Spec, Error, AIM, PM, Aider).
  * **Blocking:** WS-16.

* **WS-16 – Refactor Core Section – Orchestration**

  * Targets: `core/engine/ ← orchestrator, scheduler, executor, tools, circuit_breakers, recovery, etc.`
  * **Dependencies:** WS-15 + ALL previous sections (explicitly restated for emphasis).

* **WS-17 – Refactor Core Section – Planning**

  * Targets: `core/planning/ ← planner.py, archive.py`
  * **Dependencies:** WS-16.

**Constraint:** This phase should be scheduled last among code refactors; avoid starting any integration/test updates that assume the old layout once WS-15 begins.

---

### Phase 8 – Integration Layer (Can Partially Parallelize)

**Integration and tests across the new structure.**

* **Entry condition:** **ALL previous workstreams (WS-01–WS-17) complete.**

Two workstreams:

* **WS-18 – Update Infrastructure Scripts**

  * Targets: `infra/scripts/` (or keep at top-level `scripts/` – decision inside WS).
  * **Dependencies:** ALL previous workstreams.
  * Updates 30+ scripts to match the new directory layout.

* **WS-19 – Test Suite Updates**

  * Targets: `tests/` (remain at top-level).
  * **Dependencies:** ALL previous workstreams.
  * Updates imports, fixtures, and test data paths.

**Parallelization rule for Phase 8:**

* **WS-18 and WS-19 can partially overlap** if:

  * They do not modify the same files concurrently, and/or
  * You run them on separate branches and merge carefully.
* From a conservative scheduler perspective:

  * Treat them as **parallelizable**, but enforce file-level or branch-level isolation.

---

### Phase 9 – Documentation & Enforcement

**Finalizing the mapping and setting CI guards.**

* **Entry condition for WS-20:** ALL previous workstreams complete (WS-01–WS-19).
* **Entry condition for WS-21:** WS-01 and all refactor workstreams (WS-03–WS-19) complete.

Order:

1. **WS-20 – Final Documentation & Mapping**

   * Depends on ALL workstreams.
   * Produces:

     * Full old→new path mapping.
     * Verification docs and logs.
     * Updated `CLAUDE.md`, `README.md`, `AGENTS.md`, and architecture docs.

2. **WS-21 – CI Gate for Path Standards (Optional)**

   * Target: `.github/workflows/path_standards.yml`.
   * **Dependencies:**

     * WS-01 (needs the indexer rules/patterns).
     * All refactor workstreams (WS-03–WS-19).
   * Purpose: enforce that no deprecated paths are reintroduced.

---

## 3. Dependency Table (For Schedulers / Agents)

This table is designed to be easy to convert into `depends_on` in your workstream JSON.

| WS ID | Name                                          | Direct Dependencies                                    | Parallel Group                        |
| ----: | --------------------------------------------- | ------------------------------------------------------ | ------------------------------------- |
| WS-01 | Hardcoded Path Index System                   | –                                                      | None                                  |
| WS-02 | Section Mapping Configuration                 | WS-01                                                  | None                                  |
| WS-03 | Refactor Meta Section                         | WS-02                                                  | Phase 3 – Group 1 (with WS-04, WS-05) |
| WS-04 | Refactor GUI Section                          | WS-02                                                  | Phase 3 – Group 1                     |
| WS-05 | Refactor Infra Section – CI Foundation        | WS-02                                                  | Phase 3 – Group 1                     |
| WS-06 | Refactor AIM Section                          | WS-03, WS-04, WS-05 (i.e., Phase 3 complete)           | Phase 4 – Group 2 (with WS-07, WS-08) |
| WS-07 | Refactor PM Section – CCPM                    | WS-03, WS-04, WS-05                                    | Phase 4 – Group 2                     |
| WS-08 | Refactor Aider Section                        | WS-03, WS-04, WS-05                                    | Phase 4 – Group 2                     |
| WS-09 | Refactor Spec Section – Tools Foundation      | WS-06, WS-07, WS-08 (i.e., Phases 1–4 complete)        | None (Phase 5 sequential)             |
| WS-10 | Refactor Spec Section – OpenSpec Integration  | WS-09                                                  | None                                  |
| WS-11 | Refactor Spec Section – Documentation         | WS-10                                                  | None                                  |
| WS-12 | Refactor Error Section – Shared Utilities     | WS-11 (i.e., all prior phases complete)                | None (Phase 6 sequential)             |
| WS-13 | Refactor Error Section – Plugins              | WS-12                                                  | None                                  |
| WS-14 | Refactor Error Section – Engine Consolidation | WS-12, WS-13                                           | None                                  |
| WS-15 | Refactor Core Section – State & Data          | WS-14 + “ALL previous sections” (practically WS-01–14) | None (Phase 7 sequential)             |
| WS-16 | Refactor Core Section – Orchestration         | WS-15 + all previous sections                          | None                                  |
| WS-17 | Refactor Core Section – Planning              | WS-16                                                  | None                                  |
| WS-18 | Update Infrastructure Scripts                 | ALL previous workstreams (WS-01–WS-17)                 | Phase 8 (can overlap with WS-19)      |
| WS-19 | Test Suite Updates                            | ALL previous workstreams (WS-01–WS-17)                 | Phase 8 (can overlap with WS-18)      |
| WS-20 | Final Documentation & Mapping                 | ALL workstreams (WS-01–WS-19)                          | None                                  |
| WS-21 | CI Gate for Path Standards (Optional)         | WS-01 + all refactor WS (WS-03–WS-19)                  | Can follow WS-20 or be parallelized   |

> **Note:** “ALL previous sections/workstreams” above is expanded into specific IDs based on the phase order so a scheduler can create a strict DAG.

---

## 4. How to Read This for Execution

* If you want a **strictly safe, simpler plan**, run everything **sequentially in WS ID order** respecting dependencies.
* If you want **maximum parallelism** while staying safe:

  * Use **Group 1 (WS-03/04/05)** and **Group 2 (WS-06/07/08)** as true parallel groups.
  * Consider **WS-18 and WS-19** as parallel but:

    * Either isolate them by branch,
    * Or lock subtrees to avoid cross-file conflicts.

 agentic CLI  clear, dependency-aware path from **WS-01** (indexer) all the way to **WS-21** (CI enforcement).
