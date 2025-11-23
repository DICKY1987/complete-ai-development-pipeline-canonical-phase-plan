# AIM Module Structure

> **Module**: `aim`  
> **Full Name**: AI Manager Plus (AIM+)  
> **Purpose**: Unified AI environment and tool management  
> **Layer**: API  
> **Status**: Production

---

## Architectural Overview

The AIM module provides a unified interface for managing AI tools, environments, secrets, and capabilities. It acts as a bridge between the pipeline orchestrator and various AI tools, enabling capability-based routing and failover.

```
┌─────────────────────────────────────────────────────────────┐
│                     Pipeline Orchestrator                    │
│                    (core.engine.orchestrator)                │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                        AIM Bridge                            │
│                      (aim.bridge)                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Capability Routing: "code_generation" → [tools...]  │   │
│  └──────────────────────────────────────────────────────┘   │
└───┬───────────────────┬──────────────────┬──────────────────┘
    │                   │                  │
    ▼                   ▼                  ▼
┌─────────┐      ┌──────────────┐   ┌──────────────┐
│Registry │      │ Environment  │   │   Services   │
│         │      │              │   │              │
│ Config  │      │ • Secrets    │   │ Orchestrator │
│ Loading │      │ • Health     │   │  (Planned)   │
│ Routing │      │ • Installer  │   │              │
│         │      │ • Scanner    │   │              │
└─────────┘      └──────────────┘   └──────────────┘
```

---

## Directory Structure

```
aim/
├── README.md              # Main module documentation (user-facing)
├── STRUCTURE.md           # This file (architecture and structure)
├── DEPENDENCIES.md        # Explicit dependency declarations
├── MODULE.md              # Module metadata and overview
├── __init__.py            # Public API exports
├── __main__.py            # CLI entry point (python -m aim)
├── bridge.py              # Main integration bridge
├── exceptions.py          # Module-level exceptions
│
├── registry/              # Tool capability registry
│   ├── README.md          # Registry module documentation
│   ├── __init__.py        # Public interface
│   └── config_loader.py   # Configuration loading and validation
│
├── environment/           # Environment management
│   ├── README.md          # Environment module documentation
│   ├── __init__.py        # Public interface
│   ├── secrets.py         # Secret vault (DPAPI/keyring)
│   ├── health.py          # Health checks and validation
│   ├── scanner.py         # Duplicate/cache detection
│   ├── installer.py       # Tool installation automation
│   ├── version_control.py # Version pinning and management
│   ├── audit.py           # Audit logging
│   └── exceptions.py      # Environment-specific exceptions
│
├── services/              # Unified services layer (planned)
│   ├── README.md          # Services module documentation
│   └── __init__.py        # Public interface
│
├── cli/                   # Command-line interface
│   ├── README.md          # CLI module documentation
│   ├── __init__.py        # Public interface
│   ├── main.py            # CLI entry point
│   └── commands/          # Command implementations
│       ├── __init__.py
│       ├── secrets.py     # Secret management commands
│       ├── health.py      # Health check commands
│       ├── tools.py       # Tool management commands
│       ├── scan.py        # Environment scanning commands
│       ├── version.py     # Version control commands
│       └── audit.py       # Audit log commands
│
├── config/                # Configuration files
│   ├── README.md          # Configuration documentation
│   ├── aim_config.json    # Main configuration file
│   └── aim_config.schema.json  # JSON schema for validation
│
├── tests/                 # Test suite
│   ├── README.md          # Test documentation
│   ├── conftest.py        # Pytest fixtures and configuration
│   ├── environment/       # Environment module tests
│   │   ├── __init__.py
│   │   ├── test_audit.py
│   │   ├── test_health.py
│   │   ├── test_installer.py
│   │   ├── test_scanner.py
│   │   ├── test_secrets.py
│   │   └── test_version_control.py
│   └── registry/          # Registry module tests
│       ├── __init__.py
│       └── test_config_loader.py
│
└── .AIM_ai-tools-registry/  # Tool registry data (gitignored)
    ├── AIM_registry.json    # Tool and capability definitions
    ├── coordination_rules.json  # Tool coordination rules
    └── AIM_adapters/        # PowerShell adapter scripts
        ├── aider.ps1
        ├── jules.ps1
        └── claude-cli.ps1
```

---

## Module Hierarchy

### Layer 1: Foundation (No Dependencies)

**Purpose**: Core abstractions and configuration

- `registry/` - Configuration loading and validation
- `environment/exceptions.py` - Exception definitions
- `config/` - Configuration files and schemas

**Exports**: Configuration, schemas, base exceptions

---

### Layer 2: Environment Management (Depends on Layer 1)

**Purpose**: Environment operations and tool management

- `environment/secrets.py` - Secret management
- `environment/health.py` - Health monitoring
- `environment/scanner.py` - Environment scanning
- `environment/installer.py` - Tool installation
- `environment/version_control.py` - Version management
- `environment/audit.py` - Audit logging

**Exports**: Environment managers, health monitors, installers

---

### Layer 3: Integration (Depends on Layers 1-2)

**Purpose**: High-level integration and orchestration

- `bridge.py` - Main integration bridge
- `services/` - Service orchestration (planned)

**Exports**: Capability routing, tool invocation, service orchestrators

---

### Layer 4: User Interface (Depends on All Layers)

**Purpose**: User-facing interfaces

- `cli/` - Command-line interface
- `__main__.py` - CLI entry point

**Exports**: CLI commands, user interactions

---

## Responsibility Matrix

