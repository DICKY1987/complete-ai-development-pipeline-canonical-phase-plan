# 02_ARCHITECTURE - System Architecture & Design

**Technical design patterns, worktree mechanics, and orchestration architecture**

---

## 📋 Purpose

This folder contains all technical architecture documents that define **how the system works**, **how agents are managed**, and **how isolation is achieved**.

---

## 📁 Contents

### Core Architecture Documents

#### `PLUGIN_BASED_AGENT_ARCHITECTURE.md`
**The foundational architecture design.**

- Plugin-based CLI agent system
- Dynamic tool launching (GitHub Copilot, Aider, custom agents)
- ToolFactory pattern for interchangeable tools
- Configuration-driven agent spawning
- Process management (spawn, monitor, kill, timeout)
- Self-replication architecture

**Use this when:** Understanding the core orchestration engine or adding new agent types.

---

#### `WORKTREE_ISOLATION_DEEP_DIVE.md`
**Complete guide to Git worktree isolation.**

- How Git worktrees enable parallel execution
- File system isolation mechanics
- Zero-conflict guarantee explained
- Worktree lifecycle (create, execute, merge, cleanup)
- Memory and disk overhead analysis
- Practical implementation examples

**Use this when:** Understanding isolation mechanics or troubleshooting worktree issues.

---

#### `AGENT_ARCHITECTURE_DEEP_DIVE.md`
**Detailed comparison of agent implementation approaches.**

- **Subprocess Spawning:** External CLI tools (complexity, overhead, control)
- **Self-Replication:** Orchestrator spawning copies of itself
- **Background Tasks:** Detached processes for resilience
- Hybrid approach recommendation
- Complexity vs. capability trade-offs
- Resource overhead analysis

**Use this when:** Choosing implementation patterns or optimizing agent management.

---

#### `MULTI_AGENT_ORCHESTRATION_SUMMARY.md`
**High-level system overview.**

- How multiple agents coordinate
- Orchestrator responsibilities
- Worker agent behavior
- Communication patterns
- State management
- Error handling and recovery

**Use this when:** Getting a quick system overview or explaining to stakeholders.

---

#### `MULTI_AGENT_SIMPLE_VISUAL.md`
**Visual diagrams and flow charts.**

- System architecture diagrams
- Process flow visualizations
- Worktree isolation illustrations
- Agent lifecycle diagrams

**Use this when:** Presenting the system or visual learning.

---

## 🎯 Key Architectural Principles

### 1. Plugin-Based Design

**Why:** Enables tool interchangeability (Aider, Copilot, custom agents) without code changes.

**How:** Configuration-driven ToolFactory pattern.

```python
# Switch tools via config, not code
tools:
  copilot:
    path: "/usr/bin/gh-copilot"
    args: ["--mode", "worker"]
  aider:
    path: "/usr/local/bin/aider"
    args: ["--auto-commits"]
```

---

### 2. Worktree Isolation

**Why:** Eliminates merge conflicts during parallel execution.

**How:** Each agent gets its own Git worktree (independent working directory).

```
main/              ← Original repo
worktrees/
  ├── worker_1/    ← Workstream 1 (isolated)
  ├── worker_2/    ← Workstream 2 (isolated)
  └── worker_3/    ← Workstream 3 (isolated)
```

**Guarantee:** Zero file system conflicts, automatic merge compatibility.

---

### 3. Self-Replication Pattern

**Why:** Orchestrator can spawn copies of itself as workers, enabling recursive parallelization.

**How:** Main process spawns child processes with `--mode worker` flag.

```bash
# Main orchestrator
python orchestrator.py --mode orchestrator

# Spawns workers
python orchestrator.py --mode worker --id worker_1 --worktree /tmp/wt1
python orchestrator.py --mode worker --id worker_2 --worktree /tmp/wt2
```

---

### 4. Process Management

**Why:** High control over worker processes (monitor, timeout, kill).

**How:** `subprocess.Popen` with process tracking.

**Features:**
- Real-time output streaming
- Timeout enforcement (30 min default)
- Graceful shutdown and force-kill
- Memory limit enforcement

---

## 📊 Architecture Decisions

| Decision | Rationale | Trade-off |
|----------|-----------|-----------|
| **Worktree isolation** | Zero conflicts | +300 MB disk per agent |
| **Plugin-based agents** | Flexibility | Slight complexity increase |
| **Self-replication** | Recursive parallelization | Requires careful process management |
| **Subprocess spawning** | High control | More overhead than threading |

---

## 🔧 Implementation Patterns

### Pattern 1: Dynamic Tool Launching

**Problem:** Need to support multiple AI tools without hardcoding.

**Solution:** Configuration-driven ToolFactory.

**Benefit:** Add new tools by editing config, not code.

---

### Pattern 2: Worktree Lifecycle

**Stages:**
1. **Create:** `git worktree add /tmp/wt1 -b branch1`
2. **Execute:** Agent works in isolated directory
3. **Merge:** `git merge branch1` (automatic, conflict-free)
4. **Cleanup:** `git worktree remove /tmp/wt1`

**Benefit:** Predictable, safe, automatable.

---

### Pattern 3: Hybrid Agent Management

**Combine all three approaches:**
1. **Subprocess spawning** for external tools (Aider)
2. **Self-replication** for scaling orchestrator
3. **Background tasks** for crash resilience

**Benefit:** Maximum flexibility and reliability.

---

## 🚀 Next Steps

After understanding architecture:

1. **Implementation** → `../03_IMPLEMENTATION/` (see the code)
2. **Operations** → `../04_OPERATIONS/` (run and troubleshoot)
3. **Reference** → `../05_REFERENCE/` (patterns and examples)

---

## 📝 Document Status

- ✅ **PLUGIN_BASED_AGENT_ARCHITECTURE.md** - Complete, validated
- ✅ **WORKTREE_ISOLATION_DEEP_DIVE.md** - Complete, validated
- ✅ **AGENT_ARCHITECTURE_DEEP_DIVE.md** - Complete, validated
- ✅ **MULTI_AGENT_ORCHESTRATION_SUMMARY.md** - Complete, validated
- ✅ **MULTI_AGENT_SIMPLE_VISUAL.md** - Complete, validated

---

**Ready to implement?** → Proceed to `../03_IMPLEMENTATION/`
