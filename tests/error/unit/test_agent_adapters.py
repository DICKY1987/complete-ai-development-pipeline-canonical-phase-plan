"""Unit tests for AI agent adapters."""
from __future__ import annotations

import sys
from pathlib import Path

# Add repo root to path
_repo_root = Path(__file__).resolve().parents[3]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from typing import Dict, Any
from unittest.mock import MagicMock, patch

import pytest

from modules.error_engine.m010004_agent_adapters import (
    AgentAdapter,
    AgentInvocation,
    AgentResult,
    AiderAdapter,
    CodexAdapter,
    ClaudeAdapter,
    get_agent_adapter,
    check_agent_availability,
)


class TestAgentInvocation:
    """Test AgentInvocation dataclass."""
    
    def test_create_invocation(self):
        """Test creating an agent invocation."""
        invocation = AgentInvocation(
            agent_name="aider",
            files=["test.py"],
            error_report={"summary": {"total_issues": 1}},
        )
        
        assert invocation.agent_name == "aider"
        assert invocation.files == ["test.py"]
        assert invocation.timeout_seconds == 300  # default
    
    def test_invocation_with_custom_timeout(self):
        """Test invocation with custom timeout."""
        invocation = AgentInvocation(
            agent_name="claude",
            files=["app.py"],
            error_report={},
            timeout_seconds=60,
        )
        
        assert invocation.timeout_seconds == 60


class TestAgentResult:
    """Test AgentResult dataclass."""
    
    def test_create_result(self):
        """Test creating an agent result."""
        result = AgentResult(
            success=True,
            files_modified=["test.py"],
            stdout="Fixed issues",
            stderr="",
            duration_ms=1500,
        )
        
        assert result.success is True
        assert result.files_modified == ["test.py"]
        assert result.duration_ms == 1500
    
    def test_result_with_error(self):
        """Test result with error message."""
        result = AgentResult(
            success=False,
            files_modified=[],
            stdout="",
            stderr="Tool not found",
            duration_ms=100,
            error_message="Aider not installed",
        )
        
        assert result.success is False
        assert result.error_message == "Aider not installed"


class TestAgentAdapter:
    """Test base AgentAdapter class."""
    
    def test_base_adapter_not_implemented(self):
        """Test that base adapter methods raise NotImplementedError."""
        adapter = AgentAdapter("test", {})
        
        with pytest.raises(NotImplementedError):
            adapter.check_available()
        
        with pytest.raises(NotImplementedError):
            invocation = AgentInvocation("test", [], {})
            adapter.invoke(invocation)
    
    def test_format_error_prompt(self):
        """Test error report formatting."""
        adapter = AgentAdapter("test", {})
        
        error_report = {
            "issues": [
                {
                    "path": "test.py",
                    "line": 10,
                    "code": "E501",
                    "category": "style",
                    "message": "Line too long",
                }
            ]
        }
        
        prompt = adapter._format_error_prompt(error_report)
        
        assert "test.py" in prompt
        assert "Line 10" in prompt
        assert "E501" in prompt
        assert "Line too long" in prompt


class TestAiderAdapter:
    """Test Aider adapter."""
    
    def test_aider_adapter_creation(self):
        """Test creating Aider adapter."""
        adapter = AiderAdapter()
        
        assert adapter.name == "aider"
        assert adapter.config == {}
    
    def test_aider_with_config(self):
        """Test Aider adapter with config."""
        config = {"model": "gpt-3.5-turbo"}
        adapter = AiderAdapter(config)
        
        assert adapter.config["model"] == "gpt-3.5-turbo"
    
    @patch("shutil.which")
    def test_check_available_when_installed(self, mock_which):
        """Test availability check when aider is installed."""
        mock_which.return_value = "/usr/bin/aider"
        
        adapter = AiderAdapter()
        assert adapter.check_available() is True
        mock_which.assert_called_with("aider")
    
    @patch("shutil.which")
    def test_check_available_when_not_installed(self, mock_which):
        """Test availability check when aider is not installed."""
        mock_which.return_value = None
        
        adapter = AiderAdapter()
        assert adapter.check_available() is False
    
    @patch("shutil.which")
    def test_invoke_when_not_available(self, mock_which):
        """Test invoking when aider is not available."""
        mock_which.return_value = None
        
        adapter = AiderAdapter()
        invocation = AgentInvocation(
            agent_name="aider",
            files=["test.py"],
            error_report={"issues": []},
        )
        
        result = adapter.invoke(invocation)
        
        assert result.success is False
        assert "not found" in result.stderr.lower()
        assert result.error_message is not None
    
    def test_extract_modified_files(self):
        """Test extracting modified files from aider output."""
        adapter = AiderAdapter()
        
        stdout = """
        Applied edit to test.py
        Applied edit to utils.py
        """
        
        candidate_files = ["test.py", "utils.py", "other.py"]
        modified = adapter._extract_modified_files(stdout, candidate_files)
        
        assert "test.py" in modified
        assert "utils.py" in modified
        assert "other.py" not in modified


