````markdown
---
spec_id: FOLDER_GOVERNANCE_SPEC
version: 1.0.0
status: draft
owner: pipeline-governance
created: 2025-11-22
applies_to:
  - windows
  - wsl
  - ai_cli_tools
tools_in_scope:
  - claude_code_cli
  - github_copilot_cli
  - aider
  - codex_wrappers
---

# FOLDER_GOVERNANCE_SPEC v1.0.0

> Canonical folder and project governance rules for AI CLI tools in the local pipeline environment.

---

## 1. Scope & Objectives

### 1.1 Scope

- [FGS-SCOPE-001] This specification governs how AI CLI tools create, use, and manage folders and files on the local machine.
- [FGS-SCOPE-002] This specification applies to all AI CLI tools that read or write to the filesystem as part of development workflows.
- [FGS-SCOPE-003] This specification covers:
  - Project roots
  - Sandbox/workspace roots
  - Tool-specific metadata folders
  - Cleanup and hygiene policies

### 1.2 Objectives

- [FGS-OBJ-001] Minimize folder sprawl and confusion about which folders belong to which project.
- [FGS-OBJ-002] Ensure each project has a single, canonical project root recognized by all AI tools.
- [FGS-OBJ-003] Isolate sandbox/experimental edits from canonical repositories.
- [FGS-OBJ-004] Make tool artifacts predictable, ignorable by default in version control, and easy to clean up.
- [FGS-OBJ-005] Provide machine-readable schemas so other agents can reason about and enforce these rules.

---

## 2. Terminology (Normative)

- [FGS-TERM-001] **PROJECTS_ROOT**  
  The canonical parent folder under which all **real** project repositories MUST live.

- [FGS-TERM-002] **PROJECT_ROOT**  
  A single folder that contains one logical project, typically a git repository root.

- [FGS-TERM-003] **SANDBOX_ROOT**  
  A parent folder that contains non-canonical clones/worktrees of projects for experimentation, AI editing, or temporary work.

- [FGS-TERM-004] **TOOL_ARTIFACT_FOLDER**  
  Any folder created by an AI CLI tool to store per-project or per-session state (e.g. `.claude/`, `.copilot/`, `.aider/`).

- [FGS-TERM-005] **GLOBAL_TOOL_CONFIG_ROOT**  
  A tool’s per-user, per-machine configuration directory (e.g. `AppData\Roaming\tool`, `~/.config/tool`).

- [FGS-TERM-006] **CANONICAL_REPO**  
  The git repository located at a `PROJECT_ROOT` that represents the authoritative source for project code and specifications.

- [FGS-TERM-007] **NON_PROJECT_LOCATION**  
  Any folder that is not under `PROJECTS_ROOT` or `SANDBOX_ROOT`, including but not limited to `Downloads`, `Desktop`, `Documents`, and the user’s home directory.

---

## 3. Environment Schemas

### 3.1 High-Level Environment Schema

```yaml
env_schema_v1:
  projects_root: "C:\\Users\\richg\\ALL_AI\\projects"
  sandbox_root: "C:\\Users\\richg\\ALL_AI\\sandbox"
  allowed_project_roots:
    - "C:\\Users\\richg\\ALL_AI\\projects"
  disallowed_roots:
    - "C:\\Users\\richg\\Downloads"
    - "C:\\Users\\richg\\Desktop"
    - "C:\\Users\\richg\\Documents"
    - "C:\\Users\\richg"
  global_tool_config_roots:
    claude_code_cli:
      - "%USERPROFILE%\\.config\\claude"
      - "~/.config/claude"
    github_copilot_cli:
      - "%APPDATA%\\GithubCopilot"
      - "~/.config/github-copilot"
    aider:
      - "%USERPROFILE%\\.aider"
      - "~/.config/aider"
    codex_wrapper:
      - "%USERPROFILE%\\.codex"
      - "~/.config/codex"
````

* [FGS-SCH-ENV-001] Agents MUST treat `env_schema_v1` as the authoritative description of the local folder topology.
* [FGS-SCH-ENV-002] Additional tools MAY be appended to `global_tool_config_roots` without modifying existing keys.

### 3.2 Project Root Schema

```yaml
project_root_schema_v1:
  project_id: "string"         # Logical project identifier
  path: "absolute_path"        # Must be under projects_root
  type: "canonical_repo"       # reserved: canonical_repo
  vcs: "git"                   # version control system
  subfolders:
    src: "optional_path"
    docs: "optional_path"
    specs: "optional_path"
    tests: "optional_path"
    ai_internal: ".ai"         # preferred folder for tool artifacts
