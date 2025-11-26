# Adapter Templates

> **Tool Integration Templates - Connect External Tools to UET Framework**  
> **Purpose**: Bridge between orchestration layer and external tools  
> **Layer**: Adapter (Integration)

---

## 📋 Overview

Adapter templates provide starting points for integrating external tools and services into the UET Framework. They implement the standard adapter interface and handle communication with CLI tools, REST APIs, and custom integrations.

### What's in This Directory

```
adapters/
├── README.md                    # This file
├── INTERFACE.md                 # Adapter interface contract
│
├── subprocess/                  # CLI tool adapters
├── api/                         # REST/GraphQL API adapters
└── custom/                      # Custom integration adapters
```

---

## 🎯 Adapter Types

### 1. Subprocess Adapters (`subprocess/`)

**Purpose**: Wrap command-line tools

**Use Cases**:
- Integrate CLI tools (aider, pytest, ruff, etc.)
- Execute shell commands
- Run scripts and batch files

**Key Templates**:
- `tool-adapter-template.py` - Generic CLI tool wrapper
- `aider-adapter-example.py` - Example aider integration
- `pytest-adapter-example.py` - Example pytest integration

**Interface**:
```python
class SubprocessAdapter:
    def detect_capabilities() -> Dict[str, Any]
    def execute(request: ExecutionRequest) -> ExecutionResult
    def validate_result(result: Any) -> ValidationResult
```

---

### 2. API Adapters (`api/`)

**Purpose**: Integrate REST and GraphQL services

**Use Cases**:
- Connect to REST APIs
- Query GraphQL endpoints
- Integrate cloud services

**Key Templates**:
- `rest-adapter-template.py` - REST API client
- `graphql-adapter-template.py` - GraphQL client

**Interface**:
```python
class APIAdapter:
    def authenticate() -> bool
    def execute(request: ExecutionRequest) -> ExecutionResult
    def handle_errors(error: Exception) -> ErrorResult
```

---

### 3. Custom Adapters (`custom/`)

**Purpose**: Special-purpose integrations

**Use Cases**:
- Custom protocols
- Legacy systems
- Special workflows

**Key Templates**:
- `custom-adapter-template.py` - Base for custom integrations
- `batch-processor-template.py` - Bulk operation handler

---

## 🚀 Quick Start

### Creating a Subprocess Adapter

```bash
# 1. Copy template
cp templates/adapters/subprocess/tool-adapter-template.py \
   my_project/adapters/mytool_adapter.py

# 2. Implement required methods
# - detect_capabilities(): Return tool's capabilities
# - execute(): Run the tool
# - validate_result(): Check output

# 3. Register in router config
# Add to router_config.json:
{
  "capability": "my_capability",
  "tool": "mytool",
  "adapter": "mytool_adapter.MyToolAdapter"
}
```

### Creating an API Adapter

```bash
# 1. Copy template
cp templates/adapters/api/rest-adapter-template.py \
   my_project/adapters/api_adapter.py

# 2. Configure API endpoint
# Set base URL, authentication, headers

# 3. Implement execute() method
# Make API calls, parse responses

# 4. Test
pytest tests/adapters/test_api_adapter.py
```

---

## 📐 Adapter Interface

All adapters must implement this interface:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class ToolAdapter(ABC):
    """Base adapter interface"""
    
    @abstractmethod
    def detect_capabilities(self) -> Dict[str, Any]:
        """
        Detect and return tool capabilities.
        
        Returns:
            Dict with:
            - capabilities: List[str] - What the tool can do
            - version: str - Tool version
            - available: bool - Is tool installed/accessible
        """
        pass
    
    @abstractmethod
    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """
        Execute the tool with given request.
        
        Args:
            request: Execution request with parameters
            
        Returns:
            ExecutionResult with status, output, errors
        """
        pass
    
    @abstractmethod
    def validate_result(self, result: Any) -> ValidationResult:
        """
        Validate tool output.
        
        Args:
            result: Tool output to validate
            
        Returns:
            ValidationResult with valid/invalid + errors
        """
        pass
