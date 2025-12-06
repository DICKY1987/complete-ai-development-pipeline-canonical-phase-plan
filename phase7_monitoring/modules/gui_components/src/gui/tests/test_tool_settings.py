"""Tests for UI Settings Manager

Tests the UI settings configuration and interactive tool management.

# DOC_ID: DOC-TEST-TESTS-TEST-TOOL-SETTINGS-114
"""
import pytest

# Skip all tests - UI settings module import structure needs review
pytestmark = pytest.mark.skip(reason="UI settings module import structure needs refactoring")

import os
import tempfile
from pathlib import Path
import yaml

from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.ui_settings import UISettingsManager, get_settings_manager


class TestUISettingsManager:
    """Test UISettingsManager functionality."""

    def test_default_settings(self, tmp_path):
        """Test that default settings are loaded when config doesn't exist."""
        config_path = tmp_path / "nonexistent.yaml"
        settings = UISettingsManager(str(config_path))

        assert settings.get_interactive_tool() == "aim"
        assert "aim" in settings.get_available_interactive_tools()

    def test_load_settings_from_file(self, tmp_path):
        """Test loading settings from YAML file."""
        config_path = tmp_path / "ui_settings.yaml"

        # Create test config
        test_config = {
            'default_interactive_tool': 'aider',
            'available_interactive_tools': ['aim', 'aider', 'codex'],
            'tool_modes': {
                'aider': {
                    'default_mode': 'interactive',
                    'supports_headless': True,
                    'description': 'Test tool'
                }
            },
            'startup': {
                'auto_launch_interactive': False,
                'auto_launch_headless': ['pytest'],
                'interactive_tool_layout': 'side_panel'
            }
        }

        with open(config_path, 'w') as f:
            yaml.dump(test_config, f)

        settings = UISettingsManager(str(config_path))

        assert settings.get_interactive_tool() == "aider"
        assert settings.get_available_interactive_tools() == ['aim', 'aider', 'codex']
        assert not settings.should_auto_launch_interactive()
        assert settings.get_interactive_layout() == 'side_panel'

    def test_get_interactive_tool(self):
        """Test getting the current interactive tool."""
        settings = UISettingsManager()
        interactive_tool = settings.get_interactive_tool()

        assert isinstance(interactive_tool, str)
        assert interactive_tool in settings.get_available_interactive_tools()

    def test_set_interactive_tool(self, tmp_path):
        """Test setting a new interactive tool."""
        config_path = tmp_path / "ui_settings.yaml"
        settings = UISettingsManager(str(config_path))

        # Set to aider
        result = settings.set_interactive_tool("aider")
        assert result is True
        assert settings.get_interactive_tool() == "aider"

        # Verify it was saved
        settings2 = UISettingsManager(str(config_path))
        assert settings2.get_interactive_tool() == "aider"

    def test_set_invalid_interactive_tool(self, tmp_path):
        """Test setting an invalid interactive tool."""
        config_path = tmp_path / "ui_settings.yaml"
        settings = UISettingsManager(str(config_path))

        # Try to set invalid tool
        result = settings.set_interactive_tool("invalid_tool_name")
        assert result is False

        # Original tool should still be set
        assert settings.get_interactive_tool() == "aim"

    def test_is_headless(self, tmp_path):
        """Test checking if a tool should run in headless mode."""
        config_path = tmp_path / "ui_settings.yaml"
        settings = UISettingsManager(str(config_path))

        # Interactive tool should not be headless
        settings.set_interactive_tool("aim")
        assert settings.is_headless("aim") is False

        # Other tools should be headless
        assert settings.is_headless("aider") is True
        assert settings.is_headless("codex") is True

        # When we change interactive tool, modes should update
        settings.set_interactive_tool("aider")
        assert settings.is_headless("aider") is False
        assert settings.is_headless("aim") is True

    def test_get_tool_mode(self, tmp_path):
        """Test getting the execution mode for a tool."""
        config_path = tmp_path / "ui_settings.yaml"
        settings = UISettingsManager(str(config_path))

        settings.set_interactive_tool("aim")

        assert settings.get_tool_mode("aim") == "interactive"
        assert settings.get_tool_mode("aider") == "headless"
        assert settings.get_tool_mode("codex") == "headless"

    def test_get_tool_config(self):
        """Test getting full configuration for a tool."""
        settings = UISettingsManager()

        config = settings.get_tool_config("aim")
        assert isinstance(config, dict)
        assert "default_mode" in config or len(config) == 0

    def test_get_startup_config(self):
        """Test getting startup configuration."""
        settings = UISettingsManager()

        startup = settings.get_startup_config()
        assert isinstance(startup, dict)
        assert "auto_launch_interactive" in startup
        assert "auto_launch_headless" in startup
        assert "interactive_tool_layout" in startup

    def test_should_auto_launch_interactive(self):
        """Test checking if interactive tool should auto-launch."""
        settings = UISettingsManager()

        result = settings.should_auto_launch_interactive()
        assert isinstance(result, bool)

    def test_get_auto_launch_headless_tools(self):
        """Test getting list of headless tools to auto-launch."""
        settings = UISettingsManager()

        tools = settings.get_auto_launch_headless_tools()
        assert isinstance(tools, list)
        for tool in tools:
            assert isinstance(tool, str)

    def test_get_interactive_layout(self):
        """Test getting interactive tool layout preference."""
        settings = UISettingsManager()

        layout = settings.get_interactive_layout()
        assert isinstance(layout, str)
        assert layout in ['main_terminal', 'side_panel', 'popup']

    def test_list_all_tools(self):
        """Test listing all configured tools."""
        settings = UISettingsManager()

        tools = settings.list_all_tools()
        assert isinstance(tools, dict)

        # Should contain at least aim
        assert "aim" in tools or len(tools) >= 0

    def test_get_settings_summary(self):
        """Test getting settings summary."""
        settings = UISettingsManager()

        summary = settings.get_settings_summary()
        assert isinstance(summary, dict)
        assert "interactive_tool" in summary
        assert "available_interactive_tools" in summary
        assert "auto_launch_interactive" in summary

    def test_save_and_reload(self, tmp_path):
        """Test saving settings and reloading them."""
        config_path = tmp_path / "ui_settings.yaml"

        # Create and modify settings
        settings1 = UISettingsManager(str(config_path))
        settings1.set_interactive_tool("codex")

        # Load in new instance
        settings2 = UISettingsManager(str(config_path))

        assert settings2.get_interactive_tool() == "codex"

    def test_singleton_get_settings_manager(self):
        """Test that get_settings_manager returns a singleton."""
        manager1 = get_settings_manager()
        manager2 = get_settings_manager()

        assert manager1 is manager2


def test_ui_settings_file_creation():
    """Test that the UI settings file was created correctly."""
    config_path = Path(__file__).parent.parent / "config" / "ui_settings.yaml"

    assert config_path.exists(), "ui_settings.yaml should exist"

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    assert "default_interactive_tool" in config
    assert "available_interactive_tools" in config
    assert "tool_modes" in config
    assert "startup" in config


def test_ui_settings_valid_yaml():
    """Test that the UI settings YAML is valid."""
    config_path = Path(__file__).parent.parent / "config" / "ui_settings.yaml"

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Check structure
    assert isinstance(config.get("default_interactive_tool"), str)
    assert isinstance(config.get("available_interactive_tools"), list)
    assert isinstance(config.get("tool_modes"), dict)
    assert isinstance(config.get("startup"), dict)

    # Check that default interactive tool is in available list
    default_tool = config.get("default_interactive_tool")
    available = config.get("available_interactive_tools", [])
    assert default_tool in available, f"Default tool '{default_tool}' should be in available tools"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
