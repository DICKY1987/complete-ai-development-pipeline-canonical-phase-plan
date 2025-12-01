"""Boundary Value Analysis Patterns.

AI excels at generating boundary test cases systematically. This module
provides patterns and generators for boundary value testing.

Boundary categories:
- Numeric: min-1, min, min+1, max-1, max, max+1, 0, -1
- String: empty, single char, max_length, max_length+1, null, special chars
- Collection: empty, single_item, full, overflow
- State: uninitialized, valid, invalid, transitioning
"""
# DOC_ID: DOC-ERROR-PATTERNS-BOUNDARY-PATTERNS-048
from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .types import (
    BoundarySpec,
    BoundaryTestCase,
    PatternCategory,
    PatternFinding,
    PatternSeverity,
)


# Standard boundary values by type
BOUNDARY_PATTERNS: Dict[str, List[Dict[str, Any]]] = {
    "int": [
        {"category": "min_minus_1", "value": -2147483649, "valid": False},
        {"category": "min", "value": -2147483648, "valid": True},
        {"category": "min_plus_1", "value": -2147483647, "valid": True},
        {"category": "zero", "value": 0, "valid": True},
        {"category": "negative_one", "value": -1, "valid": True},
        {"category": "one", "value": 1, "valid": True},
        {"category": "max_minus_1", "value": 2147483646, "valid": True},
        {"category": "max", "value": 2147483647, "valid": True},
        {"category": "max_plus_1", "value": 2147483648, "valid": False},
    ],
    "float": [
        {"category": "negative_infinity", "value": float("-inf"), "valid": False},
        {"category": "min_float", "value": -1.7976931348623157e+308, "valid": True},
        {"category": "negative_small", "value": -1e-308, "valid": True},
        {"category": "negative_one", "value": -1.0, "valid": True},
        {"category": "zero", "value": 0.0, "valid": True},
        {"category": "positive_small", "value": 1e-308, "valid": True},
        {"category": "one", "value": 1.0, "valid": True},
        {"category": "max_float", "value": 1.7976931348623157e+308, "valid": True},
        {"category": "positive_infinity", "value": float("inf"), "valid": False},
        {"category": "nan", "value": float("nan"), "valid": False},
    ],
    "str": [
        {"category": "empty", "value": "", "valid": True},
        {"category": "single_char", "value": "a", "valid": True},
        {"category": "whitespace", "value": "   ", "valid": True},
        {"category": "special_chars", "value": "!@#$%^&*()", "valid": True},
        {"category": "unicode", "value": "日本語", "valid": True},
        {"category": "null_char", "value": "\x00", "valid": False},
        {"category": "newlines", "value": "line1\nline2\r\nline3", "valid": True},
        {"category": "very_long", "value": "a" * 10000, "valid": True},
        {"category": "sql_injection", "value": "'; DROP TABLE users; --", "valid": False},
        {"category": "xss", "value": "<script>alert('xss')</script>", "valid": False},
    ],
    "list": [
        {"category": "empty", "value": [], "valid": True},
        {"category": "single_item", "value": [1], "valid": True},
        {"category": "two_items", "value": [1, 2], "valid": True},
        {"category": "many_items", "value": list(range(1000)), "valid": True},
        {"category": "nested", "value": [[1], [2], [3]], "valid": True},
        {"category": "mixed_types", "value": [1, "two", 3.0], "valid": True},
        {"category": "with_none", "value": [1, None, 3], "valid": True},
    ],
    "dict": [
        {"category": "empty", "value": {}, "valid": True},
        {"category": "single_key", "value": {"key": "value"}, "valid": True},
        {"category": "nested", "value": {"a": {"b": {"c": 1}}}, "valid": True},
        {"category": "numeric_keys", "value": {1: "a", 2: "b"}, "valid": True},
        {"category": "special_key", "value": {"": "empty_key", None: "none_key"}, "valid": True},
    ],
    "bool": [
        {"category": "true", "value": True, "valid": True},
        {"category": "false", "value": False, "valid": True},
    ],
    "None": [
        {"category": "none", "value": None, "valid": True},
    ],
}

