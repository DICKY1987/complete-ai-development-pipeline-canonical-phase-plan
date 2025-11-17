#!/usr/bin/env python3
"""Path standardizer plugin using CCPM path tools"""

import subprocess
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

def validate_paths(file_paths: List[str], project_root: str, autofix: bool = False) -> Dict[str, Any]:
    """Validate and optionally fix path standards"""

    check_script = Path(project_root) / "scripts" / "check-path-standards.sh"
    fix_script = Path(project_root) / "scripts" / "fix-path-standards.sh"

    if not check_script.exists():
        return {"tool": "path_standardizer", "errors": []}

    errors = []

    for file_path in file_paths:
        # Check path standards
        result = subprocess.run(
            ["bash", str(check_script), file_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            # Path violations found
            violations = parse_violations(result.stdout)

            if autofix and fix_script.exists():
                # Apply fixes
                fix_result = subprocess.run(
                    ["bash", str(fix_script), file_path],
                    capture_output=True,
                    text=True
                )

                if fix_result.returncode == 0:
                    continue  # Fixed successfully

            # Add violations to errors
            errors.extend(violations)

    return {
        "tool": "path_standardizer",
        "errors": errors
    }

def parse_violations(output: str) -> List[Dict[str, Any]]:
    """Parse path violation messages"""
    errors = []
    for line in output.split('\n'):
        if line.strip():
            errors.append({
                "category": "path_standard",
                "severity": "warning",
                "message": line.strip(),
                "file": "",
                "line": 0
            })
    return errors

if __name__ == "__main__":
    file_paths = sys.argv[1:-1] if len(sys.argv) > 2 else []
    autofix = sys.argv[-1] == "--fix" if len(sys.argv) > 1 else False

    result = validate_paths(file_paths, str(Path.cwd()), autofix)
    print(json.dumps(result, indent=2))
