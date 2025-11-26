# Pattern Execution Visualization Design

**Document Version**: 1.0.0
**Created**: 2025-11-26
**Status**: Design Specification

---

## Table of Contents

1. [Pattern Module Lifecycle (Formalized)](#1-pattern-module-lifecycle-formalized)
2. [Internal API Surface](#2-internal-api-surface)
3. [Event Model & Data Contracts](#3-event-model--data-contracts)
4. [Pattern Activity Panel UX Specification](#4-pattern-activity-panel-ux-specification)
5. [Implementation Pseudocode](#5-implementation-pseudocode)
6. [Assumptions & Design Decisions](#6-assumptions--design-decisions)

---

## 1. Pattern Module Lifecycle (Formalized)

### Lifecycle Phases

The pattern module operates through **5 distinct phases**, each with clear boundaries, inputs, and outputs:

```
┌─────────────────────────────────────────────────────────────┐
│  PATTERN EXECUTION LIFECYCLE                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   PHASE 1    │───>│   PHASE 2    │───>│   PHASE 3    │ │
│  │  Selection   │    │  Expansion   │    │  Validation  │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│         │                                        │          │
│         v                                        v          │
│  ┌──────────────┐                        ┌──────────────┐ │
│  │   PHASE 4    │<───────────────────────│   PHASE 5    │ │
│  │  Execution   │                        │ Persistence  │ │
│  └──────────────┘                        └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Phase 1: Pattern Selection & Resolution

**Purpose**: Match job step requirements to available patterns

**Inputs**:
- `job_id`: ULID
- `step_id`: ULID
- `operation_kind`: string (e.g., "semgrep_scan", "pytest_suite")
- `pattern_id`: optional ULID (explicit pattern override)
- `context`: object (tool, language, file_type, project_type)
- `profile_preferences`: array of pattern_ids from PROJECT_PROFILE

**Process**:
1. Check for explicit `pattern_id` → use if valid
2. Query pattern registry with `operation_kind` + `context`
3. Apply profile preferences as prioritization filter
4. Select highest-priority matching pattern
5. Validate pattern is compatible with current environment

**Outputs**:
- `pattern_binding`: object containing:
  ```typescript
  {
    pattern_id: string,        // PAT-ULID
    operation_kind: string,
    job_id: string,
    step_id: string,
    selection_metadata: {
      selection_method: "explicit" | "context_match" | "profile_preference",
      candidates_evaluated: number,
      match_score: number
    }
  }
  ```

**Events Emitted**:
- `pattern.selection.started`
- `pattern.selection.resolved` | `pattern.selection.failed`

---

### Phase 2: Template Expansion & Materialization

**Purpose**: Fill pattern template with concrete values to produce executable configuration

**Inputs**:
- `pattern_binding` (from Phase 1)
- `pattern_spec`: loaded from pattern doc suite
- `job_state`: current job data (from job file)
- `project_profile`: UET configuration
- `engine_state`: runtime context (worktree path, repo path, env vars)

**Process**:
1. Load pattern spec document (includes templates, schemas, defaults)
2. Build variable resolution context from all input sources (priority order)
3. Render all template sections:
   - Command line templates → concrete shell commands
   - Prompt templates → filled prompt blocks (for LLM tools)
   - Config templates → materialized sidecar config files
4. Apply defaults for any unspecified optional parameters
5. Generate unique identifiers for all artifacts

**Outputs**:
- `materialized_pattern`: object containing:
  ```typescript
  {
    pattern_run_id: string,     // PRUN-ULID (generated here)
    pattern_id: string,
    commands: string[],          // Rendered commands ready to execute
    prompts: object[],           // For LLM tools
    config_files: Map<string, string>,  // path -> content
    artifact_paths: {            // Expected output locations
      reports: string[],
      logs: string[],
      patches: string[]
    },
    resolved_inputs: object,     // All variables with final values
    metadata: {
      template_version: string,
      expansion_timestamp: string
    }
  }
  ```

**Events Emitted**:
- `pattern.template.expansion_started`
- `pattern.template.expanded` | `pattern.template.expansion_failed`

---

### Phase 3: Pre-execution Validation & Guardrails

**Purpose**: Verify execution prerequisites and validate inputs before running

**Inputs**:
- `materialized_pattern` (from Phase 2)
- `pattern_spec.validation_rules`: validation rules from pattern doc

**Process**:
1. **Schema Validation**: Validate `resolved_inputs` against pattern's input schema
2. **Preflight Checks**:
   - Verify all target paths exist (if required)
   - Check tool availability (command exists, correct version)
   - Validate required sidecar files are present
   - Check environment prerequisites (env vars, permissions)
3. **Resource Checks**:
   - Disk space for expected outputs
   - Memory requirements (if specified)
4. Build validation report with pass/fail per check

**Outputs**:
- `validation_result`: object containing:
  ```typescript
  {
    pattern_run_id: string,
    overall_status: "pass" | "fail" | "warning",
    checks: [{
      check_name: string,
      status: "pass" | "fail" | "skip",
      message: string,
      severity: "error" | "warning" | "info"
    }],
    validated_at: string,
    can_proceed: boolean
  }
  ```

**Events Emitted**:
- `pattern.validation.started`
- `pattern.validation.completed` | `pattern.validation.failed`

**Control Flow**:
- If `validation_result.can_proceed === false` → abort, emit failure event, skip to Phase 5
- Else → proceed to Phase 4

---

### Phase 4: Execution & Observation

**Purpose**: Execute the pattern's commands/operations and capture all outputs

**Inputs**:
- `materialized_pattern` (from Phase 2)
- `execution_context`: timeout, max_retries, circuit_breaker_state

**Process**:
1. Write any sidecar config files to disk
2. Set up output capture (stdout, stderr, timing)
3. Execute command(s) in sequence (or parallel if pattern supports)
4. Monitor execution:
   - Capture real-time stdout/stderr streams
   - Track elapsed time
   - Monitor for timeout conditions
5. Collect artifacts:
   - Scan expected artifact paths
   - Compute checksums
   - Validate artifact schemas (for JSON/YAML outputs)
6. Apply post-execution rules:
   - Check exit codes against expected values
   - Apply "no diagnostics → error" rules if configured
   - Normalize tool-specific outputs to common format

**Outputs**:
- `pattern_result`: object containing:
  ```typescript
  {
    pattern_run_id: string,
    pattern_id: string,
    job_id: string,
    step_id: string,
    status: "success" | "failure" | "timeout" | "skipped",
    execution: {
      commands_run: string[],
      tool_exit_codes: number[],
      stdout: string,
      stderr: string,
      started_at: string,       // ISO 8601
      finished_at: string,
      duration_seconds: number
    },
    outputs: {
      finding_count?: number,   // Tool-specific metrics
      lines_changed?: number,
      tests_passed?: number,
      // ... extensible
    },
    artifacts: [{
      path: string,
      type: "report" | "log" | "patch" | "config",
      size_bytes: number,
      checksum_sha256: string,
      validated: boolean
    }],
    metadata: {
      retry_count: number,
      circuit_breaker_triggered: boolean
    }
  }
  ```

**Events Emitted**:
- `pattern.execution.started`
- `pattern.execution.progress` (optional, for long-running operations)
- `pattern.execution.completed` | `pattern.execution.failed` | `pattern.execution.timeout`

---

### Phase 5: Result Persistence & Routing

**Purpose**: Store execution results and route to appropriate consumers

**Inputs**:
- `pattern_result` (from Phase 4)
- `validation_result` (from Phase 3)
- `pattern_binding` (from Phase 1)

**Process**:
1. Generate complete `pattern_run_record` combining all phase outputs
2. Persist to state store:
   - DB: Insert into `pattern_runs` table
   - JSONL: Append to job-specific pattern log
3. Update related entities:
   - Link pattern_run to job step state
   - Update job-level pattern usage statistics
   - Record in worktree state if applicable
4. Route results:
   - Emit final event to event bus
   - Notify subscribed components (GUI/TUI)
   - Trigger downstream workflow steps if configured

**Outputs**:
- `pattern_run_record`: complete immutable record in state store
- Side effects: DB updates, file writes, event emissions

**Events Emitted**:
- `pattern.result.persisted`

---

## 2. Internal API Surface

### Core Pattern Module Interface

```typescript
/**
 * Main orchestrator for pattern-based execution
 */
interface IPatternExecutor {
  /**
   * Execute a complete pattern lifecycle for a job step
   */
  executePattern(request: PatternExecutionRequest): Promise<PatternResult>;

  /**
   * Get available patterns matching criteria
   */
  queryPatterns(filter: PatternFilter): Promise<PatternInfo[]>;

  /**
   * Validate a pattern without executing it
   */
  validatePattern(patternId: string, inputs: object): Promise<ValidationResult>;

  /**
   * Subscribe to pattern execution events
   */
  subscribe(callback: PatternEventCallback): UnsubscribeFn;
}

/**
 * Pattern registry for discovery and metadata
 */
interface IPatternRegistry {
  /**
   * Register a new pattern in the system
   */
  register(pattern: PatternSpec): void;

  /**
   * Find patterns matching operation and context
   */
  findMatching(operationKind: string, context: PatternContext): PatternInfo[];

  /**
   * Get full pattern specification by ID
   */
  getSpec(patternId: string): PatternSpec | null;

  /**
   * List all registered patterns
   */
  listAll(): PatternInfo[];
}

/**
 * Template engine for pattern materialization
 */
interface IPatternTemplateEngine {
  /**
   * Expand a pattern template with given variable context
   */
  expand(
    template: PatternTemplate,
    context: VariableContext
  ): MaterializedPattern;

  /**
   * Validate template syntax without rendering
   */
  validateTemplate(template: PatternTemplate): TemplateValidationResult;
}

/**
 * Event emitter for pattern lifecycle events
 */
interface IPatternEventEmitter {
  /**
   * Emit a pattern lifecycle event
   */
  emit(event: PatternEvent): void;

  /**
   * Register event handler for specific event types
   */
  on(eventType: string, handler: PatternEventHandler): void;

  /**
   * Remove event handler
   */
  off(eventType: string, handler: PatternEventHandler): void;
}

/**
 * State store adapter for pattern run persistence
 */
interface IPatternStateStore {
  /**
   * Save a pattern run record
   */
  saveRun(record: PatternRunRecord): Promise<void>;

  /**
   * Get pattern run by ID
   */
  getRun(patternRunId: string): Promise<PatternRunRecord | null>;

  /**
   * Query pattern runs by job or pattern ID
   */
  queryRuns(filter: PatternRunFilter): Promise<PatternRunRecord[]>;

  /**
   * Get pattern run statistics for a job
   */
  getJobStatistics(jobId: string): Promise<PatternStatistics>;
}
```

### Key Data Types

```typescript
type PatternExecutionRequest = {
  job_id: string;
  step_id: string;
  operation_kind: string;
  pattern_id?: string;  // Optional explicit pattern
  context: PatternContext;
  inputs: Record<string, unknown>;
  options: {
    timeout_seconds?: number;
    max_retries?: number;
    dry_run?: boolean;
  };
};

type PatternContext = {
  tool?: string;
  language?: string;
  file_type?: string;
  project_type?: string;
  environment?: string;
};

type PatternFilter = {
  operation_kind?: string;
  context?: Partial<PatternContext>;
  tags?: string[];
};

type PatternEventCallback = (event: PatternEvent) => void;
type UnsubscribeFn = () => void;
type PatternEventHandler = (event: PatternEvent) => void;

type PatternRunFilter = {
  job_id?: string;
  pattern_id?: string;
  status?: string;
  started_after?: string;
  started_before?: string;
};

type PatternStatistics = {
  total_runs: number;
  by_status: Record<string, number>;
  by_pattern: Record<string, number>;
  total_duration_seconds: number;
  average_duration_seconds: number;
};
```

---

## 3. Event Model & Data Contracts

### Event Schema (Finalized)

```typescript
type PatternEvent = {
  // Core identifiers
  event_id: string;           // EVT-<ULID>
  timestamp: string;          // ISO 8601 with milliseconds
  event_type: PatternEventType;

  // Context
  job_id: string;
  step_id: string;
  pattern_run_id: string;     // PRUN-<ULID>
  pattern_id: string;         // PAT-<ULID>

  // Status
  status: EventStatus;

  // Phase-specific data
  details: EventDetails;

  // Optional metadata
  metadata?: {
    user_id?: string;
    session_id?: string;
    correlation_id?: string;
  };
};

type PatternEventType =
  // Phase 1: Selection
  | "pattern.selection.started"
  | "pattern.selection.resolved"
  | "pattern.selection.failed"

  // Phase 2: Expansion
  | "pattern.template.expansion_started"
  | "pattern.template.expanded"
  | "pattern.template.expansion_failed"

  // Phase 3: Validation
  | "pattern.validation.started"
  | "pattern.validation.completed"
  | "pattern.validation.failed"

  // Phase 4: Execution
  | "pattern.execution.started"
  | "pattern.execution.progress"
  | "pattern.execution.completed"
  | "pattern.execution.failed"
  | "pattern.execution.timeout"

  // Phase 5: Persistence
  | "pattern.result.persisted";

type EventStatus =
  | "pending"
  | "in_progress"
  | "completed"
  | "failed"
  | "timeout"
  | "skipped";

type EventDetails =
  | SelectionDetails
  | ExpansionDetails
  | ValidationDetails
  | ExecutionDetails
  | PersistenceDetails;

type SelectionDetails = {
  operation_kind: string;
  context: PatternContext;
  selection_method?: "explicit" | "context_match" | "profile_preference";
  candidates_evaluated?: number;
  match_score?: number;
  error_message?: string;
};

type ExpansionDetails = {
  template_version: string;
  variables_resolved: number;
  commands_generated: number;
  config_files_generated: number;
  error_message?: string;
};

type ValidationDetails = {
  checks_run: number;
  checks_passed: number;
  checks_failed: number;
  can_proceed: boolean;
  failed_checks?: Array<{
    check_name: string;
    severity: "error" | "warning";
    message: string;
  }>;
};

type ExecutionDetails = {
  commands: string[];
  progress_percent?: number;    // For progress events
  duration_seconds?: number;    // For completed events
  exit_code?: number;
  finding_count?: number;
  lines_changed?: number;
  tests_passed?: number;
  error_message?: string;
  artifacts?: Array<{
    path: string;
    type: string;
    size_bytes: number;
  }>;
};

type PersistenceDetails = {
  store_type: "database" | "jsonl" | "both";
  record_size_bytes: number;
  artifacts_persisted: number;
};
```

### Event-to-Entity Relationship

```
┌────────────────────────────────────────────────────────┐
│  ENTITY RELATIONSHIP DIAGRAM                           │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌─────────┐                                          │
│  │   Job   │                                          │
│  │ (ULID)  │                                          │
│  └────┬────┘                                          │
│       │                                                │
│       │ 1:N                                            │
│       v                                                │
│  ┌──────────┐                                         │
│  │ JobStep  │                                         │
│  │  (ULID)  │                                         │
│  └────┬─────┘                                         │
│       │                                                │
│       │ 1:N                                            │
│       v                                                │
│  ┌──────────────┐         ┌──────────────┐           │
│  │ PatternRun   │────────>│   Pattern    │           │
│  │   (PRUN-*)   │   N:1   │   (PAT-*)    │           │
│  └──────┬───────┘         └──────────────┘           │
│         │                                              │
│         │ 1:N                                          │
│         v                                              │
│  ┌──────────────┐                                     │
│  │ PatternEvent │                                     │
│  │   (EVT-*)    │                                     │
│  └──────────────┘                                     │
│                                                        │
│  ┌──────────────┐                                     │
│  │  Artifact    │<────── PatternRun (1:N)            │
│  │  (file path) │                                     │
│  └──────────────┘                                     │
│                                                        │
└────────────────────────────────────────────────────────┘

Relationships:
- 1 Job has N JobSteps
- 1 JobStep can trigger N PatternRuns
- 1 Pattern can be used in N PatternRuns
- 1 PatternRun generates N PatternEvents (lifecycle events)
- 1 PatternRun produces N Artifacts (reports, logs, etc.)
```

### Database Schema (SQLite)

```sql
-- Pattern run records
CREATE TABLE pattern_runs (
  pattern_run_id TEXT PRIMARY KEY,       -- PRUN-<ULID>
  pattern_id TEXT NOT NULL,              -- PAT-<ULID>
  job_id TEXT NOT NULL,
  step_id TEXT NOT NULL,
  status TEXT NOT NULL,                  -- success, failure, timeout, skipped

  -- Execution data
  started_at TEXT NOT NULL,              -- ISO 8601
  finished_at TEXT,
  duration_seconds REAL,
  exit_code INTEGER,

  -- Results summary
  finding_count INTEGER,
  lines_changed INTEGER,
  tests_passed INTEGER,

  -- Serialized JSON blobs
  resolved_inputs TEXT,                  -- JSON
  commands_run TEXT,                     -- JSON array
  artifacts TEXT,                        -- JSON array

  -- Links
  FOREIGN KEY (job_id) REFERENCES jobs(job_id)
);

CREATE INDEX idx_pattern_runs_job ON pattern_runs(job_id);
CREATE INDEX idx_pattern_runs_pattern ON pattern_runs(pattern_id);
CREATE INDEX idx_pattern_runs_status ON pattern_runs(status);
CREATE INDEX idx_pattern_runs_started ON pattern_runs(started_at);

-- Pattern events
CREATE TABLE pattern_events (
  event_id TEXT PRIMARY KEY,             -- EVT-<ULID>
  timestamp TEXT NOT NULL,               -- ISO 8601
  event_type TEXT NOT NULL,
  pattern_run_id TEXT NOT NULL,
  job_id TEXT NOT NULL,
  step_id TEXT NOT NULL,
  pattern_id TEXT NOT NULL,
  status TEXT NOT NULL,

  -- Event data
  details TEXT NOT NULL,                 -- JSON

  FOREIGN KEY (pattern_run_id) REFERENCES pattern_runs(pattern_run_id)
);

CREATE INDEX idx_pattern_events_run ON pattern_events(pattern_run_id);
CREATE INDEX idx_pattern_events_job ON pattern_events(job_id);
CREATE INDEX idx_pattern_events_type ON pattern_events(event_type);
CREATE INDEX idx_pattern_events_timestamp ON pattern_events(timestamp);
```

---

## 4. Pattern Activity Panel UX Specification

### Overview

The Pattern Activity Panel is a **live-updating component** embedded in the Job Detail view. It provides real-time visibility into pattern execution with three main areas:

1. **Summary Header** - Aggregate statistics
2. **Timeline View** - Chronological event stream
3. **Detail Drawer** - Expandable detailed view for selected pattern run

### Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│ Pattern Activity Panel                          [Filters] [⚙️]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ SUMMARY HEADER                                            │ │
│  │                                                           │ │
│  │  Pattern Runs: 3 total  |  ✅ 2 success  |  ❌ 1 failed  │ │
│  │  Total Duration: 1m 23s  |  Avg: 27.7s                   │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ PATTERN SUMMARY TABLE                                     │ │
│  ├──────────┬───────────┬──────┬────────────┬──────────────┤ │
│  │ Pattern  │ Operation │ Runs │ Last Result│ Last Duration│ │
│  ├──────────┼───────────┼──────┼────────────┼──────────────┤ │
│  │ PAT-SE..│ semgrep   │  1   │ ✅ 12 finds │    18.7s     │ │
│  │ PAT-PY..│ pytest    │  2   │ ✅ 45 pass  │    28.2s     │ │
│  │ PAT-AI..│ aider     │  0   │     –       │      –       │ │
│  └──────────┴───────────┴──────┴────────────┴──────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ TIMELINE VIEW                                 [Live 🔴]   │ │
│  │                                                           │ │
│  │  07:15:12  🔍 Pattern selection started                  │ │
│  │            └─ semgrep_scan (PAT-SEMGRP-001)              │ │
│  │                                                           │ │
│  │  07:15:12  ✅ Pattern selected                            │ │
│  │            └─ Selected via context match (score: 0.95)   │ │
│  │                                                           │ │
│  │  07:15:13  📝 Template expansion complete                │ │
│  │            └─ 1 command, 2 config files generated        │ │
│  │                                                           │ │
│  │  07:15:13  ✓ Validation passed                           │ │
│  │            └─ All 5 checks passed                        │ │
│  │                                                           │ │
│  │  07:15:13  ▶️ Execution started                           │ │
│  │  │         └─ semgrep --config auto src/ tests/          │ │
│  │  ├─ 50%   ⏱️ Progress update (9.3s elapsed)              │ │
│  │  │                                                        │ │
│  │  07:15:30  ✅ Execution completed    [View Details →]    │ │
│  │            ├─ Exit code: 0                               │ │
│  │            ├─ Findings: 12                               │ │
│  │            ├─ Duration: 18.7s                            │ │
│  │            └─ Artifacts: 1 report                        │ │
│  │                                                           │ │
│  │  07:15:31  💾 Results persisted                          │ │
│  │            └─ PRUN-01JH9FDZKAG2J47A4WSK53JWZ1            │ │
│  │                                                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Detail Drawer (Expandable)

When user clicks **[View Details →]** on an execution event:

```
┌─────────────────────────────────────────────────────────────────┐
│ Pattern Run Detail                                      [Close]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────┐                   │
│  │ METADATA                                │                   │
│  │                                         │                   │
│  │ Pattern Run ID: PRUN-01JH9FDZ...        │                   │
│  │ Pattern: PAT-SEMGRP-001 (semgrep_scan)  │                   │
│  │ Job: JOB-01JH9F8P2ZJ1A8E5R6C792Q2EQ     │                   │
│  │ Step: STEP-003                          │                   │
│  │ Status: ✅ Success                       │                   │
│  │ Started: 2025-11-26 07:15:13.123 UTC    │                   │
│  │ Finished: 2025-11-26 07:15:30.891 UTC   │                   │
│  │ Duration: 18.768s                       │                   │
│  └─────────────────────────────────────────┘                   │
│                                                                 │
│  ┌─────────────────────────────────────────┐                   │
│  │ INPUTS (Resolved)              [Raw ▼]  │                   │
│  │                                         │                   │
│  │ target_paths:                           │                   │
│  │   - src/                                │                   │
│  │   - tests/                              │                   │
│  │ severity: medium+                       │                   │
│  │ config_profile: default                 │                   │
│  └─────────────────────────────────────────┘                   │
│                                                                 │
│  ┌─────────────────────────────────────────┐                   │
│  │ OUTPUTS                                 │                   │
│  │                                         │                   │
│  │ Exit Code: 0                            │                   │
│  │ Findings: 12                            │                   │
│  │                                         │                   │
│  │ Artifacts:                              │                   │
│  │  📄 semgrep_report.json (4.2 KB)        │                   │
│  │     [Download] [View]                   │                   │
│  └─────────────────────────────────────────┘                   │
│                                                                 │
│  ┌─────────────────────────────────────────┐                   │
│  │ LOGS                           [Expand] │                   │
│  │                                         │                   │
│  │ STDOUT:                                 │                   │
│  │ ┌─────────────────────────────────────┐ │                   │
│  │ │ Running 15 rules...                 │ │                   │
│  │ │ Scanning 234 files...               │ │                   │
│  │ │ Found 12 matches                    │ │                   │
│  │ │ Report written to: ...              │ │                   │
│  │ └─────────────────────────────────────┘ │                   │
│  │                                         │                   │
│  │ STDERR: (empty)                         │                   │
│  └─────────────────────────────────────────┘                   │
│                                                                 │
│  ┌─────────────────────────────────────────┐                   │
│  │ COMMAND EXECUTED                        │                   │
│  │                                         │                   │
│  │ semgrep --config auto \                 │                   │
│  │   --output state/reports/semgrep/... \  │                   │
│  │   --json src/ tests/                    │                   │
│  │                                         │                   │
│  │ [Copy Command]                          │                   │
│  └─────────────────────────────────────────┘                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Component Data Consumption

#### Summary Header Component
**Consumes**:
```typescript
type SummaryHeaderData = {
  total_runs: number;
  success_count: number;
  failed_count: number;
  total_duration_seconds: number;
  average_duration_seconds: number;
};
```

**Data Source**: Aggregated from `pattern_runs` table filtered by `job_id`

**Update Trigger**: On `pattern.result.persisted` event

---

#### Pattern Summary Table Component
**Consumes**:
```typescript
type PatternSummaryRow = {
  pattern_id: string;
  pattern_name: string;        // From pattern metadata
  operation_kind: string;
  run_count: number;
  last_result: {
    status: "success" | "failure" | "timeout" | "skipped";
    primary_metric: string;    // e.g., "12 findings", "45 passed"
    timestamp: string;
  } | null;
  last_duration_seconds: number | null;
};

type PatternSummaryTableData = PatternSummaryRow[];
```

**Data Source**: Aggregated query joining `pattern_runs` with pattern registry metadata

**Update Trigger**: On `pattern.result.persisted` event

---

#### Timeline View Component
**Consumes**:
```typescript
type TimelineEvent = {
  event_id: string;
  timestamp: string;
  event_type: PatternEventType;
  status: EventStatus;
  icon: string;              // Resolved from event_type
  color: string;             // Resolved from status
  primary_text: string;      // Human-readable event description
  secondary_text?: string;   // Additional context
  is_expandable: boolean;    // True for execution.completed
  pattern_run_id?: string;   // For linking to detail drawer
};

type TimelineViewData = TimelineEvent[];
```

**Data Source**: `pattern_events` table ordered by `timestamp DESC`

**Update Trigger**: Real-time via WebSocket or polling on new `PatternEvent` emissions

**Icon Mapping**:
```typescript
const EVENT_ICONS = {
  "pattern.selection.started": "🔍",
  "pattern.selection.resolved": "✅",
  "pattern.selection.failed": "❌",
  "pattern.template.expanded": "📝",
  "pattern.validation.completed": "✓",
  "pattern.validation.failed": "⚠️",
  "pattern.execution.started": "▶️",
  "pattern.execution.progress": "⏱️",
  "pattern.execution.completed": "✅",
  "pattern.execution.failed": "❌",
  "pattern.execution.timeout": "⏱️",
  "pattern.result.persisted": "💾"
};
```

**Status Colors**:
```typescript
const STATUS_COLORS = {
  "pending": "#6c757d",      // Gray
  "in_progress": "#0d6efd",  // Blue
  "completed": "#198754",    // Green
  "failed": "#dc3545",       // Red
  "timeout": "#fd7e14",      // Orange
  "skipped": "#6c757d"       // Gray
};
```

---

#### Detail Drawer Component
**Consumes**:
```typescript
type PatternRunDetail = {
  pattern_run_id: string;
  pattern_id: string;
  pattern_name: string;
  operation_kind: string;
  job_id: string;
  step_id: string;
  status: string;

  timing: {
    started_at: string;
    finished_at: string | null;
    duration_seconds: number | null;
  };

  inputs: {
    resolved: Record<string, unknown>;
    raw_json: string;
  };

  outputs: {
    exit_code: number | null;
    finding_count?: number;
    lines_changed?: number;
    tests_passed?: number;
    stdout: string;
    stderr: string;
  };

  artifacts: Array<{
    path: string;
    type: string;
    size_bytes: number;
    download_url: string;
    view_url?: string;
  }>;

  command: string;
};
```

**Data Source**:
- Primary: `pattern_runs` table by `pattern_run_id`
- Enriched: Pattern registry metadata, file system for artifact URLs

**Update Trigger**: On drawer open (user click), no auto-refresh

---

### State Update Mechanics (Live Updates)

#### WebSocket Event Stream (Preferred)

```typescript
// Client-side WebSocket connection
const ws = new WebSocket(`ws://localhost:8080/jobs/${jobId}/pattern-events`);

ws.onmessage = (message) => {
  const event: PatternEvent = JSON.parse(message.data);

  // Dispatch to React state management (e.g., Redux)
  dispatch({
    type: 'PATTERN_EVENT_RECEIVED',
    payload: event
  });
};

// React component with live updates
function TimelineView({ jobId }: { jobId: string }) {
  const events = useSelector(selectPatternEventsByJob(jobId));

  // Events are automatically added to state via WebSocket
  return (
    <div className="timeline">
      {events.map(event => (
        <TimelineEventRow key={event.event_id} event={event} />
      ))}
    </div>
  );
}
```

#### Polling Fallback

```typescript
// Poll for new events every 2 seconds
function usePatternEvents(jobId: string) {
  const [events, setEvents] = useState<PatternEvent[]>([]);
  const [lastEventId, setLastEventId] = useState<string | null>(null);

  useEffect(() => {
    const interval = setInterval(async () => {
      const response = await fetch(
        `/api/jobs/${jobId}/pattern-events?after=${lastEventId}`
      );
      const newEvents = await response.json();

      if (newEvents.length > 0) {
        setEvents(prev => [...prev, ...newEvents]);
        setLastEventId(newEvents[newEvents.length - 1].event_id);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [jobId, lastEventId]);

  return events;
}
```

---

## 5. Implementation Pseudocode

### 5.1 Event Emission from Engine

```python
# core/engine/pattern_executor.py

from typing import Protocol
import ulid
from datetime import datetime

class IPatternEventEmitter(Protocol):
    def emit(self, event: dict) -> None: ...

class PatternExecutor:
    def __init__(self, event_emitter: IPatternEventEmitter, state_store):
        self.event_emitter = event_emitter
        self.state_store = state_store

    def execute_pattern(self, request: dict) -> dict:
        """
        Full lifecycle execution with event emissions
        """
        # Generate IDs
        pattern_run_id = f"PRUN-{ulid.new()}"

        # PHASE 1: Selection
        self._emit_event(
            pattern_run_id=pattern_run_id,
            event_type="pattern.selection.started",
            status="in_progress",
            details={
                "operation_kind": request["operation_kind"],
                "context": request["context"]
            }
        )

        try:
            pattern_binding = self._select_pattern(request)

            self._emit_event(
                pattern_run_id=pattern_run_id,
                event_type="pattern.selection.resolved",
                status="completed",
                details={
                    "operation_kind": request["operation_kind"],
                    "selection_method": pattern_binding["selection_metadata"]["selection_method"],
                    "candidates_evaluated": pattern_binding["selection_metadata"]["candidates_evaluated"]
                }
            )
        except Exception as e:
            self._emit_event(
                pattern_run_id=pattern_run_id,
                event_type="pattern.selection.failed",
                status="failed",
                details={"error_message": str(e)}
            )
            raise

        # PHASE 2: Expansion
        self._emit_event(
            pattern_run_id=pattern_run_id,
            event_type="pattern.template.expansion_started",
            status="in_progress",
            details={}
        )

        materialized = self._expand_template(pattern_binding, request)

        self._emit_event(
            pattern_run_id=pattern_run_id,
            event_type="pattern.template.expanded",
            status="completed",
            details={
                "template_version": materialized["metadata"]["template_version"],
                "variables_resolved": len(materialized["resolved_inputs"]),
                "commands_generated": len(materialized["commands"])
            }
        )

        # PHASE 3: Validation
        self._emit_event(
            pattern_run_id=pattern_run_id,
            event_type="pattern.validation.started",
            status="in_progress",
            details={}
        )

        validation_result = self._validate(materialized)

        if validation_result["can_proceed"]:
            self._emit_event(
                pattern_run_id=pattern_run_id,
                event_type="pattern.validation.completed",
                status="completed",
                details={
                    "checks_run": len(validation_result["checks"]),
                    "checks_passed": sum(1 for c in validation_result["checks"] if c["status"] == "pass"),
                    "checks_failed": sum(1 for c in validation_result["checks"] if c["status"] == "fail"),
                    "can_proceed": True
                }
            )
        else:
            self._emit_event(
                pattern_run_id=pattern_run_id,
                event_type="pattern.validation.failed",
                status="failed",
                details={
                    "checks_run": len(validation_result["checks"]),
                    "checks_passed": sum(1 for c in validation_result["checks"] if c["status"] == "pass"),
                    "checks_failed": sum(1 for c in validation_result["checks"] if c["status"] == "fail"),
                    "can_proceed": False,
                    "failed_checks": [
                        {"check_name": c["check_name"], "severity": c["severity"], "message": c["message"]}
                        for c in validation_result["checks"] if c["status"] == "fail"
                    ]
                }
            )
            # Abort execution
            return {"status": "failed", "reason": "validation_failed"}

        # PHASE 4: Execution
        self._emit_event(
            pattern_run_id=pattern_run_id,
            event_type="pattern.execution.started",
            status="in_progress",
            details={
                "commands": materialized["commands"]
            }
        )

        # Execute with progress updates
        execution_result = self._execute_with_monitoring(
            materialized,
            pattern_run_id,
            on_progress=lambda pct: self._emit_event(
                pattern_run_id=pattern_run_id,
                event_type="pattern.execution.progress",
                status="in_progress",
                details={"progress_percent": pct}
            )
        )

        if execution_result["status"] == "success":
            self._emit_event(
                pattern_run_id=pattern_run_id,
                event_type="pattern.execution.completed",
                status="completed",
                details={
                    "commands": materialized["commands"],
                    "duration_seconds": execution_result["duration_seconds"],
                    "exit_code": execution_result["exit_code"],
                    "finding_count": execution_result.get("finding_count"),
                    "artifacts": execution_result["artifacts"]
                }
            )
        else:
            self._emit_event(
                pattern_run_id=pattern_run_id,
                event_type="pattern.execution.failed",
                status="failed",
                details={
                    "commands": materialized["commands"],
                    "error_message": execution_result["error_message"],
                    "exit_code": execution_result.get("exit_code")
                }
            )

        # PHASE 5: Persistence
        pattern_run_record = self._build_run_record(
            pattern_run_id,
            pattern_binding,
            materialized,
            validation_result,
            execution_result
        )

        self.state_store.save_run(pattern_run_record)

        self._emit_event(
            pattern_run_id=pattern_run_id,
            event_type="pattern.result.persisted",
            status="completed",
            details={
                "store_type": "database",
                "record_size_bytes": len(json.dumps(pattern_run_record)),
                "artifacts_persisted": len(execution_result["artifacts"])
            }
        )

        return execution_result

    def _emit_event(self, pattern_run_id: str, event_type: str, status: str, details: dict):
        """Helper to emit standardized events"""
        event = {
            "event_id": f"EVT-{ulid.new()}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "pattern_run_id": pattern_run_id,
            "pattern_id": self.current_pattern_id,  # Set during selection
            "job_id": self.current_job_id,
            "step_id": self.current_step_id,
            "status": status,
            "details": details
        }

        # Emit to event bus
        self.event_emitter.emit(event)
```

### 5.2 Event Persistence

```python
# core/state/pattern_state_store.py

import sqlite3
import json
from typing import Optional

class PatternStateStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_schema()

    def _init_schema(self):
        """Create tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pattern_runs (
                    pattern_run_id TEXT PRIMARY KEY,
                    pattern_id TEXT NOT NULL,
                    job_id TEXT NOT NULL,
                    step_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    duration_seconds REAL,
                    exit_code INTEGER,
                    finding_count INTEGER,
                    lines_changed INTEGER,
                    tests_passed INTEGER,
                    resolved_inputs TEXT,
                    commands_run TEXT,
                    artifacts TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS pattern_events (
                    event_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    pattern_run_id TEXT NOT NULL,
                    job_id TEXT NOT NULL,
                    step_id TEXT NOT NULL,
                    pattern_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details TEXT NOT NULL
                )
            """)

            # Indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pattern_runs_job ON pattern_runs(job_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pattern_events_run ON pattern_events(pattern_run_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pattern_events_job ON pattern_events(job_id)")

    def save_run(self, record: dict) -> None:
        """Persist a pattern run record"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO pattern_runs (
                    pattern_run_id, pattern_id, job_id, step_id, status,
                    started_at, finished_at, duration_seconds, exit_code,
                    finding_count, lines_changed, tests_passed,
                    resolved_inputs, commands_run, artifacts
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record["pattern_run_id"],
                record["pattern_id"],
                record["job_id"],
                record["step_id"],
                record["status"],
                record["execution"]["started_at"],
                record["execution"].get("finished_at"),
                record["execution"].get("duration_seconds"),
                record["execution"].get("exit_code"),
                record["outputs"].get("finding_count"),
                record["outputs"].get("lines_changed"),
                record["outputs"].get("tests_passed"),
                json.dumps(record["resolved_inputs"]),
                json.dumps(record["execution"]["commands_run"]),
                json.dumps(record["artifacts"])
            ))

    def save_event(self, event: dict) -> None:
        """Persist a pattern event"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO pattern_events (
                    event_id, timestamp, event_type, pattern_run_id,
                    job_id, step_id, pattern_id, status, details
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event["event_id"],
                event["timestamp"],
                event["event_type"],
                event["pattern_run_id"],
                event["job_id"],
                event["step_id"],
                event["pattern_id"],
                event["status"],
                json.dumps(event["details"])
            ))

    def get_events_for_job(self, job_id: str, after_event_id: Optional[str] = None) -> list[dict]:
        """Query events for a job, optionally after a specific event"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            if after_event_id:
                # Get timestamp of after_event_id first
                cursor = conn.execute(
                    "SELECT timestamp FROM pattern_events WHERE event_id = ?",
                    (after_event_id,)
                )
                row = cursor.fetchone()
                if not row:
                    return []

                after_timestamp = row["timestamp"]

                cursor = conn.execute("""
                    SELECT * FROM pattern_events
                    WHERE job_id = ? AND timestamp > ?
                    ORDER BY timestamp ASC
                """, (job_id, after_timestamp))
            else:
                cursor = conn.execute("""
                    SELECT * FROM pattern_events
                    WHERE job_id = ?
                    ORDER BY timestamp ASC
                """, (job_id,))

            events = []
            for row in cursor.fetchall():
                events.append({
                    "event_id": row["event_id"],
                    "timestamp": row["timestamp"],
                    "event_type": row["event_type"],
                    "pattern_run_id": row["pattern_run_id"],
                    "job_id": row["job_id"],
                    "step_id": row["step_id"],
                    "pattern_id": row["pattern_id"],
                    "status": row["status"],
                    "details": json.loads(row["details"])
                })

            return events

    def get_run_detail(self, pattern_run_id: str) -> Optional[dict]:
        """Get full detail for a pattern run"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM pattern_runs WHERE pattern_run_id = ?",
                (pattern_run_id,)
            )
            row = cursor.fetchone()

            if not row:
                return None

            return {
                "pattern_run_id": row["pattern_run_id"],
                "pattern_id": row["pattern_id"],
                "job_id": row["job_id"],
                "step_id": row["step_id"],
                "status": row["status"],
                "timing": {
                    "started_at": row["started_at"],
                    "finished_at": row["finished_at"],
                    "duration_seconds": row["duration_seconds"]
                },
                "inputs": {
                    "resolved": json.loads(row["resolved_inputs"]),
                    "raw_json": row["resolved_inputs"]
                },
                "outputs": {
                    "exit_code": row["exit_code"],
                    "finding_count": row["finding_count"],
                    "lines_changed": row["lines_changed"],
                    "tests_passed": row["tests_passed"]
                },
                "artifacts": json.loads(row["artifacts"]),
                "commands": json.loads(row["commands_run"])
            }
```

### 5.3 WebSocket Event Streaming

```python
# api/websocket_server.py

from fastapi import FastAPI, WebSocket
from typing import Dict, Set
import asyncio
import json

app = FastAPI()

# Track active WebSocket connections per job
active_connections: Dict[str, Set[WebSocket]] = {}

class PatternEventBroadcaster:
    """Broadcasts pattern events to connected WebSocket clients"""

    def __init__(self):
        self.event_queue = asyncio.Queue()

    async def broadcast_loop(self):
        """Background task that broadcasts events to all subscribers"""
        while True:
            event = await self.event_queue.get()
            job_id = event["job_id"]

            if job_id in active_connections:
                # Broadcast to all clients subscribed to this job
                disconnected = set()
                for websocket in active_connections[job_id]:
                    try:
                        await websocket.send_text(json.dumps(event))
                    except:
                        disconnected.add(websocket)

                # Clean up disconnected clients
                active_connections[job_id] -= disconnected

    def emit(self, event: dict):
        """Called by PatternExecutor to emit events"""
        self.event_queue.put_nowait(event)

# Global broadcaster
broadcaster = PatternEventBroadcaster()

@app.on_event("startup")
async def startup():
    asyncio.create_task(broadcaster.broadcast_loop())

@app.websocket("/jobs/{job_id}/pattern-events")
async def pattern_event_stream(websocket: WebSocket, job_id: str):
    await websocket.accept()

    # Register connection
    if job_id not in active_connections:
        active_connections[job_id] = set()
    active_connections[job_id].add(websocket)

    try:
        # Keep connection alive
        while True:
            # Wait for client messages (ping/pong)
            await websocket.receive_text()
    except:
        pass
    finally:
        # Unregister on disconnect
        active_connections[job_id].discard(websocket)
```

### 5.4 REST API for Events

```python
# api/pattern_api.py

from fastapi import FastAPI, Query
from typing import Optional

app = FastAPI()

@app.get("/api/jobs/{job_id}/pattern-events")
async def get_pattern_events(
    job_id: str,
    after: Optional[str] = Query(None, description="Return only events after this event_id")
):
    """Get pattern events for a job (with polling support)"""
    state_store = get_pattern_state_store()
    events = state_store.get_events_for_job(job_id, after_event_id=after)

    return {
        "job_id": job_id,
        "events": events,
        "count": len(events)
    }

@app.get("/api/jobs/{job_id}/pattern-summary")
async def get_pattern_summary(job_id: str):
    """Get aggregated pattern statistics for a job"""
    state_store = get_pattern_state_store()

    # Query all runs for this job
    runs = state_store.query_runs({"job_id": job_id})

    # Aggregate
    total_runs = len(runs)
    success_count = sum(1 for r in runs if r["status"] == "success")
    failed_count = sum(1 for r in runs if r["status"] == "failure")
    total_duration = sum(r["timing"]["duration_seconds"] or 0 for r in runs)
    avg_duration = total_duration / total_runs if total_runs > 0 else 0

    # Group by pattern
    by_pattern = {}
    for run in runs:
        pid = run["pattern_id"]
        if pid not in by_pattern:
            by_pattern[pid] = {
                "pattern_id": pid,
                "run_count": 0,
                "last_result": None,
                "last_duration": None
            }
        by_pattern[pid]["run_count"] += 1

        # Track latest
        if (by_pattern[pid]["last_result"] is None or
            run["timing"]["started_at"] > by_pattern[pid]["last_result"]["timestamp"]):
            by_pattern[pid]["last_result"] = {
                "status": run["status"],
                "primary_metric": _format_metric(run),
                "timestamp": run["timing"]["started_at"]
            }
            by_pattern[pid]["last_duration"] = run["timing"]["duration_seconds"]

    return {
        "summary": {
            "total_runs": total_runs,
            "success_count": success_count,
            "failed_count": failed_count,
            "total_duration_seconds": total_duration,
            "average_duration_seconds": avg_duration
        },
        "by_pattern": list(by_pattern.values())
    }

@app.get("/api/pattern-runs/{pattern_run_id}")
async def get_pattern_run_detail(pattern_run_id: str):
    """Get detailed information for a specific pattern run"""
    state_store = get_pattern_state_store()
    detail = state_store.get_run_detail(pattern_run_id)

    if not detail:
        return {"error": "Pattern run not found"}, 404

    # Enrich with pattern metadata
    pattern_info = get_pattern_registry().get_info(detail["pattern_id"])
    detail["pattern_name"] = pattern_info["name"]
    detail["operation_kind"] = pattern_info["operation_kind"]

    # Add artifact URLs
    for artifact in detail["artifacts"]:
        artifact["download_url"] = f"/api/artifacts/{artifact['path']}"
        if artifact["type"] == "report":
            artifact["view_url"] = f"/api/artifacts/{artifact['path']}/view"

    return detail

def _format_metric(run: dict) -> str:
    """Format primary metric for display"""
    if run["outputs"].get("finding_count"):
        return f"{run['outputs']['finding_count']} findings"
    elif run["outputs"].get("tests_passed"):
        return f"{run['outputs']['tests_passed']} passed"
    elif run["outputs"].get("lines_changed"):
        return f"{run['outputs']['lines_changed']} lines"
    else:
        return "completed"
```

### 5.5 React GUI Component

```typescript
// components/PatternActivityPanel.tsx

import React, { useEffect, useState } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { PatternEvent, PatternSummary, PatternRunDetail } from '../types';

interface PatternActivityPanelProps {
  jobId: string;
}

export const PatternActivityPanel: React.FC<PatternActivityPanelProps> = ({ jobId }) => {
  const [events, setEvents] = useState<PatternEvent[]>([]);
  const [summary, setSummary] = useState<PatternSummary | null>(null);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [detailDrawerOpen, setDetailDrawerOpen] = useState(false);

  // WebSocket connection for live events
  const ws = useWebSocket(`ws://localhost:8080/jobs/${jobId}/pattern-events`);

  // Handle incoming WebSocket events
  useEffect(() => {
    if (!ws) return;

    ws.onmessage = (message) => {
      const event: PatternEvent = JSON.parse(message.data);

      // Add event to timeline
      setEvents(prev => [...prev, event]);

      // Refresh summary if this is a persistence event
      if (event.event_type === 'pattern.result.persisted') {
        fetchSummary();
      }
    };
  }, [ws]);

  // Initial load: fetch existing events and summary
  useEffect(() => {
    fetchEvents();
    fetchSummary();
  }, [jobId]);

  const fetchEvents = async () => {
    const response = await fetch(`/api/jobs/${jobId}/pattern-events`);
    const data = await response.json();
    setEvents(data.events);
  };

  const fetchSummary = async () => {
    const response = await fetch(`/api/jobs/${jobId}/pattern-summary`);
    const data = await response.json();
    setSummary(data);
  };

  const openDetailDrawer = (patternRunId: string) => {
    setSelectedRunId(patternRunId);
    setDetailDrawerOpen(true);
  };

  return (
    <div className="pattern-activity-panel">
      {/* Summary Header */}
      {summary && (
        <div className="summary-header">
          <div className="stat">
            Pattern Runs: {summary.summary.total_runs} total
          </div>
          <div className="stat success">
            ✅ {summary.summary.success_count} success
          </div>
          <div className="stat failure">
            ❌ {summary.summary.failed_count} failed
          </div>
          <div className="stat">
            Total Duration: {formatDuration(summary.summary.total_duration_seconds)}
          </div>
          <div className="stat">
            Avg: {formatDuration(summary.summary.average_duration_seconds)}
          </div>
        </div>
      )}

      {/* Pattern Summary Table */}
      {summary && (
        <table className="pattern-summary-table">
          <thead>
            <tr>
              <th>Pattern</th>
              <th>Operation</th>
              <th>Runs</th>
              <th>Last Result</th>
              <th>Last Duration</th>
            </tr>
          </thead>
          <tbody>
            {summary.by_pattern.map(row => (
              <tr key={row.pattern_id}>
                <td>{row.pattern_id.substring(0, 10)}...</td>
                <td>{row.operation_kind || '—'}</td>
                <td>{row.run_count}</td>
                <td>
                  {row.last_result ? (
                    <span className={`status-${row.last_result.status}`}>
                      {row.last_result.status === 'success' ? '✅' : '❌'}{' '}
                      {row.last_result.primary_metric}
                    </span>
                  ) : '—'}
                </td>
                <td>
                  {row.last_duration ? formatDuration(row.last_duration) : '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {/* Timeline View */}
      <div className="timeline-view">
        <div className="timeline-header">
          <h3>Timeline</h3>
          <span className="live-indicator">🔴 Live</span>
        </div>

        <div className="timeline-events">
          {events.map(event => (
            <TimelineEventRow
              key={event.event_id}
              event={event}
              onViewDetails={openDetailDrawer}
            />
          ))}
        </div>
      </div>

      {/* Detail Drawer */}
      {detailDrawerOpen && selectedRunId && (
        <PatternDetailDrawer
          patternRunId={selectedRunId}
          onClose={() => setDetailDrawerOpen(false)}
        />
      )}
    </div>
  );
};

const TimelineEventRow: React.FC<{
  event: PatternEvent;
  onViewDetails: (patternRunId: string) => void;
}> = ({ event, onViewDetails }) => {
  const icon = EVENT_ICONS[event.event_type] || '•';
  const isExpandable = event.event_type === 'pattern.execution.completed';

  return (
    <div className={`timeline-event status-${event.status}`}>
      <span className="timestamp">{formatTime(event.timestamp)}</span>
      <span className="icon">{icon}</span>
      <span className="primary-text">{formatEventText(event)}</span>
      {event.details && (
        <div className="secondary-text">{formatEventDetails(event)}</div>
      )}
      {isExpandable && (
        <button onClick={() => onViewDetails(event.pattern_run_id)}>
          View Details →
        </button>
      )}
    </div>
  );
};

const PatternDetailDrawer: React.FC<{
  patternRunId: string;
  onClose: () => void;
}> = ({ patternRunId, onClose }) => {
  const [detail, setDetail] = useState<PatternRunDetail | null>(null);

  useEffect(() => {
    fetch(`/api/pattern-runs/${patternRunId}`)
      .then(res => res.json())
      .then(data => setDetail(data));
  }, [patternRunId]);

  if (!detail) return <div>Loading...</div>;

  return (
    <div className="detail-drawer">
      <div className="drawer-header">
        <h2>Pattern Run Detail</h2>
        <button onClick={onClose}>Close</button>
      </div>

      <div className="drawer-content">
        {/* Metadata */}
        <section className="metadata">
          <h3>Metadata</h3>
          <dl>
            <dt>Pattern Run ID:</dt>
            <dd>{detail.pattern_run_id}</dd>

            <dt>Pattern:</dt>
            <dd>{detail.pattern_id} ({detail.operation_kind})</dd>

            <dt>Status:</dt>
            <dd className={`status-${detail.status}`}>{detail.status}</dd>

            <dt>Duration:</dt>
            <dd>{formatDuration(detail.timing.duration_seconds)}</dd>
          </dl>
        </section>

        {/* Inputs */}
        <section className="inputs">
          <h3>Inputs (Resolved)</h3>
          <pre>{JSON.stringify(detail.inputs.resolved, null, 2)}</pre>
        </section>

        {/* Outputs */}
        <section className="outputs">
          <h3>Outputs</h3>
          <dl>
            <dt>Exit Code:</dt>
            <dd>{detail.outputs.exit_code}</dd>

            {detail.outputs.finding_count && (
              <>
                <dt>Findings:</dt>
                <dd>{detail.outputs.finding_count}</dd>
              </>
            )}
          </dl>

          <h4>Artifacts</h4>
          <ul className="artifacts">
            {detail.artifacts.map((artifact, i) => (
              <li key={i}>
                📄 {artifact.path} ({formatBytes(artifact.size_bytes)})
                <a href={artifact.download_url}>Download</a>
                {artifact.view_url && <a href={artifact.view_url}>View</a>}
              </li>
            ))}
          </ul>
        </section>

        {/* Logs */}
        <section className="logs">
          <h3>Logs</h3>
          <h4>STDOUT:</h4>
          <pre className="stdout">{detail.outputs.stdout}</pre>

          <h4>STDERR:</h4>
          <pre className="stderr">{detail.outputs.stderr || '(empty)'}</pre>
        </section>

        {/* Command */}
        <section className="command">
          <h3>Command Executed</h3>
          <pre>{detail.command}</pre>
          <button onClick={() => navigator.clipboard.writeText(detail.command)}>
            Copy Command
          </button>
        </section>
      </div>
    </div>
  );
};

// Utility functions
const EVENT_ICONS = {
  "pattern.selection.started": "🔍",
  "pattern.selection.resolved": "✅",
  "pattern.template.expanded": "📝",
  "pattern.validation.completed": "✓",
  "pattern.execution.started": "▶️",
  "pattern.execution.progress": "⏱️",
  "pattern.execution.completed": "✅",
  "pattern.result.persisted": "💾"
};

function formatTime(iso: string): string {
  const date = new Date(iso);
  return date.toLocaleTimeString('en-US', { hour12: false });
}

function formatDuration(seconds: number | null): string {
  if (seconds === null) return '—';
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}m ${secs.toFixed(0)}s`;
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatEventText(event: PatternEvent): string {
  switch (event.event_type) {
    case 'pattern.selection.started':
      return 'Pattern selection started';
    case 'pattern.selection.resolved':
      return 'Pattern selected';
    case 'pattern.template.expanded':
      return 'Template expansion complete';
    case 'pattern.validation.completed':
      return 'Validation passed';
    case 'pattern.execution.started':
      return 'Execution started';
    case 'pattern.execution.completed':
      return 'Execution completed';
    case 'pattern.result.persisted':
      return 'Results persisted';
    default:
      return event.event_type;
  }
}

function formatEventDetails(event: PatternEvent): string {
  const details = event.details as any;

  switch (event.event_type) {
    case 'pattern.selection.resolved':
      return `Selected via ${details.selection_method}`;
    case 'pattern.template.expanded':
      return `${details.commands_generated} command, ${details.config_files_generated} config files`;
    case 'pattern.validation.completed':
      return `All ${details.checks_passed} checks passed`;
    case 'pattern.execution.completed':
      return `Exit code: ${details.exit_code}, ${details.finding_count || 0} findings, ${formatDuration(details.duration_seconds)}`;
    default:
      return '';
  }
}
```

---

## 6. Assumptions & Design Decisions

### Assumptions

1. **Event Storage**: Events are persisted to both database and optionally JSONL for audit trail
2. **WebSocket Availability**: WebSocket support is preferred but REST polling fallback is provided
3. **Single Job Context**: The GUI/TUI shows pattern activity scoped to a single job at a time
4. **Pattern Registry**: A global pattern registry service exists that can be queried for pattern metadata
5. **Artifact Storage**: Artifacts are stored on filesystem and accessible via URLs
6. **Real-time Tolerance**: 1-2 second delay for event propagation to GUI is acceptable
7. **Scale**: System handles 10-100 pattern runs per job (not optimized for thousands)
8. **Browser Support**: Modern browsers with ES6+ and WebSocket support

### Design Decisions

#### 1. **5-Phase Lifecycle**
- **Rationale**: Clear separation of concerns makes debugging easier and allows independent optimization
- **Alternative Considered**: 3-phase model (select, execute, persist) - rejected as too coarse-grained

#### 2. **Event-First Architecture**
- **Rationale**: Events provide audit trail and enable real-time UI updates without polling
- **Alternative Considered**: Direct state queries - rejected due to poor UX for live updates

#### 3. **Separate Tables for Runs and Events**
- **Rationale**: Normalized schema reduces duplication; events can be pruned while runs remain
- **Alternative Considered**: Single table with event type - rejected due to query complexity

#### 4. **WebSocket + REST Hybrid**
- **Rationale**: WebSocket for real-time, REST for initial load and fallback
- **Alternative Considered**: REST-only with polling - rejected due to latency and server load

#### 5. **Detail Drawer vs Separate Page**
- **Rationale**: Drawer maintains context and allows quick switching between runs
- **Alternative Considered**: Full-page detail view - rejected due to poor workflow

#### 6. **ULID for IDs**
- **Rationale**: Sortable by creation time, globally unique, URL-safe
- **Alternative Considered**: UUID v4 - rejected due to lack of temporal ordering

#### 7. **Immutable Pattern Run Records**
- **Rationale**: Audit trail integrity; re-runs create new records
- **Alternative Considered**: Mutable records with update history - rejected due to complexity

#### 8. **JSON Blobs in SQLite**
- **Rationale**: Flexibility for tool-specific outputs without schema changes
- **Alternative Considered**: Fully normalized schema - rejected due to heterogeneous tool outputs

---

## Implementation Checklist

### Backend (Python)

- [ ] Implement `PatternExecutor` with 5-phase lifecycle
- [ ] Add event emission at each phase boundary
- [ ] Create `PatternStateStore` with SQLite schema
- [ ] Implement event persistence on emission
- [ ] Build WebSocket server for event streaming
- [ ] Create REST API endpoints for events and summary
- [ ] Add pattern registry service
- [ ] Implement artifact storage and URL generation

### Frontend (React/TypeScript)

- [ ] Create `PatternActivityPanel` component
- [ ] Implement `TimelineView` with live updates
- [ ] Build `PatternDetailDrawer` component
- [ ] Add WebSocket hook for event streaming
- [ ] Implement REST API client
- [ ] Add state management (Redux/Zustand)
- [ ] Style components with CSS/Tailwind
- [ ] Add error handling and loading states

### Testing

- [ ] Unit tests for each lifecycle phase
- [ ] Integration tests for event emission
- [ ] Database tests for state store
- [ ] WebSocket connection tests
- [ ] React component tests
- [ ] End-to-end tests for full flow

### Documentation

- [ ] API documentation (OpenAPI/Swagger)
- [ ] Event schema documentation
- [ ] Database schema documentation
- [ ] Component storybook
- [ ] User guide for Pattern Activity Panel

---

**End of Design Document**
