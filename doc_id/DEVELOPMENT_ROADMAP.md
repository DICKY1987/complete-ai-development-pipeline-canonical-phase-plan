# Complete Development Roadmap - Doc ID Phase 0 Auto-Assignment

**Generated**: 2025-11-30  
**Current Status**: Core implementation complete, ready for full deployment  
**Estimated Time to 100% Coverage**: 2-4 hours

---

## Current State

### ✅ Completed

1. **Core Scripts Created**
   - `scripts/doc_id_scanner.py` (341 lines)
   - `scripts/doc_id_assigner.py` (550 lines)
   - `doc_id/ID_KEY_CHEATSHEET.md` (305 lines)
   - `doc_id/COMPLETE_IMPLEMENTATION_REPORT.md` (478 lines)
   - `doc_id/SCRIPTS_DISCOVERY_SUMMARY.md` (205 lines)

2. **Integration Fixed**
   - Modified `doc_id/tools/doc_id_registry_cli.py` (registry path corrected)

3. **Testing Validated**
   - Scanner: ✅ Full repository scan (6,285 files)
   - Assigner: ✅ 3 files successfully assigned
   - Coverage tracking: ✅ Verified (5.5% → 5.6%)
   - Registry integration: ✅ Working (271 → 274 docs)

4. **Current Coverage**: 162/2,888 files (5.6%)

### ⏳ Remaining Work

- **2,726 files** still need doc_ids
- **94.4% of repository** unassigned

---

## Complete Steps to 100% Coverage

### Phase 1: Pre-Flight Validation (15 minutes)

#### Step 1.1: Verify Environment
```bash
# Ensure you're in repo root
cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"

# Check Python version
python --version  # Should be 3.8+

# Verify registry exists
python doc_id/tools/doc_id_registry_cli.py stats
```

**Expected Output**:
```
Total docs: 274
Total categories: 12
Last updated: 2025-11-30
```

#### Step 1.2: Backup Current State
```bash
# Create backup branch
git checkout -b backup-before-docid-assignment

# Commit current state
git add .
git commit -m "chore: backup before Phase 0 doc_id mass assignment"

# Return to main/master
git checkout main  # or master
```

#### Step 1.3: Baseline Scan
```bash
# Full repository scan
python scripts/doc_id_scanner.py scan

# Review statistics
python scripts/doc_id_scanner.py stats
```

**Expected Output**:
```
Total eligible files:      2888
Files with doc_id:          162 (  5.6%)
Files missing doc_id:      2726 ( 94.4%)
```

#### Step 1.4: Create Work Branch
```bash
git checkout -b feature/phase0-docid-assignment
```

---

### Phase 2: Incremental Assignment (2-3 hours)

**Strategy**: Assign by file type in batches to review changes incrementally.

#### Step 2.1: YAML Files (Highest Coverage)
```bash
# Preview
python scripts/doc_id_assigner.py auto-assign --dry-run --types yaml yml --limit 10

# Assign all YAML files
python scripts/doc_id_assigner.py auto-assign --types yaml yml --report reports/batch_yaml.json

# Review changes
git diff --stat

# Scan to verify
python scripts/doc_id_scanner.py scan
python scripts/doc_id_scanner.py stats
```

**Expected**:
- ~210 YAML files assigned
- Coverage: 5.6% → ~13%

**Checkpoint**:
```bash
git add .
git commit -m "chore: Phase 0 doc_id - assign YAML files (~210 files)"
```

#### Step 2.2: JSON Files
```bash
# Assign JSON files
python scripts/doc_id_assigner.py auto-assign --types json --report reports/batch_json.json

# Verify
python scripts/doc_id_scanner.py scan
python scripts/doc_id_scanner.py stats

# Commit
git add .
git commit -m "chore: Phase 0 doc_id - assign JSON files (~336 files)"
```

**Expected**:
- ~336 JSON files assigned
- Coverage: ~13% → ~25%

#### Step 2.3: PowerShell Files
```bash
# Assign PowerShell files
python scripts/doc_id_assigner.py auto-assign --types ps1 --report reports/batch_ps1.json

# Verify
python scripts/doc_id_scanner.py scan
python scripts/doc_id_scanner.py stats

# Commit
git add .
git commit -m "chore: Phase 0 doc_id - assign PowerShell files (~143 files)"
```

**Expected**:
- ~143 PS1 files assigned
- Coverage: ~25% → ~30%

#### Step 2.4: Shell Scripts
```bash
# Assign shell scripts
python scripts/doc_id_assigner.py auto-assign --types sh --report reports/batch_sh.json

# Verify
python scripts/doc_id_scanner.py scan
python scripts/doc_id_scanner.py stats

# Commit
git add .
git commit -m "chore: Phase 0 doc_id - assign Shell scripts (~45 files)"
```

