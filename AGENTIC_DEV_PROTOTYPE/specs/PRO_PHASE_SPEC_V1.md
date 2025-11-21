# PRO Phase Specification v1.0

**Document ID:** PRO_PHASE_SPEC_V1  
**Version:** 1.0.0  
**Last Updated:** 2025-11-20  
**Status:** Canonical  

---

## PPS-001: Overview {#PPS-001}

This specification defines the **professional mandatory structure** for every development phase executed by autonomous AI in the Game Board Protocol ecosystem.

**Core Principle:** If a phase does not meet this specification, the AI **MUST NOT** execute it.

---

## PPS-002: Phase Identity & Naming {#PPS-002}

Every phase **MUST** have dual identification for human and machine consumption.

### PPS-002.1: Phase ID (Human-Focused) {#PPS-002-1}

- **Format:** Ordered label
- **Examples:** `Phase 0`, `Phase 1A`, `Phase 1B`, `Phase 2`, `Phase 3A`
- **Purpose:** Human-readable ordering and reference

### PPS-002.2: Workstream ID (Machine-Focused) {#PPS-002-2}

- **Pattern:** `ws-{project-key}-{phase-key}-{slug}`
- **Examples:**
  - `ws-pipeline-plus-00-schema`
  - `ws-pipeline-plus-1a-task-queue`
  - `ws-pipeline-plus-1b-audit`
  - `ws-pipeline-plus-02-patch-manager`
- **Requirement:** Globally unique across all workstreams

### PPS-002.3: Binding to Workstream {#PPS-002-3}

Each phase **MUST** be bound to exactly **ONE** primary workstream.

**Canonical Invocation:**
```bash
python scripts/run_workstream.py --ws-id ws-pipeline-plus-1a-task-queue
```

**Rule:** The AI **MUST** treat this command as the **only entrypoint** for that phase.

---

## PPS-003: Mandatory Phase Fields {#PPS-003}

Every phase definition **MUST** contain the following structured fields:

### PPS-003.1: Objective (REQUIRED) {#PPS-003-1}

- **Format:** Single, tight goal (not a shopping list)
- **Requirement:** Must describe outcome in concrete, verifiable terms
- **Example:** `"Implement patch manager module with CRUD operations and tests"`
- **Anti-Pattern:** ❌ `"Create stuff and make it work"`

### PPS-003.2: Workstream ID (REQUIRED) {#PPS-003-2}

- **Pattern:** Must follow `ws-{project}-{phase}-{slug}` format
- **Validation:** Must exist in workstream registry used by orchestrator

### PPS-003.3: File Scope (REQUIRED) {#PPS-003-3}

Must explicitly enumerate:

```yaml
file_scope:
  create:
    - "core/state/task_queue.py"
    - "tests/test_task_queue.py"
  modify:
    - "core/state/__init__.py"
  read_only:
    - "config/router.config.yaml"
    - "schema/migrations/001_add_patches_table.sql"
```

**Restrictions:**
- AI **MUST NOT** create or modify any file outside this scope
- Patch application **MUST** validate diffs touch only `create` or `modify` paths

### PPS-003.4: Programmatic Acceptance Tests (REQUIRED) {#PPS-003-4}

Every phase **MUST** define programmatic tests that prove success:

**Filesystem & Config Checks (PowerShell/Bash):**
- `Test-Path` or equivalent for each required directory/file
- Example verification: `.tasks/*`, `.ledger/patches`, `.runs`, schema migration file

**Behavioral Tests (pytest):**
- Specific test modules for the phase
- Examples: `tests/test_task_queue.py`, `tests/test_audit_logger.py`
- Deterministic invocation:
  ```bash
  python -m pytest -q tests/test_task_queue.py tests/test_audit_logger.py
  ```

**Pass/Fail Rule:**
- If ANY test fails or any required file/dir is missing: **Phase is NOT complete**
- "Done" is defined **ONLY** by all checks passing (e.g., `44/44 tests passed`)
- Never by conversational judgment

### PPS-003.5: Dependencies (REQUIRED) {#PPS-003-5}

Each phase **MUST** declare:

- **must_follow:** Phases that MUST complete successfully first
- **may_run_parallel_with:** Phases that MAY run concurrently

**Canonical Pattern (Default):**
```
Phase 0 (Pre-Flight & Schema)
  ↓
Phase 1A & 1B (parallel: queue + audit)
  ↓
Phase 2 (patch management)
```

---

## PPS-004: Phase Pre-Flight Requirement {#PPS-004}

Every phase **MUST** start with a Pre-Flight block.

### PPS-004.1: Pre-Flight Verification {#PPS-004-1}

Pre-Flight **MUST** verify all prerequisites exist:

- Prior-phase artifacts (dirs, files, config)
- Environment assumptions (tools installed, services reachable)

**Example Pre-Flight Checks:**
```powershell
# WSL + Ollama connectivity check
$wslCheck = wsl --list --verbose | Select-String "Ubuntu.*2"
if (-not $wslCheck) { throw "WSL2 Ubuntu not found" }

$ollamaWin = curl -s http://localhost:11434/api/tags | ConvertFrom-Json
if (-not $ollamaWin.models) { throw "Ollama not responding on Windows" }

$ollamaWSL = wsl -d Ubuntu -- curl -sf http://172.27.16.1:11434/api/tags
if (-not $ollamaWSL) { throw "Ollama not accessible from WSL" }
```

### PPS-004.2: Pre-Flight Failure Response {#PPS-004-2}

If Pre-Flight fails, the phase **MUST NOT** proceed.

The AI **MUST** either:
- Enter a dedicated "repair" phase, **OR**
- Execute documented self-healing actions and re-run Pre-Flight

**Hard Stop Rule:** Pre-Flight failure is a **hard stop** for that phase.

