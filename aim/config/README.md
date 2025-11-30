---
doc_id: DOC-AIM-README-162
---

# AIM Configuration

> **Directory**: `aim/config/`  
> **Purpose**: Configuration files and schemas for AIM+  
> **Parent**: `aim/`  
> **Layer**: Infrastructure  
> **Status**: Production

---

## Overview

The `aim/config/` directory contains configuration files and JSON schemas for AIM+ (AI Manager Plus). Configuration serves as both runtime settings and documentation of system capabilities.

**Key Responsibilities**:
- Define tool capabilities and routing rules
- Specify environment settings and preferences
- Provide JSON schema validation
- Document system configuration contract

---

## Directory Structure

```
aim/config/
├── aim_config.json         # Main configuration file
├── aim_config.schema.json  # JSON schema for validation
└── README.md               # This file
```

---

## Configuration Files

### Main Configuration (`aim_config.json`)

Primary configuration file for AIM+ system.

**Structure**:
```json
{
  "metadata": {
    "version": "1.0",
    "contract": "AIM_PLUS_V1",
    "last_updated": "2025-11-22"
  },
  
  "tools": [
    {
      "id": "aider",
      "name": "Aider",
      "binary": "aider",
      "capabilities": ["code_generation", "refactoring"],
      "priority": 1,
      "enabled": true
    }
  ],
  
  "capabilities": {
    "code_generation": {
      "description": "Generate or modify code",
      "preferred_tools": ["aider", "jules", "claude-cli"],
      "fallback_chain": true,
      "timeout_sec": 300
    }
  },
  
  "settings": {
    "registry_path": "${AIM_REGISTRY_PATH}",
    "audit_enabled": true,
    "audit_path": ".state/aim/audit.jsonl",
    "health_check_interval_sec": 300,
    "secret_backend": "auto"
  },
  
  "environment": {
    "tool_detection": {
      "scan_paths": ["PATH", "~/.local/bin", "~/.cargo/bin"],
      "cache_ttl_sec": 3600
    },
    "installer": {
      "auto_install": false,
      "verify_checksums": true,
      "trusted_sources": ["pypi.org", "npmjs.com"]
    }
  }
}
```

**Configuration Sections**:

1. **metadata** - Version and contract information
2. **tools** - Tool definitions and capabilities
3. **capabilities** - Capability-to-tool mappings
4. **settings** - Global AIM settings
5. **environment** - Environment-specific configuration

---

### Configuration Schema (`aim_config.schema.json`)

JSON Schema for validating `aim_config.json`.

**Purpose**:
- Validate configuration syntax and structure
- Document configuration contract
- Enable IDE autocomplete and validation
- Prevent configuration errors

**Validation**:
```python
from aim.registry.config_loader import ConfigLoader

loader = ConfigLoader()
config = loader.load(validate=True)  # Validates against schema
```

**Schema Highlights**:
- Required fields: `metadata`, `tools`, `capabilities`
- Type validation for all fields
- Enum constraints for known values
- Format validation for paths and URLs
- Additional properties allowed for extensibility

---

## Configuration Principles

### 1. Configuration as Documentation

Configuration files serve as living documentation of system capabilities.

**Example**: Tool capabilities are self-documenting:
```json
{
  "id": "aider",
  "capabilities": ["code_generation", "refactoring", "documentation"],
  "description": "AI pair programming tool for codebase changes"
}
```

### 2. Environment Variable Expansion

Support `${VAR_NAME}` syntax for environment variables:

```json
{
  "settings": {
    "registry_path": "${AIM_REGISTRY_PATH}",
    "data_dir": "${HOME}/.aim"
  }
}
```

### 3. Sensible Defaults

Provide working defaults that require minimal customization:

```json
{
  "settings": {
    "audit_enabled": true,        // Default: enabled
    "secret_backend": "auto",     // Default: platform auto-detect
    "health_check_interval_sec": 300  // Default: 5 minutes
  }
}
```

### 4. Extensibility

Allow additional properties for future expansion:

```json
{
  "tools": [{
    "id": "custom_tool",
    "custom_field": "allowed"  // Additional properties permitted
  }]
}
```

---

## Configuration Loading

### Default Loading

```python
from aim.registry.config_loader import ConfigLoader

# Load default configuration
loader = ConfigLoader()
config = loader.load()

# Access sections
tools = config["tools"]
capabilities = config["capabilities"]
settings = config["settings"]
```

### Custom Configuration Path

```python
from pathlib import Path

# Load from custom location
loader = ConfigLoader(config_path=Path("/etc/aim/custom_config.json"))
config = loader.load()
```

### Environment Variable Override

```bash
# Override registry path
export AIM_REGISTRY_PATH="/custom/registry/path"

# Override entire config file
export AIM_CONFIG_PATH="/custom/config.json"
```

---

## Editing Configuration

### Manual Editing

1. Open `aim/config/aim_config.json`
2. Make changes following schema
3. Validate changes:
   ```bash
   python -c "from aim.registry.config_loader import ConfigLoader; ConfigLoader().load(validate=True)"
   ```
4. Restart affected services

### Programmatic Updates

```python
import json
from pathlib import Path

# Load config
config_path = Path("aim/config/aim_config.json")
with open(config_path) as f:
    config = json.load(f)

# Modify config
config["settings"]["audit_enabled"] = False

# Save config
with open(config_path, "w") as f:
    json.dump(config, f, indent=2)
```

---

## Common Configurations

### Disable Audit Logging

```json
{
  "settings": {
    "audit_enabled": false
  }
}
```

### Change Health Check Interval

```json
{
  "settings": {
    "health_check_interval_sec": 600  // 10 minutes
  }
}
```

### Use Specific Secret Backend

```json
{
  "settings": {
    "secret_backend": "keyring"  // Force keyring instead of auto-detect
  }
}
```

### Add Custom Tool

```json
{
  "tools": [
    {
      "id": "my_custom_tool",
      "name": "My Custom Tool",
      "binary": "my-tool",
      "capabilities": ["custom_capability"],
      "priority": 10,
      "enabled": true
    }
  ]
}
```

### Define Custom Capability

```json
{
  "capabilities": {
    "custom_capability": {
      "description": "My custom capability",
      "preferred_tools": ["my_custom_tool"],
      "fallback_chain": false,
      "timeout_sec": 120
    }
  }
}
```

---

## Validation

### Schema Validation

```bash
# Validate configuration
python -c "from aim.registry.config_loader import ConfigLoader; \
           loader = ConfigLoader(); \
           config = loader.load(validate=True); \
           print('✓ Configuration valid')"
```

### Manual Schema Check

```bash
# Using jsonschema CLI (if installed)
jsonschema -i aim/config/aim_config.json aim/config/aim_config.schema.json
```

---

## Troubleshooting

### Configuration Not Found

**Problem**: `ConfigurationError: Configuration file not found`

**Solutions**:
1. Check file exists at `aim/config/aim_config.json`
2. Set `AIM_CONFIG_PATH` environment variable
3. Verify file permissions (readable)

### Schema Validation Failed

**Problem**: `ConfigurationError: Schema validation failed`

**Solutions**:
1. Check JSON syntax (use JSON validator)
2. Verify required fields present
3. Check field types match schema
4. Review schema error details

### Environment Variable Not Expanded

**Problem**: Literal `${VAR_NAME}` in configuration

**Solutions**:
1. Ensure environment variable is set: `export VAR_NAME=value`
2. Check variable name matches exactly (case-sensitive)
3. Verify ConfigLoader performs expansion (implementation-dependent)

---

## See Also

- [aim/README.md](../README.md) - Main AIM documentation
- [aim/registry/README.md](../registry/README.md) - Registry module (loads config)
- [CODEBASE_INDEX.yaml](../../CODEBASE_INDEX.yaml) - Module dependencies
- [docs/CONFIGURATION_GUIDE.md](../../docs/CONFIGURATION_GUIDE.md) - General configuration guide
- JSON Schema: https://json-schema.org/
