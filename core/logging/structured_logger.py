from __future__ import annotations
import json
import sys
from typing import Any
from datetime import datetime

class StructuredLogger:
    def __init__(self, name: str = 'pipeline'):
        self.name = name
    
    def _log(self, level: str, msg: str, **context: Any) -> None:
        record = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'logger': self.name,
            'message': msg,
            **context
        }
        print(json.dumps(record), file=sys.stderr)
    
    def info(self, msg: str, **context: Any) -> None:
        self._log('INFO', msg, **context)
    
    def error(self, msg: str, **context: Any) -> None:
        self._log('ERROR', msg, **context)
    
    def warning(self, msg: str, **context: Any) -> None:
        self._log('WARNING', msg, **context)
    
    def debug(self, msg: str, **context: Any) -> None:
        self._log('DEBUG', msg, **context)
    
    def job_event(self, job_id: str, event: str, **data: Any) -> None:
        self.info(f"Job {event}", job_id=job_id, event=event, **data)
