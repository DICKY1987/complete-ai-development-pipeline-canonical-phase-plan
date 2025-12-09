---
doc_id: DOC-GUIDE-UI-INTERACTIVE-TOOL-SELECTION-934
---

# UI Interactive Tool Selection

## Overview

The UI settings system allows you to configure which CLI tool runs in interactive mode (where users send commands) versus headless mode (background execution). This is crucial for the hybrid GUI/Terminal/TUI architecture where:

- **One tool runs interactively** - This is where users send requests and commands
- **Other tools run headless** - They execute in the background without user interaction

## Key Features

1. **Configurable Interactive Tool** - Choose which tool serves as the user command interface
2. **Runtime Tool Switching** - Change the interactive tool from the UI without restarting
3. **Persistent Settings** - Configuration is saved and persists across sessions
4. **Auto-launch Configuration** - Control which tools start automatically with the UI

## Architecture

```
┌─────────────────────────────────────────┐
│           User Interface (GUI)          │
├─────────────────────────────────────────┤
│                                         │
│  ┌───────────────────────────────────┐  │
│  │   Interactive Tool (aim)          │  │  ← User sends commands here
│  │   Mode: INTERACTIVE               │  │
│  │   Layout: main_terminal           │  │
│  └───────────────────────────────────┘  │
│                                         │
│  Headless Tools (background):          │
│  ┌─────────────┐  ┌─────────────┐     │
│  │   aider     │  │   codex     │     │  ← Run without interaction
│  │  HEADLESS   │  │  HEADLESS   │     │
│  └─────────────┘  └─────────────┘     │
│                                         │
└─────────────────────────────────────────┘
```

## Configuration

### Location

Settings are stored in: `config/ui_settings.yaml`

### Structure

```yaml
# The primary interactive tool
default_interactive_tool: "aim"

# Available interactive tools
available_interactive_tools:
  - aim
  - aider
  - codex
  - core.ui_cli

# Tool execution modes
tool_modes:
  aim:
    default_mode: "interactive"
    supports_headless: true
    description: "AIM+ Unified CLI - AI Development Environment Manager"

  aider:
    default_mode: "headless"
    supports_headless: true
    description: "AI pair programming tool"

# UI startup behavior
startup:
  auto_launch_interactive: true
  auto_launch_headless:
    - core.ui_cli
  interactive_tool_layout: "main_terminal"
```

## Usage

### CLI Commands

```bash
# Show current settings
python -m core.ui_settings_cli show

# Change the interactive tool
python -m core.ui_settings_cli set-interactive aider

# List all tools and their modes
python -m core.ui_settings_cli list-tools

# Get mode for a specific tool
python -m core.ui_settings_cli get-mode aider

# Output as JSON
python -m core.ui_settings_cli show --json
```

### Python API

```python
from core.ui_settings import UISettingsManager

# Initialize
settings = UISettingsManager()

# Get current interactive tool
interactive_tool = settings.get_interactive_tool()
# Returns: "aim"

# Check if a tool should run headless
is_headless = settings.is_headless("aider")
# Returns: True (if aider is not the interactive tool)

# Change interactive tool
settings.set_interactive_tool("codex")
# Returns: True if successful

# Get tool execution mode
mode = settings.get_tool_mode("aider")
# Returns: "headless" or "interactive"

# Get available interactive tools
available = settings.get_available_interactive_tools()
# Returns: ["aim", "aider", "codex", "core.ui_cli"]
```

### Integration with Orchestrator

```python
from core.ui_settings import get_settings_manager
from engine.orchestrator import Orchestrator

settings = get_settings_manager()

def build_tool_command(tool_name, base_args):
    """Build command with appropriate flags based on execution mode."""
    command = [tool_name] + base_args

    if settings.is_headless(tool_name):
        # Add headless flags for background execution
        if tool_name == "aider":
            command.extend(["--yes", "--no-auto-commits"])
        # Other tool-specific headless flags...
    else:
        # Interactive mode - allow user input
        command.append("--interactive")

    return command
```

## Workflow

### Startup Sequence

1. **UI starts** → Load `ui_settings.yaml`
2. **Get interactive tool** → `settings.get_interactive_tool()`
3. **Launch interactive tool** → Open in main terminal panel
4. **Launch headless tools** → Start in background
5. **User can now send commands** → To the interactive tool

### Switching Interactive Tool

1. **User selects new tool** → From UI dropdown/menu
2. **UI calls** → `settings.set_interactive_tool("aider")`
3. **Stop current interactive tool** → Gracefully shutdown
4. **Start new interactive tool** → In interactive mode
5. **Update UI** → Show new tool as active
6. **Configuration saved** → Persists to `ui_settings.yaml`

## Examples

### Example 1: Default Configuration (AIM as interactive)

```
Interactive Tool: aim
├─ Mode: INTERACTIVE
├─ Where: main_terminal panel
└─ User sends: "aim setup --all"

Headless Tools:
├─ aider (background)
├─ codex (background)
└─ core.ui_cli (background)
```

### Example 2: Switch to Aider Interactive

```bash
python -m core.ui_settings_cli set-interactive aider
```

Result:
```
Interactive Tool: aider
├─ Mode: INTERACTIVE
├─ Where: main_terminal panel
└─ User sends: aider commands directly

Headless Tools:
├─ aim (now background)
├─ codex (background)
└─ core.ui_cli (background)
```

## Benefits

1. **Flexibility** - Choose the right tool for your workflow
2. **User Control** - Easy switching without configuration file editing
3. **Clear Separation** - Interactive vs headless modes are explicit
4. **Persistence** - Settings saved automatically
5. **Integration Ready** - Designed for GUI/TUI integration

## Related Files

- `config/ui_settings.yaml` - Configuration file
- `core/ui_settings.py` - Settings manager module
- `core/ui_settings_cli.py` - CLI interface
- `tests/test_ui_settings.py` - Test suite
- `examples/ui_tool_selection_demo.py` - Usage demonstration

## Future Enhancements

- GUI panel for interactive tool selection
- Real-time tool switching without restart
- Per-workstream tool preferences
- Tool health monitoring integration
- Custom tool launch parameters per mode

## See Also

- [Hybrid UI Architecture](../../gui/Hybrid%20UI_GUI%20shell_terminal_TUI%20engine.md)
- [Engine Implementation](../../docs/ENGINE_IMPLEMENTATION_SUMMARY.md)
- [Tool Profiles](../../config/tool_profiles.json)
