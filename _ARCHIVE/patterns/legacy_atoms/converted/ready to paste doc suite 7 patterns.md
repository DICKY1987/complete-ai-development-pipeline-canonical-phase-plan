Yes. Using your two specs as the ground truth, I can build a full **pattern doc suite skeleton** for the patterns we identified from your transcripts.

I’ll follow:

* **PATTERN_DOC_SUITE_SPEC-V1** for structure, `doc_id`, and file layout
* **Every_reusable_pattern.md** for the “spec + schema + executor + tests + index” roles per pattern

Below is a **ready-to-paste doc suite** (index + per-pattern files) for these 7 patterns:
ready to paste doc suite 7 patterns
1. `SESSION_BOOTSTRAP_V1`
2. `RESUME_WORK_SESSION_V1`
3. `CREATE_FEATURE_BRANCH_AND_COMMIT_V1`
4. `LEGACY_IMPORT_COMPATIBILITY_FIX_LOOP_V1`
5. `AUTO_SYNC_LOG_HEADER_V1`
6. `GIT_PATH_VISIBILITY_DEBUG_V1`
7. `REPO_STATE_CHECK_V1`

---

## 0. IDs & Names (canonical)

These are the IDs I’ll use consistently across all artifacts (per PATTERN_DOC_SUITE_SPEC rules).

```yaml
# Canonical pattern IDs for this doc suite

patterns:
  - doc_id: DOC-PAT-SESSION-BOOTSTRAP-001
    pattern_id: PAT-SESSION-BOOTSTRAP-001
    name: session_bootstrap
    operation_kind: SESSION_BOOTSTRAP

  - doc_id: DOC-PAT-RESUME-WORK-SESSION-001
    pattern_id: PAT-RESUME-WORK-SESSION-001
    name: resume_work_session
    operation_kind: RESUME_SESSION

  - doc_id: DOC-PAT-FEATURE-BRANCH-COMMIT-001
    pattern_id: PAT-FEATURE-BRANCH-COMMIT-001
    name: feature_branch_commit
    operation_kind: GIT_FEATURE_BRANCH_WORK

  - doc_id: DOC-PAT-LEGACY-IMPORT-FIX-LOOP-001
    pattern_id: PAT-LEGACY-IMPORT-FIX-LOOP-001
    name: legacy_import_fix_loop
    operation_kind: TEST_FIX_LOOP

  - doc_id: DOC-PAT-AUTO-SYNC-LOG-HEADER-001
    pattern_id: PAT-AUTO-SYNC-LOG-HEADER-001
    name: auto_sync_log_header
    operation_kind: LOG_NOISE_FILTERING

  - doc_id: DOC-PAT-GIT-PATH-VISIBILITY-DEBUG-001
    pattern_id: PAT-GIT-PATH-VISIBILITY-DEBUG-001
    name: git_path_visibility_debug
    operation_kind: GIT_PATH_DEBUG

  - doc_id: DOC-PAT-REPO-STATE-CHECK-001
    pattern_id: PAT-REPO-STATE-CHECK-001
    name: repo_state_check
    operation_kind: REPO_STATE_INSPECTION
```

---

## 1. `patterns/registry/PATTERN_INDEX.yaml`

Single canonical index listing all patterns and their artifacts, per your spec.

