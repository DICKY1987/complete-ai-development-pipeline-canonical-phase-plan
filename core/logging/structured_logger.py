"""Simple structured logger that writes to stderr."""
DOC_ID: DOC-CORE-LOGGING-STRUCTURED-LOGGER-867

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from typing import Any

from core.logger import Logger


class StructuredLogger(Logger):
    """Lightweight JSON-ish logger used in interface tests."""

    def __init__(self, name: str | None = None):
        self.name = name or "logger"

    def info(self, message: str, **kwargs: Any):
        self._log("INFO", message, **kwargs)

    def error(self, message: str, **kwargs: Any):
        self._log("ERROR", message, **kwargs)

    def job_event(self, job_id: str, status: str, **kwargs: Any):
        payload = {"job_id": job_id, "status": status, **kwargs}
        self._log("JOB", f"job_event:{job_id}:{status}", **payload)

    def _log(self, level: str, message: str, **kwargs: Any):
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "logger": self.name,
            "message": message,
        }
        if kwargs:
            record["data"] = kwargs
        sys.stderr.write(json.dumps(record) + "\n")
        sys.stderr.flush()


__all__ = ["StructuredLogger"]
