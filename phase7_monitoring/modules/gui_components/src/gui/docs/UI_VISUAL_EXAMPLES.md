---
doc_id: DOC-GUIDE-UI-VISUAL-EXAMPLES-937
---

# Visual Example: What the User Actually Sees

This document shows the **actual terminal interface** that users interact with.

## Opening the Interface

### Step 1: User Types Command

```
user@machine:~/pipeline$ python -m core.ui_cli --help
```

### Step 2: System Shows Help Menu

```
usage: ui_cli.py [-h] [--db-path DB_PATH]
                 {files,file-counts,workstreams,workstream-counts,errors,tools,dashboard} ...

Query pipeline state for UI components

positional arguments:
  {files,file-counts,workstreams,workstream-counts,errors,tools,dashboard}
                        Command to run
    files               Query file lifecycle records
    file-counts         Get file counts by state
    workstreams         Query workstream records
    workstream-counts   Get workstream counts by status
    errors              Query error records
    tools               Query tool health status
    dashboard           Get pipeline dashboard summary

options:
  -h, --help            show this help message and exit
  --db-path DB_PATH     Path to SQLite database (default: from env or
                        .worktrees/pipeline_state.db)
```

**What the user sees:**
- Plain text output
- List of available commands
- No clickable elements
- No buttons
- No text entry fields
- Just informational text

## Getting Command-Specific Help

### User Types:

```
user@machine:~/pipeline$ python -m core.ui_cli files --help
```

### System Shows:

```
usage: ui_cli.py files [-h]
                       [--state {discovered,classified,intake,routed,processing,
                                in_flight,awaiting_review,awaiting_commit,committed,
                                quarantined}]
                       [--workstream-id WORKSTREAM_ID]
                       [--run-id RUN_ID]
                       [--tool-id TOOL_ID]
                       [--limit LIMIT]
                       [--json]

options:
  -h, --help            show this help message and exit
  --state {discovered,classified,intake,routed,processing,in_flight,
           awaiting_review,awaiting_commit,committed,quarantined}
                        Filter by state
  --workstream-id WORKSTREAM_ID
                        Filter by workstream ID
  --run-id RUN_ID       Filter by run ID
  --tool-id TOOL_ID     Filter by tool ID
  --limit LIMIT         Max results
  --json                Output as JSON
```

**What the user sees:**
- Available command-line options
- Allowed values for `--state` flag
- Other filtering options
- Still no interactive elements

## Running a Command (Table Output)

### User Types:

```
user@machine:~/pipeline$ python -m core.ui_cli dashboard
```

### System Shows (if database is populated):

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

**What the user sees:**
- Text organized in sections
- Numbers and statistics
- No progress bars
- No graphs
- No clickable areas
- Static snapshot of current state

### System Shows (if database is empty):

```
Error: no such table: workstreams
```

**What the user sees:**
- Error message
- Database needs to be initialized first
- No helpful error dialog or suggestion
- Just raw error text

## Running a Command (JSON Output)

### User Types:

```
user@machine:~/pipeline$ python -m core.ui_cli tools --summary --json
```

### System Shows:

```json
[
  {
    "tool_id": "aider",
    "tool_name": "Aider",
    "status": "healthy",
    "success_rate": 0.968,
    "p95_latency": 8.45
  },
  {
    "tool_id": "codex",
    "tool_name": "Codex",
    "status": "healthy",
    "success_rate": 0.982,
    "p95_latency": 12.32
  },
  {
    "tool_id": "tests",
    "tool_name": "Tests",
    "status": "degraded",
    "success_rate": 0.785,
    "p95_latency": 45.67
  }
]
```

**What the user sees:**
- Raw JSON data
- Useful for scripts/automation
- No formatting or highlighting (unless terminal has JSON plugin)
- No interactive JSON explorer
- User must copy/paste or redirect to file

## Querying with Filters

### User Types:

```
user@machine:~/pipeline$ python -m core.ui_cli files --state committed --limit 5
```

### System Shows:

```
File ID       Path                                     State      Workstream    Last Processed
----------------------------------------------------------------------------------------------------
file-a1b2c3d  src/core/engine/orchestrator.py          committed  ws-refact01   2025-11-22 14:30
file-e4f5g6h  tests/test_orchestrator.py               committed  ws-refact01   2025-11-22 14:32
file-i7j8k9l  docs/ARCHITECTURE.md                     committed  ws-docs02     2025-11-22 13:15
file-m0n1o2p  config/settings.json                     committed  ws-config03   2025-11-22 12:45
file-q3r4s5t  README.md                                committed  ws-docs04     2025-11-22 11:20

Total: 5 files
```

**What the user sees:**
- Table with aligned columns
- Truncated IDs and paths (for readability)
- Total count at bottom
- No way to click on a file to see more details
- Must run another command to get more info

## What Users CANNOT See or Do

### No Visual Feedback

```
user@machine:~/pipeline$ python -m core.ui_cli workstreams --status running

# No loading spinner while query runs
# No progress indicator
# Just waits, then shows results
```

### No Interactive Elements

```
# Cannot do this:
[Click here to see more details]
[✓ Select all] [Retry selected]
[Filter: ▼] [Sort by: ▼]

# Only this:
python -m core.ui_cli files --state quarantined --limit 100
```

### No Real-time Updates

```
# To monitor in real-time, user must:
user@machine:~/pipeline$ watch -n 5 'python -m core.ui_cli dashboard'

# This re-runs the command every 5 seconds
# Shows updated output each time
# But it's not a continuous stream
```

### No Control Operations

