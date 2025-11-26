# Quick Reference: MCP Servers for Autonomous Pipeline
## Common Use Cases & Commands

---

## 🎯 Planning & Task Management

### Create Epic→Story→Task Hierarchy
```
Using Linear, create an epic titled "Implement ACMS v2 with Complete Audit Trail"

Break down the ACMS v2 epic into implementable stories with these requirements:
- Each story should be completable in 1-2 days
- Include acceptance criteria
- Tag stories with appropriate module categories (Data Acquisition, Orchestration, etc.)
- Assign complexity scores 1-10

For each story, create tasks and assign to appropriate AI agents:
- Jules CLI: mechanical/routine tasks (complexity 1-3)
- Aider CLI: complex debugging (complexity 7-10)
- Copilot CLI: orchestration (complexity 4-6)
```

### Query Planning Status
```
From the SQLite database, show me all planning items for the ACMS v2 epic:
- Group by status (todo, in_progress, review, done, blocked)
- Show assigned agents
- Calculate total estimated vs actual effort
```

---

## 🔄 Execution Tracking

### Start a New Run
```
I'm starting a new autonomous run for GitHub issue gh://myorg/myrepo/issues/456

Using SQLite, create a new run_trace with:
- Generate a ULID for run_ulid
- Link to the GitHub issue
- Set status to 'pending'
- Set phase to 'Intent'
- Capture current policy snapshot (read from /mnt/project/ files)

Then log the initial event in event_log.
```

### Track Parallel Workstreams
```
For run ULID [run_id], create 3 workstreams for parallel modifications:

Workstream 1: Modify PL-ORCH module
- lineage_id: pl-orch-mod-lineage
- instance_id: [generate ULID]
- git_worktree_path: /tmp/worktree-pl-orch
- modification_plan_path: /plans/pl-orch-mod.yaml

Workstream 2: Update PL-STATE module
[similar structure]

Workstream 3: Enhance PL-CHECK validation
[similar structure]

Store all in the workstreams table.
```

---

## 🔍 Git Operations via GitHub MCP

### Create Worktrees for Parallel Execution
```
For each workstream in run [run_id]:
1. Create a new branch from main: feature/ws-[workstream_id]
2. Fetch the latest main branch
3. Show me the branch protection rules for main
```

### CI/CD Monitoring
```
Show me all GitHub Actions workflow runs for repository myorg/myrepo:
- Filter by status: failed
- From the last 7 days
- Include logs for failed jobs
- Group by workflow name
```

### Create Pull Requests
```
For completed workstream ws_1:
1. Create a PR from branch feature/ws_1 to main
2. Title: "ACMS v2: Implement PL-ORCH modifications"
3. Body: Link to issue #456, include modification plan summary
4. Add reviewers based on CODEOWNERS
5. Enable auto-merge when checks pass
```

---

## 📊 Validation & Quality Gates

### Record SafePatch Checkpoints
```
After completing the Planning phase for run [run_id]:

Using PowerShell, get the git commit details:
- Current commit SHA
- Files changed count
- Lines added/deleted

Store in safepatch_checkpoints table with:
- checkpoint_id: [generate ULID]
- run_ulid: [run_id]
- phase: 'Planning'
- git_commit_sha: [from PowerShell]
- rollback_available: 1
```

### Execute and Record V-Model Gates
```
For run [run_id], execute the following gates:

1. Unit Tests Gate:
   - Run via GitHub Actions workflow "unit-tests"
   - Wait for completion
   - Fetch results and logs
   - Store in v_model_gates table with status

2. Integration Tests Gate:
   - Trigger "integration-tests" workflow
   - Monitor progress
   - Record results

3. Plugin Conformance Gate:
   - Use PowerShell to run conformance tests
   - Check against plugin_spec.json contract
   - Store results in plugin_conformance table
```

---

## 🧠 Memory & Context Management

### Store Design Decisions
```
Remember these design decisions for the ACMS v2 implementation:

1. We chose LangGraph for orchestration because it provides:
   - State machine approach matching our BPMN/DMN models
   - Native support for parallel workstreams
   - Built-in checkpoint/rollback capabilities

2. The Two-ID naming system uses:
   - Module ID: Permanent identifier across versions
   - Module File ID: Specific to file location
   - Workstream Lineage ID: Tracks modification history
   - Workstream Instance ID: Unique per execution

3. SafePatch boundaries are enforced at:
   - Function level for small changes
   - File level for medium changes
   - Module level for large refactors
```

### Query Past Decisions
```
What were our reasons for choosing LangGraph over alternative orchestration frameworks?

Show me all design decisions related to the plugin architecture.

What lessons did we learn from the previous ACMS v1 implementation?
```

---

## 💾 Database Queries via SQLite MCP

### Audit Trail Analysis
```
From the pipeline database, show me:

1. All events for run [run_id] in chronological order
2. Which agents performed which actions
3. Any errors or rollbacks that occurred
4. Git commit SHAs at each phase boundary

Format as a timeline visualization.
```

### Module Relationship Analysis
```
Query the modules table and show:
1. All modules in the "Orchestration" category
2. Their entry points for plugin discovery
3. Last update timestamps
4. Dependencies between modules (if tracked)
```

### Performance Metrics
```
From the planning_items table, calculate:
1. Average estimated vs actual effort by agent
2. Which agents are most accurate in estimates
3. Tasks that consistently exceed estimates
4. Complexity score vs actual effort correlation
```

---

## 🔧 PowerShell Automation

