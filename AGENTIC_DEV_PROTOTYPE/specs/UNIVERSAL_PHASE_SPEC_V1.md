# Universal Phase Specification v1.0

**Document ID:** UNIVERSAL_PHASE_SPEC_V1  
**Version:** 1.0.0  
**Last Updated:** 2025-11-20  
**Status:** Canonical  

---

## UPS-001: Overview {#UPS-001}

This specification defines the **mandatory structure and gates** for all development phases executed by autonomous AI agents in the Game Board Protocol system.

**Non-Negotiable Rule:** If an AI cannot populate every required field and satisfy every gate defined here, it **MUST NOT** proceed with that phase.

---

## UPS-002: Phase Identity & Metadata {#UPS-002}

Every phase **MUST** be represented as a structured record (JSON/YAML) with the following minimum fields:

### UPS-002.1: phase_id (REQUIRED) {#UPS-002-1}

- **Format:** String matching pattern `^PH-[0-9A-Z]+$`
- **Examples:** `"PH-00"`, `"PH-01A"`, `"PH-01B"`, `"PH-02"`
- **Purpose:** Uniquely identifies the phase in the global plan
- **Validation:** Must be unique across all phases

### UPS-002.2: workstream_id (REQUIRED) {#UPS-002-2}

- **Format:** String matching pattern `^ws-[a-z0-9-]+$`
- **Examples:** 
  - `"ws-22-pipeline-plus-phase0-schema"`
  - `"ws-23-pipeline-plus-phase1a-task-queue"`
- **Purpose:** Machine-focused globally unique identifier
- **Validation:** Must match corresponding `workstreams/*.json` ID

### UPS-002.3: title (REQUIRED) {#UPS-002-3}

- **Format:** Short, single-focus description (max 100 characters)
- **Examples:**
  - `"Pre-Flight & Schema Setup"`
  - `"Task Queue Management"`
  - `"Audit & Telemetry Foundation"`
- **Purpose:** Human-readable phase name

### UPS-002.4: objective (REQUIRED) {#UPS-002-4}

- **Format:** One tight, atomic goal in plain language
- **Examples:**
  - `"Create and validate the .tasks/.ledger/.runs directory structure and baseline schema migration for patch support"`
  - `"Implement file-based task queue plus tests for enqueue/dequeue lifecycle"`
- **Validation:** Must be a single goal, not a shopping list
- **Purpose:** Defines verifiable outcome

### UPS-002.5: phase_type (REQUIRED) {#UPS-002-5}

- **Format:** Enumerated value
- **Allowed Values:**
  - `implementation` - New feature or component
  - `refactor` - Code restructuring without behavior change
  - `integration` - Combining multiple components
  - `migration` - Data or schema migration
  - `validation_only` - Testing and validation
  - `documentation_only` - Documentation updates
- **Purpose:** Categorizes phase for orchestration

### UPS-002.6: parallel_group (OPTIONAL) {#UPS-002-6}

- **Format:** String identifier for parallel execution group
- **Examples:**
  - `phase_id: PH-01A, parallel_group: "G1"`
  - `phase_id: PH-01B, parallel_group: "G1"`
- **Purpose:** Enables concurrent execution of compatible phases
- **Pattern:** Phase 0 → Phase 1A & 1B in parallel

---

## UPS-003: Dependencies & Ordering {#UPS-003}

Every phase **MUST** explicitly define dependency ordering to ensure correct execution sequence.

### UPS-003.1: depends_on (REQUIRED) {#UPS-003-1}

- **Format:** List of `workstream_id` or `phase_id` strings
- **Example:** `["ws-22-pipeline-plus-phase0-schema"]`
- **Validation Rule:** AI **MUST NOT** start a phase until all dependencies are in programmatically verified "done" state
- **Empty List:** Allowed for initial phases (e.g., Phase 0)

### UPS-003.2: may_run_parallel_with (OPTIONAL) {#UPS-003-2}

