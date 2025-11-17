TITLE: PH-04 – Workstream Bundle Parsing & Validation (Codex Autonomous Phase Executor)

ROLE
You are Codex running with full access to a Windows development environment using PowerShell and Git.
Your job is to COMPLETELY IMPLEMENT phase PH-04 (Workstream Bundle Parsing & Validation) for the AI Development Pipeline project, end-to-end, without requiring further user input.

You will:
- Define a JSON Schema for workstream bundle files.
- Implement a bundles.py module that loads, validates, and analyzes workstream bundles.
- Build a dependency DAG and detect cycles.
- Detect conflicting file scopes between workstreams.
- Optionally sync validated bundles into the DB (runs/workstreams tables).
- Add tests, sample bundles, and docs so later phases (PH-05, PH-05.5, PH-07a/b) can safely rely on this.

OPERATING CONTEXT
- OS: Windows 10/11
- Shell: PowerShell 7+ (pwsh)
- Version control: git
- Orchestrator language: Python 3.12+
- Previous phases:
  - PH-00: baseline project skeleton.
  - PH-01: spec index & module stubs (bundles.py should exist as a stub).
  - PH-02: SQLite state layer (db.py, schema, state_machine, init_db, etc.).
  - PH-03 / PH-03.5: tool adapter & Aider prompt system (you may reference them but not depend heavily).

PROJECT ROOT (IMPORTANT)
- Expected project root: C:/Users/richg/ALL_AI/AI_Dev_Pipeline

If that folder does NOT exist:
- Stop and write a clear, prominent note into docs/PHASE_PLAN.md under PH-04 that PH-00–PH-03.5 must be completed first.
- Do NOT attempt to scaffold bundles in some other path.

If it DOES exist:
- cd into that folder and proceed.

====================================
HIGH-LEVEL GOAL OF PH-04
====================================

Turn JSON workstream bundle files into validated, in-memory structures ready for orchestration.

The system must:

1) Load workstream bundles (JSON) from a configured directory.
2) Validate them against a formal JSON Schema.
3) Build a dependency DAG (using depends_on).
4) Detect and report cycles in the DAG.
5) Detect overlapping file scopes between workstreams.
6) Optionally, register workstreams into the DB for a given run_id.
7) Provide clear CLI/automation entry points for validation.

You are NOT responsible for executing workstreams in this phase; only for **defining and validating the inputs** the orchestrator will consume.

====================================
REQUIRED OUTPUTS OF THIS PHASE
====================================

By the end of PH-04, the repo MUST have at minimum:

1) WORKSTREAM JSON SCHEMA
- schema/workstream.schema.json
  - Defines the shape of a single workstream bundle (one element of the workstreams set).
  - Required fields (you may refine names but keep these semantics):

    - id                (string)
      - Pattern: "^ws-[a-z0-9-]+$"
      - Unique across all bundles.

    - openspec_change   (string)
      - ID linking to OpenSpec change / requirement.

    - ccpm_issue        (integer or string)
      - ID of related issue (GitHub/CCPM/etc.).

    - gate              (integer)
      - Minimum: 1
      - Represents OpenSpec gate / approval level.

    - files_scope       (array of strings)
      - Each entry: relative path (e.g. "src/module/file.py").
      - Paths treated as canonical POSIX-style or Windows-style relative path (document assumption).

    - files_create      (array of strings, optional)
      - Files that this workstream is allowed to create.

    - tasks             (array of strings)
      - High-level tasks to perform in this workstream.

    - acceptance_tests  (array of strings, optional)
      - Description(s) of acceptance tests or test commands.

    - depends_on        (array of strings, optional)
      - Each string is another workstream id.
      - Must refer only to valid ids.

    - tool              (string)
      - ID of the primary tool to use (e.g., "aider").

    - circuit_breaker   (object, optional)
      - Contains things like:
        - max_attempts
        - max_error_repeats
        - oscillation_threshold

    - metadata          (object, optional)
      - Free-form metadata.

  - The schema must:
    - Mark required vs optional fields.
    - Provide descriptive titles/descriptions to help future agents.

2) BUNDLE DIRECTORY & EXAMPLE BUNDLES
- Default bundle directory:
  - <PROJECT_ROOT>/workstreams/
- Support environment variable override:
  - PIPELINE_WORKSTREAM_DIR
  - If set, use that path instead.

- Provide sample bundles for testing/documentation:
  - workstreams/example_single.json
  - workstreams/example_multi.json

  - example_single.json:
    - A single workstream with no dependencies.
  - example_multi.json:
    - 3–4 workstreams with:
      - One root (no depends_on).
      - Others depending on upstreams.
      - Distinct files_scope but at least one example of overlapping scope for testing detection.

3) bundles.py – BUNDLE LOADING & VALIDATION MODULE
Implement src/pipeline/bundles.py with responsibilities:

