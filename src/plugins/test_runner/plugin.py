#!/usr/bin/env python3
"""Test runner plugin using CCPM test-and-log.sh"""

import subprocess
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

def run_tests(file_paths: List[str], project_root: str) -> Dict[str, Any]:
    """Execute tests using test-and-log.sh and return results"""

    script_path = Path(project_root) / "scripts" / "test-and-log.sh"

    if not script_path.exists():
        return {
            "tool": "test_runner",
            "errors": [{"category": "tool_error", "severity": "error", "message": f"test-and-log.sh not found at {script_path}", "file": "", "line": 0}]
        }

    # Run test-and-log.sh
    try:
        result = subprocess.run(
            ["bash", str(script_path)],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        # Parse test output and convert to Operating Contract format
        errors = parse_test_output(result.stdout, result.stderr, result.returncode)

        return {
            "tool": "test_runner",
            "errors": errors,
            "summary": {
                "total_tests": count_tests(result.stdout),
                "passed": count_passed(result.stdout),
                "failed": count_failed(result.stdout),
                "exit_code": result.returncode
            }
        }

    except subprocess.TimeoutExpired:
        return {
            "tool": "test_runner",
            "errors": [{"category": "test_timeout", "severity": "error", "message": "Test execution exceeded 5 minute timeout", "file": "", "line": 0}]
        }
    except Exception as e:
        return {
            "tool": "test_runner",
            "errors": [{"category": "execution_error", "severity": "error", "message": f"Test execution failed: {str(e)}", "file": "", "line": 0}]
        }

def parse_test_output(stdout: str, stderr: str, exit_code: int) -> List[Dict[str, Any]]:
    """Parse test output into Operating Contract error format"""
    errors = []

    if exit_code != 0:
        # Parse pytest, jest, etc. output
        # This is framework-specific - implement parsers for each
        for line in stdout.split('\n') + stderr.split('\n'):
            if 'FAILED' in line or 'ERROR' in line or 'FAIL' in line:
                error = parse_test_failure_line(line)
                if error:
                    errors.append(error)

    return errors

def parse_test_failure_line(line: str) -> Dict[str, Any]:
    """Parse a single test failure line"""
    # Implement parsing logic for different test frameworks
    # Return None if line doesn't contain useful error info
    return {
        "category": "test_failure",
        "severity": "error",
        "message": line.strip(),
        "file": extract_file(line),
        "line": extract_line(line)
    }

def extract_file(line: str) -> str:
    """Extract file path from test output line"""
    # Implement framework-specific extraction
    return ""

def extract_line(line: str) -> int:
    """Extract line number from test output line"""
    # Implement framework-specific extraction
    return 0

def count_tests(output: str) -> int:
    """Count total tests from output"""
    # Implement framework-specific counting
    return 0

def count_passed(output: str) -> int:
    """Count passed tests from output"""
    return 0

def count_failed(output: str) -> int:
    """Count failed tests from output"""
    return 0

if __name__ == "__main__":
    # Read file paths from stdin or args
    file_paths = sys.argv[1:] if len(sys.argv) > 1 else []
    project_root = Path.cwd()

    result = run_tests(file_paths, str(project_root))
    print(json.dumps(result, indent=2))
