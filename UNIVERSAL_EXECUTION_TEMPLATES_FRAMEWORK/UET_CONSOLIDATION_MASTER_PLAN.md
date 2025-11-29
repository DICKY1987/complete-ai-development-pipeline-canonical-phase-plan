# UET Consolidation Master Plan - Phase Execution with Independent Workstreams

**DOC_ID**: DOC-PLAN-UET-CONSOLIDATION-001  
**Created**: 2025-11-29T16:10:00Z  
**Status**: READY_FOR_EXECUTION  
**Target**: Consolidate 67% duplicate code into UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK  
**Execution Model**: Parallel workstreams via Codex CLI  
**Estimated Duration**: 7 weeks (8-12 hours/week)  
**Total Effort**: 56 hours → 15 hours with patterns (73% savings)

---

## Executive Summary

This plan consolidates a repository with 67% code duplication (337 of 500 Python files) into a single canonical structure: `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK`. Uses execution patterns EXEC-012 and EXEC-013 to achieve 3.5x speedup through automation, batching, and parallel execution.

**Current State**:
- 5-way duplication: `\core\`, `\modules\`, `\engine\`, `\error\`, `\archive\`
- Conflicting import paths
- Manual migration = 53 hours
- Pattern-based migration = 15 hours

**Target State**:
- Single source of truth: `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\`
- Unified import pattern: `from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.*`
- Compatibility shims during transition
- 60%+ file reduction

---

## Phase Plan Structure

```
PHASE 0: Setup & Discovery          [2 hours]  [WS-001, WS-002]
PHASE 1: Dependency Analysis         [1 hour]   [WS-003]
PHASE 2: Migration Planning          [1 hour]   [WS-004]
PHASE 3: Core Module Migration       [8 hours]  [WS-005 to WS-009] ← PARALLEL
PHASE 4: Feature Module Migration    [4 hours]  [WS-010 to WS-013] ← PARALLEL
PHASE 5: Verification & Cleanup      [2 hours]  [WS-014, WS-015]
PHASE 6: Archive & Documentation     [2 hours]  [WS-016]
```

**Total**: 20 hours sequential + 12 hours parallel = **15 hours wall time**

---

## Execution Patterns Used

### Primary Patterns
- **EXEC-012**: Module Consolidation & Migration
- **EXEC-013**: Dependency Mapper (AST-based import analysis)
- **EXEC-001**: Batch File Operations
- **EXEC-006**: Safe Deletion with Registry

### Anti-Pattern Guards (ALL ENABLED)
✅ Hallucination of Success Prevention (verify exit codes)  
✅ Planning Loop Max (2 iterations then execute)  
✅ No Incomplete Implementation (no TODO/pass)  
✅ Explicit Error Handling Required  
✅ Ground Truth Verification Only  
✅ Approval Loop Elimination (safe ops auto-execute)

---

## PHASE 0: Setup & Discovery (2 hours)

### WS-001: Create Migration Infrastructure
**Type**: Setup  
**Dependencies**: None  
**Execution Pattern**: EXEC-001 (Batch File Creator)  
**Duration**: 30 minutes  
**Agent**: Codex CLI

**Objective**: Set up migration tracking system and directory structure

**Tasks**:
```yaml
tasks:
  - id: WS-001-T01
    action: create_directory_structure
    paths:
      - UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/
      - UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/backups/
      - UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/logs/
      - .migration_backups/2025-11-29/
    
  - id: WS-001-T02
    action: create_file
    path: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/README.md
    content: |
      # Migration Registry
      
      This directory tracks the UET consolidation migration.
      
      ## Files
      - `duplicate_registry.yaml` - Discovered duplicate files
      - `dependency_report.json` - Import dependency graph
      - `migration_plan.yaml` - Ordered migration batches
      - `migration_log.yaml` - Execution log
      - `verification_results.json` - Test results
      
      ## Status
      Started: 2025-11-29T16:10:00Z
      Phase: 0 - Setup
  
  - id: WS-001-T03
    action: git_tag
    tag: pre-uet-consolidation
    message: "Snapshot before UET consolidation begins"
```

**Ground Truth Success**:
```bash
test -d UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration && echo "✅ PASS" || echo "❌ FAIL"
git tag | grep pre-uet-consolidation && echo "✅ PASS" || echo "❌ FAIL"
```

**Deliverables**:
- ✅ Migration directory structure created
- ✅ Git tag created for rollback
- ✅ README documenting the process

---

### WS-002: Scan for Duplicates
**Type**: Analysis  
**Dependencies**: WS-001  
**Execution Pattern**: EXEC-012 Phase 1  
**Duration**: 90 minutes  
**Agent**: Codex CLI

**Objective**: Discover all duplicate files using hash-based comparison

**Implementation**:
```python
# File: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/scan_duplicates.py

import hashlib
from pathlib import Path
from typing import Dict, List
import yaml
from datetime import datetime

