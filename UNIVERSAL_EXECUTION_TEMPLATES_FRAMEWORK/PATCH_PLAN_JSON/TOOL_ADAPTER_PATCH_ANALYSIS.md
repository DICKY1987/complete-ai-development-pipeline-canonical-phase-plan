# Tool Adapter Interface Patch Analysis

**Patch ID**: 006-tool-adapter-interface  
**Created**: 2025-11-23T11:38:26.103Z  
**Priority**: MEDIUM  
**Operations**: 3

---

## Overview

This patch documents the **Tool Adapter Interface Pattern** - a critical abstraction that decouples task execution from specific tool implementations. It enables the system to route tasks (code editing, testing, validation) to external tools (aider, pytest, git) through a uniform interface.

---

## Source Files (3 Implementation Files)

1. **`core/adapters/base.py`** (123 lines)
   - `ToolConfig` - Tool configuration dataclass
   - `ExecutionResult` - Execution result dataclass
   - `ToolAdapter` - Abstract base class

2. **`core/adapters/subprocess_adapter.py`** (128 lines)
   - `SubprocessAdapter` - Concrete implementation using subprocess

3. **`core/adapters/registry.py`** (107 lines)
   - `AdapterRegistry` - Tool adapter management and lookup

**Total**: 358 lines of implementation code

---

## What This Patch Adds

### 1. Tool Adapter Pattern Documentation (`/meta/tool_adapter_pattern`)

**Complete specification** including:

#### Components

**ToolConfig** (Configuration):
- `tool_id` - Unique identifier (e.g., 'aider', 'pytest')
- `kind` - Category: 'tool', 'validator', 'analyzer'
- `command` - Base command to execute
- `capabilities` - Supported task_kinds and domains
- `limits` - Resource constraints (timeout, max_parallel)
- `safety_tier` - Safety level: 'low', 'medium', 'high'

**ExecutionResult** (Output):
- `success` - Boolean execution status
- `stdout/stderr` - Output capture
- `exit_code` - Process exit code
- `duration_seconds` - Execution time
- `error_message` - Optional error description
- `metadata` - Additional context

**ToolAdapter** (Interface):
- `execute()` - Execute task request (abstract)
- `validate_request()` - Validate request compatibility (abstract)
- `supports_task()` - Check task_kind/domain support
- `get_timeout()` - Get configured timeout

**SubprocessAdapter** (Implementation):
- Executes tools via `subprocess.run`
- Handles timeout with `TimeoutExpired` exception
- Captures stdout/stderr
- Tracks execution duration
- Returns structured `ExecutionResult`

**AdapterRegistry** (Management):
- Loads adapters from `router_config.json`
- Registers adapters by `tool_id`
- Finds adapters by task_kind/domain
- Provides direct tool lookup

#### Usage Flow

**Initialization**:
1. Create `AdapterRegistry` with config path
2. Registry loads apps from `router_config.json`
3. For each app, creates `ToolConfig`
4. Instantiates `SubprocessAdapter`
5. Registers adapter by `tool_id`

**Task Routing**:
1. Receive `ExecutionRequest` (task_kind, domain)
2. Call `registry.find_for_task(task_kind, domain)`
3. Get list of capable adapters
4. Select adapter (first, preferred, etc.)
5. Call `adapter.execute(request, timeout)`
6. Receive `ExecutionResult`
7. Store result or handle error

### 2. Adapter Implementations (`/meta/tool_adapter_pattern/adapter_implementations`)

**Current**:
- ✅ `SubprocessAdapter` - Basic subprocess execution

**Planned**:
- `AiderAdapter` - Specialized for aider code editing
- `PytestAdapter` - Specialized for pytest testing
- `GitAdapter` - Specialized for git operations
- `HTTPAdapter` - For HTTP API calls

### 3. Design Benefits (`/meta/tool_adapter_pattern/design_benefits`)

- **Decoupling**: Task logic separate from tool details
- **Testability**: Easy to mock adapters
- **Extensibility**: Add tools via interface implementation
- **Substitutability**: Swap tools without orchestration changes
- **Capability Discovery**: Find capable tools for any task
- **Configuration-Driven**: Tools defined in JSON, not hardcoded

### 4. Security Considerations (`/meta/tool_adapter_pattern/security_considerations`)

**Shell Injection Risk**:
- `shell=True` in subprocess enables injection
- Mitigation: Validate inputs, use `shell=False` with list args, safety tier enforcement

