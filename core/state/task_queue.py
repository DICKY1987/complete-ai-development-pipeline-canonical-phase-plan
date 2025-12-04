"""
Task Queue Management for Pipeline Plus
File-based task lifecycle management with concurrent access safety
"""
# DOC_ID: DOC-CORE-STATE-TASK-QUEUE-174
import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any
from filelock import FileLock
import ulid


@dataclass
class TaskPayload:
    """Payload data for a task"""
    repo_path: str
    files: List[str] = field(default_factory=list)
    description: str = ""
    prompt_file: Optional[str] = None
    patch_file: Optional[str] = None


@dataclass
class TaskConstraints:
    """Constraints on task execution"""
    allow_delegation: bool = True
    must_stay_local: bool = False
    allowed_tools: List[str] = field(default_factory=list)


@dataclass
class TaskTimeouts:
    """Timeout configuration for task execution"""
    wall_clock_sec: int = 600
    idle_output_sec: int = 120


@dataclass
class RoutingState:
    """Current routing state for task"""
    current_target: Optional[str] = None
    route_history: List[Dict[str, Any]] = field(default_factory=list)
    attempts: int = 0


@dataclass
class Task:
    """
    Task representation for the queue system
    """
    task_id: str
    source_app: str
    mode: str
    capabilities: List[str]
    payload: TaskPayload
    constraints: TaskConstraints = field(default_factory=TaskConstraints)
    timeouts: TaskTimeouts = field(default_factory=TaskTimeouts)
    routing_state: RoutingState = field(default_factory=RoutingState)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))

    @staticmethod
    def generate_id() -> str:
        """Generate a ULID for task ID"""
        return str(ulid.new())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create Task from dictionary"""
        # Convert nested dicts back to dataclasses
        if 'payload' in data and isinstance(data['payload'], dict):
            data['payload'] = TaskPayload(**data['payload'])
        if 'constraints' in data and isinstance(data['constraints'], dict):
            data['constraints'] = TaskConstraints(**data['constraints'])
        if 'timeouts' in data and isinstance(data['timeouts'], dict):
            data['timeouts'] = TaskTimeouts(**data['timeouts'])
        if 'routing_state' in data and isinstance(data['routing_state'], dict):
            data['routing_state'] = RoutingState(**data['routing_state'])
        return cls(**data)


@dataclass
class TaskStatus:
    """Status information for a task"""
    task_id: str
    state: str  # "inbox", "running", "done", "failed"
    created_at: str
    updated_at: str
    error: Optional[str] = None


@dataclass
class TaskResult:
    """Result of task execution"""
    task_id: str
    success: bool
    output: str = ""
    error: Optional[str] = None
    artifacts: Dict[str, Any] = field(default_factory=dict)


class TaskQueue:
    """
    File-based task queue manager with concurrent access safety
    """

    def __init__(self, base_path: str = ".tasks"):
        self.base_path = Path(base_path)
        self.inbox = self.base_path / "inbox"
        self.running = self.base_path / "running"
        self.done = self.base_path / "done"
        self.failed = self.base_path / "failed"

        # Ensure directories exist
        for dir_path in [self.inbox, self.running, self.done, self.failed]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def _get_task_file(self, task_id: str, state: str) -> Path:
        """Get path to task file in given state directory"""
        state_dir = getattr(self, state)
        return state_dir / f"{task_id}.json"

    def _get_lock_file(self, task_file: Path) -> Path:
        """Get lock file path for a task file"""
        return task_file.with_suffix('.lock')

    def enqueue(self, task: Task) -> str:
        """
        Add task to inbox queue
        Returns: task_id
        """
        task_file = self._get_task_file(task.task_id, "inbox")
        lock_file = self._get_lock_file(task_file)

        with FileLock(str(lock_file), timeout=10):
            with open(task_file, 'w', encoding='utf-8') as f:
                json.dump(task.to_dict(), f, indent=2)

        return task.task_id

    def dequeue(self) -> Optional[Task]:
        """
        Get next task from inbox (FIFO)
        Returns: Task or None if queue is empty
        """
        tasks = sorted(self.inbox.glob("*.json"))
        if not tasks:
            return None

        task_file = tasks[0]
        lock_file = self._get_lock_file(task_file)

        try:
            with FileLock(str(lock_file), timeout=10):
                with open(task_file, 'r', encoding='utf-8') as f:
                    task_data = json.load(f)
                task = Task.from_dict(task_data)
                return task
        except Exception:
            return None

    def peek(self, limit: int = 10) -> List[Task]:
        """
        View tasks in inbox without removing them
        Returns: List of up to 'limit' tasks
        """
        tasks = []
        for task_file in sorted(self.inbox.glob("*.json"))[:limit]:
            try:
                with open(task_file, 'r', encoding='utf-8') as f:
                    task_data = json.load(f)
                tasks.append(Task.from_dict(task_data))
            except Exception:
                continue
        return tasks

    def move_to_running(self, task_id: str) -> bool:
        """
        Move task from inbox to running
        Returns: True if successful
        """
        src_file = self._get_task_file(task_id, "inbox")
        dst_file = self._get_task_file(task_id, "running")
        lock_file = self._get_lock_file(src_file)

        try:
            with FileLock(str(lock_file), timeout=10):
                if src_file.exists():
                    src_file.rename(dst_file)
                    return True
        except Exception:
            pass
        finally:
            # Clean up lock file after releasing lock
            if lock_file.exists():
                try:
                    lock_file.unlink()
                except:
                    pass
        return False

    def complete(self, task_id: str, result: TaskResult) -> bool:
        """
        Move task from running to done with result
        Returns: True if successful
        """
        src_file = self._get_task_file(task_id, "running")
        dst_file = self._get_task_file(task_id, "done")
        lock_file = self._get_lock_file(src_file)

        success = False
        try:
            with FileLock(str(lock_file), timeout=10):
                if src_file.exists():
                    # Read original task
                    with open(src_file, 'r', encoding='utf-8') as f:
                        task_data = json.load(f)

                    # Add result data
                    task_data['result'] = asdict(result)
                    task_data['completed_at'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

                    # Write to done directory
                    with open(dst_file, 'w', encoding='utf-8') as f:
                        json.dump(task_data, f, indent=2)

                    # Remove from running
                    src_file.unlink()
                    success = True
        except Exception:
            pass
        finally:
            # Clean up lock file after releasing lock
            if lock_file.exists():
                try:
                    lock_file.unlink()
                except:
                    pass
        return success

    def fail(self, task_id: str, error: str) -> bool:
        """
        Move task from running to failed with error message
        Returns: True if successful
        """
        src_file = self._get_task_file(task_id, "running")
        dst_file = self._get_task_file(task_id, "failed")
        lock_file = self._get_lock_file(src_file)

        success = False
        try:
            with FileLock(str(lock_file), timeout=10):
                if src_file.exists():
                    # Read original task
                    with open(src_file, 'r', encoding='utf-8') as f:
                        task_data = json.load(f)

                    # Add error data
                    task_data['error'] = error
                    task_data['failed_at'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

                    # Write to failed directory
                    with open(dst_file, 'w', encoding='utf-8') as f:
                        json.dump(task_data, f, indent=2)

                    # Remove from running
                    src_file.unlink()
                    success = True
        except Exception:
            pass
        finally:
            # Clean up lock file after releasing lock
            if lock_file.exists():
                try:
                    lock_file.unlink()
                except:
                    pass
        return success

    def get_status(self, task_id: str) -> Optional[TaskStatus]:
        """
        Get current status of a task
        Returns: TaskStatus or None if not found
        """
        for state in ["inbox", "running", "done", "failed"]:
            task_file = self._get_task_file(task_id, state)
            if task_file.exists():
                try:
                    with open(task_file, 'r', encoding='utf-8') as f:
                        task_data = json.load(f)

                    return TaskStatus(
                        task_id=task_id,
                        state=state,
                        created_at=task_data.get('created_at', ''),
                        updated_at=task_data.get('completed_at') or task_data.get('failed_at') or task_data.get('created_at', ''),
                        error=task_data.get('error')
                    )
                except Exception:
                    continue
        return None
