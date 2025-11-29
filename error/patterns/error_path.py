"""Error Path Coverage Patterns.

Most code focuses on happy paths. This module systematically checks
for error handling coverage.

Error path questions for each function/module:
- What if this dependency is unavailable?
- What if this returns null/empty?
- What if this times out?
- What if this throws an exception?
- What if this returns malformed data?
- What if this is called twice simultaneously?
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .types import (
    ErrorPathCheck,
    PatternCategory,
    PatternFinding,
    PatternSeverity,
)


# Error path check types
ERROR_PATH_CHECKS = [
    "dependency_unavailable",
    "null_empty_return",
    "timeout",
    "exception",
    "malformed_data",
    "concurrent_access",
]

# Patterns that indicate external calls needing error handling
EXTERNAL_CALL_PATTERNS = {
    # Network/HTTP
    "requests.get": ["timeout", "exception", "malformed_data"],
    "requests.post": ["timeout", "exception", "malformed_data"],
    "requests.put": ["timeout", "exception", "malformed_data"],
    "requests.delete": ["timeout", "exception"],
    "httpx.get": ["timeout", "exception", "malformed_data"],
    "httpx.post": ["timeout", "exception", "malformed_data"],
    "urllib.request.urlopen": ["timeout", "exception"],
    "aiohttp": ["timeout", "exception", "malformed_data"],
    
    # Database
    "cursor.execute": ["exception", "timeout"],
    "connection.execute": ["exception", "timeout"],
    "session.execute": ["exception", "timeout"],
    "session.query": ["exception", "null_empty_return"],
    ".fetchone": ["null_empty_return"],
    ".fetchall": ["null_empty_return"],
    
    # File operations
    "open": ["exception", "dependency_unavailable"],
    "Path.read_text": ["exception", "dependency_unavailable"],
    "Path.read_bytes": ["exception", "dependency_unavailable"],
    "Path.write_text": ["exception"],
    "Path.write_bytes": ["exception"],
    "shutil.copy": ["exception", "dependency_unavailable"],
    "shutil.move": ["exception", "dependency_unavailable"],
    "os.remove": ["exception", "dependency_unavailable"],
    "os.makedirs": ["exception"],
    
    # JSON parsing
    "json.loads": ["exception", "malformed_data"],
    "json.load": ["exception", "malformed_data"],
    "json.dumps": ["exception"],
    "yaml.safe_load": ["exception", "malformed_data"],
    
    # Subprocess
    "subprocess.run": ["timeout", "exception"],
    "subprocess.Popen": ["exception"],
    "subprocess.call": ["timeout", "exception"],
    "subprocess.check_output": ["timeout", "exception"],
    
    # External services
    "boto3": ["timeout", "exception", "dependency_unavailable"],
    "redis": ["timeout", "exception", "dependency_unavailable"],
    "kafka": ["timeout", "exception", "dependency_unavailable"],
}


def analyze_error_paths(file_path: Path) -> List[PatternFinding]:
    """Analyze a file for missing error path coverage.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        List of findings about missing error handling
    """
    findings: List[PatternFinding] = []
    
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, SyntaxError):
        return findings
    
    # Analyze each function
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            findings.extend(_analyze_function_error_paths(node, str(file_path)))
    
    return findings


def _analyze_function_error_paths(
    func_node: ast.FunctionDef,
    file_path: str,
) -> List[PatternFinding]:
    """Analyze a function for missing error handling."""
    findings: List[PatternFinding] = []
    
    # Find all external calls in the function
    external_calls = _find_external_calls(func_node)
    
    for call_info in external_calls:
        # Check if call is inside try/except
        if not call_info["in_try_except"]:
            required_checks = call_info["required_checks"]
            
            for check_type in required_checks:
                severity = _get_severity_for_check(check_type)
                
                findings.append(PatternFinding(
                    pattern_category=PatternCategory.ERROR_PATH,
                    severity=severity,
                    file_path=file_path,
                    line=call_info["line"],
                    code=f"EPC-{_get_code_for_check(check_type)}",
                    message=f"Missing {check_type} handling for '{call_info['call_name']}' in function '{func_node.name}'",
                    suggested_fix=_get_fix_suggestion(check_type, call_info["call_name"]),
                    test_case=_generate_error_test(func_node.name, check_type),
                    context={
                        "function": func_node.name,
                        "call": call_info["call_name"],
                        "check_type": check_type,
                    },
                ))
    
    # Check for bare except clauses (anti-pattern)
    for node in ast.walk(func_node):
        if isinstance(node, ast.ExceptHandler):
            if node.type is None:
                findings.append(PatternFinding(
                    pattern_category=PatternCategory.ERROR_PATH,
                    severity=PatternSeverity.MAJOR,
                    file_path=file_path,
                    line=node.lineno,
                    code="EPC-006",
                    message=f"Bare except clause in function '{func_node.name}' catches all exceptions",
                    suggested_fix="Specify explicit exception types to catch",
                    context={"function": func_node.name},
                ))
    
    return findings


def _find_external_calls(func_node: ast.FunctionDef) -> List[Dict[str, Any]]:
    """Find all external calls that need error handling."""
    calls: List[Dict[str, Any]] = []
    
    # Track try/except scopes
    try_ranges: List[tuple] = []
    
    for node in ast.walk(func_node):
        if isinstance(node, ast.Try):
            # Record the range of the try block
            try_start = node.lineno
            # Find end of try block (start of first handler)
            try_end = node.handlers[0].lineno if node.handlers else try_start
            try_ranges.append((try_start, try_end))
    
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            call_name = _get_call_name(node)
            required_checks = _get_required_checks(call_name)
            
            if required_checks:
                # Check if call is inside a try block
                in_try = any(start <= node.lineno <= end for start, end in try_ranges)
                
                calls.append({
                    "call_name": call_name,
                    "line": node.lineno,
                    "in_try_except": in_try,
                    "required_checks": required_checks,
                })
    
    return calls


def _get_call_name(node: ast.Call) -> str:
    """Extract the callable name from a Call node."""
    if isinstance(node.func, ast.Name):
        return node.func.id
    elif isinstance(node.func, ast.Attribute):
        parts = []
        current = node.func
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        parts.reverse()
        return ".".join(parts)
    return "unknown"


def _get_required_checks(call_name: str) -> List[str]:
    """Get the required error checks for a given call."""
    # Direct match
    if call_name in EXTERNAL_CALL_PATTERNS:
        return EXTERNAL_CALL_PATTERNS[call_name]
    
    # Partial match (e.g., .fetchone)
    for pattern, checks in EXTERNAL_CALL_PATTERNS.items():
        if pattern.startswith(".") and call_name.endswith(pattern[1:]):
            return checks
        if call_name.startswith(pattern) or call_name.endswith(pattern):
            return checks
    
    return []


def _get_severity_for_check(check_type: str) -> PatternSeverity:
    """Determine severity based on the type of missing check."""
    severity_map = {
        "exception": PatternSeverity.MAJOR,
        "timeout": PatternSeverity.MAJOR,
        "dependency_unavailable": PatternSeverity.CRITICAL,
        "malformed_data": PatternSeverity.MAJOR,
        "null_empty_return": PatternSeverity.MINOR,
        "concurrent_access": PatternSeverity.MAJOR,
    }
    return severity_map.get(check_type, PatternSeverity.MINOR)


def _get_code_for_check(check_type: str) -> str:
    """Get the pattern code for a check type."""
    code_map = {
        "dependency_unavailable": "001",
        "null_empty_return": "002",
        "timeout": "003",
        "exception": "004",
        "malformed_data": "005",
        "concurrent_access": "007",
    }
    return code_map.get(check_type, "000")


def _get_fix_suggestion(check_type: str, call_name: str) -> str:
    """Get a fix suggestion for a missing error check."""
    suggestions = {
        "exception": f"Wrap '{call_name}' in try/except with appropriate exception types",
        "timeout": f"Add timeout parameter to '{call_name}' and handle TimeoutError",
        "dependency_unavailable": f"Check if dependency is available before calling '{call_name}'",
        "malformed_data": f"Validate response data from '{call_name}' before using",
        "null_empty_return": f"Check for None/empty return from '{call_name}'",
        "concurrent_access": f"Add locking or synchronization around '{call_name}'",
    }
    return suggestions.get(check_type, f"Add error handling for '{call_name}'")


def _generate_error_test(func_name: str, check_type: str) -> str:
    """Generate a test case for error path coverage."""
    test_templates = {
        "exception": f"""
