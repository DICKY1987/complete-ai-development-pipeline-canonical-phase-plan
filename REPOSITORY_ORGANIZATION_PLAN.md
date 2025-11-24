# Repository Organization Plan: Separation of Concerns
**Date**: 2025-11-23  
**Current State**: Mixed concerns, 49 root files, duplicated directories  
**Goal**: Clean separation aligned with domain boundaries

---

## Current Problems

### Problem 1: Root Directory Pollution (49 files)
**Issue**: 26+ markdown files at root level mixing different concerns
- Navigation docs (NAVIGATION.md, ENTRY_POINTS.md)
- Glossaries/indexes (GLOSSARY.md, API_INDEX.md, EXECUTION_INDEX.md)
- Cleanup reports (CLEANUP_*.md)
- Agent configs (AGENTS.md, CLAUDE.md)
- Planning docs (opinionated planning framework.md)
- Random files (ecision Elimination Through Pattern Recognition6.md)

**Impact**: Hard to find files, unclear ownership, no separation

---

### Problem 2: Documentation Fragmentation (4 locations)
**Current**:
- `docs/` - 150 files (general documentation)
- `devdocs/` - 177 files (developer documentation)
- `meta/` - 50 files (meta documentation?)
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/docs/` - 15 files

**Issue**: 
- No clear distinction between user docs vs developer docs vs reference
- Duplicated concerns across directories
- UET framework isolated from main docs

**Impact**: Documentation scattered, hard to maintain, unclear hierarchy

---

### Problem 3: Scripts/Tools Duplication (3 locations)
**Current**:
- `scripts/` - 92 files (automation, validation, generation)
- `tools/` - 15 files (utilities?)
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/` - 24 files

**Issue**:
- Unclear distinction between scripts vs tools
- Pattern extraction tools isolated in UET
- No clear categorization (user-facing vs internal)

**Impact**: Hard to find the right script, duplication risk

---

### Problem 4: Config Files Scattered
**Current**:
- Root: `.env`, `.env.example`, `invoke.yaml.example`, `pyproject.toml`, `pytest.ini`
- `.config/` directory exists but underutilized
- `config/` directory for application config
- `ai_policies.yaml`, `QUALITY_GATE.yaml`, `PROJECT_PROFILE.yaml` at root

**Issue**: No clear distinction between:
- Development environment config (.env, pyproject.toml)
- Application runtime config (config/)
- Project metadata (PROJECT_PROFILE.yaml)
- AI/tooling config (ai_policies.yaml)

---

### Problem 5: Unclear Module Boundaries
**Current structure**:
```
core/          (orchestration, state, planning)
engine/        (job execution - overlaps with core.engine?)
error/         (error detection)
aim/           (AIM environment)
pm/            (project management)
specifications/ (specs and tools)
```

**Issue**:
- `engine/` vs `core/engine/` - which is canonical?
- Specs mixed with tooling in `specifications/`
- No clear "adapters" or "integrations" layer

---

## Proposed Structure (Separation of Concerns)

### Principle: "One Concern, One Place"

