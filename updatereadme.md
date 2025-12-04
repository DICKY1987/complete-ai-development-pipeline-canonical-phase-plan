Here is a **structured technical review of all Phase 0–6 README files**, focusing on **completeness, architectural soundness, implementation risk, and system readiness**. I also include **cross-phase dependency risks and concrete recommendations**.

---

# ✅ Overall System Health Summary (From README Analysis)

| Phase   | Name             | Status     | Real Readiness              | Key Risk  |
| ------- | ---------------- | ---------- | --------------------------- | --------- |
| Phase 0 | Bootstrap        | ✅ Complete | **Production-Ready**        | Low       |
| Phase 1 | Planning         | ⚠️ 40%     | **Architectural Risk**      | High      |
| Phase 2 | Request Building | ✅ Complete | **Production-Ready**        | Low       |
| Phase 3 | Scheduling       | ✅ Complete | **Production-Ready**        | Low       |
| Phase 4 | Routing          | ⚠️ 60%     | **Operational Risk**        | Medium    |
| Phase 5 | Execution        | ⚠️ 50%     | **Critical Execution Risk** | Very High |
| Phase 6 | Error Recovery   | ⚠️ 60%     | **Recovery Risk**           | Medium    |

Your system is **very strong on orchestration, state, schemas, and resilience**, but **execution + planning are currently the weakest links**. This creates a **“beautiful control plane with a fragile worker plane”** condition.

---

# Phase-by-Phase Review

---

## ✅ Phase 0 – Bootstrap & Initialization



**Architectural Quality:** ★★★★★
**Operational Risk:** Low
**Testing:** 8 Passing Tests (Good for infra layer)

### Strengths

* Clean **multi-step bootstrap orchestration**
* **Strong schema-first design** (17 schemas)
* Deterministic:

  * Repo detection
  * Profile selection
  * Artifact generation
* Good separation:

  * Discovery
  * Validation
  * Generation

### Risks

* None critical
* Only gap: no explicit **version migration handling for schemas**

✅ **This phase is production-ready.**

---

## ⚠️ Phase 1 – Planning & Spec Alignment



**Architectural Quality:** ★★★★☆
**Operational Risk:** **High**
**Testing:** 0 tests
**Planner:** ⚠️ **STUB**

### Strengths

* Excellent **spec coverage** (10 core specs)
* Strong conceptual pipeline:

  * OpenSpec → Workstreams → CCPM
* Archival layer implemented ✅

### Critical Gaps

1. **planner.py is a STUB**
2. **ccpm_integration.py is partial**
3. **0 automated tests**
4. No validation loop from:

   ```
   execution results → spec drift → planning updates
   ```

### This Causes:

* Your entire **downstream pipeline depends on a weak planning layer**
* Workstreams may be **logically valid but operationally unsound**

⚠️ **This is your single most important architectural risk area.**

---

## ✅ Phase 2 – Request Building & Run Creation



**Architectural Quality:** ★★★★★
**Operational Risk:** Low
**Testing:** Implied via DB + validation tests

### Strengths

* Excellent **schema discipline**
* Strong **state persistence**
* Proper **audit logging**
* Clean **separation of concerns**

### Minor Gaps

* No explicit:

  * Retry on partial DB write failure
  * Idempotency guards for duplicate ExecutionRequests

✅ **Production-ready with minor hardening recommended.**

---

## ✅ Phase 3 – Scheduling & Task Graph



**Architectural Quality:** ★★★★★
**Operational Risk:** Low
**Testing:** ~92 tests ✅

### Strengths

* Proper DAG construction
* Cycle detection
* Topological sorting
* Strong lifecycle state machine
* Parallel vs sequential resolution handled

### Minor Gap

* No mention of **dynamic DAG mutation** during runtime (hot task injection)

✅ **This is one of your strongest technical layers.**

---

## ⚠️ Phase 4 – Tool Routing & Adapter Selection



**Architectural Quality:** ★★★★☆
**Operational Risk:** Medium
**Testing:** ~27 tests

### Strengths

* Excellent abstraction:

  * Adapter base
  * Registry
  * Tool capability matching
* Multi-instance Aider support
* AIM capability bridge is well designed

### Missing Critical Components

* ❌ ToolProcessPool
* ❌ ClusterManager
* ❌ Full Aider adapter
* ❌ Codex adapter

### Risk

You currently have:

```
Logical routing without guaranteed physical execution capacity
```

⚠️ **This phase blocks reliable horizontal scaling.**

---

## ⚠️ Phase 5 – Execution & Validation



**Architectural Quality:** ★★★★☆
**Operational Risk:** **Very High**
**Executor:** ❌ **STUB**

### Strengths

* Strong:

  * Resilient execution wrapper ✅
  * Circuit breaker ✅
  * Retry logic ✅
  * Monitoring ✅
  * Patch tracking ✅
* Acceptance testing framework exists ✅

### Critical Failure Point

* `executor.py` is a **STUB**

This means:

* Your entire system **can plan, schedule, route, and validate — but cannot reliably execute tasks**

This is a **hard system stop** for:

* Fully autonomous runs
* Headless execution
* Production deployment

🚨 **This is the most dangerous technical gap in the entire platform.**

---

## ⚠️ Phase 6 – Error Analysis, Auto-Fix & Escalation



**Architectural Quality:** ★★★★☆
**Operational Risk:** Medium
**Engine:** ⚠️ SHIM

### Strengths

* Excellent plugin ecosystem (21 plugins)
* Solid:

  * Circuit breaker
  * Retry
  * Recovery pipeline
* Strong error lifecycle design

### Weakness

* `error_engine.py` is a **framework shim**
* You depend on upstream UET behavior for:

  * Error classification
  * Patch scoring
  * Retry routing

⚠️ **Your recovery is only as strong as an external framework dependency.**

---

# Cross-Phase Dependency Risks (Critical)

Here is your **actual runtime dependency chain**:

```
Phase 1 (Planning) ──▶ Phase 2 (Request) ──▶ Phase 3 (Scheduling)
                            │
                            ▼
                     Phase 4 (Routing)
                            │
                            ▼
                     Phase 5 (Execution)
                            │
                            ▼
                     Phase 6 (Error Recovery)
```

### Current Structural Failures:

1. **Phase 1 produces weak workstreams**
2. **Phase 5 cannot execute tasks**
3. **Phase 4 cannot guarantee tool availability**
4. **Phase 6 cannot fully self-heal without external UET**

This creates a **false sense of readiness**:

> You can observe, route, validate, and audit — but execution and self-healing are not autonomous yet.

---

# Immediate Priority Fix Order (Engineering Roadmap)

### 🚨 Tier 1 – Mandatory Before Production

1. **Implement `core/engine/executor.py` (Phase 5)**
2. **Implement `core/planning/planner.py` (Phase 1)**
3. **Finalize ToolProcessPool (Phase 4)**

### ⚠️ Tier 2 – Reliability Hardening

4. Replace `error_engine.py` SHIM with native engine
5. Add idempotent request guards (Phase 2)
6. Add dynamic DAG mutation support (Phase 3)

### ✅ Tier 3 – Scalability & Governance

