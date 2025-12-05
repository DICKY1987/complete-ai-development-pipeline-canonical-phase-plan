---
doc_id: DOC-SCRIPT-README-334
---

# Safe Merge Scripts

**Purpose**: Scripts implementing safe merge pattern operations.

**Status**: Active

---

## Contents

| Script | Purpose |
|--------|---------|
| `merge_env_scan.ps1` | Phase 0: Scan merge environment |
| `safe_merge_auto.ps1` | Phase 1-6: Automated safe merge |
| `safe_pull_and_push.ps1` | Safe pull and push operations |
| `merge_file_classifier.py` | Classify files for merge strategy |
| `multi_clone_guard.py` | Guard against multi-clone issues |
| `nested_repo_detector.py` | Detect nested repositories |
| `nested_repo_normalizer.py` | Normalize nested repository structure |
| `sync_log_summary.py` | Generate sync log summaries |

---

## Usage

### Phase 0: Environment Scan

```powershell
.\merge_env_scan.ps1 -BaseBranch "main" -FeatureBranch "feature/xyz"
```

### Phase 1-6: Full Safe Merge

```powershell
.\safe_merge_auto.ps1 `
    -BaseBranch "main" `
    -FeatureBranch "feature/xyz" `
    -AllowAutoPush $true
```

---

## Related

- `../README.md` - Safe merge pattern documentation
- `../QUICKSTART.md` - Quick start guide
- `../../automation/` - Automation utilities
