# Navigation Guide

**New to this repo?** Start with [.ai-context.md](.ai-context.md) (5 min read).

---

## Quick Links

### For AI Tools (Start Here)
- **Context**: [.ai-context.md](.ai-context.md) - Repo overview in 30 seconds
- **Structure**: [CODEBASE_INDEX.yaml](CODEBASE_INDEX.yaml) - Module map (machine-readable)
- **Code Lookup**: [docs/IMPLEMENTATION_LOCATIONS.md](docs/IMPLEMENTATION_LOCATIONS.md) - Find any term
- **Edit Rules**: [ai_policies.yaml](ai_policies.yaml) - What you can/cannot edit

### For Humans
- **Start**: [README.md](README.md) - Main entry point
- **Quick Tasks**: [QUICK_START.md](QUICK_START.md) - Common workflows
- **Architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design
- **Contributing**: [AGENTS.md](AGENTS.md) - Coding guidelines

---

## By Intent

| I want to... | Go to... | Why? |
|--------------|----------|------|
| Understand system design | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Complete architecture overview |
| Run a workstream | [QUICK_START.md](QUICK_START.md) | Step-by-step execution guide |
| Find specific code | [docs/IMPLEMENTATION_LOCATIONS.md](docs/IMPLEMENTATION_LOCATIONS.md) | Term → file:line mapping |
| Add error detection | [error/README.md](error/README.md) | Error pipeline guide |
| Understand a module | [CODEBASE_INDEX.yaml](CODEBASE_INDEX.yaml) | Module purposes & dependencies |
| See all APIs | [API_INDEX.md](API_INDEX.md) | CLIs, Python APIs, configs |
| Trace execution flow | [EXECUTION_INDEX.md](EXECUTION_INDEX.md) | Execution paths, state machines |
| Check dependencies | [DEPENDENCY_INDEX.md](DEPENDENCY_INDEX.md) | Module dependency graph |
| Navigate directories | [DIRECTORY_GUIDE.md](DIRECTORY_GUIDE.md) | Complete directory tour |
| Find documentation | [docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md) | All docs indexed |

---

## By Role

### New Developer
1. [README.md](README.md) - What is this?
2. [.ai-context.md](.ai-context.md) - Quick orientation
3. [QUICK_START.md](QUICK_START.md) - Get running
4. [AGENTS.md](AGENTS.md) - Coding standards

### AI Tool
1. [.ai-context.md](.ai-context.md) - Context load
2. [CODEBASE_INDEX.yaml](CODEBASE_INDEX.yaml) - Structure
3. [ai_policies.yaml](ai_policies.yaml) - Edit rules
4. Module `.ai-module-manifest` files (when available)

### Contributor
1. [AGENTS.md](AGENTS.md) - Guidelines
2. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Design principles
3. [QUALITY_GATE.yaml](QUALITY_GATE.yaml) - Validation
4. [docs/CI_PATH_STANDARDS.md](docs/CI_PATH_STANDARDS.md) - Import rules

### Architect/Designer
1. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design
2. [CODEBASE_INDEX.yaml](CODEBASE_INDEX.yaml) - Module structure
3. [DEPENDENCY_INDEX.md](DEPENDENCY_INDEX.md) - Dependencies
4. [docs/adr/](docs/adr/) - Architecture decisions

---

## Focused Indexes

### Code Organization
- **[CODEBASE_INDEX.yaml](CODEBASE_INDEX.yaml)** - Module hierarchy, purposes, layers
- **[DIRECTORY_GUIDE.md](DIRECTORY_GUIDE.md)** - Directory structure walkthrough
- **[docs/FILE_ORGANIZATION_SYSTEM.md](docs/FILE_ORGANIZATION_SYSTEM.md)** - File organization spec

