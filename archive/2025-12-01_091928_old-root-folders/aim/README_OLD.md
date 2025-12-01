---
doc_id: DOC-AIM-README-OLD-093
---

# AIM (AI Tools Registry) Module

**Version:** 1.0  
**Status:** ✅ Production-Ready (Core Features)  
**Contract:** AIM_INTEGRATION_V1

---

## Overview

The AIM module provides **capability-based routing** for AI coding tools, enabling the pipeline to request capabilities (e.g., "code_generation") rather than hardcoding specific tools. AIM automatically selects the appropriate tool, manages fallback chains, and logs all invocations for audit purposes.

### Key Features

- ✅ **Capability-based routing** - Request "code_generation" instead of "aider"
- ✅ **Automatic fallbacks** - If primary tool fails, try fallbacks automatically
- ✅ **Centralized audit logging** - All tool invocations logged with inputs/outputs
- ✅ **Tool detection** - Automatically detect which tools are installed
- ✅ **PowerShell adapter bridge** - Unified interface for heterogeneous tools
- ✅ **Backward compatible** - Existing tool_profiles.json entries continue to work

---

## Quick Start

### 1. Verify AIM Registry

```powershell
# Check if AIM registry exists
Test-Path "aim\.AIM_ai-tools-registry"
```

### 2. Check Tool Status

```bash
python scripts/aim_status.py
```

**Example Output:**
```
AIM Registry Path: C:\...\aim\.AIM_ai-tools-registry

======================================================================
Tool ID              Detected     Version
======================================================================
aider                Yes          aider 0.5.0
jules                No           N/A
claude-cli           Yes          claude-cli 1.2.0
======================================================================
```

### 3. Use Capability Routing

```python
from aim.bridge import route_capability

# Request code generation capability
result = route_capability(
    capability="code_generation",
    payload={
        "files": ["src/main.py"],
        "prompt": "Add error handling to main function"
    },
    timeout_sec=60
)

if result["success"]:
    print(f"✓ Code generation completed")
    print(f"  Files modified: {result['content']['files_modified']}")
else:
    print(f"✗ Failed: {result['message']}")
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│ Pipeline Orchestrator (core/engine/orchestrator.py)    │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ AIM Bridge (aim/bridge.py)                             │
│ - route_capability()                                    │
│ - invoke_adapter()                                      │
│ - load_coordination_rules()                             │
└────────────────┬────────────────────────────────────────┘
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
┌────────┐  ┌────────┐  ┌──────────┐
│ Jules  │  │ Aider  │  │ Claude   │
│ Adapter│  │ Adapter│  │ Adapter  │
│  .ps1  │  │  .ps1  │  │   .ps1   │
└───┬────┘  └───┬────┘  └────┬─────┘
    │           │             │
    ▼           ▼             ▼
  jules       aider       claude CLI
```

**Data Flow:**
1. Orchestrator requests capability (e.g., "code_generation")
2. AIM bridge loads coordination rules
3. Selects primary tool (e.g., "jules")
4. Invokes PowerShell adapter with JSON payload
5. Adapter calls actual tool, parses output
6. Returns structured result to orchestrator
7. On failure, tries fallback tools (e.g., "aider", "claude-cli")
8. Logs all attempts to audit log

---

## API Reference

### Core Functions

#### `route_capability(capability, payload, timeout_sec=None)`

Route a capability request to the appropriate tool with fallback chain.

**Parameters:**
- `capability` (str): Capability name (e.g., "code_generation", "linting")
- `payload` (dict): Input data for the capability
- `timeout_sec` (int, optional): Subprocess timeout in seconds

**Returns:** `dict` with keys:
- `success` (bool): Whether operation succeeded
- `message` (str): Human-readable status message
- `content` (Any): Result data from tool

**Example:**
```python
result = route_capability(
    capability="code_generation",
    payload={
        "files": ["src/utils.py"],
        "prompt": "Add retry decorator with exponential backoff",
        "context": {
            "language": "python",
            "framework": "asyncio"
        }
    },
    timeout_sec=90
)
```

**Raises:**
- `AIMCapabilityNotFoundError` - If capability not in coordination rules
- `AIMAllToolsFailedError` - If all tools in fallback chain fail

---

#### `invoke_adapter(tool_id, capability, payload, timeout_sec=None)`

Invoke a specific tool's PowerShell adapter directly.

**Parameters:**
- `tool_id` (str): Tool identifier from registry (e.g., "aider")
- `capability` (str): Capability to invoke
- `payload` (dict): Input data
- `timeout_sec` (int, optional): Timeout in seconds

**Returns:** `dict` - Adapter result

