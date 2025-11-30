---
doc_id: DOC-AIM-README-092
---

# AIM - AI Tools Registry & Environment Manager

> **Module**: `aim`  
> **Purpose**: Unified AI environment and tool management with capability-based routing  
> **Layer**: Infrastructure/API  
> **Status**: Production

---

## Overview

The **AIM (AI Manager Plus)** module provides unified AI environment and tool management capabilities. It enables capability-based routing, allowing the pipeline to request AI capabilities (e.g., "code_generation") rather than hardcoding specific tools.

**Key Features**:
- ✅ **Capability-based routing** - Request capabilities, not specific tools
- ✅ **Automatic fallback chains** - Try multiple tools if primary fails
- ✅ **Tool detection** - Automatically detect installed AI tools
- ✅ **Secret management** - DPAPI vault (Windows) + keyring (cross-platform)
- ✅ **Health checks** - Validate environment and tool availability
- ✅ **Audit logging** - Centralized logging for all tool invocations
- ✅ **Backward compatible** - Works with existing `tool_profiles.json`

---

## Directory Structure

```
aim/
├── bridge.py                 # Main integration bridge (Python ↔ PowerShell)
├── registry/                 # Tool capability registry
│   ├── config_loader.py      # Load and validate registry
│   └── __init__.py
│
├── environment/              # Environment management
│   ├── secrets.py            # DPAPI vault + keyring integration
│   ├── health.py             # Health checks and validation
│   ├── scanner.py            # Duplicate/cache detection
│   ├── installer.py          # Tool installation automation
│   ├── version_control.py    # Version pinning and management
│   ├── audit.py              # Audit logging
│   └── exceptions.py         # AIM-specific exceptions
│
├── cli/                      # Command-line interface
│   ├── main.py               # CLI entry point
│   └── commands/             # CLI command modules
│
├── services/                 # Unified services layer
│   └── __init__.py
│
├── config/                   # Configuration files
│   └── aim_config.json       # Main configuration
│
├── .AIM_ai-tools-registry/   # Tool registry data (gitignored)
│   ├── AIM_registry.json     # Tool and capability definitions
│   ├── coordination_rules.json # Tool coordination rules
│   └── adapters/             # PowerShell adapter scripts
│       ├── aider.ps1
│       ├── jules.ps1
│       └── claude-cli.ps1
│
└── tests/                    # AIM tests
    ├── test_bridge.py
    ├── test_health.py
    └── test_secrets.py
```

---

## Quick Start

### 1. Verify AIM Registry

```bash
# Check if AIM registry exists
python -c "from aim.bridge import get_aim_registry_path; print(get_aim_registry_path())"
```

### 2. Check Tool Status

```bash
python scripts/aim_status.py
```

**Example Output**:
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

## Core Components

### Bridge Module (`bridge.py`)

Main Python-to-PowerShell integration bridge.

#### Core Functions

```python
from aim.bridge import (
    get_aim_registry_path,
    load_aim_registry,
    load_coordination_rules,
    route_capability,
    invoke_adapter,
    is_aim_available
)

# Get registry path (auto-detected or from AIM_REGISTRY_PATH env var)
registry_path = get_aim_registry_path()

# Load registry
registry = load_aim_registry()
# {
#     "tools": [...],
#     "capabilities": {...},
#     "metadata": {...}
# }

# Load coordination rules
rules = load_coordination_rules()

# Route capability to best available tool
result = route_capability(
    capability="code_generation",
    payload={"files": ["src/app.py"], "prompt": "Refactor main"},
    timeout_sec=60,
    fallback_tool="aider"  # Fallback if capability routing fails
)

# Invoke adapter directly
result = invoke_adapter(
    tool_id="aider",
    payload={"files": ["src/app.py"], "prompt": "Add logging"},
    timeout_sec=60
)

# Check if AIM is available
if is_aim_available():
    print("AIM is configured and ready")
```

#### Capability Routing Flow

```
1. Load AIM registry (.AIM_ai-tools-registry/AIM_registry.json)
2. Find capability mapping (e.g., "code_generation" → ["aider", "jules", "claude-cli"])
3. Check tool availability (detect installed tools)
4. Select best available tool from chain
5. Invoke PowerShell adapter (.AIM_ai-tools-registry/adapters/<tool>.ps1)
6. Log invocation to audit trail
7. Return result or fallback to next tool in chain
```

---

### Registry Management (`registry/`)

Loads and validates the AIM tool registry.

#### Registry Structure (`.AIM_ai-tools-registry/AIM_registry.json`)

