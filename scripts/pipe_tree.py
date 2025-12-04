#!/usr/bin/env python3
"""
PIPE Virtual Tree Generator

Generates a virtual directory tree showing how the repository would look
if reorganized around PIPE-01 to PIPE-26 pipeline structure.

Usage:
    python scripts/pipe_tree.py --output PIPELINE_VIRTUAL_TREE.txt
"""
DOC_ID: DOC - SCRIPT - SCRIPTS - PIPE - TREE - 724
DOC_ID: DOC - SCRIPT - SCRIPTS - PIPE - TREE - 724

import argparse
import fnmatch
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

import yaml


class PipeTreeGenerator:
    """Generates virtual pipeline tree from current repo structure."""

    # Fixed macro phases and their PIPE modules
    PIPELINE_STRUCTURE = {
        "A_INTAKE_AND_SPECS": [
            "PIPE-01_INTAKE_REQUEST",
            "PIPE-02_DISCOVER_RELATED_SPECS",
            "PIPE-03_NORMALIZE_REQUIREMENTS",
        ],
        "B_WORKSTREAM_AND_CONFIG": [
            "PIPE-04_MATERIALIZE_WORKSTREAM_FILE",
            "PIPE-05_VALIDATE_WORKSTREAM_SCHEMA",
            "PIPE-06_RESOLVE_CONFIG_CASCADE",
            "PIPE-07_RESOLVE_CAPABILITIES_AND_REGISTRY",
        ],
        "C_PATTERNS_AND_PLANNING": [
            "PIPE-08_SELECT_UET_PATTERNS",
            "PIPE-09_SPECIALIZE_PATTERNS_WITH_CONTEXT",
            "PIPE-10_VALIDATE_PATTERN_PLAN",
            "PIPE-11_BUILD_TASK_GRAPH_DAG",
            "PIPE-12_PERSIST_PLAN_IN_STATE",
        ],
        "D_WORKSPACE_AND_SCHEDULING": [
            "PIPE-13_PREPARE_WORKTREES_AND_CHECKPOINTS",
            "PIPE-14_ADMIT_READY_TASKS_TO_QUEUE",
            "PIPE-15_ASSIGN_PRIORITIES_AND_SLOTS",
        ],
        "E_EXECUTION_AND_VALIDATION": [
            "PIPE-16_ROUTE_TASK_TO_TOOL_ADAPTER",
            "PIPE-17_EXECUTE_TOOL_AND_CAPTURE_OUTPUT",
            "PIPE-18_RUN_POST_EXEC_TESTS_AND_CHECKS",
        ],
        "F_ERROR_AND_RECOVERY": [
            "PIPE-19_RUN_ERROR_PLUGINS_PIPELINE",
            "PIPE-20_CLASSIFY_ERRORS_AND_CHOOSE_ACTION",
            "PIPE-21_APPLY_AUTOFIX_RETRY_AND_CIRCUIT_CONTROL",
        ],
        "G_FINALIZATION_AND_LEARNING": [
            "PIPE-22_COMMIT_TASK_RESULTS_TO_STATE_AND_MODULES",
            "PIPE-23_COMPLETE_WORKSTREAM_AND_ARCHIVE",
            "PIPE-24_UPDATE_METRICS_REPORTS_AND_SUMMARIES",
            "PIPE-25_SURFACE_TO_GUI_AND_TUI",
            "PIPE-26_LEARN_AND_UPDATE_PATTERNS_PROMPTS_CONFIG",
        ],
    }

    def __init__(self, root: Path, mapping_config: Dict, ignore_patterns: List[str]):
        self.root = root
        self.mapping_config = mapping_config
        self.ignore_patterns = ignore_patterns
        self.tree: Dict[str, List[str]] = {}
        self._init_tree()

    def _init_tree(self):
        """Initialize empty tree structure."""
        for phase, pipe_modules in self.PIPELINE_STRUCTURE.items():
            for pipe_module in pipe_modules:
                self.tree[pipe_module] = []

    def _should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored."""
        path_str = str(path.relative_to(self.root))

        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(path_str, pattern):
                return True
            # Also check directory names
            if any(fnmatch.fnmatch(part, pattern) for part in path.parts):
                return True

        return False

    def _match_rule(self, rel_path: str, rule: Dict) -> bool:
        """Check if relative path matches a rule."""
        match = rule.get("match", {})

        # Check path_prefix matches
        for prefix in match.get("path_prefix", []):
            if rel_path.startswith(prefix):
                return True

        # Check file_glob matches
        for glob_pattern in match.get("file_glob", []):
            if fnmatch.fnmatch(rel_path, glob_pattern):
                return True

        return False

    def _classify_file(self, rel_path: str) -> str:
        """Classify file to a PIPE module based on mapping rules."""
        rules = self.mapping_config.get("rules", [])

        # First match wins
        for rule in rules:
            if self._match_rule(rel_path, rule):
                return rule["pipe_id"]

        # No match - use default
        return self.mapping_config.get(
            "default_pipe_id", "PIPE-26_LEARN_AND_UPDATE_PATTERNS_PROMPTS_CONFIG"
        )

    def scan_repository(self):
        """Scan repository and classify all files."""
        for path in self.root.rglob("*"):
            # Skip directories, only process files
            if path.is_dir():
                continue

            # Skip ignored paths
            if self._should_ignore(path):
                continue

            # Get relative path
            try:
                rel_path = str(path.relative_to(self.root)).replace("\\", "/")
            except ValueError:
                continue

            # Classify to PIPE module
            pipe_id = self._classify_file(rel_path)

            # Add to tree
            if pipe_id in self.tree:
                self.tree[pipe_id].append(rel_path)

    def render_tree(self) -> str:
        """Render the virtual tree as ASCII."""
        lines = ["pipeline/"]

        for phase, pipe_modules in self.PIPELINE_STRUCTURE.items():
            lines.append(f"  {phase}/")

            for pipe_module in pipe_modules:
                lines.append(f"    {pipe_module}/")

                # Get and sort files for this module
                files = sorted(self.tree.get(pipe_module, []))

                if not files:
                    lines.append(f"      (empty)")
                else:
                    for file in files:
                        lines.append(f"      {file}")

        return "\n".join(lines)

    def generate_stats(self) -> Dict:
        """Generate statistics about the mapping."""
        stats = {
            "total_files": sum(len(files) for files in self.tree.values()),
            "by_pipe": {},
            "by_phase": {},
        }

        for phase, pipe_modules in self.PIPELINE_STRUCTURE.items():
            phase_count = 0
            for pipe_module in pipe_modules:
                count = len(self.tree.get(pipe_module, []))
                stats["by_pipe"][pipe_module] = count
                phase_count += count
            stats["by_phase"][phase] = phase_count

        return stats


def load_ignore_patterns(ignore_file: Optional[Path]) -> List[str]:
    """Load ignore patterns from file."""
    default_patterns = [
        ".git/*",
        ".git/**",
        "__pycache__/*",
        "__pycache__/**",
        "*.pyc",
        ".pytest_cache/*",
        ".pytest_cache/**",
        ".venv/*",
        ".venv/**",
        "venv/*",
        "venv/**",
        "node_modules/*",
        "node_modules/**",
        ".worktrees/*",
        ".worktrees/**",
        "*.db",
        "*.db-journal",
    ]

    if ignore_file and ignore_file.exists():
        with open(ignore_file, "r", encoding="utf-8") as f:
            custom_patterns = [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]
            return default_patterns + custom_patterns

    return default_patterns


def main():
    parser = argparse.ArgumentParser(
        description="Generate virtual pipeline tree structure"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repository root directory (default: current directory)",
    )
    parser.add_argument(
        "--mapping-config",
        type=Path,
        default=Path("pipe_mapping_config.yaml"),
        help="Path to mapping configuration YAML",
    )
    parser.add_argument(
        "--ignore-file",
        type=Path,
        default=Path(".pipeignore"),
        help="Path to ignore patterns file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("PIPELINE_VIRTUAL_TREE.txt"),
        help="Output file path",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Print statistics about the mapping",
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.root.exists():
        print(f"Error: Root directory does not exist: {args.root}", file=sys.stderr)
        sys.exit(1)

    if not args.mapping_config.exists():
        print(
            f"Error: Mapping config not found: {args.mapping_config}", file=sys.stderr
        )
        sys.exit(1)

    # Load mapping configuration
    try:
        with open(args.mapping_config, "r", encoding="utf-8") as f:
            mapping_config = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading mapping config: {e}", file=sys.stderr)
        sys.exit(1)

    # Load ignore patterns
    ignore_patterns = load_ignore_patterns(
        args.ignore_file if args.ignore_file.exists() else None
    )

    # Generate tree
    print(f"Scanning repository: {args.root}")
    generator = PipeTreeGenerator(args.root, mapping_config, ignore_patterns)
    generator.scan_repository()

    # Render and save
    print(f"Rendering virtual tree...")
    tree_output = generator.render_tree()

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(tree_output)

    print(f"✓ Virtual tree written to: {args.output}")

    # Print statistics if requested
    if args.stats:
        stats = generator.generate_stats()
        print(f"\nStatistics:")
        print(f"  Total files mapped: {stats['total_files']}")
        print(f"\n  By phase:")
        for phase, count in sorted(stats["by_phase"].items()):
            print(f"    {phase}: {count} files")
        print(f"\n  Top 5 PIPE modules by file count:")
        top_pipes = sorted(stats["by_pipe"].items(), key=lambda x: x[1], reverse=True)[
            :5
        ]
        for pipe_id, count in top_pipes:
            print(f"    {pipe_id}: {count} files")


if __name__ == "__main__":
    main()
