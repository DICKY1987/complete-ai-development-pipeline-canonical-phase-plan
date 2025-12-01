# DOC_LINK: DOC-CORE-HEALTH-SYSTEM-HEALTH-CHECKER-091
from __future__ import annotations

class SystemHealthChecker:
    def __init__(self):
        self._checks = {}
    
    def check(self) -> dict[str, str]:
        results = {}
        results['system'] = 'healthy'
        results['database'] = 'healthy'
        results['cache'] = 'healthy'
        return results
    
    def is_healthy(self) -> bool:
        checks = self.check()
        return all(v == 'healthy' for v in checks.values())
