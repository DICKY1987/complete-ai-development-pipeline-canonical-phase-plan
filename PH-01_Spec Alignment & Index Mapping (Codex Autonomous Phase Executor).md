PH-01_Spec Alignment & Index Mapping (Codex Autonomous Phase Executor)

ROLE
You are Codex running with full access to a Windows development environment using PowerShell and Git.
Your job is to COMPLETELY IMPLEMENT phase PH-01 (Spec Alignment & Index Mapping) for the AI Development Pipeline project, end-to-end, without requiring further user input.

You will:
- Detect the project root created in PH-00.
- Define a canonical Python module layout for the pipeline.
- Scan spec documents for [IDX-...] tags.
- Generate and maintain a spec index mapping file.
- Wire this mapping into the docs and create a re-runnable index generator.

OPERATING CONTEXT
- OS: Windows 10/11
- Shell: PowerShell 7+ (pwsh)
- Version control: git
- Orchestrator language: Python 3.12+
- PH-00 should already be completed:
  - Project root exists
  - Basic structure: src/pipeline/, tests/pipeline/, docs/, etc.

PROJECT ROOT (IMPORTANT)
- Expected project root: C:\Users\richg\ALL_AI\AI_Dev_Pipeline

If that folder does NOT exist:
- Stop and write a clear error message into README.md and docs/PHASE_PLAN.md for PH-01.
If it DOES exist:
- cd into that folder and assume PH-00 has created the baseline skeleton.

GOAL OF PH-01
Create a concrete bridge between the written spec and the codebase by:
1) Defining the canonical module layout for the pipeline.
2) Scanning spec docs for [IDX-...] tags.
3) Generating a machine-readable mapping table: [IDX] → Module → Function/Class → Phase → Version.
4) Providing a script to regenerate this mapping whenever the spec changes.

You are NOT implementing the full pipeline behavior yet; you are setting up the “map” that future phases will follow.

REQUIRED OUTPUTS OF THIS PHASE

By the end of PH-01, the repo MUST have at minimum:

1) SPEC FOLDER & CANONICAL INDEX FILE
- docs/spec/
  - docs/spec/spec_index_map.md          (canonical mapping document)
  - (Optionally) docs/spec/README.md     (short description of spec docs and index generation)

2) CANONICAL MODULE LAYOUT (STUBS OK)
In src/pipeline/ ensure these modules exist (empty or stubbed with docstrings is fine):

- src/pipeline/db.py
- src/pipeline/orchestrator.py
- src/pipeline/tools.py
- src/pipeline/prompts.py
- src/pipeline/worktree.py
- src/pipeline/bundles.py
- src/pipeline/circuit_breakers.py
- src/pipeline/recovery.py
- src/pipeline/scheduler.py
- src/pipeline/executor.py

Each module should at least contain:
- A module-level docstring describing its planned responsibilities.
- A TODO-style comment referencing relevant phases (PH-02–PH-07, etc.).

3) IDX SCANNER & INDEX GENERATOR
- A Python script that can be re-run to rebuild the index from spec files:
  - scripts/generate_spec_index.py
    OR
  - src/pipeline/spec_index.py with a small entry script in scripts/

This script must:
- Recursively scan docs/ (or docs/spec/, if you prefer) for spec files.
- Detect any [IDX-...] tags (e.g., using regex like r"\[IDX-[A-Z0-9\-]+\]").
- Capture:
  - IDX tag (e.g., IDX-DB-SCHEMA-01)
  - File path
  - Line number
  - A short description line/snippet (e.g., the line or heading containing the tag).

4) THE MAPPING FILE
- docs/spec/spec_index_map.md
  - A Markdown table with columns at minimum:
    - IDX
    - Description
    - Source File
    - Line
    - Module
    - FunctionOrClass
    - Phase
    - Version
  - For Module/Function/Phase/Version:
    - You should make reasonable assignments where possible.
    - If you cannot infer, fill with:
      - Module: "TBD"
      - FunctionOrClass: "TBD"
      - Phase: "TBD"
      - Version: "v1.0" as a default, unless the spec explicitly suggests future version (then “v2.0+”).

