# UI Interactive Tool Selection - Quick Reference

## What is it?

A system that lets you configure which CLI tool runs in interactive mode (where you send commands) versus headless mode (background execution).

## Quick Commands

```bash
# View current settings
python -m core.ui_settings_cli show

# Change interactive tool to aider
python -m core.ui_settings_cli set-interactive aider

# Change back to aim
python -m core.ui_settings_cli set-interactive aim

# List all tools
python -m core.ui_settings_cli list-tools

# Get JSON output
python -m core.ui_settings_cli show --json
```

## Concept

```
┌─────────────────────────────────┐
│          GUI/TUI                │
├─────────────────────────────────┤
│  Interactive Tool: aim          │  ← You type commands here
│  [Mode: INTERACTIVE]            │
├─────────────────────────────────┤
│  Headless Tools:                │
│  - aider    (background)        │  ← Run without interaction
│  - codex    (background)        │
│  - pytest   (background)        │
└─────────────────────────────────┘
```

## Default Configuration

- **Interactive Tool**: `aim` (AIM+ CLI)
- **Headless Tools**: `aider`, `codex`, `pytest`, `git`, `core.ui_cli`
- **Layout**: `main_terminal`

## Python API (Quick)

```python
from core.ui_settings import get_settings_manager

settings = get_settings_manager()

# Get current interactive tool
interactive = settings.get_interactive_tool()

# Check if tool is headless
is_headless = settings.is_headless("aider")

# Change interactive tool
settings.set_interactive_tool("codex")
```

## Use Cases

### Use Case 1: Developer wants to use Aider as main interface
```bash
python -m core.ui_settings_cli set-interactive aider
# Now Aider runs interactively, AIM runs headless
```

### Use Case 2: Check what mode a tool is running in
```bash
python -m core.ui_settings_cli get-mode aider
# Output: interactive or headless
```

### Use Case 3: Programmatic integration
```python
from core.ui_settings import UISettingsManager

settings = UISettingsManager()
mode = settings.get_tool_mode("aider")

if mode == "interactive":
    # Launch in foreground with terminal
    launch_interactive(tool)
else:
    # Launch in background
    launch_headless(tool)
```

## Configuration File

Location: `config/ui_settings.yaml`

```yaml
default_interactive_tool: "aim"
available_interactive_tools:
  - aim
  - aider
  - codex
  - core.ui_cli
```

## See Full Documentation

- [UI_INTERACTIVE_TOOL_SELECTION.md](UI_INTERACTIVE_TOOL_SELECTION.md) - Complete guide
- [Examples](../examples/ui_tool_selection_demo.py) - Usage demonstrations
- [Tests](../tests/test_ui_settings.py) - Test suite