**Expected**:
- ~45 SH files assigned
- Coverage: ~30% → ~32%

#### Step 2.5: Text Files
```bash
# Assign text files
python scripts/doc_id_assigner.py auto-assign --types txt --report reports/batch_txt.json

# Verify
python scripts/doc_id_scanner.py scan
python scripts/doc_id_scanner.py stats

# Commit
git add .
git commit -m "chore: Phase 0 doc_id - assign text files (~83 files)"
```

**Expected**:
- ~83 TXT files assigned
- Coverage: ~32% → ~35%

#### Step 2.6: Python Files (Large Batch - Use Limits)
```bash
# Assign Python files in batches of 200
python scripts/doc_id_assigner.py auto-assign --types py --limit 200 --report reports/batch_py_1.json
git add . && git commit -m "chore: Phase 0 doc_id - assign Python batch 1 (200 files)"

python scripts/doc_id_assigner.py auto-assign --types py --limit 200 --report reports/batch_py_2.json
git add . && git commit -m "chore: Phase 0 doc_id - assign Python batch 2 (200 files)"

python scripts/doc_id_assigner.py auto-assign --types py --limit 200 --report reports/batch_py_3.json
git add . && git commit -m "chore: Phase 0 doc_id - assign Python batch 3 (200 files)"

python scripts/doc_id_assigner.py auto-assign --types py --limit 200 --report reports/batch_py_4.json
git add . && git commit -m "chore: Phase 0 doc_id - assign Python batch 4 (200 files)"

# Assign remaining Python files
python scripts/doc_id_assigner.py auto-assign --types py --report reports/batch_py_final.json
git add . && git commit -m "chore: Phase 0 doc_id - assign Python remaining (~12 files)"
```

**Expected**:
- ~812 PY files assigned
- Coverage: ~35% → ~63%

#### Step 2.7: Markdown Files (Largest Batch - Use Limits)
```bash
# Assign Markdown files in batches of 250
python scripts/doc_id_assigner.py auto-assign --types md --limit 250 --report reports/batch_md_1.json
git add . && git commit -m "chore: Phase 0 doc_id - assign Markdown batch 1 (250 files)"

python scripts/doc_id_assigner.py auto-assign --types md --limit 250 --report reports/batch_md_2.json
git add . && git commit -m "chore: Phase 0 doc_id - assign Markdown batch 2 (250 files)"

python scripts/doc_id_assigner.py auto-assign --types md --limit 250 --report reports/batch_md_3.json
git add . && git commit -m "chore: Phase 0 doc_id - assign Markdown batch 3 (250 files)"

python scripts/doc_id_assigner.py auto-assign --types md --limit 250 --report reports/batch_md_4.json
git add . && git commit -m "chore: Phase 0 doc_id - assign Markdown batch 4 (250 files)"

# Assign remaining Markdown files
python scripts/doc_id_assigner.py auto-assign --types md --report reports/batch_md_final.json
git add . && git commit -m "chore: Phase 0 doc_id - assign Markdown remaining (~100 files)"
```

**Expected**:
- ~1,100 MD files assigned
- Coverage: ~63% → ~100%

---

### Phase 3: Final Validation (30 minutes)

#### Step 3.1: Complete Coverage Scan
```bash
# Final scan
python scripts/doc_id_scanner.py scan

# Check statistics
python scripts/doc_id_scanner.py stats
```

**Expected Output**:
```
Total eligible files:      2888
Files with doc_id:         2888 ( 100.0%)
Files missing doc_id:         0 (   0.0%)
```

#### Step 3.2: Registry Validation
```bash
# Validate all doc_ids
python doc_id/tools/doc_id_registry_cli.py validate

# Check registry stats
python doc_id/tools/doc_id_registry_cli.py stats
```

**Expected Output**:
```
Total docs: ~3160  (274 existing + 2886 new)
No validation errors
```

#### Step 3.3: Spot Check Files
```bash
# Check a few random files
python scripts/doc_id_scanner.py check "core\engine\orchestrator.py"
python scripts/doc_id_scanner.py check "docs\DOC_ID_FRAMEWORK.md"
python scripts/doc_id_scanner.py check "config\QUALITY_GATE.yaml"
```

**Expected**: All should show `Status: present` with valid doc_ids

#### Step 3.4: Generate Final Report
```bash
# Create completion report
python scripts/doc_id_scanner.py scan > reports/final_coverage_report.txt
python doc_id/tools/doc_id_registry_cli.py stats > reports/final_registry_stats.txt
```

---

### Phase 4: Integration & Documentation (30 minutes)

