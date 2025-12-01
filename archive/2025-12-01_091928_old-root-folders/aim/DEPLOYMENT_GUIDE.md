---
doc_id: DOC-AIM-DEPLOYMENT-GUIDE-086
---

# AIM Module - Production Deployment Guide

**Version:** 1.0-RC1  
**Date:** 2025-11-20  
**Status:** Ready for Staging Deployment

---

## Overview

This guide provides step-by-step instructions for deploying the AIM module to production, testing with real workstreams, and gathering feedback. The module is at **95% production readiness** and ready for real-world validation.

---

## Pre-Deployment Checklist

### ✅ Prerequisites
- [x] All 34 tests passing (100% unit, 100% integration)
- [x] AIM registry configured at `aim/.AIM_ai-tools-registry/`
- [x] Coordination rules defined for 5 capabilities
- [x] PowerShell adapters enhanced with timeout/retry
- [x] Orchestrator integration complete
- [x] Backward compatibility verified
- [x] Documentation complete

### ⚠️ Environment Requirements
- [ ] Python 3.10+ installed
- [ ] PowerShell 7.0+ available (for adapters)
- [ ] PyYAML>=6.0 installed (`pip install PyYAML`)
- [ ] At least one AI tool installed (aider, jules, or claude-cli)
- [ ] Access to repository with write permissions
- [ ] Git configured for the environment

### 📋 Recommended Tools Installation
```bash
# Install at least one AI coding tool

# Option 1: Aider (recommended for testing)
pip install aider-chat

# Option 2: Jules (requires account)
# Download from jules.ai and run: jules login

# Option 3: Claude CLI (requires API key)
# npm install -g @anthropic-ai/claude-cli
# claude login
```

---

## Phase 1: Deploy to Staging (Day 1)

**Duration:** 2-4 hours  
**Goal:** Validate AIM works in staging environment

### Step 1.1: Environment Setup (30 min)

```bash
# Navigate to repository
cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"

# Activate virtual environment (if using)
.\.venv\Scripts\Activate.ps1

# Verify dependencies
pip install -r requirements.txt

# Run all AIM tests to verify environment
python -m pytest tests/pipeline/test_aim_bridge.py tests/integration/test_aim_*.py -v
```

**Expected Output:**
```
34 passed, 4 skipped
```

**Troubleshooting:**
- If tests fail, check PyYAML is installed: `pip show PyYAML`
- If import errors, ensure you're in repository root
- If registry errors, verify `aim/.AIM_ai-tools-registry/` exists

---

### Step 1.2: Verify AIM Registry (15 min)

```bash
# Check AIM status
python scripts/aim_status.py
```

**Expected Output:**
```
AIM Registry Path: C:\...\aim\.AIM_ai-tools-registry

Tool ID              Detected     Version
======================================================================
aider                Yes/No       aider 0.x.x (if installed)
jules                Yes/No       N/A
claude-cli           Yes/No       N/A

Capability Routing:
======================================================================
code_generation:
  Primary:  jules
  Fallback: aider, claude-cli
```

**Action Items:**
- ✅ If at least one tool detected → Proceed
- ⚠️ If no tools detected → Install aider: `pip install aider-chat`
- ⚠️ If tools require login → Run: `jules login` or `claude login`

---

### Step 1.3: Configuration Review (15 min)

**Review:** `config/aim_config.yaml`

```yaml
# Verify settings are appropriate for staging
enable_aim: true
enable_audit_logging: true
audit_log_retention_days: 30
default_timeout_ms: 30000
registry_path: "auto"
```

**Recommended Staging Adjustments:**
```yaml
# Increase timeout for slower staging environments
default_timeout_ms: 60000  # 60 seconds

# Enable verbose audit logging
enable_audit_logging: true
```

**Review:** `aim/.AIM_ai-tools-registry/AIM_cross-tool/AIM_coordination-rules.json`

Verify capabilities are configured correctly:
- `code_generation` - Primary: jules, Fallback: aider, claude-cli
- `linting` - Primary: ruff, Fallback: pylint
- `refactoring` - Primary: aider, Fallback: claude-cli
- `testing` - Primary: pytest
- `version_checking` - Primary: aider, Fallback: jules, claude-cli

---

### Step 1.4: Create Test Workstream (30 min)

**Create:** `workstreams/staging_test/ws-aim-validation.json`

