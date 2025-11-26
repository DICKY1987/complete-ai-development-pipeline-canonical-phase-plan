# MCP Server Installation Guide
## Autonomous Development Pipeline Integration

**Installation Date:** November 9, 2025
**Installation Status:** ✅ Complete

---

## 🎯 Installed MCP Servers

### 1. PowerShell.MCP (v1.3.3)
**Purpose:** Enterprise PowerShell integration with AI
**Location:** `C:\Users\richg\OneDrive\Documents\WindowsPowerShell\Modules\PowerShell.MCP\1.3.3`
**Proxy:** `C:\Users\richg\OneDrive\Documents\WindowsPowerShell\Modules\PowerShell.MCP\1.3.3\bin\PowerShell.MCP.Proxy.exe`

**Key Features:**
- Shared console experience between AI and user
- Persistent state management (variables, modules, auth)
- Zero-overhead execution
- Complete stream separation (all 6 PowerShell streams)
- Named pipe communication (local-only, no network exposure)

**Integration Points:**
- AI Shell for PowerShell (your MCP triad member)
- PowerShell Factory (deterministic factory system)
- Invoke-Build integration
- Module discovery via Python entry points

**Usage Examples:**
```powershell
# Claude can now execute PowerShell in your context:
"Generate system performance HTML report and open in browser"
"Show processes consuming more than 100MB memory"
"Export installed programs to CSV"
```

---

### 2. GitHub Official MCP
**Purpose:** Complete GitHub integration via hosted service
**Endpoint:** `https://api.githubcopilot.com/mcp/`
**Authentication:** OAuth (requires GitHub PAT)

**Key Features:**
- Repository intelligence (no local clone needed)
- Issue and PR automation
- CI/CD visibility (workflow runs, logs, re-run jobs)
- Security insights (code scanning, Dependabot alerts)
- Fine-grained controls (read-only mode, toolset toggles)