- **Format:** List of `workstream_id` or `phase_id` strings
- **Example:** `["ws-24-pipeline-plus-phase1b-audit"]`
- **Purpose:** Declares safe concurrent execution

### UPS-003.3: Parallelization Rules {#UPS-003-3}

Parallel execution (e.g., **PH-01A & PH-01B**) is allowed **ONLY** when:

1. All shared dependencies (e.g., PH-00) are verified complete
2. File scopes do not overlap except for explicitly declared shared read-only resources
3. Both phases are in the same `parallel_group`
4. No circular dependencies exist

**Validation:** Orchestrator must verify these conditions before parallel execution.

---

## UPS-004: File Scope Declaration {#UPS-004}

Each phase **MUST** declare a precise file scope. This drives patch validation and isolation.

### UPS-004.1: File Scope Structure {#UPS-004-1}

```yaml
file_scope:
  create:
    - "core/state/task_queue.py"
    - "core/state/audit_logger.py"
    - "tests/test_task_queue.py"
    - "tests/test_audit_logger.py"
  modify:
    - "scripts/SubmitTask.ps1"
    - "core/db.py"
  read_only:
    - "schema/workstream.schema.json"
    - "config/router.config.yaml"
    - "tests/conftest.py"
```

### UPS-004.2: File Scope Requirements {#UPS-004-2}

1. **create (REQUIRED)** - List of files that may be created
   - AI **MUST** restrict new file creation to this list
   - For directory creation phases, explicitly enumerate directory hierarchy

2. **modify (OPTIONAL)** - List of files that may be edited
   - AI **MUST** restrict edits to files in `create` + `modify`
   
3. **read_only (OPTIONAL)** - Files that may be read for context
   - Files in `read_only` **MUST NOT** be modified
   - Used for context gathering only

### UPS-004.3: Scope Validation {#UPS-004-3}

**Critical Rule:** Any patch touching paths outside `create` + `modify` is a **scope violation** and **MUST** be rejected by validation gates.

**Directory Creation:** For phases that create directories (e.g., Phase 0), the directory hierarchy **MUST** be explicitly enumerated in `file_scope.create`.

---

## UPS-005: Tooling & Environment Specification {#UPS-005}

Each phase **MUST** declare the tools and environment assumptions it relies on.

### UPS-005.1: Tool Declaration Structure {#UPS-005-1}

```yaml
tools:
  primary_language: "python"
  secondary_language: "powershell"
  ai_tools:
    - "aider"
  test_runners:
    - "python -m pytest -q"
  static_checkers:
    - "ruff check"
  shell:
    preferred: "pwsh"
    alternatives: ["bash"]
```

### UPS-005.2: Tool Usage Rules {#UPS-005-2}

1. AI **MUST** use declared commands to validate work
2. No ad-hoc, undocumented commands as the only proof
3. If environment is missing a required tool:
   - Phase **MUST** invoke self-healing procedures (e.g., `pip install`, `winget install`)
   - **OR** fail fast with clear error message

---

## UPS-006: Pre-Flight Check {#UPS-006}

Before executing any implementation steps, the AI **MUST** perform a Pre-Flight Check and **MUST NOT** proceed if any check fails.

### UPS-006.1: Git & Worktree State {#UPS-006-1}

- `git status --porcelain` confirms:
  - No unexpected uncommitted changes, **OR**
  - All changes explicitly associated with current workstream
- For non-trivial phases:
  - Dedicated worktree exists: `.worktrees/{workstream_id}/`
  - Current working directory is the correct worktree

### UPS-006.2: Repository Location {#UPS-006-2}

- Confirm current directory matches declared `repo_path`
- Verify path contains expected project identifiers

### UPS-006.3: Architecture Baseline {#UPS-006-3}

For phases **after PH-00**, verify:

- `.tasks/inbox`, `.tasks/running`, `.tasks/done`, `.tasks/failed` exist
- `.ledger/patches/` exists
- `.runs/` exists
- Required schema migrations exist
- Required config files exist

**Failure Response:** If missing, AI **MUST** either:
- Re-run Phase 0, **OR**
- Self-heal by creating artifacts according to standard schema

### UPS-006.4: Environment & Dependencies {#UPS-006-4}

- Python version meets or exceeds required version
- Virtual environment exists and is activatable (or explicit choice not to use venv)
- Critical dependencies for this phase are installed

### UPS-006.5: Workstream Definition Validation {#UPS-006-5}

- Corresponding `workstreams/{workstream_id}.json` exists
- Validates against `schema/workstream.schema.json`

### UPS-006.6: Pre-Flight Output Requirements {#UPS-006-6}

- Pre-flight **MUST** be captured as CLI output showing all checks and pass/fail status
- If any check fails:
  - AI **MUST** attempt self-healing
  - If self-healing fails, phase is **blocked** (not "done")

---

## UPS-007: Programmatic Acceptance Tests {#UPS-007}

Every phase **MUST** define acceptance tests that can be evaluated programmatically through CLI commands.

### UPS-007.1: Acceptance Test Structure {#UPS-007-1}

```yaml
acceptance:
  powershell:
    - name: "Phase 0 directories exist"
      command: >
        Write-Host "=== Phase 0 Acceptance Tests ===";
        @('.tasks\inbox', '.tasks\running', '.tasks\done', '.tasks\failed', 
          '.ledger\patches', '.runs') |
          ForEach-Object { if (-not (Test-Path "$_\.gitkeep")) { 
            throw "Missing $_\.gitkeep" 
          }}
    - name: "Migration file exists"
      command: >
        if (-not (Test-Path "schema\migrations\001_add_patches_table.sql")) { 
          throw "Missing migration" 
        }
  python:
    - name: "Phase 1 queue & audit tests"
      command: "python -m pytest -q tests/test_task_queue.py tests/test_audit_logger.py"
      success_pattern: "passed"
      max_failures: 0
```

### UPS-007.2: Acceptance Test Rules {#UPS-007-2}

1. **Conversation text is never sufficient**
   - "Looks good", "Seems complete", "I have implemented X" **do not count** as acceptance

2. **AI MUST run all declared acceptance commands**
   - No exceptions or shortcuts

3. **Phase completion criteria:**
   - All acceptance commands exit with **code 0**, **AND**
   - Outputs contain expected success patterns (e.g., `"20 passed"`)

4. **Failure response:**
   - Phase **MUST** remain **not done**
   - AI **MUST** enter self-healing loop

### UPS-007.3: Test Categories {#UPS-007-3}

**Filesystem & Config Checks:**
- `Test-Path` or equivalent for each required directory/file
- Verify `.tasks/*`, `.ledger/patches`, `.runs`, schema migrations, configs

**Behavioral Tests:**
- Specific test modules for the phase
- Examples: `tests/test_task_queue.py`, `tests/test_audit_logger.py`
- Invoked with deterministic commands

---

## UPS-008: Output Artifacts & Logging {#UPS-008}

Each phase **MUST** produce documented artifacts for traceability and rollback capability.

### UPS-008.1: Patch Artifacts {#UPS-008-1}

For any code changes:
- **Storage:** `.ledger/patches/{workstream_id}-{run_id}.patch`
- **Format:** Unified diff format
- **Metadata:** Recorded in patches table (see schema migrations)

### UPS-008.2: Audit Entries {#UPS-008-2}

**File:** `.runs/audit.jsonl`

**Required Fields:**
- `event_type` (e.g., `patch_captured`, `patch_validated`, `completed`)
- `task_id` / `ws_id`
- `timestamp`
- `tool_used`
- `status`

### UPS-008.3: Test Output Logs {#UPS-008-3}

- Stored directly in `.runs/` **OR**
- Retrievable via JSONL logs
- Must be timestamped and linked to phase execution

