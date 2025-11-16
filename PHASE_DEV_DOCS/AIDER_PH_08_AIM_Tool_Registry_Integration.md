---
workstream_id: ph-08-aim-integration
phase: PH-08
difficulty: medium
version_target: v1.0
depends_on: [PH-03, PH-03.5]
writable_globs:
  - "src/pipeline/aim_bridge.py"
  - "config/tool_profiles.json"
  - "config/aim_config.yaml"
  - "docs/AIM_INTEGRATION_CONTRACT.md"
  - "docs/AIM_CAPABILITIES_CATALOG.md"
  - "scripts/aim_status.py"
  - "scripts/aim_audit_query.py"
  - "tests/pipeline/test_aim_bridge.py"
  - "tests/pipeline/test_tools_aim_integration.py"
  - "tests/integration/test_aim_end_to_end.py"
readonly_globs:
  - "src/pipeline/tools.py"
  - "../Complete AI Development Pipeline – Canonical Phase Plan/.AIM_ai-tools-registry/**/*.json"
  - "../Complete AI Development Pipeline – Canonical Phase Plan/.AIM_ai-tools-registry/**/*.ps1"
---

# PH-08 – AIM Tool Registry Integration (Aider Workstream)

## 1. HEADER SUMMARY

**Workstream ID:** ph-08-aim-integration
**Phase Reference:** PH-08
**Difficulty:** medium
**Version Target:** v1.0
**Dependencies:** PH-03 (tool profiles), PH-03.5 (Aider integration)

## 2. ROLE & OBJECTIVE

Integrate the .AIM_ai-tools-registry PowerShell-based tool coordination system into the Python pipeline. Enable capability-based routing (e.g., "code_generation" → aider), fallback chains (if primary tool fails, try fallback), and audit logging for all tool invocations. This file governs only the artifacts listed in Scope.

**Mission:** Create a Python-to-PowerShell bridge that extends the existing tool adapter (tools.py) with AIM capabilities while maintaining backward compatibility—existing tool_profiles.json entries work unchanged.

## 3. SCOPE & FILE BOUNDARIES

### Writable Paths
```
src/pipeline/aim_bridge.py
config/tool_profiles.json (extend, not replace)
config/aim_config.yaml
docs/AIM_INTEGRATION_CONTRACT.md
docs/AIM_CAPABILITIES_CATALOG.md
scripts/aim_status.py
scripts/aim_audit_query.py
tests/pipeline/test_aim_bridge.py
tests/pipeline/test_tools_aim_integration.py
tests/integration/test_aim_end_to_end.py
```

### Read-only Reference Paths
```
src/pipeline/tools.py
src/pipeline/db.py
../Complete AI Development Pipeline – Canonical Phase Plan/.AIM_ai-tools-registry/AIM_registry.json
../Complete AI Development Pipeline – Canonical Phase Plan/.AIM_ai-tools-registry/AIM_cross-tool/AIM_coordination-rules.json
../Complete AI Development Pipeline – Canonical Phase Plan/.AIM_ai-tools-registry/AIM_adapters/*.ps1
```

### Explicitly Out of Scope
- **Do NOT** modify .AIM_ai-tools-registry files (external registry, read-only)
- **Do NOT** modify src/pipeline/tools.py (only extend via new module)
- **Do NOT** modify src/pipeline/db.py
- **Do NOT** change existing tool_profiles.json entries (only add optional fields)
- **Do NOT** implement new PowerShell adapters (use existing AIM adapters)

**Note:** All non-listed files must remain unchanged.

## 4. ENVIRONMENT & PRECONDITIONS

**Project Root:** C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan
**Operating System:** Windows 10/11
**Python Version:** 3.12+
**PowerShell Version:** 7+
**Shell:** PowerShell (pwsh)
**Version Control:** git

**Required Prior Phases:**
- PH-00: Project skeleton
- PH-01: Spec index
- PH-02: SQLite DB
- PH-03: Tool profiles & adapter (tools.py, tool_profiles.json)
- PH-03.5: Aider integration

