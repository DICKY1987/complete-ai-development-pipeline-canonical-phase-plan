---
doc_id: DOC-GUIDE-PROJECT-AIM-REGISTRY-README-1573
---

# AIM Registry Module

> **Module**: `aim.registry`  
> **Purpose**: Tool capability registry, configuration loading, and routing logic  
> **Parent**: `aim/`  
> **Layer**: API  
> **Status**: Production

---

## Overview

The `aim/registry/` module manages AI tool registration, capability definitions, and routing logic. It provides the core infrastructure for capability-based tool selection and configuration management.

**Key Responsibilities**:
- Load and validate AIM configuration (`aim_config.json`)
- Provide configuration schema validation
- Support environment variable expansion in configs
- Maintain backward compatibility with legacy configurations

---

## Module Structure

```
aim/registry/
├── __init__.py          # Public interface exports
├── config_loader.py     # Configuration loading and validation
└── README.md            # This file
```

---

## Core Components

### Configuration Loader (`config_loader.py`)

Unified configuration loader for merged AIM+ config.

**Class**: `ConfigLoader`

**Key Methods**:
```python
from aim.registry.config_loader import ConfigLoader

# Initialize loader
loader = ConfigLoader()  # Uses default aim/config/aim_config.json
loader = ConfigLoader(config_path=Path("/custom/path/config.json"))  # Custom path

# Load configuration
config = loader.load(validate=True)  # Load and validate against schema

# Access configuration sections
tools = config.get("tools", [])
capabilities = config.get("capabilities", {})
settings = config.get("settings", {})
```

**Features**:
- JSON schema validation (if `jsonschema` package available)
- Environment variable expansion (`${VAR_NAME}` syntax)
- Backward compatibility with legacy configs
- Automatic fallback to default paths

**Configuration Paths**:
1. Custom path (if provided to constructor)
2. Default: `aim/config/aim_config.json`
3. Schema: `aim/config/aim_config.schema.json`

---

## Public Interface

The module exposes the following through `__init__.py`:

```python
# Currently empty - consider adding:
# from .config_loader import ConfigLoader
# __all__ = ["ConfigLoader"]
```

**Suggested Enhancement**: Export `ConfigLoader` as the public interface.

---

## Integration Points

### Used By
- `aim.bridge` - Main integration bridge
- `aim.environment.health` - Health checks requiring config
- `aim.cli` - CLI commands for config management

### Dependencies
- `aim.environment.exceptions` - Configuration error handling
- `jsonschema` (optional) - Schema validation
- Standard library: `json`, `os`, `re`, `pathlib`

---

## Configuration Schema

The registry loads configuration from `aim/config/aim_config.json` which follows the schema defined in `aim/config/aim_config.schema.json`.

**Example Configuration Structure**:
```json
{
  "metadata": {
    "version": "1.0",
    "contract": "AIM_PLUS_V1"
  },
  "tools": [
    {
      "id": "aider",
      "name": "Aider",
      "binary": "aider",
      "capabilities": ["code_generation", "refactoring"],
      "priority": 1
    }
  ],
  "capabilities": {
    "code_generation": {
      "description": "Generate or modify code",
      "preferred_tools": ["aider", "jules"],
      "fallback_chain": true
    }
  },
  "settings": {
    "registry_path": "${AIM_REGISTRY_PATH}",
    "audit_enabled": true
  }
}
```

---

## Usage Examples

### Basic Configuration Loading

```python
from aim.registry.config_loader import ConfigLoader

# Load default configuration
loader = ConfigLoader()
config = loader.load(validate=True)

# Access tools
for tool in config.get("tools", []):
    print(f"Tool: {tool['id']} - Capabilities: {tool['capabilities']}")
```

### Environment Variable Expansion

```python
import os
os.environ["AIM_REGISTRY_PATH"] = "/custom/registry/path"

loader = ConfigLoader()
config = loader.load()

# ${AIM_REGISTRY_PATH} in config will be replaced with "/custom/registry/path"
print(config["settings"]["registry_path"])  # "/custom/registry/path"
```

### Custom Configuration Path

```python
from pathlib import Path
from aim.registry.config_loader import ConfigLoader

custom_path = Path("/etc/aim/custom_config.json")
loader = ConfigLoader(config_path=custom_path)
config = loader.load(validate=False)  # Skip validation if custom schema
```

---

## Error Handling

The module raises `ConfigurationError` (from `aim.environment.exceptions`) for:
- Missing configuration file
- Invalid JSON syntax
- Schema validation failures (if enabled)
- Invalid environment variable references

**Example**:
```python
from aim.registry.config_loader import ConfigLoader
from aim.environment.exceptions import ConfigurationError

try:
    loader = ConfigLoader()
    config = loader.load()
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

---

## Testing

Tests are located in `aim/tests/registry/`:

```bash
# Run registry tests
pytest aim/tests/registry/ -v

# Run specific test
pytest aim/tests/registry/test_config_loader.py -v
```

---

## Future Enhancements

**Planned Features**:
- [ ] Dynamic tool registration at runtime
- [ ] Capability routing logic (currently in `aim.bridge`)
- [ ] Tool priority calculation and selection
- [ ] Fallback chain resolution
- [ ] Configuration hot-reloading

**Migration Path**: Routing logic may be moved from `aim.bridge` to `aim.registry.router` for better separation of concerns.

---

## See Also

- [aim/README.md](../README.md) - Main AIM documentation
- [aim/config/aim_config.json](../config/aim_config.json) - Configuration file
- [aim/config/aim_config.schema.json](../config/aim_config.schema.json) - JSON schema
- [CODEBASE_INDEX.yaml](../../CODEBASE_INDEX.yaml) - Module dependencies
- [aim.bridge](../bridge.py) - Main integration bridge (uses this module)
