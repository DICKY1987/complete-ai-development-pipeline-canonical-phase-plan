---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-FILE_ORGANIZATION_SYSTEM-085
---

# File Organization System – Development vs System Files

> **Purpose**: Define a clear separation strategy between development artifacts and production system files to prevent mixing and facilitate clean handover.
> **Created**: 2025-11-22
> **Status**: Active Standard

---

## Executive Summary

This document establishes a structured file organization system that separates **System Development Files** (planning, session logs, execution summaries) from **System Files** (production code, runtime configuration, deliverables). The system prevents accidental mixing through naming conventions, directory boundaries, and `.gitignore` rules.

### Key Principles

1. **Clear Boundary** - Development artifacts in `devdocs/`, system files everywhere else
2. **Naming Convention** - Development files use ALL_CAPS with specific suffixes
3. **Runtime Isolation** - Generated artifacts use dot-prefixes (`.worktrees/`, `.runs/`)
4. **Archive Strategy** - Completed development work moves to `devdocs/archive/`

---

## Directory Structure

### Proposed Root-Level Organization

```
pipeline-root/
│
├── 📦 SYSTEM FILES (Production Codebase)
│   ├── core/                    # Core pipeline implementation
│   ├── engine/                  # Job execution engine
│   ├── error/                   # Error detection system
│   ├── aim/                     # AIM+ environment manager
│   ├── pm/                      # Project management
│   ├── specifications/          # Spec management system
│   ├── aider/                   # Aider integration
│   ├── gui/                     # GUI components
│   ├── scripts/                 # Automation scripts
│   ├── tests/                   # Test suite
│   ├── schema/                  # JSON/YAML schemas
│   ├── config/                  # Runtime configuration
│   ├── tools/                   # Internal utilities
│   ├── workstreams/             # Example workstreams
│   ├── infra/                   # CI/CD configuration
│   ├── examples/                # Example projects
│   └── legacy/                  # Archived old code
│
├── 📚 SYSTEM DOCUMENTATION (User-Facing Docs)
│   ├── docs/
│   │   ├── ARCHITECTURE.md      # System architecture
│   │   ├── CONFIGURATION_GUIDE.md
│   │   ├── COORDINATION_GUIDE.md
│   │   ├── API_REFERENCE.md
│   │   └── reference/           # API docs, guides
│   ├── README.md                # Main entry point
│   ├── AGENTS.md                # Developer guidelines
│   ├── DIRECTORY_GUIDE.md       # Navigation guide
│   └── QUICK_START.md           # Getting started
│
├── 🔧 DEVELOPMENT ARTIFACTS (Not Part of Deliverables)
│   └── devdocs/
│       ├── phases/              # Phase execution records
│       │   ├── phase-a/
│       │   ├── phase-b/
│       │   └── ...
│       ├── sessions/            # Session logs & reports
│       │   ├── 2025-11-20_MEGA_SESSION.md
│       │   └── 2025-11-22_ERROR_PIPELINE.md
│       ├── planning/            # Planning documents
│       │   ├── PHASE_ROADMAP.md
│       │   ├── MILESTONE_TRACKER.md
│       │   └── proposed/
│       ├── execution/           # Execution summaries
│       │   ├── PHASE_I_EXECUTION_SUMMARY.md
│       │   └── WORKSTREAM_G2_PROGRESS.md
│       ├── analysis/            # Code analysis reports
│       │   ├── DUPLICATE_ANALYSIS.md
│       │   └── METRICS_SUMMARY_*.md
│       ├── handoffs/            # Handoff documents
│       │   └── HANDOFF_PROMPT_2025-11-20.md
│       ├── archive/             # Completed development work
│       │   ├── 2025-11/
│       │   └── phase-h-legacy/
│       └── meta/                # Process documentation
│           ├── AGENTIC_DEV_PROCESS.md
│           └── TERMINAL_SESSION_GUIDE.md
│
└── 🗃️ RUNTIME (Generated, Git-Ignored)
    ├── .worktrees/              # Per-workstream folders
    ├── .runs/                   # Execution run records
    ├── .tasks/                  # Task queue storage
    ├── .ledger/                 # Execution ledger
    ├── logs/                    # Application logs
    ├── __pycache__/             # Python cache
    └── .pytest_cache/           # Test cache
```