**Timeout Enforcement**:
- Risk: Runaway processes
- Mitigation: Always use timeout parameter

**Resource Limits**:
- Risk: Too many parallel executions
- Mitigation: Enforce `max_parallel` from config

### 5. Integration Points (`/meta/tool_adapter_pattern/integration_points`)

- **Task Router**: Uses `AdapterRegistry` to route tasks
- **Execution Engine**: Orchestrator executes workstream steps via adapters
- **Router Config**: `router_config.v1.json` defines available tools

### 6. Implementation Status (`/implementation/tool_adapters`)

**Completion**: 30%

**Implemented**:
- ✅ Base classes and dataclasses
- ✅ SubprocessAdapter with timeout
- ✅ AdapterRegistry with config loading

**Missing**:
- ❌ Enhanced command building
- ❌ Specialized adapters (Aider, Pytest, Git)
- ❌ HTTPAdapter
- ❌ Input streaming
- ❌ Structured output parsing
- ❌ Safety tier enforcement
- ❌ max_parallel enforcement (semaphore)

---

## Key Design Patterns

### Adapter Pattern (Gang of Four)

**Intent**: Convert interface of a class into another interface clients expect

**Application**:
- **Target Interface**: `ToolAdapter` with `execute()` and `validate_request()`
- **Adaptee**: External tools (aider, pytest, git via subprocess)
- **Adapter**: `SubprocessAdapter` wraps subprocess calls
- **Client**: Orchestration engine calls adapter interface

### Registry Pattern

**Intent**: Centralized registration and lookup of components

**Application**:
- **Registry**: `AdapterRegistry` stores tool adapters
- **Registration**: `register(tool_id, adapter)` adds adapters
- **Lookup**: `get(tool_id)` retrieves by ID
- **Discovery**: `find_for_task(task_kind, domain)` finds capable adapters

---

## Router Config Structure

The adapters are configured via `router_config.v1.json`:

```json
{
  "apps": {
    "aider": {
      "kind": "tool",
      "command": "aider --yes --no-git",
      "capabilities": {
        "task_kinds": ["code_edit"],
        "domains": ["python", "javascript"]
      },
      "limits": {
        "timeout_seconds": 600,
        "max_parallel": 1
      },
      "safety_tier": "medium"
    },
    "pytest": {
      "kind": "validator",
      "command": "pytest",
      "capabilities": {
        "task_kinds": ["test"],
        "domains": ["python"]
      },
      "limits": {
        "timeout_seconds": 300,
        "max_parallel": 3
      },
      "safety_tier": "high"
    }
  }
}
```

---

## Example Usage

### Load Adapters

```python
from core.adapters.registry import AdapterRegistry

# Initialize registry with config
registry = AdapterRegistry("router_config.v1.json")

# List available tools
tools = registry.list_tools()  # ['aider', 'pytest', 'git', ...]
```

### Route Task to Tool

```python
# Find adapters for task
adapters = registry.find_for_task(
    task_kind="code_edit",
    domain="python"
)

# Execute via first capable adapter
if adapters:
    adapter = adapters[0]
    request = {
        'request_id': 'req-001',
        'task_kind': 'code_edit',
        'project_id': 'my-project',
        'parameters': {...}
    }
    
    result = adapter.execute(request, timeout=600)
    
    if result.success:
        print(f"Success! Output: {result.stdout}")
    else:
        print(f"Failed: {result.error_message}")
```

### Direct Tool Access

```python
# Get specific tool adapter
aider = registry.get('aider')

if aider:
    result = aider.execute(request)
```

---

## Integration with UET V2

### Workstream Execution

Workstream steps specify tasks that need tool execution:

```json
{
  "step_id": "edit-code",
  "task_kind": "code_edit",
  "domain": "python",
  "parameters": {
    "files": ["src/main.py"],
    "instructions": "Add error handling"
  }
}
```

**Orchestrator**:
1. Reads step from workstream
2. Calls `registry.find_for_task("code_edit", "python")`
3. Selects adapter (e.g., AiderAdapter)
4. Builds `ExecutionRequest` from step
5. Calls `adapter.execute(request)`
6. Stores `ExecutionResult` in database
7. Updates step state (success/failure)

### Task Router

The Task Router (planned) uses adapters:

