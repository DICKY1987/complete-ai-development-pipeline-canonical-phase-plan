---
doc_id: DOC-GUIDE-AIM-AI-STEWARD-920
---

Currentsub system location : "C:\Users\richg\ALL_AI\.AIM_ai-tools-registry"


treat that AIM_ai-steward thing as **“one more subsystem”** under the GUI, with two layers of integration:

1. **Under the hood**: the pipeline uses it as the *AI tool orchestrator*.
2. **In the GUI**: you get a dedicated panel + hooks in existing panels so a human can see what it’s doing.
---

## 1. Conceptual fit

Your GUI already has:

* `tools_client.py` + **Tools panel** → show and manage tools
* `terminal_panel.py` → embedded terminals
* Plugin architecture → easy to bolt on new panels

The AIM registry is:

* A **registry + router** for AI tools (jules, aider, claude-cli, etc.)
* Exposed via **PowerShell CLI** (`AIM_ai-steward.ps1`) and **module**
* Writes **JSON audit logs** you’d love to see in the GUI

So we integrate it as:

* A **new service**: `ai_registry_client.py`
* A **new panel plugin**: `ai_registry_panel.py`
* A **few enhancements** to `tools_client` / Tools panel and Terminal presets

---

## 2. Concrete file additions to the GUI tree

Add these:

```text
src/gui/services/ai_registry_client.py
src/gui/panels/ai_registry_panel.py
config/plugins/ai_registry.plugin.json
docs/AIM_INTEGRATION.md
```

### 2.1. `config/plugins/ai_registry.plugin.json`

A plugin manifest so the GUI shell knows about the panel:

```json
{
  "id": "ai_registry",
  "type": "panel",
  "title": "AI Tools Registry",
  "entry_point": "gui.panels.ai_registry_panel:AIRegistryPanel",
  "category": "Tools",
  "enabled_by_default": true,
  "order": 30,
  "requires_services": [
    "ai_registry_client",
    "logs_client",
    "config_client"
  ],
  "config": {
    "default_registry_root": "%USERPROFILE%/.AIM_ai-tools-registry"
  }
}
```

---

## 3. `ai_registry_client.py` – how the GUI talks to AIM

This service wraps the PowerShell steward CLI and hides all the ugly details from panels.

### 3.1. Responsibilities

* Run `status`, `validate`, `capability` commands via `subprocess`.
* Discover tools and capabilities from `AIM_registry.json`.
* Read **coordination rules** and expose them (primary vs fallback).
* Read **audit logs** from `AIM_audit/YYYY-MM-DD/*.json`.

### 3.2. Typical methods (Python signatures)

Rough outline:

```python
# src/gui/services/ai_registry_client.py

from pathlib import Path
from typing import List, Dict, Any, Optional

class AIRegistryClient:
    def __init__(self, gui_config, logger):
        self.registry_root = Path(
            gui_config.ai_registry.root
        )  # defaults to %USERPROFILE%/.AIM_ai-tools-registry
        self.steward_script = self.registry_root / "AIM_ai-steward" / "AIM_ai-steward.ps1"
        self.logger = logger

    def status(self) -> Dict[str, Any]:
        """
        Run: pwsh -File AIM_ai-steward.ps1 status --json
        Return parsed JSON with detected tools, versions, and health.
        """

    def validate(self) -> Dict[str, Any]:
        """
        Run: pwsh -File AIM_ai-steward.ps1 validate --json
        Return validation result (ok/errors) for registry and rules.
        """

    def invoke_capability(self, capability: str, payload: Dict[str, Any],
                          tool: Optional[str] = None) -> Dict[str, Any]:
        """
        Run a capability (e.g., code_generation) through the orchestrator.

        Equivalent PowerShell:
          pwsh -File AIM_ai-steward.ps1 capability <capability> '<json>' --json

        Returns stdout JSON: { success, content, message, tool_used, ... }.
        """

    def list_coordination_rules(self) -> Dict[str, Any]:
        """
        Read AIM_cross-tool/AIM_coordination-rules.json and return as dict.
        """

    def list_audit_files(self, date: Optional[str] = None) -> List[Path]:
        """
        List audit files under AIM_audit/YYYY-MM-DD/*.json.
        """

    def read_audit(self, audit_file: Path) -> Dict[str, Any]:
        """
        Load a single audit JSON snapshot for display.
        """
```

You’ll then register `ai_registry_client` as a service in whatever “service locator” your app_shell uses, so the panel can call it.

---

## 4. `ai_registry_panel.py` – a dedicated “AI Tools Registry” view

This panel gives the user a friendly, non-programmer view of what the registry is doing.

### 4.1. What it shows

Sections:

1. **Registry Summary**

   * Root path (`%USERPROFILE%/.AIM_ai-tools-registry` or overridden).
   * Last validation status (OK / Errors).
   * Button: **Validate registry** (runs `validate()` and shows results).

2. **Detected Tools Table**

   * Columns:

     * Tool name (jules, aider, claude-cli, …)
     * Version
     * Capabilities (e.g. `code_generation`, `summarization`)
     * Status (OK / Missing / Error)
   * Button per tool: **Run smoke test** (calls `status()` or a dedicated test via the steward if you add one).

