PH-02_Data Model, SQLite State Layer & State Machine (Codex Autonomous Phase Executor)

ROLE
You are Codex running with full access to a Windows development environment using PowerShell and Git.
Your job is to COMPLETELY IMPLEMENT phase PH-02 (Data Model, SQLite State Layer & State Machine) for the AI Development Pipeline project, end-to-end, without requiring further user input.

You will:
- Define and create the SQLite schema.
- Implement a robust db.py data-access layer.
- Implement a formal state machine for runs and workstreams.
- Provide initialization/management scripts.
- Add tests and docs so future AI agents can depend on this layer safely.

OPERATING CONTEXT
- OS: Windows 10/11
- Shell: PowerShell 7+ (pwsh)
- Version control: git
- Orchestrator language: Python 3.12+
- Previous phases:
  - PH-00: Baseline project skeleton, folders, basic docs, CI.
  - PH-01: Spec alignment, module stubs, spec index mapping.

PROJECT ROOT (IMPORTANT)
- Expected project root: C:/Users/richg/ALL_AI/AI_Dev_Pipeline

If that folder does NOT exist:
- Stop and write a clear, prominent note into docs/PHASE_PLAN.md under PH-02 that PH-00/PH-01 must be completed.
- Do NOT attempt DB creation elsewhere.

If it DOES exist:
- cd into that folder and proceed.

HIGH-LEVEL GOAL OF PH-02
Create a **solid, versionable state layer** with:
1) A clear SQLite schema (tables + indexes) for runs, workstreams, step attempts, errors, events.
2) A single db.py module that exposes well-defined functions for reading/writing state.
3) A formal state machine for workstreams (with allowed transitions enforced in code).
4) Simple CLI/PowerShell scripts to initialize and inspect the database.
5) Tests that guarantee correctness of schema and transitions.

You are NOT building the orchestrator loop yet; just the persistence + state logic it will rely on.

====================================
REQUIRED OUTPUTS OF THIS PHASE
====================================

By the end of PH-02, the repo MUST have at minimum:

1) SQLITE SCHEMA (DDL)
- A schema file (text-based) that defines tables and indexes, for example:
  - schema/schema.sql             OR
  - src/pipeline/schema.sql       (your choice, but documented)

Schema must define at least:

- Table: runs
  - run_id          TEXT PRIMARY KEY (e.g. ULID or UUID; for now you may use TEXT)
  - status          TEXT NOT NULL     -- e.g. pending, running, completed, failed, partial, abandoned
  - created_at      TEXT NOT NULL     -- ISO 8601 string (UTC)
  - updated_at      TEXT NOT NULL
  - metadata_json   TEXT NULL         -- arbitrary JSON

- Table: workstreams
  - ws_id           TEXT PRIMARY KEY
  - run_id          TEXT NOT NULL REFERENCES runs(run_id)
  - status          TEXT NOT NULL     -- e.g. pending, ready, editing, static_check, fixing, runtime_check, done, failed, blocked, abandoned
  - depends_on      TEXT NULL         -- serialized list of ws_ids (JSON)
  - created_at      TEXT NOT NULL
  - updated_at      TEXT NOT NULL
  - metadata_json   TEXT NULL

- Table: step_attempts
  - id              INTEGER PRIMARY KEY AUTOINCREMENT
  - run_id          TEXT NOT NULL REFERENCES runs(run_id)
  - ws_id           TEXT NOT NULL REFERENCES workstreams(ws_id)
  - step_name       TEXT NOT NULL     -- e.g. edit, static, fix, runtime
  - status          TEXT NOT NULL     -- success, failure, skipped, in_progress
  - started_at      TEXT NOT NULL
  - completed_at    TEXT NULL
  - result_json     TEXT NULL

- Table: errors
  - id              INTEGER PRIMARY KEY AUTOINCREMENT
  - run_id          TEXT NOT NULL REFERENCES runs(run_id)
  - ws_id           TEXT NOT NULL REFERENCES workstreams(ws_id)
  - step_name       TEXT NOT NULL
  - error_code      TEXT NOT NULL     -- short code indicating error type
  - signature       TEXT NOT NULL     -- normalized signature used by circuit breaker logic
  - message         TEXT NOT NULL
  - context_json    TEXT NULL
  - count           INTEGER NOT NULL DEFAULT 1
  - first_seen_at   TEXT NOT NULL
  - last_seen_at    TEXT NOT NULL

- Table: events
  - id              INTEGER PRIMARY KEY AUTOINCREMENT
  - timestamp       TEXT NOT NULL
  - run_id          TEXT NULL
  - ws_id           TEXT NULL
  - event_type      TEXT NOT NULL     -- e.g. "step_started", "step_completed", "error_recorded"
  - payload_json    TEXT NULL

- Table: schema_meta
  - key             TEXT PRIMARY KEY
  - value           TEXT NOT NULL
  - Example: ('schema_version', '1')

