"""Context manager wrapper for terminal state capture."""

from __future__ import annotations

import io
import sys
from contextlib import contextmanager
from typing import Iterator, Optional

from .state_capture import TerminalState, capture_state


@contextmanager
def TerminalContext() -> Iterator[TerminalState]:
    """Capture stdout/stderr during a block and yield the captured state."""
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()

    try:
        sys.stdout = stdout_buffer
        sys.stderr = stderr_buffer
        yield  # work happens inside caller's block
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        stdout_buffer.seek(0)
        stderr_buffer.seek(0)
        # Attach captured state to the context object for caller retrieval
        captured = capture_state(
            stdout=stdout_buffer.read(),
            stderr=stderr_buffer.read(),
            exit_code=None,
        )
        TerminalContext.last_state = captured  # type: ignore[attr-defined]


# Expose last captured state for convenience
TerminalContext.last_state: Optional[TerminalState] = None
