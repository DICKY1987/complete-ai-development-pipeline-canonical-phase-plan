# AIM+ Integration Plan: Unified AI Development Environment Manager

**Status**: Planning  
**Priority**: High  
**Estimated Duration**: 4 weeks (80-100 hours)  
**Created**: 2025-11-21  
**Contract Version**: AIM_PLUS_V1

---

## Executive Summary

This plan outlines the integration of **AI_MANGER** (InvokeBuild-based environment manager) into **AIM** (AI Tools Registry) to create **AIM+**, a unified AI development environment manager that combines capability-based AI tool routing with comprehensive environment management, secret handling, and health monitoring.

### Integration Goals

1. **Unified Tool Management** - Single system for AI tools + dev environment
2. **Secure Secret Handling** - DPAPI vault integrated with AI tool invocations
3. **Environment Health Checks** - Pre-flight validation before workstream execution
4. **Automated Setup** - One-command bootstrap for entire dev environment
5. **Python-First Architecture** - Migrate PowerShell plugins to Python modules
6. **Backward Compatibility** - Existing AIM contracts remain valid

### Value Proposition

| Capability | Before (Separate Systems) | After (AIM+) |
|------------|---------------------------|--------------|
| Secret Management | Manual `.env` files | DPAPI vault auto-injected into tool invocations |
| Environment Setup | Multi-step manual process | `python -m aim setup --all` |
| Health Checks | Ad-hoc verification | Automated pre-flight checks |
| Tool Installation | Scattered across CLIs | Centralized with version pinning |
| Audit Trail | Tool logs only | Tool + environment events unified |
| Configuration | 3+ JSON files | Single `aim_config.json` |

---

## Architecture Overview

### Current State

```
┌─────────────────────┐       ┌─────────────────────┐
│   AI_MANGER         │       │        AIM          │
│   (PowerShell)      │       │      (Python)       │
├─────────────────────┤       ├─────────────────────┤
│ • Secrets (DPAPI)   │       │ • Tool Registry     │
│ • Health Checks     │       │ • Capability Routing│
│ • Scanner           │       │ • Adapters (PS)     │
│ • Tool Installer    │       │ • Audit Logging     │
│ • Version Pinning   │       │ • Fallback Chains   │
│ • Watcher           │       │                     │
└─────────────────────┘       └─────────────────────┘
        ↓                              ↓
   build.ps1                      bridge.py
```

### Target State (AIM+)

```
┌────────────────────────────────────────────────────┐
│                    AIM+                            │
│         Unified AI Environment Manager             │
├────────────────────────────────────────────────────┤
│  Core Layers:                                      │
│  ┌──────────────────────────────────────────────┐ │
│  │  aim/registry/        - Tool capability DB   │ │
│  │  aim/environment/     - Env management       │ │
│  │  aim/adapters/        - Tool bridges (PS)    │ │
│  │  aim/services/        - Unified services     │ │
│  └──────────────────────────────────────────────┘ │
│                                                    │
│  Services:                                         │
│  • SecretsManager      - DPAPI vault + injection  │
│  • HealthMonitor       - Environment validation   │
│  • ToolInstaller       - Package management       │
│  • VersionController   - Pin/sync versions        │
│  • EnvironmentScanner  - Duplicate/cache finder   │
│  • AuditLogger         - Unified event trail      │
└────────────────────────────────────────────────────┘
                        ↓
            python -m aim <command>
```

### Directory Structure

