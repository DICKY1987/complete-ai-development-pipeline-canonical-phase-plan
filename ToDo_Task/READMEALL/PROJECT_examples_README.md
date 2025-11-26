# Example Implementations

**Purpose**: Reference implementations demonstrating pipeline integration patterns, UI usage, and orchestrator workflows.

## Overview

The `examples/` directory contains standalone Python scripts that demonstrate how to integrate with the pipeline orchestrator, UI settings system, and tool selection logic.

## Structure

```
examples/
├── orchestrator_integration_demo.py  # Orchestrator + UI settings integration
├── ui_infrastructure_usage.py        # UI settings manager usage
└── ui_tool_selection_demo.py         # Tool selection and execution modes
```

## Example Scripts

### Orchestrator Integration Demo

**File**: `orchestrator_integration_demo.py`

**Purpose**: Demonstrates how to build an orchestrator that respects UI settings for headless vs interactive tool execution.

**Key Concepts**:
- UI settings integration via `UISettingsManager`
- Headless mode detection for tools
- Dynamic command building based on execution mode
- Tool process management

**Usage**:
```python
from examples.orchestrator_integration_demo import EnhancedOrchestrator

# Create orchestrator with UI settings support
orchestrator = EnhancedOrchestrator()

# Build tool command with appropriate flags
command = orchestrator.build_tool_command(
    tool_name="pytest",
    base_args=["-v", "tests/"]
)

# Execute tool respecting UI settings
result = orchestrator.execute_tool("pytest", command)
```

**Example Output**:
```python
# If pytest is configured as headless:
# command = ["pytest", "-v", "tests/", "--tb=short", "--no-header"]

# If pytest is interactive:
# command = ["pytest", "-v", "tests/"]
```

**Code Highlights**:
```python
class EnhancedOrchestrator:
    def __init__(self):
        self.settings = get_settings_manager()
        self.tool_processes = {}
    
    def build_tool_command(self, tool_name: str, base_args: List[str]) -> List[str]:
        command = [tool_name] + base_args
        
        if self.settings.is_headless(tool_name):
            headless_flags = self._get_headless_flags(tool_name)
            command.extend(headless_flags)
        
        return command
```

### UI Infrastructure Usage

**File**: `ui_infrastructure_usage.py`

**Purpose**: Shows how to use the UI settings manager to query and update execution modes.

**Key Concepts**:
- Global settings access
- Tool-specific settings queries
- Execution mode toggling
- Settings persistence

**Usage**:
```python
from examples.ui_infrastructure_usage import demonstrate_ui_settings

# Show all UI settings operations
demonstrate_ui_settings()
```

**Example Operations**:
```python
from core.ui_settings import get_settings_manager

settings = get_settings_manager()

# Check if tool runs in headless mode
is_headless = settings.is_headless("pytest")

# Get all tools running in headless mode
headless_tools = settings.get_headless_tools()

# Set tool to headless mode
settings.set_headless("aider", True)

# Restore default settings
settings.reset_to_defaults()
```

**Output Example**:
```
UI Settings Manager Demo
========================

Current headless tools: ['pytest', 'ruff', 'mypy']

Tool execution modes:
  pytest: headless
  aider: interactive
  codex: interactive

Setting pytest to interactive mode...
pytest is now: interactive

Resetting to defaults...
All settings restored to defaults.
```

### UI Tool Selection Demo

**File**: `ui_tool_selection_demo.py`

**Purpose**: Demonstrates intelligent tool selection and execution mode determination based on context.

**Key Concepts**:
- Tool capability detection
- Context-aware mode selection
- Batch vs interactive tool execution
- Tool compatibility checking

**Usage**:
```python
from examples.ui_tool_selection_demo import demonstrate_tool_selection

# Show tool selection logic
demonstrate_tool_selection()
```

**Example Scenarios**:

**Scenario 1: Batch Validation**
```python
# Running 100 Python files through Ruff
context = {
    "file_count": 100,
    "user_present": False,
    "ci_mode": True
}

# Tool selection: Ruff in headless mode
# Reason: Batch operation, no user interaction needed
```

**Scenario 2: Interactive Debugging**
```python
# Running single test with debugger
context = {
    "file_count": 1,
    "user_present": True,
    "debug_mode": True
}

# Tool selection: pytest in interactive mode
# Reason: User wants to interact with debugger
```

**Scenario 3: Agent-Driven Fixes**
```python
# Aider fixing linting issues
context = {
    "file_count": 5,
    "agent_mode": "aider",
    "auto_commit": True
}

# Tool selection: Aider in headless mode
# Reason: Automated agent workflow, no user input
```

## Integration Patterns

### Pattern 1: UI-Aware Orchestrator

**Use Case**: Orchestrator that switches between headless/interactive based on UI settings

**Implementation**:
```python
class UIAwareOrchestrator:
    def __init__(self):
        self.ui_settings = get_settings_manager()
    
    def run_workstream_step(self, step):
        tool_name = step["tool"]
        
        # Build command respecting UI settings
        command = self._build_command(tool_name, step["args"])
        
        # Execute with appropriate mode
        if self.ui_settings.is_headless(tool_name):
            return self._run_headless(command)
        else:
            return self._run_interactive(command)
```

### Pattern 2: Context-Based Mode Selection

**Use Case**: Automatically determine execution mode based on runtime context

