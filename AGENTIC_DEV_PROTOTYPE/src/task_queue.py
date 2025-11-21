#!/usr/bin/env python3
"""
Task Queue Manager - PH-4B

File-based task queue for managing phase execution with priority and state tracking.
Tasks move through states: queued → running → complete/failed
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class TaskState(Enum):
    """Task execution states."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


class TaskQueue:
    """File-based task queue manager."""
    
    def __init__(self, queue_dir: str = ".tasks"):
        self.queue_dir = Path(queue_dir)
        self._init_directories()
    
    def _init_directories(self):
        """Initialize queue directory structure."""
        for state in TaskState:
            state_dir = self.queue_dir / state.value
            state_dir.mkdir(parents=True, exist_ok=True)
    
    def enqueue(
        self,
        phase_id: str,
        priority: str = "medium",
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Add task to queue.
        
        Args:
            phase_id: Phase identifier
            priority: Task priority (low/medium/high/critical)
            metadata: Optional task metadata
        
        Returns:
            Task ID
        """
        # Convert priority string to enum
        priority_map = {
            "low": TaskPriority.LOW,
            "medium": TaskPriority.MEDIUM,
            "high": TaskPriority.HIGH,
            "critical": TaskPriority.CRITICAL
        }
        priority_enum = priority_map.get(priority.lower(), TaskPriority.MEDIUM)
        
        # Create task
        task = {
            "task_id": f"task_{phase_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "phase_id": phase_id,
            "priority": priority_enum.value,
            "priority_name": priority_enum.name.lower(),
            "state": TaskState.QUEUED.value,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "metadata": metadata or {}
        }
        
        # Save to queued directory
        task_file = self.queue_dir / TaskState.QUEUED.value / f"{phase_id}.json"
        with open(task_file, 'w') as f:
            json.dump(task, f, indent=2)
        
        return task["task_id"]
    
    def dequeue(self) -> Optional[Dict]:
        """
        Get next highest priority task from queue.
        
        Returns:
            Task dictionary or None if queue is empty
        """
        queued_dir = self.queue_dir / TaskState.QUEUED.value
        
        # Get all queued tasks
        tasks = []
        for task_file in queued_dir.glob("*.json"):
            with open(task_file, 'r') as f:
                task = json.load(f)
                task["_file"] = task_file
                tasks.append(task)
        
        if not tasks:
            return None
        
        # Sort by priority (descending) and created_at (ascending)
        tasks.sort(key=lambda t: (-t["priority"], t["created_at"]))
        
        # Return highest priority task
        next_task = tasks[0]
        
        # Remove internal file reference before returning
        del next_task["_file"]
        
        return next_task
    
    def mark_running(self, phase_id: str) -> bool:
        """
        Mark task as running.
        
        Args:
            phase_id: Phase identifier
        
        Returns:
            True if successful
        """
        return self._move_task(phase_id, TaskState.QUEUED, TaskState.RUNNING)
    
    def mark_complete(self, phase_id: str, result: Optional[Dict] = None) -> bool:
        """
        Mark task as complete.
        
        Args:
            phase_id: Phase identifier
            result: Optional result data
        
        Returns:
            True if successful
        """
        success = self._move_task(phase_id, TaskState.RUNNING, TaskState.COMPLETE)
        
        if success and result:
            # Update task with result
            task_file = self.queue_dir / TaskState.COMPLETE.value / f"{phase_id}.json"
            with open(task_file, 'r') as f:
                task = json.load(f)
            
            task["result"] = result
            task["completed_at"] = datetime.utcnow().isoformat() + "Z"
            task["updated_at"] = datetime.utcnow().isoformat() + "Z"
            
            with open(task_file, 'w') as f:
                json.dump(task, f, indent=2)
        
        return success
    
    def mark_failed(self, phase_id: str, error: str) -> bool:
        """
        Mark task as failed.
        
        Args:
            phase_id: Phase identifier
            error: Error message
        
        Returns:
            True if successful
        """
        success = self._move_task(phase_id, TaskState.RUNNING, TaskState.FAILED)
        
        if success:
            # Update task with error
            task_file = self.queue_dir / TaskState.FAILED.value / f"{phase_id}.json"
            with open(task_file, 'r') as f:
                task = json.load(f)
            
            task["error"] = error
            task["failed_at"] = datetime.utcnow().isoformat() + "Z"
            task["updated_at"] = datetime.utcnow().isoformat() + "Z"
            
            with open(task_file, 'w') as f:
                json.dump(task, f, indent=2)
        
        return success
    
    def _move_task(self, phase_id: str, from_state: TaskState, to_state: TaskState) -> bool:
        """
        Move task from one state to another.
        
        Args:
            phase_id: Phase identifier
            from_state: Source state
            to_state: Target state
        
        Returns:
            True if successful
        """
        src_file = self.queue_dir / from_state.value / f"{phase_id}.json"
        dst_file = self.queue_dir / to_state.value / f"{phase_id}.json"
        
        if not src_file.exists():
            return False
        
        # Load task
        with open(src_file, 'r') as f:
            task = json.load(f)
        
        # Update state
        task["state"] = to_state.value
        task["updated_at"] = datetime.utcnow().isoformat() + "Z"
        
        # Save to new location
        with open(dst_file, 'w') as f:
            json.dump(task, f, indent=2)
        
        # Remove from old location
        src_file.unlink()
        
        return True
    
    def list_tasks(self, state: Optional[TaskState] = None) -> List[Dict]:
        """
        List tasks by state.
        
        Args:
            state: Optional state filter (lists all if None)
        
        Returns:
            List of task dictionaries
        """
        tasks = []
        
        states = [state] if state else list(TaskState)
        
        for s in states:
            state_dir = self.queue_dir / s.value
            for task_file in state_dir.glob("*.json"):
                with open(task_file, 'r') as f:
                    task = json.load(f)
                    tasks.append(task)
        
        return tasks
    
    def list_queued(self) -> List[Dict]:
        """List all queued tasks sorted by priority."""
        tasks = self.list_tasks(TaskState.QUEUED)
        tasks.sort(key=lambda t: (-t["priority"], t["created_at"]))
        return tasks
    
    def list_running(self) -> List[Dict]:
        """List all running tasks."""
        return self.list_tasks(TaskState.RUNNING)
    
    def list_complete(self) -> List[Dict]:
        """List all completed tasks."""
        return self.list_tasks(TaskState.COMPLETE)
    
    def list_failed(self) -> List[Dict]:
        """List all failed tasks."""
        return self.list_tasks(TaskState.FAILED)
    
    def get_task(self, phase_id: str) -> Optional[Dict]:
        """
        Get task by phase ID.
        
        Args:
            phase_id: Phase identifier
        
        Returns:
            Task dictionary or None
        """
        for state in TaskState:
            task_file = self.queue_dir / state.value / f"{phase_id}.json"
            if task_file.exists():
                with open(task_file, 'r') as f:
                    return json.load(f)
        
        return None
    
    def clear_state(self, state: TaskState) -> int:
        """
        Clear all tasks in a given state.
        
        Args:
            state: State to clear
        
        Returns:
            Number of tasks cleared
        """
        state_dir = self.queue_dir / state.value
        count = 0
        
        for task_file in state_dir.glob("*.json"):
            task_file.unlink()
            count += 1
        
        return count
    
    def get_stats(self) -> Dict:
        """Get queue statistics."""
        return {
            "queued": len(self.list_tasks(TaskState.QUEUED)),
            "running": len(self.list_tasks(TaskState.RUNNING)),
            "complete": len(self.list_tasks(TaskState.COMPLETE)),
            "failed": len(self.list_tasks(TaskState.FAILED)),
            "total": len(self.list_tasks())
        }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="File-based task queue manager"
    )
    parser.add_argument(
        "--enqueue",
        action="store_true",
        help="Enqueue a new task"
    )
    parser.add_argument(
        "--dequeue",
        action="store_true",
        help="Dequeue next task"
    )
    parser.add_argument(
        "--phase",
        type=str,
        help="Phase ID"
    )
    parser.add_argument(
        "--priority",
        type=str,
        default="medium",
        choices=["low", "medium", "high", "critical"],
        help="Task priority"
    )
    parser.add_argument(
        "--mark-running",
        type=str,
        metavar="PHASE_ID",
        help="Mark task as running"
    )
    parser.add_argument(
        "--mark-complete",
        type=str,
        metavar="PHASE_ID",
        help="Mark task as complete"
    )
    parser.add_argument(
        "--mark-failed",
        type=str,
        metavar="PHASE_ID",
        help="Mark task as failed"
    )
    parser.add_argument(
        "--list-queued",
        action="store_true",
        help="List queued tasks"
    )
    parser.add_argument(
        "--list-running",
        action="store_true",
        help="List running tasks"
    )
    parser.add_argument(
        "--list-complete",
        action="store_true",
        help="List completed tasks"
    )
    parser.add_argument(
        "--list-failed",
        action="store_true",
        help="List failed tasks"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show queue statistics"
    )
    parser.add_argument(
        "--get",
        type=str,
        metavar="PHASE_ID",
        help="Get task by phase ID"
    )
    
    args = parser.parse_args()
    
    try:
        queue = TaskQueue()
        
        if args.enqueue:
            if not args.phase:
                print("Error: --phase required for enqueue", file=sys.stderr)
                return 1
            
            task_id = queue.enqueue(args.phase, args.priority)
            print(json.dumps({"task_id": task_id, "phase_id": args.phase, "priority": args.priority}))
            return 0
        
        if args.dequeue:
            task = queue.dequeue()
            if task:
                print(json.dumps(task, indent=2))
                return 0
            else:
                print(json.dumps({"message": "Queue is empty"}))
                return 0
        
        if args.mark_running:
            success = queue.mark_running(args.mark_running)
            if success:
                print(json.dumps({"status": "success", "phase_id": args.mark_running, "state": "running"}))
                return 0
            else:
                print(json.dumps({"status": "error", "message": "Task not found in queued state"}))
                return 1
        
        if args.mark_complete:
            success = queue.mark_complete(args.mark_complete)
            if success:
                print(json.dumps({"status": "success", "phase_id": args.mark_complete, "state": "complete"}))
                return 0
            else:
                print(json.dumps({"status": "error", "message": "Task not found in running state"}))
                return 1
        
        if args.mark_failed:
            success = queue.mark_failed(args.mark_failed, "Manual failure")
            if success:
                print(json.dumps({"status": "success", "phase_id": args.mark_failed, "state": "failed"}))
                return 0
            else:
                print(json.dumps({"status": "error", "message": "Task not found in running state"}))
                return 1
        
        if args.list_queued:
            tasks = queue.list_queued()
            print(json.dumps(tasks, indent=2))
            return 0
        
        if args.list_running:
            tasks = queue.list_running()
            print(json.dumps(tasks, indent=2))
            return 0
        
        if args.list_complete:
            tasks = queue.list_complete()
            print(json.dumps(tasks, indent=2))
            return 0
        
        if args.list_failed:
            tasks = queue.list_failed()
            print(json.dumps(tasks, indent=2))
            return 0
        
        if args.stats:
            stats = queue.get_stats()
            print(json.dumps(stats, indent=2))
            return 0
        
        if args.get:
            task = queue.get_task(args.get)
            if task:
                print(json.dumps(task, indent=2))
                return 0
            else:
                print(json.dumps({"error": "Task not found"}))
                return 1
        
        parser.print_help()
        return 1
    
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
