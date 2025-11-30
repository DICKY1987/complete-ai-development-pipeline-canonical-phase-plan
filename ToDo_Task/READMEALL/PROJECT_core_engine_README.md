---
doc_id: DOC-GUIDE-PROJECT-CORE-ENGINE-README-1579
---

# Core Orchestration Engine

> **Module**: `core.engine`  
> **Purpose**: Workstream orchestration, execution, scheduling, and resilience  
> **Layer**: Execution/Control  
> **Status**: Production

---

## Overview

The `core/engine/` module provides the orchestration and execution engine for workstreams. It coordinates:

- **Step sequencing** - EDIT → STATIC → RUNTIME flow with FIX retry loops
- **Parallel execution** - Wave-based scheduling with dependency resolution
- **Tool integration** - Unified adapter interface for AI coding tools
- **Circuit breakers** - Fault tolerance patterns to prevent infinite loops
- **Recovery strategies** - Automatic retry with exponential backoff
- **AIM integration** - Capability-based tool routing

The engine maintains full state tracking, telemetry, and audit trails for all executions.

---

## Directory Structure

```
core/engine/
├── orchestrator.py           # Main orchestration loop (single + parallel)
├── scheduler.py              # Dependency resolution and wave scheduling
├── executor.py               # Step execution with timeout handling
├── tools.py                  # Tool adapter interface
├── circuit_breakers.py       # Circuit breaker patterns
├── recovery.py               # Recovery strategies
├── recovery_manager.py       # Recovery coordination
├── aim_integration.py        # AIM capability routing
├── validators.py             # Scope, timeout, and circuit breaker validators
├── compensation.py           # Rollback and compensation actions
├── event_bus.py              # Event publication for observability
├── metrics.py                # Execution metrics and telemetry
├── cost_tracker.py           # Cost tracking and budget enforcement
├── context_estimator.py      # Context window estimation
├── patch_manager.py          # Git patch parsing and application
├── process_spawner.py        # Worker process management
├── worker.py                 # Worker pool implementation
├── integration_worker.py     # Integration and merge coordination
├── performance.py            # Performance optimization
├── hardening.py              # Retry, health checks, rate limiting
├── test_gates.py             # Test gate enforcement
├── plan_validator.py         # Workstream plan validation
├── prompt_engine.py          # Prompt classification and routing
├── pipeline_plus_orchestrator.py  # Enhanced orchestrator (UET Phase H)
└── adapters/                 # Tool adapters
    ├── base.py               # Base adapter interface
    ├── aider_adapter.py      # Aider adapter
    ├── claude_adapter.py     # Claude CLI adapter
    └── codex_adapter.py      # Codex adapter
```

---

## Core Concepts

### Step Sequence

The orchestrator executes workstreams in a three-phase sequence:

```
EDIT (code generation)
  ↓
STATIC (linting, type checking)
  ↓ (optional FIX loop if errors)
RUNTIME (tests, integration)
  ↓ (optional FIX loop if failures)
DONE
```

Each step can trigger a FIX loop with circuit breaker protection.

### Parallel Execution

Workstreams are scheduled in **waves** based on dependency graphs:

```
Wave 1: [ws-A, ws-B, ws-C]  (no dependencies)
Wave 2: [ws-D, ws-E]         (depend on Wave 1)
Wave 3: [ws-F]               (depends on Wave 2)
```

Waves execute in parallel with configurable worker pools.

---

## Key Components

### Orchestrator (`orchestrator.py`)

Main orchestration logic for single and parallel workstream execution.

#### Single Workstream Execution

```python
from core.engine.orchestrator import run_workstream
from core.state.bundles import WorkstreamBundle

# Execute single workstream
result = run_workstream(
    run_id="run-2025-11-22-001",
    ws_id="ws-feature-auth",
    bundle_obj=bundle,
    context={"dry_run": False, "timeout_sec": 300}
)

# Result structure:
# {
#     "success": True,
#     "final_status": "completed",
#     "steps_executed": ["edit", "static", "runtime"],
#     "total_fix_iterations": 2,
#     "elapsed_seconds": 125.4
# }
```

#### Parallel Execution

```python
from core.engine.orchestrator import execute_workstreams_parallel
from core.state.bundles import load_and_validate_bundles

# Load bundles
bundles = load_and_validate_bundles("workstreams/examples")

# Execute in parallel
results = execute_workstreams_parallel(
    run_id="run-2025-11-22-001",
    bundles=bundles,
    context={
        "max_workers": 4,
        "wave_delay_sec": 5,
        "fail_fast": False
    }
)

# Results per workstream:
# {
#     "ws-feature-auth": {"success": True, ...},
#     "ws-db-setup": {"success": True, ...},
#     "ws-api-routes": {"success": False, "error": "..."}
# }
```

#### Step Functions

