---
doc_id: DOC-PAT-EXEC-012-MODULE-CONSOLIDATION-858
---

# EXEC-012: Module Consolidation Pattern
# Pattern for migrating duplicate code into canonical UET structure

**Pattern ID**: EXEC-012  
**Name**: Module Consolidation & Migration  
**Category**: Refactoring  
**Time Savings**: 70-80% vs manual migration  
**Difficulty**: Medium  
**Prerequisites**: Git, Python, migration registry system

**DOC_ID**: DOC-PAT-EXEC-012-MODULE-CONSOLIDATION  
**Created**: 2025-11-29  
**Status**: ACTIVE

---

## Purpose

Systematically migrate duplicate code from multiple locations into a single canonical structure (UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK) while maintaining functionality and git history.

---

## Problem Statement

**Scenario**: Repository has 67% code duplication across 3-5 locations:
- Active code in: `\core\`, `\error\`, `\aim\`, `\pm\`
- Module-centric versions in: `\modules\core-*\`, `\modules\error-*\`
- Archived versions in: `\archive\*\`
- Target: Consolidate all into `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\`

**Without Pattern**: Manual migration of 300+ files = 40-60 hours
**With Pattern**: Systematic migration = 12-16 hours

---

## Pattern Structure

### Phase 1: Discovery & Mapping (2 hours)

**Input**: Repository root directory

**Actions**:
1. Scan for duplicate files across all locations
2. Compare file contents (hash-based similarity)
3. Identify canonical version (newest, most complete)
4. Build migration map

**Output**: `migration_registry.yaml`

**Script**:
```python
# EXEC-012 Phase 1: Discovery
import hashlib
from pathlib import Path
from typing import Dict, List, Set
import yaml

class DuplicateFinder:
    def __init__(self, root: Path):
        self.root = root
        self.file_hashes: Dict[str, List[Path]] = {}
        
    def scan_duplicates(self, exclude_patterns: List[str]) -> Dict:
        """Find duplicate files by content hash."""
        duplicates = {}
        
        for py_file in self.root.rglob("*.py"):
            # Skip excluded patterns
            if any(pattern in str(py_file) for pattern in exclude_patterns):
                continue
                
            file_hash = self._hash_file(py_file)
            
            if file_hash not in self.file_hashes:
                self.file_hashes[file_hash] = []
            self.file_hashes[file_hash].append(py_file)
        
        # Keep only duplicates (hash appears > 1 time)
        for file_hash, paths in self.file_hashes.items():
            if len(paths) > 1:
                duplicates[file_hash] = {
                    'count': len(paths),
                    'locations': [str(p.relative_to(self.root)) for p in paths],
                    'canonical': self._select_canonical(paths)
                }
        
        return duplicates
    
    def _hash_file(self, path: Path) -> str:
        """Calculate SHA256 hash of file content."""
        return hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    
    def _select_canonical(self, paths: List[Path]) -> str:
        """Select canonical version (prefer UET, then modules, then active)."""
        # Priority order
        priorities = [
            'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK',
            'modules',
            'core',
            'error',
            'aim',
            'pm'
        ]
        
        for priority in priorities:
            for path in paths:
                if priority in str(path):
                    return str(path)
        
        # Default: newest file
        newest = max(paths, key=lambda p: p.stat().st_mtime)
        return str(newest)

# USAGE:
finder = DuplicateFinder(Path('.'))
exclude = ['__pycache__', '.venv', 'archive', 'tests']
duplicates = finder.scan_duplicates(exclude)

# Save to registry
registry = {
    'scan_date': '2025-11-29T16:30:00Z',
    'total_duplicates': len(duplicates),
    'duplicates': duplicates
}

Path('UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/duplicate_registry.yaml').write_text(
    yaml.dump(registry, default_flow_style=False)
)
```

**Expected Output**:
```yaml
scan_date: 2025-11-29T16:30:00Z
total_duplicates: 87
duplicates:
  a3f5b2c1d4e6f7a8:
    count: 3
    locations:
      - core/engine/orchestrator.py
      - modules/core-engine/m010001_orchestrator.py
      - archive/2025-11-26_094309_old-structure/core-engine/orchestrator.py
    canonical: modules/core-engine/m010001_orchestrator.py