**Integration Points:**
- Your File Watcher → Git Pipeline system
- GitHub-native identity (gh://owner/repo/{issues|pulls}/{number})
- BPMN/DMN state machines triggering GitHub Actions
- run_ulid execution traces linked to GitHub workflow runs

**Required Setup:**
1. Create GitHub Personal Access Token: https://github.com/settings/tokens
2. When Claude Desktop prompts, enter your PAT
3. Scopes needed: `repo`, `workflow`, `read:org`

**Usage Examples:**
```
"Create a pull request from my feature branch"
"Show me all failed CI runs this week"
"List open security alerts for my repositories"
"Find all issues assigned to me with label 'bug'"
```

---

### 3. Memory MCP Server (Official)
**Purpose:** Knowledge graph-based persistent memory
**Package:** `@modelcontextprotocol/server-memory`
**Transport:** stdio via npx

**Key Features:**
- Entity and relationship tracking
- Persistent knowledge graphs
- Cross-conversation context
- Semantic search capabilities

**Integration Points:**
- Track module relationships in your plugin architecture
- Store past decision context for deterministic execution
- Maintain Epic→Story→Task hierarchy relationships
- Cross-session project memory

**Usage Examples:**
```
"Remember that the PL-ORCH module coordinates all planning phases"
"What decisions did we make about the SafePatch boundaries?"
"Show me the relationship between ACMS and the File Watcher"
```

---

### 4. SQLite MCP Server
**Purpose:** Local pipeline database with complete audit trail
**Database:** `C:\Users\richg\mcp-data\pipeline.db`
**Package:** `mcp-server-sqlite`
**Transport:** stdio via uvx

**Schema Highlights:**
- **policy_versions**: Immutable git-tagged policy documents
- **run_traces**: ULID-based execution tracking
- **modules**: Two-ID naming system (Module ID + File ID)
- **workstreams**: Parallel execution with git worktrees
- **planning_items**: Epic/Story/Task hierarchy
- **event_log**: Complete JSONL audit trail
- **safepatch_checkpoints**: Git checkpoints per phase
- **v_model_gates**: Quality gate validations
- **plugin_conformance**: Contract compliance tests

**Integration Points:**
- R_PIPELINE documentation storage
- run_ulid execution traces
- Policy versioning with git tags
- SafePatch checkpoint tracking
- V-Model gate results
- Complete audit trail for governance

**Usage Examples:**
```sql
-- Track a new run
INSERT INTO run_traces (run_ulid, github_issue_key, status, phase) 
VALUES ('01HXYZ...', 'gh://owner/repo/issues/123', 'running', 'Planning');

-- Query workstreams
SELECT * FROM workstreams WHERE run_ulid = '01HXYZ...' AND status = 'in_progress';

-- Audit trail
SELECT * FROM event_log WHERE run_ulid = '01HXYZ...' ORDER BY timestamp;
```

**AI Query Examples:**
```
"Show me all runs for issue gh://owner/repo/issues/123"
"What policies were active during run 01HXYZ?"
"List all failed workstreams in the last week"
"Show me the audit trail for the last deployment"
```

---

### 5. Linear MCP Server (Optional)
**Purpose:** Project management and task tracking
**Package:** `@modelcontextprotocol/server-linear`
**Authentication:** Requires Linear API key

**Key Features:**
- Team and issue management
- Project and cycle tracking
- Sprint planning automation
- AI-driven task decomposition

**Integration Points:**
- Machine-readable Epic→Story→Task hierarchy
- Automated planning from AI analysis
- Status updates from JSONL events
- Agent dispatch based on complexity

**Required Setup:**
1. Get API key from Linear: Settings → API → Create Key
2. When Claude Desktop prompts, enter your Linear API key

**Usage Examples:**
```
"Create an epic for the ACMS v2 implementation"
"Break down this epic into implementable stories"
"Show me all tasks assigned to Jules CLI agent"
"Update story SS-123 status to 'In Progress'"
```

**Alternative:** If you prefer Jira, replace with Composio's Jira MCP:
```json
{
  "command": "npx",
  "args": ["-y", "@composio/cli", "add", "cursor", "--app", "jira"]
}
```

---

## 📋 Configuration File

**Location:** `C:\Users\richg\AppData\Roaming\Claude\claude_desktop_config.json`

**Current Configuration:**
```json
{
  "mcpServers": {
    "PowerShell": {
      "command": "C:\\Users\\richg\\OneDrive\\Documents\\WindowsPowerShell\\Modules\\PowerShell.MCP\\1.3.3\\bin\\PowerShell.MCP.Proxy.exe"
    },
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${input:github_mcp_pat}"
      }
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "sqlite": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db-path", "C:\\Users\\richg\\mcp-data\\pipeline.db"]
    },
    "linear": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-linear"],
      "env": {
        "LINEAR_API_KEY": "${input:linear_api_key}"
      }
    }
  }
}
```

---

## 🔄 Activation Steps

### 1. Restart Claude Desktop
Close and reopen Claude Desktop to load the new MCP configuration.

### 2. Provide API Keys
When prompted, provide:
- **GitHub PAT**: For GitHub MCP server
- **Linear API Key**: For Linear MCP server (if using)

### 3. Test Each Server
Try these commands to verify:

**PowerShell:**
```
"List all PowerShell modules installed on this system"
```

**GitHub:**
```
"List my GitHub repositories"
```

**Memory:**
```
"Remember that I'm working on an autonomous development pipeline"
```

**SQLite:**
```
"Show me the schema of the pipeline database"
```

**Linear:**
```
"List my Linear teams"
```

---

## 🏗️ Architecture Integration

### Your 6-Phase Workflow Enhancement

**Phase 1: Intent → Specification**
- **GitHub MCP**: Parse issue descriptions into specs
- **Memory MCP**: Recall similar past projects
- **SQLite**: Store specification in planning_items

**Phase 2: Planning → Modification Plans**
- **Linear/Jira MCP**: Create Epic→Story→Task hierarchy
- **SQLite**: Store decomposed tasks with complexity scores
- **Memory MCP**: Reference similar past plans

**Phase 3: Safe Execution → Isolated Changes**
- **PowerShell MCP**: Execute build scripts deterministically
- **GitHub MCP**: Create git worktrees via API
- **SQLite**: Track workstream status and SafePatch checkpoints

**Phase 4: Validation → Quality Gates**
- **GitHub MCP**: Run CI/CD workflows and fetch results
- **SQLite**: Store V-Model gate results
- **PowerShell MCP**: Execute conformance tests

**Phase 5: Integration → Synchronized State**
- **GitHub MCP**: Create PRs and manage merges
- **SQLite**: Update run_traces with final status
- **Memory MCP**: Store lessons learned

**Phase 6: Observability → Feedback Loop**
- **SQLite**: Query event_log for analytics
- **GitHub MCP**: Create new issues from failures
- **Memory MCP**: Build knowledge graph of patterns

---

## 🎯 LangGraph Orchestration

Your state machine can now use these MCP servers as tools:

```python
from langgraph import StateGraph

# Define your autonomous pipeline state
class PipelineState:
    github_issue_key: str
    run_ulid: str
    phase: str
    status: str
    # ... other fields

# Create graph with MCP tools
graph = StateGraph(PipelineState)

# Add nodes that use MCP servers
graph.add_node("parse_intent", parse_with_github_mcp)
graph.add_node("create_plan", plan_with_linear_mcp)
graph.add_node("execute", execute_with_powershell_mcp)
graph.add_node("validate", validate_with_github_ci_mcp)
graph.add_node("integrate", integrate_with_github_pr_mcp)
graph.add_node("observe", observe_with_sqlite_mcp)

# Connect edges based on your BPMN/DMN logic
# ...
```

---

## 📊 Database Schema Usage

### Example: Track a Complete Run

```python
import sqlite3
from ulid import ULID

# Generate run ULID
run_id = str(ULID())

# 1. Start run
conn.execute("""
    INSERT INTO run_traces (run_ulid, github_issue_key, status, phase)
    VALUES (?, ?, 'running', 'Intent')
""", (run_id, 'gh://owner/repo/issues/123'))

# 2. Log event
conn.execute("""
    INSERT INTO event_log (event_id, event_ulid, run_ulid, event_type, actor, action)
    VALUES (?, ?, ?, 'run_started', 'LangGraph', 'initialize_pipeline')
""", (str(ULID()), str(ULID()), run_id))

# 3. Create workstreams
for i in range(3):  # Parallel modifications
    conn.execute("""
        INSERT INTO workstreams (workstream_id, lineage_id, instance_id, run_ulid, status)
        VALUES (?, ?, ?, ?, 'created')
    """, (f"ws_{i}", f"lineage_{i}", f"instance_{i}", run_id))

# 4. Track checkpoints
conn.execute("""
    INSERT INTO safepatch_checkpoints 
    (checkpoint_id, run_ulid, phase, git_commit_sha, files_changed)
    VALUES (?, ?, 'Planning', ?, ?)
""", (str(ULID()), run_id, 'abc123', 5))

# 5. Record gate results
conn.execute("""
    INSERT INTO v_model_gates (gate_id, run_ulid, gate_name, gate_type, status)
    VALUES (?, ?, 'Unit Tests', 'unit_test', 'passed')
""", (str(ULID()), run_id))

conn.commit()
```

---

## 🔐 Security Notes

**PowerShell.MCP:**
- Local-only named pipe (no network exposure)
- Runs in your user context (full PowerShell access)
- Consider using read-only mode for sensitive operations

**GitHub MCP:**
- OAuth via official GitHub endpoint
- Supports fine-grained permissions
- Can toggle read-only mode

**SQLite:**
- Local file-based (C:\Users\richg\mcp-data\pipeline.db)
- No network access
- Regular backups recommended

**Linear:**
- API key stored in config (encrypted by Claude Desktop)
- Scoped to your Linear workspace

---

## 🚀 Next Steps

1. **Restart Claude Desktop** to activate all servers
2. **Test each server** with the example commands above
3. **Integrate with your existing systems:**
   - Update AI Upkeep Suite v2 to use GitHub MCP
   - Modify ACMS to log to SQLite database
   - Connect CLI Orchestrator to PowerShell MCP
   - Link File Watcher to GitHub Actions via MCP
4. **Configure Linear/Jira** for automated planning
5. **Build LangGraph orchestration** using MCP servers as tools

---

## 📚 Additional Resources

**PowerShell.MCP:**
- GitHub: https://github.com/yotsuda/PowerShell.MCP
- Documentation: (Get-Module PowerShell.MCP).ModuleBase

**GitHub MCP:**
- Documentation: https://github.com/github/github-mcp-server
- Blog: https://github.blog/ai-and-ml/generative-ai/a-practical-guide-on-how-to-use-the-github-mcp-server/

**Memory MCP:**
- Repository: https://github.com/modelcontextprotocol/servers

**SQLite MCP:**
- GitHub: https://github.com/panasenco/mcp-sqlite

**Linear MCP:**
- API Docs: https://developers.linear.app/docs

---

## 🐛 Troubleshooting

**PowerShell.MCP not loading:**
- Ensure PowerShell 7.2+ is installed
- Check proxy path in config
- Verify module loaded: `Get-Module PowerShell.MCP`

**GitHub MCP authentication fails:**
- Regenerate PAT with correct scopes
- Check token hasn't expired
- Verify network connectivity to api.githubcopilot.com

**SQLite database locked:**
- Close other connections to pipeline.db
- Check file permissions
- Restart Claude Desktop

**Linear API key invalid:**
- Verify key from Linear Settings → API
- Check key hasn't been revoked
- Ensure proper workspace access

---

**Installation Complete! 🎉**

Your autonomous development pipeline now has:
✅ PowerShell orchestration via AI
✅ Complete GitHub integration
✅ Persistent knowledge graphs
✅ Local audit trail database
✅ Project management automation

**Ready to eliminate human intervention in your development workflows!**