**Example:**
```python
result = invoke_adapter(
    tool_id="aider",
    capability="code_generation",
    payload={"prompt": "Fix bug in login function"}
)
```

**Raises:**
- `AIMToolNotFoundError` - If tool_id not in registry
- `AIMAdapterNotFoundError` - If adapter script missing
- `AIMAdapterTimeoutError` - If subprocess times out

---

#### `detect_tool(tool_id)`

Check if a tool is installed by running its detection commands.

**Parameters:**
- `tool_id` (str): Tool identifier from registry

**Returns:** `bool` - True if tool detected, False otherwise

**Example:**
```python
if detect_tool("aider"):
    print("✓ Aider is installed")
else:
    print("✗ Aider not found")
```

---

#### `get_tool_version(tool_id)`

Get the version string of an installed tool.

**Parameters:**
- `tool_id` (str): Tool identifier from registry

**Returns:** `str | None` - Version string, or None if command fails

**Example:**
```python
version = get_tool_version("aider")
print(f"Aider version: {version}")  # "aider 0.5.0"
```

---

#### `load_aim_registry()`

Load the AIM registry JSON file.

**Returns:** `dict` - Parsed registry data

**Raises:**
- `AIMRegistryNotFoundError` - If registry directory not found
- `AIMRegistryLoadError` - If JSON is malformed

---

#### `load_coordination_rules()`

Load the coordination rules JSON file.

**Returns:** `dict` - Parsed coordination rules

**Raises:**
- `FileNotFoundError` - If rules file not found
- `json.JSONDecodeError` - If JSON is malformed

---

## Configuration

### `config/aim_config.yaml`

```yaml
# Enable AIM integration layer
enable_aim: true

# Enable audit logging for all tool invocations
enable_audit_logging: true

# Audit log retention (days)
audit_log_retention_days: 30

# Default timeout for adapter invocations (milliseconds)
default_timeout_ms: 30000

# AIM registry path
# - "auto": Auto-detect relative to repository root
# - Absolute path: Custom location
# - Can be overridden by AIM_REGISTRY_PATH environment variable
registry_path: "auto"
```

### Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `AIM_REGISTRY_PATH` | Override registry location | `C:\custom\.AIM_ai-tools-registry` |

---

## Capabilities

### Supported Capabilities

| Capability | Description | Primary Tool | Fallbacks |
|------------|-------------|--------------|-----------|
| `code_generation` | Generate or modify code | jules | aider, claude-cli |
| `linting` | Static code analysis | ruff | pylint |
| `refactoring` | Code restructuring | aider | claude-cli |
| `testing` | Run tests | pytest | (none) |
| `version_checking` | Check tool versions | aider | jules, claude-cli |

**Note:** Only `code_generation` is fully implemented in the current adapters.

---

## Audit Logging

All tool invocations are logged to:
```
aim\.AIM_ai-tools-registry\AIM_audit\YYYY-MM-DD\<timestamp>_<tool>_<capability>.json
```

### Query Audit Logs

```bash
# All logs for aider
python scripts/aim_audit_query.py --tool aider

# Code generation since Nov 15
python scripts/aim_audit_query.py --capability code_generation --since 2025-11-15

# Export to CSV
python scripts/aim_audit_query.py --tool aider --format csv > results.csv
```

### Audit Log Format

```json
{
  "timestamp": "2025-11-20T21:00:00.000000Z",
  "actor": "pipeline",
  "tool_id": "aider",
  "capability": "code_generation",
  "payload": {
    "files": ["src/main.py"],
    "prompt": "Add error handling"
  },
  "result": {
    "success": true,
    "message": "Code generation completed",
    "content": {
      "files_modified": ["src/main.py"],
      "exit_code": 0
    }
  }
}
```

---

## Adapter Development Guide

### Creating a New Adapter

1. **Add tool to registry** (`aim/.AIM_ai-tools-registry/AIM_registry.json`):

```json
{
  "tools": {
    "my-tool": {
      "name": "My Tool",
      "detectCommands": ["my-tool", "C:/path/my-tool.exe"],
      "versionCommand": ["my-tool", "--version"],
      "configPaths": ["%USERPROFILE%/.my-tool"],
      "logPaths": [],
      "capabilities": ["code_generation"],
      "adapterScript": "%AIM_REGISTRY_PATH%/AIM_adapters/AIM_my-tool.ps1"
    }
  }
}
```

2. **Create adapter script** (`aim/.AIM_ai-tools-registry/AIM_adapters/AIM_my-tool.ps1`):

