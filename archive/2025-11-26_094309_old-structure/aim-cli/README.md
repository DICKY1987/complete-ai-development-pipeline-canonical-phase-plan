# AIM CLI Module

> **Module**: `aim.cli`  
> **Purpose**: Command-line interface for AIM+ operations  
> **Parent**: `aim/`  
> **Layer**: UI  
> **Status**: Production

---

## Overview

The `aim/cli/` module provides a comprehensive command-line interface for managing AI tools, secrets, environment configuration, and system health. It uses Click for command parsing and Rich for enhanced console output.

**Key Responsibilities**:
- Secret management (set, get, list, delete)
- Health checks and diagnostics
- Tool installation and management
- Environment scanning
- Version control and compatibility checking
- Audit log querying and export

---

## Module Structure

```
aim/cli/
├── __init__.py          # Public API exports
├── main.py              # CLI entry point and command group
├── commands/            # Command implementations
│   ├── __init__.py
│   ├── secrets.py       # Secret management commands
│   ├── health.py        # Health check commands
│   ├── tools.py         # Tool management commands
│   ├── scan.py          # Environment scanning commands
│   ├── version.py       # Version control commands
│   └── audit.py         # Audit log commands
└── README.md            # This file
```

---

## Core Commands

### Entry Point (`main.py`)

Main CLI entry point using Click command groups.

**Usage**:
```bash
# Show help
python -m aim.cli --help
aim --help

# Show version
aim --version
```

**Command Groups**:
- `secrets` - Secret management
- `health` - Health checks and diagnostics
- `tools` - Tool installation and management
- `scan` - Environment scanning
- `version` - Version control
- `audit` - Audit log management

---

### Secret Management (`commands/secrets.py`)

Manage API keys and credentials securely.

**Commands**:
```bash
# Set a secret
aim secrets set <key_name>
aim secrets set openai_api_key

# Get a secret (masked output)
aim secrets get <key_name>

# List all secrets
aim secrets list

# Delete a secret
aim secrets delete <key_name>

# Export secrets (encrypted backup)
aim secrets export <output_file>

# Import secrets (from backup)
aim secrets import <input_file>
```

**Features**:
- Interactive password prompts (no command-line exposure)
- Masked output for security
- Encrypted backup/restore
- Platform-native secret storage

**Example**:
```bash
$ aim secrets set openai_api_key
Enter secret value: ••••••••••••
✓ Secret 'openai_api_key' stored successfully

$ aim secrets list
Configured secrets:
  • openai_api_key
  • anthropic_api_key
  • github_token
```

---

### Health Checks (`commands/health.py`)

Monitor environment and tool health.

**Commands**:
```bash
# Run comprehensive health check
aim health check

# Check specific tool
aim health check --tool aider

# Watch mode (continuous monitoring)
aim health watch --interval 60

# Export health report
aim health report --output health_report.json
```

**Health Categories**:
- Registry status
- Tool availability
- API key configuration
- Version compatibility
- Network connectivity

**Example Output**:
```bash
$ aim health check
╭─────────────── AIM+ Health Check ───────────────╮
│                                                   │
│  ✓ Registry: OK                                  │
│  ✓ Tools Detected: 3/4                           │
│    ✓ aider (v0.5.0)                              │
│    ✓ claude-cli (v1.2.0)                         │
│    ✓ ollama (v0.1.17)                            │
│    ✗ jules (not found)                           │
│  ✓ Secrets: OK                                   │
│  ✓ Overall Status: HEALTHY                       │
│                                                   │
╰───────────────────────────────────────────────────╯
```

---

### Tool Management (`commands/tools.py`)

Install, update, and manage AI tools.

**Commands**:
```bash
# List available tools
aim tools list

# List installed tools
aim tools list --installed

# Install tool
aim tools install <tool_id>
aim tools install aider

# Install all tools
aim tools install-all

# Uninstall tool
aim tools uninstall <tool_id>

# Update tool
aim tools update <tool_id>
aim tools update --all

# Show tool info
aim tools info <tool_id>
```

