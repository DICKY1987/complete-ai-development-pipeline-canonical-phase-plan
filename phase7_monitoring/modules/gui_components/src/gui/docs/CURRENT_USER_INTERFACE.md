---
doc_id: DOC-GUIDE-CURRENT-USER-INTERFACE-923
---

# Current User Interface - Complete Description

## Overview

The AI Development Pipeline currently provides a **Command-Line Interface (CLI)** for querying and monitoring the pipeline state. There is **no graphical user interface (GUI)** at this time, though the infrastructure has been prepared for future GUI development.

## What the User Sees

### Terminal/Command Line Interface

Users interact with the system through terminal commands. The primary interface is accessed via:

```bash
python -m core.ui_cli <command> [options]
```

### Available Commands

The CLI provides 7 main commands for different aspects of the pipeline:

#### 1. **Dashboard** - Pipeline Overview
```bash
python -m core.ui_cli dashboard [--run-id RUN_ID] [--json]
```

**What you see:** A text-based dashboard showing:
- **Workstreams:** Running, Queued, Completed, Failed counts
- **Files:** Counts by lifecycle state (Intake, Classified, In Flight, Awaiting Review, Committed, Quarantined)
- **Throughput:** Files/hour and Jobs/hour metrics
- **Errors:** Errors/hour and top error types

**Example output (table format):**
```
PIPELINE DASHBOARD
============================================================

Workstreams:
  Running:    3
  Queued:     5
  Completed:  12
  Failed:     1

Files:
  Intake:           8
  Classified:       15
  In Flight:        4
  Awaiting Review:  2
  Committed:        45
  Quarantined:      1

Throughput:
  Files/hour:  12.5
  Jobs/hour:   3.2

Errors:
  Errors/hour: 0.8
  Top errors:
    - syntax: 3
    - config: 2
```

#### 2. **Files** - File Lifecycle Tracking
```bash
python -m core.ui_cli files [--state STATE] [--workstream-id ID] [--run-id ID]
                             [--tool-id ID] [--limit N] [--json]
```

**What you see:** A table of files with their current state:
- File ID (shortened to 12 characters)
- File path (shortened to 40 characters)
- Current state (e.g., committed, processing, quarantined)
- Associated workstream
- Last processed timestamp

**Example output:**
```
File ID       Path                      State        Workstream    Last Processed
---------------------------------------------------------------------------
file-abc123   src/module.py             committed    ws-refact01   2025-11-22 14:30
file-def456   tests/test_module.py      processing   ws-refact01   2025-11-22 14:45
file-ghi789   config/settings.json      classified   ws-config02   2025-11-22 14:20

Total: 3 files
```

**File states available:**
- `intake` - Newly discovered
- `classified` - Role/type identified
- `processing` - Being worked on by a tool
- `in_flight` - Active processing
- `awaiting_review` - Waiting for human review
- `committed` - Successfully committed to repository
- `quarantined` - Failed/problematic, needs attention
- `locked` - Completed, no further changes allowed
- `archived` - Moved to archive
- `deleted` - Removed from pipeline

#### 3. **File Counts** - State Distribution
```bash
python -m core.ui_cli file-counts [--run-id RUN_ID] [--json]
```

**What you see:** Count of files in each lifecycle state

**Example output:**
```
State         Count
--------------------
committed     45
processing    4
classified    15
quarantined   1
```

#### 4. **Workstreams** - Workstream Status
```bash
python -m core.ui_cli workstreams [--run-id RUN_ID] [--status STATUS]
                                   [--limit N] [--json]
```

**What you see:** Table of workstreams with:
- Workstream ID (shortened)
- Current status
- Files processed/succeeded ratio
- Duration in seconds
- Start timestamp

**Example output:**
```
Workstream ID  Status     Files    Duration  Started
-----------------------------------------------------
ws-refact01    completed  8/8      125.3s    2025-11-22 14:00
ws-config02    running    3/5      45.7s     2025-11-22 14:30
ws-tests03     failed     2/10     15.2s     2025-11-22 14:25

Total: 3 workstreams
```

**Workstream statuses:**
- `pending` - Not started
- `queued` - Waiting to start
- `running` - Currently executing
- `paused` - Temporarily stopped
- `completed` - Successfully finished
- `failed` - Encountered errors
- `cancelled` - User cancelled
- `blocked` - Waiting on dependencies