```
aim/
├── __init__.py
├── bridge.py                      # Enhanced with environment features
├── exceptions.py
│
├── registry/                      # AI Tool Registry (existing)
│   ├── __init__.py
│   ├── loader.py
│   ├── validator.py
│   └── capability_router.py
│
├── environment/                   # NEW: Environment Management
│   ├── __init__.py
│   ├── secrets.py                 # Secret vault (from AI_MANGER)
│   ├── health.py                  # Health checks (from AI_MANGER)
│   ├── installer.py               # Tool installation (from AI_MANGER)
│   ├── scanner.py                 # Duplicate/cache finder
│   ├── watcher.py                 # Config file watcher
│   └── version_control.py         # Version pinning
│
├── adapters/                      # PowerShell adapters (existing)
│   ├── AIM_aider.ps1
│   ├── AIM_jules.ps1
│   └── AIM_claude-cli.ps1
│
├── services/                      # NEW: Unified Service Layer
│   ├── __init__.py
│   ├── environment_service.py     # Orchestrates env operations
│   └── integration_service.py     # Bridges registry + environment
│
├── cli/                           # NEW: Unified CLI
│   ├── __init__.py
│   ├── main.py                    # python -m aim entry point
│   ├── commands/
│   │   ├── setup.py               # Bootstrap command
│   │   ├── health.py              # Health check command
│   │   ├── secrets.py             # Secret management
│   │   ├── tools.py               # Tool management
│   │   └── scan.py                # Scanner command
│   └── output.py                  # CLI formatting
│
├── config/                        # Merged configuration
│   ├── aim_config.json            # Unified config (merged)
│   ├── aim_config.schema.json     # JSON Schema
│   └── README.md                  # Config documentation
│
├── .AIM_ai-tools-registry/        # Registry data (existing)
│   ├── AIM_registry.json
│   ├── AIM_adapters/
│   ├── AIM_audit/
│   └── logs/
│
└── tests/                         # Test suite
    ├── test_secrets.py
    ├── test_health.py
    ├── test_installer.py
    └── test_integration.py
```

---

## Phase Breakdown

### Phase 1: Foundation & Secrets (Week 1)

**Duration**: 20-24 hours  
**Priority**: Critical  
**Dependencies**: None

#### Phase 1A: Project Structure (4 hours)

**Tasks:**
1. Create directory structure (`aim/environment/`, `aim/services/`, `aim/cli/`)
2. Set up `pyproject.toml` for CLI entry point
3. Create base exception classes
4. Initialize test directory structure

**Deliverables:**
```
aim/
├── environment/__init__.py
├── services/__init__.py
├── cli/__init__.py
└── tests/environment/
```

**Validation:**
```bash
python -c "from aim.environment import *"  # Should not error
pytest aim/tests/ -v                        # Should pass (empty)
```

#### Phase 1B: Secrets Management (8 hours)

**Tasks:**
1. Implement `aim/environment/secrets.py`:
   - `SecretsManager` class using `keyring` library
   - Methods: `set_secret()`, `get_secret()`, `list_secrets()`, `delete_secret()`
   - Support for DPAPI on Windows (fallback to `keyring` default)
   - JSON vault file for non-sensitive metadata
2. Create `aim/cli/commands/secrets.py` CLI wrapper
3. Integrate with `aim/bridge.py` for auto-injection
4. Write unit tests (`tests/environment/test_secrets.py`)

**Key Implementation:**
```python
# aim/environment/secrets.py
import keyring
from pathlib import Path
from typing import Optional

class SecretsManager:
    """Secure secret storage using system keyring (DPAPI on Windows)."""
    
    SERVICE_NAME = "aim-plus"
    
    def set_secret(self, key: str, value: str) -> None:
        """Store a secret securely."""
        keyring.set_password(self.SERVICE_NAME, key, value)
    
    def get_secret(self, key: str) -> Optional[str]:
        """Retrieve a secret."""
        return keyring.get_password(self.SERVICE_NAME, key)
    
    def list_secrets(self) -> list[str]:
        """List all stored secret keys."""
        # Implementation using vault metadata file
        pass
    
    def inject_into_env(self, keys: list[str]) -> dict[str, str]:
        """Get secrets as environment variables."""
        return {key: self.get_secret(key) for key in keys if self.get_secret(key)}
```

**Integration with bridge.py:**
```python
# aim/bridge.py (enhanced)
from aim.environment.secrets import SecretsManager

def invoke_tool(tool_id: str, capability: str, **kwargs):
    """Invoke AI tool with automatic secret injection."""
    # Existing logic...
    
    # NEW: Inject secrets before invocation
    secrets = SecretsManager()
    env_vars = secrets.inject_into_env(["OPENAI_API_KEY", "ANTHROPIC_API_KEY"])
    
    # Pass to adapter
    result = _call_adapter(tool_id, env_vars=env_vars, **kwargs)
    return result
```

