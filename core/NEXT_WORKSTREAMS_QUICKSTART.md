---
doc_id: DOC-CORE-NEXT-WORKSTREAMS-QUICKSTART-630
---

# Next Workstreams - Quick Start Guide
# DOC_LINK: DOC-GUIDE-NEXT-WORKSTREAMS-2025-12-02

## 🚀 Quick Start - Next Workstreams

### Prerequisites
- Git repository clean (`git status` should show no uncommitted changes)
- GitHub CLI authenticated (`gh auth status`)
- Python 3.10+ installed
- PowerShell 7+ installed (for GitHub sync)

---

## Option 1: Manual Execution (Recommended for First Time)

### Step 1: GitHub Project Integration (30-60 min)
```bash
# 1. Create GitHub Project
gh project create --owner @me --title "UET Next Workstreams"
# Note the project number (e.g., 42)

# 2. Sync phase plan to GitHub
pwsh scripts/Invoke-UetPhasePlanToGitHubProjectSync.ps1 \
  -PlanPath plans/NEXT_WORKSTREAMS_PHASE_PLAN.yaml \
  -ProjectNumber 42 \
  -DryRun  # First run dry-run to preview

# 3. Execute actual sync
pwsh scripts/Invoke-UetPhasePlanToGitHubProjectSync.ps1 \
  -PlanPath plans/NEXT_WORKSTREAMS_PHASE_PLAN.yaml \
  -ProjectNumber 42

# 4. Verify in GitHub UI
gh project view 42

# 5. Document results
# See workstreams/ws-next-001-github-project-integration.json for validation steps
```

### Step 2: Fix Reachability Analyzer (1-2 hours)
```bash
# See workstreams/ws-next-002-fix-reachability-analyzer.json
# Manual implementation required (code changes needed)
```

### Step 3: Test Coverage (Ongoing)
```bash
# Run coverage baseline
pytest --cov=. --cov-report=term --cov-report=html

# See workstreams/ws-next-003-test-coverage-improvement.json for weekly plan
```

### Step 4: UET Framework Review (1 hour)
```bash
# See workstreams/ws-next-005-uet-framework-review.json
# Manual review required
```

### Step 5: REFACTOR_2 Execution (3-5 days)
```bash
# BLOCKED until WS-NEXT-001 and WS-NEXT-002 complete
# See workstreams/ws-next-004-refactor-2-execution.json
```

---

## Option 2: Automated Execution (After Scripts Implemented)

### Run All Workstreams
```bash
# Dry run to preview
python scripts/execute_next_workstreams.py --dry-run

# Execute all (stops on failure)
python scripts/execute_next_workstreams.py

# Force continue on failure
python scripts/execute_next_workstreams.py --force
```

### Run Specific Workstream
```bash
python scripts/execute_next_workstreams.py \
  --workstream ws-next-001-github-project-integration
```

### Check Status
```bash
# Generate status report
python scripts/track_workstream_status.py --report

# Save report to file
python scripts/track_workstream_status.py \
  --report \
  --output reports/NEXT_WORKSTREAMS_STATUS.md
```

### Update Status Manually
```bash
python scripts/track_workstream_status.py \
  --update ws-next-001-github-project-integration completed "Validation successful"
```

---

## Dependency Graph

```
┌─────────────────────────────────────────────────┐
│ INDEPENDENT (Can Run in Parallel)               │
├─────────────────────────────────────────────────┤
│ ✅ WS-NEXT-001: GitHub Project Integration      │
│ ✅ WS-NEXT-002: Fix Reachability Analyzer       │
│ ✅ WS-NEXT-003: Test Coverage (ongoing)         │
│ ✅ WS-NEXT-005: UET Framework Review            │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ DEPENDENT (Requires WS-NEXT-001 + WS-NEXT-002)  │
├─────────────────────────────────────────────────┤
│ 🔒 WS-NEXT-004: REFACTOR_2 Execution            │
└─────────────────────────────────────────────────┘
```

---

## Recommended Execution Order

