---
status: canonical
doc_type: adr
module_refs: []
script_refs: []
doc_id: DOC-ARCH-ADR_0001_WORKSTREAM_MODEL_CHOICE-011
---

# ADR-0001: Workstream Model Choice

**Status:** Accepted  
**Date:** 2025-11-22  
**Deciders:** System Architecture Team  
**Context:** Need for structured, reproducible AI-driven development workflows

---

## Decision

We will use a **workstream-based execution model** as the core orchestration pattern for the AI development pipeline, where work is organized into sequential/parallel streams of steps with explicit dependencies and state management.

---

## Rationale

### Key Factors

1. **Structured Coordination:** Workstreams provide clear boundaries for organizing complex, multi-step development tasks
2. **Explicit Dependencies:** Step-level `depends_on` relationships enable correct execution ordering
3. **State Management:** Each workstream and step has trackable state (pending, running, success, failure)
4. **AI Agent Compatibility:** Clear, declarative structure is easy for AI agents to understand and execute
5. **Parallel Execution:** Multiple workstreams can run concurrently when dependencies allow
6. **Recovery & Retry:** Fine-grained state tracking enables step-level retry and checkpoint recovery

### Design Principles

- **Declarative over Imperative:** Define WHAT to do, not HOW (execution engine decides HOW)
- **Composability:** Workstreams can be bundled together for complex operations
- **Idempotency:** Steps should be safe to retry without side effects
- **Observability:** Every state transition is tracked in the database

---

## Consequences

### Positive

- **Reproducibility:** Same workstream bundle produces same results deterministically
- **Parallelism:** Independent workstreams execute concurrently, reducing total time
- **Clear Progress Tracking:** State machine provides real-time execution status
- **Failure Isolation:** Step failure doesn't corrupt entire workflow
- **Testability:** Individual steps can be tested in isolation
- **Tool Agnostic:** Steps can route to different tools (aider, pytest, custom scripts)

### Negative

- **Learning Curve:** New contributors must understand workstream schema and conventions
- **Verbosity:** JSON workstream definitions are more verbose than simple scripts
- **Debugging Complexity:** Multi-step failures require tracing through state transitions

### Neutral

- **Schema Evolution:** Workstream schema must be versioned carefully to maintain backward compatibility
- **Execution Overhead:** State tracking adds small overhead vs direct script execution

---

## Alternatives Considered

### Alternative 1: Task Directed Acyclic Graph (DAG)

**Description:** Use a generic task graph with nodes representing individual tasks and edges representing dependencies (similar to Apache Airflow, Dask, Luigi)

**Rejected because:**
- Too low-level - would require significant boilerplate for common patterns
- No built-in concept of "phases" or "workstreams" for grouping related tasks
- Less semantic structure - harder for AI agents to reason about intent
- Generic task graphs optimize for computation, not development workflows

### Alternative 2: Event-Driven Architecture

**Description:** Use event bus where completion of one task triggers subsequent tasks via pub/sub

**Rejected because:**
- Non-deterministic execution order makes debugging difficult
- Harder to visualize and understand workflow structure
- State tracking becomes distributed across event handlers
- Recovery is complex - need to replay event streams

### Alternative 3: Imperative Scripts

**Description:** Use Python/PowerShell scripts that directly call tools in sequence

**Rejected because:**
- No parallelism without manual threading/multiprocessing
- State management is ad-hoc and inconsistent
- Difficult to resume after failure
- No standardized tool adapter interface
- Hard for AI agents to modify or generate scripts safely

### Alternative 4: Makefile-style Build System

**Description:** Use make or similar build tools with file-based dependencies

**Rejected because:**
- Designed for compilation, not development workflows
- File-based dependencies don't map well to tasks like "run tests" or "deploy"
- Limited support for parallel execution across different task types
- Poor state tracking for non-file-producing tasks

---

## Related Decisions

- [ADR-0003: SQLite State Storage](0003-sqlite-state-storage.md) - State management implementation
- [ADR-0002: Hybrid Architecture](0002-hybrid-architecture.md) - How workstreams integrate with GUI/Terminal
- [Phase K+ Enhancement Plan](../../meta/plans/phase-K-plus-decision-context.md) - Decision context documentation

---

## References

- **Implementation:** `core/engine/orchestrator.py`
- **Schema:** `schema/workstream.schema.json`
- **State Machine:** `docs/state_machine.md`
- **Examples:** `workstreams/` directory
- **UET Framework:** `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/` (advanced workstream orchestration)

---

## Notes

### Migration Path

Existing imperative scripts in `scripts/` are being gradually converted to workstream bundles. The two approaches coexist:
- **Scripts:** Quick ad-hoc tasks, one-off operations
- **Workstreams:** Repeatable, complex, multi-step workflows

### Future Enhancements

- **Conditional Steps:** Support for `if/else` logic in workstream execution
- **Dynamic Workstreams:** Generate workstream steps programmatically based on runtime conditions
- **Workstream Templates:** Parameterized workstreams for common patterns (e.g., "test-fix-verify" loop)

---

## Revision History

| Date | Change | Author |
|------|--------|--------|
| 2025-11-22 | Initial ADR created as part of Phase K+ | GitHub Copilot |
