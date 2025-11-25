# AIM Module Dependencies

> **Module**: `aim`  
> **Purpose**: Explicit dependency declarations for AI Manager Plus  
> **Last Updated**: 2025-11-23  
> **Status**: Production

---

## Overview

This document declares all dependencies for the AIM module, both internal (other repository modules) and external (Python packages). It serves as a contract for dependency management and helps AI tools understand module boundaries.

---

## Internal Dependencies (Repository Modules)

### Module-to-Module Dependencies

The AIM module has **no dependencies** on other repository modules. It is a self-contained integration layer.

**Module ID**: `aim` (from CODEBASE_INDEX.yaml)

**Depends On**: `[]` (none)

**Used By**:
- `core.engine` - Orchestrator may use AIM for tool routing
- Pipeline scripts - Scripts may use AIM CLI
- External integrations - Other tools may invoke AIM

### Why No Internal Dependencies?

The AIM module is designed as a **foundational integration layer**. It should not depend on:
- `core.*` - Pipeline implementation details
- `error.*` - Error detection system
- `specifications.*` - Specification management

This design ensures:
- **Reusability** - AIM can be used independently
- **Testability** - Tests don't require entire pipeline
- **Portability** - AIM can be extracted to separate package
- **Clear boundaries** - No circular dependencies

---

## External Dependencies (Python Packages)

### Production Dependencies

Dependencies required for normal operation.

#### Required (Core Functionality)

```
# Configuration and validation
jsonschema>=4.0.0         # JSON schema validation

# CLI interface
click>=8.0.0              # Command-line interface framework
rich>=13.0.0              # Rich console output

# Environment management
keyring>=24.0.0           # Cross-platform secret storage
pywin32>=300; platform_system=='Windows'  # Windows DPAPI (Windows only)
```

**Installation**:
```bash
pip install jsonschema click rich keyring
pip install pywin32  # Windows only
```

#### Optional (Enhanced Features)

```
# Advanced CLI features
tabulate>=0.9.0           # Table formatting (for CLI output)

# HTTP requests (for tool installation)
requests>=2.28.0          # HTTP library for downloads

# Version parsing
packaging>=21.0           # Semantic version parsing
```

**Installation**:
```bash
pip install tabulate requests packaging
```

---

### Development Dependencies

Dependencies required for development and testing.

```
# Testing
pytest>=7.0.0             # Test framework
pytest-cov>=4.0.0         # Coverage reporting
pytest-mock>=3.10.0       # Mocking utilities

# Code quality
ruff>=0.1.0               # Linting and formatting
mypy>=1.0.0               # Type checking

# Documentation
sphinx>=5.0.0             # Documentation generation (if needed)
```

**Installation**:
```bash
pip install pytest pytest-cov pytest-mock ruff mypy
```

---

## Dependency Graph

### Visual Dependency Tree

```
aim/
├── registry/
│   ├── jsonschema (optional, for validation)
│   └── stdlib (json, os, re, pathlib)
│
├── environment/
│   ├── secrets.py
│   │   ├── keyring (required)
│   │   ├── pywin32 (Windows only)
│   │   └── stdlib (json, pathlib)
│   │
│   ├── health.py
│   │   ├── aim.registry (internal)
│   │   └── stdlib (subprocess, pathlib)
│   │
│   ├── scanner.py
│   │   └── stdlib (pathlib, os)
│   │
│   ├── installer.py
│   │   ├── requests (optional)
│   │   └── stdlib (subprocess, pathlib)
│   │
│   ├── version_control.py
│   │   ├── packaging (optional)
│   │   └── stdlib (re)
│   │
│   └── audit.py
│       └── stdlib (json, datetime, pathlib)
│
├── cli/
│   ├── click (required)
│   ├── rich (required)
│   ├── tabulate (optional)
│   ├── aim.environment (internal)
│   ├── aim.registry (internal)
│   └── stdlib
│
├── services/
│   ├── aim.registry (internal)
│   ├── aim.environment (internal)
│   └── stdlib
│
└── bridge.py
    ├── aim.registry (internal)
    ├── aim.environment (internal)
    └── stdlib (json, pathlib, subprocess)
```

---

## Dependency Constraints

### Version Constraints

**Minimum Versions** (tested compatibility):
- Python: 3.8+
- jsonschema: 4.0.0+
- click: 8.0.0+
- rich: 13.0.0+
- keyring: 24.0.0+

**Maximum Versions**: None (aim for latest compatible)

**Pinned Versions**: None (semantic versioning preferred)

### Platform-Specific Dependencies

| Package | Windows | macOS | Linux | Notes |
|---------|---------|-------|-------|-------|
| pywin32 | Required | N/A | N/A | DPAPI for secret storage |
| keyring | Optional | Required | Required | System keyring integration |

### Conflict Resolution

**Known Conflicts**: None

**Workarounds**: If `jsonschema` not available, validation is skipped with warning.

