"""Parallel execution workers

Runs scheduled workstream tasks with isolation and telemetry capture.
"""

# DOC_ID: DOC-CORE-ENGINE-EXECUTOR-149

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from core.adapters.base import ToolConfig
from core.adapters.subprocess_adapter import SubprocessAdapter
from core.engine.execution_request_builder import ExecutionRequestBuilder
from core.engine.orchestrator import Orchestrator
from core.engine.router import TaskRouter
from core.engine.scheduler import ExecutionScheduler, Task
from core.engine.state_file_manager import StateFileManager

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
        adapter_runner: Optional[
            Callable[[Task, str, Dict[str, Any]], AdapterResult]
        ] = None,
        gate_callback: Optional[Callable[[str, Task, AdapterResult], bool]] = None,
        state_manager: Optional[StateFileManager] = None,
    ):
        """
        Args:
            orchestrator: Run/state orchestrator
            router: Task router for selecting tool_id
            scheduler: Scheduler holding tasks to execute
            adapter_runner: Callable that executes a task with a tool and returns AdapterResult
                (run metadata is provided as third arg). If omitted, a default subprocess
                adapter is used based on router config.
            gate_callback: Optional quality gate callable (run_id, task, result) -> bool
        """
        self.orchestrator = orchestrator
        self.router = router
        self.scheduler = scheduler
        self.adapter_runner = adapter_runner or self._run_with_adapter
        self.gate_callback = gate_callback
        self.state_manager = state_manager or StateFileManager()

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
            # Fresh decision log per run to avoid leaking prior assignments
            if hasattr(self.router, "clear_decision_log"):
                self.router.clear_decision_log()

        sequence = 0

        while True:
            ready_tasks = self.scheduler.get_ready_tasks()
            if not ready_tasks:
                break

            for task in ready_tasks:
                sequence += 1
                self.scheduler.mark_running(task.task_id)

                tool_id = self.router.route_task(
                    task.task_kind,
                    task_id=task.task_id,
                    run_id=run_id,
                )
                task.selected_tool = tool_id

                if not tool_id:
                    task.exit_code = 1
                    task.error_log = "No capable tool found"
                    self.scheduler.mark_failed(task.task_id, "No capable tool found")
                    continue

                step_id = self.orchestrator.create_step_attempt(
                    run_id=run_id,
                    tool_id=tool_id,
                    sequence=sequence,
                    prompt=task.metadata.get("description"),
                )

                try:
                    result = self.adapter_runner(task, tool_id, run)
                except Exception as exc:  # pragma: no cover - defensive
                    # Ensure we capture execution failure cleanly
                    self.orchestrator.complete_step_attempt(
                        step_id,
                        "failed",
                        exit_code=1,
                        error_log=str(exc),
                    )
                    task.exit_code = 1
                    task.error_log = str(exc)
                    self.scheduler.mark_failed(task.task_id, str(exc))
                    continue

                exit_code = result.exit_code
                status = "succeeded" if exit_code == 0 else "failed"
                task.exit_code = exit_code
                task.output_patch_id = result.output_patch_id
                task.error_log = result.error_log
                task.result_metadata = result.metadata or {}

                # Optional quality gate hook
                if status == "succeeded" and self.gate_callback:
                    gate_passed = bool(self.gate_callback(run_id, task, result))
                    if not gate_passed:
                        status = "failed"
                        exit_code = exit_code or 1
                        task.error_log = task.error_log or "Gate rejected result"

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
                    task.error_log = (
                        task.error_log or result.error_log or "Execution failed"
                    )
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

        if self.state_manager:
            tasks = list(self.scheduler.tasks.values())
            decisions = [
                decision
                for decision in self.router.decision_log
                if getattr(decision, "run_id", None) in (None, run_id)
            ]
            self.state_manager.export_routing_decisions(run_id, decisions)
            self.state_manager.export_adapter_assignments(run_id, tasks)
            self.state_manager.export_execution_results(run_id, tasks)

        return {"run_id": run_id, "state": final_state}

    def _run_with_adapter(
        self, task: Task, tool_id: str, run: Dict[str, Any]
    ) -> AdapterResult:
        """Default adapter runner that shells out using SubprocessAdapter."""
        tool_config = self.router.get_tool_config(tool_id)
        if not tool_config:
            raise ValueError(f"Tool config not found for {tool_id}")

        config = ToolConfig(
            tool_id=tool_id,
            kind=tool_config.get("kind", "tool"),
            command=tool_config["command"],
            capabilities=tool_config.get("capabilities", {}),
            limits=tool_config.get("limits", {}),
            safety_tier=tool_config.get("safety_tier", "medium"),
        )
        adapter = SubprocessAdapter(config)

        builder = (
            ExecutionRequestBuilder()
            .with_task(task.task_kind, task.metadata.get("description", ""))
            .with_tool(tool_id, config.command)
        )

        if constraints := task.metadata.get("constraints"):
            builder.with_constraints(constraints)

        request = builder.build()
        request["project_id"] = run.get("project_id")
        request["phase_id"] = run.get("phase_id")
        request["workstream_id"] = run.get("workstream_id")

        result = adapter.execute(request, timeout=config.get_timeout())

        return AdapterResult(
            exit_code=result.exit_code,
            error_log=result.error_message or result.stderr,
            metadata={
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": result.metadata.get("command") if result.metadata else None,
            },
        )
