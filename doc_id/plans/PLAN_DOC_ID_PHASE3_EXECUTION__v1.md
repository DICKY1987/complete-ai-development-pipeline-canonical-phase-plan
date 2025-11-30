---
doc_id: DOC-GUIDE-PLAN-DOC-ID-PHASE3-EXECUTION-V1-1382
status: draft
doc_type: phase_plan
phase_label: DOC_ID_PHASE3
module_refs: []
script_refs:
  - scripts/doc_triage.py
  - doc_id_registry_cli.py
---

# PLAN_DOC_ID_PHASE3_EXECUTION__v1

**Title**: DOC_ID Project Phase 3 – Migration & Steady-State Execution  
**Repo**: `complete-ai-development-pipeline-canonical-phase-plan`  
**Related**:

- `DOC_ID_PROJECT_PHASE1_COMPLETE.md`
- `DOC_ID_PROJECT_PHASE2_COMPLETE.md`
- `DOC_ID_EXECUTION_PLAN.md`
- `PARALLEL_EXECUTION_STRATEGY.md`
- `COPILOT-DOCID-EXECUTION-GUIDE.md` (AI-facing execution guide)

---

## 1. Phase Intent

This phase replaces the original DOC_ID rollout process (multiple worktrees writing directly to `doc_id/DOC_ID_REGISTRY.yaml`, reruns after CLI crashes, manual index updates) with a **deterministic, tool-driven workflow** based on:

- Strict naming/layout rules for docs,
- Triage and migration of existing documentation,
- A typed, validated DOC_ID registry,
- Batch specs + delta files (single-writer merges),
- Safe worktree usage for parallelism.

The outcome of Phase 3 is:

1. All docs are correctly classified as `DOC_*`, `PLAN_*`, or `_DEV_*` in the right folders.  
2. `scripts/doc_triage.py` and `doc_id_registry_cli.py` exist and run without errors.  
3. `doc_id/DOC_ID_REGISTRY.yaml` validates against the new schema.  
4. At least one end-to-end batch (triage → batch-mint → merge-deltas → validate) has been executed successfully.

---

## 2. Scope

### 2.1 Includes

- All Markdown documentation in this repo:
  - `docs/**`
  - `workstreams/plans/**`
  - `modules/**` (module-local docs)
  - `developer/**` (scratch)
- The DOC_ID registry:
  - `doc_id/DOC_ID_REGISTRY.yaml`
- Tooling:
  - `scripts/doc_triage.py`
  - `doc_id_registry_cli.py`

### 2.2 Excludes

- Non-doc artifacts (`.py`, `.ps1`, `.json`, `.yaml`) except where referenced in `module_refs` / `script_refs`.
- Content of `_DEV_*` scratch files (these are kept but never governed or assigned IDs).
- Any repo-wide refactor beyond what's needed to enforce naming, front matter, and registry consistency.

---

## 3. Core Rules Copilot Must Enforce

### 3.1 Document Naming & Classification

**Classes:**

- `DOC_*` – Canonical governed docs, ID-eligible.
- `PLAN_*` – Plans that may become canonical; ID-eligible when `status: canonical`.
- `_DEV_*` – Scratch / dev notes; NEVER ID-eligible.

**Locations:**

- `docs/**/DOC_*.md` – Global canonical docs.
- `workstreams/plans/**/PLAN_*.md` – Plan docs.
- `modules/**/DOC_*.md` – Module-local canonical docs.
- `developer/**/_DEV_*.{md,txt}` – Scratch.

**ID-eligibility predicate**:

A Markdown file is ID-eligible iff:

1. Path matches:
   - `docs/**/DOC_*.md`  
   - `workstreams/plans/**/PLAN_*.md`  
   - `modules/**/DOC_*.md`
2. Basename does **not** start with `_DEV_` or `_`.
3. Extension is `.md`.
4. Front matter either:
   - already has `doc_id`, or  
   - has `status` in `{canonical, draft}`.

All other files must be ignored by the DOC_ID system.

### 3.2 Front Matter Schema (Minimum)

For `DOC_*` and canonical `PLAN_*` docs:

```yaml
---
doc_id: DOC-ENG-PIPELINE-001         # required for canonical docs
doc_type: design_spec                # guide | phase_report | plan | ...
status: canonical                    # canonical | draft | scratch
ulid: 01JDEX123456789ABC             # ULID for this doc
module_refs:
  - modules/pipeline/
script_refs:
  - scripts/validate_engine.py
---
```

