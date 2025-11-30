---
doc_id: DOC-GUIDE-QUICK-START-CHECKLIST-414
---

# Quick Start Checklist - Phase 0 Doc ID Assignment

**Goal**: Achieve 100% doc_id coverage (5.6% → 100%)  
**Time**: 3.5-4.5 hours  
**Files to Assign**: 2,726

---

## Pre-Flight (15 min)

- [ ] Backup current state
  ```bash
  git checkout -b backup-before-docid-assignment
  git checkout main
  git checkout -b feature/phase0-docid-assignment
  ```

- [ ] Verify environment
  ```bash
  python scripts/doc_id_scanner.py scan
  python scripts/doc_id_scanner.py stats
  python doc_id/tools/doc_id_registry_cli.py stats
  ```

- [ ] Create reports directory
  ```bash
  mkdir -p reports
  ```

---

## Assignment by Type (2-3 hours)

### Batch 1: YAML (15 min)
- [ ] `python scripts/doc_id_assigner.py auto-assign --types yaml yml --report reports/batch_yaml.json`
- [ ] `git add . && git commit -m "chore: Phase 0 - YAML files (~210)"`
- [ ] **Checkpoint**: ~13% coverage

### Batch 2: JSON (20 min)
- [ ] `python scripts/doc_id_assigner.py auto-assign --types json --report reports/batch_json.json`
- [ ] `git add . && git commit -m "chore: Phase 0 - JSON files (~336)"`
- [ ] **Checkpoint**: ~25% coverage

### Batch 3: PowerShell (10 min)
- [ ] `python scripts/doc_id_assigner.py auto-assign --types ps1 --report reports/batch_ps1.json`
- [ ] `git add . && git commit -m "chore: Phase 0 - PowerShell files (~143)"`
- [ ] **Checkpoint**: ~30% coverage

### Batch 4: Shell (5 min)
- [ ] `python scripts/doc_id_assigner.py auto-assign --types sh --report reports/batch_sh.json`
- [ ] `git add . && git commit -m "chore: Phase 0 - Shell scripts (~45)"`
- [ ] **Checkpoint**: ~32% coverage

### Batch 5: Text (5 min)
- [ ] `python scripts/doc_id_assigner.py auto-assign --types txt --report reports/batch_txt.json`
- [ ] `git add . && git commit -m "chore: Phase 0 - Text files (~83)"`
- [ ] **Checkpoint**: ~35% coverage

### Batch 6: Python (40 min, 5 batches)
- [ ] `python scripts/doc_id_assigner.py auto-assign --types py --limit 200 --report reports/batch_py_1.json`
- [ ] `git add . && git commit -m "chore: Phase 0 - Python batch 1 (200)"`
- [ ] `python scripts/doc_id_assigner.py auto-assign --types py --limit 200 --report reports/batch_py_2.json`
- [ ] `git add . && git commit -m "chore: Phase 0 - Python batch 2 (200)"`
- [ ] `python scripts/doc_id_assigner.py auto-assign --types py --limit 200 --report reports/batch_py_3.json`
- [ ] `git add . && git commit -m "chore: Phase 0 - Python batch 3 (200)"`
- [ ] `python scripts/doc_id_assigner.py auto-assign --types py --limit 200 --report reports/batch_py_4.json`
- [ ] `git add . && git commit -m "chore: Phase 0 - Python batch 4 (200)"`
- [ ] `python scripts/doc_id_assigner.py auto-assign --types py --report reports/batch_py_final.json`
- [ ] `git add . && git commit -m "chore: Phase 0 - Python remaining (~12)"`
- [ ] **Checkpoint**: ~63% coverage

### Batch 7: Markdown (60 min, 5 batches)
- [ ] `python scripts/doc_id_assigner.py auto-assign --types md --limit 250 --report reports/batch_md_1.json`
- [ ] `git add . && git commit -m "chore: Phase 0 - Markdown batch 1 (250)"`
- [ ] `python scripts/doc_id_assigner.py auto-assign --types md --limit 250 --report reports/batch_md_2.json`
- [ ] `git add . && git commit -m "chore: Phase 0 - Markdown batch 2 (250)"`
- [ ] `python scripts/doc_id_assigner.py auto-assign --types md --limit 250 --report reports/batch_md_3.json`
- [ ] `git add . && git commit -m "chore: Phase 0 - Markdown batch 3 (250)"`
- [ ] `python scripts/doc_id_assigner.py auto-assign --types md --limit 250 --report reports/batch_md_4.json`
- [ ] `git add . && git commit -m "chore: Phase 0 - Markdown batch 4 (250)"`
- [ ] `python scripts/doc_id_assigner.py auto-assign --types md --report reports/batch_md_final.json`
- [ ] `git add . && git commit -m "chore: Phase 0 - Markdown remaining (~100)"`
- [ ] **Checkpoint**: ~100% coverage 🎉

