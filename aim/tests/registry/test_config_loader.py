"""Unit tests for ConfigLoader."""

import pytest
import json
from pathlib import Path
import tempfile

from aim.registry.config_loader import ConfigLoader, get_config_loader, load_config
from aim.environment.exceptions import ConfigurationError


@pytest.fixture
def valid_config():
    """Create a valid configuration dict."""
    return {
        "version": "1.0.0",
        "registry": {
            "tools": {
                "test-tool": {
                    "name": "Test Tool",
                    "detectCommands": ["test"],
                    "capabilities": ["testing"]
                }
            },
            "capabilities": {
                "testing": {
                    "primaryTool": "test-tool",
                    "fallbacks": []
                }
            }
        },
        "environment": {
            "toolsRoot": "C:\\Tools",
            "pipxApps": ["pytest"],
            "npmGlobal": []
        },
        "audit": {
            "enabled": True,
            "logPath": "/tmp/audit.log",
            "events": ["tool_invoke"]
        }
    }


@pytest.fixture
def temp_config_file(valid_config, tmp_path):
    """Create a temporary config file."""
    config_file = tmp_path / "test_config.json"
    with open(config_file, "w") as f:
        json.dump(valid_config, f)
    return config_file


class TestConfigLoader:
    """Test suite for ConfigLoader."""
    
    def test_initialization(self, temp_config_file):
        """Test ConfigLoader initialization."""
        loader = ConfigLoader(temp_config_file)
        assert loader.config_path == temp_config_file
        assert loader._config is None
    
    def test_load_valid_config(self, temp_config_file):
        """Test loading a valid configuration."""
        loader = ConfigLoader(temp_config_file)
        config = loader.load(validate=False)  # Skip schema validation
        
        assert config["version"] == "1.0.0"
        assert "registry" in config
        assert "environment" in config
        assert "audit" in config
    
    def test_load_nonexistent_file(self):
        """Test loading from nonexistent file."""
        loader = ConfigLoader(Path("/nonexistent/config.json"))
        
        with pytest.raises(ConfigurationError, match="not found"):
            loader.load()
    
    def test_load_invalid_json(self, tmp_path):
        """Test loading invalid JSON."""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("{ invalid json }")
        
        loader = ConfigLoader(invalid_file)
        
        with pytest.raises(ConfigurationError, match="Invalid JSON"):
            loader.load()
    
    def test_env_var_expansion_windows(self, tmp_path, monkeypatch):
        """Test Windows-style environment variable expansion."""
        monkeypatch.setenv("TEST_VAR", "expanded_value")
        
        config = {
            "version": "1.0.0",
            "registry": {"tools": {}},
            "environment": {
                "path": "%TEST_VAR%\\subdir"
            },
            "audit": {"enabled": True}
        }
        
        config_file = tmp_path / "test.json"
        with open(config_file, "w") as f:
            json.dump(config, f)
        
        loader = ConfigLoader(config_file)
        loaded = loader.load(validate=False)
        
        assert loaded["environment"]["path"] == "expanded_value\\subdir"
    
    def test_env_var_expansion_unix(self, tmp_path, monkeypatch):
        """Test Unix-style environment variable expansion."""
        monkeypatch.setenv("TEST_VAR", "unix_value")
        
        config = {
            "version": "1.0.0",
            "registry": {"tools": {}},
            "environment": {
                "path1": "$TEST_VAR/subdir",
                "path2": "${TEST_VAR}/other"
            },
            "audit": {"enabled": True}
        }
        
        config_file = tmp_path / "test.json"
        with open(config_file, "w") as f:
            json.dump(config, f)
        
        loader = ConfigLoader(config_file)
        loaded = loader.load(validate=False)
        
        assert loaded["environment"]["path1"] == "unix_value/subdir"
        assert loaded["environment"]["path2"] == "unix_value/other"
    
    def test_nested_env_var_expansion(self, tmp_path, monkeypatch):
        """Test environment variable expansion in nested structures."""
        monkeypatch.setenv("HOME", "/home/user")
        
        config = {
            "version": "1.0.0",
            "registry": {"tools": {}},
            "environment": {
                "paths": [
                    "$HOME/.config",
                    "$HOME/.cache"
                ],
                "nested": {
                    "deep": {
                        "path": "${HOME}/deep/path"
                    }
                }
            },
            "audit": {"enabled": True}
        }
        
        config_file = tmp_path / "test.json"
        with open(config_file, "w") as f:
            json.dump(config, f)
        
        loader = ConfigLoader(config_file)
        loaded = loader.load(validate=False)
        
        assert loaded["environment"]["paths"][0] == "/home/user/.config"
        assert loaded["environment"]["paths"][1] == "/home/user/.cache"
        assert loaded["environment"]["nested"]["deep"]["path"] == "/home/user/deep/path"
    
    def test_get_registry(self, temp_config_file):
        """Test getting registry section."""
        loader = ConfigLoader(temp_config_file)
        registry = loader.get_registry()
        
        assert "tools" in registry
        assert "capabilities" in registry
        assert "test-tool" in registry["tools"]
    
    def test_get_environment(self, temp_config_file):
        """Test getting environment section."""
        loader = ConfigLoader(temp_config_file)
        env = loader.get_environment()
        
        assert "toolsRoot" in env
        assert env["toolsRoot"] == "C:\\Tools"
    
    def test_get_audit(self, temp_config_file):
        """Test getting audit section."""
        loader = ConfigLoader(temp_config_file)
        audit = loader.get_audit()
        
        assert audit["enabled"] is True
        assert "logPath" in audit
    
    def test_get_tool(self, temp_config_file):
        """Test getting specific tool config."""
        loader = ConfigLoader(temp_config_file)
        tool = loader.get_tool("test-tool")
        
        assert tool is not None
        assert tool["name"] == "Test Tool"
        assert "testing" in tool["capabilities"]
    
    def test_get_nonexistent_tool(self, temp_config_file):
        """Test getting nonexistent tool."""
        loader = ConfigLoader(temp_config_file)
        tool = loader.get_tool("nonexistent")
        
        assert tool is None
    
    def test_get_capability(self, temp_config_file):
        """Test getting capability config."""
        loader = ConfigLoader(temp_config_file)
        cap = loader.get_capability("testing")
        
        assert cap is not None
        assert cap["primaryTool"] == "test-tool"
    
    def test_get_nonexistent_capability(self, temp_config_file):
        """Test getting nonexistent capability."""
        loader = ConfigLoader(temp_config_file)
        cap = loader.get_capability("nonexistent")
        
        assert cap is None


