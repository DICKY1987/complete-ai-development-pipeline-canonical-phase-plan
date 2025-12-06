# Phase 2 Plan: Real Agent Execution & GitHub API Integration

**Phase ID**: PH-AUTO-002  
**Status**: Planned  
**Dependencies**: PH-AUTO-001 (Complete ✅)  
**Estimated Effort**: 29 hours  
**Time Savings**: Enables actual functionality + 14 hours/month

---

## Objectives

Transform MASTER_SPLINTER from simulation to production-ready orchestrator by:
1. Implementing real AI tool execution (remove mock code)
2. Adding GitHub API for automated PR creation
3. Enabling scheduled execution infrastructure
4. Adding report email distribution

---

## Gaps Addressed

### GAP-003: Mock Agent Execution (CRITICAL)
**Current**: Multi-agent coordinator simulates work with `asyncio.sleep()`  
**Target**: Execute real tools (aider, codex, pytest, ruff, mypy)  
**Priority**: CRITICAL - system is non-functional without this

### GAP-004: Manual GitHub Workflow
**Current**: Script pushes branch but user creates PR manually  
**Target**: Automated PR creation via GitHub API  
**Priority**: CRITICAL - breaks automation chain

### GAP-005: No Scheduled Execution  
**Current**: User must manually run orchestrator  
**Target**: Automated daily runs via GitHub Actions  
**Priority**: HIGH - enables true automation

### GAP-007: No Automated Report Distribution
**Current**: Reports generated but not sent  
**Target**: Email/Slack notifications on completion  
**Priority**: HIGH - stakeholder visibility

---

## Implementation Steps

### Step 1: Implement Real Tool Execution (12h)

**File**: `multi_agent_workstream_coordinator.py`

**Changes**:
```python
# BEFORE (mock)
async def execute_workstream_with_agent(self, agent_id: str, workstream: Dict):
    await asyncio.sleep(0.5)  # Simulate work
    # Mock result
    
# AFTER (real)
async def execute_workstream_with_agent(self, agent_id: str, workstream: Dict):
    tool = workstream.get("tool", "claude-code")
    profile = self.get_tool_profile(tool)
    
    # Use CLIAdapter for execution
    from core import CLIAdapter
    adapter = CLIAdapter(logger=self.log)
    
    for step in workstream.get("execution_steps", []):
        result = adapter.run_command(
            step["command"],
            timeout=profile.get("timeout_seconds", 600)
        )
        
        if not result["success"]:
            raise ExecutionError(f"Step {step['id']} failed")
    
    # Track actual file modifications via git diff
    # Create real commits
    # Run real tests
```

**Testing**:
- Run orchestrator with real workstream
- Verify actual file modifications
- Verify git commits created
- Verify tests executed

**Acceptance**:
- ✅ No `asyncio.sleep()` in execution path
- ✅ Real commands executed
- ✅ Git commits created with actual changes
- ✅ Test results captured

---

### Step 2: Add GitHub API Integration (8h)

**File**: `sync_workstreams_to_github.py`

**Dependencies**:
- `pip install PyGithub`
- `GITHUB_TOKEN` environment variable

**Implementation**:
```python
from github import Github

class WorkstreamSyncEngine:
    def __init__(self):
        self.github = Github(os.environ.get("GITHUB_TOKEN"))
        # ...
    
    def create_pull_request(self, base_branch: str) -> str:
        repo = self.github.get_repo("DICKY1987/complete-ai-development-pipeline-canonical-phase-plan")
        
        pr_body = self._generate_pr_body()
        
        pr = repo.create_pull(
            title=f"Workstream Sync: {self.feature_branch}",
            body=pr_body,
            head=self.feature_branch,
            base=base_branch,
            draft=True
        )
        
        self.log_success("PR created", pr.html_url)
        return pr.html_url
```

**Testing**:
- Create test PR with --dry-run mode
- Verify PR appears in GitHub
- Verify metadata correct
- Delete test PR

