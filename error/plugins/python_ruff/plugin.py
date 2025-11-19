from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import List

from error.shared.utils.env import scrub_env
from error.shared.utils.types import PluginIssue, PluginResult


class RuffPlugin:
    plugin_id = "python_ruff"
    name = "Ruff Linter"
    manifest = {}

    def check_tool_available(self) -> bool:
        return shutil.which("ruff") is not None

    def build_command(self, file_path: Path) -> List[str]:
        return ["ruff", "check", "--output-format", "json", str(file_path)]

    def execute(self, file_path: Path) -> PluginResult:
        cmd = self.build_command(file_path)
        env = scrub_env()
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(file_path.parent),
                env=env,
                shell=False,
            )
        except Exception as exc:
            return PluginResult(
                plugin_id=self.plugin_id,
                success=False,
                stderr=str(exc),
                stdout="",
                returncode=1,
            )

        issues: List[PluginIssue] = []
        try:
            data = json.loads(proc.stdout or "[]")
            # Ruff emits a list of findings
            for item in data:
                code = item.get("code")
                msg = item.get("message")
                loc = item.get("location", {})
                path = item.get("filename") or str(file_path)
                line = loc.get("row") or loc.get("line")
                col = loc.get("column")
                # Map to normalized issue
                issues.append(
                    PluginIssue(
                        tool="ruff",
                        path=path,
                        line=line,
                        column=col,
                        code=str(code) if code is not None else None,
                        category="style",
                        severity="warning",
                        message=msg,
                    )
                )
        except Exception:
            # If JSON parsing fails, do not raise; return empty issues but keep stderr
            pass

        # Ruff returns 1 when issues found, 0 otherwise — both are successful executions.
        success = proc.returncode in {0, 1}
        return PluginResult(
            plugin_id=self.plugin_id,
            success=success,
            issues=issues,
            stdout=proc.stdout or "",
            stderr=proc.stderr or "",
            returncode=proc.returncode,
        )


def register():
    return RuffPlugin()

