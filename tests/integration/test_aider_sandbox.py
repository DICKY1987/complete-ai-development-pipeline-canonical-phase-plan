# DOC_LINK: DOC-TEST-INTEGRATION-TEST-AIDER-SANDBOX-117
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
import sys

# Ensure repository root is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from core import prompts as aider_prompts
from core.state import db as pipeline_db


def _have_aider() -> bool:
    return shutil.which("aider") is not None


def _init_git_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=str(path), check=True, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=str(path), check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=str(path), check=True, capture_output=True)


@pytest.mark.aider
def test_aider_edit_invocation_and_prompt_file(tmp_path: Path):
    if not _have_aider():
        pytest.skip("aider not installed; skipping integration test")

    # Copy sandbox repo into temp worktree
    repo_src = Path(__file__).resolve().parents[2] / "sandbox_repos" / "sandbox_python"
    worktree = tmp_path / "wt"
    shutil.copytree(repo_src, worktree)
    _init_git_repo(worktree)

    # Minimal bundle-like dict
    bundle = {
        "id": "ws-sbx",
        "openspec_change": "OS-SBX",
        "ccpm_issue": 0,
        "gate": 1,
        "files_scope": ["src/app.py"],
        "files_create": [],
        "tasks": ["Adjust add() if needed"],
        "acceptance_tests": ["pytest -q"],
        "tool": "aider",
    }
    run_info = {"run_id": "run-sbx"}
    ws_info = {"ws_id": "ws-sbx"}
    context = {"worktree_path": str(worktree)}

    pipeline_db.init_db()
    result = aider_prompts.run_aider_edit(run_info, ws_info, bundle, context, run_id=run_info["run_id"], ws_id=ws_info["ws_id"])

    # Prompt file exists
    prompt_dir = worktree / ".aider" / "prompts"
    assert prompt_dir.exists()
    files = list(prompt_dir.glob("ws-sbx_edit_*.txt"))
    assert files, "prompt file not created"

    # Tool executed (success may vary depending on environment)
    assert "aider" in result.command_line

    # Event was recorded
    events = pipeline_db.get_events(run_id=run_info["run_id"], ws_id=ws_info["ws_id"], event_type="tool_run")
    assert len(events) >= 1

