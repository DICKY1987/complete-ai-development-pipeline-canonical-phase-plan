---
doc_id: DOC-GUIDE-FILE-ORG-VISUAL-1243
---

# File Organization Visual Guide

> **Purpose**: Visual diagrams showing the file organization system  
> **See Also**: [FILE_ORGANIZATION_SYSTEM.md](FILE_ORGANIZATION_SYSTEM.md)

---

## Conceptual Separation

```
┌─────────────────────────────────────────────────────────────────────┐
│                        REPOSITORY ROOT                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ╔═══════════════════════════════════════════════════════════╗    │
│  ║  SYSTEM FILES (Production/Deliverable)                    ║    │
│  ║  • Committed to Git                                       ║    │
│  ║  • Included in releases                                   ║    │
│  ║  • Part of the working system                             ║    │
│  ╠═══════════════════════════════════════════════════════════╣    │
│  ║  core/          - Core pipeline implementation            ║    │
│  ║  engine/        - Job execution engine                    ║    │
│  ║  error/         - Error detection system                  ║    │
│  ║  aim/           - AIM+ environment manager                ║    │
│  ║  scripts/       - Automation scripts                      ║    │
│  ║  tests/         - Test suite                              ║    │
│  ║  config/        - Runtime configuration                   ║    │
│  ║  schema/        - JSON/YAML schemas                       ║    │
│  ║  docs/          - User-facing documentation               ║    │
│  ║  README.md      - Main documentation                      ║    │
│  ║  AGENTS.md      - Developer guidelines                    ║    │
│  ╚═══════════════════════════════════════════════════════════╝    │
│                                                                     │
│  ╔═══════════════════════════════════════════════════════════╗    │
│  ║  DEVELOPMENT ARTIFACTS (Process Records)                  ║    │
│  ║  • Committed for continuity                               ║    │
│  ║  • Excluded from releases                                 ║    │
│  ║  • Tracks development process                             ║    │
│  ╠═══════════════════════════════════════════════════════════╣    │
│  ║  devdocs/                                                 ║    │
│  ║  ├── phases/       - Phase plans & completion reports     ║    │
│  ║  ├── sessions/     - Session logs & summaries             ║    │
│  ║  ├── execution/    - Progress & execution summaries       ║    │
│  ║  ├── planning/     - Active planning documents            ║    │
│  ║  ├── analysis/     - Code & metrics analysis              ║    │
│  ║  ├── handoffs/     - Handoff documents                    ║    │
│  ║  ├── archive/      - Completed development work           ║    │
│  ║  └── meta/         - Process documentation                ║    │
│  ╚═══════════════════════════════════════════════════════════╝    │
│                                                                     │
│  ╔═══════════════════════════════════════════════════════════╗    │
│  ║  RUNTIME ARTIFACTS (Generated)                            ║    │
│  ║  • NOT committed (gitignored)                             ║    │
│  ║  • Created during execution                               ║    │
│  ║  • Temporary/cache files                                  ║    │
│  ╠═══════════════════════════════════════════════════════════╣    │
│  ║  .worktrees/    - Per-workstream working folders          ║    │
│  ║  .runs/         - Execution run records                   ║    │
│  ║  .tasks/        - Task queue storage                      ║    │
│  ║  .ledger/       - Execution ledger                        ║    │
│  ║  logs/          - Application logs                        ║    │
│  ║  __pycache__/   - Python bytecode cache                   ║    │
│  ╚═══════════════════════════════════════════════════════════╝    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## File Lifecycle Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                     DEVELOPMENT PHASE                            │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
            ┌─────────────────────────────────┐
            │  Create Phase Plan              │
            │  devdocs/phases/phase-k/PLAN.md │
            └─────────────────────────────────┘
                              │
                              ▼
            ┌─────────────────────────────────┐
            │  Work Sessions (multiple)       │
            │  devdocs/sessions/SESSION_*.md  │
            └─────────────────────────────────┘
                              │
                              ▼
            ┌─────────────────────────────────┐
            │  Track Progress                 │
            │  devdocs/execution/*_PROGRESS.md│
            └─────────────────────────────────┘
                              │
                              ▼
            ┌─────────────────────────────────┐
            │  Write Production Code          │
            │  core/, engine/, tests/, etc.   │
            └─────────────────────────────────┘
                              │
                              ▼
            ┌─────────────────────────────────┐
            │  Complete Phase                 │
            │  devdocs/phases/phase-k/        │
            │  COMPLETE.md                    │
            └─────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                        CLEANUP PHASE                             │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
            ┌─────────────────────────────────┐
            │  Archive Development Artifacts  │
            │  devdocs/archive/YYYY-MM/       │
            └─────────────────────────────────┘
                              │
                              ▼
            ┌─────────────────────────────────┐
            │  System Files Remain            │
            │  core/, engine/, docs/, etc.    │
            │  (Production codebase)          │
            └─────────────────────────────────┘
```