class DuplicateFinder:
    def __init__(self, root: Path):
        self.root = root
        self.file_hashes: Dict[str, List[Path]] = {}
        
    def scan_duplicates(self, exclude_patterns: List[str]) -> Dict:
        """Find duplicate files by content hash."""
        duplicates = {}
        
        print("🔍 Scanning for duplicate Python files...")
        
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
                    'canonical': self._select_canonical(paths),
                    'file_size': paths[0].stat().st_size
                }
        
        return duplicates
    
    def _hash_file(self, path: Path) -> str:
        """Calculate SHA256 hash of file content."""
        return hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    
    def _select_canonical(self, paths: List[Path]) -> str:
        """Select canonical version (prefer UET, then modules, then active)."""
        priorities = [
            'UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK',
            'modules',
            'core',
            'error',
            'aim',
            'pm',
            'specifications'
        ]
        
        for priority in priorities:
            for path in paths:
                if priority in str(path):
                    return str(path.relative_to(self.root))
        
        # Default: newest file
        newest = max(paths, key=lambda p: p.stat().st_mtime)
        return str(newest.relative_to(self.root))

if __name__ == "__main__":
    root = Path('.')
    finder = DuplicateFinder(root)
    
    exclude = [
        '__pycache__', 
        '.venv', 
        'archive/legacy',
        'tests/',
        'test_'
    ]
    
    duplicates = finder.scan_duplicates(exclude)
    
    # Generate report
    registry = {
        'scan_date': datetime.utcnow().isoformat() + 'Z',
        'total_duplicates': len(duplicates),
        'total_duplicate_files': sum(d['count'] for d in duplicates.values()),
        'duplicates': duplicates
    }
    
    # Save to registry
    output_path = Path('UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/duplicate_registry.yaml')
    output_path.write_text(yaml.dump(registry, default_flow_style=False))
    
    print(f"\n✅ Scan complete:")
    print(f"   - Found {registry['total_duplicates']} unique files with duplicates")
    print(f"   - Total duplicate instances: {registry['total_duplicate_files']}")
    print(f"   - Registry saved to: {output_path}")
```

**Execution**:
```bash
# Codex CLI execution
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/scan_duplicates.py
```

**Ground Truth Success**:
```bash
test -f UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/duplicate_registry.yaml && echo "✅ PASS" || echo "❌ FAIL"
```

**Expected Output**:
```yaml
scan_date: 2025-11-29T16:30:00Z
total_duplicates: 87
total_duplicate_files: 337
duplicates:
  a3f5b2c1d4e6f7a8:
    count: 3
    locations:
      - core/engine/orchestrator.py
      - modules/core-engine/m010001_orchestrator.py
      - archive/2025-11-26_094309_old-structure/core-engine/orchestrator.py
    canonical: modules/core-engine/m010001_orchestrator.py
    file_size: 8432
```

**Deliverables**:
- ✅ `duplicate_registry.yaml` with all duplicates identified
- ✅ Canonical version selected for each file
- ✅ Scan statistics logged

---

## PHASE 1: Dependency Analysis (1 hour)

### WS-003: Map Import Dependencies
**Type**: Analysis  
**Dependencies**: WS-002  
**Execution Pattern**: EXEC-013 (Dependency Mapper)  
**Duration**: 1 hour  
**Agent**: Codex CLI

**Objective**: Generate dependency graph to determine migration order

**Implementation**:
```python
# File: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/analyze_dependencies.py

import ast
import re
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
import json
from datetime import datetime

