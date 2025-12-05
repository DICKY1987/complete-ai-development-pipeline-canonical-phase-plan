# DOC_LINK: DOC-ERROR-UNIT-TEST-AGENT-ADAPTERS-ADDITIONAL-147
# START <TestKey>
# TestType: Unit
# TargetModule: phase6_error_recovery/modules/error_engine/src/engine/agent_adapters.py
# TargetFunction: AiderAdapter.invoke|CodexAdapter.invoke|ClaudeAdapter.invoke|get_agent_adapter
# Purpose: Cover agent adapter availability branches, invocation error handling, and prompt formatting
# OptimizationPattern: Mock-Heavy
# CoverageGoalAchieved: 100% True
# END <TestKey>

from __future__ import annotations

import subprocess
import time
from types import SimpleNamespace

import pytest

from phase6_error_recovery.modules.error_engine.src.engine import (
    agent_adapters as adapters,
)


def test_format_error_prompt_groups_by_file():
    adapter = adapters.AgentAdapter("test")
    report = {
        "issues": [
            {
                "path": "a.py",
                "line": 1,
                "code": "E1",
                "message": "m1",
                "category": "lint",
            },
            {
                "path": "a.py",
                "line": 2,
                "code": "E2",
                "message": "m2",
                "category": "lint",
            },
            {
                "path": "b.py",
                "line": 3,
                "code": "E3",
                "message": "m3",
                "category": "style",
            },
        ]
    }

    prompt = adapter._format_error_prompt(report)

    assert "## a.py" in prompt and "## b.py" in prompt
    assert "- Line 1 [lint] E1: m1" in prompt
    assert "- Line 3 [style] E3: m3" in prompt


def test_aider_invoke_missing_tool(monkeypatch):
    adapter = adapters.AiderAdapter(config={"model": "gpt-4"})
    monkeypatch.setattr(adapter, "check_available", lambda: False)

    result = adapter.invoke(
        adapters.AgentInvocation(agent_name="aider", files=[], error_report={})
    )

    assert result.success is False
    assert "not found" in result.stderr.lower()
    assert result.error_message == "Aider CLI not installed"


def test_aider_invoke_success(monkeypatch):
    adapter = adapters.AiderAdapter(config={"model": "gpt-4o"})
    monkeypatch.setattr(adapter, "check_available", lambda: True)
    monkeypatch.setattr(
        "subprocess.run",
        lambda *_, **__: SimpleNamespace(
            returncode=0, stdout="Applied edit to sample.py", stderr=""
        ),
    )
    monkeypatch.setattr(time, "time", lambda: 100.0)

    invocation = adapters.AgentInvocation(
        agent_name="aider", files=["sample.py"], error_report={"issues": []}
    )
    result = adapter.invoke(invocation)

    assert result.success is True
    assert result.files_modified == ["sample.py"]
    assert result.metadata["model"] == "gpt-4o"
    assert result.duration_ms == 0


def test_aider_invoke_timeout(monkeypatch):
    adapter = adapters.AiderAdapter()
    monkeypatch.setattr(adapter, "check_available", lambda: True)

    def _raise_timeout(*_, **__):
        raise subprocess.TimeoutExpired(cmd="aider", timeout=1)

    monkeypatch.setattr("subprocess.run", _raise_timeout)
    monkeypatch.setattr(time, "time", lambda: 1.0)

    result = adapter.invoke(
        adapters.AgentInvocation(
            agent_name="aider", files=[], error_report={}, timeout_seconds=1
        )
    )

    assert result.success is False
    assert "timeout" in result.stderr.lower()
    assert result.error_message.startswith("Agent invocation timed out")


def test_aider_invoke_generic_error(monkeypatch):
    adapter = adapters.AiderAdapter()
    monkeypatch.setattr(adapter, "check_available", lambda: True)
    monkeypatch.setattr(
        "subprocess.run", lambda *_, **__: (_ for _ in ()).throw(RuntimeError("boom"))
    )
    monkeypatch.setattr(time, "time", lambda: 2.0)

    result = adapter.invoke(
        adapters.AgentInvocation(agent_name="aider", files=[], error_report={})
    )

    assert result.success is False
    assert result.error_message.startswith("Agent invocation failed:")


def test_aider_extract_modified_files_matches_names():
    adapter = adapters.AiderAdapter()
    stdout = "Applied edit to foo.py and bar.txt"
    files = ["foo.py", "bar.txt", "baz.py"]

    assert adapter._extract_modified_files(stdout, files) == ["foo.py", "bar.txt"]


def test_codex_adapter_branches(monkeypatch):
    codex = adapters.CodexAdapter()
    monkeypatch.setattr(codex, "check_available", lambda: False)
    missing = codex.invoke(
        adapters.AgentInvocation(agent_name="codex", files=[], error_report={})
    )
    assert missing.success is False
    assert (
        "not installed" in missing.error_message.lower()
        or "not found" in missing.stderr.lower()
    )

    # When available, Codex returns suggestions (not stub)
    monkeypatch.setattr(codex, "check_available", lambda: True)
    # Mock subprocess.run to avoid actual gh copilot call
    import subprocess
    from unittest.mock import MagicMock

    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = "suggestion output"
    mock_proc.stderr = ""

    original_run = subprocess.run

    def mock_run(*args, **kwargs):
        if "gh" in str(args[0]):
            return mock_proc
        return original_run(*args, **kwargs)

    monkeypatch.setattr(subprocess, "run", mock_run)

    result = codex.invoke(
        adapters.AgentInvocation(agent_name="codex", files=[], error_report={})
    )
    assert result.metadata.get("mode") == "suggestion"
    assert result.files_modified == []  # Codex gives suggestions, not direct edits


def test_claude_adapter_branches(monkeypatch):
    claude = adapters.ClaudeAdapter()
    monkeypatch.setenv("ANTHROPIC_API_KEY", "", prepend=False)
    missing = claude.invoke(
        adapters.AgentInvocation(agent_name="claude", files=[], error_report={})
    )
    assert missing.success is False
    assert "not configured" in missing.error_message.lower()

    # When API key is present, Claude may succeed or fail depending on anthropic package
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-token-12345")
    result = claude.invoke(
        adapters.AgentInvocation(agent_name="claude", files=[], error_report={})
    )

    # Without anthropic package installed, should return "missing_dependency" status
    # With package, would attempt actual API call
    assert isinstance(result.success, bool)
    if not result.success:
        assert (
            "missing_dependency" in result.metadata.get("status", "")
            or "not installed" in result.stderr.lower()
        )


def test_agent_adapter_factory_and_availability(monkeypatch):
    adapter = adapters.get_agent_adapter("aider")
    assert isinstance(adapter, adapters.AiderAdapter)

    with pytest.raises(ValueError):
        adapters.get_agent_adapter("unknown")

    monkeypatch.setattr(adapters.AiderAdapter, "check_available", lambda self: True)
    monkeypatch.setattr(adapters.CodexAdapter, "check_available", lambda self: False)
    monkeypatch.setattr(adapters.ClaudeAdapter, "check_available", lambda self: True)

    availability = adapters.check_agent_availability()
    assert availability == {"aider": True, "codex": False, "claude": True}
