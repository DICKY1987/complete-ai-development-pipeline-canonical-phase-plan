# AIM Integration Contract

**Contract Version:** AIM_INTEGRATION_V1
**Last Updated:** 2025-11-16

---

## 1. Overview

The AIM (AI Tools Registry) integration provides a capability-based routing layer that sits between the pipeline orchestrator and AI coding tools (Jules, Aider, Claude CLI). Rather than calling tools directly, the pipeline routes tasks by **capability** (e.g., "code_generation") and AIM selects the appropriate tool, manages fallback chains, and logs all invocations for audit purposes.

**Key Benefits:**
- **Capability-based routing**: Request "code_generation" instead of hardcoding "aider"
- **Automatic fallbacks**: If primary tool fails, try fallback tools automatically
- **Centralized audit logging**: All tool invocations logged with inputs/outputs
- **Tool detection**: Automatically detect which tools are installed
- **PowerShell adapter pattern**: Unified interface for heterogeneous tools

**Backward Compatibility:** AIM is an optional enhancement layer. Existing `tool_profiles.json` entries continue to work unchanged. The pipeline functions normally when AIM is disabled or unavailable.

---

## 2. AIM Registry Structure

The AIM registry is located at: `.AIM_ai-tools-registry/` (relative to repository root)

```
.AIM_ai-tools-registry/
├── AIM_registry.json              # Tool metadata and capabilities
├── AIM_adapters/
│   ├── AIM_jules.ps1              # Jules adapter
│   ├── AIM_aider.ps1              # Aider adapter
│   └── AIM_claude-cli.ps1         # Claude CLI adapter
├── AIM_cross-tool/
│   └── AIM_coordination-rules.json # Capability routing rules
├── AIM_audit/
│   └── YYYY-MM-DD/                # Daily audit log directories
│       └── <timestamp>_<tool>_<capability>.json
└── AIM_logs/                      # General logs (optional)
```

### AIM_registry.json

Defines tool metadata:

```json
{
  "tools": {
    "aider": {
      "name": "Aider CLI",
      "detectCommands": ["aider", "C:/Users/richg/.local/bin/aider.exe"],
      "versionCommand": ["aider", "--version"],
      "configPaths": ["%USERPROFILE%/.aider"],
      "logPaths": [],
      "capabilities": ["code_generation", "refactoring"],
      "adapterScript": "%USERPROFILE%/.AIM_ai-tools-registry/AIM_adapters/AIM_aider.ps1"
    }
  },
  "crossToolRulesPath": "%USERPROFILE%/.AIM_ai-tools-registry/AIM_cross-tool/AIM_coordination-rules.json"
}
```

### AIM_coordination-rules.json

Defines capability routing:

```json
{
  "capabilities": {
    "code_generation": {
      "primary": "jules",
      "fallback": ["aider", "claude-cli"],
      "loadBalance": false
    }
  }
}
```

---

## 3. Python-to-PowerShell Invocation Pattern

### Adapter Input (JSON via stdin)

```json
{
  "capability": "code_generation",
  "payload": {
    "files": ["src/main.py"],
    "prompt": "Add error handling to main function",
    "context": {}
  }
}
```

### Adapter Output (JSON via stdout)

```json
{
  "success": true,
  "message": "Code generation completed successfully",
  "content": {
    "files_modified": ["src/main.py"],
    "lines_added": 15,
    "exit_code": 0
  }
}
```

### Subprocess Invocation

```python
import subprocess
import json

input_data = {"capability": "code_generation", "payload": {...}}
input_json = json.dumps(input_data)

result = subprocess.run(
    ["pwsh", "-File", adapter_script_path],
    input=input_json,
    capture_output=True,
    text=True,
    timeout=30
)

output = json.loads(result.stdout)
```

**PowerShell Adapter Pattern:**
```powershell
# Read JSON from stdin
$input = $Input | Out-String | ConvertFrom-Json

# Process capability
switch ($input.capability) {
    "code_generation" {
        # Invoke tool, capture result
        $result = @{success=$true; message="..."; content=@{...}}
    }
}

# Write JSON to stdout
$result | ConvertTo-Json -Depth 10
```

---

## 4. Capability Routing Logic

### Primary Tool Selection

1. Load `AIM_coordination-rules.json`
2. For requested capability, get `primary` tool ID
3. Invoke primary tool's adapter via `invoke_adapter()`
4. If `success=true`, return result

### Fallback Chain

1. If primary tool fails (`success=false` or exception):
   - Get `fallback` array from coordination rules
   - Try each fallback tool in order
   - Return first successful result
2. If all tools fail:
   - Return error result with aggregated failure messages

### Example Flow

Request: `route_capability("code_generation", payload)`

1. Rules say: primary=jules, fallback=[aider, claude-cli]
2. Try jules → fails (not installed)
3. Try aider → succeeds → return aider result
4. (claude-cli never attempted, short-circuit on first success)

---

## 5. Audit Log Format

All tool invocations are logged to: `.AIM_ai-tools-registry/AIM_audit/<YYYY-MM-DD>/<timestamp>_<tool_id>_<capability>.json`

### Audit Entry Structure

```json
{
  "timestamp": "2025-11-16T18:45:32.123456Z",
  "actor": "pipeline",
  "tool_id": "aider",
  "capability": "code_generation",
  "payload": {
    "files": ["src/main.py"],
    "prompt": "Add error handling"
  },
  "result": {
    "success": true,
    "message": "Completed successfully",
    "content": {...}
  }
}
```

**Field Descriptions:**
- `timestamp`: ISO 8601 UTC with "Z" suffix
- `actor`: Always "pipeline" for orchestrator invocations
- `tool_id`: Tool that was invoked (e.g., "aider")
- `capability`: Capability requested (e.g., "code_generation")
- `payload`: Input data sent to adapter
- `result`: Output data from adapter

