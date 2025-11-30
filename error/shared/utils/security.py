# DOC_LINK: DOC-ERROR-UTILS-SECURITY-074
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence, Union


class SecurityError(Exception):
    """Raised when security policy is violated."""


def validate_file_path(path: Union[str, Path], *, allowed_root: Union[str, Path]) -> None:
    target = Path(path)
    root = Path(allowed_root).resolve()
    if ".." in target.parts:
        raise SecurityError("Suspicious pattern in path")
    try:
        resolved = target.resolve()
    except FileNotFoundError:
        resolved = target.resolve(strict=False)
    if not str(resolved).startswith(str(root)):
        raise SecurityError("outside allowed directory")


def validate_file_size(path: Union[str, Path], *, max_size_mb: int = 1) -> None:
    target = Path(path)
    if not target.exists():
        raise SecurityError("File does not exist")
    size = target.stat().st_size
    limit = max_size_mb * 1024 * 1024
    if size > limit:
        raise SecurityError(f"File too large ({size} bytes > {limit} bytes)")


def _apply_redaction(text: str, pattern: str, replacement: str, flags: int = 0) -> str:
    return re.sub(pattern, replacement, text, flags=flags)


def redact_secrets(text: str | None) -> str | None:
    if text is None:
        return None
    redacted = text
    redacted = _apply_redaction(redacted, r"(sk-[A-Za-z0-9-]{8,})", "[REDACTED_KEY]")
    redacted = _apply_redaction(
        redacted,
        r"(OPENAI_[A-Z_]+=)(sk-[A-Za-z0-9-]+)",
        lambda match: f"{match.group(1)}[REDACTED]"
    )
    redacted = _apply_redaction(redacted, r"[Pp]assword[:=]\s*[^\\s]+", "[REDACTED_PASSWORD]")
    redacted = _apply_redaction(redacted, r"(Authorization:\s*Bearer\s+)[A-Za-z0-9_-]+", r"\1[REDACTED]")
    redacted = _apply_redaction(redacted, r"\b[a-f0-9]{40}\b", "[REDACTED_HASH]", flags=re.IGNORECASE)
    redacted = _apply_redaction(redacted, r"-----BEGIN PRIVATE KEY-----.*?-----END PRIVATE KEY-----", "[REDACTED_PRIVATE_KEY]", flags=re.DOTALL)
    return redacted


def sanitize_path_for_log(path: Union[str, Path]) -> str:
    raw = Path(path)
    text = str(raw)
    home = Path.home()
    if text.startswith(str(home)):
        text = text.replace(str(home), "~", 1)
    if text.startswith("C:\\Users\\"):
        parts = text.split("\\")
        if len(parts) > 2:
            parts[2] = "[USER]"
            text = "\\".join(parts)
    return text


def validate_command_safe(cmd: Sequence[str]) -> None:
    if not cmd:
        raise SecurityError("Empty command")
    dangerous_commands = {"rm", "format", "del", "dd"}
    for part in cmd:
        if ";" in part or "|" in part or "$(" in part or "`" in part:
            raise SecurityError("Suspicious shell characters detected")
        if part.lower() in dangerous_commands:
            raise SecurityError("Dangerous command detected")


@dataclass
class ResourceLimits:
    max_file_size_mb: int = 10
    max_execution_time_seconds: int = 120
    max_memory_mb: int = 512

    def get_timeout(self) -> int:
        return self.max_execution_time_seconds

    def validate_file(self, path: Union[str, Path]) -> None:
        validate_file_size(path, max_size_mb=self.max_file_size_mb)
