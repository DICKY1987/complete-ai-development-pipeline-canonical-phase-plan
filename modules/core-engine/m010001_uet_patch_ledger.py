from __future__ import annotations


class PatchLedger:
    """Stub patch ledger used for dependency resolution."""

    TERMINAL_STATES = {"committed", "rolled_back", "dropped"}

    def record(self, patch_id: str, state: str) -> None:
        del patch_id, state


class ValidationResult:
    def __init__(self, ok: bool, message: str = ""):
        self.ok = ok
        self.message = message


__all__ = ["PatchLedger", "ValidationResult"]
