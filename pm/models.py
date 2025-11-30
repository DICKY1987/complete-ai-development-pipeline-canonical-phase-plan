"""
Data models for PM section

Defines core data structures:
- PRD: Product Requirements Document
- Epic: Implementation plan with tasks
- Task: Atomic unit of work
- Event: Pipeline lifecycle events

All models use Python dataclasses with type hints.
"""
# DOC_ID: DOC-PM-PM-MODELS-016
# DOC_ID: DOC-PM-PM-MODELS-010

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any


# ============================================================================
# Enums
# ============================================================================

class Status(str, Enum):
    """Status values for PRD, Epic, and Task"""
    DRAFT = "draft"
    PLANNED = "planned"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    ARCHIVED = "archived"


class Priority(str, Enum):
    """Priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Effort(str, Enum):
    """Task effort estimates"""
    SMALL = "small"    # < 2 hours
    MEDIUM = "medium"  # 2-8 hours
    LARGE = "large"    # > 8 hours


class EventType(str, Enum):
    """Pipeline event types"""
    WORKSTREAM_START = "workstream_start"
    STEP_COMPLETE = "step_complete"
    WORKSTREAM_COMPLETE = "workstream_complete"
    WORKSTREAM_BLOCKED = "workstream_blocked"
    WORKSTREAM_FAILED = "workstream_failed"


# ============================================================================
# Core Models
# ============================================================================

@dataclass
class PRD:
    """Product Requirements Document"""
    name: str
    title: str
    author: str
    date: datetime
    status: Status = Status.DRAFT
    priority: Priority = Priority.MEDIUM
    labels: List[str] = field(default_factory=list)
    
    # Content sections
    problem: str = ""
    solution: str = ""
    requirements: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    edge_cases: List[str] = field(default_factory=list)
    
    # Metadata
    file_path: Optional[Path] = None
    
    def validate(self) -> List[str]:
        """
        Validate PRD completeness.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not self.title or not self.title.strip():
            errors.append("Title is required")
        
        if not self.requirements:
            errors.append("At least one requirement is required")
        
        if not self.success_criteria:
            errors.append("At least one success criterion is required")
        
        if self.status not in Status:
            errors.append(f"Invalid status: {self.status}")
        
        if self.priority not in Priority:
            errors.append(f"Invalid priority: {self.priority}")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "title": self.title,
            "author": self.author,
            "date": self.date.isoformat(),
            "status": self.status.value if isinstance(self.status, Status) else self.status,
            "priority": self.priority.value if isinstance(self.priority, Priority) else self.priority,
            "labels": self.labels,
            "problem": self.problem,
            "solution": self.solution,
            "requirements": self.requirements,
            "success_criteria": self.success_criteria,
            "constraints": self.constraints,
            "edge_cases": self.edge_cases,
        }