---

## File Decision Matrix

```
                                    File Type Decision
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    ▼                      ▼                      ▼
            Is it executable?      Is it temporary?      Is it about process?
            (code, script)         (cache, logs)         (planning, sessions)
                    │                      │                      │
                    ▼                      ▼                      ▼
            ┌───────────────┐      ┌──────────────┐      ┌──────────────┐
            │ SYSTEM FILE   │      │ RUNTIME      │      │ DEVELOPMENT  │
            │               │      │ ARTIFACT     │      │ ARTIFACT     │
            ├───────────────┤      ├──────────────┤      ├──────────────┤
            │ Location:     │      │ Location:    │      │ Location:    │
            │ core/         │      │ .worktrees/  │      │ devdocs/     │
            │ engine/       │      │ .runs/       │      │              │
            │ scripts/      │      │ logs/        │      │              │
            │ tests/        │      │ __pycache__/ │      │              │
            │               │      │              │      │              │
            │ Git: ✅ Yes   │      │ Git: ❌ No   │      │ Git: ✅ Yes  │
            │ Release: ✅   │      │ Release: ❌  │      │ Release: ❌  │
            └───────────────┘      └──────────────┘      └──────────────┘
```

---

## Naming Convention Visual

```
┌────────────────────────────────────────────────────────────────┐
│                    SYSTEM FILES (Production)                   │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Python:      snake_case.py                                    │
│               orchestrator.py, error_engine.py                 │
│                                                                │
│  Tests:       test_*.py                                        │
│               test_orchestrator.py, test_db.py                 │
│                                                                │
│  Scripts:     snake_case.ps1 / .sh                             │
│               bootstrap.ps1, run_tests.sh                      │
│                                                                │
│  Config:      kebab-case.json / .yaml                          │
│               adapter-profiles.json, circuit-breaker.yaml      │
│                                                                │
│  Docs:        UPPERCASE.md (major) / kebab-case.md (guides)    │
│               ARCHITECTURE.md, api-overview.md                 │
│                                                                │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│              DEVELOPMENT ARTIFACTS (Process Records)           │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Phase Plans:        PHASE_<ID>_PLAN.md                        │
│                      PHASE_I_PLAN.md                           │
│                                                                │
│  Phase Complete:     PHASE_<ID>_COMPLETE.md                    │
│                      PHASE_G_COMPLETE.md                       │
│                                                                │
│  Execution:          PHASE_<ID>_EXECUTION_SUMMARY.md           │
│                      PHASE_I_EXECUTION_SUMMARY.md              │
│                                                                │
│  Sessions:           SESSION_<DATE>_<DESC>.md                  │
│                      SESSION_2025-11-22_ERROR_PIPELINE.md      │
│                                                                │
│  Progress:           <CONTEXT>_PROGRESS.md                     │
│                      WORKSTREAM_G2_PROGRESS.md                 │
│                                                                │
│  Analysis:           <TYPE>_ANALYSIS.md                        │
│                      DUPLICATE_ANALYSIS.md                     │
│                      METRICS_SUMMARY_20251120.md               │
│                                                                │
│  Handoffs:           HANDOFF_<DATE>_<DESC>.md                  │
│                      HANDOFF_2025-11-20_UET.md                 │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure: Before vs After

### BEFORE (Current - Mixed)

```
docs/
├── ARCHITECTURE.md                    ← System doc ✅
├── CONFIGURATION_GUIDE.md             ← System doc ✅
├── PHASE_I_PLAN.md                    ← Dev artifact ⚠️ (wrong location)
├── PHASE_I_COMPLETE.md                ← Dev artifact ⚠️ (wrong location)
├── PHASE_G_EXECUTION_SUMMARY.md       ← Dev artifact ⚠️ (wrong location)
├── sessions/
│   └── SESSION_SUMMARY_2025-11-19.md  ← Dev artifact ⚠️ (wrong location)
└── reference/
    └── api-overview.md                ← System doc ✅

UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/
├── core/                              ← System code ✅
├── profiles/                          ← System code ✅
├── SESSION_SUMMARY_*.md               ← Dev artifact ⚠️ (wrong location)
└── PHASE_3_COMPLETION_REPORT.md       ← Dev artifact ⚠️ (wrong location)
```

### AFTER (Proposed - Separated)

```
docs/
├── ARCHITECTURE.md                    ← System doc ✅
├── CONFIGURATION_GUIDE.md             ← System doc ✅
├── FILE_ORGANIZATION_SYSTEM.md        ← System doc ✅ (NEW)
└── reference/
    └── api-overview.md                ← System doc ✅

devdocs/                               ← NEW DIRECTORY
├── phases/
│   ├── phase-g/
│   │   ├── PLAN.md                    ← Dev artifact ✅ (moved)
│   │   ├── EXECUTION_SUMMARY.md       ← Dev artifact ✅ (moved)
│   │   └── COMPLETE.md                ← Dev artifact ✅ (moved)
│   └── phase-i/
│       ├── PLAN.md                    ← Dev artifact ✅ (moved)
│       └── COMPLETE.md                ← Dev artifact ✅ (moved)
├── sessions/
│   ├── SESSION_2025-11-19_SUMMARY.md  ← Dev artifact ✅ (moved)
│   └── uet/
│       └── SESSION_2025-11-20_*.md    ← Dev artifact ✅ (moved)
└── archive/
    └── 2025-11/
        └── phase-h-legacy/            ← Archived work ✅

UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/
├── core/                              ← System code ✅
└── profiles/                          ← System code ✅
```

---

## Release Package Contents

```
┌────────────────────────────────────────────────────────────────┐
│                    RELEASE DISTRIBUTION                        │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ✅ INCLUDED:                                                  │
│     • core/                - Production code                   │
│     • engine/              - Production code                   │
│     • error/               - Production code                   │
│     • aim/                 - Production code                   │
│     • scripts/             - Automation                        │
│     • tests/               - Test suite                        │
│     • config/              - Configuration                     │
│     • schema/              - Schemas                           │
│     • docs/                - User documentation                │
│     • README.md            - Entry point                       │
│     • AGENTS.md            - Developer guide                   │
│     • requirements.txt     - Dependencies                      │
│                                                                │
│  ❌ EXCLUDED:                                                  │
│     • devdocs/             - Development process records       │
│     • .worktrees/          - Runtime artifacts                 │
│     • .runs/               - Runtime artifacts                 │
│     • logs/                - Runtime artifacts                 │
│     • __pycache__/         - Build artifacts                   │
│     • legacy/              - Archived old code (optional)      │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Archive Strategy Visualization

```
Development Timeline:
═══════════════════════════════════════════════════════════════

Phase A ──▶ Phase B ──▶ Phase C ──▶ ... ──▶ Current Work
  │           │           │                      │
  ▼           ▼           ▼                      ▼
Archive   Archive   Archive               Active in devdocs/
  │           │           │
  ▼           ▼           ▼
devdocs/archive/
├── 2025-10/
│   ├── phase-a/
│   │   ├── PLAN.md
│   │   └── COMPLETE.md
│   └── phase-b/
│       ├── PLAN.md
│       └── COMPLETE.md
├── 2025-11/
│   ├── phase-c/
│   │   ├── PLAN.md
│   │   └── COMPLETE.md
│   └── ARCHIVE_SUMMARY.md  ← Index of what was archived
└── ...

Current Active Work:
devdocs/
├── phases/
│   └── phase-current/       ← Currently working on this
│       ├── PLAN.md
│       └── PROGRESS.md
├── sessions/
│   └── SESSION_2025-11-22_*.md  ← Recent sessions
└── planning/
    └── PHASE_ROADMAP.md     ← Future planning
```

---

## Quick Reference Card

```
╔══════════════════════════════════════════════════════════════╗
║              WHERE DOES THIS FILE GO?                        ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Python module          → core/, engine/, error/             ║
║  Test file              → tests/                             ║
║  Script                 → scripts/                           ║
║  Config                 → config/                            ║
║  Schema                 → schema/                            ║
║  System docs            → docs/                              ║
║  Phase plan             → devdocs/phases/phase-x/            ║
║  Session log            → devdocs/sessions/                  ║
║  Progress report        → devdocs/execution/                 ║
║  Analysis report        → devdocs/analysis/                  ║
║  Handoff doc            → devdocs/handoffs/                  ║
║  Completed phase        → devdocs/archive/YYYY-MM/           ║
║  Runtime worktree       → .worktrees/ (gitignored)           ║
║  Log file               → logs/ (gitignored)                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

**END OF VISUAL GUIDE**
