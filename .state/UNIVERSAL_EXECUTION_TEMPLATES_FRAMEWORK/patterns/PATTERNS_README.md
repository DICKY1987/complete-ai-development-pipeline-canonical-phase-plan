---
doc_id: DOC-PAT-PATTERNS-README-757
---

# Pattern Management Tools

This directory contains automation patterns for repository management.

## Available Patterns

### PAT-PATCH-001: Patch Lifecycle Management
**Purpose**: Automatically check, apply, and archive patch files

**Features**:
- ✅ Auto-detect if patches are already applied
- ✅ Apply unapplied patches with 3-way merge
- ✅ Archive applied patches to dated folders
- ✅ Isolate failed patches for manual review
- ✅ Dry-run mode for safety

**Usage**:
```bash
# Process all patches (searches entire repository recursively)
python scripts/process_patches.py

# Dry run (preview what would happen)
python scripts/process_patches.py --dry-run

# Check specific patch status
python scripts/process_patches.py --check path/to/patch.patch

# Apply specific patch
python scripts/process_patches.py --apply path/to/patch.patch

# Validate (for CI/CD)
python scripts/process_patches.py --validate
```

**Directory Structure**:
```
patches/
├── active/              # Pending patches (optional organization)
├── archive/            # Successfully applied patches
│   └── YYYY-MM-DD/    # Date-based archiving
└── failed/            # Patches that failed to apply
```

---

### PAT-SEARCH-001: Deep Directory Search
**Purpose**: Recursively search through nested subdirectories for files

**Features**:
- ✅ Unlimited depth recursion
- ✅ Multiple filter criteria (extension, pattern, content, size, date)
- ✅ JSON output support
- ✅ Graceful error handling
- ✅ Performance optimized (skips .git, node_modules, etc.)

**Usage**:
```bash
# Find by extension
python scripts/deep_search.py --ext .patch

# Find multiple extensions
python scripts/deep_search.py --ext .patch .diff .txt

# Find by pattern
python scripts/deep_search.py --pattern "*config*"

# Search file contents
python scripts/deep_search.py --content "TODO" --ext .py

# Limit search depth
python scripts/deep_search.py --ext .md --max-depth 3

# Find large files (> 1MB)
python scripts/deep_search.py --min-size 1048576

# Find recently modified (last 7 days)
python scripts/deep_search.py --modified-days 7 --ext .py

# JSON output
python scripts/deep_search.py --ext .patch --json

# Detailed view
python scripts/deep_search.py --ext .patch --detailed
```

**Python API**:
```python
from scripts.deep_search import DeepSearch

# Initialize searcher
searcher = DeepSearch(".")

# Find by extension
patches = searcher.find_by_extension(".patch")

# Find by multiple extensions
results = searcher.find_by_extensions([".patch", ".diff"])

# Search by content
matches = searcher.find_by_content("FIXME", "*.py")

# Custom filters
def is_large(path):
    return path.stat().st_size > 1024 * 1024

large_files = searcher.search("*", filter_func=is_large)
```

---

### PAT-SEARCH-002: README Presence Audit
**Purpose**: Identify which directories contain a README and which are missing one

**Features**:
- ? Recursively scans directories with configurable depth
- ? Detects common README filename variants (case-insensitive)
- ? Groups output into "with README" and "without README"
- ? Optional JSON output for automation pipelines

**Usage**:
```bash
# Text report for the current tree
python scripts/readme_presence_scan.py --root .

# JSON for tooling
python scripts/readme_presence_scan.py --root . --json

# Custom README names and depth limit
python scripts/readme_presence_scan.py --root . --names README.md README.txt --max-depth 2
```

---

## Integration Examples

### Combined Workflow: Find and Process Patches
```bash
# 1. Discover all patches
python scripts/deep_search.py --ext .patch --detailed

# 2. Preview processing
python scripts/process_patches.py --dry-run

# 3. Process patches
python scripts/process_patches.py
```

