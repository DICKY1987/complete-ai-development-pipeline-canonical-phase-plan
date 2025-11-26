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
    """Parse test output into Operating Contract error format."""
    errors = []
    
    if exit_code != 0:
        # Check if this is pytest output (has pytest-specific markers)
        is_pytest = 'test session starts' in stdout or '::' in stdout or 'PASSED' in stdout
        
        # Check if this is jest output
        is_jest = '●' in stdout or 'FAIL  ' in stdout or 'Test Suites:' in stdout
        
        if is_pytest:
            errors.extend(_parse_pytest_output(stdout, stderr))
        elif is_jest:
            errors.extend(_parse_jest_output(stdout, stderr))
        else:
            # Generic parsing for unknown test framework
            errors.extend(_parse_pytest_output(stdout, stderr))
    
    return errors


def _parse_pytest_output(stdout: str, stderr: str) -> List[Dict[str, Any]]:
    """Parse pytest-specific output."""
    import re
    errors = []
    
    # Look for pytest failure patterns
    # Example: "tests/test_foo.py::test_bar FAILED"
    # Example: "test_foo.py:42: AssertionError"
    
    # Pattern 1: FAILED test lines
    failed_pattern = re.compile(r'([\w/\\]+\.py)::(\w+)\s+FAILED')
    for match in failed_pattern.finditer(stdout):
        file_path = match.group(1)
        test_name = match.group(2)
        errors.append({
            "category": "test_failure",
            "severity": "error",
            "message": f"Test failed: {test_name}",
            "file": file_path,
            "line": 0,  # Will be extracted from traceback if available
        })
    
    # Pattern 2: Traceback lines with line numbers
    # Example: "  File \"test.py\", line 42, in test_function"
    traceback_pattern = re.compile(r'File "([^"]+)", line (\d+)')
    for match in traceback_pattern.finditer(stdout + stderr):
        file_path = match.group(1)
        line_num = int(match.group(2))
        
        # Try to extract the error message from following lines
        error_msg = "Test assertion failed"
        
        errors.append({
            "category": "test_failure",
            "severity": "error",
            "message": error_msg,
            "file": file_path,
            "line": line_num,
        })
    
    # Pattern 3: ERROR lines (test collection errors, etc.)
    error_pattern = re.compile(r'ERROR\s+([\w/\\]+\.py)(?:::(\w+))?')
    for match in error_pattern.finditer(stdout):
        file_path = match.group(1)
        test_name = match.group(2) or "unknown"
        errors.append({
            "category": "test_failure",
            "severity": "error",
            "message": f"Test error: {test_name}",
            "file": file_path,
            "line": 0,
        })
    
    return errors


def _parse_jest_output(stdout: str, stderr: str) -> List[Dict[str, Any]]:
    """Parse Jest test output."""
    import re
    errors = []
    
    # Jest failure pattern: "  ● test suite › test name"
    # Followed by file and line info
    
    # Look for failed test markers
    failed_pattern = re.compile(r'●\s+(.+?)›\s+(.+)')
    for match in failed_pattern.finditer(stdout):
        suite = match.group(1).strip()
        test_name = match.group(2).strip()
        
        errors.append({
            "category": "test_failure",
            "severity": "error",
            "message": f"Test failed: {suite} › {test_name}",
            "file": "",  # Jest format varies
            "line": 0,
        })
    
    # Extract file paths from Jest output
    # Pattern: "  at Object.<anonymous> (path/to/file.js:line:column)"
    jest_traceback = re.compile(r'at .+? \(([^:]+):(\d+):(\d+)\)')
    for match in jest_traceback.finditer(stdout + stderr):
        file_path = match.group(1)
        line_num = int(match.group(2))
        
        errors.append({
            "category": "test_failure",
            "severity": "error",
            "message": "Test assertion failed",
            "file": file_path,
            "line": line_num,
        })
    
    return errors

def parse_test_failure_line(line: str) -> Dict[str, Any]:
    """Parse a single test failure line."""
    import re
    
    # Try to extract file and line info from common patterns
    # Pattern: "path/to/file.py::test_name FAILED"
    pytest_match = re.match(r'([\w/\\]+\.py)::(\w+)\s+FAILED', line)
    if pytest_match:
        return {
            "category": "test_failure",
            "severity": "error",
            "message": f"Test failed: {pytest_match.group(2)}",
            "file": pytest_match.group(1),
            "line": 0,
        }
    
    # Pattern: "ERROR test_file.py::test_name"
    error_match = re.match(r'ERROR\s+([\w/\\]+\.py)(?:::(\w+))?', line)
    if error_match:
        test_name = error_match.group(2) or "unknown"
        return {
            "category": "test_failure", 
            "severity": "error",
            "message": f"Test error: {test_name}",
            "file": error_match.group(1),
            "line": 0,
        }
    
    # Generic failure line
    return {
        "category": "test_failure",
        "severity": "error",
        "message": line.strip(),
        "file": "",
        "line": 0,
    }

def extract_file(line: str) -> str:
    """Extract file path from test output line."""
    import re
    
    # Try common patterns
    # pytest: "tests/test_foo.py::test_bar"
    # jest: "  at file.js:10:5"
    
    # Pattern 1: pytest format
    pytest_match = re.search(r'([\w/\\]+\.(?:py|js|ts))', line)
    if pytest_match:
        return pytest_match.group(1)
    
    return ""


def extract_line(line: str) -> int:
    """Extract line number from test output line."""
    import re
    
    # Try multiple patterns in order of specificity
    
    # Pattern 1: "line NUMBER" (most explicit)
    line_match = re.search(r'line\s+(\d+)', line, re.IGNORECASE)
    if line_match:
        return int(line_match.group(1))
    
    # Pattern 2: ":NUMBER:" or ":NUMBER," or ":NUMBER " (common in stack traces)
    line_match = re.search(r':(\d+)(?::|,|\s)', line)
    if line_match:
        return int(line_match.group(1))
    
    # Pattern 3: Just ":NUMBER" at end of string
    line_match = re.search(r':(\d+)$', line)
    if line_match:
        return int(line_match.group(1))
    
    return 0

def count_tests(output: str) -> int:
    """Count total tests from output (best-effort for pytest)."""
    import re
    # pytest summary e.g.: '== 3 passed, 1 failed, 4 warnings in 0.12s =='
    m = re.search(r"==+\s+(.*?)\s+in\s+", output)
    if not m:
        return 0
    parts = m.group(1).split(',')
    total = 0
    for p in parts:
        p = p.strip()
        try:
            n = int(p.split()[0])
            total += n
        except Exception:
            pass
    return total

def count_passed(output: str) -> int:
    """Count passed tests from output (pytest style)."""
    import re
    m = re.search(r"(\d+)\s+passed", output)
    return int(m.group(1)) if m else 0

def count_failed(output: str) -> int:
    """Count failed tests from output (pytest style)."""
    import re
    m = re.search(r"(\d+)\s+failed", output)
    return int(m.group(1)) if m else 0

if __name__ == "__main__":
    # Read file paths from stdin or args
    file_paths = sys.argv[1:] if len(sys.argv) > 1 else []
    project_root = Path.cwd()

    result = run_tests(file_paths, str(project_root))
    print(json.dumps(result, indent=2))
