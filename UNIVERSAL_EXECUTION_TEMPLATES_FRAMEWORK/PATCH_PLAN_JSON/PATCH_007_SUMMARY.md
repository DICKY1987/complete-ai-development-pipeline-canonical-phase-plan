# Patch 007: Tool Adapter Interface - Summary

**Created**: 2025-11-23T11:38:26.103Z  
**Status**: ✅ READY TO APPLY  
**Priority**: MEDIUM

---

## What Was Done

✅ **Analyzed 3 adapter implementation files**  
✅ **Created patch file**: `007-tool-adapter-interface.json` (3 operations)  
✅ **Created analysis doc**: `TOOL_ADAPTER_PATCH_ANALYSIS.md`  
✅ **Updated apply_patches.py** to include new patch

---

## Source Files Analyzed

**Implementation code** (358 lines total):

1. **`core/adapters/base.py`** (123 lines)
   - `ToolConfig` - Tool configuration dataclass
   - `ExecutionResult` - Result dataclass
   - `ToolAdapter` - Abstract base class

2. **`core/adapters/subprocess_adapter.py`** (128 lines)
   - `SubprocessAdapter` - Concrete subprocess implementation

3. **`core/adapters/registry.py`** (107 lines)
   - `AdapterRegistry` - Tool management and lookup

---

## What Gets Added to Master Plan

### 1. `/meta/tool_adapter_pattern` (Main Documentation)

**Complete pattern specification** including:

#### Components
- **ToolConfig**: Tool metadata (id, kind, command, capabilities, limits, safety tier)
- **ExecutionResult**: Execution output (success, stdout/stderr, exit code, duration, metadata)
- **ToolAdapter**: Abstract interface with `execute()` and `validate_request()`
- **SubprocessAdapter**: Concrete implementation using subprocess
- **AdapterRegistry**: Tool registration and capability-based lookup

#### Usage Flow
- **Initialization**: Load adapters from `router_config.json`
- **Task Routing**: Find capable adapters by task_kind/domain
- **Direct Access**: Get specific tool by tool_id

#### Adapter Implementations
- ✅ **Current**: SubprocessAdapter (basic subprocess execution)
- 📋 **Planned**: AiderAdapter, PytestAdapter, GitAdapter, HTTPAdapter

#### Design Benefits
- Decoupling (task logic ≠ tool details)
- Testability (easy mocking)
- Extensibility (add tools via interface)
- Substitutability (swap implementations)
- Capability discovery (find by task_kind/domain)
- Configuration-driven (router_config.json)

#### Security Considerations
- **Shell Injection**: `shell=True` risk, needs mitigation
- **Timeout Enforcement**: Always use timeout parameter
- **Resource Limits**: Enforce `max_parallel` from config

#### Integration Points
- **Task Router**: Routes tasks to tools via registry
- **Execution Engine**: Orchestrator executes steps via adapters
- **Router Config**: `router_config.v1.json` defines tools

### 2. `/implementation/tool_adapters` (Implementation Status)

**Completion**: 30%

**Implemented** (5 components):
- ToolConfig with supports_task logic
- ExecutionResult with to_dict
- ToolAdapter abstract base
- SubprocessAdapter with timeout
- AdapterRegistry with config loading

**Missing** (7 components):
- Enhanced command building
- Specialized adapters (Aider, Pytest, Git)
- HTTPAdapter
- Input streaming
- Structured output parsing
- Safety tier enforcement
- max_parallel enforcement

---

## Key Design Pattern

### Adapter Pattern (Gang of Four)

**Intent**: Convert interface of a class into another interface clients expect

**Application**:
- **Target**: `ToolAdapter` interface
- **Adaptee**: External tools (subprocess)
- **Adapter**: `SubprocessAdapter`
- **Client**: Orchestration engine

### Registry Pattern

**Centralized** tool registration and lookup:
- Register: `register(tool_id, adapter)`
- Lookup: `get(tool_id)`
- Discovery: `find_for_task(task_kind, domain)`

---

## Router Config Example

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
    }
  }
}
```

---

## Usage Example

```python
# Initialize registry
registry = AdapterRegistry("router_config.v1.json")

# Find adapters for task
adapters = registry.find_for_task(
    task_kind="code_edit",
    domain="python"
)

# Execute via first capable adapter
result = adapters[0].execute({
    'request_id': 'req-001',
    'task_kind': 'code_edit',
    'project_id': 'my-project'
})

