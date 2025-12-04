"""Lightweight fix generator interface for reflexion loop."""

from __future__ import annotations

from typing import Callable, Dict, List

from .error_analyzer import ParsedError

FixFn = Callable[[List[ParsedError], int], Dict[str, str]]


class FixGenerator:
    """Delegates fix generation to a provided callable or a trivial fallback."""

    def __init__(self, fix_fn: FixFn | None = None):
        self._fix_fn = fix_fn or self._default_fix

    def generate(self, errors: List[ParsedError], attempt: int) -> Dict[str, str]:
        return self._fix_fn(errors, attempt)

    @staticmethod
    def _default_fix(errors: List[ParsedError], attempt: int) -> Dict[str, str]:
        summary = "; ".join(err.message for err in errors) if errors else "no error details"
        return {
            "summary": f"Attempt {attempt}: apply generic fix for {summary}",
            "patch": "# TODO: implement fix",
        }
