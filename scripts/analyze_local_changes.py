#!/usr/bin/env python3
"""
Analyze local directory changes and categorize them for merge strategy.

Usage:
    python scripts/analyze_local_changes.py --output .merge-backup/change-analysis.yaml
"""
DOC_ID: DOC-SCRIPT-SCRIPTS-ANALYZE-LOCAL-CHANGES-190
DOC_ID: DOC-SCRIPT-SCRIPTS-ANALYZE-LOCAL-CHANGES-127

import argparse
import subprocess
import yaml
from pathlib import Path
from typing import Dict, List, Set


def run_git_command(args: List[str]) -> str:
    """Run git command and return output."""
    result = subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True,
        check=False
    )
    return result.stdout.strip()


def get_modified_files() -> List[str]:
    """Get list of modified tracked files."""
    output = run_git_command(["diff", "--name-only"])
    return [f for f in output.split("\n") if f]


def get_staged_files() -> List[str]:
    """Get list of staged files."""
    output = run_git_command(["diff", "--cached", "--name-only"])
    return [f for f in output.split("\n") if f]


def get_untracked_files() -> List[str]:
    """Get list of untracked files."""
    output = run_git_command(["ls-files", "--others", "--exclude-standard"])
    return [f for f in output.split("\n") if f]


def categorize_file(filepath: str) -> str:
    """Categorize file based on path and type."""
    path = Path(filepath)
    
    # Generated/cache files - discard
    discard_patterns = [
        "__pycache__",
        ".pyc",
        ".pytest_cache",
        ".coverage",
        "*.egg-info",
        ".mypy_cache",
        ".ruff_cache",
        "node_modules",
        ".venv",
        "venv",
        ".git",
    ]
    
    for pattern in discard_patterns:
        if pattern in str(path):
            return "discard"
    
    # Temporary/backup files - discard
    if path.suffix in [".tmp", ".bak", ".swp", ".log"]:
        return "discard"
    
    # Documentation - merge
    doc_patterns = ["docs/", "README", ".md", "CHANGELOG"]
    for pattern in doc_patterns:
        if pattern in str(path):
            return "merge"
    
    # Configuration - review carefully
    config_patterns = [".yaml", ".yml", ".json", ".toml", "config/", ".env"]
    for pattern in config_patterns:
        if pattern in str(path):
            return "review"
    
    # Source code - keep local
    if path.suffix in [".py", ".js", ".ts", ".go", ".rs"]:
        # But scripts might be generated
        if "scripts/" in str(path):
            return "review"
        return "keep_local"
    
    # Tests - keep local
    if "test" in str(path).lower():
        return "keep_local"
    
    # Default: review
    return "review"


def analyze_file_content(filepath: str) -> Dict[str, any]:
    """Analyze file content for additional context."""
    try:
        path = Path(filepath)
        if not path.exists():
            return {"exists": False}
        
        stat = path.stat()
        content_sample = ""
        
        # Read first 5 lines for text files
        if path.suffix in [".py", ".md", ".txt", ".yaml", ".json"]:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    lines = [f.readline() for _ in range(5)]
                    content_sample = "".join(lines)
            except Exception:
                content_sample = "<binary or unreadable>"
        
        return {
            "exists": True,
            "size_bytes": stat.st_size,
            "modified_time": stat.st_mtime,
            "content_sample": content_sample[:200],
        }
    except Exception as e:
        return {"exists": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Analyze local changes")
    parser.add_argument("--output", required=True, help="Output YAML file path")
    args = parser.parse_args()
    
    # Collect all changes
    modified = get_modified_files()
    staged = get_staged_files()
    untracked = get_untracked_files()
    
    # Categorize changes
    analysis = {
        "summary": {
            "total_modified": len(modified),
            "total_staged": len(staged),
            "total_untracked": len(untracked),
            "total_files": len(set(modified + staged + untracked)),
        },
        "categories": {
            "keep_local": [],
            "merge": [],
            "review": [],
            "discard": [],
        },
        "files": {},
    }
    
    # Process all files
    all_files = set(modified + staged + untracked)
    for filepath in all_files:
        category = categorize_file(filepath)
        file_info = {
            "category": category,
            "status": [],
            "analysis": analyze_file_content(filepath),
        }
        
        if filepath in modified:
            file_info["status"].append("modified")
        if filepath in staged:
            file_info["status"].append("staged")
        if filepath in untracked:
            file_info["status"].append("untracked")
        
        analysis["files"][filepath] = file_info
        analysis["categories"][category].append(filepath)
    
    # Add recommendations
    analysis["recommendations"] = {
        "keep_local": {
            "count": len(analysis["categories"]["keep_local"]),
            "action": "Stash or commit these changes - they contain local work",
        },
        "merge": {
            "count": len(analysis["categories"]["merge"]),
            "action": "Review and merge with incoming changes",
        },
        "review": {
            "count": len(analysis["categories"]["review"]),
            "action": "Manual review required - may need case-by-case decision",
        },
        "discard": {
            "count": len(analysis["categories"]["discard"]),
            "action": "Safe to discard - generated or temporary files",
        },
    }
    
    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w") as f:
        yaml.dump(analysis, f, sort_keys=False, default_flow_style=False)
    
    print(f"✅ Analysis complete: {output_path}")
    print(f"\nSummary:")
    print(f"  Total files: {analysis['summary']['total_files']}")
    print(f"  Keep local: {len(analysis['categories']['keep_local'])}")
    print(f"  Merge: {len(analysis['categories']['merge'])}")
    print(f"  Review: {len(analysis['categories']['review'])}")
    print(f"  Discard: {len(analysis['categories']['discard'])}")


if __name__ == "__main__":
    main()
