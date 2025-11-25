Nice, that evaluation is actually perfect fuel for what you want: **multiple CLI instances + git worktrees, but with decision elimination and safety built in**.

You already saw the high-level “plan is good” verdict. Let me turn that into a **single, concrete spec** you can drop into the repo to govern multi-CLI + worktrees.

You can save this as:

> `specifications/MULTI_CLI_WORKTREES_EXECUTION_SPEC.md`
> or
> `docs/MULTI_CLI_WORKTREES_EXECUTION_SPEC.md`

---

````markdown
# MULTI_CLI_WORKTREES_EXECUTION_SPEC

**Status**: DRAFT  
**Version**: 0.1.0  
**Scope**: Running multiple instances of CLI tools across git worktrees  
**Audience**: AI agents (Copilot CLI, Claude Code, etc.) and humans  

---

## 1. Problem & Context

We frequently run **multiple instances of CLI apps** (Copilot CLI, custom Python CLIs, etc.) across **multiple git worktrees** to speed up large refactors and metadata updates (e.g., the DOC_ID project).

In the DOC_ID execution, this led to:

- Multiple worktrees **writing directly** to shared files (e.g., `doc_id/DOC_ID_REGISTRY.yaml`)
- CLI crashes / retries that partially succeeded → **duplicate entries, inconsistent state**
- Manual decision making per run (what scope? which files? how to retry?) → **decision fatigue**
- No single, canonical pattern for:
  - which CLI runs where,
  - what each instance is allowed to touch,
  - how results are merged and validated.

This spec defines a **deterministic execution model** for:

- Multiple CLI instances
- Multiple git worktrees
- Single-writer global state
- Template-based, self-healing runs.

---

## 2. Design Principles

1. **Single Writer for Global State**
   - Global/registry files (e.g. `doc_id/DOC_ID_REGISTRY.yaml`, central indexes) are **only written** from a single **control checkout**, never from worker worktrees.

2. **Worktree-Scoped CLI Instances**
   - Each worktree is an isolated “slice” with a declared **scope** of paths.
   - CLI instances in a worktree operate **only** on that slice and produce **deltas/patches**, not final global state.

3. **Template-Driven Execution**
   - CLI runs follow **pre-defined execution templates** (ToolExecutionTemplates) that encode:
     - scope,
     - allowed ops,
     - required outputs,
     - success criteria.
   - This minimizes runtime decisions (“What do I do?”) and improves repeatability.

4. **Ground Truth Verification**
   - All multi-worktree / multi-CLI activity is validated by:
     - schema checks (Pydantic/JSONSchema),
     - registry validation,
     - tests,
     - and explicit success metrics (e.g., zero duplicates, zero invalid docs).

5. **Self-Healing & Retry**
   - Common failures (CLI crash, partial delta generation) are handled via:
     - idempotent templates,
     - re-runnable commands,
     - rollback tags on the control checkout.

6. **Decision Elimination Telemetry**
   - Each CLI run emits structured telemetry so we can measure:
     - success/failure,
     - time per file,
     - error types,
     - number of decisions avoided (e.g. auto-selected templates).

---

## 3. Roles & Entities

### 3.1 Control Checkout

**Definition**: The primary repo checkout (non-worktree) that:

- Owns long-lived branches (`main`, `feat/*`).
- Is the **only writer** for:
  - global registries (e.g., `doc_id/DOC_ID_REGISTRY.yaml`),
  - derived indexes,
  - “state” files.
- Runs:
  - `merge-deltas`,
  - final `validate`,
  - full test suites,
  - tagging and rollback.

**MUST**:

- Run all **merge operations** and **global validations**.
- Be the only place where CLI commands that **write global state** are allowed.

---

### 3.2 Worker Worktrees

**Definition**: Additional repo checkouts created via `git worktree add`, each with a **scope**:

Examples:

```text
WT-DOCS    → docs/**, workstreams/plans/**
WT-MODULES → modules/**, core/**, aim/**, pm/**
WT-TESTS   → tests/**
````

**MUST**:

* Declare a `WT_ID` and `WT_SCOPE` via environment variables.
* Only modify files inside their declared scope.
* Produce **deltas, patches, and logs**, not final global state.

**MUST NOT**:

* Write to global registry files (e.g. `doc_id/DOC_ID_REGISTRY.yaml`).
* Run merge operations that assume exclusive write access.

---

### 3.3 CLI Instances

Each CLI instance (Copilot, `doc_id_registry_cli.py`, etc.) runs **inside exactly one checkout** (control or worktree) and is tied to:

* `WT_ID` – worktree identity (`CONTROL`, `WT-DOCS`, `WT-MODULES`, …)
* `RUN_ID` – unique run ID (e.g. `DOCID-RUN-20251124-230000`)
* `WT_SCOPE` – declared path scope
* `LOG_ROOT` – directory for logs/telemetry for that run

**Example environment setup (worker):**

```bash
cd .worktrees/wt-docs

