"""
ADAPTER_ROLE: terminal_tool_adapter
TOOL: aider
VERSION: 0.1.0

RESPONSIBILITY:
- Accept a job dict (from orchestrator).
- Build the aider CLI command.
- Run it in a subprocess (PTY on Unix, subprocess on Windows).
- Stream logs to job['paths']['log_file'].
- Return a JobResult object (exit_code, error_report_path, duration_s).
"""
# DOC_ID: DOC-PAT-ADAPTERS-AIDER-ADAPTER-440

import json
import subprocess
import time
from pathlib import Path
from typing import Dict, Any
from engine.types import JobResult


class AiderAdapter:
    """Adapter for executing Aider AI coding assistant jobs."""
    
    def __init__(self):
        self.tool_name = "aider"
    
    def run_job(self, job: Dict[str, Any]) -> JobResult:
        """Execute an Aider job."""
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
                log.write(f"=== Aider Job: {job['job_id']} ===\n")
                log.write(f"Command: {' '.join(command)}\n")
                log.write(f"Working dir: {paths['working_dir']}\n\n")
                log.flush()
                
                result = subprocess.run(
                    command,
                    cwd=paths["working_dir"],
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=job.get("metadata", {}).get("timeout_seconds", 600)
                )
                
                stdout_lines = result.stdout.split("\n") if result.stdout else []
                stderr_lines = result.stderr.split("\n") if result.stderr else []
                
                log.write("=== STDOUT ===\n")
                log.write(result.stdout or "(empty)\n")
                log.write("\n=== STDERR ===\n")
                log.write(result.stderr or "(empty)\n")
                log.write(f"\n=== Exit Code: {result.returncode} ===\n")
                
                exit_code = result.returncode
                
        except subprocess.TimeoutExpired as e:
            exit_code = -1
            stderr_lines = [f"Timeout after {e.timeout} seconds"]
            with open(log_file, "a", encoding="utf-8") as log:
                log.write(f"\n=== TIMEOUT ({e.timeout}s) ===\n")
        except Exception as e:
            exit_code = -2
            stderr_lines = [f"Execution error: {str(e)}"]
            with open(log_file, "a", encoding="utf-8") as log:
                log.write(f"\n=== ERROR ===\n{str(e)}\n")
        
        duration = time.time() - start_time
        
        if exit_code != 0:
            self._write_error_report(error_report, job, exit_code, stderr_lines)
        
        return JobResult(
            exit_code=exit_code,
            error_report_path=str(error_report),
            duration_s=duration,
            stdout="\n".join(stdout_lines[:100]),
            stderr="\n".join(stderr_lines[:50]),
            success=(exit_code == 0)
        )
    
    def validate_job(self, job: Dict[str, Any]) -> bool:
        """Validate that job has required fields for Aider."""
        required = ["job_id", "workstream_id", "tool", "command", "env", "paths"]
        if not all(k in job for k in required):
            return False
        
        if job["tool"] != "aider":
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
        """Get Aider tool metadata."""
        return {
            "tool": "aider",
            "adapter_version": "0.1.0",
            "capabilities": ["code_generation", "code_editing", "refactoring"],
            "requires_env": ["OLLAMA_API_BASE", "OPENAI_API_KEY"]
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
        return env
    
    def _write_error_report(self, path: Path, job: Dict[str, Any], 
                           exit_code: int, stderr: list):
        """Write error report JSON."""
        path.parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            "job_id": job["job_id"],
            "tool": "aider",
            "exit_code": exit_code,
            "summary": "Aider execution failed" if exit_code > 0 else "Aider timeout/error",
            "details": stderr[:20],
            "workstream_id": job["workstream_id"]
        }
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)


def run_aider_job(job: Dict[str, Any]) -> JobResult:
    """
    Convenience function for orchestrator.
    
    Args:
        job: Job dictionary conforming to job.schema.json
        
    Returns:
        JobResult with execution outcome
    """
    adapter = AiderAdapter()
    return adapter.run_job(job)