7. ClusterManager
8. Adapter health scoring
9. Failure analytics aggregation

---

# Architectural Integrity Score

| Category              | Score      |
| --------------------- | ---------- |
| Schema Discipline     | 10 / 10    |
| State Management      | 9.5 / 10   |
| DAG Scheduling        | 10 / 10    |
| Tool Abstraction      | 8 / 10     |
| Execution Reliability | **3 / 10** |
| Self-Healing          | 7 / 10     |
| End-to-End Autonomy   | **6 / 10** |

---

# Key Strategic Conclusion

You have successfully built an **enterprise-grade AI orchestration control plane**, but the **execution plane is still partially theoretical**.

Your system today is best described as:

> **“A production-quality autonomous orchestration kernel with a non-production execution backend.”**

Once **Phase 1 Planner + Phase 5 Executor** are implemented, this platform becomes **genuinely autonomous and production-deployable.**

---
Great question — and you’re exactly right to focus on this.
Your current READMEs are **excellent for humans**, but to be **maximally useful for AI agents**, they need a few additional *machine-actionable layers*.

Below is a **precise gap analysis + an AI-optimized README augmentation spec** you can standardize across all phases.

---

# 1. What Your Current READMEs Already Do Well for AI

You already provide:

✅ Phase identity and purpose
✅ High-level responsibilities
✅ Key folders and major modules
✅ Status and partial completeness
✅ Some dependency hints (e.g., routed to `core/engine/`, `core/state/`)

This gives AI **context** — but not yet **operational intelligence**.

---

# 2. Critical Information AI Still Lacks

Here are the **missing data classes** that prevent full autonomous understanding and tool orchestration.

---

## A. ❗ Explicit System Graph Position

AI needs to know *exactly* where this phase sits in the execution chain.

### Missing Today

* No standardized:

  * `upstream_phases`
  * `downstream_phases`
  * `blocking_dependencies`
  * `soft_dependencies`

### Why This Matters

Without this, an AI cannot:

* Safely reorder work
* Detect dead-phase execution
* Enforce gating rules

### Add This Block to Every README

```
## System Position

upstream_phases:
  - phase0_bootstrap
  - phase1_planning

downstream_phases:
  - phase3_scheduling

hard_blockers:
  - planner.py must emit valid workstream JSON

soft_dependencies:
  - CCPM sync
```

---

## B. ❗ Machine-Readable Entry & Exit Contracts

You describe behavior in prose, but AI needs:

* Input contract (what exactly must exist to enter this phase)
* Output contract (what artifacts must be produced to advance)

### Missing Today

* No explicit:

  * required input files
  * required DB tables
  * required state flags
  * required schema versions

### Add This Block

```
## Phase Contracts

entry_requirements:
  required_files:
    - PROJECT_PROFILE.yaml
    - workstreams/*.json
  required_db_tables:
    - runs
    - workstreams
  required_state_flags:
    - BOOTSTRAP_OK
    - PLANNING_OK

exit_artifacts:
  produced_files:
    - .state/orchestration.db
    - .state/task_queue.json
  updated_db_tables:
    - runs
    - tasks
  emitted_events:
    - RUN_CREATED
    - TASKS_SCHEDULED
```

---

## C. ❗ Canonical Source-of-Truth Declarations

Right now AI must *infer*:

* Which file is authoritative
* Which files are derived
* Which files must never be edited directly

This is extremely dangerous for autonomous systems.

### Add This Block

```
## Source of Truth

authoritative_sources:
  - schema/execution_request.v1.json
  - schema/run_record.v1.json

derived_artifacts:
  - .state/orchestration.db
  - .state/transitions.jsonl

do_not_edit_directly:
  - .state/**
  - .ledger/framework.db
```

---

## D. ❗ Negative Scope (What This Phase Does NOT Do)

You describe what each phase *does*, but not what it *must never do*.

AI agents routinely:

* Overreach scope
* Duplicate logic
* Mutate foreign phase state

### Add This Block

```
## Explicit Non-Responsibilities

this_phase_does_not:
  - execute tasks
  - apply code patches
  - modify DAG topology after scheduling
  - classify runtime errors
```

---

## E. ❗ Runtime Invocation & Control Surface

AI needs to know:

* How is this phase invoked?
* Is it auto-triggered?
* Is it manual?
* Is it resumable?

### Add This Block

```
## Invocation & Control

invocation_mode:
  - automatic_on_previous_phase_success

entrypoints:
  cli:
    - orchestrator run --phase phase3
  python:
    - core.engine.scheduler.run()

resumable: true
idempotent: true
retry_safe: true
```

---

## F. ❗ Observability & Telemetry Surface

You *log*, but you don’t declare:

* Which metrics exist
* Where logs go
* What errors look like structurally

### Add This Block

```
## Observability

log_streams:
  - logs/scheduler.jsonl
  - logs/dag_builder.jsonl

metrics:
  - dag_nodes_total
  - dag_cycles_detected
  - queue_depth
  - parallel_tasks_active

health_checks:
  - scheduler_heartbeat
  - queue_integrity_check
```

---

## G. ❗ AI-Specific Operational Guidance

Right now there is:

* No explicit guidance on:

  * When AI may modify code in this phase
  * When it must escalate
  * When to refuse execution

### Add This Block

```
## AI Operational Rules

ai_may_modify:
  - core/engine/scheduler.py
  - core/state/task_queue.py

ai_must_not_modify:
  - schema/**
  - .ledger/**
  - .state/**

ai_escalation_triggers:
  - DAG cycle detected
  - schema validation failure
  - DB write failure

ai_safe_mode_conditions:
  - missing entry contract artifacts
  - conflicting workstream IDs
```

---

## H. ❗ Formal Maturity & Risk Model

You already have "Status", but AI needs **risk-weighted readiness**.

### Add This Block

```
## Readiness Model

maturity_level: OPERATIONAL_BETA

risk_profile:
  execution_risk: LOW
  data_loss_risk: LOW
  deadlock_risk: MEDIUM
  external_dependency_risk: LOW

production_gate: ALLOWED_WITH_MONITORING
```

---

# 3. The Canonical AI-Optimized README Template

Here is the **exact unified template** that would make your system fully AI-parsable:

```
# Phase N – Name

## Purpose
## System Position
## Phase Contracts
## Phase Contents
## Current Components
## Main Operations
## Source of Truth
## Explicit Non-Responsibilities
## Invocation & Control
## Observability
## AI Operational Rules
## Test Coverage
## Known Failure Modes
## Readiness Model
## Status
```

If you normalize all READMEs to this, then:

✅ Any agent can locate authority instantly
✅ Any agent can verify entry/exit safety
✅ Any agent can know what it must *not* touch
✅ Your orchestrator can infer full lifecycle rules from docs alone
✅ You eliminate “hallucinated” system behavior

---

# 4. Key Strategic Insight

Right now, your READMEs explain **what the phase is**.

To be AI-complete, they must also define:

* **When it is allowed to run**
* **What it is allowed to touch**
* **What it must never touch**
* **What proves that it is done**
* **What breaks safety if violated**

Once those blocks exist, your documentation becomes:

> **Executable system governance**, not just reference documentation.

