# Simple Workstream Executor - Quick Start

**Created**: 2025-11-29  
**Purpose**: Execute workstreams sequentially with manual control

---

## 🚀 Quick Start

```powershell
# Navigate to repository root
cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"

# Run the simple executor
.\scripts\run_simple_executor.ps1
```

---

## 📋 What It Does

The simple executor:

1. **Loads all workstreams** from `workstreams/ws-*.json`
2. **Checks dependencies** - only shows workstreams where all dependencies are met
3. **Presents each workstream** with these options:
   - **1. Execute with Aider** - Automated AI execution
   - **2. Open files in editor** - Manual editing
   - **3. Skip** - Skip this workstream
   - **4. Mark complete** - Already done
   - **q. Quit** - Exit executor

4. **Tracks progress** - Shows completed/skipped count
5. **Saves results** to `reports/simple_executor_results.json`

---

## 🎯 Usage Example

```
📋 Workstream: ws-01-hardcoded-path-index
📝 Title: Create hardcoded path index

🔧 Tool: aider
📁 Files: 5 file patterns
✓ Tasks: 3

📝 Tasks to complete:
   1. Create scripts/path_index.py
   2. Add path validation
   3. Generate index report

Choose execution method:
  1. Execute with Aider (automated)
  2. Open files in editor (manual)
  3. Skip this workstream
  4. Mark as completed (already done)
  q. Quit executor

Your choice [1/2/3/4/q]: 1

🤖 Running Aider...
```

---

## ✅ Advantages

- **Manual control** - You choose how to execute each workstream
- **No parallelization complexity** - One workstream at a time
- **Interactive** - See what's happening at each step
- **Flexible** - Mix automated and manual execution
- **Simple** - No worktrees, no complex orchestration
- **Safe** - Can skip problematic workstreams

---

## 📊 Progress Tracking

After execution, check:

```powershell
# View results
Get-Content reports\simple_executor_results.json | ConvertFrom-Json

# View log
Get-Content logs\simple_executor.log -Tail 50
```

---

## 🔧 Requirements

- **Python 3.8+** - For executor script
- **Aider** (optional) - For automated execution: `pip install aider-chat`
- **Workstreams** - JSON files in `workstreams/` directory

---

## 💡 Tips

1. **Start with option 4** for already-completed workstreams
2. **Use option 1** (Aider) for simple, well-defined tasks
3. **Use option 2** (manual) for complex refactoring that needs human judgment
4. **Use option 3** (skip) for workstreams that need more planning
5. **Press q** to quit anytime - progress is saved

---

## 🆚 vs. Multi-Agent Orchestrator

| Feature | Simple Executor | Multi-Agent |
|---------|----------------|-------------|
| Speed | Slower (sequential) | Faster (parallel) |
| Control | Full manual control | Automated |
| Complexity | Very simple | Complex |
| Setup | None | Worktrees, config |
| Reliability | Very reliable | Needs debugging |
| Best for | Learning, testing | Production bulk work |

---

## 📝 Example Workflow

```powershell
# 1. Run executor
.\scripts\run_simple_executor.ps1

# 2. For each workstream, choose:
#    - Automated (Aider): For well-defined tasks
#    - Manual: For complex tasks
#    - Skip: For tasks needing more planning
#    - Complete: For already-done tasks

# 3. Review results
Get-Content reports\simple_executor_results.json

# 4. Commit changes
git status
git add .
git commit -m "Completed workstreams: ws-01, ws-03, ws-04"
```

---

## 🐛 Troubleshooting

**Issue**: "No workstreams found"
```powershell
# Check directory
ls workstreams\ws-*.json
```

**Issue**: "Aider not found"
```powershell
# Install Aider
pip install aider-chat

# Verify
aider --version
```

**Issue**: "Dependencies not met"
- Complete the dependency workstreams first
- Or use option 4 to mark dependencies as complete

---

## 🎯 Next Steps After Completion

1. **Review changes**: `git diff`
2. **Run tests**: `pytest tests/`
3. **Validate imports**: `python scripts/paths_index_cli.py gate`
4. **Commit work**: `git commit -m "Completed workstreams"`

---

**Ready to start?** Run: `.\scripts\run_simple_executor.ps1`