def test_{func_name}_handles_exception():
    # Mock the external call to raise an exception
    with patch('module.external_call', side_effect=Exception("Test error")):
        result = {func_name}()
        assert result is None or isinstance(result, ErrorResult)
""",
        "timeout": f"""
def test_{func_name}_handles_timeout():
    # Mock the external call to timeout
    with patch('module.external_call', side_effect=TimeoutError()):
        result = {func_name}()
        assert result is None or isinstance(result, ErrorResult)
""",
        "null_empty_return": f"""
def test_{func_name}_handles_empty_response():
    # Mock the external call to return None/empty
    with patch('module.external_call', return_value=None):
        result = {func_name}()
        assert result is not None  # Should handle gracefully
""",
        "dependency_unavailable": f"""
def test_{func_name}_handles_missing_dependency():
    # Simulate dependency being unavailable
    with patch('module.dependency_available', return_value=False):
        result = {func_name}()
        assert result is None or isinstance(result, ErrorResult)
""",
    }
    return test_templates.get(check_type, f"# Add test for {check_type} handling").strip()


def generate_error_path_checklist(file_path: Path) -> List[ErrorPathCheck]:
    """Generate a checklist of error paths to verify.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        List of error path checks that should be verified
    """
    checks: List[ErrorPathCheck] = []
    
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, SyntaxError):
        return checks
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            external_calls = _find_external_calls(node)
            
            for call_info in external_calls:
                for check_type in call_info["required_checks"]:
                    checks.append(ErrorPathCheck(
                        check_type=check_type,
                        function_name=node.name,
                        file_path=str(file_path),
                        line=call_info["line"],
                        is_covered=call_info["in_try_except"],
                        missing_handling=None if call_info["in_try_except"] else _get_fix_suggestion(check_type, call_info["call_name"]),
                    ))
    
    return checks


def scan_file_for_error_path_issues(file_path: Path) -> List[PatternFinding]:
    """Scan a file for error path coverage issues.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        List of error path related findings
    """
    return analyze_error_paths(file_path)