### APIs & Interfaces
- **[API_INDEX.md](API_INDEX.md)** - All command-line interfaces, Python APIs
- **[docs/IMPLEMENTATION_LOCATIONS.md](docs/IMPLEMENTATION_LOCATIONS.md)** - Code location finder
- **[ENTRY_POINTS.md](ENTRY_POINTS.md)** - Entry points (WS-004, coming soon)

### Runtime & Execution
- **[EXECUTION_INDEX.md](EXECUTION_INDEX.md)** - Execution flows, entry points, state machines
- **[DEPENDENCY_INDEX.md](DEPENDENCY_INDEX.md)** - Module dependencies, layer rules

### Documentation
- **[docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md)** - Complete doc catalog
- **[MASTER_NAVIGATION_INDEX.md](MASTER_NAVIGATION_INDEX.md)** - Comprehensive navigation (legacy)

---

## By Topic

### Understanding the System
| Topic | Document |
|-------|----------|
| Overall architecture | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| Module structure | [CODEBASE_INDEX.yaml](CODEBASE_INDEX.yaml) |
| Execution model | [EXECUTION_INDEX.md](EXECUTION_INDEX.md) |
| State management | [core/state/README.md](core/state/README.md) |
| Error detection | [error/README.md](error/README.md) |

### Working with Code
| Topic | Document |
|-------|----------|
| Coding standards | [AGENTS.md](AGENTS.md) |
| Import paths | [docs/CI_PATH_STANDARDS.md](docs/CI_PATH_STANDARDS.md) |
| Module boundaries | [DEPENDENCY_INDEX.md](DEPENDENCY_INDEX.md) |
| Testing strategy | [docs/guidelines/TESTING_STRATEGY.md](docs/guidelines/TESTING_STRATEGY.md) |

### Workstreams & Specs
| Topic | Document |
|-------|----------|
| Authoring workstreams | [docs/workstream_authoring_guide.md](docs/workstream_authoring_guide.md) |
| Spec management | [specifications/README.md](specifications/README.md) |
| UET framework | [UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/docs/](UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/docs/) |

### Tools & Integrations
| Topic | Document |
|-------|----------|
| AIM (AI environment) | [aim/README.md](aim/README.md) |
| Project management | [pm/README.md](pm/README.md) |
| Scripts & automation | [scripts/README.md](scripts/README.md) |

---

## Common Navigation Patterns

### "I need to modify X module"
1. Check [CODEBASE_INDEX.yaml](CODEBASE_INDEX.yaml) - Find module layer & dependencies
2. Read `<module>/README.md` - Understand module purpose
3. Check `<module>/.ai-module-manifest` - Entry points & patterns (if exists)
4. Review [ai_policies.yaml](ai_policies.yaml) - Ensure module is editable

### "I'm getting an import error"
1. Check [docs/CI_PATH_STANDARDS.md](docs/CI_PATH_STANDARDS.md) - Valid import paths
2. See [.ai-context.md](.ai-context.md) - Deprecated paths section
3. Run `python scripts/paths_index_cli.py gate` - Validate imports

### "Where is feature X implemented?"
1. Check [docs/IMPLEMENTATION_LOCATIONS.md](docs/IMPLEMENTATION_LOCATIONS.md) - Direct lookup
2. Search [API_INDEX.md](API_INDEX.md) - If it's a CLI/API
3. Search [EXECUTION_INDEX.md](EXECUTION_INDEX.md) - If it's an execution flow

### "I want to understand how Y works"
1. Check [EXECUTION_INDEX.md](EXECUTION_INDEX.md) - Execution flows
2. Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Architectural context
3. Trace code from entry point in [API_INDEX.md](API_INDEX.md)

---

## Navigation Quick Reference

