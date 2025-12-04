"""Capture terminal state for reflexion/integration (WS-04-03D)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List, Optional


def _tail(lines: List[str], limit: int = 100) -> List[str]:
    return lines[-limit:] if limit > 0 else []


def _sanitize_env(env: Dict[str, str]) -> Dict[str, str]:
    """Drop likely-secret env keys."""
DOC_ID: DOC-CORE-TERMINAL-STATE-CAPTURE-620
    filtered = {}
    for key, value in env.items():
        if any(
            term in key.upper()
            for term in ["SECRET", "TOKEN", "KEY", "PASSWORD", "PWD"]
        ):
            continue
        filtered[key] = value
    return filtered


@dataclass
class TerminalState:
    stdout_tail: List[str]
    stderr_tail: List[str]
    exit_code: Optional[int]
    cwd: str
    env: Dict[str, str]


def capture_state(
    stdout: str = "",
    stderr: str = "",
    exit_code: Optional[int] = None,
    tail_lines: int = 100,
) -> TerminalState:
    stdout_lines = stdout.splitlines()
    stderr_lines = stderr.splitlines()
    env = _sanitize_env(dict(os.environ))
    return TerminalState(
        stdout_tail=_tail(stdout_lines, tail_lines),
        stderr_tail=_tail(stderr_lines, tail_lines),
        exit_code=exit_code,
        cwd=os.getcwd(),
        env=env,
    )