**Required Tools:**
- python (3.12+)
- pwsh (PowerShell 7+)
- pytest
- jsonschema (for validation)
- PyYAML (for config)

**External Dependency:**
- AIM registry must exist at: `C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan\.AIM_ai-tools-registry`
- If missing: set AIM_REGISTRY_PATH env var or document graceful degradation

**Dependency Check:**
If AIM registry missing:
- Log warning to console
- Set enable_aim=false in aim_config.yaml
- Fall back to direct tool invocation via tools.py
- **Do NOT** fail or block pipeline operation

## 5. TARGET ARTIFACTS & ACCEPTANCE CRITERIA

### [ARTIFACT] docs/AIM_INTEGRATION_CONTRACT.md
**Type:** doc
**Purpose:** Integration contract between pipeline and AIM registry
**Must Provide:**
- Overview of AIM registry structure (registry.json, adapters, coordination rules)
- Python-to-PowerShell invocation pattern
- Capability routing logic (primary → fallback chain)
- Audit log format and location
- Environment variables (AIM_REGISTRY_PATH)
- Error handling and degradation strategy
- Contract version (AIM_INTEGRATION_V1)

**Must Not:**
- Specify AIM adapter implementation details
- Require modifications to AIM registry files

**Acceptance Tests:**
- Doc exists and includes all 7 sections
- Contract version documented

**Determinism:**
- Sections ordered: Overview, Structure, Invocation, Routing, Audit, Environment, Errors, Version

---

### [ARTIFACT] docs/AIM_CAPABILITIES_CATALOG.md
**Type:** doc
**Purpose:** Catalog of known capabilities with schemas
**Must Provide:**
- List of capabilities: code_generation, refactoring, testing, linting, version_checking
- For each capability:
  - Description
  - Expected payload schema (JSON example)
  - Expected result schema (JSON example)
  - Which tools support it (from AIM registry)
  - Example usage

**Must Not:**
- Hardcode tool names (read from registry dynamically)
- Include implementation details

**Acceptance Tests:**
- Doc exists with ≥5 capabilities documented
- Each capability has payload/result schema

**Determinism:**
- Capabilities sorted alphabetically
- Schema examples use stable field order

---

### [ARTIFACT] config/aim_config.yaml
**Type:** config
**Purpose:** AIM-specific settings
**Must Provide:**
- registry_path: path to AIM registry (default: auto-detect)
- enable_aim: true/false (global enable/disable)
- enable_audit_logging: true/false
- audit_log_retention_days: 30
- default_timeout_ms: 30000

**Must Not:**
- Contain secrets or credentials
- Override tool_profiles.json settings

**Acceptance Tests:**
- YAML parses successfully
- All required keys present
- Paths valid (absolute or repo-relative)

**Determinism:**
- Keys alphabetically sorted
- Comments explain each setting

---

### [ARTIFACT] src/pipeline/aim_bridge.py
**Type:** code
**Purpose:** Python-to-PowerShell bridge for AIM adapters
**Must Provide:**
- Functions:
  - get_aim_registry_path() -> Path
  - load_aim_registry() -> dict
  - load_coordination_rules() -> dict
  - invoke_adapter(tool_id, capability, payload) -> dict
  - route_capability(capability, payload) -> dict
  - detect_tool(tool_id) -> bool
  - get_tool_version(tool_id) -> str | None
  - record_audit_log(tool_id, capability, payload, result) -> None

**Must Not:**
- Modify AIM registry files
- Call tools directly (use PowerShell adapters)
- Block on long-running operations (set timeout)

**Acceptance Tests:**
- test_load_aim_registry (tests/pipeline/test_aim_bridge.py)
- test_invoke_adapter_success
- test_invoke_adapter_timeout
- test_route_capability_primary_success
- test_route_capability_fallback_success
- test_detect_tool
- test_record_audit_log