### Execute Invoke-Build Tasks
```
Using PowerShell.MCP, run the following build automation:

1. Execute Invoke-Build task "Generate-Documentation"
   - Pass parameter: -ModuleName "ACMS"
   - Capture all output streams
   
2. Run task "Run-ConformanceTests"
   - For all modules in category "Orchestration"
   - Generate JUnit XML report
   
3. Execute "Package-Release"
   - Version: from git tag
   - Include changelog from commits
```

### Git Operations via PowerShell
```
Use PowerShell to:
1. Check current git worktree status
2. Show uncommitted changes in staging area
3. Create annotated tag for policy version: v1.0.0-plugin-spec
4. Push tag to remote with force (after confirmation)
```

### System Integration
```
Using PowerShell.MCP:
1. Check if Docker Desktop is running
2. List all running containers
3. Deploy the ACMS agent to container "acms-dev"
4. Tail logs from the last 10 minutes
```

---

## 🔐 Policy Version Management

### Register New Policy Version
```
A new policy document plugin_contract_v2.json was created.

Using SQLite, insert into policy_versions:
- policy_id: [generate like "pol_002"]
- policy_name: "plugin_contract"
- version: "v2.0.0"
- git_tag: "v2.0.0-plugin-contract" 
- file_path: "/mnt/project/plugin_contract_v2.json"
- content_hash: [calculate SHA-256]
- created_by: "system"

Then using GitHub MCP, create the git tag.
```

### Query Active Policies for Run
```
From SQLite, get the policy_snapshot for run [run_id].

Parse the JSON and show:
1. Which policy versions were active
2. Are any newer versions available now?
3. Would a re-run use different policies?
```

---

## 📈 Reporting & Analytics

### Run Summary Report
```
For run [run_id], create a comprehensive report:

**Run Overview:**
- Start/end times (from run_traces)
- Final status and phase
- GitHub issue/PR links
- Total duration

**Workstream Summary:**
- Number of parallel workstreams
- Success/failure rates
- Average completion time

**Quality Gates:**
- All gate results from v_model_gates
- Any failures and resolution

**Audit Trail:**
- Total events logged
- Events by type and actor
- Any anomalies detected

**SafePatch Checkpoints:**
- Checkpoints created per phase
- Rollback availability
- Commit history

Format as Markdown with tables and graphs.
```

### Agent Performance Analysis
```
From planning_items, analyze agent performance over last 30 days:

**Jules CLI Agent:**
- Tasks completed vs assigned
- Average actual vs estimated effort
- Success rate
- Most common task types

[Repeat for Aider and Copilot agents]

Generate recommendations for future task assignments.
```

---

## 🔄 Integration Examples

### Complete Autonomous Flow
```
Orchestrate a complete autonomous development cycle for issue gh://myorg/myrepo/issues/789:

**Phase 1 - Intent:**
1. Fetch issue from GitHub MCP
2. Parse requirements using AI
3. Store in SQLite planning_items as Epic
4. Create run_trace with new ULID

**Phase 2 - Planning:**
1. Decompose Epic into Stories using Linear MCP
2. Stories into Tasks with complexity scores
3. Assign agents based on complexity
4. Store modification plans in workstreams

**Phase 3 - Execution:**
1. Create git worktrees via GitHub MCP
2. For each task, dispatch to assigned agent
3. Execute via PowerShell MCP
4. Log all actions to event_log
5. Create SafePatch checkpoints

**Phase 4 - Validation:**
1. Run V-Model gates via GitHub Actions
2. Execute conformance tests via PowerShell
3. Store results in v_model_gates table
4. Auto-fix minor issues, flag major ones

**Phase 5 - Integration:**
1. Merge successful workstreams
2. Create PR via GitHub MCP
3. Request reviews
4. Wait for approval and CI
5. Auto-merge when ready

**Phase 6 - Observability:**
1. Generate run summary report
2. Update issue with results
3. Store lessons learned in Memory MCP
4. Create new issues for follow-ups

Execute this flow and provide status updates at each phase.
```

---

## 🎯 Quick Commands Reference

### Status Checks
```
"What's the status of run [run_id]?"
"Show me all in-progress workstreams"
"List failed quality gates from the last run"
"What tasks are assigned to me (Jules CLI)?"
```

### Create Operations
```
"Create a new epic for [feature name]"
"Start a new autonomous run for issue #[number]"
"Create 3 parallel workstreams for [module modifications]"
"Log a checkpoint for phase [phase_name]"
```

### Query Operations
```
"Show me the audit trail for run [run_id]"
"What policies were active during the last run?"
"List all modules in category 'Orchestration'"
"Get performance metrics for agent Jules CLI"
```

### Integration Operations
```
"Create PRs for all completed workstreams"
"Trigger CI/CD pipeline via GitHub Actions"
"Run conformance tests for all plugins"
"Generate release notes from git commits"
```

---

## 📱 Emergency Commands

### Rollback
```
"Rollback workstream ws_1 to the last SafePatch checkpoint"
"Undo the last commit on branch feature/ws_1"
"Restore from checkpoint [checkpoint_id]"
```

### Debug
```
"Show me all errors in event_log for run [run_id]"
"What was the last action before the failure?"
"Display the complete trace for workstream ws_1"
"Check git status in all worktrees"
```

### Recovery
```
"Mark run [run_id] as failed and create recovery issue"
"Clean up all worktrees for failed run"
"Generate incident report for run [run_id]"
"Create rollback PR to restore previous state"
```

---

**Remember:** All these commands work naturally with Claude. Just describe what you want, and the MCP servers will handle the underlying operations!
