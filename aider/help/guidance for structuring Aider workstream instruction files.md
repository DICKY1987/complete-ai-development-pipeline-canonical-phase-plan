---
doc_id: DOC-GUIDE-GUIDANCE-FOR-STRUCTURING-AIDER-1110
---

guidance for structuring Aider workstream instruction files 


- Patterns from the Aider repository (README, CONTRIBUTING, issue template conventions, commit examples)  
- Your Codex/Claude phase executor examples (PH-00..PH-03)  
- Provided planning and command‑flow documents (IMP_PLAN, command flows, slash command list, editing principles)  
- General prompt engineering best practices for tool‑driven iterative code agents.  

No new files are being created; this is pure guidance.

----------------------------------------------------------------------
A. Core Purpose of an Aider Workstream Instruction File
----------------------------------------------------------------------
Make each file a single, self‑contained operational contract telling Aider:
1. Role & scope: What this workstream is responsible for and what it must NOT touch.  
2. Inputs & assumptions: Environment, existing repo artifacts, dependency preconditions.  
3. Artifacts & acceptance criteria: Exact files to create/edit, validations, tests.  
4. Step sequence: Ordered atomic actions Aider should perform (each mappable to one /code cycle).  
5. Safety & guardrails: Allowed paths, disallowed edits, rollback conditions.  
6. Command choreography: Which slash commands to use at each step and why.  
7. Determinism requirements: Idempotency, stable naming, reproducible outputs.  
8. Completion checklist + commit message pattern.  

Everything should optimize for minimal ambiguity, tight file scopes, observable success, and low risk of collateral edits.

----------------------------------------------------------------------
B. Recommended Section Order & Canonical Headings
----------------------------------------------------------------------
Use this consistent outline across all workstream instruction files:

1. HEADER SUMMARY  
   - Workstream ID (ws-*)  
   - Phase reference (e.g. PH-02)  
   - Difficulty label (easy|medium|hard)  
   - Version target (v1.0, v2.0+)  
   - Dependencies (list other ws-ids or “None”)  

2. ROLE & OBJECTIVE  
   One concise mission paragraph (no rambling). Ends with: “This file governs only the artifacts listed in Scope.”

3. SCOPE & FILE BOUNDARIES  
   - Writable paths (glob list)  
   - Read-only reference paths (glob list)  
   - Explicit “Out of Scope” bullet list (files or domains to avoid)  
   - Note: All non-listed files must remain unchanged.  

4. ENVIRONMENT & PRECONDITIONS  
   - OS, language versions, required prior phases.  
   - Assumed tools available (e.g. python, pytest, aider installed).  
   - If dependency missing: specify graceful abort instructions (write note to README or log file—not implement substitute logic).  

5. TARGET ARTIFACTS & ACCEPTANCE CRITERIA  
   Each artifact grouped with criteria:  
   - Path  
   - Type (code|config|doc|test|script)  
   - Required contents pattern (docstring, table schema, function signatures, JSON fields)  
   - Validation: tests pass, linter clean, table columns present, etc.  
   - Determinism rules (stable regex output, sorted columns, fixed heading)  

   Format each artifact block as:
   Artifact: src/pipeline/db.py  
   Must Provide: [list]  
   Must Not: [list]  
   Acceptance Tests: [list of test names or commands]

6. OPERATIONS SEQUENCE (Atomic Steps)  
   A numbered list. Each step describes:  
   - Intent (create/edit/validate)  
   - Files to /add or /read-only  
   - Slash command to invoke (/architect for design, /code for edits, /diff, /lint, /test, /commit)  
   - Expected outcome (diff features)  
   - Commit message template  
   Keep steps ≤ 12 lines each. Reference acceptance criteria tags.  
   Use verbs: “Design”, “Implement”, “Refine”, “Test”, “Commit”.  

7. SLASH COMMAND PLAYBOOK (Condensed)  
   Tabular quick‑reference mapping specific actions to commands:  
   - Design high-level module changes → /architect with acceptance criteria block  
   - Implement code changes → /code with only in-scope files added  
   - Inspect changes → /diff  
   - Lint/fix in-scope Python → /lint  
   - Run tests → /test pytest -q  
   - Abort or rollback last commit → /undo (if wrong scope)  
   - Add reference only → /read-only path  

