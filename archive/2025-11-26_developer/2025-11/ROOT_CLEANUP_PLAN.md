---
doc_id: DOC-GUIDE-ROOT-CLEANUP-PLAN-1127
---

# Root Directory Cleanup Plan

> **Purpose**: Document reorganization of root-level files  
> **Created**: 2025-11-22  
> **Status**: In Progress

---

## Current State

27 loose markdown/text files in root directory (should be ~7 core files).

## Target State

**Core Root Files** (keep in root):
- README.md
- AGENTS.md
- DIRECTORY_GUIDE.md
- QUICK_START.md
- LICENSE (if exists)
- CHANGELOG.md (if exists)
- .gitignore
- requirements.txt
- Other config files (.env.example, pytest.ini, etc.)

**Everything else** should be in appropriate subdirectories.

---

## File Movement Plan

### Session Reports → `docs/sessions/`
- SESSION_SUMMARY_2025-11-19.md

### Tool-Specific Notes → `docs/reference/tools/`
- CLAUDE.md
- GEMINI.md
- Invoke_POWERSHELLGALLERY.md

### AI/Development Guidelines → `docs/reference/`
- AI_DEV_HYGIENE_GUIDELINES.md (keep in root or move to docs/)
- CLI_TOOL_UPDATES.md
- CLI_TOOL_UPDATES_PROMPT.xml

### Proposed/Planning Documents → `docs/planning/` or `meta/`
- PROPOSED_DIRECTORY_TREE.md

### Technical Analysis → `docs/architecture/` or `docs/analysis/`
- Data Flow Analysis.md
- LOCAL_DIR_CLASSIFICATION.txt

### Tool/Task-Specific → Appropriate tool directories or docs/
- Task-enqueue script (pushes tasks to Aider).md → `aider/docs/` or `docs/tools/`
- apply edits without asking you every time.md → `docs/reference/`
- workstream-style" prompt structure.md → `docs/reference/` or `specifications/docs/`
- first place (per-tool headless contract.md → `docs/reference/`
- id file consolidation checker.md → `docs/maintenance/` or `tools/docs/`

### Duplicates/Unclear (investigate and handle)
- "1ollama code installed and configred on this machine.md"
- "ollama code installed and configred on this machine.md"
- "ollama-code IS installed in WSL.txt"
- "new 1.txt"

These appear to be:
- Installation notes (should be in docs/setup/ or removed if duplicates)
- Check if duplicates of each other

### Inventory/Maintenance Files → `docs/maintenance/` or archive
- legacy_inventory.txt
- repo_maint.txt
- pipeline_plus_structure_BEFORE_20251120_125719.txt
- file_inventory_pipeline_plus_20251120.csv

### AI Manager/Handoff → `aim/docs/` or `docs/integration/`
- AI_MANGER_AIM_HANDOFF.txt

---

## Actions

### Phase 1: Create Target Directories
- [x] docs/sessions/
- [x] docs/reference/
- [x] docs/archive/
- [ ] docs/reference/tools/
- [ ] docs/planning/
- [ ] docs/maintenance/
- [ ] docs/analysis/
- [ ] aider/docs/

### Phase 2: Move Files
- [ ] Move session reports
- [ ] Move tool-specific docs
- [ ] Move planning docs
- [ ] Move technical analysis
- [ ] Move maintenance files

### Phase 3: Handle Duplicates
- [ ] Identify duplicate ollama files
- [ ] Identify purpose of "new 1.txt"
- [ ] Consolidate or remove

### Phase 4: Update References
- [ ] Search for references to moved files
- [ ] Update links in documentation
- [ ] Update .gitignore if needed

### Phase 5: Verify
- [ ] Check all moved files are in correct locations
- [ ] Verify no broken links
- [ ] Update DIRECTORY_GUIDE.md if needed

---

## Notes

- Some files may be better deleted if they're truly obsolete/duplicates
- Keep AI_DEV_HYGIENE_GUIDELINES.md decision for later (useful in root?)
- Verify with user before deleting any files
- Create README.md files in new directories to explain contents
