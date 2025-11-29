from __future__ import annotations
from collections import defaultdict

class SimpleMetricsCollector:
    def __init__(self):
        self._counters: dict[str, int] = defaultdict(int)
        self._gauges: dict[str, float] = {}
        self._timings: dict[str, list[float]] = defaultdict(list)
    
    def increment(self, metric: str, value: int = 1) -> None:
        self._counters[metric] += value
    
    def gauge(self, metric: str, value: float) -> None:
        self._gauges[metric] = value
    
    def timing(self, metric: str, duration_ms: float) -> None:
        self._timings[metric].append(duration_ms)
    
    def get_stats(self) -> dict:
        return {
            'counters': dict(self._counters),
            'gauges': dict(self._gauges),
            'timings': {k: sum(v)/len(v) if v else 0 for k, v in self._timings.items()}
        }