**Determinism:**
- invoke_adapter() escapes JSON strings consistently
- Timestamps in audit logs use ISO 8601 UTC with "Z" suffix
- Fallback chain order preserved from coordination rules

---

### [ARTIFACT] config/tool_profiles.json (extended)
**Type:** config
**Purpose:** Add AIM metadata to existing tool profiles
**Must Provide:**
- Add optional fields to existing entries:
  - "aim_tool_id": string (links to AIM registry tool)
  - "aim_capabilities": array of strings
- Keep all existing fields unchanged

**Example:**
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

**Must Not:**
- Remove or modify existing fields
- Break backward compatibility

**Acceptance Tests:**
- JSON parses successfully
- Existing tools still work without AIM fields
- AIM fields validate correctly when present

**Determinism:**
- Preserve original field order, append AIM fields at end

---

### [ARTIFACT] scripts/aim_status.py
**Type:** script
**Purpose:** CLI utility for AIM tool detection
**Must Provide:**
- Command: `python scripts/aim_status.py`
- Behavior:
  - Load AIM registry
  - For each tool: detect_tool(), get_tool_version()
  - Print table: tool_id | detected | version
  - Print capability routing summary

**Must Not:**
- Modify registry or tool state
- Require interactive input

**Acceptance Tests:**
- Script runs without error
- Output includes all tools from registry
- Returns exit code 0

---

### [ARTIFACT] scripts/aim_audit_query.py
**Type:** script
**Purpose:** Query AIM audit logs
**Must Provide:**
- Command: `python scripts/aim_audit_query.py --tool TOOL --capability CAP --since YYYY-MM-DD`
- Behavior:
  - Load audit logs from AIM_audit/ directory
  - Filter by tool, capability, date range
  - Print summary or export to JSON/CSV

**Must Not:**
- Modify audit logs
- Require write access to audit directory

**Acceptance Tests:**
- Script runs with filters
- Handles missing audit logs gracefully
- Exports valid JSON/CSV

---

### [ARTIFACT] tests/pipeline/test_aim_bridge.py
**Type:** test
**Purpose:** Unit tests for aim_bridge module
**Must Provide:**
- Mock AIM registry and coordination rules
- Test cases:
  - load_aim_registry() with valid/invalid JSON
  - load_coordination_rules() with valid/invalid JSON
  - invoke_adapter() with mocked subprocess (success, failure, timeout)
  - route_capability() with primary success, fallback success, all fail
  - detect_tool() with mocked subprocess
  - get_tool_version() with mocked subprocess
  - record_audit_log() writes to temp directory

**Acceptance Tests:**
- `pytest tests/pipeline/test_aim_bridge.py -v` passes

---

### [ARTIFACT] tests/integration/test_aim_end_to_end.py
**Type:** test
**Purpose:** Integration test for AIM system
**Must Provide:**
- Mark with @pytest.mark.aim
- Skip if AIM registry not available
- Test:
  - Invoke capability via route_capability()
  - Verify audit log created
  - Verify result structure

**Acceptance Tests:**
- `pytest tests/integration/test_aim_end_to_end.py -v` passes or skips gracefully

## 6. OPERATIONS SEQUENCE (Atomic Steps)

### Step 1: Design AIM Bridge Architecture
**Intent:** Plan Python-PowerShell integration
**Files:** /read-only ../Complete AI Development Pipeline – Canonical Phase Plan/.AIM_ai-tools-registry/AIM_registry.json
**Command:** `/architect`
**Prompt:**
```
Design Python bridge for PowerShell AIM registry with:

1. Registry loading (read AIM_registry.json, coordination-rules.json)
2. Adapter invocation (echo JSON | pwsh -File adapter.ps1)
3. Capability routing (primary → fallback chain)
4. Audit logging (write to AIM_audit/<date>/*.json)
5. Tool detection (run detectCommands, versionCommand)

Constraints:
- Read-only access to AIM registry
- Subprocess for PowerShell invocation
- Timeout handling (30s default)
- Graceful degradation if AIM unavailable

Output: Function signatures + error handling strategy
```
**Expected Outcome:** Architecture design documented
**Commit:** N/A (design step)