### CI/CD Integration
```yaml
# .github/workflows/patches.yml
- name: Validate Patches
  run: |
    python scripts/process_patches.py --validate
    
- name: Find Unprocessed Patches
  run: |
    python scripts/deep_search.py --ext .patch --json > patch-report.json
```

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Ensure no pending patches
python scripts/process_patches.py --validate

# Find TODO markers
python scripts/deep_search.py --content "TODO" --ext .py > todos.txt
```

---

## Pattern Development Guidelines

### Creating New Patterns

1. **Pattern Spec** (in `patterns/specs/`)
   - Follow naming: `PAT-{CATEGORY}-{NUMBER}_{name}.md`
   - Include: Intent, Problem, Solution, Implementation, Usage
   - Reference related patterns

2. **Implementation** (in `scripts/`)
   - Python 3.8+ compatible
   - Include `--help` documentation
   - Add error handling
   - Support dry-run mode where applicable

3. **Tests** (in `patterns/tests/`)
   - Unit tests for core logic
   - Integration tests for workflows
   - Edge case coverage

### Pattern Naming Convention
```
PAT-{CATEGORY}-{NUMBER}

Categories:
- PATCH   : Patch management
- SEARCH  : File/content search
- GIT     : Git workflows
- CI      : CI/CD automation
- AUDIT   : Audit trails
- FILE    : File operations
- PERF    : Performance optimization
```

### Pattern IDs in Use
- **PAT-PATCH-001**: Patch Lifecycle Management
- **PAT-SEARCH-001**: Deep Directory Search

---

## Quality Standards

### All Scripts Must:
- ✅ Be idempotent (safe to re-run)
- ✅ Include `--help` documentation
- ✅ Handle errors gracefully
- ✅ Use descriptive naming
- ✅ Support `--dry-run` where applicable
- ✅ Provide clear output/logging

### Python Style:
- Follow PEP8
- Use type hints
- Add docstrings
- Keep functions focused
- Prefer pathlib over os.path

---

## Common Tasks

### Find All Patterns
```bash
python scripts/deep_search.py --pattern "PAT-*" --ext .md
```

### List Pattern Scripts
```bash
python scripts/deep_search.py --pattern "*pattern*" --ext .py
```

### Search Pattern Documentation
```bash
python scripts/deep_search.py --content "Pattern ID" --ext .md
```

### Find Large Files in Repository
```bash
python scripts/deep_search.py --min-size 10485760 --detailed  # > 10MB
```

### Find Recent Changes
```bash
python scripts/deep_search.py --modified-days 1 --ext .py
```

---

## Performance Notes

### Search Optimization
The deep search automatically skips:
- `.git/` - Git internals
- `.venv/`, `venv/` - Virtual environments
- `__pycache__/` - Python cache
- `node_modules/` - Node dependencies
- `.pytest_cache/` - Test cache
- `.worktrees/` - Git worktrees
- `build/`, `dist/` - Build artifacts

### Large Repositories
For very large repositories (>100k files):
```bash
# Limit depth
python scripts/deep_search.py --max-depth 5

# Search specific subtree
python scripts/deep_search.py --root specific/directory
```

---

## Troubleshooting

### "No files found"
- Check file extension format (use `.patch` not `patch`)
- Verify you're in correct directory
- Try `--include-hidden` if searching hidden files
- Use `--pattern "*"` for debugging

### "Permission denied"
- Scripts automatically skip inaccessible directories
- Check file/directory permissions
- Run with appropriate user privileges

### Patch application fails
- Check git status (uncommitted changes may conflict)
- Review patch format (must be git-compatible)
- Check failed/ directory for error details
- Try manual application: `git apply --3way patch.patch`

---

## Related Documentation

- **Pattern Specifications**: `patterns/specs/`
- **UET Patch Management**: `specs/UET_PATCH_MANAGEMENT_SPEC.md`
- **Quality Gates**: `QUALITY_GATE.yaml`
- **AI Policies**: `ai_policies.yaml`

---

## Contributing

When adding new patterns:
1. Create spec in `patterns/specs/`
2. Implement script in `scripts/`
3. Add tests in `patterns/tests/`
4. Update this README
5. Add to pattern registry

For questions or suggestions, see `AGENTS.md` for contribution guidelines.
