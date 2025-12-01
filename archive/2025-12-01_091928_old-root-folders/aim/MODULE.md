---
doc_id: DOC-AIM-MODULE-090
---

# AIM Module

> **Module ID**: `aim`  
> **Purpose**: Unified AI environment and tool management  
> **Layer**: API  
> **Last Updated**: 2025-11-22  
> **Status**: Production

---

## Overview

The `aim/` (AI Manager Plus) module provides unified AI environment and tool management capabilities. It replaces the legacy AI_MANGER system with improved architecture, security, and cross-platform support.

**Key Features**:
- Tool capability routing with fallback chains
- DPAPI vault for secret management (Windows) + keyring (cross-platform)
- Environment health checks and validation
- Automated tool installation and version pinning
- Duplicate/cache detection via scanner
- Unified audit logging

---

## Directory Structure

```
aim/
├── registry/          # Tool capability registry and routing
│   ├── registry.py    # Core registry management
│   └── router.py      # Capability-based routing
│
├── environment/       # Environment management
│   ├── secrets.py     # Secret vault (DPAPI/keyring)
│   ├── health.py      # Health checks
│   ├── scanner.py     # Duplicate/cache detection
│   ├── installer.py   # Tool installation
│   ├── version.py     # Version management
│   └── audit.py       # Audit logging
│
├── services/          # Unified services layer
│   └── service.py     # Service orchestration
│
├── cli/               # Command-line interface
│   └── cli.py         # CLI commands
│
└── config/            # Configuration
    └── aim_config.json # Main configuration file
```

---

## Key Components

### Tool Registry (`registry/`)

Manages AI tool capabilities and routing logic.

**Key Functions**:
- `register_tool()` - Register new AI tool
- `get_tool_info()` - Get tool metadata
- `route_capability()` - Route request to best available tool
- `get_fallback_chain()` - Get fallback options

**Import Pattern**:
```python
from aim.registry.registry import register_tool, get_tool_info
from aim.registry.router import route_capability
```

### Environment Management (`environment/`)

Handles secrets, health checks, and environment setup.

**Secrets Management**:
- Windows: DPAPI-based vault
- Cross-platform: system keyring integration
- No plaintext secrets in config files

**Health Checks**:
- Tool availability validation
- Version compatibility checks
- API key verification

**Import Pattern**:
```python
from aim.environment.secrets import store_secret, get_secret
from aim.environment.health import check_health
from aim.environment.scanner import scan_duplicates
```

### CLI (`cli/`)

Command-line interface for AIM operations.

**Available Commands**:
```bash
python -m aim status      # Show tool status
python -m aim health      # Health check all tools
python -m aim secrets     # Manage secrets
python -m aim scan        # Scan for duplicates/cache issues
python -m aim install     # Install/update tools
```

---

## Dependencies

**Module Dependencies** (from CODEBASE_INDEX.yaml):
- None (top-level integration module)

**External Dependencies**:
- `keyring` - Cross-platform secret storage
- `pywin32` - Windows DPAPI (Windows only)

---

## Usage Examples

### Basic Tool Registration

```python
from aim.registry.registry import register_tool

register_tool(
    name="ollama",
    capabilities=["chat", "completion"],
    endpoint="http://localhost:11434",
    models=["deepseek-r1:latest"]
)
```

### Secret Management

```python
from aim.environment.secrets import store_secret, get_secret

# Store API key securely
store_secret("openai", "api_key", "sk-...")

# Retrieve API key
api_key = get_secret("openai", "api_key")
```

### Health Check

```python
from aim.environment.health import check_health

# Check all registered tools
health_status = check_health()
print(f"Healthy tools: {health_status['healthy_count']}")
```

---

## Migration Notes

**Replaces**: `legacy/AI_MANGER_archived_2025-11-22/`

**Key Improvements**:
- Python-based (replaces PowerShell)
- Cross-platform support
- Secure secret management (no plaintext)
- Unified configuration (aim_config.json)
- Audit logging
- Capability-based routing

**Migration Steps**:
1. Run `python -m aim status` to verify installation
2. Configure tools in `aim/config/aim_config.json`
3. Store secrets via `python -m aim secrets`
4. Run health check: `python -m aim health`

---

## AI Context Priority

**HIGH** - Core infrastructure for AI tool management

**AI Agent Guidance**:
- ✅ Safe to modify: `registry/`, `environment/`, `services/`, `cli/`
- ⚠️ Review required: `config/aim_config.json` (configuration changes)
- ❌ Do not modify: Secret vault files (managed by environment module)

**Edit Policy**: `safe` (with review for config changes)

---

## Documentation

- Module overview: This file
- Configuration guide: `docs/CONFIGURATION_GUIDE.md`
- Integration guide: `docs/AIM_INTEGRATION_STATUS.md`
- Complete implementation: `docs/AIM_PLUS_FINAL_REPORT.md`

---

## See Also

- [CODEBASE_INDEX.yaml](../CODEBASE_INDEX.yaml) - Module dependencies
- [DIRECTORY_GUIDE.md](../DIRECTORY_GUIDE.md) - Repository structure
- [docs/AIM_INTEGRATION_STATUS.md](../docs/AIM_INTEGRATION_STATUS.md) - Integration status
