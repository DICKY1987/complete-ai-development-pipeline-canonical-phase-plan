# DOC_LINK: DOC-CORE-CONTRACTS-TEMPLATE-GIT-HELPER-204
# TEMPLATE: Git/Worktree Helper Module
# Purpose: Implements GitWorkspaceRefV1/GitStatusV1 contracts
# Location: modules/git_shared/{name}.py

"""
Git Workspace Helper

Manages git operations following UET contracts.
"""

import subprocess
from pathlib import Path
from typing import Optional, List
from modules.shared_types import GitWorkspaceRefV1, GitStatusV1
from modules.logging_shared import log_event
from modules.error_shared import build_error


class WorkspaceError(Exception):
    """Raised when workspace operations fail."""
    pass


def create_worktree_for_ws(ws_id: str, base_path: Optional[str] = None) -> GitWorkspaceRefV1:
    """
    Create or reuse a worktree for the given workstream.

    REQUIRED CONTRACT:
    - Creates worktree in standardized location
    - Returns GitWorkspaceRefV1
    - Idempotent - safe to call multiple times

    Args:
        ws_id: Workstream identifier (e.g. "WS-01")
        base_path: Optional base directory for worktrees

    Returns:
        GitWorkspaceRefV1 with workspace details

    Raises:
        WorkspaceError: If worktree creation fails
    """
    try:
        # 1. Determine worktree path
        if base_path is None:
            base_path = Path.cwd() / ".worktrees"

        worktree_path = Path(base_path) / ws_id

        # 2. Check if worktree already exists
        if worktree_path.exists():
            log_event({
                "event_type": "worktree.reused",
                "summary": f"Reusing existing worktree for {ws_id}",
                "details": {"ws_id": ws_id, "path": str(worktree_path)}
            })
            return {
                "workspace": ws_id,
                "root_path": str(worktree_path.resolve()),
            }

        # 3. Create new worktree
        worktree_path.parent.mkdir(parents=True, exist_ok=True)

        _run_git_command(
            ["git", "worktree", "add", str(worktree_path), "-b", f"ws-{ws_id}"],
            cwd=Path.cwd()
        )

        # 4. Log creation
        log_event({
            "event_type": "worktree.created",
            "summary": f"Created worktree for {ws_id}",
            "details": {"ws_id": ws_id, "path": str(worktree_path)}
        })

        # 5. Return reference
        return {
            "workspace": ws_id,
            "root_path": str(worktree_path.resolve()),
        }

    except subprocess.CalledProcessError as e:
        raise WorkspaceError(f"Failed to create worktree for {ws_id}: {e.stderr}")


def get_workspace_status(workspace: str) -> GitStatusV1:
    """
    Get status of a git workspace.

    REQUIRED CONTRACT:
    - Returns ahead/behind, dirty_files for workspace
    - Never modifies workspace

    Args:
        workspace: Workspace identifier or "main"

    Returns:
        GitStatusV1 with workspace status

    Raises:
        WorkspaceError: If workspace doesn't exist or git fails
    """
    try:
        # 1. Determine workspace path
        if workspace == "main":
            ws_path = Path.cwd()
        else:
            ws_path = Path.cwd() / ".worktrees" / workspace

        if not ws_path.exists():
            raise WorkspaceError(f"Workspace {workspace} not found at {ws_path}")

        # 2. Get dirty files
        result = _run_git_command(
            ["git", "status", "--porcelain"],
            cwd=ws_path
        )
        dirty_files = [
            line[3:].strip()
            for line in result.stdout.splitlines()
            if line.strip()
        ]

        # 3. Get ahead/behind info
        result = _run_git_command(
            ["git", "rev-list", "--left-right", "--count", "HEAD...@{upstream}"],
            cwd=ws_path
        )
        ahead_behind = result.stdout.strip().split()
        ahead_by = int(ahead_behind[0]) if len(ahead_behind) > 0 else 0
        behind_by = int(ahead_behind[1]) if len(ahead_behind) > 1 else 0

        # 4. Build status
        status: GitStatusV1 = {
            "workspace": workspace,
            "dirty_files": dirty_files,
            "ahead_by": ahead_by,
            "behind_by": behind_by,
        }

        return status

    except subprocess.CalledProcessError as e:
        raise WorkspaceError(f"Failed to get status for {workspace}: {e.stderr}")


def ensure_clean_workspace(workspace: str, allow_untracked: bool = False) -> None:
    """
    Ensure workspace has no uncommitted changes.

    REQUIRED CONTRACT:
    - Raises WorkspaceError if workspace is dirty
    - Never modifies workspace (no auto-commit/stash)

    Args:
        workspace: Workspace identifier
        allow_untracked: If True, allow untracked files

    Raises:
        WorkspaceError: If workspace has uncommitted changes
    """
    status = get_workspace_status(workspace)

    # Filter out untracked files if allowed
    if allow_untracked:
        # Untracked files start with "??" in porcelain format
        # But we already stripped the status prefix in get_workspace_status
        # So we need to re-check with full status
        dirty_files = [f for f in status["dirty_files"] if not f.startswith("??")]
    else:
        dirty_files = status["dirty_files"]

    if dirty_files:
        raise WorkspaceError(
            f"Workspace {workspace} has uncommitted changes:\n" +
            "\n".join(f"  - {f}" for f in dirty_files[:10]) +
            (f"\n  ... and {len(dirty_files) - 10} more" if len(dirty_files) > 10 else "")
        )


def remove_worktree(ws_id: str, force: bool = False) -> None:
    """
    Remove a worktree.

    Args:
        ws_id: Workstream identifier
        force: If True, remove even if dirty

    Raises:
        WorkspaceError: If removal fails
    """
    try:
        worktree_path = Path.cwd() / ".worktrees" / ws_id

        if not worktree_path.exists():
            log_event({
                "event_type": "worktree.already_removed",
                "summary": f"Worktree {ws_id} already removed",
                "details": {"ws_id": ws_id}
            })
            return

        # Check if clean (unless force=True)
        if not force:
            ensure_clean_workspace(ws_id)

        # Remove worktree
        _run_git_command(
            ["git", "worktree", "remove", str(worktree_path)] +
            (["--force"] if force else []),
            cwd=Path.cwd()
        )

        log_event({
            "event_type": "worktree.removed",
            "summary": f"Removed worktree {ws_id}",
            "details": {"ws_id": ws_id, "forced": force}
        })

    except subprocess.CalledProcessError as e:
        raise WorkspaceError(f"Failed to remove worktree {ws_id}: {e.stderr}")


# Internal helpers (prefix with _)

def _run_git_command(cmd: List[str], cwd: Path) -> subprocess.CompletedProcess:
    """
    Run git command and return result.

    Internal helper - do not call directly from other modules.

    Args:
        cmd: Git command and arguments
        cwd: Working directory

    Returns:
        CompletedProcess with stdout/stderr

    Raises:
        subprocess.CalledProcessError: If command fails
    """
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True
    )
    return result
