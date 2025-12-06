---
doc_id: DOC-GUIDE-UET-ERROR-PIPELINE-A-CARD-LEDGER-MD-001
---

Yes—these docs give you a *lot* of reusable patterns we can steal for the error-pipeline module. I’ll keep this at the “ideas + wiring” level, no new documents.

I’ll group the opportunities into themes:

---

## 1. Make the Error Pipeline a Card → Ledger → Registry system

In the docs module, every doc is a product with: **Doc Card → Ledger → Registry**, plus DDS and CI gates.

You can mirror this for the error pipeline:

* **ErrorPatchCard (or ErrorCaseCard)**
  YAML per patch / error case:

  * `ulid`, `key` (e.g. `ERR_PATCH_2025_001`),
  * `source_phase_id` / `source_run_id`,
  * `files_touched`, `risk_tier`, `status` (`intake`, `repairing`, `quarantined`, `escalated`, `resolved`),
  * links to:

    * originating workstream (`WS-ERR-01A`),
    * escalation workstream (`WS-ERR-02A`),
    * GitHub issue/PR id.

* **Error Ledger**
  Append-only `.ledger/error.jsonl`, modeled on the doc ledger schema (events like `CREATE`, `UPDATE`, `PUBLISH`, `CONSOLIDATE`).
  New event types for the error pipeline:

  * `PATCH_INTAKE`, `PATCH_APPLY_FAILED`, `PATCH_QUARANTINED`,
  * `PATCH_ESCALATED`, `PATCH_SUPERSEDED`, `PATCH_RESOLVED`.

* **Error Registry**
  `registry/error.registry.yaml` similar to `docs.registry.yaml`, keyed by error/patch key or ULID.

**Process improvement:**
Right now we modeled runs, step attempts, and patch ledger entries. Add this Card/Ledger/Registry layer and you get:

* a **single source of truth** for every error/patch,
* cheap audit queries (“show all quarantined patches that were escalated to GitHub but not resolved”),
* a natural place to attach additional metadata (risk, SLO impact, owner).

---

## 2. Treat Error Pipeline workers as plugins in a micro-kernel

The docs suite uses a **micro-kernel + plugins** model where each capability is a plugin with JSON I/O, manifest, and conformance tests.

You can do the same for error pipeline components:

* Define plugin keys like:

  * `error.intake` (normalize failing patch → ErrorPatchCard)
  * `error.analyze` (AI analysis of failure)
  * `error.patch.generate` (AI diff generation)
  * `error.patch.apply` (patch worker)
  * `error.escalate` (GitHub worker, email notifier, etc.)

* Each plugin has a **manifest** similar to `plugin.contract.v1`:

  * `apiVersion: error.plugin.contract.v1`
  * `key: ERR_PATCH_APPLY`
  * `inputs`: e.g. `error_case`, `patch_artifact`
  * `outputs`: e.g. `apply_result`, `test_report`
  * `conformance.tests`: fixtures and behavioral tests.

* Reuse the JSON-envelope pattern from the docs CLI (`{ ok, artifacts, messages, errors }`).

**Process improvement:**
Instead of bespoke scripts per phase, you get:

* clear plugin boundaries,
* compatibility ranges & conformance kits,
* the ability to swap implementations (e.g., different AI backends) without touching PH-ERR specs.

---

## 3. Borrow the multi-tool coordination model for Error workstreams

The **Workstream Coordination Guide** already defines a clean pattern:

* branches: `workstream/<ws_id>`
* worktrees: `.worktrees/<ws_id>/`
* scripts to check status, dependencies, and “who did what where.”

For the error pipeline:

* Use similar **worktree conventions** for error-focused work:

  * e.g. `.worktrees/err-<run_id>` for the EDIT zone where patches are applied/tested.

* Adapt the `check_workstream_status.sh` idea into `check_error_status.sh`:

  * list all error runs,
  * show which patches are `quarantined`, `escalated`, `resolved`,
  * show which tools (Aider, Codex, Claude, internal workers) have touched each patch (via branch / commit metadata).

* Apply the dependency pattern to **PH-ERR-01 → PH-ERR-02**:

  * PH-ERR-02 workstream only starts when PH-ERR-01 run has completed (or hit terminal failure) and the ErrorPatchCard has `status: quarantined`.

**Process improvement:**
You get the same **multi-tool, multi-workstream choreography**, but focused on error runs:

* easy to see *which* error cases are in which phase,
* better guardrails when multiple tools are trying to help fix the same error.

---

## 4. Use the path indexer & abstraction as first-class error-pipeline tools

You already have a **Hardcoded Path Indexer** that scans for path-like literals, classifies them, and writes results into `refactor_paths.db`.
And you have a **Path Abstraction Layer** (key→path registry, resolver, CLI).

There are several direct upgrades for the error pipeline:

1. **Declare all error pipeline paths via keys**
   Use `config/path_index.yaml` keys like:

   * `error.quarantine_dir`
   * `error.logs_dir`
   * `error.phase_docs.err01`
   * `error.phase_docs.err02`

   Then in PH-ERR specs and workers, *never* hard-code paths—always call the resolver / CLI.

2. **Use the indexer as a pre-flight check for patches**
   Before applying a patch:

   * run `paths_index_cli.py` against the patch’s changed files or the EDIT worktree, checking for:

     * reintroduced deprecated modules (`MOD_ERROR_PIPELINE`, `src.pipeline`),
     * direct references to `C:\` or other forbidden sections,
     * hard-coded paths bypassing your registry.

   If violations appear → patch is **rejected or auto-routed to error pipeline**.

3. **Use section tracking to classify risk**
   The indexer already tracks sections (`PHASE_DEV_DOCS`, `MOD_ERROR_PIPELINE`, `gui`, etc.).
   You can:

   * increase risk tier for patches touching certain sections (e.g., `error.engine`, `core.state`),
   * feed that into your `constraints` / `acceptance` for PH-ERR phases.

**Process improvement:**
Path handling becomes:

* consistent across modules,
* enforced by CI and error pipeline workers,
* easier to migrate when you move the error module again.

---

## 5. Integrate CI path standards into patch acceptance for error runs

The **CI Path Standards Enforcement** workflow already uses the indexer + regex gates to block deprecated imports like `src.pipeline.*` and `MOD_ERROR_PIPELINE.*`.

You can pull that directly into error-pipeline acceptance:

* Add a **check** in PH-ERR-01 / WS-ERR-01A acceptance:

  * after patch apply + tests but *before* Run success:

    * run the same `paths_index_cli.py gate --regex "^MOD_ERROR_PIPELINE\."` etc., over the EDIT worktree.
  * if any violation → patch is auto-quarantined and routed to PH-ERR-02.

* Extend patch policy to include:

  * “**No reintroduction of deprecated module names**,”
  * possibly “No new hard-coded paths outside allowed sections.”

**Process improvement:**
Your error pipeline becomes a **guardrail for architectural path discipline**, not just runtime failures:

* any patch that sneaks old module names back in gets caught,
* the same logic runs in CI and in the error-repair loop—no drift.

---

## 6. Give the Error Pipeline its own DDS & CI gates (mirroring docs)

The spec suite defines **Deliverable Definition Sheets (DDS)** and layered CI gates (L0–L5) for docs.

Apply the same idea:

* **DDS for the Error Pipeline module**
  Example deliverable: “Automated Error Patch Handling & Escalation”

  * Acceptance:

    * “Any patch that fails tests is either successfully repaired or escalated to GitHub with full context.”
    * “No quarantined patches older than N days without escalation or resolution.”
    * Evidence: behavior tests, patch ledger slices, registry reports.

* **Gates for Error Pipeline** (analogous to L0–L5):

  * L0: static / schema checks on PH-ERR/WS-ERR docs & plugin manifests.
  * L1: contract/unit tests for error plugins (`error.intake`, `error.apply`, etc.).
  * L2: scenario tests (Given/When/Then: patch fails; system routes to PH-ERR-01; if still failing, routes to PH-ERR-02; GitHub issue exists).
  * L3: integration tests with real Git+worktrees.
  * L4: perf (e.g., p95 time to process a failing patch).
  * L5: policy (path standards, risk thresholds).

**Process improvement:**
Error handling becomes:

* governed like a first-class product,
* testable in CI with clearly defined acceptance,
* easier to evolve over time without losing guarantees.

---

## 7. Observability & SLOs for error runs

The docs module already defines **OTel traces** and SLOs for its plugins (p95 latency, error rates, etc.).

You can:

* emit traces for each error pipeline plugin:

  * `span.name = error.patch.apply`, attributes:

    * `error_patch_ulid`,
    * `source_run_id`,
    * `phase_id`,
    * `result` (`succeeded`, `failed`, `quarantined`).

* define **Error Pipeline SLOs**, e.g.:

  * “p95 time to escalate a quarantined patch < 10 minutes,”
  * “error pipeline success rate > 99% for automated repairs.”

* feed SLO breaches into the **Error Ledger** as events (`ERROR_PIPELINE_SLO_BREACH`) for later review.

**Process improvement:**
You’ll be able to answer “how healthy is our self-healing pipeline?” with data, not vibes.

---

### TL;DR

From these other-module docs you can upgrade the error pipeline by:

* adding Card/Ledger/Registry identity for errors/patches,
* plugin-izing error workers under a micro-kernel contract,
* reusing multi-tool Git worktree coordination patterns,
* embedding the path indexer + abstraction into patch validation,
* reusing CI path gates as patch acceptance checks,
* giving the error pipeline its own DDS + gates + SLOs.

When you’re ready for the next step, we can pick *one* of these (for example, “ErrorPatchCard + Error Ledger schema”) and sketch its structure so it slots into the existing PH-ERR / WS-ERR design without yet writing a full doc.