#### Step 4.1: Update SCRIPT_INDEX.yaml
```bash
# Edit scripts/SCRIPT_INDEX.yaml to add new scripts
# Add doc_id_management section (see SCRIPTS_DISCOVERY_SUMMARY.md)
```

**Add this section**:
```yaml
doc_id_management:
  - doc_id: DOC-SCRIPT-DOC-ID-SCANNER-045
    name: doc_id_scanner
    file: scripts/doc_id_scanner.py
    language: python
    purpose: "Scan repository for doc_id coverage and generate inventory"
    usage: "python scripts/doc_id_scanner.py scan"
    priority: high
    
  - doc_id: DOC-SCRIPT-DOC-ID-ASSIGNER-046
    name: doc_id_assigner
    file: scripts/doc_id_assigner.py
    language: python
    purpose: "Auto-assign doc_ids to files missing them"
    usage: "python scripts/doc_id_assigner.py auto-assign"
    priority: high
```

#### Step 4.2: Update Main README
```bash
# Add section to README.md
```

**Add**:
```markdown
## Doc ID System

All files in this repository have unique doc_ids for tracking and cross-referencing.

- **Coverage**: 100% (2,888/2,888 files)
- **Registry**: `doc_id/specs/DOC_ID_REGISTRY.yaml`
- **Tools**: 
  - Scanner: `python scripts/doc_id_scanner.py`
  - Assigner: `python scripts/doc_id_assigner.py`
  - Registry CLI: `python doc_id/tools/doc_id_registry_cli.py`

See `doc_id/ID_KEY_CHEATSHEET.md` for complete documentation.
```

#### Step 4.3: Create CHANGELOG Entry
```bash
# Add to CHANGELOG.md (create if doesn't exist)
```

**Entry**:
```markdown
## [Unreleased] - 2025-11-30

### Added
- Phase 0 doc_id auto-assignment system
  - `scripts/doc_id_scanner.py`: Repository scanning tool
  - `scripts/doc_id_assigner.py`: Automated doc_id assignment
  - `doc_id/ID_KEY_CHEATSHEET.md`: Complete reference guide
  - Achieved 100% doc_id coverage (2,888 files)
  - Registry expanded from 274 to ~3,160 entries
```

#### Step 4.4: Final Commit
```bash
git add .
git commit -m "chore: Phase 0 doc_id - complete (100% coverage achieved)

- Assigned doc_ids to 2,726 files
- Coverage: 5.6% → 100%
- Registry: 274 → 3,160 docs
- All file types covered (py, md, yaml, json, ps1, sh, txt)
- No validation errors

Tools added:
- scripts/doc_id_scanner.py (coverage tracking)
- scripts/doc_id_assigner.py (auto-assignment)
- doc_id/ID_KEY_CHEATSHEET.md (documentation)

Refs: #[issue_number] (if applicable)"
```

---

### Phase 5: Merge & Deployment (15 minutes)

#### Step 5.1: Pre-Merge Checks
```bash
# Ensure clean working directory
git status

# Run any existing tests
# (Add your test commands here)

# Final validation
python doc_id/tools/doc_id_registry_cli.py validate
```

#### Step 5.2: Merge to Main
```bash
# Switch to main
git checkout main  # or master

# Merge feature branch
git merge feature/phase0-docid-assignment --no-ff

# Push to remote
git push origin main
```

#### Step 5.3: Tag Release (Optional)
```bash
git tag -a v1.0.0-docid-phase0 -m "Phase 0: Doc ID 100% coverage achieved"
git push origin v1.0.0-docid-phase0
```

#### Step 5.4: Clean Up
```bash
# Delete feature branch (local)
git branch -d feature/phase0-docid-assignment

# Delete backup branch (after confirming merge success)
git branch -d backup-before-docid-assignment

# Clean up reports (optional - or keep for audit trail)
# rm -rf reports/batch_*.json
```

---

## Alternative: Faster Single-Pass Assignment (1 hour)

If you want to complete faster with less incremental commits:

```bash
# Step 1: Backup
git checkout -b backup-before-docid-assignment
git checkout -b feature/phase0-docid-assignment

# Step 2: Assign everything at once
python scripts/doc_id_assigner.py auto-assign --report reports/full_assignment.json

# Step 3: Verify
python scripts/doc_id_scanner.py scan
python scripts/doc_id_scanner.py stats
python doc_id/tools/doc_id_registry_cli.py validate

# Step 4: Commit
git add .
git commit -m "chore: Phase 0 doc_id - complete (100% coverage)"

# Step 5: Merge
git checkout main
git merge feature/phase0-docid-assignment --no-ff
git push origin main
```

**Pros**: Fast, simple  
**Cons**: Massive commit, harder to review, harder to rollback partially

---

## Monitoring & Validation Commands

