---
doc_id: DOC-GUIDE-AGENT-FALLBACK-STRATEGIES-1539
---

# Agent Fallback & Self-Replication Strategies

**Problem**: What happens when primary agent (Aider) fails? How can the orchestrator spawn alternative agents?

**Solution**: Multi-tier fallback with self-replication capabilities

---

## 🎯 Overview

The orchestrator can:
1. **Detect agent failures** (timeout, crash, API limit)
2. **Fallback to alternative agents** (Aider → Copilot CLI → Claude API)
3. **Self-replicate** by spawning new instances of itself as workers
4. **Background execution** for long-running parallel tasks

---

## 🔄 Approach 1: Agent Fallback Chain

### Tier 1: Aider (Primary)
```python
class AgentFallbackChain:
    def __init__(self):
        self.fallback_order = [
            AgentType.AIDER,
            AgentType.COPILOT_CLI,
            AgentType.CLAUDE_API,
            AgentType.SELF_REPLICATE
        ]
    
    async def execute_with_fallback(self, workstream_id, ws_data):
        """Try each agent type in order until success"""
        
        for agent_type in self.fallback_order:
            try:
                logger.info(f"Attempting {workstream_id} with {agent_type}")
                
                if agent_type == AgentType.AIDER:
                    result = await self.execute_aider(workstream_id, ws_data)
                
                elif agent_type == AgentType.COPILOT_CLI:
                    result = await self.execute_copilot_cli(workstream_id, ws_data)
                
                elif agent_type == AgentType.CLAUDE_API:
                    result = await self.execute_claude_api(workstream_id, ws_data)
                
                elif agent_type == AgentType.SELF_REPLICATE:
                    result = await self.execute_self_replicated(workstream_id, ws_data)
                
                if result["success"]:
                    logger.info(f"✅ {workstream_id} succeeded with {agent_type}")
                    return result
                
            except Exception as e:
                logger.warning(f"{agent_type} failed for {workstream_id}: {e}")
                continue  # Try next fallback
        
        # All fallbacks failed
        logger.error(f"❌ All fallbacks failed for {workstream_id}")
        return {"success": False, "error": "All agents failed"}
```

### Tier 2: GitHub Copilot CLI
```python
async def execute_copilot_cli(self, workstream_id, ws_data):
    """Execute using GitHub Copilot CLI"""
    
    files = " ".join(ws_data["files_scope"])
    tasks = "\n".join(ws_data["tasks"])
    
    # Create instruction file for Copilot
    instructions_file = f"instructions/{workstream_id}.md"
    Path(instructions_file).write_text(f"""
# Workstream: {workstream_id}

## Files to modify:
{files}

## Tasks:
{tasks}
    """)
    
    # Execute Copilot CLI in batch mode
    cmd = f"""
    gh copilot suggest --files {files} --prompt-file {instructions_file}
    """
    
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await proc.communicate()
    
    return {
        "success": proc.returncode == 0,
        "exit_code": proc.returncode,
        "agent_type": "copilot_cli",
        "stdout": stdout.decode(),
        "stderr": stderr.decode()
    }
```

### Tier 3: Claude API Direct
```python
import anthropic

async def execute_claude_api(self, workstream_id, ws_data):
    """Execute using Claude API directly"""
    
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    # Read files that need modification
    file_contents = {}
    for file_path in ws_data["files_scope"]:
        file_contents[file_path] = Path(file_path).read_text()
    
    # Build prompt
    prompt = f"""
# Workstream: {workstream_id}

## Context:
You are working on a code refactoring project with the following tasks:

{chr(10).join(f"- {task}" for task in ws_data["tasks"])}

## Current file contents:
{chr(10).join(f"### {path}\n```\n{content}\n```" for path, content in file_contents.items())}

## Instructions:
1. Implement the requested changes
2. Output ONLY the modified files in this format:
   FILE: path/to/file.py
   CONTENT:
   [file content here]
   END_FILE

3. Ensure all changes are complete and tested
"""
    
    # Call Claude API
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Parse response and apply changes
    response_text = message.content[0].text
    modified_files = parse_claude_file_changes(response_text)
    
    # Apply changes to disk
    for file_path, new_content in modified_files.items():
        Path(file_path).write_text(new_content)
        logger.info(f"Updated {file_path}")
    
    return {
        "success": True,
        "agent_type": "claude_api",
        "modified_files": list(modified_files.keys())
    }

def parse_claude_file_changes(response: str) -> Dict[str, str]:
    """Parse Claude's response to extract file changes"""
    import re
    
    file_pattern = r"FILE:\s*(.+?)\s*CONTENT:\s*(.+?)\s*END_FILE"
    matches = re.findall(file_pattern, response, re.DOTALL)
    
    return {path.strip(): content.strip() for path, content in matches}
```