**Audit Log Retention:**
- Configurable via `aim_config.yaml` (`audit_log_retention_days: 30`)
- Old logs can be pruned by date directory

**Privacy:**
- Do not log secrets, API keys, or credentials
- Redact sensitive data before logging

---

## 6. Environment Variables

### AIM_REGISTRY_PATH

**Purpose:** Override default AIM registry location

**Default Behavior:**
- Auto-detect relative to repository root: `../.AIM_ai-tools-registry`
- Or use user profile: `%USERPROFILE%/.AIM_ai-tools-registry`

**Override Example:**
```bash
export AIM_REGISTRY_PATH="C:/custom/path/.AIM_ai-tools-registry"
```

**Python Implementation:**
```python
import os
from pathlib import Path

def get_aim_registry_path() -> Path:
    env_path = os.getenv("AIM_REGISTRY_PATH")
    if env_path:
        return Path(env_path)

    # Auto-detect relative to repo root
    repo_root = Path(__file__).parent.parent.parent
    aim_path = repo_root / ".AIM_ai-tools-registry"

    if not aim_path.exists():
        raise FileNotFoundError(f"AIM registry not found at {aim_path}")

    return aim_path
```

---

## 7. Error Handling & Degradation Strategy

### Graceful Degradation

**If AIM registry not found:**
- Log warning: `[AIM] Registry not found, AIM disabled. Using direct tool invocation.`
- Set `enable_aim=false` in runtime config
- Fall back to `tools.py` direct invocation
- Pipeline continues normally

**If AIM registry invalid (malformed JSON):**
- Log error with file path and JSON error
- Disable AIM for current run
- Fall back to direct tool invocation

**If adapter script missing:**
- Log error: `[AIM] Adapter script not found for tool '{tool_id}': {script_path}`
- Skip tool in fallback chain
- Try next fallback tool
- If no fallbacks available, return error

### Error Scenarios

| Scenario | Handling | Fallback Behavior |
|----------|----------|-------------------|
| Registry not found | Warn, disable AIM | Use `tools.py` directly |
| Malformed JSON | Error, disable AIM | Use `tools.py` directly |
| Adapter timeout | Error, try fallback | Next tool in fallback chain |
| Adapter non-zero exit | Parse stderr, try fallback | Next tool in fallback chain |
| Adapter invalid JSON output | Error, try fallback | Next tool in fallback chain |
| All tools fail | Return aggregated error | Propagate error to orchestrator |

### Timeout Handling

**Default Timeout:** 30 seconds (configurable via `aim_config.yaml`)

**Subprocess Timeout:**
```python
try:
    result = subprocess.run(..., timeout=timeout_sec)
except subprocess.TimeoutExpired:
    return {
        "success": False,
        "message": f"Adapter timed out after {timeout_sec}s",
        "content": None
    }
```

**Progressive Timeout:** If primary tool times out, fallback tools still get full timeout

---

## 8. Contract Version & Compatibility

**Contract Version:** `AIM_INTEGRATION_V1`

**Version Checking:**
- This contract defines the interface between Python pipeline and PowerShell adapters
- Future versions may add optional fields (backward compatible)
- Breaking changes require new contract version (e.g., `AIM_INTEGRATION_V2`)

**Compatibility Requirements:**
- Python 3.12+
- PowerShell 7+
- JSON input/output for all adapters
- ISO 8601 timestamps with "Z" suffix for audit logs

**Migration Path:**
- If AIM registry format changes, provide migration script
- Old audit logs remain readable (append-only)
- Tool adapters versioned independently of registry

---

## 9. Integration with Existing Pipeline

### Relationship with tools.py

**Direct Invocation (existing):**
```python
from src.pipeline.tools import run_tool

result = run_tool("aider", context={"prompt": "..."}, run_id="R1")
```

**AIM-based Invocation (new):**
```python
from src.pipeline.tools import run_tool_via_aim

result = run_tool_via_aim(
    tool_id="aider",  # Optional, for direct tool routing
    capability="code_generation",
    payload={"prompt": "..."},
    run_id="R1"
)
```

**Capability Routing (new):**
```python
from src.pipeline.aim_bridge import route_capability

result = route_capability(
    capability="code_generation",
    payload={"prompt": "..."}
)
# Automatically selects jules → aider → claude-cli based on rules
```

### Configuration Flag

In `tool_profiles.json` or global config:
```json
{
  "aider": {
    "type": "ai",
    "command": "aider",
    "use_aim": true,  // Enable AIM routing for this tool
    "aim_tool_id": "aider",
    "aim_capabilities": ["code_generation", "refactoring"]
  }
}
```

- If `use_aim=true` and AIM available → use AIM routing
- If `use_aim=false` or AIM unavailable → use direct invocation

---

## 10. Security Considerations

**Input Validation:**
- Validate all JSON inputs before passing to PowerShell
- Escape special characters in payload strings
- Reject payloads exceeding size limits (e.g., 1MB)

**Subprocess Safety:**
- Use `subprocess.run()` with explicit command array (no shell=True)
- Set timeout to prevent hung processes
- Limit stderr/stdout capture size

**Audit Log Security:**
- Do not log credentials, API keys, or secrets
- Restrict audit log file permissions (read-only for non-admin)
- Rotate logs based on retention policy

**Adapter Isolation:**
- Adapters run in separate PowerShell processes (isolated)
- Adapters cannot modify registry or coordination rules (read-only)
- Failures in one adapter do not crash pipeline

---

## Document Change Log

| Version | Date | Changes |
|---------|------|---------|
| AIM_INTEGRATION_V1 | 2025-11-16 | Initial contract for PH-08 |

---

**End of Contract**
