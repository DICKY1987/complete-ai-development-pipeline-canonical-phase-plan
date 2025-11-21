"""
ADAPTER_ROLE: job_orchestrator
VERSION: 0.1.0

RESPONSIBILITY:
- Accept jobs from CLI (run-job) or GUI via state store.
- Dispatch jobs to the correct tool adapter.
- Capture logs, exit code, and error info.
- Update job and workstream status in the state store.

CLI Usage:
    python -m engine.orchestrator run-job --job-file path/to/job.json
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, Any, Callable, Optional
from engine.types import JobResult, Job
from engine.adapters.aider_adapter import run_aider_job
from engine.adapters.codex_adapter import run_codex_job
from engine.adapters.tests_adapter import run_tests_job
from engine.adapters.git_adapter import run_git_job
from engine.state_store.job_state_store import JobStateStore
from engine.interfaces import StateInterface


class Orchestrator:
    """Job orchestrator for the AI Development Pipeline."""
    
    TOOL_RUNNERS: Dict[str, Callable] = {
        "aider": run_aider_job,
        "codex": run_codex_job,
        "tests": run_tests_job,
        "git": run_git_job,
    }
    
    def __init__(self, state_store: Optional[StateInterface] = None):
        """
        Initialize orchestrator.
        
        Args:
            state_store: Optional StateInterface implementation
                        (defaults to JobStateStore)
        """
        self.state_store = state_store or JobStateStore()
    
    def run_job(self, job_file: str) -> JobResult:
        """
        Execute a job from a job file.
        
        Args:
            job_file: Path to JSON file conforming to job.schema.json
            
        Returns:
            JobResult with execution outcome
        """
        job_path = Path(job_file)
        if not job_path.exists():
            return JobResult(
                exit_code=-3,
                error_report_path="",
                duration_s=0.0,
                stderr=f"Job file not found: {job_file}",
                success=False
            )
        
        with open(job_path, "r", encoding="utf-8") as f:
            job_dict = json.load(f)
        
        job = Job.from_dict(job_dict)
        
        print(f"[Orchestrator] Starting job: {job.job_id}")
        print(f"[Orchestrator] Tool: {job.tool}")
        print(f"[Orchestrator] Workstream: {job.workstream_id}")
        
        if job.tool not in self.TOOL_RUNNERS:
            return JobResult(
                exit_code=-4,
                error_report_path="",
                duration_s=0.0,
                stderr=f"No adapter found for tool: {job.tool}",
                success=False
            )
        
        runner = self.TOOL_RUNNERS[job.tool]
        
        # Mark job as running in state store
        try:
            self.state_store.mark_job_running(job.job_id)
            print(f"[Orchestrator] Marked job as running: {job.job_id}")
        except Exception as e:
            print(f"[Orchestrator] Warning: Could not mark job running: {e}")
        
        result = runner(job_dict)
        
        # Update state store with result
        try:
            self.state_store.update_job_result(job_dict, result)
            print(f"[Orchestrator] Updated state store with result")
        except Exception as e:
            print(f"[Orchestrator] Warning: Could not update state: {e}")
        
        print(f"[Orchestrator] Job completed: {job.job_id}")
        print(f"[Orchestrator] Exit code: {result.exit_code}")
        print(f"[Orchestrator] Duration: {result.duration_s:.2f}s")
        print(f"[Orchestrator] Success: {result.success}")
        
        return result
    
    def queue_job(self, job: Dict[str, Any]) -> str:
        """
        Queue a job for execution.
        
        Args:
            job: Job dictionary
            
        Returns:
            job_id for the queued job
        """
        # TODO: Implement job queue
        # For now, just return the job_id
        return job["job_id"]
    
    def get_job_status(self, job_id: str) -> str:
        """
        Get current status of a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Status string (queued, running, completed, failed, quarantined)
        """
        return self.state_store.get_job_status(job_id)


def main():
    """CLI entry point for orchestrator."""
    parser = argparse.ArgumentParser(
        description="AI Development Pipeline Job Orchestrator"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    run_parser = subparsers.add_parser("run-job", help="Run a job from file")
    run_parser.add_argument(
        "--job-file",
        required=True,
        help="Path to job JSON file"
    )
    
    args = parser.parse_args()
    
    if args.command == "run-job":
        orchestrator = Orchestrator()
        result = orchestrator.run_job(args.job_file)
        
        sys.exit(0 if result.success else result.exit_code)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
