TITLE: PH-08 – AIM Tool Registry Integration (Codex Autonomous Phase Executor)

ROLE
You are Codex running with full access to a Windows development environment using PowerShell and Git.
Your job is to COMPLETELY IMPLEMENT phase PH-08 (AIM Tool Registry Integration) for the AI Development Pipeline project, end-to-end, without requiring further user input.

You will:
- Integrate the .AIM_ai-tools-registry system into the pipeline.
- Implement Python-to-PowerShell bridge for AIM adapters.
- Add capability-based tool routing with fallback chains.
- Implement audit logging for all tool invocations.
- Extend existing tool profiles with AIM metadata.
- Keep existing tool_profiles.json working while adding AIM layer.

OPERATING CONTEXT
- OS: Windows 10/11
- Shell: PowerShell 7+ (pwsh)
- Version control: git
- Orchestrator language: Python 3.12+
- AIM Registry: PowerShell-based with JSON config
- Previous phases:
  - PH-00: project skeleton, docs, CI.
  - PH-01: spec index & canonical module layout.
  - PH-02: SQLite DB + state machine (db.py).
  - PH-03: Tool profiles & adapter layer (tool_profiles.json, tools.py).
  - PH-03.5: Aider integration & prompt engine.

PROJECT ROOT (IMPORTANT)
- Expected project root: C:\Users\richg\ALL_AI\AI_Dev_Pipeline
- AIM Registry location: C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\.AIM_ai-tools-registry

If project root does NOT exist:
- Stop and write a clear, prominent note into docs/PHASE_PLAN.md under PH-08 that PH-00–PH-03 must be completed first.
- Do NOT attempt to implement AIM integration elsewhere.

If it DOES exist:
- cd into that folder and proceed.

====================================
HIGH-LEVEL GOAL OF PH-08
====================================

Integrate AIM (AI Tools Registry) to provide:

1) **Capability-based routing**: Route tasks to tools based on capabilities (e.g., "code_generation", "refactoring", "testing").
2) **Fallback chains**: If primary tool fails, try fallback tools automatically.
3) **Audit logging**: Record all tool invocations with timestamps, inputs, outputs, and results.
4) **Tool discovery**: Automatically detect installed tools using AIM detection commands.
5) **PowerShell adapter bridge**: Invoke PowerShell AIM adapters from Python pipeline.
6) **Backward compatibility**: Keep existing tool_profiles.json working; AIM is an enhancement layer.

You are NOT replacing the existing tool adapter (tools.py); you are **extending** it with AIM capabilities.

====================================
REQUIRED OUTPUTS OF THIS PHASE
====================================

By the end of PH-08, the repo MUST have at minimum:

1) AIM INTEGRATION CONTRACT DOCUMENT
- docs/AIM_INTEGRATION_CONTRACT.md
  - Explains the relationship between pipeline and AIM registry.
  - Documents:
    - How AIM registry is structured (registry.json, adapters, coordination rules).
    - How Python pipeline invokes PowerShell adapters.
    - Capability routing logic.
    - Audit log format and location.
    - Environment variables required (AIM_REGISTRY_PATH).
    - Error handling and fallback behavior.
    - Contract version (e.g., "AIM_INTEGRATION_V1").

