"""AIM - AI Manager Plus

Unified AI environment and tool management with capability-based routing.

The AIM module provides:
- Tool capability registry and routing
- Environment management and health checks  
- Secret storage (platform-based)
- Tool installation and version control
- Environment scanning and optimization
- Audit logging
- CLI interface

Architecture:
    ┌─────────────────────────────────────────┐
    │        Pipeline Orchestrator            │
    └──────────────┬──────────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────────────┐
    │           AIM Bridge                     │
    │   (Capability-based routing)             │
    └──┬─────────────┬──────────────┬──────────┘
       │             │              │
       ▼             ▼              ▼
    Registry    Environment    Services
                                (Planned)

Modules:
    registry - Tool capability registry and config loading
    environment - Environment management and health
    cli - Command-line interface
    services - Service orchestration (planned)

See Also:
    - aim/README.md - Comprehensive module documentation
    - aim/STRUCTURE.md - Architecture and structure
    - aim/DEPENDENCIES.md - Dependency declarations
"""

__version__ = "1.0.0"

# Re-export commonly used components for convenience
# Note: Some imports may fail if dependencies not installed,
# so we use try/except to allow partial imports

# Always available: exceptions
from .exceptions import (
    AIMError,
    AIMRegistryNotFoundError,
    AIMCapabilityNotFoundError,
    AIMToolNotFoundError,
    AIMAdapterInvocationError,
    AIMAllToolsFailedError,
)

# Bridge functions (core integration)
try:
    from .bridge import (
        route_capability,
        invoke_adapter, 
        get_aim_registry_path,
        load_aim_registry,
        load_coordination_rules,
        detect_tool,
        get_tool_version,
        record_audit_log,
    )
    _bridge_available = True
except ImportError as e:
    _bridge_available = False
    # Define placeholder
    route_capability = None
    invoke_adapter = None
    
# Registry
try:
    from .registry import ConfigLoader
    _registry_available = True
except ImportError:
    _registry_available = False
    ConfigLoader = None

# Environment (most common components)
try:
    from .environment import (
        get_secrets_manager,
        HealthMonitor,
        EnvironmentScanner,
        ToolInstaller,
        VersionControl,
        AuditLogger,
        get_audit_logger,
    )
    _environment_available = True
except ImportError:
    _environment_available = False

# CLI
try:
    from .cli import cli
    _cli_available = True
except ImportError:
    _cli_available = False
    cli = None

__all__ = [
    # Version
    "__version__",
    
    # Exceptions (always available)
    "AIMError",
    "AIMRegistryNotFoundError",
    "AIMCapabilityNotFoundError",
    "AIMToolNotFoundError",
    "AIMAdapterInvocationError",
    "AIMAllToolsFailedError",
    
    # Bridge (if available)
    "route_capability",
    "invoke_adapter",
    "get_aim_registry_path",
    "load_aim_registry",
    "load_coordination_rules",
    "detect_tool",
    "get_tool_version",
    "record_audit_log",
    
    # Registry (if available)
    "ConfigLoader",
    
    # Environment (if available)
    "get_secrets_manager",
    "HealthMonitor",
    "EnvironmentScanner",
    "ToolInstaller",
    "VersionControl",
    "AuditLogger",
    "get_audit_logger",
    
    # CLI (if available)
    "cli",
]
