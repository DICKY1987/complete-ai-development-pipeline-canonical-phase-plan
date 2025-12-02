#!/usr/bin/env python3
"""
PIPE File Classifier

Quick tool to check which PIPE module a file would belong to.

Usage:
    python scripts/pipe_classify.py path/to/file.py
    python scripts/pipe_classify.py --multiple file1.py file2.py file3.py
"""

import argparse
import sys
from pathlib import Path
import yaml
import fnmatch


def load_mapping_config(config_path: Path) -> dict:
    """Load mapping configuration."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def match_rule(rel_path: str, rule: dict) -> bool:
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


def classify_file(rel_path: str, mapping_config: dict) -> tuple[str, str]:
    """
    Classify file to a PIPE module.
    
    Returns: (pipe_id, rule_name)
    """
    rules = mapping_config.get("rules", [])
    
    # First match wins
    for rule in rules:
        if match_rule(rel_path, rule):
            return (rule["pipe_id"], rule["name"])
    
    # No match - use default
    default = mapping_config.get(
        "default_pipe_id",
        "PIPE-26_LEARN_AND_UPDATE_PATTERNS_PROMPTS_CONFIG"
    )
    return (default, "default")


def get_phase_for_pipe(pipe_id: str) -> str:
    """Get macro phase for a PIPE module."""
    phase_map = {
        "PIPE-01": "A_INTAKE_AND_SPECS",
        "PIPE-02": "A_INTAKE_AND_SPECS",
        "PIPE-03": "A_INTAKE_AND_SPECS",
        "PIPE-04": "B_WORKSTREAM_AND_CONFIG",
        "PIPE-05": "B_WORKSTREAM_AND_CONFIG",
        "PIPE-06": "B_WORKSTREAM_AND_CONFIG",
        "PIPE-07": "B_WORKSTREAM_AND_CONFIG",
        "PIPE-08": "C_PATTERNS_AND_PLANNING",
        "PIPE-09": "C_PATTERNS_AND_PLANNING",
        "PIPE-10": "C_PATTERNS_AND_PLANNING",
        "PIPE-11": "C_PATTERNS_AND_PLANNING",
        "PIPE-12": "C_PATTERNS_AND_PLANNING",
        "PIPE-13": "D_WORKSPACE_AND_SCHEDULING",
        "PIPE-14": "D_WORKSPACE_AND_SCHEDULING",
        "PIPE-15": "D_WORKSPACE_AND_SCHEDULING",
        "PIPE-16": "E_EXECUTION_AND_VALIDATION",
        "PIPE-17": "E_EXECUTION_AND_VALIDATION",
        "PIPE-18": "E_EXECUTION_AND_VALIDATION",
        "PIPE-19": "F_ERROR_AND_RECOVERY",
        "PIPE-20": "F_ERROR_AND_RECOVERY",
        "PIPE-21": "F_ERROR_AND_RECOVERY",
        "PIPE-22": "G_FINALIZATION_AND_LEARNING",
        "PIPE-23": "G_FINALIZATION_AND_LEARNING",
        "PIPE-24": "G_FINALIZATION_AND_LEARNING",
        "PIPE-25": "G_FINALIZATION_AND_LEARNING",
        "PIPE-26": "G_FINALIZATION_AND_LEARNING",
    }
    
    pipe_prefix = pipe_id.split("_")[0]  # e.g., "PIPE-17"
    return phase_map.get(pipe_prefix, "UNKNOWN")


def main():
    parser = argparse.ArgumentParser(
        description="Classify files to PIPE modules"
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="File paths to classify (relative to repo root)",
    )
    parser.add_argument(
        "--mapping-config",
        type=Path,
        default=Path("pipe_mapping_config.yaml"),
        help="Path to mapping configuration YAML",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed information",
    )
    
    args = parser.parse_args()
    
    # Load mapping configuration
    if not args.mapping_config.exists():
        print(f"Error: Mapping config not found: {args.mapping_config}", file=sys.stderr)
        sys.exit(1)
    
    try:
        mapping_config = load_mapping_config(args.mapping_config)
    except Exception as e:
        print(f"Error loading mapping config: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Classify each file
    for file_path in args.files:
        # Normalize path separators to forward slashes
        rel_path = file_path.replace("\\", "/")
        
        pipe_id, rule_name = classify_file(rel_path, mapping_config)
        phase = get_phase_for_pipe(pipe_id)
        
        if args.verbose:
            print(f"\nFile: {file_path}")
            print(f"  Virtual location: pipeline/{phase}/{pipe_id}/")
            print(f"  Matched rule: {rule_name}")
            print(f"  Full path: pipeline/{phase}/{pipe_id}/{rel_path}")
        else:
            print(f"{file_path} → {pipe_id}")


if __name__ == "__main__":
    main()