### During Assignment
```bash
# Check progress
python scripts/doc_id_scanner.py stats

# View recent assignments
tail -n 20 docs_inventory.jsonl

# Check registry size
python doc_id/tools/doc_id_registry_cli.py stats | grep "Total docs"

# Check for errors
python doc_id/tools/doc_id_registry_cli.py validate
```

### After Completion
```bash
# Verify 100% coverage
python scripts/doc_id_scanner.py stats | grep "Files with doc_id"

# List any remaining missing files
python scripts/doc_id_scanner.py scan
grep '"status": "missing"' docs_inventory.jsonl

# Check registry health
python doc_id/tools/doc_id_registry_cli.py validate
```

---

## Rollback Procedures

### Partial Rollback (Undo Last Batch)
```bash
git reset HEAD~1  # Undo last commit
git checkout .    # Discard changes
```

### Full Rollback (Return to Pre-Assignment State)
```bash
git checkout backup-before-docid-assignment
git branch -D feature/phase0-docid-assignment  # Delete work branch
git checkout -b feature/phase0-docid-assignment  # Start fresh
```

### Emergency Recovery
```bash
# If main was already pushed
git revert HEAD  # Create revert commit
git push origin main
```

---

## Expected Outcomes

### Before Phase 0
- **Coverage**: 5.6% (162/2,888)
- **Registry**: 274 docs
- **Status**: Minimal tracking

### After Phase 0
- **Coverage**: 100% (2,888/2,888)
- **Registry**: ~3,160 docs
- **Status**: Full tracking across all eligible files

### Benefits Achieved
1. ✅ Every file has unique identifier
2. ✅ Cross-referencing enabled
3. ✅ Refactoring safety (files tracked through moves)
4. ✅ Documentation linking
5. ✅ Audit trail foundation
6. ✅ CI/CD integration ready

---

## Post-Completion Enhancements

### Optional Improvements

1. **CI Integration**
   ```yaml
   # .github/workflows/doc_id_validation.yml
   - name: Validate doc_id coverage
     run: |
       python scripts/doc_id_scanner.py scan
       python scripts/doc_id_scanner.py stats
       python doc_id/tools/doc_id_registry_cli.py validate
   ```

2. **Pre-commit Hook**
   ```bash
   # .git/hooks/pre-commit
   #!/bin/bash
   python scripts/doc_id_scanner.py check $(git diff --cached --name-only)
   ```

3. **Coverage Badge**
   - Add to README.md
   - Update via GitHub Actions
   - Display current percentage

4. **Documentation Generator**
   - Auto-generate cross-reference docs
   - Link files via doc_ids
   - Create dependency graphs

---

## Timeline Summary

| Phase | Duration | Commits | Files Modified |
|-------|----------|---------|----------------|
| 1. Pre-flight | 15 min | 1 | 0 |
| 2. Assignment | 2-3 hrs | 15-20 | ~2,726 |
| 3. Validation | 30 min | 0 | 0 |
| 4. Documentation | 30 min | 1 | 3-5 |
| 5. Merge | 15 min | 1 | 0 |
| **TOTAL** | **3.5-4.5 hrs** | **18-23** | **~2,735** |

---

## Success Criteria Checklist

- [ ] All 2,888 eligible files have doc_ids (100% coverage)
- [ ] Registry validates with no errors
- [ ] No duplicate doc_ids exist
- [ ] All file types properly embedded
- [ ] SCRIPT_INDEX.yaml updated
- [ ] README.md updated with doc_id section
- [ ] CHANGELOG.md entry created
- [ ] All commits have meaningful messages
- [ ] Feature branch merged to main
- [ ] Remote repository updated
- [ ] Backup branch kept (optional, for safety)

---

## Support & Troubleshooting

### Common Issues

**Issue**: "Registry not found"  
**Solution**: Check path in `doc_id/tools/doc_id_registry_cli.py` line 30

**Issue**: "Validation failed - duplicate doc_id"  
**Solution**: Run `python doc_id/tools/doc_id_registry_cli.py validate` to identify duplicates

**Issue**: "File type not eligible"  
**Solution**: Add extension to `ELIGIBLE_EXTENSIONS` in `scripts/doc_id_scanner.py`

**Issue**: "Name too long for doc_id"  
**Solution**: Increase truncation limit in `scripts/doc_id_assigner.py` line 206

### Getting Help

- Check `doc_id/ID_KEY_CHEATSHEET.md`
- Review `doc_id/COMPLETE_IMPLEMENTATION_REPORT.md`
- See `doc_id/SCRIPTS_DISCOVERY_SUMMARY.md`

---

**Ready to Begin**: Follow Phase 1, Step 1.1 above to start! 🚀
