---
doc_id: DOC-GUIDE-README-415
---

# Doc ID Framework - Main Directory

**Last Updated**: 2025-11-29  
**Status**: Production-ready (v1.0)  
**Purpose**: Document ID framework for AI Development Pipeline

---

## Overview

This directory contains the **complete Doc ID Framework** - a system for assigning unique, stable identifiers to all documents and files in the repository. The framework enables:

- **Traceability**: Track documents across moves, renames, and refactors
- **Multi-agent coordination**: Prevent conflicts during parallel operations
- **Lifecycle management**: Handle file splits, merges, and deletions
- **Conflict resolution**: Detect and resolve ID conflicts

---

## Directory Structure

```
doc_id/
├── README.md                    (This file)
│
├── analysis/                    AI evaluations & conflict analysis
│   ├── README.md
│   ├── AI_EVAL_REALITY_CHECK.md
│   ├── AI_EVAL_SYNTHESIS_AND_ACTION_PLAN.md
│   ├── CONFLICT_ANALYSIS_AND_RESOLUTION.md
│   ├── ID_FRAMEWORK_ANALYSIS_AND_ROADMAP.md
│   └── ...
│
├── plans/                       Execution plans & guides
│   ├── README.md
│   ├── DOC_ID_EXECUTION_PLAN.md
│   ├── DOC_ID_PARALLEL_EXECUTION_GUIDE.md
│   └── PLAN_DOC_ID_PHASE3_EXECUTION__v1.md
│
├── specs/                       Specifications & standards
│   ├── README.md
│   ├── DOC_ID_FRAMEWORK.md      (Main specification)
│   ├── DOC_ID_REGISTRY.yaml     (Central registry)
│   ├── ADR-010-ulid-identity.md (Architecture decision)
│   └── UTE_ID_SYSTEM_SPEC.md
│
├── tools/                       CLI tools & scripts
│   ├── README.md
│   ├── doc_id_registry_cli.py   (Registry management)
│   ├── doc_id_scanner.py        (Scan & assign IDs)
│   ├── test_doc_id_compliance.py
│   └── ...
│
├── reports/                     Coverage & inventory reports
│   ├── README.md
│   ├── DOC_ID_COVERAGE_REPORT.md
│   ├── docs_inventory.jsonl     (Current inventory)
│   └── ...
│
├── batches/                     Batch ID assignments
│   ├── README.md
│   └── batch_*.yaml
│
├── deltas/                      Incremental updates
│   ├── README.md
│   └── delta_*.yaml
│
└── session_reports/             Session completion reports
    ├── README.md
    ├── DOC_ID_PROJECT_PHASE1_COMPLETE.md
    └── DOC_ID_PROJECT_PHASE2_COMPLETE.md
```

---

## Quick Start

### 1. Scan Repository for Doc IDs

```bash
cd doc_id/tools
python doc_id_scanner.py scan
```

### 2. Check Coverage

```bash
python doc_id_scanner.py stats
```

### 3. Mint New Doc ID

```bash
python doc_id_registry_cli.py mint --category CORE --name MY-MODULE
```

### 4. Validate Consistency

```bash
powershell validate_doc_id_consistency.ps1
```

---

## Key Files

| File | Purpose |
|------|---------|
| **specs/DOC_ID_FRAMEWORK.md** | Complete framework specification |
| **specs/DOC_ID_REGISTRY.yaml** | Central ID registry (single source of truth) |
| **tools/doc_id_registry_cli.py** | CLI for minting and managing IDs |
| **tools/doc_id_scanner.py** | Scanner for assigning IDs to files |
| **reports/docs_inventory.jsonl** | Current inventory of all doc IDs |
| **reports/DOC_ID_COVERAGE_REPORT.md** | Coverage statistics |

---

## ID Format

```
DOC-<CATEGORY>-<NAME>-<SEQ>
```

**Examples**:
- `DOC-CORE-STATE-001` - Core state module
- `DOC-ERROR-PLUGIN-002` - Error detection plugin
- `DOC-SPEC-SCHEMA-003` - Schema specification

---

## Phase Completion Status

| Phase | Status | Report |
|-------|--------|--------|
| **Phase 1** | ✅ Complete | `session_reports/DOC_ID_PROJECT_PHASE1_COMPLETE.md` |
| **Phase 2** | ✅ Complete | `session_reports/DOC_ID_PROJECT_PHASE2_COMPLETE.md` |
| **Phase 3** | 🚧 In Progress | `plans/PLAN_DOC_ID_PHASE3_EXECUTION__v1.md` |

---

## Tools Reference

### Registry CLI
```bash
python tools/doc_id_registry_cli.py mint --category CORE --name MODULE
```

### Scanner
```bash
python tools/doc_id_scanner.py scan
python tools/doc_id_scanner.py report
```

---

**Status**: Production-ready (v1.0)  
**Last Updated**: 2025-11-29  
**See subdirectory READMEs for detailed information**
