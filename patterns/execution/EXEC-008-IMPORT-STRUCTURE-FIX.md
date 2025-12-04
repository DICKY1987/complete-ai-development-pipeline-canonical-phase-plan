---
doc_id: DOC-PAT-EXEC-008-IMPORT-STRUCTURE-FIX-299
pattern_id: EXEC-008
version: 1.0.0
status: active
created: 2025-12-04
category: code_quality
priority: high
---

# EXEC-008: Import Structure Fix Pattern

## Overview

**Pattern Name**: Import Structure Repair
**Problem**: Module import errors due to incorrect paths or missing packages
**Solution**: Systematic discovery and repair of import structure issues
**Impact**: Enables test collection, module reusability, proper architecture

---

## Problem Statement

### Observed Behavior
```
ModuleNotFoundError: No module named 'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core'
ModuleNotFoundError: No module named 'gui.tui_app'
ModuleNotFoundError: No module named 'modules'
ModuleNotFoundError: No module named 'core.engine.aim_integration'

Result: 15+ test files cannot be collected
```

### Root Cause
- Module path refactoring not completed
- Missing __init__.py files
- Incorrect relative/absolute imports
- Package structure misalignment with code
- Deprecated module paths still referenced

### Cost
- **7-15 test files** fail to collect
- **Features broken**: Tests can't validate functionality
- **60-120 minutes** to diagnose and fix manually
- **Cascade failures**: Dependent modules also fail

---

## Solution Pattern

### Core Principle
**Map import errors to root causes, apply systematic fixes, verify**

### Implementation Steps

```python
import ast
import subprocess
from pathlib import Path
from typing import List, Dict, Set, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class ImportError:
    file_path: str
    line_number: int
    module_name: str
    error_type: str  # 'missing_module', 'missing_init', 'wrong_path'
    suggested_fix: Optional[str] = None


class ImportStructureFixer:
    """EXEC-008: Import structure repair pattern"""

    def __init__(self, root_dir: str = "."):
        self.root = Path(root_dir)
        self.errors = []
        self.module_map = {}  # Maps module names to actual file paths

    def discover_modules(self):
        """Build map of all Python modules in project"""
        for py_file in self.root.rglob("*.py"):
            if ".venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            # Convert file path to module path
            rel_path = py_file.relative_to(self.root)
            module_parts = list(rel_path.parts[:-1])  # Exclude filename

            if rel_path.name != "__init__.py":
                module_parts.append(rel_path.stem)

            module_name = ".".join(module_parts) if module_parts else ""

            if module_name:
                self.module_map[module_name] = py_file

    def analyze_imports(self, file_path: Path) -> List[str]:
        """Extract all import statements from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())

            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

            return imports
        except Exception as e:
            print(f"⚠️  Failed to parse {file_path}: {e}")
            return []

    def check_import_validity(self, module_name: str) -> bool:
        """Check if module can be imported"""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False

    def diagnose_import_error(self, file_path: str, module_name: str, line_num: int) -> ImportError:
        """
        Diagnose root cause of import error

        Returns:
            ImportError with diagnosis and suggested fix
        """
        # Check if module exists in project
        if module_name in self.module_map:
            return ImportError(
                file_path=file_path,
                line_number=line_num,
                module_name=module_name,
                error_type="missing_init",
                suggested_fix=f"Add __init__.py files to create package structure for {module_name}"
            )

        # Check for similar module names (typo or refactoring)
        similar = self.find_similar_modules(module_name)
        if similar:
            return ImportError(
                file_path=file_path,
                line_number=line_num,
                module_name=module_name,
                error_type="wrong_path",
                suggested_fix=f"Module may have been moved. Try: {similar[0]}"
            )

        # Module doesn't exist in project
        return ImportError(
            file_path=file_path,
            line_number=line_num,
            module_name=module_name,
            error_type="missing_module",
            suggested_fix=f"Module {module_name} not found. Create it or remove import."
        )

    def find_similar_modules(self, module_name: str, max_results: int = 3) -> List[str]:
        """Find modules with similar names (Levenshtein distance)"""
        from difflib import get_close_matches
        return get_close_matches(module_name, self.module_map.keys(), n=max_results, cutoff=0.6)

    def fix_missing_init_files(self):
        """Create missing __init__.py files to establish package structure"""
        directories_needing_init = set()

        for py_file in self.root.rglob("*.py"):
            if ".venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            # Check parent directories
            current = py_file.parent
            while current != self.root:
                init_file = current / "__init__.py"
                if not init_file.exists():
                    directories_needing_init.add(current)
                current = current.parent

        created = []
        for directory in directories_needing_init:
            init_file = directory / "__init__.py"
            init_file.touch()
            created.append(str(init_file.relative_to(self.root)))

        if created:
            print(f"✅ Created {len(created)} __init__.py files:")
            for path in created:
                print(f"   {path}")

        return created

    def update_import_statement(self, file_path: str, old_import: str, new_import: str):
        """Replace import statement in file"""
        path = Path(file_path)
        content = path.read_text()

        # Handle different import styles
        patterns = [
            f"from {old_import} import",
            f"import {old_import}",
        ]

        replacements = [
            f"from {new_import} import",
            f"import {new_import}",
        ]

        modified = content
        for pattern, replacement in zip(patterns, replacements):
            modified = modified.replace(pattern, replacement)

        if modified != content:
            path.write_text(modified)
            print(f"✅ Updated import in {file_path}")
            print(f"   {old_import} → {new_import}")
            return True

        return False
```

---

## Usage Pattern

### Manual Workflow