```
📦 Repository Root
│
├── 🏗️ SOURCE CODE (Production)
│   ├── src/                          # All production code
│   │   ├── core/                     # Core domain logic
│   │   │   ├── state/                # Database, CRUD
│   │   │   ├── engine/               # Orchestration
│   │   │   └── planning/             # Workstream generation
│   │   ├── domain/                   # Domain modules
│   │   │   ├── error/                # Error detection
│   │   │   ├── aim/                  # AIM environment
│   │   │   └── pm/                   # Project management
│   │   ├── adapters/                 # External integrations
│   │   │   ├── aider/                # Aider adapter
│   │   │   └── specifications/       # Spec bridge
│   │   ├── cli/                      # CLI entry points
│   │   │   └── commands/             # Command implementations
│   │   └── gui/                      # GUI (if needed)
│
├── 📚 DOCUMENTATION (Reference)
│   ├── docs/                         # Main documentation
│   │   ├── guides/                   # User guides
│   │   │   ├── quick-start.md
│   │   │   ├── navigation.md
│   │   │   └── glossary.md
│   │   ├── reference/                # API/technical reference
│   │   │   ├── api-index.md
│   │   │   ├── execution-index.md
│   │   │   └── dependency-index.md
│   │   ├── architecture/             # Architecture docs
│   │   │   ├── codebase-index.yaml
│   │   │   ├── layers.md
│   │   │   └── modules.md
│   │   └── adr/                      # Architecture Decision Records
│   │       └── (existing ADRs)
│   │
│   └── developer/                    # Developer-specific docs
│       ├── contributing.md
│       ├── development-setup.md
│       ├── phases/                   # Phase documentation
│       ├── planning/                 # Planning docs
│       └── cleanup/                  # Cleanup reports (archive)
│
├── 🧪 SPECIFICATIONS (Contracts)
│   ├── specs/                        # Specification files only
│   │   ├── workstream/
│   │   ├── task/
│   │   ├── phase/
│   │   └── uet/                      # UET specs
│   └── schema/                       # JSON schemas
│       └── (existing schemas)
│
├── 🔧 TOOLING (Automation)
│   ├── tools/                        # User-facing tools
│   │   ├── pattern-extraction/       # From UET framework
│   │   ├── validation/               # Validation tools
│   │   └── generation/               # Generation tools
│   │
│   └── scripts/                      # Developer scripts
│       ├── dev/                      # Development helpers
│       ├── ci/                       # CI/CD scripts
│       └── maintenance/              # Maintenance scripts
│
├── ⚙️ CONFIGURATION (Settings)
│   ├── config/                       # Application runtime config
│   │   ├── profiles/
│   │   └── environments/
│   │
│   └── .config/                      # Development environment
│       ├── .env.example
│       ├── pyproject.toml
│       ├── pytest.ini
│       └── ai-policies.yaml
│
├── 🧩 TEMPLATES (Reusable)
│   ├── templates/                    # Execution templates
│   │   ├── patterns/                 # Pattern templates
│   │   │   ├── parallel/
│   │   │   ├── sequential/
│   │   │   ├── template/
│   │   │   └── meta/
│   │   ├── execution/                # Execution patterns
│   │   └── verification/             # Verification templates
│   │
│   └── examples/                     # Example workstreams/tasks
│       └── (existing examples)
│
├── 🧪 TESTING (Validation)
│   └── tests/                        # All tests
│       ├── unit/
│       ├── integration/
│       └── e2e/
│
├── 📦 INFRASTRUCTURE (Supporting)
│   ├── infra/                        # Infrastructure code
│   │   └── state/                    # State management
│   │
│   ├── .state/                       # Runtime state (gitignored)
│   ├── .pytest_cache/                # Cache (gitignored)
│   └── logs/                         # Logs (gitignored)
│
├── 🗄️ ARCHIVE (Historical)
│   ├── legacy/                       # Deprecated code
│   └── archive/                      # Old docs/reports
│       ├── cleanup-reports/
│       └── migration-logs/
│
└── 📋 ROOT (Essential Only)
    ├── README.md                     # Project overview
    ├── AGENTS.md                     # Agent guidelines
    ├── QUICK_START.md                # Getting started
    ├── CHANGELOG.md                  # Version history
    ├── LICENSE                       # License
    └── .gitignore                    # Git config
```

---

## Separation of Concerns Principles

### 1. Source Code (`src/`)
**Purpose**: Production code only  
**Concerns**: Core logic, domain modules, adapters, CLI, GUI  
**Rules**:
- All importable Python code lives here
- Organized by layer (core → domain → adapters → ui)
- No documentation, tests, or scripts mixed in

---

### 2. Documentation (`docs/` + `developer/`)
**Purpose**: Reference and guides  
**Concerns**: User docs vs developer docs vs architecture  
**Rules**:
- `docs/` = User-facing (guides, API reference, architecture)
- `developer/` = Developer-specific (contributing, setup, phases)
- All indexes/glossaries in `docs/reference/`
- No scattered markdown files at root

---

### 3. Specifications (`specs/`)
**Purpose**: Contracts and schemas  
**Concerns**: Workstream specs, task specs, phase specs, UET specs  
**Rules**:
- Only declarative specification files
- No tooling or implementation
- JSON schemas in `schema/` subdirectory

---

### 4. Tooling (`tools/` + `scripts/`)
**Purpose**: Automation and utilities  
**Concerns**: User-facing tools vs developer scripts  
**Rules**:
- `tools/` = User-facing utilities (pattern extraction, validation)
- `scripts/` = Developer automation (CI, maintenance, dev helpers)
- UET pattern extraction moves to `tools/pattern-extraction/`

