"""AIM+ Environment Management Module

Environment management, secrets, health checks, and tool lifecycle.

This module provides:
- Secret storage and management (platform-based)
- Health checks and system validation
- Tool installation and version control
- Environment scanning and optimization
- Audit logging

Public API:
    get_secrets_manager - Get platform-appropriate secrets manager
    HealthMonitor - Health check and monitoring
    EnvironmentScanner - Environment scanning and duplicate detection
    ToolInstaller - Tool installation automation
    VersionControl - Version pinning and management
    AuditLogger - Audit logging
    get_audit_logger - Get singleton audit logger
    
Exceptions:
    AIMPlusError - Base exception
    ConfigurationError - Configuration issues
    SecretsError - Secret storage failures
    HealthCheckError - Health check failures
    InstallationError - Tool installation failures
    VersionControlError - Version control issues
    ScannerError - Scanner errors

Usage:
    from aim.environment import get_secrets_manager, HealthMonitor
    
    # Secret management
    manager = get_secrets_manager()
    manager.set_secret("openai_api_key", "sk-...")
    
    # Health monitoring
    monitor = HealthMonitor()
    health = monitor.check_health()
"""
DOC_ID: DOC-PAT-AIM-ENVIRONMENT-INIT-381

__version__ = "1.0.0"

# Import public API components
from .secrets import get_secrets_manager
from .health import HealthMonitor, check_health
from .scanner import EnvironmentScanner
from .installer import ToolInstaller
from .version_control import VersionControl
from .audit import AuditLogger, get_audit_logger
from .exceptions import (
    AIMPlusError,
    ConfigurationError,
    SecretsError,
    HealthCheckError,
    InstallationError,
    VersionControlError,
    ScannerError,
)

__all__ = [
    # Version
    "__version__",
    
    # Secrets
    "get_secrets_manager",
    
    # Health
    "HealthMonitor",
    "check_health",
    
    # Scanner
    "EnvironmentScanner",
    
    # Installer
    "ToolInstaller",
    
    # Version Control
    "VersionControl",
    
    # Audit
    "AuditLogger",
    "get_audit_logger",
    
    # Exceptions
    "AIMPlusError",
    "ConfigurationError",
    "SecretsError",
    "HealthCheckError",
    "InstallationError",
    "VersionControlError",
    "ScannerError",
]