```json
{
  "id": "ws-aim-validation-001",
  "openspec_change": "AIM-VALIDATION-001",
  "ccpm_issue": 1,
  "gate": 1,
  "files_scope": ["tests/staging_test_file.py"],
  "files_create": ["tests/staging_test_file.py"],
  "tasks": [
    "Create a simple Python function that adds two numbers",
    "Add a docstring explaining the function",
    "Add basic error handling for non-numeric inputs"
  ],
  "acceptance_tests": [
    "Function should accept two numbers and return their sum",
    "Function should have a clear docstring",
    "Function should raise TypeError for non-numeric inputs"
  ],
  "depends_on": [],
  "tool": "aider",
  "capability": "code_generation",
  "capability_payload": {
    "prompt": "Create a simple add(a, b) function with error handling and docstring",
    "files": ["tests/staging_test_file.py"],
    "timeout_ms": 60000,
    "max_retries": 1
  },
  "metadata": {
    "purpose": "AIM staging validation",
    "created_by": "deployment_script",
    "created_at": "2025-11-20T21:30:00Z"
  }
}
```

**Key Points:**
- ✅ Uses `capability: "code_generation"` (new AIM routing)
- ✅ Specifies `tool: "aider"` as fallback
- ✅ Includes `capability_payload` with custom timeout
- ✅ Creates new file (low risk)

---

### Step 1.5: Run Test Workstream (1-2 hours)

```bash
# Run the test workstream
python scripts/run_workstream.py workstreams/staging_test/ws-aim-validation.json
```

**Monitor Output:**
Look for these log messages:
```
[INFO] Executing capability 'code_generation' via AIM
[INFO] AIM routing to primary tool: jules
[WARNING] Jules requires login (run 'jules login')  # If jules not set up
[INFO] Falling back to direct tool invocation: aider
[INFO] Code generation completed (attempt 1)
```

**Success Indicators:**
- ✅ File `tests/staging_test_file.py` created
- ✅ Contains `add(a, b)` function
- ✅ Has docstring
- ✅ Has error handling
- ✅ Audit log created in `aim/.AIM_ai-tools-registry/AIM_audit/`

**Failure Handling:**
If workstream fails, check:
1. Orchestrator logs: `logs/orchestrator.log`
2. AIM audit logs: `aim/.AIM_ai-tools-registry/AIM_audit/YYYY-MM-DD/`
3. Tool availability: `python scripts/aim_status.py`

---

### Step 1.6: Verify Audit Logs (15 min)

```bash
# Query audit logs
python scripts/aim_audit_query.py --capability code_generation --since 2025-11-20

# Check specific tool
python scripts/aim_audit_query.py --tool aider
```

**Expected Audit Log Entry:**
```json
{
  "timestamp": "2025-11-20T21:45:00.000000Z",
  "actor": "pipeline",
  "tool_id": "aider",
  "capability": "code_generation",
  "payload": {
    "prompt": "Create a simple add(a, b) function...",
    "files": ["tests/staging_test_file.py"],
    "timeout_ms": 60000
  },
  "result": {
    "success": true,
    "message": "Code generation completed (attempt 1)",
    "content": {
      "files_modified": [],
      "files_created": ["tests/staging_test_file.py"],
      "exit_code": 0
    }
  }
}
```

**Validation:**
- ✅ Timestamp is correct
- ✅ Tool used matches expectation
- ✅ Payload captured correctly
- ✅ Result shows success
- ✅ Files tracked correctly

---

## Phase 2: Test with Real Workstreams (Days 2-3)

**Duration:** 1-2 days  
**Goal:** Validate AIM with actual development workstreams

### Step 2.1: Identify Candidate Workstreams (1 hour)

**Criteria for Good Candidates:**
- ✅ Low-risk (non-critical features)
- ✅ Well-defined scope (clear files, tasks)
- ✅ Suitable for code_generation capability
- ⚠️ Avoid: Production-critical code
- ⚠️ Avoid: Complex multi-file refactors (start simple)

**Recommended Candidates:**
1. Adding unit tests to existing modules
2. Adding docstrings to functions
3. Creating utility functions
4. Simple bug fixes with clear reproduction steps

---

### Step 2.2: Convert Workstream to Use Capability (30 min)

**Original Workstream:**
```json
{
  "id": "ws-add-logging",
  "tool": "aider",
  "files_scope": ["src/app.py"],
  "tasks": ["Add structured logging"]
}
```

