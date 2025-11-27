from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import List

from core.invoke_utils import run_command
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
        cmd_str = ' '.join(cmd)
        env = scrub_env()
        
        try:
            result = run_command(
                cmd_str,
                timeout=120,
                cwd=file_path.parent,
                env=env,
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
            data = json.loads(result.stdout or "[]")
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
        success = result.exit_code in {0, 1}
        return PluginResult(
            plugin_id=self.plugin_id,
            success=success,
            issues=issues,
            stdout=result.stdout or "",
            stderr=result.stderr or "",
            returncode=result.exit_code,
        )


def register():
    return RuffPlugin()




def parse(file_path: Path) -> PluginResult:
    """Compatibility shim matching legacy parse entrypoint."""
    plugin = RuffPlugin()
    return plugin.execute(file_path)


__all__ = ["RuffPlugin", "parse"]