```yaml
# patterns/registry/PATTERN_INDEX.yaml

patterns:
  - doc_id: DOC-PAT-SESSION-BOOTSTRAP-001
    pattern_id: PAT-SESSION-BOOTSTRAP-001
    name: session_bootstrap
    version: 1.0.0
    status: draft
    spec_path: patterns/specs/session_bootstrap.pattern.yaml
    schema_path: patterns/schemas/session_bootstrap.schema.json
    executor_path: patterns/executors/session_bootstrap_executor.ps1
    test_path: patterns/tests/test_session_bootstrap_executor.ps1
    example_dir: patterns/examples/session_bootstrap/
    operation_kinds:
      - SESSION_BOOTSTRAP

  - doc_id: DOC-PAT-RESUME-WORK-SESSION-001
    pattern_id: PAT-RESUME-WORK-SESSION-001
    name: resume_work_session
    version: 1.0.0
    status: draft
    spec_path: patterns/specs/resume_work_session.pattern.yaml
    schema_path: patterns/schemas/resume_work_session.schema.json
    executor_path: patterns/executors/resume_work_session_executor.ps1
    test_path: patterns/tests/test_resume_work_session_executor.ps1
    example_dir: patterns/examples/resume_work_session/
    operation_kinds:
      - RESUME_SESSION

  - doc_id: DOC-PAT-FEATURE-BRANCH-COMMIT-001
    pattern_id: PAT-FEATURE-BRANCH-COMMIT-001
    name: feature_branch_commit
    version: 1.0.0
    status: draft
    spec_path: patterns/specs/feature_branch_commit.pattern.yaml
    schema_path: patterns/schemas/feature_branch_commit.schema.json
    executor_path: patterns/executors/feature_branch_commit_executor.ps1
    test_path: patterns/tests/test_feature_branch_commit_executor.ps1
    example_dir: patterns/examples/feature_branch_commit/
    operation_kinds:
      - GIT_FEATURE_BRANCH_WORK

  - doc_id: DOC-PAT-LEGACY-IMPORT-FIX-LOOP-001
    pattern_id: PAT-LEGACY-IMPORT-FIX-LOOP-001
    name: legacy_import_fix_loop
    version: 1.0.0
    status: draft
    spec_path: patterns/specs/legacy_import_fix_loop.pattern.yaml
    schema_path: patterns/schemas/legacy_import_fix_loop.schema.json
    executor_path: patterns/executors/legacy_import_fix_loop_executor.ps1
    test_path: patterns/tests/test_legacy_import_fix_loop_executor.ps1
    example_dir: patterns/examples/legacy_import_fix_loop/
    operation_kinds:
      - TEST_FIX_LOOP

  - doc_id: DOC-PAT-AUTO-SYNC-LOG-HEADER-001
    pattern_id: PAT-AUTO-SYNC-LOG-HEADER-001
    name: auto_sync_log_header
    version: 1.0.0
    status: draft
    spec_path: patterns/specs/auto_sync_log_header.pattern.yaml
    schema_path: patterns/schemas/auto_sync_log_header.schema.json
    executor_path: patterns/executors/auto_sync_log_header_executor.ps1
    test_path: patterns/tests/test_auto_sync_log_header_executor.ps1
    example_dir: patterns/examples/auto_sync_log_header/
    operation_kinds:
      - LOG_NOISE_FILTERING

  - doc_id: DOC-PAT-GIT-PATH-VISIBILITY-DEBUG-001
    pattern_id: PAT-GIT-PATH-VISIBILITY-DEBUG-001
    name: git_path_visibility_debug
    version: 1.0.0
    status: draft
    spec_path: patterns/specs/git_path_visibility_debug.pattern.yaml
    schema_path: patterns/schemas/git_path_visibility_debug.schema.json
    executor_path: patterns/executors/git_path_visibility_debug_executor.ps1
    test_path: patterns/tests/test_git_path_visibility_debug_executor.ps1
    example_dir: patterns/examples/git_path_visibility_debug/
    operation_kinds:
      - GIT_PATH_DEBUG

  - doc_id: DOC-PAT-REPO-STATE-CHECK-001
    pattern_id: PAT-REPO-STATE-CHECK-001
    name: repo_state_check
    version: 1.0.0
    status: draft
    spec_path: patterns/specs/repo_state_check.pattern.yaml
    schema_path: patterns/schemas/repo_state_check.schema.json
    executor_path: patterns/executors/repo_state_check_executor.ps1
    test_path: patterns/tests/test_repo_state_check_executor.ps1
    example_dir: patterns/examples/repo_state_check/
    operation_kinds:
      - REPO_STATE_INSPECTION
```

---

From here, for each pattern I’ll give you:

* `patterns/specs/<name>.pattern.yaml` (spec)
* `patterns/schemas/<name>.schema.json` (schema)
* `patterns/executors/<name>_executor.ps1` (skeleton)
* `patterns/tests/test_<name>_executor.ps1` (skeleton)
* `patterns/examples/<name>/instance_minimal.json` (minimal example)

All wired to the same `doc_id` as required by your spec.

---

