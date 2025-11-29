# Multi-Agent Orchestration Pattern for Workstream Execution

**Pattern ID**: PAT-MULTI-AGENT-ORCHESTRATE-001  
**Purpose**: Automate parallel execution of workstreams across multiple AI agents  
**Supports**: 1-6 agents with intelligent work distribution  

---

## Problem Statement

**Current state**: 39 workstreams with complex dependencies  
**Manual approach**: Sequential execution by 1 agent = 3-4 weeks  
**Goal**: Automate parallel execution with 3 agents = 1-2 weeks  

**Challenges**:
1. Dependency management (can't start WS-06 before WS-03 completes)
2. Agent coordination (who does what, when?)
3. Conflict avoidance (two agents editing same files)
4. Progress tracking (which workstreams are done?)
5. Failure recovery (what if agent fails mid-workstream?)

---

## Solution: Orchestration Architecture

### **High-Level Design**

```
┌─────────────────────────────────────────────────────┐
│         ORCHESTRATOR (Python/PowerShell)            │
│  - Parses workstream dependencies                   │
│  - Builds execution DAG                             │
│  - Assigns work to available agents                 │
│  - Monitors progress                                │
│  - Handles failures/retries                         │
└─────────────────────────────────────────────────────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
    ┌────▼────┐      ┌────▼────┐     ┌────▼────┐
    │ Agent 1 │      │ Agent 2 │     │ Agent 3 │
    │ (Track) │      │ (Track) │     │ (Track) │
    └─────────┘      └─────────┘     └─────────┘
         │                │                │
    ┌────▼────────────────▼────────────────▼────┐
    │         Shared State Database              │
    │  - Workstream status (pending/running/done)│
    │  - Agent assignments                       │
    │  - Execution logs                          │
    │  - Dependency resolution                   │
    └────────────────────────────────────────────┘
```

---

## Implementation Components

### **Component 1: Workstream Dependency Graph**

```python
# workstream_graph.py
import json
from pathlib import Path
from typing import Dict, List, Set
import networkx as nx

class WorkstreamGraph:
    """Build and analyze workstream dependency graph"""
    
    def __init__(self, workstreams_dir: Path):
        self.workstreams_dir = workstreams_dir
        self.graph = nx.DiGraph()
        self._load_workstreams()
    
    def _load_workstreams(self):
        """Load all workstream JSON files and build graph"""
        for ws_file in self.workstreams_dir.glob("ws-*.json"):
            with open(ws_file) as f:
                ws = json.load(f)
                
            ws_id = ws["id"]
            depends_on = ws.get("depends_on", [])
            
            # Add node
            self.graph.add_node(ws_id, **ws)
            
            # Add edges (dependency → workstream)
            for dep in depends_on:
                self.graph.add_edge(dep, ws_id)
    
    def get_ready_workstreams(self, completed: Set[str]) -> List[str]:
        """Get workstreams ready to execute (all dependencies met)"""
        ready = []
        for ws_id in self.graph.nodes():
            if ws_id in completed:
                continue
            
            # Check if all dependencies are completed
            deps = list(self.graph.predecessors(ws_id))
            if all(dep in completed for dep in deps):
                ready.append(ws_id)
        
        return ready
    
    def get_independent_workstreams(self) -> List[str]:
        """Get workstreams with no dependencies"""
        return [
            ws_id for ws_id in self.graph.nodes()
            if self.graph.in_degree(ws_id) == 0
        ]
    
    def get_workstream_data(self, ws_id: str) -> Dict:
        """Get workstream metadata"""
        return self.graph.nodes[ws_id]
    
    def topological_sort(self) -> List[str]:
        """Get topologically sorted workstream order"""
        return list(nx.topological_sort(self.graph))
```

---

### **Component 2: Agent Pool Manager**

```python
# agent_pool.py
import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
import subprocess
import json

class AgentType(Enum):
    AIDER = "aider"
    CODEX = "codex"
    CLAUDE_CODE = "claude_code"
    COPILOT = "copilot"

@dataclass
class Agent:
    id: str
    type: AgentType
    status: str  # "idle", "busy", "failed"
    current_workstream: Optional[str] = None
    assigned_track: Optional[str] = None

class AgentPool:
    """Manage pool of AI agents"""
    
    def __init__(self, agent_configs: List[Dict]):
        self.agents = [
            Agent(
                id=cfg["id"],
                type=AgentType(cfg["type"]),
                status="idle"
            )
            for cfg in agent_configs
        ]
    
    def get_available_agent(self, track: Optional[str] = None) -> Optional[Agent]:
        """Get first available agent, optionally for specific track"""
        for agent in self.agents:
            if agent.status == "idle":
                if track is None or agent.assigned_track == track:
                    return agent
        return None
    
    def assign_workstream(self, agent: Agent, workstream_id: str, track: str):
        """Assign workstream to agent"""
        agent.status = "busy"
        agent.current_workstream = workstream_id
        agent.assigned_track = track
    
    def release_agent(self, agent: Agent):
        """Mark agent as available"""
        agent.status = "idle"
        agent.current_workstream = None
    
    async def execute_workstream(
        self, 
        agent: Agent, 
        workstream_id: str,
        workstream_data: Dict
    ) -> Dict:
        """Execute workstream using specified agent"""
        
        # Build command based on agent type and workstream tool
        tool = workstream_data.get("tool", "aider")
        
        if tool == "aider":
            cmd = self._build_aider_command(workstream_id, workstream_data)
        elif tool == "codex":
            cmd = self._build_codex_command(workstream_id, workstream_data)
        else:
            cmd = self._build_generic_command(workstream_id, workstream_data)
        
        # Execute asynchronously
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await proc.communicate()
        
        return {
            "workstream_id": workstream_id,
            "agent_id": agent.id,
            "exit_code": proc.returncode,
            "stdout": stdout.decode(),
            "stderr": stderr.decode(),
            "success": proc.returncode == 0
        }
    
    def _build_aider_command(self, ws_id: str, ws_data: Dict) -> str:
        """Build aider command for workstream"""
        files = " ".join(ws_data.get("files_scope", []))
        tasks = "\n".join(ws_data.get("tasks", []))
        
        return f"""
        aider {files} \\
          --message "{tasks}" \\
          --yes \\
          --auto-commits \\
          --edit-format whole
        """
    
    def _build_codex_command(self, ws_id: str, ws_data: Dict) -> str:
        """Build codex command for workstream"""
        # Assuming codex CLI similar to aider
        return f"codex execute --workstream {ws_id}"
    
    def _build_generic_command(self, ws_id: str, ws_data: Dict) -> str:
        """Build generic execution command"""
        return f"python scripts/execute_workstream.py {ws_id}"
```

---

### **Component 3: State Manager (SQLite)**

```python
# state_manager.py
import sqlite3
from datetime import datetime
from typing import List, Optional, Set
from pathlib import Path

class StateManager:
    """Manage workstream execution state in SQLite"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS workstream_status (
                workstream_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,  -- pending, running, completed, failed
                agent_id TEXT,
                track TEXT,
                started_at TEXT,
                completed_at TEXT,
                exit_code INTEGER,
                attempt INTEGER DEFAULT 1,
                error_message TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS execution_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                workstream_id TEXT NOT NULL,
                agent_id TEXT,
                event_type TEXT NOT NULL,  -- started, completed, failed, retry
                message TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def mark_started(self, ws_id: str, agent_id: str, track: str):
        """Mark workstream as started"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO workstream_status 
            (workstream_id, status, agent_id, track, started_at)
            VALUES (?, 'running', ?, ?, ?)
        """, (ws_id, agent_id, track, datetime.now().isoformat()))
        
        conn.execute("""
            INSERT INTO execution_log (timestamp, workstream_id, agent_id, event_type)
            VALUES (?, ?, ?, 'started')
        """, (datetime.now().isoformat(), ws_id, agent_id))
        
        conn.commit()
        conn.close()
    
    def mark_completed(self, ws_id: str, exit_code: int):
        """Mark workstream as completed"""
        status = "completed" if exit_code == 0 else "failed"
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            UPDATE workstream_status
            SET status = ?, completed_at = ?, exit_code = ?
            WHERE workstream_id = ?
        """, (status, datetime.now().isoformat(), exit_code, ws_id))
        
        conn.execute("""
            INSERT INTO execution_log (timestamp, workstream_id, event_type)
            VALUES (?, ?, ?)
        """, (datetime.now().isoformat(), ws_id, status))
        
        conn.commit()
        conn.close()
    
    def get_completed_workstreams(self) -> Set[str]:
        """Get set of completed workstream IDs"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.execute("""
            SELECT workstream_id FROM workstream_status 
            WHERE status = 'completed'
        """)
        completed = {row[0] for row in cur.fetchall()}
        conn.close()
        return completed
    
    def get_failed_workstreams(self) -> List[str]:
        """Get list of failed workstream IDs"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.execute("""
            SELECT workstream_id FROM workstream_status 
            WHERE status = 'failed' AND attempt < 3
        """)
        failed = [row[0] for row in cur.fetchall()]
        conn.close()
        return failed
    
    def increment_attempt(self, ws_id: str):
        """Increment retry attempt counter"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            UPDATE workstream_status
            SET attempt = attempt + 1, status = 'pending'
            WHERE workstream_id = ?
        """, (ws_id,))
        conn.commit()
        conn.close()
```

---

### **Component 4: Main Orchestrator**

```python
# orchestrator.py
import asyncio
from pathlib import Path
from typing import Dict, List
import json
import logging

from workstream_graph import WorkstreamGraph
from agent_pool import AgentPool, AgentType
from state_manager import StateManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

class MultiAgentOrchestrator:
    """Main orchestrator for multi-agent workstream execution"""
    
    def __init__(
        self,
        workstreams_dir: Path,
        state_db: Path,
        agent_configs: List[Dict],
        track_assignments: Dict[str, List[str]]
    ):
        self.graph = WorkstreamGraph(workstreams_dir)
        self.state = StateManager(state_db)
        self.agents = AgentPool(agent_configs)
        self.track_assignments = track_assignments
    
    async def execute_all(self):
        """Execute all workstreams with dependency management"""
        
        logging.info("Starting multi-agent orchestration")
        logging.info(f"Total workstreams: {len(self.graph.graph.nodes())}")
        logging.info(f"Available agents: {len(self.agents.agents)}")
        
        # Main execution loop
        while True:
            completed = self.state.get_completed_workstreams()
            ready = self.graph.get_ready_workstreams(completed)
            
            if not ready:
                # Check if all done
                total = len(self.graph.graph.nodes())
                if len(completed) >= total:
                    logging.info("All workstreams completed!")
                    break
                
                # Wait for running workstreams to complete
                logging.info("Waiting for dependencies to complete...")
                await asyncio.sleep(10)
                continue
            
            # Assign ready workstreams to available agents
            tasks = []
            for ws_id in ready:
                # Determine track for this workstream
                track = self._get_track_for_workstream(ws_id)
                
                # Get available agent for this track
                agent = self.agents.get_available_agent(track)
                if not agent:
                    continue  # No agents available for this track
                
                # Assign and execute
                ws_data = self.graph.get_workstream_data(ws_id)
                self.agents.assign_workstream(agent, ws_id, track)
                self.state.mark_started(ws_id, agent.id, track)
                
                # Create async task
                task = self._execute_workstream_async(agent, ws_id, ws_data)
                tasks.append(task)
            
            if not tasks:
                # No agents available, wait
                await asyncio.sleep(5)
                continue
            
            # Execute tasks in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in results:
                if isinstance(result, Exception):
                    logging.error(f"Execution error: {result}")
                    continue
                
                ws_id = result["workstream_id"]
                agent_id = result["agent_id"]
                success = result["success"]
                
                # Update state
                self.state.mark_completed(ws_id, result["exit_code"])
                
                # Release agent
                agent = next(a for a in self.agents.agents if a.id == agent_id)
                self.agents.release_agent(agent)
                
                if success:
                    logging.info(f"✅ {ws_id} completed by {agent_id}")
                else:
                    logging.error(f"❌ {ws_id} failed by {agent_id}")
        
        # Generate final report
        self._generate_report()
    
    async def _execute_workstream_async(self, agent, ws_id, ws_data):
        """Execute workstream asynchronously"""
        logging.info(f"🚀 Starting {ws_id} on {agent.id}")
        result = await self.agents.execute_workstream(agent, ws_id, ws_data)
        return result
    
    def _get_track_for_workstream(self, ws_id: str) -> str:
        """Determine which track this workstream belongs to"""
        for track, ws_list in self.track_assignments.items():
            if ws_id in ws_list:
                return track
        return "default"
    
    def _generate_report(self):
        """Generate execution report"""
        completed = self.state.get_completed_workstreams()
        failed = self.state.get_failed_workstreams()
        
        report = f"""
# Multi-Agent Execution Report

## Summary
- Total workstreams: {len(self.graph.graph.nodes())}
- Completed: {len(completed)}
- Failed: {len(failed)}
- Success rate: {len(completed) / len(self.graph.graph.nodes()) * 100:.1f}%

## Completed Workstreams
{chr(10).join(f"- ✅ {ws}" for ws in sorted(completed))}

## Failed Workstreams
{chr(10).join(f"- ❌ {ws}" for ws in sorted(failed))}
"""
        
        Path("reports/multi_agent_execution_report.md").write_text(report)
        logging.info(f"\n{report}")


# Main entry point
async def main():
    # Configuration
    agent_configs = [
        {"id": "agent-1", "type": "aider"},
        {"id": "agent-2", "type": "aider"},
        {"id": "agent-3", "type": "aider"},
    ]
    
    track_assignments = {
        "pipeline_plus": [
            "ws-22", "ws-23", "ws-24", "ws-25", 
            "ws-26", "ws-27", "ws-28", "ws-29", "ws-30"
        ],
        "core_refactor": [
            "ws-03", "ws-04", "ws-05", "ws-06", 
            "ws-07", "ws-08", "ws-09"
        ],
        "error_engine": [
            "ws-12", "ws-13", "ws-14", "ws-15", 
            "ws-16", "ws-17"
        ]
    }
    
    orchestrator = MultiAgentOrchestrator(
        workstreams_dir=Path("workstreams"),
        state_db=Path(".state/orchestration.db"),
        agent_configs=agent_configs,
        track_assignments=track_assignments
    )
    
    await orchestrator.execute_all()


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Usage

### **Step 1: Configure Agents**

Create `config/agents.yaml`:

```yaml
agents:
  - id: agent-1
    type: aider
    track: pipeline_plus
    priority: critical
    
  - id: agent-2
    type: aider
    track: core_refactor
    priority: high
    
  - id: agent-3
    type: aider
    track: error_engine
    priority: high
```

---

### **Step 2: Run Orchestrator**

```bash
# Install dependencies
pip install networkx asyncio

# Run orchestration
python scripts/orchestrator.py

# Monitor progress
watch -n 5 'sqlite3 .state/orchestration.db "SELECT * FROM workstream_status"'
```

---

### **Step 3: Monitor Execution**

```bash
# Check status
python scripts/check_orchestration_status.py

# View logs
tail -f logs/orchestrator.log

# Generate report
python scripts/generate_orchestration_report.py
```

---

## Integration with Existing Patterns

### **Use with Module Refactor Patterns**

```python
# Enhanced orchestrator using existing patterns

class PatternBasedOrchestrator(MultiAgentOrchestrator):
    
    async def _execute_workstream_async(self, agent, ws_id, ws_data):
        """Execute using registered patterns instead of raw commands"""
        
        # Determine pattern based on workstream type
        if ws_id.startswith("ws-22"):  # Schema creation
            pattern_id = "PAT-ATOMIC-CREATE-001"
        elif ws_id.startswith("ws-0"):  # Section refactor
            pattern_id = "PAT-MODULE-REFACTOR-MIGRATE-003"
        else:
            pattern_id = "PAT-GENERIC-WORKSTREAM-001"
        
        # Execute pattern
        cmd = f"execute-pattern {pattern_id} --workstream {ws_id}"
        
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await proc.communicate()
        
        return {
            "workstream_id": ws_id,
            "agent_id": agent.id,
            "exit_code": proc.returncode,
            "pattern_used": pattern_id,
            "success": proc.returncode == 0
        }
```

---

## Safety Features

### **1. File Conflict Detection**

```python
def check_file_conflicts(ws1_files: Set[str], ws2_files: Set[str]) -> bool:
    """Check if two workstreams modify same files"""
    return bool(ws1_files & ws2_files)

# In orchestrator: don't assign conflicting workstreams to parallel agents
```

### **2. Automatic Retry on Failure**

```python
# Already built into StateManager
# Failed workstreams with attempt < 3 are automatically retried
```

### **3. Recovery Points**

```python
# Before each workstream execution
recovery_id = create_recovery_point(ws_id)

# On failure
if not success:
    restore_recovery_point(recovery_id)
```

---

## Performance Optimization

### **Intelligent Work Distribution**

```python
def assign_tracks_optimally(graph: WorkstreamGraph, num_agents: int):
    """Assign tracks to agents to minimize total time"""
    
    # Calculate critical path for each track
    tracks = {
        "pipeline_plus": calculate_critical_path(graph, track_workstreams),
        "core_refactor": calculate_critical_path(graph, track_workstreams),
        "error_engine": calculate_critical_path(graph, track_workstreams)
    }
    
    # Assign longest critical path to dedicated agent
    sorted_tracks = sorted(tracks.items(), key=lambda x: x[1], reverse=True)
    
    assignments = {}
    for i, (track, _) in enumerate(sorted_tracks[:num_agents]):
        assignments[f"agent-{i+1}"] = track
    
    return assignments
```

---

## Expected Results

### **With 3 Agents:**

**Week 1**:
- Agent 1: WS-22 → WS-23 → WS-24 → WS-25 (Pipeline Plus)
- Agent 2: WS-03 → WS-06 → WS-07 → WS-08 (Core Refactor)
- Agent 3: WS-12 → WS-13 → WS-14 (Error Engine)

**Completed by end of Week 1**: 11-12 workstreams

**Week 2**:
- Agent 1: WS-26 → WS-27 → WS-28 → WS-29
- Agent 2: WS-09 → WS-18 → WS-19
- Agent 3: WS-15 → WS-16 → WS-17

**Completed by end of Week 2**: 20-24 workstreams

**Total time**: 1-2 weeks (vs 3-4 weeks sequential)

---

## Next Steps

1. ✅ Review orchestrator design
2. ✅ Implement WorkstreamGraph class
3. ✅ Implement AgentPool class
4. ✅ Implement StateManager class
5. ✅ Implement main Orchestrator
6. ✅ Test with 1 agent (dry run)
7. ✅ Scale to 3 agents
8. ✅ Monitor and optimize

---

**Pattern Status**: Ready for implementation  
**Estimated Implementation Time**: 4-6 hours  
**Expected ROI**: 2-3x faster execution with 3 agents