**Installation Methods**:
- pip (Python tools)
- npm (Node.js tools)
- Binary download (platform-specific)
- Custom installers

**Example**:
```bash
$ aim tools list
Available Tools:
┌──────────────┬──────────┬─────────────────────────────┐
│ ID           │ Installed│ Capabilities                │
├──────────────┼──────────┼─────────────────────────────┤
│ aider        │    ✓     │ code_generation, refactor   │
│ jules        │    ✗     │ code_generation, docs       │
│ claude-cli   │    ✓     │ chat, completion            │
│ ollama       │    ✓     │ chat, completion, embedding │
└──────────────┴──────────┴─────────────────────────────┘

$ aim tools install jules
Installing jules...
✓ jules v1.0.0 installed successfully
```

---

### Environment Scanning (`commands/scan.py`)

Scan for duplicates, caches, and optimization opportunities.

**Commands**:
```bash
# Scan for all issues
aim scan all

# Scan for duplicate installations
aim scan duplicates

# Scan for large caches
aim scan caches

# Get cleanup recommendations
aim scan recommendations

# Clean caches (with confirmation)
aim scan clean --dry-run
aim scan clean --confirm
```

**Scan Categories**:
- Duplicate binary installations
- Large cache directories
- Configuration conflicts
- Orphaned files

**Example**:
```bash
$ aim scan duplicates
Duplicate Installations Found:
┌──────────────┬───────────────────────────────────────┐
│ Tool         │ Locations                             │
├──────────────┼───────────────────────────────────────┤
│ aider        │ • /usr/local/bin/aider                │
│              │ • /home/user/.local/bin/aider         │
├──────────────┼───────────────────────────────────────┤
│ ollama       │ • /opt/ollama/bin/ollama              │
│              │ • /usr/bin/ollama                     │
└──────────────┴───────────────────────────────────────┘

Recommendation: Remove duplicate installations to avoid conflicts
```

---

### Version Control (`commands/version.py`)

Manage tool versions and compatibility.

**Commands**:
```bash
# Check versions
aim version check

# Check specific tool version
aim version check --tool aider

# Pin tool to version
aim version pin <tool_id> <version>
aim version pin aider 0.5.0

# Unpin tool (use latest)
aim version unpin <tool_id>

# List available versions
aim version list <tool_id>

# Show version constraints
aim version constraints
```

**Features**:
- Semantic version parsing
- Compatibility checking
- Version pinning
- Automatic recommendations

**Example**:
```bash
$ aim version check
Tool Version Status:
┌──────────────┬─────────┬────────────┬────────────┐
│ Tool         │ Current │ Latest     │ Status     │
├──────────────┼─────────┼────────────┼────────────┤
│ aider        │ 0.5.0   │ 0.6.0      │ Update     │
│ claude-cli   │ 1.2.0   │ 1.2.0      │ Current    │
│ ollama       │ 0.1.17  │ 0.1.20     │ Update     │
└──────────────┴─────────┴────────────┴────────────┘
```

---

### Audit Logs (`commands/audit.py`)

Query and analyze audit logs.

**Commands**:
```bash
# View recent logs
aim audit logs --tail 50

# Filter by tool
aim audit logs --tool aider

# Filter by date range
aim audit logs --since 2025-11-20 --until 2025-11-22

# Filter by success/failure
aim audit logs --failed-only

# Export logs
aim audit export --output audit_report.jsonl

# Show statistics
aim audit stats

# Show cost summary
aim audit costs --tool aider --days 30
```

**Audit Information**:
- Timestamp and duration
- Tool and capability used
- Input/output payloads (sanitized)
- Success/failure status
- Cost (if applicable)