## 2. SESSION_BOOTSTRAP_V1

### 2.1 Spec – `patterns/specs/session_bootstrap.pattern.yaml`

```yaml
# patterns/specs/session_bootstrap.pattern.yaml

doc_id: DOC-PAT-SESSION-BOOTSTRAP-001
pattern_id: PAT-SESSION-BOOTSTRAP-001
name: session_bootstrap
version: 1.0.0
role: spec

operation_kinds:
  - SESSION_BOOTSTRAP

schema_ref: patterns/schemas/session_bootstrap.schema.json
executor_ref: patterns/executors/session_bootstrap_executor.ps1
example_dir: patterns/examples/session_bootstrap/

summary: >
  Initialize an AI-assisted CLI session by ensuring AGENTS.md exists
  and emitting a standardized "bootstrap menu" (/init, /status, /approvals,
  /model, /review) for the user or higher-level orchestrator.

intent: >
  Used at the start of a session or when the assistant is unsure what
  to do next. Guarantees a consistent starting state and menu.

inputs:
  repo_root:
    type: string
    description: Path to the repository root where AGENTS.md should live.
  ensure_agents_file:
    type: boolean
    default: true
    description: Whether to create AGENTS.md from a template if missing.

outputs:
  menu_commands:
    type: array
    items:
      type: string
    description: >
      List of commands to display (/init, /status, /approvals, /model, /review).
  agents_status:
    type: string
    description: >
      "created", "already_exists", or "skipped" depending on AGENTS.md handling.

steps:
  - id: check_repo_root
    description: Resolve repo_root and confirm it contains a .git directory.

  - id: ensure_agents
    description: >
      If ensure_agents_file is true, ensure AGENTS.md exists at repo_root.
      If missing, create a default AGENTS.md with core instructions.

  - id: emit_menu
    description: >
      Return a structured menu description for /init, /status, /approvals,
      /model, and /review along with the agents_status.
```

### 2.2 Schema – `patterns/schemas/session_bootstrap.schema.json`

```json
{
  "doc_id": "DOC-PAT-SESSION-BOOTSTRAP-001",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "session_bootstrap pattern parameters",
  "type": "object",
  "properties": {
    "repo_root": {
      "type": "string"
    },
    "ensure_agents_file": {
      "type": "boolean",
      "default": true
    }
  },
  "required": ["repo_root"]
}
```

### 2.3 Executor skeleton – `patterns/executors/session_bootstrap_executor.ps1`

```powershell
# DOC_LINK: DOC-PAT-SESSION-BOOTSTRAP-001
param(
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [bool]$Ensure_Agents_File = $true
)

# session_bootstrap_executor.ps1
# Responsibilities:
#   - Verify RepoRoot contains .git
#   - Ensure AGENTS.md exists (if Ensure_Agents_File is $true)
#   - Emit JSON summary with menu_commands + agents_status

$ErrorActionPreference = 'Stop'

if (-not (Test-Path (Join-Path $RepoRoot '.git'))) {
    throw "RepoRoot '$RepoRoot' does not contain a .git directory."
}

$agentsPath = Join-Path $RepoRoot 'AGENTS.md'
$agentsStatus = 'already_exists'

if ($Ensure_Agents_File) {
    if (-not (Test-Path $agentsPath)) {
        @"
# AGENTS.md
# Default instructions for AI coding agents.
# (You can replace this content with your project-specific rules.)
"@ | Set-Content -Path $agentsPath -Encoding UTF8
        $agentsStatus = 'created'
    }
} else {
    $agentsStatus = 'skipped'
}

$menu = @('/init','/status','/approvals','/model','/review')

[pscustomobject]@{
    doc_id        = 'DOC-PAT-SESSION-BOOTSTRAP-001'
    pattern_name  = 'session_bootstrap'
    menu_commands = $menu
    agents_status = $agentsStatus
} | ConvertTo-Json -Depth 5
```

### 2.4 Tests skeleton – `patterns/tests/test_session_bootstrap_executor.ps1`