---

## PPS-005: Standard Phase Template {#PPS-005}

All phase specs **MUST** be structurally compatible with this template:

```markdown
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
```

**Self-Healing Rules**:
* If [failure condition] → [automated fix action]
* If [failure condition] → [automated fix action]

**Success Criteria**:
* [Explicit observable state]
* [All tests green, e.g., "44/44 tests passing"]
```

**Final Line Interpretation:**  
"Every claim of success is provable via code, not vibes."

---

## PPS-006: Operator Execution Standard {#PPS-006}

This section defines the **Rules of Engagement** for AI agents. Any AI executing workstreams **MUST** behave as an **operator**, not a free-form code generator.

### PPS-006.1: Rule 1 – CLI-First, Never "Vibes" {#PPS-006-1}

**1.1 CLI as Source of Truth:**

The AI **MUST** treat the CLI as the source of truth. After any operation:
- Run concrete commands (`Get-ChildItem`, `git status`, `pytest`)
- Inspect outputs and logs
- Base decisions **ONLY** on these observations

**1.2 Never Assume Success:**

After running a workstream, tool, or script, the AI **MUST** verify:
- Required directories/files exist
- Tests pass (e.g., `44/44 passed`)
- Git status is clean or matches expected changes

**1.3 Ask the Repo, Don't Hallucinate:**

When uncertain, the AI **MUST**:
- Use `Get-ChildItem`, `ls` to discover actual files
- Use `Get-Content`, `sed/head/tail` to inspect file contents

**FORBIDDEN:** Inferring modules, paths, or directory structures without verifying on disk.

### PPS-006.2: Rule 2 – Self-Healing Execution {#PPS-006-2}

**2.1 Detect Under-Delivery from Tools:**

Example patterns:
- Workstream runs but `.tasks/*` or specified dirs are missing
- Workstream runs but required files (`core/engine/patch_manager.py`) not created

**Response:** AI **MUST**:
- Explicitly check for required artifacts
- Treat missing artifacts as tool failure, not success

**2.2 Repair Environment Directly:**

If Aider/Codex or another tool fails to produce required artifacts, AI **MUST**:
- Generate necessary PowerShell/Bash commands to create directories, `.gitkeep` files
- Write files directly via `New-Item`, `Set-Content`, or `python -c`

**REQUIRED Behavior:** Autonomous repair  
**FORBIDDEN:** Stopping and waiting for human to "fix the tool"

**2.3 Self-Healing Loop:**

For every phase, AI **MUST** implement:

1. Run the planned command(s)
2. Inspect outputs and filesystem
3. If acceptance criteria not met:
   - Apply documented self-healing steps
   - Re-run relevant tests/acceptance checks
4. Only then declare the phase successful

**Non-Negotiable:** "Run → Inspect → Fix → Re-verify" loop

---

## PPS-007: Isolation via Worktrees & Patches {#PPS-007}

### PPS-007.1: Worktree Isolation (MANDATORY) {#PPS-007-1}

Every workstream **MUST** operate in an isolated git worktree.

**Pattern:** `.worktrees/ws-22-*`, `.worktrees/ws-23-*`

**Requirements:**
- AI **MUST** create or use dedicated worktree per workstream
- All edits, tests, and patches **MUST** occur within that worktree

### PPS-007.2: Patch-First Editing (MANDATORY) {#PPS-007-2}

AI **MUST** prefer **small, localized diffs** over whole-file rewrites:
- Edits of the form `(+1 -1)` in files
- All changes **MUST** be captured as unified diff patch files
- Stored in patch ledger: `.ledger/patches/...`

### PPS-007.3: Patch Metadata & Scope Validation {#PPS-007-3}

**Required Metadata:**
- Patch hash (SHA256)
- Timestamp
- Workstream ID
- Files touched
- Scope validation result

**Validation Rules:**
- Patch **MUST** only touch files in declared `create` + `modify` scope
- Files in `read_only` **MUST NOT** appear in patch diff
- Violation → Patch rejected before application

---

## PPS-008: Atomic Execution & Small Phases {#PPS-008}

### PPS-008.1: Phase Atomicity {#PPS-008-1}

**DO:**
- Break work into small, verifiable phases (1-3 modules max per phase)
- Use patch-style minimal diffs (+1/-1 changes)
- Execute one phase completely before moving to next

**DON'T:**
- ❌ Create giant refactors touching 20+ files
- ❌ Spend 80k+ tokens on planning without executing atomic steps
- ❌ Bundle script creation + 4+ docs into one phase
- ❌ Whole-file rewrites when patches will do

### PPS-008.2: Verification Over Confidence {#PPS-008-2}

**Ground Truth Over Vibes:**

**DO:**
- ✅ Always verify with CLI commands (`git status`, `pytest`, `Test-Path`)
- ✅ Base decisions **ONLY** on observable outputs (exit codes, test results)
- ✅ Treat "all tests passed" as the **ONLY** success criterion

**DON'T:**
- ❌ Declare success based on "this looks right"
- ❌ Assume tools did their job without verification
- ❌ Mark phases "complete" without observable test output

---

## PPS-009: Cross-References {#PPS-009}

This specification is part of the Game Board Protocol specification suite:

**Related Specifications:**
- **UPS-*** - Universal Phase Specification (core requirements)
- **DR-DO-*** - Development Rules (DO practices)
- **DR-DONT-*** - Development Rules (DONT anti-patterns)

**Implementation Components:**
- Orchestrator Core (Phase 3B)
- Validation Gateway (Phase 2C)
- Patch Manager (Phase 4A)

---

## PPS-010: Version History {#PPS-010}

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2025-11-20 | Initial machine-readable version with stable IDs | Game Board Protocol |

---

**END OF SPECIFICATION**