Include appropriate indexes:
- runs(status)
- workstreams(run_id, status)
- step_attempts(run_id, ws_id, step_name)
- errors(run_id, ws_id, signature)
- events(run_id, ws_id, event_type)

2) CONFIGURABLE DB LOCATION
- Default DB path:
  - <PROJECT_ROOT>/state/pipeline_state.db
- Allow override via environment variable:
  - PIPELINE_DB_PATH
- Document this behavior in docs/ARCHITECTURE.md under a new “State & Persistence” section.

3) db.py – STATE LAYER MODULE
Implement src/pipeline/db.py with:

- A way to get a connection (using sqlite3):
  - get_connection() that:
    - Resolves DB path (PIPELINE_DB_PATH or default).
    - Ensures parent directory exists.
    - Returns a sqlite3.Connection with:
      - row_factory set to sqlite3.Row for convenience.

- Schema initialization:
  - init_db() that:
    - Creates DB file if missing.
    - Checks if schema is already applied (via schema_meta).
    - If not, applies schema/schema.sql idempotently.
    - Sets schema_meta['schema_version'] = '1'.

- Core operations:
  - create_run(status="pending", metadata=None) → run_id
  - update_run_status(run_id, new_status)
  - get_run(run_id) → dict-like object

  - create_workstream(run_id, ws_id, status="pending", depends_on=None, metadata=None)
  - update_workstream_status(ws_id, new_status)
  - get_workstream(ws_id)
  - get_workstreams_for_run(run_id)

  - record_step_attempt(run_id, ws_id, step_name, status, result_json=None, started_at=None, completed_at=None)
  - record_error(run_id, ws_id, step_name, error_code, signature, message, context_json=None)
    - If an identical (run_id, ws_id, step_name, signature) exists, increment count & update last_seen_at.
    - Otherwise insert new row with count=1.
  - record_event(run_id, ws_id, event_type, payload_json=None)

Ensure each function:
- Opens a connection (or uses a shared context) safely.
- Uses transactions where appropriate.
- Commits changes or raises on failure.

4) FORMAL STATE MACHINE (WORKSTREAM FOCUS)
Implement a small state machine in db.py (or a separate state_machine.py imported by db.py) with:

- Defined workstream states:
  - "pending"
  - "ready"
  - "editing"
  - "static_check"
  - "fixing"
  - "runtime_check"
  - "done"
  - "failed"
  - "blocked"
  - "abandoned"

- A function:
  - validate_state_transition(entity_type, from_state, to_state) → None or raises ValueError
    - entity_type: "run" or "workstream"
    - For now, runs can use a simpler state set:
      - "pending" → "running" → "completed"
      - plus "failed", "partial", "abandoned"

- For workstreams, allowed transitions might be:
  - pending → ready
  - ready → editing
  - editing → static_check
  - static_check → fixing
  - fixing → static_check or fixing → runtime_check
  - runtime_check → done
  - Any state → failed / abandoned
  - pending/ready → blocked (if dependency fails)

- Enforce state transitions:
  - update_workstream_status(ws_id, new_status) must:
    - Look up current status.
    - Call validate_state_transition("workstream", current, new).
    - Only then update the DB.

5) STATE MACHINE DOCUMENTATION
- docs/state_machine.md
  - Describe:
    - Run states and meaning.
    - Workstream states and meaning.
    - Allowed transitions (possibly with a simple diagram or ASCII art).
  - Explicitly mention that:
    - db.py enforces state transitions using validate_state_transition.
    - Illegal transitions raise an exception and should be recorded as events.

6) DB MANAGEMENT SCRIPT(S)
- scripts/init_db.py
  - Python script runnable as:
    - python scripts/init_db.py
  - Behavior:
    - Imports db.init_db()
    - Initializes or verifies DB.
    - Prints:
      - DB path.
      - Schema version.
      - Whether a fresh schema was applied or it was already up-to-date.

- (Optional but nice) scripts/db_inspect.py
  - Simple script that can:
    - Print runs and workstreams summary:
      - number of runs
      - their statuses
      - counts of workstreams per status
  - This is helpful for humans and AI agents.

7) TESTS
- tests/pipeline/test_db_state.py:
  - Use a temporary SQLite DB (e.g., override PIPELINE_DB_PATH to a temp location in tests).
  - Tests should cover:
    - init_db() creates schema and schema_meta['schema_version'] == "1".
    - create_run() and get_run() work as expected.
    - create_workstream() and get_workstreams_for_run() work.
    - update_workstream_status() enforces valid transitions:
      - legal transitions succeed
      - illegal ones raise.
    - record_error() increments count for repeated signatures.
    - record_event() inserts rows correctly.

Update your CI config if necessary to ensure these tests are run.