**Acceptance**:
- ✅ PR created automatically after push
- ✅ PR marked as draft
- ✅ PR body contains workstream metadata
- ✅ URL returned and logged

---

### Step 3: Enable Scheduled Execution (4h)

**Files**:
- `.github/workflows/scheduled-orchestrator.yml` (already exists ✅)
- `run_master_splinter.py` (enhance with state persistence)

**Changes**:
```python
# Add state persistence to prevent re-execution
class MasterOrchestrator:
    def __init__(self):
        self.state_file = Path(".state/last_run.json")
        # ...
    
    def should_run_phase(self, phase_id: str) -> bool:
        last_run = self.load_state()
        
        # Check if already executed today
        if last_run.get(phase_id):
            last_time = datetime.fromisoformat(last_run[phase_id])
            if (datetime.now() - last_time).days < 1:
                return False  # Skip, already ran today
        
        return True
    
    def mark_phase_complete(self, phase_id: str):
        self.save_state({phase_id: datetime.now().isoformat()})
```

**Testing**:
- Trigger scheduled workflow manually
- Verify execution at 2 AM UTC
- Verify state prevents duplicate runs
- Check healthcheck ping

**Acceptance**:
- ✅ Workflow runs daily automatically
- ✅ No duplicate executions
- ✅ Healthcheck pinged on success
- ✅ Artifacts uploaded to GitHub

---

### Step 4: Add Report Email Distribution (5h)

**File**: `scripts/send_report_email.py` (new)

**Dependencies**:
- `pip install sendgrid` or use SMTP

**Implementation**:
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

def send_completion_report(report_path: Path, recipients: list):
    smtp_config = {
        "host": os.environ.get("SMTP_HOST", "smtp.gmail.com"),
        "port": int(os.environ.get("SMTP_PORT", 587)),
        "user": os.environ.get("SMTP_USER"),
        "password": os.environ.get("SMTP_PASSWORD")
    }
    
    with open(report_path) as f:
        report_content = f.read()
    
    msg = MIMEMultipart()
    msg["Subject"] = f"MASTER_SPLINTER Execution Report"
    msg["From"] = smtp_config["user"]
    msg["To"] = ", ".join(recipients)
    
    # Create HTML version
    html_body = markdown_to_html(report_content)
    msg.attach(MIMEText(html_body, "html"))
    
    with smtplib.SMTP(smtp_config["host"], smtp_config["port"]) as server:
        server.starttls()
        server.login(smtp_config["user"], smtp_config["password"])
        server.send_message(msg)
```

**Testing**:
- Send test email to yourself
- Verify HTML rendering
- Test with Gmail SMTP
- Test with Slack webhook alternative

**Acceptance**:
- ✅ Email sent on completion
- ✅ Report attached/embedded
- ✅ HTML formatting correct
- ✅ Recipients configurable

---

## Expected Artifacts

1. **Enhanced Orchestrator**: `multi_agent_workstream_coordinator.py`
   - Real tool execution (no mocks)
   - Git integration
   - Test execution

2. **GitHub API Integration**: `sync_workstreams_to_github.py`
   - PR creation method
   - PR body generation
   - Error handling

3. **Email Reporter**: `scripts/send_report_email.py`
   - SMTP integration
   - HTML email generation
   - Configuration via env vars

4. **State Persistence**: `.state/last_run.json`
   - Track execution history
   - Prevent duplicates
   - Enable incremental runs

5. **Updated Documentation**: `docs/AUTOMATION_SETUP.md`
   - GitHub token setup
   - SMTP configuration
   - Email recipient management

---

## Acceptance Tests

### Test 1: Real Execution
```powershell
# Run orchestrator with real workstream
python run_master_splinter.py

# Verify:
- Actual files modified (not mocked)
- Git commits created
- Tests executed (pytest output)
```

### Test 2: GitHub PR Creation
```powershell
python sync_workstreams_to_github.py --create-pr