Core data structures:

- A WorkstreamBundle type:
  - You can use a @dataclass or a TypedDict; fields should align with the schema.
- A BundleSet or simple list[WorkstreamBundle] as the typical return type.

Core functions (minimum):

1) get_workstream_dir() -> Path
   - Determines the directory to load bundles from:
     - Use PIPELINE_WORKSTREAM_DIR if set.
     - Else default to <PROJECT_ROOT>/workstreams.
   - Ensure directory exists or raise a clear error.

2) load_bundle_file(path: Path) -> dict
   - Reads JSON from a file.
   - Returns a Python dict.

3) validate_bundle_data(data: dict, *, schema: dict=None) -> dict
   - Validates a single bundle dict against workstream.schema.json.
   - Raises a descriptive exception on failure.
   - Returns the validated dict (optionally normalized).

4) load_and_validate_bundles() -> list[WorkstreamBundle]
   - Walks the workstream dir for *.json files.
   - Loads and validates each bundle.
   - Enforces:
     - All ids are unique.
     - All depends_on references are valid (refer to existing ids).
   - Returns list of WorkstreamBundle objects (or dicts) sorted by id (or any deterministic order).

5) build_dependency_graph(bundles: list[WorkstreamBundle]) -> GraphStructure
   - Compute adjacency lists:
     - graph[id] = list of dependent ids (children).
     - reverse_graph[id] = list of prerequisites (parents).
   - Data structure can be:
     - dict[str, list[str]]

6) detect_cycles(graph) -> list[list[str]]
   - Run cycle detection (DFS or Kahn’s algorithm).
   - Return list of cycles:
     - each cycle is a list of ids showing the cycle.
   - If any cycles are detected in load_and_validate_bundles(), raise an error that includes the cycle(s).

7) detect_filescope_overlaps(bundles: list[WorkstreamBundle]) -> dict[str, list[str]]
   - Create a mapping file_path -> list of workstream ids that claim that path in files_scope.
   - Return only entries where more than one workstream claims the same path.
   - For v1:
     - Treat any overlap as a **hard error** by default.
     - Later versions might allow override flags for permitted overlaps.

8) (Optional but helpful) sync_bundles_to_db(run_id, bundles)
   - Use src/pipeline/db.py to:
     - Create workstreams rows for the run.
     - Set initial status to "pending".
     - Store depends_on as JSON.
   - This is not strictly required, but strongly recommended since PH-05 will depend on run/workstreams associations.

Error handling:
- Raise clear, typed exceptions (you may define custom exception classes like BundleValidationError, BundleDependencyError).
- Error messages must be:
  - Specific about which file and id is failing.
  - Include enough detail for AI or humans to fix the bundle.

4) VALIDATION SCRIPT / CLI
- scripts/validate_workstreams.py
  - Python script runnable as:
    - python scripts/validate_workstreams.py
  - Behavior:
    - Imports load_and_validate_bundles(), detect_filescope_overlaps().
    - Runs validation on the current workstreams directory.
    - Prints:
      - Number of bundles found.
      - Any detected cycle(s).
      - Any overlapping file scopes.
      - Success message if everything is valid.

- Optional flags:
  - --run-id to also call sync_bundles_to_db(run_id, bundles) after validation.
  - --json to print machine-readable summary (JSON) for AI tools.

5) UNIT TESTS
- tests/pipeline/test_bundles.py
  - Use a temporary directory for workstreams during tests.
  - Cover at least:

    1) Valid bundles:
       - load_and_validate_bundles() succeeds with well-formed example bundles.
       - No cycles, no overlaps → no errors.

    2) Duplicate id:
       - Two bundles with same id → validation error.

    3) Missing dependency:
       - A depends_on entry referencing a non-existent id → validation error.

    4) Simple cycle:
       - A depends_on B and B depends_on A → cycle detected and error raised.

    5) File scope overlap:
       - Two bundles with the same file in files_scope → overlaps detected and error raised.

    6) Schema validation:
       - Missing required fields (e.g., id or files_scope) produce clear errors.
       - Wrong type (string instead of array for tasks) is caught.

  - Where possible, assert that:
    - Error messages contain the filename and workstream id.
    - detect_filescope_overlaps returns the expected mapping.

6) DOCUMENTATION UPDATES
- docs/ARCHITECTURE.md:
  - Add a “Workstream Bundles & Validation” section describing:
    - The purpose and shape of workstream bundles.
    - The location and role of schema/workstream.schema.json.
    - The loading/validation process in src/pipeline/bundles.py.
    - The existence of scripts/validate_workstreams.py.

- docs/PHASE_PLAN.md:
  - Flesh out the PH-04 section with:
    - A summary of this phase.
    - Bullet list of artifacts:
      - schema/workstream.schema.json
      - src/pipeline/bundles.py
      - workstreams/example_*.json
      - scripts/validate_workstreams.py
      - tests/pipeline/test_bundles.py