### Solo Developer
1. **TODAY**: Git push + take break ✅
2. **Tomorrow** (fresh): WS-NEXT-001 (GitHub integration)
3. **Day 2**: WS-NEXT-002 (Analyzer fix)
4. **Day 3**: WS-NEXT-005 (UET review)
5. **Week 1-4**: WS-NEXT-003 (Test coverage, ongoing)
6. **Week 2**: WS-NEXT-004 (REFACTOR_2, 3-5 dedicated days)

### Team (Parallel Work)
- **Person A**: WS-NEXT-001 (GitHub integration)
- **Person B**: WS-NEXT-002 (Analyzer fix)
- **Person C**: WS-NEXT-005 (UET review)
- **QA Team**: WS-NEXT-003 (Test coverage, ongoing)
- **Lead Dev**: WS-NEXT-004 (After A+B complete)

---

## Success Criteria

### WS-NEXT-001: GitHub Project Integration
- [ ] GitHub Project created
- [ ] Phase plan synced successfully
- [ ] gh_item_id values in YAML
- [ ] Time savings documented
- [ ] Report: `reports/GITHUB_PROJECT_VALIDATION_REPORT.md`

### WS-NEXT-002: Fix Reachability Analyzer
- [ ] Entry points updated (tests/, tools/, templates/)
- [ ] Cross-validation implemented
- [ ] False positives reduced
- [ ] Tests pass
- [ ] Report: `reports/ANALYZER_FIX_VALIDATION.md`

### WS-NEXT-003: Test Coverage
- [ ] Coverage >= 10% overall
- [ ] Core engine >= 30%
- [ ] Error plugins >= 25%
- [ ] Weekly reports generated

### WS-NEXT-004: REFACTOR_2
- [ ] All 39 workstreams completed
- [ ] All tests pass
- [ ] CI gates pass
- [ ] Documentation updated
- [ ] Report: `reports/REFACTOR_2_COMPLETION_REPORT.md`

### WS-NEXT-005: UET Framework Review
- [ ] Template inventory complete
- [ ] Usage patterns documented
- [ ] Orphaned templates identified
- [ ] Report: `reports/UET_FRAMEWORK_REVIEW.md`

---

## Monitoring & Tracking

### View Status in GitHub
```bash
gh project view <project_number>
```

### View Local Status
```bash
python scripts/track_workstream_status.py --report
```

### View Workstream Details
```bash
cat workstreams/ws-next-001-github-project-integration.json | jq
```

---

## Troubleshooting

### GitHub CLI Not Authenticated
```bash
gh auth login
gh auth status
```

### PowerShell Script Won't Run
```bash
# Enable execution policy
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### Python Script Missing Dependencies
```bash
pip install -r requirements.txt
```

### Workstream Blocked
```bash
# Check dependencies
python scripts/track_workstream_status.py --report

# Force execution (ignore dependencies)
python scripts/execute_next_workstreams.py --force
```

---

## Next Steps After Completion

1. Review all deliverables
2. Update main documentation
3. Archive completed workstreams
4. Plan next iteration (if needed)
5. Celebrate! 🎉

---

## File Locations

- **Workstream Definitions**: `workstreams/ws-next-*.json`
- **Phase Plan**: `plans/NEXT_WORKSTREAMS_PHASE_PLAN.yaml`
- **Execution Scripts**: `scripts/execute_next_workstreams.py`
- **Status Tracker**: `scripts/track_workstream_status.py`
- **Status Data**: `state/workstream_status.json`
- **Reports**: `reports/`

---

## Quick Commands Cheatsheet

```bash
# Create GitHub Project
gh project create --owner @me --title "UET Next Workstreams"

# Sync to GitHub
pwsh scripts/Invoke-UetPhasePlanToGitHubProjectSync.ps1 -PlanPath plans/NEXT_WORKSTREAMS_PHASE_PLAN.yaml -ProjectNumber <N>

# Execute workstreams
python scripts/execute_next_workstreams.py [--dry-run] [--workstream <ID>]

# Check status
python scripts/track_workstream_status.py --report

# Run tests
pytest --cov=. --cov-report=term

# Validate CI
python scripts/paths_index_cli.py gate --db refactor_paths.db
```