---

### 5. Configuration (`config/` + `.config/`)
**Purpose**: Settings and environment  
**Concerns**: Runtime config vs dev environment  
**Rules**:
- `config/` = Application runtime (profiles, tool configs)
- `.config/` = Development environment (.env, pyproject.toml, pytest.ini)
- AI policies and quality gates in `.config/`

---

### 6. Templates (`templates/`)
**Purpose**: Reusable execution patterns  
**Concerns**: Pattern templates vs examples  
**Rules**:
- All UET templates consolidated here
- Organized by category (parallel, sequential, meta)
- Examples separate from production templates

---

## Migration Plan (3 Phases)

### Phase 1: Quick Wins (Root Cleanup)
**Time**: 30 minutes  
**Impact**: Immediate clarity

**Actions**:
1. Move all markdown files from root to appropriate locations:
   ```
   GLOSSARY.md → docs/reference/glossary.md
   API_INDEX.md → docs/reference/api-index.md
   EXECUTION_INDEX.md → docs/reference/execution-index.md
   NAVIGATION.md → docs/guides/navigation.md
   AGENTS.md → Keep at root (essential)
   CLAUDE.md → .config/claude.md
   CLEANUP_*.md → archive/cleanup-reports/
   ```

2. Move config files to `.config/`:
   ```
   ai_policies.yaml → .config/ai-policies.yaml
   QUALITY_GATE.yaml → .config/quality-gate.yaml
   PROJECT_PROFILE.yaml → .config/project-profile.yaml
   pytest.ini → .config/pytest.ini
   ```

3. Create directory structure:
   ```bash
   mkdir -p docs/{guides,reference,architecture}
   mkdir -p developer/{phases,planning,cleanup}
   mkdir -p archive/cleanup-reports
   mkdir -p .config
   ```

**Result**: Root has <10 essential files

---

### Phase 2: Documentation Consolidation
**Time**: 1 hour  
**Impact**: Clear doc hierarchy

**Actions**:
1. Merge `devdocs/` into `developer/`:
   ```
   devdocs/phases/ → developer/phases/
   devdocs/planning/ → developer/planning/
   devdocs/brainstorms/ → archive/brainstorms/
   ```

2. Merge `meta/` into `docs/architecture/`:
   ```
   meta/PHASE_DEV_DOCS/ → developer/phases/
   meta/workstreams/ → archive/meta-workstreams/
   ```

3. Move UET docs to main docs:
   ```
   UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/docs/ → docs/uet/
   ```

4. Archive old cleanup/migration docs:
   ```
   CLEANUP_*.md → archive/cleanup-reports/
   MIGRATION_*.md → archive/migration-logs/
   ```

**Result**: 
- `docs/` = User-facing reference
- `developer/` = Developer guides
- `archive/` = Historical context

---

### Phase 3: Code & Tooling Reorganization
**Time**: 2 hours  
**Impact**: Clean module boundaries

**Actions**:
1. Consolidate scripts:
   ```
   tools/ → scripts/dev/
   UET scripts → tools/pattern-extraction/
   scripts/validation → tools/validation/
   scripts/generate_* → tools/generation/
   scripts/paths_* → scripts/dev/
   ```

2. Resolve `engine/` vs `core/engine/`:
   ```
   # Determine canonical location
   # Option A: Deprecate root engine/, use core/engine/
   # Option B: Move core/engine/ to engine/, update imports
   ```

3. Create `src/adapters/`:
   ```
   aider/ → src/adapters/aider/
   specifications/bridge/ → src/adapters/specifications/
   ```

4. Update `CODEBASE_INDEX.yaml` to reflect new structure

**Result**:
- Clear "one tool, one place" organization
- Resolved engine/ ambiguity
- Proper adapter layer

---

## Benefits of This Structure

### For Developers
✅ **Clear ownership**: Each directory has one purpose  
✅ **Easy navigation**: Predictable locations  
✅ **Less cognitive load**: No hunting for files  
✅ **Better onboarding**: New devs understand structure immediately