```

* [FGS-SCH-PROJ-001] `project_root_schema_v1.path` MUST be a subfolder of `PROJECTS_ROOT`.
* [FGS-SCH-PROJ-002] `project_root_schema_v1.type` MUST equal `canonical_repo`.
* [FGS-SCH-PROJ-003] If `.ai` exists, AI tools SHOULD prefer using it for `TOOL_ARTIFACT_FOLDER`s.

### 3.3 Sandbox Schema

```yaml
sandbox_schema_v1:
  project_id: "string"
  sandbox_id: "string"        # e.g. "project-01_claude"
  path: "absolute_path"       # Must be under sandbox_root
  origin_project_root: "absolute_path"
  sandbox_type: "clone | worktree | scratch"
  tool_name: "claude | copilot | aider | codex | other"
```

* [FGS-SCH-SBX-001] `sandbox_schema_v1.path` MUST be a subfolder of `SANDBOX_ROOT`.
* [FGS-SCH-SBX-002] `sandbox_schema_v1.origin_project_root` MUST reference a valid `PROJECT_ROOT`.
* [FGS-SCH-SBX-003] `sandbox_schema_v1.tool_name` MUST be one of the configured tools or `other`.

### 3.4 Tool Artifact Classification Schema

```yaml
tool_artifact_schema_v1:
  folder_name: ".claude"        # example
  scope: "project | global"
  location_type: "project_root | sandbox_root | global_tool_config_root | non_project"
  managed_by: "tool_name"
  safe_to_git_ignore: true
  safe_to_delete_when_inactive: true
