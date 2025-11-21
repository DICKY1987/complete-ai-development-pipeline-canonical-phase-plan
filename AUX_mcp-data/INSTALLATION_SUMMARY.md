# MCP Server Installation - COMPLETE ✅
**Date:** November 9, 2025
**User:** richg
**System:** Windows 11 (PowerShell 7.5.4)

---

## 🎉 Installation Summary

### ✅ Successfully Installed

1. **PowerShell.MCP v1.3.3**
   - Module installed from PowerShell Gallery
   - Location: `C:\Users\richg\OneDrive\Documents\WindowsPowerShell\Modules\PowerShell.MCP\1.3.3`
   - Status: ✅ Ready

2. **GitHub Official MCP**
   - Endpoint configured: `https://api.githubcopilot.com/mcp/`
   - Status: ⚠️ Requires GitHub PAT on first use

3. **Memory MCP Server**
   - Package: `@modelcontextprotocol/server-memory`
   - Transport: stdio via npx
   - Status: ✅ Ready

4. **SQLite MCP Server**
   - Database: `C:\Users\richg\mcp-data\pipeline.db`
   - Schema: ✅ Initialized with 9 tables
   - Status: ✅ Ready

5. **Linear MCP Server**
   - Package: `@modelcontextprotocol/server-linear`
   - Status: ⚠️ Requires Linear API key on first use

### 📁 Files Created

```
C:\Users\richg\mcp-data\
├── pipeline.db              # SQLite database (initialized)
├── pipeline-schema.sql      # Database schema
├── init_db.py              # Database initialization script
├── MCP_SETUP_GUIDE.md      # Complete setup documentation
└── MCP_QUICK_REFERENCE.md  # Usage examples and commands
```

```
C:\Users\richg\AppData\Roaming\Claude\
└── claude_desktop_config.json  # MCP configuration
```

---

## 🚀 IMMEDIATE NEXT STEPS

### Step 1: Restart Claude Desktop (REQUIRED)
**Action:** Close this window and restart Claude Desktop completely.
**Why:** MCP servers only load on startup.

### Step 2: Provide API Keys
When you first use these commands, Claude will prompt for:

**GitHub Personal Access Token:**
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `workflow`, `read:org`
4. Copy the token
5. Paste when Claude prompts

**Linear API Key (Optional):**
1. Go to: https://linear.app/settings/api
2. Click "Create Key"
3. Give it a name: "Claude MCP"
4. Copy the key
5. Paste when Claude prompts

### Step 3: Test Installation
After restart, try these commands:

**Test PowerShell MCP:**
```
List all PowerShell modules installed on my system
```

**Test Memory MCP:**
```
Remember that I'm building an autonomous development pipeline called ACMS
```

**Test SQLite MCP:**
```
Show me the tables in my pipeline database
```

**Test GitHub MCP (after providing PAT):**
```
List my GitHub repositories
```

**Test Linear MCP (after providing API key):**
```
Show my Linear teams
```

---

## 🎯 What You Can Do Now

### Autonomous Pipeline Integration

**1. Track Your First Run:**
```
Start a new autonomous run for a sample task. Use the SQLite database to:
- Create a run_trace with a ULID
- Log the initial event
- Create a workstream entry
- Store a SafePatch checkpoint
```

**2. GitHub Integration:**
```
Show me all my open GitHub issues. For each issue:
- Create an Epic in the planning_items table
- Generate a modification plan
- Track the issue key: gh://owner/repo/issues/{number}
```

**3. Module Registration:**
```
Register the following modules in the SQLite modules table:
- PL-ORCH (category: Orchestration)
- PL-STATE (category: State Change)
- PL-CHECK (category: Configuration/Validation)
- PL-INGEST (category: Data Acquisition)
- PL-CTX (category: Data Transformation)
```

**4. Policy Versioning:**
```
From the /mnt/project/ directory, register all policy files in the policy_versions table:
- plugin_spec.json
- plugin_contract_v1.json
- error_contract_v1.json
- compatibility_matrix.yaml
Tag each with appropriate version numbers.
```

### Daily Workflow Examples

**Morning Standup:**
```
From my SQLite database and Linear, show me:
- All tasks assigned to me
- In-progress workstreams
- Failed quality gates from yesterday
- Upcoming deadlines this week
```

**Start Development:**
```
For Linear issue SS-123:
1. Create a new run_trace in SQLite
2. Generate modification plan
3. Create git worktree via GitHub MCP
4. Log initial checkpoint
5. Begin implementation with PowerShell automation
```

**Code Review:**
```
For workstream ws_1:
1. Run conformance tests via PowerShell
2. Check V-Model gates
3. Create PR via GitHub MCP
4. Update SQLite with results
```

**End of Day:**
```
Generate a summary report from SQLite:
- Today's completed tasks
- In-progress workstreams
- Quality gate results
- Audit trail of all actions
```