---

Perfect — here are **all four deliverables**, fully aligned to your system architecture and PAT-CHECK enforcement goals.

---

# ✅ 1. **Patched AI-Optimized README (Reference Implementation)**

**Target Phase:** Phase 3 – Scheduling & Task Graph
This is your **gold standard** that all other phases should be normalized to.

```markdown
# Phase 3 – Scheduling & Task Graph

## Purpose
Load workstreams, construct the execution DAG, resolve dependencies, and populate the execution task queue.

## System Position
upstream_phases:
  - phase2_request_building
downstream_phases:
  - phase4_routing
hard_blockers:
  - Valid ExecutionRequest must exist
  - Valid workstream JSON must exist
soft_dependencies:
  - CCPM sync completion

## Phase Contracts
entry_requirements:
  required_files:
    - workstreams/*.json
    - PROJECT_PROFILE.yaml
  required_db_tables:
    - runs
    - workstreams
  required_state_flags:
    - REQUEST_VALIDATED

exit_artifacts:
  produced_files:
    - .state/task_queue.json
  updated_db_tables:
    - tasks
  emitted_events:
    - DAG_BUILT
    - TASKS_QUEUED

## Phase Contents
Located in: `phase3_scheduling/`
- README.md

## Current Components
- `core/engine/scheduler.py` – DAG-based scheduler
- `core/engine/dag_builder.py` – DAG construction
- `core/engine/state_machine.py` – Task lifecycle
- `core/state/dag_utils.py` – Cycle detection, topo sort
- `core/state/task_queue.py` – FIFO queue

## Main Operations
- Load workstreams + dependencies
- Build DAG (spec + author-defined)
- Detect cycles
- Determine parallel vs sequential execution
- Populate task queue with PENDING tasks

## Source of Truth
authoritative_sources:
  - core/engine/dag_builder.py
  - schema/workstream_spec.v1.json
derived_artifacts:
  - .state/task_queue.json
  - .state/transitions.jsonl
do_not_edit_directly:
  - .state/**
  - .ledger/**

## Explicit Non-Responsibilities
this_phase_does_not:
  - execute tasks
  - select tools
  - apply patches
  - classify runtime errors

## Invocation & Control
invocation_mode:
  - automatic_on_phase2_success
entrypoints:
  cli:
    - orchestrator run --phase phase3
  python:
    - core.engine.scheduler.run()
resumable: true
idempotent: true
retry_safe: true

## Observability
log_streams:
  - logs/scheduler.jsonl
metrics:
  - dag_nodes_total
  - dag_cycles_detected
  - queue_depth
health_checks:
  - scheduler_heartbeat
  - queue_integrity_check

## AI Operational Rules
ai_may_modify:
  - core/engine/scheduler.py
  - core/state/task_queue.py
ai_must_not_modify:
  - schema/**
  - .state/**
  - .ledger/**
ai_escalation_triggers:
  - DAG cycle detected
  - DB insert failure
  - missing workstream spec
ai_safe_mode_conditions:
  - missing ExecutionRequest
  - invalid schema validation

## Test Coverage
~92 tests for engine components

## Known Failure Modes
- DAG cycle → execution deadlock
- Missing dependency → task starvation
- Corrupt queue file → run abort

## Readiness Model
maturity_level: PRODUCTION_READY
risk_profile:
  execution_risk: LOW
  data_loss_risk: LOW
  deadlock_risk: MEDIUM
production_gate: ALLOWED

## Status
✅ Complete (100%)
```

This README is now:

* **Machine-parsable**
* **Contract-enforced**
* **AI-safe**
* **Orchestrator-executable**

---

# ✅ 2. **Repo-Wide Auto-Normalization Diff Plan**

This is the **agentic patch strategy** to convert every phase README to the canonical template.

### Normalization Passes

### PASS 1 — Header & Structural Alignment

Insert missing standardized headings in this order:

```
Purpose
System Position
Phase Contracts
Phase Contents
Current Components
Main Operations
Source of Truth
Explicit Non-Responsibilities
Invocation & Control
Observability
AI Operational Rules
Test Coverage
Known Failure Modes
Readiness Model
Status
```

---

### PASS 2 — System Graph Injection

Auto-infer:

* upstream_phases
* downstream_phases

From:

* orchestrator DAG
* plan execution order

---

### PASS 3 — Contract Synthesis

Generate:

* entry_requirements
* exit_artifacts

By parsing:

* schema/**
* db initialization code
* .state writes

---

### PASS 4 — Source of Truth Classification

Heuristics:

* `schema/**` → authoritative
* `core/**` → authoritative
* `.state/**`, `.ledger/**` → derived + immutable

---

### PASS 5 — AI Governance Injection

Auto-insert:

* ai_may_modify
* ai_must_not_modify
* ai_escalation_triggers
* ai_safe_mode_conditions

From:

* adapter registry
* error pipeline
* safe-merge rules

---

### PASS 6 — Readiness & Risk Scoring

Map:

* % implemented
* presence of stubs
* test coverage

To:

* maturity_level
* production_gate

---

### Output Guarantee

After this pipeline:

* All READMEs become **PAT-CHECK-enforceable**
* All phases gain **formal AI execution safety**
* Orchestrator can treat docs as **runtime governance**

---

# ✅ 3. **JSON Schema for README Validation (PAT-CHECK-001 Compatible)**

This is the **formal enforcement layer**.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AI Optimized Phase README Schema",
  "type": "object",
  "required": [
    "Purpose",
    "System Position",
    "Phase Contracts",
    "Current Components",
    "Main Operations",
    "Source of Truth",
    "Explicit Non-Responsibilities",
    "Invocation & Control",
    "Observability",
    "AI Operational Rules",
    "Test Coverage",
    "Known Failure Modes",
    "Readiness Model",
    "Status"
  ],
  "properties": {
    "System Position": {
      "type": "object",
      "required": ["upstream_phases", "downstream_phases"]
    },
    "Phase Contracts": {
      "type": "object",
      "required": ["entry_requirements", "exit_artifacts"]
    },
    "Invocation & Control": {
      "type": "object",
      "required": ["resumable", "idempotent"]
    },
    "AI Operational Rules": {
      "type": "object",
      "required": [
        "ai_may_modify",
        "ai_must_not_modify",
        "ai_escalation_triggers"
      ]
    },
    "Readiness Model": {
      "type": "object",
      "required": ["maturity_level", "production_gate"]
    }
  }
}
```

PAT-CHECK can now:

* Reject incomplete READMEs
* Block unsafe autonomy
* Prevent undocumented execution paths

---

# ✅ 4. **AI Rulebook for Documentation-Based Orchestration Safety**

This is the **governance doctrine your agents must obey.**

---

## AI ORCHESTRATION RULEBOOK (DOC-DRIVEN)

### RULE 1 — **No Phase May Execute Without Valid Entry Contracts**

If any required file, table, or flag is missing → **ABORT IMMEDIATELY**

---

### RULE 2 — **Authority Is Defined by “Source of Truth”**

AI **MUST NOT**:

* Modify derived artifacts
* Modify schema without escalation

---

### RULE 3 — **Negative Scope Is Binding**

If a phase says:

```
this_phase_does_not:
  - execute tasks
```

Then any attempt to execute tasks in that phase = **HARD VIOLATION**

---

### RULE 4 — **AI May Only Modify Files Explicitly Whitelisted**

Files not in `ai_may_modify` are:

* Read-only
* Escalation-required

---

### RULE 5 — **Observability Is a Hard Safety Requirement**

If declared:

* log_stream is missing
* metric emission fails
  → **ENTER SAFE MODE**

---

### RULE 6 — **Readiness Model Gates Autonomy**

Mapping:

* `DESIGN_ONLY` → No execution
* `OPERATIONAL_BETA` → Human approval required
* `PRODUCTION_READY` → Full autonomy allowed

---

### RULE 7 — **Status Overrides Optimism**

If:

```
Status = ⚠️ Partial
```

Then:

* Auto-execution is **disallowed**
* Only inspection, patching, or simulation permitted

---

### RULE 8 — **Cross-Phase Mutation Is Forbidden**

No phase may:

* Write foreign phase state
* Modify another phase’s authoritative files

Violations → **Safety violation + escalation**

---

### RULE 9 — **Documentation Is Runtime Law**

If code and README disagree:

* README controls governance
* Code is treated as suspect

---

### RULE 10 — **No Undocumented Execution Paths**

If an action is not described in:

* Main Operations
* Invocation & Control
* Phase Contracts

Then AI **must refuse to perform it**.

---

# ✅ Final Strategic Result

You now have:

* ✅ A **machine-authoritative README reference**
* ✅ A **repo-wide normalization pipeline**
* ✅ A **formal JSON validation schema**
* ✅ A **governance rulebook that prevents AI hallucination & scope creep**

This elevates your documentation from:

> “Reference material”
> to:
> **“Executable system governance and safety law.”**

---

# ✅ Next Optional Enhancements (If You Want)

I can also generate:

* 🔁 A **README auto-patcher script (Python or PowerShell)**
* 🧠 A **PAT-CHECK-README-001 enforcement tool**
* 🗺 A **graph generator that builds the Phase DAG directly from READMEs**
* 🧬 A **Doc-to-Plan synthesizer that creates master_plan.json from phase READMEs**

---

Nice, let’s make your auto-patcher real. Below is a **Python script** that:

* Scans your repo for `README.md` files under `phase*/` folders
* Normalizes them into the **AI-optimized canonical template**
* Preserves existing content where possible
* Adds **stub sections** (with clear TODO markers) for anything missing
* Creates a `README.md.bak` backup before rewriting

You can extend it later to auto-fill more details phase-by-phase, but this gets you a consistent, machine-parseable structure everywhere.

---

## `normalize_phase_readmes.py`

```python
#!/usr/bin/env python
"""
Normalize phase README files to a canonical AI-optimized structure.

Usage:
    python normalize_phase_readmes.py --write
    python normalize_phase_readmes.py --dry-run

Behavior:
- Finds README.md files under directories whose name starts with "phase".
- Parses existing sections.
- Converts inline "**Purpose**: ..." into a "## Purpose" section.
- Rewrites each README with a canonical ordered section list.
- Preserves existing section content when possible.
- Adds TODO placeholders for missing sections.
- Creates README.md.bak before modifying (when --write is used).
"""

import argparse
import textwrap
from pathlib import Path
from typing import Dict, List, Tuple


CANONICAL_SECTION_ORDER: List[str] = [
    "Purpose",
    "System Position",
    "Phase Contracts",
    "Phase Contents",
    "Current Components",
    "Main Operations",
    "Source of Truth",
    "Explicit Non-Responsibilities",
    "Invocation & Control",
    "Observability",
    "AI Operational Rules",
    "Test Coverage",
    "Known Failure Modes",
    "Readiness Model",
    "Status",
]

# Simple default placeholders for new sections.
PLACEHOLDER_TEXT: Dict[str, str] = {
    "System Position": textwrap.dedent(
        """\
        upstream_phases:
          - [TODO: fill with upstream phase IDs, e.g. phase2_request_building]
        downstream_phases:
          - [TODO: fill with downstream phase IDs, e.g. phase4_routing]
        hard_blockers:
          - [TODO: list conditions that must be true before this phase can run]
        soft_dependencies:
          - [TODO: non-blocking dependencies or external syncs]
        """
    ),
    "Phase Contracts": textwrap.dedent(
        """\
        entry_requirements:
          required_files:
            - [TODO: list required input files]
          required_db_tables:
            - [TODO: list required DB tables, if any]
          required_state_flags:
            - [TODO: list required state flags / readiness signals]
        exit_artifacts:
          produced_files:
            - [TODO: list files produced by this phase]
          updated_db_tables:
            - [TODO: list DB tables updated by this phase]
          emitted_events:
            - [TODO: list events emitted to the orchestration/event bus]
        """
    ),
    "Phase Contents": "[TODO: describe folder layout and key subdirectories]\n",
    "Source of Truth": textwrap.dedent(
        """\
        authoritative_sources:
          - [TODO: list authoritative specs/code for this phase]
        derived_artifacts:
          - [TODO: list generated/derived files]
        do_not_edit_directly:
          - .state/**
          - .ledger/**
        """
    ),
    "Explicit Non-Responsibilities": textwrap.dedent(
        """\
        this_phase_does_not:
          - [TODO: list responsibilities explicitly out of scope for this phase]
        """
    ),
    "Invocation & Control": textwrap.dedent(
        """\
        invocation_mode:
          - [TODO: e.g. automatic_on_previous_phase_success | manual]
        entrypoints:
          cli:
            - [TODO: CLI commands to invoke this phase]
          python:
            - [TODO: Python entrypoints to invoke this phase]
        resumable: [TODO: true|false]
        idempotent: [TODO: true|false]
        retry_safe: [TODO: true|false]
        """
    ),
    "Observability": textwrap.dedent(
        """\
        log_streams:
          - [TODO: list log files/streams for this phase]
        metrics:
          - [TODO: list metrics exposed by this phase]
        health_checks:
          - [TODO: list health/diagnostic checks for this phase]
        """
    ),
    "AI Operational Rules": textwrap.dedent(
        """\
        ai_may_modify:
          - [TODO: list files/directories AI may modify in this phase]
        ai_must_not_modify:
          - schema/**
          - .state/**
          - .ledger/**
        ai_escalation_triggers:
          - [TODO: conditions that require human review or escalation]
        ai_safe_mode_conditions:
          - [TODO: conditions under which execution should be downgraded to safe mode]
        """
    ),
    "Test Coverage": "[TODO: summarize test coverage numbers, files, and gaps]\n",
    "Known Failure Modes": "[TODO: list typical failure modes and their impact]\n",
    "Readiness Model": textwrap.dedent(
        """\
        maturity_level: [TODO: DESIGN_ONLY | OPERATIONAL_BETA | PRODUCTION_READY]
        risk_profile:
          execution_risk: [TODO: LOW|MEDIUM|HIGH]
          data_loss_risk: [TODO: LOW|MEDIUM|HIGH]
          deadlock_risk: [TODO: LOW|MEDIUM|HIGH]
          external_dependency_risk: [TODO: LOW|MEDIUM|HIGH]
        production_gate: [TODO: DISALLOWED | ALLOWED_WITH_MONITORING | ALLOWED]
        """
    ),
    "Status": "[TODO: e.g. ✅ Complete (100%) or ⚠️ Partial (60%)]\n",
}