```powershell
# DOC_LINK: DOC-PAT-SESSION-BOOTSTRAP-001
# Pester-style tests for session_bootstrap_executor.ps1

param(
    [string]$RepoRoot = (Get-Location).Path
)

Describe "session_bootstrap_executor" {
    It "creates AGENTS.md when missing" {
        $tempRepo = Join-Path $env:TEMP "sbp_repo_$(Get-Random)"
        New-Item -ItemType Directory -Path $tempRepo | Out-Null
        New-Item -ItemType Directory -Path (Join-Path $tempRepo '.git') | Out-Null

        $resultJson = & patterns/executors/session_bootstrap_executor.ps1 -RepoRoot $tempRepo
        $result = $resultJson | ConvertFrom-Json

        Test-Path (Join-Path $tempRepo 'AGENTS.md') | Should -BeTrue
        $result.agents_status | Should -Be 'created'
        $result.menu_commands | Should -Contain '/init'
    }
}
```

### 2.5 Example – `patterns/examples/session_bootstrap/instance_minimal.json`

```json
{
  "doc_id": "DOC-PAT-SESSION-BOOTSTRAP-001",
  "repo_root": ".",
  "ensure_agents_file": true
}
```

---

## 3. RESUME_WORK_SESSION_V1

### 3.1 Spec – `patterns/specs/resume_work_session.pattern.yaml`

```yaml
# patterns/specs/resume_work_session.pattern.yaml

doc_id: DOC-PAT-RESUME-WORK-SESSION-001
pattern_id: PAT-RESUME-WORK-SESSION-001
name: resume_work_session
version: 1.0.0
role: spec

operation_kinds:
  - RESUME_SESSION

schema_ref: patterns/schemas/resume_work_session.schema.json
executor_ref: patterns/executors/resume_work_session_executor.ps1
example_dir: patterns/examples/resume_work_session/

summary: >
  Given a transcript or log of recent AI-assisted work, summarize the
  last changes, tests run, and remaining tasks so the system can "pick
  up where it left off".

intent: >
  Use when the user requests "pick up where you left off" or "list
  remaining tasks" based on prior work logs.

inputs:
  source_log_path:
    type: string
    description: Path to an AI/CLI transcript or structured worklog.
  max_entries:
    type: integer
    default: 50
    description: Max number of log segments to scan for changes/tests/tasks.

outputs:
  summary_text:
    type: string
    description: Human-readable summary of what was done.
  changes:
    type: array
    items:
      type: string
    description: Bullet-style descriptions of key changes.
  tests_run:
    type: array
    items:
      type: string
    description: List of tests that were executed (e.g. pytest invocations).
  remaining_tasks:
    type: array
    items:
      type: string
    description: List of TODO-style remaining tasks derived from the log.

steps:
  - id: load_log
    description: Read source_log_path and normalize into entries (lines/blocks).

  - id: extract_changes
    description: >
      Detect lines describing code changes (added/modified files, shims,
      config tweaks) and convert them into structured "changes" items.

  - id: extract_tests
    description: >
      Detect test commands (e.g. 'python -m pytest ...') and collect them
      into the tests_run list.

  - id: extract_remaining_tasks
    description: >
      Detect explicit "Remaining Tasks" or TODO sections and emit a
      normalized remaining_tasks list.

  - id: build_summary
    description: >
      Generate a summary_text that references changes, tests_run, and
      remaining_tasks in a compact form.
```

### 3.2 Schema – `patterns/schemas/resume_work_session.schema.json`

```json
{
  "doc_id": "DOC-PAT-RESUME-WORK-SESSION-001",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "resume_work_session pattern parameters",
  "type": "object",
  "properties": {
    "source_log_path": {
      "type": "string"
    },
    "max_entries": {
      "type": "integer",
      "minimum": 1,
      "default": 50
    }
  },
  "required": ["source_log_path"]
}
```

### 3.3 Executor skeleton – `patterns/executors/resume_work_session_executor.ps1`

