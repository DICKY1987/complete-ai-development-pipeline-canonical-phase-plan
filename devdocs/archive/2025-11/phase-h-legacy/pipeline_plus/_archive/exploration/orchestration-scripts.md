# Orchestration Scripts Documentation

**Complete AI Development Pipeline - Canonical Phase Plan**

This document provides a comprehensive overview of all orchestration scripts in the repository, detailing what each script does, the files it interacts with, and what events trigger its execution.

---

## Table of Contents

1. [Overview](#overview)
2. [Script Categories](#script-categories)
3. [Detailed Script Analysis](#detailed-script-analysis)
4. [File Interaction Matrix](#file-interaction-matrix)
5. [Trigger Mechanisms](#trigger-mechanisms)
6. [Dependencies & Execution Flow](#dependencies--execution-flow)

---

## Overview

The AI Development Pipeline uses a combination of PowerShell, Python, and Bash scripts to orchestrate various phases of the development lifecycle. These scripts manage:

- **Repository initialization and bootstrapping**
- **Workstream execution and orchestration**
- **Database operations and state management**
- **Validation and verification**
- **Code generation and mapping**
- **Tool integration and status monitoring**
- **Error handling and pipeline management**

---

## Script Categories

### 1. Bootstrap & Initialization Scripts
- `scripts/bootstrap.ps1`
- `scripts/init_db.py`

### 2. Workstream Orchestration Scripts
- `scripts/run_workstream.py`
- `src/pipeline/orchestrator.py`
- `scripts/generate_workstreams.py`

### 3. Validation & Verification Scripts
- `scripts/validate_workstreams.py`
- `scripts/validate_workstreams_authoring.py`
- `scripts/check_workstream_status.ps1`
- `scripts/check_workstream_status.sh`

### 4. Code Generation & Mapping Scripts
- `scripts/generate_spec_index.py`
- `scripts/generate_spec_mapping.py`

### 5. Database & State Management Scripts
- `scripts/db_inspect.py`
- `src/pipeline/db.py`
- `src/pipeline/db_sqlite.py`

### 6. Error Handling & Pipeline Scripts
- `scripts/run_error_engine.py`
- `src/pipeline/error_pipeline_cli.py`
- `src/pipeline/error_engine.py`

### 7. Tool Integration & Monitoring Scripts
- `scripts/aim_status.py`
- `src/pipeline/aim_bridge.py`

### 8. Testing Scripts
- `scripts/test.ps1`

---

## Detailed Script Analysis

### 1. Bootstrap & Initialization Scripts

#### **scripts/bootstrap.ps1**

**Description:**  
Initializes the repository skeleton by creating essential directories and checking for required tools.

**Files Touched:**
- **Creates:**
  - `docs/` - Documentation directory
  - `plans/` - Phase planning directory
  - `scripts/` - Scripts directory
  - `tests/` - Test directory
  - `assets/` - Assets directory

**Files Read:** None (only checks tool availability)

**Triggers:**
- **Manual execution:** `pwsh ./scripts/bootstrap.ps1`
- **First-time setup:** Run when initializing a new repository clone

**External Dependencies:**
- PowerShell 7+ (`pwsh`)
- Optional: Python (checked but not required)
- Optional: Node.js (checked but not required)

**Exit Behavior:**
- Creates directories if they don't exist
- Reports tool availability status
- Always exits successfully

---

#### **scripts/init_db.py**

**Description:**  
Initializes the pipeline database with the required schema, creating tables for runs, workstreams, events, errors, and step attempts.

**Files Touched:**
- **Creates/Updates:**
  - `state/pipeline.db` (default location, configurable via `--db` parameter)
  
**Files Read:**
- `schema/schema.sql` - Database schema definition (optional, configurable via `--schema` parameter)
- `src/pipeline/db.py` - Database initialization logic

**Triggers:**
- **Manual execution:** `python scripts/init_db.py [--db PATH] [--schema PATH]`
- **Before first workstream run:** Required to set up database before orchestration
- **Database reset:** Run to reinitialize database structure

**External Dependencies:**
- Python 3.8+
- SQLite3
- `src/pipeline/db` module

**Exit Behavior:**
- Creates database file and tables
- Prints database path
- Returns 0 on success

---

### 2. Workstream Orchestration Scripts

#### **scripts/run_workstream.py**

**Description:**  
CLI entry point to run a single workstream end-to-end via the Phase 5 orchestrator. Executes the EDIT → STATIC → RUNTIME sequence for a specified workstream.

**Files Touched:**

**Creates/Updates:**
- `state/pipeline.db` - Records run state, events, and step attempts
- `.worktrees/ws-<workstream-id>/` - Creates git worktree for isolated workspace
- Workstream-specific files as defined in the workstream bundle

**Files Read:**
- `workstreams/<ws-id>.json` - Workstream bundle definition
- `src/pipeline/orchestrator.py` - Core orchestration logic
- `src/pipeline/bundles.py` - Bundle loading and validation
- `config/tool_profiles.json` - Tool configuration (if static/runtime tools configured)

**Triggers:**
- **Manual execution:** `python scripts/run_workstream.py --ws-id <workstream-id> [--run-id RUN] [--dry-run]`
- **Automated pipeline:** Called by higher-level orchestration (future phases)
- **CI/CD integration:** Can be integrated into GitHub Actions or other CI systems

**Command-line Options:**
- `--ws-id` (required): Workstream identifier (e.g., `ws-hello-world`)
- `--run-id` (optional): Custom run identifier (default: auto-generated timestamp)
- `--dry-run`: Simulate execution without invoking external tools

**External Dependencies:**
- Python 3.8+
- Aider (for EDIT step)
- Static analysis tools (if configured in bundle)
- Runtime test tools (if configured in bundle)
- Git (for worktree management)

**Exit Behavior:**
- Returns 0 if final status is "done"
- Returns 1 if workstream fails
- Returns 2 on error
- Outputs JSON result summary

**Environment Variables:**
- `PIPELINE_DRY_RUN=1` - Enables dry-run mode

---

#### **src/pipeline/orchestrator.py**

**Description:**  
Core orchestration engine implementing the EDIT → STATIC → RUNTIME workflow for workstreams. Manages state transitions, executes tool adapters, handles FIX loops with circuit breakers, and records comprehensive telemetry.

**Files Touched:**

**Creates/Updates:**
- `state/pipeline.db` - Extensive database writes:
  - `runs` table - Run lifecycle records
  - `workstreams` table - Workstream status updates
  - `events` table - Step starts/ends, fix attempts, breaker trips
  - `step_attempts` table - Detailed step execution records
  - `errors` table - Error signatures and contexts
- `.worktrees/ws-<ws-id>/` - Git worktree for isolated edits (via `worktree.py`)
- Source code files (via Aider in EDIT/FIX steps)

**Files Read:**
- `workstreams/<bundle-id>.json` - Bundle specifications
- `config/tool_profiles.json` - Tool adapter configurations
- `config/circuit_breakers.yaml` - Circuit breaker thresholds and rules
- `src/pipeline/prompts.py` - Aider prompt templates
- `src/pipeline/tools.py` - Tool execution adapters
- `src/pipeline/bundles.py` - Bundle data structures
- `src/pipeline/circuit_breakers.py` - Breaker logic

**Triggers:**
- **Called by:** `scripts/run_workstream.py`
- **Function calls:**
  - `run_single_workstream_from_bundle(ws_id, run_id, context)` - Main entry point
  - `run_workstream(run_id, ws_id, bundle_obj, context)` - Core workflow
  - `run_edit_step()` - Execute EDIT phase
  - `run_static_with_fix()` - Execute STATIC phase with FIX retries
  - `run_runtime_with_fix()` - Execute RUNTIME phase with FIX retries

**External Dependencies:**
- All dependencies from `run_workstream.py`
- Circuit breaker configuration
- Worktree management utilities

**Key Behaviors:**
- **State Machine:** Transitions: `pending → started → editing → ready_for_static → static_check → runtime_tests → done/failed`
- **Circuit Breakers:** Prevents infinite FIX loops via:
  - Max fix attempts per step
  - Error signature repetition detection
  - Diff oscillation detection
- **Scope Validation:** Ensures edits only touch files in `files_scope`
- **Dry Run Support:** Simulates execution without external tool invocation
- **Comprehensive Logging:** Records all events, attempts, and errors to database

---

#### **scripts/generate_workstreams.py**

**Description:**  
Generates draft workstream bundles from a specification ID using the planner module. Currently implements a stub/placeholder for future automated planning logic.

**Files Touched:**

**Creates:**
- `workstreams/ws-generated-placeholder-<spec-id>-<index>.json` - Draft workstream bundle files

**Files Read:**
- `src/pipeline/planner.py` - Planning logic (currently stub implementation)

**Triggers:**
- **Manual execution:** `python scripts/generate_workstreams.py --spec-id <spec-id> [--output-dir DIR] [--options JSON]`
- **Specification processing:** Run when converting OpenSpec or CCPM issues to workstreams

**Command-line Options:**
- `--spec-id` (required): Specification identifier (e.g., OpenSpec ID, CCPM issue ID)
- `--output-dir` (default: `workstreams`): Output directory for generated bundles
- `--options` (default: `{}`): JSON string of planner options (e.g., `'{"group_by": "language"}'`)

**External Dependencies:**
- Python 3.8+
- `src/pipeline/planner` module

**Exit Behavior:**
- Returns 0 on success (generates placeholder bundles)
- Returns 1 on NotImplementedError or validation errors
- Currently generates placeholder bundles; full implementation planned for future phases

**Current Status:**
- **Phase:** PH-05.5 (stub/placeholder)
- **Future:** Will implement automated decomposition, file scope inference, and AI-assisted planning

---

### 3. Validation & Verification Scripts

#### **scripts/validate_workstreams.py**

**Description:**  
Validates all workstream bundle files in the workstreams directory. Checks for JSON schema compliance, dependency resolution, circular dependencies, and file scope overlaps. Optionally syncs validated bundles to the database.

**Files Touched:**

**Files Read:**
- `workstreams/*.json` - All workstream bundle files
- `src/pipeline/bundles.py` - Validation logic and schema definitions

**Files Updated (optional):**
- `state/pipeline.db` - If `--run-id` is provided, syncs bundles to database

**Triggers:**
- **Manual execution:** `python scripts/validate_workstreams.py [--run-id RUN] [--json]`
- **Pre-orchestration:** Run before executing workstreams to ensure validity
- **CI/CD checks:** Integrate into pre-commit or PR validation workflows

**Command-line Options:**
- `--run-id`: Optional run ID to sync validated bundles to database
- `--json`: Output results in JSON format for machine parsing

**External Dependencies:**
- Python 3.8+
- `src/pipeline/bundles` module
- JSON schema validator

**Exit Behavior:**
- Returns 0 if all bundles are valid and no overlaps detected
- Returns 1 on validation errors:
  - Schema violations
  - Unresolved dependencies
  - Circular dependencies
  - File scope overlaps
- Prints error details or JSON summary

**Validation Checks:**
- **Schema compliance:** All required fields present and correctly typed
- **Dependency resolution:** All `depends_on` workstream IDs exist
- **Cycle detection:** No circular dependency chains
- **File scope overlaps:** No file claimed by multiple workstreams

---

#### **scripts/validate_workstreams_authoring.py**

**Description:**  
Advanced validation tool for workstream authoring. Provides detailed error reporting for bundle validation issues, including schema violations, dependency errors, cycles, and file scope conflicts. Designed for authoring workflows with machine-readable JSON output.

**Files Touched:**

**Files Read:**
- `workstreams/*.json` - All workstream bundle files
- `src/pipeline/bundles.py` - Validation and schema logic

**Triggers:**
- **Manual execution:** `python scripts/validate_workstreams_authoring.py [--dir DIR] [--json]`
- **Authoring workflow:** Run during workstream bundle creation/editing
- **Editor integration:** Can be integrated into IDE validation
- **Pre-commit hooks:** Validate before committing changes

**Command-line Options:**
- `--dir`: Custom workstream directory (default: `workstreams/` or `PIPELINE_WORKSTREAM_DIR` env var)
- `--json`: Output structured JSON for programmatic consumption

**External Dependencies:**
- Python 3.8+
- `src/pipeline/bundles` module

**Exit Behavior:**
- Returns 0 if all bundles valid
- Returns 1 on validation errors with detailed error breakdown
- JSON output includes:
  - `ok`: boolean success flag
  - `bundles_checked`: count of bundles examined
  - `errors`: array of error objects with `type`, `file`, `id`, `details`

**Error Types Reported:**
- `schema`: JSON schema validation failures
- `dependency`: Unresolved dependency references
- `cycle`: Circular dependency chains
- `overlap`: File scope conflicts between bundles
- `config`: Configuration/directory not found
- `unexpected`: Unexpected runtime errors

---

#### **scripts/check_workstream_status.ps1**

**Description:**  
PowerShell-based workstream status checker for Windows environments. Reports on active workstream branches, worktrees, and implementation status of key files across phases PH-01 to PH-03.

**Files Touched:**

**Files Read:**
- `.git/` - Git repository metadata (branches, worktrees)
- `src/pipeline/db.py` - Checks for function implementations
- `src/pipeline/tools.py` - Checks for DB integration
- `schema/schema.sql` - Verifies schema file existence
- `docs/ARCHITECTURE.md` - Checks documentation
- `docs/state_machine.md` - Checks documentation
- `docs/PHASE_PLAN.md` - Checks documentation
- `tests/pipeline/test_*.py` - Verifies test files
- `scripts/generate_spec_index.py` - Checks script existence
- `config/tool_profiles.json` - Checks config file

**Triggers:**
- **Manual execution:** `pwsh scripts/check_workstream_status.ps1`
- **Status check:** Run to verify phase completion progress
- **Windows environments:** Alternative to bash version

**External Dependencies:**
- PowerShell 7+
- Git

**Output Sections:**
1. **Active workstream branches:** Lists all `workstream/*` branches
2. **Active worktrees:** Lists all worktrees with `ws-ph` prefix
3. **Key file implementation status:** Checks existence and implementation of phase-specific files
4. **Summary:** Total counts

**Color-coded Status:**
- ✅ Green: File exists or function implemented
- ❌ Red: File/function not found or stub only

---

#### **scripts/check_workstream_status.sh**

**Description:**  
Bash-based workstream status checker for Unix/Linux/macOS environments. Functionally identical to the PowerShell version, providing status reports on workstream progress across phases.

**Files Touched:**

**Files Read:** (Same as PowerShell version)
- Git repository metadata
- Pipeline source files
- Documentation files
- Test files
- Configuration files

**Triggers:**
- **Manual execution:** `bash scripts/check_workstream_status.sh`
- **Status check:** Run to verify phase completion progress
- **Unix/Linux/macOS environments:** Alternative to PowerShell version

**External Dependencies:**
- Bash 4.0+
- Git
- grep, sed (standard Unix utilities)

**Output Sections:** (Same structure as PowerShell version)
1. Active workstream branches
2. Active worktrees
3. Key file implementation status (PH-01, PH-02, PH-03)
4. Summary statistics

**Implementation Checks:**
- File existence in current directory or main branch
- Function implementation via regex pattern matching
- DB integration via keyword search

---

### 4. Code Generation & Mapping Scripts

#### **scripts/generate_spec_index.py**

**Description:**  
Scans documentation directories recursively for specification index tags of the form `[IDX-...]` and generates a structured summary. Supports both text and JSON output formats.

**Files Touched:**

**Files Read:**
- `docs/**/*.md` - All Markdown files in docs directory
- `docs/**/*.txt` - All text files in docs directory

**Files Created:** None (outputs to stdout)

**Triggers:**
- **Manual execution:** `python scripts/generate_spec_index.py [--docs-dir DIR] [--format FORMAT]`
- **Documentation indexing:** Run after adding/updating specification documents
- **Pipeline integration:** Can be integrated into doc generation workflows

**Command-line Options:**
- `--docs-dir` (default: `docs`): Path to documentation directory
- `--format` (default: `text`): Output format (`text` or `json`)

**External Dependencies:**
- Python 3.8+

**Output Format (text):**
```
IDX-TAG: file/path.md:line - description/context
```

**Output Format (json):**
```json
[
  {
    "idx": "IDX-TAG",
    "file": "relative/path/to/file.md",
    "line": 42,
    "description": "Context or heading"
  }
]
```

**Behavior:**
- Recursively scans for `.md` and `.txt` files
- Extracts `[IDX-...]` tags using regex pattern
- Captures nearest preceding heading for context
- Outputs relative paths from repository root

---

#### **scripts/generate_spec_mapping.py**

**Description:**  
Generates intelligent specification-to-code mappings from IDX tags found in documentation. Creates semantic mappings to target modules, functions, phases, and versions based on tag patterns. Outputs formatted Markdown documentation.

**Files Touched:**

**Files Read:**
- `docs/**/*.md` - Scans for IDX tags
- `docs/**/*.txt` - Scans for IDX tags
- `src/pipeline/spec_index.py` - Mapping logic and semantic rules

**Files Created:**
- `docs/spec/spec_index_map.md` - Generated mapping documentation

**Triggers:**
- **Manual execution:** `python scripts/generate_spec_mapping.py [--docs-dir DIR] [--output FILE] [--verbose]`
- **Documentation generation:** Run after spec document updates
- **Mapping regeneration:** Run when IDX tags are added/modified

**Command-line Options:**
- `--docs-dir` (default: `docs`): Documentation directory to scan
- `--output` (default: `docs/spec/spec_index_map.md`): Output file path
- `--verbose`: Print detailed progress information

**External Dependencies:**
- Python 3.8+
- `src/pipeline/spec_index` module

**Semantic Mapping Rules:**

**Module Assignment:**
- `IDX-DB-*` → `src/pipeline/db.py`
- `IDX-PROMPT-*` → `src/pipeline/prompts.py`
- `IDX-TOOL-*` → `src/pipeline/tools.py`
- `IDX-WORKTREE-*` → `src/pipeline/worktree.py`
- `IDX-STATE-*` → `src/pipeline/db.py`
- `IDX-SCHEMA-*` → `schema/schema.sql`
- `IDX-CB-*` → `src/pipeline/circuit_breakers.py`
- `IDX-RECOVERY-*` → `src/pipeline/recovery.py`

**Phase Assignment:**
- PH-01: Spec mapping, index scanning, module stubs
- PH-02: Database, state machine, CRUD operations
- PH-03: Tool adapters, profiles, integration
- PH-04: Orchestration, scheduling, execution
- PH-05: Circuit breakers, recovery, observability
- PH-06: Bundles, worktrees, full pipeline

**Version Assignment:**
- v1.0: Core functionality (IDX 01-50)
- v2.0: Enhanced features (IDX 51-99)
- v3.0: Advanced features (IDX 100+)

**Output:**
- Markdown document with mapping rules documentation
- Table of all IDX tags with inferred mappings
- Supports empty state with placeholder guidance

---

### 5. Database & State Management Scripts

#### **scripts/db_inspect.py**

**Description:**  
Inspects the pipeline database and prints table names with row counts. Useful for quick database verification and debugging.

**Files Touched:**

**Files Read:**
- `state/pipeline.db` (default, or path specified via `--db`)

**Triggers:**
- **Manual execution:** `python scripts/db_inspect.py [--db PATH]`
- **Database verification:** Run to check database state
- **Debugging:** Use to verify table creation and data presence

**Command-line Options:**
- `--db`: Custom database file path (default: uses `db.py` defaults)

**External Dependencies:**
- Python 3.8+
- SQLite3
- `src/pipeline/db` module

**Output:**
```
Tables:
  - runs: 5
  - workstreams: 12
  - events: 47
  - errors: 3
  - step_attempts: 18
```

**Behavior:**
- Connects to database
- Queries `sqlite_master` for table names
- Counts rows in each table
- Excludes SQLite system tables

---

#### **src/pipeline/db.py**

**Description:**  
Core database abstraction layer. Provides all database operations including connection management, schema initialization, CRUD operations for runs/workstreams/events/errors, and state machine validation.

**Files Touched:**

**Creates/Updates:**
- `state/pipeline.db` - Main database file (default location)

**Files Read:**
- `schema/schema.sql` - Database schema definition

**Triggers:**
- **Called by:**
  - `scripts/init_db.py` - Database initialization
  - `src/pipeline/orchestrator.py` - All orchestration operations
  - `scripts/db_inspect.py` - Database inspection
  - Any module requiring database access

**Key Functions:**
- `init_db(db_path, schema_path)` - Initialize/create database
- `get_connection(db_path)` - Get SQLite connection
- `create_run(run_id, status, metadata)` - Create new run
- `get_run(run_id)` - Retrieve run record
- `update_run_status(run_id, status)` - Update run status
- `create_workstream(ws_id, run_id, status, metadata)` - Create workstream
- `get_workstream(ws_id)` - Retrieve workstream record
- `update_workstream_status(ws_id, status)` - Update workstream status with state machine validation
- `validate_state_transition(from_state, to_state)` - Validate state transitions
- `record_event(event_type, run_id, ws_id, payload)` - Log event to events table
- `record_error(error_code, signature, message, run_id, ws_id, step_name, context)` - Record error
- `record_step_attempt(run_id, ws_id, step_name, outcome, started_at, completed_at, result)` - Record step execution
- `get_error_context(run_id, ws_id)` - Retrieve error pipeline context

**State Machine Transitions:**
- `pending` → `started`
- `started` → `editing`
- `editing` → `ready_for_static` | `failed`
- `ready_for_static` → `static_check`
- `static_check` → `runtime_tests` | `failed`
- `runtime_tests` → `done` | `failed`

**Database Schema Tables:**
- `runs` - Pipeline run metadata
- `workstreams` - Workstream execution records
- `events` - Event log (starts, ends, errors)
- `errors` - Error catalog with signatures
- `step_attempts` - Detailed step execution history
- `error_pipeline_contexts` - Error recovery state

---

### 6. Error Handling & Pipeline Scripts

#### **scripts/run_error_engine.py**

**Description:**  
Runs the deterministic error pipeline on specified files using a plugin-based validation system. Processes files through registered plugins, caches results, and reports validation status.

**Files Touched:**

**Files Read:**
- Files specified as command-line arguments
- `.state/validation_cache.json` (default cache location, configurable)

**Files Updated:**
- `.state/validation_cache.json` - File hash cache for incremental validation

**Triggers:**
- **Manual execution:** `python scripts/run_error_engine.py <files...> [--cache PATH]`
- **Validation workflow:** Run on Python, PowerShell, or other files requiring validation
- **CI/CD integration:** Can be integrated into automated validation pipelines

**Command-line Options:**
- `files` (required): One or more file paths to validate
- `--cache` (default: `.state/validation_cache.json`): Path to hash cache JSON file

**External Dependencies:**
- Python 3.8+
- `MOD_ERROR_PIPELINE.pipeline_engine` - Pipeline engine
- `MOD_ERROR_PIPELINE.plugin_manager` - Plugin system
- `MOD_ERROR_PIPELINE.file_hash_cache` - Caching system

**Exit Behavior:**
- Returns 0 if all files pass validation (no errors)
- Returns 1 if any file has validation errors
- Prints status summary for each file

**Output Format:**
```
file/path.py: PASSED | errors=0 warnings=2
file/path.ps1: FAILED | errors=3 warnings=1
```

**Behavior:**
- Loads file hash cache
- Creates cache directory if needed
- Processes each file through plugin pipeline
- Skips unchanged files (via hash comparison)
- Saves updated cache
- Reports error/warning counts

---

#### **src/pipeline/error_pipeline_cli.py**

**Description:**  
CLI interface for advancing the error pipeline state machine by one tick. Used for interactive or step-by-step error recovery workflows.

**Files Touched:**

**Files Read:**
- `state/pipeline.db` - Error context retrieval

**Files Updated:**
- `state/pipeline.db` - Updated error pipeline state

**Triggers:**
- **Manual execution:** `python -m src.pipeline.error_pipeline_cli --run-id RUN --ws-id WS [--py FILES] [--ps FILES]`
- **Error recovery:** Run to advance error recovery state machine
- **Interactive debugging:** Use for step-by-step error resolution

**Command-line Options:**
- `--run-id` (required): Run identifier
- `--ws-id` (required): Workstream identifier
- `--py`: Python files to include in error context
- `--ps`: PowerShell files to include in error context

**External Dependencies:**
- Python 3.8+
- `src.pipeline.error_context` - Error context data structures
- `src.pipeline.error_pipeline_service` - State machine tick logic
- `src.pipeline.db` - Database access

**Output:**
```
state=<current_state> attempt=<n> agent=<agent_id> final=<status>
```

**Behavior:**
- Retrieves error context from database
- Seeds target files if provided and context is empty
- Calls `tick()` to advance state machine one step
- Prints updated state information

---

#### **src/pipeline/error_engine.py**

**Description:**  
Error detection and recovery engine. Implements error state machine, coordinates error recovery workflows, and manages error pipeline contexts.

**Files Touched:**

**Files Read:**
- `state/pipeline.db` - Error contexts and recovery state

**Files Updated:**
- `state/pipeline.db` - Error recovery progress

**Triggers:**
- **Called by:**
  - `src/pipeline/error_pipeline_cli.py` - Interactive error recovery
  - `src/pipeline/error_pipeline_service.py` - Automated error handling
  - Orchestration modules - Error detection and routing

**Key Capabilities:**
- Error signature computation
- Error pattern recognition
- Recovery strategy selection
- Agent coordination for fixes
- State machine progression

**Integration Points:**
- Works with circuit breakers to prevent infinite loops
- Coordinates with orchestrator for fix attempts
- Uses database for persistence

---

### 7. Tool Integration & Monitoring Scripts

#### **scripts/aim_status.py**

**Description:**  
AIM (AI Tools Registry) status utility. Displays tool detection status, version information, and capability routing configuration for all tools in the AIM registry.

**Files Touched:**

**Files Read:**
- `.AIM_ai-tools-registry/` - AIM registry directory
- `.AIM_ai-tools-registry/registry.json` (or similar) - Tool registry data
- `Coordination Mechanisms/coordination_rules.json` (or similar) - Capability routing rules
- `src/pipeline/aim_bridge.py` - AIM bridge functions

**Triggers:**
- **Manual execution:** `python scripts/aim_status.py`
- **Tool verification:** Run to check which AI tools are detected
- **Configuration debugging:** Use to verify capability routing

**External Dependencies:**
- Python 3.8+
- `src/pipeline/aim_bridge` module
- AIM registry directory structure

**Output Sections:**

1. **AIM Registry Path:** Shows location of registry
2. **Tool Detection Table:**
   ```
   Tool ID              Detected     Version
   ======================================================================
   aider                Yes          0.44.0
   codex                No           N/A
   claude-cli           Yes          1.2.3
   ```
3. **Capability Routing:**
   ```
   Capability Routing:
   ======================================================================
   
   code_editing:
     Primary:  aider
     Fallback: codex, claude-cli
   
   documentation:
     Primary:  claude-cli
     Fallback: (none)
   ```

**Behavior:**
- Loads AIM registry
- Detects each registered tool
- Queries tool versions where available
- Loads and displays capability routing rules
- Reports primary and fallback tool assignments

---

#### **src/pipeline/aim_bridge.py**

**Description:**  
Bridge module for AIM (AI Tools Registry) integration. Provides functions for tool detection, version querying, registry loading, and capability routing.

**Files Touched:**

**Files Read:**
- `.AIM_ai-tools-registry/` - Registry structure and metadata
- Registry configuration files (JSON/YAML)
- Coordination rules configuration

**Triggers:**
- **Called by:**
  - `scripts/aim_status.py` - Status reporting
  - `src/pipeline/tools.py` - Tool routing decisions
  - `src/pipeline/prompts.py` - AI tool selection
  - Orchestration components - Capability-based tool selection

**Key Functions:**
- `detect_tool(tool_id)` - Check if tool is available
- `get_tool_version(tool_id)` - Query tool version
- `load_aim_registry()` - Load registry data
- `get_aim_registry_path()` - Get registry directory path
- `load_coordination_rules()` - Load capability routing configuration
- `route_to_capability(capability)` - Select tool for capability

**Behavior:**
- Lazy loading of registry data
- Tool detection via command execution
- Version parsing from tool output
- Capability-based routing with fallbacks

---

### 8. Testing Scripts

#### **scripts/test.ps1**

**Description:**  
PowerShell test runner for repository validation. Runs basic checks to verify repository setup and script availability.

**Files Touched:**

**Files Read:**
- Repository files (for verification checks)

**Triggers:**
- **Manual execution:** `pwsh scripts/test.ps1`
- **Post-bootstrap:** Run after `bootstrap.ps1` to verify setup
- **CI/CD validation:** Can be integrated into automated testing

**External Dependencies:**
- PowerShell 7+

**Behavior:**
- Verifies directory structure
- Checks script availability
- Reports test results
- Returns appropriate exit code

---

## File Interaction Matrix

| Script | Database | Workstreams | Schema | Docs | Config | Git | Source Code |
|--------|----------|-------------|--------|------|--------|-----|-------------|
| **bootstrap.ps1** | ❌ | ❌ | ❌ | Creates | ❌ | ❌ | ❌ |
| **init_db.py** | Creates | ❌ | Reads | ❌ | ❌ | ❌ | ❌ |
| **run_workstream.py** | Updates | Reads | ❌ | ❌ | Reads | Uses | Updates |
| **orchestrator.py** | Writes | Reads | ❌ | ❌ | Reads | Uses | Updates |
| **generate_workstreams.py** | ❌ | Creates | ❌ | ❌ | ❌ | ❌ | ❌ |
| **validate_workstreams.py** | Optional | Reads | ❌ | ❌ | ❌ | ❌ | ❌ |
| **validate_workstreams_authoring.py** | ❌ | Reads | ❌ | ❌ | ❌ | ❌ | ❌ |
| **check_workstream_status.ps1** | ❌ | ❌ | Checks | Checks | Checks | Reads | Checks |
| **check_workstream_status.sh** | ❌ | ❌ | Checks | Checks | Checks | Reads | Checks |
| **generate_spec_index.py** | ❌ | ❌ | ❌ | Reads | ❌ | ❌ | ❌ |
| **generate_spec_mapping.py** | ❌ | ❌ | ❌ | Reads/Creates | ❌ | ❌ | ❌ |
| **db_inspect.py** | Reads | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **run_error_engine.py** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | Validates |
| **error_pipeline_cli.py** | Updates | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **aim_status.py** | ❌ | ❌ | ❌ | ❌ | Reads | ❌ | ❌ |

**Legend:**
- ✅ Creates - Script creates this type of file
- 📖 Reads - Script reads this type of file
- ✏️ Updates - Script modifies this type of file
- 🔍 Checks - Script verifies existence/implementation
- 🔧 Uses - Script uses this system (e.g., Git operations)
- ❌ - No interaction

---

## Trigger Mechanisms

### Manual Triggers (CLI Execution)

All scripts can be executed manually via command line:

```bash
# Bootstrap
pwsh ./scripts/bootstrap.ps1

# Database
python scripts/init_db.py [--db PATH] [--schema PATH]
python scripts/db_inspect.py [--db PATH]

# Workstream Orchestration
python scripts/run_workstream.py --ws-id <id> [--run-id <id>] [--dry-run]
python scripts/generate_workstreams.py --spec-id <id> [--output-dir DIR]

# Validation
python scripts/validate_workstreams.py [--run-id <id>] [--json]
python scripts/validate_workstreams_authoring.py [--dir DIR] [--json]
pwsh scripts/check_workstream_status.ps1
bash scripts/check_workstream_status.sh

# Code Generation
python scripts/generate_spec_index.py [--docs-dir DIR] [--format FORMAT]
python scripts/generate_spec_mapping.py [--docs-dir DIR] [--output FILE]

# Error Pipeline
python scripts/run_error_engine.py <files...> [--cache PATH]
python -m src.pipeline.error_pipeline_cli --run-id <id> --ws-id <id>

# Tool Status
python scripts/aim_status.py

# Testing
pwsh ./scripts/test.ps1
```

### Programmatic Triggers (Function Calls)

Many orchestration components are called programmatically:

```python
# From scripts
from src.pipeline import orchestrator
result = orchestrator.run_single_workstream_from_bundle(ws_id, run_id, context)

# From modules
from src.pipeline import db
db.init_db()
db.create_run(run_id, status="in_progress")

# From error pipeline
from src.pipeline.error_pipeline_service import tick
ctx = tick(error_context)
```

### Automated Triggers (Future)

Planned automated triggers (not yet implemented):

- **GitHub Actions Workflows:** CI/CD integration for validation and orchestration
- **Cron Jobs:** Scheduled workstream execution
- **Git Hooks:** Pre-commit validation, post-merge orchestration
- **Event-Based:** Webhook triggers from issue trackers or spec systems
- **Watch Mode:** File system monitoring for spec changes

### Environment-Based Triggers

Some scripts modify behavior based on environment:

```bash
# Dry-run mode
PIPELINE_DRY_RUN=1 python scripts/run_workstream.py --ws-id ws-test

# Custom database location
export PIPELINE_DB_PATH=/custom/path/pipeline.db
python scripts/init_db.py

# Custom workstream directory
export PIPELINE_WORKSTREAM_DIR=/custom/workstreams
python scripts/validate_workstreams.py
```

---

## Dependencies & Execution Flow

### Typical Orchestration Workflow

```
1. bootstrap.ps1
   ↓ (creates directory structure)
   
2. init_db.py
   ↓ (initializes database)
   
3. generate_workstreams.py (optional)
   ↓ (creates workstream bundles from specs)
   
4. validate_workstreams_authoring.py
   ↓ (validates bundle syntax and structure)
   
5. validate_workstreams.py
   ↓ (validates bundles and checks for conflicts)
   
6. run_workstream.py
   ↓ (executes workstream via orchestrator)
   
7. check_workstream_status.ps1 / .sh
   ↓ (verifies completion status)
```

### Orchestrator Internal Flow

```
orchestrator.py
├── run_single_workstream_from_bundle()
│   ├── Load bundle from workstreams/*.json
│   └── Call run_workstream()
│
└── run_workstream()
    ├── Initialize DB records (run, workstream)
    │
    ├── run_edit_step()
    │   ├── Create worktree (worktree.py)
    │   ├── Run Aider edit (prompts.py)
    │   └── Record to DB
    │
    ├── run_static_with_fix()
    │   ├── run_static_step()
    │   │   └── Execute static tools (tools.py)
    │   │
    │   └── FIX loop (if failed)
    │       ├── Check circuit breakers (circuit_breakers.py)
    │       ├── Record error (db.py)
    │       ├── Run Aider fix (prompts.py)
    │       └── Retry static step
    │
    ├── run_runtime_with_fix()
    │   ├── run_runtime_step()
    │   │   └── Execute runtime tools (tools.py)
    │   │
    │   └── FIX loop (if failed)
    │       └── (similar to static fix loop)
    │
    └── Validate scope (worktree.py)
```

### Database Interaction Flow

```
Scripts/Modules
    ↓
db.py (abstraction layer)
    ↓
SQLite Connection
    ↓
state/pipeline.db
    ├── runs
    ├── workstreams
    ├── events
    ├── errors
    ├── step_attempts
    └── error_pipeline_contexts
```

### Tool Integration Flow

```
orchestrator.py
    ↓
tools.py::run_tool(tool_id, config)
    ↓
aim_bridge.py (route to capability)
    ↓
AIM Registry (.AIM_ai-tools-registry/)
    ↓
Tool Profiles (config/tool_profiles.json)
    ↓
External Tools (aider, pytest, linters, etc.)
```

---

## Script Dependency Graph

```
bootstrap.ps1 (no dependencies)
    ↓
init_db.py
    ├── src/pipeline/db.py
    └── schema/schema.sql
        ↓
validate_workstreams_authoring.py
    └── src/pipeline/bundles.py
        ↓
validate_workstreams.py
    ├── src/pipeline/bundles.py
    └── src/pipeline/db.py (optional)
        ↓
run_workstream.py
    └── src/pipeline/orchestrator.py
        ├── src/pipeline/db.py
        ├── src/pipeline/bundles.py
        ├── src/pipeline/worktree.py
        ├── src/pipeline/tools.py
        │   ├── src/pipeline/aim_bridge.py
        │   └── config/tool_profiles.json
        ├── src/pipeline/prompts.py
        └── src/pipeline/circuit_breakers.py
            └── config/circuit_breakers.yaml
```

**Parallel/Independent Scripts:**
- `generate_spec_index.py` (independent)
- `generate_spec_mapping.py` (uses spec_index.py)
- `db_inspect.py` (requires db.py)
- `check_workstream_status.ps1/.sh` (git only)
- `aim_status.py` (requires aim_bridge.py)
- `run_error_engine.py` (MOD_ERROR_PIPELINE)
- `error_pipeline_cli.py` (db.py + error modules)
- `generate_workstreams.py` (uses planner.py stub)

---

## Key Configuration Files

### Files That Control Orchestration Behavior

1. **workstreams/*.json** - Workstream bundle definitions
   - Defines what files to edit
   - Specifies tools to use
   - Lists acceptance tests
   - Declares dependencies

2. **schema/schema.sql** - Database schema
   - Defines tables and relationships
   - Controls state machine transitions
   - Structures telemetry data

3. **config/tool_profiles.json** - Tool adapter configurations
   - Maps tool IDs to execution commands
   - Specifies success/failure patterns
   - Configures tool-specific options

4. **config/circuit_breakers.yaml** - Circuit breaker rules
   - Max fix attempts per step
   - Error signature repetition limits
   - Diff oscillation detection thresholds

5. **.AIM_ai-tools-registry/** - AI tools registry
   - Tool detection and capability metadata
   - Coordination and routing rules
   - Tool version requirements

6. **Coordination Mechanisms/** - Capability routing
   - Primary and fallback tool assignments
   - Capability definitions
   - Agent coordination rules

---

## Environment Variables

| Variable | Used By | Purpose |
|----------|---------|---------|
| `PIPELINE_DRY_RUN` | orchestrator.py, run_workstream.py | Enable simulation mode |
| `PIPELINE_DB_PATH` | db.py, init_db.py | Custom database location |
| `PIPELINE_WORKSTREAM_DIR` | bundles.py, validation scripts | Custom workstreams directory |
| `PIPELINE_SCHEMA_PATH` | db.py | Custom schema file location |

---

## Exit Codes

| Exit Code | Meaning | Scripts Using |
|-----------|---------|---------------|
| 0 | Success | All scripts |
| 1 | Validation/execution failure | Most scripts |
| 2 | CLI argument error | run_workstream.py |

---

## Summary

This repository contains a comprehensive orchestration system with 15+ scripts managing:

- **17 workstreams** across 6 phases (PH-00 to PH-05)
- **Database-driven state management** with SQLite
- **Git worktree isolation** for parallel development
- **AI tool integration** via AIM registry
- **Circuit breakers** to prevent infinite loops
- **Comprehensive telemetry** and error tracking
- **Cross-platform support** (PowerShell, Bash, Python)

The orchestration scripts enable:
- Automated workstream execution
- Validation and verification
- Error recovery and FIX loops
- Specification-to-code mapping
- Tool status monitoring
- Database inspection and debugging

All scripts are designed for both manual CLI execution and programmatic integration into larger automation workflows.

---

**Generated:** 2025-11-17  
**Repository:** [DICKY1987/complete-ai-development-pipeline-canonical-phase-plan](https://github.com/DICKY1987/complete-ai-development-pipeline-canonical-phase-plan)
