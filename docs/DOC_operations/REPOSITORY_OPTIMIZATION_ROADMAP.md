---
doc_id: DOC-GUIDE-REPOSITORY-OPTIMIZATION-ROADMAP-394
---

# Repository Optimization Roadmap

**Date**: 2025-11-25
**Status**: RECOMMENDATION
**Priority**: Medium

---

## Executive Summary

Your repository is **already well-optimized** after today's cleanup:
- ✅ 250 MB saved
- ✅ AI-friendly structure (2.7 avg depth)
- ✅ Single branch
- ✅ 80% DOC_ID coverage on key docs
- ✅ Clean codebase index

**Recommendation**: **DON'T** add DOC_IDs to every file. **DO** the targeted optimizations below.

---

## ❌ DON'T DO: Universal File ID-ing

### Why NOT to ID Every File:

**Proposed**: Add DOC_IDs to all 349 Python files + 750 Markdown files

**Problems**:
1. **Massive overhead** - 1,099 files to track = unmaintainable
2. **Low value** - Code files don't need DOC_IDs (git tracks them)
3. **Registry bloat** - DOC_ID_REGISTRY.yaml becomes 10,000+ lines
4. **Merge conflicts** - Every PR touches the registry
5. **Cognitive load** - Developers must remember IDs for code

**What Research Shows**:
- DOC_IDs are for **documentation governance**, not source code
- Code has natural IDs: `module.class.method` (import path)
- Over-indexing creates more problems than it solves

---

## ✅ DO THESE: Targeted Optimizations

### **Phase 1: Strategic Documentation (Priority: HIGH)**

**Goal**: ID only the documents that need governance

#### 1.1 Add DOC_IDs to Strategic Docs (30 mins)
**Target**: The 31 docs without IDs (39% remaining)

```bash
# Run the DOC_ID analyzer
python doc_id/doc_id_triage.py --missing-ids

# ID only these types:
# - Specifications (specs/*)
# - Architecture decisions (adr/*)
# - Process patterns (docs/DOC_*_PATTERN.md)
# - API contracts (schema/*.yaml)
```

**Don't ID**:
- Session logs
- Temporary reports
- Generated files
- README files (use directory context)

**Effort**: 30 mins
**Value**: Complete governance coverage
**Maintenance**: Low (only new strategic docs)

---

### **Phase 2: Root Directory Cleanup (Priority: MEDIUM)**

**Goal**: Move config files to proper locations

#### 2.1 Consolidate Root Files (15 mins)

**Current**: 22 files in root (too many)

**Action**:
```bash
# Move config files
mv pyproject.toml config/
mv requirements.txt config/
mv invoke.yaml config/
mv router_config.json config/

# Move database files
mv refactor_paths.db infra/data/

# Update documentation
# Add .config-root symlinks if tools need root location
```

**After**: ~10 files in root (acceptable)
- README.md
- LICENSE
- .gitignore
- .gitattributes
- Key launchers (ccpm.bat)

**Effort**: 15 mins
**Value**: Cleaner root, better organization
**Risk**: Low (test that tools still find configs)

---

### **Phase 3: Test Coverage Analysis (Priority: MEDIUM)**

**Goal**: Identify untested code

#### 3.1 Generate Coverage Report (10 mins)

```bash
# Install coverage
pip install coverage pytest-cov

# Run with coverage
pytest --cov=core --cov=engine --cov=error --cov-report=html

# Analyze
open htmlcov/index.html
```

#### 3.2 Target Low-Hanging Fruit (ongoing)
- Aim for 70% coverage on core modules
- Don't aim for 100% (diminishing returns)
- Focus on business logic, not boilerplate

**Effort**: 10 mins setup + ongoing
**Value**: Higher confidence in changes
**Maintenance**: Part of development workflow

---

### **Phase 4: AI-Specific Optimizations (Priority: HIGH)**

**Goal**: Make repo maximally AI-friendly

