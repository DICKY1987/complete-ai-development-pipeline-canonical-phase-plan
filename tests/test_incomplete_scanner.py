"""
Test suite for incomplete implementation scanner.


DOC_ID: DOC-TEST-TESTS-TEST-INCOMPLETE-SCANNER-349
"""

import ast
import sys
from pathlib import Path
from textwrap import dedent

import pytest

# Add scripts to path for import
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from scan_incomplete_implementation import (
    AllowlistConfig,
    Finding,
    calculate_severity,
    check_class_stub,
    check_function_stub,
    detect_pattern_stubs,
    is_allowed_stub,
)


class TestFunctionStubDetection:
    """Test detection of function stubs."""

    def test_detect_pass_stub(self):
        """Should detect function with only pass."""
        code = dedent(
            """
            def my_function():
                pass
        """
        )
        tree = ast.parse(code)
        func = tree.body[0]

        finding = check_function_stub(func, Path("test.py"))

        assert finding is not None
        assert finding.kind == "stub_function"
        assert finding.reason == "function_body_is_pass"
        assert finding.symbol == "my_function"

    def test_detect_ellipsis_stub(self):
        """Should detect function with only ellipsis."""
        code = dedent(
            """
            def my_function():
                ...
        """
        )
        tree = ast.parse(code)
        func = tree.body[0]

        finding = check_function_stub(func, Path("test.py"))

        assert finding is not None
        assert finding.reason == "function_body_is_ellipsis"

    def test_detect_not_implemented_stub(self):
        """Should detect function that raises NotImplementedError."""
        code = dedent(
            """
            def my_function():
                raise NotImplementedError("Not yet implemented")
        """
        )
        tree = ast.parse(code)
        func = tree.body[0]

        finding = check_function_stub(func, Path("test.py"))

        assert finding is not None
        assert finding.reason == "raises_not_implemented_error"

    def test_ignore_real_implementation(self):
        """Should not flag functions with real logic."""
        code = dedent(
            """
            def my_function():
                x = 1 + 2
                return x * 3
        """
        )
        tree = ast.parse(code)
        func = tree.body[0]

        finding = check_function_stub(func, Path("test.py"))

        assert finding is None

    def test_ignore_docstring_only(self):
        """Should not flag docstring-only as stub (handled separately)."""
        code = dedent(
            """
            def my_function():
                \"\"\"This is a docstring.\"\"\"
                pass
        """
        )
        tree = ast.parse(code)
        func = tree.body[0]

        finding = check_function_stub(func, Path("test.py"))

        # Should still detect the pass after docstring
        assert finding is not None


class TestClassStubDetection:
    """Test detection of class stubs."""

    def test_detect_all_stub_methods(self):
        """Should detect class where all methods are stubs."""
        code = dedent(
            """
            class MyClass:
                def method1(self):
                    pass

                def method2(self):
                    raise NotImplementedError
        """
        )
        tree = ast.parse(code)
        cls = tree.body[0]

        finding = check_class_stub(cls, Path("test.py"))

        assert finding is not None
        assert finding.kind == "stub_class"
        assert finding.symbol == "MyClass"

    def test_ignore_mixed_implementation(self):
        """Should not flag class with some real implementations."""
        code = dedent(
            """
            class MyClass:
                def real_method(self):
                    return 42

                def stub_method(self):
                    pass
        """
        )
        tree = ast.parse(code)
        cls = tree.body[0]

        finding = check_class_stub(cls, Path("test.py"))

        assert finding is None


class TestPatternDetection:
    """Test pattern-based stub detection."""

    def test_detect_todo_markers(self):
        """Should detect TODO comments."""
        content = dedent(
            """
            def my_function():
                # TODO: implement this
                pass
        """
        )

        findings = detect_pattern_stubs(content, Path("test.py"))

        todo_findings = [f for f in findings if f.kind == "todo_marker"]
        assert len(todo_findings) > 0
        assert "TODO" in todo_findings[0].body_preview

    def test_detect_fixme_markers(self):
        """Should detect FIXME comments."""
        content = "# FIXME: This is broken\n"

        findings = detect_pattern_stubs(content, Path("test.py"))

        assert len(findings) > 0
        assert "FIXME" in findings[0].body_preview


