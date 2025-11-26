# AIM Environment Module

> **Module**: `aim.environment`  
> **Purpose**: Environment management, secrets, health checks, and tool lifecycle  
> **Parent**: `aim/`  
> **Layer**: API  
> **Status**: Production

---

## Overview

The `aim/environment/` module provides comprehensive environment management capabilities for AI tools. It handles secret storage, health monitoring, tool installation, environment scanning, and version control.

**Key Responsibilities**:
- Secure secret storage (DPAPI on Windows, keyring cross-platform)
- Health checks and system validation
- Tool installation and version management
- Environment scanning and duplicate detection
- Audit logging for tool invocations
- Exception handling for AIM operations

---

## Module Structure

```
aim/environment/
├── __init__.py           # Public API exports
├── secrets.py            # Secret vault (DPAPI/keyring)
├── health.py             # Health checks and validation
├── scanner.py            # Duplicate/cache detection
├── installer.py          # Tool installation automation
├── version_control.py    # Version pinning and management
├── audit.py              # Audit logging
├── exceptions.py         # AIM-specific exceptions
└── README.md             # This file
```

---

## Core Components

### Secret Management (`secrets.py`)

Secure storage for API keys and credentials using platform-native storage.

**Key Classes/Functions**:
```python
from aim.environment.secrets import get_secrets_manager

# Get platform-appropriate secrets manager
manager = get_secrets_manager()  # DPAPI on Windows, keyring elsewhere

# Store secret
manager.set_secret("openai_api_key", "sk-...")

# Retrieve secret
api_key = manager.get_secret("openai_api_key")

# Delete secret
manager.delete_secret("openai_api_key")

# List all secrets
secrets = manager.list_secrets()
```

**Platform Support**:
- **Windows**: DPAPI (Data Protection API) - encrypted at rest
- **macOS/Linux**: System keyring via `keyring` package
- **Fallback**: In-memory storage (not recommended for production)

**Security Features**:
- No plaintext secrets in config files
- Automatic encryption at rest (platform-dependent)
- Secure delete operations
- Audit trail for secret access

---

### Health Monitoring (`health.py`)

Environment and tool availability validation.

**Key Classes/Functions**:
```python
from aim.environment.health import HealthMonitor

# Create health monitor
monitor = HealthMonitor()

# Run comprehensive health check
health = monitor.check_health()
# Returns:
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
# Returns:
# {
#     "installed": True,
#     "version": "0.5.0",
#     "accessible": True,
#     "last_check": "2025-11-22T10:00:00Z"
# }
```

**Health Check Categories**:
- Registry existence and validity
- Tool binary detection and accessibility
- Version compatibility
- API key configuration
- Network connectivity (optional)

---

### Environment Scanner (`scanner.py`)

Detect duplicate installations, cache issues, and optimization opportunities.

**Key Classes/Functions**:
```python
from aim.environment.scanner import ToolScanner

# Create scanner
scanner = ToolScanner()

# Scan for duplicate installations
duplicates = scanner.scan_duplicates()
# Returns:
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
# Returns:
# {
#     "aider": {"path": "~/.aider", "size_mb": 250},
#     "claude-cli": {"path": "~/.claude", "size_mb": 150}
# }

# Get cleanup recommendations
recommendations = scanner.get_cleanup_recommendations()
```

**Scanner Features**:
- Duplicate binary detection across PATH
- Cache size analysis
- Cleanup recommendations
- Configuration conflict detection

---

### Tool Installer (`installer.py`)

Automated tool installation and version management.

**Key Classes/Functions**:
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

# Update tool to specific version
installer.update_tool("aider", version="0.6.0")

# Check if tool needs update
needs_update = installer.check_for_updates("aider")
```

**Installation Methods**:
- pip-based installation (Python tools)
- npm-based installation (Node.js tools)
- Binary download (platform-specific)
- Custom installation scripts

---

### Version Control (`version_control.py`)

Version pinning, compatibility checking, and upgrade management.

**Key Classes/Functions**:
```python
from aim.environment.version_control import VersionManager

# Create version manager
vm = VersionManager()

# Pin tool to specific version
vm.pin_version("aider", "0.5.0")

# Check version compatibility
is_compatible = vm.check_compatibility("aider", "0.5.0")

# Get recommended version
recommended = vm.get_recommended_version("aider")

# List available versions
versions = vm.list_available_versions("aider")
```

**Features**:
- Semantic version parsing
- Compatibility matrix checking
- Automatic version recommendations
- Version constraint resolution

---

### Audit Logging (`audit.py`)

Centralized logging for all tool invocations and environment operations.

**Key Classes/Functions**:
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

# Export logs
logger.export_logs(output_path="audit_report.jsonl")
```

**Audit Log Storage**: `.state/aim/audit.jsonl` (JSON Lines format)

**Logged Information**:
- Timestamp and duration
- Tool ID and capability
- Input/output payloads
- Success/failure status
- Cost (if applicable)
- User context