Scratch docs (`_DEV_*`) MUST NOT have `doc_id`.

---

## 4. Execution Patterns (Correcting the Old Process)

This phase replaces the original inefficient behavior documented in:

* `DOC_ID_EXECUTION_PLAN.md`
* `PARALLEL_EXECUTION_STRATEGY.md`
* `DOC_ID_PROJECT_PHASE1_COMPLETE.md`
* `DOC_ID_PROJECT_PHASE2_COMPLETE.md`
* `DOC_ID_PROJECT_SESSION_REPORT.md`

**Key problems in the old process:**

* Multiple worktrees wrote directly to `doc_id/DOC_ID_REGISTRY.yaml`.
* CLI crashes (e.g., emoji/Unicode output) led to partial success and repeated reruns → duplicate registry entries.
* Indexes and registry updates were often done interactively by AI with no single canonical process.
* No consistent triage or classification of docs (`DOC_` vs `_DEV_` vs plan docs).

The following patterns MUST be used going forward.

---

### 4.1 PAT-DOCID-TRIAGE-001 – Repository Doc Triage

**Goal:** Classify all Markdown docs and produce a concrete migration queue.

**Tool:** `scripts/doc_triage.py`

**Behavior (Copilot):**

1. Implement `scripts/doc_triage.py` to:

   * Scan `*.md` under repo root.
   * Skip `.git`, `node_modules`, `.venv` etc.
   * Classify:

     * `_DEV_*` outside `developer/**` → `needs_move`
     * `docs/**` files not starting with `DOC_` or `PLAN_` → `needs_rename`
     * `DOC_*` docs without `doc_id` → `needs_mint`
     * Any `DOC_*/PLAN_*` with invalid front matter → `needs_fix`

2. Example minimal triage script:

   ```bash
   python scripts/doc_triage.py > triage_report.txt
   ```

3. Migration steps:

   * Move `_DEV_*` into `developer/**`.
   * Rename important docs to `DOC_*` or `PLAN_*`.
   * Collect `needs_mint` docs into batch specs for Phase 3 execution (PAT-DOCID-BATCH-001).

This pattern **replaces** ad hoc manual scanning and "grep the repo to see what's left".

---

### 4.2 PAT-DOCID-SMOKE-001 – Single-Module Smoke Test

**Goal:** Prove the new tooling on a small scope before touching the whole repo.

**Scope example:** `modules/pipeline/`.

**Steps:**

1. Run triage on `modules/pipeline/` only; fix naming/front matter to match Section 3.

2. Create a batch spec:

   ```yaml
   # doc_id/docid_batches/docid_batch_modules_pipeline.yaml
   batch_id: DOCID-BATCH-MODULES-PIPELINE-001
   description: Assign doc_ids to pipeline module docs
   category: docs
   items:
     - logical_name: PIPELINE_OVERVIEW
       title: "Pipeline Engine Overview"
       artifacts:
         - path: modules/pipeline/DOC_PIPELINE_OVERVIEW__v1.md
   tags:
     - type:guide
     - module:pipeline
   ```

3. Run `batch-mint` in dry-run mode:

   ```bash
   python doc_id_registry_cli.py \
     --registry doc_id/DOC_ID_REGISTRY.yaml \
     batch-mint \
     --batch doc_id/docid_batches/docid_batch_modules_pipeline.yaml \
     --mode dry-run \
     --dry-run-report doc_id/docid_reports/preview_PIPELINE_001.md
   ```

4. Run `batch-mint` in deltas-only mode:

   ```bash
   python doc_id_registry_cli.py \
     --registry doc_id/DOC_ID_REGISTRY.yaml \
     batch-mint \
     --batch doc_id/docid_batches/docid_batch_modules_pipeline.yaml \
     --mode deltas-only \
     --delta-out doc_id/docid_deltas/delta_DOCID_PIPELINE_001.jsonl \
     --no-registry
   ```

5. Merge delta on the control checkout:

   ```bash
   python doc_id_registry_cli.py \
     --registry doc_id/DOC_ID_REGISTRY.yaml \
     merge-deltas \
     doc_id/docid_deltas/delta_DOCID_PIPELINE_001.jsonl \
     --report doc_id/docid_reports/merge_DOCID_PIPELINE_001.md
   ```

6. Validate:

   ```bash
   python doc_id_registry_cli.py \
     --registry doc_id/DOC_ID_REGISTRY.yaml \
     validate --duplicates \
     --report doc_id/docid_reports/final_validation_PIPELINE_001.md
   ```