8. PROMPT TEMPLATES FOR THIS WORKSTREAM  
   Provide 2–3 reusable mini prompt frames Aider can copy into /code or /architect:  
   - “Design Phase Prompt”  
   - “Implementation Prompt”  
   - “Test & Validation Prompt”  
   These templates must embed acceptance criteria verbatim and enumerate constraints (no extraneous file edits).  

9. SAFETY & GUARDRAILS  
   - Path allowlist enforcement: only touches globs under Scope.  
   - No edits to dependencies or shared invariants (list them).  
   - Fail-fast rule: if required prior artifact missing, write note in designated log file and stop.  
   - Scope violation response: /undo and restate constraints.  
   - Rollback triggers (test failure, diff includes out-of-scope file, linter introduces new errors).  

10. DETERMINISM & REPRODUCIBILITY RULES  
    - Stable ordering (e.g., sort Markdown tables by key).  
    - Timestamp policy (avoid or isolate).  
    - Error signatures normalization (strip volatile tokens).  
    - Idempotent reruns produce identical diffs unless acceptance criteria expanded.  

11. TEST & VALIDATION MATRIX  
    Table: Row per acceptance criterion → columns: “Criterion”, “Verification Command”, “Artifacts”, “Failure Handling”.  
    Failure handling must direct Aider to: /test, analyze output, apply minimal fix, re-run /test, then /commit.  

12. COMPLETION CHECKLIST  
    - Re-list all acceptance bullets with [ ] checkboxes.  
    - Add final commit message pattern (Conventional Commits + ws-id).  
    - Confirmation action: produce summary diff & ensure no extraneous files changed.  

13. APPENDIX (Optional)  
    - Reference to bigger architecture (phase mapping, IDX tags mapping logic).  
    - Crosswalk table translating Codex/Claude style fields → Aider equivalents (see section F below).  
    Keep appendix purely referential; no new tasks.

----------------------------------------------------------------------
C. Wording Guidelines for Reliable Interpretation
----------------------------------------------------------------------
1. Use imperative, single-action verbs (“Create”, “Add docstring”, “Implement function validate_state_transition”).  
2. Avoid chaining: one sentence per required behavior.  
3. Always specify file path first, then the required change.  
4. For code requirements, list required identifiers explicitly. Example: “Add functions: get_connection(), init_db(), create_run(), update_run_status().”  
5. Include acceptance criteria verbatim close to prompts; repetition aids model retention.  
6. Negative constraints explicit: “Do NOT modify any file outside src/pipeline/db.py, tests/pipeline/test_db_state.py.”  
7. Use stable tokens for cross-referencing (e.g., IDX tags, ws-id) rather than pronouns.  
8. Avoid ambiguous adjectives (“simple”, “clean”)—replace with measurable conditions (“≤ 120 lines”, “no TODO left”, “flake8 passes”).  
9. Put lists before actions in prompts: Aider responds better when scope is enumerated prior to instructions.  

----------------------------------------------------------------------
D. Translating Codex/Claude Phase Files to Aider Format
----------------------------------------------------------------------
Codex/Claude structure (Role, Operating Context, Goals, Required Outputs, Execution Plan) → Aider optimized mapping:

| Original Element | Aider Workstream Section |
|------------------|--------------------------|
| ROLE | Role & Objective (Section 2) |
| OPERATING CONTEXT | Environment & Preconditions (Section 4) |
| GOAL / REQUIRED OUTPUTS | Target Artifacts & Acceptance Criteria (Section 5) |
| EXECUTION PLAN steps | Operations Sequence (Section 6) |
| CONSTRAINTS & PRINCIPLES | Safety & Guardrails + Determinism (Sections 9–10) |
| COMPLETION CHECKLIST | Completion Checklist (Section 12) |
| Interaction Style | Wording Guidelines + Slash Command Playbook (Sections 3, 7, C) |

Condense verbose narrative into crisp enumerated artifacts and testable statements. Remove broad prose that doesn’t change execution logic. Replace long contextual paragraphs with bullet constraints.

----------------------------------------------------------------------
E. Command Formatting & Metadata Conventions
----------------------------------------------------------------------
- Use a “Command Intent Block” preceding each slash command reference:

Example:
Intent: Implement CRUD methods
Files: /add src/pipeline/db.py
Command: /code
Constraints: Only add functions listed; keep existing docstring; no external imports beyond sqlite3, typing, datetime.