**Deliverables:**
- `aim/environment/secrets.py` - Full implementation
- `aim/cli/commands/secrets.py` - CLI wrapper
- `tests/environment/test_secrets.py` - Unit tests (>90% coverage)
- Updated `aim/bridge.py` - Secret auto-injection

**Validation:**
```bash
# Manual test
python -m aim secrets set OPENAI_API_KEY sk-test123
python -m aim secrets list
python -m aim secrets get OPENAI_API_KEY  # Should show value

# Unit tests
pytest aim/tests/environment/test_secrets.py -v
```

#### Phase 1C: Configuration Merge (8 hours)

**Tasks:**
1. Design merged `aim_config.json` schema:
   - Merge `AI_MANGER/config/toolstack.config.json`
   - Merge `aim/.AIM_ai-tools-registry/AIM_registry.json`
   - Add new environment sections
2. Implement `aim/registry/config_loader.py`
3. Create JSON Schema for validation
4. Migration script: `scripts/migrate_config.py`
5. Update existing loaders to use merged config

**Schema Design:**
```json
{
  "$schema": "aim_config.schema.json",
  "version": "1.0.0",
  
  "registry": {
    "tools": {
      "aider": {
        "name": "Aider CLI",
        "detectCommands": ["aider", "%USERPROFILE%/.local/bin/aider.exe"],
        "versionCommand": ["aider", "--version"],
        "capabilities": ["code_generation"],
        "adapterScript": "%AIM_REGISTRY_PATH%/AIM_adapters/AIM_aider.ps1",
        "pinnedVersion": "0.5.0",
        "autoUpdate": false
      }
    },
    "capabilities": {
      "code_generation": {
        "primaryTool": "aider",
        "fallbacks": ["jules", "claude-cli"]
      }
    }
  },
  
  "environment": {
    "toolsRoot": "C:\\Tools",
    "pipxApps": ["aider-chat", "ruff", "black", "pytest"],
    "npmGlobal": ["@anthropic-ai/claude-code", "@google/jules"],
    "secretsVault": "%USERPROFILE%/.aim/secrets.json",
    "centralCache": "C:\\Tools\\cache\\aim",
    "healthChecks": {
      "enabled": true,
      "requiredCommands": ["git", "python", "node"],
      "requiredPaths": ["C:\\Tools\\pipx\\bin"]
    }
  },
  
  "audit": {
    "enabled": true,
    "logPath": "%AIM_REGISTRY_PATH%/AIM_audit/audit.jsonl",
    "events": ["tool_invoke", "secret_access", "health_check"]
  }
}
```

**Deliverables:**
- `aim/config/aim_config.json` - Merged configuration
- `aim/config/aim_config.schema.json` - JSON Schema
- `aim/registry/config_loader.py` - Unified loader
- `scripts/migrate_config.py` - Migration utility
- Updated `aim/bridge.py` to use new config

**Validation:**
```bash
# Validate schema
python scripts/validate_config.py

# Test migration
python scripts/migrate_config.py --dry-run
python scripts/migrate_config.py --apply

# Load test
python -c "from aim.registry.config_loader import load_config; load_config()"
```

---

### Phase 2: Health & Installation (Week 2)

**Duration**: 20-24 hours  
**Priority**: High  
**Dependencies**: Phase 1 complete

#### Phase 2A: Health Check System (8 hours)

**Tasks:**
1. Implement `aim/environment/health.py`:
   - `HealthMonitor` class
   - Check command availability
   - Validate PATH order
   - Check directory permissions
   - Verify AI tool detection
2. Create `aim/cli/commands/health.py`
3. Integrate with orchestrator for pre-flight checks
4. JSON report generation
5. Unit tests

