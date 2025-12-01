---
doc_id: DOC-AIM-AI-STEWARD-CONFIG-ORCHESTRATOR-TUI-156
---

# AI-Steward Config Orchestrator (TUI-Aware, Headless-First)

**Technical Design for Agentic AI Implementation (No UI Spec)**

---

## 0. Purpose & Scope

This document defines the **backend architecture, data models, and operations** for a system that:

* Manages **AI tools, profiles, and configuration** (env vars, YAML, JSON, `.env`).
* Exposes a **stable, scriptable API** for:

  * Headless execution (scripts, CI, task runners).
  * A future **TUI client**, without prescribing any UI layout or behavior.
* Ensures **config-first** design: all behavior flows from config; UI clients are optional and stateless.

**Out of scope (must NOT be implemented/spec’d here):**

* Any UI layout, screen design, key bindings, colors, widgets, or interaction flows.
* Any framework-specific TUI details (e.g., Textual widget trees, prompt_toolkit prompts, etc.).

The target implementer is an **agentic AI** (e.g., Claude, Codex, etc.) that will generate code in Python + PowerShell on Windows.

---

## 1. High-Level Requirements

### 1.1 Functional Requirements

1. **Config Store**

   * Store configuration for:

     * AI tools (e.g., codex, claude, aider, CrewAI, LangGraph, GPTScript, etc.).
     * Execution profiles (e.g., `dev`, `local`, `prod`, `codespace`).
     * Environment variables (especially secrets) and default CLI flags.
   * Config is persisted in **files** (YAML, JSON, `.env`) on disk.

2. **Profiles**

   * Support multiple named profiles:

     * Each profile can override or extend default tool configuration.
     * Only one profile is “active” at a time.
   * Provide operations to:

     * Get/set the active profile.
     * Enumerate available profiles.
     * Read/write profile-scoped config values.

3. **Tools Registry**

   * Maintain a canonical registry of known tools with:

     * Unique ID and human-friendly name.
     * Classification (e.g., `cli`, `python`, `platform`).
     * Launch metadata (command, arguments, optional interpreter).
     * Required env var keys.
     * Path(s) to tool-specific config files (YAML/JSON).
   * Provide operations to:

     * List tools.
     * Retrieve tool metadata.
     * Add/update/remove tools (with validation).

4. **Config Resolution**

   * Given a **profile name** and **tool ID**, the system must resolve:

     * Final env var set to use.
     * Final config values (merged defaults + profile overrides).
     * Final command/arguments to launch the tool.
   * Provide a deterministic resolution order:

     1. Built-in defaults.
     2. Tool base config.
     3. Profile base config.
     4. Profile overrides for that tool.
     5. Inline overrides passed by the caller.

5. **Headless Execution Integration**

   * Provide backend functions / CLI commands to:

     * Export environment variables for a given profile (e.g., as a `.ps1` script that sets `$env:...`).
     * Generate a “launch command” (string/array) for a given tool + profile.
     * Optionally run healthchecks (e.g., `--version`, test prompts) in a controlled way.

6. **TUI Client Integration**

   * Expose a clean programmatic API for:

     * Listing and reading configs.
     * Updating config entries.
     * Applying changes to disk.
   * TUI client must use these APIs; **no TUI logic in the core modules.**

### 1.2 Non-Functional Requirements

* **Headless-first:** System must work perfectly from scripts and CI with no interactive UI.
* **Deterministic behavior:** Given the same config and inputs, resolution and output must be identical.
* **Extensibility:** It must be easy to:

  * Add new tools.
  * Add new profiles.
  * Attach new clients (TUI, REST API, etc.).
* **Auditability & safety:**

  * `.env` for secrets should be separated and excluded from VCS.
  * Clear separation between “public config” and “secret config”.

---

## 2. Target Environment & Technology Choices

### 2.1 OS & Shell

* Primary target: **Windows 10/11**, PowerShell 7+.
* All paths and scripts must be valid on Windows; design should remain portable where possible.

### 2.2 Languages

* **Python** (3.11+ recommended)

  * Core config library.
  * Cross-platform logic for YAML/JSON/.env parsing and resolution.