def find_phase_readmes(root: Path) -> List[Path]:
    """
    Find README.md files under directories whose name starts with 'phase'.
    """
    candidates: List[Path] = []
    for path in root.rglob("README.md"):
        # parent dir name should start with "phase"
        if path.parent.name.lower().startswith("phase"):
            candidates.append(path)
    return sorted(candidates)


def parse_readme_sections(content: str) -> Tuple[str, Dict[str, str], str]:
    """
    Parse a README.md into:
    - title: first level-1 heading line (e.g. "# Phase 3 – ...")
    - sections: mapping from section name (without "## ") to body text
    - leading_text: any text before the first "##" heading (used to extract Purpose)
    """
    lines = content.splitlines()
    title = ""
    sections: Dict[str, str] = {}
    leading_lines: List[str] = []

    current_section_name = None
    current_buf: List[str] = []

    # First pass: identify title and split by ## headings
    for i, line in enumerate(lines):
        if i == 0 and line.startswith("# "):
            title = line.strip()
            continue

        if line.startswith("## "):
            # Flush previous section
            if current_section_name is None:
                # This is the first section; everything seen so far is leading text
                leading_lines = current_buf
            else:
                sections[current_section_name] = "\n".join(current_buf).strip() + "\n"

            current_section_name = line[3:].strip()
            current_buf = []
        else:
            current_buf.append(line)

    # Flush last section or leading text
    if current_section_name is None:
        # No section headings at all
        leading_lines = current_buf
    else:
        sections[current_section_name] = "\n".join(current_buf).strip() + "\n"

    leading_text = "\n".join(leading_lines).strip() + ("\n" if leading_lines else "")

    return title, sections, leading_text


def extract_or_build_purpose(leading_text: str, sections: Dict[str, str]) -> str:
    """
    Build the "Purpose" section body.

    Priority:
    1. Existing "Purpose" section (if present)
    2. A line starting with "**Purpose**:" in leading_text
    3. Empty placeholder
    """
    if "Purpose" in sections and sections["Purpose"].strip():
        return sections["Purpose"].rstrip() + "\n"

    purpose_lines = []
    for line in leading_text.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("**purpose**:"):
            purpose_lines.append(stripped.lstrip("*").rstrip("*").split(":", 1)[1].strip())
        elif stripped.lower().startswith("purpose:"):
            purpose_lines.append(stripped.split(":", 1)[1].strip())

    if purpose_lines:
        return "\n".join(purpose_lines).strip() + "\n"

    # Fallback placeholder
    return "[TODO: describe the purpose of this phase]\n"


def build_normalized_readme(
    title: str,
    sections: Dict[str, str],
    leading_text: str,
) -> str:
    """
    Construct a normalized README content string using the canonical section order.
    """
    lines: List[str] = []

    # Keep the original title (or a default if missing)
    if not title:
        title = "# [TODO: Phase Title]"
    lines.append(title)
    lines.append("")  # blank line after title

    # Build/override Purpose
    purpose_body = extract_or_build_purpose(leading_text, sections)
    lines.append("## Purpose")
    lines.append("")
    lines.append(purpose_body.rstrip())
    lines.append("")

    # Ensure we don't re-use any previous "Purpose" section
    normalized_sections = dict(sections)
    normalized_sections.pop("Purpose", None)

    # For every canonical section beyond Purpose
    for name in CANONICAL_SECTION_ORDER:
        if name == "Purpose":
            continue

        lines.append(f"## {name}")
        lines.append("")

        if name in normalized_sections and normalized_sections[name].strip():
            body = normalized_sections[name].rstrip()
        else:
            body = PLACEHOLDER_TEXT.get(name, "[TODO: fill this section]\n").rstrip()

        lines.append(body)
        lines.append("")

    # Strip trailing blank lines
    while lines and not lines[-1].strip():
        lines.pop()

    return "\n".join(lines) + "\n"