class TestConfigLoaderHelpers:
    """Test helper functions."""
    
    def test_get_config_loader_singleton(self):
        """Test singleton pattern of get_config_loader."""
        loader1 = get_config_loader()
        loader2 = get_config_loader()
        
        assert loader1 is loader2
    
    def test_load_config_convenience(self, temp_config_file, monkeypatch):
        """Test load_config convenience function."""
        # Temporarily override default path
        import aim.registry.config_loader as module
        original_path = ConfigLoader.DEFAULT_CONFIG_PATH
        ConfigLoader.DEFAULT_CONFIG_PATH = temp_config_file
        
        try:
            # Reset singleton
            module._loader = None
            
            config = load_config(validate=False)
            assert config["version"] == "1.0.0"
        finally:
            ConfigLoader.DEFAULT_CONFIG_PATH = original_path
            module._loader = None


class TestConfigLoaderEdgeCases:
    """Edge case tests."""
    
    def test_undefined_env_var(self, tmp_path):
        """Test that undefined env vars are left unchanged."""
        config = {
            "version": "1.0.0",
            "registry": {"tools": {}},
            "environment": {
                "path": "%UNDEFINED_VAR%/path"
            },
            "audit": {"enabled": True}
        }
        
        config_file = tmp_path / "test.json"
        with open(config_file, "w") as f:
            json.dump(config, f)
        
        loader = ConfigLoader(config_file)
        loaded = loader.load(validate=False)
        
        # Undefined vars should remain unchanged
        assert "%UNDEFINED_VAR%" in loaded["environment"]["path"]
    
    def test_empty_config_sections(self, tmp_path):
        """Test config with empty sections."""
        config = {
            "version": "1.0.0",
            "registry": {
                "tools": {}
            },
            "environment": {},
            "audit": {}
        }
        
        config_file = tmp_path / "test.json"
        with open(config_file, "w") as f:
            json.dump(config, f)
        
        loader = ConfigLoader(config_file)
        loaded = loader.load(validate=False)
        
        assert loaded["registry"]["tools"] == {}
        assert loaded["environment"] == {}
