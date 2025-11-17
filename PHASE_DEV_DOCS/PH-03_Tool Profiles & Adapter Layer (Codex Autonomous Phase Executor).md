PH-03_Tool Profiles & Adapter Layer (Codex Autonomous Phase Executor)

ROLE
You are Codex running with full access to a Windows development environment using PowerShell and Git.
Your job is to COMPLETELY IMPLEMENT phase PH-03 (Tool Profiles & Adapter Layer) for the AI Development Pipeline project, end-to-end, without requiring further user input.

You will:
- Define a config-driven tool profile format (JSON).
- Implement a robust tools.py adapter with a single run_tool() entry point.
- Integrate with the existing state/DB layer for events and errors.
- Add tests and minimal docs so future phases (PH-03.5, PH-06) can depend on this safely.

OPERATING CONTEXT
- OS: Windows 10/11
- Shell: PowerShell 7+ (pwsh)
- Version control: git
- Orchestrator language: Python 3.12+
- Previous phases:
  - PH-00: project skeleton (src/pipeline/, tests/pipeline/, docs/, scripts/, CI).
  - PH-01: spec index, canonical module stubs, including src/pipeline/tools.py.
  - PH-02: SQLite state layer (db.py, schema, state_machine, init_db, etc.).

PROJECT ROOT (IMPORTANT)
- Expected project root: C:/Users/richg/ALL_AI/AI_Dev_Pipeline

If that folder does NOT exist:
- Stop and write a clear, prominent note into docs/PHASE_PLAN.md under PH-03 that PH-00–PH-02 must be completed.
- Do NOT attempt to create tool configs elsewhere.

If it DOES exist:
- cd into that folder and proceed.

====================================
HIGH-LEVEL GOAL OF PH-03
====================================

Create a **single, reliable abstraction layer** for invoking external tools (AI tools, linters, tests, etc.) where:

1) Tools are defined declaratively in a config file (JSON).
2) Code calls run_tool(tool_id, context) and doesn’t worry about:
   - Exact command line
   - Environment variables
   - Timeouts
   - Exit code handling
3) All runs are logged via the DB layer:
   - Events entries (start, finish).
   - Error entries (on failure).
4) The abstraction is stable enough that PH-03.5 can layer Aider-specific prompt logic on top of it.

You are NOT responsible for writing prompts or Aider integration in this phase (that’s PH-03.5); just the generic tool layer.

====================================
REQUIRED OUTPUTS OF THIS PHASE
====================================

By the end of PH-03, the repo MUST have at minimum:

1) TOOL PROFILE CONFIG FILE
- config/tool_profiles.json
  - JSON structure defining tool profiles.
  - File should be human-editable and stable.

Proposed schema (you may refine, but keep it simple and documented):

- Root: object with keys as tool IDs (e.g., "echo", "pytest", "psscriptanalyzer", "pester", "aider-basic")
- Value: object with fields, e.g.:

  {
    "echo": {
      "type": "utility",              // "ai", "static_check", "test", "utility"
      "command": "echo",              // base command (string)
      "args": ["{message}"],          // default args template (list of strings)
      "env": {},                      // key/value pairs or template strings
      "working_dir": "{cwd}",         // template (optional)
      "timeout_sec": 60,              // default timeout
      "success_exit_codes": [0],      // list of acceptable exit codes
      "capture_output": true          // capture stdout/stderr
    },
    "pytest": {
      "type": "test",
      "command": "pytest",
      "args": ["-q"],
      "env": {},
      "working_dir": "{repo_root}",
      "timeout_sec": 600,
      "success_exit_codes": [0],
      "capture_output": true
    }
  }

- Include at least 3 example tools:
  - "echo" (for simple smoke tests).
  - "pytest" (Python tests).
  - A placeholder for PowerShell-based static checks (e.g., "psscriptanalyzer") with a sensible command; even if not fully used yet, define the profile so future phases can hook into it.

2) CONFIG RESOLUTION & OVERRIDES
- Default location:
  - <PROJECT_ROOT>/config/tool_profiles.json
- Environment variable override:
  - PIPELINE_TOOL_PROFILES_PATH
  - If set, use that path instead.
- Document this behavior in docs/ARCHITECTURE.md under a new “Tool Profiles & Adapter Layer” subsection.

3) tools.py – TOOL ADAPTER MODULE
Implement src/pipeline/tools.py with:

Core design:

- Data structures
  - A ToolResult class or dict with fields:
    - tool_id
    - command_line (list of strings or a joined string)
    - exit_code
    - stdout
    - stderr
    - timed_out (bool)
    - started_at
    - completed_at
    - duration_sec
    - success (bool)   // derived from exit_code and profile.success_exit_codes

