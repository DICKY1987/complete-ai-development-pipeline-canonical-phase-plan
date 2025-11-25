# UET V2 File Scope & Isolation

**Purpose**: Define file access rules and isolation boundaries to prevent conflicts  
**Status**: DRAFT  
**Last Updated**: 2025-11-23

---

## Table of Contents

- [File Scope Rules](#file-scope-rules)
- [Isolation Strategies](#isolation-strategies)
- [Conflict Detection](#conflict-detection)
- [Merge Resolution](#merge-resolution)
- [Worktree Management](#worktree-management)

---

## File Scope Rules

### Access Modes

Each task declares how it accesses files:

```json
{
  "step_id": "WS-007-001",
  "files": ["core/engine/executor.py"],
  "file_access": {
    "core/engine/executor.py": {
      "mode": "edit",
      "scope": "lines:45-120",
      "reason": "Add retry logic to execute() method"
    }
  }
}
```

**Supported Modes**:

| Mode | Description | Lock Type | Allowed Concurrency |
|------|-------------|-----------|---------------------|
| **read** | Read-only access | None | ∞ (unlimited readers) |
| **edit** | Modify existing file | Exclusive | 1 (exclusive writer) |
| **create** | Create new file | Exclusive | 1 (creator only) |
| **delete** | Delete file | Exclusive | 1 (deleter only) |
| **append** | Append to file (logs) | Shared | N (multiple appenders) |

### Scope Granularity

**File-Level Scope**:
```json
{
  "files": ["core/executor.py"],
  "file_access": {"core/executor.py": {"mode": "edit"}}
}
```
- ❌ **Conflict**: Any other task editing `core/executor.py`

**Line-Level Scope** (fine-grained):
```json
{
  "files": ["core/executor.py"],
  "file_access": {
    "core/executor.py": {
      "mode": "edit",
      "scope": "lines:45-55"
    }
  }
}
```
- ✅ **No Conflict**: Another task editing lines 100-120
- ❌ **Conflict**: Another task editing lines 50-60 (overlap)

**Function-Level Scope** (semantic):
```json
{
  "files": ["core/executor.py"],
  "file_access": {
    "core/executor.py": {
      "mode": "edit",
      "scope": "function:execute",
      "reason": "Add timeout parameter"
    }
  }
}
```
- Automatically detects function boundaries (via AST)
- ❌ **Conflict**: Another task modifying `execute()`
- ✅ **No Conflict**: Task modifying `cleanup()` in same file

---

## Isolation Strategies

### Strategy 1: Git Worktrees (Per-Worker Isolation)

**Approach**: Each worker gets its own git worktree (separate working directory, shared .git)

```python
import subprocess
from pathlib import Path

class WorktreeManager:
    def __init__(self, base_repo: str, worktree_dir: str = ".worktrees"):
        self.base_repo = Path(base_repo)
        self.worktree_dir = Path(worktree_dir)
    
    def create_worktree(self, worker_id: str, branch_name: str) -> Path:
        """
        Create isolated worktree for worker.
        
        Args:
            worker_id: Unique worker identifier
            branch_name: Branch to checkout in worktree
        
        Returns:
            Path to worktree directory
        """
        worktree_path = self.worktree_dir / worker_id
        
        # Create worktree
        subprocess.run([
            "git", "worktree", "add",
            str(worktree_path),
            branch_name
        ], check=True, cwd=self.base_repo)
        
        return worktree_path
    
    def remove_worktree(self, worker_id: str) -> None:
        """Remove worker's worktree."""
        worktree_path = self.worktree_dir / worker_id
        
        subprocess.run([
            "git", "worktree", "remove", str(worktree_path)
        ], check=True, cwd=self.base_repo)
```

**Directory Structure**:
```
project-root/
├── .git/                  # Shared git database
├── .worktrees/            # Isolated worktrees
│   ├── worker-001/        # Worker 1's isolated copy
│   │   └── core/
│   │       └── executor.py
│   ├── worker-002/        # Worker 2's isolated copy
│   │   └── core/
│   │       └── scheduler.py
│   └── integration/       # Integration worker's copy
│       └── core/
└── main/                  # Main worktree
    └── core/
```

**Benefits**:
- Complete isolation (no file conflicts during editing)
- Fast (hardlinks, shared .git)
- Merge conflicts detected only at integration time

**Workflow**:
```
1. Worker spawns → create worktree
2. Worker executes task → edits in worktree
3. Worker completes → commit to branch
4. Integration Worker collects branches → merge to main
5. Worker terminates → remove worktree
```

---

### Strategy 2: File Locking (Shared Filesystem)

**Approach**: Multiple workers share same filesystem with lock-based coordination

```python
import fcntl
from contextlib import contextmanager

class FileLockManager:
    def __init__(self):
        self.locks = {}  # file_path -> lock file descriptor
    
    @contextmanager
    def acquire_lock(self, file_path: str, mode: str):
        """
        Acquire lock on file.
        
        Args:
            file_path: File to lock
            mode: 'read' (shared) or 'edit' (exclusive)
        
        Raises:
            FileLockError: If lock cannot be acquired
        """
        lock_path = f"{file_path}.lock"
        lock_fd = open(lock_path, 'w')
        
        try:
            if mode == 'read':
                # Shared lock (multiple readers)
                fcntl.flock(lock_fd, fcntl.LOCK_SH)
            elif mode in ['edit', 'create', 'delete']:
                # Exclusive lock (single writer)
                fcntl.flock(lock_fd, fcntl.LOCK_EX)
            
            yield
        
        finally:
            # Release lock
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            lock_fd.close()
```

**Usage**:
```python
# Task A: Read file (shared lock)
with lock_manager.acquire_lock("core/executor.py", mode="read"):
    content = Path("core/executor.py").read_text()

# Task B: Edit file (exclusive lock, blocks if Task A holds lock)
with lock_manager.acquire_lock("core/executor.py", mode="edit"):
    # Blocks until Task A releases shared lock
    content = Path("core/executor.py").read_text()
    content += "\n# Added by Task B"
    Path("core/executor.py").write_text(content)
```

**Limitations**:
- Platform-specific (fcntl on Unix, different API on Windows)
- Deadlock risk if not careful
- Slower than worktrees for many files

---

### Strategy 3: Copy-on-Write (CoW) Filesystem

**Approach**: Use CoW filesystem features (Btrfs, ZFS) for instant snapshots

```python
import subprocess

class CoWManager:
    def create_snapshot(self, source: str, dest: str) -> None:
        """Create CoW snapshot (instant, space-efficient)."""
        # Btrfs example
        subprocess.run([
            "btrfs", "subvolume", "snapshot",
            source, dest
        ], check=True)
    
    def delete_snapshot(self, snapshot: str) -> None:
        """Delete snapshot."""
        subprocess.run([
            "btrfs", "subvolume", "delete", snapshot
        ], check=True)
```

**Benefits**:
- Instant snapshots (no copy overhead)
- Space-efficient (only stores changes)
- Fast rollback

**Limitations**:
- Requires specific filesystem (Btrfs, ZFS)
- Not portable across all systems

---

## Conflict Detection

### File-Level Conflicts

```python
class ConflictDetector:
    def detect_file_conflicts(self, task_a: dict, task_b: dict) -> bool:
        """
        Check if two tasks conflict at file level.
        
        Returns:
            True if conflict exists
        """
        files_a = set(task_a.get('files', []))
        files_b = set(task_b.get('files', []))
        
        # Check for file overlap
        overlap = files_a & files_b
        if not overlap:
            return False  # No conflict
        
        # Check access modes
        for file in overlap:
            mode_a = task_a['file_access'][file]['mode']
            mode_b = task_b['file_access'][file]['mode']
            
            # Read-read: OK (shared)
            if mode_a == 'read' and mode_b == 'read':
                continue
            
            # Any write mode: CONFLICT
            if mode_a in ['edit', 'create', 'delete'] or mode_b in ['edit', 'create', 'delete']:
                return True  # Conflict
        
        return False  # No conflict
```

### Line-Level Conflicts

```python
class LineRangeConflictDetector:
    def detect_line_conflicts(self, task_a: dict, task_b: dict) -> bool:
        """
        Check if two tasks conflict at line level.
        
        Returns:
            True if line ranges overlap
        """
        files_a = set(task_a.get('files', []))
        files_b = set(task_b.get('files', []))
        
        overlap = files_a & files_b
        if not overlap:
            return False
        
        for file in overlap:
            range_a = self._parse_line_range(task_a['file_access'][file].get('scope', ''))
            range_b = self._parse_line_range(task_b['file_access'][file].get('scope', ''))
            
            if self._ranges_overlap(range_a, range_b):
                return True  # Conflict
        
        return False
    
    def _parse_line_range(self, scope: str) -> tuple:
        """Parse 'lines:45-55' into (45, 55)."""
        if not scope or not scope.startswith('lines:'):
            return (None, None)  # Full file
        
        parts = scope.split(':')[1].split('-')
        return (int(parts[0]), int(parts[1]))
    
    def _ranges_overlap(self, range_a: tuple, range_b: tuple) -> bool:
        """Check if line ranges overlap."""
        if range_a == (None, None) or range_b == (None, None):
            return True  # Full file edit
        
        start_a, end_a = range_a
        start_b, end_b = range_b
        
        return not (end_a < start_b or end_b < start_a)
```

### Function-Level Conflicts (AST-Based)

```python
import ast

class FunctionConflictDetector:
    def detect_function_conflicts(self, file_path: str, task_a: dict, task_b: dict) -> bool:
        """
        Check if two tasks modify same function.
        
        Returns:
            True if same function targeted
        """
        func_a = task_a['file_access'][file_path].get('scope', '').replace('function:', '')
        func_b = task_b['file_access'][file_path].get('scope', '').replace('function:', '')
        
        if not func_a or not func_b:
            return True  # No scope = full file
        
        return func_a == func_b  # Same function = conflict
    
    def get_function_line_range(self, file_path: str, function_name: str) -> tuple:
        """Get line range for function using AST."""
        with open(file_path) as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                return (node.lineno, node.end_lineno)
        
        raise ValueError(f"Function {function_name} not found")
```

---

## Merge Resolution

### Automatic Merge (No Conflicts)

```python
class AutoMerger:
    def merge_patches(self, patch_a: PatchArtifact, patch_b: PatchArtifact) -> PatchArtifact:
        """
        Merge two non-conflicting patches.
        
        Args:
            patch_a: First patch (unified diff)
            patch_b: Second patch (unified diff)
        
        Returns:
            Combined patch
        
        Raises:
            MergeConflictError: If patches conflict
        """
        # Check for conflicts
        if self._has_conflicts(patch_a, patch_b):
            raise MergeConflictError("Patches modify overlapping lines")
        
        # Combine diffs
        combined_diff = self._combine_diffs(patch_a.diff_text, patch_b.diff_text)
        
        return PatchArtifact(
            patch_id=generate_ulid(),
            format="unified_diff",
            diff_text=combined_diff,
            files_touched=list(set(patch_a.files_touched + patch_b.files_touched))
        )
    
    def _has_conflicts(self, patch_a: PatchArtifact, patch_b: PatchArtifact) -> bool:
        """Check if patches touch same lines."""
        # Parse diffs
        hunks_a = self._parse_hunks(patch_a.diff_text)
        hunks_b = self._parse_hunks(patch_b.diff_text)
        
        # Check for overlapping hunks
        for file, hunks_a_file in hunks_a.items():
            if file not in hunks_b:
                continue
            
            hunks_b_file = hunks_b[file]
            for hunk_a in hunks_a_file:
                for hunk_b in hunks_b_file:
                    if self._hunks_overlap(hunk_a, hunk_b):
                        return True  # Conflict
        
        return False  # No conflict
```

### Manual Merge (Conflicts Detected)

```python
class ManualMergeOrchestrator:
    def handle_conflict(self, patch_a: PatchArtifact, patch_b: PatchArtifact) -> None:
        """
        Escalate conflict to human review.
        
        Creates a merge conflict task with:
        - Both patches
        - Conflict details (files, lines)
        - Suggested resolution strategies
        """
        conflict = MergeConflict(
            patch_id_1=patch_a.patch_id,
            patch_id_2=patch_b.patch_id,
            conflicting_files=self._get_conflicting_files(patch_a, patch_b),
            conflict_type="line_overlap",
            resolution_options=[
                "Accept Patch A",
                "Accept Patch B",
                "Merge Manually",
                "Reject Both"
            ]
        )
        
        # Create human review task
        self.human_review.create_task(
            task_type="MERGE_CONFLICT",
            title=f"Resolve conflict between {patch_a.patch_id} and {patch_b.patch_id}",
            details=conflict
        )
```

---

## Worktree Management

### Lifecycle

```python
class WorktreeLifecycleManager:
    def __init__(self, base_repo: str):
        self.base_repo = Path(base_repo)
        self.worktree_manager = WorktreeManager(base_repo)
    
    def spawn_worker_worktree(self, worker_id: str) -> str:
        """Create worktree for new worker."""
        branch_name = f"worker/{worker_id}"
        
        # Create branch
        subprocess.run([
            "git", "branch", branch_name, "main"
        ], check=True, cwd=self.base_repo)
        
        # Create worktree
        worktree_path = self.worktree_manager.create_worktree(worker_id, branch_name)
        
        return str(worktree_path)
    
    def commit_worker_changes(self, worker_id: str, message: str) -> str:
        """Commit changes from worker's worktree."""
        worktree_path = self.worktree_manager.worktree_dir / worker_id
        
        # Stage all changes
        subprocess.run(["git", "add", "-A"], check=True, cwd=worktree_path)
        
        # Commit
        result = subprocess.run(
            ["git", "commit", "-m", message],
            check=True,
            cwd=worktree_path,
            capture_output=True,
            text=True
        )
        
        # Get commit SHA
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            cwd=worktree_path,
            capture_output=True,
            text=True
        ).stdout.strip()
        
        return sha
    
    def cleanup_worker_worktree(self, worker_id: str) -> None:
        """Remove worktree after worker terminates."""
        # Delete branch
        subprocess.run([
            "git", "branch", "-D", f"worker/{worker_id}"
        ], check=True, cwd=self.base_repo)
        
        # Remove worktree
        self.worktree_manager.remove_worktree(worker_id)
```

### Integration Worker Merge

```python
class IntegrationWorker:
    def merge_worker_branches(self, worker_ids: List[str]) -> MergeResult:
        """
        Merge branches from multiple workers.
        
        Returns:
            MergeResult with success status and conflicts
        """
        conflicts = []
        
        for worker_id in worker_ids:
            branch_name = f"worker/{worker_id}"
            
            # Try merge
            result = subprocess.run(
                ["git", "merge", "--no-ff", branch_name, "-m", f"Merge worker {worker_id}"],
                cwd=self.base_repo,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                # Merge conflict
                conflicts.append({
                    'worker_id': worker_id,
                    'branch': branch_name,
                    'error': result.stderr
                })
                
                # Abort merge
                subprocess.run(["git", "merge", "--abort"], cwd=self.base_repo)
        
        if conflicts:
            return MergeResult(success=False, conflicts=conflicts)
        
        return MergeResult(success=True, conflicts=[])
```

---

## Best Practices

### 1. Declare File Scope Explicitly

❌ **Bad** (vague):
```json
{
  "files": ["core/executor.py"],
  "file_access": {"core/executor.py": {"mode": "edit"}}
}
```

✅ **Good** (specific):
```json
{
  "files": ["core/executor.py"],
  "file_access": {
    "core/executor.py": {
      "mode": "edit",
      "scope": "function:execute",
      "reason": "Add timeout parameter to execute() method"
    }
  }
}
```

### 2. Minimize File Overlap

**Design tasks to touch different files when possible**:
```json
{
  "steps": [
    {"step_id": "A", "files": ["core/executor.py"]},
    {"step_id": "B", "files": ["core/scheduler.py"]},  // Different file, can parallelize
    {"step_id": "C", "files": ["core/router.py"]}
  ]
}
```

### 3. Use Worktrees for Parallelism

**For parallel tasks editing different files**:
- Each worker gets isolated worktree
- No locking needed
- Merge at integration time

### 4. Use Fine-Grained Scope for Same File

**If multiple tasks MUST edit same file**:
```json
{
  "steps": [
    {
      "step_id": "A",
      "files": ["core/executor.py"],
      "file_access": {"core/executor.py": {"scope": "function:execute"}}
    },
    {
      "step_id": "B",
      "files": ["core/executor.py"],
      "file_access": {"core/executor.py": {"scope": "function:cleanup"}}
    }
  ]
}
```

---

## References

- **DAG Scheduler**: [DAG_SCHEDULER.md](DAG_SCHEDULER.md)
- **Component Contracts**: [COMPONENT_CONTRACTS.md](COMPONENT_CONTRACTS.md)
- **State Machines**: [STATE_MACHINES.md](STATE_MACHINES.md)

---

**Last Updated**: 2025-11-23  
**Next Review**: Before Phase A starts
