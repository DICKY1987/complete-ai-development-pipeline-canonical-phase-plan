---
doc_id: DOC-GUIDE-ONE-TOUCH-SOLUTION-PLAN-1529
---

# One-Touch Multi-Agent Solution - Complete Implementation Plan

## Executive Summary

To achieve **true one-touch execution** of 39 workstreams with 3 agents in 1-2 weeks, we need:

1. ✅ **Multi-agent orchestrator** (already created)
2. ✅ **Git worktrees** (already used in your system)  
3. ❌ **Missing**: Worktree automation + agent isolation
4. ❌ **Missing**: Pre-flight validation
5. ❌ **Missing**: One-command launcher

---

## Current State Analysis

### ✅ **What You Have**

1. **Orchestrator** (`scripts/multi_agent_orchestrator.py`)
   - Dependency graph management
   - Agent pool with async execution
   - SQLite state tracking

2. **Workstream Definitions** (`workstreams/*.json`)
   - 39 workstreams with dependencies
   - Task lists and acceptance tests

3. **Worktree Infrastructure** (Evidence from grep)
   - `adr/0008-database-location-worktree.md`
   - `scripts/create_migration_worktrees.ps1`
   - `scripts/create_docid_worktrees.ps1`
   - `scripts/cleanup_worktrees.ps1`
   - `pm/rules/worktree-operations.md`

### ❌ **What's Missing for One-Touch**

1. **Automatic worktree creation per agent**
2. **Agent isolation** (each agent in own worktree)
3. **Pre-flight validation** (check dependencies, git status)
4. **Single launcher script** (one command to rule them all)
5. **Post-execution cleanup** (auto-merge or cleanup worktrees)

---

## Why Git Worktrees Are CRITICAL

### **Problem Without Worktrees**

```
3 agents working in same directory:
├─ Agent 1: Editing core/state/db.py for WS-15
├─ Agent 2: Editing core/state/db.py for WS-03  ❌ CONFLICT!
└─ Agent 3: Editing tests/test_db.py for WS-19
```

**Result**: Git conflicts, failed commits, agents stepping on each other

### **Solution With Worktrees**

```
main/
├─ .git/
└─ workstreams/

.worktrees/
├─ agent-1-ws-22/     # Isolated workspace for Agent 1
│  └─ core/
├─ agent-2-ws-03/     # Isolated workspace for Agent 2
│  └─ core/
└─ agent-3-ws-12/     # Isolated workspace for Agent 3
   └─ error/
```

**Result**: Zero conflicts, parallel execution, clean merges

---

## Complete One-Touch Architecture

```
┌──────────────────────────────────────────────────────┐
│  ONE-TOUCH LAUNCHER (run_multi_agent_refactor.ps1)  │
│  - Validates prerequisites                           │
│  - Creates 3 agent worktrees                        │
│  - Launches orchestrator                            │
│  - Monitors execution                               │
│  - Cleans up on completion                          │
└──────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼─────┐   ┌────▼─────┐   ┌────▼─────┐
    │ Worktree │   │ Worktree │   │ Worktree │
    │ agent-1  │   │ agent-2  │   │ agent-3  │
    │ (branch: │   │ (branch: │   │ (branch: │
    │  ws-22)  │   │  ws-03)  │   │  ws-12)  │
    └────┬─────┘   └────┬─────┘   └────┬─────┘
         │               │               │
         │               │               │
    ┌────▼─────┐   ┌────▼─────┐   ┌────▼─────┐
    │ Agent 1  │   │ Agent 2  │   │ Agent 3  │
    │ (aider)  │   │ (aider)  │   │ (aider)  │
    └────┬─────┘   └────┬─────┘   └────┬─────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
                ┌────────▼────────┐
                │ Orchestrator    │
                │ (manages tasks) │
                └─────────────────┘
```

---

## Implementation: Missing Components

### **Component 1: Worktree Manager**

