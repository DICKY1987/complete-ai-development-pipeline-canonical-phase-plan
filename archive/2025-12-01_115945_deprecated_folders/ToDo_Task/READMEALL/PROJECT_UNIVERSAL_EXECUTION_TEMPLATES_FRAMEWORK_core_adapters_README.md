---
doc_id: DOC-GUIDE-PROJECT-UNIVERSAL-EXECUTION-TEMPLATES-1593
---

# core/adapters

**Purpose**: Tool integration layer providing uniform interfaces for executing external tools (CLI, API, custom implementations).

## Overview

Adapters provide a consistent execution interface for heterogeneous tools:
- **Subprocess adapters** - Execute CLI tools (aider, pytest, ruff, git)
- **API adapters** - Integrate with REST/GraphQL services
- **Custom adapters** - Domain-specific tool implementations

All adapters implement the same contract, allowing the engine to treat tools uniformly.

## Key Files

- **`base.py`** - ToolAdapter abstract base class
- **`registry.py`** - AdapterRegistry for tool lookup and management
- **`subprocess_adapter.py`** - CLI tool execution
- **`api_adapter.py`** - HTTP/REST API integration
- **`factory.py`** - Adapter creation and configuration

## Dependencies

**Depends on:**
- `schema/` - For execution_request.v1.json validation
- `core/state/` - For execution logging

**Used by:**
- `core/engine/` - For task execution

## Adapter Interface

All adapters implement this contract:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class ToolAdapter(ABC):
    """Base class for all tool adapters"""
    
    @abstractmethod
    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """
        Execute a tool with the given request.
        
        Args:
            request: ExecutionRequest with action, context, params
            
        Returns:
            ExecutionResult with status, output, errors
        """
        pass
    
    @abstractmethod
    def validate_request(self, request: ExecutionRequest) -> bool:
        """Validate request before execution"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Return tool capabilities (domains, actions)"""
        pass
```

## Adapter Registry

Central registry for discovering and instantiating adapters.

### Usage
```python
from core.adapters import AdapterRegistry

# Load registry from config
registry = AdapterRegistry("router_config.json")

# Get adapter by tool name
aider_adapter = registry.get("aider")
pytest_adapter = registry.get("pytest")

# Find adapters for a task
capable = registry.find_for_task(
    action="code_edit",
    domain="python"
)
# Returns: [aider_adapter, cursor_adapter]

# List all registered tools
tools = registry.list_tools()
# Returns: ["aider", "pytest", "ruff", "mypy", ...]
```

### Registry Configuration

`router_config.json`:
```json
{
  "tools": {
    "aider": {
      "adapter_type": "subprocess",
      "capabilities": {
        "domains": ["python", "javascript", "code"],
        "actions": ["edit", "refactor", "generate"]
      },
      "config": {
        "command": "aider",
        "timeout": 300,
        "max_retries": 3
      }
    },
    "pytest": {
      "adapter_type": "subprocess",
      "capabilities": {
        "domains": ["python", "testing"],
        "actions": ["test", "verify"]
      },
      "config": {
        "command": "pytest",
        "args": ["-v", "--tb=short"]
      }
    }
  }
}
```

## Subprocess Adapter

Executes CLI tools via subprocess.

### Usage
```python
from core.adapters.subprocess_adapter import SubprocessAdapter

# Create adapter
adapter = SubprocessAdapter(
    tool_name="aider",
    command="aider",
    timeout=300
)

# Execute
request = ExecutionRequest(
    action="edit",
    context={
        "files": ["main.py"],
        "instructions": "Add type hints"
    }
)

result = adapter.execute(request)

if result.success:
    print(f"Output: {result.stdout}")
else:
    print(f"Error: {result.stderr}")
    print(f"Exit code: {result.exit_code}")
```

### Features
- **Timeout handling** - Kills process after timeout
- **Stream output** - Capture stdout/stderr
- **Environment injection** - Pass environment variables
- **Working directory** - Set execution context
- **Signal handling** - Proper subprocess cleanup

### Implementation
```python
import subprocess
from typing import Optional, Dict

