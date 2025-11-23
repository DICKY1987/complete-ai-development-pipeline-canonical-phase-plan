# CHECKLIST SYSTEM - QUICK REFERENCE

## Daily Commands

```powershell
# Run full validation
.\scripts\validate\validate_repo_checklist.ps1

# Check only infrastructure (always passes)
.\scripts\validate\validate_repo_checklist.ps1 -RequirementFilter "STATE-OBS-001,STATE-OBS-002,STATE-OBS-003,STATE-OBS-004,AUDIT-001,AUDIT-002"

# Before commit (critical checks)
.\scripts\validate\validate_repo_checklist.ps1 -RequirementFilter "ACS-ARTIFACTS-001,STATE-OBS-001"

# JSON output for CI
.\scripts\validate\validate_repo_checklist.ps1 -JsonOutput > validation.json
```

## Files You Should Know

- **.ai-orch/checklists/repo_checklist.json** - Add new requirements here
- **.state/current.json** - Current repo state (auto-updated)
- **.state/transitions.jsonl** - Audit log (append-only)
- **scripts/validate/validate_repo_checklist.ps1** - The validator
- **docs/operations/CHECKLIST_QUICK_START.md** - Full guide

## Current Status

✅ **7 checks passing** - All new infrastructure validated
❌ **2 checks failing** - Pre-existing issues (not blocking)
⚠️ **10 checks skipped** - Future enhancements

## What's Working Right Now

- Core ACS artifacts validation
- State directory structure validation
- State file validation (current.json, transitions.jsonl)
- Index files validation
- Audit documentation validation

## Quick Troubleshooting

**"Checklist file not found"**
→ Make sure you're in repo root

**"Unsupported check type"**  
→ That check isn't implemented yet (skipped, not a failure)

**"Test suite failed"**
→ Pre-existing pytest issue (tests/ast conflicts with stdlib)

**"Workstream validation failed"**
→ Pre-existing schema mismatch issue

## Adding a New Requirement

1. Edit `.ai-orch/checklists/repo_checklist.json`
2. Add requirement with unique ID
3. Test: `.\scripts\validate\validate_repo_checklist.ps1 -RequirementFilter "YOUR-ID"`

## More Help

- Quick Start: `docs/operations/CHECKLIST_QUICK_START.md`
- Full Guide: `docs/operations/REPO_CHECKLIST.md`
- Status Report: `VALIDATION_STATUS_REPORT.txt`

---
Last Updated: 2025-11-23
Version: 1.0.0
