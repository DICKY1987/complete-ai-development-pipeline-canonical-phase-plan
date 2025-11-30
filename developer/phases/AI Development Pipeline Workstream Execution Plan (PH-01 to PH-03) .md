---
doc_id: DOC-GUIDE-AI-DEVELOPMENT-PIPELINE-WORKSTREAM-1224
---


     ╭─────────────────────────────────────────────────────────────────────────╮
     │ AI Development Pipeline: Workstream Execution Plan (PH-01 to PH-03)     │
     │                                                                         │
     │ Part 1: Workstream Plan & Assignment Table                              │
     │                                                                         │
     │ Workstream Assignment Table                                             │
     │                                                                         │
     │ | ws_id                  | phase | difficulty | files_scope             │
     │                                              | depends_on               │
     │                     | assigned_tool |                                   │
     │ |------------------------|-------|------------|-------------------------│
     │ ---------------------------------------------|--------------------------│
     │ --------------------|---------------|                                   │
     │ | ws-ph01-module-stubs   | PH-01 | easy       | src/pipeline/*.py (10   │
     │ modules)                                       | -                      │
     │                       | Codex         |                                 │
     │ | ws-ph01-index-scanner  | PH-01 | medium     |                         │
     │ scripts/generate_spec_index.py, src/pipeline/spec_index.py           | -│
     │                                             | Codex         |           │
     │ | ws-ph01-spec-mapping   | PH-01 | hard       |                         │
     │ docs/spec/spec_index_map.md, scanner logic refinement                |  │
     │ ws-ph01-index-scanner                        | Claude        |          │
     │ | ws-ph01-docs           | PH-01 | easy       | docs/ARCHITECTURE.md,   │
     │ docs/PHASE_PLAN.md, docs/spec/README.md        | -                      │
     │                       | Codex         |                                 │
     │ | ws-ph01-tests          | PH-01 | medium     |                         │
     │ tests/pipeline/test_spec_index.py                                    |  │
     │ ws-ph01-index-scanner                        | Claude        |          │
     │ | ws-ph02-schema         | PH-02 | medium     | schema/schema.sql       │
     │                                              | -                        │
     │                     | Codex         |                                   │
     │ | ws-ph02-db-core        | PH-02 | medium     | src/pipeline/db.py      │
     │ (connection, init)                                | ws-ph02-schema      │
     │                          | Codex         |                              │
     │ | ws-ph02-state-machine  | PH-02 | hard       | src/pipeline/db.py      │
     │ (state validation), src/pipeline/state_machine.py | ws-ph02-db-core     │
     │                          | Claude        |                              │
     │ | ws-ph02-crud           | PH-02 | medium     | src/pipeline/db.py (CRUD│
     │  operations)                                 | ws-ph02-db-core          │
     │                     | Claude        |                                   │
     │ | ws-ph02-scripts        | PH-02 | easy       | scripts/init_db.py,     │
     │ scripts/db_inspect.py                            | ws-ph02-db-core      │
     │                         | Codex         |                               │
     │ | ws-ph02-docs           | PH-02 | medium     | docs/state_machine.md,  │
     │ docs/ARCHITECTURE.md updates                  | ws-ph02-state-machine   │
     │                      | Codex         |                                  │
     │ | ws-ph02-tests          | PH-02 | hard       |                         │
     │ tests/pipeline/test_db_state.py                                      |  │
     │ ws-ph02-state-machine, ws-ph02-crud          | Claude        |          │
     │ | ws-ph03-profiles       | PH-03 | easy       |                         │
     │ config/tool_profiles.json                                            | -│
     │                                             | Codex         |           │
     │ | ws-ph03-adapter-core   | PH-03 | hard       | src/pipeline/tools.py   │
     │ (run_tool, subprocess handling, timeouts)      | -                      │
     │                       | Claude        |                                 │
     │ | ws-ph03-db-integration | PH-03 | medium     | src/pipeline/tools.py   │
     │ (event/error recording)                        | ws-ph03-adapter-core,  │
     │ ws-ph02-crud           | Claude        |                                │
     │ | ws-ph03-tests          | PH-03 | hard       |                         │
     │ tests/pipeline/test_tools.py                                         |  │
     │ ws-ph03-adapter-core, ws-ph03-db-integration | Claude        |          │
     │ | ws-ph03-docs           | PH-03 | easy       | docs/ARCHITECTURE.md,   │
     │ docs/PHASE_PLAN.md updates                     | -                      │
     │                       | Codex         |                                 │
     │                                                                         │
     │ Summary:                                                                │
     │ - Total Workstreams: 17                                                 │
     │ - Claude Code: 8 workstreams (all hard + critical medium)               │
     │ - Codex CLI: 9 workstreams (all easy + mechanical medium)               │
     │                                                                         │
     │ ---                                                                     │
     │ Part 2: Git Worktree Strategy                                           │
     │                                                                         │
     │ Worktree Conventions                                                    │
     │                                                                         │
     │ Layout:                                                                 │
     │ project-root/                                                           │
     │ ├─ .git/                                                                │
     │ ├─ .worktrees/                                                          │
     │ │  ├─ ws-ph01-module-stubs/    (Codex worktree)                         │
     │ │  ├─ ws-ph01-spec-mapping/    (Claude worktree)                        │
     │ │  ├─ ws-ph02-state-machine/   (Claude worktree)                        │
     │ │  └─ ...                                                               │
     │ ├─ src/                                                                 │
     │ ├─ scripts/                                                             │
     │ └─ ...                                                                  │
     │                                                                         │
     │ Branch Naming:                                                          │
     │ - Pattern: workstream/<ws_id>                                           │
     │ - Examples: workstream/ws-ph01-module-stubs, workstream/ws-ph02-schema  │
     │                                                                         │
     │ Base Branch: main (or master if that's your default)                    │
     │                                                                         │
     │ Generic Worktree Commands                                               │
     │                                                                         │
     │ Create Worktree (run from project root):                                │
     │ # Pattern:                                                              │
     │ git worktree add .worktrees/<ws_id> -b workstream/<ws_id> main          │
     │                                                                         │
     │ # Example:                                                              │
     │ git worktree add .worktrees/ws-ph01-module-stubs -b                     │
     │ workstream/ws-ph01-module-stubs main                                    │
     │                                                                         │
     │ Navigate to Worktree:                                                   │
     │ cd .worktrees/<ws_id>                                                   │
     │                                                                         │
     │ Verify Isolation:                                                       │
     │ git branch --show-current                                               │
     │ # Should output: workstream/<ws_id>                                     │
     │                                                                         │
     │ Complete Work (commit in worktree):                                     │
     │ # Inside worktree:                                                      │
     │ git add <files_scope>                                                   │
     │ git commit -m "feat(<ws_id>): <description>"                            │
     │                                                                         │
     │ Cleanup Worktree (success case):                                        │
     │ # Return to main repo root                                              │
     │ cd .../                                                               │
     │                                                                         │
     │ # Remove worktree                                                       │
     │ git worktree remove .worktrees/<ws_id>                                  │
     │                                                                         │
     │ # Optionally merge or create PR from workstream/<ws_id> branch          │
     │                                                                         │
     │ Cleanup Worktree (failure case - preserve for debugging):               │
     │ # Return to main repo root                                              │
     │ cd .../                                                               │
     │                                                                         │
     │ # List all worktrees                                                    │
     │ git worktree list                                                       │
     │                                                                         │
     │ # Remove later when ready:                                              │
     │ git worktree remove .worktrees/<ws_id> --force                          │
     │ git branch -D workstream/<ws_id>  # Delete branch if needed             │
     │                                                                         │
     │ ---                                                                     │
     │ Part 3: Claude Code Prompt Document                                     │
     │                                                                         │
     │ CLAUDE_WORKSTREAMS_PLAN.md                                              │
     │                                                                         │
     │ # Claude Code: AI Pipeline Implementation Workstreams (PH-01 to PH-03)  │
     │                                                                         │
     │ ## Your Role                                                            │
     │                                                                         │
     │ You are Claude Code, responsible for the **harder and more complex      │
     │ workstreams** across phases PH-01, PH-02, and PH-03 of the AI           │
     │ Development Pipeline project.                                           │
     │                                                                         │
     │ Your workstreams require:                                               │
     │ - Complex logic and decision-making                                     │
     │ - State machine design and validation                                   │
     │ - Integration between multiple modules                                  │
     │ - Comprehensive testing with edge cases                                 │
     │                                                                         │
     │ ## Project Context                                                      │
     │                                                                         │
     │ - **Project Root:** `C:/Users/richg/ALL_AI/AI_Dev_Pipeline`             │
     │ - **Tech Stack:** Python 3.12+, SQLite, PowerShell 7                    │
     │ - **Working Method:** Git worktrees for isolation                       │
     │ - **Branch Pattern:** `workstream/<ws_id>`                              │
     │ - **Worktree Path:** `.worktrees/<ws_id>/`                              │
     │                                                                         │
     │ ## Your Assigned Workstreams                                            │
     │                                                                         │
     │ You have been assigned **8 workstreams** total. Execute them in         │
     │ dependency order.                                                       │
     │                                                                         │
     │ ---                                                                     │
     │                                                                         │
     │ ### Workstream 1: ws-ph01-spec-mapping                                  │
     │                                                                         │
     │ **Phase:** PH-01                                                        │
     │ **Difficulty:** Hard                                                    │
     │ **Goal:** Generate intelligent spec-to-code mappings in                 │
     │ `spec_index_map.md`                                                     │
     │                                                                         │
     │ **Dependencies:**                                                       │
     │ - `ws-ph01-index-scanner` (Codex will complete first)                   │
     │                                                                         │
     │ **Files in Scope:**                                                     │
     │ - `docs/spec/spec_index_map.md` (create/generate)                       │
     │ - `scripts/generate_spec_index.py` or `src/pipeline/spec_index.py`      │
     │ (refine mapping logic)                                                  │
     │                                                                         │
     │ **Git Worktree Setup:**                                                 │
     │ ```bash                                                                 │
     │ cd C:/Users/richg/ALL_AI/AI_Dev_Pipeline                                │
     │ git worktree add .worktrees/ws-ph01-spec-mapping -b                     │
     │ workstream/ws-ph01-spec-mapping main                                    │
     │ cd .worktrees/ws-ph01-spec-mapping                                      │
     │                                                                         │
     │ Tasks:                                                                  │
     │ 1. Review the index scanner created by Codex in ws-ph01-index-scanner   │
     │ 2. Enhance the mapping logic to intelligently assign:                   │
     │   - Module (based on IDX tag semantics: DB → db.py, PROMPT → prompts.py,│
     │  etc.)                                                                  │
     │   - Function/Class names (infer from context)                           │
     │   - Phase assignment (PH-02 for DB, PH-03 for tools, etc.)              │
     │   - Version (v1.0 vs v2.0+)                                             │
     │ 3. Generate docs/spec/spec_index_map.md with complete mappings          │
     │ 4. Ensure the mapping is a well-formatted Markdown table with columns:  │
     │   - IDX | Description | Source File | Line | Module | FunctionOrClass | │
     │ Phase | Version                                                         │
     │                                                                         │
     │ Acceptance Criteria:                                                    │
     │ - ✅ docs/spec/spec_index_map.md exists with >= 1 mapped IDX entry (or  │
     │ note if none found)                                                     │
     │ - ✅ Mapping logic uses semantic rules (documented in code comments)    │
     │ - ✅ Table is valid Markdown and human-readable                         │
     │ - ✅ No hardcoded paths (use relative paths from project root)          │
     │                                                                         │
     │ Commit Pattern:                                                         │
     │ git add docs/spec/spec_index_map.md scripts/generate_spec_index.py      │
     │ git commit -m "feat(ws-ph01-spec-mapping): generate intelligent         │
     │ spec-to-code mappings"                                                  │
     │                                                                         │
     │ ---                                                                     │
     │ Workstream 2: ws-ph01-tests                                             │
     │                                                                         │
     │ Phase: PH-01                                                            │
     │ Difficulty: Medium                                                      │
     │ Goal: Create comprehensive tests for the spec index scanner             │
     │                                                                         │
     │ Dependencies:                                                           │
     │ - ws-ph01-index-scanner (Codex)                                         │
     │                                                                         │
     │ Files in Scope:                                                         │
     │ - tests/pipeline/test_spec_index.py (create)                            │
     │                                                                         │
     │ Git Worktree Setup:                                                     │
     │ cd C:/Users/richg/ALL_AI/AI_Dev_Pipeline                                │
     │ git worktree add .worktrees/ws-ph01-tests -b workstream/ws-ph01-tests   │
     │ main                                                                    │
     │ cd .worktrees/ws-ph01-tests                                             │
     │                                                                         │
     │ Tasks:                                                                  │
     │ 1. Create tests/pipeline/test_spec_index.py                             │
     │ 2. Import the index scanner logic from src/pipeline/spec_index.py or    │
     │ scripts/generate_spec_index.py                                          │
     │ 3. Write tests that cover:                                              │
     │   - Scanner finds IDX tags correctly                                    │
     │   - Scanner handles missing/empty docs gracefully                       │
     │   - Scanner produces valid output structure                             │
     │   - Edge cases: malformed tags, nested directories, large files         │
     │ 4. Use pytest fixtures for temp directories and mock spec files         │
     │                                                                         │
     │ Acceptance Criteria:                                                    │
     │ - ✅ tests/pipeline/test_spec_index.py exists with >= 4 test functions  │
     │ - ✅ Tests pass when run with pytest tests/pipeline/test_spec_index.py  │
     │ - ✅ Coverage includes success and failure paths                        │
     │ - ✅ No external dependencies (use temp files/dirs)                     │
     │                                                                         │
     │ Commit Pattern:                                                         │
     │ git add tests/pipeline/test_spec_index.py                               │
     │ git commit -m "test(ws-ph01-tests): add comprehensive spec index scanner│
     │  tests"                                                                 │
     │                                                                         │
     │ ---                                                                     │
     │ Workstream 3: ws-ph02-state-machine                                     │
     │                                                                         │
     │ Phase: PH-02                                                            │
     │ Difficulty: Hard                                                        │
     │ Goal: Implement formal state machine with transition validation         │
     │                                                                         │
     │ Dependencies:                                                           │
     │ - ws-ph02-db-core (Codex will create db.py foundation)                  │
     │                                                                         │
     │ Files in Scope:                                                         │
     │ - src/pipeline/db.py (add state transition logic)                       │
     │ - src/pipeline/state_machine.py (optional separate module)              │
     │                                                                         │
     │ Git Worktree Setup:                                                     │
     │ cd C:/Users/richg/ALL_AI/AI_Dev_Pipeline                                │
     │ git worktree add .worktrees/ws-ph02-state-machine -b                    │
     │ workstream/ws-ph02-state-machine main                                   │
     │ cd .worktrees/ws-ph02-state-machine                                     │
     │                                                                         │
     │ Tasks:                                                                  │
     │ 1. Define allowed states for:                                           │
     │   - Runs: pending, running, completed, failed, partial, abandoned       │
     │   - Workstreams: pending, ready, editing, static_check, fixing,         │
     │ runtime_check, done, failed, blocked, abandoned                         │
     │ 2. Implement validate_state_transition(entity_type, from_state,         │
     │ to_state):                                                              │
     │   - Returns None if valid                                               │
     │   - Raises ValueError with clear message if invalid                     │
     │ 3. Define valid transition rules (e.g., workstream state diagram):      │
     │   - pending → ready                                                     │
     │   - ready → editing                                                     │
     │   - editing → static_check                                              │
     │   - static_check → fixing OR runtime_check                              │
     │   - fixing → static_check (retry loop)                                  │
     │   - runtime_check → done                                                │
     │   - Any state → failed/abandoned                                        │
     │   - pending/ready → blocked (dependency failure)                        │
     │ 4. Integrate into update_workstream_status() and update_run_status():   │
     │   - Call validate_state_transition() before UPDATE                      │
     │   - Record event if transition blocked                                  │
     │ 5. Add comprehensive docstrings explaining state machine                │
     │                                                                         │
     │ Acceptance Criteria:                                                    │
     │ - ✅ validate_state_transition() function exists and works              │
     │ - ✅ Valid transitions succeed, invalid ones raise ValueError           │
     │ - ✅ State machine logic is documented (docstrings or comments)         │
     │ - ✅ update_workstream_status() enforces transitions                    │
     │ - ✅ State diagram documented in code or separate docs/state_machine.md │
     │                                                                         │
     │ Commit Pattern:                                                         │
     │ git add src/pipeline/db.py src/pipeline/state_machine.py                │
     │ git commit -m "feat(ws-ph02-state-machine): implement formal state      │
     │ machine with validation"                                                │
     │                                                                         │
     │ ---                                                                     │
     │ Workstream 4: ws-ph02-crud                                              │
     │                                                                         │
     │ Phase: PH-02                                                            │
     │ Difficulty: Medium                                                      │
     │ Goal: Implement CRUD operations for runs, workstreams, steps, errors,   │
     │ events                                                                  │
     │                                                                         │
     │ Dependencies:                                                           │
     │ - ws-ph02-db-core (Codex creates connection and init)                   │
     │                                                                         │
     │ Files in Scope:                                                         │
     │ - src/pipeline/db.py (add CRUD functions)                               │
     │                                                                         │
     │ Git Worktree Setup:                                                     │
     │ cd C:/Users/richg/ALL_AI/AI_Dev_Pipeline                                │
     │ git worktree add .worktrees/ws-ph02-crud -b workstream/ws-ph02-crud main│
     │ cd .worktrees/ws-ph02-crud                                              │
     │                                                                         │
     │ Tasks:                                                                  │
     │ 1. Implement CRUD functions in db.py:                                   │
     │   - Runs: create_run(), update_run_status(), get_run()                  │
     │   - Workstreams: create_workstream(), update_workstream_status(),       │
     │ get_workstream(), get_workstreams_for_run()                             │
     │   - Steps: record_step_attempt()                                        │
     │   - Errors: record_error() (with dedup logic: increment count if        │
     │ signature exists)                                                       │
     │   - Events: record_event()                                              │
     │ 2. Each function should:                                                │
     │   - Open connection via get_connection()                                │
     │   - Use transactions (commit/rollback)                                  │
     │   - Return meaningful data (run_id, ws_id, etc.)                        │
     │   - Handle errors gracefully                                            │
     │ 3. Use ISO 8601 UTC timestamps: datetime.utcnow().isoformat() + "Z"     │
     │ 4. For record_error(): check if (run_id, ws_id, step_name, signature)   │
     │ exists:                                                                 │
     │   - If yes: UPDATE count+1, last_seen_at                                │
     │   - If no: INSERT with count=1                                          │
     │                                                                         │
     │ Acceptance Criteria:                                                    │
     │ - ✅ All CRUD functions exist and have type hints                       │
     │ - ✅ Functions use transactions correctly                               │
     │ - ✅ record_error() implements dedup logic                              │
     │ - ✅ Timestamps are ISO 8601 UTC format                                 │
     │ - ✅ No SQL injection vulnerabilities (use parameterized queries)       │
     │                                                                         │
     │ Commit Pattern:                                                         │
     │ git add src/pipeline/db.py                                              │
     │ git commit -m "feat(ws-ph02-crud): implement CRUD operations for all DB │
     │ entities"                                                               │
     │                                                                         │
     │ ---                                                                     │
     │ Workstream 5: ws-ph02-tests                                             │
     │                                                                         │
     │ Phase: PH-02                                                            │
     │ Difficulty: Hard                                                        │
     │ Goal: Comprehensive tests for DB layer and state machine                │
     │                                                                         │
     │ Dependencies:                                                           │
     │ - ws-ph02-state-machine (Claude)                                        │
     │ - ws-ph02-crud (Claude)                                                 │
     │                                                                         │
     │ Files in Scope:                                                         │
     │ - tests/pipeline/test_db_state.py (create)                              │
     │                                                                         │
     │ Git Worktree Setup:                                                     │
     │ cd C:/Users/richg/ALL_AI/AI_Dev_Pipeline                                │
     │ git worktree add .worktrees/ws-ph02-tests -b workstream/ws-ph02-tests   │
     │ main                                                                    │
     │ cd .worktrees/ws-ph02-tests                                             │
     │                                                                         │
     │ Tasks:                                                                  │
     │ 1. Create tests/pipeline/test_db_state.py                               │
     │ 2. Use temp DB (override PIPELINE_DB_PATH in test fixtures)             │
     │ 3. Test coverage:                                                       │
     │   - Schema initialization (init_db())                                   │
     │   - Run CRUD operations                                                 │
     │   - Workstream CRUD operations                                          │
     │   - State machine: valid transitions pass, invalid raise ValueError     │
     │   - Error deduplication (same signature increments count)               │
     │   - Event recording                                                     │
     │   - Edge cases: missing run_id, null fields, concurrent writes          │
     │ 4. Use pytest fixtures for setup/teardown                               │
     │                                                                         │
     │ Acceptance Criteria:                                                    │
     │ - ✅ tests/pipeline/test_db_state.py exists with >= 10 test functions   │
     │ - ✅ All tests pass with pytest tests/pipeline/test_db_state.py         │
     │ - ✅ Tests use temp DB (no side effects on real DB)                     │
     │ - ✅ Coverage >= 80% for db.py                                          │
     │ - ✅ State machine transitions fully tested                             │
     │                                                                         │
     │ Commit Pattern:                                                         │
     │ git add tests/pipeline/test_db_state.py                                 │
     │ git commit -m "test(ws-ph02-tests): comprehensive DB and state machine  │
     │ tests"                                                                  │
     │                                                                         │
     │ ---                                                                     │
     │ Workstream 6: ws-ph03-adapter-core                                      │
     │                                                                         │
     │ Phase: PH-03                                                            │
     │ Difficulty: Hard                                                        │
     │ Goal: Implement core tool adapter with subprocess handling, timeouts,   │
     │ error capture                                                           │
     │                                                                         │
     │ Dependencies: None (can start immediately)                              │
     │                                                                         │
     │ Files in Scope:                                                         │
     │ - src/pipeline/tools.py (create core adapter)                           │
     │                                                                         │
     │ Git Worktree Setup:                                                     │
     │ cd C:/Users/richg/ALL_AI/AI_Dev_Pipeline                                │
     │ git worktree add .worktrees/ws-ph03-adapter-core -b                     │
     │ workstream/ws-ph03-adapter-core main                                    │
     │ cd .worktrees/ws-ph03-adapter-core                                      │
     │                                                                         │
     │ Tasks:                                                                  │
     │ 1. Create src/pipeline/tools.py                                         │
     │ 2. Implement:                                                           │
     │   - ToolResult dataclass/dict with fields:                              │
     │       - tool_id, command_line, exit_code, stdout, stderr, timed_out,    │
     │ started_at, completed_at, duration_sec, success                         │
     │   - load_tool_profiles() → loads config/tool_profiles.json              │
     │   - get_tool_profile(tool_id) → retrieves specific tool config          │
     │   - render_command(tool_id, context) → template substitution ({cwd},    │
     │ {repo_root}, etc.)                                                      │
     │   - run_tool(tool_id, context, *, run_id=None, ws_id=None) → main entry │
     │ point:                                                                  │
     │       - Renders command from profile                                    │
     │     - Runs subprocess with timeout                                      │
     │     - Captures stdout/stderr                                            │
     │     - Determines success based on exit codes                            │
     │     - Returns ToolResult                                                │
     │ 3. Handle timeouts using subprocess.run(timeout=...)                    │
     │ 4. Handle working directory and environment variable overrides          │
     │ 5. NO DB integration yet (that's ws-ph03-db-integration)                │
     │                                                                         │
     │ Acceptance Criteria:                                                    │
     │ - ✅ run_tool() can execute simple commands (e.g., "echo")              │
     │ - ✅ Timeout handling works (sets timed_out=True, exit_code=-1)         │
     │ - ✅ Template substitution works for {cwd}, {repo_root}                 │
     │ - ✅ Error handling: missing tool, invalid profile                      │
     │ - ✅ ToolResult captures all required fields                            │
     │                                                                         │
     │ Commit Pattern:                                                         │
     │ git add src/pipeline/tools.py                                           │
     │ git commit -m "feat(ws-ph03-adapter-core): implement core tool adapter  │
     │ with subprocess handling"                                               │
     │                                                                         │
     │ ---                                                                     │
     │ Workstream 7: ws-ph03-db-integration                                    │
     │                                                                         │
     │ Phase: PH-03                                                            │
     │ Difficulty: Medium                                                      │
     │ Goal: Integrate tools.py with db.py for event/error recording           │
     │                                                                         │
     │ Dependencies:                                                           │
     │ - ws-ph03-adapter-core (Claude)                                         │
     │ - ws-ph02-crud (Claude - needs record_event() and record_error())       │
     │                                                                         │
     │ Files in Scope:                                                         │
     │ - src/pipeline/tools.py (add DB calls)                                  │
     │                                                                         │
     │ Git Worktree Setup:                                                     │
     │ cd C:/Users/richg/ALL_AI/AI_Dev_Pipeline                                │
     │ git worktree add .worktrees/ws-ph03-db-integration -b                   │
     │ workstream/ws-ph03-db-integration main                                  │
     │ cd .worktrees/ws-ph03-db-integration                                    │
     │                                                                         │
     │ Tasks:                                                                  │
     │ 1. Import db.record_event() and db.record_error() in tools.py           │
     │ 2. Modify run_tool() to:                                                │
     │   - Record "tool_started" event before execution (if run_id/ws_id       │
     │ provided)                                                               │
     │   - Record "tool_finished" event after execution                        │
     │   - Record error entry on failure (non-zero exit, timeout)              │
     │   - Generate error signature:                                           │
     │ f"{tool_id}::{error_code}::{normalized_stderr}"                         │
     │ 3. Event payloads should include:                                       │
     │   - tool_started: {tool_id, command, profile_type}                      │
     │   - tool_finished: {tool_id, exit_code, success, duration_sec}          │
     │   - tool_timeout: {tool_id, timeout_sec}                                │
     │ 4. Handle case where run_id/ws_id are None (skip DB calls gracefully)   │
     │                                                                         │
     │ Acceptance Criteria:                                                    │
     │ - ✅ run_tool() calls db.record_event() when run_id provided            │
     │ - ✅ Errors are recorded with proper signatures                         │
     │ - ✅ DB calls are optional (work without run_id/ws_id)                  │
     │ - ✅ No errors when DB calls made with valid IDs                        │
     │                                                                         │
     │ Commit Pattern:                                                         │
     │ git add src/pipeline/tools.py                                           │
     │ git commit -m "feat(ws-ph03-db-integration): wire tool adapter to DB for│
     │  events/errors"                                                         │
     │                                                                         │
     │ ---                                                                     │
     │ Workstream 8: ws-ph03-tests                                             │
     │                                                                         │
     │ Phase: PH-03                                                            │
     │ Difficulty: Hard                                                        │
     │ Goal: Comprehensive tests for tool adapter                              │
     │                                                                         │
     │ Dependencies:                                                           │
     │ - ws-ph03-adapter-core (Claude)                                         │
     │ - ws-ph03-db-integration (Claude)                                       │
     │                                                                         │
     │ Files in Scope:                                                         │
     │ - tests/pipeline/test_tools.py (create)                                 │
     │                                                                         │
     │ Git Worktree Setup:                                                     │
     │ cd C:/Users/richg/ALL_AI/AI_Dev_Pipeline                                │
     │ git worktree add .worktrees/ws-ph03-tests -b workstream/ws-ph03-tests   │
     │ main                                                                    │
     │ cd .worktrees/ws-ph03-tests                                             │
     │                                                                         │
     │ Tasks:                                                                  │
     │ 1. Create tests/pipeline/test_tools.py                                  │
     │ 2. Use temp tool_profiles.json and temp DB                              │
     │ 3. Test coverage:                                                       │
     │   - load_tool_profiles() validates JSON                                 │
     │   - render_command() substitutes templates correctly                    │
     │   - run_tool("echo", {...}) succeeds                                    │
     │   - Timeout handling (use short timeout on sleep command)               │
     │   - Non-zero exit codes marked as failure                               │
     │   - DB event/error recording (when run_id provided)                     │
     │   - Missing tool binary handled gracefully                              │
     │ 4. Use pytest fixtures for temp configs and DB                          │
     │                                                                         │
     │ Acceptance Criteria:                                                    │
     │ - ✅ tests/pipeline/test_tools.py exists with >= 8 test functions       │
     │ - ✅ All tests pass                                                     │
     │ - ✅ Coverage includes success, failure, timeout cases                  │
     │ - ✅ DB integration tested (events/errors recorded)                     │
     │ - ✅ Tests use isolated temp resources                                  │
     │                                                                         │
     │ Commit Pattern:                                                         │
     │ git add tests/pipeline/test_tools.py                                    │
     │ git commit -m "test(ws-ph03-tests): comprehensive tool adapter tests    │
     │ with DB integration"                                                    │
     │                                                                         │
     │ ---                                                                     │
     │ Constraints & Guidelines                                                │
     │                                                                         │
     │ File Scope Discipline                                                   │
     │                                                                         │
     │ - ONLY modify files listed in files_scope for your workstream           │
     │ - Do NOT edit files assigned to Codex workstreams                       │
     │ - If you need to modify an overlapping file, coordinate or wait for     │
     │ dependencies                                                            │
     │                                                                         │
     │ Git Worktree Isolation                                                  │
     │                                                                         │
     │ - Work inside .worktrees/<ws_id>/ directory                             │
     │ - All commits on workstream/<ws_id> branch                              │
     │ - Do NOT modify main branch directly                                    │
     │ - Do NOT delete other worktrees                                         │
     │                                                                         │
     │ Code Quality                                                            │
     │                                                                         │
     │ - Use type hints for all functions                                      │
     │ - Write comprehensive docstrings                                        │
     │ - Follow PEP8 / Black formatting                                        │
     │ - No hardcoded paths (use environment variables or relative paths)      │
     │                                                                         │
     │ Testing                                                                 │
     │                                                                         │
     │ - All tests must pass before marking workstream complete                │
     │ - Use pytest fixtures for setup/teardown                                │
     │ - Use temp files/DBs to avoid side effects                              │
     │                                                                         │
     │ Commit Messages                                                         │
     │                                                                         │
     │ - Use Conventional Commits format                                       │
     │ - Pattern: <type>(<ws_id>): <description>                               │
     │ - Types: feat, fix, test, docs, refactor                                │
     │                                                                         │
     │ ---                                                                     │
     │ Execution Order                                                         │
     │                                                                         │
     │ 1. Phase PH-01: (wait for Codex to complete dependencies)               │
     │   - ws-ph01-spec-mapping (after ws-ph01-index-scanner)                  │
     │   - ws-ph01-tests (after ws-ph01-index-scanner)                         │
     │ 2. Phase PH-02: (wait for Codex to complete ws-ph02-db-core)            │
     │   - ws-ph02-state-machine (after ws-ph02-db-core)                       │
     │   - ws-ph02-crud (after ws-ph02-db-core)                                │
     │   - ws-ph02-tests (after ws-ph02-state-machine + ws-ph02-crud)          │
     │ 3. Phase PH-03: (can start adapter-core immediately)                    │
     │   - ws-ph03-adapter-core (no dependencies)                              │
     │   - ws-ph03-db-integration (after ws-ph03-adapter-core + ws-ph02-crud)  │
     │   - ws-ph03-tests (after ws-ph03-db-integration)                        │
     │                                                                         │
     │ ---                                                                     │
     │ Success Criteria                                                        │
     │                                                                         │
     │ Each workstream is complete when:                                       │
     │ - ✅ All files in files_scope created/modified as specified             │
     │ - ✅ All acceptance criteria met                                        │
     │ - ✅ Tests pass (if applicable)                                         │
     │ - ✅ Code committed to workstream/<ws_id> branch                        │
     │ - ✅ No violations of file scope or git worktree isolation              │
     │                                                                         │
     │ Report completion status for each workstream as you finish.             │
     │                                                                         │
     │ ---                                                                     │
     │                                                                         │
     │ ## Part 4: Codex CLI Prompt Document                                    │
     │                                                                         │
     │ ### CODEX_WORKSTREAMS_PLAN.md                                           │
     │                                                                         │
     │ ```markdown                                                             │
     │ # Codex CLI: AI Pipeline Implementation Workstreams (PH-01 to PH-03)    │
     │                                                                         │
     │ ## Your Role                                                            │
     │                                                                         │
     │ You are Codex CLI, responsible for the **simpler and more mechanical    │
     │ workstreams** across phases PH-01, PH-02, and PH-03 of the AI           │
     │ Development Pipeline project.                                           │
     │                                                                         │
     │ Your workstreams involve:                                               │
     │ - Creating well-structured file stubs                                   │
     │ - Writing straightforward configuration files                           │
     │ - Implementing mechanical CRUD operations                               │
     │ - Writing clear documentation                                           │
     │                                                                         │
     │ ## Project Context                                                      │
     │                                                                         │
     │ - **Project Root:** `C:/Users/richg/ALL_AI/AI_Dev_Pipeline`             │
     │ - **Tech Stack:** Python 3.12+, SQLite, PowerShell 7                    │
     │ - **Working Method:** Git worktrees for isolation                       │
     │ - **Branch Pattern:** `workstream/<ws_id>`                              │
     │ - **Worktree Path:** `.worktrees/<ws_id>/`                              │
     │                                                                         │
     │ ## Your Assigned Workstreams                                            │
     │                                                                         │
     │ You have been assigned **9 workstreams** total. Many can run in parallel│
     │  as they have minimal dependencies.                                     │
     │                                                                         │
     │ ---                                                                     │
     │                                                                         │
     │ ### Workstream 1: ws-ph01-module-stubs                                  │
     │                                                                         │
     │ **Phase:** PH-01                                                        │
     │ **Difficulty:** Easy                                                    │
     │ **Goal:** Create canonical module stubs for the pipeline                │
     │                                                                         │
     │ **Dependencies:** None                                                  │
     │                                                                         │
     │ **Files in Scope:**                                                     │
     │ - `src/pipeline/db.py`                                                  │
     │ - `src/pipeline/orchestrator.py`                                        │
     │ - `src/pipeline/tools.py`                                               │
     │ - `src/pipeline/prompts.py`                                             │
     │ - `src/pipeline/worktree.py`                                            │
     │ - `src/pipeline/bundles.py`                                             │
     │ - `src/pipeline/circuit_breakers.py`                                    │
     │ - `src/pipeline/recovery.py`                                            │
     │ - `src/pipeline/scheduler.py`                                           │
     │ - `src/pipeline/executor.py`                                            │
     │                                                                         │
     │ **Git Worktree Setup:**                                                 │
     │ ```bash                                                                 │
     │ cd C:/Users/richg/ALL_AI/AI_Dev_Pipeline                                │
     │ git worktree add .worktrees/ws-ph01-module-stubs -b                     │
     │ workstream/ws-ph01-module-stubs main                                    │
     │ cd .worktrees/ws-ph01-module-stubs                                      │
     │                                                                         │
     │ Tasks:                                                                  │
     │ 1. Ensure src/pipeline/ directory exists                                │
     │ 2. Create each module file listed above                                 │
     │ 3. For each module, add:                                                │
     │   - Module-level docstring describing its purpose (2-4 sentences)       │
     │   - TODO comment indicating which phase will implement it               │
     │   - Example:                                                            │
     │   """                                                                   │
     │ Database access layer for AI Development Pipeline.                      │
     │ Provides SQLite state management for runs, workstreams, steps, errors,  │
     │ and events.                                                             │
     │ Implements state machine validation and CRUD operations.                │
     │ """                                                                     │
     │ # TODO: Full implementation in PH-02                                    │
     │ 4. Module purposes:                                                     │
     │   - db.py: SQLite state layer, CRUD, state machine                      │
     │   - orchestrator.py: Main pipeline execution loop                       │
     │   - tools.py: External tool adapter (Aider, pytest, etc.)               │
     │   - prompts.py: Prompt template engine for AI tools                     │
     │   - worktree.py: Git worktree lifecycle management                      │
     │   - bundles.py: Workstream bundle parsing and validation                │
     │   - circuit_breakers.py: Retry limits and oscillation detection         │
     │   - recovery.py: Crash recovery and resume logic                        │
     │   - scheduler.py: DAG-based workstream scheduling                       │
     │   - executor.py: Parallel execution workers                             │
     │                                                                         │
     │ Acceptance Criteria:                                                    │
     │ - ✅ All 10 module files exist in src/pipeline/                         │
     │ - ✅ Each has a clear docstring                                         │
     │ - ✅ Each has a TODO comment                                            │
     │ - ✅ Files are valid Python (can be imported)                           │
     │                                                                         │
     │ Commit Pattern:                                                         │
     │ git add src/pipeline/*.py                                               │
     │ git commit -m "chore(ws-ph01-module-stubs): create canonical pipeline   │
     │ module stubs"                                                           │
     │                                                                         │
     │ ---                                                                     │
     │ Workstream 2: ws-ph01-index-scanner                                     │
     │                                                                         │
     │ Phase: PH-01                                                            │
     │ Difficulty: Medium                                                      │
     │ Goal: Create script to scan docs for [IDX-...] tags                     │
     │                                                                         │
     │ Dependencies: None                                                      │
     │                                                                         │
     │ Files in Scope:                                                         │
     │ - scripts/generate_spec_index.py (create)                               │
     │ - OR src/pipeline/spec_index.py + small wrapper in scripts/             │
     │                                                                         │
     │ Git Worktree Setup:                                                     │
     │ cd C:/Users/richg/ALL_AI/AI_Dev_Pipeline                                │
     │ git worktree add .worktrees/ws-ph01-index-scanner -b                    │
     │ workstream/ws-ph01-index-scanner main                                   │
     │ cd .worktrees/ws-ph01-index-scanner                                     │
     │                                                                         │
     │ Tasks:                                                                  │
     │ 1. Create scripts/generate_spec_index.py                                │
     │ 2. Implement:                                                           │
     │   - Walk docs/ directory recursively                                    │
     │   - Find all .md and .txt files                                         │
     │   - Use regex to find [IDX-...] tags: r"/[IDX-[A-Z0-9/-]+\]"            │
     │   - Extract:                                                            │
     │       - IDX tag (e.g., IDX-DB-SCHEMA-01)                                │
     │     - File path (relative to project root)                              │
     │     - Line number                                                       │
     │     - Short description (the line containing the tag, or nearest        │
     │ heading)                                                                │
     │   - Return list of dicts: [{idx, file, line, description}, ...]         │
     │ 3. Add CLI capability:                                                  │
     │   - python scripts/generate_spec_index.py runs scan and prints results  │
     │   - Output format: simple text or JSON                                  │
     │ 4. Handle edge cases:                                                   │
     │   - No spec files found → return empty list (don't crash)               │
     │   - Malformed tags → skip them                                          │
     │                                                                         │
     │ Acceptance Criteria:                                                    │
     │ - ✅ Script exists and runs without errors                              │
     │ - ✅ Can find IDX tags in test files                                    │
     │ - ✅ Returns structured data (list of dicts)                            │
     │ - ✅ Handles empty/missing docs gracefully                              │
     │ - ✅ No hardcoded paths                                                 │
     │                                                                         │
     │ Commit Pattern:                                                         │
     │ git add scripts/generate_spec_index.py                                  │
     │ git commit -m "feat(ws-ph01-index-scanner): implement spec index tag    │
     │ scanner"                                                                │
     │                                                                         │
     │ ---                                                                     │
     │ Workstream 3: ws-ph01-docs                                              │
     │                                                                         │
     │ Phase: PH-01                                                            │
     │ Difficulty: Easy                                                        │
     │ Goal: Update architecture and phase plan docs for PH-01                 │
     │                                                                         │
     │ Dependencies: None (can run in parallel)                                │
     │                                                                         │
     │ Files in Scope:                                                         │
     │ - docs/ARCHITECTURE.md (update)                                         │
     │ - docs/PHASE_PLAN.md (update)                                           │
     │ - docs/spec/README.md (create)                                          │
     │                                                                         │
     │ Git Worktree Setup:                                                     │
     │ cd C:/Users/richg/ALL_AI/AI_Dev_Pipeline                                │
     │ git worktree add .worktrees/ws-ph01-docs -b workstream/ws-ph01-docs main│
     │ cd .worktrees/ws-ph01-docs                                              │
     │                                                                         │
     │ Tasks:                                                                  │
     │ 1. Update docs/ARCHITECTURE.md:                                         │
     │   - Add section: "Spec Mapping & IDX Index"                             │
     │   - Describe:                                                           │
     │       - Location of spec files (docs/spec/)                             │
     │     - Purpose of spec_index_map.md                                      │
     │     - How to run scripts/generate_spec_index.py                         │
     │ 2. Update docs/PHASE_PLAN.md:                                           │
     │   - Add PH-01 section:                                                  │
     │       - One paragraph summary                                           │
     │     - Bullet list of artifacts: spec_index_map.md, module stubs, index  │
     │ scanner                                                                 │
     │ 3. Create docs/spec/README.md:                                          │
     │   - Explain spec file organization                                      │
     │   - Explain IDX tagging convention                                      │
     │   - How to regenerate index                                             │
     │                                                                         │
     │ Acceptance Criteria:                                                    │
     │ - ✅ All three docs updated/created                                     │
     │ - ✅ Clear, concise explanations                                        │
     │ - ✅ Valid Markdown formatting                                          │
     │ - ✅ Consistent with AGENTS.md style guide                              │
     │                                                                         │
     │ Commit Pattern:                                                         │
     │ git add docs/ARCHITECTURE.md docs/PHASE_PLAN.md docs/spec/README.md     │
     │ git commit -m "docs(ws-ph01-docs): update architecture and phase docs   │
     │ for PH-01"                                                              │
     │                                                                         │
     │ ---                                                                     │
     │ Workstream 4: ws-ph02-schema                                            │
     │                                                                         │
     │ Phase: PH-02                                                            │
     │ Difficulty: Medium                                                      │
     │ Goal: Create SQLite schema DDL file                                     │
     │                                                                         │
     │ Dependencies: None                                                      │
     │                                                                         │
     │ Files in Scope:                                                         │
     │ - schema/schema.sql (create)                                            │
     │                                                                         │
     │ Git Worktree Setup:                                                     │
     │ cd C:/Users/richg/ALL_AI/AI_Dev_Pipeline                                │
     │ git worktree add .worktrees/ws-ph02-schema -b workstream/ws-ph02-schema │
     │ main                                                                    │
     │ cd .worktrees/ws-ph02-schema                                            │
     │                                                                         │
     │ Tasks:                                                                  │
     │ 1. Create schema/schema.sql                                             │
     │ 2. Define tables:                                                       │
     │   - schema_meta (key TEXT PRIMARY KEY, value TEXT)                      │
     │   - runs (run_id TEXT PRIMARY KEY, status TEXT, created_at TEXT,        │
     │ updated_at TEXT, metadata_json TEXT)                                    │
     │   - workstreams (ws_id TEXT PRIMARY KEY, run_id TEXT FK, status TEXT,   │
     │ depends_on TEXT, created_at, updated_at, metadata_json)                 │
     │   - step_attempts (id INTEGER PRIMARY KEY AUTOINCREMENT, run_id, ws_id, │
     │ step_name, status, started_at, completed_at, result_json)               │
     │   - errors (id INTEGER PRIMARY KEY AUTOINCREMENT, run_id, ws_id,        │
     │ step_name, error_code, signature, message, context_json, count INTEGER  │
     │ DEFAULT 1, first_seen_at, last_seen_at)                                 │
     │   - events (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp, run_id,    │
     │ ws_id, event_type, payload_json)                                        │
     │ 3. Add indexes:                                                         │
     │   - runs(status)                                                        │
     │   - workstreams(run_id, status)                                         │
     │   - step_attempts(run_id, ws_id, step_name)                             │
     │   - errors(run_id, ws_id, signature)                                    │
     │   - events(run_id, ws_id, event_type)                                   │
     │ 4. Use CREATE TABLE IF NOT EXISTS for idempotency                       │
     │ 5. Add foreign key constraints where appropriate                        │
     │                                                                         │
     │ Acceptance Criteria:                                                    │
     │ - ✅ schema/schema.sql exists with all 6 tables                         │
     │ - ✅ All indexes defined                                                │
     │ - ✅ Foreign keys added                                                 │
     │ - ✅ Idempotent (can run multiple times)                                │
     │                                                                         │
     │ Commit Pattern:                                                         │
     │ git add schema/schema.sql                                               │
     │ git commit -m "feat(ws-ph02-schema): define SQLite schema for pipeline  │
     │ state"                                                                  │
     │                                                                         │
     │ ---                                                                     │
     │ Workstream 5: ws-ph02-db-core                                           │
     │                                                                         │
     │ Phase: PH-02                                                            │
     │ Difficulty: Medium                                                      │
     │ Goal: Implement DB connection and initialization                        │
     │                                                                         │
     │ Dependencies:                                                           │
     │ - ws-ph02-schema (needs schema.sql)                                     │
     │                                                                         │
     │ Files in Scope:                                                         │
     │ - src/pipeline/db.py (add connection and init functions)                │
     │                                                                         │
     │ Git Worktree Setup:                                                     │
     │ cd C:/Users/richg/ALL_AI/AI_Dev_Pipeline                                │
     │ git worktree add .worktrees/ws-ph02-db-core -b                          │
     │ workstream/ws-ph02-db-core main                                         │
     │ cd .worktrees/ws-ph02-db-core                                           │
     │                                                                         │
     │ Tasks:                                                                  │
     │ 1. Open src/pipeline/db.py (created in ws-ph01-module-stubs)            │
     │ 2. Implement:                                                           │
     │   - get_connection():                                                   │
     │       - Resolves DB path: PIPELINE_DB_PATH env var or                   │
     │ state/pipeline_state.db                                                 │
     │     - Creates parent directory if needed                                │
     │     - Returns sqlite3.Connection with row_factory=sqlite3.Row           │
     │   - init_db():                                                          │
     │       - Calls get_connection()                                          │
     │     - Checks if schema applied (query schema_meta)                      │
     │     - If not, reads and executes schema/schema.sql                      │
     │     - Inserts schema_meta row: ('schema_version', '1')                  │
     │     - Commits                                                           │
     │ 3. Add imports: sqlite3, os, pathlib                                    │
     │ 4. Use relative path resolution                                         │
     │                                                                         │
     │ Acceptance Criteria:                                                    │
     │ - ✅ get_connection() works and returns valid connection                │
     │ - ✅ init_db() creates DB and applies schema                            │
     │ - ✅ Idempotent (running twice doesn't break)                           │
     │ - ✅ DB path configurable via PIPELINE_DB_PATH                          │
     │                                                                         │
     │ Commit Pattern:                                                         │
     │ git add src/pipeline/db.py                                              │
     │ git commit -m "feat(ws-ph02-db-core): implement DB connection and schema│
     │  initialization"                                                        │
     │                                                                         │
     │ ---                                                                     │
     │ Workstream 6: ws-ph02-scripts                                           │
     │                                                                         │
     │ Phase: PH-02                                                            │
     │ Difficulty: Easy                                                        │
     │ Goal: Create DB management scripts                                      │
     │                                                                         │
     │ Dependencies:                                                           │
     │ - ws-ph02-db-core (needs init_db())                                     │
     │                                                                         │
     │ Files in Scope:                                                         │
     │ - scripts/init_db.py (create)                                           │
     │ - scripts/db_inspect.py (create)                                        │
     │                                                                         │
     │ Git Worktree Setup:                                                     │
     │ cd C:/Users/richg/ALL_AI/AI_Dev_Pipeline                                │
     │ git worktree add .worktrees/ws-ph02-scripts -b                          │
     │ workstream/ws-ph02-scripts main                                         │
     │ cd .worktrees/ws-ph02-scripts                                           │
     │                                                                         │
     │ Tasks:                                                                  │
     │ 1. Create scripts/init_db.py:                                           │
     │   - Import db.init_db()                                                 │
     │   - Call it                                                             │
     │   - Print DB path and schema version                                    │
     │   - Example:                                                            │
     │   import sys; sys.path.insert(0, '.')                                   │
     │ from src.pipeline import db                                             │
     │                                                                         │
     │ db.init_db()                                                            │
     │ print("DB initialized at:", ...)                                        │
     │ print("Schema version:", ...)                                           │
     │ 2. Create scripts/db_inspect.py:                                        │
     │   - Import db.get_connection()                                          │
     │   - Query and print:                                                    │
     │       - Number of runs                                                  │
     │     - Number of workstreams                                             │
     │     - Status summary                                                    │
     │   - Simple text output                                                  │
     │                                                                         │
     │ Acceptance Criteria:                                                    │
     │ - ✅ Both scripts exist and run without errors                          │
     │ - ✅ init_db.py creates/verifies DB                                     │
     │ - ✅ db_inspect.py prints useful summary                                │
     │                                                                         │
     │ Commit Pattern:                                                         │
     │ git add scripts/init_db.py scripts/db_inspect.py                        │
     │ git commit -m "feat(ws-ph02-scripts): add DB initialization and         │
     │ inspection scripts"                                                     │
     │                                                                         │
     │ ---                                                                     │
     │ Workstream 7: ws-ph02-docs                                              │
     │                                                                         │
     │ Phase: PH-02                                                            │
     │ Difficulty: Medium                                                      │
     │ Goal: Document state machine and update architecture docs               │
     │                                                                         │
     │ Dependencies:                                                           │
     │ - ws-ph02-state-machine (Claude will create state machine logic)        │
     │                                                                         │
     │ Files in Scope:                                                         │
     │ - docs/state_machine.md (create)                                        │
     │ - docs/ARCHITECTURE.md (update)                                         │
     │                                                                         │
     │ Git Worktree Setup:                                                     │
     │ cd C:/Users/richg/ALL_AI/AI_Dev_Pipeline                                │
     │ git worktree add .worktrees/ws-ph02-docs -b workstream/ws-ph02-docs main│
     │ cd .worktrees/ws-ph02-docs                                              │
     │                                                                         │
     │ Tasks:                                                                  │
     │ 1. Create docs/state_machine.md:                                        │
     │   - Describe run states and transitions                                 │
     │   - Describe workstream states and transitions                          │
     │   - Include ASCII diagram or bullet list of valid transitions           │
     │   - Explain that db.py enforces these via validate_state_transition()   │
     │ 2. Update docs/ARCHITECTURE.md:                                         │
     │   - Add section: "State & Persistence"                                  │
     │   - Describe:                                                           │
     │       - SQLite DB at state/pipeline_state.db                            │
     │     - Tables: runs, workstreams, step_attempts, errors, events          │
     │     - How to init: python scripts/init_db.py                            │
     │                                                                         │
     │ Acceptance Criteria:                                                    │
     │ - ✅ docs/state_machine.md exists with clear state descriptions         │
     │ - ✅ docs/ARCHITECTURE.md updated with State section                    │
     │ - ✅ Valid Markdown formatting                                          │
     │                                                                         │
     │ Commit Pattern:                                                         │
     │ git add docs/state_machine.md docs/ARCHITECTURE.md                      │
     │ git commit -m "docs(ws-ph02-docs): document state machine and DB        │
     │ architecture"                                                           │
     │                                                                         │
     │ ---                                                                     │
     │ Workstream 8: ws-ph03-profiles                                          │
     │                                                                         │
     │ Phase: PH-03                                                            │
     │ Difficulty: Easy                                                        │
     │ Goal: Create tool profiles configuration file                           │
     │                                                                         │
     │ Dependencies: None                                                      │
     │                                                                         │
     │ Files in Scope:                                                         │
     │ - config/tool_profiles.json (create)                                    │
     │                                                                         │
     │ Git Worktree Setup:                                                     │
     │ cd C:/Users/richg/ALL_AI/AI_Dev_Pipeline                                │
     │ git worktree add .worktrees/ws-ph03-profiles -b                         │
     │ workstream/ws-ph03-profiles main                                        │
     │ cd .worktrees/ws-ph03-profiles                                          │
     │                                                                         │
     │ Tasks:                                                                  │
     │ 1. Create config/tool_profiles.json                                     │
     │ 2. Define at least 3 tool profiles:                                     │
     │   - echo: Simple utility for testing                                    │
     │   - pytest: Python test runner                                          │
     │   - psscriptanalyzer: PowerShell static checker (placeholder)           │
     │ 3. Schema for each tool:                                                │
     │ {                                                                       │
     │   "tool-id": {                                                          │
     │     "type": "ai|static_check|test|utility",                             │
     │     "command": "executable",                                            │
     │     "args": ["arg1", "{template_var}"],                                 │
     │     "env": {"KEY": "value"},                                            │
     │     "working_dir": "{cwd}",                                             │
     │     "timeout_sec": 60,                                                  │
     │     "success_exit_codes": [0],                                          │
     │     "capture_output": true                                              │
     │   }                                                                     │
     │ }                                                                       │
     │ 4. Example profiles:                                                    │
     │ {                                                                       │
     │   "echo": {                                                             │
     │     "type": "utility",                                                  │
     │     "command": "echo",                                                  │
     │     "args": ["{message}"],                                              │
     │     "env": {},                                                          │
     │     "timeout_sec": 10,                                                  │
     │     "success_exit_codes": [0],                                          │
     │     "capture_output": true                                              │
     │   },                                                                    │
     │   "pytest": {                                                           │
     │     "type": "test",                                                     │
     │     "command": "pytest",                                                │
     │     "args": ["-q"],                                                     │
     │     "env": {},                                                          │
     │     "working_dir": "{repo_root}",                                       │
     │     "timeout_sec": 600,                                                 │
     │     "success_exit_codes": [0],                                          │
     │     "capture_output": true                                              │
     │   },                                                                    │
     │   "psscriptanalyzer": {                                                 │
     │     "type": "static_check",                                             │
     │     "command": "pwsh",                                                  │
     │     "args": ["-Command", "Invoke-ScriptAnalyzer", "-Path", "{file}"],   │
     │     "env": {},                                                          │
     │     "timeout_sec": 120,                                                 │
     │     "success_exit_codes": [0],                                          │
     │     "capture_output": true                                              │
     │   }                                                                     │
     │ }                                                                       │
     │                                                                         │
     │ Acceptance Criteria:                                                    │
     │ - ✅ config/tool_profiles.json exists                                   │
     │ - ✅ Valid JSON (no syntax errors)                                      │
     │ - ✅ At least 3 tool profiles defined                                   │
     │ - ✅ Each profile has all required fields                               │
     │                                                                         │
     │ Commit Pattern:                                                         │
     │ git add config/tool_profiles.json                                       │
     │ git commit -m "feat(ws-ph03-profiles): define tool profiles for pipeline│
     │  tools"                                                                 │
     │                                                                         │
     │ ---                                                                     │
     │ Workstream 9: ws-ph03-docs                                              │
     │                                                                         │
     │ Phase: PH-03                                                            │
     │ Difficulty: Easy                                                        │
     │ Goal: Update architecture and phase docs for PH-03                      │
     │                                                                         │
     │ Dependencies: None (can run in parallel)                                │
     │                                                                         │
     │ Files in Scope:                                                         │
     │ - docs/ARCHITECTURE.md (update)                                         │
     │ - docs/PHASE_PLAN.md (update)                                           │
     │                                                                         │
     │ Git Worktree Setup:                                                     │
     │ cd C:/Users/richg/ALL_AI/AI_Dev_Pipeline                                │
     │ git worktree add .worktrees/ws-ph03-docs -b workstream/ws-ph03-docs main│
     │ cd .worktrees/ws-ph03-docs                                              │
     │                                                                         │
     │ Tasks:                                                                  │
     │ 1. Update docs/ARCHITECTURE.md:                                         │
     │   - Add section: "Tool Profiles & Adapter Layer"                        │
     │   - Describe:                                                           │
     │       - Location: config/tool_profiles.json                             │
     │     - Purpose: Config-driven tool execution                             │
     │     - Tool types: ai, static_check, test, utility                       │
     │     - How tools.py uses these profiles                                  │
     │ 2. Update docs/PHASE_PLAN.md:                                           │
     │   - Add PH-03 section:                                                  │
     │       - One paragraph summary                                           │
     │     - Artifacts: tool_profiles.json, tools.py, tests                    │
     │                                                                         │
     │ Acceptance Criteria:                                                    │
     │ - ✅ Both docs updated                                                  │
     │ - ✅ Clear explanations                                                 │
     │ - ✅ Valid Markdown                                                     │
     │                                                                         │
     │ Commit Pattern:                                                         │
     │ git add docs/ARCHITECTURE.md docs/PHASE_PLAN.md                         │
     │ git commit -m "docs(ws-ph03-docs): update architecture and phase docs   │
     │ for PH-03"                                                              │
     │                                                                         │
     │ ---                                                                     │
     │ Constraints & Guidelines                                                │
     │                                                                         │
     │ File Scope Discipline                                                   │
     │                                                                         │
     │ - ONLY modify files listed in files_scope for your workstream           │
     │ - Do NOT edit files assigned to Claude workstreams                      │
     │ - If overlap needed, coordinate or note it                              │
     │                                                                         │
     │ Git Worktree Isolation                                                  │
     │                                                                         │
     │ - Work inside .worktrees/<ws_id>/ directory                             │
     │ - All commits on workstream/<ws_id> branch                              │
     │ - Do NOT modify main branch directly                                    │
     │                                                                         │
     │ Code Quality                                                            │
     │                                                                         │
     │ - Follow Python PEP8 style                                              │
     │ - Use clear variable names                                              │
     │ - Add docstrings to functions                                           │
     │ - Keep it simple and readable                                           │
     │                                                                         │
     │ Documentation                                                           │
     │                                                                         │
     │ - Write clear, concise docs                                             │
     │ - Follow existing style in AGENTS.md                                    │
     │ - Use proper Markdown formatting                                        │
     │                                                                         │
     │ Commit Messages                                                         │
     │                                                                         │
     │ - Use Conventional Commits format                                       │
     │ - Pattern: <type>(<ws_id>): <description>                               │
     │ - Types: feat, fix, docs, chore, test                                   │
     │                                                                         │
     │ ---                                                                     │
     │ Execution Order                                                         │
     │                                                                         │
     │ Can Start Immediately (No Dependencies):                                │
     │                                                                         │
     │ - ws-ph01-module-stubs                                                  │
     │ - ws-ph01-index-scanner                                                 │
     │ - ws-ph01-docs                                                          │
     │ - ws-ph02-schema                                                        │
     │ - ws-ph03-profiles                                                      │
     │ - ws-ph03-docs                                                          │
     │                                                                         │
     │ Wait for Dependencies:                                                  │
     │                                                                         │
     │ - ws-ph02-db-core (after ws-ph02-schema)                                │
     │ - ws-ph02-scripts (after ws-ph02-db-core)                               │
     │ - ws-ph02-docs (after Claude completes ws-ph02-state-machine)           │
     │                                                                         │
     │ ---                                                                     │
     │ Success Criteria                                                        │
     │                                                                         │
     │ Each workstream is complete when:                                       │
     │ - ✅ All files in files_scope created/modified                          │
     │ - ✅ All acceptance criteria met                                        │
     │ - ✅ Files are valid (Python can import, JSON parses, etc.)             │
     │ - ✅ Code committed to workstream/<ws_id> branch                        │
     │ - ✅ No violations of file scope or git isolation                       │
     │                                                                         │
     │ Report completion status for each workstream as you finish.             │
     │                                                                         │
     │ ---                                                                     │
     │                                                                         │
     │ This comprehensive plan provides:                                       │
     │ 1. **17 independent workstreams** across PH-01, PH-02, PH-03            │
     │ 2. **Clear division** between Claude (8 hard workstreams) and Codex (9  │
     │ easy/mechanical workstreams)                                            │
     │ 3. **Git worktree isolation** for parallel development                  │
     │ 4. **Two ready-to-use prompt documents** that can be pasted directly    │
     │ into Claude Code CLI and Codex CLI                                      │
     │                                                                         │
     │ The workstreams are designed to minimize file overlap and maximize      │
     │ parallel execution while respecting dependencies.                       │
     │                                                                         │
     │                                                                         │
     │                                                                         │
     │                                                                         │
     │                                                                         │
     │                                                                         │
     │                                                                         │
     │                                                                         │
     │                                                                         │
     │                                                                         │
     │                                                                         │
     │                                                                         │
     │                                                                         │
     │                                                                         │
     │                                                                         │
     │                                                                         │
     │                                                                         │
     │                                                                         │
     │                                                                         │
     │                                                                         │
     │                                                                         │
     │                                                                         │
     ╰─────────────────────────────────────────────────────────────────────────╯

> /export 
  ⎿  Conversation copied to clipboard



