Short version: you **have** defined most of the handoffs in pieces (phase specs, DAG snapshots, run DB tables, patch ledger, pattern automation tables), but you **haven’t yet captured them in one “Pipeline I/O Contract” doc**, and a couple of handoffs (esp. orchestrator ↔ error engine/pattern automation) are still only partially wired.

Let me walk the chain you asked about:

> planning → execution → error detection → saving

…and spell out what each stage *expects from the previous one*.

---

## 1. Planning → Execution: what the engine expects

### 1.1 Phase / Workstream specs → “what to do”

**Source of truth**

* **Universal Phase Specification** and “Document 1: The Universal Phase Spec mandatory structure” define the *shape* of every phase/workstream:
  `phase_id`, `workstream_id`, `objective`, `file_scope`, `dependencies`, `tools`, `acceptance`, etc.

**What planning emits**

For each phase/workstream you effectively have (conceptually as YAML/JSON):

```yaml
phase_id: "PH-01A"
workstream_id: "ws-pipeline-plus-1a-task-queue"
title: "Task Queue Management"
objective: "Implement task queue module with enqueue/dequeue, status, and tests."
phase_type: "implementation"
depends_on: ["PH-00"]
may_run_parallel_with: ["PH-01B"]

file_scope:
  create:
    - "core/state/task_queue.py"
    - "tests/test_task_queue.py"
  modify:
    - "core/state/__init__.py"
  read_only:
    - "config/router.config.yaml"
    - "schema/migrations/001_add_patches_table.sql"

tools:
  primary_language: "python"
  test_runners:
    - "python -m pytest -q"

acceptance:
  powershell: [...]
  python: [...]
```

**What the execution engine expects**

The **orchestrator** expects, per workstream:

* A **single entrypoint** command:
  `python scripts/run_workstream.py --ws-id <workstream_id>`
* A **validated workstream/phase document** that:

  * Has `file_scope` (create/modify/read_only)
  * Has `acceptance` commands and success patterns
  * Has `depends_on` / `may_run_parallel_with` to drive scheduling

In other words, **planning → execution** handoff at this level is:

> *“Here is a Phase/Workstream spec that tells you *what* to do, where you’re allowed to touch, and how we will prove you succeeded.”*

---

### 1.2 DAG snapshots → “in what order to do it”

**Source of truth**

The **Three-Tier DAG-as-Derived-State** plan defines the **DAG snapshot schemas** and how they are derived from module manifests + pattern registry.

Typical repo-wide snapshot:

```json
{
  "schema_version": "1.0.0",
  "generated_at": "...",
  "dag_type": "pipeline",
  "source_hash": "sha256:...",
  "nodes": ["PH-00", "PH-01A", "PH-01B", "PH-02"],
  "edges": {
    "PH-01A": ["PH-00"],
    "PH-01B": ["PH-00"],
    "PH-02":  ["PH-01A", "PH-01B"]
  },
  "topo_levels": [
    ["PH-00"],
    ["PH-01A", "PH-01B"],
    ["PH-02"]
  ],
  "critical_path": ["PH-00","PH-01A","PH-02"]
}
```

**What execution expects**

The **DAG builder / orchestrator** expects:

* A **Tier-1/Tier-3 snapshot** whose `nodes` map to known `phase_id` / `workstream_id`
* Graph integrity: no cycles, valid `topo_levels`, `edges` only between known nodes 

So the **handoff contract** here is:

> *Planning must produce DAG JSON that references only real phases/workstreams and passes the DAG schema; execution trusts this to drive run ordering and parallelism.*

---

## 2. Execution → Error Detection / Pattern Automation

Once the orchestrator starts running a phase/workstream, you’ve designed two main “observers”:

1. **Error engine / error plugins** (classic error handling)
2. **Pattern Automation system** (auto-learning from repeated executions)

### 2.1 Orchestrator → Pattern Automation hooks

**Source of truth**

The **Pattern Automation Activation – Phase Plan** defines:

* DB tables: `execution_logs`, `pattern_candidates`, `anti_patterns` 
* A hook class `PatternAutomationHooks` that the orchestrator calls on task start/complete. 