---

## File Categorization

### Category 1: System Files (Production)

**Definition**: Files that are part of the actual system deliverables or production codebase.

**Location**: Root-level directories (`core/`, `engine/`, `error/`, `scripts/`, `tests/`, etc.)

**Naming Convention**:
- Python: `snake_case.py` (e.g., `orchestrator.py`, `error_engine.py`)
- Config: `kebab-case.json` or `.yaml` (e.g., `adapter-profiles.json`)
- Scripts: `snake_case.ps1` or `.sh` (e.g., `bootstrap.ps1`, `run_tests.sh`)
- Tests: `test_*.py` (e.g., `test_orchestrator.py`)

**Examples**:
```
✅ core/state/db.py
✅ engine/orchestrator.py
✅ error/plugins/python_ruff/plugin.py
✅ scripts/validate_workstreams.py
✅ config/adapter-profiles.json
✅ tests/pipeline/test_orchestrator.py
```

**Git Treatment**: Committed, versioned, part of releases

---

### Category 2: System Documentation (User-Facing)

**Definition**: Documentation that describes the system for end users, developers, and AI tools.

**Location**: `docs/` and root-level markdown files

**Naming Convention**:
- ALL_CAPS for major documents (e.g., `ARCHITECTURE.md`, `README.md`)
- kebab-case for specific guides (e.g., `configuration-guide.md`)
- Sentence case for headings

**Examples**:
```
✅ README.md
✅ AGENTS.md
✅ DIRECTORY_GUIDE.md
✅ docs/ARCHITECTURE.md
✅ docs/CONFIGURATION_GUIDE.md
✅ docs/reference/api-overview.md
```

**Git Treatment**: Committed, versioned, part of releases

---

### Category 3: Development Artifacts (Process Records)

**Definition**: Documents created during development to track progress, plan work, or record sessions. Not part of the final deliverable.

**Location**: `devdocs/` (centralized development documentation root)

**Naming Convention**:
- Phase plans: `PHASE_<ID>_<TYPE>.md` (e.g., `PHASE_I_PLAN.md`, `PHASE_G_COMPLETE.md`)
- Session logs: `SESSION_<DATE>_<DESCRIPTION>.md` (e.g., `SESSION_2025-11-22_ERROR_PIPELINE.md`)
- Execution summaries: `<CONTEXT>_EXECUTION_SUMMARY.md` (e.g., `PHASE_I_EXECUTION_SUMMARY.md`)
- Progress reports: `<CONTEXT>_PROGRESS.md` or `_PROGRESS_REPORT.md`
- Completion reports: `<CONTEXT>_COMPLETE.md` or `_COMPLETION_REPORT.md`
- Handoffs: `HANDOFF_<DATE>_<CONTEXT>.md`
- Analysis: `<TYPE>_ANALYSIS.md` or `METRICS_SUMMARY_<DATE>.md`

**Examples**:
```
✅ devdocs/phases/phase-i/PHASE_I_PLAN.md
✅ devdocs/phases/phase-i/PHASE_I_EXECUTION_SUMMARY.md
✅ devdocs/phases/phase-i/PHASE_I_COMPLETE.md
✅ devdocs/sessions/SESSION_2025-11-20_MEGA_SESSION.md
✅ devdocs/planning/PHASE_ROADMAP.md
✅ devdocs/planning/MILESTONE_TRACKER.md
✅ devdocs/execution/WORKSTREAM_G2_PROGRESS.md
✅ devdocs/analysis/DUPLICATE_ANALYSIS.md
✅ devdocs/handoffs/HANDOFF_2025-11-20_UET.md
✅ devdocs/archive/2025-11/ARCHIVE_SUMMARY.md
```

**Git Treatment**: Committed for continuity, excluded from releases/distributions

---

### Category 4: Runtime Artifacts (Generated)