```python
from core.engine.orchestrator import (
    run_edit_step,
    run_static_step,
    run_runtime_step,
    run_static_with_fix,
    run_runtime_with_fix
)

# Execute individual steps
edit_result = run_edit_step(run_id, ws_id, bundle, context)
static_result = run_static_with_fix(run_id, ws_id, bundle, context)
runtime_result = run_runtime_with_fix(run_id, ws_id, bundle, context)
```

---

### Scheduler (`scheduler.py`)

Resolves dependencies and schedules workstreams into execution waves.

```python
from core.engine.scheduler import build_execution_plan

# Build execution plan from bundles
plan = build_execution_plan(bundles)

# Plan structure:
# {
#     "waves": [
#         ["ws-A", "ws-B"],      # Wave 0 (no dependencies)
#         ["ws-C"],              # Wave 1 (depends on ws-A)
#         ["ws-D", "ws-E"]       # Wave 2 (depends on ws-C)
#     ],
#     "total_waves": 3,
#     "total_workstreams": 5,
#     "dependency_graph": {...}
# }
```

**Scheduling Algorithm**:
1. Build dependency graph from `depends_on` fields
2. Detect and reject circular dependencies
3. Perform topological sort to determine wave ordering
4. Group independent workstreams into same wave
5. Apply conflict groups (workstreams in same conflict group cannot run in parallel)

---

### Tool Adapter (`tools.py`)

Unified interface for executing AI coding tools (Aider, Claude CLI, etc.).

```python
from core.engine.tools import run_tool, load_tool_profiles

# Load tool profiles
profiles = load_tool_profiles("config/tool_profiles.json")

# Execute tool
result = run_tool(
    tool_id="aider",
    context={
        "worktree_path": "/path/to/worktree",
        "files": ["src/auth.py"],
        "prompt": "Add JWT authentication",
        "timeout_sec": 300
    },
    profiles=profiles
)

# Result structure:
# ToolResult(
#     success=True,
#     exit_code=0,
#     stdout="...",
#     stderr="",
#     elapsed_sec=45.2,
#     content={
#         "files_modified": ["src/auth.py"],
#         "diff": "...",
#         "tool": "aider"
#     }
# )
```

**Tool Profiles**:
Tool profiles are defined in `config/tool_profiles.json`:

```json
{
  "aider": {
    "binary": "aider",
    "args": [
      "--yes",
      "--no-auto-commits",
      "--message", "{prompt}"
    ],
    "env": {
      "AIDER_NO_GIT": "1"
    },
    "timeout_sec": 300
  }
}
```

**Variable Substitution**:
Context variables are substituted into tool arguments:
- `{prompt}` → context["prompt"]
- `{files}` → " ".join(context["files"])
- `{worktree_path}` → context["worktree_path"]

---

### Circuit Breakers (`circuit_breakers.py`)

Prevents infinite FIX loops and detects oscillating repairs.

```python
from core.engine.circuit_breakers import (
    FixLoopState,
    allow_fix_attempt,
    detect_oscillation
)

# Initialize state
state = FixLoopState()

# Check if fix attempt is allowed
if allow_fix_attempt(state, step="static", cfg=breaker_config):
    # Attempt fix
    result = run_fix_step(...)
    
    # Check for oscillation
    if detect_oscillation(state, cfg=breaker_config):
        raise CircuitBreakerError("Oscillating fix detected")
```

**Circuit Breaker Configuration** (`config/circuit_breaker_config.yaml`):

```yaml
max_fix_iterations:
  static: 3
  runtime: 2

oscillation_window: 5
min_oscillation_repeats: 2

timeouts:
  edit: 600
  static: 300
  runtime: 300
  fix: 300
```

**Oscillation Detection**:
Detects when the same error signature appears repeatedly (e.g., fix → error → fix → same error).

---

### AIM Integration (`aim_integration.py`)

Capability-based routing to AI tools via the AIM registry.

```python
from core.engine.aim_integration import execute_with_aim, is_aim_available

# Check if AIM is available
if is_aim_available():
    # Use capability routing
    result = execute_with_aim(
        capability="code_generation",
        payload={
            "files": ["src/auth.py"],
            "prompt": "Add error handling",
            "language": "python"
        },
        fallback_tool="aider",
        context={"worktree_path": "/path/to/worktree"},
        run_id="run-2025-11-22-001",
        ws_id="ws-feature-auth"
    )
else:
    # Fallback to direct tool invocation
    result = run_tool("aider", context)
```

**How It Works**:
1. AIM registry maps capabilities to tools (e.g., `code_generation` → `["aider", "jules", "claude-cli"]`)
2. Registry selects best available tool based on installation status
3. Falls back through tool chain if primary tool fails
4. Logs all invocations for audit trail

See `aim/README.md` for AIM registry details.

---

### Recovery Manager (`recovery_manager.py`)

Coordinates recovery strategies after failures.