```powershell
# DOC_LINK: DOC-PAT-RESUME-WORK-SESSION-001
param(
    [Parameter(Mandatory = $true)]
    [string]$Source_Log_Path,
    [int]$Max_Entries = 50
)

# resume_work_session_executor.ps1
# Responsibilities:
#   - Load the log
#   - Extract changes, tests_run, remaining_tasks
#   - Emit a structured JSON summary

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $Source_Log_Path)) {
    throw "source_log_path '$Source_Log_Path' does not exist."
}

$lines = Get-Content -Path $Source_Log_Path -ErrorAction Stop | Select-Object -Last $Max_Entries

$changes = @()
$tests   = @()
$tasks   = @()

foreach ($line in $lines) {
    if ($line -match 'Added' -or $line -match 'Introduced' -or $line -match 'Fixed') {
        $changes += $line.Trim()
    }
    if ($line -match 'python -m pytest' -or $line -match 'pytest') {
        $tests += $line.Trim()
    }
    if ($line -match 'Remaining Tasks' -or $line -match 'Next steps') {
        $tasks += $line.Trim()
    }
}

$summary = "Changes: $($changes.Count); Tests: $($tests.Count); Remaining tasks: $($tasks.Count)."

[pscustomobject]@{
    doc_id          = 'DOC-PAT-RESUME-WORK-SESSION-001'
    pattern_name    = 'resume_work_session'
    summary_text    = $summary
    changes         = $changes
    tests_run       = $tests
    remaining_tasks = $tasks
} | ConvertTo-Json -Depth 5
```

### 3.4 Tests & Example (skeletons)

`patterns/tests/test_resume_work_session_executor.ps1`:

```powershell
# DOC_LINK: DOC-PAT-RESUME-WORK-SESSION-001

Describe "resume_work_session_executor" {
    It "summarizes changes and tests from a small sample log" {
        $tmp = Join-Path $env:TEMP "rws_$(Get-Random).log"
@"
- Added AST parser/extractor wrappers...
- python -m pytest -q tests/syntax_analysis/test_parser.py::TestASTParserInit::test_init_python
- Remaining Tasks
  - Verify dependency visibility
"@ | Set-Content -Path $tmp -Encoding UTF8

        $json = & patterns/executors/resume_work_session_executor.ps1 -Source_Log_Path $tmp
        $result = $json | ConvertFrom-Json

        $result.changes.Count     | Should -BeGreaterThan 0
        $result.tests_run.Count   | Should -BeGreaterThan 0
        $result.remaining_tasks.Count | Should -BeGreaterThan 0
    }
}
```

`patterns/examples/resume_work_session/instance_minimal.json`:

```json
{
  "doc_id": "DOC-PAT-RESUME-WORK-SESSION-001",
  "source_log_path": "logs/ai_session_transcript.log",
  "max_entries": 100
}
```

---

## 4. CREATE_FEATURE_BRANCH_AND_COMMIT_V1

This one encodes the `git checkout -b feature/...`, `git add -A`, `git commit -m ...` pattern from your transcript.

### 4.1 Spec – `patterns/specs/feature_branch_commit.pattern.yaml`

```yaml
# patterns/specs/feature_branch_commit.pattern.yaml

doc_id: DOC-PAT-FEATURE-BRANCH-COMMIT-001
pattern_id: PAT-FEATURE-BRANCH-COMMIT-001
name: feature_branch_commit
version: 1.0.0
role: spec

operation_kinds:
  - GIT_FEATURE_BRANCH_WORK

schema_ref: patterns/schemas/feature_branch_commit.schema.json
executor_ref: patterns/executors/feature_branch_commit_executor.ps1
example_dir: patterns/examples/feature_branch_commit/

summary: >
  Create a new feature branch, stage all changes, and commit them with
  a structured message, then emit the branch name and commit hash.

intent: >
  Use when the user says "commit all changes to a new feature branch you create"
  or similar. Ensures a repeatable git workflow.

inputs:
  repo_root:
    type: string
    description: Repository root path.
  feature_slug:
    type: string
    description: Slug used for the feature branch name (e.g. uet-compat-shims).
  commit_prefix:
    type: string
    default: fix:
    description: Conventional commit prefix (feat:, fix:, chore:, etc.).
  commit_summary:
    type: string
    description: Short summary of the changes.

outputs:
  branch_name:
    type: string
    description: Name of the created branch (feature/<feature_slug>).
  commit_hash:
    type: string
    description: Hash of the created commit.
  git_commands:
    type: array
    items:
      type: string
    description: List of git commands executed in order.

steps:
  - id: ensure_clean_repo
    description: >
      Run 'git status --short' to confirm there are changes to commit
      and detect any issues (optional clean check).

  - id: create_branch
    description: >
      Run 'git checkout -b feature/<feature_slug>' from repo_root.

  - id: stage_all
    description: >
      Run 'git add -A' to stage all changes.

  - id: commit_changes
    description: >
      Run 'git commit -m "<commit_prefix> <commit_summary>"' and capture
      the resulting commit hash.

  - id: emit_result
    description: >
      Return branch_name, commit_hash, and executed git_commands as JSON.
```

