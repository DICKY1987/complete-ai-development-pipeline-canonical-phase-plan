"""
ADAPTER_ROLE: terminal_tool_adapter
TOOL: tests
VERSION: 0.1.0

RESPONSIBILITY:
- Accept a job dict (from orchestrator).
- Build and run test commands (pytest, unittest, etc.).
- Run tests in a subprocess.
- Stream logs to job['paths']['log_file'].
- Return a JobResult object (exit_code, error_report_path, duration_s).

USAGE:
- Run automated tests after code changes
- Supports pytest, unittest, and custom test runners
- Captures test results and coverage reports
"""

import json
import subprocess
import time
from pathlib import Path
from typing import Dict, Any
from engine.types import JobResult


class TestsAdapter:
    """Adapter for executing test suite jobs."""
    
    def __init__(self):
        self.tool_name = "tests"
    
    def run_job(self, job: Dict[str, Any]) -> JobResult:
        """Execute a tests job."""
        start_time = time.time()
        
        command = self._build_command(job)
        env = self._build_env(job)
        paths = job["paths"]
        
        log_file = Path(paths["log_file"])
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        error_report = Path(paths["error_report"])
        
        stdout_lines = []
        stderr_lines = []
        
        try:
            with open(log_file, "w", encoding="utf-8") as log:
                log.write(f"=== Tests Job: {job['job_id']} ===\n")
                log.write(f"Command: {' '.join(command)}\n")
                log.write(f"Working dir: {paths['working_dir']}\n\n")
                log.flush()
                
                result = subprocess.run(
                    command,
                    cwd=paths["working_dir"],
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=job.get("metadata", {}).get("timeout_seconds", 300)
                )
                
                stdout_lines = result.stdout.split("\n") if result.stdout else []
                stderr_lines = result.stderr.split("\n") if result.stderr else []
                
                log.write("=== STDOUT ===\n")
                log.write(result.stdout or "(empty)\n")
                log.write("\n=== STDERR ===\n")
                log.write(result.stderr or "(empty)\n")
                log.write(f"\n=== Exit Code: {result.returncode} ===\n")
                
                # Parse test results
                test_summary = self._parse_test_results(result.stdout, result.stderr)
                log.write(f"\n=== Test Summary ===\n")
                log.write(json.dumps(test_summary, indent=2))
                log.write("\n")
                
                exit_code = result.returncode
                
        except subprocess.TimeoutExpired as e:
            exit_code = -1
            stderr_lines = [f"Tests timeout after {e.timeout} seconds"]
            with open(log_file, "a", encoding="utf-8") as log:
                log.write(f"\n=== TIMEOUT ({e.timeout}s) ===\n")
        except Exception as e:
            exit_code = -2
            stderr_lines = [f"Execution error: {str(e)}"]
            with open(log_file, "a", encoding="utf-8") as log:
                log.write(f"\n=== ERROR ===\n{str(e)}\n")
        
        duration = time.time() - start_time
        
        # Write error report if tests failed
        if exit_code != 0:
            self._write_error_report(error_report, job, exit_code, stderr_lines, 
                                    test_summary if 'test_summary' in locals() else {})
        
        return JobResult(
            exit_code=exit_code,
            error_report_path=str(error_report),
            duration_s=duration,
            stdout="\n".join(stdout_lines[:100]),
            stderr="\n".join(stderr_lines[:50]),
            success=(exit_code == 0),
            metadata=test_summary if 'test_summary' in locals() else {}
        )
    
    def validate_job(self, job: Dict[str, Any]) -> bool:
        """Validate that job has required fields for tests."""
        required = ["job_id", "workstream_id", "tool", "command", "env", "paths"]
        if not all(k in job for k in required):
            return False
        
        if job["tool"] != "tests":
            return False
        
        cmd = job.get("command", {})
        if "exe" not in cmd or "args" not in cmd:
            return False
        
        paths = job.get("paths", {})
        required_paths = ["repo_root", "working_dir", "log_file", "error_report"]
        if not all(k in paths for k in required_paths):
            return False
        
        return True
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get tests tool metadata."""
        return {
            "tool": "tests",
            "adapter_version": "0.1.0",
            "capabilities": ["unit_tests", "integration_tests", "coverage"],
            "supported_runners": ["pytest", "unittest", "custom"]
        }
    
    def _build_command(self, job: Dict[str, Any]) -> list:
        """Build command line from job specification."""
        cmd = job["command"]
        return [cmd["exe"]] + cmd["args"]
    
    def _build_env(self, job: Dict[str, Any]) -> Dict[str, str]:
        """Build environment variables from job specification."""
        import os
        env = os.environ.copy()
        env.update(job["env"])
        
        # Add PYTHONPATH if not set
        if "PYTHONPATH" not in env:
            env["PYTHONPATH"] = job["paths"]["repo_root"]
        
        return env
    
    def _parse_test_results(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """
        Parse test output to extract summary.
        
        Supports pytest and unittest output formats.
        """
        summary = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0
        }
        
        # Parse pytest output
        if "pytest" in stdout.lower() or "test session starts" in stdout.lower():
            # Look for pytest summary line
            for line in stdout.split("\n"):
                if " passed" in line or " failed" in line:
                    # Example: "5 passed, 2 failed in 1.23s"
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed" and i > 0:
                            try:
                                summary["passed"] = int(parts[i-1])
                            except ValueError:
                                pass
                        elif part == "failed" and i > 0:
                            try:
                                summary["failed"] = int(parts[i-1])
                            except ValueError:
                                pass
                        elif part == "skipped" and i > 0:
                            try:
                                summary["skipped"] = int(parts[i-1])
                            except ValueError:
                                pass
        
        summary["total"] = summary["passed"] + summary["failed"] + summary["skipped"] + summary["errors"]
        return summary
    
    def _write_error_report(self, path: Path, job: Dict[str, Any], 
                           exit_code: int, stderr: list, test_summary: Dict[str, Any]):
        """Write error report JSON."""
        path.parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            "job_id": job["job_id"],
            "tool": "tests",
            "exit_code": exit_code,
            "summary": f"Tests failed: {test_summary.get('failed', 'unknown')} failures" if exit_code > 0 else "Tests timeout/error",
            "test_results": test_summary,
            "details": stderr[:20],
            "workstream_id": job["workstream_id"]
        }
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)


def run_tests_job(job: Dict[str, Any]) -> JobResult:
    """
    Convenience function for orchestrator.
    
    Args:
        job: Job dictionary conforming to job.schema.json
        
    Returns:
        JobResult with execution outcome and test summary
    """
    adapter = TestsAdapter()
    return adapter.run_job(job)
