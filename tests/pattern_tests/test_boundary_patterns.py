"""Tests for boundary value analysis patterns."""
from __future__ import annotations

import sys
from pathlib import Path

# Add project root to Python path for imports
_test_file = Path(__file__).resolve()
_repo_root = _test_file.parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

import pytest
import tempfile

from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.patterns.boundary_patterns import (
    BOUNDARY_PATTERNS,
    generate_boundary_tests,
    scan_file_for_boundary_issues,
    analyze_function_boundaries,
)
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.patterns.types import PatternCategory, PatternSeverity


class TestBoundaryPatterns:
    """Test boundary pattern detection."""
# DOC_ID: DOC-TEST-PATTERN-TESTS-TEST-BOUNDARY-PATTERNS-130
    
    def test_boundary_patterns_exist(self):
        """Verify boundary patterns are defined for common types."""
        assert "int" in BOUNDARY_PATTERNS
        assert "str" in BOUNDARY_PATTERNS
        assert "float" in BOUNDARY_PATTERNS
        assert "list" in BOUNDARY_PATTERNS
        assert "dict" in BOUNDARY_PATTERNS
    
    def test_int_boundaries_include_edge_cases(self):
        """Verify int boundaries include critical values."""
        int_patterns = BOUNDARY_PATTERNS["int"]
        categories = [p["category"] for p in int_patterns]
        
        assert "min" in categories
        assert "max" in categories
        assert "zero" in categories
        assert "negative_one" in categories
    
    def test_str_boundaries_include_edge_cases(self):
        """Verify string boundaries include critical values."""
        str_patterns = BOUNDARY_PATTERNS["str"]
        categories = [p["category"] for p in str_patterns]
        
        assert "empty" in categories
        assert "single_char" in categories
        assert "special_chars" in categories
        assert "sql_injection" in categories
        assert "xss" in categories


class TestGenerateBoundaryTests:
    """Test boundary test case generation."""
    
    def test_generate_int_boundaries(self):
        """Generate boundary tests for int parameter."""
        spec = generate_boundary_tests("count", "int")
        
        assert spec.param_type == "int"
        assert len(spec.boundaries) > 0
        
        # Check we have min/max boundaries
        categories = [b.test_category for b in spec.boundaries]
        assert "min" in categories
        assert "max" in categories
    
    def test_generate_str_boundaries(self):
        """Generate boundary tests for str parameter."""
        spec = generate_boundary_tests("name", "str")
        
        assert spec.param_type == "str"
        assert len(spec.boundaries) > 0
        
        # Should include empty and special chars
        categories = [b.test_category for b in spec.boundaries]
        assert "empty" in categories
        assert "special_chars" in categories
    
    def test_generate_with_constraints(self):
        """Generate boundaries with custom constraints."""
        spec = generate_boundary_tests(
            "age",
            "int",
            constraints={"min": 0, "max": 150}
        )
        
        # Should include constraint-specific boundaries
        categories = [b.test_category for b in spec.boundaries]
        assert "constraint_min" in categories
        assert "constraint_max" in categories
    
    def test_generate_with_max_length(self):
        """Generate boundaries for string with max_length."""
        spec = generate_boundary_tests(
            "username",
            "str",
            constraints={"max_length": 50}
        )
        
        categories = [b.test_category for b in spec.boundaries]
        assert "constraint_maxlen" in categories
        assert "constraint_maxlen_plus_1" in categories


class TestScanFileForBoundaryIssues:
    """Test file scanning for boundary issues."""
    
    def test_detect_unvalidated_parameter(self):
        """Detect function with unvalidated parameter."""
        code = '''
def process_data(value):
    """Process the value."""
    return value * 2
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            findings = scan_file_for_boundary_issues(Path(f.name))
            
            # Should find the unvalidated parameter
            assert len(findings) > 0
            assert findings[0].pattern_category == PatternCategory.BOUNDARY_VALUE
    
    def test_validated_parameter_no_finding(self):
        """No finding for validated parameter."""
        code = '''
def process_data(value):
    """Process the value."""
    if value is None:
        raise ValueError("value cannot be None")
    if value < 0:
        raise ValueError("value must be non-negative")
    return value * 2
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            findings = scan_file_for_boundary_issues(Path(f.name))
            
            # Should not report issue since parameter is validated
            param_findings = [f for f in findings if "value" in f.message]
            assert len(param_findings) == 0
    
    def test_skip_self_parameter(self):
        """Don't report findings for 'self' parameter."""
        code = '''
class MyClass:
    def method(self, data):
        return data
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            findings = scan_file_for_boundary_issues(Path(f.name))
            
            # Should not have findings for 'self'
            self_findings = [f for f in findings if "'self'" in f.message]
            assert len(self_findings) == 0