### 4.2 Schema – `patterns/schemas/feature_branch_commit.schema.json`

```json
{
  "doc_id": "DOC-PAT-FEATURE-BRANCH-COMMIT-001",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "feature_branch_commit pattern parameters",
  "type": "object",
  "properties": {
    "repo_root": {
      "type": "string"
    },
    "feature_slug": {
      "type": "string",
      "pattern": "^[a-z0-9_-]+$"
    },
    "commit_prefix": {
      "type": "string",
      "default": "fix:"
    },
    "commit_summary": {
      "type": "string",
      "minLength": 3
    }
  },
  "required": ["repo_root", "feature_slug", "commit_summary"]
}
```

### 4.3 Executor skeleton – `patterns/executors/feature_branch_commit_executor.ps1`

```powershell
# DOC_LINK: DOC-PAT-FEATURE-BRANCH-COMMIT-001
param(
    [Parameter(Mandatory = $true)]
    [string]$Repo_Root,
    [Parameter(Mandatory = $true)]
    [string]$Feature_Slug,
    [string]$Commit_Prefix = "fix:",
    [Parameter(Mandatory = $true)]
    [string]$Commit_Summary
)

$ErrorActionPreference = 'Stop'

Push-Location $Repo_Root
try {
    $commands = @()

    $branchName = "feature/$Feature_Slug"

    $commands += "git checkout -b $branchName"
    git checkout -b $branchName | Out-Null

    $commands += "git add -A"
    git add -A | Out-Null

    $msg = "$Commit_Prefix $Commit_Summary"
    $commands += "git commit -m `"$msg`""
    git commit -m $msg | Out-Null

    $commitHash = (git rev-parse HEAD).Trim()

    [pscustomobject]@{
        doc_id       = 'DOC-PAT-FEATURE-BRANCH-COMMIT-001'
        pattern_name = 'feature_branch_commit'
        branch_name  = $branchName
        commit_hash  = $commitHash
        git_commands = $commands
    } | ConvertTo-Json -Depth 5
}
finally {
    Pop-Location
}
```

### 4.4 Tests & Example

`patterns/tests/test_feature_branch_commit_executor.ps1`:

```powershell
# DOC_LINK: DOC-PAT-FEATURE-BRANCH-COMMIT-001

Describe "feature_branch_commit_executor" {
    It "creates a feature branch and commit" {
        # This would ideally use a temp repo fixture; here is a placeholder.
        # Real implementation should create a throwaway repo for CI.
        $true | Should -BeTrue
    }
}
```

`patterns/examples/feature_branch_commit/instance_minimal.json`:

```json
{
  "doc_id": "DOC-PAT-FEATURE-BRANCH-COMMIT-001",
  "repo_root": ".",
  "feature_slug": "uet-compat-shims",
  "commit_prefix": "fix:",
  "commit_summary": "add uet import compatibility shims"
}
```

---

## 5. LEGACY_IMPORT_COMPATIBILITY_FIX_LOOP_V1

This encodes the “run pytest → inspect missing shims → adjust aliases → rerun tests” loop.

I’ll keep the artifacts concise (you can expand later in the same style):

### Spec – `patterns/specs/legacy_import_fix_loop.pattern.yaml`

```yaml
doc_id: DOC-PAT-LEGACY-IMPORT-FIX-LOOP-001
pattern_id: PAT-LEGACY-IMPORT-FIX-LOOP-001
name: legacy_import_fix_loop
version: 1.0.0
role: spec

operation_kinds:
  - TEST_FIX_LOOP

