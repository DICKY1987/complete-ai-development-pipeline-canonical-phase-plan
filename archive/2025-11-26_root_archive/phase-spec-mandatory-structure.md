# Document 1: The Universal Phase Specification mandatory structure (“The What”)

This specification defines the **mandatory structure** for every Development Phase executed by an autonomous AI in this ecosystem. If a phase does not meet this specification, the AI MUST NOT execute it.

---

## 1. Phase Identity & Naming

1.1 **Every phase MUST have a unique Phase ID and Workstream ID.**

* **Phase ID**: Human-focused, ordered label:

  * Examples: `Phase 0`, `Phase 1A`, `Phase 1B`, `Phase 2`, `Phase 3A`, etc.
* **Workstream ID**: Machine-focused, globally unique:

  * Pattern:
    `ws-{project-key}-{phase-key}-{slug}`
  * Example:
    `ws-pipeline-plus-00-schema`, `ws-pipeline-plus-1a-task-queue`, `ws-pipeline-plus-1b-audit`, `ws-pipeline-plus-02-patch-manager`. 

1.2 **Each Phase MUST be bound to exactly ONE primary workstream.**

* The canonical invocation MUST be a deterministic command such as:

  ```bash
  python scripts/run_workstream.py --ws-id ws-pipeline-plus-1a-task-queue
  ```

* The AI MUST treat this command as the **only entrypoint** for that phase. 

---

## 2. Mandatory Phase Fields

Every Phase definition MUST contain at least the following fields:

```yaml
phase:
  id: "Phase 1A"
  workstream_id: "ws-pipeline-plus-1a-task-queue"
  objective: "Implement task queue module with enqueue/dequeue, status, and tests."
  file_scope:
    create:
      - "core/state/task_queue.py"
      - "tests/test_task_queue.py"
    modify:
      - "core/state/__init__.py"
    read_only:
      - "config/router.config.yaml"
      - "schema/migrations/001_add_patches_table.sql"
  dependencies:
    must_follow:
      - "Phase 0"
    may_run_parallel_with:
      - "Phase 1B"
  acceptance_tests:
    powershell_block: |
      # PowerShell checks for files/dirs
      # + pytest invocation
    python_block: |
      # Python assertions if needed
```

2.1 **Objective (REQUIRED)**

* MUST be a **single, tight goal**, not a shopping list.
* MUST describe the outcome in concrete, verifiable terms.

  * Example: “Implement patch manager module with CRUD operations and tests.” 

2.2 **Workstream ID (REQUIRED)**

* MUST follow the `ws-{project}-{phase}-{slug}` pattern.
* MUST exist in the workstream registry used by the orchestrator.

2.3 **File Scope (REQUIRED)**

* MUST explicitly enumerate:

  * `create`: files that may be created.
  * `modify`: files that may be edited.
  * `read_only`: files that may be read but not changed.
* The AI MUST NOT create or modify any file **outside** this scope.
* Patch application MUST validate that diffs touch only `create` or `modify` paths. 

2.4 **Programmatic Acceptance Tests (REQUIRED)**

Every Phase MUST define **programmatic tests** that prove success:

* **Filesystem & config checks** (PowerShell/Bash):

  * `Test-Path` or equivalent for each required directory/file.
  * Example: `.tasks/*`, `.ledger/patches`, `.runs`, schema migration file, router config. 

* **Behavioral tests** (usually pytest):

  * Specific test modules for the phase:

    * e.g., `tests/test_task_queue.py`, `tests/test_audit_logger.py`, `tests/test_patch_manager.py`. 
  * MUST be invoked with deterministic commands, e.g.:

    ```bash
    python -m pytest -q tests/test_task_queue.py tests/test_audit_logger.py
    ```

* **Pass/Fail rule**:

  * If ANY test fails or any required file/dir is missing, **the Phase is NOT complete**.
  * “Done” is defined ONLY by all checks passing (e.g., 44/44 tests passed), never by conversational judgment. 

2.5 **Dependencies (REQUIRED)**

* Each Phase MUST declare:

  * `must_follow`: phases that MUST complete successfully first.
  * `may_run_parallel_with`: phases that MAY run concurrently once their prerequisites are satisfied.
* **Canonical pattern** (MUST be the default unless explicitly overridden):

  * Phase 0 (Pre-Flight & Schema setup)
    → Phase 1A & 1B (parallel, e.g., queue + audit)
    → Phase 2 (patch management)
  * Future Phases 3/4 MAY also run in parallel if their dependencies are satisfied. 