7) GIT COMMIT
- Stage all new/modified files.
- Commit with message:
  - "PH-04: workstream bundle parsing and validation"
- Do NOT push (remote management is out of scope).

====================================
CONSTRAINTS & PRINCIPLES
====================================

- Do NOT break or remove outputs from PH-00–PH-03.5; extend them only.
- Keep schema and code **machine-friendly**:
  - Simple field names.
  - No unnecessary nesting.
- Make validation **strict by default**:
  - Unknown fields may be allowed or disallowed, but document the behavior.
- Keep bundle loading deterministic:
  - Sorting by id or filename before building graphs is recommended.
- Avoid external dependencies besides standard library (json, os, pathlib, typing) and jsonschema if you choose to use it:
  - If you add jsonschema, pin it in requirements.txt and ensure tests/CI still pass.

====================================
EXECUTION PLAN (WHAT YOU SHOULD DO)
====================================

You should:

1) PRECHECKS & NAVIGATION
   - Confirm C:/Users/richg/ALL_AI/AI_Dev_Pipeline exists.
   - cd C:/Users/richg/ALL_AI/AI_Dev_Pipeline
   - Confirm src/pipeline/, docs/, schema/ exist; if not, create them and note missing earlier phases in docs/PHASE_PLAN.md.

2) DEFINE WORKSTREAM SCHEMA
   - Create schema/workstream.schema.json with the fields and constraints described above.
   - Ensure schema is self-contained and valid JSON Schema draft-07 (or later).

3) CREATE EXAMPLE BUNDLES
   - Ensure workstreams/ exists.
   - Add example_single.json and example_multi.json illustrating valid structure.
   - Optionally add intentionally invalid examples for tests under a separate test fixture directory (tests/data/workstreams_invalid/).

4) IMPLEMENT bundles.py
   - Open src/pipeline/bundles.py (stub from PH-01).
   - Implement:
     - get_workstream_dir()
     - load_bundle_file(path)
     - validate_bundle_data(...)
     - load_and_validate_bundles()
     - build_dependency_graph(...)
     - detect_cycles(...)
     - detect_filescope_overlaps(...)
     - (optional) sync_bundles_to_db(run_id, bundles)

5) IMPLEMENT VALIDATION SCRIPT
   - Create scripts/validate_workstreams.py.
   - Wire it to:
     - Run load_and_validate_bundles().
     - Run detect_filescope_overlaps().
     - Print a human-readable summary.
     - Exit with non-zero code on validation failure.

6) ADD TESTS
   - Implement tests/pipeline/test_bundles.py.
   - Use test fixtures or dynamically created temp directories for bundle files.
   - Test valid and invalid scenarios as listed.

7) RUN TESTS
   - From project root:
     - Run: pytest
   - Fix any failing tests before considering phase complete.

8) UPDATE DOCS
   - Update docs/ARCHITECTURE.md ("Workstream Bundles & Validation").
   - Update docs/PHASE_PLAN.md PH-04 section.

9) GIT COMMIT
   - Stage and commit with message:
     - "PH-04: workstream bundle parsing and validation"

====================================
PHASE COMPLETION CHECKLIST
====================================

Before you consider PH-04 done, ensure all of the following are true:

[ ] schema/workstream.schema.json exists and defines all core fields and constraints
[ ] workstreams/ directory exists with at least example_single.json and example_multi.json
[ ] src/pipeline/bundles.py exists with:
    - get_workstream_dir()
    - load_bundle_file()
    - validate_bundle_data()
    - load_and_validate_bundles()
    - build_dependency_graph()
    - detect_cycles()
    - detect_filescope_overlaps()
    - (optional) sync_bundles_to_db()
[ ] scripts/validate_workstreams.py exists and validates bundles end-to-end
[ ] tests/pipeline/test_bundles.py exists and covers:
    - valid bundles
    - duplicate ids
    - missing dependency
    - simple cycle
    - file scope overlap
    - schema violations
[ ] pytest passes successfully
[ ] docs/ARCHITECTURE.md has a “Workstream Bundles & Validation” section
[ ] docs/PHASE_PLAN.md has an updated PH-04 section listing artifacts and behavior
[ ] A git commit with message like "PH-04: workstream bundle parsing and validation" has been created

====================================
INTERACTION STYLE
====================================

- Do NOT ask the user questions unless you are completely blocked.
- Make reasonable assumptions and document them in:
  - schema/workstream.schema.json (descriptions)
  - docs/PHASE_PLAN.md (PH-04 section)
- When you output your response, clearly separate:
  - PowerShell commands you would run.
  - JSON, Python, and Markdown file contents you would create or modify.

END OF PROMPT