---

## Validation (30 min)

- [ ] Final scan
  ```bash
  python scripts/doc_id_scanner.py scan
  python scripts/doc_id_scanner.py stats
  ```

- [ ] Verify 100% coverage
  ```bash
  # Should show: Files with doc_id: 2888 (100.0%)
  ```

- [ ] Validate registry
  ```bash
  python doc_id/tools/doc_id_registry_cli.py validate
  python doc_id/tools/doc_id_registry_cli.py stats
  ```

- [ ] Spot check files
  ```bash
  python scripts/doc_id_scanner.py check "core\engine\orchestrator.py"
  python scripts/doc_id_scanner.py check "docs\DOC_ID_FRAMEWORK.md"
  python scripts/doc_id_scanner.py check "config\QUALITY_GATE.yaml"
  ```

---

## Documentation (30 min)

- [ ] Update `scripts/SCRIPT_INDEX.yaml`
  - Add doc_id_scanner entry
  - Add doc_id_assigner entry

- [ ] Update `README.md`
  - Add Doc ID System section
  - Note 100% coverage

- [ ] Create `CHANGELOG.md` entry
  - Document Phase 0 completion
  - List tools added

- [ ] Final commit
  ```bash
  git add .
  git commit -m "chore: Phase 0 doc_id - complete (100% coverage)
  
  - Assigned doc_ids to 2,726 files
  - Coverage: 5.6% → 100%
  - Registry: 274 → ~3,160 docs
  - Tools: scanner, assigner, cheatsheet"
  ```

---

## Merge & Deploy (15 min)

- [ ] Switch to main
  ```bash
  git checkout main
  ```

- [ ] Merge feature branch
  ```bash
  git merge feature/phase0-docid-assignment --no-ff
  ```

- [ ] Push to remote
  ```bash
  git push origin main
  ```

- [ ] Tag release (optional)
  ```bash
  git tag -a v1.0.0-docid-phase0 -m "Phase 0: 100% doc_id coverage"
  git push origin v1.0.0-docid-phase0
  ```

- [ ] Clean up branches
  ```bash
  git branch -d feature/phase0-docid-assignment
  # Keep backup branch for safety
  ```

---

## Success Verification

**Final checks**:
- [ ] Coverage = 100% (2,888/2,888 files)
- [ ] Registry validates with 0 errors
- [ ] No duplicate doc_ids
- [ ] All commits pushed
- [ ] Documentation updated

---

## Time Breakdown

| Task | Duration | Commits |
|------|----------|---------|
| Pre-flight | 15 min | 1 |
| YAML/JSON/Scripts | 50 min | 5 |
| Python files | 40 min | 5 |
| Markdown files | 60 min | 5 |
| Validation | 30 min | 0 |
| Documentation | 30 min | 1 |
| Merge | 15 min | 1 |
| **TOTAL** | **3h 40m** | **18** |

---

## Alternative: Fast Track (1 hour)

Skip batches, assign everything at once:

```bash
# Backup
git checkout -b backup-before-docid-assignment
git checkout -b feature/phase0-docid-fast

# Assign all
python scripts/doc_id_assigner.py auto-assign --report reports/full_assignment.json

# Validate
python scripts/doc_id_scanner.py scan
python scripts/doc_id_scanner.py stats
python doc_id/tools/doc_id_registry_cli.py validate

# Commit & merge
git add .
git commit -m "chore: Phase 0 doc_id complete (100% coverage)"
git checkout main
git merge feature/phase0-docid-fast --no-ff
git push origin main
```

**Pros**: Fast  
**Cons**: Massive commit, harder to review/rollback

---

**Start here**: Begin with Pre-Flight checklist above ⬆️
