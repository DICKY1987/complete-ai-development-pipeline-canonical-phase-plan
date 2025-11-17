#!/usr/bin/env python3
"""
Convert OpenSpec proposals to workstream bundles.

This bridge script parses OpenSpec change proposals and generates
workstream JSON bundles conforming to schema/workstream.schema.json.

Usage:
    python scripts/spec_to_workstream.py --change-id test-001
    python scripts/spec_to_workstream.py --change-id test-001 --output workstreams/my-ws.json
    python scripts/spec_to_workstream.py --list
    python scripts/spec_to_workstream.py --interactive
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Repository root
REPO_ROOT = Path(__file__).parent.parent.resolve()
OPENSPEC_DIR = REPO_ROOT / "openspec"
CHANGES_DIR = OPENSPEC_DIR / "changes"
WORKSTREAMS_DIR = REPO_ROOT / "workstreams"
SCHEMA_PATH = REPO_ROOT / "schema" / "workstream.schema.json"


class OpenSpecParser:
    """Parse OpenSpec change proposals and extract structured data."""

    def __init__(self, change_id: str):
        self.change_id = change_id
        self.change_dir = CHANGES_DIR / change_id

        if not self.change_dir.exists():
            raise ValueError(f"Change directory not found: {self.change_dir}")

    def parse(self) -> Dict[str, Any]:
        """Parse OpenSpec change and return structured data."""
        proposal = self._parse_proposal()
        tasks = self._parse_tasks()
        specs = self._parse_specs()

        return {
            "change_id": self.change_id,
            "proposal": proposal,
            "tasks": tasks,
            "specs": specs,
        }

    def _parse_proposal(self) -> Dict[str, Any]:
        """Parse proposal.md for metadata and description."""
        proposal_path = self.change_dir / "proposal.md"

        if not proposal_path.exists():
            return {"title": self.change_id, "description": ""}

        content = proposal_path.read_text(encoding="utf-8")

        # Extract frontmatter
        title = self._extract_frontmatter_title(content)

        # Extract description (everything after frontmatter and first heading)
        description = self._extract_description(content)

        return {
            "title": title or self.change_id,
            "description": description,
        }

    def _parse_tasks(self) -> List[str]:
        """Parse tasks.md for task list."""
        tasks_path = self.change_dir / "tasks.md"

        if not tasks_path.exists():
            return []

        content = tasks_path.read_text(encoding="utf-8")

        # Extract markdown task list items
        task_pattern = re.compile(r"^[-*]\s+\[[ x]\]\s+(.+)$", re.MULTILINE)
        tasks = task_pattern.findall(content)

        return [task.strip() for task in tasks if task.strip()]

    def _parse_specs(self) -> List[Dict[str, Any]]:
        """Parse spec deltas for requirements and scenarios."""
        specs = []

        # Look for spec files in change directory
        for spec_file in self.change_dir.glob("**/*.md"):
            if spec_file.name in ["proposal.md", "tasks.md"]:
                continue

            spec_data = self._parse_spec_file(spec_file)
            if spec_data:
                specs.append(spec_data)

        return specs

    def _parse_spec_file(self, spec_path: Path) -> Optional[Dict[str, Any]]:
        """Parse a single spec file for requirements and scenarios."""
        content = spec_path.read_text(encoding="utf-8")

        requirements = []

        # Extract requirements with SHALL/MUST keywords
        req_pattern = re.compile(
            r"###\s+Requirement:\s+(.+?)\n(.+?)(?=###|##|\Z)",
            re.DOTALL
        )

        for match in req_pattern.finditer(content):
            req_name = match.group(1).strip()
            req_body = match.group(2).strip()

            # Extract scenarios
            scenario_pattern = re.compile(
                r"####\s+Scenario:\s+(.+?)\n(.+?)(?=####|###|##|\Z)",
                re.DOTALL
            )

            scenarios = []
            for scenario_match in scenario_pattern.finditer(req_body):
                scenario_name = scenario_match.group(1).strip()
                scenario_body = scenario_match.group(2).strip()
                scenarios.append({
                    "name": scenario_name,
                    "body": scenario_body
                })

            requirements.append({
                "name": req_name,
                "body": req_body,
                "scenarios": scenarios
            })

        if not requirements:
            return None

        return {
            "file": str(spec_path.relative_to(self.change_dir)),
            "requirements": requirements
        }

    def _extract_frontmatter_title(self, content: str) -> Optional[str]:
        """Extract title from YAML frontmatter."""
        frontmatter_pattern = re.compile(r"^---\n(.+?)\n---", re.DOTALL)
        match = frontmatter_pattern.search(content)

        if match:
            frontmatter = match.group(1)
            title_match = re.search(r"^title:\s*(.+)$", frontmatter, re.MULTILINE)
            if title_match:
                return title_match.group(1).strip()

        return None

    def _extract_description(self, content: str) -> str:
        """Extract description from content."""
        # Remove frontmatter
        content = re.sub(r"^---\n.+?\n---\n", "", content, flags=re.DOTALL)

        # Remove first heading
        content = re.sub(r"^#\s+.+\n", "", content, flags=re.MULTILINE)

        return content.strip()


class WorkstreamGenerator:
    """Generate workstream bundles from OpenSpec data."""

    def __init__(self, spec_data: Dict[str, Any]):
        self.spec_data = spec_data

    def generate(self, ws_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate workstream bundle JSON."""
        change_id = self.spec_data["change_id"]
        proposal = self.spec_data["proposal"]
        tasks = self.spec_data["tasks"]

        # Generate workstream ID if not provided
        if not ws_id:
            ws_id = self._generate_ws_id(proposal["title"])

        # Extract file scope from tasks and specs
        files_scope = self._extract_files_scope()
        files_create = self._extract_files_create()

        # Generate acceptance tests from scenarios
        acceptance_tests = self._generate_acceptance_tests()

        bundle = {
            "id": ws_id,
            "openspec_change": change_id,
            "ccpm_issue": 0,  # Placeholder, update manually or via automation
            "gate": 1,
            "files_scope": files_scope or ["src/"],  # Default scope
            "files_create": files_create,
            "tasks": tasks or [proposal["description"]],
            "acceptance_tests": acceptance_tests,
            "depends_on": [],
            "tool": "aider",
            "circuit_breaker": {
                "max_attempts": 5,
                "max_error_repeats": 3,
                "oscillation_threshold": 2
            },
            "metadata": {
                "owner": "generated-from-openspec",
                "openspec_title": proposal["title"],
                "generated_by": "spec_to_workstream.py",
                "notes": f"Auto-generated from OpenSpec change {change_id}"
            }
        }

        return bundle

    def _generate_ws_id(self, title: str) -> str:
        """Generate workstream ID from title."""
        # Convert title to lowercase kebab-case
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower())
        slug = slug.strip("-")

        return f"ws-{slug}"

    def _extract_files_scope(self) -> List[str]:
        """Extract file paths mentioned in tasks and specs."""
        files = set()

        # Extract from task descriptions
        for task in self.spec_data["tasks"]:
            # Look for file patterns in task text
            file_patterns = re.findall(r"[\w/.-]+\.(py|json|md|yaml|yml|txt|sh|ps1)", task)
            files.update(file_patterns)

        # Extract from spec requirements
        for spec in self.spec_data.get("specs", []):
            for req in spec.get("requirements", []):
                file_patterns = re.findall(
                    r"[\w/.-]+\.(py|json|md|yaml|yml|txt|sh|ps1)",
                    req["body"]
                )
                files.update(file_patterns)

        return sorted(files)

    def _extract_files_create(self) -> List[str]:
        """Extract files to be created from tasks."""
        files = set()

        # Look for "create" or "add" keywords in tasks
        create_pattern = re.compile(r"(?:create|add)\s+[\w/.-]+\.(py|json|md|yaml|yml|txt|sh|ps1)", re.IGNORECASE)

        for task in self.spec_data["tasks"]:
            matches = create_pattern.findall(task)
            files.update(matches)

        return sorted(files)

    def _generate_acceptance_tests(self) -> List[str]:
        """Generate acceptance tests from scenarios."""
        tests = []

        for spec in self.spec_data.get("specs", []):
            for req in spec.get("requirements", []):
                for scenario in req.get("scenarios", []):
                    # Convert scenario to test description
                    test_desc = f"Verify: {scenario['name']}"
                    tests.append(test_desc)

        return tests


