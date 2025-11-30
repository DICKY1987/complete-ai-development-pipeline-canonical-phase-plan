---
doc_id: DOC-GUIDE-ANTI-PATTERNS-CHECKLIST-193
---

# Anti-Pattern Guard Checklist

## Before Each Commit
- [ ] No TODOs in committed code
- [ ] All subprocess.run() use check=True
- [ ] All scripts have been tested
- [ ] Exit codes verified programmatically

## Before Batch Execution
- [ ] Checkpoint created after each batch
- [ ] Validation gate passes before next batch
- [ ] Dry-run completed first

## Before Final Commit
- [ ] All 11 guards passing
- [ ] No duplicate files in searches
- [ ] Worktrees cleaned up
- [ ] Documentation updated