- Public functions:
  - load_tool_profiles() → dict
    - Loads JSON from the resolved path.
    - Validates basic structure; raises clear exceptions on fatal errors.
  - get_tool_profile(tool_id) → dict
    - Convenience wrapper.
  - render_command(tool_id, context) → (cmd_list, env, working_dir, timeout_sec)
    - Applies context substitutions to profile fields.
    - Context may include:
      - "cwd", "repo_root", "ws_id", etc.
      - For now, focus on making {cwd} and {repo_root} available.
  - run_tool(tool_id, context, *, run_id=None, ws_id=None) → ToolResult
    - Main entry point that:
      - Records a “tool_started” event via db.record_event().
      - Builds & runs the command via subprocess.
      - Enforces timeout.
      - Captures stdout/stderr.
      - Determines success/failure.
      - On failure:
        - Records an error via db.record_error() with:
          - step_name = context.get("step_name", tool_id)
          - error_code based on tool type or exit code.
          - signature derived from (tool_id, exit_code, trimmed stderr).
      - Records a “tool_finished” event with summary info.

Implementation details:

- Use Python’s subprocess module (no external libs).
- Handle working directory:
  - If profile.working_dir is a template, substitute context values.
  - If omitted, use the current process working directory.
- Handle environment:
  - Start from os.environ copy and overlay profile.env after template substitution.
- Handle timeout:
  - Use subprocess.run(..., timeout=timeout_sec).
  - If a TimeoutExpired occurs:
    - Set exit_code to a sentinel (e.g., -1).
    - Mark timed_out=True.
    - Record an error with a distinct error_code like "TIMEOUT".
- Ensure run_tool NEVER silently swallows errors; always return a ToolResult and record DB entries when run_id/ws_id are provided.

4) LOGGING & DB INTEGRATION
- tools.py MUST use db.py from PH-02 to record events and errors when run_id/ws_id are provided.
  - `record_event(run_id, ws_id, event_type, payload_json)`
  - `record_error(run_id, ws_id, step_name, error_code, signature, message, context_json)`

- Example event types:
  - "tool_started"
  - "tool_finished"
  - "tool_timeout"
  - "tool_failed"

Payload JSON should be something like:
  - For tool_started:
    { "tool_id": "...", "rendered_command": [...], "profile_type": "..." }
  - For tool_finished:
    { "tool_id": "...", "exit_code": ..., "success": true/false, "duration_sec": ... }
  - For tool_timeout:
    { "tool_id": "...", "timeout_sec": ..., "partial_output": "..." }

Even if run_id/ws_id are None, run_tool should still function (just skip DB calls).

5) UNIT TESTS
- tests/pipeline/test_tools.py
  - Use a temporary tool_profiles JSON file:
    - Point PIPELINE_TOOL_PROFILES_PATH at that file during tests.
  - Tests should cover at least:
    - load_tool_profiles() loads and validates profiles.
    - get_tool_profile("echo") returns expected structure.
    - render_command() performs template substitution ({cwd}, {repo_root}).
    - run_tool("echo", ...) executes successfully and returns ToolResult with success=True.
    - run_tool() handles:
      - Non-zero exit code as failure.
      - Timeout case correctly by setting timed_out=True and marking success=False.
    - When run_id/ws_id are provided:
      - db.record_event and db.record_error are called (or, if you avoid direct call assertions, assert that the events/errors tables have corresponding records).
  - Use the test DB strategy already established in PH-02:
    - Override PIPELINE_DB_PATH to a temp DB for tests.
    - Call db.init_db() before running tool tests.

6) OPTIONAL SMOKE SCRIPT
- scripts/tool_smoke_test.py (optional but helpful)
  - Example usage:
    - python scripts/tool_smoke_test.py --tool echo --message "Hello"
  - Uses run_tool("echo", {"message": ...}) and prints results.

7) DOCUMENTATION
- docs/ARCHITECTURE.md:
  - Add a “Tool Profiles & Adapter Layer” subsection describing:
    - The purpose of config/tool_profiles.json.
    - The existence of src/pipeline/tools.py and run_tool().
    - How tools are categorized (ai, static_check, test, utility).
    - The relationship to DB events/errors.

- docs/PHASE_PLAN.md:
  - Flesh out the PH-03 section with:
    - One paragraph summary of tool profile system.
    - Bullet list of new artifacts:
      - config/tool_profiles.json
      - src/pipeline/tools.py
      - tests/pipeline/test_tools.py
      - (optional) scripts/tool_smoke_test.py

