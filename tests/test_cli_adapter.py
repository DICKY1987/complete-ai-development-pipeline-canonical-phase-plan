"""Tests for CLIAdapter."""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import CLIAdapter


def test_cli_adapter_initialization():
    """Test CLIAdapter initialization."""
    adapter = CLIAdapter()
    assert adapter is not None
    assert adapter.execution_history == []
    print("✅ test_cli_adapter_initialization passed")


def test_run_simple_command():
    """Test running a simple command."""
    adapter = CLIAdapter(logger=lambda x: None)  # Silent logger
    result = adapter.run_command("python --version")
    assert result["success"] is True
    assert "Python" in result["stdout"]
    print("✅ test_run_simple_command passed")


def test_run_script_success():
    """Test running a successful script."""
    adapter = CLIAdapter(logger=lambda x: None)
    test_script = Path("test_temp.py")
    test_script.write_text('print("test output")')
    
    result = adapter.run_script(test_script)
    test_script.unlink()
    
    assert result["success"] is True
    assert "test output" in result["stdout"]
    print("✅ test_run_script_success passed")


def test_execution_summary():
    """Test execution summary."""
    adapter = CLIAdapter(logger=lambda x: None)
    adapter.run_command("python --version")
    
    summary = adapter.get_execution_summary()
    assert summary["total_executions"] >= 1
    assert summary["successful"] >= 0
    print("✅ test_execution_summary passed")


if __name__ == "__main__":
    print("Running CLIAdapter tests...")
    test_cli_adapter_initialization()
    test_run_simple_command()
    test_run_script_success()
    test_execution_summary()
    print("\n✅ All tests passed!")