**Definition**: Files and directories created at runtime by the system during execution.

**Location**: Dot-prefixed directories at root level

**Naming Convention**:
- Directories: `.worktrees/`, `.runs/`, `.tasks/`, `.ledger/`
- Log files: `pipeline_YYYYMMDD_HHMMSS.log`
- State: `pipeline_state.db`, `*.jsonl`

**Examples**:
```
✅ .worktrees/ws-abc-123/
✅ .runs/run_20251122_170000/
✅ .tasks/pending/task_001.json
✅ .ledger/execution.jsonl
✅ logs/pipeline_20251122_170745.log
✅ __pycache__/orchestrator.cpython-311.pyc
```

**Git Treatment**: Fully ignored (`.gitignore`), never committed

---

## Migration Plan

### Phase 1: Create `devdocs/` Structure (Immediate)

**Actions**:
1. Create `devdocs/` directory at root level
2. Create subdirectories: `phases/`, `sessions/`, `planning/`, `execution/`, `analysis/`, `handoffs/`, `archive/`, `meta/`
3. Update `.gitignore` to include runtime artifacts
4. Document the new structure in `FILE_ORGANIZATION_SYSTEM.md` (this file)

**No file moves yet** - establish structure first.

---

### Phase 2: Move Development Artifacts (Staged Migration)

**Priority 1 - Phase Documentation** (Move First):
```
docs/PHASE_*_PLAN.md           → devdocs/phases/phase-*/PLAN.md
docs/PHASE_*_COMPLETE.md       → devdocs/phases/phase-*/COMPLETE.md
docs/PHASE_*_EXECUTION_SUMMARY.md → devdocs/phases/phase-*/EXECUTION_SUMMARY.md
docs/PHASE_*_PROGRESS.md       → devdocs/phases/phase-*/PROGRESS.md
docs/PHASE_ROADMAP.md          → devdocs/planning/PHASE_ROADMAP.md
```

**Priority 2 - Session Logs**:
```
docs/sessions/*                           → devdocs/sessions/
UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/SESSION_*.md → devdocs/sessions/uet/
PROCESS_DEEP_DIVE_OPTOMIZE/session_reports/ → devdocs/sessions/process-deep-dive/
AGENTIC_DEV_PROTOTYPE/SESSION_*.md        → devdocs/sessions/agentic-proto/
```

**Priority 3 - Execution Summaries**:
```
docs/*_EXECUTION_SUMMARY.md    → devdocs/execution/
docs/*_PROGRESS*.md            → devdocs/execution/
docs/*_COMPLETION*.md          → devdocs/execution/
```

**Priority 4 - Analysis Reports**:
```
docs/analysis/*                → devdocs/analysis/
PROCESS_DEEP_DIVE_OPTOMIZE/reports/ → devdocs/analysis/process-deep-dive/
*/METRICS_SUMMARY_*.md         → devdocs/analysis/
```

**Priority 5 - Handoffs & Meta**:
```
*/HANDOFF_*.md                 → devdocs/handoffs/
PROCESS_DEEP_DIVE_OPTOMIZE/TERMINAL_SESSION_SAVE_GUIDE.md → devdocs/meta/
*/DATA_COLLECTION_*.md         → devdocs/meta/
```

**Priority 6 - Archive Completed Work**:
```
docs/archive/phase-h-legacy/   → devdocs/archive/phase-h-legacy/
docs/archive/cleanup-reports/  → devdocs/archive/cleanup-reports/
legacy/*_archived_2025-11-22/  → devdocs/archive/2025-11/
```

---

### Phase 3: Clean Up Temporary Directories (After Migration)

**Candidates for Removal/Archive**:
```
PROCESS_DEEP_DIVE_OPTOMIZE/     → devdocs/archive/process-deep-dive/
UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/ → Keep core/, profiles/, schema/; move docs to devdocs/
Multi-Document Versioning Automation final_spec_docs/ → Assess if still active
AGENTIC_DEV_PROTOTYPE/          → devdocs/archive/agentic-prototype/
```

