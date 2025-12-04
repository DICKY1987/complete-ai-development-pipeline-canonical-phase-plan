#!/usr/bin/env python3
"""
Generate repository map showing all modules, functions, and classes.

Usage:
    python scripts/generate_repository_map.py
    python scripts/generate_repository_map.py --output custom_map.yaml
    python scripts/generate_repository_map.py --include "core/**/*.py" "phase*/**/*.py"
"""
# DOC_ID: DOC-SCRIPTS-GENERATE-REPOSITORY-MAP-208

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.ast.repository_mapper import RepositoryMapper


def main():
    parser = argparse.ArgumentParser(description="Generate AST-based repository map")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("AST_REPOSITORY_MAP.yaml"),
        help="Output file path (default: AST_REPOSITORY_MAP.yaml)",
    )
    parser.add_argument(
        "--include", nargs="+", default=None, help="Include patterns (default: **/*.py)"
    )
    parser.add_argument(
        "--exclude",
        nargs="+",
        default=None,
        help="Exclude patterns (default: tests, __pycache__, etc.)",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root path (default: current directory)",
    )

    args = parser.parse_args()

    print(f"Generating repository map for: {args.root}")
    print(f"Output: {args.output}")

    mapper = RepositoryMapper(args.root)
    mapper.generate_and_save(
        args.output, include_patterns=args.include, exclude_patterns=args.exclude
    )

    print("\nDone!")


if __name__ == "__main__":
    main()
