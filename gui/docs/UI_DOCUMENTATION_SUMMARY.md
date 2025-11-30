---
doc_id: DOC-GUIDE-UI-DOCUMENTATION-SUMMARY-1426
---

# User Interface Documentation Summary

## Problem Statement Response

**Question:** *"Describe the user interface currently. What does the user see? Are there clickable buttons? Is there a place to enter text?"*

## Answer Summary

### What the User Currently Sees

The AI Development Pipeline provides a **command-line interface (CLI)** accessed through the terminal. Users see:

1. **Text-based output only** - No graphical elements
2. **Tables with aligned columns** showing pipeline data
3. **Statistics and metrics** (counts, percentages, rates)
4. **Timestamps** in ISO 8601 format
5. **File paths and IDs** (truncated for readability)

### Are There Clickable Buttons?

**No.** The interface has **no clickable buttons** whatsoever. All interaction happens through:
- Typing commands in the terminal
- Using command-line flags and arguments
- Shell features (tab completion, command history)

### Is There a Place to Enter Text?

**No graphical text input fields.** All text input is via:
- Command-line arguments (e.g., `--state committed`)
- Command-line flags (e.g., `--json`)
- Shell input/redirection for automation

The interface is purely **command-driven** - users type commands and receive text output.

## Available Interface Components

The CLI provides **7 main commands** for querying pipeline state:

### 1. Dashboard
```bash
python -m core.ui_cli dashboard [--json]
```
Shows overall pipeline health, workstream counts, file counts, throughput, and error rates.

### 2. Files
```bash
python -m core.ui_cli files [--state STATE] [--workstream-id ID] [--json]
```
Lists files with their lifecycle state, path, and processing status.

### 3. File Counts
```bash
python -m core.ui_cli file-counts [--run-id ID] [--json]
```
Shows distribution of files across lifecycle states.

### 4. Workstreams
```bash
python -m core.ui_cli workstreams [--status STATUS] [--json]
```
Lists workstreams with status, progress, and timing information.

### 5. Workstream Counts
```bash
python -m core.ui_cli workstream-counts [--json]
```
Shows distribution of workstreams by status.

### 6. Errors
```bash
python -m core.ui_cli errors [--severity LEVEL] [--category CAT] [--json]
```
Tracks errors with severity levels, categories, and occurrence counts.

### 7. Tools
```bash
python -m core.ui_cli tools [--tool-id ID] [--summary] [--json]
```
Monitors tool health, success rates, and performance metrics.

## Example: What a User Sees

When running the dashboard command:

```bash
$ python -m core.ui_cli dashboard
```

**Output:**
```
PIPELINE DASHBOARD
============================================================

Workstreams:
  Running:    2
  Queued:     4
  Completed:  18
  Failed:     0

Files:
  Intake:           3
  Classified:       8
  In Flight:        2
  Awaiting Review:  1
  Committed:        67
  Quarantined:      0

Throughput:
  Files/hour:  8.5
  Jobs/hour:   2.1

Errors:
  Errors/hour: 0.3
  Top errors:
    - config: 2
    - timeout: 1
```

## Interaction Model

### User Actions:
- ✓ Type commands
- ✓ Use shell tab completion
- ✓ Navigate command history (↑↓ arrows)
- ✓ Pipe output to other tools
- ✓ Redirect output to files
- ✗ No clicking
- ✗ No drag-and-drop
- ✗ No form filling
- ✗ No menu navigation

### Output Formats:
- ✓ Text tables (human-readable)
- ✓ JSON (machine-readable)
- ✗ No graphs or charts
- ✗ No colors (unless terminal supports ANSI)
- ✗ No progress bars or animations

## What Users CANNOT Do

The current interface does **not** support:

1. **Starting/Stopping Operations** - No commands to start workstreams, pause runs, or retry jobs
2. **Modifying Configuration** - Cannot change settings through the UI
3. **Editing Files** - No file viewing or editing
4. **Real-time Updates** - Must manually re-run commands
5. **Interactive Filtering** - All filtering via command-line flags
6. **Batch Operations** - Cannot select multiple items
7. **Visual Navigation** - No menus, panels, or clickable links
8. **Notifications** - No alerts when events occur

These are **read-only query operations only**.

## Future Plans

A **graphical user interface (GUI)** is planned for future implementation:

- **Design Documents:** Located in `gui/` directory
- **Concept:** Hybrid GUI/Terminal architecture
- **Planned Features:**
  - Clickable pipeline board with drag-and-drop
  - Live log streaming
  - Interactive file explorer
  - Start/stop/retry buttons
  - Tool health dashboard with charts
  - Configuration editors
  
**Status:** Infrastructure is ready (event system, data models, APIs), but GUI is not yet implemented.

## Documentation Files

Three comprehensive documentation files have been created:

1. **`docs/CURRENT_USER_INTERFACE.md`** (447 lines)
   - Complete interface description
   - All commands and their options
   - Sample outputs
   - States, statuses, and categories
   - Current limitations
   - Future GUI reference

2. **`docs/UI_FLOW_DIAGRAM.md`** (449 lines)
   - Command flow diagrams (ASCII art)
   - Database schema relationships
   - File lifecycle state transitions
   - Workstream status flow
   - User interaction points
   - Future GUI mockup

3. **`docs/UI_QUICK_REFERENCE.md`** (642 lines)
   - Command examples with real output
   - Common workflows and use cases
   - Advanced usage (jq, scripting, automation)
   - Reference tables
   - Troubleshooting guide
   - Tips and best practices

## Quick Access

From the terminal:

```bash
# View documentation
cat docs/CURRENT_USER_INTERFACE.md
cat docs/UI_FLOW_DIAGRAM.md
cat docs/UI_QUICK_REFERENCE.md

# Try the interface
python -m core.ui_cli --help
python -m core.ui_cli dashboard
python -m core.ui_cli tools --summary

# Export as JSON
python -m core.ui_cli dashboard --json
```

## Key Takeaways

1. **Text-Only Interface:** CLI commands in terminal, no graphical elements
2. **No Clickable Elements:** Zero buttons, links, or interactive components
3. **No Text Fields:** All input via command-line arguments
4. **Read-Only Operations:** Query and view only, no control operations
5. **Two Output Modes:** Human-readable tables or machine-readable JSON
6. **Future GUI Planned:** Design documents exist but GUI not yet implemented

The interface is designed for developers comfortable with command-line tools and for automation/scripting scenarios.