```python
# scripts/worktree_manager.py
import subprocess
from pathlib import Path
from typing import List, Dict

class WorktreeManager:
    """Manage git worktrees for agent isolation"""
    
    def __init__(self, base_repo: Path, worktree_root: Path):
        self.base_repo = base_repo
        self.worktree_root = worktree_root
        self.worktree_root.mkdir(parents=True, exist_ok=True)
    
    def create_agent_worktree(
        self, 
        agent_id: str, 
        branch_name: str,
        workstream_id: str
    ) -> Path:
        """Create isolated worktree for agent"""
        
        worktree_path = self.worktree_root / f"{agent_id}-{workstream_id}"
        
        # Create branch for this workstream
        subprocess.run(
            ["git", "checkout", "-b", branch_name, "main"],
            cwd=self.base_repo,
            check=True
        )
        
        # Create worktree
        subprocess.run(
            ["git", "worktree", "add", str(worktree_path), branch_name],
            cwd=self.base_repo,
            check=True
        )
        
        return worktree_path
    
    def cleanup_agent_worktree(self, agent_id: str, workstream_id: str):
        """Remove worktree after completion"""
        
        worktree_path = self.worktree_root / f"{agent_id}-{workstream_id}"
        
        subprocess.run(
            ["git", "worktree", "remove", str(worktree_path)],
            cwd=self.base_repo,
            check=True
        )
    
    def merge_worktree_changes(
        self, 
        branch_name: str, 
        target_branch: str = "main"
    ):
        """Merge worktree changes back to main"""
        
        subprocess.run(
            ["git", "checkout", target_branch],
            cwd=self.base_repo,
            check=True
        )
        
        subprocess.run(
            ["git", "merge", "--no-ff", branch_name],
            cwd=self.base_repo,
            check=True
        )
    
    def list_worktrees(self) -> List[Dict]:
        """List all active worktrees"""
        
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=self.base_repo,
            capture_output=True,
            text=True
        )
        
        # Parse output
        worktrees = []
        current = {}
        for line in result.stdout.split("\n"):
            if line.startswith("worktree "):
                if current:
                    worktrees.append(current)
                current = {"path": line.split()[1]}
            elif line.startswith("branch "):
                current["branch"] = line.split()[1]
        
        if current:
            worktrees.append(current)
        
        return worktrees
```

---

### **Component 2: Enhanced Orchestrator with Worktrees**

```python
# Additions to scripts/multi_agent_orchestrator.py

from worktree_manager import WorktreeManager

class MultiAgentOrchestrator:
    
    def __init__(self, ...):
        # ... existing init code ...
        self.worktree_manager = WorktreeManager(
            base_repo=Path.cwd(),
            worktree_root=Path(".worktrees")
        )
    
    async def _execute_workstream_async(self, agent, ws_id, ws_data):
        """Execute workstream in isolated worktree"""
        
        # Create unique branch for this workstream
        branch_name = f"ws/{ws_id}/{agent.id}"
        
        # Create worktree for this agent
        worktree_path = self.worktree_manager.create_agent_worktree(
            agent_id=agent.id,
            branch_name=branch_name,
            workstream_id=ws_id
        )
        
        logger.info(f"Created worktree: {worktree_path} for {ws_id}")
        
        # Execute workstream in worktree
        result = await self.agents.execute_workstream_in_worktree(
            agent=agent,
            workstream_id=ws_id,
            workstream_data=ws_data,
            worktree_path=worktree_path
        )
        
        # On success, merge back to main
        if result["success"]:
            try:
                self.worktree_manager.merge_worktree_changes(
                    branch_name=branch_name,
                    target_branch="main"
                )
                logger.info(f"Merged {branch_name} to main")
            except Exception as e:
                logger.error(f"Merge failed for {branch_name}: {e}")
                result["success"] = False
        
        # Cleanup worktree
        self.worktree_manager.cleanup_agent_worktree(agent.id, ws_id)
        
        return result


class AgentPool:
    
    async def execute_workstream_in_worktree(
        self,
        agent: Agent,
        workstream_id: str,
        workstream_data: Dict,
        worktree_path: Path
    ) -> Dict:
        """Execute workstream in isolated worktree"""
        
        tool = workstream_data.get("tool", "aider")
        
        if tool == "aider":
            cmd = self._build_aider_command_with_worktree(
                workstream_id, 
                workstream_data, 
                worktree_path
            )
        # ... other tools ...
        
        # Execute in worktree directory
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=worktree_path  # ← Execute in worktree!
        )
        
        stdout, stderr = await proc.communicate()
        
        return {
            "workstream_id": workstream_id,
            "agent_id": agent.id,
            "exit_code": proc.returncode,
            "success": proc.returncode == 0,
            "worktree": str(worktree_path)
        }
    
    def _build_aider_command_with_worktree(
        self, 
        ws_id: str, 
        ws_data: Dict,
        worktree_path: Path
    ) -> str:
        """Build aider command to run in worktree"""
        
        files = " ".join(ws_data.get("files_scope", []))
        tasks = ws_data.get("tasks", [])
        task_text = "\\n".join(tasks)
        
        return f"""
        cd {worktree_path} && aider {files} \\
          --message "{task_text}" \\
          --yes \\
          --auto-commits \\
          --edit-format whole
        """
```

---

### **Component 3: Pre-Flight Validator**