- Show commit messages inline after each operation:
Commit: feat(ws-ph02-crud): implement CRUD operations (create_run, update_run_status, etc.)

- Metadata keys recommended within file for machine parsing (optional JSON front-matter or fenced block):
```
---
workstream_id: ws-ph02-crud
phase: PH-02
difficulty: medium
version_target: v1.0
depends_on: [ws-ph02-db-core]
writable_globs: ["src/pipeline/db.py", "tests/pipeline/test_db_state.py"]
readonly_globs: ["schema/schema.sql"]
---
```
Keep front-matter minimal, flat, and stable.

----------------------------------------------------------------------
F. Crosswalk Examples (Codex/Claude → Aider Terms)
----------------------------------------------------------------------
- “Dependencies” → “depends_on” list at top + guard in Preconditions.  
- “Module-level docstring responsibilities” → Acceptance Criteria “Must Provide: module docstring summarizing responsibilities”.  
- “Deterministic script” → Determinism rule: sorted output, stable headers, no timestamp except in comment.  
- “If no spec files exist, create empty mapping file” → Step with conditional abort producing placeholder, no crash.  
- “State machine transitions enforcement” → Artifact criteria enumerating allowed transitions table + test names verifying them.  

----------------------------------------------------------------------
G. Common Pitfalls Writing for Aider & Avoidance Strategies
----------------------------------------------------------------------
1. Overly broad scope (“update database module”) → Always enumerate exact function names, docstring changes, paths.  
2. Hidden multi-file edits → Provide explicit file path lists; use ‘Out of Scope’ section to block uncertain files.  
3. Ambiguous success metrics → Convert to testable commands (pytest -q, flake8, regex search).  
4. Non-deterministic outputs (ordering varies) → Specify stable sort rules, exclude timestamps or mark them with <!-- dynamic --> comment.  
5. Prompt drift when large context pasted → Segment instructions: design vs implement vs test.  
6. Missing negative constraints → Add “Must Not” for each artifact (eg: “Must Not: introduce network calls; add third-party dependency”).  
7. Unclear rollback → Provide /undo usage and postcondition re-check policy.  
8. Incomplete acceptance reproduction → Mirror each acceptance item in both artifact block and final checklist.  
9. Unscoped edit due to missing /add → Always instruct to /add only the file(s) before requesting changes.  
10. Mixing design & implementation in one step → Use /architect for design exploration separate from /code application.

----------------------------------------------------------------------
H. Recommended Formatting Patterns
----------------------------------------------------------------------
Use consistent block labeling to help the model parse:

Artifact Block:
[ARTIFACT] src/pipeline/tools.py
Type: code
Purpose: Tool adapter layer
Must Provide:
- Dataclass ToolResult(fields: tool_id, command_line, exit_code, stdout, stderr, timed_out, started_at, completed_at, duration_sec, success)
- Functions: load_tool_profiles(), get_tool_profile(), render_command(), run_tool()
Must Not:
- Add network calls
- Modify DB schema
Acceptance:
- Tests pass: tests/pipeline/test_tools.py::test_run_tool_echo
- Lint passes: /lint
Determinism:
- Results reproducible for echo command (same exit_code and normalized stdout)

Operation Step Format:
Step 3: Implement run_tool core
Add: /add src/pipeline/tools.py
Command: /code (include acceptance criteria block below)
Expected Diff: Adds ToolResult dataclass & run_tool() the only new functions
Commit: feat(ws-ph03-adapter-core): implement run_tool abstraction

Prompt Template (Implementation):
Prompt:
Implement ToolResult and run_tool() per acceptance criteria:
Acceptance Criteria:
- Dataclass with required fields (see list)
- run_tool executes command, captures output, sets success based on success_exit_codes
- No DB integration yet
Constraints:
- Only edit src/pipeline/tools.py
- No new imports beyond: dataclasses, subprocess, datetime, typing, os, json
Return summary of new functions.
End Prompt.

----------------------------------------------------------------------
I. File-Editing Guidance Patterns
----------------------------------------------------------------------
For multi-pass implementations:
1. Pass 1 (/architect): propose function signatures & error handling strategy.  
2. Pass 2 (/code): create skeleton functions with docstrings only.  
3. Pass 3 (/code): fill logic for each function; run /diff, /lint, /test.  
4. Pass 4 (/code): refine edge cases (timeouts, non-zero exit) limited to diff blocks.  
5. Pass 5 (/test): run tests; if failing, targeted patch steps referencing the failing test name.