### UPS-008.4: Completion Requirement {#UPS-008-4}

**Critical Rule:** No phase is **complete** until these artifacts exist and pass their validations.

---

## UPS-009: Self-Healing & Error Recovery {#UPS-009}

AI agents **MUST** implement autonomous error recovery following these principles:

### UPS-009.1: Self-Healing Loop {#UPS-009-1}

1. **Detect** - Run verification commands
2. **Diagnose** - Identify specific failure
3. **Repair** - Apply targeted fix
4. **Re-verify** - Run tests again
5. **Repeat** - Until success or max attempts exceeded

### UPS-009.2: Common Self-Healing Actions {#UPS-009-2}

- Create missing directories
- Install missing dependencies
- Fix syntax errors
- Regenerate corrupted files
- Re-run failed migrations

### UPS-009.3: Escalation Criteria {#UPS-009-3}

AI **MUST** escalate (mark phase as blocked) when:
- Self-healing attempts exceed 3 iterations
- Fundamental prerequisite is missing (e.g., wrong repository)
- Unrecoverable environment issue detected

---

## UPS-010: Phase State Machine {#UPS-010}

Every phase progresses through these states:

### UPS-010.1: State Definitions {#UPS-010-1}

- **NOT_STARTED** - Initial state, dependencies may not be satisfied
- **READY** - Dependencies satisfied, ready to queue
- **QUEUED** - In task queue, awaiting execution
- **RUNNING** - Currently executing
- **VALIDATING** - Executing acceptance tests
- **COMPLETE** - All acceptance tests passed
- **FAILED** - Acceptance tests failed after max retries
- **BLOCKED** - Cannot proceed due to environment or dependency issues

### UPS-010.2: State Transitions {#UPS-010-2}

```
NOT_STARTED → READY (when dependencies complete)
READY → QUEUED (by orchestrator)
QUEUED → RUNNING (by executor)
RUNNING → VALIDATING (after implementation)
VALIDATING → COMPLETE (tests pass)
VALIDATING → RUNNING (tests fail, retry)
RUNNING → BLOCKED (unrecoverable error)
RUNNING → FAILED (max retries exceeded)
```

### UPS-010.3: Terminal States {#UPS-010-3}

- **COMPLETE** - Success, next phases can proceed
- **FAILED** - Permanent failure, requires manual intervention
- **BLOCKED** - Waiting for external resolution

---

## UPS-011: Validation Gates {#UPS-011}

Every phase submission **MUST** pass these validation gates before execution:

### UPS-011.1: Schema Validation {#UPS-011-1}

- Phase specification validates against JSON schema
- All required fields present
- Field formats correct

### UPS-011.2: Dependency Validation {#UPS-011-2}

- All `depends_on` phases exist
- No circular dependencies
- Parallel group conflicts detected

### UPS-011.3: File Scope Validation {#UPS-011-3}

- No overlapping `create`/`modify` scopes in parallel phases
- All paths are valid relative paths
- No absolute paths or path traversal attacks

### UPS-011.4: Guard Rules Validation {#UPS-011-4}

- Phase conforms to development rules (DR-DO-*, DR-DONT-*)
- Anti-patterns detected and blocked
- Best practices enforced

---

## UPS-012: Cross-References {#UPS-012}

This specification is part of the Game Board Protocol specification suite:

**Related Specifications:**
- **PPS-*** - PRO Phase Specification (professional template)
- **DR-DO-*** - Development Rules (DO practices)
- **DR-DONT-*** - Development Rules (DONT anti-patterns)

**Implementation Components:**
- Schema Generator (Phase 1E)
- Spec Renderer (Phase 1F)
- Validation Gateway (Phase 2C)

---

## UPS-013: Version History {#UPS-013}

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2025-11-20 | Initial machine-readable version with stable IDs | Game Board Protocol |

---

**END OF SPECIFICATION**