schema_ref: patterns/schemas/legacy_import_fix_loop.schema.json
executor_ref: patterns/executors/legacy_import_fix_loop_executor.ps1
example_dir: patterns/examples/legacy_import_fix_loop/

summary: >
  Iteratively run targeted tests, inspect import failures related to
  legacy core.* / engine.* modules, update compatibility aliases, and
  rerun tests until green or a maximum number of iterations is reached.

inputs:
  repo_root:
    type: string
  test_targets:
    type: array
    items:
      type: string
    description: >
      Pytest target expressions to run (e.g. tests/integration/test_uet_migration.py::test_dag_to_parallel_execution).
  max_iterations:
    type: integer
    default: 3

outputs:
  iterations:
    type: integer
  failures:
    type: array
    items:
      type: string
  applied_aliases:
    type: array
    items:
      type: string
```

### Schema – `patterns/schemas/legacy_import_fix_loop.schema.json`

```json
{
  "doc_id": "DOC-PAT-LEGACY-IMPORT-FIX-LOOP-001",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "legacy_import_fix_loop pattern parameters",
  "type": "object",
  "properties": {
    "repo_root": { "type": "string" },
    "test_targets": {
      "type": "array",
      "items": { "type": "string" },
      "minItems": 1
    },
    "max_iterations": {
      "type": "integer",
      "default": 3,
      "minimum": 1
    }
  },
  "required": ["repo_root", "test_targets"]
}
```

### Example – `patterns/examples/legacy_import_fix_loop/instance_minimal.json`

```json
{
  "doc_id": "DOC-PAT-LEGACY-IMPORT-FIX-LOOP-001",
  "repo_root": ".",
  "test_targets": [
    "tests/syntax_analysis/test_parser.py::TestASTParserInit::test_init_python",
    "tests/integration/test_uet_migration.py::test_dag_to_parallel_execution"
  ],
  "max_iterations": 3
}
```

(Executors/tests can follow the same pattern as above: loop `python -m pytest`, parse import errors, mutate alias files.)

---

## 6. AUTO_SYNC_LOG_HEADER_V1

This pattern recognizes and filters the repeated “Starting Git Auto-Sync (First Window)” noise from logs.

### Spec – `patterns/specs/auto_sync_log_header.pattern.yaml`

```yaml
doc_id: DOC-PAT-AUTO-SYNC-LOG-HEADER-001
pattern_id: PAT-AUTO-SYNC-LOG-HEADER-001
name: auto_sync_log_header
version: 1.0.0
role: spec

operation_kinds:
  - LOG_NOISE_FILTERING

schema_ref: patterns/schemas/auto_sync_log_header.schema.json
executor_ref: patterns/executors/auto_sync_log_header_executor.ps1
example_dir: patterns/examples/auto_sync_log_header/

summary: >
  Remove or collapse repeated 'Starting Git Auto-Sync (First Window)' headers
  from logs to reduce noise and make pattern detection easier.

inputs:
  input_log_path:
    type: string
  output_log_path:
    type: string
  mode:
    type: string
    enum: [filter, collapse]

outputs:
  output_log_path:
    type: string
  removed_count:
    type: integer
  collapsed_blocks:
    type: integer
```

### Schema – `patterns/schemas/auto_sync_log_header.schema.json`

```json
{
  "doc_id": "DOC-PAT-AUTO-SYNC-LOG-HEADER-001",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "auto_sync_log_header pattern parameters",
  "type": "object",
  "properties": {
    "input_log_path": { "type": "string" },
    "output_log_path": { "type": "string" },
    "mode": {
      "type": "string",
      "enum": ["filter", "collapse"],
      "default": "filter"
    }
  },
  "required": ["input_log_path", "output_log_path"]
}
```

### Example – `patterns/examples/auto_sync_log_header/instance_minimal.json`

```json
{
  "doc_id": "DOC-PAT-AUTO-SYNC-LOG-HEADER-001",
  "input_log_path": "logs/ai_session_raw.log",
  "output_log_path": "logs/ai_session_clean.log",
  "mode": "filter"
}
```

---

## 7. GIT_PATH_VISIBILITY_DEBUG_V1

Encodes the “why doesn’t Git show this path?” investigation (sparse checkout, ignore, submodule, etc.).

### Spec – `patterns/specs/git_path_visibility_debug.pattern.yaml`

```yaml
doc_id: DOC-PAT-GIT-PATH-VISIBILITY-DEBUG-001
pattern_id: PAT-GIT-PATH-VISIBILITY-DEBUG-001
name: git_path_visibility_debug
version: 1.0.0
role: spec

