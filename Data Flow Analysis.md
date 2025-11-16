
 ▐▛███▜▌   Claude Code v2.0.42
▝▜█████▛▘  Sonnet 4.5 · Claude Pro
  ▘▘ ▝▝    C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonic…

● Complete Data Flow Analysis_Complete AI Development Pipeline
Data Flow Analysis_Complete AI Development Pipeline

  1. INPUT DATA SOURCES

● A. Specification Documents

  Source: docs/spec/*.md or *.txt files
  Format: Markdown/Text with [IDX-...] tags
  Content:
    - Requirements specifications
    - Architecture decisions
    - Feature descriptions with indexed references

  Flow: → PH-01 Index Scanner → spec_index_map.md

  B. Workstream Bundle Files

  Source: workstreams/*.json
  Format: JSON
  Schema:
  {
    "id": "ws-001",
    "openspec_change": "...",
    "gate": "gate-name",
    "files_scope": ["src/module.py"],
    "files_create": ["src/new_module.py"],
    "tasks": ["task1", "task2"],
    "acceptance_tests": ["test command"],
    "depends_on": ["ws-000"],
    "tool": "aider",
    "circuit_breaker": {
      "max_attempts": 3,
      "oscillation_threshold": 2
    }
  }

  Flow: → Bundle Parser (PH-04) → DAG Construction → Scheduler

  C. CCPM/OpenSpec Artifacts

  Source: .claude/prds/, .claude/epics/, .claude/context/
  Format: Markdown with frontmatter
  Content:
    - PRDs (Product Requirements Documents)
    - Epic decompositions
    - Task specifications
    - Project context

  Flow: → PRD Parser → Epic Planning → Task Decomposition →
  workstreams/*.json

  D. Tool Profiles

  Source: config/tool_profiles.json
  Format: JSON
  Schema:
  {
    "tool-id": {
      "type": "ai|static_check|test|utility",
      "command": "executable",
      "args": ["{template}", "vars"],
      "env": {"KEY": "value"},
      "timeout_sec": 60,
      "success_exit_codes": [0]
    }
  }

  Flow: → Tool Adapter (PH-03) → run_tool() execution

  ---
  2. DATA TRANSFORMATION PIPELINE

● Stage 1: Planning & Bundle Generation (PH-01, PH-04, PH-05.5)

  INPUT: PRD/Epic/OpenSpec Changes
    ↓
  [Planner.py - v2.0+]
    - Analyzes OpenSpec changes
    - Applies decomposition_rules.yaml
    - Generates import graphs
    ↓
  OUTPUT: workstreams/*.json (multiple bundles)
    - Each representing an atomic unit of work
    - With dependency relationships (DAG)
    - File scope constraints

  Stage 2: Validation & DAG Construction (PH-04)

  INPUT: workstreams/*.json files
    ↓
  [bundles.py]
    - Load all bundle files
    - Validate against schema/workstream.schema.json
    - Check for:
      • Duplicate IDs
      • Valid gates
      • Circular dependencies
      • File scope overlaps
    ↓
  OUTPUT: 
    - In-memory DAG structure
    - Validated bundle objects
    - Dependency ordering

  Stage 3: Run Initialization (PH-02, PH-05)

  INPUT: Validated bundles + User command
    ↓
  [orchestrator.py: run_pipeline()]
    ↓
  [db.py: create_run()]
    - Generates run_id (ULID/UUID)
    - Sets status = "pending"
    - Records metadata_json
    ↓
  SQLite: INSERT INTO runs
    {
      run_id: "RUN-2025-001",
      status: "pending",
      created_at: "2025-11-16T10:30:00Z",
      metadata_json: {...}
    }
    ↓
  For each bundle:
    [db.py: create_workstream()]
      ↓
    SQLite: INSERT INTO workstreams
      {
        ws_id: "ws-001",
        run_id: "RUN-2025-001",
        status: "pending",
        depends_on: '["ws-000"]',
        metadata_json: {...}
      }

  Stage 4: Workstream Scheduling (PH-07a)

  INPUT: Run + Workstreams in DB
    ↓
  [scheduler.py]
    WHILE not all_complete(run_id):
      - Query: SELECT * FROM workstreams WHERE status='pending'
      - Check dependencies: all depends_on in status='done'
      - Transition: pending → ready
      ↓
  [db.py: update_workstream_status()]
    - Validates transition (state machine)
    - Updates workstreams.status
    - Records event
    ↓
  SQLite Updates:
    UPDATE workstreams SET status='ready' WHERE ws_id='ws-001'
    INSERT INTO events (event_type='state_transition', ...)

  Stage 5: Worktree Creation (PH-04.5)

  INPUT: Workstream marked 'ready'
    ↓
  [worktree.py: create_worktree()]
    - Branch naming: ws/{change-id}/{ws-id}
    - Location: .worktrees/{ws-id}/
    - Base: main/develop
    ↓
  Git Operations:
    git worktree add .worktrees/ws-001 -b ws/change-123/ws-001
    ↓
  OUTPUT: Isolated working directory
    - Clean checkout
    - Dedicated branch
    - Scope enforcement ready

  Stage 6: EDIT Step (PH-03.5, PH-05)

  INPUT: Workstream + Bundle + Worktree
    ↓
  [prompts.py: build_edit_prompt()]
    - Loads template: templates/prompts/edit.txt.j2
    - Injects:
      • openspec_change details
      • files_scope list
      • tasks list
      • project context from .claude/context/
    ↓
  Rendered Prompt (Text)
    ↓
  [tools.py: run_tool("aider", context)]
    - Reads config/tool_profiles.json["aider"]
    - Renders command: aider --message "{prompt}" {files_scope}
    - Sets env: AIDER_NO_AUTO_COMMITS=1
    - Enforces timeout
    ↓
  [subprocess execution]
    - Working dir: .worktrees/ws-001/
    - Captures stdout/stderr
    - Records start time
    ↓
  Aider Output:
    - Modified files in files_scope
    - Logs/diagnostics
    ↓
  [db.py: record_step_attempt()]
    INSERT INTO step_attempts
      {
        ws_id: "ws-001",
        step_name: "edit",
        status: "success",
        result_json: {
          "files_modified": [...],
          "diff_hash": "abc123"
        }
      }
    ↓
  [worktree.py: verify_scope()]
    - git diff --name-only
    - Compare vs files_scope + files_create
    - FAIL if out-of-scope changes
    ↓
  State Transition: editing → static_check

  Stage 7: STATIC Check Step (PH-05)

  INPUT: Modified worktree
    ↓
  [orchestrator.py: run_static_checks()]
    For each static tool in bundle.tools:
      ↓
    [tools.py: run_tool("pytest"|"psscriptanalyzer", ...)]
      - Runs in worktree
      - Captures exit code + output
      ↓
    Tool Result:
      {
        exit_code: 0 or non-zero,
        stdout: "test output",
        stderr: "errors if any",
        success: true/false
      }
      ↓
    IF success:
      [db.py: record_step_attempt("static", "success")]
      State: static_check → runtime_check
    ELSE:
      [db.py: record_error()]
        INSERT INTO errors
          {
            ws_id: "ws-001",
            step_name: "static",
            error_code: "LINT_ERROR",
            signature: "pytest::test_foo::AssertionError",
            message: "...",
            count: 1
          }
      State: static_check → fixing

  Stage 8: FIX Loop (PH-06)

  INPUT: Failed static/runtime check
    ↓
  [circuit_breakers.py: check_limits()]
    - Query errors table for signature counts
    - Check max_attempts, oscillation threshold
    ↓
  IF breaker NOT tripped:
    [prompts.py: build_fix_prompt()]
      - Loads: templates/prompts/fix.txt.j2
      - Injects:
        • Error list from errors table
        • Previous diff hash
        • Original tasks
      ↓
    [tools.py: run_tool("aider", fix_context)]
      - Aider attempts fix
      ↓
    [orchestrator.py: re_run_check()]
      - Re-runs failed static/runtime test
      ↓
    IF success:
      State: fixing → runtime_check/done
    ELSE:
      [db.py: record_error()] (increments count)
      [circuit_breakers.py: detect_oscillation()]
        - Compares diff hashes
        - Increments oscillation counter
      ↓
      LOOP or FAIL
  ELSE (breaker tripped):
    State: fixing → failed
    [db.py: record_event("circuit_breaker_tripped")]

  Stage 9: RUNTIME Check Step (PH-05)

  INPUT: Code passing static checks
    ↓
  [orchestrator.py: run_runtime_checks()]
    - Runs acceptance_tests from bundle
    ↓
  [tools.py: run_tool(acceptance_test_command)]
    - Executes in worktree
    ↓
  IF success:
    State: runtime_check → done
    [db.py: update_workstream_status("done")]
  ELSE:
    → FIX Loop (same as static failures)

  Stage 10: Completion & Merge (PH-04.5)

  INPUT: Workstream status = 'done'
    ↓
  [worktree.py: finalize_worktree()]
    - Verify all changes committed
    - Push branch to remote (optional)
    ↓
  [integrations/github.py: create_pr()] (PH-08)
    - gh pr create
    - Links to OpenSpec/CCPM issue
    ↓
  [worktree.py: cleanup_worktree()]
    - Remove .worktrees/ws-001/
    OR
    - Keep for debugging if failed
    ↓
  [scheduler.py: update_dependent_workstreams()]
    - Find workstreams with depends_on=['ws-001']
    - Transition: pending → ready

  ---
  3. STATE PERSISTENCE (SQLite Schema Flow)

● ┌─────────────────────────────────────────────────────────────┐
  │                    SQLITE DATABASE                          │
  │                 (state/pipeline_state.db)                   │
  └─────────────────────────────────────────────────────────────┘

  ┌──────────────┐
  │ schema_meta  │  ← Stores schema version for migrations
  ├──────────────┤
  │ key: TEXT PK │
  │ value: TEXT  │
  └──────────────┘
       ↓
     Example: ('schema_version', '1')

  ┌────────────────────────────────────────────┐
  │ runs                                        │  ← Top-level execution
  tracking
  ├────────────────────────────────────────────┤
  │ run_id: TEXT PK (ULID)                     │
  │ status: TEXT (pending|running|completed|   │
  │               failed|partial|abandoned)    │
  │ created_at: TEXT (ISO 8601 UTC)            │
  │ updated_at: TEXT                           │
  │ metadata_json: TEXT (arbitrary data)       │
  └────────────────────────────────────────────┘
       ↓ 1:N
  ┌────────────────────────────────────────────┐
  │ workstreams                                 │  ← Individual work units
  ├────────────────────────────────────────────┤
  │ ws_id: TEXT PK                             │
  │ run_id: TEXT FK → runs                     │
  │ status: TEXT (pending|ready|editing|       │
  │   static_check|fixing|runtime_check|done|  │
  │   failed|blocked|abandoned)                │
  │ depends_on: TEXT (JSON array of ws_ids)    │
  │ created_at: TEXT                           │
  │ updated_at: TEXT                           │
  │ metadata_json: TEXT                        │
  └────────────────────────────────────────────┘
       ↓ 1:N
  ┌────────────────────────────────────────────┐
  │ step_attempts                               │  ← Execution history per
  step
  ├────────────────────────────────────────────┤
  │ id: INTEGER PK AUTOINCREMENT               │
  │ run_id: TEXT FK → runs                     │
  │ ws_id: TEXT FK → workstreams               │
  │ step_name: TEXT (edit|static|fix|runtime)  │
  │ status: TEXT (success|failure|in_progress) │
  │ started_at: TEXT                           │
  │ completed_at: TEXT                         │
  │ result_json: TEXT                          │
  └────────────────────────────────────────────┘

  ┌────────────────────────────────────────────┐
  │ errors                                      │  ← Error tracking &
  circuit breakers
  ├────────────────────────────────────────────┤
  │ id: INTEGER PK AUTOINCREMENT               │
  │ run_id: TEXT FK → runs                     │
  │ ws_id: TEXT FK → workstreams               │
  │ step_name: TEXT                            │
  │ error_code: TEXT (TIMEOUT|LINT_ERROR|...)  │
  │ signature: TEXT (normalized for dedup)     │
  │ message: TEXT                              │
  │ context_json: TEXT                         │
  │ count: INTEGER (incremented on repeat)     │
  │ first_seen_at: TEXT                        │
  │ last_seen_at: TEXT                         │
  └────────────────────────────────────────────┘

  ┌────────────────────────────────────────────┐
  │ events                                      │  ← Audit trail
  ├────────────────────────────────────────────┤
  │ id: INTEGER PK AUTOINCREMENT               │
  │ timestamp: TEXT                            │
  │ run_id: TEXT (nullable)                    │
  │ ws_id: TEXT (nullable)                     │
  │ event_type: TEXT (tool_started|           │
  │   state_transition|circuit_breaker_tripped)│
  │ payload_json: TEXT                         │
  └────────────────────────────────────────────┘

  Data Flow Through State Machine:

  Workstream State Transitions (enforced by db.py):

  pending ──────────────────────────────────────→ ready
     ↑                                              ↓
     │                                         (dependencies met)
     │                                              ↓
  blocked ←───────────────────────────────────── editing
     ↑                                              ↓
     │                                         (Aider complete)
     │                                              ↓
     │                                        static_check
     │                                         ↙         ↘
     │                                    (pass)      (fail)
     │                                      ↓            ↓
     │                                runtime_check   fixing
     │                                      ↓            ↓
     │                                   (pass)    (retry loop)
     │                                      ↓            ↓
     │                                    done      failed/abandoned
     │                                                   ↓
     └───────────────────────────────────────────(blocks dependents)

  Run State Transitions:

  pending → running → completed
              ↓
           partial  (some workstreams failed)
              ↓
           failed   (critical failures)

  ---
  4. ERROR & EVENT DATA FLOWS

● Error Flow:

  Tool Execution Failure
    ↓
  [tools.py: run_tool() captures]
    - exit_code
    - stderr content
    - timeout flag
    ↓
  [Error Signature Generation]
    signature = f"{tool_id}::{error_type}::{normalized_message}"
    Example: "pytest::AssertionError::test_auth_fails"
    ↓
  [db.py: record_error()]
    Query: SELECT * FROM errors WHERE signature=?
    ↓
    IF exists:
      UPDATE errors SET count=count+1, last_seen_at=NOW()
    ELSE:
      INSERT INTO errors (count=1, first_seen_at=NOW())
    ↓
  [circuit_breakers.py: check_breaker()]
    - Reads error.count
    - Checks vs max_attempts_per_signature
    - Checks oscillation (diff hash patterns)
    ↓
    IF breaker trips:
      [db.py: record_event("circuit_breaker_tripped")]
      [orchestrator.py: mark_workstream_failed()]

  Event Flow:

  Any Significant Action
    ↓
  [Component calls db.record_event()]
    ↓
  INSERT INTO events
    {
      timestamp: NOW(),
      run_id: "RUN-001",
      ws_id: "ws-001",
      event_type: "tool_started"|"state_transition"|"scope_violation",
      payload_json: {context-specific data}
    }
    ↓
  Event Types Tracked:
    - run_created
    - workstream_created
    - state_transition
    - tool_started
    - tool_finished
    - tool_timeout
    - tool_failed
    - circuit_breaker_tripped
    - scope_violation
    - dependency_blocked
    - crash_detected
    - resume_initiated

  Observability Flow (PH-09):

  events + errors tables
    ↓
  [Diagnostic Commands]
    pipeline show-run --id RUN-001
    pipeline show-errors --run RUN-001
    pipeline show-events --ws ws-001
    ↓
  Query & Format:
    - Aggregate by event_type
    - Group errors by signature
    - Timeline reconstruction
    ↓
  OUTPUT: Human/AI-readable reports (JSON/Markdown)

  ---
  5. OUTPUT ARTIFACTS & INTEGRATION POINTS

● A. Code Changes

  Successful Workstream
    ↓
  Git Repository Changes:
    - Branch: ws/{change-id}/{ws-id}
    - Modified files: as per files_scope
    - New files: as per files_create
    - Commits: Aider-generated (atomic per EDIT/FIX)
    ↓
  Push to Remote:
    git push origin ws/change-123/ws-001

  B. Pull Requests (PH-08)

  [integrations/github.py]
    ↓
  gh pr create \
    --title "Workstream ws-001: {description}" \
    --body "{OpenSpec link, tasks, acceptance tests}" \
    --label "epic:{epic-name}" \
    --base main
    ↓
  OUTPUT: PR URL
    ↓
  [db.py: update_workstream_metadata()]
    metadata_json['pr_url'] = "https://github.com/..."

  C. CCPM/OpenSpec Updates (PH-08)

  Workstream Status Changes
    ↓
  [integrations/openspec.py]
    - POST status to OpenSpec API
    - Update gate completion status
    ↓
  [integrations/github.py]
    - gh issue comment {ccpm_issue}
    - Posts progress update with:
      • Completed tasks
      • Test results
      • PR link

  D. Logs & Diagnostics

  Per-Run Logging:
    logs/{run_id}/
      ├─ run.jsonl          (structured events)
      ├─ ws-001.jsonl       (per-workstream)
      ├─ tool_outputs/
      │   ├─ aider_001.log
      │   └─ pytest_001.log
      └─ summary.json       (final report)

  Format (JSONL):
  {
    "timestamp": "2025-11-16T10:30:00Z",
    "level": "INFO",
    "run_id": "RUN-001",
    "ws_id": "ws-001",
    "step": "edit",
    "message": "Aider edit completed",
    "context": {...}
  }

  E. Summary Reports

  Run Completion
    ↓
  [orchestrator.py: generate_summary()]
    Queries:
      - runs table for overall status
      - workstreams for per-ws results
      - errors for failure analysis
      - events for timeline
    ↓
  OUTPUT: reports/{run_id}_summary.json
  {
    "run_id": "RUN-001",
    "status": "completed",
    "workstreams": {
      "total": 5,
      "done": 4,
      "failed": 1
    },
    "duration_sec": 1234,
    "errors_by_signature": {...},
    "timeline": [...]
  }
    ↓
  Markdown Report (optional):
    reports/{run_id}_summary.md

  ---
  COMPLETE DATA FLOW DIAGRAM

  ┌──────────────────────────────────────────────────────────────────────┐
  │                         INPUT LAYER                                   │
  ├──────────────────────────────────────────────────────────────────────┤
  │  [Spec Docs]  [PRDs/Epics]  [Workstream Bundles]  [Tool Profiles]   │
  │      ↓             ↓                ↓                    ↓            │
  │  [IDX Tags]   [CCPM Tasks]    [JSON Files]        [Config JSON]      │
  └──────────────┬───────────────────┬──────────────────┬────────────────┘
                 ↓                   ↓                  ↓
  ┌──────────────────────────────────────────────────────────────────────┐
  │                      PROCESSING LAYER                                 │
  ├──────────────────────────────────────────────────────────────────────┤
  │  PH-01: Index Scanner → spec_index_map.md                            │
  │  PH-04: Bundle Parser → Validated Bundles + DAG                      │
  │  PH-05: Orchestrator  → Run Initialization                           │
  │         └→ DB: create_run(), create_workstream()                     │
  │  PH-07a: Scheduler    → Dependency Resolution                        │
  │         └→ DB: update_workstream_status(pending→ready)               │
  │  PH-04.5: Worktree Mgr → Git Isolation                              │
  │         └→ .worktrees/{ws-id}/ branches                             │
  └──────────────┬───────────────────────────────────────────────────────┘
                 ↓
  ┌──────────────────────────────────────────────────────────────────────┐
  │                    EXECUTION LAYER (per workstream)                   │
  ├──────────────────────────────────────────────────────────────────────┤
  │  Step 1: EDIT                                                        │
  │    prompts.py → build_edit_prompt() → Jinja template                │
  │    tools.py   → run_tool("aider", prompt)                           │
  │    Aider      → Modifies files in worktree                          │
  │    DB         → record_step_attempt("edit", result)                 │
  │    State      → editing → static_check                              │
  │         ↓                                                            │
  │  Step 2: STATIC                                                      │
  │    tools.py   → run_tool("pytest"|"psscriptanalyzer")              │
  │    IF success:                                                       │
  │      State   → static_check → runtime_check                        │
  │    IF failure:                                                       │
  │      DB      → record_error(signature, count++)                    │
  │      State   → static_check → fixing                               │
  │         ↓                                                            │
  │  Step 3: FIX (loop)                                                  │
  │    circuit_breakers.py → check_limits()                            │
  │    IF NOT tripped:                                                   │
  │      prompts.py → build_fix_prompt(errors)                         │
  │      tools.py   → run_tool("aider", fix_prompt)                    │
  │      Re-run STATIC                                                   │
  │    ELSE:                                                             │
  │      State → fixing → failed                                        │
  │         ↓                                                            │
  │  Step 4: RUNTIME                                                     │
  │    tools.py → run_tool(acceptance_tests)                           │
  │    IF success:                                                       │
  │      State → runtime_check → done                                  │
  │    ELSE:                                                             │
  │      → FIX loop                                                      │
  └──────────────┬───────────────────────────────────────────────────────┘
                 ↓
  ┌──────────────────────────────────────────────────────────────────────┐
  │                      PERSISTENCE LAYER                                │
  ├──────────────────────────────────────────────────────────────────────┤
  │  SQLite DB: state/pipeline_state.db                                  │
  │  ┌─────────────┬──────────────┬───────────────┬──────────┐         │
  │  │   runs      │ workstreams  │ step_attempts │  errors  │         │
  │  └─────────────┴──────────────┴───────────────┴──────────┘         │
  │  │                       events                            │         │
  │  └─────────────────────────────────────────────────────────┘         │
  │                           ↕                                          │
  │  db.py API:                                                          │
  │    - create_run(), update_run_status()                              │
  │    - create_workstream(), update_workstream_status()                │
  │    - record_step_attempt(), record_error(), record_event()          │
  │    - validate_state_transition() ← state machine enforcement        │
  └──────────────┬───────────────────────────────────────────────────────┘
                 ↓
  ┌──────────────────────────────────────────────────────────────────────┐
  │                        OUTPUT LAYER                                   │
  ├──────────────────────────────────────────────────────────────────────┤
  │  Git Artifacts:                                                      │
  │    ├─ Branches: ws/{change}/{ws-id}                                 │
  │    ├─ Commits: Aider-generated changes                              │
  │    └─ Tags: (optional release markers)                              │
  │                                                                       │
  │  GitHub Integration:                                                 │
  │    ├─ Pull Requests (via gh pr create)                             │
  │    └─ Issue Comments (status updates)                              │
  │                                                                       │
  │  CCPM/OpenSpec:                                                      │
  │    ├─ Gate status updates                                           │
  │    └─ Task completion markers                                       │
  │                                                                       │
  │  Logs & Reports:                                                     │
  │    ├─ logs/{run_id}/*.jsonl                                        │
  │    ├─ reports/{run_id}_summary.{json|md}                           │
  │    └─ tool_outputs/*.log                                            │
  │                                                                       │
  │  Diagnostics (CLI):                                                  │
  │    ├─ pipeline show-run --id RUN-001                               │
  │    ├─ pipeline show-errors --run RUN-001                           │
  │    └─ pipeline show-events --ws ws-001                             │
  └──────────────────────────────────────────────────────────────────────┘

  ---
  KEY DATA FLOW CHARACTERISTICS

  1. Idempotency

  - DB operations are transactional
  - Schema init can run multiple times safely
  - State transitions are validated before commit

  2. Crash Recovery Flow

  Unexpected Termination
    ↓
  [recovery.py: detect_interrupted_runs()]
    Query: SELECT * FROM runs WHERE status='running'
    ↓
  For each interrupted run:
    - Check DB + worktree consistency
    - Offer: resume | abandon | rollback
    ↓
  Resume Flow:
    - Load last completed step per workstream
    - Re-initialize orchestrator state
    - Continue from checkpoint

  3. Parallel Execution Flow (PH-07b)

  [executor.py: WorkerPool]
    ↓
  Queue: [ws-001, ws-002, ws-003] (all ready, no deps)
    ↓
  Worker 1: run_workstream(ws-001)
  Worker 2: run_workstream(ws-002)
  Worker 3: run_workstream(ws-003)
    ↓
  Shared Resource: SQLite DB (with transaction locking)
    ↓
  Each worker:
    - Acquires lock for state updates
    - Writes to isolated worktree
    - Releases lock
    ↓
  Completion: Independent merge/PR creation

  4. Context Propagation

  Every data transformation carries:
    - run_id (top-level execution identifier)
    - ws_id (workstream identifier)
    - step_name (current execution stage)
    ↓
  Used for:
    - DB correlation (joins across tables)
    - Log aggregation
    - Error attribution
    - Recovery checkpointing

  ---
  SUMMARY: Data Lifecycle

  1. PLANNING
     Spec → PRD → Epic → Tasks → workstreams/*.json

  2. VALIDATION
     JSON → Schema Check → DAG → Scope Analysis

  3. INITIALIZATION
     Bundles → DB (runs + workstreams in "pending")

  4. SCHEDULING
     Dependency resolution → Status transitions → "ready"

  5. EXECUTION
     ready → EDIT → STATIC → FIX? → RUNTIME → done
     (All state in DB, code in worktrees)

  6. PERSISTENCE
     Every action → events table
     Every error → errors table (with signature + count)
     Every step → step_attempts table

  7. COMPLETION
     done → PR creation → CCPM update → cleanup

  8. OBSERVABILITY
     DB queries → CLI tools → Reports → Human/AI consumption

  This data flow architecture ensures:
  - Full traceability (spec → code)
  - Crash resilience (DB checkpointing)
  - Circuit breaker safety (error counting)
  - Parallel scalability (isolated worktrees)
  - AI debuggability (structured logs + events)

  Would you like me to dive deeper into any specific data flow path or
  create visualizations for particular subsystems?