**Key Implementation:**
```python
# aim/environment/health.py
from dataclasses import dataclass
from typing import Optional
import shutil
import subprocess

@dataclass
class HealthCheck:
    """Result of a single health check."""
    name: str
    status: str  # "pass", "warn", "fail"
    message: str
    details: Optional[dict] = None

class HealthMonitor:
    """System health validation."""
    
    def check_all(self) -> list[HealthCheck]:
        """Run all health checks."""
        return [
            self.check_commands(),
            self.check_ai_tools(),
            self.check_paths(),
            self.check_permissions(),
            self.check_secrets_vault()
        ]
    
    def check_commands(self) -> HealthCheck:
        """Verify required commands are available."""
        required = ["git", "python", "node", "pipx", "npm"]
        missing = [cmd for cmd in required if not shutil.which(cmd)]
        
        if not missing:
            return HealthCheck("commands", "pass", "All required commands found")
        return HealthCheck("commands", "fail", f"Missing: {', '.join(missing)}")
    
    def check_ai_tools(self) -> HealthCheck:
        """Check AI tool availability."""
        from aim.registry.loader import load_aim_registry
        
        registry = load_aim_registry()
        detected = []
        
        for tool_id, tool_info in registry["tools"].items():
            for cmd in tool_info["detectCommands"]:
                if shutil.which(cmd):
                    detected.append(tool_id)
                    break
        
        if detected:
            return HealthCheck(
                "ai_tools", "pass", 
                f"Detected: {', '.join(detected)}",
                {"detected": detected}
            )
        return HealthCheck("ai_tools", "warn", "No AI tools detected")
```

**Integration with orchestrator:**
```python
# core/engine/orchestrator.py (enhancement)
from aim.environment.health import HealthMonitor

class Orchestrator:
    def execute_workstream(self, ws_id: str, run_id: str):
        # NEW: Pre-flight health check
        health = HealthMonitor()
        checks = health.check_all()
        
        failed = [c for c in checks if c.status == "fail"]
        if failed:
            raise RuntimeError(f"Pre-flight checks failed: {[c.name for c in failed]}")
        
        # Existing execution logic...
```

**Deliverables:**
- `aim/environment/health.py` - Full implementation
- `aim/cli/commands/health.py` - CLI wrapper
- `tests/environment/test_health.py` - Unit tests
- Integration with orchestrator

**Validation:**
```bash
# CLI test
python -m aim health check --json
python -m aim health check --verbose

# Unit tests
pytest aim/tests/environment/test_health.py -v
```

#### Phase 2B: Tool Installer (12 hours)

**Tasks:**
1. Implement `aim/environment/installer.py`:
   - `ToolInstaller` class
   - Install via `pipx`, `npm`, `winget`
   - Version pinning support
   - Parallel installation
   - Rollback on failure
2. Create `aim/cli/commands/tools.py`
3. Integrate with version control
4. Unit and integration tests

**Key Implementation:**
```python
# aim/environment/installer.py
from dataclasses import dataclass
from typing import Literal
import subprocess
import asyncio

@dataclass
class InstallResult:
    """Result of a tool installation."""
    tool: str
    success: bool
    version: str
    message: str

class ToolInstaller:
    """Automated tool installation and management."""
    
    async def install_pipx(self, package: str, version: Optional[str] = None) -> InstallResult:
        """Install Python package via pipx."""
        cmd = ["pipx", "install"]
        if version:
            cmd.append(f"{package}=={version}")
        else:
            cmd.append(package)
        
        try:
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                version = await self._get_pipx_version(package)
                return InstallResult(package, True, version, "Installed successfully")
            
            return InstallResult(package, False, "", stderr.decode())
        except Exception as e:
            return InstallResult(package, False, "", str(e))
    
    async def install_all(self, tools: list[dict]) -> list[InstallResult]:
        """Install multiple tools in parallel."""
        tasks = []
        for tool in tools:
            if tool["manager"] == "pipx":
                tasks.append(self.install_pipx(tool["name"], tool.get("version")))
            elif tool["manager"] == "npm":
                tasks.append(self.install_npm(tool["name"], tool.get("version")))
        
        return await asyncio.gather(*tasks)
```

**Deliverables:**
- `aim/environment/installer.py` - Full implementation
- `aim/cli/commands/tools.py` - CLI wrapper
- `tests/environment/test_installer.py` - Tests
- Integration with `aim/environment/version_control.py`