class TestCodexAdapter:
    """Test Codex/GitHub Copilot CLI adapter."""
    
    def test_codex_adapter_creation(self):
        """Test creating Codex adapter."""
        adapter = CodexAdapter()
        
        assert adapter.name == "codex"
    
    @patch("subprocess.run")
    def test_check_available_when_installed(self, mock_run):
        """Test availability check when gh copilot is installed."""
        mock_run.return_value = MagicMock(returncode=0)
        
        adapter = CodexAdapter()
        assert adapter.check_available() is True
    
    @patch("subprocess.run")
    def test_check_available_when_not_installed(self, mock_run):
        """Test availability check when gh copilot is not installed."""
        mock_run.side_effect = FileNotFoundError()
        
        adapter = CodexAdapter()
        assert adapter.check_available() is False
    
    def test_invoke_stub_implementation(self):
        """Test that Codex invoke returns stub message."""
        adapter = CodexAdapter()
        invocation = AgentInvocation(
            agent_name="codex",
            files=["test.py"],
            error_report={},
        )
        
        result = adapter.invoke(invocation)
        
        # Should return stub for now
        assert result.success is False
        assert "stub" in result.metadata.get("status", "").lower()


class TestClaudeAdapter:
    """Test Claude API adapter."""
    
    def test_claude_adapter_creation(self):
        """Test creating Claude adapter."""
        adapter = ClaudeAdapter()
        
        assert adapter.name == "claude"
    
    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
    def test_check_available_with_api_key(self):
        """Test availability check with API key set."""
        adapter = ClaudeAdapter()
        assert adapter.check_available() is True
    
    @patch.dict("os.environ", {}, clear=True)
    def test_check_available_without_api_key(self):
        """Test availability check without API key."""
        adapter = ClaudeAdapter()
        assert adapter.check_available() is False
    
    def test_invoke_stub_implementation(self):
        """Test that Claude invoke returns stub message."""
        adapter = ClaudeAdapter()
        invocation = AgentInvocation(
            agent_name="claude",
            files=["test.py"],
            error_report={},
        )
        
        result = adapter.invoke(invocation)
        
        # Should return stub for now
        assert result.success is False
        assert "stub" in result.metadata.get("status", "").lower()


class TestAgentFactory:
    """Test agent adapter factory."""
    
    def test_get_aider_adapter(self):
        """Test getting Aider adapter from factory."""
        adapter = get_agent_adapter("aider")
        
        assert isinstance(adapter, AiderAdapter)
        assert adapter.name == "aider"
    
    def test_get_codex_adapter(self):
        """Test getting Codex adapter from factory."""
        adapter = get_agent_adapter("codex")
        
        assert isinstance(adapter, CodexAdapter)
        assert adapter.name == "codex"
    
    def test_get_claude_adapter(self):
        """Test getting Claude adapter from factory."""
        adapter = get_agent_adapter("claude")
        
        assert isinstance(adapter, ClaudeAdapter)
        assert adapter.name == "claude"
    
    def test_get_adapter_case_insensitive(self):
        """Test that factory is case-insensitive."""
        adapter1 = get_agent_adapter("Aider")
        adapter2 = get_agent_adapter("AIDER")
        
        assert isinstance(adapter1, AiderAdapter)
        assert isinstance(adapter2, AiderAdapter)
    
    def test_get_adapter_with_config(self):
        """Test getting adapter with custom config."""
        config = {"model": "gpt-4"}
        adapter = get_agent_adapter("aider", config)
        
        assert adapter.config == config
    
    def test_get_unknown_adapter_raises(self):
        """Test that unknown adapter name raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            get_agent_adapter("unknown")
        
        assert "Unknown agent" in str(exc_info.value)
        assert "unknown" in str(exc_info.value)


class TestCheckAgentAvailability:
    """Test availability checking function."""
    
    @patch("error.engine.agent_adapters.AiderAdapter.check_available")
    @patch("error.engine.agent_adapters.CodexAdapter.check_available")
    @patch("error.engine.agent_adapters.ClaudeAdapter.check_available")
    def test_check_all_agents_available(self, mock_claude, mock_codex, mock_aider):
        """Test checking availability of all agents."""
        mock_aider.return_value = True
        mock_codex.return_value = True
        mock_claude.return_value = True
        
        availability = check_agent_availability()
        
        assert availability["aider"] is True
        assert availability["codex"] is True
        assert availability["claude"] is True
    
    @patch("error.engine.agent_adapters.AiderAdapter.check_available")
    @patch("error.engine.agent_adapters.CodexAdapter.check_available")
    @patch("error.engine.agent_adapters.ClaudeAdapter.check_available")
    def test_check_mixed_availability(self, mock_claude, mock_codex, mock_aider):
        """Test mixed availability."""
        mock_aider.return_value = True
        mock_codex.return_value = False
        mock_claude.return_value = False
        
        availability = check_agent_availability()
        
        assert availability["aider"] is True
        assert availability["codex"] is False
        assert availability["claude"] is False
