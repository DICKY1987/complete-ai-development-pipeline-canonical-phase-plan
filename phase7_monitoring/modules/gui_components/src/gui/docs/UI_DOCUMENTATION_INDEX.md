---
doc_id: DOC-GUIDE-UI-DOCUMENTATION-INDEX-931
---

# User Interface Documentation Index

## Quick Answer to: "What does the user see?"

The user sees a **terminal/command-line interface only**. There are:
- ✗ **NO clickable buttons**
- ✗ **NO text entry fields**
- ✗ **NO graphical interface**

The user sees **text-based output** from CLI commands.

See **[UI Documentation Summary](UI_DOCUMENTATION_SUMMARY.md)** for the complete answer.

---

## Documentation Files

This repository contains comprehensive documentation of the current user interface:

### 📋 Start Here

**[UI Documentation Summary](UI_DOCUMENTATION_SUMMARY.md)** (6 KB)
- Executive summary answering the problem statement
- Direct answers to all key questions
- Quick overview of available commands
- Links to detailed documentation

### 📖 Detailed Documentation

**[Current User Interface](CURRENT_USER_INTERFACE.md)** (13 KB)
- Complete description of CLI interface
- All 7 commands with full syntax and options
- Sample outputs in table and JSON formats
- File states, workstream statuses, error categories
- Clear statement: No buttons, no text fields
- What users can and cannot do
- Future GUI plans

**[UI Quick Reference](UI_QUICK_REFERENCE.md)** (16 KB)
- 50+ concrete command examples
- Common workflows and use cases
- Advanced usage with jq and shell scripting
- Reference tables for all states/statuses
- Troubleshooting guide
- Tips and best practices

### 📊 Visual Documentation

**[UI Flow Diagram](UI_FLOW_DIAGRAM.md)** (16 KB)
- Command flow diagrams (ASCII art)
- Complete command tree
- Database schema relationships
- File lifecycle state machine
- Workstream status flow
- Tool health indicators
- User interaction summary
- Future GUI mockup

**[UI Visual Examples](UI_VISUAL_EXAMPLES.md)** (13 KB)
- Real terminal session walkthrough
- Actual help output from commands
- Step-by-step user workflow
- Visual terminal window diagram
- Comparison: Current CLI vs Future GUI
- "What users cannot do" examples

### 🔧 Technical Documentation

**[UI Implementation Summary](UI_IMPLEMENTATION_SUMMARY.md)** (13 KB)
- Infrastructure and architecture
- Event system, database schema, data models
- Query clients and APIs
- Tool instrumentation
- File lifecycle management
- Error record management
- Integration points

**[UI Data Requirements](UI_DATA_REQUIREMENTS.md)** (11 KB)
- API contracts for UI components
- Request/response formats
- Data models and schemas
- Integration patterns

---

## Navigation by Purpose

### "I want to understand what the interface looks like"
1. Start: [UI Documentation Summary](UI_DOCUMENTATION_SUMMARY.md)
2. Then: [UI Visual Examples](UI_VISUAL_EXAMPLES.md)
3. Details: [Current User Interface](CURRENT_USER_INTERFACE.md)

### "I need to use the interface"
1. Start: [UI Quick Reference](UI_QUICK_REFERENCE.md)
2. Details: [Current User Interface](CURRENT_USER_INTERFACE.md)
3. Help: Get command help with `python -m core.ui_cli --help`

### "I want to understand how it works"
1. Start: [UI Flow Diagram](UI_FLOW_DIAGRAM.md)
2. Details: [UI Implementation Summary](UI_IMPLEMENTATION_SUMMARY.md)
3. Technical: [UI Data Requirements](UI_DATA_REQUIREMENTS.md)

### "I'm building automation/scripts"
1. Start: [UI Quick Reference](UI_QUICK_REFERENCE.md) - See "Advanced Usage" section
2. Use: JSON output mode with `--json` flag
3. Reference: [UI Data Requirements](UI_DATA_REQUIREMENTS.md) for API contracts

---

## Quick Command Reference

