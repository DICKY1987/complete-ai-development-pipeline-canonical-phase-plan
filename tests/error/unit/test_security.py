"""Tests for security utilities."""
import sys
from pathlib import Path

# Add repo root
_repo_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_repo_root))

import pytest
from error.shared.utils.security import (
    SecurityError,
    validate_file_path,
    validate_file_size,
    redact_secrets,
    sanitize_path_for_log,
    validate_command_safe,
    ResourceLimits,
)


class TestValidateFilePath:
    """Test file path validation."""
    
    def test_valid_path_in_cwd(self, tmp_path):
        """Test that valid paths within cwd are accepted."""
        # Create a test file in tmp_path
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        # Should not raise
        validate_file_path(test_file, allowed_root=tmp_path)
    
    def test_path_outside_root_rejected(self, tmp_path):
        """Test that paths outside allowed root are rejected."""
        outside_path = Path("/etc/passwd")
        
        with pytest.raises(SecurityError) as exc_info:
            validate_file_path(outside_path, allowed_root=tmp_path)
        
        assert "outside allowed directory" in str(exc_info.value)
    
    def test_directory_traversal_rejected(self, tmp_path):
        """Test that directory traversal attempts are rejected."""
        traversal_path = tmp_path / ".." / ".." / "etc" / "passwd"
        
        with pytest.raises(SecurityError) as exc_info:
            validate_file_path(traversal_path, allowed_root=tmp_path)
        
        assert "Suspicious pattern" in str(exc_info.value) or "outside allowed" in str(exc_info.value)


class TestValidateFileSize:
    """Test file size validation."""
    
    def test_small_file_accepted(self, tmp_path):
        """Test that small files are accepted."""
        test_file = tmp_path / "small.txt"
        test_file.write_text("small content")
        
        # Should not raise (file is < 1MB)
        validate_file_size(test_file, max_size_mb=10)
    
    def test_large_file_rejected(self, tmp_path):
        """Test that large files are rejected."""
        test_file = tmp_path / "large.txt"
        # Write 2MB of data
        test_file.write_bytes(b"x" * (2 * 1024 * 1024))
        
        with pytest.raises(SecurityError) as exc_info:
            validate_file_size(test_file, max_size_mb=1)
        
        assert "too large" in str(exc_info.value).lower()
    
    def test_nonexistent_file_rejected(self, tmp_path):
        """Test that nonexistent files are rejected."""
        test_file = tmp_path / "nonexistent.txt"
        
        with pytest.raises(SecurityError) as exc_info:
            validate_file_size(test_file)
        
        assert "does not exist" in str(exc_info.value)


class TestRedactSecrets:
    """Test secret redaction."""
    
    def test_redact_api_keys(self):
        """Test that API keys are redacted."""
        text = "My key is sk-1234567890abcdefghijklmnopqrstuvwxyz"
        result = redact_secrets(text)
        
        assert "sk-1234567890" not in result
        assert "[REDACTED" in result
    
    def test_redact_openai_keys(self):
        """Test OpenAI key redaction."""
        text = "OPENAI_API_KEY=sk-proj-abcdefghijklmnop"
        result = redact_secrets(text)
        
        assert "sk-proj-" not in result
        assert "[REDACTED" in result
    
    def test_redact_passwords(self):
        """Test password redaction."""
        test_cases = [
            "password: mysecretpass",
            "PASSWORD=admin123",
            'passwd="letmein"',
        ]
        
        for text in test_cases:
            result = redact_secrets(text)
            assert "mysecret" not in result.lower()
            assert "admin123" not in result
            assert "letmein" not in result
            assert "[REDACTED" in result
    
    def test_redact_tokens(self):
        """Test token redaction."""
        text = "Authorization: Bearer abc123xyz789"
        result = redact_secrets(text)
        
        assert "abc123xyz789" not in result
        assert "[REDACTED" in result
    
    def test_redact_git_hashes(self):
        """Test that Git-like hashes are redacted."""
        text = "Commit: a" * 40  # 40-char hex string
        result = redact_secrets(text)
        
        assert "[REDACTED_HASH]" in result
    
    def test_redact_private_keys(self):
        """Test private key redaction."""
        text = """
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
-----END PRIVATE KEY-----
"""
        result = redact_secrets(text)
        
        assert "BEGIN PRIVATE KEY" not in result
        assert "[REDACTED_PRIVATE_KEY]" in result
    
    def test_empty_string_handled(self):
        """Test that empty strings are handled."""
        assert redact_secrets("") == ""
        assert redact_secrets(None) == None


class TestSanitizePathForLog:
    """Test path sanitization for logging."""
    
    def test_sanitize_home_directory(self):
        """Test that home directory is replaced with ~."""
        from pathlib import Path as PathLib
        home = PathLib.home()
        test_path = home / "projects" / "myfile.txt"
        
        result = sanitize_path_for_log(test_path)
        
        assert result.startswith("~")
        assert str(home) not in result
    
    def test_sanitize_username_windows(self):
        """Test Windows username sanitization."""
        path = Path(r"C:\Users\johndoe\Documents\file.txt")
        result = sanitize_path_for_log(path)
        
        # Should replace username
        assert "johndoe" not in result or "[USER]" in result


class TestValidateCommandSafe:
    """Test command safety validation."""
    
    def test_safe_command_accepted(self):
        """Test that safe commands are accepted."""
        safe_commands = [
            ["python", "script.py"],
            ["pytest", "tests/"],
            ["ls", "-la"],
        ]
        
        for cmd in safe_commands:
            # Should not raise
            validate_command_safe(cmd)
    
    def test_shell_injection_rejected(self):
        """Test that shell injection attempts are rejected."""
        dangerous_commands = [
            ["python", "script.py; rm -rf /"],
            ["ls", "|", "grep", "secret"],
            ["echo", "$(whoami)"],
        ]
        
        for cmd in dangerous_commands:
            with pytest.raises(SecurityError):
                validate_command_safe(cmd)
    
    def test_dangerous_commands_rejected(self):
        """Test that dangerous commands are rejected."""
        dangerous = [
            ["rm", "-rf", "/"],
            ["del", "C:\\"],
            ["format", "C:"],
        ]
        
        for cmd in dangerous:
            with pytest.raises(SecurityError) as exc_info:
                validate_command_safe(cmd)
            
            assert "Dangerous command" in str(exc_info.value)
    
    def test_empty_command_rejected(self):
        """Test that empty commands are rejected."""
        with pytest.raises(SecurityError):
            validate_command_safe([])


class TestResourceLimits:
    """Test ResourceLimits class."""
    
    def test_default_limits(self):
        """Test default resource limits."""
        limits = ResourceLimits()
        
        assert limits.max_file_size_mb == 10
        assert limits.max_execution_time_seconds == 120
        assert limits.max_memory_mb == 512
    
    def test_custom_limits(self):
        """Test custom resource limits."""
        limits = ResourceLimits(
            max_file_size_mb=5,
            max_execution_time_seconds=60,
            max_memory_mb=256,
        )
        
        assert limits.max_file_size_mb == 5
        assert limits.get_timeout() == 60
    
    def test_validate_file(self, tmp_path):
        """Test file validation with resource limits."""
        limits = ResourceLimits(max_file_size_mb=1)
        
        # Small file should pass
        small_file = tmp_path / "small.txt"
        small_file.write_text("small")
        limits.validate_file(small_file)
        
        # Large file should fail
        large_file = tmp_path / "large.txt"
        large_file.write_bytes(b"x" * (2 * 1024 * 1024))
        
        with pytest.raises(SecurityError):
            limits.validate_file(large_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