class SubprocessAdapter(ToolAdapter):
    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        cmd = self._build_command(request)
        env = self._build_environment(request)
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=request.context.get("working_dir"),
                text=True
            )
            
            stdout, stderr = process.communicate(timeout=self.timeout)
            
            return ExecutionResult(
                success=process.returncode == 0,
                stdout=stdout,
                stderr=stderr,
                exit_code=process.returncode
            )
            
        except subprocess.TimeoutExpired:
            process.kill()
            return ExecutionResult(
                success=False,
                error="Execution timeout"
            )
```

## API Adapter

Integrates with REST/GraphQL APIs.

### Usage
```python
from core.adapters.api_adapter import APIAdapter

# Create adapter
adapter = APIAdapter(
    base_url="https://api.example.com",
    auth_token="secret_token"
)

# Execute API call
request = ExecutionRequest(
    action="analyze",
    context={
        "endpoint": "/code/analyze",
        "method": "POST",
        "payload": {
            "file": "main.py",
            "language": "python"
        }
    }
)

result = adapter.execute(request)

if result.success:
    data = result.response_data
    print(f"Analysis: {data}")
```

### Features
- **Authentication** - Bearer tokens, API keys, OAuth
- **Retry logic** - Exponential backoff for transient failures
- **Rate limiting** - Respect API rate limits
- **Timeout** - Request timeout handling
- **SSL verification** - Configurable certificate validation

## Custom Adapter

Implement domain-specific tool integration.

### Example: Language Server Protocol Adapter
```python
from core.adapters.base import ToolAdapter

class LSPAdapter(ToolAdapter):
    """Adapter for Language Server Protocol tools"""
    
    def __init__(self, language: str, server_command: str):
        self.language = language
        self.server_command = server_command
        self.client = None
    
    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        if not self.client:
            self._start_server()
        
        action = request.action
        
        if action == "analyze":
            return self._analyze_code(request)
        elif action == "refactor":
            return self._refactor_code(request)
        else:
            raise ValueError(f"Unsupported action: {action}")
    
    def _start_server(self):
        # Initialize LSP client
        self.client = LSPClient(self.server_command)
        self.client.initialize()
    
    def _analyze_code(self, request):
        # Use LSP diagnostics
        diagnostics = self.client.get_diagnostics(request.context["file"])
        return ExecutionResult(
            success=True,
            data={"diagnostics": diagnostics}
        )
    
    def get_capabilities(self):
        return {
            "domains": [self.language, "code"],
            "actions": ["analyze", "refactor", "complete"]
        }
```

### Registering Custom Adapter
```json
{
  "tools": {
    "pylsp": {
      "adapter_type": "custom",
      "adapter_class": "LSPAdapter",
      "adapter_module": "core.adapters.lsp_adapter",
      "capabilities": {
        "domains": ["python", "code"],
        "actions": ["analyze", "refactor"]
      },
      "config": {
        "language": "python",
        "server_command": "pylsp"
      }
    }
  }
}
```

## Execution Request Format

```python
@dataclass
class ExecutionRequest:
    """Standard request format for all adapters"""
    
    action: str              # What to do: "edit", "test", "analyze"
    domain: str              # Domain: "python", "javascript", "code"
    context: Dict[str, Any]  # Tool-specific context
    params: Dict[str, Any]   # Additional parameters
    timeout: Optional[int]   # Override default timeout
```

### Example Requests

**Code editing:**
```python
ExecutionRequest(
    action="edit",
    domain="python",
    context={
        "files": ["main.py", "utils.py"],
        "instructions": "Add error handling to all functions"
    },
    params={
        "model": "gpt-4",
        "auto_commit": True
    }
)
```

**Testing:**
```python
ExecutionRequest(
    action="test",
    domain="python",
    context={
        "test_files": ["tests/test_main.py"],
        "markers": ["unit", "not slow"]
    },
    params={
        "verbose": True,
        "coverage": True
    }
)
```

## Execution Result Format

```python
@dataclass
class ExecutionResult:
    """Standard result format from all adapters"""
    
    success: bool            # Did execution succeed?
    stdout: str              # Standard output
    stderr: str              # Standard error
    exit_code: int           # Process exit code (subprocess only)
    data: Dict[str, Any]     # Structured result data
    error: Optional[str]     # Error message if failed
    duration: float          # Execution time in seconds