# Verify in GitHub:
- PR exists
- PR is draft
- PR body has metadata
```

### Test 3: Scheduled Execution
```powershell
# Manually trigger workflow
gh workflow run scheduled-orchestrator.yml

# Verify in GitHub Actions:
- Workflow completes
- Artifacts uploaded
- Healthcheck pinged
```

### Test 4: Email Distribution
```powershell
python scripts/send_report_email.py --test

# Verify:
- Email received
- HTML renders correctly
- Report content included
```

---

## Dependencies & Prerequisites

### Environment Variables (GitHub Secrets)
- `GITHUB_TOKEN` - Personal access token with repo scope
- `HEALTHCHECK_URL` - Already configured ✅
- `SMTP_HOST` - Email server (e.g., smtp.gmail.com)
- `SMTP_PORT` - Usually 587 for TLS
- `SMTP_USER` - Email username
- `SMTP_PASSWORD` - App password (not account password)
- `REPORT_RECIPIENTS` - Comma-separated email list

### Python Packages
```
PyGithub>=2.1.0
markdown2>=2.4.0
sendgrid>=6.10.0  # Optional, for SendGrid instead of SMTP
```

### GitHub Permissions
- Personal Access Token needs:
  - `repo` - Full control of private repositories
  - `workflow` - Update GitHub Action workflows

---

## Risk Mitigation

### Risk 1: Real execution breaks existing workflows
**Mitigation**: 
- Add `--dry-run` flag to orchestrator
- Test with isolated workstreams first
- Keep mock mode as fallback option

### Risk 2: SMTP credentials compromised
**Mitigation**:
- Use app passwords (not account passwords)
- Store in GitHub Secrets (encrypted)
- Rotate regularly
- Consider SendGrid API instead

### Risk 3: Scheduled workflow runs too frequently
**Mitigation**:
- Add state persistence
- Check last run timestamp
- Skip if already ran today

### Risk 4: GitHub API rate limits
**Mitigation**:
- Check rate limit before operations
- Implement exponential backoff
- Use conditional requests (ETags)

---

## Success Metrics

After Phase 2 completion:

| Metric | Current (PH-001) | Target (PH-002) |
|--------|------------------|-----------------|
| Mock executions | 100% | 0% |
| Manual PR creation | 100% | 0% |
| Manual report checking | 100% | 0% |
| Automation coverage | 60% | 80% |
| Time savings | 45h/mo | 59h/mo (+14h) |

---

## Implementation Timeline

### Week 1 (16h)
- Day 1-2: Implement real tool execution (12h)
- Day 3: GitHub API integration (4h)

### Week 2 (13h)
- Day 1: Scheduled execution enhancement (4h)
- Day 2: Email distribution (5h)
- Day 3: Testing and documentation (4h)

**Total**: 29 hours over 2 weeks

---

## Next Phase Preview: PH-AUTO-003

**Title**: Polish & Resilience  
**Focus**: Error handling, retry logic, conflict detection  
**Effort**: 17 hours  
**Savings**: 8 hours/month  
**Target Automation**: 95%

---

## References

- Gap Analysis: `DEVELOPMENT_TEMP_DOCS/MASTER_SPLINTER_AUTOMATION_GAP_ANALYSIS.md`
- Phase 1 Report: `MASTER_SPLINTER/reports/EXECUTION_REPORT_PH-AUTO-001_*.md`
- Execution Patterns: `docs/DOC_reference/ai-agents/EXECUTION_PATTERNS_MANDATORY.md`
- GitHub API Docs: https://docs.github.com/en/rest/pulls/pulls
- SMTP Guide: https://docs.python.org/3/library/smtplib.html

---

**Status**: Ready to begin  
**Dependencies Met**: ✅ PH-AUTO-001 complete  
**Next Action**: Review and approve, then begin Step 1
