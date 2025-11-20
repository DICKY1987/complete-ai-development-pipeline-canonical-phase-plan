#!/usr/bin/env python3
"""
Orchestrator Core - PH-3B

Manages phase execution lifecycle with state machine.
Coordinates validation, prompt generation, and execution tracking.
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import dependencies
sys.path.insert(0, str(Path(__file__).parent.parent))
from validation_gateway import ValidationGateway
from prompt_renderer import PromptRenderer
from orchestrator.state_machine import StateMachine, PhaseState, StateTransitionError


class OrchestratorCore:
    """Core orchestrator for phase execution management."""
    
    def __init__(self, ledger_dir: str = ".ledger"):
        self.ledger_dir = Path(ledger_dir)
        self.ledger_dir.mkdir(parents=True, exist_ok=True)
        
        self.validator = ValidationGateway()
        self.prompt_renderer = PromptRenderer()
        self.state_machines: Dict[str, StateMachine] = {}
    
    def queue_phase(
        self,
        phase_spec_file: str,
        force: bool = False
    ) -> bool:
        """
        Queue a phase for execution.
        
        Args:
            phase_spec_file: Path to phase specification file
            force: Skip validation if True
        
        Returns:
            True if phase was queued successfully
        """
        try:
            # Load phase spec
            with open(phase_spec_file, 'r', encoding='utf-8') as f:
                spec = json.load(f)
            
            phase_id = spec.get("phase_id", "UNKNOWN")
            
            # Validate phase unless forced
            if not force:
                validation_result = self.validator.validate_file(phase_spec_file)
                
                if not validation_result.passed:
                    print(f"✗ Phase {phase_id} failed validation:")
                    for error in validation_result.errors[:5]:
                        print(f"  - {error}")
                    return False
            
            # Create state machine if needed
            if phase_id not in self.state_machines:
                self.state_machines[phase_id] = StateMachine()
            
            sm = self.state_machines[phase_id]
            
            # Transition to QUEUED
            try:
                sm.transition(PhaseState.QUEUED, trigger="queued for execution")
            except StateTransitionError as e:
                print(f"✗ Cannot queue {phase_id}: {e}")
                return False
            
            # Create ledger entry
            self._update_ledger(phase_id, spec, sm)
            
            print(f"✓ Phase {phase_id} queued successfully")
            return True
        
        except FileNotFoundError:
            print(f"✗ Phase spec file not found: {phase_spec_file}")
            return False
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON in phase spec: {e.msg}")
            return False
        except Exception as e:
            print(f"✗ Error queueing phase: {e}")
            return False
    
    def start_phase(self, phase_id: str) -> bool:
        """
        Start execution of a queued phase.
        
        Args:
            phase_id: Phase identifier
        
        Returns:
            True if phase started successfully
        """
        if phase_id not in self.state_machines:
            print(f"✗ Phase {phase_id} not found")
            return False
        
        sm = self.state_machines[phase_id]
        
        try:
            sm.transition(PhaseState.RUNNING, trigger="execution started")
            
            # Update ledger
            ledger_file = self.ledger_dir / f"{phase_id}.json"
            if ledger_file.exists():
                with open(ledger_file, 'r') as f:
                    ledger = json.load(f)
                
                ledger["execution_status"] = "RUNNING"
                ledger["started_timestamp"] = datetime.utcnow().isoformat() + "Z"
                ledger["state_transitions"] = sm.get_history()
                
                with open(ledger_file, 'w') as f:
                    json.dump(ledger, f, indent=2)
            
            print(f"✓ Phase {phase_id} started")
            return True
        
        except StateTransitionError as e:
            print(f"✗ Cannot start {phase_id}: {e}")
            return False
    
    def complete_phase(self, phase_id: str) -> bool:
        """
        Mark a phase as complete.
        
        Args:
            phase_id: Phase identifier
        
        Returns:
            True if phase completed successfully
        """
        if phase_id not in self.state_machines:
            print(f"✗ Phase {phase_id} not found")
            return False
        
        sm = self.state_machines[phase_id]
        
        try:
            sm.transition(PhaseState.COMPLETE, trigger="execution completed")
            
            # Update ledger
            ledger_file = self.ledger_dir / f"{phase_id}.json"
            if ledger_file.exists():
                with open(ledger_file, 'r') as f:
                    ledger = json.load(f)
                
                ledger["execution_status"] = "COMPLETE"
                ledger["completed_timestamp"] = datetime.utcnow().isoformat() + "Z"
                ledger["state_transitions"] = sm.get_history()
                
                with open(ledger_file, 'w') as f:
                    json.dump(ledger, f, indent=2)
            
            print(f"✓ Phase {phase_id} completed")
            return True
        
        except StateTransitionError as e:
            print(f"✗ Cannot complete {phase_id}: {e}")
            return False
    
    def fail_phase(self, phase_id: str, reason: str = "") -> bool:
        """
        Mark a phase as failed.
        
        Args:
            phase_id: Phase identifier
            reason: Failure reason
        
        Returns:
            True if phase was marked as failed
        """
        if phase_id not in self.state_machines:
            print(f"✗ Phase {phase_id} not found")
            return False
        
        sm = self.state_machines[phase_id]
        
        try:
            sm.transition(PhaseState.FAILED, trigger=f"execution failed: {reason}")
            
            # Update ledger
            ledger_file = self.ledger_dir / f"{phase_id}.json"
            if ledger_file.exists():
                with open(ledger_file, 'r') as f:
                    ledger = json.load(f)
                
                ledger["execution_status"] = "FAILED"
                ledger["failed_timestamp"] = datetime.utcnow().isoformat() + "Z"
                ledger["failure_reason"] = reason
                ledger["state_transitions"] = sm.get_history()
                
                with open(ledger_file, 'w') as f:
                    json.dump(ledger, f, indent=2)
            
            print(f"✗ Phase {phase_id} failed: {reason}")
            return True
        
        except StateTransitionError as e:
            print(f"✗ Cannot fail {phase_id}: {e}")
            return False
    
    def get_status(self, phase_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current status of a phase.
        
        Args:
            phase_id: Phase identifier
        
        Returns:
            Status dictionary or None if not found
        """
        if phase_id not in self.state_machines:
            return None
        
        sm = self.state_machines[phase_id]
        
        # Load ledger if exists
        ledger_file = self.ledger_dir / f"{phase_id}.json"
        ledger_data = {}
        
        if ledger_file.exists():
            with open(ledger_file, 'r') as f:
                ledger_data = json.load(f)
        
        return {
            "phase_id": phase_id,
            "current_state": sm.get_state().value,
            "is_terminal": sm.is_terminal(),
            "transition_count": len(sm.get_history()),
            "ledger_exists": ledger_file.exists(),
            **ledger_data
        }
    
    def list_phases(self) -> List[Dict[str, Any]]:
        """
        List all known phases.
        
        Returns:
            List of phase status dictionaries
        """
        phases = []
        
        # Get phases from state machines
        for phase_id in self.state_machines:
            status = self.get_status(phase_id)
            if status:
                phases.append(status)
        
        # Also check ledger for phases not in memory
        for ledger_file in self.ledger_dir.glob("*.json"):
            phase_id = ledger_file.stem
            if phase_id not in self.state_machines:
                with open(ledger_file, 'r') as f:
                    ledger_data = json.load(f)
                
                phases.append({
                    "phase_id": phase_id,
                    "current_state": ledger_data.get("execution_status", "unknown").lower(),
                    "ledger_exists": True,
                    **ledger_data
                })
        
        return sorted(phases, key=lambda x: x["phase_id"])
    
    def _update_ledger(
        self,
        phase_id: str,
        spec: Dict[str, Any],
        state_machine: StateMachine
    ) -> None:
        """Update ledger file for a phase."""
        ledger_file = self.ledger_dir / f"{phase_id}.json"
        
        ledger_entry = {
            "phase_id": phase_id,
            "phase_name": spec.get("phase_name", ""),
            "execution_status": state_machine.get_state().value.upper(),
            "queued_timestamp": datetime.utcnow().isoformat() + "Z",
            "state_transitions": state_machine.get_history(),
            "workstream_id": spec.get("workstream_id", ""),
            "estimated_effort_hours": spec.get("estimated_effort_hours", 0),
            "dependencies": spec.get("dependencies", [])
        }
        
        with open(ledger_file, 'w', encoding='utf-8') as f:
            json.dump(ledger_entry, f, indent=2)