```bash
# Step 1: Identify import errors
pytest tests/ --collect-only 2>&1 | grep "ModuleNotFoundError"

# Step 2: Analyze each error
# Example: ModuleNotFoundError: No module named 'gui.tui_app'

# Step 3: Check if module exists
find gui/ -name "*tui_app*" -o -name "*tui*"

# Step 4: Create missing __init__.py files
# If gui/tui_app/ exists but missing __init__.py
touch gui/__init__.py
touch gui/tui_app/__init__.py

# Step 5: Fix import paths
# If module was renamed, update imports
sed -i 's/from gui.tui_app/from gui.tui/g' tests/**/*.py

# Step 6: Verify fix
python -c "from gui.tui_app import SomeClass"
pytest tests/gui/ --collect-only
```

### Automated Workflow

```python
from patterns.execution.exec008 import ImportStructureFixer

fixer = ImportStructureFixer(root_dir=".")

# Step 1: Discover all modules
fixer.discover_modules()
print(f"Found {len(fixer.module_map)} modules")

# Step 2: Fix missing __init__.py files
created = fixer.fix_missing_init_files()

# Step 3: Scan test files for import errors
test_files = Path("tests").rglob("*.py")
errors = []

for test_file in test_files:
    imports = fixer.analyze_imports(test_file)
    for import_name in imports:
        if not fixer.check_import_validity(import_name):
            error = fixer.diagnose_import_error(
                str(test_file),
                import_name,
                0  # Line number from AST if available
            )
            errors.append(error)

# Step 4: Report errors with suggested fixes
for error in errors:
    print(f"\n{error.error_type.upper()}: {error.file_path}")
    print(f"  Module: {error.module_name}")
    print(f"  Fix: {error.suggested_fix}")

# Step 5: Apply automated fixes
for error in errors:
    if error.error_type == "wrong_path" and error.suggested_fix:
        # Extract suggested module name
        suggested = error.suggested_fix.split("Try: ")[1]
        fixer.update_import_statement(
            error.file_path,
            error.module_name,
            suggested
        )
```

---

## Common Import Issues

### Missing __init__.py

```
Project structure:
├── core/
│   ├── engine/
│   │   └── router.py   # ❌ No __init__.py files
│   └── memory/
│       └── episodic.py

Import fails:
from core.engine.router import Router  # ModuleNotFoundError

Solution:
touch core/__init__.py
touch core/engine/__init__.py
touch core/memory/__init__.py
```

### Incorrect Module Path

```python
# WRONG (old path after refactoring)
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.interfaces import ToolAdapter

# CORRECT (new path)
from uet.interfaces import ToolAdapter
```

### Circular Import

```python
# module_a.py
from module_b import FunctionB  # ❌ Circular dependency

def function_a():
    return FunctionB()

# module_b.py
from module_a import FunctionA  # ❌ Circular dependency

def function_b():
    return FunctionA()

# Solution: Move shared code to third module or use late import
```

### Package vs Module Confusion

```python
# If gui/tui/ is a package (has __init__.py):
from gui.tui import MainApp  # ✅ Import from package

# If gui/tui.py is a module:
from gui.tui import MainApp  # ✅ Import from module

# Don't mix both - causes confusion
```

---

## Verification Checklist

- [ ] All __init__.py files present in package hierarchy
- [ ] Module can be imported: `python -c "import <module>"`
- [ ] Tests collect successfully: `pytest tests/ --collect-only`
- [ ] No circular import warnings
- [ ] IDE recognizes imports (no red squiggles)
- [ ] CI/CD builds succeed

---

## Anti-Patterns

❌ **Don't**: Add random __init__.py files without understanding structure
✅ **Do**: Map out package hierarchy first

❌ **Don't**: Use sys.path hacks to fix import issues
✅ **Do**: Fix the actual package structure

❌ **Don't**: Mix relative and absolute imports randomly
✅ **Do**: Choose one style and use consistently

❌ **Don't**: Leave deprecated import paths in code
✅ **Do**: Update all imports when refactoring modules

---

## Tools

### Automated Import Sorting

```bash
# Use isort to organize imports
pip install isort
isort core/ error/ gui/ tests/

# Configuration in pyproject.toml
[tool.isort]
profile = "black"
line_length = 120
```

### Import Graph Visualization

```python
# Use pydeps to visualize module dependencies
pip install pydeps
pydeps core --max-bacon=2 --cluster
```

---

## Metrics

- **Fix Time**: 30-90 minutes for complex refactoring
- **Success Rate**: 90%+ with systematic approach
- **Prevention**: 95% of future import errors via __init__.py
- **Maintenance**: Run import validation in CI

---

## Integration

### Pre-Commit Hook

```bash
# .git/hooks/pre-commit
python -c "
import sys
from pathlib import Path

# Check all packages have __init__.py
for py_file in Path('.').rglob('*.py'):
    if '.venv' in str(py_file):
        continue
    parent = py_file.parent
    if parent != Path('.') and not (parent / '__init__.py').exists():
        print(f'Missing __init__.py in {parent}')
        sys.exit(1)
"
```

### CI Validation

```yaml
# .github/workflows/import-check.yml
- name: Check imports
  run: |
    pytest tests/ --collect-only
    if [ $? -ne 0 ]; then
      echo "::error::Import errors detected"
      exit 1
    fi
```

---

## References

- **Python Modules**: https://docs.python.org/3/tutorial/modules.html
- **Package Structure**: https://packaging.python.org/en/latest/
- **Validation Report**: `reports/validation/VALIDATION_SUMMARY.md`

---

**Status**: ✅ Active
**Priority**: 🟠 HIGH
**Est. Time**: 60 minutes
**Complexity**: Medium-High