@dataclass
class Task:
    """Atomic unit of work within an Epic"""
    task_id: str
    title: str
    epic_name: str
    status: Status = Status.PLANNED
    priority: Priority = Priority.MEDIUM
    assignee: Optional[str] = None
    effort: Effort = Effort.MEDIUM
    parallel: bool = True  # Can run in parallel by default
    dependencies: List[str] = field(default_factory=list)  # Other task IDs
    file_scope: List[Path] = field(default_factory=list)
    github_issue: Optional[int] = None
    
    # Content
    description: str = ""
    acceptance_criteria: List[str] = field(default_factory=list)
    technical_notes: str = ""
    files_to_modify: Dict[str, str] = field(default_factory=dict)  # path: description
    
    # Metadata
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    file_path: Optional[Path] = None
    
    def validate(self) -> List[str]:
        """
        Validate task completeness.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not self.title or not self.title.strip():
            errors.append("Title is required")
        
        if not self.file_scope:
            errors.append("File scope is required (at least one file)")
        
        if not self.acceptance_criteria:
            errors.append("At least one acceptance criterion is required")
        
        # Check for circular dependencies (simplified check)
        if self.task_id in self.dependencies:
            errors.append("Task cannot depend on itself")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "epic_name": self.epic_name,
            "status": self.status.value if isinstance(self.status, Status) else self.status,
            "priority": self.priority.value if isinstance(self.priority, Priority) else self.priority,
            "assignee": self.assignee,
            "effort": self.effort.value if isinstance(self.effort, Effort) else self.effort,
            "parallel": self.parallel,
            "dependencies": self.dependencies,
            "file_scope": [str(p) for p in self.file_scope],
            "github_issue": self.github_issue,
            "description": self.description,
            "acceptance_criteria": self.acceptance_criteria,
            "technical_notes": self.technical_notes,
            "files_to_modify": self.files_to_modify,
            "created": self.created.isoformat() if self.created else None,
            "updated": self.updated.isoformat() if self.updated else None,
        }


@dataclass
class Epic:
    """Implementation plan with tasks"""
    name: str
    title: str
    prd_name: str
    created: datetime
    status: Status = Status.PLANNED
    priority: Priority = Priority.MEDIUM
    github_issue: Optional[int] = None
    
    # Content
    technical_approach: str = ""
    dependencies: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    implementation_plan: str = ""
    
    # Tasks (populated separately)
    tasks: List[Task] = field(default_factory=list)
    
    # Metadata
    updated: Optional[datetime] = None
    file_path: Optional[Path] = None
    metadata_path: Optional[Path] = None
    
    def validate(self) -> List[str]:
        """
        Validate epic completeness.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not self.title or not self.title.strip():
            errors.append("Title is required")
        
        if not self.prd_name or not self.prd_name.strip():
            errors.append("PRD reference is required")
        
        if not self.technical_approach or not self.technical_approach.strip():
            errors.append("Technical approach is required")
        
        # Validate task dependency graph (no cycles)
        if self.tasks:
            task_ids = {t.task_id for t in self.tasks}
            for task in self.tasks:
                for dep_id in task.dependencies:
                    if dep_id not in task_ids:
                        errors.append(f"Task {task.task_id} references unknown dependency: {dep_id}")
        
        return errors
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None
    
    def progress_percent(self) -> float:
        """Calculate completion percentage."""
        if not self.tasks:
            return 0.0
        completed = sum(1 for t in self.tasks if t.status == Status.COMPLETED)
        return (completed / len(self.tasks)) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "title": self.title,
            "prd_name": self.prd_name,
            "created": self.created.isoformat(),
            "status": self.status.value if isinstance(self.status, Status) else self.status,
            "priority": self.priority.value if isinstance(self.priority, Priority) else self.priority,
            "github_issue": self.github_issue,
            "technical_approach": self.technical_approach,
            "dependencies": self.dependencies,
            "risks": self.risks,
            "implementation_plan": self.implementation_plan,
            "tasks": [t.to_dict() for t in self.tasks],
            "updated": self.updated.isoformat() if self.updated else None,
        }


@dataclass
class WorkstreamEvent:
    """Pipeline lifecycle event"""
    event_type: EventType
    ws_id: str
    epic_name: Optional[str] = None
    task_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    payload: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "event_type": self.event_type.value if isinstance(self.event_type, EventType) else self.event_type,
            "ws_id": self.ws_id,
            "epic_name": self.epic_name,
            "task_id": self.task_id,
            "timestamp": self.timestamp.isoformat(),
            "payload": self.payload,
        }


# ============================================================================
# Validation Errors
# ============================================================================

@dataclass
class ValidationError:
    """Validation error detail"""
    field: str
    message: str
    severity: str = "error"  # error | warning
    
    def __str__(self) -> str:
        return f"{self.severity.upper()}: {self.field} - {self.message}"


@dataclass
class ConflictError:
    """File-scope conflict between parallel tasks"""
    task1_id: str
    task2_id: str
    conflicting_files: List[Path]
    
    def __str__(self) -> str:
        files = ", ".join(str(f) for f in self.conflicting_files)
        return f"Conflict between {self.task1_id} and {self.task2_id}: {files}"
