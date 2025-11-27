"""Pattern state client for accessing pattern execution data.

Provides interfaces for panels to access pattern execution state
and events for visualization.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from enum import Enum


class PatternStatus(Enum):
    """Status of a pattern execution run."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PatternEventType(Enum):
    """Types of pattern execution events."""
    STARTED = "started"
    PHASE_STARTED = "phase_started"
    PHASE_COMPLETED = "phase_completed"
    VALIDATION_PASSED = "validation_passed"
    VALIDATION_FAILED = "validation_failed"
    EXECUTED = "executed"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PatternRun:
    """Information about a pattern execution run."""
    run_id: str
    pattern_id: str
    pattern_name: str
    status: PatternStatus
    start_time: datetime
    end_time: Optional[datetime]
    progress: float  # 0.0 to 1.0
    current_phase: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class PatternEvent:
    """Event in a pattern execution run."""
    event_id: str
    run_id: str
    event_type: PatternEventType
    timestamp: datetime
    phase: Optional[str]
    message: str
    details: Optional[dict] = None


class PatternStateStore(ABC):
    """Abstract interface for pattern state storage."""
    
    @abstractmethod
    def get_recent_runs(self, limit: int = 50) -> List[PatternRun]:
        """Get recent pattern runs."""
        pass
    
    @abstractmethod
    def get_run_events(self, run_id: str) -> List[PatternEvent]:
        """Get all events for a specific run."""
        pass
    
    @abstractmethod
    def get_active_patterns(self) -> List[PatternRun]:
        """Get currently active pattern runs."""
        pass


class InMemoryPatternStateStore(PatternStateStore):
    """In-memory pattern state store with seeded test data."""
    
    def __init__(self):
        now = datetime.now()
        
        # Seed some pattern runs
        self._runs = [
            PatternRun(
                run_id="run-001",
                pattern_id="PAT-GUI-PANEL-001",
                pattern_name="Panel Framework Implementation",
                status=PatternStatus.COMPLETED,
                start_time=now,
                end_time=now,
                progress=1.0,
                current_phase="Testing"
            ),
            PatternRun(
                run_id="run-002",
                pattern_id="PAT-ATOMIC-CREATE-001",
                pattern_name="Atomic File Creation",
                status=PatternStatus.RUNNING,
                start_time=now,
                end_time=None,
                progress=0.6,
                current_phase="Phase B: Creating Files"
            ),
            PatternRun(
                run_id="run-003",
                pattern_id="PAT-ATOMIC-REFINE-001",
                pattern_name="Code Refinement",
                status=PatternStatus.FAILED,
                start_time=now,
                end_time=now,
                progress=0.4,
                current_phase="Validation",
                error_message="Test suite failed: 2 tests"
            ),
        ]
        
        # Seed events for runs
        self._events = {
            "run-001": [
                PatternEvent("evt-001", "run-001", PatternEventType.STARTED, now, None, "Pattern execution started"),
                PatternEvent("evt-002", "run-001", PatternEventType.PHASE_STARTED, now, "Phase A", "Starting Phase A: Setup"),
                PatternEvent("evt-003", "run-001", PatternEventType.PHASE_COMPLETED, now, "Phase A", "Phase A completed successfully"),
                PatternEvent("evt-004", "run-001", PatternEventType.PHASE_STARTED, now, "Phase B", "Starting Phase B: Implementation"),
                PatternEvent("evt-005", "run-001", PatternEventType.PHASE_COMPLETED, now, "Phase B", "Phase B completed successfully"),
                PatternEvent("evt-006", "run-001", PatternEventType.VALIDATION_PASSED, now, "Testing", "All tests passed"),
                PatternEvent("evt-007", "run-001", PatternEventType.COMPLETED, now, None, "Pattern execution completed"),
            ],
            "run-002": [
                PatternEvent("evt-101", "run-002", PatternEventType.STARTED, now, None, "Pattern execution started"),
                PatternEvent("evt-102", "run-002", PatternEventType.PHASE_STARTED, now, "Phase A", "Starting Phase A: Analysis"),
                PatternEvent("evt-103", "run-002", PatternEventType.PHASE_COMPLETED, now, "Phase A", "Phase A completed successfully"),
                PatternEvent("evt-104", "run-002", PatternEventType.PHASE_STARTED, now, "Phase B", "Starting Phase B: Creating Files"),
            ],
            "run-003": [
                PatternEvent("evt-201", "run-003", PatternEventType.STARTED, now, None, "Pattern execution started"),
                PatternEvent("evt-202", "run-003", PatternEventType.PHASE_STARTED, now, "Validation", "Running test suite"),
                PatternEvent("evt-203", "run-003", PatternEventType.VALIDATION_FAILED, now, "Validation", "Test suite failed: 2 tests"),
                PatternEvent("evt-204", "run-003", PatternEventType.FAILED, now, None, "Pattern execution failed"),
            ],
        }
    
    def get_recent_runs(self, limit: int = 50) -> List[PatternRun]:
        return self._runs[:limit]
    
    def get_run_events(self, run_id: str) -> List[PatternEvent]:
        return self._events.get(run_id, [])
    
    def get_active_patterns(self) -> List[PatternRun]:
        return [run for run in self._runs if run.status == PatternStatus.RUNNING]


class PatternClient:
    """Client for accessing pattern execution state from panels."""
    
    def __init__(self, store: PatternStateStore):
        self._store = store
    
    def get_recent_runs(self, limit: int = 50) -> List[PatternRun]:
        """Get recent pattern runs.
        
        Args:
            limit: Maximum number of runs to return
            
        Returns:
            List of PatternRun objects
        """
        return self._store.get_recent_runs(limit)
    
    def get_run_events(self, run_id: str) -> List[PatternEvent]:
        """Get all events for a specific run.
        
        Args:
            run_id: Pattern run identifier
            
        Returns:
            List of PatternEvent objects
        """
        return self._store.get_run_events(run_id)
    
    def get_active_patterns(self) -> List[PatternRun]:
        """Get currently active pattern runs.
        
        Returns:
            List of active PatternRun objects
        """
        return self._store.get_active_patterns()
