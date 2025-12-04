"""Parallel execution workers

Runs scheduled workstream tasks with isolation and telemetry capture.
"""

# DOC_ID: DOC-CORE-ENGINE-EXECUTOR-149

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from core.engine.orchestrator import Orchestrator
from core.engine.router import TaskRouter
from core.engine.scheduler import ExecutionScheduler, Task

__all__ = ["AdapterResult", "Executor"]


@dataclass
class AdapterResult:
    """Container for adapter execution outcomes."""

    exit_code: int = 0
    output_patch_id: Optional[str] = None
    error_log: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Executor:
    """Executes scheduled tasks by routing them to adapters and updating run state."""

    def __init__(
        self,
        orchestrator: Orchestrator,
        router: TaskRouter,
        scheduler: ExecutionScheduler,
        adapter_runner: Callable[[Task, str], AdapterResult],
        gate_callback: Optional[Callable[[str, Task, AdapterResult], bool]] = None,
    ):
        """
        Args:
            orchestrator: Run/state orchestrator
            router: Task router for selecting tool_id
            scheduler: Scheduler holding tasks to execute
            adapter_runner: Callable that executes a task with a tool and returns AdapterResult
            gate_callback: Optional quality gate callable (run_id, task, result) -> bool
        """
        self.orchestrator = orchestrator
        self.router = router
        self.scheduler = scheduler
        self.adapter_runner = adapter_runner
        self.gate_callback = gate_callback

    def run(self, run_id: str) -> Dict[str, Any]:
        """Execute all ready tasks in the scheduler for the given run.

        Returns:
            Summary dict with run_id and final state.
        """
        run = self.orchestrator.get_run_status(run_id)
        if not run:
            raise ValueError(f"Run not found: {run_id}")

        if run["state"] == "pending":
            self.orchestrator.start_run(run_id)

        sequence = 0

        while True:
            ready_tasks = self.scheduler.get_ready_tasks()
            if not ready_tasks:
                break

            for task in ready_tasks:
                sequence += 1
                self.scheduler.mark_running(task.task_id)

                tool_id = self.router.route_task(task.task_kind)
                if not tool_id:
                    self.scheduler.mark_failed(task.task_id, "No capable tool found")
                    continue

                step_id = self.orchestrator.create_step_attempt(
                    run_id=run_id,
                    tool_id=tool_id,
                    sequence=sequence,
                    prompt=task.metadata.get("description"),
                )

                try:
                    result = self.adapter_runner(task, tool_id)
                except Exception as exc:  # pragma: no cover - defensive
                    # Ensure we capture execution failure cleanly
                    self.orchestrator.complete_step_attempt(
                        step_id,
                        "failed",
                        exit_code=1,
                        error_log=str(exc),
                    )
                    self.scheduler.mark_failed(task.task_id, str(exc))
                    continue

                exit_code = result.exit_code
                status = "succeeded" if exit_code == 0 else "failed"

                # Optional quality gate hook
                if status == "succeeded" and self.gate_callback:
                    gate_passed = bool(self.gate_callback(run_id, task, result))
                    if not gate_passed:
                        status = "failed"
                        exit_code = exit_code or 1

                self.orchestrator.complete_step_attempt(
                    step_id,
                    status,
                    exit_code=exit_code,
                    output_patch_id=result.output_patch_id,
                    error_log=result.error_log,
                )

                if status == "succeeded":
                    self.scheduler.mark_completed(task.task_id, result)
                else:
                    self.scheduler.mark_failed(
                        task.task_id, result.error_log or "Execution failed"
                    )

        final_state = (
            "succeeded"
            if self.scheduler.is_complete() and not self.scheduler.has_failures()
            else "failed"
        )
        exit_code = 0 if final_state == "succeeded" else 1

        self.orchestrator.complete_run(run_id, final_state, exit_code=exit_code)

        return {"run_id": run_id, "state": final_state}