---

### Step 2: Implement AIM Integration Contract
**Intent:** Document integration contract
**Files:** /add docs/AIM_INTEGRATION_CONTRACT.md
**Command:** `/code`
**Prompt:**
```
Create docs/AIM_INTEGRATION_CONTRACT.md with:

Sections:
1. Overview (what is AIM registry)
2. Registry Structure (registry.json, adapters/*.ps1, coordination-rules.json)
3. Invocation Pattern (echo JSON | pwsh -File adapter.ps1)
4. Capability Routing Logic (primary → fallbacks)
5. Audit Log Format (ISO 8601, fields: timestamp, actor, tool_id, capability, payload, result)
6. Environment Variables (AIM_REGISTRY_PATH)
7. Error Handling (degradation strategy, timeout, invalid JSON)
8. Contract Version (AIM_INTEGRATION_V1)

Constraints:
- Markdown format
- Code examples for JSON I/O
- Clear error scenarios

Determinism:
- Sections in order listed
- Examples use stable data
```
**Expected Outcome:** Complete contract document
**Commit:** `docs(ph-08): add AIM integration contract`

---

### Step 3: Implement Capabilities Catalog
**Intent:** Document known capabilities
**Files:** /add docs/AIM_CAPABILITIES_CATALOG.md
**Command:** `/code`
**Prompt:**
```
Create docs/AIM_CAPABILITIES_CATALOG.md with:

Capabilities (alphabetically):
1. code_generation
2. linting
3. refactoring
4. testing
5. version_checking

For each:
- Description (1-2 sentences)
- Payload schema (JSON example)
- Result schema (JSON example)
- Supported tools (read from AIM registry if possible, else placeholder)
- Example usage

Constraints:
- Markdown format with JSON code blocks
- Stable schema field order

Determinism:
- Capabilities alphabetically sorted
- Schema examples formatted with 2-space indent
```
**Expected Outcome:** Capabilities catalog
**Commit:** `docs(ph-08): add AIM capabilities catalog`

---

### Step 4: Implement AIM Config
**Intent:** Create AIM configuration file
**Files:** /add config/aim_config.yaml
**Command:** `/code`
**Prompt:**
```
Create config/aim_config.yaml:

registry_path: "auto"  # Auto-detect or set to path
enable_aim: true
enable_audit_logging: true
audit_log_retention_days: 30
default_timeout_ms: 30000

Comments:
- Explain each setting
- Note: "auto" detects registry relative to repo

Determinism:
- Keys alphabetically sorted
- Inline comments for each key
```
**Expected Outcome:** AIM config file
**Commit:** `config(ph-08): add AIM configuration`

---

### Step 5: Implement get_aim_registry_path
**Intent:** Locate AIM registry directory
**Files:** /add src/pipeline/aim_bridge.py
**Command:** `/code`
**Prompt:**
```
Implement get_aim_registry_path() in src/pipeline/aim_bridge.py:

Logic:
1. Check env var AIM_REGISTRY_PATH
2. If set, return Path(AIM_REGISTRY_PATH)
3. Else, auto-detect relative to repo:
   - repo_root = Path(__file__).parent.parent.parent
   - aim_path = repo_root / ".." / "Complete AI Development Pipeline – Canonical Phase Plan" / ".AIM_ai-tools-registry"
4. Verify directory exists, else raise FileNotFoundError with clear message

Return: Path object

Constraints:
- Use pathlib.Path
- Clear error message if not found
- No side effects (pure function)
```
**Expected Outcome:** get_aim_registry_path() function
**Commit:** `feat(ph-08): implement AIM registry path resolution`

---