**Validation:**
```bash
# Dry run
python -m aim tools install --dry-run

# Install specific tool
python -m aim tools install aider-chat --pin 0.5.0

# Install from config
python -m aim tools install --from-config

# Unit tests
pytest aim/tests/environment/test_installer.py -v
```

---

### Phase 3: Scanner & Watcher (Week 3)

**Duration**: 16-20 hours  
**Priority**: Medium  
**Dependencies**: Phase 2 complete

#### Phase 3A: Environment Scanner (8 hours)

**Tasks:**
1. Implement `aim/environment/scanner.py`:
   - Duplicate file detection (by hash)
   - Misplaced cache directory finder
   - Multiple AI tool installation detector
   - Report generation (JSON)
2. Create `aim/cli/commands/scan.py`
3. Unit tests

**Key Implementation:**
```python
# aim/environment/scanner.py
import hashlib
from pathlib import Path
from collections import defaultdict

class EnvironmentScanner:
    """Scan for environment issues and inefficiencies."""
    
    def find_duplicates(self, roots: list[Path], min_size_kb: int = 100) -> dict:
        """Find duplicate files by hash."""
        hash_map = defaultdict(list)
        
        for root in roots:
            for file in root.rglob("*"):
                if not file.is_file():
                    continue
                if file.stat().st_size < min_size_kb * 1024:
                    continue
                
                file_hash = self._hash_file(file)
                hash_map[file_hash].append(str(file))
        
        # Only return hashes with duplicates
        return {h: files for h, files in hash_map.items() if len(files) > 1}
    
    def find_misplaced_caches(self, roots: list[Path]) -> list[dict]:
        """Find cache directories outside central location."""
        patterns = [
            ".aider", ".jules", ".claude",
            "node_modules/.cache", ".pytest_cache",
            "__pycache__", ".mypy_cache"
        ]
        
        misplaced = []
        for root in roots:
            for pattern in patterns:
                for path in root.rglob(pattern):
                    if path.is_dir():
                        misplaced.append({
                            "path": str(path),
                            "pattern": pattern,
                            "size_mb": self._dir_size(path) / (1024 * 1024)
                        })
        
        return misplaced
    
    def find_duplicate_tools(self) -> dict:
        """Find multiple installations of same tool."""
        # Check pipx, npm, system PATH for duplicates
        pass
```

**Deliverables:**
- `aim/environment/scanner.py` - Full implementation
- `aim/cli/commands/scan.py` - CLI wrapper
- `tests/environment/test_scanner.py` - Tests

**Validation:**
```bash
python -m aim scan duplicates --min-size 1024
python -m aim scan caches --json
python -m aim scan tools
pytest aim/tests/environment/test_scanner.py -v
```

#### Phase 3B: Version Control (8 hours)

**Tasks:**
1. Implement `aim/environment/version_control.py`:
   - Track pinned versions from config
   - Detect version drift
   - Sync to desired versions
   - Report current vs. desired
2. Integrate with installer
3. Create `aim/cli/commands/version.py`
4. Tests

**Deliverables:**
- `aim/environment/version_control.py` - Implementation
- `aim/cli/commands/version.py` - CLI wrapper
- Tests

**Validation:**
```bash
python -m aim version report
python -m aim version sync --dry-run
python -m aim version sync --apply
```

---

### Phase 4: Integration & Polish (Week 4)

**Duration**: 20-24 hours  
**Priority**: High  
**Dependencies**: Phases 1-3 complete

#### Phase 4A: Unified CLI (8 hours)

**Tasks:**
1. Implement `aim/cli/main.py` with subcommands:
   - `setup` - Bootstrap entire environment
   - `health` - Run health checks
   - `secrets` - Manage secrets
   - `tools` - Install/update tools
   - `scan` - Run scanner
   - `version` - Version control
   - `config` - Config management
2. Rich CLI output with colors/tables
3. Progress indicators for long operations
4. JSON output mode for automation