class TestSeverityScoring:
    """Test severity calculation."""

    def test_critical_severity_for_core_modules(self):
        """Core modules should get critical severity."""
        finding = Finding(
            kind="stub_function",
            path="core/engine/executor.py",
            symbol="execute",
            reason="function_body_is_pass",
        )

        severity, score = calculate_severity(finding, Path("."))

        assert severity == "critical"
        assert score == 3.0

    def test_major_severity_for_domain_modules(self):
        """Domain modules should get major severity."""
        finding = Finding(
            kind="stub_function",
            path="aim/bridge.py",
            symbol="process",
            reason="function_body_is_pass",
        )

        severity, score = calculate_severity(finding, Path("."))

        assert severity == "major"
        assert score == 2.0

    def test_minor_severity_for_other_modules(self):
        """Other modules should get minor severity."""
        finding = Finding(
            kind="stub_function",
            path="utils/helper.py",
            symbol="helper_func",
            reason="function_body_is_pass",
        )

        severity, score = calculate_severity(finding, Path("."))

        assert severity == "minor"
        assert score == 1.0


class TestWhitelistMechanism:
    """Test whitelist/allowlist mechanism."""

    def test_allowed_patterns(self):
        """Should recognize allowed patterns."""
        finding = Finding(
            kind="stub_function",
            path="tests/fixtures/dummy.py",
            symbol="fixture",
            reason="function_body_is_pass",
        )

        allowlist = AllowlistConfig(path_patterns=["tests/fixtures/**/*.py"])
        is_allowed = is_allowed_stub("tests/fixtures/dummy.py", finding, allowlist, {})

        assert is_allowed is True

    def test_archived_code_allowed(self):
        """Archived code should be allowed."""
        finding = Finding(
            kind="stub_function",
            path="_ARCHIVE/old_code.py",
            symbol="old_func",
            reason="function_body_is_pass",
        )

        allowlist = AllowlistConfig(path_patterns=["_ARCHIVE/**/*"])
        is_allowed = is_allowed_stub("_ARCHIVE/old_code.py", finding, allowlist, {})

        assert is_allowed is True

    def test_inline_marker_detection(self):
        """Should detect INCOMPLETE_OK marker."""
        finding = Finding(
            kind="stub_function",
            path="core/interface.py",
            symbol="abstract_method",
            reason="function_body_is_pass",
            body_preview="# INCOMPLETE_OK: Abstract interface",
        )

        allowlist = AllowlistConfig()
        is_allowed = is_allowed_stub(
            "core/interface.py",
            finding,
            allowlist,
            {"core/interface.py": finding.body_preview},
        )

        assert is_allowed is True

    def test_allowed_severity_downgrade(self):
        """calculate_severity should downgrade to allowed_stub when allowlisted."""
        finding = Finding(
            kind="stub_function",
            path="docs/examples/demo.py",
            symbol="demo",
            reason="function_body_is_pass",
            body_preview="# STUB_ALLOWED",
        )
        allowlist = AllowlistConfig(path_patterns=["docs/examples/**/*"])

        severity, _ = calculate_severity(
            finding,
            Path("."),
            allowlist,
            {"docs/examples/demo.py": finding.body_preview},
        )

        assert severity == "allowed_stub"


class TestEndToEnd:
    """End-to-end integration tests."""

    def test_scan_sample_file(self, tmp_path):
        """Should scan a complete file and find multiple issues."""
        test_file = tmp_path / "sample.py"
        test_file.write_text(
            dedent(
                """
            # Sample file with multiple stub types

            def implemented_function():
                return 42

            def stub_function_pass():
                pass

            def stub_function_ellipsis():
                ...

            def stub_function_not_implemented():
                raise NotImplementedError

            class StubClass:
                def method1(self):
                    pass

                def method2(self):
                    raise NotImplementedError

            class MixedClass:
                def real_method(self):
                    return "real"

                def stub_method(self):
                    pass

            # TODO: Add more functionality
        """
            )
        )

        from scan_incomplete_implementation import (
            detect_pattern_stubs,
            detect_python_stubs,
        )

        content = test_file.read_text()
        findings = []
        findings.extend(detect_python_stubs(test_file, content))
        findings.extend(detect_pattern_stubs(content, test_file))

        # Should find 3 stub functions + 1 stub class + TODO marker
        stub_functions = [f for f in findings if f.kind == "stub_function"]
        stub_classes = [f for f in findings if f.kind == "stub_class"]
        todo_markers = [f for f in findings if f.kind == "todo_marker"]

        assert len(stub_functions) >= 3
        assert len(stub_classes) >= 1
        assert len(todo_markers) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