def process_readme(path: Path, write: bool = False) -> None:
    original_content = path.read_text(encoding="utf-8")
    title, sections, leading_text = parse_readme_sections(original_content)
    new_content = build_normalized_readme(title, sections, leading_text)

    if new_content == original_content:
        print(f"[SKIP] {path} (already normalized)")
        return

    print(f"[UPDATE] {path}")
    if write:
        backup = path.with_suffix(path.suffix + ".bak")
        if not backup.exists():
            backup.write_text(original_content, encoding="utf-8")
            print(f"        Backup created: {backup}")
        else:
            print(f"        Backup already exists: {backup}")
        path.write_text(new_content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Normalize phase README files to a canonical AI-optimized structure."
    )
    parser.add_argument(
        "--root",
        type=str,
        default=".",
        help="Repository root (default: current directory)",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Actually rewrite README files (default: dry-run)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Explicit dry-run mode (overrides --write)",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    write = args.write and not args.dry_run

    print(f"Scanning for phase READMEs under: {root}")
    readmes = find_phase_readmes(root)
    if not readmes:
        print("No phase README.md files found.")
        return

    for readme in readmes:
        process_readme(readme, write=write)

    if not write:
        print("\nDry-run complete. Re-run with --write to apply changes.")


if __name__ == "__main__":
    main()
```

---

## How to Use This in Your Repo

1. **Save the script**
   Save as `tools/normalize_phase_readmes.py` (or anywhere you like in the repo).

2. **Run a dry run first (recommended):**

```bash
cd /path/to/your/repo
python tools/normalize_phase_readmes.py --dry-run
```

You’ll see which `README.md` files would be updated.

3. **Apply changes:**

```bash
python tools/normalize_phase_readmes.py --write
```

For each modified README it will:

* Create `README.md.bak` (if not already present)
* Overwrite `README.md` with the normalized structure

---

## What This Gives You Right Now

* **Every phase README** will:

  * Have a `## Purpose` section (even if it used to be inline `**Purpose**:`)
  * Use the **same ordered set of headings**
  * Have **TODO placeholders** for missing AI-governance sections
* You can now:

  * Point PAT-CHECK at these docs
  * Ask an agent to “fill in all TODOs for phase X based on code/state”
  * Safely parse them as structured governance inputs for your orchestrator

---
Nice, let’s wire this into a **PAT-CHECK-README-001** style validator you can drop straight into the repo.

I’ll give you:

1. A **simple JSON “view” spec** for how we represent a README to the validator
2. A **standalone Python validator**: `pat_check_readme_001.py`
3. The **JSON report format** so your orchestrator / TUI can consume it

You can decide later whether to import the normalize script or just keep them as siblings.

---

## 1. JSON “View” of a README

We’ll treat each `README.md` as a **section map**:

```json
{
  "path": "phase3_scheduling/README.md",
  "title": "Phase 3 – Scheduling & Task Graph",
  "sections": {
    "Purpose": "…",
    "System Position": "…",
    "Phase Contracts": "…",
    "Phase Contents": "…",
    "Current Components": "…",
    "Main Operations": "…",
    "Source of Truth": "…",
    "Explicit Non-Responsibilities": "…",
    "Invocation & Control": "…",
    "Observability": "…",
    "AI Operational Rules": "…",
    "Test Coverage": "…",
    "Known Failure Modes": "…",
    "Readiness Model": "…",
    "Status": "…"
  }
}
```

The schema will validate **the `sections` object**, not raw markdown.

---

## 2. `pat_check_readme_001.py` – README Validator

Save this in your repo (e.g. `tools/pat_check_readme_001.py`).

```python
#!/usr/bin/env python
"""
PAT-CHECK-README-001

Validate phase README.md files against the AI-optimized README contract.

- Parses README.md under phase*/ directories
- Builds a JSON "view" with sections keyed by heading
- Validates required sections and some structural rules
- Emits a JSON report file listing PASS/FAIL and reasons

Usage:
    python tools/pat_check_readme_001.py --root . --report .reports/pat_check_readme_001.json

Requires:
    pip install jsonschema
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any

from jsonschema import Draft7Validator

CANONICAL_SECTION_ORDER: List[str] = [
    "Purpose",
    "System Position",
    "Phase Contracts",
    "Phase Contents",
    "Current Components",
    "Main Operations",
    "Source of Truth",
    "Explicit Non-Responsibilities",
    "Invocation & Control",
    "Observability",
    "AI Operational Rules",
    "Test Coverage",
    "Known Failure Modes",
    "Readiness Model",
    "Status",
]

# JSON Schema for sections (not full markdown, just the view)
README_SCHEMA: Dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "AI Optimized Phase README Schema",
    "type": "object",
    "required": [
        "Purpose",
        "System Position",
        "Phase Contracts",
        "Current Components",
        "Main Operations",
        "Source of Truth",
        "Explicit Non-Responsibilities",
        "Invocation & Control",
        "Observability",
        "AI Operational Rules",
        "Test Coverage",
        "Known Failure Modes",
        "Readiness Model",
        "Status",
    ],
    "properties": {
        "Purpose": {"type": "string", "minLength": 1},
        "System Position": {
            "type": "string",
            "minLength": 1
        },
        "Phase Contracts": {
            "type": "string",
            "minLength": 1
        },
        "Current Components": {
            "type": "string",
            "minLength": 1
        },
        "Main Operations": {
            "type": "string",
            "minLength": 1
        },
        "Source of Truth": {
            "type": "string",
            "minLength": 1
        },
        "Explicit Non-Responsibilities": {
            "type": "string",
            "minLength": 1
        },
        "Invocation & Control": {
            "type": "string",
            "minLength": 1
        },
        "Observability": {
            "type": "string",
            "minLength": 1
        },
        "AI Operational Rules": {
            "type": "string",
            "minLength": 1
        },
        "Test Coverage": {
            "type": "string",
            "minLength": 1
        },
        "Known Failure Modes": {
            "type": "string",
            "minLength": 1
        },
        "Readiness Model": {
            "type": "string",
            "minLength": 1
        },
        "Status": {
            "type": "string",
            "minLength": 1
        }
    },
    "additionalProperties": True
}


def find_phase_readmes(root: Path) -> List[Path]:
    """
    Find README.md files under directories whose name starts with 'phase'.
    """
    candidates: List[Path] = []
    for path in root.rglob("README.md"):
        if path.parent.name.lower().startswith("phase"):
            candidates.append(path)
    return sorted(candidates)


def parse_readme_sections(content: str) -> Tuple[str, Dict[str, str]]:
    """
    Parse markdown README into:
    - title: first level-1 heading (# ...)
    - sections: mapping from section name (without ##) to body text
    """
    lines = content.splitlines()
    title = ""
    sections: Dict[str, str] = {}

    current_section = None
    buf: List[str] = []

    for i, line in enumerate(lines):
        if i == 0 and line.startswith("# "):
            title = line[2:].strip()
            continue

        if line.startswith("## "):
            # flush previous section
            if current_section is not None:
                sections[current_section] = "\n".join(buf).strip() + ("\n" if buf else "")
            current_section = line[3:].strip()
            buf = []
        else:
            buf.append(line)

    if current_section is not None:
        sections[current_section] = "\n".join(buf).strip() + ("\n" if buf else "")

    return title, sections


def has_todo_markers(text: str) -> bool:
    """
    Detects if a section still contains placeholder TODO markers.
    """
    lowered = text.lower()
    return "[todo" in lowered or "todo:" in lowered


def validate_readme(path: Path) -> Dict[str, Any]:
    """
    Validate a single README and return a structured result dict.
    """
    content = path.read_text(encoding="utf-8")
    title, sections = parse_readme_sections(content)
    view = {
        "path": str(path),
        "title": title,
        "sections": sections,
    }

    # Prepare the object to validate: just the sections mapping
    sections_obj = sections

    validator = Draft7Validator(README_SCHEMA)
    errors = list(validator.iter_errors(sections_obj))

    issues: List[Dict[str, Any]] = []

    # Schema-level issues
    for e in errors:
        # e.path typically points at the offending key, e.message has human text
        issues.append(
            {
                "kind": "schema_error",
                "message": e.message,
                "path": list(e.path),
            }
        )

    # Extra semantic checks
    # 1) Ensure canonical sections are present explicitly
    for required in CANONICAL_SECTION_ORDER:
        if required not in sections_obj:
            issues.append(
                {
                    "kind": "missing_section",
                    "section": required,
                    "message": f"Section '{required}' is missing.",
                }
            )

    # 2) Check for TODO markers in critical sections
    for name in CANONICAL_SECTION_ORDER:
        body = sections_obj.get(name, "")
        if body and has_todo_markers(body):
            issues.append(
                {
                    "kind": "todo_placeholder",
                    "section": name,
                    "message": f"Section '{name}' still contains TODO placeholders.",
                }
            )

    status = "PASS" if not issues else "FAIL"

    return {
        "path": str(path),
        "title": title,
        "status": status,
        "issue_count": len(issues),
        "issues": issues,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PAT-CHECK-README-001: validate phase README files."
    )
    parser.add_argument(
        "--root",
        type=str,
        default=".",
        help="Repository root (default: current directory)",
    )
    parser.add_argument(
        "--report",
        type=str,
        default=".reports/pat_check_readme_001.json",
        help="Path to write JSON report (default: .reports/pat_check_readme_001.json)",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)

    readmes = find_phase_readmes(root)
    if not readmes:
        print(f"No phase README.md files found under {root}")
        return

    results: List[Dict[str, Any]] = []
    overall_fail = False

    for readme in readmes:
        result = validate_readme(readme)
        results.append(result)
        status = result["status"]
        print(f"[{status}] {readme}")
        if status == "FAIL":
            overall_fail = True
            for issue in result["issues"]:
                kind = issue.get("kind")
                msg = issue.get("message")
                section = issue.get("section", "")
                if section:
                    print(f"    - {kind} in '{section}': {msg}")
                else:
                    print(f"    - {kind}: {msg}")

    report = {
        "check_id": "PAT-CHECK-README-001",
        "root": str(root),
        "results": results,
    }

    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nReport written to: {report_path}")

    if overall_fail:
        # Non-zero exit so orchestrators can treat this as a gate
        raise SystemExit(1)


if __name__ == "__main__":
    main()
```

---

### How to run it

From repo root:

```bash
# 1) Install dependency once
pip install jsonschema

# 2) Run the check
python tools/pat_check_readme_001.py --root . --report .reports/pat_check_readme_001.json
```

* Exit code `0` → all READMEs pass
* Exit code `1` → at least one README failed validation (perfect for CI / orchestrator gates)

---

## 3. JSON Report Shape (for your orchestrator / TUI)

Example of `.reports/pat_check_readme_001.json`:

```json
{
  "check_id": "PAT-CHECK-README-001",
  "root": "/path/to/repo",
  "results": [
    {
      "path": "phase3_scheduling/README.md",
      "title": "Phase 3 – Scheduling & Task Graph",
      "status": "PASS",
      "issue_count": 0,
      "issues": []
    },
    {
      "path": "phase1_planning/README.md",
      "title": "Phase 1 – Planning & Spec Alignment",
      "status": "FAIL",
      "issue_count": 3,
      "issues": [
        {
          "kind": "missing_section",
          "section": "System Position",
          "message": "Section 'System Position' is missing."
        },
        {
          "kind": "todo_placeholder",
          "section": "Phase Contracts",
          "message": "Section 'Phase Contracts' still contains TODO placeholders."
        },
        {
          "kind": "schema_error",
          "message": "'Status' is a required property",
          "path": []
        }
      ]
    }
  ]
}
```

Your TUI / GUI can:

* Show a **per-phase PASS/FAIL grid**
* Drill into “why is this phase not safe for autonomy?”
* Highlight TODOs for agents to fix

---

Alright, let’s wire this into your world properly. I’ll do two things:

1. **Extend the Python validator** to also check **section ordering**.
2. Give you a **PowerShell wrapper** so PAT-CHECK plugs cleanly into your existing patterns.

---

## 1) Updated `pat_check_readme_001.py` with Section Ordering Check

Below is a **drop-in replacement** for the previous version.
New part: a **check that sections appear in the canonical order** and emit a `ordering_error` issue if they don’t.

```python
#!/usr/bin/env python
"""
PAT-CHECK-README-001

Validate phase README.md files against the AI-optimized README contract.

- Parses README.md under phase*/ directories
- Builds a JSON "view" with sections keyed by heading
- Validates required sections and some structural rules
- Checks that canonical sections appear in canonical order
- Emits a JSON report file listing PASS/FAIL and reasons

Usage:
    python tools/pat_check_readme_001.py --root . --report .reports/pat_check_readme_001.json

Requires:
    pip install jsonschema
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any

from jsonschema import Draft7Validator

CANONICAL_SECTION_ORDER: List[str] = [
    "Purpose",
    "System Position",
    "Phase Contracts",
    "Phase Contents",
    "Current Components",
    "Main Operations",
    "Source of Truth",
    "Explicit Non-Responsibilities",
    "Invocation & Control",
    "Observability",
    "AI Operational Rules",
    "Test Coverage",
    "Known Failure Modes",
    "Readiness Model",
    "Status",
]

# JSON Schema for sections (not full markdown, just the view)
README_SCHEMA: Dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "AI Optimized Phase README Schema",
    "type": "object",
    "required": [
        "Purpose",
        "System Position",
        "Phase Contracts",
        "Current Components",
        "Main Operations",
        "Source of Truth",
        "Explicit Non-Responsibilities",
        "Invocation & Control",
        "Observability",
        "AI Operational Rules",
        "Test Coverage",
        "Known Failure Modes",
        "Readiness Model",
        "Status",
    ],
    "properties": {
        "Purpose": {"type": "string", "minLength": 1},
        "System Position": {"type": "string", "minLength": 1},
        "Phase Contracts": {"type": "string", "minLength": 1},
        "Current Components": {"type": "string", "minLength": 1},
        "Main Operations": {"type": "string", "minLength": 1},
        "Source of Truth": {"type": "string", "minLength": 1},
        "Explicit Non-Responsibilities": {"type": "string", "minLength": 1},
        "Invocation & Control": {"type": "string", "minLength": 1},
        "Observability": {"type": "string", "minLength": 1},
        "AI Operational Rules": {"type": "string", "minLength": 1},
        "Test Coverage": {"type": "string", "minLength": 1},
        "Known Failure Modes": {"type": "string", "minLength": 1},
        "Readiness Model": {"type": "string", "minLength": 1},
        "Status": {"type": "string", "minLength": 1}
    },
    "additionalProperties": True
}


def find_phase_readmes(root: Path) -> List[Path]:
    """
    Find README.md files under directories whose name starts with 'phase'.
    """
    candidates: List[Path] = []
    for path in root.rglob("README.md"):
        if path.parent.name.lower().startswith("phase"):
            candidates.append(path)
    return sorted(candidates)


def parse_readme_sections(content: str) -> Tuple[str, Dict[str, str], List[str]]:
    """
    Parse markdown README into:
    - title: first level-1 heading (# ...)
    - sections: mapping from section name (without ##) to body text
    - order: list of section names in the order they appear
    """
    lines = content.splitlines()
    title = ""
    sections: Dict[str, str] = {}
    order: List[str] = []

    current_section = None
    buf: List[str] = []

    for i, line in enumerate(lines):
        if i == 0 and line.startswith("# "):
            title = line[2:].strip()
            continue

        if line.startswith("## "):
            # flush previous section
            if current_section is not None:
                sections[current_section] = "\n".join(buf).strip() + ("\n" if buf else "")
            current_section = line[3:].strip()
            order.append(current_section)
            buf = []
        else:
            buf.append(line)

    if current_section is not None:
        sections[current_section] = "\n".join(buf).strip() + ("\n" if buf else "")

    return title, sections, order


def has_todo_markers(text: str) -> bool:
    """
    Detects if a section still contains placeholder TODO markers.
    """
    lowered = text.lower()
    return "[todo" in lowered or "todo:" in lowered


def check_section_order(order: List[str]) -> List[Dict[str, Any]]:
    """
    Compare the actual README section order to the canonical order and
    return a list of ordering issues (if any).
    """
    issues: List[Dict[str, Any]] = []

    # Build a mapping of section -> index in actual order
    index_map = {name: idx for idx, name in enumerate(order)}

    # Only consider canonical sections that actually appear
    present_canonical = [s for s in CANONICAL_SECTION_ORDER if s in index_map]

    # If fewer than 2 canonical sections appear, no meaningful ordering check
    if len(present_canonical) < 2:
        return issues

    # Check that indices are strictly increasing w.r.t canonical order
    last_idx = -1
    last_name = None
    for name in present_canonical:
        idx = index_map[name]
        if idx < last_idx:
            issues.append(
                {
                    "kind": "ordering_error",
                    "message": (
                        f"Section '{name}' appears before '{last_name}' "
                        "but should come after it in canonical order."
                    ),
                    "section": name,
                    "previous_section": last_name,
                }
            )
        else:
            last_idx = idx
            last_name = name

    return issues


def validate_readme(path: Path) -> Dict[str, Any]:
    """
    Validate a single README and return a structured result dict.
    """
    content = path.read_text(encoding="utf-8")
    title, sections, order = parse_readme_sections(content)
    view = {
        "path": str(path),
        "title": title,
        "sections": sections,
        "order": order,
    }

    sections_obj = sections

    validator = Draft7Validator(README_SCHEMA)
    errors = list(validator.iter_errors(sections_obj))

    issues: List[Dict[str, Any]] = []

    # Schema-level issues
    for e in errors:
        issues.append(
            {
                "kind": "schema_error",
                "message": e.message,
                "path": list(e.path),
            }
        )

    # 1) Ensure canonical sections are present
    for required in CANONICAL_SECTION_ORDER:
        if required not in sections_obj:
            issues.append(
                {
                    "kind": "missing_section",
                    "section": required,
                    "message": f"Section '{required}' is missing.",
                }
            )

    # 2) Check for TODO markers in critical sections
    for name in CANONICAL_SECTION_ORDER:
        body = sections_obj.get(name, "")
        if body and has_todo_markers(body):
            issues.append(
                {
                    "kind": "todo_placeholder",
                    "section": name,
                    "message": f"Section '{name}' still contains TODO placeholders.",
                }
            )

    # 3) Check ordering
    ordering_issues = check_section_order(order)
    issues.extend(ordering_issues)

    status = "PASS" if not issues else "FAIL"

    return {
        "path": str(path),
        "title": title,
        "status": status,
        "issue_count": len(issues),
        "issues": issues,
        "view": view,  # optional, useful for debugging / agents
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PAT-CHECK-README-001: validate phase README files."
    )
    parser.add_argument(
        "--root",
        type=str,
        default=".",
        help="Repository root (default: current directory)",
    )
    parser.add_argument(
        "--report",
        type=str,
        default=".reports/pat_check_readme_001.json",
        help="Path to write JSON report (default: .reports/pat_check_readme_001.json)",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)

    readmes = find_phase_readmes(root)
    if not readmes:
        print(f"No phase README.md files found under {root}")
        return

    results: List[Dict[str, Any]] = []
    overall_fail = False

    for readme in readmes:
        result = validate_readme(readme)
        results.append(result)
        status = result["status"]
        print(f"[{status}] {readme}")
        if status == "FAIL":
            overall_fail = True
            for issue in result["issues"]:
                kind = issue.get("kind")
                msg = issue.get("message")
                section = issue.get("section", "")
                if section:
                    print(f"    - {kind} in '{section}': {msg}")
                else:
                    print(f"    - {kind}: {msg}")

    report = {
        "check_id": "PAT-CHECK-README-001",
        "root": str(root),
        "results": results,
    }

    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nReport written to: {report_path}")

    if overall_fail:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
```

---

## 2) PowerShell Wrapper: `Invoke-PATCheckReadme001.ps1`

This wraps the Python check into your **pattern-y**, CI/tui-friendly world.

Save as: `tools/Invoke-PATCheckReadme001.ps1`

```powershell
<#
.SYNOPSIS
  Wrapper for PAT-CHECK-README-001 (phase README validator).

.DESCRIPTION
  - Locates Python
  - Invokes pat_check_readme_001.py with root + report path
  - Surfaces pass/fail status and basic stats
  - Returns non-zero exit code on failure (CI / orchestrator gate)

.PARAMETER Root
  Repository root to scan. Defaults to current directory.

.PARAMETER PythonPath
  Optional explicit python executable path. Defaults to 'python'.

.PARAMETER ReportPath
  Path to JSON report. Defaults to '.reports/pat_check_readme_001.json'.

.EXAMPLE
  # Basic usage
  powershell -File tools/Invoke-PATCheckReadme001.ps1

.EXAMPLE
  # Custom root + report path
  powershell -File tools/Invoke-PATCheckReadme001.ps1 -Root "C:\repo" -ReportPath ".reports\readme_check.json"
#>

[CmdletBinding()]
param(
    [string]$Root = ".",
    [string]$PythonPath = "python",
    [string]$ReportPath = ".reports/pat_check_readme_001.json"
)

$ErrorActionPreference = "Stop"

Write-Host "=== PAT-CHECK-README-001 ===" -ForegroundColor Cyan
Write-Host "Root       : $Root"
Write-Host "PythonPath : $PythonPath"
Write-Host "ReportPath : $ReportPath"
Write-Host ""

# Resolve paths
$rootFull = (Resolve-Path -Path $Root).Path
$reportFull = Join-Path -Path $rootFull -ChildPath $ReportPath

# Ensure script exists
$scriptPath = Join-Path -Path $rootFull -ChildPath "tools\pat_check_readme_001.py"
if (-not (Test-Path $scriptPath)) {
    Write-Host "ERROR: pat_check_readme_001.py not found at: $scriptPath" -ForegroundColor Red
    exit 1
}

# Ensure report directory exists
$reportDir = Split-Path -Path $reportFull -Parent
if (-not (Test-Path $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
}

# Build arguments
$arguments = @(
    "`"$scriptPath`"",
    "--root", "`"$rootFull`"",
    "--report", "`"$reportFull`""
)