8) GIT COMMIT
- Stage all new/modified files.
- Commit with message:
  - "PH-03: tool profiles and adapter layer"
- Do NOT push (remote management is out of scope).

====================================
CONSTRAINTS & PRINCIPLES
====================================

- Do NOT break or remove outputs from PH-00–PH-02; extend them only.
- tools.py should NOT:
  - Implement prompt logic, Aider-specific contracts, or FIX loops (that’s PH-03.5/PH-06).
  - Access the DB directly for anything beyond events/errors (no schema changes here).
- Use only standard library (json, os, pathlib, subprocess, datetime, typing, etc.).
- Keep configuration-driven behavior:
  - No hardcoded paths to tools; rely on PATH or env overrides plus the config.
- Design for AI-friendliness:
  - Clear function names.
  - Minimal side effects.
  - Good docstrings.

====================================
EXECUTION PLAN (WHAT YOU SHOULD DO)
====================================

You should:

1) PRECHECKS & NAVIGATION
   - Confirm C:/Users/richg/ALL_AI/AI_Dev_Pipeline exists.
   - cd C:/Users/richg/ALL_AI/AI_Dev_Pipeline
   - Confirm src/pipeline/ and docs/ exist; if not, create them and note in docs/PHASE_PLAN.md that earlier phases may not be fully complete.

2) CREATE/UPDATE TOOL PROFILE CONFIG
   - Ensure config/ directory exists.
   - Create config/tool_profiles.json with:
     - At least "echo", "pytest", and a PowerShell/static-check tool profile.
     - Document meaning of each field in a top-level comment (if you use a separate docs section) or in docs/ARCHITECTURE.md.

3) IMPLEMENT tools.py
   - Open src/pipeline/tools.py (it may exist as a stub from PH-01).
   - Implement:
     - load_tool_profiles()
     - get_tool_profile(tool_id)
     - render_command(tool_id, context)
     - run_tool(tool_id, context, run_id=None, ws_id=None)
     - ToolResult (as a dataclass or plain dict with type hints).
   - Import db functions (db.record_event, db.record_error) and call them when run_id/ws_id are provided.

4) ADD TESTS
   - Implement tests/pipeline/test_tools.py.
   - Use pytest fixtures to:
     - Setup a temporary DB (using PIPELINE_DB_PATH + db.init_db()).
     - Setup a temporary tool_profiles JSON file and point PIPELINE_TOOL_PROFILES_PATH to it.
   - Cover the success, failure, and timeout cases.

5) OPTIONAL SMOKE SCRIPT
   - Implement scripts/tool_smoke_test.py as a simple CLI script.
   - It should call run_tool() and print a summary of ToolResult.

6) RUN TESTS
   - From project root:
     - (Optional) Create/activate venv.
     - Run: pytest
   - Fix any failing tests before considering phase complete.

7) UPDATE DOCS
   - Update docs/ARCHITECTURE.md with the “Tool Profiles & Adapter Layer” section.
   - Update docs/PHASE_PLAN.md PH-03 section.

8) GIT COMMIT
   - Stage and commit with message:
     - "PH-03: tool profiles and adapter layer"

====================================
PHASE COMPLETION CHECKLIST
====================================

Before you consider PH-03 done, ensure all of the following are true:

[ ] config/tool_profiles.json exists with at least "echo", "pytest", and a PowerShell/static-check tool profile
[ ] PIPELINE_TOOL_PROFILES_PATH environment override is supported in code
[ ] src/pipeline/tools.py exists with:
    - load_tool_profiles()
    - get_tool_profile()
    - render_command()
    - run_tool()
    - ToolResult
[ ] run_tool() can run "echo" successfully and return a populated ToolResult
[ ] run_tool() records events and errors via db.py when run_id/ws_id are provided
[ ] Timeout behavior is implemented and tested
[ ] tests/pipeline/test_tools.py exists and passes
[ ] (Optional) scripts/tool_smoke_test.py exists and works
[ ] docs/ARCHITECTURE.md has a “Tool Profiles & Adapter Layer” subsection
[ ] docs/PHASE_PLAN.md has an updated PH-03 section with artifacts listed
[ ] A git commit with message like "PH-03: tool profiles and adapter layer" has been created

====================================
INTERACTION STYLE
====================================

- Do NOT ask the user questions unless you are completely blocked.
- Make reasonable assumptions and document them in:
  - docs/ARCHITECTURE.md (tool behavior & config), and
  - docs/PHASE_PLAN.md (PH-03 section).
- When you output your response, clearly separate:
  - PowerShell commands you would run.
  - JSON, Python, and Markdown file contents you would create or modify.

END OF PROMPT