* **PowerShell**

  * Wrapper scripts for:

    * Bootstrapping environment.
    * Exporting env vars for a profile.
    * Calling the Python backend functions.
  * Optional simple, non-TUI CLI entrypoints.

### 2.3 Storage format

* **YAML** for primary config and registry (human-friendly).
* **JSON** optional for machine-only artifacts if needed.
* **`.env`** files for secrets; loaded into env vars at runtime.

---

## 3. Directory Layout & Files

Use `%USERPROFILE%\ai-steward` as the root config directory by default.

```text
%USERPROFILE%\ai-steward\
  config\
    ai-tools.registry.yaml       # canonical tools registry
    profiles\
      dev.yaml                   # dev profile
      local.yaml                 # local workstation
      prod.yaml                  # production-like
    active-profile.yaml          # indicates which profile is selected
    defaults.yaml                # optional global defaults for all tools
  secrets\
    dev.env                      # env vars for dev profile
    local.env                    # env vars for local profile
    prod.env                     # env vars for prod profile
  scripts\
    Export-ProfileEnv.ps1        # generate env for a profile
    Resolve-ToolCommand.ps1      # resolve command for tool+profile
  python\
    ai_steward_core\
      __init__.py
      paths.py
      models.py
      loader.py
      resolver.py
      profiles.py
      tools_registry.py
      env_manager.py
      cli.py                     # headless CLI entrypoint (no TUI)
      tests\
        test_loader.py
        test_resolver.py
        ...
```

The future **TUI client** (not specified here) will import `ai_steward_core` or call `cli.py`.

---

## 4. Data Models & Schemas

### 4.1 Tool Registry Schema (`ai-tools.registry.yaml`)

Example structure:

```yaml
version: 1
tools:
  codex:
    id: codex
    name: "Codex CLI"
    type: "cli"                  # cli | python | platform
    command: "codex"
    default_args: []             # base CLI args, e.g. ["--fs", "workspace-write"]
    env_keys:
      - "CODEX_FS"
      - "CODEX_APPROVAL"
      - "OPENAI_API_KEY"
    config_files:
      - "config/tools/codex.yaml"
    description: "Local AI dev CLI"

  crewai:
    id: "crewai"
    name: "CrewAI"
    type: "python"
    python_module: "crewai_runner"  # optional: module to invoke
    entry_function: "main"          # optional
    env_keys:
      - "OPENAI_API_KEY"
    config_files:
      - "config/tools/crewai.yaml"
    description: "Agent crews framework"

  langgraph:
    id: "langgraph"
    name: "LangGraph"
    type: "python"
    python_module: "langgraph_runner"
    env_keys:
      - "OPENAI_API_KEY"
      - "LANGCHAIN_TRACING_V2"      # example
    config_files:
      - "config/tools/langgraph.yaml"
    description: "Graph-based agent workflows"
```

**Invariants:**

* `tools` is a map keyed by unique `id`.
* `type` determines what launch metadata is required:

  * `cli` → must have `command`.
  * `python` → must have at least `python_module` or `command`.
  * `platform` → may have `command` and/or `docker_compose_file`, etc. (optional, for Dify/SuperAGI).

### 4.2 Profile Schema (`config/profiles/<name>.yaml`)

Each profile can define:

* Global overrides (e.g., default model).
* Tool-specific overrides (args, env, settings).

```yaml
name: "dev"
description: "Developer workstation profile"

global:
  default_model: "gpt-4.1"
  log_level: "info"

tools:
  codex:
    extra_args:
      - "--fs"
      - "workspace-write"
      - "--approval"
      - "always"
    overrides:
      model: "gpt-4.1"
      temperature: 0.1

  crewai:
    overrides:
      default_crew: "dev-experiments"
      max_steps: 10
```

### 4.3 Active Profile (`config/active-profile.yaml`)

Single small file:

```yaml
name: "dev"
```

### 4.4 Secrets (`secrets/<profile>.env`)

Format:

```text
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
CODEX_APPROVAL=always
CODEX_FS=workspace-write
```

**Rules:**

* `.env` files are **never** checked into version control.
* The core library must provide functions to:

  * Load these into an env dict (not automatically into OS env).
  * Merge them with existing env values (caller decides what to export).

