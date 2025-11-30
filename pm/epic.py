"""
Epic Management

Handles creation, loading, validation, and task decomposition for Epics.
Epics are stored as Markdown files with metadata sidecars in pm/workspace/epics/{epic-name}/
"""
DOC_ID: DOC-PM-PM-EPIC-014
DOC_ID: DOC-PM-PM-EPIC-008

from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
import re

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    from jinja2 import Environment, FileSystemLoader
    HAS_JINJA2 = True
except ImportError:
    HAS_JINJA2 = False

from pm.models import Epic, Task, PRD, Status, Priority, Effort
from pm import WORKSPACE_ROOT, TEMPLATES_ROOT


class EpicManager:
    """Manages Epic lifecycle operations"""
    
    def __init__(self, workspace_dir: Optional[Path] = None, template_dir: Optional[Path] = None):
        self.workspace_dir = Path(workspace_dir) if workspace_dir else WORKSPACE_ROOT / "epics"
        self.template_dir = Path(template_dir) if template_dir else TEMPLATES_ROOT
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
    
    def create_epic_from_prd(
        self,
        prd: PRD,
        *,
        technical_approach: str = "",
        dependencies: Optional[List[str]] = None,
        risks: Optional[List[str]] = None,
        implementation_plan: str = "",
    ) -> Epic:
        """
        Create an Epic from a PRD.
        
        Args:
            prd: Source PRD
            technical_approach: Technical architecture decisions
            dependencies: List of dependencies
            risks: List of risks
            implementation_plan: High-level implementation plan
        
        Returns:
            Epic instance
        
        Raises:
            ValueError: If epic already exists
        """
        epic_dir = self.workspace_dir / prd.name
        if epic_dir.exists():
            raise ValueError(f"Epic '{prd.name}' already exists at {epic_dir}")
        
        # Create epic directory
        epic_dir.mkdir(parents=True, exist_ok=True)
        (epic_dir / "tasks").mkdir(exist_ok=True)
        
        # Create Epic instance
        epic = Epic(
            name=prd.name,
            title=prd.title,
            prd_name=prd.name,
            created=datetime.utcnow(),
            status=Status.PLANNED,
            priority=prd.priority,
            technical_approach=technical_approach,
            dependencies=dependencies or [],
            risks=risks or [],
            implementation_plan=implementation_plan,
            file_path=epic_dir / "epic.md",
            metadata_path=epic_dir / ".metadata.yaml",
        )
        
        # Validate
        errors = epic.validate()
        if errors:
            raise ValueError(f"Epic validation failed: {'; '.join(errors)}")
        
        # Save
        self._save_epic(epic)
        self._save_metadata(epic)
        
        return epic
    
    def load_epic(self, name: str, load_tasks: bool = True) -> Epic:
        """
        Load Epic from directory.
        
        Args:
            name: Epic name
            load_tasks: Whether to load all tasks (default: True)
        
        Returns:
            Epic instance
        
        Raises:
            FileNotFoundError: If epic doesn't exist
        """
        epic_dir = self.workspace_dir / name
        if not epic_dir.exists():
            raise FileNotFoundError(f"Epic '{name}' not found at {epic_dir}")
        
        epic_file = epic_dir / "epic.md"
        if not epic_file.exists():
            raise FileNotFoundError(f"Epic file not found: {epic_file}")
        
        # Parse epic file
        epic = self._parse_epic_file(epic_file)
        
        # Load metadata
        metadata = self._load_metadata(epic_dir / ".metadata.yaml")
        if metadata:
            epic.github_issue = metadata.get("github_issue")
            epic.status = Status(metadata.get("status", "planned"))
            epic.updated = self._parse_date(metadata.get("updated_at"))
        
        # Load tasks
        if load_tasks:
            epic.tasks = self._load_tasks(epic_dir / "tasks", epic.name)
        
        return epic
    
    def list_epics(self, status_filter: Optional[Status] = None) -> List[Epic]:
        """
        List all epics in workspace.
        
        Args:
            status_filter: Optional status to filter by
        
        Returns:
            List of Epic instances (without tasks loaded)
        """
        epics = []
        for epic_dir in self.workspace_dir.iterdir():
            if not epic_dir.is_dir():
                continue
            try:
                epic = self.load_epic(epic_dir.name, load_tasks=False)
                if status_filter is None or epic.status == status_filter:
                    epics.append(epic)
            except Exception:
                # Skip malformed epics
                continue
        
        return sorted(epics, key=lambda e: e.created, reverse=True)
    
    def decompose_epic(
        self,
        epic: Epic,
        tasks_data: List[Dict],
    ) -> Epic:
        """
        Decompose epic into tasks.
        
        Args:
            epic: Epic to decompose
            tasks_data: List of task dictionaries with keys:
                - title: Task title (required)
                - description: Task description
                - acceptance_criteria: List of criteria
                - file_scope: List of file paths
                - effort: small | medium | large
                - parallel: bool
                - dependencies: List of task IDs
        
        Returns:
            Updated Epic with tasks
        
        Raises:
            ValueError: If task data is invalid
        """
        epic_dir = self.workspace_dir / epic.name
        tasks_dir = epic_dir / "tasks"
        tasks_dir.mkdir(exist_ok=True)
        
        # Create tasks
        tasks = []
        for idx, task_data in enumerate(tasks_data, start=1):
            task_id = f"task-{idx:02d}"
            
            task = Task(
                task_id=task_id,
                title=task_data.get("title", ""),
                epic_name=epic.name,
                status=Status.PLANNED,
                priority=epic.priority,
                effort=Effort(task_data.get("effort", "medium")),
                parallel=task_data.get("parallel", True),
                dependencies=task_data.get("dependencies", []),
                file_scope=[Path(f) for f in task_data.get("file_scope", [])],
                description=task_data.get("description", ""),
                acceptance_criteria=task_data.get("acceptance_criteria", []),
                technical_notes=task_data.get("technical_notes", ""),
                files_to_modify=task_data.get("files_to_modify", {}),
                created=datetime.utcnow(),
                file_path=tasks_dir / f"{task_id}.md",
            )
            
            # Validate
            errors = task.validate()
            if errors:
                raise ValueError(f"Task {task_id} validation failed: {'; '.join(errors)}")
            
            # Save task
            self._save_task(task)
            tasks.append(task)
        
        # Update epic
        epic.tasks = tasks
        epic.updated = datetime.utcnow()
        
        # Save epic and metadata
        self._save_epic(epic)
        self._save_metadata(epic)
        
        return epic
    
    def update_task_status(self, epic_name: str, task_id: str, status: Status) -> Task:
        """
        Update task status.
        
        Args:
            epic_name: Epic name
            task_id: Task ID
            status: New status
        
        Returns:
            Updated Task
        """
        epic = self.load_epic(epic_name)
        task = epic.get_task(task_id)
        
        if task is None:
            raise ValueError(f"Task {task_id} not found in epic {epic_name}")
        
        task.status = status
        task.updated = datetime.utcnow()
        
        # Save task
        self._save_task(task)
        
        # Update epic metadata
        epic.updated = datetime.utcnow()
        self._save_metadata(epic)
        
        return task
    
    def _save_epic(self, epic: Epic) -> None:
        """Save epic to file using Jinja2 template."""
        if not HAS_JINJA2:
            raise RuntimeError("Jinja2 is required. Install with: pip install jinja2")
        
        env = Environment(loader=FileSystemLoader(str(self.template_dir)))
        template = env.get_template("epic.md.j2")
        
        content = template.render(
            title=epic.title,
            prd_name=epic.prd_name,
            created=epic.created.strftime("%Y-%m-%d"),
            status=epic.status.value if isinstance(epic.status, Status) else epic.status,
            priority=epic.priority.value if isinstance(epic.priority, Priority) else epic.priority,
            github_issue=epic.github_issue,
            technical_approach=epic.technical_approach,
            dependencies=epic.dependencies,
            risks=epic.risks,
            implementation_plan=epic.implementation_plan,
            tasks=epic.tasks,
        )
        
        assert epic.file_path is not None
        epic.file_path.write_text(content, encoding="utf-8")
    
    def _save_task(self, task: Task) -> None:
        """Save task to file using Jinja2 template."""
        if not HAS_JINJA2:
            raise RuntimeError("Jinja2 is required. Install with: pip install jinja2")
        
        env = Environment(loader=FileSystemLoader(str(self.template_dir)))
        template = env.get_template("task.md.j2")
        
        content = template.render(
            title=task.title,
            epic_name=task.epic_name,
            task_id=task.task_id,
            status=task.status.value if isinstance(task.status, Status) else task.status,
            priority=task.priority.value if isinstance(task.priority, Priority) else task.priority,
            assignee=task.assignee,
            effort=task.effort.value if isinstance(task.effort, Effort) else task.effort,
            parallel=task.parallel,
            dependencies=task.dependencies,
            file_scope=task.file_scope,
            github_issue=task.github_issue,
            description=task.description,
            acceptance_criteria=task.acceptance_criteria,
            technical_notes=task.technical_notes,
            files_to_modify=task.files_to_modify,
            created=task.created.strftime("%Y-%m-%d %H:%M:%S") if task.created else None,
            updated=task.updated.strftime("%Y-%m-%d %H:%M:%S") if task.updated else None,
        )
        
        assert task.file_path is not None
        task.file_path.write_text(content, encoding="utf-8")
    
    def _save_metadata(self, epic: Epic) -> None:
        """Save epic metadata to YAML sidecar."""
        if not HAS_YAML:
            raise RuntimeError("PyYAML is required. Install with: pip install pyyaml")
        
        metadata = {
            "epic_name": epic.name,
            "status": epic.status.value if isinstance(epic.status, Status) else epic.status,
            "task_count": len(epic.tasks),
            "completed_tasks": sum(1 for t in epic.tasks if t.status == Status.COMPLETED),
            "progress_percent": epic.progress_percent(),
            "github_issue": epic.github_issue,
            "created_at": epic.created.isoformat(),
            "updated_at": (epic.updated or datetime.utcnow()).isoformat(),
        }
        
        assert epic.metadata_path is not None
        epic.metadata_path.write_text(yaml.dump(metadata, default_flow_style=False), encoding="utf-8")
    
    def _load_metadata(self, path: Path) -> Optional[Dict]:
        """Load metadata from YAML file."""
        if not path.exists():
            return None
        
        if not HAS_YAML:
            return None
        
        try:
            return yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            return None
    
    def _parse_epic_file(self, path: Path) -> Epic:
        """Parse epic from markdown file with YAML frontmatter."""
        if not HAS_YAML:
            raise RuntimeError("PyYAML is required. Install with: pip install pyyaml")
        
        content = path.read_text(encoding="utf-8")
        
        # Extract frontmatter
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
        if not match:
            raise ValueError(f"Invalid epic format: missing YAML frontmatter in {path}")
        
        frontmatter_text, body_text = match.groups()
        frontmatter = yaml.safe_load(frontmatter_text) or {}
        
        # Parse sections
        sections = self._parse_sections(body_text)
        
        return Epic(
            name=path.parent.name,
            title=frontmatter.get("title", ""),
            prd_name=frontmatter.get("prd", ""),
            created=self._parse_date(frontmatter.get("created")),
            status=Status(frontmatter.get("status", "planned")),
            priority=Priority(frontmatter.get("priority", "medium")),
            github_issue=frontmatter.get("github_issue"),
            technical_approach=sections.get("technical_approach", ""),
            dependencies=sections.get("dependencies", []),
            risks=sections.get("risks", []),
            implementation_plan=sections.get("implementation_plan", ""),
            file_path=path,
            metadata_path=path.parent / ".metadata.yaml",
        )
    
    def _parse_sections(self, body: str) -> dict:
        """Parse markdown body into sections."""
        sections = {}
        
        # Technical Approach
        tech_match = re.search(r'## Technical Approach\s*\n+(.*?)(?=\n##|\Z)', body, re.DOTALL)
        if tech_match:
            sections["technical_approach"] = tech_match.group(1).strip()
        
        # Implementation Plan
        plan_match = re.search(r'## Implementation Plan\s*\n+(.*?)(?=\n##|\Z)', body, re.DOTALL)
        if plan_match:
            sections["implementation_plan"] = plan_match.group(1).strip()
        
        # Lists
        sections["dependencies"] = self._parse_list_section(body, "Dependencies")
        sections["risks"] = self._parse_risk_section(body)
        
        return sections
    
    def _parse_list_section(self, body: str, section_name: str) -> List[str]:
        """Parse a list section."""
        pattern = rf'## {section_name}\s*\n+(.*?)(?=\n##|\Z)'
        match = re.search(pattern, body, re.DOTALL)
        if not match:
            return []
        
        items = []
        for line in match.group(1).strip().split('\n'):
            line = line.strip()
            if line.startswith('- '):
                items.append(line[2:].strip())
        
        return items
    
    def _parse_risk_section(self, body: str) -> List[str]:
        """Parse risk assessment section."""
        pattern = r'## Risk Assessment\s*\n+(.*?)(?=\n##|\Z)'
        match = re.search(pattern, body, re.DOTALL)
        if not match:
            return []
        
        risks = []
        for line in match.group(1).strip().split('\n'):
            line = line.strip()
            if line.startswith('- **Risk:**'):
                risk_text = line.replace('- **Risk:**', '').strip()
                risks.append(risk_text)
        
        return risks
    
    def _load_tasks(self, tasks_dir: Path, epic_name: str) -> List[Task]:
        """Load all tasks from tasks directory."""
        if not tasks_dir.exists():
            return []
        
        tasks = []
        for task_file in sorted(tasks_dir.glob("*.md")):
            try:
                task = self._parse_task_file(task_file, epic_name)
                tasks.append(task)
            except Exception:
                # Skip malformed tasks
                continue
        
        return tasks
    
    def _parse_task_file(self, path: Path, epic_name: str) -> Task:
        """Parse task from markdown file."""
        if not HAS_YAML:
            raise RuntimeError("PyYAML is required. Install with: pip install pyyaml")
        
        content = path.read_text(encoding="utf-8")
        
        # Extract frontmatter
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
        if not match:
            raise ValueError(f"Invalid task format in {path}")
        
        frontmatter_text, body_text = match.groups()
        frontmatter = yaml.safe_load(frontmatter_text) or {}
        
        # Parse body sections
        sections = self._parse_task_sections(body_text)
        
        return Task(
            task_id=frontmatter.get("task_id", path.stem),
            title=frontmatter.get("title", ""),
            epic_name=epic_name,
            status=Status(frontmatter.get("status", "planned")),
            priority=Priority(frontmatter.get("priority", "medium")),
            assignee=frontmatter.get("assignee"),
            effort=Effort(frontmatter.get("effort", "medium")),
            parallel=frontmatter.get("parallel", True),
            dependencies=self._parse_list_value(frontmatter.get("dependencies", [])),
            file_scope=[Path(f) for f in self._parse_list_value(frontmatter.get("file_scope", []))],
            github_issue=frontmatter.get("github_issue"),
            description=sections.get("description", ""),
            acceptance_criteria=sections.get("acceptance_criteria", []),
            technical_notes=sections.get("technical_notes", ""),
            files_to_modify=sections.get("files_to_modify", {}),
            created=self._parse_date(frontmatter.get("created")),
            updated=self._parse_date(frontmatter.get("updated")),
            file_path=path,
        )
    
    def _parse_task_sections(self, body: str) -> dict:
        """Parse task body sections."""
        sections = {}
        
        # Description
        desc_match = re.search(r'## Description\s*\n+(.*?)(?=\n##|\Z)', body, re.DOTALL)
        if desc_match:
            sections["description"] = desc_match.group(1).strip()
        
        # Technical Notes
        notes_match = re.search(r'## Technical Notes\s*\n+(.*?)(?=\n##|\Z)', body, re.DOTALL)
        if notes_match:
            sections["technical_notes"] = notes_match.group(1).strip()
        
        # Acceptance Criteria (checkboxes)
        sections["acceptance_criteria"] = self._parse_checkboxes(body, "Acceptance Criteria")
        
        # Files to Modify
        sections["files_to_modify"] = self._parse_files_section(body)
        
        return sections
    
    def _parse_checkboxes(self, body: str, section_name: str) -> List[str]:
        """Parse checkbox list."""
        pattern = rf'## {section_name}\s*\n+(.*?)(?=\n##|\Z)'
        match = re.search(pattern, body, re.DOTALL)
        if not match:
            return []
        
        items = []
        for line in match.group(1).strip().split('\n'):
            line = line.strip()
            if line.startswith('- [ ]') or line.startswith('- [x]'):
                items.append(line[5:].strip())
        
        return items
    
    def _parse_files_section(self, body: str) -> Dict[str, str]:
        """Parse files to modify section."""
        pattern = r'## Files to Modify\s*\n+(.*?)(?=\n##|\Z)'
        match = re.search(pattern, body, re.DOTALL)
        if not match:
            return {}
        
        files = {}
        for line in match.group(1).strip().split('\n'):
            line = line.strip()
            if line.startswith('- **`') and '`**:' in line:
                parts = line.split('`**:', 1)
                if len(parts) == 2:
                    file_path = parts[0].replace('- **`', '').strip()
                    description = parts[1].strip()
                    files[file_path] = description
        
        return files
    
    def _parse_date(self, date_str) -> datetime:
        """Parse date string."""
        if isinstance(date_str, datetime):
            return date_str
        if isinstance(date_str, str):
            try:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except Exception:
                try:
                    return datetime.strptime(date_str, "%Y-%m-%d")
                except Exception:
                    pass
        return datetime.utcnow()
    
    def _parse_list_value(self, value) -> List[str]:
        """Parse list from various formats."""
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            if value == '[]':
                return []
            return [v.strip() for v in value.split(',') if v.strip()]
        return []


# Convenience functions
def create_epic_from_prd(prd: PRD, **kwargs) -> Epic:
    """Create epic from PRD (convenience function)."""
    manager = EpicManager()
    return manager.create_epic_from_prd(prd, **kwargs)


def load_epic(name: str) -> Epic:
    """Load epic (convenience function)."""
    manager = EpicManager()
    return manager.load_epic(name)


def list_epics(status_filter: Optional[Status] = None) -> List[Epic]:
    """List epics (convenience function)."""
    manager = EpicManager()
    return manager.list_epics(status_filter)
