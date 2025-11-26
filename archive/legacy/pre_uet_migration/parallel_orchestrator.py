"""
Parallel Orchestrator - Wave-Based Parallel Execution
Executes workstreams in parallel using DAG waves
"""

from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import time


@dataclass
class ExecutionResult:
    """Result of workstream execution."""
    workstream_id: str
    status: str
    duration: float
    output: str = ""
    error: str = ""


class ParallelOrchestrator:
    """Execute workstreams in parallel using DAG-based waves."""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def execute_phase(self, workstreams: List[Dict]) -> Dict:
        """Execute all workstreams in DAG order."""
        from core.engine.dag_builder import DAGBuilder
        
        # Build DAG
        builder = DAGBuilder()
        plan = builder.build_from_workstreams(workstreams)
        
        results = []
        total_duration = 0
        
        # Execute wave by wave
        for wave_num, wave in enumerate(plan['waves'], 1):
            print(f"🌊 Executing wave {wave_num}/{len(plan['waves'])} ({len(wave)} workstreams)")
            wave_results = self.execute_wave(wave, builder.workstreams)
            results.extend(wave_results)
            total_duration += max([r.duration for r in wave_results], default=0)
        
        return {
            'results': results,
            'total_workstreams': len(workstreams),
            'successful': sum(1 for r in results if r.status == 'completed'),
            'failed': sum(1 for r in results if r.status == 'failed'),
            'duration': total_duration,
            'waves_executed': len(plan['waves'])
        }
    
    def execute_wave(self, wave: List[str], workstreams: Dict) -> List[ExecutionResult]:
        """Execute a single wave of workstreams in parallel."""
        futures = {}
        
        for ws_id in wave:
            ws = workstreams[ws_id]
            future = self.executor.submit(self._execute_workstream, ws)
            futures[future] = ws_id
        
        results = []
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
        
        return results
    
    def _execute_workstream(self, workstream: Dict) -> ExecutionResult:
        """Execute a single workstream (stub - actual execution would call tools)."""
        ws_id = workstream.get('workstream_id') or workstream.get('id')
        start_time = time.time()
        
        try:
            # Simulate execution
            time.sleep(0.1)
            
            duration = time.time() - start_time
            return ExecutionResult(
                workstream_id=ws_id,
                status='completed',
                duration=duration,
                output=f"Executed {ws_id}"
            )
        except Exception as e:
            duration = time.time() - start_time
            return ExecutionResult(
                workstream_id=ws_id,
                status='failed',
                duration=duration,
                error=str(e)
            )
    
    def monitor_execution(self) -> Dict:
        """Get current execution progress snapshot."""
        return {
            'max_workers': self.max_workers,
            'active': True
        }
    
    def shutdown(self):
        """Shutdown executor."""
        self.executor.shutdown(wait=True)
