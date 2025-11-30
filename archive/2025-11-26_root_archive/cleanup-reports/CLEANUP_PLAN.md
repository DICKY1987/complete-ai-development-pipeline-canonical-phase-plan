---
doc_id: DOC-GUIDE-CLEANUP-PLAN-1138
---

# Repository Cleanup Plan - 2025-11-23

## Analysis Summary

**Total Size**: ~22 MB  
**Total Files**: ~1,500  
**Top Issues**:
1. Cache files (5 MB)
2. Duplicate/stale prototype directories
3. Root-level temp/chat files
4. Archived legacy folders not compressed

---

## Cleanup Actions

### 🗑️ IMMEDIATE DELETE (Safe - Regenerable/Cached)

#### 1. Aider Cache (5 MB)
```bash
rm -rf .aider.tags.cache.v4/
```
**Reason**: Auto-generated cache, will regenerate on next Aider run

#### 2. Root-level temp/chat files
```bash
rm ".sync-log.txt"
rm "successfully installed a bunch of Python refactoring tools.txt"
rm "VALIDATION_STATUS_REPORT.txt"
rm "clude explain to github.txt"
rm "2025-11-22-find-the-main-excution-scripts-move-the-procees.txt"
rm "main execution scriptmodif.txt"
rm "test_sync.txt"
```
**Reason**: Temporary session files, not part of codebase

---

### 📦 ARCHIVE (Compress & Move)

#### 3. PROCESS_DEEP_DIVE_OPTOMIZE/ (0.86 MB, 51 files)
```bash
# This appears to be completed research/analysis
tar -czf legacy/PROCESS_DEEP_DIVE_OPTOMIZE_archived_2025-11-23.tar.gz PROCESS_DEEP_DIVE_OPTOMIZE/
rm -rf PROCESS_DEEP_DIVE_OPTOMIZE/
```
**Reason**: Historical data collection, no active development

#### 4. AGENTIC_DEV_PROTOTYPE/ (1.38 MB, 144 files)
```bash
# Old prototype, superseded by current core/
tar -czf legacy/AGENTIC_DEV_PROTOTYPE_archived_2025-11-23.tar.gz AGENTIC_DEV_PROTOTYPE/
rm -rf AGENTIC_DEV_PROTOTYPE/
```
**Reason**: Early prototype, functionality moved to `core/`

#### 5. Prompt/ (0.40 MB, 15 files)
```bash
# Generic prompt templates, move to docs
mv Prompt/ docs/prompt-templates/
git add docs/prompt-templates/
```
**Reason**: Should be in docs/, not root

---

### 🔄 REORGANIZE (Move to Correct Location)

#### 6. UET Chat Files
```bash
# Move chat files to docs/scratch/ per DOC-ORG-SPEC
cd UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK
mv "chat 2.md" ../docs/scratch/uet_chat_2025-11-22.md
mv "claude chat.txt" ../docs/scratch/uet_claude_chat_2025-11-22.txt
mv "CLAUDE_CHAT_UTE.txt" ../docs/scratch/uet_claude_chat_detailed_2025-11-22.txt
```

#### 7. Root-level spec files (should be in specs/)
```bash
# Already handled by our doc reorg plan
# Will be moved when we apply doc_move_plan.jsonl
```

---

### ✅ KEEP (Active/Required)

#### Keep these directories:
- `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/` - Active framework
- `core/` - Production code
- `tests/` - Test suite
- `docs/` - Documentation
- `devdocs/` - Development documentation (organized)
- `aim/`, `pm/`, `ccpm/` - Active modules
- `meta/` - Phase development docs
- `scripts/` - Utility scripts
- `legacy/` - Proper archive location

---

## Execution Order

### Phase 1: Safe Deletes (No Risk)
```powershell
cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"

# Delete cache
Remove-Item -Recurse -Force .aider.tags.cache.v4

# Delete temp files
Remove-Item ".sync-log.txt"
Remove-Item "successfully installed a bunch of Python refactoring tools.txt"
Remove-Item "VALIDATION_STATUS_REPORT.txt"
Remove-Item "clude explain to github.txt"
Remove-Item "2025-11-22-find-the-main-excution-scripts-move-the-procees.txt"
Remove-Item "main execution scriptmodif.txt"
Remove-Item "test_sync.txt"

git status
```

