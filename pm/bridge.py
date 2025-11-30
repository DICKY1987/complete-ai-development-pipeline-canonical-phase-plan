"""
Bridge Layer - Format Conversions

Converts between different formats:
- OpenSpec Change → PRD
- PRD → Epic
- Epic → Workstream Bundles
- Workstream State → Task Status

This module bridges the PM section with the core pipeline.
"""
# DOC_ID: DOC-PM-PM-BRIDGE-013
# DOC_ID: DOC-PM-PM-BRIDGE-007

from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import json
import re

from pm.models import PRD, Epic, Task, Status, Priority, Effort
from pm.prd import PRDManager
from pm.epic import EpicManager


class OpenSpecToPRDConverter:
    """Convert OpenSpec change to PRD"""
    
    def convert(self, change_dir: Path) -> PRD:
        """
        Convert OpenSpec change directory to PRD.
        
        Expected structure:
        change_dir/
        ├── proposal.md  (with YAML frontmatter)
        └── tasks.md     (task list)
        
        Args:
            change_dir: Path to OpenSpec change directory
        
        Returns:
            PRD instance
        
        Raises:
            FileNotFoundError: If required files missing
            ValueError: If files are malformed
        """
        proposal_file = change_dir / "proposal.md"
        tasks_file = change_dir / "tasks.md"
        
        if not proposal_file.exists():
            raise FileNotFoundError(f"proposal.md not found in {change_dir}")
        
        # Parse proposal
        proposal_data = self._parse_proposal(proposal_file)
        
        # Parse tasks (if exists)
        tasks = []
        if tasks_file.exists():
            tasks = self._parse_tasks_file(tasks_file)
        
        # Convert to PRD
        prd_manager = PRDManager()
        
        prd = prd_manager.create_prd(
            name=change_dir.name,
            title=proposal_data.get("title", change_dir.name.replace("-", " ").title()),
            author=proposal_data.get("author", "Unknown"),
            problem=proposal_data.get("problem", ""),
            solution=proposal_data.get("solution", ""),
            requirements=proposal_data.get("requirements", tasks),
            success_criteria=proposal_data.get("success_criteria", []),
            constraints=proposal_data.get("constraints", []),
            edge_cases=proposal_data.get("edge_cases", []),
            priority=Priority(proposal_data.get("priority", "medium")),
            labels=["openspec", change_dir.name],
        )
        
        return prd
    
    def _parse_proposal(self, path: Path) -> Dict[str, Any]:
        """Parse OpenSpec proposal.md file."""
        content = path.read_text(encoding="utf-8")
        
        # Try to extract YAML frontmatter
        data = {}
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
        
        if match:
            try:
                import yaml
                frontmatter_text, body_text = match.groups()
                data = yaml.safe_load(frontmatter_text) or {}
            except Exception:
                body_text = content
        else:
            body_text = content
        
        # Extract sections from body
        sections = self._parse_markdown_sections(body_text)
        data.update(sections)
        
        return data
    
    def _parse_markdown_sections(self, text: str) -> Dict[str, Any]:
        """Extract common sections from markdown."""
        sections = {}
        
        # Problem
        problem_match = re.search(r'#+\s*Problem\s*\n+(.*?)(?=\n#+|\Z)', text, re.DOTALL | re.IGNORECASE)
        if problem_match:
            sections["problem"] = problem_match.group(1).strip()
        
        # Solution
        solution_match = re.search(r'#+\s*Solution\s*\n+(.*?)(?=\n#+|\Z)', text, re.DOTALL | re.IGNORECASE)
        if solution_match:
            sections["solution"] = solution_match.group(1).strip()
        
        # Requirements
        req_match = re.search(r'#+\s*Requirements?\s*\n+(.*?)(?=\n#+|\Z)', text, re.DOTALL | re.IGNORECASE)
        if req_match:
            sections["requirements"] = self._extract_list_items(req_match.group(1))
        
        return sections
    
    def _extract_list_items(self, text: str) -> List[str]:
        """Extract list items from markdown text."""
        items = []
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                items.append(line[2:].strip())
            elif re.match(r'^\d+\.\s+', line):
                items.append(re.sub(r'^\d+\.\s+', '', line).strip())
        return items
    
    def _parse_tasks_file(self, path: Path) -> List[str]:
        """Parse tasks.md file into list of requirements."""
        content = path.read_text(encoding="utf-8")
        tasks = []
        
        for line in content.split('\n'):
            line = line.strip()
            # Match checkbox items: - [ ] Task description
            if re.match(r'^- \[[ x]\]\s+', line):
                task = re.sub(r'^- \[[ x]\]\s+', '', line).strip()
                tasks.append(task)
        
        return tasks