```

* [FGS-SCH-TA-001] `tool_artifact_schema_v1.safe_to_git_ignore` MUST be true for all `TOOL_ARTIFACT_FOLDER`s.
* [FGS-SCH-TA-002] `tool_artifact_schema_v1.location_type` MUST be derivable from the folder’s absolute path and the environment schema.

---

## 4. Normative Requirements

### 4.1 Project Roots

* [FGS-REQ-ROOT-001] There MUST be exactly one `PROJECTS_ROOT` per machine profile used by the pipeline.
* [FGS-REQ-ROOT-002] All canonical project repositories MUST reside under `PROJECTS_ROOT`.
* [FGS-REQ-ROOT-003] A `PROJECT_ROOT` MUST NOT be located directly under any `NON_PROJECT_LOCATION`.
* [FGS-REQ-ROOT-004] Agents MUST treat any folder not under `PROJECTS_ROOT` or `SANDBOX_ROOT` as `NON_PROJECT_LOCATION` unless explicitly whitelisted.

### 4.2 Sandbox Roots

* [FGS-REQ-SBX-001] If `SANDBOX_ROOT` is defined, all sandboxes for AI tools SHOULD be created under `SANDBOX_ROOT`.
* [FGS-REQ-SBX-002] A sandbox MUST clearly encode both `project_id` and `tool_name` in its directory name (e.g. `project-01_claude`).
* [FGS-REQ-SBX-003] Sandboxes MUST NOT be treated as canonical sources for specs or system code.
* [FGS-REQ-SBX-004] Changes made in sandboxes MUST be reconciled back to the corresponding `CANONICAL_REPO` via patch, PR, or explicitly logged copy operations.

### 4.3 Tool Invocation Location

* [FGS-REQ-INVOKE-001] AI CLI tools MUST be invoked only when the current working directory is:

  * A `PROJECT_ROOT`, or
  * A `SANDBOX_ROOT` descendant.
* [FGS-REQ-INVOKE-002] AI CLI tools MUST NOT be invoked from `NON_PROJECT_LOCATION`s for project-related operations.
* [FGS-REQ-INVOKE-003] Wrappers or launch scripts SHOULD enforce [FGS-REQ-INVOKE-001] and [FGS-REQ-INVOKE-002] by validating CWD against `env_schema_v1`.

### 4.4 Tool Artifact Folders

* [FGS-REQ-TA-001] Tool-specific per-project folders (e.g. `.claude`, `.copilot`, `.aider`) SHOULD be located:

  * Either directly under `PROJECT_ROOT`, or
  * Under `PROJECT_ROOT/.ai/`.
* [FGS-REQ-TA-002] Tool-specific per-sandbox folders SHOULD be located:

  * Either directly under the sandbox root for that project, or
  * Under `<sandbox_path>/.ai/`.
* [FGS-REQ-TA-003] Tool artifact folders MUST NOT be used to store canonical project specifications or source code that cannot be regenerated.
* [FGS-REQ-TA-004] Each `TOOL_ARTIFACT_FOLDER` MUST be safe to:

  * Add to `.gitignore`, and
  * Delete when inactive (rebuildable by the tool).

### 4.5 Global Tool Config Roots

* [FGS-REQ-GLOBAL-001] `GLOBAL_TOOL_CONFIG_ROOT` paths MUST be treated as infrastructure, not project data.
* [FGS-REQ-GLOBAL-002] Agents MUST NOT infer project context from files under `GLOBAL_TOOL_CONFIG_ROOT`.
* [FGS-REQ-GLOBAL-003] `GLOBAL_TOOL_CONFIG_ROOT` SHOULD NOT be located under `PROJECTS_ROOT` or `SANDBOX_ROOT`.

### 4.6 Cleanup & Hygiene

* [FGS-REQ-CLEAN-001] Any `TOOL_ARTIFACT_FOLDER` discovered under `NON_PROJECT_LOCATION` MUST be classified as a cleanup candidate.
* [FGS-REQ-CLEAN-002] Cleanup agents SHOULD:

  * Generate a report of candidate folders,
  * Confirm there is no associated `PROJECT_ROOT` or sandbox mapping,
  * Then propose deletion or archival actions.
* [FGS-REQ-CLEAN-003] A periodic “folder hygiene” task SHOULD be scheduled (e.g. weekly) to enforce [FGS-REQ-CLEAN-001] and [FGS-REQ-CLEAN-002].

---

## 5. Operational Procedures (For Agents)

### 5.1 Determining If CWD Is Valid for Tool Invocation

**Algorithm (pseudo-steps):**

* [FGS-OP-CWD-001] Given `cwd`:

  1. If `cwd` is under `PROJECTS_ROOT` and contains `.git/` → classify as `PROJECT_ROOT`.
  2. Else if `cwd` is under `SANDBOX_ROOT` → classify as `SANDBOX`.
  3. Else → classify as `NON_PROJECT_LOCATION`.

* [FGS-OP-CWD-002] If classification is `NON_PROJECT_LOCATION`, the agent MUST:

  * Refuse to execute project-related AI CLI actions, and
  * Recommend cd-ing into a valid `PROJECT_ROOT` or sandbox.

### 5.2 Creating a New Project

* [FGS-OP-PROJ-001] When an agent is instructed to create a new project:

  1. Generate a `project_id`.
  2. Create a folder at `PROJECTS_ROOT/<project_id_or_name>`.
  3. Initialize a git repository at that path.
  4. Optionally create `src/`, `docs/`, `specs/`, `tests/`, `.ai/`.
  5. Register the project using `project_root_schema_v1`.

### 5.3 Creating a Sandbox for a Project

* [FGS-OP-SBX-001] When a sandbox is requested for tool `T`:

  1. Validate that the source is a valid `PROJECT_ROOT`.
  2. Construct `sandbox_id = "<project_name>_<tool_name>"`.
  3. Create a folder at `SANDBOX_ROOT/<sandbox_id>`.
  4. Create a clone or git worktree from the canonical repo into this path.
  5. Record metadata using `sandbox_schema_v1`.

### 5.4 Classifying Existing Tool Folders

* [FGS-OP-TA-001] For each folder matching known tool patterns (e.g. `.claude`, `.copilot`, `.aider`):

  1. Determine absolute path.
  2. Resolve `location_type`:

     * Under `PROJECTS_ROOT` → `project_root`
     * Under `SANDBOX_ROOT` → `sandbox_root`
     * Under any `GLOBAL_TOOL_CONFIG_ROOT` → `global_tool_config_root`
     * Else → `non_project`
  3. Emit a `tool_artifact_schema_v1` record.

* [FGS-OP-TA-002] If `location_type == "non_project"`, mark as `cleanup_candidate: true`.

---

## 6. Integration With Higher-Level Governance

* [FGS-INT-001] This spec MAY be referenced by higher-level documents (e.g. PHASE_SPEC_MASTER, WORKSTREAM_SPEC) via `spec_ref: FOLDER_GOVERNANCE_SPEC@1.0.0`.

* [FGS-INT-002] Phase plans that include file operations SHOULD declare:

  * Expected `PROJECT_ROOT`,
  * Optional `SANDBOX_ROOT` usage,
  * Any additional tool artifacts to be whitelisted.

* [FGS-INT-003] Execution orchestrators MUST enforce [FGS-REQ-INVOKE-001] and [FGS-REQ-INVOKE-002] before launching AI CLI tools as part of a workstream.

---

## 7. Conformance

* [FGS-CONF-001] A tool integration is considered **conformant** with this spec if:

  * It never invokes AI CLI tools from `NON_PROJECT_LOCATION`s.
  * It creates or uses tool artifacts only as specified in [FGS-REQ-TA-001]–[FGS-REQ-TA-004].
  * It respects the canonical/sandbox split as defined in [FGS-REQ-ROOT-001]–[FGS-REQ-SBX-004].

* [FGS-CONF-002] An agent MAY enforce stricter policies (e.g. forbidding any tool artifacts at `PROJECT_ROOT` and requiring `PROJECT_ROOT/.ai/`).

* [FGS-CONF-003] Non-conformant behaviors SHOULD be logged as governance violations and surfaced to the user for remediation.

---

```
```
