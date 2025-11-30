"""
GitHub sync helpers for CCPM integration.

Primary path uses the `gh` CLI when present. Fallback is a no-op unless a
`GITHUB_TOKEN` and repo config are supplied (REST API can be added later).

All functions are safe to call when disabled; they become no-ops.
Enable via env var `ENABLE_GH_SYNC=true` or config `config/github.yaml`.
"""
# DOC_ID: DOC-PM-PM-GITHUB-SYNC-044

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional


_CFG_DEFAULT = {
    "enable-sync": False,
    "owner": "",
    "repo": "",
    "default-labels": ["pipeline"],
}


def _repo_root() -> Path:
    cur = Path.cwd().resolve()
    while cur != cur.parent:
        if (cur / ".git").exists():
            return cur
        cur = cur.parent
    return Path.cwd().resolve()


def _load_cfg() -> dict[str, Any]:
    cfg_path = _repo_root() / "config" / "github.yaml"
    data = dict(_CFG_DEFAULT)
    if cfg_path.exists():
        try:
            import yaml  # type: ignore

            y = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
            if isinstance(y, dict):
                data.update({k: v for k, v in y.items() if v is not None})
        except Exception:
            pass
    # env overrides
    if os.getenv("ENABLE_GH_SYNC") is not None:
        data["enable-sync"] = os.getenv("ENABLE_GH_SYNC", "").lower() in {"1", "true", "yes"}
    if os.getenv("GITHUB_OWNER"):
        data["owner"] = os.getenv("GITHUB_OWNER")
    if os.getenv("GITHUB_REPO"):
        data["repo"] = os.getenv("GITHUB_REPO")
    return data


def _enabled() -> bool:
    cfg = _load_cfg()
    return bool(cfg.get("enable-sync"))


def _gh_available() -> bool:
    return shutil.which("gh") is not None


def _gh_repo_args() -> list[str]:
    cfg = _load_cfg()
    owner = (cfg.get("owner") or "").strip()
    repo = (cfg.get("repo") or "").strip()
    if owner and repo:
        return ["--repo", f"{owner}/{repo}"]
    return []


def _run(cmd: list[str], timeout: int = 30) -> tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except Exception as e:
        return 1, "", str(e)


def comment(issue_number: int | str, text: str) -> bool:
    """Post a comment to an issue when enabled. Returns True on success.

    Safe no-op when disabled or gh not present.
    """
    if not _enabled() or not _gh_available():
        return False
    args = ["gh", "issue", "comment", str(issue_number), "-b", text]
    args.extend(_gh_repo_args())
    code, _, _ = _run(args)
    return code == 0


def ensure_epic(title: str, body: str = "", labels: Optional[Iterable[str]] = None) -> Optional[int]:
    """Find or create an epic issue; returns issue number or None.

    Heuristic: search by title; if not found, create with labels.
    """
    if not _enabled() or not _gh_available():
        return None
    # search by title
    search = [
        "gh",
        "issue",
        "list",
        "--search",
        title,
        "--json",
        "number,title",
    ]
    search.extend(_gh_repo_args())
    code, out, _ = _run(search)
    if code == 0 and out.strip():
        try:
            items = json.loads(out)
            for it in items:
                if (it.get("title") or "").strip().lower() == title.strip().lower():
                    return int(it.get("number"))
        except Exception:
            pass
    # create
    args = ["gh", "issue", "create", "--title", title]
    if body:
        args += ["--body", body]
    for lab in (labels or _load_cfg().get("default-labels") or []):
        args += ["--label", lab]
    args.extend(_gh_repo_args())
    code, out, _ = _run(args)
    if code == 0:
        # `gh issue create` prints URL on success; fetch number via last list
        # As a simple approach, attempt a fresh search again
        code2, out2, _ = _run(search)
        if code2 == 0 and out2.strip():
            try:
                items = json.loads(out2)
                for it in items:
                    if (it.get("title") or "").strip().lower() == title.strip().lower():
                        return int(it.get("number"))
            except Exception:
                return None
    return None


def set_status(issue_number: int | str, state: str = "", add_labels: Optional[Iterable[str]] = None) -> bool:
    """Update labels and/or close/open the issue. Returns True on partial/total success.

    Safe no-op when disabled or gh not present.
    """
    if not _enabled() or not _gh_available():
        return False

    ok = True
    if add_labels:
        args = ["gh", "issue", "edit", str(issue_number)]
        for lab in add_labels:
            args += ["--add-label", lab]
        args.extend(_gh_repo_args())
        code, _, _ = _run(args)
        ok = ok and (code == 0)

    if state:
        # allowed states: open|closed
        args2 = ["gh", "issue", "edit", str(issue_number), "--state", state]
        args2.extend(_gh_repo_args())
        code2, _, _ = _run(args2)
        ok = ok and (code2 == 0)
    return ok


@dataclass
class LifecycleEvent:
    run_id: str
    ws_id: str
    step: str
    final_status: str | None = None


def post_lifecycle_comment(issue_number: int | str, ev: LifecycleEvent) -> bool:
    """Format and post a concise lifecycle comment."""
    msg = []
    if ev.step == "workstream_start":
        msg.append(f"WS {ev.ws_id} started (run {ev.run_id}).")
    elif ev.step == "workstream_end":
        msg.append(f"WS {ev.ws_id} finished (run {ev.run_id}) → {ev.final_status}.")
    else:
        msg.append(f"WS {ev.ws_id} event: {ev.step} (run {ev.run_id}).")
    return comment(issue_number, "\n".join(msg))

