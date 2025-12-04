"""Minimal error analyzer for reflexion loop (WS-04-03A)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List


@dataclass
class ParsedError:
    message: str
    file: str | None = None
    line: int | None = None


class ErrorAnalyzer:
    """Parses stderr/test output into structured errors."""

    FILE_LINE_RE = re.compile(r"(?P<file>[\w./\\-]+):(?P<line>\d+)")

    @classmethod
    def parse(cls, stderr: str) -> List[ParsedError]:
        errors: List[ParsedError] = []
        for line in stderr.splitlines():
            line = line.strip()
            if not line:
                continue
            match = cls.FILE_LINE_RE.search(line)
            if match:
                errors.append(
                    ParsedError(
                        message=line,
                        file=match.group("file"),
                        line=int(match.group("line")),
                    )
                )
            else:
                errors.append(ParsedError(message=line, file=None, line=None))
        return errors