# State boundary patterns
STATE_PATTERNS = {
    "uninitialized": {"description": "Object not yet initialized", "valid": False},
    "valid": {"description": "Object in valid state", "valid": True},
    "invalid": {"description": "Object in invalid state", "valid": False},
    "transitioning": {"description": "Object between states", "valid": False},
    "disposed": {"description": "Object already disposed/closed", "valid": False},
}


def generate_boundary_tests(
    param_name: str,
    param_type: str,
    constraints: Optional[Dict[str, Any]] = None,
) -> BoundarySpec:
    """Generate boundary test cases for a parameter.
    
    Args:
        param_name: Name of the parameter
        param_type: Python type annotation string
        constraints: Optional constraints like min, max, max_length
        
    Returns:
        BoundarySpec with all applicable test cases
    """
    spec = BoundarySpec(param_type=param_type)
    constraints = constraints or {}
    
    # Normalize type string
    base_type = _normalize_type(param_type)
    
    # Get patterns for this type
    patterns = BOUNDARY_PATTERNS.get(base_type, [])
    
    for pattern in patterns:
        test_case = BoundaryTestCase(
            parameter_name=param_name,
            parameter_type=param_type,
            test_value=pattern["value"],
            test_category=pattern["category"],
            expected_behavior=_get_expected_behavior(pattern, constraints),
            is_valid_input=pattern.get("valid", True),
        )
        spec.boundaries.append(test_case)
    
    # Add constraint-specific boundaries
    if "min" in constraints:
        min_val = constraints["min"]
        spec.boundaries.extend([
            BoundaryTestCase(param_name, param_type, min_val - 1, "constraint_min_minus_1", "Should reject", False),
            BoundaryTestCase(param_name, param_type, min_val, "constraint_min", "Should accept", True),
            BoundaryTestCase(param_name, param_type, min_val + 1, "constraint_min_plus_1", "Should accept", True),
        ])
    
    if "max" in constraints:
        max_val = constraints["max"]
        spec.boundaries.extend([
            BoundaryTestCase(param_name, param_type, max_val - 1, "constraint_max_minus_1", "Should accept", True),
            BoundaryTestCase(param_name, param_type, max_val, "constraint_max", "Should accept", True),
            BoundaryTestCase(param_name, param_type, max_val + 1, "constraint_max_plus_1", "Should reject", False),
        ])
    
    if "max_length" in constraints:
        max_len = constraints["max_length"]
        spec.boundaries.extend([
            BoundaryTestCase(param_name, param_type, "a" * (max_len - 1), "constraint_maxlen_minus_1", "Should accept", True),
            BoundaryTestCase(param_name, param_type, "a" * max_len, "constraint_maxlen", "Should accept", True),
            BoundaryTestCase(param_name, param_type, "a" * (max_len + 1), "constraint_maxlen_plus_1", "Should reject", False),
        ])
    
    return spec


def _normalize_type(type_str: str) -> str:
    """Normalize a type annotation to a base type."""
    type_str = type_str.strip()
    
    # Handle Optional[X]
    if type_str.startswith("Optional["):
        inner = type_str[9:-1]
        return _normalize_type(inner)
    
    # Handle Union types
    if type_str.startswith("Union["):
        # Take the first non-None type
        inner = type_str[6:-1]
        parts = [p.strip() for p in inner.split(",")]
        for part in parts:
            if part != "None":
                return _normalize_type(part)
    
    # Handle List, Set, Tuple
    if type_str.startswith(("List[", "list[")):
        return "list"
    if type_str.startswith(("Dict[", "dict[")):
        return "dict"
    if type_str.startswith(("Set[", "set[")):
        return "list"  # Similar testing approach
    if type_str.startswith(("Tuple[", "tuple[")):
        return "list"
    
    # Map common type annotations
    type_map = {
        "int": "int",
        "float": "float",
        "str": "str",
        "bool": "bool",
        "list": "list",
        "dict": "dict",
        "bytes": "str",
        "NoneType": "None",
    }
    
    return type_map.get(type_str, "str")  # Default to str testing


def _get_expected_behavior(pattern: Dict[str, Any], constraints: Dict[str, Any]) -> str:
    """Determine expected behavior for a boundary test."""
    if not pattern.get("valid", True):
        return "Should raise ValidationError or handle gracefully"
    return "Should process normally"


