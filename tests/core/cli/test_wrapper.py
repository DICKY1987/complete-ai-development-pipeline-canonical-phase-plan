"""Tests for CLI wrapper functionality."""
DOC_ID: DOC-CORE-CLI-TEST-WRAPPER-875

import tempfile
from pathlib import Path
import pytest

from core.cli.wrapper import CLIWrapper, ExecutionResult


def test_cli_wrapper_python_script():
    """Test wrapping a Python script."""
    wrapper = CLIWrapper(timeout=10)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('print("Hello from test script")\n')
        f.write('exit(0)\n')
        script_path = f.name
    
    try:
        result = wrapper.wrap(script_path, args=[])
        
        assert result.exit_code == 0
        assert result.succeeded
        assert "Hello from test script" in result.stdout
        assert result.timed_out is False
    finally:
        Path(script_path).unlink()


def test_cli_wrapper_timeout():
    """Test script timeout handling."""
    wrapper = CLIWrapper(timeout=1)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('import time\n')
        f.write('time.sleep(10)\n')
        script_path = f.name
    
    try:
        result = wrapper.wrap(script_path, args=[])
        
        assert result.exit_code == -1
        assert not result.succeeded
        assert result.timed_out is True
    finally:
        Path(script_path).unlink()


def test_cli_wrapper_non_interactive_mode():
    """Test NON_INTERACTIVE environment variable is set."""
    wrapper = CLIWrapper()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('import os\n')
        f.write('print(os.environ.get("NON_INTERACTIVE", "not_set"))\n')
        script_path = f.name
    
    try:
        result = wrapper.wrap(script_path, non_interactive=True)
        
        assert result.exit_code == 0
        assert "1" in result.stdout
    finally:
        Path(script_path).unlink()


def test_cli_wrapper_execution_logging():
    """Test that executions are logged."""
    with tempfile.TemporaryDirectory() as tmpdir:
        state_dir = Path(tmpdir) / ".state"
        wrapper = CLIWrapper(state_dir=state_dir)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('print("test")\n')
            script_path = f.name
        
        try:
            wrapper.wrap(script_path)
            
            log_file = state_dir / "cli_executions.jsonl"
            assert log_file.exists()
            
            content = log_file.read_text()
            assert 'test' in content
        finally:
            Path(script_path).unlink()


def test_cli_wrapper_failed_script():
    """Test handling of failed scripts."""
    wrapper = CLIWrapper()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('exit(1)\n')
        script_path = f.name
    
    try:
        result = wrapper.wrap(script_path)
        
        assert result.exit_code == 1
        assert not result.succeeded
    finally:
        Path(script_path).unlink()