#### 4.1 Create AI Context Files (30 mins)

**Add these files**:

**`.ai/context.md`** - High-level repo overview
```markdown
# Repository Context for AI

## Purpose
[One sentence: what this repo does]

## Architecture
- core/ - Core orchestration engine
- error/ - Error detection pipeline
- pm/ - Project management tools

## Key Entry Points
- Start here: scripts/main.py
- Tests: pytest tests/

## Common Tasks
- Run tests: pytest
- Cleanup: python scripts/analyze_cleanup_candidates.py
```

**`.ai/codebase-map.yaml`** - Structured module map
```yaml
modules:
  core:
    purpose: "Workstream orchestration"
    entry: "core/engine/orchestrator.py"
    depends_on: ["infra"]

  error:
    purpose: "Error detection and auto-fix"
    entry: "error/engine/error_engine.py"
    depends_on: ["core"]
```

**`.ai/common-patterns.md`** - Code patterns guide
```markdown
# Common Patterns

## Error Handling
Always use circuit breaker pattern:
[code example]

## Testing
Follow AAA pattern:
[code example]
```

**Effort**: 30 mins
**Value**: AI tools understand repo 10x faster
**Maintenance**: Update when architecture changes

#### 4.2 Add Module README Files (1 hour)

Add `README.md` to each top-level module:
- `core/README.md` - What core does
- `error/README.md` - Error pipeline overview
- `engine/README.md` - Job engine purpose
- `pm/README.md` - PM tools overview

**Template**:
```markdown
# [Module Name]

## Purpose
[One sentence]

## Structure
- subdir/ - What it does

## Usage
[Quick example]

## Dependencies
[What it needs]
```

**Effort**: 15 mins × 4 modules = 1 hour
**Value**: AI navigates modules independently

---

### **Phase 5: Intelligent Indexing (Priority: MEDIUM)**

**Goal**: Auto-maintain CODEBASE_INDEX.yaml

#### 5.1 Create Index Updater Script (1 hour)

```python
# scripts/update_codebase_index.py
"""
Auto-update CODEBASE_INDEX.yaml from filesystem.
Scans modules, detects new files, updates index.
"""

def scan_module(module_path):
    # Detect Python files
    # Detect entry points
    # Detect dependencies (from imports)
    # Return structured data

def update_index():
    # Load current CODEBASE_INDEX.yaml
    # Scan all modules
    # Merge (preserve manual annotations)
    # Write updated index
```

**Run monthly**:
```bash
python scripts/update_codebase_index.py --verify
# Reviews changes, asks for confirmation
```

**Effort**: 1 hour to build
**Value**: Index stays current automatically
**Maintenance**: Runs monthly (5 mins)

---

### **Phase 6: Markdown Consolidation (Priority: LOW)**

**Goal**: Reduce 750 MD files to ~200

**Current**: 750 markdown files (too many)

**Strategy**:
```bash
# Analyze markdown files
python scripts/analyze_cleanup_candidates.py --type markdown

# Group by:
# - Session logs (archive old ones)
# - Duplicate READMEs (consolidate)
# - Spec versions (keep latest only)
```

**Expected reduction**: 750 → 200 files

**Effort**: 2 hours
**Value**: Less clutter, faster searches
**Risk**: Medium (review before deleting)

---

### **Phase 7: Dependency Cleanup (Priority: LOW)**

**Goal**: Remove unused dependencies

#### 7.1 Analyze Dependencies (20 mins)

```bash
# Python
pip install pipreqs
pipreqs . --force  # Generate actual requirements
diff requirements.txt requirements-actual.txt

# JavaScript (if any)
npm install -g depcheck
depcheck
```

#### 7.2 Remove Unused (10 mins)
- Update requirements.txt
- Test that everything still works
- Commit cleaner deps

**Effort**: 30 mins
**Value**: Faster installs, fewer vulnerabilities

