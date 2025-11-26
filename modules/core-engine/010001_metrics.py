"""Metrics aggregation and reporting.

Phase I WS-I9: Enhanced metrics and reporting for parallel execution.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import json


@dataclass
class ExecutionMetrics:
    """Execution metrics for a run."""
    run_id: str
    total_duration_sec: float = 0.0
    total_cost_usd: float = 0.0
    total_tokens: int = 0
    workstreams_completed: int = 0
    workstreams_failed: int = 0
    parallelism_efficiency: float = 0.0
    bottlenecks: List[str] = field(default_factory=list)
    error_frequency: Dict[str, int] = field(default_factory=dict)
    
    # Phase I additions
    wave_count: int = 0
    avg_wave_duration: float = 0.0
    worker_utilization: float = 0.0
    merge_conflicts: int = 0
    test_gate_failures: int = 0
    budget_status: Optional[str] = None


@dataclass
class WorkstreamMetrics:
    """Metrics for individual workstream."""
    workstream_id: str
    duration_sec: float
    cost_usd: float
    tokens: int
    status: str
    worker_id: Optional[str] = None
    wave_number: Optional[int] = None
    retry_count: int = 0


class MetricsAggregator:
    """Metrics and observability."""
    
    def compute_metrics(self, run_id: str) -> ExecutionMetrics:
        """Aggregate all metrics for a run.
        
        Args:
            run_id: Run ID
            
        Returns:
            ExecutionMetrics with complete run statistics
        """
        from modules.core_engine.010001_cost_tracker import CostTracker
        from modules.core_state.010003_db import get_connection, get_events
        
        tracker = CostTracker()
        total_cost = tracker.get_total_cost(run_id)
        
        # Get workstream statistics
        conn = get_connection()
        
        try:
            # Workstream counts
            cursor = conn.execute("""
                SELECT status, COUNT(*) 
                FROM workstreams 
                WHERE run_id = ?
                GROUP BY status
            """, (run_id,))
            
            status_counts = dict(cursor.fetchall())
            completed = status_counts.get('done', 0)
            failed = status_counts.get('failed', 0)
            
            # Token usage
            cursor = conn.execute("""
                SELECT SUM(input_tokens + output_tokens)
                FROM cost_tracking
                WHERE run_id = ?
            """, (run_id,))
            
            total_tokens = cursor.fetchone()[0] or 0
            
            # Merge conflicts
            cursor = conn.execute("""
                SELECT COUNT(*)
                FROM events
                WHERE run_id = ? AND event_type = 'merge_conflict_detected'
            """, (run_id,))
            
            merge_conflicts = cursor.fetchone()[0] or 0
            
            # Test gate failures
            cursor = conn.execute("""
                SELECT COUNT(*)
                FROM events
                WHERE run_id = ? AND event_type = 'test_gate_executed'
                  AND json_extract(payload_json, '$.passed') = 0
            """, (run_id,))
            
            test_gate_failures = cursor.fetchone()[0] or 0
        
        finally:
            conn.close()
        
        # Get execution events
        events = get_events(run_id=run_id, limit=10000)
        
        # Calculate duration
        start_event = next((e for e in reversed(events) if e['event_type'] == 'parallel_execution_start'), None)
        end_event = next((e for e in events if e['event_type'] == 'parallel_execution_end'), None)
        
        duration = 0.0
        if start_event and end_event:
            start_time = datetime.fromisoformat(start_event['timestamp'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end_event['timestamp'].replace('Z', '+00:00'))
            duration = (end_time - start_time).total_seconds()
        
        # Wave statistics
        wave_count = 0
        if end_event and end_event.get('payload'):
            wave_count = end_event['payload'].get('wave_count', 0)
        
        avg_wave_duration = duration / wave_count if wave_count > 0 else 0.0
        
        # Error frequency
        error_frequency = {}
        for event in events:
            if event['event_type'] in ('step_end', 'test_gate_executed'):
                payload = event.get('payload', {})
                if not payload.get('passed') and not payload.get('success'):
                    error_type = event['event_type']
                    error_frequency[error_type] = error_frequency.get(error_type, 0) + 1
        
        # Budget status
        budget_status = None
        for event in reversed(events):
            if event['event_type'] in ('budget_warning', 'budget_exceeded'):
                budget_status = event['event_type']
                break
        
        return ExecutionMetrics(
            run_id=run_id,
            total_duration_sec=duration,
            total_cost_usd=total_cost,
            total_tokens=total_tokens,
            workstreams_completed=completed,
            workstreams_failed=failed,
            wave_count=wave_count,
            avg_wave_duration=avg_wave_duration,
            merge_conflicts=merge_conflicts,
            test_gate_failures=test_gate_failures,
            error_frequency=error_frequency,
            budget_status=budget_status
        )
    
    def compute_workstream_metrics(self, run_id: str) -> List[WorkstreamMetrics]:
        """Compute metrics for each workstream in a run.
        
        Args:
            run_id: Run ID
            
        Returns:
            List of WorkstreamMetrics
        """
        from modules.core_state.010003_db import get_connection
        
        conn = get_connection()
        
        try:
            cursor = conn.execute("""
                SELECT 
                    w.id,
                    w.status,
                    COALESCE(SUM(c.estimated_cost_usd), 0) as cost,
                    COALESCE(SUM(c.input_tokens + c.output_tokens), 0) as tokens
                FROM workstreams w
                LEFT JOIN cost_tracking c ON c.workstream_id = w.id AND c.run_id = w.run_id
                WHERE w.run_id = ?
                GROUP BY w.id
            """, (run_id,))
            
            metrics = []
            for row in cursor.fetchall():
                metrics.append(WorkstreamMetrics(
                    workstream_id=row[0],
                    status=row[1],
                    cost_usd=float(row[2]),
                    tokens=int(row[3]),
                    duration_sec=0.0  # TODO: Calculate from events
                ))
            
            return metrics
        
        finally:
            conn.close()
    
    def generate_report(self, run_id: str, output_file: Optional[str] = None) -> str:
        """Generate execution report.
        
        Args:
            run_id: Run ID
            output_file: Optional output file path
            
        Returns:
            Report as formatted string
        """
        metrics = self.compute_metrics(run_id)
        ws_metrics = self.compute_workstream_metrics(run_id)
        
        report = []
        report.append("=" * 80)
        report.append(f"PARALLEL EXECUTION REPORT: {run_id}")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        report.append("SUMMARY")
        report.append("-" * 40)
        report.append(f"  Total Duration:      {metrics.total_duration_sec:.1f}s")
        report.append(f"  Total Cost:          ${metrics.total_cost_usd:.4f}")
        report.append(f"  Total Tokens:        {metrics.total_tokens:,}")
        report.append(f"  Completed:           {metrics.workstreams_completed}")
        report.append(f"  Failed:              {metrics.workstreams_failed}")
        report.append(f"  Waves:               {metrics.wave_count}")
        report.append(f"  Avg Wave Duration:   {metrics.avg_wave_duration:.1f}s")
        report.append("")
        
        # Quality metrics
        report.append("QUALITY")
        report.append("-" * 40)
        report.append(f"  Merge Conflicts:     {metrics.merge_conflicts}")
        report.append(f"  Test Gate Failures:  {metrics.test_gate_failures}")
        if metrics.budget_status:
            report.append(f"  Budget Status:       {metrics.budget_status}")
        report.append("")
        
        # Top workstreams by cost
        ws_by_cost = sorted(ws_metrics, key=lambda x: x.cost_usd, reverse=True)[:5]
        report.append("TOP 5 WORKSTREAMS BY COST")
        report.append("-" * 40)
        for ws in ws_by_cost:
            report.append(f"  {ws.workstream_id:30s} ${ws.cost_usd:.4f}")
        report.append("")
        
        # Error frequency
        if metrics.error_frequency:
            report.append("ERROR FREQUENCY")
            report.append("-" * 40)
            for error_type, count in sorted(metrics.error_frequency.items(), key=lambda x: x[1], reverse=True):
                report.append(f"  {error_type:30s} {count:4d}")
            report.append("")
        
        report.append("=" * 80)
        
        report_str = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_str)
        
        return report_str
    
    def export_metrics_json(self, run_id: str, output_file: str) -> None:
        """Export metrics to JSON file.
        
        Args:
            run_id: Run ID
            output_file: Output JSON file path
        """
        metrics = self.compute_metrics(run_id)
        ws_metrics = self.compute_workstream_metrics(run_id)
        
        data = {
            'run_id': run_id,
            'metrics': {
                'total_duration_sec': metrics.total_duration_sec,
                'total_cost_usd': metrics.total_cost_usd,
                'total_tokens': metrics.total_tokens,
                'workstreams_completed': metrics.workstreams_completed,
                'workstreams_failed': metrics.workstreams_failed,
                'wave_count': metrics.wave_count,
                'avg_wave_duration': metrics.avg_wave_duration,
                'merge_conflicts': metrics.merge_conflicts,
                'test_gate_failures': metrics.test_gate_failures,
                'budget_status': metrics.budget_status,
                'error_frequency': metrics.error_frequency
            },
            'workstreams': [
                {
                    'id': ws.workstream_id,
                    'status': ws.status,
                    'cost_usd': ws.cost_usd,
                    'tokens': ws.tokens
                }
                for ws in ws_metrics
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
