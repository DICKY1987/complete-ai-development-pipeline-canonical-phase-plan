#!/usr/bin/env python
"""
PAT-CHECK-README-001

Validate phase README.md files against the AI-optimized README contract.

- Parses README.md under phase*/ directories
- Builds a JSON "view" with sections keyed by heading
- Validates required sections and some structural rules
- Checks that canonical sections appear in canonical order
- Emits a JSON report file listing PASS/FAIL and reasons

Usage:
    python tools/pat_check_readme_001.py --root . --report .reports/pat_check_readme_001.json

Requires:
    pip install jsonschema
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from jsonschema import Draft7Validator

CANONICAL_SECTION_ORDER: List[str] = [
    "Purpose",
    "System Position",
    "Phase Contracts",
    "Phase Contents",
    "Current Components",
    "Main Operations",
    "Source of Truth",
    "Explicit Non-Responsibilities",
    "Invocation & Control",
    "Observability",
    "AI Operational Rules",
    "Test Coverage",
    "Known Failure Modes",
    "Readiness Model",
    "Status",
]

# JSON Schema for sections (not full markdown, just the view)
README_SCHEMA: Dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "AI Optimized Phase README Schema",
    "type": "object",
    "required": [
        "Purpose",
        "System Position",
        "Phase Contracts",
        "Current Components",
        "Main Operations",
        "Source of Truth",
        "Explicit Non-Responsibilities",
        "Invocation & Control",
        "Observability",
        "AI Operational Rules",
        "Test Coverage",
        "Known Failure Modes",
        "Readiness Model",
        "Status",
    ],
    "properties": {
        "Purpose": {"type": "string", "minLength": 1},
        "System Position": {"type": "string", "minLength": 1},
        "Phase Contracts": {"type": "string", "minLength": 1},
        "Current Components": {"type": "string", "minLength": 1},
        "Main Operations": {"type": "string", "minLength": 1},
        "Source of Truth": {"type": "string", "minLength": 1},
        "Explicit Non-Responsibilities": {"type": "string", "minLength": 1},
        "Invocation & Control": {"type": "string", "minLength": 1},
        "Observability": {"type": "string", "minLength": 1},
        "AI Operational Rules": {"type": "string", "minLength": 1},
        "Test Coverage": {"type": "string", "minLength": 1},
        "Known Failure Modes": {"type": "string", "minLength": 1},
        "Readiness Model": {"type": "string", "minLength": 1},
        "Status": {"type": "string", "minLength": 1},
    },
    "additionalProperties": True,
}


def find_phase_readmes(root: Path) -> List[Path]:
    """
    Find README.md files under directories whose name starts with 'phase'.
    """
    candidates: List[Path] = []
    for path in root.rglob("README.md"):
        if path.parent.name.lower().startswith("phase"):
            candidates.append(path)
    return sorted(candidates)


def parse_readme_sections(content: str) -> Tuple[str, Dict[str, str], List[str]]:
    """
    Parse markdown README into:
    - title: first level-1 heading (# ...)
    - sections: mapping from section name (without ##) to body text
    - order: list of section names in the order they appear
    """
    lines = content.splitlines()
    title = ""
    sections: Dict[str, str] = {}
    order: List[str] = []

    current_section = None
    buf: List[str] = []

    for i, line in enumerate(lines):
        if i == 0 and line.startswith("# "):
            title = line[2:].strip()
            continue

        if line.startswith("## "):
            # flush previous section
            if current_section is not None:
                sections[current_section] = "\n".join(buf).strip() + (
                    "\n" if buf else ""
                )
            current_section = line[3:].strip()
            order.append(current_section)
            buf = []
        else:
            buf.append(line)

    if current_section is not None:
        sections[current_section] = "\n".join(buf).strip() + ("\n" if buf else "")

    return title, sections, order


def has_todo_markers(text: str) -> bool:
    """
    Detects if a section still contains placeholder TODO markers.
    """
    lowered = text.lower()
    return "[todo" in lowered or "todo:" in lowered


def check_section_order(order: List[str]) -> List[Dict[str, Any]]:
    """
    Compare the actual README section order to the canonical order and
    return a list of ordering issues (if any).
    """
    issues: List[Dict[str, Any]] = []

    # Build a mapping of section -> index in actual order
    index_map = {name: idx for idx, name in enumerate(order)}

    # Only consider canonical sections that actually appear
    present_canonical = [s for s in CANONICAL_SECTION_ORDER if s in index_map]

    # If fewer than 2 canonical sections appear, no meaningful ordering check
    if len(present_canonical) < 2:
        return issues

    # Check that indices are strictly increasing w.r.t canonical order
    last_idx = -1
    last_name = None
    for name in present_canonical:
        idx = index_map[name]
        if idx < last_idx:
            issues.append(
                {
                    "kind": "ordering_error",
                    "message": (
                        f"Section '{name}' appears before '{last_name}' "
                        "but should come after it in canonical order."
                    ),
                    "section": name,
                    "previous_section": last_name,
                }
            )
        else:
            last_idx = idx
            last_name = name

    return issues


def validate_readme(path: Path) -> Dict[str, Any]:
    """
    Validate a single README and return a structured result dict.
    """
    content = path.read_text(encoding="utf-8")
    title, sections, order = parse_readme_sections(content)
    view = {
        "path": str(path),
        "title": title,
        "sections": sections,
        "order": order,
    }

    sections_obj = sections

    validator = Draft7Validator(README_SCHEMA)
    errors = list(validator.iter_errors(sections_obj))

    issues: List[Dict[str, Any]] = []

    # Schema-level issues
    for e in errors:
        issues.append(
            {
                "kind": "schema_error",
                "message": e.message,
                "path": list(e.path),
            }
        )

    # 1) Ensure canonical sections are present
    for required in CANONICAL_SECTION_ORDER:
        if required not in sections_obj:
            issues.append(
                {
                    "kind": "missing_section",
                    "section": required,
                    "message": f"Section '{required}' is missing.",
                }
            )

    # 2) Check for TODO markers in critical sections
    for name in CANONICAL_SECTION_ORDER:
        body = sections_obj.get(name, "")
        if body and has_todo_markers(body):
            issues.append(
                {
                    "kind": "todo_placeholder",
                    "section": name,
                    "message": f"Section '{name}' still contains TODO placeholders.",
                }
            )

    # 3) Check ordering
    ordering_issues = check_section_order(order)
    issues.extend(ordering_issues)

    status = "PASS" if not issues else "FAIL"

    return {
        "path": str(path),
        "title": title,
        "status": status,
        "issue_count": len(issues),
        "issues": issues,
        "view": view,  # optional, useful for debugging / agents
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PAT-CHECK-README-001: validate phase README files."
    )
    parser.add_argument(
        "--root",
        type=str,
        default=".",
        help="Repository root (default: current directory)",
    )
    parser.add_argument(
        "--report",
        type=str,
        default=".reports/pat_check_readme_001.json",
        help="Path to write JSON report (default: .reports/pat_check_readme_001.json)",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)

    readmes = find_phase_readmes(root)
    if not readmes:
        print(f"No phase README.md files found under {root}")
        return

    results: List[Dict[str, Any]] = []
    overall_fail = False

    for readme in readmes:
        result = validate_readme(readme)
        results.append(result)
        status = result["status"]
        print(f"[{status}] {readme}")
        if status == "FAIL":
            overall_fail = True
            for issue in result["issues"]:
                kind = issue.get("kind")
                msg = issue.get("message")
                section = issue.get("section", "")
                if section:
                    print(f"    - {kind} in '{section}': {msg}")
                else:
                    print(f"    - {kind}: {msg}")

    report = {
        "check_id": "PAT-CHECK-README-001",
        "root": str(root),
        "results": results,
    }

    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nReport written to: {report_path}")

    if overall_fail:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