---

## 🔁 Approach 2: Self-Replication (Recursive Agent Spawning)

The orchestrator spawns **copies of itself** as worker agents for each workstream.

### Architecture
```
Main Orchestrator (Parent)
    ├── Worker 1 (Child Process) → Workstream WS-03
    ├── Worker 2 (Child Process) → Workstream WS-12
    └── Worker 3 (Child Process) → Workstream WS-22
```

### Implementation
```python
class SelfReplicatingOrchestrator:
    """Orchestrator that spawns itself as worker agents"""
    
    async def execute_as_worker_pool(self):
        """Spawn worker processes for each workstream"""
        
        ready_workstreams = self.graph.get_ready_workstreams(set())
        
        # Spawn worker processes
        worker_tasks = []
        for ws_id in ready_workstreams[:3]:  # Max 3 parallel workers
            task = self.spawn_worker_agent(ws_id)
            worker_tasks.append(task)
        
        # Wait for all workers to complete
        results = await asyncio.gather(*worker_tasks)
        
        for result in results:
            logger.info(f"Worker completed: {result}")
    
    async def spawn_worker_agent(self, workstream_id: str):
        """Spawn a new instance of this script as a worker"""
        
        # Self-replicate: Run same script in worker mode
        cmd = f"""
        python multi_agent_orchestrator.py \\
            --mode worker \\
            --workstream {workstream_id} \\
            --worktree .worktrees/worker-{workstream_id}
        """
        
        logger.info(f"🔄 Spawning worker for {workstream_id}")
        
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await proc.communicate()
        
        return {
            "workstream_id": workstream_id,
            "success": proc.returncode == 0,
            "exit_code": proc.returncode
        }
    
    def run_as_worker(self, workstream_id: str, worktree_path: Path):
        """Execute as a worker agent (called in child process)"""
        
        logger.info(f"🤖 Worker started for {workstream_id} in {worktree_path}")
        
        # Load workstream data
        ws_file = Path(f"workstreams/{workstream_id}.json")
        ws_data = json.loads(ws_file.read_text())
        
        # Execute workstream using any available tool
        # Try Aider first, fallback to others
        try:
            result = self._execute_with_aider(ws_data, worktree_path)
        except Exception as e:
            logger.warning(f"Aider failed: {e}, trying Copilot CLI")
            result = self._execute_with_copilot(ws_data, worktree_path)
        
        # Report result back to parent
        logger.info(f"✅ Worker completed {workstream_id}")
        return result

# Modified main entry point to support worker mode
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["orchestrator", "worker"], default="orchestrator")
    parser.add_argument("--workstream", help="Workstream ID (worker mode)")
    parser.add_argument("--worktree", help="Worktree path (worker mode)")
    
    args = parser.parse_args()
    
    if args.mode == "orchestrator":
        # Run as main orchestrator
        asyncio.run(main())
    else:
        # Run as worker agent
        orchestrator = SelfReplicatingOrchestrator(...)
        orchestrator.run_as_worker(args.workstream, Path(args.worktree))
```

---

## 🚀 Approach 3: Background Task Execution (Detached Processes)

Run workstreams as **completely independent background tasks** that persist after parent exits.

