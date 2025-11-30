#!/usr/bin/env python3
"""
Worktree Manager for Multi-Agent Orchestration
Provides isolated git worktrees for parallel agent execution
"""
# DOC_ID: DOC-SCRIPT-SCRIPTS-WORKTREE-MANAGER-245
# DOC_ID: DOC-SCRIPT-SCRIPTS-WORKTREE-MANAGER-182

import subprocess
import logging
import threading
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger('worktree_manager')


class WorktreeManager:
    """Manage git worktrees for agent isolation"""
    
    def __init__(self, base_repo: Path, worktree_root: Path):
        self.base_repo = base_repo
        self.worktree_root = worktree_root
        self.worktree_root.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()  # CRITICAL: Prevent race conditions in git operations
        logger.info(f"WorktreeManager initialized: worktrees in {worktree_root}")
    
    def create_agent_worktree(
        self, 
        agent_id: str, 
        branch_name: str,
        workstream_id: str
    ) -> Path:
        """Create isolated worktree for agent
        
        Args:
            agent_id: Unique agent identifier (e.g., "agent-1")
            branch_name: Git branch name (e.g., "ws/ws-22/agent-1")
            workstream_id: Workstream ID (e.g., "ws-22")
            
        Returns:
            Path to created worktree
        """
        # CRITICAL: Use lock to prevent race conditions when multiple agents
        # create worktrees/branches simultaneously
        with self._lock:
            worktree_path = self.worktree_root / f"{agent_id}-{workstream_id}"
            
            # Check if branch already exists
            branch_exists = subprocess.run(
                ["git", "rev-parse", "--verify", branch_name],
                cwd=self.base_repo,
                capture_output=True
            ).returncode == 0
            
            if not branch_exists:
                # Create branch from main
                subprocess.run(
                    ["git", "checkout", "-b", branch_name, "main"],
                    cwd=self.base_repo,
                    capture_output=True,
                    check=True
                )
                # Switch back to main
                subprocess.run(
                    ["git", "checkout", "main"],
                    cwd=self.base_repo,
                    capture_output=True,
                    check=True
                )
            
            # Create worktree
            subprocess.run(
                ["git", "worktree", "add", str(worktree_path), branch_name],
                cwd=self.base_repo,
                capture_output=True,
                check=True
            )
            
            logger.info(f"Created worktree: {worktree_path} (branch: {branch_name})")
            return worktree_path
    
    def cleanup_agent_worktree(self, agent_id: str, workstream_id: str):
        """Remove worktree after completion
        
        Args:
            agent_id: Agent identifier
            workstream_id: Workstream ID
        """
        worktree_path = self.worktree_root / f"{agent_id}-{workstream_id}"
        
        if not worktree_path.exists():
            logger.warning(f"Worktree not found: {worktree_path}")
            return
        
        # Remove worktree
        result = subprocess.run(
            ["git", "worktree", "remove", str(worktree_path), "--force"],
            cwd=self.base_repo,
            capture_output=True
        )
        
        if result.returncode == 0:
            logger.info(f"Removed worktree: {worktree_path}")
        else:
            logger.error(f"Failed to remove worktree: {result.stderr.decode()}")
    
    def merge_worktree_changes(
        self, 
        branch_name: str, 
        target_branch: str = "main"
    ) -> bool:
        """Merge worktree changes back to target branch
        
        Args:
            branch_name: Source branch to merge from
            target_branch: Target branch (default: "main")
            
        Returns:
            True if merge succeeded, False otherwise
        """
        try:
            # Checkout target branch
            subprocess.run(
                ["git", "checkout", target_branch],
                cwd=self.base_repo,
                capture_output=True,
                check=True
            )
            
            # Pull latest
            subprocess.run(
                ["git", "pull", "--rebase"],
                cwd=self.base_repo,
                capture_output=True,
                check=True
            )
            
            # Merge with --no-ff to preserve history
            result = subprocess.run(
                ["git", "merge", "--no-ff", "-m", f"Merge {branch_name}", branch_name],
                cwd=self.base_repo,
                capture_output=True
            )
            
            if result.returncode == 0:
                logger.info(f"Merged {branch_name} → {target_branch}")
                
                # Delete merged branch
                subprocess.run(
                    ["git", "branch", "-d", branch_name],
                    cwd=self.base_repo,
                    capture_output=True
                )
                
                return True
            else:
                logger.error(f"Merge conflict: {result.stderr.decode()}")
                # Abort merge
                subprocess.run(
                    ["git", "merge", "--abort"],
                    cwd=self.base_repo,
                    capture_output=True
                )
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Merge failed: {e}")
            return False
    
    def list_worktrees(self) -> List[Dict]:
        """List all active worktrees
        
        Returns:
            List of dicts with worktree info: [{path, branch, commit}, ...]
        """
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=self.base_repo,
            capture_output=True,
            text=True,
            check=True
        )
        
        worktrees = []
        current = {}
        
        for line in result.stdout.split("\n"):
            line = line.strip()
            if not line:
                if current:
                    worktrees.append(current)
                    current = {}
                continue
                
            if line.startswith("worktree "):
                current["path"] = line.split(maxsplit=1)[1]
            elif line.startswith("HEAD "):
                current["commit"] = line.split(maxsplit=1)[1]
            elif line.startswith("branch "):
                current["branch"] = line.split(maxsplit=1)[1]
            elif line.startswith("detached"):
                current["branch"] = "DETACHED"
        
        if current:
            worktrees.append(current)
        
        return worktrees
    
    def cleanup_all_worktrees(self):
        """Remove all worktrees (except main)"""
        worktrees = self.list_worktrees()
        
        for wt in worktrees:
            path = Path(wt["path"])
            # Skip main repository
            if path == self.base_repo:
                continue
            
            logger.info(f"Removing worktree: {path}")
            subprocess.run(
                ["git", "worktree", "remove", str(path), "--force"],
                cwd=self.base_repo,
                capture_output=True
            )
    
    def get_worktree_status(self, worktree_path: Path) -> Optional[str]:
        """Get git status of worktree
        
        Args:
            worktree_path: Path to worktree
            
        Returns:
            Status string or None if error
        """
        if not worktree_path.exists():
            return None
        
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=worktree_path,
            capture_output=True,
            text=True
        )
        
        return result.stdout.strip() if result.returncode == 0 else None


if __name__ == "__main__":
    # Test/demo
    logging.basicConfig(level=logging.INFO)
    
    manager = WorktreeManager(
        base_repo=Path.cwd(),
        worktree_root=Path(".worktrees")
    )
    
    print("Active worktrees:")
    for wt in manager.list_worktrees():
        print(f"  {wt['path']} ({wt.get('branch', 'N/A')})")
