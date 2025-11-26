# Tool Adapters

> **Module**: `core.engine.adapters`  
> **Purpose**: Tool-specific adapter implementations  
> **Layer**: Integration/Adapters  
> **Status**: Production

---

## Overview

The `core/engine/adapters/` directory contains adapter implementations for AI coding tools. Adapters provide:

- **Unified interface** - Consistent API across different tools
- **Configuration management** - Tool-specific argument mapping
- **Error handling** - Graceful degradation and retries
- **Result normalization** - Standardized output format

All adapters implement the `BaseAdapter` interface defined in `base.py`.

---

## Directory Structure

```
core/engine/adapters/
├── __init__.py          # Adapter registry
├── base.py              # Base adapter interface
├── aider_adapter.py     # Aider integration
├── claude_adapter.py    # Claude CLI integration
└── codex_adapter.py     # Codex integration
```

---

## Available Adapters

### Aider Adapter (`aider_adapter.py`)

**Tool**: [Aider](https://github.com/paul-gauthier/aider)  
**Capabilities**: Code generation, editing, refactoring  
**Status**: ✅ Production

#### Configuration

```python
from core.engine.adapters.aider_adapter import AiderAdapter

adapter = AiderAdapter(
    binary_path="aider",  # Path to aider executable
    default_args=[
        "--yes",              # Auto-confirm changes
        "--no-auto-commits",  # Don't auto-commit
        "--model", "gpt-4"    # Model selection
    ],
    env_vars={
        "AIDER_NO_GIT": "1"   # Disable git integration
    },
    timeout_sec=300
)
```

#### Usage

```python
from core.engine.adapters.aider_adapter import AiderAdapter

adapter = AiderAdapter()

result = adapter.execute(
    prompt="Add error handling to the authenticate function",
    files=["src/auth.py"],
    context={
        "worktree_path": "/path/to/worktree",
        "timeout_sec": 300
    }
)

# Result structure:
# {
#     "success": True,
#     "exit_code": 0,
#     "stdout": "...",
#     "stderr": "",
#     "files_modified": ["src/auth.py"],
#     "elapsed_sec": 45.2
# }
```

#### Supported Features

- ✅ File editing with context
- ✅ Multi-file edits
- ✅ Streaming output
- ✅ Model selection (GPT-4, Claude, etc.)
- ✅ Auto-commit control
- 🔜 Architect mode
- 🔜 Test generation

---

### Claude CLI Adapter (`claude_adapter.py`)

**Tool**: Claude CLI  
**Capabilities**: Code generation, analysis, refactoring  
**Status**: ✅ Production

#### Configuration

```python
from core.engine.adapters.claude_adapter import ClaudeAdapter

adapter = ClaudeAdapter(
    binary_path="claude",
    api_key="sk-...",  # Or via ANTHROPIC_API_KEY env var
    model="claude-3-opus-20240229",
    max_tokens=4096,
    timeout_sec=300
)
```

#### Usage

```python
result = adapter.execute(
    prompt="Refactor this function to use async/await",
    files=["src/api.py"],
    context={
        "worktree_path": "/path/to/worktree",
        "model": "claude-3-sonnet-20240229"  # Override default
    }
)
```

#### Supported Features

- ✅ Code generation
- ✅ Multi-file analysis
- ✅ Streaming responses
- ✅ Model selection (Opus, Sonnet, Haiku)
- ✅ Token usage tracking
- 🔜 Project-wide refactoring
- 🔜 Test generation

---

### Codex Adapter (`codex_adapter.py`)

**Tool**: OpenAI Codex  
**Capabilities**: Code completion, generation  
**Status**: ✅ Beta

#### Configuration

```python
from core.engine.adapters.codex_adapter import CodexAdapter

adapter = CodexAdapter(
    api_key="sk-...",  # Or via OPENAI_API_KEY env var
    model="gpt-4",
    temperature=0.2,
    max_tokens=2048,
    timeout_sec=180
)
```

#### Usage

```python
result = adapter.execute(
    prompt="Generate unit tests for the User class",
    files=["src/models.py"],
    context={"test_framework": "pytest"}
)
```

#### Supported Features

- ✅ Code generation
- ✅ Single-file focus
- ✅ Temperature control
- 🔜 Multi-file context
- 🔜 Function calling

---

## Base Adapter Interface

All adapters must implement the `BaseAdapter` interface:

```python
# core/engine/adapters/base.py

from abc import ABC, abstractmethod
from typing import Dict, List, Any

class BaseAdapter(ABC):
    """
    Base interface for tool adapters.
    
    All adapters must implement this interface to ensure
    consistent behavior across different tools.
    """
    
    @abstractmethod
    def execute(
        self,
        prompt: str,
        files: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute tool with given prompt and files.
        
        Args:
            prompt: Natural language instruction
            files: List of file paths to operate on
            context: Additional context (worktree_path, timeout, etc.)
        
        Returns:
            Result dictionary with keys:
            - success: bool
            - exit_code: int
            - stdout: str
            - stderr: str
            - files_modified: List[str]
            - elapsed_sec: float
            - error: str? (if success=False)
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate adapter configuration.
        
        Returns:
            True if configuration is valid
        
        Raises:
            ConfigError: If configuration is invalid
        """
        pass
    
    def get_capabilities(self) -> Dict[str, bool]:
        """
        Report adapter capabilities.
        
        Returns:
            Dictionary of capability flags:
            - multi_file: bool
            - streaming: bool
            - model_selection: bool
            - cost_tracking: bool
        """
        return {
            "multi_file": False,
            "streaming": False,
            "model_selection": False,
            "cost_tracking": False
        }
```

---

## Adapter Registry

The adapter registry manages tool discovery and instantiation:

```python
# core/engine/adapters/__init__.py

from core.engine.adapters.base import BaseAdapter
from core.engine.adapters.aider_adapter import AiderAdapter
from core.engine.adapters.claude_adapter import ClaudeAdapter
from core.engine.adapters.codex_adapter import CodexAdapter

# Adapter registry
ADAPTERS = {
    "aider": AiderAdapter,
    "claude": ClaudeAdapter,
    "codex": CodexAdapter,
}

def get_adapter(tool_id: str, **kwargs) -> BaseAdapter:
    """
    Get adapter instance by tool ID.
    
    Args:
        tool_id: Tool identifier (e.g., "aider", "claude")
        **kwargs: Adapter-specific configuration
    
    Returns:
        Configured adapter instance
    
    Raises:
        ValueError: If tool_id not found
    """
    if tool_id not in ADAPTERS:
        raise ValueError(f"Unknown tool: {tool_id}")
    
    adapter_class = ADAPTERS[tool_id]
    return adapter_class(**kwargs)

def list_adapters() -> List[str]:
    """List all registered adapters."""
    return list(ADAPTERS.keys())
```

### Usage

```python
from core.engine.adapters import get_adapter, list_adapters

# List available adapters
adapters = list_adapters()
# Returns: ["aider", "claude", "codex"]

# Get adapter instance
adapter = get_adapter("aider", timeout_sec=300)
result = adapter.execute(
    prompt="Add logging",
    files=["src/api.py"],
    context={"worktree_path": "."}
)
```

---

## Creating a New Adapter

To add support for a new tool:

### 1. Create Adapter Module

```python
# core/engine/adapters/mytool_adapter.py

from core.engine.adapters.base import BaseAdapter
from typing import Dict, List, Any
import subprocess

class MyToolAdapter(BaseAdapter):
    """Adapter for MyTool."""
    
    def __init__(self, binary_path: str = "mytool", timeout_sec: int = 300):
        self.binary_path = binary_path
        self.timeout_sec = timeout_sec
    
    def execute(
        self,
        prompt: str,
        files: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute MyTool."""
        
        # Build command
        cmd = [
            self.binary_path,
            "--prompt", prompt,
            "--files", *files
        ]
        
        # Execute
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=context.get("timeout_sec", self.timeout_sec),
                cwd=context.get("worktree_path", ".")
            )
            
            return {
                "success": result.returncode == 0,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "files_modified": self._parse_modified_files(result.stdout),
                "elapsed_sec": 0.0  # Measure if needed
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "exit_code": -1,
                "error": "Tool execution timeout"
            }
    
    def validate_config(self) -> bool:
        """Validate MyTool is installed."""
        try:
            subprocess.run(
                [self.binary_path, "--version"],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def get_capabilities(self) -> Dict[str, bool]:
        return {
            "multi_file": True,
            "streaming": False,
            "model_selection": False,
            "cost_tracking": False
        }
```

### 2. Register Adapter

```python
# core/engine/adapters/__init__.py

from core.engine.adapters.mytool_adapter import MyToolAdapter

ADAPTERS = {
    "aider": AiderAdapter,
    "claude": ClaudeAdapter,
    "codex": CodexAdapter,
    "mytool": MyToolAdapter,  # Add here
}
```

### 3. Add Tests

```python
# tests/adapters/test_mytool_adapter.py

from core.engine.adapters.mytool_adapter import MyToolAdapter

def test_mytool_execution():
    adapter = MyToolAdapter()
    
    result = adapter.execute(
        prompt="Test prompt",
        files=["test.py"],
        context={"worktree_path": "/tmp"}
    )
    
    assert result["success"]
    assert result["exit_code"] == 0
```

---

## Configuration Management

Adapters can be configured via:

1. **Direct instantiation**:
   ```python
   adapter = AiderAdapter(binary_path="/usr/local/bin/aider")
   ```

2. **Tool profiles** (`config/tool_profiles.json`):
   ```json
   {
     "aider": {
       "binary": "aider",
       "args": ["--yes", "--no-auto-commits"],
       "timeout_sec": 300
     }
   }
   ```

3. **Environment variables**:
   ```bash
   export AIDER_BINARY=/usr/local/bin/aider
   export ANTHROPIC_API_KEY=sk-...
   ```

---

## Error Handling

Adapters should handle errors gracefully:

```python
def execute(self, prompt, files, context):
    try:
        # Execute tool
        result = self._run_tool(...)
        
        if result.returncode != 0:
            return {
                "success": False,
                "exit_code": result.returncode,
                "error": f"Tool failed: {result.stderr}"
            }
        
        return {"success": True, ...}
    
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Tool execution timeout"
        }
    
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Tool binary not found: {self.binary_path}"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {e}"
        }
```

---

## Testing

Tests for adapters are in `tests/adapters/`:

```bash
# Run adapter tests
pytest tests/adapters/ -v

# Test specific adapter
pytest tests/adapters/test_aider_adapter.py -v

# Test with mocking (no actual tool execution)
pytest tests/adapters/ -v --mock
```

---

## Best Practices

1. **Always validate configuration** - Check tool availability before execution
2. **Handle timeouts gracefully** - Set reasonable defaults and allow overrides
3. **Normalize output** - Return consistent result structure
4. **Log all invocations** - Record commands for debugging
5. **Support dry-run mode** - Allow testing without actual execution
6. **Track costs** - Report token usage for API-based tools
7. **Use streaming when possible** - Provide progress feedback

---

## Related Documentation

- **Base Interface**: `core/engine/adapters/base.py` - Adapter contract
- **Tool Profiles**: `config/tool_profiles.json` - Tool configuration
- **Orchestrator**: `core/engine/README.md` - Execution engine
- **AIM Integration**: `aim/README.md` - Capability-based routing

---

**For AI Tools**: Adapters provide a unified interface to execute coding tools. When adding new tool support, implement the `BaseAdapter` interface and register in the adapter registry.