if result.success:
    print(f"Success! {result.stdout}")
```

---

## Integration with UET V2

### Workstream Execution Flow

1. Orchestrator reads workstream step
2. Calls `registry.find_for_task(task_kind, domain)`
3. Selects capable adapter
4. Builds `ExecutionRequest` from step
5. Calls `adapter.execute(request)`
6. Stores `ExecutionResult` in database
7. Updates step state (success/failure)

### Task Router (Planned)

```python
class TaskRouter:
    def route(self, task):
        adapters = self.registry.find_for_task(
            task['task_kind'], 
            task.get('domain')
        )
        adapter = self.select_adapter(adapters, task)
        return adapter.execute(task)
```

---

## Security Issues Identified

### Current Risks

1. ❌ **Shell Injection**: `shell=True` in subprocess
2. ❌ **No Input Validation**: Parameters not sanitized
3. ❌ **No Safety Tier Enforcement**: Tier not checked
4. ❌ **No Resource Limits**: `max_parallel` not enforced

### Recommended Fixes

```python
# Use shell=False with list args
cmd = ['aider', '--yes', file_path]
subprocess.run(cmd, shell=False, ...)

# Validate inputs
import shlex
safe_arg = shlex.quote(user_input)

# Enforce safety tier
if config.safety_tier == 'high':
    validate_strict(request)

# Enforce max_parallel
semaphore = Semaphore(config.get_max_parallel())
```

---

## Next Steps (Implementation Roadmap)

### Phase 1: Hardening (High Priority)
1. Fix shell injection (use `shell=False`)
2. Add input validation/sanitization
3. Implement safety tier enforcement
4. Add max_parallel enforcement

### Phase 2: Specialization (Medium Priority)
5. Implement AiderAdapter
6. Implement PytestAdapter
7. Implement GitAdapter
8. Add structured output parsers

### Phase 3: Enhancement (Lower Priority)
9. Implement HTTPAdapter
10. Add input streaming
11. Add health checks
12. Implement selection strategies

---

## Benefits

✅ **Decoupling**: Task execution independent of tool details  
✅ **Testability**: Easy to mock adapters  
✅ **Extensibility**: Add tools without core changes  
✅ **Configuration-Driven**: Tools defined in JSON  
✅ **Capability Discovery**: Find tools by task requirements  
✅ **Clear Abstraction**: Uniform interface for diverse tools

---

## Statistics

| Metric | Value |
|--------|-------|
| **Implementation Lines** | 358 |
| **Classes** | 5 |
| **Current Adapters** | 1 (Subprocess) |
| **Planned Adapters** | 4 (Aider, Pytest, Git, HTTP) |
| **Completion** | 30% |
| **Workstream** | WS-03-02A |
| **Design Patterns** | Adapter + Registry |
| **JSON Operations** | 3 |

---

## Updated Patch Summary

After adding Patch 007:

| Patch | Operations | What It Adds |
|-------|------------|--------------|
| **001** | 22 | Config files, architecture, Phase 7 |
| **002** | 15 | AI tool config, sandbox, docs |
| **003** | 25 | State machines, contracts, DAG |
| **004** | 18 | Complete plan, prompts, errors |
| **005** | 11 | ADRs, design principles, rejected alternatives |
| **007** | 3 | **Tool Adapter pattern, implementation status** |
| **TOTAL** | **94** | **Complete UET V2 Foundation + Patterns** |

---

## How to Apply

```bash
cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\PATCH_PLAN_JSON"

# Apply all 6 patches (including tool adapter patch)
python apply_patches.py
```

**Expected**: `UET_V2_MASTER_PLAN.json` with tool adapter pattern documented

---

## Validation

After applying:

```python
import json
plan = json.loads(open("UET_V2_MASTER_PLAN.json").read())

# Check tool_adapter_pattern added
assert "tool_adapter_pattern" in plan["meta"]

# Check components documented
components = plan["meta"]["tool_adapter_pattern"]["components"]
assert len(components) == 5

# Check implementation status
impl = plan["implementation"]["tool_adapters"]
assert impl["completion_percentage"] == 30
assert len(impl["implemented_components"]) == 5
```

---

**Status**: ✅ **READY TO APPLY**

Patch 007 documents the Tool Adapter Interface - a foundational pattern for routing tasks to external tools! 🔌
