#!/usr/bin/env python3
"""
Automation Index Generator

Parses AUTOMATION_COMPONENTS_REPORT.md and generates automation_index.json
This bridges your existing documentation to the machine-readable format
required by the self-healing orchestrator.
"""
DOC_ID: DOC-CORE-ORCHESTRATOR-GENERATE-INDEX-781

import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def generate_ulid() -> str:
    """Generate a ULID"""
    import random

    chars = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
    timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
    ts_part = ""
    for i in range(9, -1, -1):
        ts_part = chars[(timestamp >> (i * 5)) & 31] + ts_part
    rand_part = "".join(random.choice(chars) for _ in range(16))
    return ts_part[:10] + rand_part[:16]


def get_git_info(repo_root: Path) -> Dict[str, str]:
    """Get current git information"""
    info = {"sha": "", "branch": ""}
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo_root, capture_output=True, text=True
        )
        if result.returncode == 0:
            info["sha"] = result.stdout.strip()

        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            info["branch"] = result.stdout.strip()
    except Exception:
        pass
    return info


def discover_github_workflows(repo_root: Path) -> List[Dict[str, Any]]:
    """Discover GitHub workflow files"""
    workflows = []
    workflow_dir = repo_root / ".github" / "workflows"

    if not workflow_dir.exists():
        return workflows

    counter = 1
    for yml_file in workflow_dir.glob("*.yml"):
        content = yml_file.read_text(errors="ignore")

        # Extract workflow name
        name_match = re.search(r'^name:\s*["\']?([^"\'\n]+)', content, re.MULTILINE)
        name = name_match.group(1).strip() if name_match else yml_file.stem

        # Detect triggers
        triggers = []
        if re.search(r"on:\s*\n\s*push:", content) or re.search(
            r"on:\s*\[?'?push", content
        ):
            triggers.append("push")
        if re.search(r"pull_request:", content):
            triggers.append("pr")
        if re.search(r"schedule:", content):
            triggers.append("schedule")
        if re.search(r"workflow_dispatch:", content):
            triggers.append("manual")
        if re.search(r"workflow_call:", content):
            triggers.append("workflow_call")

        workflows.append(
            {
                "id": f"AUTO-GH-{counter:03d}",
                "type": "github_workflow",
                "path": str(yml_file.relative_to(repo_root)).replace("\\", "/"),
                "name": name,
                "description": f"GitHub Actions workflow: {name}",
                "trigger": triggers or ["manual"],
                "validator": "github_actions",
                "timeout_seconds": 600,
                "metadata": {"priority": "high", "tags": ["ci-cd", "github-actions"]},
            }
        )
        counter += 1

    return workflows


def discover_scripts(repo_root: Path) -> List[Dict[str, Any]]:
    """Discover PowerShell and Python scripts"""
    scripts = []

    ps_counter = 1
    py_counter = 1

    # PowerShell scripts
    for ps_file in repo_root.rglob("*.ps1"):
        rel_path = str(ps_file.relative_to(repo_root)).replace("\\", "/")

        # Skip excluded directories
        if any(x in rel_path for x in ["node_modules", ".git", "vendor", ".venv"]):
            continue

        # Determine type
        if "patterns/executors" in rel_path:
            unit_type = "pattern_executor"
            prefix = "PE"
        else:
            unit_type = "powershell"
            prefix = "PS"

        counter = ps_counter if prefix == "PS" else ps_counter

        scripts.append(
            {
                "id": f"AUTO-{prefix}-{counter:03d}",
                "type": unit_type,
                "path": rel_path,
                "name": ps_file.stem,
                "trigger": ["cli", "manual"],
                "validator": "process_exit_code",
                "timeout_seconds": 300,
                "metadata": {
                    "priority": "medium",
                    "tags": ["powershell", "automation"],
                },
            }
        )
        ps_counter += 1

    # Python scripts
    for py_file in repo_root.rglob("*.py"):
        rel_path = str(py_file.relative_to(repo_root)).replace("\\", "/")

        # Skip excluded directories and special files
        if any(
            x in rel_path
            for x in ["node_modules", ".git", "vendor", ".venv", "__pycache__"]
        ):
            continue
        if py_file.name.startswith("__"):
            continue

        # Determine type
        is_test = "test" in rel_path.lower() or py_file.name.startswith("test_")
        is_core = "/core/" in rel_path
        is_glossary = "glossary/scripts" in rel_path

        if is_test:
            unit_type = "test_suite"
            prefix = "TS"
            validator = "pytest"
            timeout = 600
        elif is_glossary:
            unit_type = "glossary_script"
            prefix = "GS"
            validator = "process_exit_code"
            timeout = 300
        elif is_core:
            unit_type = "core_module"
            prefix = "CM"
            validator = "process_exit_code"
            timeout = 300
        else:
            unit_type = "python"
            prefix = "PY"
            validator = "process_exit_code"
            timeout = 300

        scripts.append(
            {
                "id": f"AUTO-{prefix}-{py_counter:03d}",
                "type": unit_type,
                "path": rel_path,
                "name": py_file.stem,
                "trigger": ["cli", "pipeline"] if is_test else ["cli", "manual"],
                "validator": validator,
                "timeout_seconds": timeout,
                "metadata": {
                    "priority": "high" if is_core else "medium",
                    "tags": ["python", unit_type.replace("_", "-")],
                },
            }
        )
        py_counter += 1

    return scripts


