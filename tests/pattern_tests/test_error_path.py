"""Tests for error path coverage patterns."""
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

from error.patterns.error_path import (
    analyze_error_paths,
    generate_error_path_checklist,
    scan_file_for_error_path_issues,
    EXTERNAL_CALL_PATTERNS,
)
from error.patterns.types import PatternCategory, PatternSeverity


class TestExternalCallPatterns:
    """Test external call pattern detection."""
# DOC_ID: DOC-TEST-PATTERN-TESTS-TEST-ERROR-PATH-131

    def test_http_patterns_defined(self):
        """HTTP call patterns should be defined."""
        assert "requests.get" in EXTERNAL_CALL_PATTERNS
        assert "requests.post" in EXTERNAL_CALL_PATTERNS

    def test_database_patterns_defined(self):
        """Database call patterns should be defined."""
        assert "cursor.execute" in EXTERNAL_CALL_PATTERNS
        assert ".fetchone" in EXTERNAL_CALL_PATTERNS

    def test_file_patterns_defined(self):
        """File operation patterns should be defined."""
        assert "open" in EXTERNAL_CALL_PATTERNS
        assert "json.loads" in EXTERNAL_CALL_PATTERNS


class TestAnalyzeErrorPaths:
    """Test error path analysis."""

    def test_detect_unhandled_http_call(self):
        """Detect HTTP call without error handling."""
        code = '''
import requests

def fetch_data(url):
    response = requests.get(url)
    return response.json()
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()

            findings = analyze_error_paths(Path(f.name))

            # Should find unhandled HTTP call
            http_findings = [
                f for f in findings
                if PatternCategory.ERROR_PATH == f.pattern_category
            ]
            assert len(http_findings) > 0

    def test_handled_http_call_no_finding(self):
        """No finding for properly handled HTTP call."""
        code = '''
import requests

def fetch_data(url):
    try:
        response = requests.get(url, timeout=30)
        return response.json()
    except requests.RequestException as e:
        return None
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()

            findings = analyze_error_paths(Path(f.name))

            # Should not find issues (call is in try block)
            assert all(f.code != "EPC-004" for f in findings)  # No exception handling issue

    def test_detect_bare_except(self):
        """Detect bare except clause."""
        code = '''
def risky_operation():
    try:
        do_something()
    except:
        pass
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()

            findings = analyze_error_paths(Path(f.name))

            # Should find bare except
            bare_except_findings = [
                f for f in findings
                if "EPC-006" in f.code or "bare" in f.message.lower()
            ]
            assert len(bare_except_findings) > 0

    def test_detect_unhandled_json_parse(self):
        """Detect JSON parsing without error handling."""
        code = '''
import json

def parse_config(data):
    config = json.loads(data)
    return config
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()

            findings = analyze_error_paths(Path(f.name))

            # Should find unhandled json.loads
            json_findings = [
                f for f in findings
                if "json" in f.message.lower() or "malformed" in f.message.lower()
            ]
            assert len(json_findings) > 0


class TestErrorPathChecklist:
    """Test error path checklist generation."""

    def test_generate_checklist_for_file(self):
        """Generate checklist for file with external calls."""
        code = '''
import requests
import json

def process():
    response = requests.get("http://api.example.com")
    data = json.loads(response.text)
    return data
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()

            checklist = generate_error_path_checklist(Path(f.name))

            # Should have checks for HTTP and JSON calls
            assert len(checklist) > 0

            check_types = [c.check_type for c in checklist]
            assert "exception" in check_types or "timeout" in check_types

    def test_checklist_marks_uncovered(self):
        """Checklist marks uncovered error paths."""
        code = '''
import requests

def fetch():
    return requests.get("http://example.com")
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()

            checklist = generate_error_path_checklist(Path(f.name))

            # Should have uncovered checks
            uncovered = [c for c in checklist if not c.is_covered]
            assert len(uncovered) > 0


class TestScanFileForErrorPathIssues:
    """Test file scanning convenience function."""

    def test_scan_returns_findings(self):
        """Scan file returns findings list."""
        code = '''
def simple_func():
    open("file.txt").read()
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()

            findings = scan_file_for_error_path_issues(Path(f.name))

            assert isinstance(findings, list)

    def test_scan_empty_file(self):
        """Scan empty file returns empty list."""
        code = '# Empty file\n'

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()

            findings = scan_file_for_error_path_issues(Path(f.name))

            assert findings == []
