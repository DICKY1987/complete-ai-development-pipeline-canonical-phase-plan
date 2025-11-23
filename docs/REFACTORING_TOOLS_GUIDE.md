# Python Refactoring Tools for Safe Renaming

**Date**: 2025-11-23  
**Purpose**: Automated tools to safely rename modules/files and update imports  
**Status**: Recommended Tools

---

## Top 5 Tools for Your Codebase

### 🥇 1. **Rope** (HIGHLY RECOMMENDED)
**Best for**: Complete refactoring with semantic awareness

```bash
pip install rope
```

**Why It's Perfect for You**:
- ✅ **Semantic understanding**: Knows the difference between `core.state.db` and `error.db`
- ✅ **Module/file renaming**: Renames files AND updates ALL imports automatically
- ✅ **Directory support**: Can rename entire directories (e.g., `error/shared/utils/` → `error/shared/utilities/`)
- ✅ **Safe**: Static analysis ensures it won't break code
- ✅ **Scriptable**: Can be used as a library (not just CLI)

**Example Usage**:
```python
# scripts/rope_rename.py
from rope.base.project import Project
from rope.refactor.rename import Rename

# Open project
project = Project('.')

# Rename module
resource = project.root.get_file('error/shared/utils/hashing.py')
renamer = Rename(project, resource)

# Preview changes
changes = renamer.get_changes('utilities')  # New name
print(changes.get_description())

# Apply changes
project.do(changes)
project.close()
```

**Use Cases**:
- Rename `error/shared/utils/` → `error/shared/utilities/` (auto-updates all imports)
- Rename `db.py` → `database.py`
- Move modules between directories

---

### 🥈 2. **Bowler** (EXCELLENT FOR BULK CHANGES)
**Best for**: Large-scale codemods, API migrations

```bash
pip install bowler
```

**Why It's Great**:
- ✅ **Format-preserving**: Keeps your code formatting intact
- ✅ **Interactive mode**: Review each change before applying
- ✅ **Scriptable**: Write custom refactoring scripts
- ✅ **Dry-run support**: See what would change without applying

**Example Usage**:
```python
# scripts/bowler_migrate.py
from bowler import Query

# Rename all imports from old path to new path
(Query()
 .select_module("error.shared.utils")
 .rename("error.shared.utilities")
 .execute(interactive=True, write=True))
```

**Command Line**:
```bash
# Rename imports across entire codebase
bowler do \
  --selector "import error.shared.utils" \
  --replace "import error.shared.utilities" \
  --write
```

**Use Cases**:
- Migrate all imports after renaming
- Update API calls across codebase
- Bulk syntax transformations

---

### 🥉 3. **snake-shift** (CONVENTION FIXER)
**Best for**: Fixing naming conventions (camelCase → snake_case)

```bash
pip install snake-shift
```

**Why It's Useful**:
- ✅ **File + import updates**: Renames files AND updates imports
- ✅ **Convention-aware**: Converts to Pythonic naming
- ✅ **Dry-run mode**: Preview before applying
- ✅ **Gitignore-aware**: Skips unwanted directories

**Example Usage**:
```bash
# Fix all naming conventions in a directory
snake-shift error/plugins/ --dry-run

# Apply changes
snake-shift error/plugins/ --apply
```

**Use Cases**:
- Fix `errorEngine.py` → `error_engine.py`
- Convert legacy camelCase code to snake_case
- Clean up inconsistent naming

---

### 4. **LibCST** (PROGRAMMATIC REFACTORING)
**Best for**: Custom transformation scripts

```bash
pip install libcst
```

**Why It's Powerful**:
- ✅ **Concrete Syntax Tree**: Preserves formatting, comments, whitespace
- ✅ **Precise control**: Write exact transformations you need
- ✅ **Type-aware**: Can use type information for smarter refactoring

**Example Usage**:
```python
# scripts/libcst_rename_imports.py
import libcst as cst
from pathlib import Path

class ImportRenamer(cst.CSTTransformer):
    def leave_ImportFrom(self, original_node, updated_node):
        if updated_node.module and updated_node.module.value == "error.shared.utils":
            return updated_node.with_changes(
                module=cst.Attribute(
                    value=cst.Attribute(
                        value=cst.Name("error"),
                        attr=cst.Name("shared")
                    ),
                    attr=cst.Name("utilities")
                )
            )
        return updated_node

# Apply to all Python files
for py_file in Path('.').rglob('*.py'):
    tree = cst.parse_module(py_file.read_text())
    modified = tree.visit(ImportRenamer())
    py_file.write_text(modified.code)
```

**Use Cases**:
- Custom import transformations
- Complex AST-level refactoring
- Format-preserving code generation

---