### Step 6: Implement load_aim_registry
**Intent:** Load AIM_registry.json
**Files:** /add src/pipeline/aim_bridge.py
**Command:** `/code`
**Prompt:**
```
Implement load_aim_registry() in src/pipeline/aim_bridge.py:

Logic:
1. aim_path = get_aim_registry_path()
2. registry_file = aim_path / "AIM_registry.json"
3. with open(registry_file) as f: data = json.load(f)
4. Return data

Error Handling:
- FileNotFoundError: raise with message
- JSONDecodeError: raise with file path

Return: dict

Constraints:
- Import json
- Use pathlib.Path
```
**Expected Outcome:** load_aim_registry() function
**Commit:** `feat(ph-08): implement AIM registry loader`

---

### Step 7: Implement load_coordination_rules
**Intent:** Load coordination-rules.json
**Files:** /add src/pipeline/aim_bridge.py
**Command:** `/code`
**Prompt:**
```
Implement load_coordination_rules() in src/pipeline/aim_bridge.py:

Logic:
1. aim_path = get_aim_registry_path()
2. rules_file = aim_path / "AIM_cross-tool" / "AIM_coordination-rules.json"
3. with open(rules_file) as f: data = json.load(f)
4. Return data

Return: dict

Constraints:
- Same error handling as load_aim_registry()
```
**Expected Outcome:** load_coordination_rules() function
**Commit:** `feat(ph-08): implement coordination rules loader`

---

### Step 8: Implement invoke_adapter
**Intent:** Invoke PowerShell adapter via subprocess
**Files:** /add src/pipeline/aim_bridge.py
**Command:** `/code`
**Prompt:**
```
Implement invoke_adapter(tool_id, capability, payload) in src/pipeline/aim_bridge.py:

Logic:
1. registry = load_aim_registry()
2. tool = registry["tools"][tool_id]
3. adapter_script = tool["adapterScript"] (expand env vars)
4. input_json = json.dumps({"capability": capability, "payload": payload})
5. Run subprocess:
   - cmd: echo '<input_json>' | pwsh -File <adapter_script>
   - timeout: 30s (from config)
   - capture stdout, stderr
6. Parse stdout as JSON
7. Return result dict {"success": bool, "message": str, "content": any}

Error Handling:
- Timeout: return {"success": false, "message": "Timeout"}
- Non-zero exit: return {"success": false, "message": stderr}
- Invalid JSON: return {"success": false, "message": "Invalid JSON output"}

Return: dict

Constraints:
- Use subprocess.run()
- Escape JSON strings for PowerShell (use json.dumps)
- Set timeout from config or default 30s
```
**Expected Outcome:** invoke_adapter() function
**Commit:** `feat(ph-08): implement PowerShell adapter invocation`

---

### Step 9: Implement route_capability
**Intent:** Route capability to primary/fallback tools
**Files:** /add src/pipeline/aim_bridge.py
**Command:** `/code`
**Prompt:**
```
Implement route_capability(capability, payload) in src/pipeline/aim_bridge.py:

Logic:
1. rules = load_coordination_rules()
2. Get primary tool for capability from rules
3. Invoke primary: result = invoke_adapter(primary_tool, capability, payload)
4. If result["success"]: return result
5. Else, try fallbacks in order:
   - For each fallback: result = invoke_adapter(fallback_tool, capability, payload)
   - If success: return result
6. If all fail: return {"success": false, "message": "All tools failed for capability"}

Audit:
- Call record_audit_log() for each attempt

Return: dict

Constraints:
- Fallback chain from coordination rules
- Log all attempts
```
**Expected Outcome:** route_capability() function
**Commit:** `feat(ph-08): implement capability routing with fallbacks`

---

### Step 10: Implement detect_tool & get_tool_version
**Intent:** Tool detection utilities
**Files:** /add src/pipeline/aim_bridge.py
**Command:** `/code`
**Prompt:**
```
Implement detect_tool(tool_id) and get_tool_version(tool_id) in src/pipeline/aim_bridge.py:

detect_tool(tool_id) -> bool:
1. registry = load_aim_registry()
2. detect_cmds = registry["tools"][tool_id]["detectCommands"]
3. For each cmd: run subprocess with check=False
4. If any exits with 0: return True
5. Else: return False

get_tool_version(tool_id) -> str | None:
1. registry = load_aim_registry()
2. version_cmd = registry["tools"][tool_id]["versionCommand"]
3. Run subprocess, capture stdout
4. If success: return stdout.strip()
5. Else: return None

Constraints:
- Timeout 5s for detection
- Handle missing commands gracefully
```
**Expected Outcome:** detect_tool() and get_tool_version() functions
**Commit:** `feat(ph-08): implement tool detection utilities`

