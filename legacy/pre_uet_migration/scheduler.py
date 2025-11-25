"""DAG-based task scheduler for parallel execution."""

from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from core.state.bundles import WorkstreamBundle
from core.engine.worker import WorkerPool, Worker


@dataclass
class SchedulingWave:
    """One wave of parallel execution."""
    workstream_ids: Set[str] = field(default_factory=set)
    estimated_duration: float = 0.0


@dataclass
class ExecutionPlan:
    """Multi-wave execution plan."""
    waves: List[SchedulingWave] = field(default_factory=list)
    critical_path: List[str] = field(default_factory=list)
    total_duration_seq: float = 0.0
    total_duration_par: float = 0.0


def build_execution_plan(
    bundles: List[WorkstreamBundle],
    max_workers: int = 4
) -> ExecutionPlan:
    """Generate multi-wave execution plan using parallelism detector."""
    from core.planning.parallelism_detector import detect_parallel_opportunities
    
    profile = detect_parallel_opportunities(bundles, max_workers)
    
    plan = ExecutionPlan()
    for wave_set in profile.waves:
        wave = SchedulingWave(workstream_ids=wave_set)
        plan.waves.append(wave)
    
    plan.total_duration_seq = len(bundles)
    plan.total_duration_par = len(profile.waves)
    
    return plan


class TaskScheduler:
    """Assigns tasks to workers from execution plan."""
    
    def __init__(self, worker_pool: WorkerPool):
        self.worker_pool = worker_pool
        self.ready_queue: List[str] = []
        self.running: Dict[str, str] = {}  # workstream_id -> worker_id
    
    def get_next_tasks(self, plan: ExecutionPlan, completed: Set[str]) -> List[str]:
        """Get workstream_ids ready for execution."""
        ready = []
        
        for wave in plan.waves:
            for ws_id in wave.workstream_ids:
                if ws_id not in completed and ws_id not in self.running:
                    ready.append(ws_id)
            
            if ready:
                break  # Process one wave at a time
        
        return ready
    
    def assign_task(self, workstream_id: str, adapter_type: str = "aider") -> Optional[str]:
        """Assign workstream to idle worker, return worker_id."""
        worker = self.worker_pool.get_idle_worker(adapter_type)
        
        if not worker:
            return None
        
        self.worker_pool.assign_task(worker.worker_id, workstream_id)
        self.running[workstream_id] = worker.worker_id
        
        return worker.worker_id