---

## 5. Core Modules & Responsibilities (Python: `ai_steward_core`)

### 5.1 `paths.py`

* Encapsulate platform-specific path resolution (e.g. `%USERPROFILE%\ai-steward`).
* Functions:

```python
def get_root_dir() -> Path: ...
def get_config_dir() -> Path: ...
def get_secrets_dir() -> Path: ...
def get_registry_path() -> Path: ...
def get_profiles_dir() -> Path: ...
def get_profile_path(profile_name: str) -> Path: ...
def get_profile_env_path(profile_name: str) -> Path: ...
def get_active_profile_path() -> Path: ...
```

### 5.2 `models.py`

* Data classes / pydantic models for:

  * `ToolMetadata`
  * `ProfileConfig`
  * `GlobalConfig`
  * `ResolvedToolConfig`

Example:

```python
@dataclass
class ToolMetadata:
  id: str
  name: str
  type: str
  command: Optional[str] = None
  python_module: Optional[str] = None
  entry_function: Optional[str] = None
  default_args: List[str] = field(default_factory=list)
  env_keys: List[str] = field(default_factory=list)
  config_files: List[str] = field(default_factory=list)
  description: Optional[str] = None

@dataclass
class ResolvedToolConfig:
  tool_id: str
  profile: str
  command: List[str]          # final argv to run
  env: Dict[str, str]         # final environment to use
  settings: Dict[str, Any]    # merged config values
```

### 5.3 `loader.py`

* Functions to **load** and **save** YAML/JSON and `.env` files.

Key methods:

```python
def load_yaml(path: Path) -> dict: ...
def save_yaml(path: Path, data: dict) -> None: ...

def load_env_file(path: Path) -> Dict[str, str]: ...
def save_env_file(path: Path, env: Dict[str, str]) -> None: ...
```

### 5.4 `tools_registry.py`

* Load the `ai-tools.registry.yaml` file and expose:

```python
def load_registry() -> Dict[str, ToolMetadata]: ...
def get_tool(tool_id: str) -> ToolMetadata: ...
def list_tools() -> List[ToolMetadata]: ...
def add_or_update_tool(tool: ToolMetadata) -> None: ...
def remove_tool(tool_id: str) -> None: ...
```

* Must validate:

  * Required fields by `type`.
  * No duplicate IDs.
  * Paths, if relative, are resolved relative to `config` root.

### 5.5 `profiles.py`

* Manage profiles and active profile selection.

```python
def list_profiles() -> List[str]: ...
def load_profile(name: str) -> dict: ...
def save_profile(name: str, data: dict) -> None: ...
def get_active_profile_name() -> str: ...
def set_active_profile_name(name: str) -> None: ...
```

* Optional helper: `ensure_profile_exists(name)`.

### 5.6 `env_manager.py`

* High-level environment management.

```python
def load_profile_env(profile: str) -> Dict[str, str]:
    """Load secrets/<profile>.env into a dict."""
    ...

def merge_env(base: Dict[str, str], overlay: Dict[str, str]) -> Dict[str, str]:
    """Return a new env dict; overlay wins on conflicts."""
    ...

def filter_env_for_tool(env: Dict[str, str], tool: ToolMetadata) -> Dict[str, str]:
    """Return env dict containing only keys listed in tool.env_keys."""
    ...
```

* This module must **not** directly modify `os.environ` except in explicit functions the caller invokes.

### 5.7 `resolver.py`

Core resolution logic that:

* Takes:

  * `tool_id`
  * `profile` (optional, default to active)
  * optional inline overrides
* Returns:

  * `ResolvedToolConfig` with `command`, `env`, `settings`.

Pseudo-code outline:

```python
def resolve_tool_config(
    tool_id: str,
    profile: Optional[str] = None,
    inline_settings: Optional[Dict[str, Any]] = None,
    inline_env: Optional[Dict[str, str]] = None,
    inline_args: Optional[List[str]] = None,
) -> ResolvedToolConfig:
    # 1) Load metadata & profile
    tool = tools_registry.get_tool(tool_id)
    profile_name = profile or profiles.get_active_profile_name()
    profile_cfg = profiles.load_profile(profile_name)

    # 2) Load defaults
    defaults_cfg = load_defaults()  # from config/defaults.yaml if exists

    # 3) Load tool-specific configs from config_files
    tool_settings = {}
    for cfg_path in tool.config_files:
        tool_settings = deep_merge(tool_settings, loader.load_yaml(resolve_path(cfg_path)))

    # 4) Merge settings: defaults -> tool_settings -> profile_global -> profile_tool -> inline_settings
    merged_settings = {}
    merged_settings = deep_merge(merged_settings, defaults_cfg.get("global", {}))
    merged_settings = deep_merge(merged_settings, tool_settings)
    merged_settings = deep_merge(merged_settings, profile_cfg.get("global", {}))
    merged_settings = deep_merge(merged_settings, profile_cfg.get("tools", {}).get(tool_id, {}).get("overrides", {}))
    if inline_settings:
        merged_settings = deep_merge(merged_settings, inline_settings)

    # 5) Env
    base_env = os.environ.copy()
    profile_env = env_manager.load_profile_env(profile_name)
    final_env = env_manager.merge_env(base_env, profile_env)
    if inline_env:
        final_env = env_manager.merge_env(final_env, inline_env)
    tool_env = env_manager.filter_env_for_tool(final_env, tool)

    # 6) Command / args
    argv: List[str] = []
    if tool.type == "cli":
        argv = [tool.command]
    elif tool.type == "python":
        # Example: python -m some_module
        argv = ["python", "-m", tool.python_module or tool.command]
    # else platform-specific behaviors as needed

    # Append default args, profile extra args, then inline args
    argv.extend(tool.default_args)
    profile_tool_cfg = profile_cfg.get("tools", {}).get(tool_id, {})
    argv.extend(profile_tool_cfg.get("extra_args", []))
    if inline_args:
        argv.extend(inline_args)

    return ResolvedToolConfig(
        tool_id=tool_id,
        profile=profile_name,
        command=argv,
        env=tool_env,
        settings=merged_settings,
    )
```

---

## 6. PowerShell Integration

### 6.1 `Export-ProfileEnv.ps1`

Purpose:

* Generate an environment suitable for a profile (and optionally a tool) that can be dot-sourced in a shell.

Behavior:

* Parameters:

  * `-Profile` (string, optional; defaults to active profile).
  * `-ToolId` (string, optional; if specified, only export keys relevant to that tool via `env_keys`).
  * `-AsScript` (switch; outputs `Set-Item Env:` commands instead of modifying the current process).

Implementation outline:

1. Call Python CLI with a subcommand, e.g.:

   ```powershell
   $json = python .\python\ai_steward_core\cli.py export-env --profile dev --tool codex
   ```

2. Deserialize JSON to a dictionary.

3. If `-AsScript`:

   * Emit lines like: `Set-Item Env:OPENAI_API_KEY "value"`.

4. Else:

   * Iterate and set `$env:KEY = "value"`.

### 6.2 `Resolve-ToolCommand.ps1`

Purpose:

* Resolve the command for a tool + profile and optionally execute it.

Parameters:

* `-ToolId` (mandatory).
* `-Profile` (optional; default active).
* `-DryRun` (switch; just print resolved command+env).

Steps:

1. Call Python CLI:

   ```powershell
   $json = python .\python\ai_steward_core\cli.py resolve-tool `
              --tool-id $ToolId `
              --profile $Profile
   ```

2. Deserialize JSON.

3. If `-DryRun`, output:

   * Command array.
   * Env keys to be set.

4. Else:

   * Set env vars in current process.
   * Invoke the command via `Start-Process` or `&`.

---

## 7. Python CLI (`ai_steward_core/cli.py`)

This CLI is **headless** and will also serve as the API surface for non-Python clients (PowerShell, TUI, etc.).

### 7.1 Commands

1. `list-tools`

   * Output: JSON array with tool metadata.

2. `get-tool`

   * Args: `--tool-id`
   * Output: JSON object with tool metadata.

3. `list-profiles`

   * Output: JSON array of profile names.

4. `get-active-profile`

   * Output: `{ "name": "dev" }`

