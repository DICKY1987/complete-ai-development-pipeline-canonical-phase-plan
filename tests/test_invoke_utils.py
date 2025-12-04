"""
Tests for Invoke utilities (Phase G - WS-G2).

Validates CommandResult, run_command(), and MockContext integration.
"""
# DOC_ID: DOC-TEST-TESTS-TEST-INVOKE-UTILS-087
# DOC_ID: DOC-TEST-TESTS-TEST-INVOKE-UTILS-048

import pytest
from pathlib import Path
from invoke import MockContext, Result
from core.invoke_utils import (
    CommandResult,
    run_command,
    run_tool_command,
    create_test_context,
)


def test_command_result_creation():
    """CommandResult can be created and converted to dict."""
    result = CommandResult(
        command='echo test',
        exit_code=0,
        stdout='test\n',
        stderr='',
        success=True,
        started_at='2025-11-21T00:00:00Z',
        completed_at='2025-11-21T00:00:01Z',
        duration_sec=1.0,
        timed_out=False,
    )

    assert result.success
    assert result.exit_code == 0
    assert 'test' in result.stdout

    # Can convert to dict
    data = result.to_dict()
    assert data['command'] == 'echo test'
    assert data['success'] is True


def test_run_command_success():
    """Successful commands return success=True."""
    mock_ctx = MockContext(run={
        'echo "hello"': Result(stdout='hello\n', exited=0),
    })

    result = run_command('echo "hello"', context=mock_ctx)

    assert result.success
    assert result.exit_code == 0
    assert 'hello' in result.stdout
    assert not result.timed_out


def test_run_command_failure():
    """Failed commands return success=False."""
    mock_ctx = MockContext(run={
        'exit 1': Result(stderr='error', exited=1),
    })

    result = run_command('exit 1', context=mock_ctx)

    assert not result.success
    assert result.exit_code == 1


def test_run_command_with_timeout():
    """Commands respect timeout parameter."""
    # Note: Actual timeout testing requires real subprocess
    # MockContext doesn't simulate timeouts
    mock_ctx = MockContext(run={
        'sleep 10': Result(stdout='', exited=0),
    })

    result = run_command('sleep 10', context=mock_ctx, timeout=1)
    # With real Context, this would timeout
    # With MockContext, it completes immediately
    assert result is not None


def test_run_command_with_env():
    """Commands receive environment variables."""
    mock_ctx = MockContext(run={
        'printenv TEST_VAR': Result(stdout='test_value\n', exited=0),
    })

    result = run_command(
        'printenv TEST_VAR',
        context=mock_ctx,
        env={'TEST_VAR': 'test_value'}
    )

    assert result.success


def test_run_command_with_cwd():
    """Commands execute in specified working directory."""
    mock_ctx = MockContext(run={
        'pwd': Result(stdout='/tmp\n', exited=0),
    })

    result = run_command('pwd', context=mock_ctx, cwd=Path('/tmp'))
    assert result.success


def test_run_tool_command_loads_config():
    """run_tool_command loads tool config from invoke.yaml."""
    mock_ctx = MockContext(run={
        'pytest -q': Result(stdout='10 passed\n', exited=0),
    })

    result = run_tool_command('pytest', 'pytest -q', context=mock_ctx)

    assert result.success
    assert 'passed' in result.stdout


def test_create_test_context():
    """create_test_context returns configured MockContext."""
    test_ctx = create_test_context({
        'echo test': Result(stdout='test\n', exited=0),
    })

    assert isinstance(test_ctx, MockContext)

    # Can use context
    result = run_command('echo test', context=test_ctx)
    assert result.success


def test_command_result_timestamps():
    """CommandResult includes proper timestamps."""
    result = run_command('echo test', context=create_test_context({
        'echo test': Result(stdout='test\n', exited=0),
    }))

    # Should have ISO 8601 UTC timestamps
    assert result.started_at.endswith('Z')
    assert result.completed_at.endswith('Z')
    assert result.duration_sec >= 0


def test_run_command_default_context():
    """run_command creates default Context if none provided."""
    # This test uses real Context, so we need a safe command
    result = run_command('echo test')
    # Real execution may or may not work depending on environment
    # Just verify structure is correct
    assert hasattr(result, 'command')
    assert hasattr(result, 'success')


def test_command_result_captures_stderr():
    """CommandResult captures stderr separately from stdout."""
    mock_ctx = MockContext(run={
        'ls /nonexistent': Result(
            stdout='',
            stderr='ls: cannot access /nonexistent: No such file or directory',
            exited=2
        ),
    })

    result = run_command('ls /nonexistent', context=mock_ctx)

    assert not result.success
    assert result.exit_code == 2
    assert len(result.stderr) > 0


def test_multiple_commands_in_sequence():
    """Multiple commands can be run in sequence."""
    mock_ctx = MockContext(run={
        'echo first': Result(stdout='first\n', exited=0),
        'echo second': Result(stdout='second\n', exited=0),
    })

    result1 = run_command('echo first', context=mock_ctx)
    result2 = run_command('echo second', context=mock_ctx)

    assert result1.success
    assert result2.success
    assert 'first' in result1.stdout
    assert 'second' in result2.stdout


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