```json
{
  "metadata": {
    "version": "1.0",
    "contract": "AIM_INTEGRATION_V1"
  },
  "tools": [
    {
      "id": "aider",
      "name": "Aider",
      "binary": "aider",
      "capabilities": ["code_generation", "refactoring"],
      "priority": 1
    },
    {
      "id": "jules",
      "name": "Jules AI",
      "binary": "jules",
      "capabilities": ["code_generation", "documentation"],
      "priority": 2
    }
  ],
  "capabilities": {
    "code_generation": {
      "description": "Generate or modify code",
      "preferred_tools": ["aider", "jules", "claude-cli"],
      "fallback_chain": true
    },
    "refactoring": {
      "description": "Refactor existing code",
      "preferred_tools": ["aider"],
      "fallback_chain": false
    }
  }
}
```

#### Coordination Rules (`.AIM_ai-tools-registry/coordination_rules.json`)

```json
{
  "sequential_tools": ["aider", "prettier"],
  "conflict_resolution": {
    "strategy": "last_write_wins"
  },
  "retry_policy": {
    "max_retries": 3,
    "backoff_sec": 2
  }
}
```

---

### Environment Management (`environment/`)

#### Secret Management (`secrets.py`)

Secure storage for API keys and credentials.

```python
from aim.environment.secrets import get_secrets_manager

# Get secrets manager (DPAPI on Windows, keyring on other platforms)
manager = get_secrets_manager()

# Store secret
manager.set_secret("openai_api_key", "sk-...")

# Retrieve secret
api_key = manager.get_secret("openai_api_key")

# Delete secret
manager.delete_secret("openai_api_key")

# List all secrets
secrets = manager.list_secrets()
```

**Platforms**:
- **Windows**: Uses DPAPI (Data Protection API) for encryption
- **macOS/Linux**: Uses system keyring (via `keyring` package)

---

#### Health Checks (`health.py`)

Validate environment and tool availability.

```python
from aim.environment.health import HealthMonitor

# Create health monitor
monitor = HealthMonitor()

# Run health check
health = monitor.check_health()

# Health structure:
# {
#     "registry_exists": True,
#     "tools_detected": ["aider", "claude-cli"],
#     "missing_tools": ["jules"],
#     "secrets_configured": True,
#     "api_keys_valid": True,
#     "overall_status": "healthy"  # or "degraded" or "critical"
# }

# Check specific tool
tool_health = monitor.check_tool_health("aider")
# {
#     "installed": True,
#     "version": "0.5.0",
#     "accessible": True,
#     "last_check": "2025-11-22T10:00:00Z"
# }
```

---

#### Scanner (`scanner.py`)

Detect duplicate installations and caches.

```python
from aim.environment.scanner import ToolScanner

# Create scanner
scanner = ToolScanner()

# Scan for duplicates
duplicates = scanner.scan_duplicates()

# Duplicates structure:
# {
#     "aider": [
#         "/usr/local/bin/aider",
#         "/home/user/.local/bin/aider"
#     ],
#     "claude-cli": [
#         "C:\\Program Files\\claude\\claude.exe",
#         "C:\\Users\\user\\AppData\\Local\\claude\\claude.exe"
#     ]
# }

# Scan for caches
caches = scanner.scan_caches()
# {
#     "aider": {"path": "~/.aider", "size_mb": 250},
#     "claude-cli": {"path": "~/.claude", "size_mb": 150}
# }
```

---

#### Installer (`installer.py`)

Automated tool installation and version management.

```python
from aim.environment.installer import ToolInstaller

# Create installer
installer = ToolInstaller()

# Install tool
result = installer.install_tool(
    tool_id="aider",
    version="0.5.0",
    force=False  # Skip if already installed
)

# Uninstall tool
installer.uninstall_tool("aider")

# Update tool
installer.update_tool("aider", version="0.6.0")
```

---

#### Audit Logging (`audit.py`)

Centralized logging for all tool invocations.

```python
from aim.environment.audit import AuditLogger

# Create audit logger
logger = AuditLogger()

# Log tool invocation
logger.log_invocation(
    tool_id="aider",
    capability="code_generation",
    input_payload={"files": ["src/app.py"], "prompt": "Add logging"},
    output_result={"success": True, "files_modified": ["src/app.py"]},
    duration_sec=45.2,
    cost_usd=0.05
)

# Query audit logs
logs = logger.query_logs(
    start_date="2025-11-22",
    tool_id="aider",
    success_only=True
)
```

**Audit Log Location**: `.state/aim/audit.jsonl` (JSON Lines format)

---

### CLI Interface (`cli/`)

Command-line interface for AIM operations.

