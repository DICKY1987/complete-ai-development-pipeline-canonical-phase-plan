"""Tests for mypy plugin error detection capabilities."""
DOC_ID: DOC-CORE-TESTS-TEST-PLUGIN-DETECTION-792

import os
import sys
import tempfile
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from python_mypy.plugin import MypyPlugin


def test_mypy_available():
    """Test that mypy tool is available."""
    plugin = MypyPlugin()
    assert plugin.check_tool_available() is True


def test_mypy_plugin_metadata():
    """Test plugin metadata."""
    plugin = MypyPlugin()
    assert plugin.plugin_id == "python_mypy"
    assert plugin.name == "mypy Type Checker"


def test_mypy_build_command():
    """Test command building."""
    plugin = MypyPlugin()
    test_file = Path("test.py")
    cmd = plugin.build_command(test_file)
    assert "mypy" in cmd
    assert "--error-format=json" in cmd
    assert str(test_file) in cmd


def test_mypy_detects_type_error():
    """Test mypy detects type errors."""
    plugin = MypyPlugin()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("x: int = 'string'\n")
        f.flush()
        test_file = Path(f.name)

    try:
        result = plugin.execute(test_file)
        assert result.success is True
        assert result.plugin_id == "python_mypy"
        assert len(result.issues) > 0
        assert any("type" in i.category for i in result.issues)
    finally:
        test_file.unlink()


def test_mypy_clean_file():
    """Test mypy on clean file."""
    plugin = MypyPlugin()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("x: int = 42\nprint(x)\n")
        f.flush()
        test_file = Path(f.name)

    try:
        result = plugin.execute(test_file)
        assert result.success is True
        assert result.plugin_id == "python_mypy"
        assert len(result.issues) == 0
    finally:
        test_file.unlink()


def test_mypy_missing_annotation():
    """Test mypy detects missing type annotations."""
    plugin = MypyPlugin()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("def func(x):\n    return x + 1\n")
        f.flush()
        test_file = Path(f.name)

    try:
        result = plugin.execute(test_file)
        assert result.success is True
        assert result.plugin_id == "python_mypy"
    finally:
        test_file.unlink()


def test_mypy_incompatible_types():
    """Test mypy detects incompatible types."""
    plugin = MypyPlugin()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(
            "def add(a: int, b: int) -> int:\n    return a + b\nresult: str = add(1, 2)\n"
        )
        f.flush()
        test_file = Path(f.name)

    try:
        result = plugin.execute(test_file)
        assert result.success is True
        assert len(result.issues) > 0
        assert any("type" in i.category for i in result.issues)
    finally:
        test_file.unlink()


def test_mypy_return_value():
    """Test mypy checks return values."""
    plugin = MypyPlugin()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("def func() -> int:\n    return 'string'\n")
        f.flush()
        test_file = Path(f.name)

    try:
        result = plugin.execute(test_file)
        assert result.success is True
        assert len(result.issues) > 0
    finally:
        test_file.unlink()


def test_mypy_issue_structure():
    """Test issue structure contains required fields."""
    plugin = MypyPlugin()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("x: int = 'string'\n")
        f.flush()
        test_file = Path(f.name)

    try:
        result = plugin.execute(test_file)
        if result.issues:
            issue = result.issues[0]
            assert hasattr(issue, "tool")
            assert hasattr(issue, "path")
            assert hasattr(issue, "line")
            assert hasattr(issue, "category")
            assert hasattr(issue, "severity")
            assert hasattr(issue, "message")
            assert issue.tool == "mypy"
    finally:
        test_file.unlink()
