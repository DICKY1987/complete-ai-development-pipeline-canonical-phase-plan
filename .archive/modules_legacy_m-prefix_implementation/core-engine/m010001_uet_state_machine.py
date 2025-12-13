# DOC_LINK: DOC-PAT-CORE-ENGINE-M010001-UET-STATE-MACHINE-517
from __future__ import annotations


class RunStateMachine:
    """Minimal Run state machine placeholder for imports."""

    VALID_STATES = {
        "pending": ["running", "canceled"],
        "running": ["succeeded", "failed", "canceled", "quarantined"],
        "succeeded": [],
        "failed": ["quarantined"],
        "canceled": [],
        "quarantined": [],
    }

    @staticmethod
    def validate_transition(current: str, target: str) -> str | None:
        if target not in RunStateMachine.VALID_STATES.get(current, []):
            return f"Invalid transition {current} -> {target}"
        return None


class StepStateMachine:
    """Minimal Step state machine placeholder."""

    VALID_STATES = {
        "running": ["succeeded", "failed", "canceled"],
        "succeeded": [],
        "failed": [],
        "canceled": [],
    }

    @staticmethod
    def validate_transition(current: str, target: str) -> str | None:
        if target not in StepStateMachine.VALID_STATES.get(current, []):
            return f"Invalid transition {current} -> {target}"
        return None


__all__ = ["RunStateMachine", "StepStateMachine"]
