"""Tests for subprocess adapter - WS-03-02A"""

import pytest
import sys
from pathlib import Path

# Add framework root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.adapters.base import ToolConfig
from core.adapters.subprocess_adapter import SubprocessAdapter


class TestSubprocessAdapter:
    """Test SubprocessAdapter functionality"""

    # DOC_ID: DOC-TEST-ADAPTERS-TEST-SUBPROCESS-ADAPTER-168

    def test_create_adapter(self):
        """Test creating a subprocess adapter"""
        config = ToolConfig(
            tool_id="echo",
            kind="tool",
            command="echo test",
            capabilities={"task_kinds": ["test"]},
        )

        adapter = SubprocessAdapter(config)
        assert adapter.config.tool_id == "echo"

    def test_validate_request_valid(self):
        """Test validating a valid request"""
        config = ToolConfig(
            tool_id="test", kind="tool", command="echo", capabilities={}
        )
        adapter = SubprocessAdapter(config)

        request = {
            "request_id": "01234567890123456789012345",
            "task_kind": "test",
            "project_id": "test-project",
        }

        assert adapter.validate_request(request)

    def test_validate_request_missing_fields(self):
        """Test validating request with missing fields"""
        config = ToolConfig(
            tool_id="test", kind="tool", command="echo", capabilities={}
        )
        adapter = SubprocessAdapter(config)

        request = {
            "request_id": "01234567890123456789012345",
        }

        assert not adapter.validate_request(request)

    def test_execute_success(self):
        """Test executing a successful command"""
        # Use Python executable to echo text (cross-platform)
        config = ToolConfig(
            tool_id="python",
            kind="tool",
            command=f'{sys.executable} -c "print(\\"Hello World\\")"',
            capabilities={"task_kinds": ["test"]},
        )
        adapter = SubprocessAdapter(config)

        request = {
            "request_id": "01234567890123456789012345",
            "task_kind": "test",
            "project_id": "test",
        }

        result = adapter.execute(request)

        assert result.success
        assert "Hello World" in result.stdout
        assert result.exit_code == 0
        assert result.duration_seconds > 0

    def test_execute_failure(self):
        """Test executing a failing command"""
        # Use Python to exit with error code
        config = ToolConfig(
            tool_id="python",
            kind="tool",
            command=f'{sys.executable} -c "import sys; sys.exit(1)"',
            capabilities={"task_kinds": ["test"]},
        )
        adapter = SubprocessAdapter(config)

        request = {
            "request_id": "01234567890123456789012345",
            "task_kind": "test",
            "project_id": "test",
        }

        result = adapter.execute(request)

        assert not result.success
        assert result.exit_code == 1

    def test_execute_timeout(self):
        """Test command timeout"""
        # Use Python to sleep longer than timeout
        config = ToolConfig(
            tool_id="python",
            kind="tool",
            command=f'{sys.executable} -c "import time; time.sleep(10)"',
            capabilities={"task_kinds": ["test"]},
            limits={"timeout_seconds": 1},
        )
        adapter = SubprocessAdapter(config)

        request = {
            "request_id": "01234567890123456789012345",
            "task_kind": "test",
            "project_id": "test",
        }

        result = adapter.execute(request, timeout=1)

        assert not result.success
        assert "timed out" in result.error_message.lower()
        assert result.metadata.get("timeout_exceeded") is True

    def test_execute_invalid_request(self):
        """Test executing with invalid request"""
        config = ToolConfig(
            tool_id="test", kind="tool", command="echo", capabilities={}
        )
        adapter = SubprocessAdapter(config)

        result = adapter.execute({})

        assert not result.success
        assert "Invalid request" in result.error_message

    def test_supports_task(self):
        """Test task support checking"""
        config = ToolConfig(
            tool_id="test",
            kind="tool",
            command="echo",
            capabilities={"task_kinds": ["code_edit", "refactor"]},
        )
        adapter = SubprocessAdapter(config)

        assert adapter.supports_task("code_edit")
        assert adapter.supports_task("refactor")
        assert not adapter.supports_task("deployment")
