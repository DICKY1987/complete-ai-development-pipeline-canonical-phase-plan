# Pipeline Restructuring Toolkit - Complete

## ✅ What's Been Created

A complete, working toolkit for the PIPE-01 to PIPE-26 pipeline restructure visualization and planning.

### Files Created (6 new files)

| File | Size | Purpose |
|------|------|---------|
| **pipe_mapping_config.yaml** | 8.6 KB | Maps existing paths → 26 PIPE modules |
| **scripts/pipe_tree.py** | 10.4 KB | Virtual tree generator (Python 3.7+) |
| **scripts/pipe_classify.py** | 4.7 KB | Quick file classifier |
| **PIPELINE_VIRTUAL_TREE.txt** | 144 KB | Generated virtual tree (2,259 files) |
| **PIPELINE_VIRTUAL_TREE_README.md** | 4.8 KB | User guide & quick start |
| **PIPELINE_RESTRUCTURE_SUMMARY.md** | 6.1 KB | Analysis & recommendations |
| **PIPE_TOOLS_REFERENCE.md** | 4.4 KB | Command reference |
| **PIPELINE_MASTER_INDEX.md** | This file | Master index |

### Already Existed
- **.pipeignore** - Exclusion patterns (updated with defaults)

---

## 🚀 Quick Start (30 seconds)

```bash
# Generate the virtual tree
python scripts/pipe_tree.py --stats

# Check where a file belongs
python scripts/pipe_classify.py --verbose engine/orchestrator/core.py

# Review the output
cat PIPELINE_VIRTUAL_TREE.txt | less
```

---

## 📊 Current Analysis

**Total Files Mapped**: 2,259

**Distribution by Phase**:
- A (Intake & Specs): 95 files → 4%
- B (Workstream & Config): 128 files → 6%
- C (Patterns & Planning): 59 files → 3%
- D (Workspace & Scheduling): 47 files → 2%
- E (Execution & Validation): 189 files → 8%
- F (Error & Recovery): 130 files → 6%
- G (Finalization & Learning): 1,611 files → 71%

**Top 5 PIPE Modules**:
1. PIPE-22 (Commit Results) → 836 files (37%)
2. PIPE-26 (Learn & Update) → 708 files (31%)
3. PIPE-18 (Post-Exec Tests) → 119 files (5%)
4. PIPE-19 (Error Plugins) → 114 files (5%)
5. PIPE-02 (Discover Specs) → 78 files (3%)

---

## 📖 Documentation Map

### Start Here
1. **PIPELINE_VIRTUAL_TREE_README.md** - Full user guide
2. **PIPELINE_RESTRUCTURE_SUMMARY.md** - Analysis & next steps
3. **PIPE_TOOLS_REFERENCE.md** - Command cheat sheet

### Configuration
- **pipe_mapping_config.yaml** - Edit to adjust file classifications
- **.pipeignore** - Edit to exclude more files

### Generated Output
- **PIPELINE_VIRTUAL_TREE.txt** - Virtual directory tree (regenerate anytime)

### Original Specification
- **masssive mof.md** - Full design rationale and spec

---

## 🎯 Use Cases

### 1. Understanding Architecture
**Problem**: "Where does error detection happen?"
```bash
python scripts/pipe_classify.py modules/error-engine/error_engine.py
# → PIPE-20_CLASSIFY_ERRORS_AND_CHOOSE_ACTION
```

### 2. Planning Refactors
**Problem**: "What files are involved in workstream execution?"
```bash
grep -A 100 "PIPE-04_MATERIALIZE_WORKSTREAM" PIPELINE_VIRTUAL_TREE.txt
# See all 98 files involved
```

### 3. Onboarding New Developers
**Problem**: "What does the pipeline do, step by step?"
```bash
# Show them PIPELINE_VIRTUAL_TREE.txt
# They can see 26 concrete steps with actual code
```

### 4. Validating Mapping Rules
**Problem**: "Did my config change work?"
```bash
# Before: edit pipe_mapping_config.yaml
python scripts/pipe_tree.py --stats
# After: check PIPELINE_VIRTUAL_TREE.txt
```

---

## 🔧 Common Commands

### Generate Virtual Tree
```bash
python scripts/pipe_tree.py --stats --output PIPELINE_VIRTUAL_TREE.txt
```

### Classify Single File
```bash
python scripts/pipe_classify.py engine/orchestrator/core.py
```

### Classify Multiple Files
```bash
python scripts/pipe_classify.py \
  engine/orchestrator/core.py \
  modules/error-engine/error_engine.py \
  scripts/run_workstream.py
```

### Find All Files in One PIPE Module
```bash
grep -A 200 "PIPE-17_EXECUTE_TOOL" PIPELINE_VIRTUAL_TREE.txt
```

### Count Files per Phase
```bash
python scripts/pipe_tree.py --stats 2>&1 | grep "By phase:" -A 10
```

---

## ✨ What This Enables

### Immediate Value (No Code Changes Required)
- ✅ **Mental model** - Understand how code maps to pipeline
- ✅ **Documentation** - Reference for explaining architecture
- ✅ **Planning** - Know which files to refactor together
- ✅ **Communication** - Common vocabulary (PIPE-XX IDs)