---

## 3. Phase Pre-Flight Requirement

3.1 **Every Phase MUST start with a Pre-Flight block.**

* Pre-Flight MUST verify that **all prerequisites for that phase exist**:

  * Prior-phase artifacts (dirs, files, config).
  * Environment assumptions (tools installed, services reachable).
* Example Pre-Flight checks (Phase 0 and ollama-code plan):

  ````powershell
  # Example: WSL + Ollama connectivity for a Phase 0 pre-flight
  $wslCheck = wsl --list --verbose | Select-String "Ubuntu.*2"
  if (-not $wslCheck) { throw "WSL2 Ubuntu not found" }

  $ollamaWin = curl -s http://localhost:11434/api/tags | ConvertFrom-Json
  if (-not $ollamaWin.models) { throw "Ollama not responding on Windows" }

  $ollamaWSL = wsl -d Ubuntu -- curl -sf http://172.27.16.1:11434/api/tags
  if (-not $ollamaWSL) { throw "Ollama not accessible from WSL" }
  ``` :contentReference[oaicite:8]{index=8}  
  ````

3.2 **If Pre-Flight fails, the Phase MUST NOT proceed.**

* The AI MUST treat any Pre-Flight failure as a **hard stop** for that phase.
* The AI MUST either:

  * Enter a dedicated “repair” Phase, OR
  * Execute documented self-healing actions (see Document 2) and re-run Pre-Flight.

---

## 4. Standard Phase Template (Normative)

All Phase specs MUST be structurally compatible with the following template (or a strict superset):

````markdown
### Phase X: [Descriptive Name]

**Objective**: [Single tight goal]

**Workstream**: ws-[project]-[phase]-[slug]

**File Scope**:
- CREATE:
  - [files to create]
- MODIFY:
  - [files to modify]
- READ-ONLY:
  - [files to read only]

**Dependencies**:
- MUST FOLLOW:
  - [phase ids]
- MAY RUN PARALLEL WITH:
  - [phase ids]

**Tasks**:
1. [Specific action]
2. [Specific action]
3. ...

**Implementation Notes** (optional but encouraged):
- [Command or code hints, if helpful]

**Acceptance Tests (Programmatic)**:

```powershell
# Filesystem checks
# Test commands + throws on failure

# Behavior checks (tests)
python -m pytest -q tests/test_*.py
if ($LASTEXITCODE -ne 0) { throw "Tests failed" }
````

**Self-Healing Rules**:

* If [failure condition] → [automated fix action]
* If [failure condition] → [automated fix action]

**Success Criteria**:

* [Explicit observable state]
* [All tests green, e.g., "44/44 tests passing"]