---

## Dependency Installation

### Standard Installation

```bash
# Install AIM with required dependencies
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"

# Install with all optional dependencies
pip install -e ".[all]"
```

### Manual Installation

```bash
# Core dependencies
pip install jsonschema click rich keyring

# Windows-specific
pip install pywin32  # Windows only

# Optional dependencies
pip install tabulate requests packaging

# Development dependencies
pip install pytest pytest-cov pytest-mock ruff mypy
```

### Verification

```bash
# Verify dependencies installed
python -c "import jsonschema, click, rich, keyring; print('✓ Core dependencies OK')"

# Check optional dependencies
python -c "import tabulate, requests, packaging; print('✓ Optional dependencies OK')"
```

---

## Import Patterns

### Correct Import Patterns

```python
# Registry
from aim.registry.config_loader import ConfigLoader

# Environment
from aim.environment.secrets import get_secrets_manager
from aim.environment.health import HealthMonitor
from aim.environment.scanner import ToolScanner
from aim.environment.installer import ToolInstaller
from aim.environment.version_control import VersionManager
from aim.environment.audit import AuditLogger

# Exceptions
from aim.environment.exceptions import (
    ConfigurationError,
    ToolNotFoundError,
    SecretStorageError
)

# CLI
from aim.cli.main import cli
```

### Import Validation

The repository enforces section-based imports via CI:

```bash
# Check for deprecated imports (should find none in aim/)
python scripts/paths_index_cli.py gate --db refactor_paths.db
```

---

## Dependency Management

### Adding New Dependencies

1. **Evaluate necessity**: Is it really needed? Can stdlib be used?
2. **Check license**: Ensure compatible with project license
3. **Check maintenance**: Is package actively maintained?
4. **Add to requirements**: Update `requirements.txt` or `pyproject.toml`
5. **Document here**: Add to this file with rationale
6. **Update tests**: Ensure tests don't break with new dependency

### Removing Dependencies

1. **Verify unused**: Search codebase for imports
2. **Check tests**: Ensure tests don't rely on it
3. **Update docs**: Remove from this file
4. **Remove from requirements**: Update dependency files
5. **Test thoroughly**: Run full test suite

---

## Dependency Alternatives

### Optional Backends

Several components support multiple backends:

| Component | Primary Backend | Alternative | Fallback |
|-----------|----------------|-------------|----------|
| Secret storage | keyring | pywin32 (Windows) | In-memory (testing) |
| Validation | jsonschema | None | Skip validation |
| HTTP | requests | urllib | Manual download |

### Graceful Degradation

```python
# Example: Optional jsonschema
try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    # Validation skipped with warning

def load_config(validate=True):
    if validate and not JSONSCHEMA_AVAILABLE:
        logger.warning("jsonschema not available, skipping validation")
        validate = False
    # ... rest of implementation
```

---

## Security Considerations

### Dependency Security

1. **Pin versions** in production deployments
2. **Audit dependencies** regularly using tools like `pip-audit`
3. **Minimize dependencies** to reduce attack surface
4. **Review licenses** to ensure compliance

### Checking for Vulnerabilities

```bash
# Install pip-audit
pip install pip-audit

# Audit dependencies
pip-audit

# Check specific package
pip-audit --requirement requirements.txt
```

---

## Upgrade Strategy

### Regular Updates

- **Minor updates**: Monthly (backward compatible)
- **Patch updates**: As needed (security fixes)
- **Major updates**: Quarterly (review breaking changes)

### Upgrade Process

1. **Check changelog**: Review breaking changes
2. **Update requirements**: Bump versions
3. **Run tests**: Ensure nothing breaks
4. **Update docs**: Document any changes
5. **Deploy**: Roll out to production

---

## Troubleshooting

### Dependency Not Found

**Problem**: `ModuleNotFoundError: No module named 'keyring'`

**Solution**:
```bash
pip install keyring
```

### Version Conflict

**Problem**: `ERROR: pip's dependency resolver...`

**Solutions**:
1. Create fresh virtual environment
2. Install in order: core dependencies, then optional
3. Use `pip install --upgrade` to resolve conflicts

### Platform-Specific Issues

**Windows**: Missing `pywin32`
```bash
pip install pywin32
```

**macOS**: Keyring access denied
```bash
# Grant keychain access in System Preferences > Security & Privacy
```

**Linux**: Missing system dependencies for keyring
```bash
# Ubuntu/Debian
sudo apt-get install python3-dbus

# Fedora
sudo dnf install python3-dbus
```

---

## See Also

- [aim/README.md](README.md) - Main module documentation
- [aim/STRUCTURE.md](STRUCTURE.md) - Module structure
- [requirements.txt](../requirements.txt) - Repository dependencies
- [pyproject.toml](../pyproject.toml) - Project configuration
- [CODEBASE_INDEX.yaml](../CODEBASE_INDEX.yaml) - Module dependency graph