| Module | Primary Responsibility | Key Classes/Functions | Dependencies |
|--------|----------------------|----------------------|--------------|
| `registry/` | Configuration loading | `ConfigLoader` | stdlib, jsonschema |
| `environment/secrets` | Secret management | `get_secrets_manager()` | keyring, pywin32 |
| `environment/health` | Health monitoring | `HealthMonitor` | registry, secrets |
| `environment/scanner` | Environment scanning | `ToolScanner` | registry |
| `environment/installer` | Tool installation | `ToolInstaller` | registry |
| `environment/version_control` | Version management | `VersionManager` | registry |
| `environment/audit` | Audit logging | `AuditLogger` | stdlib |
| `bridge` | Integration bridge | `route_capability()` | registry, environment |
| `services/` | Orchestration | `AIMService` (planned) | All above |
| `cli/` | User interface | `cli` (Click group) | All above |

---

## Data Flow

### Configuration Loading

```
aim/config/aim_config.json
    ↓
registry/config_loader.py
    ↓ (validate against schema)
aim/config/aim_config.schema.json
    ↓ (expand env vars)
Environment Variables (${VAR_NAME})
    ↓ (return config dict)
Application Code
```

### Capability Routing

```
Pipeline Request
    ↓
bridge.route_capability(capability="code_generation")
    ↓ (load config)
registry/config_loader.py
    ↓ (check tool availability)
environment/health.py
    ↓ (select best tool)
registry/ (capability mapping)
    ↓ (invoke tool)
PowerShell Adapter (.AIM_ai-tools-registry/AIM_adapters/)
    ↓ (log invocation)
environment/audit.py
    ↓ (return result)
Pipeline
```

### Secret Management

```
CLI: aim secrets set <key>
    ↓
cli/commands/secrets.py
    ↓
environment/secrets.py
    ↓ (platform detection)
Windows: DPAPI | macOS/Linux: keyring
    ↓ (encrypted storage)
System Secret Store
```

---

## File Responsibilities

### Single Responsibility Principle

Each file has a focused responsibility:

- **`bridge.py`** - Integration point; capability routing only
- **`config_loader.py`** - Configuration loading; no business logic
- **`secrets.py`** - Secret storage; no health checking
- **`health.py`** - Health monitoring; no installation
- **`installer.py`** - Tool installation; no scanning
- **`scanner.py`** - Environment scanning; no installation
- **`audit.py`** - Audit logging; no tool invocation

### File Size Guidelines

- **Small files** (&lt;300 lines): Single class or set of related functions
- **Medium files** (300-800 lines): Primary module with multiple functions
- **Large files** (&gt;800 lines): Consider splitting into submodules

Current file sizes are within acceptable ranges.

---

## Interface Definitions

### Public APIs (Exported via `__init__.py`)

Each module exports a clean public API:

```python
# aim/__init__.py (planned enhancement)
from .bridge import route_capability, invoke_adapter, is_aim_available
from .environment.secrets import get_secrets_manager
from .environment.health import HealthMonitor
from .registry.config_loader import ConfigLoader

__all__ = [
    "route_capability",
    "invoke_adapter",
    "is_aim_available",
    "get_secrets_manager",
    "HealthMonitor",
    "ConfigLoader",
]
```

### Internal APIs (Module-to-Module)

- `registry` → `environment`: Provide configuration
- `environment` → `registry`: No dependencies (isolation)
- `bridge` → `registry`, `environment`: Orchestrate operations
- `cli` → All: User interface to all modules

---

## State Management

### Stateless Components

- `config_loader.py` - Pure function (load config)
- `bridge.py` - Stateless routing (no instance state)

### Stateful Components

- `HealthMonitor` - Caches health check results
- `AuditLogger` - Maintains log file handle
- `ToolInstaller` - Tracks installation state

### Persistent State

- **Configuration**: `aim/config/aim_config.json`
- **Secrets**: Platform-specific secret store
- **Audit logs**: `.state/aim/audit.jsonl`
- **Health cache**: In-memory (TTL-based)
- **Registry data**: `.AIM_ai-tools-registry/` (gitignored)

---

## Extensibility Points

### Adding New Components

1. **New Environment Component**:
   - Add file to `environment/`
   - Export in `environment/__init__.py`
   - Add tests in `tests/environment/`
   - Document in `environment/README.md`

2. **New CLI Command**:
   - Add file to `cli/commands/`
   - Register in `cli/main.py`
   - Add tests in `tests/cli/`
   - Document in `cli/README.md`

3. **New Tool**:
   - Add to `config/aim_config.json` (tools section)
   - Add PowerShell adapter (if needed)
   - Update capability mappings
   - Document in `README.md`

---

## Testing Structure

Tests mirror source structure:

```
aim/registry/config_loader.py
    → aim/tests/registry/test_config_loader.py

aim/environment/health.py
    → aim/tests/environment/test_health.py

aim/cli/commands/secrets.py
    → aim/tests/cli/test_secrets.py (planned)
```

See [tests/README.md](tests/README.md) for testing details.

---

## Documentation Structure

Each directory has documentation:

- **README.md** - User-facing module documentation
- **STRUCTURE.md** (this file) - Architecture and organization
- **DEPENDENCIES.md** - Explicit dependency declarations

This follows the repository's documentation standards.

---

## See Also

- [aim/README.md](README.md) - Main module documentation
- [aim/DEPENDENCIES.md](DEPENDENCIES.md) - Dependency declarations
- [aim/MODULE.md](MODULE.md) - Module metadata
- [CODEBASE_INDEX.yaml](../CODEBASE_INDEX.yaml) - Repository module index
- [DIRECTORY_GUIDE.md](../DIRECTORY_GUIDE.md) - Repository structure guide
