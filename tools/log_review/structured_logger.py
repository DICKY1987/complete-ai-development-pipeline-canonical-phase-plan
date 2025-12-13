"""Simple structured logger that writes to stderr."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from typing import Any


class StructuredLogger:
    """Lightweight JSON logger for structured logging.
    
    Implements the Logger protocol with JSON output to stderr.
    """

    def __init__(self, name: str = "pipeline"):
        self.name = name

    def info(self, msg: str, **context: Any) -> None:
        self._log("INFO", msg, **context)

    def error(self, msg: str, **context: Any) -> None:
        self._log("ERROR", msg, **context)

    def warning(self, msg: str, **context: Any) -> None:
        self._log("WARNING", msg, **context)

    def debug(self, msg: str, **context: Any) -> None:
        self._log("DEBUG", msg, **context)

    def job_event(self, job_id: str, event: str, **data: Any) -> None:
        """Log job-specific event."""
        payload = {"job_id": job_id, "event": event, **data}
        self._log("JOB", f"job_event:{job_id}:{event}", **payload)

    def _log(self, level: str, msg: str, **context: Any) -> None:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "logger": self.name,
            "message": msg,
        }
        if context:
            record["data"] = context
        print(json.dumps(record), file=sys.stderr, flush=True)


__all__ = ["StructuredLogger"]
