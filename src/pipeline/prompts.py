"""Aider prompt engine and helpers.

Builds EDIT and FIX prompts from templates and provides thin helpers to run
the Aider CLI via the tool adapter (`run_tool`). Prompt files are stored under
`<worktree>/.aider/prompts/` per workstream and step.
"""

from __future__ import annotations

import os
import shutil
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from .tools import run_tool, ToolResult

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
]


def _repo_root() -> Path:
    cur = Path.cwd().resolve()
    while cur != cur.parent:
        if (cur / ".git").exists():
            return cur
        cur = cur.parent
    return Path.cwd().resolve()


def _templates_dir() -> Path:
    return _repo_root() / "templates" / "prompts"


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


def build_edit_prompt(run_info: Mapping[str, Any], ws_info: Mapping[str, Any], bundle: Any, context: Mapping[str, Any]) -> str:
    b = _to_plain(bundle)
    ctx = {
        "run_id": run_info.get("run_id"),
        "ws_id": ws_info.get("ws_id") or b.get("id"),
        "openspec_change": b.get("openspec_change"),
        "ccpm_issue": b.get("ccpm_issue"),
        "gate": b.get("gate"),
        "tasks": b.get("tasks", []),
        "acceptance_tests": b.get("acceptance_tests", []),
        "files_scope": b.get("files_scope", []),
        "files_create": b.get("files_create", []),
        "worktree_path": context.get("worktree_path"),
        "repo_root": str(_repo_root()),
    }
    return _render_template("edit_prompt.txt.j2", ctx)


def build_fix_prompt(run_info: Mapping[str, Any], ws_info: Mapping[str, Any], bundle: Any, errors: Any, context: Mapping[str, Any]) -> str:
    b = _to_plain(bundle)
    # Summarize errors into short strings
    def _summ(e: Any) -> str:
        s = str(e)
        return s if len(s) <= 400 else (s[:397] + "...")

    error_summaries = []
    if isinstance(errors, (list, tuple)):
        error_summaries = [_summ(e) for e in errors]
    elif errors is not None:
        error_summaries = [_summ(errors)]

    ctx = {
        "run_id": run_info.get("run_id"),
        "ws_id": ws_info.get("ws_id") or b.get("id"),
        "openspec_change": b.get("openspec_change"),
        "ccpm_issue": b.get("ccpm_issue"),
        "gate": b.get("gate"),
        "tasks": b.get("tasks", []),
        "acceptance_tests": b.get("acceptance_tests", []),
        "files_scope": b.get("files_scope", []),
        "files_create": b.get("files_create", []),
        "worktree_path": context.get("worktree_path"),
        "repo_root": str(_repo_root()),
        "error_summaries": error_summaries,
    }
    return _render_template("fix_prompt.txt.j2", ctx)


def prepare_aider_prompt_file(prompt_text: str, worktree_path: str | os.PathLike[str], ws_id: str, step_name: str) -> str:
    base = Path(worktree_path)
    out_dir = base / ".aider" / "prompts"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    fname = f"{ws_id}_{step_name}_{ts}.txt"
    prompt_file = out_dir / fname
    prompt_file.write_text(prompt_text, encoding="utf-8")
    return str(prompt_file.resolve())


def _aider_available() -> bool:
    return shutil.which("aider") is not None


def run_aider_edit(run_info: Mapping[str, Any], ws_info: Mapping[str, Any], bundle: Any, context: Mapping[str, Any], *, run_id: Optional[str] = None, ws_id: Optional[str] = None) -> ToolResult:
    prompt = build_edit_prompt(run_info, ws_info, bundle, context)
    worktree_path = context.get("worktree_path")
    if not worktree_path:
        raise ValueError("context.worktree_path is required")
    ws_identifier = ws_id or ws_info.get("ws_id") or getattr(bundle, "id", None) or _to_plain(bundle).get("id")
    prompt_file = prepare_aider_prompt_file(prompt, worktree_path, ws_identifier, "edit")

    tool_ctx = {
        "model_name": context.get("model_name", os.getenv("AIDER_MODEL", "gpt-4o-mini")),
        "prompt_file": prompt_file,
        "worktree_path": worktree_path,
    }
    result = run_tool("aider", tool_ctx, run_id=run_id, ws_id=ws_id or ws_identifier)

    # Record event if DB available
    try:
        from . import db

        db.init_db()
        payload = {
            "tool_result": result.to_dict(),
            "step": "edit",
            "prompt_file": prompt_file,
        }
        db.record_event(
            event_type="tool_run",
            run_id=run_id,
            ws_id=ws_id or ws_identifier,
            payload=payload,
        )
    except Exception:
        pass

    return result


def run_aider_fix(run_info: Mapping[str, Any], ws_info: Mapping[str, Any], bundle: Any, errors: Any, context: Mapping[str, Any], *, run_id: Optional[str] = None, ws_id: Optional[str] = None) -> ToolResult:
    prompt = build_fix_prompt(run_info, ws_info, bundle, errors, context)
    worktree_path = context.get("worktree_path")
    if not worktree_path:
        raise ValueError("context.worktree_path is required")
    ws_identifier = ws_id or ws_info.get("ws_id") or getattr(bundle, "id", None) or _to_plain(bundle).get("id")
    prompt_file = prepare_aider_prompt_file(prompt, worktree_path, ws_identifier, "fix")

    tool_ctx = {
        "model_name": context.get("model_name", os.getenv("AIDER_MODEL", "gpt-4o-mini")),
        "prompt_file": prompt_file,
        "worktree_path": worktree_path,
    }
    result = run_tool("aider", tool_ctx, run_id=run_id, ws_id=ws_id or ws_identifier)

    # Record event
    try:
        from . import db

        db.init_db()
        payload = {
            "tool_result": result.to_dict(),
            "step": "fix",
            "prompt_file": prompt_file,
        }
        db.record_event(
            event_type="tool_run",
            run_id=run_id,
            ws_id=ws_id or ws_identifier,
            payload=payload,
        )
    except Exception:
        pass

    return result