5. `set-active-profile`

   * Args: `--name`

6. `get-profile`

   * Args: `--name`
   * Output: JSON representation of profile YAML.

7. `update-profile`

   * Args: `--name`, `--json-patch` or `--file`
   * Apply changes to the profile YAML (atomic write).

8. `export-env`

   * Args: `--profile`, `--tool-id` (optional).
   * Output: JSON dict of env key/values.

9. `resolve-tool`

   * Args: `--tool-id`, `--profile`, optional inline overrides.
   * Output: `ResolvedToolConfig` as JSON:

     ```json
     {
       "tool_id": "codex",
       "profile": "dev",
       "command": ["codex", "--fs", "workspace-write"],
       "env": { "OPENAI_API_KEY": "..." },
       "settings": { "model": "gpt-4.1" }
     }
     ```

**Note:** UI clients (including a TUI) must consume this CLI or the Python API. They should not re-implement resolution logic.

---

## 8. Error Handling & Validation

### 8.1 Validation Rules

* `ai-tools.registry.yaml`:

  * Each tool must have a unique `id`.
  * `type` must be one of known values (`cli`, `python`, `platform`).
  * Required fields by `type` must be present.
* Profiles:

  * `name` must match filename (`dev.yaml` → `name: dev` recommended).
  * Tools referenced under `tools:` must exist in registry.
* Secrets:

  * If `secrets/<profile>.env` is missing, warn but do not fail; caller can still run with partial env.

### 8.2 Error Types

Return structured errors (JSON) from CLI when appropriate:

```json
{
  "error": {
    "code": "TOOL_NOT_FOUND",
    "message": "Tool 'xyz' not defined in registry",
    "detail": { "tool_id": "xyz" }
  }
}
```

The TUI or scripts can display or log these; the core must not assume interactive handling.

---

## 9. Testing Strategy

### 9.1 Unit Tests (Python)

* `test_loader.py`:

  * Loading/saving YAML and `.env`.
* `test_tools_registry.py`:

  * Registry validation, duplicate detection, type checks.
* `test_profiles.py`:

  * Listing, loading, and active profile changes.
* `test_resolver.py`:

  * Resolution merging order.
  * Env filtering by `env_keys`.
  * Command construction by `type`.

### 9.2 Integration Tests

* Setup a temporary root directory with:

  * Dummy registry.
  * Profiles `dev`, `prod`.
  * `.env` files with test keys.
* Test:

  * `cli.py resolve-tool` outputs correct merged command and env.
  * PowerShell `Export-ProfileEnv.ps1` sets or generates expected env.
  * Changing `active-profile.yaml` changes default resolution behavior.

---

## 10. Implementation Plan (for Agentic AI)

1. **Create Python package `ai_steward_core`**

   * Implement `paths.py`, `loader.py`, `models.py`.
   * Implement `tools_registry.py`, `profiles.py`, `env_manager.py`.
   * Implement `resolver.py` using the merge logic above.

2. **Implement YAML/Env schemas & sample data**

   * Generate `ai-tools.registry.yaml` with at least:

     * `codex`, `crewai`, `langgraph`, `gptscript` as examples.
   * Create sample `profiles/dev.yaml` and `secrets/dev.env`.

3. **Implement CLI (`cli.py`)**

   * Use `argparse` or `click` to expose commands in section 7.
   * Ensure all outputs are JSON (except explicit help).

4. **Implement PowerShell wrappers**

   * `Export-ProfileEnv.ps1` and `Resolve-ToolCommand.ps1` that:

     * Call `python ai_steward_core/cli.py ...`
     * Interpret JSON and modify/use PowerShell env and commands.

5. **Write tests**

   * Python unit + integration tests as described.
   * Optional Pester tests for PowerShell wrappers.

6. **Document usage (developer docs)**

   * Explain the order of precedence for config resolution.
   * Provide examples of:

     * Adding a new tool to registry.
     * Adding a new profile.
     * Resolving and running a tool from PowerShell.

---

This specification is intentionally **UI-agnostic**.
Any TUI, web UI, or CLI with interactivity must treat the **config files and `ai_steward_core` APIs** as the single source of truth, and must not embed independent resolution logic.
