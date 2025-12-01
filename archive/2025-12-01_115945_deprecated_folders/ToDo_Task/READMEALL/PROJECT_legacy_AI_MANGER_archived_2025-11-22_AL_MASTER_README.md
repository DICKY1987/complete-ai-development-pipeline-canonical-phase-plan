---
doc_id: DOC-GUIDE-PROJECT-LEGACY-AI-MANGER-ARCHIVED-2025-1586
---

# ToolStack - Configuration-Driven Development Environment Manager

## Overview

ToolStack is a comprehensive PowerShell-based system for managing development tools, configurations, and caches on Windows. It provides **separation of configuration from execution**, allowing you to define all your tools, paths, and settings in JSON files rather than hardcoded scripts.

## 📁 Directory Structure

```
toolstack/
├── config/
│   ├── toolstack.config.json       # Main configuration
│   ├── cache-patterns.json         # Cache directory patterns
│   ├── tools/
│   │   ├── python-tools.json       # Python/pipx tools
│   │   ├── node-tools.json         # Node.js/npm tools
│   │   └── system-tools.json       # System packages (winget)
│   └── schemas/
│       ├── toolstack-schema.json           # Main config schema
│       ├── tool-manifest-schema.json       # Tool manifest schema
│       └── cache-patterns-schema.json      # Cache patterns schema
├── scripts/
│   ├── Install-ToolStack.ps1       # Main orchestrator
│   ├── Install-Tools.ps1           # Tool installation engine
│   ├── Set-Environment.ps1         # Environment configuration
│   ├── Enforce-CachePolicy.ps1     # Cache centralization
│   └── Migrate-ToConfigDriven.ps1  # Migration helper
└── lib/
    ├── ToolStack.Helpers.psm1      # Shared functions
    └── ToolStack.Validation.psm1   # Schema validation
```

## 🚀 Quick Start

### 1. Install Everything

```powershell
cd toolstack/scripts
.\Install-ToolStack.ps1 -Tasks All
```

### 2. Dry Run (Preview Changes)

```powershell
.\Install-ToolStack.ps1 -Tasks All -DryRun
```

### 3. Specific Tasks

```powershell
# Only install tools
.\Install-ToolStack.ps1 -Tasks Install

# Only configure environment
.\Install-ToolStack.ps1 -Tasks Configure

# Only enforce cache policy
.\Install-ToolStack.ps1 -Tasks Enforce

# Verify installations
.\Install-ToolStack.ps1 -Tasks Verify
```

## 📝 Configuration

### Main Config: `config/toolstack.config.json`

Key sections:

```json
{
  "paths": {
    "root": "C:\\Tools",              // Base directory
    "projectRoots": ["C:\\Projects"]  // Projects to monitor
  },
  "features": {
    "generateWrappers": true,         // Create wrapper scripts
    "enableCacheEnforcement": true,   // Centralize caches
    "dryRun": false                   // Test mode
  }
}
```

### Adding Tools

Edit the appropriate manifest in `config/tools/`:

**Python tool (pipx):**
```json
{
  "name": "my-tool",
  "package": "my-package",
  "description": "Description",
  "wrapper": {
    "enabled": true,
    "envVars": ["MY_CACHE_DIR"]
  }
}
```

**Node.js tool (npm):**
```json
{
  "name": "my-cli",
  "package": "@scope/my-cli",
  "description": "Description"
}
```

### Adding Cache Patterns

Edit `config/cache-patterns.json`:

```json
{
  "patterns": [
    {
      "name": ".my-cache",
      "type": "directory",
      "recursive": true,
      "description": "My tool cache"
    }
  ]
}
```

## 🔄 Migrating from Old Scripts

If you have existing hardcoded scripts:

```powershell
cd toolstack/scripts
.\Migrate-ToConfigDriven.ps1 `
    -OldScriptsPath "C:\OldScripts" `
    -OutputPath "..\config" `
    -Force