**Enhanced with Capability:**
```json
{
  "id": "ws-add-logging",
  "tool": "aider",  // Keep as fallback
  "capability": "code_generation",  // ADD THIS
  "capability_payload": {  // ADD THIS
    "prompt": "Add structured logging using Python logging module",
    "files": ["src/app.py"],
    "timeout_ms": 90000,
    "max_retries": 1
  },
  "files_scope": ["src/app.py"],
  "tasks": ["Add structured logging"]
}
```

**Migration Checklist:**
- [ ] Add `capability` field (e.g., "code_generation")
- [ ] Add `capability_payload` with:
  - [ ] `prompt` - Clear, specific instruction
  - [ ] `files` - List of files to modify
  - [ ] `timeout_ms` - Appropriate for task complexity
  - [ ] `max_retries` - 0-2 based on reliability needs
- [ ] Keep `tool` field as fallback
- [ ] Test schema validation: `python scripts/validate_workstreams.py`

---

### Step 2.3: Run and Monitor (per workstream)

```bash
# Run workstream with increased logging
PYTHONPATH=. python -m core.engine.orchestrator workstreams/ws-add-logging.json --verbose

# Or use standard script
python scripts/run_workstream.py workstreams/ws-add-logging.json
```

**Monitoring Checklist:**
- [ ] AIM routing logged (INFO level)
- [ ] Primary tool attempt logged
- [ ] Fallback triggered (if primary fails)
- [ ] Execution time within timeout
- [ ] Files modified correctly
- [ ] No unexpected errors
- [ ] Audit log created

**After Each Run:**
1. Review generated code quality
2. Check audit logs for errors
3. Verify fallback behavior (if triggered)
4. Note performance (execution time)
5. Document any issues

---

### Step 2.4: Create Feedback Log (ongoing)

**Create:** `aim/STAGING_FEEDBACK.md`

Template:
```markdown
# AIM Staging Feedback Log

## Workstream: ws-add-logging
**Date:** 2025-11-20  
**Capability:** code_generation  
**Tool Used:** aider (fallback from jules)

### What Worked
- Capability routing successful
- Fallback worked when jules required login
- Audit log captured all details
- Generated code quality: Good

### Issues Encountered
- Jules authentication required (expected)
- Timeout of 60s too short for complex file (needed 90s)

### Recommendations
- Increase default timeout for code_generation to 90s
- Add better error message for auth requirements

### Code Quality: 4/5
- Clean implementation
- Good docstrings
- Minor: Could use more specific variable names

---
```

**Track:**
- Success rate (X/Y workstreams succeeded)
- Average execution time
- Fallback frequency (how often primary fails)
- Tool preference (which tool used most)
- Error categories (auth, timeout, tool error)

---

## Phase 3: Monitor Audit Logs (Ongoing)

**Duration:** Continuous during staging  
**Goal:** Identify patterns, issues, optimization opportunities

### Step 3.1: Daily Audit Review (15 min/day)

```bash
# Today's activity
python scripts/aim_audit_query.py --since $(date -I)

# Success rate by capability
python scripts/aim_audit_query.py --capability code_generation | grep -c "success.*true"

# Failures only
python scripts/aim_audit_query.py --format json | jq 'select(.result.success == false)'
```

**Metrics to Track:**
| Metric | Target | Action if Below |
|--------|--------|-----------------|
| Success Rate | >80% | Review failure reasons |
| Avg Execution Time | <60s | Check for hangs/timeouts |
| Fallback Rate | <30% | Improve primary tool setup |
| Auth Errors | <10% | Document login process |

---

### Step 3.2: Identify Patterns (weekly)

**Analyze:**
1. **Most used capability** - Which capability gets most traffic?
2. **Most reliable tool** - Which tool has highest success rate?
3. **Common failure modes** - Auth? Timeout? Tool errors?
4. **Performance bottlenecks** - Which capability is slowest?

**Example Analysis:**
```bash
# Group by tool
python scripts/aim_audit_query.py --format json | \
  jq -r '.tool_id' | sort | uniq -c | sort -rn

# Average execution time by capability
python scripts/aim_audit_query.py --format json | \
  jq -r '[.capability, .result.content.duration_sec] | @csv'
```

**Action Items from Patterns:**
- If jules fails frequently → Document login process better
- If timeouts common → Increase default timeout
- If specific files slow → Optimize file scope
- If aider most reliable → Consider making it primary

---

### Step 3.3: Security Review (weekly)

**Check Audit Logs For:**
- ✅ No secrets in prompts or payloads
- ✅ No forbidden paths accessed (/.git/, /.env)
- ✅ File patterns within whitelist
- ✅ Payload sizes under 1MB limit

