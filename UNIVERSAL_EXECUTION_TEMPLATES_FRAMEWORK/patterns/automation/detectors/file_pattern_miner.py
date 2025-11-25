"""File Pattern Miner (AUTO-002)

Detect when user creates N similar files manually and suggest batch patterns.
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class FileStructure:
    """Analyzed structure of a file."""
    extension: str
    size_bytes: int
    sections: List[str]
    key_patterns: Set[str]
    variables: Dict[str, List[str]]


class FilePatternMiner:
    """Watch file operations for repetitive patterns."""
    
    def __init__(self, db_connection, time_window_hours: int = 24):
        self.db = db_connection
        self.time_window_hours = time_window_hours
        self.recent_files: Dict[str, FileStructure] = {}
    
    def on_file_created(self, filepath: Path, content: str):
        """Hook into file creation."""
        structure = self._analyze_structure(filepath, content)
        
        # Get recent similar files
        similar = self._get_recent_similar(structure, hours=self.time_window_hours)
        
        if len(similar) >= 2:  # After 3rd similar file (2 + current)
            template = self._extract_template([s for _, s in similar] + [content])
            self._propose_batch_pattern(template, filepath.parent, similar)
    
    def _analyze_structure(self, filepath: Path, content: str) -> FileStructure:
        """Extract file metadata and structure."""
        sections = []
        variables = {}
        key_patterns = set()
        
        # Detect sections (headings, keys, etc.)
        if filepath.suffix in ['.md', '.markdown']:
            sections = [line.strip() for line in content.split('\n') if line.startswith('#')]
            key_patterns.update(sections)
        elif filepath.suffix in ['.yaml', '.yml']:
            import re
            keys = re.findall(r'^(\w+):', content, re.MULTILINE)
            sections = keys
            key_patterns.update(keys)
        elif filepath.suffix == '.py':
            import re
            # Extract function/class definitions
            funcs = re.findall(r'^def (\w+)', content, re.MULTILINE)
            classes = re.findall(r'^class (\w+)', content, re.MULTILINE)
            sections = classes + funcs
            key_patterns.update(sections)
        
        return FileStructure(
            extension=filepath.suffix,
            size_bytes=len(content.encode()),
            sections=sections,
            key_patterns=key_patterns,
            variables=variables
        )
    
    def _get_recent_similar(self, structure: FileStructure, hours: int) -> List[tuple]:
        """Find recently created similar files."""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        similar = []
        for filepath, file_struct in self.recent_files.items():
            if file_struct.extension != structure.extension:
                continue
            
            # Calculate similarity
            common_sections = len(file_struct.key_patterns & structure.key_patterns)
            total_sections = len(file_struct.key_patterns | structure.key_patterns)
            similarity = common_sections / max(total_sections, 1)
            
            if similarity >= 0.7:  # 70% similar
                similar.append((filepath, file_struct))
        
        return similar
    
    def _extract_template(self, contents: List[str]) -> str:
        """Generate template from similar files."""
        # Find common lines
        lines_sets = [set(c.split('\n')) for c in contents]
        common_lines = set.intersection(*lines_sets) if lines_sets else set()
        
        # Find variable lines (different in each)
        all_lines = set.union(*lines_sets) if lines_sets else set()
        variable_lines = all_lines - common_lines
        
        # Build template (common + placeholders for variables)
        template_lines = []
        for line in contents[0].split('\n'):
            if line in common_lines:
                template_lines.append(line)
            elif line.strip():
                # Try to identify variable part
                template_lines.append(self._generalize_line(line, contents))
        
        return '\n'.join(template_lines)
    
    def _generalize_line(self, line: str, all_contents: List[str]) -> str:
        """Replace specific values with variables."""
        # Simple heuristic: if line contains quoted string or number, make it a variable
        import re
        
        # Replace quoted strings
        line = re.sub(r'"([^"]+)"', '"{variable}"', line)
        line = re.sub(r"'([^']+)'", "'{variable}'", line)
        
        # Replace numbers
        line = re.sub(r'\b\d+\b', '{number}', line)
        
        return line
    
    def _propose_batch_pattern(self, template: str, directory: Path, similar_files: List):
        """Propose creating remaining files with batch pattern."""
        pattern_id = f"AUTO-FILE-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Save template
        templates_dir = Path(__file__).parent.parent.parent / "templates"
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        template_file = templates_dir / f"{pattern_id}.template"
        template_file.write_text(template, encoding='utf-8')
        
        # Generate notification
        print(f"\n🤖 Pattern Detected!")
        print(f"   You've created {len(similar_files) + 1} similar files in {directory}")
        print(f"   Template: {template_file}")
        print(f"   \n   Suggest using PAT-BATCH-CREATE-001 for remaining files?")
        print(f"   Variables detected: {self._count_variables(template)}")