def main():
    """CLI entry point for orchestrator."""
    parser = argparse.ArgumentParser(
        description="Phase execution orchestrator"
    )
    parser.add_argument(
        "--queue",
        type=str,
        help="Queue a phase for execution"
    )
    parser.add_argument(
        "--start",
        type=str,
        help="Start execution of a queued phase"
    )
    parser.add_argument(
        "--complete",
        type=str,
        help="Mark a phase as complete"
    )
    parser.add_argument(
        "--fail",
        type=str,
        help="Mark a phase as failed"
    )
    parser.add_argument(
        "--status",
        type=str,
        help="Get status of a phase"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all phases"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip validation when queueing"
    )
    
    args = parser.parse_args()
    
    try:
        orchestrator = OrchestratorCore()
        
        if args.queue:
            success = orchestrator.queue_phase(args.queue, args.force)
            return 0 if success else 1
        
        elif args.start:
            success = orchestrator.start_phase(args.start)
            return 0 if success else 1
        
        elif args.complete:
            success = orchestrator.complete_phase(args.complete)
            return 0 if success else 1
        
        elif args.fail:
            success = orchestrator.fail_phase(args.fail, reason="manual failure")
            return 0 if success else 1
        
        elif args.status:
            status = orchestrator.get_status(args.status)
            if status:
                print(json.dumps(status, indent=2))
                return 0
            else:
                print(f"Phase {args.status} not found")
                return 1
        
        elif args.list:
            phases = orchestrator.list_phases()
            for phase in phases:
                state = phase.get("current_state", "unknown")
                print(f"{phase['phase_id']}: {state}")
            return 0
        
        else:
            parser.print_help()
            return 1
    
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