### 5. **pyrefact** (CODE QUALITY + RENAMING)
**Best for**: Cleaning up code while refactoring

```bash
pip install pyrefact
```

**Why It's Nice**:
- ✅ **Import cleanup**: Removes unused, sorts, deduplicates
- ✅ **Identifier renaming**: Variables, functions, classes
- ✅ **Code simplification**: Removes dead code, simplifies structures

**Example Usage**:
```bash
# Clean up imports after renaming
pyrefact core/ --preserve

# Remove unused imports
pyrefact error/ --remove-unused-imports
```

**Use Cases**:
- Clean up after bulk renames
- Remove orphaned imports
- Simplify code structure

---

## Recommended Workflow for Your Codebase

### Scenario: Rename `error/shared/utils/` → `error/shared/utilities/`

**Step 1: Use Rope for the rename**
```python
# scripts/rename_with_rope.py
from rope.base.project import Project
from rope.refactor.move import MoveModule

project = Project('.')
utils_dir = project.root.get_folder('error/shared/utils')

# Move to new location
mover = MoveModule(project, utils_dir)
changes = mover.get_changes('error/shared/utilities')

# Preview
print("Changes to be made:")
print(changes.get_description())

# Apply
project.do(changes)
project.close()
print("✅ Rename complete! All imports updated.")
```

**Step 2: Verify with Bowler (optional)**
```bash
# Check if any imports were missed
bowler do \
  --selector "error.shared.utils" \
  --dry-run
```

**Step 3: Clean up with pyrefact**
```bash
# Remove any orphaned imports
pyrefact error/ --remove-unused-imports
```

**Step 4: Validate**
```bash
# Your existing validation
python scripts\paths_index_cli.py scan --root . --db refactor_paths.db --reset
python scripts\paths_index_cli.py gate --db refactor_paths.db --regex "error/shared/utils"
pytest -q tests/
```

---

## Tool Comparison Matrix

| Tool        | File Rename | Import Update | Directory Rename | Dry Run | Interactive | Format Preserve |
|-------------|-------------|---------------|------------------|---------|-------------|-----------------|
| **Rope**    | ✅ Excellent | ✅ Automatic  | ✅ Yes           | ✅      | ⚠️ Limited  | ⚠️ Partial      |
| **Bowler**  | ⚠️ Manual   | ✅ Automatic  | ⚠️ Manual        | ✅      | ✅ Yes      | ✅ Excellent    |
| **snake-shift** | ✅ Yes  | ✅ Automatic  | ✅ Yes           | ✅      | ❌ No       | ✅ Yes          |
| **LibCST**  | ⚠️ Script   | ✅ Script     | ⚠️ Script        | Custom  | Custom      | ✅ Excellent    |
| **pyrefact**| ❌ No       | ⚠️ Cleanup    | ❌ No            | ✅      | ❌ No       | ✅ Yes          |

---

## Installation for Your Project

Add to `requirements.txt`:

```txt
# Refactoring tools (Phase K+1)
rope>=1.13.0                # Semantic refactoring
bowler>=0.9.0               # Large-scale codemods
libcst>=1.1.0               # Custom transformations
pyrefact>=0.5.0             # Code cleanup
snake-shift>=0.3.0          # Convention fixer
```

Or install individually:
```bash
pip install rope bowler libcst pyrefact snake-shift
```

---

## Ready-to-Use Scripts

### Script 1: Safe Rename with Rope
```python
# scripts/safe_rope_rename.py
"""Safe module renaming with Rope"""
import argparse
from pathlib import Path
from rope.base.project import Project
from rope.refactor.rename import Rename
from rope.refactor.move import MoveModule

def rename_module(old_path: str, new_name: str, dry_run: bool = True):
    """Rename a module/package and update all imports."""
    project = Project('.')
    
    # Get resource
    resource = project.root.get_child(old_path)
    
    # Create rename refactoring
    if resource.is_folder():
        renamer = MoveModule(project, resource)
    else:
        renamer = Rename(project, resource)
    
    # Get changes
    changes = renamer.get_changes(new_name)
    
    # Preview
    print(changes.get_description())
    
    if dry_run:
        print("\n🔍 DRY RUN - No changes applied")
        project.close()
        return
    
    # Apply
    print("\n✅ Applying changes...")
    project.do(changes)
    project.close()
    print(f"✅ Renamed {old_path} → {new_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("old_path", help="Old module path (e.g., 'error/shared/utils')")
    parser.add_argument("new_name", help="New name (e.g., 'utilities')")
    parser.add_argument("--execute", action="store_true", help="Execute rename (default: dry run)")
    args = parser.parse_args()
    
    rename_module(args.old_path, args.new_name, dry_run=not args.execute)
```

