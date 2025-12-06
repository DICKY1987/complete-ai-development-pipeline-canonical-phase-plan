"""Tests for base adapter interface - WS-03-02A"""

import sys
from pathlib import Path

import pytest

# Add framework root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.adapters.base import ExecutionResult, ToolConfig


class TestToolConfig:
    """Test ToolConfig functionality"""

    # DOC_ID: DOC-TEST-ADAPTERS-TEST-BASE-INSTANCE-TEST-001

    def test_create_tool_config(self):
        """Test creating a tool config"""
        config = ToolConfig(
            tool_id="aider",
            kind="tool",
            command="aider --yes",
            capabilities={
                "task_kinds": ["code_edit", "refactor"],
                "domains": ["python", "javascript"],
            },
        )

        assert config.tool_id == "aider"
        assert config.kind == "tool"
        assert config.command == "aider --yes"

    def test_supports_task_matching(self):
        """Test task kind matching"""
        config = ToolConfig(
            tool_id="test",
            kind="tool",
            command="echo",
            capabilities={"task_kinds": ["code_edit", "analysis"]},
        )

        assert config.supports_task("code_edit")
        assert config.supports_task("analysis")
        assert not config.supports_task("deployment")

    def test_supports_task_with_domain(self):
        """Test domain filtering"""
        config = ToolConfig(
            tool_id="test",
            kind="tool",
            command="echo",
            capabilities={"task_kinds": ["code_edit"], "domains": ["python", "rust"]},
        )

        assert config.supports_task("code_edit", "python")
        assert config.supports_task("code_edit", "rust")
        assert not config.supports_task("code_edit", "javascript")

    def test_get_timeout_default(self):
        """Test default timeout"""
        config = ToolConfig(
            tool_id="test", kind="tool", command="echo", capabilities={}
        )

        assert config.get_timeout() == 300  # 5 minutes

    def test_get_timeout_custom(self):
        """Test custom timeout"""
        config = ToolConfig(
            tool_id="test",
            kind="tool",
            command="echo",
            capabilities={},
            limits={"timeout_seconds": 60},
        )

        assert config.get_timeout() == 60

    def test_get_max_parallel_default(self):
        """Test default max parallel"""
        config = ToolConfig(
            tool_id="test", kind="tool", command="echo", capabilities={}
        )

        assert config.get_max_parallel() == 1

    def test_get_max_parallel_custom(self):
        """Test custom max parallel"""
        config = ToolConfig(
            tool_id="test",
            kind="tool",
            command="echo",
            capabilities={},
            limits={"max_parallel": 4},
        )

        assert config.get_max_parallel() == 4


class TestExecutionResult:
    """Test ExecutionResult functionality"""

    def test_create_success_result(self):
        """Test creating a successful result"""
        result = ExecutionResult(
            success=True, stdout="Hello World", exit_code=0, duration_seconds=1.5
        )

        assert result.success
        assert result.stdout == "Hello World"
        assert result.exit_code == 0
        assert result.duration_seconds == 1.5

    def test_create_failure_result(self):
        """Test creating a failure result"""
        result = ExecutionResult(
            success=False,
            stderr="Error occurred",
            exit_code=1,
            error_message="Command failed",
        )

        assert not result.success
        assert result.stderr == "Error occurred"
        assert result.exit_code == 1
        assert result.error_message == "Command failed"

    def test_to_dict(self):
        """Test converting result to dict"""
        result = ExecutionResult(
            success=True, stdout="output", metadata={"tool": "test"}
        )

        d = result.to_dict()
        assert d["success"] is True
        assert d["stdout"] == "output"
        assert d["metadata"] == {"tool": "test"}