---

### Step 11: Implement record_audit_log
**Intent:** Write audit logs
**Files:** /add src/pipeline/aim_bridge.py
**Command:** `/code`
**Prompt:**
```
Implement record_audit_log(tool_id, capability, payload, result) in src/pipeline/aim_bridge.py:

Logic:
1. aim_path = get_aim_registry_path()
2. date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
3. audit_dir = aim_path / "AIM_audit" / date
4. audit_dir.mkdir(parents=True, exist_ok=True)
5. timestamp = datetime.now(timezone.utc).isoformat() + "Z"
6. filename = f"{timestamp}_{tool_id}_{capability}.json"
7. entry = {
     "timestamp": timestamp,
     "actor": "pipeline",
     "tool_id": tool_id,
     "capability": capability,
     "payload": payload,
     "result": result
   }
8. Write entry to audit_dir / filename

Constraints:
- ISO 8601 UTC with "Z" suffix
- Create directory if missing
- Handle write errors gracefully (log warning, don't crash)
```
**Expected Outcome:** record_audit_log() function
**Commit:** `feat(ph-08): implement audit logging`

---

### Step 12: Extend tool_profiles.json
**Intent:** Add AIM metadata to existing tools
**Files:** /add config/tool_profiles.json
**Command:** `/code`
**Prompt:**
```
Extend config/tool_profiles.json:

For existing "aider" entry, add:
  "aim_tool_id": "aider",
  "aim_capabilities": ["code_generation", "refactoring"]

Keep all existing fields unchanged

Constraints:
- Preserve original field order
- Append AIM fields at end of each tool object
- Validate JSON syntax
```
**Expected Outcome:** Extended tool_profiles.json
**Commit:** `config(ph-08): extend tool profiles with AIM metadata`

---

### Step 13: Implement aim_status.py
**Intent:** CLI for tool detection
**Files:** /add scripts/aim_status.py
**Command:** `/code`
**Prompt:**
```
Implement scripts/aim_status.py:

Main:
1. Load AIM registry
2. For each tool in registry["tools"]:
   - detected = detect_tool(tool_id)
   - version = get_tool_version(tool_id) if detected else "N/A"
   - Print: f"{tool_id:<20} {detected:<10} {version}"
3. Load coordination rules
4. Print capability routing summary

Output Format:
Tool ID              Detected   Version
--------------------------------------------
aider                True       0.5.0
jules                False      N/A

Capability Routing:
- code_generation: aider (primary), jules (fallback)

Constraints:
- Tabular output
- Exit code 0 on success
```
**Expected Outcome:** aim_status.py script
**Commit:** `feat(ph-08): add AIM status CLI utility`

---

### Step 14: Implement aim_audit_query.py
**Intent:** CLI for audit log queries
**Files:** /add scripts/aim_audit_query.py
**Command:** `/code`
**Prompt:**
```
Implement scripts/aim_audit_query.py:

Args:
- --tool TOOL_ID (optional filter)
- --capability CAPABILITY (optional filter)
- --since YYYY-MM-DD (optional date filter)
- --format json|csv|text (default: text)

Logic:
1. Load audit logs from AIM_audit/
2. Parse all JSON files
3. Filter by tool, capability, since date
4. Print summary or export to JSON/CSV

Constraints:
- Handle missing audit directory gracefully
- Validate date format
- Sort results by timestamp
```
**Expected Outcome:** aim_audit_query.py script
**Commit:** `feat(ph-08): add audit log query CLI utility`

---