### Medium-Term Value (With Manifests)
- ⬜ **Contracts** - Define inputs/outputs per PIPE module
- ⬜ **Dependencies** - Track inter-module dependencies
- ⬜ **Isolation** - Test PIPE modules independently
- ⬜ **Parallel work** - Multiple teams on different PIPEs

### Long-Term Value (Physical Restructure)
- ⬜ **Clarity** - Code location = conceptual model
- ⬜ **Modularity** - Self-contained PIPE modules
- ⬜ **AI-friendly** - Clear boundaries for AI reasoning
- ⬜ **Maintainability** - Easy to find and change code

---

## 🗺️ Next Steps

### Phase 1: Review & Refine (Current)
- [x] Generate initial virtual tree
- [ ] Review PIPELINE_VIRTUAL_TREE.txt
- [ ] Identify misclassified files
- [ ] Refine pipe_mapping_config.yaml
- [ ] Re-generate until satisfied

### Phase 2: Create Manifests
For each PIPE module, create a manifest:
```yaml
# Example: PIPE-17_manifest.yaml
pipe_id: PIPE-17_EXECUTE_TOOL_AND_CAPTURE_OUTPUT
phase: E_EXECUTION_AND_VALIDATION
inputs:
  - PIPE-16 (adapter selection)
  - config/router_config.json
outputs:
  - logs/
  - state/task_updates
implementation_paths:
  - engine/orchestrator/
  - aider/
  - modules/aim-environment/
```

### Phase 3: Use for Navigation
- Reference manifests in documentation
- Use PIPE-XX IDs in commit messages
- Tag issues/PRs with PIPE-XX labels
- Organize work by PIPE module

### Phase 4: Physical Migration (Optional)
Only if you decide to restructure:
1. Pick one small PIPE module
2. Create pipeline/X_*/PIPE-XX_*/ directory
3. Move files incrementally
4. Update imports
5. Test thoroughly
6. Repeat for other modules

---

## 🎓 Key Concepts

### PIPE Module
One of 26 stable execution boundaries (PIPE-01 to PIPE-26). Each represents a discrete step in the pipeline.

### Macro Phase
Grouping of related PIPE modules (A-G). Makes 26 steps easier to remember.

### Virtual Tree
Shows how repo would look if restructured, without moving any files.

### Mapping Rule
Configuration that assigns existing paths to PIPE modules.

### Manifest
YAML file describing a PIPE module's contracts and current implementation.

---

## ⚠️ Important Notes

### This is Visualization Only
- ✅ No files are moved
- ✅ No imports are changed
- ✅ No code is modified
- ✅ Safe to run anytime

### Mapping is Deterministic
- First matching rule wins
- Same input = same output
- No AI guessing or heuristics

### Configuration is Adjustable
- Edit `pipe_mapping_config.yaml` anytime
- Re-run `pipe_tree.py` to see changes
- Iterate until mapping feels right

---

## 🆘 Troubleshooting

### "No module named yaml"
```bash
pip install pyyaml
```

### Files classified incorrectly
1. Find matching rule: `python scripts/pipe_classify.py --verbose path/to/file.py`
2. Edit `pipe_mapping_config.yaml`
3. Re-run: `python scripts/pipe_tree.py --stats`

### Too many files in PIPE-26
PIPE-26 is the default bucket. Add more specific rules above it.

### Tool runs slowly
Exclude more paths in `.pipeignore` (especially large directories).

---

## 📝 Modification Examples

### Add a New Mapping Rule
Edit `pipe_mapping_config.yaml`:
```yaml
rules:
  - name: my_custom_component
    pipe_id: PIPE-17_EXECUTE_TOOL_AND_CAPTURE_OUTPUT
    match:
      path_prefix:
        - "my_component/"
      file_glob:
        - "special_*.py"
```

### Exclude More Files
Edit `.pipeignore`:
```
# My custom exclusions
temp/
scratch/
*.tmp
experimental/
```

### Change Default PIPE Module
Edit `pipe_mapping_config.yaml`:
```yaml
default_pipe_id: PIPE-24_UPDATE_METRICS_REPORTS_AND_SUMMARIES
```

---

## 🎉 Success Criteria

You've successfully set up the toolkit when:
- ✅ `python scripts/pipe_tree.py --stats` runs without errors
- ✅ `PIPELINE_VIRTUAL_TREE.txt` contains ~2,000+ files
- ✅ `python scripts/pipe_classify.py engine/orchestrator/core.py` returns a PIPE-XX ID
- ✅ You can explain which PIPE module owns any given file

---

## 📚 Resources

- **This Repository**: All tools and docs are here
- **masssive mof.md**: Original specification and design
- **GitHub Issues**: Tag with `pipeline-restructure` label
- **AI Prompts**: Reference PIPE-XX IDs for context

---

**Status**: ✅ Toolkit Complete & Ready to Use
**Created**: 2025-12-02
**Version**: 1.0
**Tools**: Python 3.7+, PyYAML
**Files Mapped**: 2,259
**PIPE Modules**: 26
**Macro Phases**: 7

---

**Questions?** See `PIPELINE_VIRTUAL_TREE_README.md` or `PIPE_TOOLS_REFERENCE.md`
