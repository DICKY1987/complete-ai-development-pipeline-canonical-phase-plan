# DOC_LINK: DOC-CORE-ENGINE-ADAPTERS-081
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Sequence


@dataclass
class ExecutionResult:
    success: bool
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    duration_sec: float = 0.0
    timed_out: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class ToolAdapter:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.name: str = "tool"

    def build_command(self, task: Dict[str, Any], prompt_file: Optional[Path] = None) -> str:
        raise NotImplementedError

    def get_default_timeout(self) -> Optional[int]:
        return self.config.get("timeout")

    def get_model_name(self) -> Optional[str]:
        return self.config.get("model")


class AiderAdapter(ToolAdapter):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.name = "aider"

    def build_command(self, task: Dict[str, Any], prompt_file: Optional[Path] = None) -> str:
        parts: list[str] = ["aider", "--no-auto-commits", "--yes"]
        model = self.get_model_name()
        if model:
            parts.extend(["--model", model])
        if prompt_file:
            parts.extend(["--message-file", str(prompt_file)])

        if task.get("mode") == "patch_apply_validate":
            patch_file = task.get("payload", {}).get("patch_file", "patch.diff")
            parts.extend(["git", "apply", str(patch_file)])
        return " ".join(parts)


class CodexAdapter(ToolAdapter):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.name = "codex"

    def build_command(self, task: Dict[str, Any], prompt_file: Optional[Path] = None) -> str:
        parts = ["gh", "copilot", "suggest"]
        if prompt_file:
            parts.extend(["--file", str(prompt_file)])
        return " ".join(parts)


class ClaudeAdapter(ToolAdapter):
    SUPPORTED_MODES: Sequence[str] = ("prompt", "review")

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.name = "claude"

    def build_command(self, task: Dict[str, Any], prompt_file: Optional[Path] = None) -> str:
        mode = task.get("mode", "prompt")
        if mode not in self.SUPPORTED_MODES:
            raise ValueError(f"Unsupported mode: {mode}")

        parts = ["claude"]
        model = self.get_model_name() or "claude-3-opus"
        parts.extend(["--model", model])
        if mode == "review":
            parts.append("review")
        if prompt_file:
            parts.extend(["--input-file", str(prompt_file)])
        return " ".join(parts)