```python
# scripts/preflight_validator.py
import subprocess
import sys
from pathlib import Path

class PreFlightValidator:
    """Validate prerequisites before multi-agent execution"""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.errors = []
        self.warnings = []
    
    def validate_all(self) -> bool:
        """Run all validations"""
        
        print("🔍 Running pre-flight validation...")
        
        self.check_git_clean()
        self.check_dependencies()
        self.check_workstreams()
        self.check_disk_space()
        
        self.print_results()
        
        return len(self.errors) == 0
    
    def check_git_clean(self):
        """Ensure git working tree is clean"""
        
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.repo_root,
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            self.errors.append(
                "Git working tree is not clean. Commit or stash changes first."
            )
        else:
            print("✅ Git working tree is clean")
    
    def check_dependencies(self):
        """Check required dependencies"""
        
        # Check Python packages
        try:
            import networkx
            print("✅ networkx installed")
        except ImportError:
            self.errors.append("networkx not installed. Run: pip install networkx")
        
        # Check git worktree support
        result = subprocess.run(
            ["git", "worktree", "list"],
            cwd=self.repo_root,
            capture_output=True
        )
        
        if result.returncode == 0:
            print("✅ Git worktree support available")
        else:
            self.errors.append("Git worktree not supported. Upgrade git to 2.5+")
        
        # Check aider
        result = subprocess.run(
            ["which", "aider"],
            capture_output=True
        )
        
        if result.returncode == 0:
            print("✅ aider found")
        else:
            self.warnings.append("aider not found in PATH")
    
    def check_workstreams(self):
        """Check workstream files exist"""
        
        ws_dir = self.repo_root / "workstreams"
        if not ws_dir.exists():
            self.errors.append("workstreams/ directory not found")
            return
        
        ws_files = list(ws_dir.glob("ws-*.json"))
        if len(ws_files) < 10:
            self.warnings.append(f"Only {len(ws_files)} workstream files found")
        else:
            print(f"✅ Found {len(ws_files)} workstream files")
    
    def check_disk_space(self):
        """Check available disk space"""
        
        import shutil
        stats = shutil.disk_usage(self.repo_root)
        
        free_gb = stats.free / (1024**3)
        
        if free_gb < 5:
            self.errors.append(f"Low disk space: {free_gb:.1f} GB free")
        elif free_gb < 10:
            self.warnings.append(f"Disk space: {free_gb:.1f} GB free (recommended: 10+ GB)")
        else:
            print(f"✅ Disk space: {free_gb:.1f} GB free")
    
    def print_results(self):
        """Print validation results"""
        
        print("\n" + "="*60)
        
        if self.warnings:
            print("⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  - {error}")
            print("\nFix errors before proceeding.")
        else:
            print("✅ All pre-flight checks passed!")
        
        print("="*60 + "\n")


if __name__ == "__main__":
    validator = PreFlightValidator(Path.cwd())
    success = validator.validate_all()
    sys.exit(0 if success else 1)
```

---

### **Component 4: One-Touch Launcher (PowerShell)**