### Implementation
```python
import subprocess

class BackgroundTaskManager:
    """Manage background execution of workstreams"""
    
    def __init__(self, task_db: Path):
        self.task_db = task_db
        self.tasks_dir = Path("background_tasks")
        self.tasks_dir.mkdir(exist_ok=True)
    
    def spawn_background_workstream(self, workstream_id: str, ws_data: Dict):
        """Spawn workstream as detached background process"""
        
        # Create execution script
        script_path = self.tasks_dir / f"{workstream_id}_runner.py"
        script_path.write_text(f"""
import sys
import json
from pathlib import Path
from datetime import datetime

# Workstream data
ws_id = "{workstream_id}"
ws_data = {json.dumps(ws_data, indent=2)}

# Log file
log_file = Path("logs/bg_{workstream_id}.log")
log_file.parent.mkdir(exist_ok=True)

with open(log_file, "a") as f:
    f.write(f"{{datetime.now()}} - Starting {{ws_id}}\\n")
    
    try:
        # Execute using Aider
        import subprocess
        files = " ".join(ws_data["files_scope"])
        tasks = "\\n".join(ws_data["tasks"])
        
        cmd = f'aider {{files}} --message "{{tasks}}" --yes --auto-commits'
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        f.write(f"{{datetime.now()}} - Exit code: {{result.returncode}}\\n")
        f.write(result.stdout)
        
        # Mark as complete in database
        import sqlite3
        conn = sqlite3.connect(".state/orchestration.db")
        conn.execute(
            "UPDATE workstream_status SET status='completed' WHERE workstream_id=?",
            (ws_id,)
        )
        conn.commit()
        
        sys.exit(0 if result.returncode == 0 else 1)
        
    except Exception as e:
        f.write(f"{{datetime.now()}} - ERROR: {{e}}\\n")
        sys.exit(1)
""")
        
        # Spawn as detached background process (survives parent exit)
        if os.name == 'nt':  # Windows
            subprocess.Popen(
                ["python", str(script_path)],
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:  # Unix-like
            subprocess.Popen(
                ["nohup", "python", str(script_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setpgrp  # Detach from parent process group
            )
        
        logger.info(f"🚀 Spawned background task for {workstream_id}")
    
    def check_background_status(self):
        """Poll database to check background task status"""
        conn = sqlite3.connect(self.task_db)
        cursor = conn.execute("""
            SELECT workstream_id, status, completed_at 
            FROM workstream_status 
            WHERE status IN ('running', 'completed')
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        return {
            "running": [r[0] for r in results if r[1] == "running"],
            "completed": [r[0] for r in results if r[1] == "completed"]
        }
```

---

## 📊 Comparison Matrix

| Approach | Isolation | Complexity | Resilience | Best For |
|----------|-----------|------------|------------|----------|
| **Fallback Chain** | Medium | Low | High | Single orchestrator with tool diversity |
| **Self-Replication** | High | Medium | Very High | Massive parallelism (10+ workstreams) |
| **Background Tasks** | Very High | High | Extreme | Long-running tasks, survives crashes |

---

## 🎯 Recommended Hybrid Approach

Combine all three for maximum resilience:

```python
class HybridOrchestrator:
    """Best-of-all-worlds approach"""
    
    async def execute_workstream_with_fallback(self, ws_id, ws_data):
        """
        1. Try Aider in worktree (primary)
        2. If fails → Try Copilot CLI (fallback)
        3. If fails → Spawn self-replicated worker with Claude API
        4. If long-running → Detach as background process
        """
        
        # Attempt 1: Aider in worktree
        try:
            result = await self.execute_aider_in_worktree(ws_id, ws_data)
            if result["success"]:
                return result
        except Exception as e:
            logger.warning(f"Aider failed: {e}")
        
        # Attempt 2: Copilot CLI fallback
        try:
            result = await self.execute_copilot_cli(ws_id, ws_data)
            if result["success"]:
                return result
        except Exception as e:
            logger.warning(f"Copilot CLI failed: {e}")
        
        # Attempt 3: Self-replicate with Claude API
        logger.info(f"Spawning self-replicated worker for {ws_id}")
        result = await self.spawn_worker_with_claude(ws_id, ws_data)
        
        if result["success"]:
            return result
        
        # Attempt 4: Last resort - background detached process
        logger.warning(f"Detaching {ws_id} as background task")
        self.spawn_background_task(ws_id, ws_data)
        
        return {"success": True, "mode": "background"}
```

---

## ✅ Implementation Checklist

- [ ] Add `AgentType.COPILOT_CLI` to enum
- [ ] Add `AgentType.CLAUDE_API` to enum
- [ ] Implement `execute_copilot_cli()` method
- [ ] Implement `execute_claude_api()` method
- [ ] Add `--mode worker` argument parsing
- [ ] Implement `spawn_worker_agent()` method
- [ ] Implement `spawn_background_task()` method
- [ ] Add fallback chain logic to orchestrator
- [ ] Test each fallback tier independently
- [ ] Test hybrid approach end-to-end

---

## 🔧 Configuration Example

```yaml
# .orchestrator_config.yaml
agent_fallback:
  enabled: true
  timeout_seconds: 300
  
  tiers:
    - name: aider
      priority: 1
      timeout: 300
    
    - name: copilot_cli
      priority: 2
      timeout: 180
    
    - name: claude_api
      priority: 3
      timeout: 120
      api_key_env: ANTHROPIC_API_KEY
    
    - name: self_replicate
      priority: 4
      max_workers: 10
  
  background_mode:
    enabled: true
    max_concurrent: 5
    poll_interval_seconds: 30
```

---

## 🎬 Next Steps

1. **Immediate**: Implement Tier 2 (Copilot CLI fallback)
2. **Short-term**: Add self-replication for massive parallelism
3. **Long-term**: Background task manager for 24/7 operation

**This ensures zero single points of failure.**
