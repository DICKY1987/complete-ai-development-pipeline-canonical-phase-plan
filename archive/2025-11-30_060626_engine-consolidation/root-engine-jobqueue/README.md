---
doc_id: DOC-GUIDE-README-417
---

# Engine Implementation Documentation

## Overview

This directory implements the **hybrid GUI/Terminal/TUI architecture** for the AI Development Pipeline, following the design specifications in `gui/`.

## Architecture

```
engine/
├── interfaces/          # Protocol definitions (contracts)
│   ├── state_interface.py
│   ├── adapter_interface.py
│   └── orchestrator_interface.py
├── adapters/           # Tool-specific adapters
│   └── aider_adapter.py
├── orchestrator/       # Job orchestration
│   └── orchestrator.py
├── state_store/        # State persistence
└── types.py           # Shared types (Job, JobResult, JobStatus)
```

## Key Concepts

### Job-Based Execution

All tool executions (Aider, Codex, tests, git) are defined as **job JSON files** conforming to `schema/jobs/job.schema.json`.

**Example:**
```bash
python -m engine.orchestrator run-job --job-file schema/jobs/aider_job.example.json
```

### Adapter Pattern

Each CLI tool gets a thin adapter implementing `AdapterInterface`:

- **Input**: Job dictionary (from JSON)
- **Responsibility**: Build command, execute in subprocess, capture logs
- **Output**: `JobResult` (exit code, duration, logs, error report)

### Protocol-Based Contracts

Components communicate via Python `Protocol` interfaces:

- **StateInterface**: State persistence contract
- **AdapterInterface**: Tool adapter contract  
- **OrchestratorInterface**: Orchestrator contract

This enables loose coupling and easy mocking for tests.

## Usage

### Running a Job

```bash
# Using the orchestrator CLI
python -m engine.orchestrator run-job --job-file path/to/job.json
```

### Creating a Job File

See `schema/jobs/aider_job.example.json` for a complete example.

Required fields:
- `job_id`: Unique identifier (e.g., `job-2025-11-20-001`)
- `workstream_id`: Owning workstream
- `tool`: Tool name (`aider`, `codex`, etc.)
- `command`: Executable and arguments
- `env`: Environment variables
- `paths`: Repo root, working dir, log file, error report

### Adding a New Adapter

1. Create `engine/adapters/<tool>_adapter.py`
2. Implement `AdapterInterface` protocol
3. Add header with `ADAPTER_ROLE: terminal_tool_adapter`
4. Register in `Orchestrator.TOOL_RUNNERS`

**Template:**
```python
"""
ADAPTER_ROLE: terminal_tool_adapter
TOOL: <tool_name>
VERSION: 0.1.0
"""

from engine.types import JobResult

def run_<tool>_job(job: dict) -> JobResult:
    # Build command
    # Execute in subprocess
    # Capture logs
    # Return JobResult
    pass
```

## Integration with Existing Code

The `engine/` structure is designed to coexist with the current `core/` directory:

- **Phase 1 (Current)**: `engine/` is standalone with minimal dependencies
- **Phase 2**: Integrate with `core/state/` for persistence
- **Phase 3**: Add shims in `src/pipeline/` for backward compatibility

See `gui/Plan Map coreStructure to engine Hybrid Architecture.md` for the full migration plan.

## GUI Integration

The GUI **never** calls tools directly. It only:

1. Reads state via `StateInterface`
2. Submits jobs via `orchestrator run-job` CLI

See `gui/Top-level layout split GUI vs Engine vs Specs.md` for GUI design.

## Status

**Current**: Phase 1 - Foundation
- ✅ Protocol interfaces defined
- ✅ Job schema created
- ✅ Aider adapter implemented
- ✅ Orchestrator CLI working
- ⏳ State store integration pending
- ⏳ Additional adapters pending (Codex, tests, git)

**Next Steps**:
1. Integrate with existing `core/state/db.py`
2. Create `engine/state_store/job_state_store.py`
3. Add Codex and tests adapters
4. Implement job queue mechanism
