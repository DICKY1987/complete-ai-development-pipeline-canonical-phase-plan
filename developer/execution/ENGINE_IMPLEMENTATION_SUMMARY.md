# Hybrid GUI Architecture - Implementation Summary

## What Was Created

This implementation establishes the **hybrid GUI/Terminal/TUI architecture** foundation for the AI Development Pipeline, following the design documents in `gui/`.

## Directory Structure

```
engine/                              # New: Execution engine layer
├── interfaces/                      # Protocol-based contracts
│   ├── __init__.py
│   ├── state_interface.py          # State persistence contract
│   ├── adapter_interface.py        # Tool adapter contract
│   └── orchestrator_interface.py   # Orchestrator contract
├── adapters/                        # Tool-specific adapters
│   ├── __init__.py
│   └── aider_adapter.py            # Aider CLI wrapper
├── orchestrator/                    # Job orchestration
│   ├── __init__.py
│   ├── __main__.py                 # CLI entry point
│   └── orchestrator.py             # Main orchestrator logic
├── state_store/                     # State persistence (future)
│   └── __init__.py
├── __init__.py
├── types.py                         # Shared types (Job, JobResult)
└── README.md                        # Usage documentation

specs/                               # Job specifications
└── jobs/
    ├── job.schema.json              # Standard job schema
    └── aider_job.example.json       # Example Aider job
```

## Key Components

### 1. Job Schema (`schema/jobs/job.schema.json`)

Defines the standard contract for all tool executions:
- **job_id**: Unique identifier
- **workstream_id**: Owning workstream
- **tool**: Tool to execute (aider, codex, tests, git)
- **command**: Executable and arguments
- **env**: Environment variables
- **paths**: Repo root, working dir, log file, error report
- **metadata**: Tool-specific config (timeouts, retries, etc.)

### 2. Protocol Interfaces (`engine/interfaces/`)

Type-safe contracts without tight coupling:
- **StateInterface**: Database operations (jobs, runs, workstreams, events)
- **AdapterInterface**: Tool execution (run_job, validate_job, get_tool_info)
- **OrchestratorInterface**: Job lifecycle (run_job, queue_job, get_job_status)

### 3. Shared Types (`engine/types.py`)

- **Job**: Job definition dataclass
- **JobResult**: Execution result (exit code, logs, duration, success)
- **JobStatus**: Job state tracking

### 4. Aider Adapter (`engine/adapters/aider_adapter.py`)

Reference implementation showing the adapter pattern:
- Builds command from job spec
- Executes in subprocess with timeout
- Streams logs to file
- Returns standardized JobResult
- Writes error report JSON on failure

### 5. Orchestrator (`engine/orchestrator/orchestrator.py`)

Central coordinator with CLI interface:
```bash
python -m engine.orchestrator run-job --job-file path/to/job.json
```

Responsibilities:
- Loads and validates job files
- Dispatches to appropriate adapter
- (Future) Updates state store
- (Future) Handles retries and escalations

## Architectural Principles

### Separation of Concerns

**GUI Layer** (future):
- Only reads state via `StateInterface`
- Only submits jobs via orchestrator CLI
- Never calls tools directly

**Engine Layer** (implemented):
- Job lifecycle management
- Tool execution through adapters
- State persistence

**Terminal/TUI Layer**:
- Actual tool processes (Aider, Codex, etc.)
- Emit logs and structured output

### Job-Based Execution

Everything is a job:
1. Create job JSON file
2. Submit to orchestrator
3. Orchestrator dispatches to adapter
4. Adapter runs tool and captures results
5. State updated for GUI visibility

### Protocol-Based Contracts

Uses Python `Protocol` for contracts:
- No inheritance required
- Easy to mock for testing
- Type-safe with IDE support
- Sections remain independent

## Usage Examples

### Run an Aider Job

```bash
python -m engine.orchestrator run-job --job-file schema/jobs/aider_job.example.json
```

### Create a Custom Job

```json
{
  "job_id": "job-2025-11-20-002",
  "workstream_id": "ws-my-feature",
  "tool": "aider",
  "command": {
    "exe": "aider",
    "args": ["--message", "Fix the bug in auth.py"]
  },
  "env": {
    "OLLAMA_API_BASE": "http://127.0.0.1:11434"
  },
  "paths": {
    "repo_root": "C:/path/to/repo",
    "working_dir": "C:/path/to/repo",
    "log_file": "logs/job-2025-11-20-002.log",
    "error_report": "logs/job-2025-11-20-002.error.json"
  },
  "metadata": {
    "timeout_seconds": 300
  }
}
```

## Integration with Existing Code

This is **Phase 1** of the architecture migration:

- ✅ **Independent engine layer** created
- ⏳ **State integration** pending (will use existing `core/state/db.py`)
- ⏳ **Additional adapters** pending (Codex, tests, git)
- ⏳ **Job queue** pending
- ⏳ **GUI panels** pending

No changes to existing `core/` code yet - this coexists safely.

## Next Steps

### Phase 2: State Integration
1. Create `engine/state_store/job_state_store.py`
2. Wrap existing `core/state/db.py` with `StateInterface`
3. Wire into orchestrator for job status tracking

### Phase 3: Additional Adapters
1. `engine/adapters/codex_adapter.py`
2. `engine/adapters/tests_adapter.py`
3. `engine/adapters/git_adapter.py`

### Phase 4: Job Queue
1. `engine/orchestrator/job_queue.py`
2. Status transitions: queued → running → completed/failed/quarantined

### Phase 5: GUI Foundation
1. Follow `gui/` specs to create panel plugins
2. Use orchestrator CLI for all tool execution
3. Read-only state queries via `StateInterface`

## Design Documents

All design decisions documented in `gui/`:
- `Hybrid UI_GUI shell_terminal_TUI engine.md` - Architecture overview
- `Top-level layout split GUI vs Engine vs Specs.md` - Structure and contracts
- `Plan Map coreStructure to engine Hybrid Architecture.md` - Migration plan
- `GUI_PIPELINE.txt` - Permissions matrix and plugin schema
- `Pipeline Radar plugin.md` - Example panel design

## Testing

Orchestrator is functional and can be tested:

```bash
# Show help
python -m engine.orchestrator --help

# Run example job (requires aider installed)
python -m engine.orchestrator run-job --job-file schema/jobs/aider_job.example.json
```

## Compliance with AGENTS.md

This implementation follows repository guidelines:
- ✅ Uses section-based directory structure (`engine/`)
- ✅ Protocol-based interfaces for clean contracts
- ✅ Job schema for declarative specifications
- ✅ No changes to existing `core/` code
- ✅ Windows-first (subprocess works cross-platform)
- ✅ Documented with headers (ADAPTER_ROLE, RESPONSIBILITY)
- ✅ Type hints throughout

## Status: Phase 1 Complete ✅

The foundation is in place. The orchestrator can execute jobs, adapters follow a standard pattern, and the architecture supports the GUI layer when ready to implement.
