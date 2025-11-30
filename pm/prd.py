"""
PRD (Product Requirements Document) Management

Handles creation, loading, validation, and management of PRDs.
PRDs are stored as Markdown files with YAML frontmatter in pm/workspace/prds/
"""
# DOC_ID: DOC-PM-PM-PRD-017
# DOC_ID: DOC-PM-PM-PRD-011

from datetime import datetime
from pathlib import Path
from typing import List, Optional
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

from pm.models import PRD, Status, Priority, ValidationError
from pm import WORKSPACE_ROOT, TEMPLATES_ROOT


class PRDManager:
    """Manages PRD lifecycle operations"""
    
    def __init__(self, workspace_dir: Optional[Path] = None, template_dir: Optional[Path] = None):
        self.workspace_dir = Path(workspace_dir) if workspace_dir else WORKSPACE_ROOT / "prds"
        self.template_dir = Path(template_dir) if template_dir else TEMPLATES_ROOT
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
    
    def create_prd(
        self,
        name: str,
        title: str,
        author: str,
        *,
        problem: str = "",
        solution: str = "",
        requirements: Optional[List[str]] = None,
        success_criteria: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
        edge_cases: Optional[List[str]] = None,
        status: Status = Status.DRAFT,
        priority: Priority = Priority.MEDIUM,
        labels: Optional[List[str]] = None,
    ) -> PRD:
        """
        Create a new PRD.
        
        Args:
            name: Kebab-case identifier (e.g., 'user-authentication')
            title: Human-readable title
            author: Author name
            problem: Problem statement
            solution: Solution overview
            requirements: List of requirements
            success_criteria: List of success criteria
            constraints: List of constraints
            edge_cases: List of edge cases
            status: PRD status (default: draft)
            priority: PRD priority (default: medium)
            labels: List of labels
        
        Returns:
            PRD instance
        
        Raises:
            ValueError: If name is invalid or PRD already exists
        """
        # Validate name format
        if not self._validate_name(name):
            raise ValueError(
                f"Invalid PRD name '{name}'. Must be kebab-case (lowercase, hyphens only)."
            )
        
        # Check if PRD already exists
        prd_path = self.workspace_dir / f"{name}.md"
        if prd_path.exists():
            raise ValueError(f"PRD '{name}' already exists at {prd_path}")
        
        # Create PRD instance
        prd = PRD(
            name=name,
            title=title,
            author=author,
            date=datetime.utcnow(),
            status=status,
            priority=priority,
            labels=labels or [],
            problem=problem,
            solution=solution,
            requirements=requirements or [],
            success_criteria=success_criteria or [],
            constraints=constraints or [],
            edge_cases=edge_cases or [],
            file_path=prd_path,
        )
        
        # Validate before saving
        errors = prd.validate()
        if errors:
            raise ValueError(f"PRD validation failed: {'; '.join(errors)}")
        
        # Save to file
        self._save_prd(prd)
        
        return prd
    
    def load_prd(self, name: str) -> PRD:
        """
        Load PRD from file.
        
        Args:
            name: PRD name (without .md extension)
        
        Returns:
            PRD instance
        
        Raises:
            FileNotFoundError: If PRD doesn't exist
            ValueError: If PRD file is malformed
        """
        prd_path = self.workspace_dir / f"{name}.md"
        if not prd_path.exists():
            raise FileNotFoundError(f"PRD '{name}' not found at {prd_path}")
        
        return self._parse_prd_file(prd_path)
    
    def list_prds(self, status_filter: Optional[Status] = None) -> List[PRD]:
        """
        List all PRDs in workspace.
        
        Args:
            status_filter: Optional status to filter by
        
        Returns:
            List of PRD instances (metadata only, not full content)
        """
        prds = []
        for prd_file in self.workspace_dir.glob("*.md"):
            try:
                prd = self._parse_prd_file(prd_file, metadata_only=True)
                if status_filter is None or prd.status == status_filter:
                    prds.append(prd)
            except Exception:
                # Skip malformed files
                continue
        
        return sorted(prds, key=lambda p: p.date, reverse=True)
    
    def update_prd(self, name: str, **updates) -> PRD:
        """
        Update PRD fields.
        
        Args:
            name: PRD name
            **updates: Fields to update
        
        Returns:
            Updated PRD instance
        """
        prd = self.load_prd(name)
        
        # Update allowed fields
        for key, value in updates.items():
            if hasattr(prd, key):
                setattr(prd, key, value)
        
        # Validate
        errors = prd.validate()
        if errors:
            raise ValueError(f"PRD validation failed: {'; '.join(errors)}")
        
        # Save
        self._save_prd(prd)
        
        return prd
    
    def delete_prd(self, name: str) -> None:
        """
        Delete PRD file.
        
        Args:
            name: PRD name
        
        Raises:
            FileNotFoundError: If PRD doesn't exist
        """
        prd_path = self.workspace_dir / f"{name}.md"
        if not prd_path.exists():
            raise FileNotFoundError(f"PRD '{name}' not found")
        
        prd_path.unlink()
    
    def _validate_name(self, name: str) -> bool:
        """Validate PRD name format (kebab-case)."""
        return bool(re.match(r'^[a-z][a-z0-9\-]*$', name))
    
    def _save_prd(self, prd: PRD) -> None:
        """Save PRD to file using Jinja2 template."""
        if not HAS_JINJA2:
            raise RuntimeError("Jinja2 is required for PRD rendering. Install with: pip install jinja2")
        
        # Render template
        env = Environment(loader=FileSystemLoader(str(self.template_dir)))
        template = env.get_template("prd.md.j2")
        
        content = template.render(
            title=prd.title,
            author=prd.author,
            date=prd.date.strftime("%Y-%m-%d"),
            status=prd.status.value if isinstance(prd.status, Status) else prd.status,
            priority=prd.priority.value if isinstance(prd.priority, Priority) else prd.priority,
            labels=prd.labels,
            problem=prd.problem,
            solution=prd.solution,
            requirements=prd.requirements,
            success_criteria=prd.success_criteria,
            constraints=prd.constraints,
            edge_cases=prd.edge_cases,
        )
        
        # Write to file
        assert prd.file_path is not None
        prd.file_path.write_text(content, encoding="utf-8")
    
    def _parse_prd_file(self, path: Path, metadata_only: bool = False) -> PRD:
        """Parse PRD from markdown file with YAML frontmatter."""
        if not HAS_YAML:
            raise RuntimeError("PyYAML is required for PRD parsing. Install with: pip install pyyaml")
        
        content = path.read_text(encoding="utf-8")
        
        # Extract frontmatter
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
        if not match:
            raise ValueError(f"Invalid PRD format: missing YAML frontmatter in {path}")
        
        frontmatter_text, body_text = match.groups()
        frontmatter = yaml.safe_load(frontmatter_text) or {}
        
        # Parse sections from body (if not metadata_only)
        sections = {}
        if not metadata_only:
            sections = self._parse_sections(body_text)
        
        # Create PRD instance
        return PRD(
            name=path.stem,
            title=frontmatter.get("title", ""),
            author=frontmatter.get("author", ""),
            date=self._parse_date(frontmatter.get("date")),
            status=Status(frontmatter.get("status", "draft")),
            priority=Priority(frontmatter.get("priority", "medium")),
            labels=self._parse_labels(frontmatter.get("labels", [])),
            problem=sections.get("problem", ""),
            solution=sections.get("solution", ""),
            requirements=sections.get("requirements", []),
            success_criteria=sections.get("success_criteria", []),
            constraints=sections.get("constraints", []),
            edge_cases=sections.get("edge_cases", []),
            file_path=path,
        )
    
    def _parse_sections(self, body: str) -> dict:
        """Parse markdown body into sections."""
        sections = {}
        
        # Extract each section
        problem_match = re.search(r'# Problem Statement\s*\n+(.*?)(?=\n#|\Z)', body, re.DOTALL)
        if problem_match:
            sections["problem"] = problem_match.group(1).strip()
        
        solution_match = re.search(r'# Solution Overview\s*\n+(.*?)(?=\n#|\Z)', body, re.DOTALL)
        if solution_match:
            sections["solution"] = solution_match.group(1).strip()
        
        # Parse lists
        sections["requirements"] = self._parse_list_section(body, "Requirements")
        sections["success_criteria"] = self._parse_list_section(body, "Success Criteria")
        sections["constraints"] = self._parse_list_section(body, "Constraints")
        sections["edge_cases"] = self._parse_list_section(body, "Edge Cases")
        
        return sections
    
    def _parse_list_section(self, body: str, section_name: str) -> List[str]:
        """Parse a list section from markdown."""
        pattern = rf'# {section_name}\s*\n+(.*?)(?=\n#|\Z)'
        match = re.search(pattern, body, re.DOTALL)
        if not match:
            return []
        
        section_text = match.group(1).strip()
        items = []
        for line in section_text.split('\n'):
            line = line.strip()
            if line.startswith('- '):
                items.append(line[2:].strip())
        
        return items
    
    def _parse_date(self, date_str) -> datetime:
        """Parse date string to datetime."""
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
    
    def _parse_labels(self, labels) -> List[str]:
        """Parse labels from various formats."""
        if isinstance(labels, list):
            return labels
        if isinstance(labels, str):
            return [l.strip() for l in labels.split(',') if l.strip()]
        return []


# Convenience functions
def create_prd(name: str, title: str, author: str, **kwargs) -> PRD:
    """Create a PRD (convenience function)."""
    manager = PRDManager()
    return manager.create_prd(name, title, author, **kwargs)


def load_prd(name: str) -> PRD:
    """Load a PRD (convenience function)."""
    manager = PRDManager()
    return manager.load_prd(name)


def list_prds(status_filter: Optional[Status] = None) -> List[PRD]:
    """List PRDs (convenience function)."""
    manager = PRDManager()
    return manager.list_prds(status_filter)