### Step 15: Add Unit Tests
**Intent:** Test aim_bridge module
**Files:** /add tests/pipeline/test_aim_bridge.py
**Command:** `/test`
**Prompt:**
```
Create tests/pipeline/test_aim_bridge.py:

Test Cases:
- test_load_aim_registry_success: mock registry file, load successfully
- test_load_aim_registry_missing: FileNotFoundError
- test_invoke_adapter_success: mock subprocess, parse result
- test_invoke_adapter_timeout: subprocess times out
- test_route_capability_primary_success: primary tool succeeds
- test_route_capability_fallback_success: primary fails, fallback succeeds
- test_detect_tool_true: detect command returns 0
- test_detect_tool_false: detect command returns non-zero
- test_record_audit_log: writes file to temp directory

Run: pytest tests/pipeline/test_aim_bridge.py -v

Constraints:
- Mock subprocess.run()
- Mock filesystem (use temp directories)
- Clear test names
```
**Expected Outcome:** All tests pass
**Commit:** `test(ph-08): add AIM bridge unit tests`

---

### Step 16: Add Integration Test
**Intent:** End-to-end AIM test
**Files:** /add tests/integration/test_aim_end_to_end.py
**Command:** `/test`
**Prompt:**
```
Create tests/integration/test_aim_end_to_end.py:

Mark: @pytest.mark.aim

Test:
- Skip if AIM registry not available
- Invoke route_capability("version_checking", {})
- Assert result["success"] is bool
- Verify audit log created in AIM_audit/

Run: pytest tests/integration/test_aim_end_to_end.py -v -m aim

Constraints:
- Skip gracefully if AIM unavailable
- Don't require specific tools installed
```
**Expected Outcome:** Test passes or skips
**Commit:** `test(ph-08): add AIM integration test`

---

### Step 17: Update Documentation
**Intent:** Document AIM integration
**Files:** /add docs/ARCHITECTURE.md (append), docs/PHASE_PLAN.md (append)
**Command:** `/code`
**Prompt:**
```
Update docs/ARCHITECTURE.md:

Add section "AIM Tool Registry Integration":
- Role of AIM as capability routing layer
- Python-PowerShell bridge design
- Capability routing and fallback chains
- Audit logging
- Backward compatibility with tool_profiles.json

Update docs/PHASE_PLAN.md:

Add PH-08 section with artifacts list
```
**Expected Outcome:** Documentation updated
**Commit:** `docs(ph-08): document AIM integration architecture`

---

### Step 18: Final Validation
**Intent:** Ensure all criteria met
**Command:** `/test`
**Run:**
```bash
pytest tests/pipeline/test_aim_bridge.py -v
pytest tests/integration/test_aim_end_to_end.py -v -m aim
python scripts/aim_status.py
python scripts/aim_audit_query.py --help
```
**Expected Outcome:** All tests pass, scripts run

---

## 7. SLASH COMMAND PLAYBOOK

| Action | Command | Usage |
|--------|---------|-------|
| Design architecture | `/architect` | With requirements block |
| Implement code | `/code` | Add files first via /add |
| Inspect changes | `/diff` | After each code step |
| Lint Python | `/lint` | After implementation |
| Run tests | `/test` | With pytest command |
| Undo last change | `/undo` | If wrong scope |
| Add reference | `/read-only` | For AIM registry files |

## 8. PROMPT TEMPLATES

### Implementation Prompt
```
Implement [function_name] in src/pipeline/aim_bridge.py:

Logic:
- [Step-by-step algorithm]

Error Handling:
- [Specific errors to catch]

Return: [type]

Constraints:
- [Import restrictions]
- [Performance limits]
```

### Test Prompt
```
Test [component_name]:

Test Cases:
- [List from test matrix]

Mocks:
- [What to mock]

Run: pytest [test_file] -v

Expected: All tests pass
```

## 9. SAFETY & GUARDRAILS

**Path Allowlist:**
- Only modify src/pipeline/aim_bridge.py and config/aim_config.yaml
- Read AIM registry files, never write

