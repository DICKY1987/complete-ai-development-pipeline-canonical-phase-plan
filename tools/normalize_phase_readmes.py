#!/usr/bin/env python
"""
Normalize phase README files to a canonical AI-optimized structure.

Usage:
    python normalize_phase_readmes.py --write
    python normalize_phase_readmes.py --dry-run

Behavior:
- Finds README.md files under directories whose name starts with "phase".
- Parses existing sections.
- Converts inline "**Purpose**: ..." into a "## Purpose" section.
- Rewrites each README with a canonical ordered section list.
- Preserves existing section content when possible.
- Adds TODO placeholders for missing sections.
- Creates README.md.bak before modifying (when --write is used).
"""

import argparse
import textwrap
from pathlib import Path
from typing import Dict, List, Tuple

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

# Simple default placeholders for new sections.
PLACEHOLDER_TEXT: Dict[str, str] = {
    "System Position": textwrap.dedent(
        """\
        upstream_phases:
          - [TODO: fill with upstream phase IDs, e.g. phase2_request_building]
        downstream_phases:
          - [TODO: fill with downstream phase IDs, e.g. phase4_routing]
        hard_blockers:
          - [TODO: list conditions that must be true before this phase can run]
        soft_dependencies:
          - [TODO: non-blocking dependencies or external syncs]
        """
    ),
    "Phase Contracts": textwrap.dedent(
        """\
        entry_requirements:
          required_files:
            - [TODO: list required input files]
          required_db_tables:
            - [TODO: list required DB tables, if any]
          required_state_flags:
            - [TODO: list required state flags / readiness signals]
        exit_artifacts:
          produced_files:
            - [TODO: list files produced by this phase]
          updated_db_tables:
            - [TODO: list DB tables updated by this phase]
          emitted_events:
            - [TODO: list events emitted to the orchestration/event bus]
        """
    ),
    "Phase Contents": "[TODO: describe folder layout and key subdirectories]\n",
    "Source of Truth": textwrap.dedent(
        """\
        authoritative_sources:
          - [TODO: list authoritative specs/code for this phase]
        derived_artifacts:
          - [TODO: list generated/derived files]
        do_not_edit_directly:
          - .state/**
          - .ledger/**
        """
    ),
    "Explicit Non-Responsibilities": textwrap.dedent(
        """\
        this_phase_does_not:
          - [TODO: list responsibilities explicitly out of scope for this phase]
        """
    ),
    "Invocation & Control": textwrap.dedent(
        """\
        invocation_mode:
          - [TODO: e.g. automatic_on_previous_phase_success | manual]
        entrypoints:
          cli:
            - [TODO: CLI commands to invoke this phase]
          python:
            - [TODO: Python entrypoints to invoke this phase]
        resumable: [TODO: true|false]
        idempotent: [TODO: true|false]
        retry_safe: [TODO: true|false]
        """
    ),
    "Observability": textwrap.dedent(
        """\
        log_streams:
          - [TODO: list log files/streams for this phase]
        metrics:
          - [TODO: list metrics exposed by this phase]
        health_checks:
          - [TODO: list health/diagnostic checks for this phase]
        """
    ),
    "AI Operational Rules": textwrap.dedent(
        """\
        ai_may_modify:
          - [TODO: list files/directories AI may modify in this phase]
        ai_must_not_modify:
          - schema/**
          - .state/**
          - .ledger/**
        ai_escalation_triggers:
          - [TODO: conditions that require human review or escalation]
        ai_safe_mode_conditions:
          - [TODO: conditions under which execution should be downgraded to safe mode]
        """
    ),
    "Test Coverage": "[TODO: summarize test coverage numbers, files, and gaps]\n",
    "Known Failure Modes": "[TODO: list typical failure modes and their impact]\n",
    "Readiness Model": textwrap.dedent(
        """\
        maturity_level: [TODO: DESIGN_ONLY | OPERATIONAL_BETA | PRODUCTION_READY]
        risk_profile:
          execution_risk: [TODO: LOW|MEDIUM|HIGH]
          data_loss_risk: [TODO: LOW|MEDIUM|HIGH]
          deadlock_risk: [TODO: LOW|MEDIUM|HIGH]
          external_dependency_risk: [TODO: LOW|MEDIUM|HIGH]
        production_gate: [TODO: DISALLOWED | ALLOWED_WITH_MONITORING | ALLOWED]
        """
    ),
    "Status": "[TODO: e.g. ✅ Complete (100%) or ⚠️ Partial (60%)]\n",
}


def find_phase_readmes(root: Path) -> List[Path]:
    """
    Find README.md files under directories whose name starts with 'phase'.
    """
    candidates: List[Path] = []
    for path in root.rglob("README.md"):
        # parent dir name should start with "phase"
        if path.parent.name.lower().startswith("phase"):
            candidates.append(path)
    return sorted(candidates)


