---
doc_id: DOC-GUIDE-UTE-ARCHITECTURE-796
---

# UET Architecture Guide

## Mental Model

UET is a **DAG-based orchestration system** for AI-driven development workflows.

**Think of it as:** "Airflow for AI agents" - autonomous task scheduling, resilient execution, and comprehensive state management for any development workflow.

## Core Concept

The Universal Execution Templates Framework enables AI agents to autonomously manage complex development workflows by providing:
- **Schema-driven execution**: Type-safe operations with 17 JSON schemas
- **Project-agnostic templates**: Pre-built profiles for any project type
- **Resilient orchestration**: Circuit breakers, retries, and automatic recovery
- **Real-time monitoring**: Progress tracking with detailed metrics

## Execution Flow

```
1. BOOTSTRAP
   └─> Discovers project structure
   └─> Selects matching profile
   └─> Generates PROJECT_PROFILE.yaml + router_config.json
   └─> Validates all artifacts

2. ROUTING
   └─> Receives task specification
   └─> Finds capable tools from registry
   └─> Creates execution request

3. SCHEDULING
   └─> Resolves task dependencies
   └─> Creates execution DAG (topological sort)
   └─> Generates parallel batches

4. EXECUTION
   └─> Runs tasks via tool adapters
   └─> Applies resilience patterns (retry, circuit breaker)
   └─> Updates run state in real-time

5. MONITORING
   └─> Tracks progress per task and run
   └─> Calculates completion percentage and ETA
   └─> Reports status snapshots
```

## Key Concepts

### Profile
A project type template containing:
- Tool routing configuration
- Phase definitions
- Domain-specific constraints
- Recommended workflows

**Available profiles**: `software-dev-python`, `data-pipeline`, `documentation`, `operations`, `generic`

### Phase
A major workflow stage with defined:
- **Inputs**: Required artifacts/state before phase starts
- **Outputs**: Generated artifacts/state after phase completes
- **Workstreams**: Parallel execution streams within the phase
- **Dependencies**: Other phases that must complete first

**Example**: `analyze` phase → `implement` phase → `test` phase → `integrate` phase

### Workstream
A parallel execution stream within a phase that contains:
- Ordered sequence of tasks
- Domain-specific logic (e.g., "python_testing", "code_editing")
- Independent execution from other workstreams

### Task
The atomic unit of work that is:
- Routed to a specific tool based on capabilities
- Executed via tool adapters
- Tracked for progress and state
- Retried on failure with exponential backoff

### Adapter
Tool integration layer that provides:
- **Subprocess adapters**: CLI tool execution
- **API adapters**: REST/GraphQL integration
- **Custom adapters**: Domain-specific tool interfaces

## System Layers

```
┌─────────────────────────────────────────────────┐
│              CLI / API Layer                    │
│  Entry points for humans and AI agents          │
├─────────────────────────────────────────────────┤
│         Bootstrap Orchestrator                  │
│  Project discovery and configuration            │
├─────────────────────────────────────────────────┤
│           Execution Engine                      │
│  ┌──────────┬──────────┬──────────────────┐    │
│  │  Router  │Scheduler │   Monitor        │    │
│  │          │          │                  │    │
│  │ Task→Tool│ DAG      │ Progress         │    │
│  │ matching │ ordering │ tracking         │    │
│  └──────────┴──────────┴──────────────────┘    │
├─────────────────────────────────────────────────┤
│        Tool Adapter Layer                       │
│  ┌──────────┬──────────┬──────────────────┐    │
│  │Subprocess│   API    │     Custom       │    │
│  │          │          │                  │    │
│  │ CLI exec │ HTTP     │ Domain-specific  │    │
│  └──────────┴──────────┴──────────────────┘    │
├─────────────────────────────────────────────────┤
│     Resilience & State Layer                    │
│  ┌──────────┬──────────┬──────────────────┐    │
│  │ Circuit  │  Retry   │    State DB      │    │
│  │ Breaker  │  Logic   │                  │    │
│  │          │          │ SQLite + JSONL   │    │
│  └──────────┴──────────┴──────────────────┘    │
├─────────────────────────────────────────────────┤
│          Schema Foundation                      │
│       17 JSON Schemas (v1)                      │
│  Type-safe contracts for all operations         │
└─────────────────────────────────────────────────┘
```