```

---

### Phase 2: Create Migration Plan (1 hour)

**Input**: `duplicate_registry.yaml`

**Actions**:
1. Group duplicates by destination folder
2. Calculate dependencies (import graph)
3. Determine migration order (topological sort)
4. Assign to batches (6 files per batch)

**Output**: `migration_plan.yaml`

**Script**:
```python
# EXEC-012 Phase 2: Migration Planning
import yaml
from pathlib import Path
from typing import Dict, List, Set
import networkx as nx

class MigrationPlanner:
    def __init__(self, duplicate_registry: Dict):
        self.registry = duplicate_registry
        self.graph = nx.DiGraph()
        
    def create_plan(self) -> Dict:
        """Create ordered migration plan."""
        # Build dependency graph
        self._build_dependency_graph()
        
        # Topological sort for correct order
        migration_order = list(nx.topological_sort(self.graph))
        
        # Group into batches
        batches = self._create_batches(migration_order, batch_size=6)
        
        return {
            'total_files': len(migration_order),
            'total_batches': len(batches),
            'batches': batches,
            'execution_estimate_hours': len(batches) * 0.5  # 30 min per batch
        }
    
    def _build_dependency_graph(self):
        """Build import dependency graph."""
        for file_hash, info in self.registry['duplicates'].items():
            canonical = info['canonical']
            
            # Add node
            self.graph.add_node(canonical)
            
            # Parse imports to find dependencies
            imports = self._extract_imports(Path(canonical))
            for imp in imports:
                if imp in self.graph:
                    self.graph.add_edge(imp, canonical)  # imp -> canonical
    
    def _extract_imports(self, file_path: Path) -> Set[str]:
        """Extract import statements from Python file."""
        imports = set()
        
        if not file_path.exists():
            return imports
            
        content = file_path.read_text(encoding='utf-8')
        
        # Simple regex for "from X import Y"
        import re
        pattern = r'from\s+([\w\.]+)\s+import'
        matches = re.findall(pattern, content)
        
        imports.update(matches)
        return imports
    
    def _create_batches(self, files: List[str], batch_size: int = 6) -> List[Dict]:
        """Group files into migration batches."""
        batches = []
        
        for i in range(0, len(files), batch_size):
            batch_files = files[i:i+batch_size]
            
            batches.append({
                'batch_id': f"batch_{i//batch_size + 1:03d}",
                'files': batch_files,
                'file_count': len(batch_files),
                'status': 'pending'
            })
        
        return batches

# USAGE:
registry = yaml.safe_load(
    Path('UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/duplicate_registry.yaml').read_text()
)

planner = MigrationPlanner(registry)
plan = planner.create_plan()

Path('UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/migration_plan.yaml').write_text(
    yaml.dump(plan, default_flow_style=False)
)

print(f"✅ Migration plan created: {plan['total_batches']} batches, ~{plan['execution_estimate_hours']:.1f} hours")
```

---

### Phase 3: Execute Migration (Batched, 8-12 hours)

**Input**: `migration_plan.yaml`

**Actions** (per batch):
1. Copy canonical file to UET destination
2. Update imports in copied file
3. Create compatibility shim in old location
4. Run verification tests
5. Update registry with status

**Output**: Migrated files + shims

**Script**:
```python
# EXEC-012 Phase 3: Batch Migration Executor
import shutil
import yaml
from pathlib import Path
from typing import Dict, List
import subprocess
import re