export WT_ID=WT-DOCS
export WT_SCOPE="docs"
export RUN_ID="DOCID-RUN-$(date +%Y%m%d-%H%M%S)"
export LOG_ROOT="../../.logs/${RUN_ID}_${WT_ID}"
mkdir -p "$LOG_ROOT"
```

**MUST**:

* Read and respect `WT_SCOPE` and `WT_ID`.
* Only operate on files within scope.
* Emit logs / telemetry in `$LOG_ROOT`.

---

### 3.4 ToolExecutionTemplate & WorkItem (conceptual)

To align with your UTE / Decision Elimination patterns, each CLI run is defined by:

* **ToolExecutionTemplate**: a named, reusable template describing:

  * `template_id`
  * `required_env` (WT_ID, WT_SCOPE)
  * `input_scope` (path globs)
  * `commands` (ordered shell/CLI invocations)
  * `expected_outputs` (delta files, reports)
  * `ground_truth_checks` (validation commands)

* **ToolWorkItem**: a concrete instance:

  * `work_item_id`
  * `template_id`
  * `scope_paths`
  * `run_id`
  * `status` (`pending|running|success|failed|retryable`)
  * `outputs` (paths to deltas, reports, logs)

Templates → WorkItems → Telemetry = decision elimination + traceability.

---

## 4. Multi-Instance Execution Pattern

### WT-EXEC-001 – Worktree & CLI Setup

**Goal**: Create N worker worktrees and bind one CLI instance per worktree, plus a control checkout.

**Steps**:

1. From control checkout:

   ```bash
   git checkout feat/big-change

   git worktree add .worktrees/wt-docs    feat/big-change
   git worktree add .worktrees/wt-modules feat/big-change
   git worktree add .worktrees/wt-tests   feat/big-change
   ```

2. For each worktree, set env vars and start the CLI:

   ```bash
   # Example: docs worktree
   cd .worktrees/wt-docs
   export WT_ID=WT-DOCS
   export WT_SCOPE="docs"
   export RUN_ID="DOCID-RUN-$(date +%Y%m%d-%H%M%S)"
   export LOG_ROOT="../../.logs/${RUN_ID}_${WT_ID}"
   mkdir -p "$LOG_ROOT"

   # Start AI CLI with explicit instructions:
   github-copilot-cli chat
   # or your CLI, with a system message:
   # - "You are operating in WT-DOCS"
   # - "Only touch files under docs/** and workstreams/plans/**"
   # - "Do not edit global registries; produce deltas and batch specs only"
   ```

3. Repeat for `WT-MODULES`, `WT-TESTS`, etc., with corresponding `WT_SCOPE`.

---

### WT-EXEC-002 – Worker Pattern (Delta-Producing Runs)

Workers apply this pattern **instead of** writing global state:

1. **Discover / triage** files inside scope.
2. **Apply template** (e.g. “_DOCID_BATCH_TEMPLATE_v1”, “LINT_FIX_TEMPLATE_v1”).
3. **Run CLI** in a mode that:

   * reads global state (if needed),
   * produces **deltas/patches**,
   * does **not** write global registries.

**Example (DOC_ID case):**

```bash
# In WT-DOCS
python scripts/doc_triage.py > "$LOG_ROOT/triage_${WT_ID}.txt"

# Update or create batch spec:
# doc_id/docid_batches/docid_batch_docs.yaml

# Dry-run
python doc_id_registry_cli.py \
  --registry ../../doc_id/DOC_ID_REGISTRY.yaml \
  batch-mint \
  --batch doc_id/docid_batches/docid_batch_docs.yaml \
  --mode dry-run \
  --dry-run-report "$LOG_ROOT/preview_${RUN_ID}_${WT_ID}.md"

# Deltas-only run (no registry writes)
DELTA_OUT="../../doc_id/docid_deltas/delta_${RUN_ID}_${WT_ID}.jsonl"

python doc_id_registry_cli.py \
  --registry ../../doc_id/DOC_ID_REGISTRY.yaml \
  batch-mint \
  --batch doc_id/docid_batches/docid_batch_docs.yaml \
  --mode deltas-only \
  --delta-out "$DELTA_OUT" \
  --no-registry