### For AI Agents
✅ **Clearer context**: Separation guides tool selection  
✅ **Better scoping**: file_scope can target specific concerns  
✅ **Faster searches**: Know where to look for what  
✅ **Reduced errors**: Less chance of editing wrong file

### For Maintenance
✅ **Easier cleanup**: Archive old stuff without fear  
✅ **Clear deprecation**: `legacy/` and `archive/` are obvious  
✅ **Better git history**: Changes grouped by concern  
✅ **Simpler CI/CD**: Target specific directories

---

## Implementation Commands

### Phase 1: Quick Wins (Run Now)
```powershell
# Create new structure
New-Item -ItemType Directory -Path "docs/guides", "docs/reference", "docs/architecture" -Force
New-Item -ItemType Directory -Path "developer/phases", "developer/planning", "developer/cleanup" -Force
New-Item -ItemType Directory -Path "archive/cleanup-reports", "archive/migration-logs" -Force
New-Item -ItemType Directory -Path ".config" -Force

# Move markdown files
Move-Item "GLOSSARY.md" "docs/reference/glossary.md"
Move-Item "API_INDEX.md" "docs/reference/api-index.md"
Move-Item "EXECUTION_INDEX.md" "docs/reference/execution-index.md"
Move-Item "DEPENDENCY_INDEX.md" "docs/reference/dependency-index.md"
Move-Item "NAVIGATION.md" "docs/guides/navigation.md"
Move-Item "ENTRY_POINTS.md" "docs/guides/entry-points.md"

# Move config files
Move-Item "ai_policies.yaml" ".config/ai-policies.yaml"
Move-Item "QUALITY_GATE.yaml" ".config/quality-gate.yaml"
Move-Item "PROJECT_PROFILE.yaml" ".config/project-profile.yaml"
Move-Item "pytest.ini" ".config/pytest.ini"

# Archive cleanup reports
Move-Item "CLEANUP_*.md" "archive/cleanup-reports/"
Move-Item "MIGRATION_*.md" "archive/migration-logs/"

# Commit
git add -A
git commit -m "refactor: Phase 1 - Root cleanup and separation of concerns"
```

### Phase 2: Documentation Consolidation (Next)
```powershell
# Merge devdocs
Move-Item "devdocs/phases/*" "developer/phases/"
Move-Item "devdocs/planning/*" "developer/planning/"
Move-Item "devdocs/brainstorms/*" "archive/brainstorms/"

# Merge meta
Move-Item "meta/PHASE_DEV_DOCS/*" "developer/phases/"

# Move UET docs
Move-Item "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/docs/*" "docs/uet/"

# Commit
git add -A
git commit -m "refactor: Phase 2 - Documentation consolidation"
```

### Phase 3: Code Reorganization (Final)
```powershell
# Consolidate tools
New-Item -ItemType Directory -Path "tools/pattern-extraction", "tools/validation", "tools/generation" -Force
Move-Item "UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/pattern_extraction/*" "tools/pattern-extraction/"

# Create adapters
New-Item -ItemType Directory -Path "src/adapters/aider", "src/adapters/specifications" -Force

# Update imports (requires code changes)
# ... (detailed in separate migration guide)

# Commit
git add -A
git commit -m "refactor: Phase 3 - Code and tooling reorganization"
```

---

## Success Criteria

### Metrics
- Root directory: **<10 essential files** (down from 49)
- Documentation locations: **2** (docs + developer, down from 4)
- Scripts locations: **2** (tools + scripts, down from 3)
- Clear module boundaries: **100% of imports follow layer rules**

### Validation
```bash
# Root should have <10 files
ls -1 | wc -l  # Should be <10

# No scattered markdown
find . -maxdepth 1 -name "*.md" | wc -l  # Should be <=5

# All docs in 2 places
find docs developer -name "*.md" | wc -l  # Should be >300

# No duplicate directories
ls -d docs devdocs meta 2>/dev/null | wc -l  # Should be 1 (docs only)
```

---

## Related Documents

- [CODEBASE_INDEX.yaml](../CODEBASE_INDEX.yaml) - Module structure (needs update)
- [DIRECTORY_GUIDE.md](../DIRECTORY_GUIDE.md) - Current guide (needs rewrite)
- [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) - Architecture overview

---

_Generated: 2025-11-23_  
_Pattern: separation_of_concerns_v1_  
_Next Step: Execute Phase 1 cleanup_
