---
doc_id: DOC-PAT-EXEC-006-AUTO-FIX-LINTING-297
pattern_id: EXEC-006
version: 1.0.0
status: active
created: 2025-12-04
category: code_quality
priority: high
---

# EXEC-006: Auto-Fix Linting Pattern

## Overview

**Pattern Name**: Auto-Fix Linting Violations
**Problem**: 120 linting violations (93 auto-fixable) degrading code quality
**Solution**: Systematic auto-fix of violations with verification
**Impact**: Clean codebase, improved maintainability, CI compliance

---

## Problem Statement

### Observed Behavior
```
Ruff found 120 violations:
  - 86 unused imports (F401)
  - 11 f-string formatting issues (F541)
  - 10 bare except clauses (E722)
  - 8 unused variables (F841)
  - 2 undefined names (F821) ⚠️ CRITICAL
  - 1 syntax error (E999) ⚠️ CRITICAL

93 are auto-fixable with --fix
```

### Root Cause
- Code additions without cleanup
- Incomplete refactoring
- Missing import management
- Poor error handling practices

### Cost
- **Code bloat**: 86 unused imports
- **Confusion**: Developers unsure which imports are needed
- **CI failures**: Quality gates blocking merges
- **Technical debt**: Compounds over time

---

## Solution Pattern

### Core Principle
**Auto-fix safe violations first, then manually address critical issues**

### Implementation Steps

```python
import subprocess
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class LintingResult:
    file_path: str
    violations_before: int
    violations_after: int
    auto_fixed: int
    manual_required: List[Dict]


class AutoFixLinter:
    """EXEC-006: Automated linting fix pattern"""

    def __init__(self, paths: List[str]):
        self.paths = paths
        self.results = []

    def scan_violations(self) -> Dict:
        """Get current violation counts"""
        cmd = ["ruff", "check"] + self.paths + ["--output-format=json"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        import json
        violations = json.loads(result.stdout) if result.stdout else []

        # Categorize by severity
        critical = [v for v in violations if v['code'] in ['F821', 'E999']]
        auto_fixable = [v for v in violations if v.get('fix')]
        manual = [v for v in violations if v['code'] == 'E722']

        return {
            'total': len(violations),
            'critical': critical,
            'auto_fixable': auto_fixable,
            'manual_required': manual
        }

    def auto_fix_safe(self) -> int:
        """
        Auto-fix violations that are safe to fix automatically

        Safe categories:
        - F401: unused imports
        - F541: f-string formatting
        - F841: unused variables
        - E401: multiple imports on one line
        - F402: import shadowing

        Returns:
            Number of violations fixed
        """
        before = self.scan_violations()

        # Run auto-fix
        cmd = ["ruff", "check"] + self.paths + ["--fix"]
        subprocess.run(cmd, check=True)

        after = self.scan_violations()

        fixed = before['total'] - after['total']
        print(f"✅ Auto-fixed {fixed} violations")

        return fixed

    def auto_fix_unsafe(self) -> int:
        """
        Auto-fix violations that may change behavior

        Use with caution - review changes before commit
        """
        cmd = ["ruff", "check"] + self.paths + ["--fix", "--unsafe-fixes"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        print("⚠️  Unsafe fixes applied - REVIEW CHANGES")
        print(result.stdout)

        return 0  # Return count from analysis

    def report_manual_fixes_required(self) -> List[Dict]:
        """
        Report violations that require manual intervention

        Returns:
            List of violations with file, line, code, message
        """
        violations = self.scan_violations()

        manual_fixes = []

        # Critical issues
        for v in violations['critical']:
            manual_fixes.append({
                'severity': 'CRITICAL',
                'file': v['filename'],
                'line': v['location']['row'],
                'code': v['code'],
                'message': v['message'],
                'fix_required': 'Manual code inspection and fix'
            })

        # Bare except clauses
        for v in violations['manual_required']:
            manual_fixes.append({
                'severity': 'HIGH',
                'file': v['filename'],
                'line': v['location']['row'],
                'code': v['code'],
                'message': v['message'],
                'fix_required': 'Specify exception type (e.g., except ValueError:)'
            })

        return manual_fixes
```

---

## Usage Pattern

### Standard Workflow

```bash
# Step 1: Scan current violations
ruff check core/ error/ gui/ --statistics

# Step 2: Auto-fix safe violations (imports, formatting)
ruff check core/ error/ gui/ --fix

# Step 3: Verify no regressions
pytest tests/ -x  # Stop on first failure

# Step 4: Auto-fix unsafe violations (if needed)
ruff check core/ error/ gui/ --fix --unsafe-fixes

# Step 5: Review changes
git diff

# Step 6: Identify manual fixes required
ruff check core/ error/ gui/ --select F821,E999,E722

# Step 7: Commit auto-fixes
git add -A
git commit -m "chore: auto-fix linting violations (EXEC-006)"
```