```

**MUST** (for all worker CLIs):

* Use **deltas-only** or equivalent mode where possible.
* Never write to shared registry files directly.
* Tag their outputs with `WT_ID` and `RUN_ID`.

---

### WT-EXEC-003 – Control Pattern (Merge & Verify)

**Goal**: Centralize merging and validation on the control checkout.

1. From control checkout, set a rollback tag:

   ```bash
   git tag -a "pre-batch-$(date +%Y%m%d-%H%M%S)" \
     -m "Checkpoint before multi-CLI batch"
   ```

2. Merge all worker outputs:

   * For DOC_ID example:

     ```bash
     python doc_id_registry_cli.py \
       --registry doc_id/DOC_ID_REGISTRY.yaml \
       merge-deltas \
       doc_id/docid_deltas/delta_* \
       --report doc_id/docid_reports/merge_DOCID_ALL_001.md
     ```

   * For other CLIs:

     * Apply patches in a deterministic order.
     * Regenerate derived files as needed.

3. Run ground truth checks:

   ```bash
   python doc_id_registry_cli.py \
     --registry doc_id/DOC_ID_REGISTRY.yaml \
     validate --duplicates \
     --report doc_id/docid_reports/final_validation_DOCID_ALL_001.md

   # Project tests
   pytest
   # or your standard test harness
   ```

4. If **anything fails**:

   ```bash
   git reset --hard pre-batch-YYYYMMDD-HHMMSS
   git worktree prune
   ```

5. If all passes:

   ```bash
   git add doc_id/DOC_ID_REGISTRY.yaml doc_id/docid_reports/*.md doc_id/docid_deltas/*.jsonl
   git commit -m "Apply DOC_ID batch from multi-worktree run"
   ```

**MUST**:

* Treat this pattern as the only way to update global registry-like state from multiple workers.
* Never bypass `merge-deltas` / analogous merge logic.

---

### WT-EXEC-004 – Self-Healing & Retry

To avoid the “rerun until it works and hope the registry survives” anti-pattern:

* **Worker failures**:

  * If a worker CLI crashes or produces an invalid delta, fix it **in that worktree only** and rerun the template.
  * Do **not** attempt to “fix” by editing registry directly.

* **Merge failures**:

  * If `merge-deltas` or tests fail in control:

    * Use the rollback tag.
    * Fix templates or batch specs as needed.
    * Re-run workers to produce clean deltas.

Because workers never touch global state directly, retries are safe and isolated.

---

## 5. Telemetry & Decision Elimination

Each CLI run (per worktree) SHOULD emit telemetry like:

```json
{
  "run_id": "DOCID-RUN-20251124-230000",
  "wt_id": "WT-DOCS",
  "template_id": "DOCID_BATCH_TEMPLATE_v1",
  "scope": ["docs/**", "workstreams/plans/**"],
  "start_time": "2025-11-24T23:00:00Z",
  "end_time": "2025-11-24T23:12:00Z",
  "status": "success",
  "files_processed": 42,
  "decisions_auto": 15,
  "decisions_manual": 0,
  "errors": [],
  "outputs": [
    "doc_id/docid_deltas/delta_DOCID-RUN-20251124-230000_WT-DOCS.jsonl",
    "doc_id/docid_reports/preview_DOCID-RUN-20251124-230000_WT-DOCS.md"
  ]
}
```

**MUST (for telemetry-aware CLIs):**

* Report at least:

  * `run_id`, `wt_id`, `template_id`, `status`, `errors`.
* Make it possible to correlate:

  * CLI runs → deltas → merges → registry state.

This ties directly into your **Decision Elimination** pattern: you can quantify how many decisions were automated and where manual intervention was still needed.

---

## 6. Anti-Patterns (Explicitly Forbidden)

To avoid repeating the DOC_ID project’s early issues:

* ❌ Running multiple CLI instances in different worktrees that **all write directly** to shared registry or state files.
* ❌ Retrying failed CLI runs that partially wrote to global state, without rollback or cleanup.
* ❌ Manual, unstructured edits to registries when a CLI already exists to manage them.
* ❌ Letting AI agents operate without `WT_ID`, `WT_SCOPE`, and clear instructions on what they are allowed to touch.

---

## 7. Success Criteria

This spec is considered **successfully adopted** when:

1. All multi-CLI / multi-worktree runs follow WT-EXEC-001…004.
2. Registry-like files (DOC_ID or others) are only updated via:

   * worker deltas,
   * control merges,
   * validation passes.
3. CLI crash / retry cycles no longer produce duplicate or inconsistent registry entries.
4. We can show, from telemetry, that:

   * decision points per run are decreasing,
   * time per file and failure rate are improving.

---



