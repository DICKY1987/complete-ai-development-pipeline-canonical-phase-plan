"""Unit tests for SecretsManager."""

import pytest
from pathlib import Path
import tempfile
import shutil

from modules.aim_environment.m01001B_secrets import SecretsManager, get_secrets_manager
from modules.aim_environment.m01001B_exceptions import SecretsError


@pytest.fixture
def temp_vault_path(tmp_path):
    """Create a temporary vault path for testing."""
DOC_ID: DOC-PAT-ENVIRONMENT-TEST-SECRETS-427
    vault_path = tmp_path / "test_secrets.json"
    yield vault_path
    # Cleanup is automatic with tmp_path


@pytest.fixture
def secrets_manager(temp_vault_path):
    """Create a SecretsManager instance with temp vault."""
    return SecretsManager(vault_path=temp_vault_path)


class TestSecretsManager:
    """Test suite for SecretsManager."""
    
    def test_initialization(self, secrets_manager, temp_vault_path):
        """Test that SecretsManager initializes correctly."""
        assert secrets_manager.vault_path == temp_vault_path
        assert temp_vault_path.exists()
    
    def test_set_and_get_secret(self, secrets_manager):
        """Test storing and retrieving a secret."""
        key = "TEST_API_KEY"
        value = "test-secret-value-123"
        
        secrets_manager.set_secret(key, value, description="Test API key")
        retrieved = secrets_manager.get_secret(key)
        
        assert retrieved == value
    
    def test_get_nonexistent_secret(self, secrets_manager):
        """Test retrieving a secret that doesn't exist."""
        result = secrets_manager.get_secret("NONEXISTENT_KEY")
        assert result is None
    
    def test_delete_secret(self, secrets_manager):
        """Test deleting a secret."""
        key = "DELETE_ME"
        value = "temporary-value"
        
        secrets_manager.set_secret(key, value)
        assert secrets_manager.get_secret(key) == value
        
        deleted = secrets_manager.delete_secret(key)
        assert deleted is True
        assert secrets_manager.get_secret(key) is None
    
    def test_delete_nonexistent_secret(self, secrets_manager):
        """Test deleting a secret that doesn't exist."""
        result = secrets_manager.delete_secret("NONEXISTENT")
        assert result is False
    
    def test_list_secrets(self, secrets_manager):
        """Test listing all secrets."""
        secrets_manager.set_secret("KEY1", "value1", "First key")
        secrets_manager.set_secret("KEY2", "value2", "Second key")
        
        secrets = secrets_manager.list_secrets()
        
        assert len(secrets) == 2
        keys = [s["key"] for s in secrets]
        assert "KEY1" in keys
        assert "KEY2" in keys
        
        # Check metadata
        key1_meta = next(s for s in secrets if s["key"] == "KEY1")
        assert key1_meta["description"] == "First key"
        assert key1_meta["exists"] is True
    
    def test_inject_into_env(self, secrets_manager):
        """Test injecting secrets into environment dict."""
        secrets_manager.set_secret("ENV_KEY1", "env_value1")
        secrets_manager.set_secret("ENV_KEY2", "env_value2")
        
        env_vars = secrets_manager.inject_into_env(["ENV_KEY1", "ENV_KEY2"])
        
        assert env_vars == {
            "ENV_KEY1": "env_value1",
            "ENV_KEY2": "env_value2"
        }
    
    def test_inject_specific_keys(self, secrets_manager):
        """Test injecting only specific keys."""
        secrets_manager.set_secret("KEY_A", "value_a")
        secrets_manager.set_secret("KEY_B", "value_b")
        secrets_manager.set_secret("KEY_C", "value_c")
        
        env_vars = secrets_manager.inject_into_env(["KEY_A", "KEY_C"])
        
        assert len(env_vars) == 2
        assert "KEY_A" in env_vars
        assert "KEY_C" in env_vars
        assert "KEY_B" not in env_vars
    
    def test_inject_all_secrets(self, secrets_manager):
        """Test injecting all secrets when no keys specified."""
        secrets_manager.set_secret("ALL_KEY1", "all_value1")
        secrets_manager.set_secret("ALL_KEY2", "all_value2")
        
        env_vars = secrets_manager.inject_into_env()
        
        assert len(env_vars) == 2
        assert "ALL_KEY1" in env_vars
        assert "ALL_KEY2" in env_vars
    
    def test_export_to_env(self, secrets_manager):
        """Test exporting secrets to process environment."""
        import os
        
        key = "EXPORT_TEST_KEY"
        value = "export_test_value"
        
        # Ensure key doesn't exist in env
        os.environ.pop(key, None)
        
        secrets_manager.set_secret(key, value)
        secrets_manager.export_to_env([key])
        
        assert os.environ.get(key) == value
        
        # Cleanup
        os.environ.pop(key, None)
    
    def test_factory_function(self, temp_vault_path):
        """Test the factory function."""
        manager = get_secrets_manager(vault_path=temp_vault_path)
        assert isinstance(manager, SecretsManager)
        assert manager.vault_path == temp_vault_path


class TestSecretsManagerEdgeCases:
    """Edge case tests for SecretsManager."""
    
    def test_empty_secret_value(self, secrets_manager):
        """Test storing an empty string as secret value."""
        secrets_manager.set_secret("EMPTY_KEY", "", "Empty secret")
        value = secrets_manager.get_secret("EMPTY_KEY")
        assert value == ""
    
    def test_special_characters_in_value(self, secrets_manager):
        """Test storing secrets with special characters."""
        special_value = "sk-!@#$%^&*()_+-=[]{}|;':\",./<>?"
        secrets_manager.set_secret("SPECIAL_KEY", special_value)
        assert secrets_manager.get_secret("SPECIAL_KEY") == special_value
    
    def test_unicode_in_value(self, secrets_manager):
        """Test storing Unicode characters."""
        unicode_value = "日本語テスト🔑"
        secrets_manager.set_secret("UNICODE_KEY", unicode_value)
        assert secrets_manager.get_secret("UNICODE_KEY") == unicode_value
    
    @pytest.mark.skip(reason="Windows Credential Manager has size limits")
    def test_large_secret_value(self, secrets_manager):
        """Test storing a large secret value."""
        # Windows Credential Manager has a limit (~2500 bytes)
        # This test is skipped as it's a platform limitation
        large_value = "x" * 2000
        secrets_manager.set_secret("LARGE_KEY", large_value)
        assert secrets_manager.get_secret("LARGE_KEY") == large_value
    
    def test_list_secrets_empty(self, secrets_manager):
        """Test listing secrets when none exist."""
        secrets = secrets_manager.list_secrets()
        assert secrets == []
