"""Unit tests for Tool Adapters

DOC_ID: DOC-TEST-TESTS-TEST-ADAPTERS-354
"""

# DOC_ID: DOC - TEST - TESTS - TEST - ADAPTERS - 343

# DOC_ID: DOC - TEST - TESTS - TEST - ADAPTERS - 343
from pathlib import Path

import pytest

from core.engine.adapters import (
    AiderAdapter,
    ClaudeAdapter,
    CodexAdapter,
    ExecutionResult,
    ToolAdapter,
)


@pytest.fixture
def sample_task():
    return {
        "mode": "prompt",
        "payload": {"files": ["src/test.py"], "description": "Test task"},
        "timeouts": {"wall_clock_sec": 300},
    }


@pytest.fixture
def aider_config():
    return {"model": "gpt-4", "timeout": 600}


def test_execution_result_creation():
    result = ExecutionResult(
        success=True, exit_code=0, stdout="output", stderr="", duration_sec=1.5
    )
    assert result.success is True
    assert result.exit_code == 0
    assert result.duration_sec == 1.5


def test_aider_adapter_init(aider_config):
    adapter = AiderAdapter(aider_config)
    assert adapter.name == "aider"
    assert adapter.config == aider_config


def test_aider_build_prompt_command(sample_task):
    adapter = AiderAdapter({"model": "gpt-4"})
    command = adapter.build_command(sample_task)
    assert "aider" in command
    assert "--no-auto-commits" in command
    assert "--yes" in command
    assert "--model" in command
    assert "gpt-4" in command


def test_aider_build_command_with_prompt_file(sample_task, tmp_path):
    adapter = AiderAdapter()
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("Test prompt")
    command = adapter.build_command(sample_task, prompt_file)
    assert "--message-file" in command
    assert str(prompt_file) in command


def test_codex_adapter_init():
    adapter = CodexAdapter()
    assert adapter.name == "codex"


def test_codex_build_command(sample_task):
    adapter = CodexAdapter()
    command = adapter.build_command(sample_task)
    assert "gh" in command
    assert "copilot" in command
    assert "suggest" in command


def test_claude_adapter_init():
    adapter = ClaudeAdapter()
    assert adapter.name == "claude"


def test_claude_build_prompt_command(sample_task):
    adapter = ClaudeAdapter({"model": "claude-3-opus"})
    command = adapter.build_command(sample_task)
    assert "claude" in command
    assert "--model" in command


def test_claude_build_review_command():
    adapter = ClaudeAdapter()
    task = {"mode": "review", "payload": {"files": ["src/test.py"]}}
    command = adapter.build_command(task)
    assert "claude" in command
    assert "review" in command


def test_adapter_get_default_timeout():
    adapter = AiderAdapter({"timeout": 900})
    assert adapter.get_default_timeout() == 900


def test_adapter_get_model_name():
    adapter = AiderAdapter({"model": "gpt-4-turbo"})
    assert adapter.get_model_name() == "gpt-4-turbo"


def test_execution_result_defaults():
    result = ExecutionResult(success=False, exit_code=1)
    assert result.success is False
    assert result.stdout == ""
    assert result.stderr == ""
    assert result.timed_out is False


def test_aider_patch_apply_mode():
    adapter = AiderAdapter()
    task = {"mode": "patch_apply_validate", "payload": {"patch_file": "test.patch"}}
    command = adapter.build_command(task)
    assert "git" in command
    assert "apply" in command
    assert "test.patch" in command


def test_claude_unsupported_mode():
    adapter = ClaudeAdapter()
    task = {"mode": "unsupported", "payload": {}}
    with pytest.raises(ValueError):
        adapter.build_command(task)


def test_adapter_name_inference():
    assert AiderAdapter().name == "aider"
    assert CodexAdapter().name == "codex"
    assert ClaudeAdapter().name == "claude"


# DOC_LINK: DOC-TEST-TESTS-TEST-ADAPTERS-034
# DOC_LINK: DOC-TEST-TESTS-TEST-ADAPTERS-073
# DOC_LINK: DOC-TEST-TESTS-TEST-ADAPTERS-301
# DOC_LINK: DOC-TEST-TESTS-TEST-ADAPTERS-319
# DOC_LINK: DOC-TEST-TESTS-TEST-ADAPTERS-337