**Key Implementation:**
```python
# aim/cli/main.py
import click
from rich.console import Console

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """AIM+ - Unified AI Development Environment Manager"""
    pass

@cli.command()
@click.option("--all", is_flag=True, help="Install everything")
@click.option("--secrets-only", is_flag=True, help="Setup secrets vault only")
@click.option("--tools-only", is_flag=True, help="Install tools only")
def setup(all, secrets_only, tools_only):
    """Bootstrap development environment."""
    console = Console()
    
    with console.status("[bold green]Setting up AIM+..."):
        if all or secrets_only:
            from aim.environment.secrets import SecretsManager
            SecretsManager().initialize()
            console.print("✓ Secrets vault initialized", style="green")
        
        if all or tools_only:
            from aim.environment.installer import ToolInstaller
            installer = ToolInstaller()
            # ... install tools
            console.print("✓ Tools installed", style="green")
    
    console.print("[bold green]Setup complete!")

if __name__ == "__main__":
    cli()
```

**Deliverables:**
- `aim/cli/main.py` - Unified CLI
- `aim/cli/output.py` - Formatting helpers
- `pyproject.toml` - CLI entry point configuration
- Documentation: `aim/CLI_REFERENCE.md`

**Validation:**
```bash
python -m aim --help
python -m aim setup --all
python -m aim health check
python -m aim secrets list
```

#### Phase 4B: Orchestrator Integration (8 hours)

**Tasks:**
1. Update `core/engine/orchestrator.py`:
   - Pre-flight health checks
   - Auto-inject secrets before tool invocation
   - Log environment events
2. Update `core/engine/tools.py`:
   - Use AIM+ for tool detection
   - Version validation before execution
3. Integration tests
4. Update workstream templates

**Deliverables:**
- Enhanced `core/engine/orchestrator.py`
- Enhanced `core/engine/tools.py`
- Integration tests: `tests/integration/test_aim_plus.py`
- Updated workstream examples

**Validation:**
```bash
# Run workstream with AIM+ integration
python scripts/run_workstream.py --ws-id test-aim-integration

# Verify secrets auto-injection
python -m pytest tests/integration/test_aim_plus.py -v
```

#### Phase 4C: Documentation & Migration (8 hours)

**Tasks:**
1. Write comprehensive documentation:
   - `aim/README.md` - Overview
   - `aim/MIGRATION_GUIDE.md` - AI_MANGER → AIM+ migration
   - `aim/CLI_REFERENCE.md` - CLI commands
   - `aim/CONFIGURATION.md` - Config reference
   - `aim/ARCHITECTURE.md` - System design
2. Create migration script
3. Update existing docs to reference AIM+
4. Deprecation notices for AI_MANGER

**Deliverables:**
- Complete documentation set
- `scripts/migrate_to_aim_plus.py` - Migration script
- Updated repository `README.md`
- `AI_MANGER/DEPRECATED.md` - Deprecation notice

**Validation:**
```bash
# Test migration
python scripts/migrate_to_aim_plus.py --dry-run

# Verify docs build
mkdocs build  # If using mkdocs
```

---

## Testing Strategy

### Unit Tests (Target: >85% coverage)

**Test Suites:**
```
aim/tests/
├── environment/
│   ├── test_secrets.py          # Secrets management
│   ├── test_health.py           # Health checks
│   ├── test_installer.py        # Tool installation
│   ├── test_scanner.py          # Environment scanner
│   └── test_version_control.py  # Version pinning
├── registry/
│   ├── test_config_loader.py    # Merged config loading
│   └── test_integration.py      # Registry + environment
├── cli/
│   ├── test_commands.py         # CLI command tests
│   └── test_output.py           # Formatting tests
└── integration/
    └── test_aim_plus.py         # End-to-end tests
```

**Testing Commands:**
```bash
# Unit tests
pytest aim/tests/ -v --cov=aim --cov-report=html

# Integration tests
pytest aim/tests/integration/ -v --slow

# Specific module
pytest aim/tests/environment/test_secrets.py -v
```

### Integration Tests

**Scenarios:**
1. **End-to-end setup**: `setup --all` → verify all components
2. **Secret injection**: Store secret → invoke tool → verify env var passed
3. **Health check failure**: Simulate missing command → verify graceful failure
4. **Version sync**: Pin version → install → verify correct version
5. **Scanner detection**: Create duplicates → scan → verify found

### Manual Testing Checklist