```python
from core.engine.recovery_manager import RecoveryManager

# Initialize recovery manager
recovery = RecoveryManager()

# Attempt recovery after failure
recovered = recovery.attempt_recovery(
    run_id="run-2025-11-22-001",
    ws_id="ws-feature-auth",
    error=exception,
    context={"step": "static"}
)

if recovered:
    # Retry step
    result = run_static_step(...)
```

**Recovery Strategies**:
1. **Automatic retry** - Retry with exponential backoff
2. **Context reduction** - Reduce file scope and retry
3. **Tool fallback** - Try alternative tool
4. **Manual intervention** - Pause and request human review

---

### Metrics and Telemetry (`metrics.py`)

Tracks execution metrics for observability.

```python
from core.engine.metrics import MetricsAggregator

# Create aggregator
metrics = MetricsAggregator()

# Record execution
metrics.record_step_execution(
    ws_id="ws-feature-auth",
    step="edit",
    duration_sec=45.2,
    success=True
)

# Get summary
summary = metrics.get_summary()
# {
#     "total_workstreams": 5,
#     "successful": 4,
#     "failed": 1,
#     "total_duration_sec": 320.5,
#     "avg_duration_sec": 64.1
# }
```

---

### Cost Tracking (`cost_tracker.py`)

Tracks API costs and enforces budgets.

```python
from core.engine.cost_tracker import CostTracker

# Initialize tracker
tracker = CostTracker(budget_usd=10.0)

# Record token usage
tracker.record_usage(
    model="gpt-4",
    input_tokens=1000,
    output_tokens=500
)

# Check budget
if tracker.is_over_budget():
    raise BudgetExceededError(f"Budget exceeded: ${tracker.total_cost_usd:.2f}")
```

---

## Execution Flow

### Single Workstream Flow

```
1. Load bundle from database
2. Create worktree
3. Execute EDIT step
   - Route via AIM if capability specified
   - Otherwise use tool profile directly
   - Record step attempt in database
4. Execute STATIC step
   - Run linters/type checkers
   - If errors → FIX loop (max 3 iterations)
   - Circuit breaker prevents infinite loops
5. Execute RUNTIME step
   - Run tests
   - If failures → FIX loop (max 2 iterations)
6. Update workstream status to "completed" or "failed"
7. Record final metrics
```

### Parallel Execution Flow

```
1. Load all bundles
2. Validate dependencies and detect cycles
3. Build execution plan (waves)
4. For each wave:
   a. Create worker pool (size = max_workers)
   b. Submit workstreams to workers
   c. Wait for wave completion
   d. Check for failures (fail_fast mode)
5. Aggregate results
6. Return per-workstream outcomes
```

---

## Configuration

### Environment Variables

- **`PIPELINE_DRY_RUN`** - Skip external tool invocations (default: `0`)
- **`PIPELINE_MAX_WORKERS`** - Maximum parallel workers (default: `4`)
- **`PIPELINE_TIMEOUT_SEC`** - Global timeout for all steps (default: `3600`)
- **`AIM_REGISTRY_PATH`** - Path to AIM registry (optional, auto-detected)

### Configuration Files

- **`config/tool_profiles.json`** - Tool adapter configurations
- **`config/circuit_breaker_config.yaml`** - Circuit breaker settings
- **`config/decomposition_rules.yaml`** - Workstream decomposition rules

---

## Testing

Tests are located in `tests/orchestrator/` and `tests/integration/`:

```bash
# Unit tests
pytest tests/orchestrator/test_orchestrator.py -v
pytest tests/orchestrator/test_scheduler.py -v
pytest tests/orchestrator/test_circuit_breakers.py -v

# Integration tests
pytest tests/integration/test_parallel_execution.py -v
```

---

## Best Practices

1. **Always set timeouts** - Prevents hanging on unresponsive tools
2. **Use circuit breakers** - Prevents infinite FIX loops
3. **Monitor metrics** - Track execution time and success rates
4. **Test in dry-run mode** - Validate logic without running tools
5. **Handle tool failures gracefully** - Use fallback chains via AIM
6. **Respect conflict groups** - Don't run conflicting workstreams in parallel
7. **Log all state transitions** - Use event bus for observability

---

## Migration from Legacy

Legacy import paths are deprecated:

```python
# ❌ DEPRECATED
from src.pipeline.orchestrator import run_workstream
from src.pipeline.tools import run_tool

# ✅ USE INSTEAD
from core.engine.orchestrator import run_workstream
from core.engine.tools import run_tool
```

---

## Related Documentation

- **State Management**: `core/state/README.md` - Database and CRUD operations
- **AIM Integration**: `aim/README.md` - Capability-based tool routing
- **Tool Profiles**: `config/tool_profiles.json` - Tool configuration
- **Circuit Breakers**: `config/circuit_breaker_config.yaml` - Fault tolerance settings
- **Parent Module**: `core/README.md` - Core pipeline overview
- **Architecture**: `docs/architecture/orchestration.md` - Design decisions