8) DOCUMENTATION UPDATES
- docs/ARCHITECTURE.md:
  - Add a section “State & Persistence”:
    - Describe:
      - that state is stored in SQLite at state/pipeline_state.db by default.
      - the role of runs, workstreams, step_attempts, errors, events.
      - the existence of scripts/init_db.py and how to use it.

- docs/PHASE_PLAN.md:
  - Flesh out PH-02 section with:
    - One-paragraph summary of DB + state machine.
    - Bullet list of artifacts created (db.py, schema.sql, state_machine.md, tests, scripts).

9) GIT COMMIT
- Stage all new/modified files.
- Commit with message:
  - "PH-02: data model, SQLite state layer, and state machine"
- Do NOT push (remote configuration is out of scope for this phase).

====================================
CONSTRAINTS & PRINCIPLES
====================================

- Do NOT break or remove outputs from PH-00 and PH-01; only extend them.
- Keep db.py focused on persistence/state, not on orchestration logic.
- Use Python’s standard library sqlite3 (no heavy DB frameworks).
- Use ISO 8601 UTC timestamps (e.g., datetime.datetime.utcnow().isoformat() + "Z").
- Avoid hardcoding an absolute path inside db.py; use:
  - PIPELINE_DB_PATH env var if set, else state/pipeline_state.db relative to project root.
- Make schema initialization idempotent:
  - Running init_db() multiple times should be safe.

====================================
EXECUTION PLAN (WHAT YOU SHOULD DO)
====================================

You should:

1) PRECHECKS & NAVIGATION
   - Confirm C:/Users/richg/ALL_AI/AI_Dev_Pipeline exists.
   - cd C:/Users/richg/ALL_AI/AI_Dev_Pipeline
   - Confirm src/pipeline/ exists; if not, create it but also note in docs/PHASE_PLAN.md that PH-00/01 may be incomplete.

2) CREATE SCHEMA FILE
   - Create schema/ directory or choose a clear location (e.g., src/pipeline/schema.sql).
   - Write schema.sql with CREATE TABLE statements & indexes.
   - Ensure it can be executed multiple times without breaking (use IF NOT EXISTS where appropriate).

3) IMPLEMENT db.py
   - Fill src/pipeline/db.py with:
     - Connection helpers.
     - init_db().
     - CRUD/access functions for runs, workstreams, step_attempts, errors, events.
     - validate_state_transition() and update_* wrappers that enforce transitions.

4) CREATE STATE MACHINE DOC
   - Write docs/state_machine.md describing:
     - run states & transitions.
     - workstream states & transitions.
     - mention that db.py is the source of truth and enforces them.

5) MANAGEMENT SCRIPTS
   - Implement scripts/init_db.py.
   - (Optional) Implement scripts/db_inspect.py.

6) TESTS
   - Implement tests/pipeline/test_db_state.py.
   - Ensure tests:
     - Use a temp DB path (set PIPELINE_DB_PATH in test environment).
     - Call init_db(), create_run(), create_workstream(), state transitions, error/event recording.

7) RUN TESTS
   - From project root:
     - (Optional) Create/activate venv.
     - Run: pytest
   - Fix any failing tests before considering phase complete.

8) UPDATE DOCS
   - Update docs/ARCHITECTURE.md and docs/PHASE_PLAN.md as described.

9) GIT COMMIT
   - Stage and commit with the PH-02 message.

====================================
PHASE COMPLETION CHECKLIST
====================================

Before you consider PH-02 done, ensure all of the following are true:

[ ] schema/schema.sql (or equivalent) exists and defines runs, workstreams, step_attempts, errors, events, schema_meta, plus indexes
[ ] src/pipeline/db.py exists with:
    - get_connection()
    - init_db()
    - create_run(), update_run_status(), get_run()
    - create_workstream(), update_workstream_status(), get_workstreams_for_run()
    - record_step_attempt(), record_error(), record_event()
    - validate_state_transition() and enforced transitions
[ ] DB path configurable via PIPELINE_DB_PATH, defaulting to state/pipeline_state.db
[ ] docs/state_machine.md exists and accurately describes states & transitions
[ ] scripts/init_db.py exists and can initialize/verify the DB
[ ] tests/pipeline/test_db_state.py exists and passes
[ ] docs/ARCHITECTURE.md has a “State & Persistence” section referencing DB path and tables
[ ] docs/PHASE_PLAN.md has an updated PH-02 section with artifacts listed
[ ] A git commit with message like "PH-02: data model, SQLite state layer, and state machine" has been created

====================================
INTERACTION STYLE
====================================

- Do NOT ask the user questions unless you are completely blocked.
- Make reasonable assumptions and document them in docs/state_machine.md and docs/PHASE_PLAN.md.
- When you output your response, clearly separate:
  - PowerShell commands you would run.
  - Python / SQL / Markdown file contents you would create or modify.

END OF PROMPT
