---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-DATA_FLOWS-112
---

# Data Flow Diagrams

**Purpose:** Visualize how data moves through the system to help AI agents understand request/response patterns and state propagation.

**Last Updated:** 2025-11-22
**Maintainer:** System Architecture Team

---

## Overview

These diagrams show:
- **Request/Response Flows:** How data enters and exits
- **State Propagation:** How state changes flow through system
- **Data Transformations:** Where and how data is modified

---

## Flow 1: Workstream Execution Data Flow

### High-Level Flow

```
User Input (JSON Bundle)
    ↓
[Validator] → Validated Workstream Object
    ↓
[Orchestrator] → Execution Plan (Steps Ordered)
    ↓
[Database] ← Store Initial State (S_PENDING)
    ↓
[Step Executor] → For Each Step:
    ├─ Load Step Context
    ├─ [Tool Adapter] → Execute Tool
    │   ├─ Command Template Rendering
    │   ├─ Subprocess Execution
    │   └─ Result Parsing
    ├─ [Database] ← Store Step Result
    └─ State Transition (S_SUCCESS/S_FAILED)
    ↓
[Database] ← Final Workstream State
    ↓
User Output (Execution Result)
```

### Detailed Data Transformations

```
Step 1: Load & Validate
─────────────────────────
Input:  workstreams/bundle.json (File)
        {
          "ws_id": "WS-001",
          "steps": [...],
          "name": "My Workstream"
        }

↓ [File Read + JSON Parse]

Output: Python Dict
        ws_data = {
          "ws_id": "WS-001",
          "steps": [Step1, Step2],
          "name": "My Workstream"
        }

↓ [Schema Validation]

Output: ValidatedWorkstream object
        ws = ValidatedWorkstream(
          ws_id="WS-001",
          steps=[...],
          validated=True
        )

Step 2: Create Database Record
────────────────────────────────
Input:  ValidatedWorkstream object

↓ [Extract Fields]

Output: SQL INSERT
        INSERT INTO workstreams (ws_id, name, state, created_at)
        VALUES ('WS-001', 'My Workstream', 'S_PENDING', '2025-11-22...')

↓ [Execute SQL]

Output: Database Row
        | ws_id  | name          | state     | created_at |
        |--------|---------------|-----------|------------|
        | WS-001 | My Workstream | S_PENDING | 2025-11-22 |

Step 3: Execute Step
────────────────────────
Input:  Step object
        {
          "step_id": "s1",
          "tool_profile_id": "aider",
          "context": {"files": ["x.py"], "instruction": "Fix"}
        }

↓ [Load Tool Profile from config/tool_profiles.json]

Output: ToolProfile
        {
          "tool_id": "aider",
          "command_template": "aider {files} --message '{instruction}'",
          "timeout_seconds": 300
        }

↓ [Render Template]

Output: Rendered Command (String)
        "aider x.py --message 'Fix'"

↓ [Subprocess Execute]

Output: ProcessResult
        {
          "returncode": 0,
          "stdout": "Modified x.py\n",
          "stderr": "",
          "duration_ms": 5000
        }

↓ [Parse Result]

Output: ToolResult
        {
          "status": "success",
          "exit_code": 0,
          "files_modified": ["x.py"],
          "output": "Modified x.py"
        }

↓ [Store in Database]

Output: step_results table row
        | step_id | status  | exit_code | files_modified | output       |
        |---------|---------|-----------|----------------|--------------|
        | s1      | success | 0         | ["x.py"]       | Modified x.py|
```

### State Flow Through Database

```
Time → State Transitions
──────────────────────────

T0: Workstream Created
    workstreams: ws_id=WS-001, state=S_PENDING
    steps:       s1=S_PENDING, s2=S_PENDING

T1: Execution Starts
    workstreams: ws_id=WS-001, state=S_RUNNING
    steps:       s1=S_PENDING, s2=S_PENDING

T2: Step s1 Starts
    workstreams: ws_id=WS-001, state=S_RUNNING
    steps:       s1=S_RUNNING, s2=S_PENDING

T3: Step s1 Completes
    workstreams: ws_id=WS-001, state=S_RUNNING
    steps:       s1=S_SUCCESS, s2=S_PENDING

T4: Step s2 Starts
    workstreams: ws_id=WS-001, state=S_RUNNING
    steps:       s1=S_SUCCESS, s2=S_RUNNING

T5: Step s2 Completes
    workstreams: ws_id=WS-001, state=S_RUNNING
    steps:       s1=S_SUCCESS, s2=S_SUCCESS

T6: Workstream Completes
    workstreams: ws_id=WS-001, state=S_SUCCESS
    steps:       s1=S_SUCCESS, s2=S_SUCCESS
```