Always restrict each patch to one conceptual change cluster (eg: “timeout handling”) to keep diffs minimal and reviewable.

----------------------------------------------------------------------
J. Git & Commit Conventions for Aider Context
----------------------------------------------------------------------
- Conventional Commits + scope: feat(ws-id): short imperative  
- Use consistent prefixes for categories: feat|fix|test|docs|chore|refactor  
- Avoid chaining multiple artifact creations in one commit—prefer 1–2 related files per commit.  
- Include ws-id for traceability.  

----------------------------------------------------------------------
K. Incorporating GitHub Repo Insights
----------------------------------------------------------------------
Observed in Aider repo (README, CONTRIBUTING, HISTORY, recent commits):
- Preference for concise commit messages with actionable verbs.  
- Extensive CHANGELOG: supports deterministic artifacts and version bump workflow.  
- Pre-commit hooks (.pre-commit-config.yaml) emphasize style & linting—include step to optionally run /run pre-commit (if integrated locally).  
- Issue template uses structured fields (summary, steps, expected vs actual). Mirror this structure inside acceptance criteria to reduce ambiguity.  
- Tests directory separated by feature modules—keep new tests under same hierarchical pattern for discoverability.  
- Frequent small commits vs large multi-file changes. Emulate by subdividing operations.

Actionable Integration:
- Mandate running /lint after each code creation step to align with repo’s lint culture.  
- Provide optional step for adding HISTORY.md entry only when feature-level change occurs (skip for stubs).  
- Encourage marking unstable or dynamic blocks with comments (repo often uses explicit docstrings & comments for clarity).  

----------------------------------------------------------------------
L. Example Condensed Skeleton (GUIDELINE ONLY, NOT A WORKSTREAM FILE)
----------------------------------------------------------------------
HEADER SUMMARY  
workstream_id: ws-ph02-state-machine | phase: PH-02 | difficulty: hard | version: v1.0 | depends_on: [ws-ph02-db-core]

ROLE & OBJECTIVE  
Implement formal run/workstream state machine and enforce transitions in db layer without modifying schema or unrelated modules.

SCOPE & FILE BOUNDARIES  
Writable: ["src/pipeline/db.py", "tests/pipeline/test_db_state.py"]  
Read-only: ["schema/schema.sql"]  
Out of Scope: orchestrator logic, tools adapter, prompts, adding new tables.

(… continue with remaining sections per template …)

This example should NOT be used verbatim—adapt per workstream.

----------------------------------------------------------------------
M. Quality Assurance Checklist for Every Instruction File
----------------------------------------------------------------------
Before finalizing each workstream instruction file:
- Section order matches template A–L (or justified deviations).  
- Every acceptance criterion ties to a verification command.  
- No unresolved ambiguous terms (“optimize”, “clean”).  
- Negative constraints present for each artifact.  
- Dependencies clearly enumerated with conditional abort instructions.  
- Prompt templates embed acceptance criteria and constraints.  
- Determinism rules explicitly stated (sorting, stable IDs, no random seeds).  
- Completion checklist mirrors artifact acceptance list 1:1.  

----------------------------------------------------------------------
N. Summary of “Do” vs “Do Not”
Do:
- Enumerate explicit functions, file paths, tests, commands.
- Separate design vs implementation steps.
- Include rollback & abort logic.
- Use stable tokens (ws-id, function names).
- Provide clear negative constraints.

Do Not:
- Generate broad narrative instructions without measurable outputs.
- Combine unrelated artifact changes into one step.
- Omit file path when requesting edit.
- Rely on implicit repository conventions; restate critical ones.
- Introduce dependencies or tools not listed in environment section.

----------------------------------------------------------------------
O. Next Steps (If You Expand)
- Build a meta validator script to parse front-matter and ensure each required section present (optional).  
- Introduce IDX tag references in artifacts (IDX-DB-SCHEMA-01 → db.py responsibilities) for traceability in larger spec mapping.  
- Provide a global “workstream index” doc listing all ws-ids, phases, and cross-file dependencies (Aider can use /read-only).  

----------------------------------------------------------------------

End of guidance. Let me know if you want:
- A templated front-matter block
- A validator schema (YAML/JSON) for instruction files
- Automated conversion examples from existing Codex/Claude prompts.