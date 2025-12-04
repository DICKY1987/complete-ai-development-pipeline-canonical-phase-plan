"""Tests for adapter registry - WS-03-02A"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add framework root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.adapters.base import ToolConfig
from core.adapters.registry import AdapterRegistry
from core.adapters.subprocess_adapter import SubprocessAdapter


class TestAdapterRegistry:
    """Test AdapterRegistry functionality"""

    # DOC_ID: DOC-TEST-ADAPTERS-TEST-REGISTRY-167

    def test_create_empty_registry(self):
        """Test creating an empty registry"""
        registry = AdapterRegistry()
        assert len(registry.adapters) == 0

    def test_register_adapter(self):
        """Test registering an adapter"""
        registry = AdapterRegistry()

        config = ToolConfig(
            tool_id="test", kind="tool", command="echo", capabilities={}
        )
        adapter = SubprocessAdapter(config)

        registry.register("test", adapter)

        assert "test" in registry.adapters
        assert registry.get("test") == adapter

    def test_get_nonexistent_adapter(self):
        """Test getting adapter that doesn't exist"""
        registry = AdapterRegistry()
        assert registry.get("nonexistent") is None

    def test_list_tools(self):
        """Test listing all tool IDs"""
        registry = AdapterRegistry()

        for tool_id in ["tool1", "tool2", "tool3"]:
            config = ToolConfig(
                tool_id=tool_id, kind="tool", command="echo", capabilities={}
            )
            adapter = SubprocessAdapter(config)
            registry.register(tool_id, adapter)

        tools = registry.list_tools()
        assert len(tools) == 3
        assert "tool1" in tools
        assert "tool2" in tools
        assert "tool3" in tools

    def test_get_config(self):
        """Test getting tool config"""
        registry = AdapterRegistry()

        config = ToolConfig(
            tool_id="test",
            kind="validator",
            command="ruff",
            capabilities={"task_kinds": ["lint"]},
        )
        adapter = SubprocessAdapter(config)
        registry.register("test", adapter)

        retrieved_config = registry.get_config("test")
        assert retrieved_config is not None
        assert retrieved_config.tool_id == "test"
        assert retrieved_config.kind == "validator"

    def test_find_for_task_basic(self):
        """Test finding adapters for a task"""
        registry = AdapterRegistry()

        # Register tool that supports code_edit
        config1 = ToolConfig(
            tool_id="editor",
            kind="tool",
            command="echo",
            capabilities={"task_kinds": ["code_edit"]},
        )
        registry.register("editor", SubprocessAdapter(config1))

        # Register tool that doesn't support code_edit
        config2 = ToolConfig(
            tool_id="linter",
            kind="validator",
            command="lint",
            capabilities={"task_kinds": ["lint"]},
        )
        registry.register("linter", SubprocessAdapter(config2))

        # Find tools for code_edit
        capable = registry.find_for_task("code_edit")
        assert len(capable) == 1
        assert capable[0].config.tool_id == "editor"

    def test_find_for_task_with_domain(self):
        """Test finding adapters with domain filter"""
        registry = AdapterRegistry()

        # Python editor
        config1 = ToolConfig(
            tool_id="python-editor",
            kind="tool",
            command="echo",
            capabilities={"task_kinds": ["code_edit"], "domains": ["python"]},
        )
        registry.register("python-editor", SubprocessAdapter(config1))

        # JavaScript editor
        config2 = ToolConfig(
            tool_id="js-editor",
            kind="tool",
            command="echo",
            capabilities={"task_kinds": ["code_edit"], "domains": ["javascript"]},
        )
        registry.register("js-editor", SubprocessAdapter(config2))

        # Find Python editors
        capable = registry.find_for_task("code_edit", domain="python")
        assert len(capable) == 1
        assert capable[0].config.tool_id == "python-editor"

    def test_load_from_config(self):
        """Test loading adapters from config file"""
        # Get path to test config
        test_config = Path(__file__).parent / "test_router_config.json"

        registry = AdapterRegistry()
        registry.load_from_config(str(test_config))

        # Check tools were loaded
        assert len(registry.list_tools()) == 3
        assert "aider" in registry.list_tools()
        assert "codex" in registry.list_tools()
        assert "ruff" in registry.list_tools()

        # Check configs were parsed correctly
        aider_config = registry.get_config("aider")
        assert aider_config is not None
        assert aider_config.kind == "tool"
        assert aider_config.command == "aider --yes"
        assert "code_edit" in aider_config.capabilities.get("task_kinds", [])
        assert aider_config.limits["timeout_seconds"] == 600

        ruff_config = registry.get_config("ruff")
        assert ruff_config is not None
        assert ruff_config.kind == "validator"
        assert ruff_config.safety_tier == "low"

    def test_load_from_config_on_init(self):
        """Test loading config during initialization"""
        test_config = Path(__file__).parent / "test_router_config.json"

        registry = AdapterRegistry(config_path=str(test_config))

        assert len(registry.list_tools()) == 3
        assert registry.get("aider") is not None