```python
class TaskRouter:
    def __init__(self, registry: AdapterRegistry):
        self.registry = registry
    
    def route(self, task: Dict) -> ExecutionResult:
        adapters = self.registry.find_for_task(
            task['task_kind'],
            task.get('domain')
        )
        
        # Select best adapter (strategy pattern)
        adapter = self.select_adapter(adapters, task)
        
        # Execute
        return adapter.execute(task)
```

---

## Benefits for AI Agents

### Clear Abstraction

AI agents understand the adapter pattern and can:
- Implement new adapters by extending `ToolAdapter`
- Add tools to `router_config.json`
- Route tasks without knowing tool details

### Configuration-Driven

Tools defined in JSON, not code:
- AI can modify config without code changes
- Easy to enable/disable tools
- Clear capability declarations

### Testability

Mock adapters for testing:

```python
class MockAdapter(ToolAdapter):
    def execute(self, request, timeout=None):
        return ExecutionResult(success=True, stdout="Mock output")
    
    def validate_request(self, request):
        return True

# Use in tests
registry.register('mock', MockAdapter(mock_config))
```

---

## Security Hardening Needed

### Current Issues

1. **Shell Injection**: `shell=True` in `subprocess.run`
2. **No Input Validation**: Request parameters not sanitized
3. **No Safety Tier Enforcement**: `safety_tier` not checked
4. **No Resource Limits**: `max_parallel` not enforced

### Recommended Fixes

```python
# Use shell=False with list args
cmd = ['aider', '--yes', '--no-git', file_path]
result = subprocess.run(cmd, shell=False, ...)

# Validate inputs
import shlex
safe_arg = shlex.quote(user_input)

# Enforce safety tier
if tool_config.safety_tier == 'high':
    # Extra validation
    if not validate_strict(request):
        raise SecurityError("High-tier validation failed")

# Enforce max_parallel with semaphore
semaphore = Semaphore(tool_config.get_max_parallel())
with semaphore:
    result = subprocess.run(...)
```

---

## Next Steps for Implementation

### Phase 1: Hardening (High Priority)
1. ✅ Fix shell injection (use `shell=False` with list args)
2. ✅ Add input validation and sanitization
3. ✅ Implement safety tier enforcement
4. ✅ Add max_parallel enforcement with semaphore

### Phase 2: Specialization (Medium Priority)
5. ✅ Implement `AiderAdapter` with aider-specific logic
6. ✅ Implement `PytestAdapter` with pytest output parsing
7. ✅ Implement `GitAdapter` with git command structuring
8. ✅ Add structured output parsers for each tool

### Phase 3: Enhancement (Lower Priority)
9. Implement `HTTPAdapter` for API calls
10. Add input streaming support
11. Add adapter health checks
12. Implement adapter selection strategies (round-robin, load-based)

---

## Statistics

| Metric | Value |
|--------|-------|
| **Lines of Code** | 358 |
| **Classes** | 5 |
| **Abstract Methods** | 2 |
| **Concrete Adapters** | 1 (SubprocessAdapter) |
| **Planned Adapters** | 4 (Aider, Pytest, Git, HTTP) |
| **Completion** | 30% |
| **Workstream** | WS-03-02A |
| **Design Pattern** | Adapter + Registry |

---

## Validation After Applying

```python
import json
plan = json.loads(open("UET_V2_MASTER_PLAN.json").read())

# Check tool_adapter_pattern added
assert "tool_adapter_pattern" in plan["meta"]

# Check components documented
components = plan["meta"]["tool_adapter_pattern"]["components"]
assert "tool_config" in components
assert "execution_result" in components
assert "tool_adapter" in components
assert "subprocess_adapter" in components
assert "adapter_registry" in components

# Check implementation status
impl = plan["implementation"]["tool_adapters"]
assert impl["completion_percentage"] == 30
assert len(impl["implemented_components"]) == 5
assert len(impl["missing_components"]) == 7
```

---

## Summary

This patch documents the **Tool Adapter Interface Pattern** - a foundational abstraction for the UET V2 framework. It:

✅ **Decouples** task execution from tool implementation  
✅ **Enables** tool substitution and testing  
✅ **Provides** uniform interface for diverse tools  
✅ **Documents** current implementation (30% complete)  
✅ **Identifies** security issues and next steps  
✅ **Guides** future adapter development

**Priority**: MEDIUM - Important architectural pattern, but implementation is ongoing

**Impact**: Metadata enrichment + implementation roadmap

**Ready to apply**: Yes - no breaking changes, adds documentation context