def analyze_function_boundaries(
    file_path: Path,
    function_name: str,
) -> List[PatternFinding]:
    """Analyze a function for missing boundary validation.
    
    Args:
        file_path: Path to the Python file
        function_name: Name of the function to analyze
        
    Returns:
        List of findings about missing boundary checks
    """
    findings: List[PatternFinding] = []
    
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, SyntaxError):
        return findings
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            findings.extend(_analyze_function_node(node, str(file_path)))
            break
    
    return findings


def _analyze_function_node(
    func_node: ast.FunctionDef,
    file_path: str,
) -> List[PatternFinding]:
    """Analyze a function AST node for boundary validation issues."""
    findings: List[PatternFinding] = []
    
    # Check for parameters without validation
    for arg in func_node.args.args:
        param_name = arg.arg
        has_validation = _check_parameter_validation(func_node, param_name)
        
        if not has_validation and param_name != "self":
            findings.append(PatternFinding(
                pattern_category=PatternCategory.BOUNDARY_VALUE,
                severity=PatternSeverity.MINOR,
                file_path=file_path,
                line=arg.lineno if hasattr(arg, "lineno") else func_node.lineno,
                code="BVA-001",
                message=f"Parameter '{param_name}' lacks boundary validation",
                suggested_fix=f"Add validation for '{param_name}' at function entry",
                test_case=_generate_test_suggestion(param_name, arg.annotation),
            ))
    
    return findings


def _check_parameter_validation(func_node: ast.FunctionDef, param_name: str) -> bool:
    """Check if a parameter has validation in the function body."""
    for node in ast.walk(func_node):
        # Check for isinstance checks
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "isinstance":
                if node.args and isinstance(node.args[0], ast.Name):
                    if node.args[0].id == param_name:
                        return True
        
        # Check for comparisons (e.g., if param < 0)
        if isinstance(node, ast.Compare):
            if isinstance(node.left, ast.Name) and node.left.id == param_name:
                return True
        
        # Check for 'if param:' or 'if not param:'
        if isinstance(node, ast.If):
            test = node.test
            if isinstance(test, ast.Name) and test.id == param_name:
                return True
            if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
                if isinstance(test.operand, ast.Name) and test.operand.id == param_name:
                    return True
        
        # Check for 'if param is None'
        if isinstance(node, ast.Compare):
            if isinstance(node.left, ast.Name) and node.left.id == param_name:
                for op, comparator in zip(node.ops, node.comparators):
                    if isinstance(op, (ast.Is, ast.IsNot)) and isinstance(comparator, ast.Constant):
                        if comparator.value is None:
                            return True
    
    return False


def _generate_test_suggestion(param_name: str, annotation: Optional[ast.expr]) -> str:
    """Generate a test case suggestion for boundary testing."""
    type_str = "Any"
    if annotation:
        # Use ast.unparse for Python 3.9+, fallback to readable representation
        if hasattr(ast, "unparse"):
            type_str = ast.unparse(annotation)
        elif isinstance(annotation, ast.Name):
            type_str = annotation.id
        elif isinstance(annotation, ast.Constant):
            type_str = str(annotation.value)
        else:
            type_str = annotation.__class__.__name__
    
    return f"""
def test_{param_name}_boundary_values():
    # Test boundary values for {param_name} ({type_str})
    boundary_values = generate_boundary_tests("{param_name}", "{type_str}")
    for test_case in boundary_values.boundaries:
        if test_case.is_valid_input:
            # Should not raise
            result = function_under_test({param_name}=test_case.test_value)
        else:
            # Should handle gracefully
            with pytest.raises((ValueError, TypeError)):
                function_under_test({param_name}=test_case.test_value)
""".strip()


def scan_file_for_boundary_issues(file_path: Path) -> List[PatternFinding]:
    """Scan an entire file for boundary validation issues.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        List of boundary-related findings
    """
    findings: List[PatternFinding] = []
    
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, SyntaxError):
        return findings
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            findings.extend(_analyze_function_node(node, str(file_path)))
    
    return findings