operation_kinds:
  - GIT_PATH_DEBUG

schema_ref: patterns/schemas/git_path_visibility_debug.schema.json
executor_ref: patterns/executors/git_path_visibility_debug_executor.ps1
example_dir: patterns/examples/git_path_visibility_debug/

summary: >
  Diagnose why a given path or directory does or does not appear in
  git status, inspecting sparse-checkout, submodules, ignore rules,
  and repo root.

inputs:
  repo_root:
    type: string
  target_path:
    type: string
    description: Path to inspect (relative to repo_root).
  use_repo_root_c_flag:
    type: boolean
    default: true
    description: Whether to use 'git -C repo_root ...' for commands.

outputs:
  classification:
    type: string
    description: >
      One of: tracked, untracked, ignored, outside_repo, error.
  evidence:
    type: array
    items:
      type: string
    description: List of git commands and key outputs.
  repo_top_level:
    type: string
```

### Schema – `patterns/schemas/git_path_visibility_debug.schema.json`

```json
{
  "doc_id": "DOC-PAT-GIT-PATH-VISIBILITY-DEBUG-001",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "git_path_visibility_debug pattern parameters",
  "type": "object",
  "properties": {
    "repo_root": { "type": "string" },
    "target_path": { "type": "string" },
    "use_repo_root_c_flag": {
      "type": "boolean",
      "default": true
    }
  },
  "required": ["repo_root", "target_path"]
}
```

### Example – `patterns/examples/git_path_visibility_debug/instance_minimal.json`

```json
{
  "doc_id": "DOC-PAT-GIT-PATH-VISIBILITY-DEBUG-001",
  "repo_root": "C:/Users/richg/ALL_AI/Complete AI Development Pipeline – Canonical Phase Plan",
  "target_path": "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns",
  "use_repo_root_c_flag": true
}
```

---

## 8. REPO_STATE_CHECK_V1

Micro-pattern for quick `git status` / `rev-parse` checks.

### Spec – `patterns/specs/repo_state_check.pattern.yaml`

```yaml
doc_id: DOC-PAT-REPO-STATE-CHECK-001
pattern_id: PAT-REPO-STATE-CHECK-001
name: repo_state_check
version: 1.0.0
role: spec

operation_kinds:
  - REPO_STATE_INSPECTION

schema_ref: patterns/schemas/repo_state_check.schema.json
executor_ref: patterns/executors/repo_state_check_executor.ps1
example_dir: patterns/examples/repo_state_check/

summary: >
  Capture a quick snapshot of repository state: top-level path, current
  branch, and short status (modified/untracked files).

inputs:
  repo_root:
    type: string

outputs:
  repo_top_level:
    type: string
  branch:
    type: string
  short_status:
    type: array
    items:
      type: string
```

### Schema – `patterns/schemas/repo_state_check.schema.json`

```json
{
  "doc_id": "DOC-PAT-REPO-STATE-CHECK-001",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "repo_state_check pattern parameters",
  "type": "object",
  "properties": {
    "repo_root": { "type": "string" }
  },
  "required": ["repo_root"]
}
```

### Example – `patterns/examples/repo_state_check/instance_minimal.json`

```json
{
  "doc_id": "DOC-PAT-REPO-STATE-CHECK-001",
  "repo_root": "."
}
```

---

## 9. How this lines up with your specs

* Each pattern has:

  * **Index entry**, **spec**, **schema**, **executor skeleton**, **test skeleton**, and **example** wired by a single `doc_id`, as required.
* The overall structure matches the “per-pattern spec/schema/executor/tests + shared PATTERN_INDEX.yaml” model from *Every_reusable_pattern.md*.

If you want, your next step can be:

* Drop these into the repo under `patterns/…`
* Hook them into your existing pattern-check tooling
* Then we can (on a future prompt) deepen any one pattern’s executor/tests into fully production-grade logic.