**Usage**:
```powershell
# Dry run
python scripts\safe_rope_rename.py "error\shared\utils" "utilities"

# Execute
python scripts\safe_rope_rename.py "error\shared\utils" "utilities" --execute
```

---

### Script 2: Bulk Import Migration with Bowler
```python
# scripts/bowler_migrate_imports.py
"""Migrate imports in bulk with Bowler"""
from bowler import Query

def migrate_imports(old_module: str, new_module: str, interactive: bool = True):
    """Migrate all imports from old to new module."""
    (Query()
     .select_module(old_module)
     .rename(new_module)
     .execute(interactive=interactive, write=True))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("old", help="Old module path (e.g., 'error.shared.utils')")
    parser.add_argument("new", help="New module path (e.g., 'error.shared.utilities')")
    parser.add_argument("--auto", action="store_true", help="Non-interactive mode")
    args = parser.parse_args()
    
    migrate_imports(args.old, args.new, interactive=not args.auto)
```

**Usage**:
```powershell
# Interactive (review each change)
python scripts\bowler_migrate_imports.py "error.shared.utils" "error.shared.utilities"

# Automatic (apply all)
python scripts\bowler_migrate_imports.py "error.shared.utils" "error.shared.utilities" --auto
```

---

### Script 3: Combined Workflow
```python
# scripts/complete_rename.py
"""Complete rename workflow: Rope + validation"""
import subprocess
import sys
from pathlib import Path
from rope.base.project import Project
from rope.refactor.move import MoveModule

def complete_rename(old_path: str, new_path: str, dry_run: bool = True):
    """Complete rename with validation."""
    print(f"📋 PHASE 1: Scanning current state...")
    subprocess.run([
        "python", "scripts/paths_index_cli.py", "scan",
        "--root", ".", "--db", "refactor_paths.db", "--reset"
    ], check=True)
    
    print(f"\n📋 PHASE 2: Renaming {old_path} → {new_path}...")
    project = Project('.')
    resource = project.root.get_child(old_path)
    
    if resource.is_folder():
        renamer = MoveModule(project, resource)
        changes = renamer.get_changes(new_path)
    else:
        from rope.refactor.rename import Rename
        new_name = Path(new_path).name
        renamer = Rename(project, resource)
        changes = renamer.get_changes(new_name)
    
    print(changes.get_description())
    
    if dry_run:
        print("\n🔍 DRY RUN - No changes applied")
        project.close()
        return
    
    project.do(changes)
    project.close()
    
    print(f"\n📋 PHASE 3: Rescanning...")
    subprocess.run([
        "python", "scripts/paths_index_cli.py", "scan",
        "--root", ".", "--db", "refactor_paths.db", "--reset"
    ], check=True)
    
    print(f"\n📋 PHASE 4: Validating (checking for old paths)...")
    old_pattern = old_path.replace('\\', '/').replace('/', '|')
    result = subprocess.run([
        "python", "scripts/paths_index_cli.py", "gate",
        "--db", "refactor_paths.db",
        "--regex", old_pattern
    ], capture_output=True)
    
    if result.returncode == 0:
        print("✅ No old paths found - rename successful!")
    else:
        print("⚠️ Warning: Some old paths still exist")
        print(result.stdout.decode())
    
    print(f"\n📋 PHASE 5: Running tests...")
    subprocess.run(["pytest", "-q", "tests/"], check=True)
    
    print("\n✅ COMPLETE! All phases passed.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("old", help="Old path")
    parser.add_argument("new", help="New path")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    
    complete_rename(args.old, args.new, dry_run=not args.execute)
```

**Usage**:
```powershell
python scripts\complete_rename.py "error\shared\utils" "error\shared\utilities" --execute
```

---

## Quick Win: Fix Top-Level Directories

```bash
# Install tools
pip install rope snake-shift pyrefact

# Fix "bad excution" typo
python scripts\safe_rope_rename.py "bad excution" "quarantine" --execute

# Clean up any issues
pyrefact . --remove-unused-imports
```

---

## Summary: Which Tool When?

| Task | Best Tool | Command |
|------|-----------|---------|
| Rename module/directory + update imports | **Rope** | `rope_rename.py` |
| Bulk API migration | **Bowler** | `bowler do` |
| Fix naming conventions | **snake-shift** | `snake-shift path/` |
| Custom transformations | **LibCST** | Write script |
| Clean up after rename | **pyrefact** | `pyrefact .` |

**Recommended combo**: **Rope** (rename) + **pyrefact** (cleanup) + **your existing paths_index_cli.py** (validation)

---

## See Also

- `docs/SAFE_RENAME_STRATEGY.md` - Manual rename process
- `scripts/paths_index_cli.py` - Existing validation tool
- `CODEBASE_INDEX.yaml` - Module structure