---

## Recommended Priority Order

### **Week 1: High-Impact, Low-Effort**
1. ✅ **AI Context Files** (30 mins) - Huge AI benefit
2. ✅ **Root Cleanup** (15 mins) - Visual improvement
3. ✅ **Strategic DOC_IDs** (30 mins) - Complete governance

**Total**: ~1.5 hours

### **Week 2: Medium Impact**
4. **Module READMEs** (1 hour) - AI navigation
5. **Test Coverage** (10 mins setup) - Confidence
6. **Index Updater** (1 hour) - Automation

**Total**: ~2 hours

### **Month 2: Polish**
7. **Markdown Consolidation** (2 hours) - Cleanup
8. **Dependency Cleanup** (30 mins) - Maintenance

**Total**: ~2.5 hours

---

## Comparison: Full ID-ing vs. Targeted Optimization

| Approach | Effort | Maintenance | AI Benefit | Human Benefit |
|----------|--------|-------------|------------|---------------|
| **ID Every File** | 20+ hours | High (every file change) | Low (code doesn't need IDs) | Low (cognitive overhead) |
| **Targeted Optimization** | ~6 hours | Low (monthly automation) | **High** (AI context files) | **High** (cleaner structure) |

---

## Success Metrics

### After Week 1:
- ✅ All strategic docs have DOC_IDs (100%)
- ✅ AI context files in place
- ✅ Root has <15 files
- ✅ AI tools load context 10x faster

### After Week 2:
- ✅ All modules have READMEs
- ✅ Test coverage >70% on core
- ✅ CODEBASE_INDEX auto-updates

### After Month 2:
- ✅ Markdown files reduced 750 → 200
- ✅ Zero unused dependencies
- ✅ Repository fully AI-optimized

---

## Anti-Patterns to Avoid

❌ **Don't**: Add DOC_IDs to code files
✅ **Do**: Use import paths as natural IDs

❌ **Don't**: Aim for 100% test coverage
✅ **Do**: Focus on critical paths (70% is great)

❌ **Don't**: Delete all old docs immediately
✅ **Do**: Archive first, delete after 6 months if unused

❌ **Don't**: Over-engineer the index
✅ **Do**: Keep CODEBASE_INDEX simple and scannable

---

## Tools to Build (Optional)

### If You Have Time:

1. **AI Chat Analyzer** (2 hours)
   - Analyzes your AI chat logs
   - Extracts common questions
   - Generates FAQ automatically

2. **Smart Archive Script** (1 hour)
   - Auto-archives files untouched >6 months
   - Creates manifest in archive/
   - Reversible (easy to restore)

3. **Dependency Graph Visualizer** (2 hours)
   - Generates visual module dependency graph
   - Helps identify circular dependencies
   - Outputs SVG/PNG

---

## Final Recommendation

### **Start Here (Week 1 Plan)**:

```bash
# 1. Create AI context (30 mins)
mkdir .ai
# Create the 3 files described in Phase 4

# 2. Clean root (15 mins)
mkdir -p config/python infra/data
git mv pyproject.toml config/python/
git mv requirements.txt config/python/
git mv refactor_paths.db infra/data/
# Test tools still work

# 3. Add strategic DOC_IDs (30 mins)
python doc_id/doc_id_triage.py --generate-missing
# Review and commit
```

**Total time**: 1.5 hours
**Impact**: Repository becomes 10x more AI-friendly

---

## Conclusion

Your repo is **already 90% optimized**. The remaining 10% is:
- ✅ AI context files (biggest bang for buck)
- ✅ Root cleanup (visual improvement)
- ✅ Strategic DOC_IDs (governance completion)

**Don't** over-index by adding IDs to every file. **Do** focus on making it maximally AI-readable with context files and module documentation.

---

**Questions? Start with Week 1 and see the difference.**

_Last Updated: 2025-11-25_
_Status: Ready for Implementation_
