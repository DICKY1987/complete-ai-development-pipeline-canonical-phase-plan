---
doc_id: DOC-PAT-EXEC-005-SYNTAX-ERROR-FIX-296
pattern_id: EXEC-005
version: 1.0.0
status: active
created: 2025-12-04
category: code_quality
priority: critical
---

# EXEC-005: Syntax Error Fix Pattern

## Overview

**Pattern Name**: Syntax Error Fix
**Problem**: Syntax errors (IndentationError, SyntaxError) blocking code execution
**Solution**: Locate, analyze, and fix syntax errors with verification
**Impact**: Enables code to parse and import correctly

---

## Problem Statement

### Observed Behavior
```
IndentationError: unexpected unindent at line 22 in core/autonomous/fix_generator.py
Prevents entire module from being imported
Blocks 5+ test files from running
```

### Root Cause
- Incorrect indentation levels
- Missing/extra colons, parentheses, brackets
- Invalid Python syntax
- Copy-paste errors with whitespace

### Cost
- **BLOCKING**: Code cannot run at all
- **Cascade failures**: Dependent modules fail to import
- **Test failures**: Cannot validate any functionality
- **15-30 minutes** typical resolution time

---

## Solution Pattern

### Core Principle
**Locate exact syntax error, understand context, fix with minimal changes, verify**

### Implementation Steps

```python
# Step 1: Identify syntax error location
def locate_syntax_error(file_path: str) -> tuple[int, str]:
    """
    Compile file to get exact line number and error message

    Returns:
        (line_number, error_message)
    """
    try:
        with open(file_path, 'r') as f:
            compile(f.read(), file_path, 'exec')
    except SyntaxError as e:
        return (e.lineno, str(e))
    except IndentationError as e:
        return (e.lineno, str(e))

    return (0, "No syntax error found")


# Step 2: Analyze context
def analyze_context(file_path: str, line_number: int, context_lines: int = 5):
    """Show lines around error for context"""
    with open(file_path, 'r') as f:
        lines = f.readlines()

    start = max(0, line_number - context_lines - 1)
    end = min(len(lines), line_number + context_lines)

    for i in range(start, end):
        marker = ">>> " if i == line_number - 1 else "    "
        print(f"{marker}{i+1:4d}: {lines[i]}", end='')


# Step 3: Fix with verification
def fix_syntax_error(file_path: str, line_number: int, fix_description: str):
    """
    Apply fix and verify it compiles

    Args:
        file_path: Path to file with syntax error
        line_number: Line number of error
        fix_description: Human-readable description of fix

    Returns:
        True if fix successful and file compiles
    """
    # Make backup
    backup_path = f"{file_path}.backup"
    shutil.copy(file_path, backup_path)

    try:
        # Apply fix (manual edit or automated)
        # ... fix logic here ...

        # Verify file now compiles
        with open(file_path, 'r') as f:
            compile(f.read(), file_path, 'exec')

        print(f"✅ Fix verified: {fix_description}")
        os.remove(backup_path)
        return True

    except (SyntaxError, IndentationError) as e:
        print(f"❌ Fix failed: {e}")
        # Restore backup
        shutil.copy(backup_path, file_path)
        os.remove(backup_path)
        return False
```

---

## Usage Pattern

### Manual Workflow

```bash
# 1. Identify error
python -m py_compile core/autonomous/fix_generator.py

# 2. View context
# Use pattern to show lines 17-27 (error on line 22)

# 3. Fix indentation
# Edit file to correct indentation

# 4. Verify
python -m py_compile core/autonomous/fix_generator.py
python -c "from core.autonomous.fix_generator import FixGenerator; print('OK')"

# 5. Run tests
pytest tests/autonomous/test_reflexion.py -v
```

### Automated Workflow

```python
from patterns.execution.exec005 import SyntaxErrorFixer

fixer = SyntaxErrorFixer()

# Scan for syntax errors
errors = fixer.scan_directory("core/", "error/", "gui/")

for file_path, line_num, error_msg in errors:
    print(f"Found error in {file_path}:{line_num}: {error_msg}")

    # Show context
    fixer.show_context(file_path, line_num)

    # Apply automated fix if possible
    if fixer.can_auto_fix(error_msg):
        success = fixer.auto_fix(file_path, line_num, error_msg)
        if success:
            print(f"✅ Auto-fixed {file_path}")
    else:
        print(f"⚠️  Manual fix required for {file_path}")
```

---

## Common Syntax Error Patterns

### IndentationError: unexpected unindent
```python
# WRONG
def function_a():
    line1
    line2
def function_b():  # ❌ IndentationError
    line1

# CORRECT
def function_a():
    line1
    line2

def function_b():  # ✅ Proper indentation
    line1
```

### SyntaxError: invalid syntax
```python
# WRONG
if condition  # ❌ Missing colon
    do_something()

# CORRECT
if condition:  # ✅ Colon added
    do_something()
```

### SyntaxError: unmatched parentheses
```python
# WRONG
result = function(
    arg1,
    arg2
# ❌ Missing closing paren

# CORRECT
result = function(
    arg1,
    arg2
)  # ✅ Closing paren added
```

---

## Verification Checklist

- [ ] File compiles without errors: `python -m py_compile <file>`
- [ ] Module can be imported: `python -c "import <module>"`
- [ ] Affected tests pass: `pytest tests/<module>/`
- [ ] No new syntax errors introduced
- [ ] Code formatting preserved (run ruff/black if needed)

---

## Anti-Patterns

❌ **Don't**: Make large refactoring changes while fixing syntax
✅ **Do**: Make minimal surgical fix to the specific line

❌ **Don't**: Fix syntax without verifying compilation
✅ **Do**: Always verify with `python -m py_compile`

❌ **Don't**: Ignore cascade effects on dependent modules
✅ **Do**: Re-run tests on dependent modules after fix

---

## Metrics

- **Fix Time**: 5-15 minutes per syntax error
- **Verification Time**: 2-5 minutes
- **Success Rate**: ~95% with proper context analysis
- **Cascade Prevention**: Fixes typically unblock 5-10 dependent files

---

## Integration

### Pre-Commit Hook
```bash
# .git/hooks/pre-commit
python -m compileall -q core/ error/ gui/
if [ $? -ne 0 ]; then
    echo "❌ Syntax errors detected - commit blocked"
    exit 1
fi
```

### CI/CD Gate
```yaml
# .github/workflows/syntax-check.yml
- name: Check Python syntax
  run: |
    python -m compileall -q .
    if [ $? -ne 0 ]; then
      echo "::error::Syntax errors detected"
      exit 1
    fi
```

---

## References

- **Python AST Module**: https://docs.python.org/3/library/ast.html
- **py_compile**: https://docs.python.org/3/library/py_compile.html
- **Validation Phase**: `reports/validation/VALIDATION_SUMMARY.md`

---

**Status**: ✅ Active
**Priority**: 🔴 CRITICAL
**Est. Time**: 15 minutes
**Complexity**: Low