```markdown
## Pre-Release Checklist

### Phase 1
- [ ] Secrets vault creates on first use
- [ ] Secrets persist across sessions
- [ ] Secrets auto-inject into tool invocations
- [ ] Config migration completes without errors
- [ ] Merged config validates against schema

### Phase 2
- [ ] Health checks detect all required commands
- [ ] Health checks detect AI tools
- [ ] Failed health check blocks workstream execution
- [ ] Tool installation completes successfully
- [ ] Version pinning enforced

### Phase 3
- [ ] Scanner finds duplicate files
- [ ] Scanner detects misplaced caches
- [ ] Scanner detects duplicate tool installations
- [ ] Version report shows drift
- [ ] Version sync fixes drift

### Phase 4
- [ ] CLI `--help` works for all commands
- [ ] JSON output mode works
- [ ] Progress indicators display correctly
- [ ] Orchestrator pre-flight checks run
- [ ] Workstream execution uses AIM+
- [ ] Documentation renders correctly
```

---

## Migration Path

### For Existing AI_MANGER Users

**Step 1: Backup Current State**
```bash
# Backup secrets vault
cp "%USERPROFILE%/.toolstack/secrets.json" "%USERPROFILE%/.toolstack/secrets.json.bak"

# Backup config
cp AI_MANGER/config/toolstack.config.json toolstack.config.json.bak
```

**Step 2: Run Migration Script**
```bash
python scripts/migrate_to_aim_plus.py --dry-run
python scripts/migrate_to_aim_plus.py --apply
```

**Step 3: Verify Migration**
```bash
python -m aim health check
python -m aim secrets list
python -m aim tools list
```

**Step 4: Test Workstream**
```bash
python scripts/run_workstream.py --ws-id test-migration
```

### For Existing AIM Users

**Step 1: No Breaking Changes**
- Existing `aim/bridge.py` imports remain valid
- `AIM_registry.json` format compatible (extended)

**Step 2: Opt-in to New Features**
```bash
# Enable environment features
python -m aim setup --secrets-only

# Start using new CLI
python -m aim health check
```

---

## Rollback Plan

If integration causes issues:

**Immediate Rollback:**
```bash
# Restore AI_MANGER
git checkout AI_MANGER/

# Use legacy build
pwsh AI_MANGER/build.ps1 Bootstrap
```

**Gradual Rollback:**
```bash
# Disable AIM+ features in config
{
  "environment": {
    "enabled": false  // Add this flag
  }
}
```

---

## Success Metrics

### Phase 1 Success Criteria
- [ ] Secrets stored/retrieved without errors
- [ ] Secrets auto-inject into tool calls
- [ ] Config migration completes
- [ ] Unit tests pass (>85% coverage)

### Phase 2 Success Criteria
- [ ] Health checks detect system state
- [ ] Failed checks prevent workstream execution
- [ ] Tools install via CLI
- [ ] Version pinning works

### Phase 3 Success Criteria
- [ ] Scanner finds real issues
- [ ] Version drift detected and fixable

### Phase 4 Success Criteria
- [ ] CLI usable for all operations
- [ ] Orchestrator integrates seamlessly
- [ ] Documentation complete
- [ ] Migration path validated

### Overall Success
- [ ] 100% backward compatibility with AIM
- [ ] All AI_MANGER features available in AIM+
- [ ] Single command bootstrap works
- [ ] Integration tests pass
- [ ] Performance: <5s for health check, <2min for full setup

---

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| DPAPI secrets fail on non-Windows | High | Medium | Use `keyring` library (cross-platform) |
| Config migration loses data | High | Low | Dry-run mode + validation + backups |
| PowerShell adapter breaks | High | Low | Keep adapters unchanged; only enhance |
| Performance degradation | Medium | Low | Async operations + caching |
| Breaking changes to AIM contract | High | Low | Extensive backward compat tests |

---

## Dependencies

### Python Packages (Add to `requirements.txt`)
```
keyring>=24.0.0          # Cross-platform secret storage
rich>=13.0.0             # CLI output formatting
click>=8.1.0             # CLI framework
aiofiles>=23.0.0         # Async file operations
jsonschema>=4.20.0       # Config validation
```