2) AIM BRIDGE MODULE
- src/pipeline/aim_bridge.py
  - Responsibilities:
    - Load AIM_registry.json.
    - Load AIM coordination rules.
    - Invoke PowerShell AIM adapters via subprocess.
    - Parse JSON input/output for adapters.
    - Handle capability routing.
    - Implement fallback chains.
    - Record audit logs.

  - Core functions:

    1) get_aim_registry_path() -> Path
       - Returns path to AIM registry directory.
       - Uses environment variable AIM_REGISTRY_PATH if set.
       - Else defaults to ../Complete AI Development Pipeline – Canonical Phase Plan/.AIM_ai-tools-registry relative to repo root.
       - Raises clear error if not found.

    2) load_aim_registry() -> dict
       - Loads AIM_registry.json.
       - Returns parsed dict with tools metadata.

    3) load_coordination_rules() -> dict
       - Loads AIM_cross-tool/AIM_coordination-rules.json.
       - Returns routing rules (primary, fallbacks, load balancing).

    4) invoke_adapter(tool_id: str, capability: str, payload: dict) -> dict
       - Builds JSON input: {"capability": capability, "payload": payload}.
       - Invokes PowerShell adapter script via subprocess:
         - echo '<json>' | pwsh -File <adapter_script_path>
       - Parses JSON output: {"success": bool, "message": str, "content": any}.
       - Returns result dict.
       - Handles errors: non-zero exit, invalid JSON, timeout.

    5) route_capability(capability: str, payload: dict) -> dict
       - Uses coordination rules to select primary tool for capability.
       - Invokes primary tool's adapter.
       - On failure, tries fallback tools in order.
       - Returns result from first successful tool.
       - Logs all attempts to audit log.

    6) detect_tool(tool_id: str) -> bool
       - Runs detectCommands from registry for given tool.
       - Returns True if any detect command succeeds (exit code 0).
       - Returns False otherwise.

    7) get_tool_version(tool_id: str) -> str | None
       - Runs versionCommand from registry for given tool.
       - Parses and returns version string.
       - Returns None if command fails.

    8) record_audit_log(tool_id: str, capability: str, payload: dict, result: dict) -> None
       - Appends audit entry to AIM_audit/<YYYY-MM-DD>/<timestamp>_<tool_id>_<capability>.json.
       - Entry includes:
         - timestamp (ISO 8601 UTC)
         - actor (e.g., "pipeline")
         - tool_id
         - capability
         - payload (input)
         - result (output from adapter)
       - Creates directory if needed.

3) EXTENDED TOOL PROFILES
- Modify config/tool_profiles.json to include:
  - "aim_tool_id" field (optional) linking to AIM registry tool.
  - "aim_capabilities" list (optional) specifying what this tool can do.

  Example:
  ```json
  {
    "aider": {
      "type": "ai",
      "command": "aider",
      "args": ["--no-auto-commits", "--yes"],
      "aim_tool_id": "aider",
      "aim_capabilities": ["code_generation", "refactoring"]
    }
  }
  ```

- Keep existing tool profiles working for backward compatibility.
- AIM fields are optional; if present, aim_bridge.py uses them.

4) ENHANCED TOOLS.PY INTEGRATION
- Modify src/pipeline/tools.py to optionally use AIM:

  - Add function: run_tool_via_aim(tool_id: str, capability: str, payload: dict, run_id=None, ws_id=None) -> ToolResult
    - Calls aim_bridge.route_capability(capability, payload).
    - Converts AIM result to ToolResult.
    - Records to DB (events/errors) if run_id/ws_id provided.
    - Falls back to run_tool() if AIM unavailable or disabled.

  - Add configuration flag in tool profile or global config:
    - "use_aim": true/false
    - If true, use AIM routing; if false, use direct invocation.

5) AIM CONFIGURATION
- config/aim_config.yaml
  - AIM-specific settings:
    - registry_path: path to AIM registry (overrides default)
    - enable_aim: true/false (global enable/disable)
    - enable_audit_logging: true/false
    - audit_log_retention_days: 30
    - default_timeout_ms: 30000
  - Validate on load.

6) CAPABILITY CATALOG
- docs/AIM_CAPABILITIES_CATALOG.md
  - Documents all known capabilities:
    - code_generation
    - refactoring
    - testing
    - linting
    - version_checking
  - For each capability:
    - Description
    - Expected payload schema
    - Expected result schema
    - Which tools support it (from AIM registry)
  - This is a living document; update as new capabilities are added.

7) UNIT TESTS
- tests/pipeline/test_aim_bridge.py
  - Mock AIM registry and coordination rules.
  - Test:
    - load_aim_registry() with valid/invalid JSON.
    - load_coordination_rules() with valid/invalid JSON.
    - invoke_adapter() with mocked subprocess (success, failure, timeout).
    - route_capability() with primary success, primary fail + fallback success, all fail.
    - detect_tool() with mocked subprocess.
    - get_tool_version() with mocked subprocess.
    - record_audit_log() writes to temp directory.

- tests/pipeline/test_tools_aim_integration.py
  - Test run_tool_via_aim() with mocked aim_bridge.
  - Test fallback to run_tool() when AIM disabled.
  - Test ToolResult conversion from AIM result.