**Evaluation Criteria**:
- Is this an active workstream or completed experiment?
- Does it contain production code or just development artifacts?
- Is it referenced by current systems?

---

## Naming Convention Rules

### Development File Patterns (ALL_CAPS + Suffix)

| Pattern | Example | Location |
|---------|---------|----------|
| `PHASE_<ID>_PLAN.md` | `PHASE_I_PLAN.md` | `devdocs/phases/phase-i/` |
| `PHASE_<ID>_COMPLETE.md` | `PHASE_G_COMPLETE.md` | `devdocs/phases/phase-g/` |
| `PHASE_<ID>_EXECUTION_SUMMARY.md` | `PHASE_I_EXECUTION_SUMMARY.md` | `devdocs/phases/phase-i/` |
| `SESSION_<DATE>_<DESC>.md` | `SESSION_2025-11-20_MEGA.md` | `devdocs/sessions/` |
| `<CONTEXT>_PROGRESS.md` | `WORKSTREAM_G2_PROGRESS.md` | `devdocs/execution/` |
| `<TYPE>_ANALYSIS.md` | `DUPLICATE_ANALYSIS.md` | `devdocs/analysis/` |
| `HANDOFF_<DATE>_<DESC>.md` | `HANDOFF_2025-11-20_UET.md` | `devdocs/handoffs/` |
| `METRICS_SUMMARY_<DATE>.md` | `METRICS_SUMMARY_20251120.md` | `devdocs/analysis/` |

### System File Patterns (lowercase/kebab-case)

| Pattern | Example | Location |
|---------|---------|----------|
| `snake_case.py` | `orchestrator.py` | `core/engine/` |
| `test_*.py` | `test_orchestrator.py` | `tests/pipeline/` |
| `kebab-case.json` | `adapter-profiles.json` | `config/` |
| `snake_case.ps1` | `bootstrap.ps1` | `scripts/` |
| `UPPERCASE.md` (root docs) | `ARCHITECTURE.md` | `docs/` |
| `kebab-case.md` (guides) | `api-overview.md` | `docs/reference/` |

---

## `.gitignore` Rules

### Current Rules (Keep)

```gitignore
# Runtime artifacts
.worktrees/
.runs/
.tasks/
.ledger/
logs/
__pycache__/
.pytest_cache/
*.pyc
*.pyo
*.pyd

# Environment
.venv/
venv/
.env.local

# Build artifacts
dist/
build/
*.egg-info/

# IDE
.vscode/
.idea/
```

### Proposed Additions

```gitignore
# Development workspace (if needed for local notes)
devdocs/scratch/
devdocs/.drafts/

# Temporary exports
*.tmp.md
*.draft.md
```

**Note**: `devdocs/` itself is **NOT** gitignored - development artifacts are committed for continuity.

---

## Handover & Cleanup Process

### For Release Preparation

1. **System Files Review**:
   - Verify all production code is in proper locations (`core/`, `engine/`, `error/`, etc.)
   - Ensure tests are comprehensive and passing
   - Validate documentation is up-to-date

2. **Development Artifacts**:
   - Archive completed phase docs: `devdocs/phases/phase-*/ → devdocs/archive/YYYY-MM/`
   - Archive old session logs: `devdocs/sessions/ → devdocs/archive/YYYY-MM/sessions/`
   - Keep only active planning documents in `devdocs/planning/`

3. **Distribution Package** (Excludes):
   - `devdocs/` entirely
   - `.worktrees/`, `.runs/`, `.tasks/`, `.ledger/`
   - `logs/`, `__pycache__/`, `.pytest_cache/`
   - `legacy/` (optional)

4. **Archive Strategy**:
   ```
   devdocs/archive/
   ├── 2025-11/
   │   ├── phase-h-legacy/
   │   ├── sessions/
   │   └── ARCHIVE_SUMMARY.md
   └── 2025-12/
       └── ...
   ```

---

## Implementation Checklist

### Immediate (Phase 1)

