---
status: draft
doc_type: guide
module_refs: []
script_refs: []
doc_id: DOC-GUIDE-CI_PATH_STANDARDS-077
---

# CI Path Standards Enforcement

**Created**: 2025-11-19
**Workflow**: `.github/workflows/path_standards.yml`
**Status**: Active

---

## Overview

This CI workflow automatically checks for deprecated path patterns in pull requests and pushes to the main branch. It prevents regressions to the old repository structure after the Phase E refactor.

## What Gets Checked

The workflow scans the repository for two types of deprecated import patterns:

### 1. Old `src.pipeline.*` Imports

**Deprecated**:
```python
from src.pipeline.db import init_db
from src.pipeline.orchestrator import Orchestrator
```

**Current**:
```python
from core.state.db import init_db
from core.engine.orchestrator import Orchestrator
```

**CI Check**: Matches import module names starting with `src.pipeline.`

### 2. Old `MOD_ERROR_PIPELINE.*` Imports

**Deprecated**:
```python
from MOD_ERROR_PIPELINE.error_engine import ErrorEngine
from MOD_ERROR_PIPELINE.plugins.syntax_checker import SyntaxChecker
```

**Current**:
```python
from error.engine.error_engine import ErrorEngine
from error.plugins.syntax_checker import SyntaxChecker
```

**CI Check**: Matches import module names starting with `MOD_ERROR_PIPELINE.`

---

## How It Works

1. **Scan**: The workflow uses `scripts/paths_index_cli.py` to scan all repository files and extract import statements via AST parsing
2. **Gate Checks**: Two regex-based gate checks run to detect deprecated import patterns
3. **Fail on Violation**: If any deprecated import pattern is found in Python code, the workflow fails
4. **Report**: A summary report shows what was found

**Note**: The checks focus on Python import statements. Documentation files (`.md`, `.txt`) and config files (`.yaml`, `.json`) that may reference old paths for migration documentation are excluded from gate checks.

---

## Workflow Status Badge

Add this badge to `README.md`:

```markdown
![Path Standards](https://github.com/YOUR_ORG/YOUR_REPO/actions/workflows/path_standards.yml/badge.svg)
```

---

## How to Fix Violations

If the CI check fails, follow these steps:

### Step 1: Review the Error Report

The workflow output will show:
```
Gate failed: 3 legacy occurrences matched regex: ^src\.pipeline\.
  src/utils/helper.py:15 -> src.pipeline.db
  tests/test_integration.py:8 -> src.pipeline.orchestrator
  scripts/migrate.py:22 -> src.pipeline.scheduler
```

### Step 2: Update Imports

Use the [Section Refactor Mapping](SECTION_REFACTOR_MAPPING.md) to find the correct new import:

| Old Import | New Import |
|------------|------------|
| `from src.pipeline.db import *` | `from core.state.db import *` |
| `from src.pipeline.orchestrator import *` | `from core.engine.orchestrator import *` |
| `from src.pipeline.planner import *` | `from core.planning.planner import *` |
| `from MOD_ERROR_PIPELINE.error_engine import *` | `from error.engine.error_engine import *` |
| `from MOD_ERROR_PIPELINE.plugins.* import *` | `from error.plugins.* import *` |

### Step 3: Update Hardcoded Paths (if any)

If you have hardcoded path references in string literals, replace them with new paths.

### Step 4: Test Locally (Optional)

Run the path standards check locally before pushing:

```bash
# Scan the repository
python scripts/paths_index_cli.py scan --root . --db path_standards.db --reset

# Check for violations
python scripts/paths_index_cli.py gate --db path_standards.db --regex "^src\.pipeline\."
python scripts/paths_index_cli.py gate --db path_standards.db --regex "^MOD_ERROR_PIPELINE\."

# View summary
python scripts/paths_index_cli.py summary --db path_standards.db
```

---

## Exceptions

### Documentation Files

Documentation files (`.md`, `.txt`) are excluded from gate checks because they often contain:
- Migration examples showing "before and after"
- Historical references
- Deprecation notices

If you need to reference old paths in documentation, it's allowed.

### Legacy Test Files

If you have legacy integration tests that cannot be updated immediately:
1. Document the exception in a comment
2. Create a tracking issue to update them
3. Consider moving them to a `tests/legacy/` directory

**Do not disable the CI check** – exceptions should be rare and temporary.

---

## Maintaining the Workflow

### Adding New Patterns

To check for additional deprecated patterns, add a new gate step:

```yaml
- name: Check for deprecated pattern
  run: |
    python scripts/paths_index_cli.py gate \
      --db path_standards.db \
      --regex "your_regex_here" \
      --limit 20
```

### Adjusting Sensitivity

The `--limit` parameter controls how many violations are displayed (default: 50). Adjust if needed:

```yaml
--limit 10   # Show fewer violations
--limit 100  # Show more violations
```

### Including Documentation Files

To check documentation files as well, add `--all-exts`:

```yaml
python scripts/paths_index_cli.py gate \
  --db path_standards.db \
  --regex "from\s+src\.pipeline\." \
  --all-exts
```

---

## Troubleshooting

### False Positives

If the gate catches a legitimate use (e.g., in a comment or string):

1. **Check the context**: Review the file and line number
2. **Refactor if possible**: Even comments should use current paths
3. **Exception rare**: Consider if the old reference is truly necessary

### Workflow Not Running

Ensure:
- The workflow file is in `.github/workflows/`
- The file has `.yml` extension
- GitHub Actions is enabled for the repository
- The workflow has correct YAML syntax

### Database Not Found

The workflow creates a fresh database on each run. If you see "database not found" errors:
- Check that `scripts/paths_index_cli.py` exists
- Verify Python dependencies are installed
- Check the scan step completed successfully

---

## Related Documentation

- **Refactor Mapping**: [docs/SECTION_REFACTOR_MAPPING.md](SECTION_REFACTOR_MAPPING.md)
- **Migration Guide**: [docs/MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) (to be created in WS-22)
- **Phase F Plan**: [docs/PHASE_F_PLAN.md](PHASE_F_PLAN.md)
- **Deprecation Plan**: [docs/DEPRECATION_PLAN.md](DEPRECATION_PLAN.md) (to be created in WS-24)

---

## Questions?

If you encounter issues with the path standards check:
1. Review the mapping document for correct new paths
2. Check the workflow logs for detailed error messages
3. Run the checks locally to debug
4. Open an issue if you believe the check is incorrect

---

**Last Updated**: 2025-11-19
**Status**: Active
**Contact**: See repository maintainers