def list_changes() -> List[Tuple[str, str]]:
    """List all available OpenSpec changes."""
    changes = []

    if not CHANGES_DIR.exists():
        return changes

    for change_dir in sorted(CHANGES_DIR.iterdir()):
        if not change_dir.is_dir():
            continue

        change_id = change_dir.name
        proposal_path = change_dir / "proposal.md"

        title = change_id
        if proposal_path.exists():
            try:
                parser = OpenSpecParser(change_id)
                data = parser.parse()
                title = data["proposal"]["title"]
            except Exception:
                pass

        changes.append((change_id, title))

    return changes


def interactive_mode():
    """Interactive mode for selecting changes and generating workstreams."""
    print("OpenSpec to Workstream Converter")
    print("=" * 50)
    print()

    # List available changes
    changes = list_changes()

    if not changes:
        print("No OpenSpec changes found in openspec/changes/")
        return 1

    print("Available changes:")
    for i, (change_id, title) in enumerate(changes, 1):
        print(f"  {i}. {change_id} - {title}")
    print()

    # Select change
    while True:
        try:
            selection = input("Select change number (or 'q' to quit): ").strip()
            if selection.lower() == 'q':
                return 0

            idx = int(selection) - 1
            if 0 <= idx < len(changes):
                change_id, title = changes[idx]
                break
            else:
                print("Invalid selection. Try again.")
        except (ValueError, KeyboardInterrupt):
            print("\nCancelled.")
            return 1

    print()
    print(f"Selected: {change_id} - {title}")
    print()

    # Parse change
    try:
        parser = OpenSpecParser(change_id)
        spec_data = parser.parse()
    except Exception as e:
        print(f"Error parsing change: {e}")
        return 1

    # Generate workstream
    generator = WorkstreamGenerator(spec_data)
    bundle = generator.generate()

    print("Generated workstream bundle:")
    print("-" * 50)
    print(json.dumps(bundle, indent=2))
    print("-" * 50)
    print()

    # Ask to save
    default_filename = f"{bundle['id']}.json"
    save = input(f"Save to workstreams/{default_filename}? [Y/n]: ").strip().lower()

    if save in ["", "y", "yes"]:
        output_path = WORKSTREAMS_DIR / default_filename
        output_path.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
        print(f"✓ Saved to {output_path}")
        print()
        print("Next steps:")
        print(f"  1. Review and edit {output_path}")
        print(f"  2. Validate: python scripts/validate_workstreams.py")
        print(f"  3. Run: python scripts/run_workstream.py --ws-id {bundle['id']}")
        return 0
    else:
        print("Not saved.")
        return 0


