"""Pattern event emission and aggregation.

Implements the Pattern Event Specification for tracking pattern execution
lifecycle events and building PatternRun objects.

See: docs/PATTERN_EVENT_SPEC.md
"""
# DOC_ID: DOC-PAT-PATTERN-EVENT-SYSTEM-PATTERN-EVENTS-804

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field

try:
    from ulid import new as new_ulid
    def generate_ulid():
        return str(new_ulid())
except ImportError:
    # Fallback to basic ULID-like generation
    import time
    import random
    def generate_ulid():
        timestamp = int(time.time() * 1000)
        random_part = ''.join(random.choices('0123456789ABCDEFGHJKMNPQRSTVWXYZ', k=16))
        return f"{timestamp:013X}{random_part}"


@dataclass
class PatternEvent:
    """Pattern lifecycle event."""
    
    event_id: str
    event_type: str
    timestamp: str
    job_id: str
    pattern_run_id: str
    pattern_id: str
    status: str
    details: Dict[str, Any]
    step_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        event_type: str,
        job_id: str,
        pattern_run_id: str,
        pattern_id: str,
        status: str,
        details: Dict[str, Any],
        step_id: Optional[str] = None,
    ) -> PatternEvent:
        """Create new pattern event with auto-generated ID and timestamp."""
        return cls(
            event_id=f"EVT-{generate_ulid()}",
            event_type=event_type,
            timestamp=datetime.now(timezone.utc).isoformat(),
            job_id=job_id,
            pattern_run_id=pattern_run_id,
            pattern_id=pattern_id,
            status=status,
            details=details,
            step_id=step_id,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class PatternRun:
    """Complete pattern execution record."""
    
    pattern_run_id: str
    pattern_id: str
    job_id: str
    operation_kind: str
    status: str
    started_at: str
    pattern_version: Optional[str] = None
    step_id: Optional[str] = None
    finished_at: Optional[str] = None
    duration_seconds: Optional[float] = None
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    events: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    tool_metadata: Dict[str, str] = field(default_factory=dict)
    error: Optional[Dict[str, Any]] = None
    
    @classmethod
    def create(
        cls,
        pattern_id: str,
        job_id: str,
        operation_kind: str,
        step_id: Optional[str] = None,
        pattern_version: Optional[str] = None,
    ) -> PatternRun:
        """Create new pattern run with auto-generated ID."""
        return cls(
            pattern_run_id=f"PRUN-{generate_ulid()}",
            pattern_id=pattern_id,
            job_id=job_id,
            operation_kind=operation_kind,
            status="pending",
            started_at=datetime.now(timezone.utc).isoformat(),
            step_id=step_id,
            pattern_version=pattern_version,
        )
    
    def mark_started(self):
        """Mark run as started."""
        self.status = "in_progress"
        self.started_at = datetime.now(timezone.utc).isoformat()
    
    def mark_completed(self, outputs: Dict[str, Any], artifacts: List[str] = None):
        """Mark run as completed successfully."""
        self.status = "success"
        self.finished_at = datetime.now(timezone.utc).isoformat()
        self.outputs = outputs
        if artifacts:
            self.artifacts = artifacts
        self._calculate_duration()
    
    def mark_failed(self, error: Dict[str, Any]):
        """Mark run as failed."""
        self.status = "failed"
        self.finished_at = datetime.now(timezone.utc).isoformat()
        self.error = error
        self._calculate_duration()
    
    def add_event(self, event_id: str):
        """Add event ID to run's event list."""
        self.events.append(event_id)
    
    def _calculate_duration(self):
        """Calculate duration from started_at to finished_at."""
        if self.started_at and self.finished_at:
            start = datetime.fromisoformat(self.started_at.replace('Z', '+00:00'))
            end = datetime.fromisoformat(self.finished_at.replace('Z', '+00:00'))
            self.duration_seconds = (end - start).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


class PatternEventEmitter:
    """Emits pattern events to JSONL storage."""
    
    def __init__(self, events_dir: Path = None):
        """Initialize emitter.
        
        Args:
            events_dir: Directory for event storage (default: state/events/)
        """
        if events_dir is None:
            events_dir = Path("state/events")
        
        self.events_dir = Path(events_dir)
        self.events_dir.mkdir(parents=True, exist_ok=True)
        
        self.global_log = self.events_dir / "pattern_events.jsonl"
    
    def emit(self, event: PatternEvent, job_scoped: bool = False):
        """Emit pattern event to JSONL storage.
        
        Args:
            event: PatternEvent to emit
            job_scoped: If True, also write to job-specific log
        """
        # Write to global log
        with self.global_log.open("a") as f:
            f.write(event.to_json() + "\n")
        
        # Write to job-scoped log if requested
        if job_scoped:
            job_log_dir = self.events_dir / "jobs" / event.job_id
            job_log_dir.mkdir(parents=True, exist_ok=True)
            job_log = job_log_dir / "pattern_events.jsonl"
            
            with job_log.open("a") as f:
                f.write(event.to_json() + "\n")
    
    def get_events(
        self,
        job_id: Optional[str] = None,
        pattern_run_id: Optional[str] = None,
    ) -> List[PatternEvent]:
        """Retrieve pattern events from storage.
        
        Args:
            job_id: Filter by job ID
            pattern_run_id: Filter by pattern run ID
        
        Returns:
            List of PatternEvent objects
        """
        events = []
        
        # Determine which log to read
        if job_id:
            log_file = self.events_dir / "jobs" / job_id / "pattern_events.jsonl"
        else:
            log_file = self.global_log
        
        if not log_file.exists():
            return events
        
        # Read and filter events
        with log_file.open("r") as f:
            for line in f:
                if not line.strip():
                    continue
                
                data = json.loads(line)
                
                # Apply filters
                if pattern_run_id and data.get("pattern_run_id") != pattern_run_id:
                    continue
                
                events.append(PatternEvent(**data))
        
        return events


class PatternRunAggregator:
    """Aggregates pattern events into PatternRun objects."""
    
    def __init__(self, emitter: PatternEventEmitter):
        """Initialize aggregator.
        
        Args:
            emitter: PatternEventEmitter instance
        """
        self.emitter = emitter
        self._runs: Dict[str, PatternRun] = {}
    
    def handle_event(self, event: PatternEvent) -> PatternRun:
        """Process event and update corresponding PatternRun.
        
        Args:
            event: PatternEvent to process
        
        Returns:
            Updated PatternRun object
        """
        run_id = event.pattern_run_id
        
        # Get or create run
        if run_id not in self._runs:
            # Initialize from first event
            self._runs[run_id] = PatternRun(
                pattern_run_id=run_id,
                pattern_id=event.pattern_id,
                job_id=event.job_id,
                operation_kind=event.details.get("operation_kind", "unknown"),
                status="pending",
                started_at=event.timestamp,
                step_id=event.step_id,
            )
        
        run = self._runs[run_id]
        run.add_event(event.event_id)
        
        # Update run based on event type
        if event.event_type == "pattern.selection.resolved":
            run.inputs = event.details.get("inputs_preview", {})
        
        elif event.event_type == "pattern.template.expanded":
            run.artifacts.extend(event.details.get("generated_artifacts", []))
        
        elif event.event_type == "pattern.execution.started":
            run.mark_started()
            run.tool_metadata = {
                "command": event.details.get("command", ""),
                "executor": event.details.get("executor", ""),
            }
        
        elif event.event_type == "pattern.execution.completed":
            outputs = {
                "exit_code": event.details.get("exit_code"),
                "duration_seconds": event.details.get("duration_seconds"),
                **event.details.get("result_summary", {})
            }
            artifacts = event.details.get("artifacts", [])
            run.mark_completed(outputs, artifacts)
        
        elif event.event_type == "pattern.execution.failed":
            error = {
                "type": event.details.get("error_type"),
                "message": event.details.get("error_message"),
                "exit_code": event.details.get("exit_code"),
            }
            run.mark_failed(error)
        
        return run
    
    def get_run(self, pattern_run_id: str) -> Optional[PatternRun]:
        """Get pattern run by ID.
        
        Args:
            pattern_run_id: Pattern run identifier
        
        Returns:
            PatternRun object or None
        """
        return self._runs.get(pattern_run_id)
    
    def rebuild_from_events(self, job_id: str) -> List[PatternRun]:
        """Rebuild all pattern runs for a job from events.
        
        Args:
            job_id: Job identifier
        
        Returns:
            List of PatternRun objects
        """
        events = self.emitter.get_events(job_id=job_id)
        
        for event in events:
            self.handle_event(event)
        
        # Return runs for this job
        return [
            run for run in self._runs.values()
            if run.job_id == job_id
        ]


# Convenience function for single-module usage
def emit_pattern_event(
    event_type: str,
    job_id: str,
    pattern_run_id: str,
    pattern_id: str,
    status: str,
    details: Dict[str, Any],
    step_id: Optional[str] = None,
    emitter: Optional[PatternEventEmitter] = None,
) -> PatternEvent:
    """Emit a pattern event (convenience function).
    
    Args:
        event_type: Event type (e.g., 'pattern.execution.started')
        job_id: Job identifier
        pattern_run_id: Pattern run identifier
        pattern_id: Pattern identifier
        status: Execution status
        details: Event-specific metadata
        step_id: Optional step identifier
        emitter: Optional emitter instance (creates default if None)
    
    Returns:
        Created PatternEvent
    """
    if emitter is None:
        emitter = PatternEventEmitter()
    
    event = PatternEvent.create(
        event_type=event_type,
        job_id=job_id,
        pattern_run_id=pattern_run_id,
        pattern_id=pattern_id,
        status=status,
        details=details,
        step_id=step_id,
    )
    
    emitter.emit(event, job_scoped=True)
    return event
