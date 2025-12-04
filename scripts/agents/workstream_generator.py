#!/usr/bin/env python3
"""
Workstream Generator Agent

Purpose: Automatically generate workstream JSON files from natural language descriptions.

This agent helps reduce manual JSON authoring errors and speeds up task creation by:
- Taking natural language task descriptions
- Generating compliant workstream JSON with proper structure
- Including FILES_SCOPE, constraints, acceptance criteria
- Validating against schema automatically
- Suggesting appropriate phase/workstream IDs

Usage:
    python scripts/agents/workstream_generator.py \
        --description "Add retry logic to executor with exponential backoff" \
        --phase PH-007 \
        --files "core/engine/executor.py,tests/engine/test_executor.py" \
        --output workstreams/ws-auto-001.json

    # Interactive mode
    python scripts/agents/workstream_generator.py --interactive

Status: TEMPLATE - Ready for implementation
Priority: HIGH
See: docs/AGENT_ANALYSIS_AND_RECOMMENDATIONS.md for full specification
"""
# DOC_ID: DOC-SCRIPT-AGENTS-WORKSTREAM-GENERATOR-266

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional


class WorkstreamGenerator:
    """Generate workstream JSON files from natural language descriptions."""

    def __init__(self, schema_path: Optional[Path] = None):
        """
        Initialize the workstream generator.

        Args:
            schema_path: Path to workstream schema for validation (optional)
        """
        self.schema_path = schema_path or Path("schema/workstream-bundle.schema.json")
        self.templates_dir = Path("workstreams/examples")

    def generate_workstream_id(self, phase: str) -> str:
        """
        Generate the next available workstream ID for a phase.

        Args:
            phase: Phase identifier (e.g., "PH-007")

        Returns:
            Workstream ID (e.g., "WS-007-001")
        """
        # TODO: Implement ID generation logic
        # - Scan existing workstreams for the phase
        # - Find the highest number
        # - Increment and format
        return f"{phase.replace('PH-', 'WS-')}-001"

    def parse_description(self, description: str) -> Dict:
        """
        Parse natural language description to extract key information.

        Args:
            description: Natural language task description

        Returns:
            Dictionary with extracted information (action, scope, constraints, etc.)
        """
        # TODO: Implement NLP or pattern matching
        # - Extract action verbs (add, refactor, fix, etc.)
        # - Identify affected components
        # - Extract constraints from keywords
        # - Suggest acceptance criteria

        return {
            "action": "implement",
            "component": "unknown",
            "constraints": [],
            "criteria": [],
        }

    def suggest_files_scope(
        self, description: str, files: Optional[List[str]] = None
    ) -> List[str]:
        """
        Suggest FILES_SCOPE based on description or use provided files.

        Args:
            description: Task description
            files: Explicitly provided file list

        Returns:
            List of file paths that should be in scope
        """
        if files:
            return files

        # TODO: Implement intelligent file suggestion
        # - Map components to typical file locations
        # - Include test files by convention
        # - Check if files exist

        return []

    def generate_constraints(self, description: str, parsed_info: Dict) -> List[str]:
        """
        Generate constraints based on description and repository policies.

        Args:
            description: Task description
            parsed_info: Parsed information from description

        Returns:
            List of constraint strings
        """
        # TODO: Implement constraint generation
        # - Extract explicit constraints from description
        # - Add standard constraints (e.g., "use section-based imports")
        # - Add context-specific constraints (e.g., for database changes)

        return [
            "Use section-based import patterns",
            "Add corresponding tests",
            "Follow existing code style",
        ]

    def generate_acceptance_criteria(
        self, description: str, parsed_info: Dict
    ) -> List[str]:
        """
        Generate acceptance criteria for the task.

        Args:
            description: Task description
            parsed_info: Parsed information from description

        Returns:
            List of acceptance criteria strings
        """
        # TODO: Implement criteria generation
        # - Standard criteria (tests pass)
        # - Feature-specific criteria
        # - Quality criteria (no deprecated imports, etc.)

        return [
            "All tests pass",
            "No deprecated import patterns",
            "Code follows repository conventions",
        ]

    def create_workstream_json(
        self,
        description: str,
        phase: str,
        files: Optional[List[str]] = None,
        ws_id: Optional[str] = None,
    ) -> Dict:
        """
        Create a complete workstream JSON structure.

        Args:
            description: Natural language task description
            phase: Phase identifier
            files: List of files in scope
            ws_id: Workstream ID (auto-generated if not provided)

        Returns:
            Complete workstream JSON dictionary
        """
        # Generate or use provided workstream ID
        workstream_id = ws_id or self.generate_workstream_id(phase)

        # Parse description
        parsed_info = self.parse_description(description)

        # Build workstream structure
        workstream = {
            "phase": phase,
            "workstream_id": workstream_id,
            "description": description,
            "metadata": {
                "priority": "normal",
                "complexity": "medium",
                "estimated_effort_hours": 4,
            },
            "files_scope": self.suggest_files_scope(description, files),
            "constraints": self.generate_constraints(description, parsed_info),
            "acceptance_criteria": self.generate_acceptance_criteria(
                description, parsed_info
            ),
            "steps": [
                {
                    "step_id": f"{workstream_id}-001",
                    "description": f"Implement: {description}",
                    "tool": "claude-code",
                    "parameters": {},
                },
                {
                    "step_id": f"{workstream_id}-002",
                    "description": "Run tests and validation",
                    "tool": "pytest",
                    "parameters": {},
                },
            ],
        }

        return workstream

    def validate_against_schema(self, workstream: Dict) -> bool:
        """
        Validate workstream JSON against schema.

        Args:
            workstream: Workstream dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        # TODO: Implement schema validation
        # - Load JSON schema
        # - Validate workstream structure
        # - Report validation errors

        print("⚠️  Schema validation not yet implemented")
        return True

    def save_workstream(self, workstream: Dict, output_path: Path) -> None:
        """
        Save workstream JSON to file.

        Args:
            workstream: Workstream dictionary
            output_path: Path to save JSON file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(workstream, f, indent=2)

        print(f"✅ Workstream saved to: {output_path}")

    def interactive_mode(self) -> None:
        """Run in interactive mode, prompting user for inputs."""
        print("🤖 Workstream Generator - Interactive Mode")
        print("=" * 50)

        # Gather inputs
        description = input("\nTask description: ").strip()
        phase = input("Phase (e.g., PH-007): ").strip()
        files_input = input("Files (comma-separated, or press Enter to skip): ").strip()

        files = [f.strip() for f in files_input.split(",")] if files_input else None

        # Generate workstream
        workstream = self.create_workstream_json(description, phase, files)

        # Show preview
        print("\n" + "=" * 50)
        print("Preview:")
        print("=" * 50)
        print(json.dumps(workstream, indent=2))

        # Confirm save
        save = input("\nSave this workstream? (y/n): ").strip().lower()
        if save == "y":
            ws_id = workstream["workstream_id"]
            output_path = Path(f"workstreams/{ws_id.lower()}.json")
            self.save_workstream(workstream, output_path)
        else:
            print("❌ Workstream not saved")


