# Archival Validation Checklist

**Generated**: 2025-12-02 04:28:52
**Pattern**: EXEC-017

## Pre-Archive Validation

- [ ] Review comprehensive_archival_report.json
- [ ] Review parallel_implementations_decision_checklist.md
- [ ] Review Tier 1 candidates (90%+ confidence)
- [ ] Run pre-archive validation:
  ```bash
  python scripts/validate_archival_safety.py --mode pre-archive
  ```
- [ ] Git status clean (no uncommitted changes)
- [ ] Test suite passing:
  ```bash
  pytest -q tests/
  ```

## Execution

- [ ] Run Tier 1 script in DRY RUN mode:
  ```powershell
  .\cleanup_reports\archival_plan_tier1_automated.ps1
  ```
- [ ] Review dry run output
- [ ] If satisfied, edit script: Set `$DryRun = $false`
- [ ] Execute archival

## Post-Archive Validation

- [ ] Run post-archive validation:
  ```bash
  python scripts/validate_archival_safety.py --mode post-archive
  ```
- [ ] Test suite still passing:
  ```bash
  pytest -q tests/
  ```
- [ ] No import errors
- [ ] Entry points functional
- [ ] Git status check:
  ```bash
  git status
  ```

## Commit

- [ ] Review changes
- [ ] Commit with pattern-compliant message:
  ```bash
  git add .
  git commit -m "chore: Archive obsolete Python code (Tier 1 - EXEC-017)

  Archived N files based on comprehensive 6-signal analysis
  Pattern: EXEC-017
  Confidence: 90-100%
  Configuration: 90-day staleness, 90% threshold

  All validation checks passed"
  ```

## Rollback (if needed)

- [ ] Option 1: Git revert
  ```bash
  git revert HEAD
  ```
- [ ] Option 2: Restore from archive
  ```bash
  # Copy files back from archive directory
  ```