```
Root Navigation Flow:

README.md ──────┬──→ QUICK_START.md (tasks)
                │
                ├──→ .ai-context.md (AI tools)
                │       │
                │       └──→ CODEBASE_INDEX.yaml (structure)
                │
                ├──→ docs/ARCHITECTURE.md (design)
                │
                └──→ AGENTS.md (contributing)

Finding Code:

docs/IMPLEMENTATION_LOCATIONS.md ──→ Exact file:line
API_INDEX.md ────────────────────→ CLIs & APIs  
EXECUTION_INDEX.md ──────────────→ Execution flows
CODEBASE_INDEX.yaml ─────────────→ Module structure

Understanding Modules:

CODEBASE_INDEX.yaml ──→ Module overview
<module>/README.md ───→ Module details
<module>/.ai-module-manifest ──→ AI-readable spec (new)
```

---

## File Organization

### Root Level (Navigate From Here)
- **README.md** - Main entry point
- **.ai-context.md** - AI orientation (NEW)
- **NAVIGATION.md** - This file
- **QUICK_START.md** - Task-based guide
- **AGENTS.md** - Contribution guidelines

### Navigation Indexes
- **CODEBASE_INDEX.yaml** - Module structure
- **API_INDEX.md** - All APIs
- **EXECUTION_INDEX.md** - Execution flows
- **DEPENDENCY_INDEX.md** - Dependencies
- **DIRECTORY_GUIDE.md** - Directory walkthrough

### Documentation
- **docs/** - System documentation (architecture, guides)
- **devdocs/** - Development artifacts (phase plans, reports)
- **Module READMEs** - Per-module documentation

### Code
- **core/** - State management, orchestration, planning
- **engine/** - Job execution (standalone)
- **error/** - Error detection pipeline
- **aim/** - AI environment manager
- **pm/** - Project management
- **specifications/** - Spec tools & management

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Recommended starting point |
| 📋 | Reference document |
| 🔧 | Tool/script |
| 🧪 | Testing/validation |
| 📊 | Metrics/analysis |
| 🗂️ | Index/catalog |
| ⚠️ | Important/critical |
| 📁 | Directory |

---

## Tips

### For Fast Navigation
1. **Bookmark this file** - Central navigation hub
2. **Use indexes** - API, EXECUTION, DEPENDENCY for targeted lookup
3. **Start with .ai-context.md** - Fastest orientation (AI tools)
4. **Check module READMEs** - Before editing any module

### For Deep Understanding
1. **Read ARCHITECTURE.md first** - System design principles
2. **Trace dependencies** - Use DEPENDENCY_INDEX.md
3. **Follow execution flows** - Use EXECUTION_INDEX.md
4. **Read ADRs** - Architecture decisions in docs/adr/

### For AI Tools
1. **Load .ai-context.md** - 30-second context
2. **Parse CODEBASE_INDEX.yaml** - Module structure
3. **Check ai_policies.yaml** - Edit constraints
4. **Read module manifests** - `.ai-module-manifest` files (when available)

---

## Recently Updated

**2025-11-23**:
- ✅ Created `.ai-context.md` - AI-optimized orientation
- ✅ Created `NAVIGATION.md` - This file
- 🚧 Module manifests (WS-002) - In progress

**See**: [.ai-context.md](.ai-context.md) for recent major changes

---

## Next Steps

1. **New to repo?** → [.ai-context.md](.ai-context.md) or [README.md](README.md)
2. **Want to code?** → [AGENTS.md](AGENTS.md) + [QUICK_START.md](QUICK_START.md)
3. **Need specific info?** → Use indexes (API, EXECUTION, DEPENDENCY)
4. **Lost?** → Start here (this file) and navigate by intent

---

**For Contributors**: Start with [AGENTS.md](AGENTS.md) for coding standards, then review module-specific documentation.

**Deprecated Navigation Docs**: `MASTER_NAVIGATION_INDEX.md` and `DIRECTORY_GUIDE.md` have been archived to [docs/archive/navigation/](docs/archive/navigation/). Use this file (NAVIGATION.md) instead.

**Last Updated**: 2025-11-23  
**Status**: Active - Updated as part of PH-AI-NAV-002