5) ARCHITECTURE & PHASE PLAN UPDATES
- docs/ARCHITECTURE.md:
  - Add a section “Spec Mapping & IDX Index” that:
    - Explains that docs/spec/spec_index_map.md is the canonical map between the spec and the code.
    - Explains the purpose of scripts/generate_spec_index.py.
- docs/PHASE_PLAN.md:
  - Under the PH-01 heading, describe:
    - The existence of the index map.
    - The presence of the module layout stubs.
    - How the index keeps spec and code aligned.

6) OPTIONAL TESTS
- A small test in tests/pipeline/ (e.g., tests/pipeline/test_spec_index.py) that:
  - Runs the core indexing logic in a dry-run mode.
  - Asserts that:
    - The script finds at least 0 or more IDX tags without crashing.
    - The mapping file exists after generation.

CONSTRAINTS & PRINCIPLES
- DO NOT delete or override anything produced by PH-00 unless necessary; extend or update instead.
- Keep the module layout simple and consistent. If you need additional modules, you may create them but keep the above set as the baseline.
- The index generator must be deterministic: given the same spec files, it produces the same spec_index_map.md content (modulo timestamps if you include them).
- Avoid hardcoding absolute paths inside the Python scripts; use relative paths from the project root.

SPEC DISCOVERY RULES
Because you cannot ask the user where the spec lives, use this heuristic:

1) Look for spec-like files under docs/:
   - Any .md or .txt file under docs/ or docs/spec/ that contains “[IDX-”.
   - These are treated as “spec sources”.

2) If no such files exist:
   - Create docs/spec/spec_index_map.md with:
     - A note that no spec files with IDX tags were found yet.
   - Document this in docs/spec/README.md and docs/PHASE_PLAN.md under PH-01.
   - Still create module stubs and the generator script.
   - In scripts/generate_spec_index.py, handle the “no IDX tags found” case gracefully (no crash).

3) If they do exist:
   - Parse them and fill the mapping table as described.

MODULE RESPONSIBILITY GUIDELINES
When deciding the Module column for each IDX entry, align them with the following responsibilities:

- db.py                 → SQLite schema, state machine, CRUD, migrations.
- orchestrator.py       → run_workstream, run_pipeline, high-level flow.
- tools.py              → tool adapters, invoking external tools, capturing results.
- prompts.py            → prompt templates and context assembly for AI tools.
- worktree.py           → git worktree lifecycle and local repo safety.
- bundles.py            → workstream bundles (load, validate, DAG).
- circuit_breakers.py   → retries, oscillation detection, per-error limits.
- recovery.py           → crash recovery, resume logic, manual recovery commands.
- scheduler.py          → multi-workstream DAG scheduling (sequential).
- executor.py           → parallel execution, workers, resource limits.

You should:
- Map an IDX referring to DB tables or state transitions → db.py.
- IDX about orchestrator main loop → orchestrator.py.
- IDX about prompts or Aider usage → prompts.py/tools.py.
- IDX about worktrees or git safety → worktree.py.
- IDX about bundles and DAG → bundles.py/scheduler.py.
- IDX about circuit breakers → circuit_breakers.py.
- IDX about crash recovery → recovery.py.
- IDX about parallel execution → executor.py.

ASSUMED VERSIONING RULES FOR "Version" COLUMN
- Default to "v1.0" if:
  - The functionality is required for a functioning, single-node orchestrator.
- Use "v2.0+" if:
  - It is clearly performance optimization (e.g., parallel execution).
  - It is explicitly described as advanced, optional, or future enhancement.

EXECUTION PLAN (WHAT YOU SHOULD ACTUALLY DO)

You should:

1) DETECT PROJECT ROOT & PRECHECKS
   - Confirm C:\Users\richg\ALL_AI\AI_Dev_Pipeline exists; if not, treat as error and:
     - Create docs/PHASE_PLAN.md if missing.
     - Add a PH-01 section noting that project root is missing and PH-00 must be completed.
     - Stop further destructive actions.

   - If it exists:
     - cd C:\Users\richg\ALL_AI\AI_Dev_Pipeline
     - Confirm src/pipeline/ and docs/ exist; if missing, create them (but note that PH-00 may not be complete in README.md).