**Implementation**:
```python
def select_execution_mode(tool_name, context):
    """Select headless vs interactive based on context."""
    
    # CI always uses headless
    if context.get("ci_mode"):
        return "headless"
    
    # User-triggered interactive tasks
    if context.get("user_present") and context.get("debug_mode"):
        return "interactive"
    
    # Batch operations use headless
    if context.get("file_count", 0) > 10:
        return "headless"
    
    # Fall back to UI settings
    settings = get_settings_manager()
    return "headless" if settings.is_headless(tool_name) else "interactive"
```

### Pattern 3: Tool Capability Detection

**Use Case**: Check if tool supports headless mode before forcing it

**Implementation**:
```python
from core.engine.tools_adapter import ToolsAdapter

adapter = ToolsAdapter()

# Check if tool supports headless
supports_headless = adapter.tool_supports_headless("pytest")

if not supports_headless and force_headless:
    raise ValueError(f"Tool 'pytest' does not support headless mode")
```

## Running Examples

### Interactive Mode

```bash
# Run orchestrator demo
python examples/orchestrator_integration_demo.py

# Run UI settings demo
python examples/ui_infrastructure_usage.py

# Run tool selection demo
python examples/ui_tool_selection_demo.py
```

### Importing as Modules

```python
# In your code
from examples.orchestrator_integration_demo import EnhancedOrchestrator
from examples.ui_infrastructure_usage import demonstrate_ui_settings
from examples.ui_tool_selection_demo import ToolSelector

# Use example implementations
orchestrator = EnhancedOrchestrator()
selector = ToolSelector()
```

### Testing Examples

```bash
# Run example tests (if available)
pytest tests/examples/ -v

# Test specific example
pytest tests/examples/test_orchestrator_demo.py -v
```

## Example Use Cases

### Use Case 1: CI Pipeline Integration

**Goal**: Run all tools in headless mode for CI

**Implementation**:
```python
from core.ui_settings import get_settings_manager
from examples.orchestrator_integration_demo import EnhancedOrchestrator

# Configure all tools for headless in CI
settings = get_settings_manager()
settings.set_headless_all(True)

# Run orchestrator
orchestrator = EnhancedOrchestrator()
result = orchestrator.run_workstream("ci-validation")
```

### Use Case 2: Developer Interactive Debugging

**Goal**: Run single test interactively with debugger

**Implementation**:
```python
from core.ui_settings import get_settings_manager
from examples.orchestrator_integration_demo import EnhancedOrchestrator

# Configure pytest for interactive mode
settings = get_settings_manager()
settings.set_headless("pytest", False)

# Run single test with debugger
orchestrator = EnhancedOrchestrator()
command = orchestrator.build_tool_command(
    "pytest",
    ["tests/test_my_feature.py::test_specific_case", "-s", "--pdb"]
)
orchestrator.execute_tool("pytest", command)
```

### Use Case 3: Batch Validation

**Goal**: Validate 100+ files with Ruff in headless mode

**Implementation**:
```python
from examples.ui_tool_selection_demo import ToolSelector

selector = ToolSelector()

context = {
    "file_count": 150,
    "ci_mode": False,
    "batch_mode": True
}

# Automatically selects headless mode for batch
mode = selector.select_mode("ruff", context)
# mode == "headless"
```

## Extending Examples

### Adding New Examples

1. **Create new Python file** in `examples/`
2. **Import required modules**:
   ```python
   from core.ui_settings import get_settings_manager
   from core.engine.tools_adapter import ToolsAdapter
   ```
3. **Implement example class or functions**
4. **Add docstrings** explaining usage
5. **Include `if __name__ == "__main__":` block** for standalone execution

**Template**:
```python
"""
My Example Implementation

Demonstrates <concept>.
"""

from typing import List, Dict, Any
from core.ui_settings import get_settings_manager


class MyExample:
    """Example implementation of <concept>."""
    
    def __init__(self):
        """Initialize example."""
        self.settings = get_settings_manager()
    
    def demonstrate(self):
        """Run demonstration."""
        print("Example output:")
        # Implementation
        

def main():
    """Main entry point."""
    example = MyExample()
    example.demonstrate()


if __name__ == "__main__":
    main()
```

### Adding Tests for Examples

**Create test file**: `tests/examples/test_my_example.py`

```python
def test_my_example():
    from examples.my_example import MyExample
    
    example = MyExample()
    result = example.demonstrate()
    
    assert result is not None
```

## Best Practices

1. **Keep examples self-contained**: Minimal dependencies
2. **Add extensive docstrings**: Explain what and why
3. **Include usage examples**: Show how to import and use
4. **Make runnable**: Add `if __name__ == "__main__":` block
5. **Test examples**: Ensure they work with latest code

## Troubleshooting

**Issue**: ImportError when running example
- Ensure repository root in PYTHONPATH
- Run from repository root: `python examples/script.py`

**Issue**: UI settings not persisting
- Check `config/ui_settings.yaml` exists
- Verify write permissions

**Issue**: Tool not found
- Ensure tool installed in environment
- Check `config/tool_profiles.json` for configuration

## Related Sections

- **Core**: `core/` - Modules used by examples
- **GUI**: `gui/` - UI components that examples demonstrate
- **Config**: `config/` - Configuration files examples reference
- **Tests**: `tests/examples/` - Example tests

## See Also

- [UI Settings README](../core/README.md#ui-settings)
- [Tools Adapter README](../core/engine/README.md#tools-adapter)
- [Orchestrator Guide](../docs/orchestrator_guide.md)