**No Edits to AIM Registry:**
- .AIM_ai-tools-registry is external, read-only

**Fail-Fast:**
- If AIM registry missing and AIM_REGISTRY_PATH not set: warn and disable AIM

**Scope Violation:**
- If diff includes tools.py or db.py modifications: `/undo`

**Rollback Triggers:**
- Test failure: fix, re-test
- Subprocess timeout: verify timeout setting

## 10. DETERMINISM & REPRODUCIBILITY

**Subprocess Invocation:**
- Escape JSON consistently via json.dumps()
- Stable PowerShell command format

**Audit Logs:**
- ISO 8601 UTC with "Z" suffix
- Filename format: {timestamp}_{tool_id}_{capability}.json

**Fallback Order:**
- Preserved from coordination-rules.json

**Error Messages:**
- Stable format: "[aim_bridge] Error: {message}"

## 11. TEST & VALIDATION MATRIX

| Criterion | Verification | Artifacts | Failure Handling |
|-----------|--------------|-----------|------------------|
| Registry loads | `pytest tests/pipeline/test_aim_bridge.py::test_load_aim_registry -v` | aim_bridge.py | Fix JSON parsing |
| Adapter invokes | `pytest tests/pipeline/test_aim_bridge.py::test_invoke_adapter_success -v` | aim_bridge.py | Fix subprocess call |
| Routing works | `pytest tests/pipeline/test_aim_bridge.py::test_route_capability* -v` | aim_bridge.py | Fix fallback logic |
| Audit logs | `pytest tests/pipeline/test_aim_bridge.py::test_record_audit_log -v` | aim_bridge.py | Fix file writing |
| Integration | `pytest tests/integration/test_aim_end_to_end.py -v -m aim` | All | Check AIM registry available |
| Scripts run | `python scripts/aim_status.py` | aim_status.py | Fix import errors |

## 12. COMPLETION CHECKLIST

- [ ] docs/AIM_INTEGRATION_CONTRACT.md exists with 8 sections
- [ ] docs/AIM_CAPABILITIES_CATALOG.md lists ≥5 capabilities
- [ ] config/aim_config.yaml exists with all settings
- [ ] src/pipeline/aim_bridge.py implements 8 functions
- [ ] config/tool_profiles.json extended with aim_tool_id, aim_capabilities
- [ ] scripts/aim_status.py provides tool detection CLI
- [ ] scripts/aim_audit_query.py provides audit query CLI
- [ ] tests/pipeline/test_aim_bridge.py exists and passes
- [ ] tests/integration/test_aim_end_to_end.py exists and passes/skips
- [ ] docs/ARCHITECTURE.md has AIM section
- [ ] docs/PHASE_PLAN.md has PH-08 section
- [ ] Git commit: `feat(ph-08): AIM tool registry integration`

**Final Commit Message:**
```
feat(ph-08): AIM tool registry integration

- Implement Python-to-PowerShell bridge for AIM adapters
- Add capability-based routing with fallback chains
- Implement audit logging for all tool invocations
- Extend tool_profiles.json with AIM metadata
- Add CLI utilities for tool status and audit queries
- Maintain backward compatibility with existing tools

🤖 Generated with Aider

Co-Authored-By: Aider <noreply@aider.com>
```

## 13. APPENDIX

### Crosswalk: Codex → Aider
| Codex | Aider |
|-------|-------|
| ROLE | Role & Objective |
| OPERATING CONTEXT | Environment & Preconditions |
| REQUIRED OUTPUTS | Target Artifacts |
| EXECUTION PLAN | Operations Sequence |
| CONSTRAINTS | Safety & Guardrails |

### AIM Registry Structure
```
.AIM_ai-tools-registry/
├── AIM_registry.json (tool metadata)
├── AIM_adapters/*.ps1 (PowerShell adapters)
├── AIM_cross-tool/AIM_coordination-rules.json (routing)
└── AIM_audit/<date>/*.json (audit logs)
```

END OF WORKSTREAM
