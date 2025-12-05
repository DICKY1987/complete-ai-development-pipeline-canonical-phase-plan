"""Reflexion loop orchestrator (WS-04-03A)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from core.memory import EpisodicMemory

from .error_analyzer import ErrorAnalyzer, ParsedError
from .fix_generator import FixGenerator

RunFn = Callable[[], Dict[str, object]]
ValidateFn = Callable[[Dict[str, object]], Dict[str, object]]


@dataclass
class AttemptResult:
    iteration: int
    success: bool
    errors: List[ParsedError] = field(default_factory=list)
    fix_applied: Optional[Dict[str, str]] = None
    details: Dict[str, object] = field(default_factory=dict)


@dataclass
class ReflexionResult:
    success: bool
    attempts: List[AttemptResult]
    escalated: bool


class ReflexionLoop:
    """Coordinates generate→validate→analyze→fix up to N iterations."""
    # DOC_ID: DOC-CORE-AUTONOMOUS-REFLEXION-612

    def __init__(
        self,
        run_fn: RunFn,
        validate_fn: ValidateFn,
        fix_generator: Optional[FixGenerator] = None,
        max_iterations: int = 3,
        memory: Optional[EpisodicMemory] = None,
    ):
        self.run_fn = run_fn
        self.validate_fn = validate_fn
        self.fix_generator = fix_generator or FixGenerator()
        self.max_iterations = max_iterations
        self.memory = memory

    def run(
        self,
        task_id: str,
        task_description: str,
        user_prompt: str,
        files_changed: List[str],
        project_conventions: Optional[List[str]] = None,
    ) -> ReflexionResult:
        attempts: List[AttemptResult] = []
        project_conventions = project_conventions or []

        for iteration in range(1, self.max_iterations + 1):
            run_output = self.run_fn()
            validation = self.validate_fn(run_output)
            success = bool(validation.get("success"))

            if success:
                attempt = AttemptResult(
                    iteration=iteration,
                    success=True,
                    errors=[],
                    fix_applied=None,
                    details=validation,
                )
                attempts.append(attempt)
                self._record_memory(
                    task_id=task_id,
                    task_description=task_description,
                    user_prompt=user_prompt,
                    files_changed=files_changed,
                    edit_accepted=True,
                    project_conventions=project_conventions,
                )
                return ReflexionResult(success=True, attempts=attempts, escalated=False)

            errors = ErrorAnalyzer.parse(validation.get("stderr", "") or "")
            fix = self.fix_generator.generate(errors, iteration)

            attempt = AttemptResult(
                iteration=iteration,
                success=False,
                errors=errors,
                fix_applied=fix,
                details=validation,
            )
            attempts.append(attempt)

        # Escalate after exhausting iterations
        self._record_memory(
            task_id=task_id,
            task_description=task_description,
            user_prompt=user_prompt,
            files_changed=files_changed,
            edit_accepted=False,
            project_conventions=project_conventions,
        )
        return ReflexionResult(success=False, attempts=attempts, escalated=True)

    def _record_memory(
        self,
        task_id: str,
        task_description: str,
        user_prompt: str,
        files_changed: List[str],
        edit_accepted: bool,
        project_conventions: List[str],
    ) -> None:
        if not self.memory:
            return
        self.memory.record_episode(
            task_id=task_id,
            task_description=task_description,
            user_prompt=user_prompt,
            files_changed=files_changed,
            edit_accepted=edit_accepted,
            project_conventions=project_conventions,
        )
