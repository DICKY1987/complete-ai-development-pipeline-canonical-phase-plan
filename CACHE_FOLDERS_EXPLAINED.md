# Cache and Knowledge Folders - Quick Reference

**Date**: 2025-12-04
**Question**: What are `.ruff_cache/`, `__pycache__/`, and `project_knowledge/`?

---

## Quick Answer

### 1. `.ruff_cache/` - Linter Cache ✅ KEEP (auto-managed)
- **Type**: Ruff Python linter cache
- **Size**: 0.01 MB (9 files)
- **Purpose**: Speeds up code linting
- **Safe to delete**: YES (regenerates automatically)
- **Git status**: ✅ In `.gitignore` (not tracked)

### 2. `__pycache__/` - Python Bytecode Cache ✅ KEEP (auto-managed)
- **Type**: Python bytecode cache
- **Size**: 2.43 KB (2 files)
- **Purpose**: Compiled Python for faster imports
- **Safe to delete**: YES (regenerates on next run)
- **Git status**: ✅ In `.gitignore` (not tracked)

### 3. `project_knowledge/` - Empty Knowledge Base ⚠️ REMOVE (empty)
- **Type**: AI assistant knowledge base (intended)
- **Size**: 0 KB (EMPTY - no files)
- **Purpose**: Metadata for AI tools (never used)
- **Safe to delete**: YES (currently empty)
- **Git status**: ❌ NOT in `.gitignore` (would be tracked if not empty)

---

## Detailed Analysis

### `.ruff_cache/` - Ruff Linter Cache

**What is Ruff?**
- Modern, extremely fast Python linter written in Rust
- Replacement for Flake8, pylint, pycodestyle, etc.
- Used to check Python code quality

**What's in .ruff_cache/?**
```
.ruff_cache/
├── .gitignore
├── 0.14.4/              (Ruff version)
└── CACHEDIR.TAG         (Cache directory marker)
```

**How it works:**
1. You run: `ruff check .`
2. Ruff analyzes Python files
3. Results cached in `.ruff_cache/`
4. Next run is much faster (uses cache)

**Management:**
- ✅ Automatically managed by Ruff
- ✅ In `.gitignore` (not committed to git)
- ✅ Safe to delete anytime (regenerates)
- Size grows over time (old versions accumulate)

**Action**: Leave it alone, it's working correctly

---

### `__pycache__/` - Python Bytecode Cache

**What is __pycache__?**
- Python's built-in bytecode cache system
- Created automatically by Python interpreter
- Stores compiled `.pyc` files (Python bytecode)

**What's in __pycache__/?**
```
__pycache__/
├── conftest.cpython-312-pytest-8.4.2.pyc
└── conftest.cpython-312-pytest-9.0.0.pyc
```

**How it works:**
1. You run Python code: `python script.py`
2. Python compiles `.py` → `.pyc` (bytecode)
3. Bytecode cached in `__pycache__/`
4. Next run imports faster (no recompile needed)

**Why 2 files?**
- Different pytest versions (8.4.2 and 9.0.0)
- Python caches per-version for compatibility

**Management:**
- ✅ Automatically managed by Python
- ✅ In `.gitignore` (not committed to git)
- ✅ Safe to delete anytime (regenerates)
- Found in every directory with `.py` files

**Action**: Leave it alone, it's working correctly

---

### `project_knowledge/` - Empty Knowledge Base

**What is project_knowledge/?**
- Directory for AI assistant context/metadata
- Mentioned in one doc as example location for specs
- **Currently EMPTY** - never actually used

**Intended purpose:**
- Store project-specific context for AI tools
- Example: Cursor IDE, Codeium, GitHub Copilot
- Would contain:
  - Custom instructions
  - Project architecture notes
  - Context for AI assistants

**Current status:**
- ✅ Empty directory (0 files)
- ✅ No code references it
- ❌ Not in `.gitignore` (would be tracked if populated)
- Only mentioned in one GUI planning doc as example

**Reference found:**
```markdown
# From gui/guiimprove.md:
"Here's a spec you can drop into `project_knowledge/` as something like:"
```

**Action**: **REMOVE** (empty, not used, would need `.gitignore` entry if kept)

---

## Recommendations

### Immediate Actions

**1. Delete `project_knowledge/`** ⚠️
```bash
# It's empty and not used
rm -rf project_knowledge/
```

**Reason**: Empty directory serving no purpose

**2. Leave `.ruff_cache/`** ✅
- Actively used by Ruff linter
- Already in `.gitignore`
- Performance benefit

**3. Leave `__pycache__/`** ✅
- Actively used by Python
- Already in `.gitignore`
- Performance benefit

---

## Optional: Cache Cleanup

If you want to clean up caches (they'll regenerate):

```bash
# Clean all Python caches
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Clean Ruff cache
rm -rf .ruff_cache/

# Clean all at once
find . -type d \( -name "__pycache__" -o -name ".ruff_cache" \) -exec rm -rf {} + 2>/dev/null
```

**When to clean:**
- Switching Python versions
- After major package updates
- Troubleshooting import issues
- Reducing disk space

**Note**: They regenerate automatically on next use

---

## Git Tracking Status

### Currently in `.gitignore` ✅
```gitignore
__pycache__/
*.pyc
*.pyo
.ruff_cache/
```

### Should be added ⚠️
```gitignore
# Add this if you keep project_knowledge/
project_knowledge/
```

---

## Summary Table

| Folder | Type | Size | Purpose | Keep? | Action |
|--------|------|------|---------|-------|--------|
| `.ruff_cache/` | Linter cache | 0.01 MB | Speed up linting | ✅ YES | Leave alone |
| `__pycache__/` | Python cache | 2.43 KB | Speed up imports | ✅ YES | Leave alone |
| `project_knowledge/` | Knowledge base | 0 KB | AI context (unused) | ❌ NO | Delete |

---

## Additional Cache Locations

You likely have more `__pycache__/` directories throughout the project:

```bash
# Count all __pycache__ directories
find . -type d -name "__pycache__" | wc -l

# Total size of all Python caches
du -sh $(find . -type d -name "__pycache__")
```

**These are all normal and expected!**

---

## Conclusion

**Keep:**
- ✅ `.ruff_cache/` - Active linter cache (0.01 MB)
- ✅ `__pycache__/` - Active Python cache (2.43 KB)
- ✅ All other `__pycache__/` directories in project

**Remove:**
- ❌ `project_knowledge/` - Empty, unused (0 KB)

**Total impact**: Removing empty directory, keeping functional caches.