### Phase 2: Archive Old Prototypes
```powershell
# Compress and archive
tar -czf legacy/PROCESS_DEEP_DIVE_OPTOMIZE_archived_2025-11-23.tar.gz PROCESS_DEEP_DIVE_OPTOMIZE/
tar -czf legacy/AGENTIC_DEV_PROTOTYPE_archived_2025-11-23.tar.gz AGENTIC_DEV_PROTOTYPE/

# Remove originals
Remove-Item -Recurse -Force PROCESS_DEEP_DIVE_OPTOMIZE
Remove-Item -Recurse -Force AGENTIC_DEV_PROTOTYPE

git add legacy/*.tar.gz
git status
```

### Phase 3: Reorganize Prompts
```powershell
# Move to docs
New-Item -ItemType Directory -Path docs/prompt-templates -Force
Move-Item Prompt/* docs/prompt-templates/
Remove-Item Prompt

git add docs/prompt-templates/
git rm -r Prompt/
git status
```

### Phase 4: Move UET Chat Files
```powershell
cd UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK

# Move to docs/scratch
Move-Item "chat 2.md" ../docs/scratch/uet_chat_2025-11-22.md -Force
Move-Item "claude chat.txt" ../docs/scratch/uet_claude_chat_2025-11-22.txt -Force
Move-Item "CLAUDE_CHAT_UTE.txt" ../docs/scratch/uet_claude_chat_detailed_2025-11-22.txt -Force

cd ..
git add docs/scratch/
git status
```

### Phase 5: Commit Cleanup
```powershell
git commit -m "chore: Repository cleanup - remove cache, archive prototypes, reorganize

- Removed: .aider.tags.cache.v4/ (5 MB auto-generated cache)
- Removed: 7 root-level temp/chat files
- Archived: PROCESS_DEEP_DIVE_OPTOMIZE/ → legacy/ (0.86 MB)
- Archived: AGENTIC_DEV_PROTOTYPE/ → legacy/ (1.38 MB)
- Moved: Prompt/ → docs/prompt-templates/
- Moved: UET chat files → docs/scratch/

Total space saved: ~7 MB
Total files removed/archived: ~200

See CLEANUP_PLAN.md for details."
```

---

## Expected Results

### Before Cleanup:
```
Root files: ~20 files (8 temp/chat)
Directories: 30
Total size: ~22 MB
```

### After Cleanup:
```
Root files: ~12 files (all required)
Directories: 28 (-2 archived)
Total size: ~15 MB (-7 MB)
Archived: 2.24 MB compressed to ~0.5 MB
```

### Benefits:
1. ✅ Cleaner root directory (no temp files)
2. ✅ Reduced repo size by 32%
3. ✅ Better organization (docs in docs/)
4. ✅ Archived prototypes preserved but out of the way
5. ✅ Follows DOC-ORG-SPEC structure

---

## Risk Assessment

| Action | Risk | Mitigation |
|--------|------|------------|
| Delete cache | None | Regenerates automatically |
| Delete temp files | None | Session outputs, not code |
| Archive prototypes | Low | Compressed archives kept in legacy/ |
| Move prompts | None | Git tracks rename |
| Move UET chats | None | Follows DOC-ORG-SPEC |

**Overall Risk**: **LOW** - All changes are git-tracked and reversible

---

## Rollback Plan

If issues arise:
```powershell
# Undo last commit
git reset --soft HEAD~1

# Restore from archives
cd legacy
tar -xzf PROCESS_DEEP_DIVE_OPTOMIZE_archived_2025-11-23.tar.gz -C ..
tar -xzf AGENTIC_DEV_PROTOTYPE_archived_2025-11-23.tar.gz -C ..
```

---

**Approved for execution**: ⏸️ Awaiting confirmation  
**Estimated time**: 5 minutes  
**Space savings**: ~7 MB (32% reduction)
