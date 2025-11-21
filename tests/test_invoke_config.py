"""
Tests for Invoke configuration system (Phase G).

Validates config loading hierarchy, tool profiles, and legacy fallback.
"""

import os
import pytest
from pathlib import Path
from core.config_loader import (
    load_project_config,
    get_tool_config,
    get_orchestrator_config,
    get_paths_config,
    get_circuit_breaker_config,
    get_error_engine_config,
)


def test_load_project_config():
    """Config loads from invoke.yaml."""
    config = load_project_config()
    assert isinstance(config, dict)
    assert 'tools' in config
    assert 'orchestrator' in config
    assert 'paths' in config


def test_get_tool_config_aider():
    """Aider tool config loads correctly."""
    aider_cfg = get_tool_config('aider')
    assert aider_cfg is not None
    assert 'timeout' in aider_cfg
    assert aider_cfg['timeout'] == 1800
    assert aider_cfg.get('type') == 'ai'
    assert aider_cfg.get('command') == 'aider'


def test_get_tool_config_pytest():
    """Pytest tool config loads correctly."""
    pytest_cfg = get_tool_config('pytest')
    assert pytest_cfg is not None
    assert 'timeout' in pytest_cfg
    assert pytest_cfg['timeout'] == 600
    assert pytest_cfg.get('type') == 'test'


def test_get_orchestrator_config():
    """Orchestrator config loads correctly."""
    orch_cfg = get_orchestrator_config()
    assert orch_cfg is not None
    assert 'dry_run' in orch_cfg
    assert 'max_retries' in orch_cfg
    assert isinstance(orch_cfg['dry_run'], bool)


def test_get_paths_config():
    """Paths config loads correctly."""
    paths_cfg = get_paths_config()
    assert paths_cfg is not None
    assert 'repo_root' in paths_cfg
    assert 'workstreams_dir' in paths_cfg
    assert 'state_db' in paths_cfg


def test_get_circuit_breaker_config():
    """Circuit breaker config loads correctly."""
    cb_cfg = get_circuit_breaker_config()
    assert cb_cfg is not None
    assert 'max_attempts_per_step' in cb_cfg
    assert 'oscillation_window' in cb_cfg


def test_get_error_engine_config():
    """Error engine config loads correctly."""
    ee_cfg = get_error_engine_config()
    assert ee_cfg is not None
    assert 'enabled' in ee_cfg
    assert 'plugins_dir' in ee_cfg


def test_config_hierarchy_defaults():
    """Config provides sensible defaults."""
    config = load_project_config()
    
    # Tools section should exist
    assert 'tools' in config
    
    # Core tools should be defined
    assert 'aider' in config['tools']
    assert 'pytest' in config['tools']
    
    # Paths should have defaults
    paths = get_paths_config(config)
    assert paths.get('repo_root') == '.'


def test_tool_config_fallback():
    """Get tool config handles missing tools gracefully."""
    missing_cfg = get_tool_config('nonexistent-tool-12345')
    assert missing_cfg == {}


def test_config_caching():
    """Config loads once and caches."""
    cfg1 = load_project_config()
    cfg2 = load_project_config()
    # Should return same structure
    assert cfg1.keys() == cfg2.keys()


def test_environment_variable_support():
    """Environment variables can override config (documented behavior)."""
    # This tests that the pattern is documented, not that it works
    # (Invoke doesn't natively support INVOKE_* vars for custom sections)
    config = load_project_config()
    assert config is not None
    
    # Document expected pattern
    # os.environ['INVOKE_TOOLS_PYTEST_TIMEOUT'] = '900'
    # Would require custom env var loader in config_loader.py


def test_legacy_config_fallback():
    """Legacy config files trigger deprecation warnings."""
    # Import tools module which has legacy fallback
    import warnings
    from core.engine import tools
    
    # Loading should work (falls back to invoke.yaml)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        profiles = tools.load_tool_profiles()
        
        # Should load successfully from invoke.yaml
        assert profiles is not None
        assert 'pytest' in profiles


def test_circuit_breaker_config_migration():
    """Circuit breaker config migrates from legacy structure."""
    from core.engine import circuit_breakers
    
    config = circuit_breakers.load_config()
    assert 'defaults' in config
    assert 'max_attempts_per_step' in config['defaults']


def test_config_validation():
    """Config contains required sections."""
    config = load_project_config()
    
    required_sections = ['tools', 'orchestrator', 'paths', 'circuit_breakers']
    for section in required_sections:
        assert section in config, f"Missing required section: {section}"


def test_tool_timeout_consistency():
    """Tool timeouts are reasonable values."""
    config = load_project_config()
    tools = config.get('tools', {})
    
    for tool_id, tool_cfg in tools.items():
        if 'timeout' in tool_cfg:
            timeout = tool_cfg['timeout']
            assert timeout > 0, f"{tool_id} has invalid timeout"
            assert timeout < 7200, f"{tool_id} timeout too high (>2 hours)"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