```bash
# Get help
python -m core.ui_cli --help
python -m core.ui_cli <command> --help

# Check pipeline status
python -m core.ui_cli dashboard

# Monitor workstreams
python -m core.ui_cli workstreams --status running

# Track files
python -m core.ui_cli files --state processing

# Check for errors
python -m core.ui_cli errors --severity error

# Monitor tools
python -m core.ui_cli tools --summary

# Export as JSON
python -m core.ui_cli <command> --json
```

See [UI Quick Reference](UI_QUICK_REFERENCE.md) for complete command list with examples.

---

## Key Facts

### Current State
- **Interface Type:** Command-line only (CLI)
- **Graphical UI:** None (planned for future)
- **Interactive Elements:** None
- **Input Method:** Command-line arguments only
- **Output Formats:** Text tables or JSON
- **Operations:** Read-only queries only

### Available Commands
1. `dashboard` - Pipeline overview
2. `files` - File lifecycle tracking
3. `file-counts` - File state distribution
4. `workstreams` - Workstream status
5. `workstream-counts` - Workstream distribution
6. `errors` - Error monitoring
7. `tools` - Tool health status

### What Users See
- Terminal window with command prompt
- Text-based output (tables or JSON)
- Statistics and metrics
- Timestamps and file paths
- Error messages and status information

### What Users Do NOT See
- ✗ Buttons or clickable elements
- ✗ Text input fields or forms
- ✗ Menus or dropdown lists
- ✗ Progress bars or animations
- ✗ Graphs or charts
- ✗ Real-time updates (must re-run commands)

### What Users CANNOT Do
- ✗ Start/stop/pause operations
- ✗ Modify configuration
- ✗ Edit files
- ✗ Batch operations
- ✗ Interactive filtering
- ✗ Visual navigation

Users can only **query and view** pipeline state.

---

## Future Development

### Planned GUI (Not Yet Implemented)

Design documents exist in the `gui/` directory:
- `gui/Hybrid UI_GUI shell_terminal_TUI engine.md` - Architecture
- `gui/GUI_PIPELINE_SPEC.txt` - Detailed specification
- `docs/GUI_DEVELOPMENT_GUIDE.md` - Implementation guide

**Planned Features:**
- Clickable pipeline board
- Interactive file explorer
- Live log streaming
- Start/stop/retry buttons
- Tool health dashboard with charts
- Configuration editors
- Real-time updates

**Status:** Infrastructure ready, GUI not yet built.

---

## Documentation Statistics

- **Total Files:** 5 main documentation files + 2 technical reference files
- **Total Size:** ~80 KB of documentation
- **Total Lines:** ~2,100 lines
- **Coverage:** Complete description of current CLI interface
- **Diagrams:** 15+ ASCII diagrams and flow charts
- **Examples:** 50+ command examples with output
- **Reference Tables:** 10+ tables for states, statuses, categories

---

## Related Documentation

- **[QUICK_START.md](../../QUICK_START.md)** - Repository quick start guide
- **[DIRECTORY_GUIDE.md](../../DIRECTORY_GUIDE.md)** - Repository navigation
- **[README.md](../../README.md)** - Main repository README
- **[ENGINE_QUICK_REFERENCE.md](ENGINE_QUICK_REFERENCE.md)** - Engine usage guide
- **[GUI_DEVELOPMENT_GUIDE.md](GUI_DEVELOPMENT_GUIDE.md)** - Future GUI development

---

## Getting Help

### In the Documentation
- Read [UI Documentation Summary](UI_DOCUMENTATION_SUMMARY.md) for quick answers
- Check [UI Quick Reference](UI_QUICK_REFERENCE.md) for command examples
- Review [UI Visual Examples](UI_VISUAL_EXAMPLES.md) to see what it looks like

### At the Command Line
```bash
# General help
python -m core.ui_cli --help

# Command-specific help
python -m core.ui_cli dashboard --help
python -m core.ui_cli files --help
python -m core.ui_cli errors --help
# etc.
```

### Try It Out
```bash
# Quick test (may fail if database not initialized)
python -m core.ui_cli dashboard

# Get help first
python -m core.ui_cli --help
```

---

## Last Updated

This documentation was created on 2025-11-22 and accurately describes the command-line interface as implemented in `core/ui_cli.py`.

**Note:** The interface is CLI-only. If you see references to a GUI or graphical interface, those are **design documents for future development** and not yet implemented.