```bash
# Check for potential secrets
python scripts/aim_audit_query.py --format json | \
  grep -iE "(password|api_key|secret|token)" || echo "✓ No secrets found"

# Check for forbidden path attempts
python scripts/aim_audit_query.py --format json | \
  grep -E "(/\.git/|/\.env)" || echo "✓ No forbidden paths"
```

**If Issues Found:**
1. Document in `aim/SECURITY_INCIDENTS.md`
2. Review coordination rules security section
3. Add validation if needed
4. Notify team

---

## Phase 4: Gather User Feedback (Ongoing)

**Duration:** Throughout staging period  
**Goal:** Collect developer experience feedback

### Step 4.1: Create Feedback Survey

**Questions for Developers:**
1. How easy was it to add `capability` to your workstream? (1-5)
2. Did AIM select the right tool for your task? (Yes/No)
3. How would you rate the generated code quality? (1-5)
4. Were error messages helpful? (1-5)
5. Did fallback behavior work as expected? (Yes/No)
6. Would you recommend AIM routing to others? (Yes/No)
7. What could be improved?

**Collect Feedback:**
- Create issue template: `.github/ISSUE_TEMPLATE/aim_feedback.md`
- Add feedback form: `aim/FEEDBACK_FORM.md`
- Schedule 1:1 with users of workstreams
- Monitor #pipeline Slack channel (if applicable)

---

### Step 4.2: Feedback Categories

**Track Feedback in Categories:**

**1. Ease of Use:**
- Schema clarity (capability vs tool)
- Documentation quality
- Migration difficulty

**2. Reliability:**
- Success rate perception
- Fallback transparency
- Error message clarity

**3. Code Quality:**
- Output quality by tool
- Consistency across runs
- Need for manual fixes

**4. Performance:**
- Execution time acceptable?
- Timeout settings appropriate?
- Retry logic helpful?

---

### Step 4.3: Weekly Feedback Review

**Schedule:** Friday afternoon, 30 min

**Review:**
1. Feedback submissions this week
2. Common themes/patterns
3. Blockers or critical issues
4. Quick wins (easy improvements)

**Action Items:**
- Update documentation based on confusion
- Adjust default timeouts if needed
- Improve error messages for common failures
- Celebrate successes (share positive feedback)

---

## Phase 5: Optional Phase 4 Polish (Days 4-5)

**Duration:** 2 days (only if feedback indicates need)  
**Goal:** Refinements based on real-world usage

### Decide: Run Phase 4 If...
- ⚠️ Success rate < 70%
- ⚠️ User satisfaction < 3/5
- ⚠️ Common pain points identified
- ⚠️ Performance issues observed

### Skip Phase 4 If...
- ✅ Success rate > 85%
- ✅ User satisfaction > 4/5
- ✅ No critical issues
- ✅ Minor feedback only

---

### Phase 4 Tasks (If Needed)

**Documentation (2 hours)**
- [ ] Update `docs/ARCHITECTURE.md` with AIM integration diagrams
- [ ] Add troubleshooting section based on real issues
- [ ] Create migration guide with real workstream examples
- [ ] Document common pitfalls and solutions

**Performance (4 hours)**
- [ ] Add registry caching with TTL (reduce file I/O)
- [ ] Implement async adapter invocation (parallel fallbacks)
- [ ] Optimize subprocess handling (reuse processes)
- [ ] Add performance benchmarks

**Security (2 hours)**
- [ ] Implement input validation in bridge (before routing)
- [ ] Add audit log integrity checks (SHA256 hashes)
- [ ] Implement payload sanitization (strip secrets)
- [ ] Security scan of adapter scripts

**Maintenance (2 hours)**
- [ ] Implement audit log pruning (retention policy)
- [ ] Create adapters for ruff and pytest
- [ ] Add health check endpoint
- [ ] Create monitoring dashboard

---

## Success Criteria

### MVP Success (Required for Production)
- [x] 34/34 tests passing
- [ ] 10+ real workstreams tested in staging
- [ ] >80% success rate with real workstreams
- [ ] <5% critical errors requiring manual intervention
- [ ] User satisfaction >3.5/5
- [ ] No security incidents
- [ ] Documentation complete and accurate

### Full Production Success (Ideal)
- [ ] 20+ real workstreams tested
- [ ] >90% success rate
- [ ] User satisfaction >4/5
- [ ] Average execution time <45 seconds
- [ ] Fallback rate <20%
- [ ] Zero security incidents
- [ ] Positive feedback from majority of users

---

## Rollback Plan

