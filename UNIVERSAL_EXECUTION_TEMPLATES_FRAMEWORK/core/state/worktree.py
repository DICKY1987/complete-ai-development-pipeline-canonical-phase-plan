"""Git worktree helpers

Minimal helpers to create and manage per-workstream working directories.

For PH-05 we keep the implementation conservative to avoid destructive git
operations. We create a dedicated directory under ``.worktrees/<ws-id>`` and
return its path. A later phase can wire real ``git worktree`` commands.

Functions here are intentionally lightweight and easy to monkeypatch in tests.
"""
# DOC_ID: DOC-CORE-STATE-WORKTREE-176

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Tuple

__all__ = [
    "get_repo_root",
    "get_worktrees_base",
    "get_worktree_path",
    "create_worktree_for_ws",
    "validate_scope",
]


def get_repo_root() -> Path:
    cur = Path.cwd().resolve()
    while cur != cur.parent:
        if (cur / ".git").exists():
            return cur
        cur = cur.parent
    return Path.cwd().resolve()


def get_worktrees_base() -> Path:
    return get_repo_root() / ".worktrees"


def get_worktree_path(ws_id: str) -> Path:
    return get_worktrees_base() / ws_id


def create_worktree_for_ws(run_id: str, ws_id: str) -> str:
    """Create (or reuse) a dedicated directory for a workstream.

    Returns the absolute path as a string. This is a safe stub that only
    ensures the folder exists; it does not call ``git worktree``.
    """
    wt_path = get_worktree_path(ws_id)
    wt_path.mkdir(parents=True, exist_ok=True)
    return str(wt_path.resolve())


def validate_scope(worktree_path: str | Path, allowed_paths: Iterable[str]) -> Tuple[bool, List[str]]:
    """Validate that changes stay within the declared file scope.

    PH-05 provides a permissive stub that always returns OK. Tests can
    monkeypatch this to simulate violations. The function returns:

    - ok: True if within scope
    - out_of_scope_files: list of offending file paths (relative to repo root)
    """
    return True, []
