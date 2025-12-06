#!/usr/bin/env python3
"""
Regenerate AUTOMATION_COMPONENTS_REPORT.md with current component counts

Scans repository for:
- GitHub workflows
- Python scripts
- PowerShell scripts
- Core modules
- Tests


DOC_ID: DOC-SCRIPT-SCRIPTS-REGENERATE-AUTOMATION-REPORT-772
"""

import os
from datetime import datetime, timezone
from pathlib import Path


def count_files(root: Path, pattern: str, exclude_dirs: list) -> list:
    """Count files matching pattern, excluding specific directories"""
    files = []
    for file_path in root.rglob(pattern):
        rel_path = file_path.relative_to(root)
        if not any(exclude in str(rel_path) for exclude in exclude_dirs):
            files.append(str(rel_path).replace("\\", "/"))
    return files


def main():
    repo_root = Path(__file__).parent.parent

    exclude_dirs = [
        ".venv",
        "__pycache__",
        "node_modules",
        ".git",
        "_ARCHIVE",
        "legacy",
        ".worktrees",
    ]

    # Count components
    workflows = list((repo_root / ".github" / "workflows").glob("*.yml"))
    py_scripts = count_files(repo_root / "scripts", "*.py", exclude_dirs)
    ps_scripts = count_files(repo_root / "scripts", "*.ps1", exclude_dirs)
    pattern_executors_ps = count_files(
        repo_root / "patterns" / "executors", "*.ps1", exclude_dirs
    )
    pattern_executors_py = count_files(
        repo_root / "patterns" / "executors", "*.py", exclude_dirs
    )

    # Core modules
    core_modules = []
    for section in ["core", "error", "aim", "pm", "specifications"]:
        if (repo_root / section).exists():
            core_modules.extend(
                count_files(repo_root / section, "*.py", exclude_dirs + ["tests"])
            )

    # Pattern specs
    pattern_specs = count_files(
        repo_root / "patterns" / "specifications", "*.yaml", exclude_dirs
    )
    pattern_specs.extend(
        count_files(repo_root / "patterns" / "specifications", "*.yml", exclude_dirs)
    )

    # Glossary automation
    glossary_auto = count_files(
        repo_root / "glossary" / "scripts", "*.py", exclude_dirs
    )

    # Tests
    tests = count_files(repo_root / "tests", "*.py", exclude_dirs)

    total = (
        len(workflows)
        + len(py_scripts)
        + len(ps_scripts)
        + len(pattern_executors_ps)
        + len(pattern_executors_py)
        + len(core_modules)
        + len(pattern_specs)
        + len(glossary_auto)
        + len(tests)
    )

    # Generate report
    report = f"""---
doc_id: DOC-GUIDE-AUTOMATION-COMPONENTS-REPORT-455
---

# Automation Components Report
**Generated:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}
**Repository:** Complete AI Development Pipeline – Canonical Phase Plan

---

## Executive Summary

This repository contains **{total} automation components** across 9 categories:

| Category | Count | Purpose |
|----------|-------|---------|
| GitHub Workflows | {len(workflows)} | CI/CD automation triggers |
| Python Scripts | {len(py_scripts)} | Automation utilities and tools |
| PowerShell Scripts | {len(ps_scripts)} | Windows-native automation |
| Pattern Executors (PowerShell) | {len(pattern_executors_ps)} | Reusable pattern implementations |
| Pattern Executors (Python) | {len(pattern_executors_py)} | GitHub Projects v2 sync |
| Core Framework Modules | {len(core_modules)} | Self-configuring orchestration engine |
| Pattern Specifications | {len(pattern_specs)} | Automation pattern definitions |
| Glossary Automation | {len(glossary_auto)} | Term management automation |
| Test Automation | {len(tests)} | Automated testing suite |
| **TOTAL** | **{total}** | |

---

## 1. GitHub Workflows ({len(workflows)})

**Location:** `.github/workflows/`
**Purpose:** Continuous integration and deployment automation

### Active Workflows

"""

    # List workflows
    for i, wf in enumerate(sorted(workflows), 1):
        report += f"{i}. **{wf.name}**\n"

    report += f"""
---

## 2. Python Scripts ({len(py_scripts)})

**Location:** `scripts/`
**Purpose:** Core automation utilities

**Count:** {len(py_scripts)} Python scripts in scripts/ directory

---

## 3. PowerShell Scripts ({len(ps_scripts)})

**Location:** `scripts/`
**Purpose:** Windows-native automation

**Count:** {len(ps_scripts)} PowerShell scripts in scripts/ directory

---

## 4. Pattern Executors (PowerShell) ({len(pattern_executors_ps)})

**Location:** `patterns/executors/`
**Purpose:** Reusable automation patterns

**Count:** {len(pattern_executors_ps)} PowerShell pattern executors

---

## 5. Pattern Executors (Python) ({len(pattern_executors_py)})

**Location:** `patterns/executors/`
**Purpose:** Python-based automation patterns

**Count:** {len(pattern_executors_py)} Python pattern executors

---

## 6. Core Framework Modules ({len(core_modules)})

**Locations:** `core/`, `error/`, `aim/`, `pm/`, `specifications/`
**Purpose:** Self-configuring orchestration engine

**Count:** {len(core_modules)} Python modules

---

## 7. Pattern Specifications ({len(pattern_specs)})

**Location:** `patterns/specifications/`
**Purpose:** Pattern metadata and definitions

**Count:** {len(pattern_specs)} YAML specification files

---

## 8. Glossary Automation ({len(glossary_auto)})

**Location:** `glossary/scripts/`
**Purpose:** Term management and validation

**Count:** {len(glossary_auto)} automation scripts

---

## 9. Test Automation ({len(tests)})

**Location:** `tests/`
**Purpose:** Automated test suite

**Count:** {len(tests)} test files

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
"""

    # Write report
    output_path = repo_root / "AUTOMATION_COMPONENTS_REPORT.md"
    output_path.write_text(report, encoding="utf-8")

    print(f"✓ Report regenerated: {output_path}")
    print(f"  Total components: {total}")
    print(f"  GitHub workflows: {len(workflows)}")
    print(f"  Python scripts: {len(py_scripts)}")
    print(f"  PowerShell scripts: {len(ps_scripts)}")
    print(f"  Core modules: {len(core_modules)}")
    print(f"  Tests: {len(tests)}")


if __name__ == "__main__":
    main()