8) INTEGRATION TESTS
- tests/integration/test_aim_end_to_end.py
  - Mark with pytest.mark.slow or pytest.mark.aim.
  - Tests should:
    - Check if AIM registry is available (skip if not).
    - Check if at least one tool is installed (e.g., aider).
    - Invoke capability via route_capability().
    - Verify result success.
    - Verify audit log created.

9) CLI UTILITIES
- scripts/aim_status.py
  - Runnable as:
    - python scripts/aim_status.py
  - Behavior:
    - Loads AIM registry.
    - For each tool in registry:
      - Run detect_tool().
      - If detected, run get_tool_version().
      - Print: tool_id, detected (yes/no), version.
    - Print capability routing summary (which tools handle which capabilities).

- scripts/aim_audit_query.py
  - Runnable as:
    - python scripts/aim_audit_query.py --tool TOOL_ID --capability CAPABILITY --since YYYY-MM-DD
  - Behavior:
    - Loads audit logs from AIM_audit/.
    - Filters by tool, capability, date range.
    - Prints summary or exports to JSON/CSV.

10) DOCUMENTATION UPDATES
- docs/ARCHITECTURE.md:
  - Add "AIM Tool Registry Integration" section describing:
    - Role of AIM as capability routing layer.
    - How aim_bridge.py interfaces with PowerShell adapters.
    - Capability-based routing and fallback chains.
    - Audit logging for tool invocations.
    - Relationship with existing tools.py.

- docs/PHASE_PLAN.md:
  - Flesh out PH-08 section with:
    - Summary of AIM integration.
    - List of artifacts:
      - docs/AIM_INTEGRATION_CONTRACT.md
      - docs/AIM_CAPABILITIES_CATALOG.md
      - config/aim_config.yaml
      - src/pipeline/aim_bridge.py
      - Modified config/tool_profiles.json
      - Modified src/pipeline/tools.py
      - scripts/aim_status.py
      - scripts/aim_audit_query.py
      - tests/pipeline/test_aim_bridge.py
      - tests/integration/test_aim_end_to_end.py
    - Note: AIM is optional enhancement; existing tool profiles work without it.

11) GIT COMMIT
- Stage all new/modified files.
- Commit with message:
  - "PH-08: AIM tool registry integration"
- Do NOT push (remote configuration is out of scope).

====================================
CONSTRAINTS & PRINCIPLES
====================================

- Do NOT break or remove outputs from PH-00–PH-03.5; only extend them.
- Backward compatibility:
  - Existing tool_profiles.json entries must work unchanged.
  - AIM is an optional layer; pipeline works without it.
- PowerShell invocation safety:
  - Always escape/quote JSON strings properly when passing to pwsh.
  - Set timeout to prevent hung processes.
  - Handle stderr and non-zero exit codes gracefully.
- AIM registry is external:
  - Do not modify .AIM_ai-tools-registry files; only read them.
  - If registry missing, degrade gracefully (log warning, use direct tool invocation).
- Audit logging:
  - Do not log secrets or sensitive data in audit logs.
  - Rotate/clean old logs based on retention policy.
- Capability routing:
  - If no tool supports a capability, raise clear error (don't fail silently).
  - If all tools fail, return error result (don't crash).

Implementation details:
- Use subprocess.run() to invoke PowerShell scripts.
- Use json module to encode/decode payloads.
- Use pathlib.Path for all file paths.
- Use environment variable AIM_REGISTRY_PATH for flexibility.
- For audit logs, use ISO 8601 timestamps with "Z" suffix (UTC).

====================================
EXECUTION PLAN (WHAT YOU SHOULD DO)
====================================

You should:

1) PRECHECKS & NAVIGATION
   - Confirm C:\Users\richg\ALL_AI\AI_Dev_Pipeline exists.
   - cd C:\Users\richg\ALL_AI\AI_Dev_Pipeline
   - Confirm .AIM_ai-tools-registry exists at expected location.
   - Confirm src/pipeline/, docs/, config/ exist; if not, create them and note in docs/PHASE_PLAN.md that earlier phases may be incomplete.

2) WRITE AIM INTEGRATION CONTRACT DOC
   - Create docs/AIM_INTEGRATION_CONTRACT.md with:
     - Overview of AIM registry.
     - Python-to-PowerShell bridge design.
     - Capability routing logic.
     - Audit log format.
     - Environment variables.
     - Error handling.
     - Contract version.

