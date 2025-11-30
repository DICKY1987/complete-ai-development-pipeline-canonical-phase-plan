#!/usr/bin/env python3
"""
Generate implementation location mappings for all specialized terms.

This script scans Python files for class/function definitions, YAML/JSON files
for configuration, and creates a mapping of all 47 specialized terms to their
exact implementation locations (file:line).

Usage:
    python scripts/generate_implementation_map.py [--output DOCS/IMPLEMENTATION_LOCATIONS.md]
"""
# DOC_ID: DOC-PAT-GENERATION-GENERATE-IMPLEMENTATION-MAP-620

import argparse
import ast
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
from datetime import datetime
from dataclasses import dataclass


@dataclass
class TermLocation:
    """Represents a single location where a term is implemented."""
    file_path: str
    line_number: int
    location_type: str  # 'class', 'function', 'schema', 'config', 'doc'
    description: str
    context: str = ""  # Additional context (e.g., method name, parent class)


class ImplementationMapper:
    """Generate implementation location mappings."""

    # Define all 47 specialized terms
    TERMS = {
        "Core Engine": [
            "Workstream", "Step", "Bundle", "Orchestrator", "Executor",
            "Scheduler", "Tool Profile", "Circuit Breaker", "Retry Logic",
            "Recovery Strategy", "Timeout Handling", "Dependency Resolution"
        ],
        "Error Detection": [
            "Error Engine", "Error Plugin", "Detection Rule", "Error State Machine",
            "Fix Strategy", "Incremental Detection", "File Hash Cache",
            "Error Escalation", "Plugin Manifest", "Error Context"
        ],
        "Specifications": [
            "OpenSpec", "Specification Index", "Spec Resolver", "Spec Guard",
            "Spec Patcher", "Change Proposal", "Spec Bridge", "URI Resolution"
        ],
        "State Management": [
            "Pipeline Database", "Worktree Management", "State Transition",
            "Checkpoint", "Archive", "CRUD Operations", "Bundle Loading",
            "Sidecar Metadata"
        ],
        "Integrations": [
            "AIM Bridge", "CCPM Integration", "Aider Adapter", "Git Adapter",
            "Test Adapter", "Tool Registry", "Profile Matching",
            "Compensation Action", "Rollback Strategy"
        ]
    }

    # Map terms to search patterns
    TERM_PATTERNS = {
        # Core Engine
        "Workstream": ["workstream", "Workstream"],
        "Step": ["Step", "step"],
        "Bundle": ["Bundle", "bundle"],
        "Orchestrator": ["Orchestrator", "orchestrator"],
        "Executor": ["Executor", "executor"],
        "Scheduler": ["Scheduler", "scheduler"],
        "Tool Profile": ["tool_profile", "ToolProfile", "profile"],
        "Circuit Breaker": ["CircuitBreaker", "circuit_breaker"],
        "Retry Logic": ["retry", "Retry"],
        "Recovery Strategy": ["Recovery", "recovery"],
        "Timeout Handling": ["timeout", "Timeout"],
        "Dependency Resolution": ["dependency", "dependencies", "resolve_dependencies"],

        # Error Detection
        "Error Engine": ["ErrorEngine", "error_engine"],
        "Error Plugin": ["ErrorPlugin", "error_plugin", "Plugin"],
        "Detection Rule": ["detection", "rule"],
        "Error State Machine": ["StateMachine", "state_machine"],
        "Fix Strategy": ["fix", "Fix"],
        "Incremental Detection": ["incremental", "hash"],
        "File Hash Cache": ["hash_cache", "file_hash"],
        "Error Escalation": ["escalate", "escalation"],
        "Plugin Manifest": ["manifest"],
        "Error Context": ["ErrorContext", "error_context"],

        # Specifications
        "OpenSpec": ["openspec", "OpenSpec"],
        "Specification Index": ["spec_index", "indexer"],
        "Spec Resolver": ["resolver", "Resolver"],
        "Spec Guard": ["guard", "Guard"],
        "Spec Patcher": ["patcher", "Patcher"],
        "Change Proposal": ["proposal", "change"],
        "Spec Bridge": ["bridge", "Bridge"],
        "URI Resolution": ["resolve_uri", "parse_uri"],

        # State Management
        "Pipeline Database": ["init_db", "database", "db.py"],
        "Worktree Management": ["worktree", "Worktree"],
        "State Transition": ["transition", "update_status"],
        "Checkpoint": ["checkpoint", "Checkpoint"],
        "Archive": ["archive", "Archive"],
        "CRUD Operations": ["crud", "create_", "get_", "update_", "delete_"],
        "Bundle Loading": ["load_bundle", "validate_bundle"],
        "Sidecar Metadata": ["sidecar", "Sidecar"],

        # Integrations
        "AIM Bridge": ["aim/bridge", "AIMBridge"],
        "CCPM Integration": ["ccpm", "CCPM"],
        "Aider Adapter": ["aider", "Aider"],
        "Git Adapter": ["git_adapter", "GitAdapter"],
        "Test Adapter": ["test_adapter", "TestAdapter"],
        "Tool Registry": ["registry", "Registry"],
        "Profile Matching": ["match_profile", "select_profile"],
        "Compensation Action": ["compensate", "saga"],
        "Rollback Strategy": ["rollback", "Rollback"]
    }

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.term_locations: Dict[str, List[TermLocation]] = {
            term: [] for category in self.TERMS.values() for term in category
        }

    def scan_python_files(self) -> None:
        """Scan Python files for class and function definitions."""
        print("Scanning Python files...")

        python_files = list(self.repo_root.rglob("*.py"))
        # Exclude test files and virtual environments
        python_files = [
            f for f in python_files
            if '.venv' not in str(f) and '__pycache__' not in str(f)
            and 'sandbox_repos' not in str(f)
        ]

        for py_file in python_files:
            try:
                self._analyze_python_file(py_file)
            except Exception as e:
                print(f"Warning: Could not analyze {py_file}: {e}")

    def _analyze_python_file(self, py_file: Path) -> None:
        """Analyze a single Python file using AST."""
        try:
            content = py_file.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(py_file))
            relative_path = py_file.relative_to(self.repo_root)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    line_number = node.lineno

                    # Match against term patterns
                    for term, patterns in self.TERM_PATTERNS.items():
                        if any(pattern.lower() in class_name.lower() for pattern in patterns):
                            self.term_locations[term].append(TermLocation(
                                file_path=str(relative_path),
                                line_number=line_number,
                                location_type="class",
                                description=f"Class definition: {class_name}"
                            ))

                elif isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    line_number = node.lineno

                    # Match against term patterns
                    for term, patterns in self.TERM_PATTERNS.items():
                        if any(pattern.lower() in func_name.lower() for pattern in patterns):
                            self.term_locations[term].append(TermLocation(
                                file_path=str(relative_path),
                                line_number=line_number,
                                location_type="function",
                                description=f"Function: {func_name}()"
                            ))

        except SyntaxError:
            pass  # Skip files with syntax errors

    def scan_config_files(self) -> None:
        """Scan YAML and JSON configuration files."""
        print("Scanning configuration files...")

        config_patterns = {
            "Tool Profile": ["invoke.yaml", "tool_profiles.yaml"],
            "Circuit Breaker": ["circuit_breaker.yaml"],
            "Plugin Manifest": ["manifest.json"],
        }

        for term, filenames in config_patterns.items():
            for filename in filenames:
                config_files = list(self.repo_root.rglob(filename))
                for config_file in config_files:
                    if '.venv' in str(config_file) or 'sandbox_repos' in str(config_file):
                        continue

                    relative_path = config_file.relative_to(self.repo_root)
                    self.term_locations[term].append(TermLocation(
                        file_path=str(relative_path),
                        line_number=1,
                        location_type="config",
                        description=f"Configuration file: {filename}"
                    ))

    def scan_schema_files(self) -> None:
        """Scan JSON schema files."""
        print("Scanning schema files...")

        schema_patterns = {
            "Workstream": ["workstream.schema.json"],
            "Step": ["workstream.schema.json"],
            "Bundle": ["bundle.schema.json"],
            "Sidecar Metadata": ["sidecar.schema.json"],
            "Pipeline Database": ["database.sql"],
        }

        for term, filenames in schema_patterns.items():
            for filename in filenames:
                schema_files = list(self.repo_root.rglob(filename))
                for schema_file in schema_files:
                    if '.venv' in str(schema_file) or 'sandbox_repos' in str(schema_file):
                        continue

                    relative_path = schema_file.relative_to(self.repo_root)
                    self.term_locations[term].append(TermLocation(
                        file_path=str(relative_path),
                        line_number=1,
                        location_type="schema",
                        description=f"Schema definition: {filename}"
                    ))

    def scan_documentation(self) -> None:
        """Scan documentation files for term references."""
        print("Scanning documentation files...")

        doc_patterns = {
            "Orchestrator": ["ARCHITECTURE.md"],
            "Error Engine": ["plugin-ecosystem-summary.md"],
            "Error State Machine": ["state_machine.md"],
            "OpenSpec": ["openspec_bridge.md", "QUICKSTART_OPENSPEC.md"],
            "Workstream": ["workstream_authoring_guide.md"],
        }

        for term, filenames in doc_patterns.items():
            for filename in filenames:
                doc_files = list(self.repo_root.rglob(filename))
                for doc_file in doc_files:
                    relative_path = doc_file.relative_to(self.repo_root)
                    self.term_locations[term].append(TermLocation(
                        file_path=str(relative_path),
                        line_number=1,
                        location_type="doc",
                        description=f"Documentation: {filename}"
                    ))

    def generate_markdown(self, output_path: Path) -> None:
        """Generate the implementation locations markdown file."""
        print(f"Generating implementation map at {output_path}...")

        lines = [
            "# Implementation Locations - AI Development Pipeline",
            "",
            f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}  ",
            "**Purpose**: Map every specialized term to exact code locations (file:line)  ",
            "**Auto-Generated**: By `scripts/generate_implementation_map.py`  ",
            "",
            "> **Usage**: AI agents can use this to quickly locate implementations of any specialized term.  ",
            "> **Format**: `Term → File:Line → Description`",
            "",
            "---",
            "",
            "## 📋 Quick Lookup Table",
            "",
            "| Term | Primary Location | Category | Locations Found |",
            "|------|------------------|----------|-----------------|"
        ]

        # Build quick lookup table
        term_number = 1
        for category, terms in self.TERMS.items():
            for term in terms:
                locations = self.term_locations[term]
                if locations:
                    primary = locations[0]
                    location_str = f"`{primary.file_path}:{primary.line_number}`"
                else:
                    location_str = "*Not found*"

                lines.append(
                    f"| [{term}](#{term_number}-{term.lower().replace(' ', '-')}) | "
                    f"{location_str} | {category} | {len(locations)} |"
                )
                term_number += 1

        lines.extend(["", "---", ""])

        # Add detailed mappings by category
        term_number = 1
        for category, terms in self.TERMS.items():
            lines.append(f"## {category}")
            lines.append("")

            for term in terms:
                lines.append(f"### {term_number}. {term}")
                lines.append("")

                locations = self.term_locations[term]

                if locations:
                    lines.append("| Location | Type | Description |")
                    lines.append("|----------|------|-------------|")

                    for loc in sorted(locations, key=lambda l: (l.location_type, l.file_path)):
                        lines.append(
                            f"| `{loc.file_path}:{loc.line_number}` | "
                            f"{loc.location_type.title()} | {loc.description} |"
                        )

                    lines.append("")
                else:
                    lines.append("*No implementation locations found for this term.*")
                    lines.append("")

                lines.append("---")
                lines.append("")
                term_number += 1

        # Add statistics
        lines.append("## 📊 Statistics")
        lines.append("")
        lines.append(f"**Total Terms**: {sum(len(terms) for terms in self.TERMS.values())}  ")

        total_locations = sum(len(locs) for locs in self.term_locations.values())
        lines.append(f"**Total Locations Found**: {total_locations}  ")

        terms_with_locations = sum(1 for locs in self.term_locations.values() if locs)
        lines.append(f"**Terms with Locations**: {terms_with_locations}  ")
        lines.append("")

        lines.append("**Coverage by Category**:")
        for category, terms in self.TERMS.items():
            category_locations = sum(len(self.term_locations[term]) for term in terms)
            lines.append(f"- **{category}**: {len(terms)} terms, {category_locations} locations")

        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## 🔄 Maintenance")
        lines.append("")
        lines.append("**Auto-Generated**: This file is automatically generated. Do not edit manually.")
        lines.append("")
        lines.append("**Update Commands**:")
        lines.append("```bash")
        lines.append("# Regenerate implementation map")
        lines.append("python scripts/generate_implementation_map.py")
        lines.append("```")
        lines.append("")
        lines.append("**Update Schedule**:")
        lines.append("- **Weekly**: Automatically regenerated")
        lines.append("- **On PR**: Regenerated if Python files changed")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(f"**Last Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}  ")
        lines.append("**Generator**: `scripts/generate_implementation_map.py`")
        lines.append("")

        # Write output
        output_path.write_text('\n'.join(lines), encoding='utf-8')
        print(f"Implementation map generated: {output_path}")

    def run(self, output_path: Path) -> int:
        """Run the full mapping generation process."""
        self.scan_python_files()
        self.scan_config_files()
        self.scan_schema_files()
        self.scan_documentation()
        self.generate_markdown(output_path)

        # Check coverage
        terms_without_locations = [
            term for term, locs in self.term_locations.items() if not locs
        ]

        if terms_without_locations:
            print(f"\n⚠️  Warning: {len(terms_without_locations)} terms have no locations:")
            for term in terms_without_locations:
                print(f"  - {term}")

        return 0


def main():
    parser = argparse.ArgumentParser(
        description="Generate implementation location mappings for specialized terms"
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('docs/IMPLEMENTATION_LOCATIONS_GENERATED.md'),
        help='Output file path (default: docs/IMPLEMENTATION_LOCATIONS_GENERATED.md)'
    )

    args = parser.parse_args()

    # Resolve paths
    repo_root = Path(__file__).parent.parent.resolve()
    output_path = (repo_root / args.output).resolve()

    # Run mapper
    mapper = ImplementationMapper(repo_root)
    mapper.run(output_path)

    print("\n✅ Implementation map generation complete!")
    print(f"Output: {output_path}")

    return 0


if __name__ == '__main__':
    exit(main())