3. **Capability Routing View**

   * Shows rules from `AIM_coordination-rules.json`, e.g.:

     | Capability      | Primary Tool | Fallback 1 | Fallback 2 |
     | --------------- | ------------ | ---------- | ---------- |
     | code_generation | jules        | aider      | claude-cli |

   * Maybe an info note: “The pipeline uses these choices when asking AI to write code.”

4. **Recent Audits**

   * List of the last N audit entries across `AIM_audit/YYYY-MM-DD/*.json`.
   * Columns:

     * Timestamp
     * Capability
     * Tool used
     * Success/failure
     * Short message
   * Click → show detailed JSON in a side panel (read-only).

### 4.2. What it can *do* (Permissions)

Hook into your permissions matrix like this:

* Allowed:

  * Call `status`, `validate`, `invoke_capability` (for tests, not general UX).
  * Read registry, rules, and audits.
* Not allowed:

  * Directly edit `AIM_registry.json` or rules.
  * Directly edit adapter scripts.

The panel can provide **“Open in File Explorer”** links to those files if the user wants to edit them manually.

---

## 5. Integrating with the existing Tools & Terminal panels

### 5.1. Tools panel: show the registry as a tool

In `tools_client.py`, treat AIM as a **special tool**:

* Add an entry like:

  * Name: “AI Tools Registry (AIM)”
  * Type: “orchestrator”
  * Health: from `ai_registry_client.status()`
* In the Tools panel:

  * Show this orchestrator at the top.
  * Clicking it can:

    * Jump to the AI Registry panel, **or**
    * Show a quick summary inline.

This makes it obvious that jules/aider/claude aren’t just random CLIs; they’re behind a managed registry.

### 5.2. Terminal panel: preset for AIM steward

Add a preset to `env_profiles.yaml` or a separate `terminal_presets` file:

```yaml
presets:
  - id: aim_steward
    label: "AI Tools Registry (Steward CLI)"
    shell: "pwsh"
    working_dir: "C:\\Users\\richg\\.AIM_ai-tools-registry\\AIM_ai-steward"
    prelude: ""
    command: "pwsh -File .\\AIM_ai-steward.ps1"
```

User flow:

* Open **Terminal** panel.
* Click **New Tab → AI Tools Registry (Steward CLI)**.
* They get a live CLI session with all `status`, `validate`, and `capability` commands at their fingertips, for power use beyond the simple GUI.

---

## 6. Using AIM underneath the pipeline’s AI tools

This is the deeper integration: teaching the **pipeline engine** to go through AIM when it wants AI help.

### 6.1. In `tool_profiles.json` (pipeline side)

Instead of having separate entries like “aider”, “claude-cli”, etc., you can define a **single “ai_codegen” tool** that calls the steward:

```json
{
  "ai_codegen": {
    "type": "process",
    "command": "pwsh",
    "args": [
      "-File",
      "C:\\Users\\richg\\.AIM_ai-tools-registry\\AIM_ai-steward\\AIM_ai-steward.ps1",
      "capability",
      "code_generation",
      "{payload_json}",
      "--json"
    ],
    "working_dir": "{repo_root}",
    "timeout_sec": 600,
    "capture_output": true,
    "success_exit_codes": [0]
  }
}
```

The pipeline:

* Creates a payload JSON describing the code task (files, spec snippet, etc.).
* Calls `run_tool("ai_codegen", payload_json=...)`.
* The **steward** picks the right tool (jules → aider → claude-cli fallback).
* Audit logs are written by AIM and can be viewed in your **AI Registry panel**.

From the GUI side:

* The Tools panel shows “AI Codegen (via AIM)” as one tool.
* The AI Registry panel gives more detail (which underlying tools, routing, audits).

---

## 7. A small integration doc for agents

It’s worth adding `docs/AIM_INTEGRATION.md` with the essentials:

* Where the registry lives (`%USERPROFILE%/.AIM_ai-tools-registry`).
* How `ai_registry_client` calls it.
* Which panels depend on it.
* How pipeline tools use AIM via `tool_profiles.json`.

That way an agentic AI has a **single place** to understand the integration before touching code.

---

### TL;DR

To integrate your PowerShell-based AI tools registry into the GUI:

1. Add an **`ai_registry_client` service** that wraps `AIM_ai-steward.ps1` (status, validate, capability, audits).
2. Add an **AI Tools Registry panel** (plugin) that shows:

   * Detected tools, capabilities, routing rules, and recent audits,
   * Buttons for status/validate.
3. Enhance:

   * **Tools panel** to show AIM as an orchestrator tool, and
   * **Terminal panel** with a preset that opens the Steward CLI.
4. Optionally route all pipeline AI editing through AIM via a single `ai_codegen` tool entry in `tool_profiles.json`.

This keeps non-programmer UX simple (“there’s one AI Codegen engine, here’s its health & history”) while giving you all the power and auditability of the registry underneath.

Currentsub system location : "C:\Users\richg\ALL_AI\.AIM_ai-tools-registry"