Write-Host "Invoking: $PythonPath $($arguments -join ' ')" -ForegroundColor DarkGray

# Invoke Python
& $PythonPath $arguments
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0 -and $exitCode -ne $null) {
    Write-Host ""
    Write-Host "PAT-CHECK-README-001 FAILED (exit code $exitCode)" -ForegroundColor Red
} else {
    Write-Host ""
    Write-Host "PAT-CHECK-README-001 PASSED" -ForegroundColor Green
}

# Try to show a quick summary from the JSON report
if (Test-Path $reportFull) {
    try {
        $json = Get-Content -Raw -Path $reportFull | ConvertFrom-Json

        $results = $json.results
        if ($results) {
            Write-Host ""
            Write-Host "Summary:" -ForegroundColor Cyan

            $table = $results | Select-Object `
                @{Name="Status"; Expression={ $_.status } },
                @{Name="Phase";  Expression={ $_.title } },
                @{Name="Path";   Expression={ $_.path } },
                @{Name="Issues"; Expression={ $_.issue_count } }

            $table | Format-Table -AutoSize
        }
    } catch {
        Write-Host "Warning: Could not parse report JSON at $reportFull" -ForegroundColor Yellow
    }
}

exit $exitCode
```

### How to use it

From repo root:

```powershell
# basic
powershell -File tools\Invoke-PATCheckReadme001.ps1

# with specific python (e.g. venv)
powershell -File tools\Invoke-PATCheckReadme001.ps1 -PythonPath ".venv\Scripts\python.exe"
```

* If any README fails → wrapper exits with **non-zero** code → CI / orchestrator can block.
* It also prints a **small table** summarizing phase, status, and issue count.

---

If you want, I can next:

* Add a **companion wrapper** that runs:

  1. the **normalizer**
  2. then **PAT-CHECK-README-001**

  as a single “DOC-GOVERNANCE-INIT” step, so agents always start from normalized docs before validating.