---

## 📊 Database Schema Overview

Your `pipeline.db` has these tables:

| Table | Purpose |
|-------|---------|
| `policy_versions` | Immutable git-tagged policy documents |
| `run_traces` | ULID-based execution tracking |
| `modules` | Two-ID naming system registry |
| `workstreams` | Parallel execution tracking |
| `planning_items` | Epic/Story/Task hierarchy |
| `event_log` | Complete JSONL audit trail |
| `safepatch_checkpoints` | Git checkpoints per phase |
| `v_model_gates` | Quality gate validations |
| `plugin_conformance` | Contract compliance tests |

All ready to use with natural language queries!

---

## 🔧 Configuration Details

**PowerShell Requirements:**
- ✅ PowerShell 7.5.4 detected
- ✅ Module location verified
- ✅ Proxy executable configured

**Node.js Requirements:**
- ✅ npm 11.6.1 detected
- ✅ npx available for Memory & Linear MCPs

**Python Requirements:**
- ✅ uvx 0.9.6 detected
- ✅ Available for SQLite MCP

**All dependencies satisfied!**

---

## 📚 Documentation Locations

- **Complete Setup Guide:** `C:\Users\richg\mcp-data\MCP_SETUP_GUIDE.md`
- **Quick Reference:** `C:\Users\richg\mcp-data\MCP_QUICK_REFERENCE.md`
- **Database Schema:** `C:\Users\richg\mcp-data\pipeline-schema.sql`
- **Config File:** `C:\Users\richg\AppData\Roaming\Claude\claude_desktop_config.json`

---

## 🎓 Learning Path

### Beginner (First Week)
1. Test each MCP server individually
2. Create simple entries in SQLite database
3. Practice basic GitHub operations
4. Store and retrieve memories

### Intermediate (Week 2-4)
1. Track a complete run through all 6 phases
2. Use parallel workstreams
3. Automate planning with Linear
4. Build audit trails

### Advanced (Month 2+)
1. Integrate with LangGraph orchestration
2. Implement BPMN/DMN state machines
3. Full autonomous pipeline execution
4. Multi-agent coordination

---

## 🐛 Troubleshooting

**If MCP servers don't appear after restart:**
1. Check: `C:\Users\richg\AppData\Roaming\Claude\logs\mcp.log`
2. Verify config: `C:\Users\richg\AppData\Roaming\Claude\claude_desktop_config.json`
3. Ensure all paths are correct
4. Check Windows Defender isn't blocking executables

**If PowerShell commands fail:**
1. Verify PowerShell 7 is default: `pwsh -Version`
2. Check execution policy: `Get-ExecutionPolicy`
3. Module loaded: `Get-Module PowerShell.MCP`

**If database queries fail:**
1. Check database exists: `C:\Users\richg\mcp-data\pipeline.db`
2. Verify uvx installed: `uvx --version`
3. Test manually: `uvx mcp-server-sqlite --help`

**If GitHub authentication fails:**
1. Regenerate PAT with correct scopes
2. Check token in config input
3. Verify: `gh auth status` (if GitHub CLI installed)

---

## 💡 Pro Tips

1. **Use Memory MCP for Context:** Store design decisions, patterns, and lessons learned. It builds a knowledge graph automatically.

2. **SQLite for Audit Trails:** Every autonomous action should log to event_log with ULID for traceability.

3. **GitHub MCP for CI/CD:** Skip manual workflow triggering - let AI monitor and manage your pipelines.

4. **PowerShell for Everything Windows:** From file operations to registry management, it's all accessible now.

5. **Linear for Planning:** Let AI decompose epics into stories and tasks with appropriate complexity scores.

---

## 🎯 Your Autonomous Pipeline is Ready!

You now have:
✅ **Planning:** Linear MCP for automated task decomposition
✅ **Execution:** PowerShell MCP for deterministic operations
✅ **Validation:** GitHub MCP for CI/CD integration
✅ **Tracking:** SQLite MCP for complete audit trails
✅ **Memory:** Knowledge graphs for persistent context

**Next Command:**
```
After restarting Claude Desktop, say:
"Show me what MCP servers are available and test each one"
```

---

## 📞 Getting Help

**Documentation:**
- Setup Guide: `C:\Users\richg\mcp-data\MCP_SETUP_GUIDE.md`
- Quick Reference: `C:\Users\richg\mcp-data\MCP_QUICK_REFERENCE.md`

**Community:**
- MCP Discord: https://discord.gg/modelcontextprotocol
- GitHub Discussions: https://github.com/modelcontextprotocol/servers/discussions

**Your Project Context:**
- Project files: `/mnt/project/`
- Architecture docs: Already in your project knowledge

---

🎉 **Installation Complete! Time to Build Autonomous Systems!** 🎉