def parse_components_report(report_path: Path) -> Dict[str, int]:
    """Parse AUTOMATION_COMPONENTS_REPORT.md to get expected counts"""
    if not report_path.exists():
        return {}

    content = report_path.read_text(errors="ignore")
    counts = {}

    # Extract counts from the summary table
    patterns = {
        "github_workflows": r"GitHub Workflows\s*\|\s*(\d+)",
        "python_scripts": r"Python Scripts\s*\|\s*(\d+)",
        "powershell_scripts": r"PowerShell Scripts\s*\|\s*(\d+)",
        "pattern_executors": r"Pattern Executors.*\|\s*(\d+)",
        "core_modules": r"Core Framework Modules\s*\|\s*(\d+)",
        "pattern_specs": r"Pattern Specifications\s*\|\s*(\d+)",
        "glossary_scripts": r"Glossary Automation\s*\|\s*(\d+)",
        "tests": r"Test Automation\s*\|\s*(\d+)",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            counts[key] = int(match.group(1))

    return counts


def generate_automation_index(
    repo_root: Path,
    output_path: Optional[Path] = None,
    report_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Generate a complete automation index

    Args:
        repo_root: Repository root path
        output_path: Where to write the index (optional)
        report_path: Path to AUTOMATION_COMPONENTS_REPORT.md for validation

    Returns:
        The generated index
    """
    print(f"Generating automation index for: {repo_root}")

    # Get git info
    git_info = get_git_info(repo_root)

    # Discover all automation units
    all_units = []

    print("  Discovering GitHub workflows...")
    all_units.extend(discover_github_workflows(repo_root))

    print("  Discovering scripts...")
    all_units.extend(discover_scripts(repo_root))

    # Sort by ID for consistency
    all_units.sort(key=lambda x: x["id"])

    # Re-number to ensure sequential IDs
    counters = {}
    for unit in all_units:
        prefix = unit["id"].rsplit("-", 1)[0]  # e.g., "AUTO-GH"
        counters[prefix] = counters.get(prefix, 0) + 1
        unit["id"] = f"{prefix}-{counters[prefix]:03d}"

    # Calculate summary
    by_type = {}
    for unit in all_units:
        t = unit["type"]
        by_type[t] = by_type.get(t, 0) + 1

    # Build index
    index = {
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository": {
            "name": repo_root.name,
            "root_path": str(repo_root),
            "git_sha": git_info.get("sha", ""),
            "branch": git_info.get("branch", ""),
        },
        "summary": {"total_units": len(all_units), "by_type": by_type},
        "automation_units": all_units,
    }

    # Validate against report if provided
    if report_path and report_path.exists():
        expected = parse_components_report(report_path)
        print(f"\n  Validation against report:")
        print(f"    Expected total: {sum(expected.values())}")
        print(f"    Discovered: {len(all_units)}")

        # Note: counts may differ due to filtering rules

    # Write output
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(index, f, indent=2)
        print(f"\n  Wrote index to: {output_path}")

    print(f"\n  Summary:")
    print(f"    Total units: {len(all_units)}")
    for t, count in sorted(by_type.items()):
        print(f"    - {t}: {count}")

    return index


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate automation_index.json from repository scan"
    )
    parser.add_argument(
        "--repo-root", type=Path, required=True, help="Repository root path"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".automation-health/automation_index.json"),
        help="Output path for index",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Path to AUTOMATION_COMPONENTS_REPORT.md for validation",
    )

    args = parser.parse_args()

    index = generate_automation_index(
        repo_root=args.repo_root.resolve(),
        output_path=args.output.resolve(),
        report_path=args.report.resolve() if args.report else None,
    )

    print(f"\nGenerated index with {len(index['automation_units'])} units")


if __name__ == "__main__":
    main()