```

See [INTERFACE.md](INTERFACE.md) for complete interface specification.

---

## 🔧 Implementation Guide

### Step 1: Detect Capabilities

```python
def detect_capabilities(self) -> Dict[str, Any]:
    """Check if tool is available and what it can do"""
    try:
        # Run tool with --version or similar
        result = subprocess.run(
            ["mytool", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        return {
            "capabilities": ["code_analysis", "linting"],
            "version": result.stdout.strip(),
            "available": result.returncode == 0
        }
    except FileNotFoundError:
        return {
            "capabilities": [],
            "version": None,
            "available": False
        }
```

### Step 2: Execute Tool

```python
def execute(self, request: ExecutionRequest) -> ExecutionResult:
    """Run the tool"""
    # Build command
    cmd = self._build_command(request)
    
    # Execute with timeout and retry
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=request.timeout or 300,
            cwd=request.work_dir
        )
        
        return ExecutionResult(
            status="success" if result.returncode == 0 else "failed",
            output=result.stdout,
            errors=result.stderr,
            exit_code=result.returncode
        )
    except subprocess.TimeoutExpired:
        return ExecutionResult(
            status="timeout",
            output="",
            errors="Execution timed out"
        )
```

### Step 3: Validate Result

```python
def validate_result(self, result: Any) -> ValidationResult:
    """Check if output is valid"""
    errors = []
    
    # Check for known error patterns
    if "ERROR" in result.output:
        errors.append("Tool reported errors")
    
    # Validate output format
    if not self._is_valid_format(result.output):
        errors.append("Invalid output format")
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors
    )
```

---

## 🎯 Best Practices

### Error Handling

```python
# Use try-except blocks
try:
    result = self._run_tool(request)
except subprocess.CalledProcessError as e:
    return ExecutionResult(
        status="failed",
        errors=str(e)
    )
except FileNotFoundError:
    return ExecutionResult(
        status="failed",
        errors="Tool not found - is it installed?"
    )
```

### Timeouts

```python
# Always set reasonable timeouts
DEFAULT_TIMEOUT = 300  # 5 minutes

def execute(self, request):
    timeout = request.timeout or DEFAULT_TIMEOUT
    # Use timeout in subprocess.run()
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

def execute(self, request):
    logger.info(f"Executing {self.tool_name} with request: {request.task_id}")
    # ... execution ...
    logger.info(f"Completed with status: {result.status}")
```

### Resilience

```python
from core.engine.resilience import retry_with_backoff

@retry_with_backoff(max_retries=3, base_delay=1.0)
def execute(self, request):
    # This will automatically retry on failure
    # with exponential backoff
    return self._run_tool(request)
```

---

## ✅ Testing Adapters

### Unit Tests

```python
# tests/adapters/test_mytool_adapter.py
import pytest
from adapters.mytool_adapter import MyToolAdapter

def test_detect_capabilities():
    adapter = MyToolAdapter()
    caps = adapter.detect_capabilities()
    
    assert caps["available"] is True
    assert "code_analysis" in caps["capabilities"]

def test_execute_success():
    adapter = MyToolAdapter()
    request = ExecutionRequest(
        task_id="test-001",
        work_dir="/tmp/test"
    )
    
    result = adapter.execute(request)
    assert result.status == "success"
```

### Integration Tests

```python
def test_full_workflow():
    """Test adapter in complete workflow"""
    adapter = MyToolAdapter()
    
    # 1. Detect capabilities
    caps = adapter.detect_capabilities()
    assert caps["available"]
    
    # 2. Execute
    result = adapter.execute(request)
    assert result.status == "success"
    
    # 3. Validate
    validation = adapter.validate_result(result)
    assert validation.valid
```

---

## 📚 Related Documentation

- **[Templates Main README](../README.md)** - Overview of all templates
- **[INTERFACE.md](INTERFACE.md)** - Complete adapter interface spec
- **[Orchestration Templates](../orchestration/README.md)** - Task definitions
- **[Configuration Templates](../configuration/README.md)** - Router config
- **[UET Resilience Spec](../../specs/UET_EXECUTION_KERNEL_PARALLELISM_STRATEGY_SPEC_V2.md)**

---

## 🔍 Available Adapters

### Built-in Examples

- **aider-adapter-example.py**: AI-powered code editing
- **pytest-adapter-example.py**: Python testing framework

### Community Adapters

Check the [adapter registry](../../docs/ADAPTER_REGISTRY.md) for community-contributed adapters.

---

## 📞 Support

**Q: How do I add a new tool?**  
A: Copy `tool-adapter-template.py`, implement the interface, register in router config.

**Q: How do I handle tool failures?**  
A: Use the resilience patterns in `core.engine.resilience` for retry logic.

**Q: Can I call APIs instead of CLI tools?**  
A: Yes! Use the API adapter templates in `api/`.

---

**Last Updated**: 2025-11-23  
**Related**: [Orchestration](../orchestration/README.md), [Configuration](../configuration/README.md)
