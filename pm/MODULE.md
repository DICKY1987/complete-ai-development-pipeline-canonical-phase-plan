# PM Module

> **Module ID**: `pm`  
> **Purpose**: Project management and CCPM integrations  
> **Layer**: API  
> **Last Updated**: 2025-11-22  
> **Status**: Production

---

## Overview

The `pm/` (Project Management) module provides integration with project management tools and Critical Chain Project Management (CCPM) methodologies.

**Key Features**:
- PM CLI commands
- Local planning artifacts
- CCPM optimization tools
- Task scheduling and buffer management

---

## Directory Structure

```
pm/
├── commands/          # PM CLI commands
│   └── *.py           # Command implementations
│
├── workspace/         # Local planning artifacts (gitignored)
│   └── *.json         # Workspace data files
│
├── context/           # CCPM context management
│   └── README.md      # Context documentation
│
└── hooks/             # Integration hooks
    └── README.md      # Hook documentation
```

---

## Key Components

### PM Commands (`commands/`)

Command-line interface for project management operations.

**Import Pattern**:
```python
from pm.commands import run_pm_command
```

### Workspace (`workspace/`)

Local planning artifacts and workspace data.

**Note**: This directory is gitignored - workspace files are local to each developer.

---

## Dependencies

**Module Dependencies** (from CODEBASE_INDEX.yaml):
- None (top-level integration module)

**External Dependencies**:
- CCPM tools (installed separately)

---

## Usage Examples

### PM Command Execution

```python
from pm.commands import run_pm_command

# Execute PM command
result = run_pm_command("status")
```

---

## AI Context Priority

**MEDIUM** - Project coordination

**AI Agent Guidance**:
- ✅ Safe to modify: `commands/`
- ⚠️ Caution: `workspace/` (local artifacts, gitignored)
- 📚 Reference only: `context/`, `hooks/`

**Edit Policy**: `safe`

---

## Documentation

- Module overview: This file
- CCPM optimization: `docs/phase-09-ccpm-optimization-checklist.md`
- Context management: `pm/context/README.md`
- Hook documentation: `pm/hooks/README.md`

---

## See Also

- [CODEBASE_INDEX.yaml](../CODEBASE_INDEX.yaml) - Module dependencies
- [DIRECTORY_GUIDE.md](../DIRECTORY_GUIDE.md) - Repository structure
- [ccpm/](../ccpm/) - CCPM implementation