```
# These commands DO NOT exist:
python -m core.ui_cli workstreams --start ws-refact01    # ❌ No
python -m core.ui_cli workstreams --pause ws-refact01    # ❌ No
python -m core.ui_cli workstreams --retry ws-refact01    # ❌ No
python -m core.ui_cli files --quarantine file-abc123     # ❌ No

# Only queries like:
python -m core.ui_cli workstreams --status running       # ✓ Yes
python -m core.ui_cli files --state quarantined          # ✓ Yes
```

## Terminal Session Example

Here's what a complete terminal session looks like:

```
user@machine:~/complete-ai-development-pipeline$ python -m core.ui_cli --help
usage: ui_cli.py [-h] [--db-path DB_PATH] {files,file-counts,...} ...
[... help text ...]

user@machine:~/complete-ai-development-pipeline$ python -m core.ui_cli dashboard
PIPELINE DASHBOARD
============================================================
[... dashboard output ...]

user@machine:~/complete-ai-development-pipeline$ python -m core.ui_cli errors --severity error
Error ID      Severity  Category  Message                          Count
------------------------------------------------------------------------
err-abc123    error     syntax    SyntaxError at line 42: unexp    2

Total: 1 errors

user@machine:~/complete-ai-development-pipeline$ python -m core.ui_cli files --state quarantined
File ID       Path               State        Workstream    Last Processed
---------------------------------------------------------------------------

Total: 0 files

user@machine:~/complete-ai-development-pipeline$ python -m core.ui_cli tools --summary
Tool          Status     Success Rate  P95 Latency
--------------------------------------------------
Aider         healthy    96.8%         8.45s
Codex         healthy    98.2%         12.32s
Tests         degraded   78.5%         45.67s

user@machine:~/complete-ai-development-pipeline$
```

**What the user experiences:**
1. Types a command and presses Enter
2. Waits (no progress indicator)
3. Sees text output
4. Cursor returns to prompt
5. Repeats for next command
6. No mouse interaction
7. No graphical feedback
8. Pure command-line workflow

## Visual Summary: UI Elements

```
┌────────────────────────────────────────────────────────────┐
│  Terminal Window                                      [×]   │
├────────────────────────────────────────────────────────────┤
│ user@machine:~/pipeline$                                   │
│                                                            │
│ [Blinking cursor here - only place to "enter text"]       │
│                                                            │
│                                                            │
│                                                            │
│ ┌────────────────────────────────────────────────────────┐│
│ │ User types here using keyboard                         ││
│ │ - No text box visible                                  ││
│ │ - No form fields                                       ││
│ │ - No dropdown menus                                    ││
│ │ - Just command prompt                                  ││
│ └────────────────────────────────────────────────────────┘│
│                                                            │
│ After pressing Enter:                                      │
│ ┌────────────────────────────────────────────────────────┐│
│ │ Text output appears                                    ││
│ │ - Tables with data                                     ││
│ │ - Or JSON strings                                      ││
│ │ - Or error messages                                    ││
│ │ - No buttons                                           ││
│ │ - No clickable links                                   ││
│ │ - No interactive elements                              ││
│ └────────────────────────────────────────────────────────┘│
│                                                            │
│ user@machine:~/pipeline$ [Cursor returns to prompt]       │
│                                                            │
└────────────────────────────────────────────────────────────┘

Keyboard only input:
  ✓ Type commands
  ✓ Press Enter to execute
  ✓ Use arrow keys for history
  ✓ Use Tab for completion (if configured)
  ✓ Ctrl+C to cancel

Mouse interaction:
  ✗ No clicking
  ✗ No selecting (except for copy/paste in terminal)
  ✗ No drag and drop
  ✗ No hovering for tooltips
```

## Comparison: Current vs. Future

### Current CLI Interface (What Exists Now)

```
$ python -m core.ui_cli dashboard

PIPELINE DASHBOARD
============================================================
Workstreams:
  Running:    2
  Queued:     4
  Completed:  18
  Failed:     0
[...]

$ █  [Cursor waits for next command]
```

**Characteristics:**
- Text only
- No interactivity
- Manual refresh (re-run command)
- Read-only queries
- No buttons
- No text fields
- No visual feedback

### Future GUI (Planned, Not Yet Built)

```
┌─────────────────────────────────────────────────────────┐
│ File  Edit  View  Tools  Help                          │
├──────────────────┬──────────────────────────────────────┤
│ Workstreams      │ Detail Panel                         │
│ ┌──────────────┐ │ ┌──────────────────────────────────┐ │
│ │[●] Running(2)│◄┼─┤ Status: Running                  │ │
│ │[ ] Queued(4) │ │ │ Files: 8/10                      │ │
│ │[✓]Complete(18│ │ │                                  │ │
│ │[✗] Failed(0) │ │ │ [Start] [Pause] [Retry]          │ │
│ └──────────────┘ │ └──────────────────────────────────┘ │
├──────────────────┴──────────────────────────────────────┤
│ Logs: [Filter▼] [Search: ________]                     │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 14:30:15 [INFO] Aider started...                    │ │
│ │ 14:30:42 [WARN] Test coverage...                    │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Would have:**
- Clickable buttons ✓
- Text input fields ✓
- Live updates ✓
- Interactive controls ✓
- Visual feedback ✓
- Graphs and charts ✓

**Status:** NOT YET IMPLEMENTED - design documents only

## Key Insight

**The user currently sees:**
- A command-line terminal
- Text output only
- No GUI, no buttons, no forms

**The user must:**
- Know the commands
- Type them correctly
- Interpret text output
- Use shell features for efficiency

This is a **developer-focused, automation-friendly interface**, not a point-and-click graphical application.