### System Requirements
- Python 3.10+
- PowerShell 7+ (for adapters)
- Git
- pipx (for Python tool installation)
- npm (for Node tool installation)

---

## Timeline

```
Week 1: Foundation & Secrets
├─ Day 1-2: Project structure + secrets implementation
├─ Day 3-4: Config merge + migration script
└─ Day 5: Testing + documentation

Week 2: Health & Installation
├─ Day 1-2: Health check system
├─ Day 3-5: Tool installer + version control
└─ Day 5: Testing + integration

Week 3: Scanner & Watcher
├─ Day 1-2: Environment scanner
├─ Day 3-4: Version control system
└─ Day 5: Testing + refinement

Week 4: Integration & Polish
├─ Day 1-2: Unified CLI
├─ Day 3: Orchestrator integration
├─ Day 4-5: Documentation + migration + release prep
```

**Total Estimated Time**: 80-100 hours (4 weeks full-time or 8 weeks part-time)

---

## Post-Integration Roadmap

### Future Enhancements (Not in Scope)

1. **GUI Integration** - Integrate with Phase 3 GUI panels
2. **Cloud Sync** - Sync secrets across machines (encrypted)
3. **Team Management** - Shared tool profiles for teams
4. **Auto-Update** - Automatic tool updates with rollback
5. **Plugin System** - Extensible plugin architecture
6. **Docker Support** - Containerized environment setup

---

## Appendix A: Key Decisions

### Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-11-21 | Use `keyring` instead of DPAPI-only | Cross-platform support |
| 2025-11-21 | Merge configs into single `aim_config.json` | Reduce complexity |
| 2025-11-21 | Keep PowerShell adapters unchanged | Minimize risk |
| 2025-11-21 | Python-first for new modules | Consistency with pipeline |
| 2025-11-21 | Async tool installation | Performance |

### Open Questions

- [ ] Should we support multiple secret backends (Azure KeyVault, 1Password)?
- [ ] Should scanner auto-fix issues or only report?
- [ ] Should we preserve AI_MANGER plugin system or deprecate?
- [ ] Should health checks be configurable per-workstream?

---

## Appendix B: File Inventory

### New Files Created (Estimated: 35-40 files)

```
aim/
├── environment/          # 7 files
├── services/             # 3 files
├── cli/                  # 10 files
├── config/               # 3 files
└── tests/                # 15+ files

docs/
└── AIM_PLUS_INTEGRATION_PLAN.md (this file)

scripts/
├── migrate_to_aim_plus.py
└── validate_aim_config.py
```

### Modified Files (Estimated: 10 files)

```
aim/bridge.py
aim/__init__.py
core/engine/orchestrator.py
core/engine/tools.py
requirements.txt
pyproject.toml
README.md
docs/ARCHITECTURE.md
```

---

## Appendix C: Command Reference

### Quick Command Summary

```bash
# Setup
python -m aim setup --all                    # Bootstrap everything
python -m aim setup --secrets-only           # Just secrets vault

# Health
python -m aim health check                   # Run all checks
python -m aim health check --json            # JSON output

# Secrets
python -m aim secrets set KEY VALUE          # Store secret
python -m aim secrets get KEY                # Retrieve secret
python -m aim secrets list                   # List all keys
python -m aim secrets delete KEY             # Remove secret

# Tools
python -m aim tools list                     # Show installed tools
python -m aim tools install aider            # Install specific tool
python -m aim tools install --from-config    # Install from config
python -m aim tools update --all             # Update all tools

# Version Control
python -m aim version report                 # Show version drift
python -m aim version sync --dry-run         # Preview sync
python -m aim version sync --apply           # Apply sync

# Scanner
python -m aim scan duplicates                # Find duplicate files
python -m aim scan caches                    # Find misplaced caches
python -m aim scan tools                     # Find duplicate tools

# Config
python -m aim config validate                # Validate config
python -m aim config show                    # Display config
python -m aim config migrate                 # Migrate from old format
```

---

**Document Status**: Draft for Review  
**Next Steps**: Review with stakeholders → Approve → Begin Phase 1  
**Approval Required From**: Architecture team, AIM maintainers

---

*End of Integration Plan*
