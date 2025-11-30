---
doc_id: DOC-GUIDE-IMPLEMENTATION-SUMMARY-UI-TOOL-SELECTION-1417
---

# Implementation Summary: UI Interactive Tool Selection

## Problem Statement

> "The cli apps and other tools are supposed to run headless but one needs run normally as the place where the user sends requests and commands. I want the tool that does this be able to be changed in the interface to open when the user interface starts"

## Solution

Implemented a comprehensive system for managing which CLI tool runs in **interactive mode** (where users send commands) versus **headless mode** (background execution).

## Architecture

```
┌───────────────────────────────────────────────────────────┐
│                     User Interface (GUI)                   │
├───────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │   Interactive Tool: aim                          │    │
│  │   Mode: INTERACTIVE                              │    │  ← User sends commands here
│  │   Layout: main_terminal                          │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
│  Headless Tools (background):                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   aider     │  │   codex     │  │   pytest    │      │  ← Run without interaction
│  │  HEADLESS   │  │  HEADLESS   │  │  HEADLESS   │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
│                                                            │
└───────────────────────────────────────────────────────────┘
```

## Key Features

### 1. Configuration Management
- **File**: `config/ui_settings.yaml`
- Stores which tool is interactive
- Defines available interactive tools
- Controls auto-launch behavior
- Persists across sessions

### 2. Settings Manager
- **Module**: `core/ui_settings.py`
- Provides Python API for managing settings
- Supports runtime tool switching
- Automatically saves changes
- Singleton pattern for global access

### 3. CLI Interface
- **Command**: `python -m core.ui_settings_cli`
- View current settings
- Change interactive tool
- List all tools and modes
- JSON output support

### 4. Orchestrator Integration
- **Example**: `examples/orchestrator_integration_demo.py`
- Shows how to integrate with job orchestrator
- Demonstrates headless vs interactive command building
- Handles tool switching at runtime

## Usage Examples

### View Current Settings
```bash
python -m core.ui_settings_cli show
```
Output:
```
=== UI Settings ===

Interactive Tool:        aim
Mode:                    interactive
Layout:                  main_terminal
Auto-launch Interactive: True
Auto-launch Headless:    core.ui_cli

Available Interactive Tools:
  - aim (current)
  - aider
  - codex
  - core.ui_cli
```

### Change Interactive Tool
```bash
python -m core.ui_settings_cli set-interactive aider
```
Output:
```
Interactive tool changed: aim → aider
Settings saved to: config/ui_settings.yaml
```

### List All Tools
```bash
python -m core.ui_settings_cli list-tools
```
Output:
```
=== Tool Configurations ===

Tool                 Mode            Description
-------------------------------------------------------------------------------------
aim                  interactive     AIM+ Unified CLI - AI Development... *
aider                headless        AI pair programming tool
codex                headless        Codex CLI for autonomous code generation
core.ui_cli          headless        Pipeline state query CLI
pytest               headless        Python test runner
git                  headless        Git version control

* = Current interactive tool
```

### Programmatic API
```python
from core.ui_settings import get_settings_manager

settings = get_settings_manager()

# Get current interactive tool
interactive_tool = settings.get_interactive_tool()  # "aim"

# Check if tool should run headless
is_headless = settings.is_headless("aider")  # True

# Change interactive tool
success = settings.set_interactive_tool("codex")  # True

# Get tool execution mode
mode = settings.get_tool_mode("aider")  # "headless" or "interactive"
```

## Implementation Details

### Files Created

1. **config/ui_settings.yaml** (Configuration)
   - Default interactive tool: `aim`
   - Available tools: `aim`, `aider`, `codex`, `core.ui_cli`
   - Auto-launch settings
   - Layout preferences

2. **core/ui_settings.py** (Settings Manager - 280 lines)
   - `UISettingsManager` class
   - Methods for get/set interactive tool
   - Headless mode detection
   - Configuration persistence
   - Singleton accessor