If this pattern passes, the tooling is ready for repo-wide application.

---

### 4.3 PAT-DOCID-BATCH-001 – Batch Minting via Specs & Deltas

**Goal:** Bulk-assign doc_ids without direct concurrent edits to the registry.

**Rules:**

* Worktrees and local runs:

  * Use `batch-mint --mode deltas-only --no-registry`.
* Only the control checkout:

  * Runs `merge-deltas` and writes `doc_id/DOC_ID_REGISTRY.yaml`.

**Steps:**

1. Define/extend a batch spec in `doc_id/docid_batches/`.
2. Run `batch-mint` with `--mode dry-run` and inspect the preview.
3. Run `batch-mint` with `--mode deltas-only` to create a delta JSONL.
4. On the control checkout, run `merge-deltas` with all relevant delta files.
5. Regenerate indexes and run `validate` + `stats`.

This pattern replaces the old "run CLI from each worktree and let them all write into the shared registry" behavior.

---

### 4.4 PAT-DOCID-MERGE-001 – Safe Delta Merge with Rollback

**Goal:** Keep the registry consistent and recoverable.

**Steps:**

1. Before merging any batch, tag the repo:

   ```bash
   git tag -a "pre-docid-batch-$(date +%Y%m%d-%H%M%S)" \
     -m "Checkpoint before DOC_ID batch"
   ```

2. Merge deltas:

   ```bash
   python doc_id_registry_cli.py \
     --registry doc_id/DOC_ID_REGISTRY.yaml \
     merge-deltas \
     doc_id/docid_deltas/delta_*.jsonl \
     --report doc_id/docid_reports/merge_DOCID_ALL_001.md
   ```

3. If merge is bad or registry fails validation:

   ```bash
   git reset --hard pre-docid-batch-YYYYMMDD-HHMMSS
   git worktree prune
   ```

4. If merge is good:

   * Commit updated `doc_id/DOC_ID_REGISTRY.yaml`,
   * Commit `doc_id/docid_reports/merge_DOCID_ALL_001.md`,
   * Commit any regenerated indexes.

This pattern ensures every batch operation is atomically reversible, unlike the original approach.

---

### 4.5 PAT-DOCID-WT-001 – Worktree Usage Without Shared Registry Writes

**Goal:** Use Git worktrees for isolation and parallelism without reintroducing shared-write hazards.

**Rules:**

* Worktrees MAY:

  * Rename/move docs.
  * Edit front matter.
  * Create batch specs.
  * Run `batch-mint --mode deltas-only --no-registry`.
* Worktrees MUST NOT:

  * Run `merge-deltas`.
  * Write `doc_id/DOC_ID_REGISTRY.yaml` directly.

**Example pattern:**

1. On main checkout:

   ```bash
   git checkout feat/docid-rollout
   git worktree add .worktrees/docid-docs feat/docid-rollout
   git worktree add .worktrees/docid-modules feat/docid-rollout
   ```

2. In `.worktrees/docid-docs`:

   * Run triage scoped to `docs/**`.
   * Fix naming/front matter.
   * Generate deltas with `batch-mint --mode deltas-only`.

3. In `.worktrees/docid-modules`:

   * Same for `modules/**`.

4. Back on main checkout:

   * Merge all deltas.
   * Regenerate indexes.
   * Run full validation and tests.
   * Commit.

This corrects the earlier strategy where each worktree acted as a shared writer on the registry.

---

## 5. Phase Completion Criteria

Phase 3 is complete when:

1. `scripts/doc_triage.py` exists and reports **zero violations** after cleanup.
2. `doc_id_registry_cli.py validate` passes without errors.
3. `doc_id/DOC_ID_REGISTRY.yaml` conforms to the new schema (Pydantic model).
4. At least one full batch (PAT-DOCID-SMOKE-001 + PAT-DOCID-BATCH-001 + PAT-DOCID-MERGE-001) has completed successfully.
5. Old habits have been eliminated:

   * No worktree directly edits `doc_id/DOC_ID_REGISTRY.yaml`.
   * No bulk registry edits are done manually.
   * Indexes are generated from the registry, not hand-maintained.

When these are true, DOC_ID Phase 3 (Migration & Steady-State Execution) is considered complete, and further optimization (e.g. CI integration, richer metadata, module-centric refactors) can proceed as DOC_ID Phase 4+.

---


