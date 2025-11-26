"""Test gate enforcement for parallel execution.

Phase I WS-I7: Quality gates and test enforcement.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


@dataclass
class TestGate:
    """Test gate configuration."""
    gate_id: str
    gate_type: str  # 'static', 'runtime', 'custom'
    tool_id: str
    required: bool = True
    blocking: bool = True  # Block execution if gate fails
    wave_boundary: bool = False  # Enforce at wave boundaries


@dataclass
class GateResult:
    """Result of gate enforcement."""
    gate_id: str
    passed: bool
    workstream_id: str
    error_message: Optional[str] = None
    executed_at: Optional[datetime] = None


class TestGateEnforcer:
    """Enforces quality gates during parallel execution."""
    
    def __init__(self, gates: List[TestGate]):
        """Initialize gate enforcer.
        
        Args:
            gates: List of gates to enforce
        """
        self.gates = gates
    
    def enforce_gates(
        self,
        workstream_id: str,
        run_id: str,
        context: Dict[str, Any]
    ) -> List[GateResult]:
        """Enforce all gates for a workstream.
        
        Args:
            workstream_id: Workstream ID
            run_id: Execution run ID
            context: Execution context
            
        Returns:
            List of GateResult objects
        """
        results = []
        
        for gate in self.gates:
            result = self._execute_gate(gate, workstream_id, run_id, context)
            results.append(result)
            
            # Stop if blocking gate fails
            if gate.blocking and not result.passed:
                break
        
        return results
    
    def _execute_gate(
        self,
        gate: TestGate,
        workstream_id: str,
        run_id: str,
        context: Dict[str, Any]
    ) -> GateResult:
        """Execute single gate.
        
        Args:
            gate: Gate configuration
            workstream_id: Workstream ID
            run_id: Run ID
            context: Execution context
            
        Returns:
            GateResult
        """
        from core.engine import tools
        from core.state import db
        
        executed_at = datetime.now(timezone.utc)
        
        try:
            # Execute gate tool
            tool_result = tools.run_tool(
                gate.tool_id,
                context,
                run_id=run_id,
                ws_id=workstream_id
            )
            
            passed = bool(tool_result.success)
            error_msg = None if passed else str(tool_result.error)
            
            # Record gate result
            db.record_event(
                event_type='test_gate_executed',
                run_id=run_id,
                ws_id=workstream_id,
                payload={
                    'gate_id': gate.gate_id,
                    'gate_type': gate.gate_type,
                    'passed': passed,
                    'blocking': gate.blocking
                }
            )
            
            return GateResult(
                gate_id=gate.gate_id,
                passed=passed,
                workstream_id=workstream_id,
                error_message=error_msg,
                executed_at=executed_at
            )
        
        except Exception as e:
            # Gate execution failed
            db.record_event(
                event_type='test_gate_error',
                run_id=run_id,
                ws_id=workstream_id,
                payload={
                    'gate_id': gate.gate_id,
                    'error': str(e)
                }
            )
            
            return GateResult(
                gate_id=gate.gate_id,
                passed=False,
                workstream_id=workstream_id,
                error_message=str(e),
                executed_at=executed_at
            )
    
    def enforce_wave_gates(
        self,
        wave_workstreams: List[str],
        run_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, List[GateResult]]:
        """Enforce wave-boundary gates across multiple workstreams.
        
        Args:
            wave_workstreams: List of workstream IDs in wave
            run_id: Run ID
            context: Execution context
            
        Returns:
            Dict mapping workstream_id to gate results
        """
        wave_gates = [g for g in self.gates if g.wave_boundary]
        
        results = {}
        for ws_id in wave_workstreams:
            ws_results = []
            for gate in wave_gates:
                result = self._execute_gate(gate, ws_id, run_id, context)
                ws_results.append(result)
            results[ws_id] = ws_results
        
        return results
    
    def get_blocking_failures(self, results: List[GateResult]) -> List[GateResult]:
        """Get list of blocking gate failures.
        
        Args:
            results: List of gate results
            
        Returns:
            List of failed blocking gates
        """
        return [r for r in results if not r.passed]


def create_default_gates() -> List[TestGate]:
    """Create default test gates for parallel execution.
    
    Returns:
        List of default TestGate configurations
    """
    return [
        TestGate(
            gate_id='syntax-check',
            gate_type='static',
            tool_id='python-syntax-check',
            required=True,
            blocking=True,
            wave_boundary=False
        ),
        TestGate(
            gate_id='lint',
            gate_type='static',
            tool_id='ruff',
            required=False,
            blocking=False,
            wave_boundary=False
        ),
        TestGate(
            gate_id='unit-tests',
            gate_type='runtime',
            tool_id='pytest',
            required=True,
            blocking=True,
            wave_boundary=True  # Enforce at wave boundaries
        ),
    ]


class GateEnforcementError(Exception):
    """Raised when blocking gate fails."""
    pass
