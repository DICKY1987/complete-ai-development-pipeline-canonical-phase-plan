"""Metrics aggregation and reporting."""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ExecutionMetrics:
    run_id: str
    total_duration_sec: float = 0.0
    total_cost_usd: float = 0.0
    total_tokens: int = 0
    workstreams_completed: int = 0
    workstreams_failed: int = 0
    parallelism_efficiency: float = 0.0
    bottlenecks: List[str] = None
    error_frequency: Dict[str, int] = None


class MetricsAggregator:
    """Metrics and observability."""
    
    def compute_metrics(self, run_id: str) -> ExecutionMetrics:
        """Aggregate all metrics for a run."""
        from core.engine.cost_tracker import CostTracker
        
        tracker = CostTracker()
        total_cost = tracker.get_total_cost(run_id)
        
        return ExecutionMetrics(
            run_id=run_id,
            total_cost_usd=total_cost
        )
