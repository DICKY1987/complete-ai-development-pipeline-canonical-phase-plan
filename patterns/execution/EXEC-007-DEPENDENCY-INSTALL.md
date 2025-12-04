---
doc_id: DOC-PAT-EXEC-007-DEPENDENCY-INSTALL-298
pattern_id: EXEC-007
version: 1.0.0
status: active
created: 2025-12-04
category: environment
priority: high
---

# EXEC-007: Dependency Installation Pattern

## Overview

**Pattern Name**: Safe Dependency Installation
**Problem**: Missing dependencies causing import errors and test failures
**Solution**: Detect, install, and verify dependencies systematically
**Impact**: Enables code execution, tests pass, features work

---

## Problem Statement

### Observed Behavior
```
ModuleNotFoundError: No module named 'tree_sitter_javascript'
ModuleNotFoundError: No module named 'tree_sitter'
ModuleNotFoundError: No module named 'tree_sitter_python'

Result: AST intelligence system broken, 5+ test files fail
```

### Root Cause
- Dependencies added to code without updating requirements
- Missing packages not tracked in requirements.txt/pyproject.toml
- Environment drift between development and production
- No automated dependency verification

### Cost
- **2-5 test files fail** per missing dependency
- **15-30 minutes** to diagnose and fix
- **Feature breakage**: AST intelligence unusable
- **CI failures**: Blocks deployment

---

## Solution Pattern

### Core Principle
**Detect missing dependencies, install them, persist to requirements, verify**

### Implementation Steps

```python
import subprocess
import importlib
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class Dependency:
    name: str
    import_name: Optional[str] = None  # May differ from package name
    min_version: Optional[str] = None
    install_command: Optional[str] = None

    def __post_init__(self):
        if self.import_name is None:
            self.import_name = self.name


class DependencyManager:
    """EXEC-007: Safe dependency installation pattern"""

    def __init__(self, requirements_file: str = "requirements.txt"):
        self.requirements_file = Path(requirements_file)
        self.installed = set()
        self.failed = set()

    def check_dependency(self, dep: Dependency) -> bool:
        """Check if dependency is importable"""
        try:
            importlib.import_module(dep.import_name)
            return True
        except ImportError:
            return False

    def install_dependency(self, dep: Dependency) -> bool:
        """
        Install dependency using pip

        Returns:
            True if installation successful
        """
        package_spec = dep.name
        if dep.min_version:
            package_spec = f"{dep.name}>={dep.min_version}"

        cmd = ["pip", "install", package_spec]

        print(f"Installing {package_spec}...")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            # Verify installation
            if self.check_dependency(dep):
                print(f"✅ Successfully installed {dep.name}")
                self.installed.add(dep.name)
                return True
            else:
                print(f"❌ Installation succeeded but import failed for {dep.name}")
                self.failed.add(dep.name)
                return False

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep.name}")
            print(f"Error: {e.stderr}")
            self.failed.add(dep.name)
            return False

    def update_requirements(self, deps: List[Dependency]):
        """Add installed dependencies to requirements.txt"""
        if not self.requirements_file.exists():
            self.requirements_file.touch()

        existing = set()
        if self.requirements_file.exists():
            with open(self.requirements_file, 'r') as f:
                existing = {line.split('==')[0].split('>=')[0].strip()
                           for line in f if line.strip() and not line.startswith('#')}

        new_deps = []
        for dep in deps:
            if dep.name in self.installed and dep.name not in existing:
                if dep.min_version:
                    new_deps.append(f"{dep.name}>={dep.min_version}")
                else:
                    new_deps.append(dep.name)

        if new_deps:
            with open(self.requirements_file, 'a') as f:
                f.write('\n# Dependencies added by EXEC-007 pattern\n')
                for dep in new_deps:
                    f.write(f"{dep}\n")

            print(f"✅ Added {len(new_deps)} dependencies to {self.requirements_file}")

    def batch_install(self, deps: List[Dependency]) -> Dict[str, bool]:
        """
        Install multiple dependencies, update requirements

        Returns:
            Dict mapping dependency name to success status
        """
        results = {}

        for dep in deps:
            # Check if already installed
            if self.check_dependency(dep):
                print(f"✓ {dep.name} already installed")
                results[dep.name] = True
                continue

            # Install
            success = self.install_dependency(dep)
            results[dep.name] = success

        # Update requirements file
        self.update_requirements(deps)

        return results
```

---

## Usage Pattern

### Manual Workflow

```bash
# Step 1: Identify missing dependencies
python -c "import tree_sitter"  # Fails

# Step 2: Install missing package
pip install tree-sitter tree-sitter-javascript tree-sitter-python

# Step 3: Verify installation
python -c "import tree_sitter; print('OK')"
python -c "import tree_sitter_javascript; print('OK')"

# Step 4: Update requirements
pip freeze | grep tree-sitter >> requirements.txt

# Step 5: Test dependent functionality
pytest tests/ast_analysis/ -v
```

### Automated Workflow