---

## Flow 2: Error Detection Data Flow

### High-Level Flow

```
User: python error/engine/error_engine.py
    ↓
[Plugin Discovery]
    ├─ Scan error/plugins/*/manifest.json
    ├─ Load Plugin Modules
    └─ Filter by Language
    ↓
Selected Plugins: [python_ruff, python_mypy]
    ↓
[File Scanner]
    ├─ Find *.py files
    ├─ Load File Hashes from DB
    └─ Identify Changed Files
    ↓
Changed Files: [file1.py, file2.py, file3.py]
    ↓
[Parallel Plugin Execution]
    ├─ Worker 1: python_ruff on file1.py
    │   └─ subprocess.run(['ruff', 'check', 'file1.py'])
    ├─ Worker 2: python_mypy on file1.py
    │   └─ subprocess.run(['mypy', 'file1.py'])
    └─ Workers process remaining files...
    ↓
Plugin Results: [ErrorRecord, ErrorRecord, ...]
    ↓
[Aggregation]
    ├─ Deduplicate Errors
    ├─ Enrich with Context
    └─ Store in Database
    ↓
[Report Generation]
    └─ Format as JSON/HTML/Console
    ↓
User: error_report.json + exit code
```

### Data Transformation Detail

```
Input: File to Scan
─────────────────────
file1.py (content):
    import os
    import sys  # unused
    print(x)    # NameError

↓ [Hash Calculation]

File Hash: sha256("import os\nimport sys...")
         = "abc123..."

↓ [Cache Check in Database]

Query: SELECT hash FROM file_hashes WHERE file_path = 'file1.py'
Result: "def456..."  (different! file changed)

↓ [Execute Plugin: python_ruff]

Command: ruff check file1.py --output-format json
Output (JSON):
[
  {
    "filename": "file1.py",
    "line": 2,
    "column": 1,
    "rule": "F401",
    "message": "sys imported but unused",
    "severity": "warning"
  }
]

↓ [Parse Plugin Output]

ErrorRecord:
{
  "plugin_id": "python_ruff",
  "file_path": "file1.py",
  "line": 2,
  "column": 1,
  "severity": "WARNING",
  "message": "sys imported but unused",
  "rule_code": "F401"
}

↓ [Execute Plugin: python_mypy]

Command: mypy file1.py
Output (text):
file1.py:3: error: Name 'x' is not defined

↓ [Parse Plugin Output]

ErrorRecord:
{
  "plugin_id": "python_mypy",
  "file_path": "file1.py",
  "line": 3,
  "column": null,
  "severity": "ERROR",
  "message": "Name 'x' is not defined",
  "rule_code": "name-defined"
}

↓ [Aggregate Results]

Combined Errors: [Error1(ruff), Error2(mypy)]
Deduplicated: 2 unique errors (no duplicates in this case)

↓ [Store in Database]

INSERT INTO errors (file_path, line, severity, message, detected_at)
VALUES
  ('file1.py', 2, 'WARNING', 'sys imported but unused', NOW()),
  ('file1.py', 3, 'ERROR', 'Name x not defined', NOW())

↓ [Update File Hash Cache]

UPDATE file_hashes SET hash = 'abc123...' WHERE file_path = 'file1.py'
```

---

## Flow 3: Specification Resolution Data Flow

### High-Level Flow

```
Code: resolve_uri("spec://core/state/db#initialization")
    ↓
[URI Parser]
    └─ Extract: scheme=spec, path=core/state/db, anchor=initialization
    ↓
[Resolution Cache Check]
    ├─ HIT → Return cached ResolvedSpec
    └─ MISS → Continue resolution
    ↓
[Path Resolution]
    ├─ Build candidates:
    │   - specifications/content/core/state/db.md
    │   - specifications/content/core/state/db/index.md
    ├─ Check file existence
    └─ Select first existing file
    ↓
Found: specifications/content/core/state/db.md
    ↓
[File Read]
    └─ Load markdown content
    ↓
[Markdown Parsing]
    ├─ Parse to AST
    ├─ Extract headings/anchors
    └─ Find ## Initialization section
    ↓
[Section Extraction]
    └─ Extract content from line 45-68
    ↓
[Cross-Reference Resolution]
    ├─ Scan for spec:// links
    ├─ Recursively resolve (depth limit 3)
    └─ Build reference graph
    ↓
[Cache Storage]
    └─ Store in resolution_cache (TTL 300s)
    ↓
Output: ResolvedSpec object
    {
      "uri": "spec://core/state/db#initialization",
      "file_path": "specifications/content/core/state/db.md",
      "line_number": 45,
      "content": "## Initialization\n\nTo initialize...",
      "references": ["spec://core/engine/orchestrator"]
    }
```