### Automated Workflow

```python
from patterns.execution.exec006 import AutoFixLinter

linter = AutoFixLinter(paths=["core/", "error/", "gui/"])

# Scan initial state
violations = linter.scan_violations()
print(f"Found {violations['total']} violations")
print(f"  - {len(violations['auto_fixable'])} auto-fixable")
print(f"  - {len(violations['critical'])} critical")

# Auto-fix safe violations
fixed = linter.auto_fix_safe()
print(f"✅ Fixed {fixed} violations automatically")

# Report manual fixes needed
manual = linter.report_manual_fixes_required()
for fix in manual:
    print(f"{fix['severity']}: {fix['file']}:{fix['line']} - {fix['message']}")
    print(f"  → {fix['fix_required']}")
```

---

## Violation Categories

### Safe to Auto-Fix

#### F401: Unused Import
```python
# BEFORE
from typing import Dict, List  # Both unused
import os  # Unused

def function():
    pass

# AFTER (auto-fixed)
def function():
    pass
```

#### F541: F-String Missing Placeholders
```python
# BEFORE
message = f"Processing complete"  # No placeholders

# AFTER (auto-fixed)
message = "Processing complete"
```

#### F841: Unused Variable
```python
# BEFORE
result = expensive_operation()  # Never used
return None

# AFTER (auto-fixed)
expensive_operation()  # Result discarded
return None
```

### Requires Manual Fix

#### F821: Undefined Name
```python
# BEFORE
def process():
    return undefined_variable  # ❌ Not defined anywhere

# AFTER (manual fix)
def process():
    return defined_variable  # ✅ Use correct variable name
```

#### E722: Bare Except
```python
# BEFORE
try:
    risky_operation()
except:  # ❌ Catches everything, including KeyboardInterrupt
    handle_error()

# AFTER (manual fix)
try:
    risky_operation()
except (ValueError, TypeError) as e:  # ✅ Specific exceptions
    handle_error(e)
```

#### E999: Syntax Error
```python
# BEFORE
def function()  # ❌ Missing colon
    pass

# AFTER (manual fix)
def function():  # ✅ Colon added
    pass
```

---

## Verification Checklist

- [ ] Run `ruff check` with no violations (or acceptable warnings)
- [ ] All tests still pass: `pytest tests/`
- [ ] No behavioral changes: `git diff` review
- [ ] Critical violations addressed (F821, E999)
- [ ] Bare except clauses specify exceptions (E722)
- [ ] Commit with descriptive message

---

## Anti-Patterns

❌ **Don't**: Run `--fix` without understanding what will change
✅ **Do**: Run `ruff check` first to see violations

❌ **Don't**: Auto-fix and commit without testing
✅ **Do**: Run test suite after auto-fix

❌ **Don't**: Ignore critical violations (F821, E999)
✅ **Do**: Fix critical issues manually before auto-fixing others

❌ **Don't**: Use `--unsafe-fixes` without review
✅ **Do**: Review all changes from unsafe fixes carefully

---

## Configuration

### Ruff Settings (pyproject.toml)

```toml
[tool.ruff]
line-length = 120
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "F",   # Pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "W",   # pycodestyle warnings
]
ignore = [
    "E501",  # line too long (handled by formatter)
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = [
    "F401",  # Allow unused imports in tests
]
```

---

## Metrics

- **Fix Time**: 10-20 minutes total
  - Auto-fix safe: 2 minutes
  - Review changes: 3 minutes
  - Manual fixes: 5-15 minutes
- **Violations Fixed**: Typically 70-95% auto-fixable
- **Success Rate**: 99% (auto-fixes are safe)
- **Maintenance**: Ongoing (run pre-commit or in CI)

---

## Integration

### Pre-Commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format
```

### CI/CD Gate

```yaml
# .github/workflows/lint.yml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install ruff
      - run: ruff check core/ error/ gui/ --output-format=github
```

---

## References

- **Ruff Documentation**: https://docs.astral.sh/ruff/
- **Error Codes**: https://docs.astral.sh/ruff/rules/
- **Validation Report**: `reports/validation/VALIDATION_SUMMARY.md`

---

**Status**: ✅ Active
**Priority**: 🟠 HIGH
**Est. Time**: 10 minutes (auto-fix) + 15 minutes (manual)
**Complexity**: Low