def parse_readme_sections(content: str) -> Tuple[str, Dict[str, str], str]:
    """
    Parse a README.md into:
    - title: first level-1 heading line (e.g. "# Phase 3 – ...")
    - sections: mapping from section name (without "## ") to body text
    - leading_text: any text before the first "##" heading (used to extract Purpose)
    """
    lines = content.splitlines()
    title = ""
    sections: Dict[str, str] = {}
    leading_lines: List[str] = []

    current_section_name = None
    current_buf: List[str] = []

    # First pass: identify title and split by ## headings
    for i, line in enumerate(lines):
        if i == 0 and line.startswith("# "):
            title = line.strip()
            continue

        if line.startswith("## "):
            # Flush previous section
            if current_section_name is None:
                # This is the first section; everything seen so far is leading text
                leading_lines = current_buf
            else:
                sections[current_section_name] = "\n".join(current_buf).strip() + "\n"

            current_section_name = line[3:].strip()
            current_buf = []
        else:
            current_buf.append(line)

    # Flush last section or leading text
    if current_section_name is None:
        # No section headings at all
        leading_lines = current_buf
    else:
        sections[current_section_name] = "\n".join(current_buf).strip() + "\n"

    leading_text = "\n".join(leading_lines).strip() + ("\n" if leading_lines else "")

    return title, sections, leading_text


def extract_or_build_purpose(leading_text: str, sections: Dict[str, str]) -> str:
    """
    Build the "Purpose" section body.

    Priority:
    1. Existing "Purpose" section (if present)
    2. A line starting with "**Purpose**:" in leading_text
    3. Empty placeholder
    """
    if "Purpose" in sections and sections["Purpose"].strip():
        return sections["Purpose"].rstrip() + "\n"

    purpose_lines = []
    for line in leading_text.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("**purpose**:"):
            purpose_lines.append(
                stripped.lstrip("*").rstrip("*").split(":", 1)[1].strip()
            )
        elif stripped.lower().startswith("purpose:"):
            purpose_lines.append(stripped.split(":", 1)[1].strip())

    if purpose_lines:
        return "\n".join(purpose_lines).strip() + "\n"

    # Fallback placeholder
    return "[TODO: describe the purpose of this phase]\n"


def build_normalized_readme(
    title: str,
    sections: Dict[str, str],
    leading_text: str,
) -> str:
    """
    Construct a normalized README content string using the canonical section order.
    """
    lines: List[str] = []

    # Keep the original title (or a default if missing)
    if not title:
        title = "# [TODO: Phase Title]"
    lines.append(title)
    lines.append("")  # blank line after title

    # Build/override Purpose
    purpose_body = extract_or_build_purpose(leading_text, sections)
    lines.append("## Purpose")
    lines.append("")
    lines.append(purpose_body.rstrip())
    lines.append("")

    # Ensure we don't re-use any previous "Purpose" section
    normalized_sections = dict(sections)
    normalized_sections.pop("Purpose", None)

    # For every canonical section beyond Purpose
    for name in CANONICAL_SECTION_ORDER:
        if name == "Purpose":
            continue

        lines.append(f"## {name}")
        lines.append("")

        if name in normalized_sections and normalized_sections[name].strip():
            body = normalized_sections[name].rstrip()
        else:
            body = PLACEHOLDER_TEXT.get(name, "[TODO: fill this section]\n").rstrip()

        lines.append(body)
        lines.append("")

    # Strip trailing blank lines
    while lines and not lines[-1].strip():
        lines.pop()

    return "\n".join(lines) + "\n"


def process_readme(path: Path, write: bool = False) -> None:
    original_content = path.read_text(encoding="utf-8")
    title, sections, leading_text = parse_readme_sections(original_content)
    new_content = build_normalized_readme(title, sections, leading_text)

    if new_content == original_content:
        print(f"[SKIP] {path} (already normalized)")
        return

    print(f"[UPDATE] {path}")
    if write:
        backup = path.with_suffix(path.suffix + ".bak")
        if not backup.exists():
            backup.write_text(original_content, encoding="utf-8")
            print(f"        Backup created: {backup}")
        else:
            print(f"        Backup already exists: {backup}")
        path.write_text(new_content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Normalize phase README files to a canonical AI-optimized structure."
    )
    parser.add_argument(
        "--root",
        type=str,
        default=".",
        help="Repository root (default: current directory)",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Actually rewrite README files (default: dry-run)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Explicit dry-run mode (overrides --write)",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    write = args.write and not args.dry_run

    print(f"Scanning for phase READMEs under: {root}")
    readmes = find_phase_readmes(root)
    if not readmes:
        print("No phase README.md files found.")
        return

    for readme in readmes:
        process_readme(readme, write=write)

    if not write:
        print("\nDry-run complete. Re-run with --write to apply changes.")


if __name__ == "__main__":
    main()