```

- The final line of the Phase spec MUST be interpretable as:  
  **“Every claim of success is provable via code, not vibes.”** :contentReference[oaicite:9]{index=9}  

---

# Document 2: The Operator Execution Standard (“The How”)

This standard defines the **Rules of Engagement** for AI agents. Any AI executing workstreams in this system MUST behave as an **operator**, not a free-form code generator.

---

## Rule 1 – CLI-First, Never “Vibes”

1.1 **The AI MUST treat the CLI as the source of truth.**

- After any operation, the AI MUST:
  - Run concrete commands (e.g., `Get-ChildItem`, `git status`, `pytest`) to observe reality. :contentReference[oaicite:10]{index=10}  
  - Inspect outputs and logs.
  - Base decisions ONLY on these observations.

1.2 **The AI MUST NOT assume success.**

- After running a workstream, tool, or script, the AI MUST verify:
  - Required directories/files exist.
  - Tests pass (e.g., `44/44 passed`).
  - Git status is clean (or matches expected changes). :contentReference[oaicite:11]{index=11}  

1.3 **The AI MUST ask the repo, not hallucinate structure.**

- When uncertain, the AI MUST:
  - Use `Get-ChildItem`, `ls`, or equivalent to discover actual files.
  - Use `Get-Content` or `sed/head/tail` to inspect file contents. :contentReference[oaicite:12]{index=12}  
- It is FORBIDDEN to infer modules, paths, or directory structures without verifying them on disk.

---

## Rule 2 – Self-Healing Execution

2.1 **The AI MUST detect under-delivery from tools.**

- Example pattern:
  - Workstream runs but `.tasks/*` or specified dirs are missing.
  - Workstream runs but `core/engine/patch_manager.py` and `tests/test_patch_manager.py` are not created. :contentReference[oaicite:13]{index=13}  
- In such cases, the AI MUST:
  - Explicitly check for required artifacts.
  - Treat missing artifacts as a tool failure, not as success.

2.2 **The AI MUST repair the environment directly when a tool misses.**

- If Aider/Codex or another CLI tool fails to produce the required artifacts, the AI MUST:
  - Generate the necessary PowerShell/Bash commands to create directories, `.gitkeep` files, migrations, router configs, etc. :contentReference[oaicite:14]{index=14}  
  - Or write files directly (e.g., via `New-Item`, `Set-Content`, or `python -c`).
- This behavior is REQUIRED; it is FORBIDDEN to stop and wait for a human to “fix the tool.”

2.3 **Self-Healing Loop**

For every phase, the AI MUST implement:

1. Run the planned command(s) (workstream, tool, tests).
2. Inspect outputs and filesystem.
3. If acceptance criteria are not met:
   - Apply documented self-healing steps.
   - Re-run relevant tests/acceptance checks.
4. Only then may it declare the Phase successful.

- This “Run → Inspect → Fix → Re-verify” loop is non-negotiable. :contentReference[oaicite:15]{index=15}  

---

## Rule 3 – Isolation via Worktrees & Patch Files

3.1 **Every workstream MUST operate in an isolated git worktree.**

- Pattern:
  - `.worktrees/ws-22-*`, `.worktrees/ws-23-*`, etc. :contentReference[oaicite:16]{index=16}  
- Requirements:
  - The AI MUST create or use a dedicated worktree per workstream.
  - All edits, tests, and patches MUST occur within that worktree.

3.2 **Patch-First Editing is MANDATORY.**

- The AI MUST prefer **small, localized diffs** over whole-file rewrites:
  - Edits of the form `(+1 -1)` in `task_queue.py`, `audit_logger.py`, etc. :contentReference[oaicite:17]{index=17}  
- All changes MUST be captured as unified diff patch files and stored in the patch ledger (e.g., `.ledger/patches/…`). :contentReference[oaicite:18]{index=18}  

3.3 **Patch Metadata & Scope Validation (REQUIRED)**

- For every patch, the AI MUST maintain metadata including:
  - `patch_id`, `task_id`, `workstream_id`, `source_tool`, `files_modified`, `diff_hash`, `validated`, `applied`. :contentReference[oaicite:19]{index=19}  
- Before applying any patch, the AI MUST:
  - Validate that all modified files are within the declared `file_scope`.
  - Reject patches that touch locked/protected areas.
  - Detect oscillation (repeated identical diffs).

3.4 **Task Queue Isolation**

- Tasks MUST be represented as JSON in:
  - `.tasks/inbox/`, `.tasks/running/`, `.tasks/done/`, `.tasks/failed/`. :contentReference[oaicite:20]{index=20}  
- Work on any single task MUST NOT leak outside its assigned worktree or file scope.

---

## Rule 4 – Operator Mindset

4.1 The AI MUST behave like an operator:

- Run commands.
- Inspect outputs.
- Reason about discrepancies vs. spec.
- Fix the environment (files, dirs, tests).
- Re-run checks until the environment matches the spec. :contentReference[oaicite:21]{index=21}  

4.2 The AI MUST NOT:

- Behave as a passive code generator that emits code without running it.
- Declare success based on internal confidence or “this looks right.”
- Ask the user for permission to fix clear, test-detected errors.

---

# Document 3: Validation & Architecture Guardrail (“The Check”)

This document defines the **Ground Truth** and architectural invariants. If these conditions are not met, the AI MUST treat the system as invalid and move into repair mode.

---

## 1. Ground Truth: Tests & Checks, Not Feelings

1.1 **Tests are the sole arbiter of correctness.**

- For each phase, tests MUST:
  - Exist before or be created as part of the phase.
  - Be executable via deterministic CLI commands (e.g., `python -m pytest -q ...`). :contentReference[oaicite:22]{index=22}  
- “Done” is ONLY when:
  - All prescribed tests pass (e.g., `44/44 tests passing`). :contentReference[oaicite:23]{index=23}  
  - All filesystem/config checks succeed.

1.2 **No phase MAY complete without tests.**

- If tests for a given module do not exist, the phase MUST include:
  - Creation of appropriate test modules.
  - Integration of these tests into the test suite.

1.3 **Test Coverage for Core Subsystems**

At minimum, the following MUST be covered:

- Task queue (enqueue/dequeue, status, locking). :contentReference[oaicite:24]{index=24}  
- Audit & telemetry logging.
- Patch manager (conflict detection, stats, multi-file support). :contentReference[oaicite:25]{index=25}  
- Any new tool integration (e.g., ollama-code) must have dedicated tests as part of its plan. :contentReference[oaicite:26]{index=26}  

---

## 2. Standard Directory & Artifact Layout

The repository MUST be “pre-tooled” to reflect the pipeline architecture. The following directories and artifacts are **required**:

2.1 **Queues**

- `.tasks/inbox/` – New tasks as JSON.
- `.tasks/running/` – Tasks being executed.
- `.tasks/done/` – Successfully completed tasks.
- `.tasks/failed/` – Failed tasks. :contentReference[oaicite:27]{index=27}  

2.2 **Patch Ledger**

- `.ledger/patches/` – All patch files for workstreams. :contentReference[oaicite:28]{index=28}  
- Optional but recommended:
  - `.ledger/events/` – High-level workflow events.
  - `.ledger/errors/` – Error logs.

2.3 **Runs & Observability**

- `.runs/` – Execution logs, run IDs, and snapshots. :contentReference[oaicite:29]{index=29}  
- DB or registry (e.g., SQLite) tracking:
  - `runs`, `workstreams`, `steps`, `errors`, `events`. :contentReference[oaicite:30]{index=30}  

2.4 **Schema & Migrations**

- `schema/migrations/001_add_patches_table.sql` (and subsequent migrations). :contentReference[oaicite:31]{index=31}  

2.5 **Router Configuration**

- `config/router.config.yaml` – Routing rules for tools and tasks. :contentReference[oaicite:32]{index=32}  

2.6 **Workstream & Spec Files**

- Centralized WORKSTREAM spec(s) (e.g., `WORKSTREAM_V1.1`) that define tasks, file scope, and tests in a tool-neutral format. :contentReference[oaicite:33]{index=33}  

If any of these core directories or files are missing:

- Phase 0 (“Pre-Flight & Schema Setup”) MUST create them. :contentReference[oaicite:34]{index=34}  
- Subsequent phases MUST fail their Pre-Flight checks until Phase 0 is complete.

---

## 3. Mandatory Validation Workflow per Phase

For every Phase:

3.1 **Pre-Flight Checks**

- Verify presence and structure of:
  - Required directories (`.tasks/*`, `.ledger/patches`, `.runs`, etc.).
  - Required config and schema files.
  - Required tools and CLIs.

3.2 **Execution**

- Run the Phase’s primary command(s) (e.g., `scripts/run_workstream.py` with the correct `--ws-id`).

3.3 **Post-Execution Validation**

- Run:
  - Filesystem checks (PowerShell/Bash).
  - Test suite subset or full suite.
- The Phase MUST NOT be marked `done` until:
  - All checks pass.
  - Git status is clean, or changes are precisely as expected.

3.4 **Recording Outcomes**

- Every completed Phase MUST:
  - Write a record to the DB (`runs`, `workstreams`, `steps`) indicating success/failure. :contentReference[oaicite:35]{index=35}  
  - Optionally, store a patch file capturing the final diff for that Phase.

---

## 4. Parallelism Guardrail

4.1 **Parallel execution is allowed ONLY when dependencies are explicit and satisfied.**

- Example allowed pattern:
  - Phase 0 → Phase 1A & 1B in parallel → Phase 2. :contentReference[oaicite:36]{index=36}  

4.2 **Parallel phases MUST NOT share mutable file scope.**

- If two phases might touch the same files, they MUST:
  - Either run in sequence, OR
  - Use distinct worktrees with later merge logic.

---

# Document 4: Anti-Pattern Blocklist

The following behaviors are strictly prohibited. If an AI attempts any of these, the orchestration layer MUST halt the operation or redirect it into a corrective path.

---

## 1. “Giant Fuzzy Refactors”

**Definition:** Asking the AI to “refactor the whole project” with no phase structure, acceptance tests, or file scope.

- FORBIDDEN:
  - Large, undefined refactors across entire repos.
  - Prompts that lack explicit files, objectives, or tests.
- REQUIRED Alternative:
  - Phase-based, atomic workstreams with tight scope and explicit WS IDs. :contentReference[oaicite:37]{index=37}  

---

## 2. Declaring Success Without Tests

**Definition:** Marking a phase “done” without running tests or acceptance checks.

- FORBIDDEN:
  - Using conversational reasoning (“this looks correct”) as the basis for completion.
  - Skipping pytest or filesystem validation.
- REQUIRED Alternative:
  - Always run programmatic acceptance tests and only accept “all tests green” (e.g., `44/44 tests passed`) as completion. :contentReference[oaicite:38]{index=38}  

---

## 3. Proceeding with a Dirty or Ambiguous Git State

**Definition:** Starting new phases or applying patches when git status is unclear or contains unrelated changes.

- FORBIDDEN:
  - Running workstreams in the main worktree without isolating via worktrees.
  - Applying patches that touch files outside the declared scope.
- REQUIRED Alternative:
  - Always use isolated worktrees per workstream.
  - Always validate patch scope against `file_scope` before applying. :contentReference[oaicite:39]{index=39} :contentReference[oaicite:40]{index=40}  

---

## 4. Whole-File Rewrites When a Patch Will Do

**Definition:** Replacing entire files when only small, localized changes are needed.

- FORBIDDEN:
  - Overwriting large modules for minor fixes.
  - Reformatting entire files without necessity.
- REQUIRED Alternative:
  - Patch-style, minimal diffs (`+1/-1` style changes). :contentReference[oaicite:41]{index=41}  

---

## 5. Trusting Tool Output Without Verification

**Definition:** Assuming that Aider/Codex/ollama-code or any other tool “must have done the work” without checking.

- FORBIDDEN:
  - Assuming directories, files, or modules exist because a tool was told to create them.
  - Skipping checks after tool execution.
- REQUIRED Alternative:
  - Always verify that required artifacts actually exist and pass their tests.
  - If not, invoke self-healing behavior and repair the environment. :contentReference[oaicite:42]{index=42}  

---

## 6. Asking the User for Permission to Fix Clear Failures

**Definition:** Tools asking “should I fix this syntax error/test failure?” instead of just fixing it.

- FORBIDDEN:
  - Prompting the user to approve obvious fixes to failing tests or broken imports.
- REQUIRED Alternative:
  - The AI MUST autonomously:
    - Fix the failure.
    - Re-run tests.
    - Only surface to the user if:
      - Business logic is ambiguous, OR
      - Multiple valid behaviors exist and require domain input.

---

## 7. Editing Outside Declared File Scope

**Definition:** Making changes in files not listed in the Phase’s file scope.

- FORBIDDEN:
  - Touching any file not explicitly named in `create` or `modify`.
- REQUIRED Alternative:
  - Update the Phase spec (and have it re-validated) before expanding scope.
  - Reject or quarantine patches that exceed scope. :contentReference[oaicite:43]{index=43}  

---

## 8. Inventing Architecture On the Fly

**Definition:** Creating new directories, configs, or architectural patterns that contradict the established `.tasks`, `.ledger`, `.runs`, schema, and router structure.

- FORBIDDEN:
  - Ad-hoc addition of new root-level subsystems without updating architecture docs.
- REQUIRED Alternative:
  - Use and extend the **pre-tooled architecture**: queues, ledger, runs, router, schema. :contentReference[oaicite:44]{index=44}  

---

## 9. Over-Broad Parallelism

**Definition:** Running multiple phases in parallel without clear dependency analysis or with overlapping file scope.

- FORBIDDEN:
  - Parallel phases that race over the same files or schema.
- REQUIRED Alternative:
  - Only use parallelism where dependencies allow and scopes don’t intersect:
    - E.g., Phase 0 → Phase 1A & 1B (parallel, non-overlapping) → Phase 2. :contentReference[oaicite:45]{index=45}  

---

## 10. Using the AI as a “Free-Form Code Genie”

**Definition:** Treating the AI as a generic coder instead of an operator over a designed pipeline.

- FORBIDDEN:
  - Ignoring workstreams, tests, task queues, and patch ledgers.
  - Letting the AI freestyle system design without grounding in the repo’s structure.
- REQUIRED Alternative:
  - Treat the **repo + workstreams + tests** as the real prompt.
  - Use the AI as a deterministic operator that drives the CLI, inspects reality, and enforces these guardrails. :contentReference[oaicite:46]{index=46} :contentReference[oaicite:47]{index=47}  

---

These four documents together form the **Protocol of Non-Negotiables**.  
If any of these requirements cannot be satisfied for a given project, the AI MUST NOT proceed with autonomous execution until the deficiencies are corrected.
```