```python
from patterns.execution.exec007 import DependencyManager, Dependency

# Define required dependencies
dependencies = [
    Dependency(
        name="tree-sitter",
        import_name="tree_sitter",
        min_version="0.20.0"
    ),
    Dependency(
        name="tree-sitter-javascript",
        import_name="tree_sitter_javascript"
    ),
    Dependency(
        name="tree-sitter-python",
        import_name="tree_sitter_python"
    ),
]

# Install and verify
manager = DependencyManager()
results = manager.batch_install(dependencies)

# Report
for dep_name, success in results.items():
    status = "✅" if success else "❌"
    print(f"{status} {dep_name}")

# Verify all succeeded
if all(results.values()):
    print("\n✅ All dependencies installed successfully")
else:
    failed = [name for name, success in results.items() if not success]
    print(f"\n❌ Failed to install: {', '.join(failed)}")
```

---

## Common Dependency Patterns

### Package Name ≠ Import Name

```python
# Package: tree-sitter-javascript
# Import: tree_sitter_javascript

Dependency(
    name="tree-sitter-javascript",
    import_name="tree_sitter_javascript"
)

# Package: Pillow
# Import: PIL
Dependency(
    name="Pillow",
    import_name="PIL"
)

# Package: beautifulsoup4
# Import: bs4
Dependency(
    name="beautifulsoup4",
    import_name="bs4"
)
```

### Version Constraints

```python
# Minimum version
Dependency(
    name="pytest",
    min_version="7.0.0"
)

# Exact version (use install_command)
Dependency(
    name="ruff",
    install_command="pip install ruff==0.1.9"
)
```

### Optional Dependencies

```python
# Try to install, don't fail if unavailable
def install_optional(dep: Dependency) -> bool:
    """Install optional dependency, return success without failing"""
    try:
        return manager.install_dependency(dep)
    except Exception as e:
        print(f"⚠️  Optional dependency {dep.name} not available: {e}")
        return False
```

---

## Verification Checklist

- [ ] Dependency installs without errors
- [ ] Module can be imported: `python -c "import <module>"`
- [ ] Dependent tests pass: `pytest tests/<module>/`
- [ ] Added to requirements.txt or pyproject.toml
- [ ] Version constraint specified (if needed)
- [ ] CI/CD pipeline updated (if needed)

---

## Anti-Patterns

❌ **Don't**: Install globally without tracking in requirements
✅ **Do**: Always update requirements.txt after install

❌ **Don't**: Install without version constraints for production
✅ **Do**: Specify minimum versions for stability

❌ **Don't**: Assume install success based on exit code alone
✅ **Do**: Verify with actual import test

❌ **Don't**: Install dependencies one at a time manually
✅ **Do**: Use batch installation with verification

---

## Requirements Management

### requirements.txt Format

```txt
# Core dependencies
pytest>=7.0.0
ruff>=0.1.0

# AST parsing (added by EXEC-007)
tree-sitter>=0.20.0
tree-sitter-javascript>=0.21.0
tree-sitter-python>=0.21.0

# Testing utilities
pytest-cov>=4.0.0
pytest-html>=3.2.0
```

### pyproject.toml Format

```toml
[project]
dependencies = [
    "pytest>=7.0.0",
    "ruff>=0.1.0",
    "tree-sitter>=0.20.0",
    "tree-sitter-javascript>=0.21.0",
    "tree-sitter-python>=0.21.0",
]

[project.optional-dependencies]
dev = [
    "pytest-cov>=4.0.0",
    "pytest-html>=3.2.0",
]
```

---

## Environment Management

### Virtual Environment Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify environment
pip list
python -c "import tree_sitter; print('OK')"
```

### Dependency Lock File

```bash
# Generate lock file for reproducible installs
pip freeze > requirements.lock

# Install from lock file (exact versions)
pip install -r requirements.lock
```

---

## Metrics

- **Install Time**: 15-60 seconds per package
- **Verification Time**: 5-10 seconds
- **Success Rate**: 95%+ for published packages
- **Maintenance**: Update quarterly or when features change

---

## Integration

### Pre-Flight Check Script

```python
# scripts/check_dependencies.py
from patterns.execution.exec007 import DependencyManager, Dependency

REQUIRED_DEPS = [
    Dependency("pytest", min_version="7.0.0"),
    Dependency("ruff", min_version="0.1.0"),
    Dependency("tree-sitter", "tree_sitter", min_version="0.20.0"),
]

def main():
    manager = DependencyManager()

    missing = []
    for dep in REQUIRED_DEPS:
        if not manager.check_dependency(dep):
            missing.append(dep.name)

    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("\nRun: python scripts/install_dependencies.py")
        return 1

    print("✅ All dependencies available")
    return 0

if __name__ == "__main__":
    exit(main())
```

### CI/CD Cache

```yaml
# .github/workflows/test.yml
- name: Cache dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}

- name: Install dependencies
  run: pip install -r requirements.txt

- name: Verify dependencies
  run: python scripts/check_dependencies.py
```

---

## References

- **pip Documentation**: https://pip.pypa.io/
- **pyproject.toml**: https://packaging.python.org/en/latest/specifications/pyproject-toml/
- **Validation Report**: `reports/validation/VALIDATION_SUMMARY.md`

---

**Status**: ✅ Active
**Priority**: 🟠 HIGH
**Est. Time**: 15 minutes
**Complexity**: Low