- [ ] Create `devdocs/` directory structure
- [ ] Create subdirectories: `phases/`, `sessions/`, `planning/`, `execution/`, `analysis/`, `handoffs/`, `archive/`, `meta/`
- [ ] Add this file: `docs/FILE_ORGANIZATION_SYSTEM.md`
- [ ] Update `.gitignore` with proposed additions
- [ ] Document structure in `DIRECTORY_GUIDE.md`

### Short-term (Phase 2 - Staged)

- [ ] Move phase documentation to `devdocs/phases/`
- [ ] Move session logs to `devdocs/sessions/`
- [ ] Move execution summaries to `devdocs/execution/`
- [ ] Move analysis reports to `devdocs/analysis/`
- [ ] Move handoff documents to `devdocs/handoffs/`
- [ ] Update all internal cross-references

### Medium-term (Phase 3)

- [ ] Evaluate temporary directories for archival
- [ ] Archive `PROCESS_DEEP_DIVE_OPTOMIZE/` completed work
- [ ] Archive `AGENTIC_DEV_PROTOTYPE/` if no longer active
- [ ] Consolidate `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/` docs
- [ ] Update build/release scripts to exclude `devdocs/`

### Ongoing Maintenance

- [ ] New phase docs go directly to `devdocs/phases/`
- [ ] Session logs go to `devdocs/sessions/`
- [ ] Archive completed phases monthly
- [ ] Keep `devdocs/planning/` current with active work only
- [ ] Review and clean `devdocs/archive/` quarterly

---

## Benefits

### 1. Clear Separation
- **Production code** in standard locations (`core/`, `engine/`, `tests/`)
- **Development artifacts** in dedicated `devdocs/` tree
- **Runtime data** in dot-prefixed directories

### 2. Easier Cleanup
- Archive entire `devdocs/phases/phase-x/` when complete
- No risk of deleting production code
- Simple distribution: exclude `devdocs/` entirely

### 3. Better Navigation
- AI tools know where to find system code vs process docs
- New contributors see clean production structure
- Development history preserved but separate

### 4. Flexible Archival
- Archive by phase: `devdocs/archive/phase-g/`
- Archive by date: `devdocs/archive/2025-11/`
- Keep active planning accessible

### 5. Handover Ready
- `devdocs/` can be shared or omitted as needed
- System files are self-contained
- Clear documentation of what's what

---

## Cross-References

- [DIRECTORY_GUIDE.md](DIRECTORY_GUIDE.md) - Repository navigation
- [AGENTS.md](../AGENTS.md) - Coding guidelines
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) - Doc inventory

---

## Appendix A: Current State Analysis

### Directories with Mixed Content

| Directory | System Files | Dev Artifacts | Action |
|-----------|--------------|---------------|--------|
| `docs/` | ✅ ARCHITECTURE.md, guides | ❌ PHASE_*.md, session logs | Split: keep architecture, move phases |
| `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/` | ✅ core/, profiles/, schema/ | ❌ SESSION_*.md, PHASE_*.md | Split: keep system, move docs |
| `PROCESS_DEEP_DIVE_OPTOMIZE/` | ❌ None | ✅ All session reports, analysis | Archive entirely |
| `AGENTIC_DEV_PROTOTYPE/` | ❓ Possible specs | ✅ Session logs, reports | Evaluate & split/archive |
| `Multi-Document Versioning Automation final_spec_docs/` | ❓ Tools? | ✅ Phase docs | Evaluate status |

### Recommended Priority Actions

1. **High Priority**: Move all `PHASE_*.md` files from `docs/` to `devdocs/phases/`
2. **High Priority**: Consolidate session logs from multiple locations to `devdocs/sessions/`
3. **Medium Priority**: Archive `PROCESS_DEEP_DIVE_OPTOMIZE/` (appears completed)
4. **Medium Priority**: Evaluate `AGENTIC_DEV_PROTOTYPE/` and `Multi-Document Versioning...` for archival
5. **Low Priority**: Clean up temporary files (`__tmp_o.py`, `nul`, etc.)

---

**END OF FILE ORGANIZATION SYSTEM SPECIFICATION**