### Data Structure Evolution

```
String URI
─────────────
"spec://core/state/db#initialization"

↓ [Parse]

ParsedURI (Dataclass)
─────────────────────
ParsedURI(
  scheme="spec",
  path="core/state/db",
  anchor="initialization"
)

↓ [Resolve Path]

FilePath + exists
──────────────────
"/path/to/specifications/content/core/state/db.md" (exists=True)

↓ [Read]

Raw Content (String)
────────────────────
"# Database Module\n\n## Overview\n\n## Initialization\n\nTo initialize..."

↓ [Parse Markdown]

MarkdownAST
───────────
Document(
  children=[
    Heading(level=1, text="Database Module"),
    Heading(level=2, text="Overview"),
    Heading(level=2, text="Initialization", line=45),
    Paragraph(...)
  ]
)

↓ [Extract Section]

SectionContent
──────────────
{
  "heading": "Initialization",
  "line": 45,
  "content": "To initialize the database...",
  "subsections": []
}

↓ [Resolve References]

ResolvedSpec (Final)
────────────────────
ResolvedSpec(
  uri="spec://core/state/db#initialization",
  file_path="specifications/content/core/state/db.md",
  line_number=45,
  content="## Initialization\n\nTo initialize...",
  references=[
    ResolvedRef("spec://core/engine/orchestrator", ...)
  ],
  resolved_at="2025-11-22T20:00:00Z"
)
```

---

## Data Flow Patterns

### Pattern 1: Request-Response

```
Client → Server → Database → Server → Client

Example: Create Workstream
──────────────────────────
Client:  POST /workstreams {ws_id: "WS-001", ...}
Server:  Validate input
Database: INSERT workstream
Server:  Return {status: "created", ws_id: "WS-001"}
Client:  Receive confirmation
```

### Pattern 2: Event-Driven State Propagation

```
State Change → Event → Subscribers → Side Effects

Example: Step Completion
─────────────────────────
Orchestrator: transition_step("s1", S_SUCCESS)
Database:     UPDATE steps SET state='S_SUCCESS'
Event Bus:    emit("step_completed", {step_id: "s1"})
Subscribers:
  - Progress Monitor: update_progress()
  - Logger: log_completion()
  - Next Step Trigger: check_dependencies("s2")
```

### Pattern 3: Pipeline Processing

```
Input → Stage1 → Stage2 → Stage3 → Output

Example: Error Detection
────────────────────────
Files →  [Scan] → Changed Files
      →  [Plugin Exec] → Raw Results
      →  [Parse] → ErrorRecords
      →  [Aggregate] → Deduplicated Errors
      →  [Store] → Database
      →  [Report] → JSON Output
```

---

## State Propagation Map

```
User Action
    ↓
Workstream State Change
    ↓
┌─────────────────────────────┐
│ Database (Source of Truth)  │
│  - workstreams table        │
│  - state_transitions log    │
└─────────────────────────────┘
    ↓                ↓
UI State         Step States
Updates          Propagate
    ↓                ↓
Progress         Next Step
Monitor          Triggered
```

### State Update Sequence

```
1. User submits workstream
   └─> workstreams.state = S_PENDING

2. Orchestrator starts execution
   └─> workstreams.state = S_RUNNING
   └─> state_transitions.log(S_PENDING → S_RUNNING)

3. For each step:
   a. steps.state = S_RUNNING
   b. Execute tool
   c. steps.state = S_SUCCESS/S_FAILED
   d. If success → trigger next step
   e. If failed → retry logic

4. All steps complete
   └─> workstreams.state = S_SUCCESS
   └─> completion_time = NOW()
```

---

## Related Documentation

- [Execution Traces](../EXECUTION_TRACES_SUMMARY.md) - Runtime behavior
- [ADR-0001: Workstream Model](../adr/0001-workstream-model-choice.md)
- [ADR-0003: SQLite Storage](../adr/0003-sqlite-state-storage.md)
- [Error Catalog](ERROR_CATALOG.md) - Error handling

---

**Flows Documented:** 3 major flows
**Patterns Identified:** 3 patterns
**Last Updated:** 2025-11-22