### When to Rollback
- ⛔ Critical security issue discovered
- ⛔ Success rate drops below 50%
- ⛔ Data loss or corruption occurs
- ⛔ Team consensus to revert

### Rollback Procedure

**Step 1: Stop New Workstreams (5 min)**
```bash
# Disable AIM in configuration
# Edit config/aim_config.yaml
enable_aim: false
```

**Step 2: Revert Orchestrator Changes (10 min)**
```bash
# Revert to pre-AIM version
git revert <commit-hash-of-aim-integration>

# Or manual revert: Remove capability check from orchestrator.py
# Lines 76-100 in run_edit_step()
```

**Step 3: Update Workstreams (variable)**
```bash
# Remove capability fields from active workstreams
# They will fall back to direct tool invocation
```

**Step 4: Communicate (15 min)**
- Post in team channel
- Update documentation with rollback status
- Document reason for rollback
- Plan corrective actions

---

## Timeline Summary

| Phase | Duration | Key Activities |
|-------|----------|----------------|
| **Phase 1: Staging Setup** | 2-4 hours | Environment, test workstream, verify |
| **Phase 2: Real Workstreams** | 1-2 days | 10+ workstreams, monitor, document |
| **Phase 3: Monitoring** | Ongoing | Daily audit review, weekly analysis |
| **Phase 4: Feedback** | Ongoing | Surveys, 1:1s, issue tracking |
| **Phase 5: Polish** | 2 days (optional) | Based on feedback, optimize |

**Total:** 3-5 days to production-ready, or 5-7 days with optional polish

---

## Go/No-Go Decision Criteria

### Go to Production If:
- ✅ Success rate >80% in staging
- ✅ No critical bugs or security issues
- ✅ User feedback mostly positive (>3.5/5)
- ✅ Performance acceptable (<60s avg)
- ✅ Fallback behavior working reliably
- ✅ Audit logs capturing correctly
- ✅ Documentation complete

### Stay in Staging If:
- ⚠️ Success rate 60-80% (needs improvement)
- ⚠️ Minor bugs but workarounds exist
- ⚠️ User feedback mixed (2.5-3.5/5)
- ⚠️ Performance acceptable but not optimal
- ⚠️ Need more data (< 10 workstreams tested)

### Rollback to Development If:
- ⛔ Success rate <60%
- ⛔ Critical bugs or security issues
- ⛔ User feedback negative (<2.5/5)
- ⛔ Fundamental design issues discovered
- ⛔ Data loss or corruption

---

## Contact and Escalation

### For Questions:
- **Documentation:** `aim/README.md` - Full user guide
- **Troubleshooting:** `aim/README.md` Section "Troubleshooting"
- **Architecture:** `aim/PRODUCTION_READINESS_ANALYSIS.md`

### For Issues:
- **GitHub Issues:** Label with `aim-module` and `staging`
- **Slack:** #pipeline channel (if applicable)
- **Email:** pipeline-team@example.com (update as needed)

### Escalation Path:
1. **Level 1:** Check `aim/README.md` Troubleshooting
2. **Level 2:** Review audit logs + staging feedback
3. **Level 3:** Post in team channel with details
4. **Level 4:** Escalate to tech lead if blocking

---

## Appendix A: Useful Commands

```bash
# Check AIM status
python scripts/aim_status.py

# Run all tests
python -m pytest tests/pipeline/test_aim_bridge.py tests/integration/test_aim_*.py -v

# Validate workstream schema
python scripts/validate_workstreams.py workstreams/my-workstream.json

# Run single workstream
python scripts/run_workstream.py workstreams/my-workstream.json

# Query audit logs (today)
python scripts/aim_audit_query.py --since $(date -I)

# Query by tool
python scripts/aim_audit_query.py --tool aider

# Query by capability
python scripts/aim_audit_query.py --capability code_generation

# Export to CSV
python scripts/aim_audit_query.py --format csv > audit_report.csv

# Check for errors
python scripts/aim_audit_query.py --format json | jq 'select(.result.success == false)'
```

---

## Appendix B: Example Staging Workstreams

See `workstreams/staging_test/` directory for examples:
- `ws-aim-validation.json` - Simple function creation
- `ws-add-docstrings.json` - Add docstrings to module
- `ws-add-tests.json` - Generate unit tests
- `ws-refactor-simple.json` - Simple refactoring task

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-20  
**Author:** AI Development Pipeline Team  
**Status:** Ready for Use

For the latest version, see: `aim/DEPLOYMENT_GUIDE.md`