```powershell
# scripts/run_multi_agent_refactor.ps1

<#
.SYNOPSIS
    One-touch launcher for multi-agent workstream execution

.DESCRIPTION
    This script automates the complete multi-agent refactor:
    1. Pre-flight validation
    2. Worktree setup
    3. Orchestrator launch
    4. Progress monitoring
    5. Cleanup

.PARAMETER DryRun
    Run in dry-run mode (no actual changes)

.PARAMETER Agents
    Number of agents to use (default: 3)

.EXAMPLE
    .\run_multi_agent_refactor.ps1

.EXAMPLE
    .\run_multi_agent_refactor.ps1 -DryRun -Agents 1
#>

param(
    [switch]$DryRun,
    [int]$Agents = 3
)

$ErrorActionPreference = "Stop"

Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Multi-Agent Workstream Orchestrator - One-Touch Launch ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Step 1: Pre-Flight Validation
Write-Host "Step 1/5: Pre-Flight Validation" -ForegroundColor Yellow
Write-Host "─────────────────────────────────" -ForegroundColor Yellow

python scripts/preflight_validator.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Pre-flight validation failed. Fix errors and try again." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 2: Create Logs & State Directories
Write-Host "Step 2/5: Setup Directories" -ForegroundColor Yellow
Write-Host "─────────────────────────────" -ForegroundColor Yellow

$directories = @("logs", "reports", ".state", ".worktrees")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "✅ Created $dir/" -ForegroundColor Green
    } else {
        Write-Host "✓ $dir/ exists" -ForegroundColor Gray
    }
}

Write-Host ""

# Step 3: Clean Old Worktrees
Write-Host "Step 3/5: Cleanup Old Worktrees" -ForegroundColor Yellow
Write-Host "──────────────────────────────────" -ForegroundColor Yellow

$existingWorktrees = git worktree list --porcelain | Select-String "^worktree" | ForEach-Object { $_.ToString().Split()[1] }
$baseRepo = git rev-parse --show-toplevel

foreach ($wt in $existingWorktrees) {
    if ($wt -ne $baseRepo -and (Test-Path $wt)) {
        Write-Host "Removing old worktree: $wt" -ForegroundColor Gray
        git worktree remove $wt --force 2>$null
    }
}

Write-Host "✅ Old worktrees cleaned" -ForegroundColor Green
Write-Host ""

# Step 4: Launch Orchestrator
Write-Host "Step 4/5: Launch Orchestrator" -ForegroundColor Yellow
Write-Host "────────────────────────────────" -ForegroundColor Yellow

$orchestratorArgs = @()
if ($DryRun) {
    $orchestratorArgs += "--dry-run"
}
$orchestratorArgs += "--agents", $Agents

Write-Host "Starting orchestrator with $Agents agents..." -ForegroundColor Cyan
Write-Host ""

# Run orchestrator in foreground
python scripts/multi_agent_orchestrator.py @orchestratorArgs

$orchestratorExit = $LASTEXITCODE

Write-Host ""

# Step 5: Post-Execution Summary
Write-Host "Step 5/5: Post-Execution Summary" -ForegroundColor Yellow
Write-Host "───────────────────────────────────" -ForegroundColor Yellow

if ($orchestratorExit -eq 0) {
    Write-Host "✅ Multi-agent execution completed successfully!" -ForegroundColor Green
    
    # Check results
    if (Test-Path "reports/multi_agent_execution_report.md") {
        Write-Host ""
        Write-Host "📊 Final Report:" -ForegroundColor Cyan
        Get-Content "reports/multi_agent_execution_report.md" | Select-Object -First 20
        Write-Host ""
        Write-Host "Full report: reports/multi_agent_execution_report.md" -ForegroundColor Gray
    }
    
    # Show database stats
    $completedCount = & sqlite3 .state/orchestration.db "SELECT COUNT(*) FROM workstream_status WHERE status='completed'" 2>$null
    $totalCount = & sqlite3 .state/orchestration.db "SELECT COUNT(*) FROM workstream_status" 2>$null
    
    if ($completedCount -and $totalCount) {
        Write-Host ""
        Write-Host "Progress: $completedCount / $totalCount workstreams completed" -ForegroundColor Cyan
    }
    
} else {
    Write-Host "❌ Orchestrator exited with errors (code: $orchestratorExit)" -ForegroundColor Red
    Write-Host "Check logs/orchestrator.log for details" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    Execution Complete                    ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

exit $orchestratorExit
```

---

## One-Touch Usage

### **Single Command Execution**

```powershell
# Full automated refactor with 3 agents
.\scripts\run_multi_agent_refactor.ps1

# Dry run with 1 agent
.\scripts\run_multi_agent_refactor.ps1 -DryRun -Agents 1

# Production run with 6 agents
.\scripts\run_multi_agent_refactor.ps1 -Agents 6
```

**That's it!** The script handles:
- ✅ Pre-flight checks
- ✅ Directory setup
- ✅ Worktree creation per agent
- ✅ Orchestrator launch
- ✅ Progress monitoring
- ✅ Cleanup
- ✅ Final report

---

## File Summary

### **New Files to Create**

1. **`scripts/worktree_manager.py`** (Component 1)
   - Worktree creation/cleanup
   - Merge management

2. **`scripts/preflight_validator.py`** (Component 3)
   - Git status check
   - Dependency validation
   - Disk space check

3. **`scripts/run_multi_agent_refactor.ps1`** (Component 4)
   - One-touch launcher
   - End-to-end automation

### **Files to Modify**

1. **`scripts/multi_agent_orchestrator.py`** (Component 2)
   - Add `WorktreeManager` integration
   - Update `_execute_workstream_async()` to use worktrees
   - Update `AgentPool.execute_workstream()` to run in worktree

---

## Benefits of Complete Solution

### **Before (Current State)**

```bash
# Manual steps required:
1. Check git status
2. Install dependencies
3. Create directories
4. Configure agents
5. Run orchestrator
6. Monitor manually
7. Handle conflicts
8. Cleanup worktrees
```

**Time**: 30-60 minutes setup + 1-2 weeks execution

### **After (One-Touch)**

```powershell
.\scripts\run_multi_agent_refactor.ps1
```

**Time**: 2 minutes setup + 1-2 weeks automated execution

**Speedup**: 15-30x faster setup, zero manual intervention

---

## Next Steps

1. ✅ Create `worktree_manager.py`
2. ✅ Create `preflight_validator.py`
3. ✅ Create `run_multi_agent_refactor.ps1`
4. ✅ Update `multi_agent_orchestrator.py` with worktree support
5. ✅ Test with 1 agent, 1 workstream
6. ✅ Scale to 3 agents, full workstream set

**Ready to implement?**