3) IMPLEMENT AIM BRIDGE MODULE
   - Create src/pipeline/aim_bridge.py with:
     - get_aim_registry_path()
     - load_aim_registry()
     - load_coordination_rules()
     - invoke_adapter()
     - route_capability()
     - detect_tool()
     - get_tool_version()
     - record_audit_log()

4) EXTEND TOOL PROFILES
   - Modify config/tool_profiles.json to add:
     - "aim_tool_id" field to existing tools (aider, etc.).
     - "aim_capabilities" list.
   - Keep existing fields intact.

5) ENHANCE TOOLS.PY
   - Modify src/pipeline/tools.py to add:
     - run_tool_via_aim() function.
     - Logic to check "use_aim" flag and route accordingly.

6) CREATE AIM CONFIG
   - Create config/aim_config.yaml with:
     - registry_path, enable_aim, enable_audit_logging, audit_log_retention_days, default_timeout_ms.

7) WRITE CAPABILITIES CATALOG
   - Create docs/AIM_CAPABILITIES_CATALOG.md with:
     - List of known capabilities.
     - Payload/result schemas.
     - Tool support matrix.

8) ADD TESTS
   - Implement tests/pipeline/test_aim_bridge.py.
   - Implement tests/pipeline/test_tools_aim_integration.py.
   - Implement tests/integration/test_aim_end_to_end.py.

9) ADD CLI UTILITIES
   - Create scripts/aim_status.py.
   - Create scripts/aim_audit_query.py.

10) RUN TESTS
    - From project root:
      - Run: pytest tests/pipeline/test_aim_bridge.py
      - Run: pytest tests/pipeline/test_tools_aim_integration.py
      - Run: pytest tests/integration/test_aim_end_to_end.py --slow (if AIM available)
    - Fix any failing tests before marking PH-08 complete.

11) UPDATE DOCS
    - Update docs/ARCHITECTURE.md with AIM integration section.
    - Update docs/PHASE_PLAN.md with detailed PH-08 description.

12) GIT COMMIT
    - Stage and commit with message:
      - "PH-08: AIM tool registry integration"

====================================
PHASE COMPLETION CHECKLIST
====================================

Before you consider PH-08 done, ensure all of the following are true:

[ ] docs/AIM_INTEGRATION_CONTRACT.md exists and documents integration contract, capability routing, audit logging, and contract version
[ ] docs/AIM_CAPABILITIES_CATALOG.md exists and lists known capabilities with schemas and tool support
[ ] config/aim_config.yaml exists with AIM configuration settings
[ ] src/pipeline/aim_bridge.py implements:
    - get_aim_registry_path()
    - load_aim_registry()
    - load_coordination_rules()
    - invoke_adapter()
    - route_capability()
    - detect_tool()
    - get_tool_version()
    - record_audit_log()
[ ] config/tool_profiles.json extended with aim_tool_id and aim_capabilities fields
[ ] src/pipeline/tools.py extended with run_tool_via_aim() function
[ ] scripts/aim_status.py provides tool detection and status summary
[ ] scripts/aim_audit_query.py provides audit log querying
[ ] tests/pipeline/test_aim_bridge.py exists and passes
[ ] tests/pipeline/test_tools_aim_integration.py exists and passes
[ ] tests/integration/test_aim_end_to_end.py exists and passes (or skips gracefully if AIM unavailable)
[ ] docs/ARCHITECTURE.md has an "AIM Tool Registry Integration" section
[ ] docs/PHASE_PLAN.md has an updated PH-08 section listing artifacts and behavior
[ ] A git commit with message like "PH-08: AIM tool registry integration" has been created

====================================
INTERACTION STYLE
====================================

- Do NOT ask the user questions unless you are completely blocked.
- Make reasonable assumptions and document them in:
  - docs/AIM_INTEGRATION_CONTRACT.md
  - docs/AIM_CAPABILITIES_CATALOG.md
  - docs/PHASE_PLAN.md (PH-08 section)
- When you output your response, clearly separate:
  - PowerShell commands you would run.
  - Python, YAML, JSON, and Markdown file contents you would create or modify.

END OF PROMPT