3. **core/ui_settings_cli.py** (CLI Interface - 250 lines)
   - `show` - Display current settings
   - `set-interactive` - Change interactive tool
   - `list-tools` - List all tools and modes
   - `get-mode` - Get mode for specific tool
   - JSON output support

4. **config/tool_profiles.json** (Updated)
   - Added `headless_mode_supported` flags
   - Added `headless_args` for tools

### Files Added for Documentation/Examples

5. **tests/test_ui_settings.py** (Test Suite - 18 tests)
   - Test all UISettingsManager methods
   - Test configuration loading/saving
   - Test tool switching
   - Test mode detection
   - **All 18 tests passing ✓**

6. **docs/UI_INTERACTIVE_TOOL_SELECTION.md** (Full Documentation)
   - Architecture explanation
   - Usage examples
   - Integration patterns
   - Workflow descriptions

7. **docs/UI_TOOL_SELECTION_QUICK_REF.md** (Quick Reference)
   - Common commands
   - Quick examples
   - Use cases

8. **examples/ui_tool_selection_demo.py** (Demo Script)
   - Simulates UI startup
   - Demonstrates tool switching
   - Shows API usage

9. **examples/orchestrator_integration_demo.py** (Integration Example)
   - Shows orchestrator integration
   - Demonstrates command building
   - Runtime tool switching

## Testing

### Test Results
```
tests/test_ui_settings.py::TestUISettingsManager
  ✓ test_default_settings
  ✓ test_load_settings_from_file
  ✓ test_get_interactive_tool
  ✓ test_set_interactive_tool
  ✓ test_set_invalid_interactive_tool
  ✓ test_is_headless
  ✓ test_get_tool_mode
  ✓ test_get_tool_config
  ✓ test_get_startup_config
  ✓ test_should_auto_launch_interactive
  ✓ test_get_auto_launch_headless_tools
  ✓ test_get_interactive_layout
  ✓ test_list_all_tools
  ✓ test_get_settings_summary
  ✓ test_save_and_reload
  ✓ test_singleton_get_settings_manager
  ✓ test_ui_settings_file_creation
  ✓ test_ui_settings_valid_yaml

18 passed in 0.08s ✓
```

### Manual Validation
- ✓ CLI commands work correctly
- ✓ Settings persist across invocations
- ✓ Tool switching updates configuration
- ✓ JSON output is valid
- ✓ Python API functions correctly
- ✓ Demo scripts run successfully

## Benefits

1. **User Control** - Easily switch which tool is interactive
2. **Flexibility** - Support different workflows (aim-first, aider-first, etc.)
3. **Persistence** - Settings saved automatically
4. **Integration Ready** - Designed for GUI/orchestrator integration
5. **Well Tested** - Comprehensive test coverage
6. **Well Documented** - Multiple documentation resources

## Next Steps for Integration

### For GUI Integration:
1. Add UI dropdown/menu for tool selection
2. Call `settings.set_interactive_tool(selected_tool)` on change
3. Restart/relaunch tools with new modes
4. Update UI to show current interactive tool

### For Orchestrator Integration:
```python
from core.ui_settings import get_settings_manager

settings = get_settings_manager()

def launch_tool(tool_name, args):
    if settings.is_headless(tool_name):
        # Add headless flags
        command = build_headless_command(tool_name, args)
        run_in_background(command)
    else:
        # Interactive mode
        command = build_interactive_command(tool_name, args)
        run_in_terminal_panel(command)
```

## Conclusion

Successfully implemented a complete system for managing interactive vs headless tool execution. The system is:
- ✓ Fully functional
- ✓ Well tested (18/18 tests passing)
- ✓ Well documented
- ✓ Ready for GUI integration
- ✓ Backward compatible

The implementation directly addresses the problem statement by allowing users to configure and change which tool runs interactively when the UI starts, while all other tools run headless in the background.
