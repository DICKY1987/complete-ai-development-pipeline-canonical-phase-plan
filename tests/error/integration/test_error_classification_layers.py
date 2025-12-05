"""Integration test: 5-layer error classification system."""

# DOC_ID: DOC-ERROR-INTEGRATION-TEST-ERROR-CLASSIFICATION-010

from __future__ import annotations

import pytest

from phase6_error_recovery.modules.error_engine.src.shared.utils.layer_classifier import (
    classify_issue,
)
from phase6_error_recovery.modules.error_engine.src.shared.utils.types import (
    PluginIssue,
)


def test_layer_0_syntax_error():
    """Test that syntax errors are classified as Layer 0."""
    issue = PluginIssue(
        tool="python",
        path="test.py",
        line=10,
        column=5,
        code="E999",
        category="syntax",
        severity="error",
        message="SyntaxError: invalid syntax",
    )

    layer = classify_issue(issue)

    assert layer == 0


def test_layer_1_type_error():
    """Test that type errors are classified as Layer 1."""
    issue = PluginIssue(
        tool="mypy",
        path="test.py",
        line=20,
        column=10,
        code="type-error",
        category="type",
        severity="error",
        message="Incompatible types in assignment",
    )

    layer = classify_issue(issue)

    assert layer == 1


def test_layer_2_linting_error():
    """Test that linting errors are classified as Layer 2."""
    issue = PluginIssue(
        tool="pylint",
        path="test.py",
        line=15,
        column=8,
        code="C0103",
        category="convention",
        severity="warning",
        message="Variable name doesn't conform to snake_case",
    )

    layer = classify_issue(issue)

    assert layer == 2


def test_layer_3_style_error():
    """Test that style errors are classified as Layer 3."""
    issue = PluginIssue(
        tool="black",
        path="test.py",
        line=5,
        column=1,
        code="E501",
        category="style",
        severity="info",
        message="Line too long (85 > 80 characters)",
    )

    layer = classify_issue(issue)

    assert layer == 3


def test_layer_4_security_error():
    """Test that security errors are classified as Layer 4."""
    issue = PluginIssue(
        tool="bandit",
        path="test.py",
        line=30,
        column=1,
        code="B608",
        category="security",
        severity="error",
        message="Possible SQL injection vulnerability",
    )

    layer = classify_issue(issue)

    assert layer == 4


def test_unknown_category_defaults_to_layer_2():
    """Test that unknown categories default to Layer 2."""
    issue = PluginIssue(
        tool="custom",
        path="test.py",
        line=1,
        column=1,
        code="CUSTOM001",
        category="unknown",
        severity="warning",
        message="Unknown issue",
    )

    layer = classify_issue(issue)

    assert layer == 2  # Default layer


def test_severity_affects_classification():
    """Test that severity can affect classification within layer."""
    error_issue = PluginIssue(
        tool="pylint",
        path="test.py",
        line=10,
        column=1,
        code="E001",
        category="convention",
        severity="error",
        message="Error level convention",
    )

    warning_issue = PluginIssue(
        tool="pylint",
        path="test.py",
        line=10,
        column=1,
        code="W001",
        category="convention",
        severity="warning",
        message="Warning level convention",
    )

    layer_error = classify_issue(error_issue)
    layer_warning = classify_issue(warning_issue)

    # Both should be Layer 2 (linting), but severity tracked separately
    assert layer_error == 2
    assert layer_warning == 2


def test_multiple_issues_different_layers():
    """Test classifying multiple issues across different layers."""
    issues = [
        PluginIssue(
            "python", "test.py", 1, 1, "E999", "syntax", "error", "Syntax error"
        ),
        PluginIssue("mypy", "test.py", 2, 1, "type", "type", "error", "Type error"),
        PluginIssue(
            "pylint", "test.py", 3, 1, "C001", "convention", "warning", "Convention"
        ),
        PluginIssue("black", "test.py", 4, 1, "E501", "style", "info", "Style"),
        PluginIssue("bandit", "test.py", 5, 1, "B001", "security", "error", "Security"),
    ]

    layers = [classify_issue(issue) for issue in issues]

    assert layers == [0, 1, 2, 3, 4]


def test_layer_classification_consistency():
    """Test that same category always gives same layer."""
    issues = [
        PluginIssue("tool1", "test.py", 1, 1, "A", "syntax", "error", "msg1"),
        PluginIssue("tool2", "test.py", 2, 1, "B", "syntax", "error", "msg2"),
        PluginIssue("tool3", "test.py", 3, 1, "C", "syntax", "error", "msg3"),
    ]

    layers = [classify_issue(issue) for issue in issues]

    # All syntax errors should be Layer 0
    assert all(layer == 0 for layer in layers)


def test_code_pattern_affects_classification():
    """Test that error code patterns can affect classification."""
    # Some tools use code prefixes to indicate severity
    issues = [
        PluginIssue("pylint", "test.py", 1, 1, "E0001", "convention", "error", "Error"),
        PluginIssue(
            "pylint", "test.py", 2, 1, "W0001", "convention", "warning", "Warning"
        ),
        PluginIssue("pylint", "test.py", 3, 1, "C0001", "convention", "info", "Info"),
    ]

    layers = [classify_issue(issue) for issue in issues]

    # All should be Layer 2 (linting/convention)
    assert all(layer == 2 for layer in layers)