def main():
    parser = argparse.ArgumentParser(
        description="Convert OpenSpec proposals to workstream bundles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--change-id",
        help="OpenSpec change ID to convert"
    )
    parser.add_argument(
        "--output",
        help="Output workstream JSON path (default: workstreams/<ws-id>.json)"
    )
    parser.add_argument(
        "--ws-id",
        help="Override workstream ID (default: auto-generated from title)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available OpenSpec changes"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Interactive mode for selecting and converting changes"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print bundle JSON without saving"
    )

    args = parser.parse_args()

    # List mode
    if args.list:
        changes = list_changes()
        if not changes:
            print("No OpenSpec changes found in openspec/changes/")
            return 1

        print("Available OpenSpec changes:")
        for change_id, title in changes:
            print(f"  {change_id:20s} {title}")
        return 0

    # Interactive mode
    if args.interactive:
        return interactive_mode()

    # Conversion mode
    if not args.change_id:
        parser.error("--change-id is required (or use --interactive)")

    try:
        # Parse OpenSpec change
        openspec_parser = OpenSpecParser(args.change_id)
        spec_data = openspec_parser.parse()

        # Generate workstream bundle
        generator = WorkstreamGenerator(spec_data)
        bundle = generator.generate(ws_id=args.ws_id)

        # Determine output path
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = WORKSTREAMS_DIR / f"{bundle['id']}.json"

        # Output or save
        bundle_json = json.dumps(bundle, indent=2) + "\n"

        if args.dry_run:
            print(bundle_json)
        else:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(bundle_json, encoding="utf-8")
            print(f"✓ Generated workstream: {output_path}")
            print()
            print("Next steps:")
            print(f"  1. Review and edit {output_path}")
            print(f"  2. Validate: python scripts/validate_workstreams.py")
            print(f"  3. Run: python scripts/run_workstream.py --ws-id {bundle['id']}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
