"""Tests for ProcessExecutor protocol and SubprocessExecutor implementation."""

import time
import pytest
from pathlib import Path

from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.interfaces.process_executor import (
    ProcessExecutor,
    ProcessResult,
    ProcessHandle,
    ProcessExecutionError,
)
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.execution.subprocess_executor import SubprocessExecutor


class TestProcessExecutorProtocol:
    """Test ProcessExecutor protocol compliance."""
# DOC_ID: DOC-TEST-INTERFACES-TEST-PROCESS-EXECUTOR-123
    
    def test_subprocess_executor_implements_protocol(self):
        """SubprocessExecutor implements ProcessExecutor protocol."""
        executor = SubprocessExecutor()
        assert isinstance(executor, ProcessExecutor)
    
    def test_process_result_success_property(self):
        """ProcessResult.success returns True for exit_code 0."""
        result = ProcessResult(
            exit_code=0,
            stdout="output",
            stderr="",
            duration_s=1.0,
        )
        assert result.success is True
        
        result_fail = ProcessResult(
            exit_code=1,
            stdout="",
            stderr="error",
            duration_s=1.0,
        )
        assert result_fail.success is False


class TestSubprocessExecutor:
    """Test SubprocessExecutor implementation."""
    
    def test_run_simple_command(self):
        """Run simple command successfully."""
        executor = SubprocessExecutor()
        # Use python -c instead of echo (works on Windows)
        result = executor.run(['python', '-c', 'print("test")'])
        
        assert result.success
        assert result.exit_code == 0
        assert 'test' in result.stdout
        assert result.duration_s > 0
        assert not result.timed_out
        assert not result.dry_run
    
    def test_run_with_timeout(self):
        """Process respects timeout."""
        executor = SubprocessExecutor()
        start = time.time()
        
        # Use a command that sleeps longer than timeout
        result = executor.run(['python', '-c', 'import time; time.sleep(10)'], timeout=1)
        
        duration = time.time() - start
        assert duration < 3  # Should be killed quickly
        assert result.timed_out is True
        assert result.exit_code == -1
    
    def test_dry_run_mode(self):
        """Dry-run mode doesn't execute commands."""
        executor = SubprocessExecutor(dry_run=True)
        result = executor.run(['rm', '-rf', '/'])  # Dangerous command, safe in dry-run
        
        assert result.dry_run is True
        assert result.success
        assert '[DRY-RUN]' in result.stdout
        assert 'rm -rf /' in result.stdout
    
    def test_check_raises_on_failure(self):
        """check=True raises ProcessExecutionError on failure."""
        executor = SubprocessExecutor()
        
        with pytest.raises(ProcessExecutionError) as exc_info:
            executor.run(['python', '-c', 'import sys; sys.exit(1)'], check=True)
        
        assert exc_info.value.result.exit_code == 1
    
    def test_run_async(self):
        """Async execution returns handle."""
        executor = SubprocessExecutor()
        handle = executor.run_async(['python', '-c', 'print("async test")'])
        
        assert isinstance(handle, ProcessHandle)
        assert handle.pid > 0
        assert handle.command == ['python', '-c', 'print("async test")']
        assert handle.started_at > 0
        
        # Clean up
        time.sleep(0.5)  # Let process finish
        executor.kill(handle)
    
    def test_kill_async_process(self):
        """Kill terminates async process."""
        executor = SubprocessExecutor()
        handle = executor.run_async(['python', '-c', 'import time; time.sleep(100)'])
        
        time.sleep(0.5)  # Let process start
        executor.kill(handle)
        
        # Process should be terminated
        time.sleep(0.5)
        # If we try to kill again, it should be already gone
        executor.kill(handle)  # Should not raise


class TestProcessExecutorEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_command(self):
        """Empty command is handled gracefully."""
        executor = SubprocessExecutor()
        result = executor.run([])
        
        assert not result.success
        assert result.exit_code == -1
    
    def test_nonexistent_command(self):
        """Nonexistent command is handled gracefully."""
        executor = SubprocessExecutor()
        result = executor.run(['nonexistent-command-xyz-123'])
        
        assert not result.success
        assert result.exit_code == -1
        assert len(result.stderr) > 0
    
    def test_custom_cwd(self):
        """Custom working directory is respected."""
        executor = SubprocessExecutor()
        result = executor.run(['python', '-c', 'import os; print(os.getcwd())'], cwd=Path.cwd())
        
        assert result.success
        assert str(Path.cwd()) in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