**Example**:
```bash
$ aim audit stats
Audit Statistics (Last 30 Days):
┌──────────────┬───────────┬──────────┬──────────────┐
│ Tool         │ Invocations│ Success │ Avg Duration │
├──────────────┼───────────┼──────────┼──────────────┤
│ aider        │ 45        │ 43 (96%) │ 38.5s        │
│ claude-cli   │ 12        │ 12 (100%)│ 5.2s         │
│ ollama       │ 23        │ 21 (91%) │ 12.3s        │
└──────────────┴───────────┴──────────┴──────────────┘

Total Cost: $2.45
```

---

## Public Interface

The module exposes the following through `__init__.py`:

```python
__version__ = "1.0.0"
__all__ = []  # Currently minimal
```

**Suggested Enhancement**: Export CLI entry point:
```python
from .main import cli

__all__ = ["cli"]
```

---

## Integration Points

### Entry Points

The CLI can be invoked in multiple ways:

1. **As Python module**:
   ```bash
   python -m aim.cli <command>
   ```

2. **Via installed command** (after pip install):
   ```bash
   aim <command>
   ```

3. **Direct execution** (with shebang):
   ```bash
   ./aim/cli/main.py <command>
   ```

### Used By
- End users for manual operations
- CI/CD pipelines for automation
- Scripts for batch operations

### Dependencies
- `aim.environment.*` - Environment management
- `aim.registry.*` - Configuration loading
- External: `click`, `rich`, `tabulate`
- Standard library: `json`, `os`, `pathlib`, `datetime`

---

## Configuration

CLI behavior can be customized via:

**Environment Variables**:
- `AIM_CONFIG_PATH` - Override config file location
- `AIM_REGISTRY_PATH` - Override registry location
- `AIM_NO_COLOR` - Disable colored output
- `AIM_VERBOSE` - Enable verbose logging

**Config File** (`aim/config/aim_config.json`):
```json
{
  "cli": {
    "default_output_format": "table",
    "color_enabled": true,
    "pager_enabled": false,
    "confirm_destructive": true
  }
}
```

---

## Testing

Tests are located in `aim/tests/cli/`:

```bash
# Run CLI tests
pytest aim/tests/cli/ -v

# Run specific command tests
pytest aim/tests/cli/test_secrets.py -v
pytest aim/tests/cli/test_health.py -v

# Test with real terminal (PTY)
pytest aim/tests/cli/ --with-pty -v
```

---

## Development

### Adding a New Command

1. Create command file in `commands/`:
   ```python
   # aim/cli/commands/mycommand.py
   import click
   
   @click.group()
   def mycommand():
       """My command description."""
       pass
   
   @mycommand.command()
   def subcommand():
       """Subcommand description."""
       click.echo("Hello from mycommand!")
   ```

2. Register in `main.py`:
   ```python
   from aim.cli.commands.mycommand import mycommand
   
   cli.add_command(mycommand)
   ```

3. Add tests:
   ```python
   # aim/tests/cli/test_mycommand.py
   from click.testing import CliRunner
   from aim.cli.main import cli
   
   def test_mycommand():
       runner = CliRunner()
       result = runner.invoke(cli, ["mycommand", "subcommand"])
       assert result.exit_code == 0
       assert "Hello" in result.output
   ```

---

## Best Practices

1. **User Experience**:
   - Use Rich for formatted output
   - Show progress for long operations
   - Confirm destructive actions
   - Provide helpful error messages

2. **Error Handling**:
   - Catch and display user-friendly errors
   - Exit with appropriate codes (0=success, 1=error)
   - Log errors to audit trail

3. **Testing**:
   - Use `CliRunner` for command testing
   - Mock external dependencies
   - Test both success and error paths

4. **Documentation**:
   - Add docstrings to all commands
   - Keep help text concise and actionable
   - Provide examples in help text

---

## See Also

- [aim/README.md](../README.md) - Main AIM documentation
- [aim/environment/README.md](../environment/README.md) - Environment module
- [CODEBASE_INDEX.yaml](../../CODEBASE_INDEX.yaml) - Module dependencies
- Click documentation: https://click.palletsprojects.com/
- Rich documentation: https://rich.readthedocs.io/