class EpicToWorkstreamConverter:
    """Convert Epic + Tasks to Workstream bundles"""
    
    def convert(
        self,
        epic: Epic,
        tool_profile: str = "aider",
        base_gate: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        Convert Epic to workstream bundle(s).
        
        Args:
            epic: Epic to convert
            tool_profile: Tool to use (default: aider)
            base_gate: Starting gate number (default: 1)
        
        Returns:
            List of workstream bundle dictionaries (one per task)
        """
        bundles = []
        
        for idx, task in enumerate(epic.tasks, start=1):
            bundle = self._task_to_workstream(
                task,
                tool_profile=tool_profile,
                gate=base_gate + idx - 1,
                epic_issue=epic.github_issue,
            )
            bundles.append(bundle)
        
        return bundles
    
    def _task_to_workstream(
        self,
        task: Task,
        tool_profile: str,
        gate: int,
        epic_issue: Optional[int],
    ) -> Dict[str, Any]:
        """Convert single task to workstream bundle."""
        
        # Build metadata
        metadata = {
            "ws_id": f"ws-{task.epic_name}-{task.task_id}",
            "description": task.title,
            "tool": tool_profile,
            "gate": gate,
            "files_scope": [str(f) for f in task.file_scope],
            "ccpm_epic": task.epic_name,
            "ccpm_task": task.task_id,
            "ccpm_issue": task.github_issue,
            "priority": task.priority.value if isinstance(task.priority, Priority) else task.priority,
            "parallel": task.parallel,
            "dependencies": task.dependencies,
        }
        
        # Build context
        context = {
            "epic": task.epic_name,
            "task_id": task.task_id,
            "description": task.description,
            "acceptance_criteria": task.acceptance_criteria,
            "technical_notes": task.technical_notes,
            "files_to_modify": task.files_to_modify,
        }
        
        # Build steps (simplified - can be expanded)
        steps = [
            {
                "name": "edit",
                "tool": tool_profile,
                "prompt": self._build_prompt(task),
                "timeout": 300,
            }
        ]
        
        return {
            "metadata": metadata,
            "context": context,
            "steps": steps,
        }
    
    def _build_prompt(self, task: Task) -> str:
        """Build AI prompt from task details."""
        prompt_parts = [
            f"# Task: {task.title}",
            "",
            "## Description",
            task.description or "See acceptance criteria below.",
            "",
            "## Acceptance Criteria",
        ]
        
        for criterion in task.acceptance_criteria:
            prompt_parts.append(f"- {criterion}")
        
        if task.technical_notes:
            prompt_parts.extend([
                "",
                "## Technical Notes",
                task.technical_notes,
            ])
        
        if task.files_to_modify:
            prompt_parts.extend([
                "",
                "## Files to Modify",
            ])
            for file_path, description in task.files_to_modify.items():
                prompt_parts.append(f"- `{file_path}`: {description}")
        
        prompt_parts.extend([
            "",
            "## Instructions",
            "Implement the changes described above following the acceptance criteria.",
            "Ensure all changes are tested and documented.",
        ])
        
        return "\n".join(prompt_parts)


class WorkstreamStatusSync:
    """Sync workstream execution state back to tasks"""
    
    def __init__(self):
        self.epic_manager = EpicManager()
    
    def sync_workstream_to_task(
        self,
        ws_id: str,
        state: str,
    ) -> None:
        """
        Update task status based on workstream state.
        
        Args:
            ws_id: Workstream ID (format: ws-{epic}-{task})
            state: Workstream state (S_SUCCESS, S4_QUARANTINE, etc.)
        """
        # Parse workstream ID
        parts = ws_id.split('-')
        if len(parts) < 3:
            return  # Invalid format
        
        epic_name = parts[1]
        task_id = '-'.join(parts[2:])  # Handle task-01, task-02, etc.
        
        # Map workstream state to task status
        task_status = self._map_state_to_status(state)
        
        if task_status:
            try:
                self.epic_manager.update_task_status(epic_name, task_id, task_status)
            except Exception:
                # Silent fail - task might not exist
                pass
    
    def _map_state_to_status(self, state: str) -> Optional[Status]:
        """Map workstream state to task status."""
        state_mapping = {
            "S_INIT": Status.IN_PROGRESS,
            "S0_BASELINE_CHECK": Status.IN_PROGRESS,
            "S0_MECHANICAL_AUTOFIX": Status.IN_PROGRESS,
            "S1_AIDER_FIX": Status.IN_PROGRESS,
            "S2_CODEX_FIX": Status.IN_PROGRESS,
            "S3_CLAUDE_FIX": Status.IN_PROGRESS,
            "S_SUCCESS": Status.COMPLETED,
            "S4_QUARANTINE": Status.BLOCKED,
        }
        
        return state_mapping.get(state)


class BridgeAPI:
    """
    Unified API for all bridge conversions.
    
    This is the main interface for the core pipeline to interact with PM.
    """
    
    def __init__(self):
        self.openspec_converter = OpenSpecToPRDConverter()
        self.epic_converter = EpicToWorkstreamConverter()
        self.status_sync = WorkstreamStatusSync()
        self.prd_manager = PRDManager()
        self.epic_manager = EpicManager()
    
    # OpenSpec → PRD
    def openspec_to_prd(self, change_dir: Path) -> PRD:
        """Convert OpenSpec change to PRD."""
        return self.openspec_converter.convert(change_dir)
    
    # PRD → Epic
    def prd_to_epic(
        self,
        prd: PRD,
        technical_approach: str = "",
        **kwargs
    ) -> Epic:
        """Convert PRD to Epic."""
        return self.epic_manager.create_epic_from_prd(
            prd,
            technical_approach=technical_approach,
            **kwargs
        )
    
    # Epic → Workstream Bundles
    def epic_to_workstreams(
        self,
        epic: Epic,
        tool_profile: str = "aider",
    ) -> List[Dict[str, Any]]:
        """Convert Epic to workstream bundles."""
        return self.epic_converter.convert(epic, tool_profile=tool_profile)
    
    # Workstream State → Task Status
    def sync_workstream_status(self, ws_id: str, state: str) -> None:
        """Sync workstream execution state to task."""
        self.status_sync.sync_workstream_to_task(ws_id, state)
    
    # Convenience: Full Pipeline
    def openspec_to_workstreams(
        self,
        change_dir: Path,
        tool_profile: str = "aider",
        auto_decompose: bool = True,
    ) -> tuple[PRD, Epic, List[Dict[str, Any]]]:
        """
        Complete conversion: OpenSpec → PRD → Epic → Workstreams.
        
        Args:
            change_dir: OpenSpec change directory
            tool_profile: Tool to use for workstreams
            auto_decompose: Automatically decompose epic into tasks
        
        Returns:
            Tuple of (PRD, Epic, Workstream bundles)
        """
        # OpenSpec → PRD
        prd = self.openspec_to_prd(change_dir)
        
        # PRD → Epic
        epic = self.prd_to_epic(
            prd,
            technical_approach=f"Auto-generated from OpenSpec change {change_dir.name}",
        )
        
        # Auto-decompose if requested
        if auto_decompose and prd.requirements:
            # Simple decomposition: one task per requirement
            tasks_data = [
                {
                    "title": req,
                    "description": f"Implement: {req}",
                    "file_scope": ["TBD"],  # Will be refined manually
                    "acceptance_criteria": [f"Requirement implemented: {req}"],
                    "effort": "medium",
                    "parallel": True,
                }
                for req in prd.requirements
            ]
            epic = self.epic_manager.decompose_epic(epic, tasks_data)
        
        # Epic → Workstreams
        workstreams = self.epic_to_workstreams(epic, tool_profile=tool_profile)
        
        return prd, epic, workstreams
    
    # Save workstreams to files
    def save_workstreams(
        self,
        workstreams: List[Dict[str, Any]],
        output_dir: Path,
    ) -> List[Path]:
        """
        Save workstream bundles as JSON files.
        
        Args:
            workstreams: List of workstream dictionaries
            output_dir: Directory to save files
        
        Returns:
            List of created file paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        created_files = []
        for ws in workstreams:
            ws_id = ws["metadata"]["ws_id"]
            file_path = output_dir / f"{ws_id}.json"
            
            file_path.write_text(
                json.dumps(ws, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            created_files.append(file_path)
        
        return created_files


# Convenience functions
def openspec_to_prd(change_dir: Path) -> PRD:
    """Convert OpenSpec change to PRD (convenience)."""
    bridge = BridgeAPI()
    return bridge.openspec_to_prd(change_dir)


def prd_to_epic(prd: PRD, **kwargs) -> Epic:
    """Convert PRD to Epic (convenience)."""
    bridge = BridgeAPI()
    return bridge.prd_to_epic(prd, **kwargs)


def epic_to_workstreams(epic: Epic, tool_profile: str = "aider") -> List[Dict[str, Any]]:
    """Convert Epic to workstreams (convenience)."""
    bridge = BridgeAPI()
    return bridge.epic_to_workstreams(epic, tool_profile)


def sync_workstream_status(ws_id: str, state: str) -> None:
    """Sync workstream status to task (convenience)."""
    bridge = BridgeAPI()
    bridge.sync_workstream_status(ws_id, state)
