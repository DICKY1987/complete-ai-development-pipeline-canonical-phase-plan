"""
CCPM Integration for Core Planning

This module provides integration between CCPM workflows and core pipeline execution.
It converts CCPM epics/tasks into workstream bundles and validates parallel execution.
"""
# DOC_ID: DOC-CORE-PLANNING-CCPM-INTEGRATION-165

from pathlib import Path
from typing import List, Dict, Any, Optional

# Import PM models (will use bridge when needed)
try:
    from pm.models import Task, Epic, ConflictError
    from pm.bridge import BridgeAPI
    HAS_PM = True
except ImportError:
    HAS_PM = False


def task_to_workstream(
    task: 'Task',
    tool_profile: str = "aider",
    gate: int = 1,
) -> Dict[str, Any]:
    """
    Convert a CCPM Task into a workstream bundle.

    This is a convenience wrapper around the PM bridge layer.

    Args:
        task: Task instance from PM section
        tool_profile: Tool to use (default: aider)
        gate: Gate number for this workstream

    Returns:
        Workstream bundle dictionary

    Raises:
        RuntimeError: If PM section not available
    """
    if not HAS_PM:
        raise RuntimeError("PM section not installed. Cannot convert tasks to workstreams.")

    bridge = BridgeAPI()

    # Create a temporary epic for conversion
    # (In practice, task would already be part of an epic)
    from pm.models import Epic as EpicModel
    from datetime import datetime

    temp_epic = EpicModel(
        name=task.epic_name,
        title=f"Epic for {task.task_id}",
        prd_name=task.epic_name,
        created=datetime.now(UTC),
        tasks=[task],
    )

    workstreams = bridge.epic_to_workstreams(temp_epic, tool_profile=tool_profile)

    if workstreams:
        ws = workstreams[0]
        ws["metadata"]["gate"] = gate
        return ws

    return {}


def validate_parallel_tasks(tasks: List['Task']) -> List['ConflictError']:
    """
    Check for file-scope conflicts between tasks marked as parallel.

    Args:
        tasks: List of Task instances

    Returns:
        List of ConflictError instances (empty if safe to parallelize)
    """
    if not HAS_PM:
        return []

    conflicts = []

    # Build file → task mapping
    file_map: Dict[Path, List[str]] = {}
    for task in tasks:
        if not task.parallel:
            continue  # Skip non-parallel tasks

        for file_path in task.file_scope:
            if file_path not in file_map:
                file_map[file_path] = []
            file_map[file_path].append(task.task_id)

    # Find conflicts (files touched by multiple parallel tasks)
    for file_path, task_ids in file_map.items():
        if len(task_ids) > 1:
            # Multiple tasks touch the same file - conflict!
            for i in range(len(task_ids)):
                for j in range(i + 1, len(task_ids)):
                    from pm.models import ConflictError as ConflictErrorModel
                    conflicts.append(
                        ConflictErrorModel(
                            task1_id=task_ids[i],
                            task2_id=task_ids[j],
                            conflicting_files=[file_path],
                        )
                    )

    return conflicts


def epic_to_workstream_bundle(
    epic: 'Epic',
    tool_profile: str = "aider",
    output_dir: Optional[Path] = None,
) -> List[Path]:
    """
    Convert an Epic to workstream bundles and optionally save them.

    Args:
        epic: Epic instance
        tool_profile: Tool to use for all tasks
        output_dir: Directory to save workstream files (optional)

    Returns:
        List of created file paths (if output_dir provided), else empty list

    Raises:
        RuntimeError: If PM section not available
        ValueError: If epic has parallel conflicts
    """
    if not HAS_PM:
        raise RuntimeError("PM section not installed.")

    # Validate parallel tasks
    conflicts = validate_parallel_tasks(epic.tasks)
    if conflicts:
        conflict_details = '; '.join(str(c) for c in conflicts)
        raise ValueError(f"Parallel task conflicts detected: {conflict_details}")

    # Convert epic to workstreams
    bridge = BridgeAPI()
    workstreams = bridge.epic_to_workstreams(epic, tool_profile=tool_profile)

    # Save to files if output_dir provided
    if output_dir:
        return bridge.save_workstreams(workstreams, output_dir)

    return []


def sync_workstream_result(ws_id: str, final_state: str) -> None:
    """
    Sync workstream execution result back to CCPM task.

    This should be called by the orchestrator after workstream completion.

    Args:
        ws_id: Workstream ID (format: ws-{epic}-{task})
        final_state: Final state (S_SUCCESS, S4_QUARANTINE, etc.)
    """
    if not HAS_PM:
        return  # Silent no-op if PM not available

    from pm.bridge import sync_workstream_status
    sync_workstream_status(ws_id, final_state)


# Integration helpers for orchestrator

class CCPMIntegration:
    """
    Integration layer for orchestrator to use CCPM workflows.

    This provides a clean interface for the core pipeline to interact
    with PM section without tight coupling.
    """

    @staticmethod
    def is_available() -> bool:
        """Check if PM section is available."""
        return HAS_PM

    @staticmethod
    def load_epic(epic_name: str) -> Optional['Epic']:
        """Load epic by name."""
        if not HAS_PM:
            return None

        try:
            from pm.epic import load_epic
            return load_epic(epic_name)
        except Exception:
            return None

    @staticmethod
    def generate_workstreams_from_epic(
        epic_name: str,
        tool_profile: str = "aider",
        output_dir: Optional[Path] = None,
    ) -> List[Path]:
        """
        Generate workstream files from epic name.

        Args:
            epic_name: Name of epic to convert
            tool_profile: Tool profile to use
            output_dir: Where to save workstream files

        Returns:
            List of created workstream file paths

        Raises:
            ValueError: If epic not found or has conflicts
        """
        epic = CCPMIntegration.load_epic(epic_name)
        if not epic:
            raise ValueError(f"Epic '{epic_name}' not found")

        return epic_to_workstream_bundle(epic, tool_profile, output_dir)

    @staticmethod
    def update_task_from_workstream(ws_id: str, state: str) -> None:
        """Update task status based on workstream state."""
        sync_workstream_result(ws_id, state)

    @staticmethod
    def get_epic_metadata(epic_name: str) -> Optional[Dict[str, Any]]:
        """
        Get epic metadata for display/tracking.

        Returns:
            Dictionary with epic info, or None if not found
        """
        epic = CCPMIntegration.load_epic(epic_name)
        if not epic:
            return None

        return {
            "name": epic.name,
            "title": epic.title,
            "status": epic.status.value if hasattr(epic.status, 'value') else str(epic.status),
            "priority": epic.priority.value if hasattr(epic.priority, 'value') else str(epic.priority),
            "task_count": len(epic.tasks),
            "completed_tasks": sum(1 for t in epic.tasks if str(t.status) == "completed"),
            "progress_percent": epic.progress_percent(),
            "github_issue": epic.github_issue,
        }


# Export main integration class
__all__ = [
    "CCPMIntegration",
    "task_to_workstream",
    "validate_parallel_tasks",
    "epic_to_workstream_bundle",
    "sync_workstream_result",
]
