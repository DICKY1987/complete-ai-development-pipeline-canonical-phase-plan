# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AIM (AI Tools Registry) is a coordination system for managing multiple AI coding tools (Jules, Aider, Claude CLI). It provides a centralized registry, capability routing, PowerShell adapters for tool integration, and audit logging.

## Architecture

**Registry System**: The core is `AIM_registry.json` which defines:
- Tool metadata (detection commands, version commands, config paths)
- Capability mappings (e.g., "code_generation")
- References to adapter scripts

**Adapter Pattern**: Each tool has a PowerShell adapter script in `AIM_adapters/`:
- Accepts JSON input via stdin with `{capability, payload}` structure
- Returns JSON output with `{success, message, content}` structure
- Handles capability routing (e.g., "version", "code_generation")
- Uses `Invoke-External` helper function for subprocess execution

**Coordination Rules**: `AIM_cross-tool/AIM_coordination-rules.json` defines capability routing:
- Primary tool selection per capability
- Fallback chains
- Load balancing configuration

**Audit System**: `AIM_audit/YYYY-MM-DD/*.json` logs all capability invocations with:
- Timestamp, actor, capability, tool, input payload, and result

## Development Commands

**Run an adapter manually**:
```powershell
# Echo JSON to adapter stdin
'{"capability":"version","payload":{}}' | pwsh -File AIM_adapters/AIM_aider.ps1

# Get adapter help
pwsh -File AIM_adapters/AIM_aider.ps1 -?
```

**Validate all JSON files**:
```powershell
pwsh -Command "Get-ChildItem -Recurse *.json | % { Get-Content $_ | ConvertFrom-Json | Out-Null }"
```

**Lint and format PowerShell**:
```powershell
pwsh -Command "Invoke-ScriptAnalyzer .; Invoke-Formatter -Path AIM_adapters"
```

**Run tests** (when Tests/ directory exists):
```powershell
pwsh -Command "Invoke-Pester"
```

## Coding Standards

**PowerShell**:
- Requires PowerShell 7+
- Use 2-space indentation, no tabs
- Set `Set-StrictMode -Version Latest` and `$ErrorActionPreference = 'Stop'`
- Functions: PascalCase; parameters: PascalCase with descriptive names
- All scripts must handle JSON input validation gracefully

**Naming Convention**:
- All files prefixed with `AIM_` (e.g., `AIM_jules.ps1`, `AIM_registry.json`)
- Adapter scripts: `AIM_<toolname>.ps1`

**JSON Structure**:
- Always use `-Depth 10` with `ConvertTo-Json` to avoid truncation
- Validate incoming JSON with try-catch blocks

## Adding a New Tool

1. Add tool entry to `AIM_registry.json` with:
   - `name`, `detectCommands`, `versionCommand`, `configPaths`, `logPaths`
   - `capabilities` array
   - `adapterScript` path

2. Create adapter script `AIM_adapters/AIM_<tool>.ps1`:
   - Read JSON from stdin
   - Implement capability handlers in switch statement
   - Use `Invoke-External` for subprocess calls
   - Return structured JSON responses

3. Update `AIM_cross-tool/AIM_coordination-rules.json` to route capabilities

4. Add Pester smoke test in `Tests/` directory (when created)

## Commit Guidelines

- Imperative mood with scope prefix: `adapters: add jules adapter`, `registry: update tool IDs`
- Link issues with `Fixes #123` when applicable
- PRs require: summary, affected paths, test evidence, rollback notes
