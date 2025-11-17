"""Aider prompt engine and helpers.

Builds EDIT and FIX prompts from templates and provides thin helpers to run
the Aider CLI via the tool adapter (`run_tool`). Prompt files are stored under
`<worktree>/.aider/prompts/` per workstream and step.

Moved from src/pipeline/prompts.py as part of WS-08.
"""

from __future__ import annotations

import os
import shutil
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

# Import from src.pipeline.tools - this is the correct dependency direction
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.pipeline.tools import run_tool, ToolResult

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Environment = None  # type: ignore

__all__ = [
    "build_edit_prompt",
    "build_fix_prompt",
    "prepare_aider_prompt_file",
    "run_aider_edit",
    "run_aider_fix",
    "TemplateRender",
]


def _repo_root() -> Path:
    cur = Path.cwd().resolve()
    while cur != cur.parent:
        if (cur / ".git").exists():
            return cur
        cur = cur.parent
    return Path.cwd().resolve()


def _templates_dir() -> Path:
    return _repo_root() / "aider" / "templates" / "prompts"


def _template_env() -> Optional[Environment]:  # type: ignore
    if Environment is None:
        return None
    return Environment(
        loader=FileSystemLoader(str(_templates_dir())),
        autoescape=select_autoescape(disabled_extensions=(".txt", ".j2")),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _to_plain(obj: Any) -> Any:
    if is_dataclass(obj):
        return asdict(obj)
    if hasattr(obj, "__dict__"):
        return dict(obj.__dict__)
    return obj


def _render_template(name: str, context: Mapping[str, Any]) -> str:
    env = _template_env()
    ctx = dict(context)
    if env is not None:
        tpl = env.get_template(name)
        return tpl.render(**ctx)
    # Fallback: naive formatting replacement for key placeholders
    text = (_templates_dir() / name).read_text(encoding="utf-8")
    for k, v in ctx.items():
        text = text.replace("{{ " + k + " }}", str(v))
    return text


class TemplateRender:
    """Render helper encapsulating template name + context."""

    def __init__(self, template: str, context: Mapping[str, Any]) -> None:
        self.template = template
        self.context = {k: _to_plain(v) for k, v in context.items()}

    def render(self) -> str:
        return _render_template(self.template, self.context)


def build_edit_prompt(tasks: list[str], repo_path: Path, ws_id: str, **kwargs: Any) -> str:
    """Build EDIT prompt from template tasks.txt.j2."""
    context = {
        "tasks": tasks,
        "repo_path": str(repo_path),
        "ws_id": ws_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    context.update(kwargs)
    return _render_template("tasks.txt.j2", context)


def build_fix_prompt(
    error_summary: str,
    error_details: str,
    files: list[str],
    repo_path: Path,
    ws_id: str,
    **kwargs: Any,
) -> str:
    """Build FIX prompt from template fix.txt.j2."""
    context = {
        "error_summary": error_summary,
        "error_details": error_details,
        "files": files,
        "repo_path": str(repo_path),
        "ws_id": ws_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    context.update(kwargs)
    return _render_template("fix.txt.j2", context)


def prepare_aider_prompt_file(worktree: Path, step_name: str, content: str) -> Path:
    """Write prompt content to <worktree>/.aider/prompts/<step>.txt and return path."""
    prompt_dir = worktree / ".aider" / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    out = prompt_dir / f"{step_name}.txt"
    out.write_text(content, encoding="utf-8")
    return out


def run_aider_edit(
    cwd: Path,
    files: list[str],
    tasks: list[str],
    repo_root: Path,
    ws_id: str,
    timeout_seconds: int = 300,
    **template_kwargs: Any,
) -> ToolResult:
    """Run aider in EDIT mode with generated prompt."""
    prompt = build_edit_prompt(tasks, repo_root, ws_id, **template_kwargs)
    prompt_file = prepare_aider_prompt_file(cwd, "edit", prompt)
    return run_tool(
        "aider",
        cwd=cwd,
        timeout_seconds=timeout_seconds,
        files=files,
        prompt_file=str(prompt_file),
    )


def run_aider_fix(
    cwd: Path,
    files: list[str],
    error_summary: str,
    error_details: str,
    repo_root: Path,
    ws_id: str,
    timeout_seconds: int = 300,
    **template_kwargs: Any,
) -> ToolResult:
    """Run aider in FIX mode with generated prompt."""
    prompt = build_fix_prompt(
        error_summary, error_details, files, repo_root, ws_id, **template_kwargs
    )
    prompt_file = prepare_aider_prompt_file(cwd, "fix", prompt)
    return run_tool(
        "aider",
        cwd=cwd,
        timeout_seconds=timeout_seconds,
        files=files,
        prompt_file=str(prompt_file),
    )