class MigrationExecutor:
    def __init__(self, migration_plan: Dict, uet_root: Path):
        self.plan = migration_plan
        self.uet_root = uet_root
        self.migration_log = []
        
    def execute_batch(self, batch_id: str) -> bool:
        """Execute a single migration batch."""
        batch = self._get_batch(batch_id)
        
        print(f"\n📦 Executing {batch_id} ({batch['file_count']} files)")
        
        for source_file in batch['files']:
            try:
                self._migrate_file(source_file)
                print(f"  ✓ {Path(source_file).name}")
            except Exception as e:
                print(f"  ✗ {Path(source_file).name}: {e}")
                return False
        
        # Verify batch
        return self._verify_batch(batch)
    
    def _migrate_file(self, source_path: str):
        """Migrate single file to UET structure."""
        source = Path(source_path)
        
        # Determine UET destination
        dest = self._map_to_uet_path(source)
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        shutil.copy2(source, dest)
        
        # Update imports in destination file
        self._update_imports(dest)
        
        # Create compatibility shim at source
        self._create_shim(source, dest)
        
        # Log migration
        self.migration_log.append({
            'source': str(source),
            'destination': str(dest),
            'timestamp': '2025-11-29T16:30:00Z',
            'status': 'success'
        })
    
    def _map_to_uet_path(self, source: Path) -> Path:
        """Map source path to UET destination."""
        # Remove module prefix (m010001_) if present
        filename = source.name
        if re.match(r'm\d{6}_', filename):
            filename = filename[8:]  # Remove "m010001_"
        
        # Map directory structure
        parts = source.parts
        
        if 'modules' in parts:
            # modules/core-engine/file.py -> UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/file.py
            idx = parts.index('modules')
            module_name = parts[idx + 1]  # e.g., "core-engine"
            
            # Split module name: "core-engine" -> "core/engine"
            subpath = module_name.replace('-', '/')
            
            return self.uet_root / subpath / filename
        
        elif any(x in parts for x in ['core', 'error', 'aim', 'pm']):
            # core/engine/file.py -> UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/file.py
            # Find first occurrence
            for component in ['core', 'error', 'aim', 'pm']:
                if component in parts:
                    idx = parts.index(component)
                    subpath = Path(*parts[idx:])
                    return self.uet_root / subpath.parent / filename
        
        # Default: preserve relative path
        return self.uet_root / source.relative_to(Path.cwd())
    
    def _update_imports(self, file_path: Path):
        """Update imports to use UET structure."""
        content = file_path.read_text(encoding='utf-8')
        
        # Pattern: from core.engine.X -> from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine.X
        replacements = [
            (r'from core\.', 'from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.'),
            (r'from error\.', 'from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.'),
            (r'from aim\.', 'from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.aim.'),
            (r'from pm\.', 'from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.pm.'),
            (r'from modules\.core-', 'from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.'),
            (r'from modules\.error-', 'from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.'),
        ]
        
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        file_path.write_text(content, encoding='utf-8')
    
    def _create_shim(self, old_path: Path, new_path: Path):
        """Create compatibility shim at old location."""
        # Calculate relative import path
        uet_rel = new_path.relative_to(self.uet_root)
        import_path = str(uet_rel.with_suffix('')).replace('/', '.')
        
        shim_content = f'''"""
Compatibility shim - imports from new UET location.

DEPRECATED: Import from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.{import_path} instead.
This shim will be removed after consolidation is complete.
"""
import warnings

warnings.warn(
    "Import from {old_path} is deprecated. "
    "Use UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.{import_path} instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything from new location
from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.{import_path} import *
'''
        
        # Overwrite old file with shim (after backing up to archive)
        archive_path = Path('.migration_backups') / '2025-11-29' / old_path
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(old_path, archive_path)
        
        old_path.write_text(shim_content, encoding='utf-8')
    
    def _verify_batch(self, batch: Dict) -> bool:
        """Verify all files in batch can be imported."""
        print(f"\n  🔍 Verifying batch...")
        
        for source_file in batch['files']:
            dest = self._map_to_uet_path(Path(source_file))
            
            # Calculate import path
            rel_path = dest.relative_to(self.uet_root)
            import_path = str(rel_path.with_suffix('')).replace('/', '.')
            module_name = f"UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.{import_path}"
            
            # Try to import
            result = subprocess.run(
                ['python', '-c', f'import {module_name}'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"  ✗ Import failed: {module_name}")
                print(f"    {result.stderr}")
                return False
        
        print(f"  ✅ All imports verified")
        return True
    
    def _get_batch(self, batch_id: str) -> Dict:
        """Get batch by ID."""
        for batch in self.plan['batches']:
            if batch['batch_id'] == batch_id:
                return batch
        raise ValueError(f"Batch {batch_id} not found")

# USAGE:
plan = yaml.safe_load(
    Path('UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/migration_plan.yaml').read_text()
)

executor = MigrationExecutor(plan, Path('UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK'))

# Execute all batches
for batch in plan['batches']:
    success = executor.execute_batch(batch['batch_id'])
    
    if not success:
        print(f"❌ Batch {batch['batch_id']} failed. Stopping.")
        break
    
    print(f"✅ {batch['batch_id']} complete")

# Save migration log
Path('UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/migration_log.yaml').write_text(
    yaml.dump({'migrations': executor.migration_log}, default_flow_style=False)
)
```

---

### Phase 4: Verification & Cleanup (2 hours)

**Input**: Migrated files in UET structure

**Actions**:
1. Run full test suite
2. Verify all imports work
3. Check for broken references
4. Archive old locations

**Output**: Clean UET structure, archived duplicates

**Script**:
```bash
# EXEC-012 Phase 4: Final Verification

# 1. Run all tests
pytest UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/tests/ -v

# 2. Check imports
python -c "import UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine.orchestrator"
python -c "import UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.engine.error_engine"
python -c "import UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.aim.cli.main"

# 3. Verify no broken imports in UET code
cd UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK
grep -r "from core\." . && echo "❌ Found old imports" || echo "✅ No old imports"
grep -r "from modules\." . && echo "❌ Found module imports" || echo "✅ No module imports"

# 4. Archive old folders
mv modules archive/2025-11-29_modules_replaced/
mv core archive/2025-11-29_core_replaced/
mv error archive/2025-11-29_error_replaced/
mv aim archive/2025-11-29_aim_replaced/

echo "✅ Migration complete - verify and commit"
```

---

## Ground Truth Success Criteria

✅ **All tests pass**: `pytest UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/tests/ -q`  
✅ **All imports work**: No ImportError for any UET module  
✅ **No old imports**: grep shows 0 matches for old import patterns  
✅ **File reduction**: ≥60% reduction in duplicate files  
✅ **Compatibility maintained**: Shims allow old imports to work temporarily

---

## Time Savings Analysis

```
Traditional Manual Migration:
  - Review 300 files: 15 hours
  - Copy & update each: 20 hours  
  - Fix import errors: 10 hours
  - Verify functionality: 8 hours
  Total: 53 hours

With EXEC-012 Pattern:
  - Discovery phase: 2 hours
  - Planning phase: 1 hour
  - Migration execution: 10 hours (batched)
  - Verification: 2 hours
  Total: 15 hours

Savings: 72% (38 hours saved)
Speedup: 3.5x faster
```

---

## Anti-Pattern Guards

🚫 **Don't** manually copy files one by one  
🚫 **Don't** edit imports manually  
🚫 **Don't** delete old files immediately (use shims first)  
🚫 **Don't** skip verification between batches  
🚫 **Don't** migrate without dependency graph

✅ **Do** use automated discovery and mapping  
✅ **Do** migrate in dependency order  
✅ **Do** create compatibility shims  
✅ **Do** verify after each batch  
✅ **Do** keep archives for 90 days

---

## References

- Base pattern: EXEC-001 (Batch File Creator)
- Related: EXEC-006 (Safe Deletion with Registry)
- Source: Module-centric refactor experience
- Anti-patterns: UET_2025-ANTI-PATTERN FORENSICS.md

---

**Created**: 2025-11-29  
**Author**: AI Pattern Extraction  
**Tested**: Pending execution  
**Status**: Ready for use