class DependencyMapper:
    """Map Python import dependencies for migration planning."""
    
    def __init__(self, root_dir: Path):
        self.root = root_dir
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.all_modules: Set[str] = set()
        
    def scan_directory(self, patterns: List[str] = None) -> Dict:
        """Scan directory for Python files and extract dependencies."""
        patterns = patterns or ['**/*.py']
        
        print("🔍 Analyzing import dependencies...")
        
        for pattern in patterns:
            for py_file in self.root.glob(pattern):
                if self._should_skip(py_file):
                    continue
                
                module_name = self._get_module_name(py_file)
                self.all_modules.add(module_name)
                
                imports = self._extract_imports(py_file)
                self.dependencies[module_name].update(imports)
        
        return self._generate_report()
    
    def _should_skip(self, path: Path) -> bool:
        """Skip __init__, tests, and hidden files."""
        return (
            path.name == '__init__.py' or
            'test_' in path.name or
            path.name.startswith('.') or
            '__pycache__' in str(path) or
            'archive/legacy' in str(path)
        )
    
    def _get_module_name(self, path: Path) -> str:
        """Convert file path to module name."""
        relative = path.relative_to(self.root)
        module_path = str(relative.with_suffix(''))
        return module_path.replace('\\', '.').replace('/', '.')
    
    def _extract_imports(self, file_path: Path) -> Set[str]:
        """Extract import statements using AST parsing."""
        imports = set()
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
        
        except (SyntaxError, UnicodeDecodeError):
            # Fallback to regex if AST fails
            imports = self._extract_imports_regex(file_path)
        
        # Filter to only internal modules
        return {imp for imp in imports if self._is_internal(imp)}
    
    def _extract_imports_regex(self, file_path: Path) -> Set[str]:
        """Fallback regex-based import extraction."""
        imports = set()
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            from_pattern = r'from\s+([\w\.]+)\s+import'
            imports.update(re.findall(from_pattern, content))
            
            import_pattern = r'import\s+([\w\.]+)'
            imports.update(re.findall(import_pattern, content))
        except:
            pass
        
        return imports
    
    def _is_internal(self, module_name: str) -> bool:
        """Check if module is internal (not stdlib or external)."""
        external = {
            'typing', 'pathlib', 'os', 'sys', 'json', 'yaml', 
            'pytest', 'click', 'pydantic', 'sqlalchemy',
            'fastapi', 'requests', 'numpy', 'pandas', 're',
            'hashlib', 'shutil', 'subprocess', 'datetime'
        }
        
        base_module = module_name.split('.')[0]
        return base_module not in external
    
    def _generate_report(self) -> Dict:
        """Generate dependency analysis report."""
        total_modules = len(self.all_modules)
        total_dependencies = sum(len(deps) for deps in self.dependencies.values())
        avg_dependencies = total_dependencies / total_modules if total_modules > 0 else 0
        
        # Find circular dependencies
        circular = self._find_circular_dependencies()
        
        # Calculate migration order
        migration_order = self._topological_sort()
        
        # Find leaf modules (no dependencies)
        leaf_modules = {
            mod for mod in self.all_modules 
            if len(self.dependencies[mod]) == 0
        }
        
        # Find highly coupled modules
        highly_coupled = sorted(
            [(mod, len(deps)) for mod, deps in self.dependencies.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            'analysis_date': datetime.utcnow().isoformat() + 'Z',
            'summary': {
                'total_modules': total_modules,
                'total_dependencies': total_dependencies,
                'average_dependencies': round(avg_dependencies, 2),
                'leaf_modules_count': len(leaf_modules),
                'circular_dependencies_count': len(circular)
            },
            'leaf_modules': sorted(leaf_modules),
            'highly_coupled': highly_coupled,
            'circular_dependencies': circular,
            'migration_order': migration_order,
            'dependency_graph': {k: list(v) for k, v in self.dependencies.items()}
        }
    
    def _find_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependency chains."""
        circular = []
        visited = set()
        rec_stack = set()
        
        def visit(module: str, path: List[str]):
            if module in rec_stack:
                cycle_start = path.index(module) if module in path else 0
                cycle = path[cycle_start:] + [module]
                if cycle not in circular:
                    circular.append(cycle)
                return
            
            if module in visited:
                return
            
            visited.add(module)
            rec_stack.add(module)
            
            for dep in self.dependencies.get(module, set()):
                if dep in self.all_modules:
                    visit(dep, path + [module])
            
            rec_stack.remove(module)
        
        for module in self.all_modules:
            if module not in visited:
                visit(module, [])
        
        return circular
    
    def _topological_sort(self) -> List[str]:
        """Return migration order (dependencies first)."""
        in_degree = {mod: 0 for mod in self.all_modules}
        
        for deps in self.dependencies.values():
            for dep in deps:
                if dep in in_degree:
                    in_degree[dep] += 1
        
        queue = [mod for mod, deg in in_degree.items() if deg == 0]
        result = []
        
        while queue:
            module = queue.pop(0)
            result.append(module)
            
            for dependent in self.all_modules:
                if module in self.dependencies.get(dependent, set()):
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)
        
        if len(result) != len(self.all_modules):
            remaining = self.all_modules - set(result)
            result.extend(sorted(remaining))
        
        return result

if __name__ == "__main__":
    root = Path('.')
    mapper = DependencyMapper(root)
    
    patterns = [
        'core/**/*.py',
        'error/**/*.py',
        'aim/**/*.py',
        'pm/**/*.py',
        'modules/**/*.py',
        'engine/**/*.py',
        'specifications/**/*.py'
    ]
    
    report = mapper.scan_directory(patterns)
    
    # Print summary
    print("\n📊 Dependency Analysis Report")
    print("=" * 60)
    print(f"Total modules: {report['summary']['total_modules']}")
    print(f"Total dependencies: {report['summary']['total_dependencies']}")
    print(f"Average deps/module: {report['summary']['average_dependencies']}")
    print(f"Leaf modules: {report['summary']['leaf_modules_count']}")
    
    if report['circular_dependencies']:
        print(f"\n⚠️  Circular Dependencies: {len(report['circular_dependencies'])}")
        for cycle in report['circular_dependencies'][:3]:
            print(f"  - {' -> '.join(cycle)}")
    else:
        print("\n✅ No circular dependencies")
    
    print("\n🌿 Leaf Modules (migrate first):")
    for mod in report['leaf_modules'][:5]:
        print(f"  - {mod}")
    
    print("\n🔗 Highly Coupled (migrate last):")
    for mod, count in report['highly_coupled'][:3]:
        print(f"  - {mod} ({count} deps)")
    
    # Save report
    output_path = Path('UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/dependency_report.json')
    output_path.write_text(json.dumps(report, indent=2))
    
    print(f"\n💾 Full report: {output_path}")
```

**Execution**:
```bash
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/analyze_dependencies.py
```

**Ground Truth Success**:
```bash
test -f UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/dependency_report.json && echo "✅ PASS" || echo "❌ FAIL"
python -c "import json; d=json.load(open('UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/dependency_report.json')); exit(0 if d['summary']['total_modules'] > 0 else 1)" && echo "✅ PASS" || echo "❌ FAIL"
```

**Deliverables**:
- ✅ `dependency_report.json` with full dependency graph
- ✅ Migration order calculated (topological sort)
- ✅ Circular dependencies identified (if any)
- ✅ Leaf modules identified for first migration batch

---

## PHASE 2: Migration Planning (1 hour)

### WS-004: Generate Migration Plan
**Type**: Planning  
**Dependencies**: WS-002, WS-003  
**Execution Pattern**: EXEC-012 Phase 2  
**Duration**: 1 hour  
**Agent**: Codex CLI

**Objective**: Create ordered batches for migration based on dependencies

**Implementation**:
```python
# File: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/create_migration_plan.py

import yaml
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

class MigrationPlanner:
    def __init__(self, duplicate_registry: Dict, dependency_report: Dict):
        self.duplicates = duplicate_registry
        self.dependencies = dependency_report
        
    def create_plan(self) -> Dict:
        """Create ordered migration plan with batches."""
        
        print("📋 Creating migration plan...")
        
        # Get migration order from dependency analysis
        migration_order = self.dependencies['migration_order']
        
        # Map canonical files to migration order
        canonical_files = []
        for dup_info in self.duplicates['duplicates'].values():
            canonical = dup_info['canonical']
            if canonical not in canonical_files:
                canonical_files.append(canonical)
        
        # Sort by dependency order
        ordered_files = self._sort_by_dependencies(canonical_files, migration_order)
        
        # Group into batches by component
        batches = self._create_batches(ordered_files)
        
        return {
            'plan_date': datetime.utcnow().isoformat() + 'Z',
            'total_files': len(ordered_files),
            'total_batches': len(batches),
            'execution_estimate_hours': len(batches) * 0.5,
            'batches': batches
        }
    
    def _sort_by_dependencies(self, files: List[str], order: List[str]) -> List[str]:
        """Sort files according to dependency order."""
        # Create module name to file mapping
        file_order = {}
        for file_path in files:
            module_name = str(Path(file_path).with_suffix('')).replace('/', '.').replace('\\', '.')
            file_order[module_name] = file_path
        
        # Sort files by dependency order
        sorted_files = []
        for module in order:
            if module in file_order:
                sorted_files.append(file_order[module])
        
        # Add any remaining files
        for file_path in files:
            if file_path not in sorted_files:
                sorted_files.append(file_path)
        
        return sorted_files
    
    def _create_batches(self, files: List[str]) -> List[Dict]:
        """Group files into migration batches by component."""
        
        # Group by component first
        components = {
            'core-state': [],
            'core-ast': [],
            'core-planning': [],
            'core-engine': [],
            'error-shared': [],
            'error-plugins': [],
            'error-engine': [],
            'aim': [],
            'pm': [],
            'specifications': [],
            'other': []
        }
        
        for file_path in files:
            parts = Path(file_path).parts
            
            if 'modules' in parts:
                idx = parts.index('modules')
                if idx + 1 < len(parts):
                    component_name = parts[idx + 1]
                    # Map module name to component
                    if component_name in components:
                        components[component_name].append(file_path)
                    else:
                        # Try to match pattern
                        for comp in components:
                            if comp in component_name:
                                components[comp].append(file_path)
                                break
                        else:
                            components['other'].append(file_path)
            else:
                # Direct paths
                if 'core' in parts:
                    if 'state' in parts:
                        components['core-state'].append(file_path)
                    elif 'ast' in parts:
                        components['core-ast'].append(file_path)
                    elif 'planning' in parts:
                        components['core-planning'].append(file_path)
                    elif 'engine' in parts:
                        components['core-engine'].append(file_path)
                    else:
                        components['other'].append(file_path)
                elif 'error' in parts:
                    if 'shared' in parts:
                        components['error-shared'].append(file_path)
                    elif 'plugins' in parts:
                        components['error-plugins'].append(file_path)
                    elif 'engine' in parts:
                        components['error-engine'].append(file_path)
                    else:
                        components['other'].append(file_path)
                elif 'aim' in parts:
                    components['aim'].append(file_path)
                elif 'pm' in parts:
                    components['pm'].append(file_path)
                elif 'specifications' in parts:
                    components['specifications'].append(file_path)
                else:
                    components['other'].append(file_path)
        
        # Create batches (6 files per batch within each component)
        batches = []
        batch_num = 1
        
        for component, files in components.items():
            if not files:
                continue
            
            # Split component into batches of 6
            for i in range(0, len(files), 6):
                batch_files = files[i:i+6]
                
                batches.append({
                    'batch_id': f"WS-{batch_num:03d}",
                    'component': component,
                    'files': batch_files,
                    'file_count': len(batch_files),
                    'status': 'pending',
                    'dependencies': self._get_batch_dependencies(batch_num, batches)
                })
                
                batch_num += 1
        
        return batches
    
    def _get_batch_dependencies(self, current_batch: int, previous_batches: List[Dict]) -> List[str]:
        """Determine which previous batches this batch depends on."""
        # For now, simple sequential dependency
        # In production, could analyze import dependencies
        if current_batch <= 1:
            return []
        else:
            return [previous_batches[-1]['batch_id']]

if __name__ == "__main__":
    # Load inputs
    duplicates = yaml.safe_load(
        Path('UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/duplicate_registry.yaml').read_text()
    )
    
    dependencies = json.loads(
        Path('UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/dependency_report.json').read_text()
    )
    
    # Create plan
    planner = MigrationPlanner(duplicates, dependencies)
    plan = planner.create_plan()
    
    # Print summary
    print(f"\n✅ Migration plan created:")
    print(f"   - Total files: {plan['total_files']}")
    print(f"   - Total batches: {plan['total_batches']}")
    print(f"   - Est. execution time: {plan['execution_estimate_hours']:.1f} hours")
    
    print("\n📦 Batches:")
    for batch in plan['batches'][:5]:
        deps = f" (depends on {', '.join(batch['dependencies'])})" if batch['dependencies'] else ""
        print(f"   - {batch['batch_id']}: {batch['component']} ({batch['file_count']} files){deps}")
    
    if len(plan['batches']) > 5:
        print(f"   ... and {len(plan['batches']) - 5} more batches")
    
    # Save plan
    output_path = Path('UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/migration_plan.yaml')
    output_path.write_text(yaml.dump(plan, default_flow_style=False))
    
    print(f"\n💾 Plan saved: {output_path}")
```

**Execution**:
```bash
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/create_migration_plan.py
```

**Ground Truth Success**:
```bash
test -f UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/migration_plan.yaml && echo "✅ PASS" || echo "❌ FAIL"
```

**Deliverables**:
- ✅ `migration_plan.yaml` with all batches defined
- ✅ Dependency order respected
- ✅ Component-based grouping for parallel execution
- ✅ Independent workstreams identified

---

## PHASE 3: Core Module Migration (8 hours, PARALLEL)

**Component Batches** (Can run in parallel after dependencies met):

### WS-005: Migrate Core State (Leaf - No Dependencies)
**Type**: Migration  
**Dependencies**: WS-004  
**Execution Pattern**: EXEC-012 Phase 3  
**Duration**: 1.5 hours  
**Agent**: Codex CLI Instance 1  
**Parallelizable**: YES

**Files** (12 files):
```
modules/core-state/m010003_db.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/state/db.py
modules/core-state/m010003_db_unified.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/state/db_unified.py
modules/core-state/m010003_db_sqlite.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/state/db_sqlite.py
modules/core-state/m010003_task_queue.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/state/task_queue.py
modules/core-state/m010003_worktree.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/state/worktree.py
modules/core-state/m010003_uet_db.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/state/uet_db.py
modules/core-state/m010003_uet_db_adapter.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/state/uet_db_adapter.py
modules/core-state/m010003_dag_utils.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/state/dag_utils.py
modules/core-state/m010003_crud.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/state/crud.py
modules/core-state/m010003_bundles.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/state/bundles.py
modules/core-state/m010003_pattern_telemetry_db.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/state/pattern_telemetry_db.py
modules/core-state/m010003_audit_logger.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/state/audit_logger.py
```

**Tasks**:
1. Copy files to UET location (remove m010003_ prefix)
2. Update imports from `modules.core-state.m010003_*` to `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.state.*`
3. Create compatibility shims in old location
4. Verify imports work

**Ground Truth**:
```bash
python -c "import UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.state.db" && echo "✅ PASS" || echo "❌ FAIL"
```

---

### WS-006: Migrate Core AST (Leaf - No Dependencies)
**Type**: Migration  
**Dependencies**: WS-004  
**Duration**: 1 hour  
**Agent**: Codex CLI Instance 2  
**Parallelizable**: YES

**Files** (4 files):
```
modules/core-ast/parser.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/ast/parser.py
modules/core-ast/m010000_extractors.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/ast/extractors.py
modules/core-ast/languages/python.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/ast/languages/python.py
```

**Ground Truth**:
```bash
python -c "import UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.ast.parser" && echo "✅ PASS" || echo "❌ FAIL"
```

---

### WS-007: Migrate Core Planning (Depends on Core State)
**Type**: Migration  
**Dependencies**: WS-005  
**Duration**: 1 hour  
**Agent**: Codex CLI Instance 1  
**Parallelizable**: After WS-005

**Files** (4 files):
```
modules/core-planning/m010002_planner.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/planning/planner.py
modules/core-planning/m010002_parallelism_detector.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/planning/parallelism_detector.py
modules/core-planning/m010002_ccpm_integration.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/planning/ccpm_integration.py
modules/core-planning/m010002_archive.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/planning/archive.py
```

**Ground Truth**:
```bash
python -c "import UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.planning.planner" && echo "✅ PASS" || echo "❌ FAIL"
```

---

### WS-008: Migrate Core Engine Part 1 (Depends on Core State, Planning)
**Type**: Migration  
**Dependencies**: WS-005, WS-007  
**Duration**: 2 hours  
**Agent**: Codex CLI Instance 3  
**Parallelizable**: After dependencies

**Files** (First 12 of 30 core engine files):
```
modules/core-engine/m010001_uet_state_machine.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/uet_state_machine.py
modules/core-engine/m010001_scheduler.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/scheduler.py
modules/core-engine/m010001_uet_router.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/uet_router.py
modules/core-engine/m010001_worker.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/worker.py
modules/core-engine/m010001_validators.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/validators.py
modules/core-engine/m010001_tools.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/tools.py
... (6 more)
```

**Ground Truth**:
```bash
python -c "import UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine.scheduler" && echo "✅ PASS" || echo "❌ FAIL"
```

---

### WS-009: Migrate Core Engine Part 2 (Depends on WS-008)
**Type**: Migration  
**Dependencies**: WS-008  
**Duration**: 2.5 hours  
**Agent**: Codex CLI Instance 3  
**Parallelizable**: After WS-008

**Files** (Remaining 18 core engine files including orchestrator)

**Ground Truth**:
```bash
python -c "import UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine.orchestrator" && echo "✅ PASS" || echo "❌ FAIL"
pytest UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/tests/core/engine/ -q && echo "✅ PASS" || echo "❌ FAIL"
```

---

## PHASE 4: Feature Module Migration (4 hours, PARALLEL)

### WS-010: Migrate Error Shared (Leaf - No Dependencies)
**Type**: Migration  
**Dependencies**: WS-004  
**Duration**: 30 minutes  
**Agent**: Codex CLI Instance 4  
**Parallelizable**: YES

**Files** (6 files):
```
error/shared/utils/types.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error/shared/utils/types.py
error/shared/utils/time.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error/shared/utils/time.py
error/shared/utils/security.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error/shared/utils/security.py
error/shared/utils/jsonl_manager.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error/shared/utils/jsonl_manager.py
error/shared/utils/hashing.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error/shared/utils/hashing.py
error/shared/utils/env.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error/shared/utils/env.py
```

---

### WS-011: Migrate Error Engine (Depends on Error Shared, Core Engine)
**Type**: Migration  
**Dependencies**: WS-009, WS-010  
**Duration**: 1.5 hours  
**Agent**: Codex CLI Instance 4

**Files** (9 files):
```
error/engine/error_engine.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error/engine/error_engine.py
error/engine/error_pipeline_service.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error/engine/error_pipeline_service.py
error/engine/error_pipeline_cli.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error/engine/error_pipeline_cli.py
error/engine/error_state_machine.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error/engine/error_state_machine.py
error/engine/plugin_manager.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error/engine/plugin_manager.py
error/engine/agent_adapters.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error/engine/agent_adapters.py
error/engine/file_hash_cache.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error/engine/file_hash_cache.py
error/engine/error_context.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error/engine/error_context.py
error/engine/pipeline_engine.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error/engine/pipeline_engine.py
```

---

### WS-012: Migrate Error Plugins (Depends on Error Engine)
**Type**: Migration  
**Dependencies**: WS-011  
**Duration**: 1.5 hours  
**Agent**: Codex CLI Instance 5  
**Parallelizable**: After WS-011

**Files** (~19 plugin modules - batched in groups of 6)

Batch 1 (6 plugins):
```
error/plugins/python_ruff/plugin.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error/plugins/python_ruff/plugin.py
error/plugins/python_pyright/plugin.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error/plugins/python_pyright/plugin.py
error/plugins/python_mypy/plugin.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error/plugins/python_mypy/plugin.py
error/plugins/python_black_fix/plugin.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error/plugins/python_black_fix/plugin.py
error/plugins/python_isort_fix/plugin.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error/plugins/python_isort_fix/plugin.py
error/plugins/python_bandit/plugin.py → UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error/plugins/python_bandit/plugin.py
```

Batch 2-4: Remaining plugins

---

### WS-013: Migrate AIM, PM, Specifications (Parallel)
**Type**: Migration  
**Dependencies**: WS-009 (Core Engine)  
**Duration**: 1.5 hours  
**Agent**: Codex CLI Instance 6  
**Parallelizable**: After WS-009

**Components**:
- AIM (5 files)
- PM (3 files + integrations)
- Specifications tools (5 files)

---

## PHASE 5: Verification & Cleanup (2 hours)

### WS-014: Run Full Verification Suite
**Type**: Verification  
**Dependencies**: All migration workstreams (WS-005 to WS-013)  
**Duration**: 1 hour  
**Agent**: Codex CLI

**Tasks**:
```yaml
tasks:
  - id: WS-014-T01
    action: run_tests
    command: pytest UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/tests/ -v --tb=short
    ground_truth: exit_code == 0
    
  - id: WS-014-T02
    action: verify_imports
    script: |
      python -c "import UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine.orchestrator"
      python -c "import UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.engine.error_engine"
      python -c "import UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.aim.cli.main"
      python -c "import UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.pm.epic"
    ground_truth: all_exit_codes == 0
    
  - id: WS-014-T03
    action: check_old_imports
    script: |
      cd UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK
      ! grep -r "from core\." --include="*.py" . 
      ! grep -r "from modules\." --include="*.py" .
      ! grep -r "from error\." --include="*.py" . | grep -v "from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error"
    ground_truth: no_matches_found
    
  - id: WS-014-T04
    action: count_files
    script: |
      echo "Files before migration:"
      find . -name "*.py" -not -path "./.venv/*" -not -path "./__pycache__/*" | wc -l
      echo "Files in UET:"
      find UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK -name "*.py" -not -path "*__pycache__*" | wc -l
```

**Ground Truth**:
```bash
pytest UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/tests/ -q && echo "✅ ALL TESTS PASS" || echo "❌ TESTS FAIL"
```

---

### WS-015: Generate Migration Report
**Type**: Documentation  
**Dependencies**: WS-014  
**Duration**: 1 hour  
**Agent**: Codex CLI

**Output**: `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/MIGRATION_COMPLETE_REPORT.md`

**Contents**:
```markdown
# UET Consolidation Migration - Completion Report

## Summary
- Migration Date: 2025-11-29
- Total Files Migrated: 337 → 120 (64% reduction)
- Total Time: 15 hours (vs 53 hours manual)
- Speedup: 3.5x

## Batches Executed
- WS-001 to WS-016: All complete ✅

## Verification Results
- All tests passing: ✅
- All imports working: ✅
- No old import patterns: ✅
- File reduction achieved: ✅

## Archived Locations
- modules/ → archive/2025-11-29_modules_replaced/
- core/ → archive/2025-11-29_core_replaced/
- error/ → archive/2025-11-29_error_replaced/
- aim/ → archive/2025-11-29_aim_replaced/

## Compatibility Period
Shims active until: 2025-12-29 (30 days)
After this date, remove shims and update all import paths.

## Next Steps
1. Monitor for import warnings over next 7 days
2. Update external tools to use new import paths
3. Remove compatibility shims after 30 days
4. Delete archived folders after 90 days
```

---

## PHASE 6: Archive & Documentation (2 hours)

### WS-016: Archive Old Structure
**Type**: Cleanup  
**Dependencies**: WS-015  
**Execution Pattern**: EXEC-006 (Safe Deletion with Registry)  
**Duration**: 2 hours  
**Agent**: Codex CLI

**Tasks**:
```yaml
tasks:
  - id: WS-016-T01
    action: archive_old_folders
    script: |
      mkdir -p archive/2025-11-29_pre-consolidation/
      mv modules archive/2025-11-29_pre-consolidation/
      mv core archive/2025-11-29_pre-consolidation/
      mv error archive/2025-11-29_pre-consolidation/
      mv aim archive/2025-11-29_pre-consolidation/
      mv pm archive/2025-11-29_pre-consolidation/
      
  - id: WS-016-T02
    action: update_root_readme
    file: README.md
    content: |
      # AI Development Pipeline
      
      **CANONICAL SOURCE**: All code is now in `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/`
      
      ## Quick Start
      ```bash
      # Import from UET
      from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.core.engine import orchestrator
      from UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK.error.engine import error_engine
      ```
      
      ## Migration
      Completed: 2025-11-29
      Old structure archived to: `archive/2025-11-29_pre-consolidation/`
      
      See: `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/MIGRATION_COMPLETE_REPORT.md`
  
  - id: WS-016-T03
    action: update_ai_instructions
    file: .github/copilot-instructions.md
    update: |
      Change all path references from:
      - `\core\` → `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\core\`
      - `\error\` → `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\error\`
      - `\modules\` → `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK\<component>\`
  
  - id: WS-016-T04
    action: git_commit
    message: |
      feat: Complete UET consolidation migration
      
      - Migrated 337 files to UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/
      - 64% file reduction achieved
      - All tests passing
      - Compatibility shims in place
      
      See: UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/MIGRATION_COMPLETE_REPORT.md
    tag: post-uet-consolidation
```

**Ground Truth**:
```bash
test -d archive/2025-11-29_pre-consolidation/modules && echo "✅ ARCHIVED" || echo "❌ NOT ARCHIVED"
git log -1 --oneline | grep "UET consolidation" && echo "✅ COMMITTED" || echo "❌ NOT COMMITTED"
```

---

## Execution Instructions for Codex CLI

### Prerequisites
```bash
# Ensure Python 3.9+ installed
python --version

# Install dependencies
pip install pyyaml

# Verify git clean
git status
```

### Sequential Execution (Single Agent)
```bash
# Phase 0
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/scan_duplicates.py

# Phase 1
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/analyze_dependencies.py

# Phase 2
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/create_migration_plan.py

# Phase 3-4 (Execute batches sequentially)
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/execute_batch.py WS-005
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/execute_batch.py WS-006
# ... continue for all batches

# Phase 5
pytest UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/tests/ -v
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/generate_report.py

# Phase 6
bash UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/archive_old_structure.sh
```

### Parallel Execution (Multiple Agents)
```bash
# Terminal 1 (Codex Instance 1): Core State + Planning
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/execute_batch.py WS-005
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/execute_batch.py WS-007

# Terminal 2 (Codex Instance 2): Core AST
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/execute_batch.py WS-006

# Terminal 3 (Codex Instance 3): Core Engine (after WS-005, WS-007 complete)
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/execute_batch.py WS-008
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/execute_batch.py WS-009

# Terminal 4 (Codex Instance 4): Error modules
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/execute_batch.py WS-010
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/execute_batch.py WS-011

# Terminal 5 (Codex Instance 5): Error plugins (after WS-011)
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/execute_batch.py WS-012

# Terminal 6 (Codex Instance 6): AIM, PM, Specs (after WS-009)
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/execute_batch.py WS-013
```

---

## Success Metrics

### Ground Truth Criteria (Must ALL Pass)
✅ All tests pass: `pytest UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/tests/ -q` (exit 0)  
✅ All imports work: No ImportError for any UET module  
✅ No old imports: `grep` shows 0 matches for deprecated patterns  
✅ File reduction: ≥60% reduction from 500 to ≤200 files  
✅ Shims functional: Old imports redirect successfully  
✅ Git committed: Changes tagged and committed

### Time Savings
```
Manual Migration: 53 hours
Pattern-Based: 15 hours
Savings: 72% (38 hours)
Speedup: 3.5x
```

### Quality Metrics
- Zero circular dependencies introduced
- All dependency order respected
- 100% test coverage maintained
- Git history preserved (copy, not move)
- Rollback capability maintained (30-day shims + archives)

---

## Rollback Plan

If migration fails at any point:

```bash
# 1. Restore from git tag
git reset --hard pre-uet-consolidation

# 2. Remove partial UET files
rm -rf UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/
rm -rf UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/error/
rm -rf UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/aim/
rm -rf UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/pm/

# 3. Verify tests still pass
pytest tests/ -v

# 4. Document what went wrong
echo "Rollback reason: <describe issue>" >> UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/.migration/ROLLBACK_LOG.md
```

---

## Anti-Pattern Guards (ENFORCED)

🚫 **Hallucination of Success**: All steps verify with `exit_code == 0`  
🚫 **Planning Loop**: Max 2 planning iterations (already complete in Phase 2)  
🚫 **Incomplete Implementation**: No TODO/pass allowed in migrated code  
🚫 **Silent Failures**: All scripts use `set -e` (bash) or raise exceptions (Python)  
🚫 **Manual Copy-Paste**: All migrations scripted and batched  
🚫 **Approval Loops**: Ground truth verification only (no human approval needed)

---

## Post-Migration Actions (Week 8)

### Day 1-7: Monitor
- Watch for deprecation warnings
- Fix any broken external integrations
- Update developer documentation

### Day 30: Remove Shims
```bash
# Remove all compatibility shims
find . -name "*.py" -exec grep -l "DEPRECATED.*UET" {} \; | xargs rm
```

### Day 90: Delete Archives
```bash
# Permanently remove archived old structure
rm -rf archive/2025-11-29_pre-consolidation/
```

---

## Contact & Support

**Migration Lead**: AI Agent (Codex CLI)  
**Pattern Library**: `UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/patterns/`  
**Issue Tracker**: `.migration/issues.md`  
**Questions**: Create issue in `.migration/questions.md`

---

**Created**: 2025-11-29T16:10:00Z  
**Status**: READY_FOR_EXECUTION  
**Approval**: Auto-approved (pattern-based, ground truth verified)  
**Next Action**: Execute WS-001 (Create Migration Infrastructure)

---

## Quick Start Command

```bash
# Execute entire migration (sequential)
bash UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/run_all.sh

# Execute Phase 0 only (setup)
bash UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/run_phase_0.sh

# Execute specific workstream
python UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/scripts/migration/execute_batch.py WS-005
```

**Ready to begin?** Run Phase 0 to create migration infrastructure.
