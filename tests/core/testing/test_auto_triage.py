"""Tests for test auto-triage functionality."""

import pytest
from core.testing.auto_triage import TestTriage, FailureCategory


def test_classify_import_error():
    """Test classification of import errors."""
    triage = TestTriage()
    
    output = "ImportError: No module named 'requests'"
    result = triage.classify_failure(output)
    
    assert result.category == FailureCategory.IMPORT_ERROR
    assert result.auto_fixable is True
    assert result.recommended_action == "create_error_recovery_task"
    assert result.details['missing_module'] == 'requests'


def test_classify_syntax_error():
    """Test classification of syntax errors."""
    triage = TestTriage()
    
    output = "SyntaxError: invalid syntax at line 42"
    result = triage.classify_failure(output)
    
    assert result.category == FailureCategory.SYNTAX_ERROR
    assert result.auto_fixable is True


def test_classify_assertion_error():
    """Test classification of assertion errors."""
    triage = TestTriage()
    
    output = "AssertionError: assert 5 == 10"
    result = triage.classify_failure(output)
    
    assert result.category == FailureCategory.ASSERTION_ERROR
    assert result.auto_fixable is False
    assert result.recommended_action == "analyze_logic_bug"


def test_classify_timeout():
    """Test classification of timeout errors."""
    triage = TestTriage()
    
    output = "TimeoutError: Operation timed out after 30 seconds"
    result = triage.classify_failure(output)
    
    assert result.category == FailureCategory.TIMEOUT
    assert result.recommended_action == "increase_timeout_or_optimize"


def test_classify_known_flaky():
    """Test detection of known flaky tests."""
    triage = TestTriage(known_flaky_tests=["test_network_"])
    
    result = triage.classify_failure(
        "Some error",
        test_name="test_network_connection"
    )
    
    assert result.category == FailureCategory.KNOWN_FLAKY
    assert result.recommended_action == "skip_and_log"


def test_classify_unknown():
    """Test classification of unknown errors."""
    triage = TestTriage()
    
    output = "SomeWeirdError: this is unusual"
    result = triage.classify_failure(output)
    
    assert result.category == FailureCategory.UNKNOWN
    assert result.auto_fixable is False
    assert result.recommended_action == "manual_review"


def test_triage_batch():
    """Test batch triage of multiple failures."""
    triage = TestTriage()
    
    test_results = [
        {"name": "test_1", "output": "ImportError: No module named 'foo'"},
        {"name": "test_2", "output": "AssertionError: assert False"},
        {"name": "test_3", "output": "SyntaxError: invalid syntax"}
    ]
    
    results = triage.triage_batch(test_results)
    
    assert len(results) == 3
    assert results[0].category == FailureCategory.IMPORT_ERROR
    assert results[1].category == FailureCategory.ASSERTION_ERROR
    assert results[2].category == FailureCategory.SYNTAX_ERROR


def test_get_auto_fixable_failures():
    """Test filtering for auto-fixable failures."""
    triage = TestTriage()
    
    test_results = [
        {"name": "test_1", "output": "ImportError: No module named 'foo'"},
        {"name": "test_2", "output": "AssertionError: assert False"},
        {"name": "test_3", "output": "SyntaxError: invalid syntax"}
    ]
    
    auto_fixable = triage.get_auto_fixable_failures(test_results)
    
    assert len(auto_fixable) == 2  # Import and Syntax errors
    assert all(r.auto_fixable for r in auto_fixable)
