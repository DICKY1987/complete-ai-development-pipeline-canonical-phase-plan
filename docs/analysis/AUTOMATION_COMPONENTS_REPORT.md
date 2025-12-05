---
doc_id: DOC-GUIDE-AUTOMATION-COMPONENTS-REPORT-455
---

# Automation Components Report
**Generated:** 2025-12-05 11:18:06 UTC
**Repository:** Complete AI Development Pipeline – Canonical Phase Plan

---

## Executive Summary

This repository contains **566 automation components** across 9 categories:

| Category | Count | Purpose |
|----------|-------|---------|
| GitHub Workflows | 11 | CI/CD automation triggers |
| Python Scripts | 109 | Automation utilities and tools |
| PowerShell Scripts | 63 | Windows-native automation |
| Pattern Executors (PowerShell) | 100 | Reusable pattern implementations |
| Pattern Executors (Python) | 0 | GitHub Projects v2 sync |
| Core Framework Modules | 109 | Self-configuring orchestration engine |
| Pattern Specifications | 0 | Automation pattern definitions |
| Glossary Automation | 2 | Term management automation |
| Test Automation | 172 | Automated testing suite |
| **TOTAL** | **566** | |

---

## 1. GitHub Workflows (11)

**Location:** `.github/workflows/`
**Purpose:** Continuous integration and deployment automation

### Active Workflows

1. **doc_id_validation.yml**
2. **documentation.yml**
3. **glossary-validation.yml**
4. **milestone_completion.yml**
5. **module_id_validation.yml**
6. **path_standards.yml**
7. **pattern-automation.yml**
8. **project_item_sync.yml**
9. **quality-gates.yml**
10. **registry_integrity.yml**
11. **splinter_phase_sync.yml**

---

## 2. Python Scripts (109)

**Location:** `scripts/`
**Purpose:** Core automation utilities

**Count:** 109 Python scripts in scripts/ directory

---

## 3. PowerShell Scripts (63)

**Location:** `scripts/`
**Purpose:** Windows-native automation

**Count:** 63 PowerShell scripts in scripts/ directory

---

## 4. Pattern Executors (PowerShell) (100)

**Location:** `patterns/executors/`
**Purpose:** Reusable automation patterns

**Count:** 100 PowerShell pattern executors

---

## 5. Pattern Executors (Python) (0)

**Location:** `patterns/executors/`
**Purpose:** Python-based automation patterns

**Count:** 0 Python pattern executors

---

## 6. Core Framework Modules (109)

**Locations:** `core/`, `error/`, `aim/`, `pm/`, `specifications/`
**Purpose:** Self-configuring orchestration engine

**Count:** 109 Python modules

---

## 7. Pattern Specifications (0)

**Location:** `patterns/specifications/`
**Purpose:** Pattern metadata and definitions

**Count:** 0 YAML specification files

---

## 8. Glossary Automation (2)

**Location:** `glossary/scripts/`
**Purpose:** Term management and validation

**Count:** 2 automation scripts

---

## 9. Test Automation (172)

**Location:** `tests/`
**Purpose:** Automated test suite

**Count:** 172 test files

---

## Usage

These automation components are monitored and orchestrated through:

1. **GitHub Actions** - CI/CD workflows (.github/workflows/*.yml)
2. **Phase Coordinator** - Core automation engine (core/engine/phase_coordinator.py)
3. **Error Recovery** - Self-healing loop (error/engine/error_engine.py)
4. **State Management** - Execution tracking (.state/ directory)

For monitoring active automation:
- Check `.state/` directory for execution state files
- Review `config/coordinator_config.yaml` for phase settings
- Monitor GitHub Actions at repository Actions tab

---

**End of Report**