```bash
# Check AIM status
python -m aim.cli status

# List tools
python -m aim.cli tools list

# Install tool
python -m aim.cli tools install aider

# Check health
python -m aim.cli health

# Manage secrets
python -m aim.cli secrets set openai_api_key
python -m aim.cli secrets list

# View audit logs
python -m aim.cli audit --tool aider --days 7
```

---

## Integration with Pipeline

### From Orchestrator

```python
from core.engine.aim_integration import execute_with_aim, is_aim_available

# Check if AIM is available
if is_aim_available():
    # Use capability routing
    result = execute_with_aim(
        capability="code_generation",
        payload={
            "files": ["src/auth.py"],
            "prompt": "Add JWT authentication",
            "language": "python"
        },
        fallback_tool="aider",
        context={"worktree_path": "/path/to/worktree"},
        run_id="run-2025-11-22-001",
        ws_id="ws-feature-auth"
    )
else:
    # Fallback to direct tool invocation
    from core.engine.tools import run_tool
    result = run_tool("aider", context)
```

### From Workstream Bundle

```json
{
  "id": "ws-feature-auth",
  "capability": "code_generation",
  "capability_payload": {
    "language": "python",
    "complexity": "medium"
  },
  "tool": "aider",  // Fallback if capability routing unavailable
  "files_scope": ["src/auth.py"],
  "tasks": ["Implement JWT authentication"]
}
```

---

## Configuration

### Environment Variables

- **`AIM_REGISTRY_PATH`** - Override AIM registry location (default: auto-detect)
- **`AIM_AUDIT_ENABLED`** - Enable audit logging (default: `true`)
- **`AIM_HEALTH_CHECK_INTERVAL`** - Health check interval in seconds (default: `300`)

### Configuration File (`config/aim_config.json`)

```json
{
  "registry_path": "aim/.AIM_ai-tools-registry",
  "audit_enabled": true,
  "audit_path": ".state/aim/audit.jsonl",
  "health_check_interval_sec": 300,
  "secret_backend": "auto",  // "auto", "dpapi", "keyring"
  "tool_detection": {
    "scan_paths": ["PATH", "~/.local/bin"],
    "cache_ttl_sec": 3600
  }
}
```

---

## Testing

Tests are located in `aim/tests/`:

```bash
# Unit tests
pytest aim/tests/test_bridge.py -v
pytest aim/tests/test_health.py -v
pytest aim/tests/test_secrets.py -v

# Integration tests
pytest aim/tests/test_integration.py -v
```

---

## Best Practices

1. **Use capability routing** - More flexible than hardcoding tools
2. **Configure fallback chains** - Ensure availability even if primary tool fails
3. **Enable audit logging** - Track all tool invocations for debugging
4. **Run health checks regularly** - Detect environment issues early
5. **Secure API keys** - Use secrets manager, never commit keys
6. **Monitor tool costs** - Track API usage and set budgets
7. **Keep registry updated** - Add new tools as they become available

---

## Migration from Legacy

AIM replaces the legacy `AI_MANGER` system with improved architecture:

```python
# ❌ LEGACY (AI_MANGER)
from AI_MANGER.plugins.Common import run_tool

# ✅ NEW (AIM)
from aim.bridge import route_capability
```

Legacy systems are archived in `legacy/AI_MANGER_archived_2025-11-22/`.

---

## Related Documentation

- **Bridge Integration**: `core/engine/aim_integration.py` - Pipeline integration
- **Tool Profiles**: `config/tool_profiles.json` - Direct tool configuration
- **Orchestrator**: `core/engine/README.md` - Execution engine
- **Module Overview**: `aim/MODULE.md` - Module architecture
- **Deployment Guide**: `aim/DEPLOYMENT_GUIDE.md` - Production setup
- **Status Reports**: `aim/FINAL_STATUS.md` - Feature completion status

---

## Roadmap

### Phase 1 (Current - Production)
- ✅ Capability-based routing
- ✅ Tool detection
- ✅ Secret management (DPAPI/keyring)
- ✅ Health checks
- ✅ Audit logging
- ✅ CLI interface

### Phase 2 (Planned)
- 🔜 Cost optimization (select cheapest tool for capability)
- 🔜 Performance monitoring (track tool latency)
- 🔜 Multi-tool orchestration (use multiple tools in sequence)
- 🔜 Tool benchmarking (compare tool outputs)
- 🔜 Automatic tool updates

### Phase 3 (Future)
- 🔜 Cloud-hosted registry
- 🔜 Distributed tool execution
- 🔜 Custom adapter DSL
- 🔜 AI-powered tool selection