def main():
    """Main entry point for the workstream generator agent."""
    parser = argparse.ArgumentParser(
        description="Generate workstream JSON files from natural language descriptions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (recommended for first-time users)
  python scripts/agents/workstream_generator.py --interactive

  # Generate from command line
  python scripts/agents/workstream_generator.py \\
    --description "Add retry logic to executor with exponential backoff" \\
    --phase PH-007 \\
    --files "core/engine/executor.py,tests/engine/test_executor.py" \\
    --output workstreams/ws-007-042.json

  # Auto-generate output path
  python scripts/agents/workstream_generator.py \\
    --description "Fix import paths in error plugins" \\
    --phase PH-008
        """,
    )

    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Run in interactive mode"
    )

    parser.add_argument(
        "--description", "-d", help="Natural language description of the task"
    )

    parser.add_argument("--phase", "-p", help="Phase identifier (e.g., PH-007)")

    parser.add_argument("--files", "-f", help="Comma-separated list of files in scope")

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output path for workstream JSON (auto-generated if not provided)",
    )

    parser.add_argument(
        "--schema", type=Path, help="Path to workstream schema for validation"
    )

    args = parser.parse_args()

    # Initialize generator
    generator = WorkstreamGenerator(schema_path=args.schema)

    # Run in appropriate mode
    if args.interactive:
        generator.interactive_mode()
    else:
        # Validate required arguments for non-interactive mode
        if not args.description or not args.phase:
            parser.error(
                "--description and --phase are required in non-interactive mode"
            )

        # Parse files if provided
        files = [f.strip() for f in args.files.split(",")] if args.files else None

        # Generate workstream
        workstream = generator.create_workstream_json(
            description=args.description, phase=args.phase, files=files
        )

        # Determine output path
        if args.output:
            output_path = args.output
        else:
            ws_id = workstream["workstream_id"]
            output_path = Path(f"workstreams/{ws_id.lower()}.json")

        # Validate
        if generator.validate_against_schema(workstream):
            generator.save_workstream(workstream, output_path)
        else:
            print("❌ Validation failed. Workstream not saved.")
            sys.exit(1)


if __name__ == "__main__":
    main()