The **expected input from the orchestrator** on each task:

```python
task_spec = {
  "operation_kind": "EXEC-ATOMIC-CREATE",
  "file_scope": {...},      # from phase/workstream
  "tools_used": [...],
  "context": {...},         # WS, phase, module, etc.
}

result = {
  "success": True/False,
  "stdout": "...",
  "stderr": "...",
  "files_touched": [...],
  "patch_id": "PATCH-...",
}
```

The hooks then log into `execution_logs`:

````sql
INSERT INTO execution_logs (
  timestamp,
  operation_kind,
  file_types,
  tools_used,
  input_signature,
  output_signature,
  success,
  time_taken_seconds,
  context
) VALUES (...);
``` :contentReference[oaicite:6]{index=6}  

and may promote aggregates into `pattern_candidates` / `anti_patterns`.

**So the contract is:**

> Execution must provide enough structured data (operation_kind, file types, signatures, success, timing, context) so the detectors can cluster similar executions and learn new patterns or anti-patterns.

Right now this is **specified but not fully implemented**: the plan explicitly lists “Orchestrator integration hooks” and DB tables as the missing 30%. :contentReference[oaicite:7]{index=7}  

---

### 2.2 Orchestrator → Error Engine / `modules/error_shared`

Separately, the **5-Phase Completion Plan** + `error-shared` module work define the **shared error utilities** used by error plugins:

- `modules/error_shared` exposes things like:
  - `types`, `time`, `hashing`, `jsonl_manager`, `env`, `security`   
- The error plugins import those symbols via the new module path.

The implicit contract:

- **Execution / error engine** can rely on:
  - Stable imports like `from modules.error_shared import jsonl_manager, security`
  - Utilities to hash executions, manage JSONL logs, and enforce basic security/env checks
- In return, the **error plugins** expect the orchestrator to surface failures with at least:
  - An error type / code
  - The affected files / workstream
  - Enough context to write a structured log via `jsonl_manager`

This is mostly **implementation-level**, but you do not yet have a small formal `ErrorEvent` schema doc tying this together.

---

## 3. Execution → Saving: DB, ledgers, and state

You’ve actually defined this fairly clearly in the **UET Engine Replacement** plan + Universal Phase Spec.

### 3.1 Run / Step / Event tables

**Source of truth**

UET engine replacement introduces:

- `uet_runs` – one per run of a phase/workstream
- `step_attempts` – individual task/step attempts within a run
- `run_events` – timeline of events
- `patch_ledger` – all patch artifacts   

The orchestrator is expected to:

1. **Create a run row** when starting a phase/workstream.
2. **Create step_attempt rows** for each execution step (tool call / pattern execution).
3. **Record run_events** for state transitions (queued → running → succeeded/failed, patch captured, tests run, etc.).
4. **Insert into patch_ledger** whenever a code patch is generated.

So the **execution → saving** contract here is:

> The engine must *never* mark a phase “done” without corresponding `uet_runs`, `step_attempts`, `run_events`, and `patch_ledger` records that match the actual CLI-observed reality.

### 3.2 Patch artifacts & audit logs

**Source of truth**

The **Universal Phase Spec** requires each phase to produce:

- A `.ledger/patches/{workstream_id}-{run_id}.patch` file
- Audit entries in `.runs/audit.jsonl` with `event_type`, `task_id/ws_id`, tool, and outcome :contentReference[oaicite:10]{index=10}  

So for each successful phase:

- Execution writes **patch file(s)** + **DB ledger row(s)**.
- Execution writes **audit events** to `.runs/audit.jsonl`.

This matches the DB schema above: the file artifacts and DB rows are two synchronized views of the same “what happened” story.

---

## 4. Planning ← Saving / Patterns: closing the loop

The **Unified Pattern Implementation** and **Template Implementation** plans describe how all this saved data feeds back into **future planning**:   

- The **pattern system** has:
  - Specs + schemas + executors + tests under `patterns/`
  - A `PATTERN_INDEX.yaml` registry of all known patterns :contentReference[oaicite:12]{index=12}  
- The **template system** has:
  - Phase templates, verification templates, decision templates, self-healing templates under `templates/` :contentReference[oaicite:13]{index=13}  

The idea is:

1. Pattern Automation promotes recurring successful `execution_logs` clusters to `pattern_candidates`.
2. Humans/AI approve them into `patterns/registry/PATTERN_INDEX.yaml`.
3. Future **planning** doesn’t invent bespoke plans; it instantiates:
   - Phase templates (`phase_templates/*.template.yaml`)
   - Execution patterns (`execution_patterns/*.pattern.yaml`)
   - Verification templates (`verification_templates/*.verify.yaml`)

So long-term, the **data handoff goes full circle**:

> Saved execution telemetry → patterns/atoms → templates → new phase/workstream plans → DAG → execution → telemetry…

---

## 5. So… have you actually *defined* these handoffs?

### 5.1 Explicitly defined

You **do** have explicit contracts for:

- **Phase / Workstream spec** structure (planning → execution)  
  – Universal Phase Spec & Document 1.   
- **DAG snapshot** structure (planning → orchestrator schedule)  
  – `dag_snapshot.schema.json` & `module_tasks.schema.json`. :contentReference[oaicite:15]{index=15}  
- **Pattern + template schemas** (execution uses these as pre-compiled behavior)  
  – Pattern & template frameworks.   
- **Run / Step / Event / Patch DB tables** (execution → saving)  
  – UET engine DB section.   
- **Patch & audit artifacts on disk** (execution → .ledger/.runs)  
  – Universal Phase Spec output/artifact rules. :contentReference[oaicite:18]{index=18}  
- **Pattern automation DB tables** (execution → pattern learning)  
  – `execution_logs`, `pattern_candidates`, `anti_patterns`. :contentReference[oaicite:19]{index=19}  

### 5.2 Partially defined / implicit

You **partially** have, but have *not* captured as a single schema:

- The **“ExecutionRequest” / task envelope** that the orchestrator passes into pattern executors and hooks (you refer to `operation_kind`, `file_scope`, `constraints`, `tools`, etc., but there’s no single `ExecutionRequest.schema.json` yet).
- The **“ErrorEvent” / plugin payload**, i.e., a tiny contract for how an execution failure is described and handed over to error plugins.
- A **single doc that enumerates all four I/O contracts end-to-end**:

  1. PhaseSpec/WorkstreamSpec (planning → engine)  
  2. DagSnapshot (planning → scheduler)  
  3. Run/StepAttempt/Patch/Audit (engine → persistence)  
  4. ExecutionLog/PatternCandidate/AntiPattern (engine → pattern automation)

### 5.3 Implementation status

- The **docs** describe the contracts fairly well.
- The **engine wiring** is still WIP in exactly the places you’d expect:
  - Pattern automation plan says “Missing DB tables + orchestrator hooks” (today they’re specs, not live code). :contentReference[oaicite:20]{index=20}  
  - 5-Phase Completion Plan notes “Pattern automation infrastructure 100% complete; orchestrator integration 0% – hooks never called.” :contentReference[oaicite:21]{index=21}  

So the reality is:

> The handoff contracts are *mostly defined on paper*, but the orchestrator isn’t yet consistently **emitting** all the expected records (DB + JSONL + pattern logs), and you’re missing one unifying “PIPELINE_DATA_HANDOFF_SPEC” doc.

---

## 6. If you want a next concrete step

If you’d like, I can next:

- Draft `UET_PIPELINE_IO_CONTRACTS.md` that:

  - Defines **four JSON/YAML schemas**:
    - `PhaseSpecV1`
    - `DagSnapshotV1`
    - `ExecutionRequestV1` + `RunRecordV1` / `StepAttemptV1`
    - `ErrorEventV1` + `ExecutionLogV1` / `PatternCandidateV1`
  - And maps each field back to the existing docs so your CLIs can enforce “only use these shapes” across modules.

But to answer your question directly: **yes, the shapes/expectations exist; no, they’re not yet centralized into one contract, and the orchestrator → pattern/error side is still partially unimplemented.**
````