```

## Error Handling

Adapters handle errors consistently:

```python
try:
    result = adapter.execute(request)
except ToolNotFoundError:
    # Tool command not available
    logger.error(f"Tool {tool_name} not found in PATH")
except ExecutionTimeoutError:
    # Execution exceeded timeout
    logger.error(f"Execution timed out after {timeout}s")
except ValidationError as e:
    # Request validation failed
    logger.error(f"Invalid request: {e}")
except ToolExecutionError as e:
    # General execution failure
    logger.error(f"Execution failed: {e}")
```

## Testing

Test coverage: 27/27 tests passing

```bash
# Run adapter tests
pytest tests/adapters/ -v

# Specific adapter
pytest tests/adapters/test_subprocess_adapter.py -v
pytest tests/adapters/test_api_adapter.py -v

# Mock external tools
pytest tests/adapters/ -v --mock-subprocess
```

### Test Examples

```python
def test_subprocess_adapter_success():
    adapter = SubprocessAdapter("echo", "echo")
    request = ExecutionRequest(
        action="test",
        domain="shell",
        context={"args": ["Hello, World!"]}
    )
    
    result = adapter.execute(request)
    
    assert result.success
    assert "Hello, World!" in result.stdout
    assert result.exit_code == 0

def test_subprocess_adapter_timeout():
    adapter = SubprocessAdapter("sleep", "sleep", timeout=1)
    request = ExecutionRequest(
        action="test",
        domain="shell",
        context={"args": ["10"]}  # Sleep 10 seconds
    )
    
    result = adapter.execute(request)
    
    assert not result.success
    assert "timeout" in result.error.lower()
```

## Common Patterns

### Pattern 1: Adapter with Retry
```python
from core.engine.resilience import ResilientExecutor

executor = ResilientExecutor()
executor.register_tool("flaky_tool", max_retries=3)

adapter = registry.get("flaky_tool")
result = executor.execute("flaky_tool", lambda: adapter.execute(request))
```

### Pattern 2: Adapter Chaining
```python
# Execute multiple tools in sequence
tools = ["format", "lint", "test"]

results = []
for tool_name in tools:
    adapter = registry.get(tool_name)
    result = adapter.execute(request)
    results.append(result)
    
    if not result.success:
        break  # Stop on first failure
```

### Pattern 3: Parallel Adapter Execution
```python
from concurrent.futures import ThreadPoolExecutor

# Run multiple adapters concurrently
adapters = [registry.get(t) for t in ["lint", "test", "typecheck"]]

with ThreadPoolExecutor(max_workers=3) as pool:
    futures = [pool.submit(a.execute, request) for a in adapters]
    results = [f.result() for f in futures]
```

## Adding a New Adapter

1. **Create adapter class:**
```python
# core/adapters/my_adapter.py
from core.adapters.base import ToolAdapter

class MyAdapter(ToolAdapter):
    def execute(self, request):
        # Implementation
        pass
    
    def validate_request(self, request):
        # Validation
        pass
    
    def get_capabilities(self):
        return {
            "domains": ["my_domain"],
            "actions": ["my_action"]
        }
```

2. **Register in config:**
```json
{
  "tools": {
    "my_tool": {
      "adapter_type": "custom",
      "adapter_class": "MyAdapter",
      "adapter_module": "core.adapters.my_adapter",
      "capabilities": {
        "domains": ["my_domain"],
        "actions": ["my_action"]
      }
    }
  }
}
```

3. **Add tests:**
```python
# tests/adapters/test_my_adapter.py
def test_my_adapter():
    adapter = MyAdapter()
    result = adapter.execute(request)
    assert result.success
```

## References

- **Specification**: `specs/UET_TASK_ROUTING_SPEC.md`
- **Schemas**: `schema/execution_request.v1.json`
- **Engine usage**: `core/engine/README.md`
- **Tests**: `tests/adapters/`