#### 5. **Workstream Counts** - Status Distribution
```bash
python -m core.ui_cli workstream-counts [--run-id RUN_ID] [--json]
```

**What you see:** Count of workstreams by status

**Example output:**
```
Status      Count
------------------
running     3
completed   12
queued      5
failed      1
```

#### 6. **Errors** - Error Tracking
```bash
python -m core.ui_cli errors [--run-id RUN_ID] [--workstream-id ID]
                              [--severity LEVEL] [--category CAT]
                              [--tool-id ID] [--limit N] [--json]
```

**What you see:** Table of errors with:
- Error ID (shortened)
- Severity level
- Error category
- Human-readable message (truncated to 50 chars)
- Occurrence count

**Example output:**
```
Error ID      Severity  Category  Message                                Count
--------------------------------------------------------------------------------
err-abc123    error     syntax    SyntaxError at line 42: unexpected to  3
err-def456    warning   config    Missing environment variable OLLAMA_A  1
err-ghi789    critical  network   Connection timeout to API endpoint     5

Total: 3 errors
```

**Severity levels:**
- `warning` - Minor issues, not blocking
- `error` - Serious problems, may block progress
- `critical` - Severe issues requiring immediate attention

**Error categories:**
- `syntax` - Code syntax errors
- `config` - Configuration problems
- `network` - Network/connectivity issues
- `timeout` - Operation timeouts
- `permission` - File/system permission errors
- `dependency` - Missing or incompatible dependencies
- `validation` - Data/input validation failures
- `resource` - Resource exhaustion (memory, disk, etc.)
- `tool` - Tool-specific errors
- `integration` - Inter-tool communication issues
- `unknown` - Uncategorized errors

#### 7. **Tools** - Tool Health Monitoring
```bash
python -m core.ui_cli tools [--tool-id ID] [--summary] [--json]
```

**What you see (list mode):** Table of all tools with:
- Tool ID
- Display name
- Current status
- Success rate percentage
- Request count (5-minute window)

**Example output:**
```
Tool ID  Name    Status     Success Rate  Requests (5m)
--------------------------------------------------------
aider    Aider   healthy    95.5%         24
codex    Codex   healthy    98.2%         12
tests    Tests   degraded   75.0%         8

Total: 3 tools
```

**What you see (specific tool):** Detailed health information:
```
Tool: Aider
Status: healthy
Success Rate: 95.5%
P95 Latency: 12.34s
Requests (5m/15m/60m): 24/68/245
```

**Tool statuses:**
- `healthy` - Operating normally
- `degraded` - Experiencing issues but functional
- `unreachable` - Cannot connect to tool
- `circuit_open` - Circuit breaker triggered, not accepting requests
- `unknown` - Status cannot be determined

### JSON Output Mode

**All commands support `--json` flag** for machine-readable output. This is useful for:
- Building automation scripts
- Feeding data to monitoring tools
- Creating custom visualizations
- Integrating with other systems

**Example JSON output:**
```bash
python -m core.ui_cli dashboard --json
```

```json
{
  "workstreams_running": 3,
  "workstreams_queued": 5,
  "workstreams_completed": 12,
  "workstreams_failed": 1,
  "files_intake": 8,
  "files_classified": 15,
  "files_in_flight": 4,
  "files_awaiting_review": 2,
  "files_committed": 45,
  "files_quarantined": 1,
  "files_per_hour": 12.5,
  "errors_per_hour": 0.8,
  "top_error_types": [
    ["syntax", 3],
    ["config", 2]
  ]
}
```

## Interactive Elements

### No Clickable Buttons
The current CLI interface has **no clickable buttons**. All interaction is through typing commands.

### No Text Input Fields
There are **no graphical text input fields**. Users provide input via:
- Command-line arguments (e.g., `--state committed`)
- Command-line flags (e.g., `--json`)
- Piping/redirection if needed for automation

### Command Completion
Users can use shell features:
- **Tab completion** (if shell supports it)
- **Command history** (up/down arrows)
- **Ctrl+C** to cancel long-running queries

## How to Use the Interface

### Basic Workflow

1. **Check overall status:**
   ```bash
   python -m core.ui_cli dashboard
   ```