```powershell
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Read JSON input from stdin
$inputJson = [Console]::In.ReadToEnd()
$req = $null
try { $req = $inputJson | ConvertFrom-Json } catch { $req = $null }

if (-not $req) {
  @{ success=$false; message='Invalid JSON input' } | ConvertTo-Json -Depth 6
  exit 1
}

$cap = "$($req.capability)"

switch ($cap) {
  'code_generation' {
    $prompt = $req.payload.prompt
    $files = $req.payload.files -join ' '
    
    # Invoke tool
    $result = & my-tool generate --prompt $prompt --files $files
    
    # Return structured output
    @{
      success = ($LASTEXITCODE -eq 0)
      message = if ($LASTEXITCODE -eq 0) { 'Success' } else { 'Failed' }
      content = @{
        files_modified = @($files)
        exit_code = $LASTEXITCODE
      }
    } | ConvertTo-Json -Depth 10
    
    exit $LASTEXITCODE
  }
  
  Default {
    @{
      success = $false
      message = "Unsupported capability: $cap"
      content = @{}
    } | ConvertTo-Json -Depth 6
    exit 1
  }
}
```

3. **Add to coordination rules** (`aim/.AIM_ai-tools-registry/AIM_cross-tool/AIM_coordination-rules.json`):

```json
{
  "capabilities": {
    "code_generation": {
      "primary": "my-tool",
      "fallback": ["aider", "claude-cli"],
      "loadBalance": false
    }
  }
}
```

---

## Troubleshooting

### Issue: "AIM registry not found"

**Cause:** Registry directory missing or `AIM_REGISTRY_PATH` incorrect.

**Solution:**
```powershell
# Verify registry exists
Test-Path "aim\.AIM_ai-tools-registry"

# Or set environment variable
$env:AIM_REGISTRY_PATH = "C:\path\to\.AIM_ai-tools-registry"
```

---

### Issue: "All tools failed for capability 'code_generation'"

**Cause:** No tools in fallback chain are installed or authenticated.

**Solution:**
```bash
# Check which tools are detected
python scripts/aim_status.py

# Install missing tools
pip install aider-chat

# Verify authentication (for Jules, Claude)
jules login
claude login
```

---

### Issue: Tests fail with "ModuleNotFoundError: No module named 'yaml'"

**Cause:** PyYAML not installed.

**Solution:**
```bash
pip install PyYAML>=6.0
```

---

### Issue: Adapter times out

**Cause:** Tool is waiting for input or processing is slow.

**Solution:**
```python
# Increase timeout
result = route_capability(
    capability="code_generation",
    payload=payload,
    timeout_sec=120  # 2 minutes
)
```

Or update `config/aim_config.yaml`:
```yaml
default_timeout_ms: 120000  # 2 minutes
```

---

## Testing

### Run Unit Tests

```bash
python -m pytest tests/pipeline/test_aim_bridge.py -v
```

### Run Integration Tests

```bash
python -m pytest tests/integration/test_aim_end_to_end.py -v --tb=short
```

**Note:** Integration tests require at least one AI tool to be installed.

---

## Security

### Input Validation

AIM validates all payloads before invoking adapters:
- **Payload size limit:** 1MB (configurable in coordination rules)
- **File pattern whitelist:** Only allowed file extensions
- **Forbidden paths:** Blocks access to `.git/`, `.env`, etc.

### Audit Integrity

All audit logs include:
- ISO 8601 timestamps (UTC)
- Actor identification
- Full input/output capture
- SHA256 integrity hashes (future)

### Credential Management

- Never commit API keys or secrets
- Use environment variables for authentication
- Tools may require separate login (`jules login`, `claude login`)

---

## Roadmap

### ✅ Completed (v1.0)
- Core bridge API
- PowerShell adapter pattern
- Capability routing with fallbacks
- Audit logging
- Tool detection
- Unit test coverage (19/19 tests passing)

### 🚧 In Progress
- Adapter output parsing (file tracking, line counts)
- Timeout handling with Start-Job
- Retry logic with exponential backoff

### 📋 Planned (v1.1)
- All 5 capabilities fully implemented
- Security constraint enforcement
- Registry caching with TTL
- Async adapter invocation
- Audit log pruning (retention policy)

---

## License

This module is part of the Complete AI Development Pipeline project.

---

## Support

- **Documentation:** `docs/AIM_docs/`
- **Contract:** `docs/AIM_docs/AIM_INTEGRATION_CONTRACT.md`
- **Capabilities Catalog:** `docs/AIM_docs/AIM_CAPABILITIES_CATALOG.md`
- **Phase Plan:** `meta/PHASE_DEV_DOCS/PH_08_AIM_Tool_Registry_Integration.md`

---

**Last Updated:** 2025-11-20  
**Maintainer:** AI Development Pipeline Team