2) ENSURE MODULE LAYOUT
   - For each module listed above, create it if it does not exist.
   - Add a module-level docstring describing responsibilities.
   - Add a comment referencing PH-01 and later phases that will implement functionality.
   - Do NOT implement real logic yet; stubs are acceptable.

3) CREATE docs/spec/ STRUCTURE
   - Ensure docs/spec/ exists.
   - Create docs/spec/README.md with:
     - Brief explanation of spec files.
     - The role of spec_index_map.md.
     - How to run the index generator script.

4) IMPLEMENT INDEX GENERATOR SCRIPT
   - Create scripts/generate_spec_index.py (or use src/pipeline/spec_index.py with a small script wrapper).
   - Behavior:
     - Walk docs/ recursively for .md and .txt.
     - Find lines with “[IDX-”.
     - Extract:
       - IDX tag (e.g. [IDX-DB-SCHEMA-01] → IDX-DB-SCHEMA-01)
       - File path (relative to project root).
       - Line number.
       - Short description:
         - Use the full line with IDX, or
         - The nearest preceding Markdown heading, if available.
     - Build an in-memory list of entries.

   - Next, for each entry:
     - Decide Module/FunctionOrClass/Phase/Version using the rules above.
     - Where uncertain, set these to “TBD” except Version, which can default to "v1.0".

   - Finally:
     - Write docs/spec/spec_index_map.md:
       - Include an auto-generated notice at the top (e.g. “This file is auto-generated by scripts/generate_spec_index.py”).
       - Write a Markdown table with the columns:
         - IDX | Description | Source File | Line | Module | FunctionOrClass | Phase | Version

5) INTEGRATE WITH ARCHITECTURE & PHASE PLAN DOCS
   - Update docs/ARCHITECTURE.md:
     - Add a section “Spec Mapping & IDX Index”.
     - Explain briefly:
       - where spec docs live,
       - how IDX tags are used,
       - how the mapping file connects spec → code.
   - Update docs/PHASE_PLAN.md:
     - Flesh out the PH-01 section with:
       - A short explanation of the index map.
       - The presence of module stubs.
       - A note on scripts/generate_spec_index.py.

6) OPTIONAL TEST
   - Add tests/pipeline/test_spec_index.py:
     - Import the core indexing functionality (from src/pipeline/spec_index.py if you put it there).
     - Run it on docs/ (possibly with a dry-run flag or test mode).
     - Assert that:
       - It returns a list (even if empty).
       - It does not throw exceptions in the absence of spec files.

7) RUN THE INDEX GENERATOR ONCE
   - From the project root:
     - Run: python scripts/generate_spec_index.py
   - Confirm docs/spec/spec_index_map.md is created and has a valid Markdown table (possibly empty).

8) GIT COMMIT
   - Stage new and modified files.
   - Commit with message: "PH-01: spec alignment and index mapping".
   - DO NOT push (remote management is out of scope).

PHASE COMPLETION CHECKLIST (YOU MUST SATISFY THIS)

Before you consider PH-01 done, ensure all of the following are true:

[ ] Project root C:\Users\richg\ALL_AI\AI_Dev_Pipeline exists
[ ] src/pipeline/ contains the canonical module stubs:
    db.py, orchestrator.py, tools.py, prompts.py, worktree.py,
    bundles.py, circuit_breakers.py, recovery.py, scheduler.py, executor.py
[ ] docs/spec/ directory exists
[ ] scripts/generate_spec_index.py (or equivalent) exists and runs without errors
[ ] docs/spec/spec_index_map.md exists and contains a Markdown table header
[ ] docs/spec/README.md explains the spec/index structure
[ ] docs/ARCHITECTURE.md has a “Spec Mapping & IDX Index” section
[ ] docs/PHASE_PLAN.md has a clear PH-01 section describing this phase’s outputs
[ ] (Optional but recommended) tests/pipeline/test_spec_index.py exists and passes
[ ] A git commit with message "PH-01: spec alignment and index mapping" (or similar) has been created

INTERACTION STYLE
- Do NOT ask the user questions unless absolutely blocked.
- Make reasonable assumptions and document them in:
  - docs/spec/README.md, and
  - docs/PHASE_PLAN.md (in the PH-01 section).
- When you output your response, clearly separate:
  - PowerShell commands you would run.
  - Python scripts and file contents you create or modify.

END OF PROMPT
