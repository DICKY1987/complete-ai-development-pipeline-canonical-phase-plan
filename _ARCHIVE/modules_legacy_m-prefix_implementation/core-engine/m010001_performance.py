"""Performance optimization utilities for parallel execution.

Phase I WS-I10: Performance tuning and optimization.
"""
# DOC_ID: DOC-PAT-CORE-ENGINE-M010001-PERFORMANCE-503

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import time


@dataclass
class PerformanceProfile:
    """Performance profiling results."""
    operation: str
    duration_sec: float
    cpu_usage: Optional[float] = None
    memory_mb: Optional[float] = None
    io_wait: Optional[float] = None


@dataclass
class OptimizationRecommendation:
    """Performance optimization recommendation."""
    category: str  # 'worker_count', 'batch_size', 'context_size', etc.
    current_value: Any
    recommended_value: Any
    expected_improvement: str
    reasoning: str


class PerformanceOptimizer:
    """Performance optimization and tuning."""
    
    def __init__(self):
        """Initialize performance optimizer."""
        self.profiles: List[PerformanceProfile] = []
    
    def profile_operation(
        self,
        operation: str,
        func: callable,
        *args,
        **kwargs
    ) -> tuple[Any, PerformanceProfile]:
        """Profile an operation.
        
        Args:
            operation: Operation name
            func: Function to profile
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Tuple of (result, PerformanceProfile)
        """
        start_time = time.time()
        
        result = func(*args, **kwargs)
        
        duration = time.time() - start_time
        
        profile = PerformanceProfile(
            operation=operation,
            duration_sec=duration
        )
        
        self.profiles.append(profile)
        
        return result, profile
    
    def analyze_execution(
        self,
        run_id: str
    ) -> List[OptimizationRecommendation]:
        """Analyze execution and generate recommendations.
        
        Args:
            run_id: Run ID to analyze
            
        Returns:
            List of optimization recommendations
        """
        from modules.core_engine import MetricsAggregator
        from modules.core_state import get_events
        
        aggregator = MetricsAggregator()
        metrics = aggregator.compute_metrics(run_id)
        events = get_events(run_id=run_id, limit=10000)
        
        recommendations = []
        
        # Analyze worker utilization
        worker_events = [e for e in events if 'worker' in e.get('event_type', '')]
        
        if worker_events:
            # Calculate idle time
            idle_ratio = self._calculate_worker_idle_ratio(events)
            
            if idle_ratio > 0.3:
                recommendations.append(OptimizationRecommendation(
                    category='worker_count',
                    current_value='unknown',
                    recommended_value='increase by 1-2',
                    expected_improvement='10-20% speedup',
                    reasoning=f'Workers idle {idle_ratio*100:.1f}% of time'
                ))
        
        # Analyze wave distribution
        if metrics.wave_count > 0:
            workstreams_per_wave = (metrics.workstreams_completed + metrics.workstreams_failed) / metrics.wave_count
            
            if workstreams_per_wave < 2:
                recommendations.append(OptimizationRecommendation(
                    category='dependencies',
                    current_value=f'{workstreams_per_wave:.1f} workstreams/wave',
                    recommended_value='reduce dependencies',
                    expected_improvement='30-50% speedup',
                    reasoning='Low parallelism due to dependencies'
                ))
        
        # Analyze cost efficiency
        if metrics.total_cost_usd > 0:
            cost_per_workstream = metrics.total_cost_usd / (metrics.workstreams_completed or 1)
            
            if cost_per_workstream > 0.10:
                recommendations.append(OptimizationRecommendation(
                    category='cost_optimization',
                    current_value=f'${cost_per_workstream:.4f}/workstream',
                    recommended_value='reduce context size or use cheaper model',
                    expected_improvement='30-50% cost reduction',
                    reasoning='High cost per workstream'
                ))
        
        return recommendations
    
    def _calculate_worker_idle_ratio(self, events: List[Dict[str, Any]]) -> float:
        """Calculate ratio of time workers were idle.
        
        Args:
            events: List of events
            
        Returns:
            Idle ratio (0.0 to 1.0)
        """
        # Simplified calculation - in production would track actual idle time
        busy_events = len([e for e in events if 'BUSY' in str(e.get('payload', {}))])
        idle_events = len([e for e in events if 'IDLE' in str(e.get('payload', {}))])
        
        total = busy_events + idle_events
        if total == 0:
            return 0.0
        
        return idle_events / total
    
    def optimize_worker_count(
        self,
        workstream_count: int,
        avg_duration_sec: float,
        available_resources: int = 8
    ) -> int:
        """Calculate optimal worker count.
        
        Args:
            workstream_count: Number of workstreams
            avg_duration_sec: Average workstream duration
            available_resources: Available CPU cores/workers
            
        Returns:
            Recommended worker count
        """
        # Simple heuristic: use sqrt(N) workers for N workstreams
        # but cap at available resources
        import math
        
        optimal = min(
            int(math.sqrt(workstream_count)) + 1,
            available_resources,
            workstream_count  # Never more workers than workstreams
        )
        
        return max(2, optimal)  # Minimum 2 workers
    
    def generate_performance_report(
        self,
        run_id: str
    ) -> str:
        """Generate performance optimization report.
        
        Args:
            run_id: Run ID
            
        Returns:
            Report string
        """
        recommendations = self.analyze_execution(run_id)
        
        report = []
        report.append("=" * 80)
        report.append(f"PERFORMANCE OPTIMIZATION REPORT: {run_id}")
        report.append("=" * 80)
        report.append("")
        
        if not recommendations:
            report.append("✓ No optimization recommendations - execution is well-tuned!")
        else:
            report.append(f"Found {len(recommendations)} optimization opportunities:")
            report.append("")
            
            for i, rec in enumerate(recommendations, 1):
                report.append(f"{i}. {rec.category.upper()}")
                report.append(f"   Current:     {rec.current_value}")
                report.append(f"   Recommended: {rec.recommended_value}")
                report.append(f"   Impact:      {rec.expected_improvement}")
                report.append(f"   Reasoning:   {rec.reasoning}")
                report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)


class WorkloadBalancer:
    """Balance workload across workers."""
    
    def balance_workload(
        self,
        workstreams: List[Any],
        worker_count: int
    ) -> List[List[Any]]:
        """Balance workstreams across workers.
        
        Args:
            workstreams: List of workstreams
            worker_count: Number of workers
            
        Returns:
            List of workstream batches per worker
        """
        # Simple round-robin distribution
        batches = [[] for _ in range(worker_count)]
        
        for i, ws in enumerate(workstreams):
            batches[i % worker_count].append(ws)
        
        return batches
    
    def optimize_batch_size(
        self,
        total_items: int,
        avg_processing_time_sec: float,
        target_duration_sec: float = 300.0
    ) -> int:
        """Calculate optimal batch size.
        
        Args:
            total_items: Total number of items
            avg_processing_time_sec: Average processing time per item
            target_duration_sec: Target batch duration
            
        Returns:
            Optimal batch size
        """
        if avg_processing_time_sec == 0:
            return 10  # Default
        
        batch_size = int(target_duration_sec / avg_processing_time_sec)
        
        return max(1, min(batch_size, total_items))