## Entry Points

### CLI Usage
```bash
# Bootstrap a project
python core/bootstrap/orchestrator.py /path/to/project

# Run with specific profile
python core/bootstrap/orchestrator.py /path/to/project --profile software-dev-python
```

### Python API
```python
from core import BootstrapOrchestrator, ExecutionScheduler, ResilientExecutor

# Bootstrap
bootstrap = BootstrapOrchestrator("/path/to/project")
result = bootstrap.run()

# Schedule tasks
scheduler = ExecutionScheduler()
scheduler.add_tasks(tasks)
order = scheduler.get_execution_order()

# Execute with resilience
executor = ResilientExecutor()
result = executor.execute("aider", lambda: operation())
```

## State Management

### Run State
- **Storage**: SQLite database (`core/state/db.py`)
- **Schema**: `run_state.v1.json`
- **Tracked data**: run_id, status, start/end times, task states, metrics

### Audit Trail
- **Format**: Append-only JSONL logs
- **Purpose**: Complete execution history for debugging and replay
- **Contents**: Every state transition, tool invocation, error, and result

### Checkpoint System
- **Identity**: ULID-based (lexicographically sortable, time-ordered)
- **Purpose**: Time-travel debugging and state recovery
- **Recovery**: Replay execution from any checkpoint

### State Transitions

**Run States:**
```
PENDING → RUNNING → COMPLETED
            ↓
          FAILED
            ↓
        RETRYING → COMPLETED
                 ↓
               FAILED (terminal)
```

**Task States:**
```
PENDING → SCHEDULED → RUNNING → COMPLETED
            ↓           ↓
          BLOCKED     FAILED
                        ↓
                    RETRYING → COMPLETED
                               ↓
                             FAILED (terminal)
```

## Resilience Patterns

### Circuit Breaker
- **Purpose**: Prevent cascading failures from external tools
- **States**: CLOSED (normal) → OPEN (failing) → HALF_OPEN (testing recovery)
- **Configuration**: Failure threshold, recovery timeout per tool

### Retry with Exponential Backoff
- **Purpose**: Handle transient failures gracefully
- **Strategy**: `delay = base_delay * (2 ^ attempt_number)`
- **Configuration**: Max retries, base delay per tool

### Timeout Management
- **Purpose**: Prevent indefinite waiting on stuck operations
- **Implementation**: Per-tool timeout configuration
- **Handling**: Timeout triggers retry logic

## Data Flow

```
User Request
    ↓
Bootstrap discovers project → Generates profile + config
    ↓
Task specifications → Router finds capable tools
    ↓
Scheduler creates DAG → Orders tasks topologically
    ↓
Executor runs via adapters → Updates state DB
    ↓
Monitor tracks progress → Calculates metrics
    ↓
Results returned → Audit trail logged
```

## Extension Points

### Adding a New Tool Adapter
1. Implement adapter interface in `core/adapters/`
2. Register in `router_config.json`
3. Define capabilities (domains, actions)
4. Add tests in `tests/adapters/`

### Creating a Custom Profile
1. Create directory in `profiles/`
2. Define `profile.json` with metadata
3. Create `router_config.json` for tool routing
4. Add phase definitions in `phases/`
5. Write `README.md` with usage guide

### Adding a New Phase Type
1. Define schema in `schema/phase_spec.v1.json`
2. Create phase template in profile
3. Document inputs, outputs, constraints
4. Add validation logic

## Performance Characteristics

- **Parallel execution**: Up to N concurrent tasks (configurable)
- **Dependency resolution**: O(V + E) topological sort
- **State persistence**: Async writes, batch commits
- **Monitor overhead**: <5% execution time
- **Recovery time**: Sub-second checkpoint restoration

## Security Considerations

- **Tool sandboxing**: Subprocess isolation per adapter
- **Credential management**: Environment variable injection
- **Audit compliance**: Complete execution trail
- **State integrity**: Append-only logs prevent tampering

## References

- **Full specifications**: See `specs/` directory
- **Schemas**: See `schema/` directory
- **Dependency graph**: See `DEPENDENCIES.md`
- **Current status**: See `specs/STATUS.md`
