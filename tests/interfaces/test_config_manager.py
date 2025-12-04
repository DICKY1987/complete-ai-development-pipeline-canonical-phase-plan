"""Tests for ConfigManager protocol and implementations."""

import pytest
import tempfile
from pathlib import Path

from core.config_manager import (
    ConfigManager,
    ConfigValidationError,
    ToolProfileNotFoundError,
)
from core.config.yaml_config_manager import YamlConfigManager


class TestConfigManagerProtocol:
    """Test ConfigManager protocol compliance."""
# DOC_ID: DOC-TEST-INTERFACES-TEST-CONFIG-MANAGER-121

    def test_yaml_config_manager_implements_protocol(self):
        """YamlConfigManager implements ConfigManager protocol."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('test: value')
            config = YamlConfigManager(f.name)
            assert isinstance(config, ConfigManager)


class TestYamlConfigManager:
    """Test YamlConfigManager implementation."""

    @pytest.fixture
    def config_file(self):
        """Create temporary YAML config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
execution:
  timeout: 300
  dry_run: false

tools:
  aider:
    model: gpt-4
    enabled: true
  codex:
    model: gpt-4-turbo
    enabled: true

logging:
  level: INFO
""")
            yield f.name

    def test_get_simple_key(self, config_file):
        """Get simple configuration value."""
        config = YamlConfigManager(config_file)

        level = config.get('logging.level')

        assert level == 'INFO'

    def test_get_nested_key(self, config_file):
        """Get nested configuration value."""
        config = YamlConfigManager(config_file)

        timeout = config.get('execution.timeout')

        assert timeout == 300

    def test_get_with_default(self, config_file):
        """Get returns default if key not found."""
        config = YamlConfigManager(config_file)

        value = config.get('nonexistent.key', 'default')

        assert value == 'default'

    def test_get_tool_profile(self, config_file):
        """Get tool-specific profile."""
        config = YamlConfigManager(config_file)

        aider = config.get_tool_profile('aider')

        assert aider['model'] == 'gpt-4'
        assert aider['enabled'] is True

    def test_get_tool_profile_not_found(self, config_file):
        """Getting nonexistent tool profile raises error."""
        config = YamlConfigManager(config_file)

        with pytest.raises(ToolProfileNotFoundError):
            config.get_tool_profile('nonexistent')

    def test_set_runtime_override(self, config_file):
        """Set runtime configuration override."""
        config = YamlConfigManager(config_file)

        config.set('execution.dry_run', True)

        assert config.get('execution.dry_run') is True

    def test_override_takes_precedence(self, config_file):
        """Runtime override takes precedence over file."""
        config = YamlConfigManager(config_file)

        # Original value
        assert config.get('execution.timeout') == 300

        # Override
        config.set('execution.timeout', 600)

        # Override value returned
        assert config.get('execution.timeout') == 600

    def test_validate_all_valid_config(self, config_file):
        """Validate returns empty list for valid config."""
        config = YamlConfigManager(config_file)

        errors = config.validate_all()

        assert errors == []

    def test_validate_catches_invalid_timeout(self):
        """Validation catches invalid timeout."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('execution:\n  timeout: -100\n')
            config = YamlConfigManager(f.name)

            errors = config.validate_all()

            assert len(errors) > 0
            assert 'timeout' in errors[0].lower()

    def test_reload_picks_up_changes(self, config_file):
        """Reload picks up file changes."""
        config = YamlConfigManager(config_file)

        # Original value
        assert config.get('logging.level') == 'INFO'

        # Modify file
        with open(config_file, 'w') as f:
            f.write('logging:\n  level: DEBUG\n')

        # Reload
        config.reload()

        # New value
        assert config.get('logging.level') == 'DEBUG'

    def test_reload_keeps_overrides(self, config_file):
        """Reload keeps runtime overrides."""
        config = YamlConfigManager(config_file)

        config.set('custom.value', 'override')
        config.reload()

        assert config.get('custom.value') == 'override'

    def test_get_all_returns_full_config(self, config_file):
        """get_all returns complete configuration."""
        config = YamlConfigManager(config_file)

        all_config = config.get_all()

        assert 'execution' in all_config
        assert 'tools' in all_config
        assert all_config['execution']['timeout'] == 300

    def test_get_all_includes_overrides(self, config_file):
        """get_all includes runtime overrides."""
        config = YamlConfigManager(config_file)

        config.set('execution.timeout', 600)
        all_config = config.get_all()

        assert all_config['execution']['timeout'] == 600

    def test_empty_config_file(self):
        """Handle empty configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('')
            config = YamlConfigManager(f.name)

            value = config.get('any.key', 'default')
            assert value == 'default'

    def test_nonexistent_config_file(self):
        """Handle nonexistent configuration file."""
        config = YamlConfigManager('/nonexistent/config.yaml')

        value = config.get('any.key', 'default')
        assert value == 'default'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