```

This will:
- Extract tool lists from old scripts
- Generate JSON configuration files
- Preserve your old scripts (unchanged)

## 🎯 Key Features

### 1. Centralized Tool Installation
- **System packages** (winget): Git, Python, Node.js
- **Python tools** (pipx): ruff, black, mypy, pytest
- **Node.js tools** (npm): eslint, prettier, Claude Code, Gemini CLI

### 2. Environment Configuration
- XDG Base Directory compliance
- Tool-specific cache paths
- Automatic PATH management
- Wrapper script generation

### 3. Cache Enforcement
- Detects cache directories in projects
- Creates junctions/symlinks to central location
- Optional real-time watching
- Safe quarantine of existing caches

### 4. Wrapper Scripts
Auto-generated `.cmd` wrappers that:
- Inject environment variables
- Add default arguments
- Maintain centralized configs

## 📚 Documentation

### Variable Expansion

Configs support these variable formats:

- `${paths.root}` - Reference other paths
- `${env:USERNAME}` - Environment variables  
- `${installManagers.pipx.bin}` - Package manager paths

### JSON Schema Validation

All configs have schemas for:
- Auto-completion in VS Code
- Validation before execution
- Documentation of valid options

To enable in VS Code, install the "JSON Schema" extension.

### Real-Time Cache Watching

Monitor projects and auto-centralize new caches:

```powershell
.\Enforce-CachePolicy.ps1 -Config $config -Watch
```

Press Ctrl+C to stop. Keep window open while watching.

## 🛠️ Customization

### Custom Tool Root

```powershell
# Edit config/toolstack.config.json
{
  "paths": {
    "root": "D:\\DevTools"  // Change from C:\\Tools
  }
}
```

### Custom Project Roots

```json
{
  "paths": {
    "projectRoots": [
      "C:\\Work",
      "D:\\Projects",
      "E:\\OpenSource"
    ]
  }
}
```

### Disable Features

```json
{
  "features": {
    "generateWrappers": false,        // No wrapper scripts
    "enableCacheEnforcement": false,  // No cache centralization
    "enableWatcher": false            // No real-time monitoring
  }
}
```

## 🔍 Troubleshooting

### Symlinks Require Admin/Developer Mode

**Solution 1:** Enable Developer Mode (Windows Settings → Update & Security → For Developers)

**Solution 2:** Run as Administrator (script will use junctions as fallback)

### Tools Not Found After Install

**Solution:** Open a NEW terminal (environment changes require new session)

### PATH Not Updated

## Optional Components

The repository includes optional extras to extend ToolStack:

- config/claude: JSON templates for editor/agent integrations (e.g., code-runner, jupyter, GitHub/MCP). Copy and adapt as needed.
- plugins/MCP: Plugin module and manifest for MCP-based integrations. See plugin-manifest-schema.json for validation.
- scripts/extra: Convenience installers and orchestration helpers (Install-DevTools.ps1, Install-CliStack.ps1, etc.). Use when you want a one-shot bootstrap.
- scripts/subsystem: Self-contained install subsystem (config, scripts, validators) for advanced workflows or packaging.
- logs/ARCHIVE_REVIEW and ARCHIVE_REVIEW: Archived logs and distribution snapshots retained for diff/review; safe to delete once reviewed.

**Solution:** Check that scripts completed successfully, then restart terminal

### Validation Errors

```powershell
# Validate config manually
Import-Module .\lib\ToolStack.Validation.psm1
Test-ToolStackConfig -ConfigPath ".\config\toolstack.config.json"
```

## 📦 What Gets Installed

### System Tools (via winget)
- Git
- Python 3.12
- Node.js
- GitHub CLI
- PowerShell 7+

### Python Tools (via pipx)
- aider-chat, ruff, black, mypy, pytest
- pyright, pre-commit, uv, nox
- isort, pylint, invoke, langgraph-cli

### Node.js Tools (via npm)
- eslint, prettier
- @anthropic-ai/claude-code
- @google/generative-ai-cli
- github-copilot-cli
- @specifyapp/cli, @google/jules

## 🔐 Security

- Scripts are unsigned by default
- Set execution policy: `Set-ExecutionPolicy -Scope Process Bypass`
- Review configs before running
- DryRun mode tests without changes

## 📄 License

This is a utility project. Modify and use as needed.

## 🤝 Contributing

To add tools:
1. Edit appropriate JSON in `config/tools/`
2. Test with `-DryRun`
3. Run full installation

## 💡 Tips

- Always use `-DryRun` first to preview changes
- Back up important data before cache enforcement
- Use schemas for auto-completion in editors
- Check quarantine folder if caches go missing
- Keep old scripts as backup during migration

## 🆘 Support

For issues:
1. Check this README
2. Review config files for typos
3. Test with `-DryRun` to identify issues
4. Check Windows Event Viewer for errors

---

**Happy Coding! 🎉**