---

### Exception Handling (`exceptions.py`)

AIM-specific exceptions for better error handling.

**Available Exceptions**:
```python
from aim.environment.exceptions import (
    ConfigurationError,      # Configuration issues
    ToolNotFoundError,       # Tool binary not found
    SecretStorageError,      # Secret storage failures
    HealthCheckError,        # Health check failures
    InstallationError,       # Tool installation failures
    VersionMismatchError,    # Version compatibility issues
    AuditLogError           # Audit logging failures
)

# Example usage
try:
    config = loader.load()
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

---

## Public Interface

The module exposes the following through `__init__.py`:

```python
# Currently minimal - enhancement needed
__version__ = "1.0.0"
__all__ = []  # To be populated with public API
```

**Suggested Enhancement**: Export primary classes and functions:
```python
from .secrets import get_secrets_manager
from .health import HealthMonitor
from .scanner import ToolScanner
from .installer import ToolInstaller
from .version_control import VersionManager
from .audit import AuditLogger
from .exceptions import *

__all__ = [
    "get_secrets_manager",
    "HealthMonitor",
    "ToolScanner",
    "ToolInstaller",
    "VersionManager",
    "AuditLogger",
    # Exceptions
    "ConfigurationError",
    "ToolNotFoundError",
    # ... etc
]
```

---

## Integration Points

### Used By
- `aim.bridge` - Main integration bridge
- `aim.cli` - CLI commands for environment management
- `core.engine.aim_integration` - Pipeline orchestrator

### Dependencies
- `aim.registry.config_loader` - Configuration loading
- External: `keyring`, `pywin32` (Windows), `requests`, `jsonschema`
- Standard library: `json`, `os`, `pathlib`, `datetime`, `subprocess`

---

## Configuration

Environment variables used by this module:

- **`AIM_SECRETS_BACKEND`** - Override secret backend (`dpapi`, `keyring`, `memory`)
- **`AIM_AUDIT_PATH`** - Override audit log path (default: `.state/aim/audit.jsonl`)
- **`AIM_AUDIT_ENABLED`** - Enable/disable audit logging (default: `true`)
- **`AIM_HEALTH_CHECK_INTERVAL`** - Health check cache interval in seconds (default: `300`)

**Configuration File** (`aim/config/aim_config.json`):
```json
{
  "environment": {
    "secret_backend": "auto",
    "audit_enabled": true,
    "audit_path": ".state/aim/audit.jsonl",
    "health_check_interval_sec": 300,
    "tool_detection": {
      "scan_paths": ["PATH", "~/.local/bin"],
      "cache_ttl_sec": 3600
    }
  }
}
```

---

## Usage Examples

### Complete Environment Setup

```python
from aim.environment import (
    get_secrets_manager,
    HealthMonitor,
    ToolScanner,
    ToolInstaller
)

# 1. Check environment health
monitor = HealthMonitor()
health = monitor.check_health()

if health["overall_status"] != "healthy":
    print(f"Environment issues detected: {health}")

# 2. Scan for problems
scanner = ToolScanner()
duplicates = scanner.scan_duplicates()
if duplicates:
    print(f"Duplicate installations found: {duplicates}")

# 3. Install missing tools
installer = ToolInstaller()
for missing_tool in health["missing_tools"]:
    installer.install_tool(missing_tool)

# 4. Configure secrets
secrets = get_secrets_manager()
secrets.set_secret("openai_api_key", "sk-...")

# 5. Re-check health
health = monitor.check_health()
print(f"Final status: {health['overall_status']}")
```

---

## Testing

Tests are located in `aim/tests/environment/`:

```bash
# Run all environment tests
pytest aim/tests/environment/ -v

# Run specific component tests
pytest aim/tests/environment/test_health.py -v
pytest aim/tests/environment/test_secrets.py -v
pytest aim/tests/environment/test_scanner.py -v
```

**Test Markers**:
- `@pytest.mark.aim` - Tests requiring AIM registry
- Platform-specific tests use appropriate markers

---

## Security Considerations

1. **Secrets Management**:
   - Never log secret values
   - Use platform-native encryption
   - Rotate secrets regularly
   - Audit secret access

2. **Audit Logs**:
   - Protect audit log files (read-only for non-admin)
   - Implement log rotation
   - Sanitize sensitive data before logging

3. **Tool Installation**:
   - Verify tool signatures where possible
   - Use trusted repositories only
   - Validate checksums for binary downloads

---

## See Also

- [aim/README.md](../README.md) - Main AIM documentation
- [aim/config/aim_config.json](../config/aim_config.json) - Configuration
- [CODEBASE_INDEX.yaml](../../CODEBASE_INDEX.yaml) - Module dependencies
- [docs/CONFIGURATION_GUIDE.md](../../docs/CONFIGURATION_GUIDE.md) - Configuration guide