2. **Investigate specific areas:**
   ```bash
   # See what files are being processed
   python -m core.ui_cli files --state processing

   # Check for errors
   python -m core.ui_cli errors --severity error

   # Monitor tool health
   python -m core.ui_cli tools --summary
   ```

3. **Filter by run or workstream:**
   ```bash
   # All files in a specific workstream
   python -m core.ui_cli files --workstream-id ws-refact01

   # All errors in a specific run
   python -m core.ui_cli errors --run-id run-2025-11-22-001
   ```

4. **Export data for analysis:**
   ```bash
   # Save to JSON file
   python -m core.ui_cli dashboard --json > dashboard-$(date +%Y%m%d).json

   # Pipe to jq for filtering
   python -m core.ui_cli files --json | jq '.[] | select(.current_state == "quarantined")'
   ```

### Common Use Cases

**"What's currently running?"**
```bash
python -m core.ui_cli workstreams --status running
```

**"Are there any errors I should look at?"**
```bash
python -m core.ui_cli errors --severity critical
python -m core.ui_cli errors --severity error
```

**"Which files are stuck in quarantine?"**
```bash
python -m core.ui_cli files --state quarantined
```

**"Is Aider working properly?"**
```bash
python -m core.ui_cli tools --tool-id aider
```

**"How many files have been completed?"**
```bash
python -m core.ui_cli file-counts
```

## Limitations of Current Interface

### What You CANNOT Do via UI

1. **Start/Stop Operations** - No commands to start workstreams, pause runs, or retry failed jobs
2. **Modify Configuration** - Cannot change settings through the UI
3. **Edit Files** - No file viewing or editing capabilities
4. **Real-time Updates** - Must manually re-run commands to see updates
5. **Interactive Navigation** - No menus, panels, or clickable elements
6. **Visualizations** - No graphs, charts, or diagrams
7. **Filtering UI** - No interactive filtering (must use command-line flags)
8. **Batch Operations** - No way to select multiple items and act on them
9. **Notifications** - No alerts or notifications when events occur

### Database Requirement

**Important:** The CLI requires a populated database to function. If you see errors like:
```
Error: no such table: workstreams
```

This means the database hasn't been initialized yet. The pipeline must be run at least once to populate the database with data.

## Future GUI Plans

The repository includes extensive documentation for a planned **Hybrid GUI/Terminal Architecture**:

- **Location:** `gui/` directory contains design documents
- **Concept:** Graphical control panel wrapping terminal/TUI processes
- **Features planned:**
  - Pipeline board (drag-and-drop cards for workstreams)
  - Live log streaming
  - Clickable file explorer
  - Tool health dashboard with charts
  - Error/quarantine center with remediation actions
  - Start/stop/retry buttons
  - Configuration editors

See:
- `gui/Hybrid UI_GUI shell_terminal_TUI engine.md` - Architecture design
- `gui/GUI_PIPELINE_SPEC.txt` - Detailed GUI specification
- `docs/GUI_DEVELOPMENT_GUIDE.md` - Implementation guide

**Status:** Infrastructure is ready (event system, data models, query APIs), but the GUI itself is not yet implemented.

## Summary

### What the User Currently Sees:
- **Text-based terminal output** only
- **Tables** showing pipeline status, files, workstreams, errors, tools
- **JSON output** for machine consumption
- **No graphical elements** - purely command-line driven

### Available Commands:
1. `dashboard` - Overall pipeline health
2. `files` - File lifecycle and state
3. `file-counts` - File state distribution
4. `workstreams` - Workstream status and progress
5. `workstream-counts` - Workstream status distribution
6. `errors` - Error tracking and monitoring
7. `tools` - Tool health and performance metrics

### Interaction Methods:
- **Command-line arguments** for filtering and options
- **Flags** for output format (`--json`)
- **Shell features** (tab completion, history, piping)
- **No clickable buttons** or interactive elements
- **No text entry fields** or forms

### Data Visualization:
- **Text tables** with aligned columns
- **Summary statistics** (counts, rates, percentages)
- **Timestamps** in ISO format
- **Truncated values** for readability (IDs, paths)
- **No graphs or charts**

The interface is designed for:
- Developers comfortable with command-line tools
- Automation and scripting (via JSON output)
- Quick status checks and monitoring
- Debugging and troubleshooting
- Integration with other CLI tools (jq, grep, etc.)
