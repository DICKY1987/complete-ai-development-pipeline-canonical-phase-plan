"""
Patch Management System for Pipeline Plus
Core patch lifecycle—capture, store, parse, apply
"""
import hashlib
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any


@dataclass
class PatchParseResult:
    """Result of parsing a patch file"""
    files_modified: List[str]
    hunks: int
    line_count: int
    additions: int
    deletions: int


@dataclass
class ApplyResult:
    """Result of applying a patch"""
    success: bool
    message: str
    conflicts: List[str] = field(default_factory=list)


@dataclass
class PatchArtifact:
    """Patch artifact with metadata"""
    patch_id: str
    patch_file: Path
    diff_hash: str
    files_modified: List[str]
    line_count: int
    created_at: str
    run_id: Optional[str] = None
    ws_id: Optional[str] = None
    step_name: Optional[str] = None
    attempt: int = 1
    validated: bool = False
    applied: bool = False


class PatchManager:
    """
    Core patch lifecycle manager
    - Capture patches from git worktrees
    - Parse patch contents
    - Apply patches safely
    - Store patch metadata
    """
    
    def __init__(self, ledger_path: str = ".ledger/patches"):
        self.ledger_path = Path(ledger_path)
        self.ledger_path.mkdir(parents=True, exist_ok=True)
    
    def capture_patch(
        self,
        run_id: str,
        ws_id: str,
        worktree_path: str,
        step_name: str = "edit",
        attempt: int = 1
    ) -> PatchArtifact:
        """
        Capture git diff from worktree and create patch artifact
        
        Args:
            run_id: Run identifier
            ws_id: Workstream identifier
            worktree_path: Path to git worktree
            step_name: Step name (edit, fix_static, fix_runtime)
            attempt: Attempt number
            
        Returns:
            PatchArtifact with captured diff
        """
        # Generate patch diff
        result = subprocess.run(
            ['git', 'diff', '--no-ext-diff'],
            cwd=worktree_path,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"git diff failed: {result.stderr}")
        
        diff_content = result.stdout
        
        # Parse patch to extract files
        parse_result = self.parse_patch_content(diff_content)
        
        # Compute diff hash (SHA256)
        diff_hash = hashlib.sha256(diff_content.encode('utf-8')).hexdigest()
        
        # Create patch file
        patch_filename = f"{ws_id}-{run_id}-{step_name}-{attempt}.patch"
        patch_file = self.ledger_path / patch_filename
        
        # Store patch content
        with open(patch_file, 'w', encoding='utf-8') as f:
            f.write(diff_content)
        
        # Create artifact
        patch_id = f"{ws_id}-{run_id}-{step_name}-{attempt}"
        artifact = PatchArtifact(
            patch_id=patch_id,
            patch_file=patch_file,
            diff_hash=diff_hash,
            files_modified=parse_result.files_modified,
            line_count=parse_result.line_count,
            created_at=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            run_id=run_id,
            ws_id=ws_id,
            step_name=step_name,
            attempt=attempt
        )
        
        return artifact
    
    def parse_patch(self, patch_file: Path) -> PatchParseResult:
        """
        Parse a patch file to extract metadata
        
        Args:
            patch_file: Path to patch file
            
        Returns:
            PatchParseResult with extracted metadata
        """
        with open(patch_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse_patch_content(content)
    
    def parse_patch_content(self, content: str) -> PatchParseResult:
        """
        Parse patch content to extract metadata
        
        Args:
            content: Patch file content (unified diff format)
            
        Returns:
            PatchParseResult with extracted metadata
        """
        files_modified = []
        hunks = 0
        additions = 0
        deletions = 0
        
        # Parse unified diff format
        # Lines starting with "diff --git" indicate file changes
        # Lines starting with "@@ " indicate hunks
        # Lines starting with "+" are additions
        # Lines starting with "-" are deletions
        
        for line in content.split('\n'):
            # Extract modified files
            if line.startswith('diff --git '):
                # Format: diff --git a/path/to/file b/path/to/file
                match = re.search(r'diff --git a/(.*?) b/(.*?)$', line)
                if match:
                    file_path = match.group(2)  # Use the 'b/' path
                    if file_path not in files_modified:
                        files_modified.append(file_path)
            
            # Count hunks
            elif line.startswith('@@'):
                hunks += 1
            
            # Count additions (but not the +++ file marker)
            elif line.startswith('+') and not line.startswith('+++'):
                additions += 1
            
            # Count deletions (but not the --- file marker)
            elif line.startswith('-') and not line.startswith('---'):
                deletions += 1
        
        line_count = additions + deletions
        
        return PatchParseResult(
            files_modified=files_modified,
            hunks=hunks,
            line_count=line_count,
            additions=additions,
            deletions=deletions
        )
    
    def apply_patch(
        self,
        patch_file: Path,
        target_path: str,
        dry_run: bool = False
    ) -> ApplyResult:
        """
        Apply a patch file to a target directory
        
        Args:
            patch_file: Path to patch file
            target_path: Target directory to apply patch
            dry_run: If True, only check if patch can be applied
            
        Returns:
            ApplyResult with success status and details
        """
        # First, check if patch can be applied (dry run)
        check_result = subprocess.run(
            ['git', 'apply', '--check', str(patch_file)],
            cwd=target_path,
            capture_output=True,
            text=True
        )
        
        if check_result.returncode != 0:
            # Parse conflicts from stderr
            conflicts = []
            for line in check_result.stderr.split('\n'):
                if 'error:' in line:
                    conflicts.append(line.strip())
            
            return ApplyResult(
                success=False,
                message=f"Patch cannot be applied: {check_result.stderr}",
                conflicts=conflicts
            )
        
        if dry_run:
            return ApplyResult(
                success=True,
                message="Patch can be applied (dry run)"
            )
        
        # Apply the patch
        apply_result = subprocess.run(
            ['git', 'apply', str(patch_file)],
            cwd=target_path,
            capture_output=True,
            text=True
        )
        
        if apply_result.returncode != 0:
            return ApplyResult(
                success=False,
                message=f"Patch application failed: {apply_result.stderr}"
            )
        
        return ApplyResult(
            success=True,
            message="Patch applied successfully"
        )
    
    def reverse_patch(
        self,
        patch_file: Path,
        target_path: str
    ) -> ApplyResult:
        """
        Reverse a patch (unapply)
        
        Args:
            patch_file: Path to patch file
            target_path: Target directory
            
        Returns:
            ApplyResult with success status
        """
        result = subprocess.run(
            ['git', 'apply', '--reverse', str(patch_file)],
            cwd=target_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return ApplyResult(
                success=False,
                message=f"Reverse patch failed: {result.stderr}"
            )
        
        return ApplyResult(
            success=True,
            message="Patch reversed successfully"
        )
    
    def get_patch_stats(self, patch_file: Path) -> Dict[str, Any]:
        """
        Get detailed statistics about a patch
        
        Args:
            patch_file: Path to patch file
            
        Returns:
            Dictionary with patch statistics
        """
        parse_result = self.parse_patch(patch_file)
        
        with open(patch_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            'files_modified': parse_result.files_modified,
            'file_count': len(parse_result.files_modified),
            'hunks': parse_result.hunks,
            'line_count': parse_result.line_count,
            'additions': parse_result.additions,
            'deletions': parse_result.deletions,
            'diff_hash': hashlib.sha256(content.encode('utf-8')).hexdigest(),
            'size_bytes': len(content.encode('utf-8'))
        }
