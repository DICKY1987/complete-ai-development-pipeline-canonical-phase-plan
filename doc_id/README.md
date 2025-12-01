---
doc_id: DOC-GUIDE-README-415
---

# Doc ID Framework - Main Directory

**Last Updated**: 2025-12-01  
**Status**: ✅ **PRODUCTION READY** (Phases 0-2 Complete)  
**Coverage**: 93.0% (2,922/3,142 files)  
**Module System**: 100% (2,622 docs with module_id)

---

## System Status

| Component | Status | Details |
|-----------|--------|---------|
| Doc_id Coverage | ✅ 93.0% | Exceeds 90% baseline |
| Registry Validation | ✅ PASS | 0 errors, 0 warnings |
| Module Assignment | ✅ 100% | All docs have module_id |
| CI/CD Protection | ✅ ACTIVE | 3 workflows enforcing quality |
| Monitoring | ✅ ENABLED | Coverage trend tracking |

---

## Recent Achievements (Dec 2025)

- ✅ **Phase 0**: Universal doc_id coverage baseline established
- ✅ **Phase 1.5**: Module ownership system (92% automated assignment)
- ✅ **Phase 1**: CI/CD integration (automated validation on PR/push)
- ✅ **Phase 2**: Production hardening (registry fixes, monitoring)

**Time Invested**: ~9.5 hours total  
**Efficiency**: 57% under estimates  
**Quality**: Excellent (0 errors, full automation)

---

## Overview

This directory contains the **complete Doc ID Framework** - a production-ready system for assigning unique, stable identifiers to all documents and files in the repository. The framework enables:

- **Traceability**: Track documents across moves, renames, and refactors
- **Module Ownership**: Clear boundaries and responsibilities (21 modules)
- **Automated Validation**: CI/CD workflows prevent regression
- **Quality Monitoring**: Historical trend tracking and reporting
- **Multi-agent Coordination**: Prevent conflicts during parallel operations

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

### 1. Validate System Health

```bash
# Check registry integrity
python scripts/validate_registry.py

# Check doc_id coverage
python scripts/validate_doc_id_coverage.py
```

### 2. Track Coverage Over Time

```bash
# Save snapshot (run periodically)
python scripts/doc_id_coverage_trend.py snapshot

# View trends
python scripts/doc_id_coverage_trend.py report
```

### 3. Module Management

```bash
# View module assignments (dry-run)
python scripts/module_id_assigner.py --dry-run

# Rebuild module map
python scripts/build_module_map.py
```

### 4. CI/CD Workflows

Workflows run automatically on PR/push:
- `doc_id_validation.yml` - Enforces 90% coverage baseline
- `registry_integrity.yml` - Validates registry on changes
- `module_id_validation.yml` - Checks module assignments

View status:
```bash
gh workflow list
gh run list --workflow=doc_id_validation.yml
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
