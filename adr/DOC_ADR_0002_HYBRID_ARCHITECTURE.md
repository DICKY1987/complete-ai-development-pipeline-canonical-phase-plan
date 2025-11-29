---
status: canonical
doc_type: adr
module_refs: []
script_refs: []
doc_id: DOC-ARCH-ADR_0002_HYBRID_ARCHITECTURE-002
---

# ADR-0002: Hybrid Architecture (GUI/Terminal/TUI)

**Status:** Accepted  
**Date:** 2025-11-22  
**Deciders:** System Architecture Team  
**Context:** Need to support multiple execution modes for different user preferences and environments

---

## Decision

We will implement a **hybrid architecture** that supports three execution modes:
1. **GUI Mode:** Rich graphical interface for interactive workflow management
2. **Terminal Mode:** Command-line execution for automation and CI/CD
3. **TUI Mode:** Text-based UI for terminal users who want interactivity without GUI overhead

All modes share a common execution engine based on **job-based execution patterns** rather than direct workstream execution.

---

## Rationale

### User Needs Drive Architecture

Different users have different preferences:
- **Visual Learners:** Prefer GUI with real-time graphs, progress bars, log viewers
- **Power Users:** Prefer terminal with scriptability and integration into existing workflows
- **Remote/SSH Users:** Need TUI for interactive monitoring without X11/RDP overhead

### Shared Execution Engine

All three modes delegate to the same underlying execution engine (`engine/`), which:
- Converts workstreams into **jobs** (atomic units of execution)
- Manages job queue and worker pools
- Tracks state in SQLite database (`.worktrees/pipeline_state.db`)
- Provides adapters for different tools (aider, pytest, git, etc.)

This separation ensures:
- **Consistency:** Same behavior regardless of UI mode
- **Testability:** Engine can be tested independently
- **Flexibility:** New UI modes can be added without changing execution logic

---

## Consequences

### Positive

- **User Choice:** Users select mode based on preference and environment
- **Automation Friendly:** Terminal mode integrates easily into CI/CD pipelines
- **Remote Accessible:** TUI works over SSH without GUI dependencies
- **Development Flexibility:** UI and engine can evolve independently
- **Testing Isolation:** Engine tests don't require GUI mocking

### Negative

- **Implementation Overhead:** Must maintain three UI implementations
- **API Surface:** Engine must expose consistent API for all UIs
- **State Synchronization:** All UIs must stay in sync with engine state

### Neutral

- **Documentation Burden:** Must document all three modes
- **User Confusion:** Users need guidance on which mode to use

---

## Alternatives Considered

### Alternative 1: GUI-Only Architecture

**Description:** Build rich Electron or Qt GUI with all logic embedded

**Rejected because:**
- Not usable in headless CI/CD environments
- Poor SSH/remote access experience
- Difficult to automate and script
- Excludes terminal-first users (developers, DevOps, CLI enthusiasts)

### Alternative 2: Terminal-Only Architecture

**Description:** CLI-only interface with flags and options

**Rejected because:**
- Steep learning curve for non-technical users
- Limited visualization of complex workflows
- Hard to monitor long-running processes interactively
- Requires memorizing many commands and flags

### Alternative 3: Web-Based Dashboard

**Description:** Browser-based UI with REST API backend

**Rejected because:**
- Requires web server deployment and port management
- Authentication/security complexity for local development
- Network overhead for local operations
- Doesn't solve terminal-only user needs

### Alternative 4: Single Mode with Plugins

**Description:** Pick one mode (e.g., Terminal) and support GUI via plugins

**Rejected because:**
- Plugin architecture adds complexity without clear benefit
- First-class support for all modes is better than bolted-on plugins
- User experience suffers when UI feels "second-class"

---

## Related Decisions

- [ADR-0001: Workstream Model Choice](0001-workstream-model-choice.md) - Execution model
- [ADR-0003: SQLite State Storage](0003-sqlite-state-storage.md) - Shared state backend
- [Engine Documentation](../ENGINE_IMPLEMENTATION_SUMMARY.md) - Job-based execution details

---

## References

- **Engine Implementation:** `engine/` directory
- **Job Runner:** `engine/job_runner.py`
- **GUI Design:** `gui/` directory (design docs, not yet implemented)
- **Queue Management:** `engine/queue.py`
- **State Database:** `.worktrees/pipeline_state.db`

---

## Notes

### Current Status (2025-11-22)

- **Terminal Mode:** ✅ Fully implemented via `scripts/run_workstream.py`
- **Engine (Job-based):** ✅ Implemented in `engine/`
- **TUI Mode:** ⏳ Planned (design docs in `gui/`)
- **GUI Mode:** ⏳ Planned (design docs in `gui/`)

### Job-Based Execution Pattern

The engine converts workstreams into jobs:

```
Workstream → Multiple Jobs
  ├─ Job 1: Setup environment
  ├─ Job 2: Run tests (parallel workers)
  ├─ Job 3: Generate report
  └─ Job 4: Cleanup
```

Jobs are:
- **Atomic:** Complete fully or fail fully
- **Retryable:** Can be rerun on failure
- **Trackable:** State stored in database
- **Queue-based:** Managed by worker pool

### UI Responsibilities

Each UI mode is responsible for:
- **Displaying State:** Read from database, show progress/status
- **User Input:** Collect parameters, confirmation, manual overrides
- **Triggering Execution:** Submit jobs to engine queue
- **Log Streaming:** Display real-time output from jobs

Engine is responsible for:
- **Execution:** Actually running tools and commands
- **State Management:** Tracking job lifecycle in database
- **Concurrency:** Managing worker pools and parallelism
- **Recovery:** Retry logic, circuit breakers, checkpoints

---

## Revision History

| Date | Change | Author |
|------|--------|--------|
| 2025-11-22 | Initial ADR created as part of Phase K+ | GitHub Copilot |
