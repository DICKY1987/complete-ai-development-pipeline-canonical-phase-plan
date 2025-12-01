# Phase 2: Production Hardening - Implementation Plan

**Date**: 2025-12-01  
**Status**: 🚀 STARTING  
**Estimated Time**: 2.5 hours

---

## Goals

1. **Edge case handling** - Robust file name sanitization, better exclusions
2. **Performance optimization** - Faster scans for large repositories
3. **Error resilience** - Better error messages and recovery
4. **Monitoring** - Coverage tracking and trend analysis
5. **Quality improvements** - Enhanced validation and conflict detection

---

## Prerequisites

✅ Phase 0 complete (100% doc_id coverage)  
✅ Phase 1.5 complete (92% module_id coverage)  
✅ Phase 1 complete (CI/CD integration)  
✅ Validation scripts working  
✅ Registry validated (1 known issue)

---

## Deliverables

### 1. Enhanced Validation & Error Handling

#### Fix Known Issues
- ✅ Missing 'status' field in DOC-SCRIPT-RECOVERY-019
- ✅ Improved name sanitization for special characters
- ✅ Better error messages with actionable suggestions

#### Robust Exclusions
- ✅ Exclude submodules (ccpm/)
- ✅ Exclude worktrees (.worktrees/)
- ✅ Exclude build artifacts properly

### 2. Performance Optimizations

#### Faster Scanning
- ✅ Cache file stat results
- ✅ Skip binary files early
- ✅ Parallel scanning for large repos (optional)

#### Efficient Validation
- ✅ Incremental validation (only changed files)
- ✅ Fast-path for already-validated docs

### 3. Monitoring & Tracking

#### Coverage Trends
- ✅ `doc_id_coverage_trend.py` - Track coverage over time
- ✅ `coverage_history.jsonl` - Historical snapshots
- ✅ Trend reports with charts

#### Quality Metrics
- ✅ Duplicate detection
- ✅ Orphaned doc detection
- ✅ Consistency checks

### 4. Improved Tooling

#### Enhanced CLI
- ✅ Better help messages
- ✅ Progress indicators
- ✅ Colored output for readability

#### Registry Tools
- ✅ Conflict detection
- ✅ Auto-fix common issues
- ✅ Bulk operations support

---

## Implementation Tasks

### Task 2.1: Fix Known Registry Issue (10 min)

**Issue**: DOC-SCRIPT-RECOVERY-019 missing 'status' field

**Fix**:
```bash
# Find and fix the entry in registry
python -c "
import yaml
from pathlib import Path

registry_path = Path('doc_id/specs/DOC_ID_REGISTRY.yaml')
with open(registry_path, 'r') as f:
    registry = yaml.safe_load(f)

# Find and fix the doc
for doc in registry['docs']:
    if doc['doc_id'] == 'DOC-SCRIPT-RECOVERY-019':
        doc['status'] = 'active'
        print(f'Fixed: {doc[\"doc_id\"]}')
        break

# Save
with open(registry_path, 'w') as f:
    yaml.dump(registry, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
"

# Verify
python scripts/validate_registry.py
```

### Task 2.2: Enhanced Name Sanitization (30 min)

**File**: `scripts/doc_id_assigner.py`

**Improvements**:
```python
def sanitize_name(name: str) -> str:
    """
    Robust name sanitization for doc_ids.
    
    Handles:
    - Leading/trailing special characters
    - Multiple consecutive dashes
    - Non-ASCII characters
    - Length limits
    """
    # Remove leading non-alphanumeric
    name = re.sub(r'^[^A-Za-z0-9]+', '', name)
    
    # Replace special chars and spaces with dashes
    name = re.sub(r'[^A-Za-z0-9-]+', '-', name)
    
    # Collapse multiple dashes
    name = re.sub(r'-+', '-', name)
    
    # Remove trailing dashes
    name = name.strip('-')
    
    # Handle empty result
    if not name:
        name = 'UNNAMED'
    
    # Limit length and uppercase
    return name[:40].upper()
```

### Task 2.3: Better Exclusion Patterns (20 min)

**File**: `scripts/doc_id_scanner.py` and `scripts/validate_doc_id_coverage.py`

**Enhanced exclusions**:
```python
EXCLUDED_DIRS = {
    # Version control
    '.git', '.hg', '.svn',
    
    # Python
    '__pycache__', '.pytest_cache', '.tox', '.eggs',
    'venv', '.venv', 'env', '.env',
    'dist', 'build', '*.egg-info',
    
    # Node
    'node_modules', '.npm',
    
    # IDE
    '.vscode', '.idea', '.vs',
    
    # Build artifacts
    'target', 'out', 'bin', 'obj',
    
    # Git worktrees
    '.worktrees',
    
    # Submodules
    'ccpm',  # Known submodule
    
    # Temporary
    'temp', 'tmp', '.temp', '.tmp',
}

# Add pattern-based exclusions
EXCLUDED_PATTERNS = [
    r'\.git/',
    r'__pycache__/',
    r'node_modules/',
    r'\.worktrees/',
    r'ccpm/',
]
```

### Task 2.4: Coverage Trend Tracking (45 min)

**Create**: `scripts/doc_id_coverage_trend.py`

```python
#!/usr/bin/env python3
"""
DOC_ID Coverage Trend Tracker

Tracks doc_id coverage over time for monitoring and reporting.

Usage:
    python scripts/doc_id_coverage_trend.py snapshot
    python scripts/doc_id_coverage_trend.py report
    python scripts/doc_id_coverage_trend.py chart
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict

REPO_ROOT = Path(__file__).parent.parent
HISTORY_FILE = REPO_ROOT / "doc_id" / "reports" / "coverage_history.jsonl"


def save_snapshot():
    """Save current coverage snapshot"""
    # Import from validate_doc_id_coverage
    from validate_doc_id_coverage import scan_repository
    
    results = scan_repository()
    
    snapshot = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'total_files': results['total_eligible'],
        'files_with_docid': results['with_doc_id'],
        'coverage_percent': results['coverage_percent'],
    }
    
    # Append to history
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, 'a') as f:
        json.dump(snapshot, f)
        f.write('\n')
    
    print(f"Snapshot saved: {snapshot['coverage_percent']}% coverage")
    return snapshot


def load_history() -> List[Dict]:
    """Load coverage history"""
    if not HISTORY_FILE.exists():
        return []
    
    history = []
    with open(HISTORY_FILE, 'r') as f:
        for line in f:
            if line.strip():
                history.append(json.loads(line))
    
    return history


def generate_report():
    """Generate trend report"""
    history = load_history()
    
    if not history:
        print("No history data available")
        return
    
    print("DOC_ID Coverage Trend Report")
    print("=" * 50)
    print(f"\nSnapshots: {len(history)}")
    print(f"First: {history[0]['timestamp'][:10]}")
    print(f"Latest: {history[-1]['timestamp'][:10]}")
    
    print(f"\nCurrent Coverage: {history[-1]['coverage_percent']}%")
    print(f"Files: {history[-1]['files_with_docid']}/{history[-1]['total_files']}")
    
    if len(history) > 1:
        first = history[0]
        last = history[-1]
        delta = last['coverage_percent'] - first['coverage_percent']
        print(f"\nChange: {delta:+.2f}%")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Track doc_id coverage trends')
    parser.add_argument('action', choices=['snapshot', 'report', 'chart'],
                        help='Action to perform')
    
    args = parser.parse_args()
    
    if args.action == 'snapshot':
        save_snapshot()
    elif args.action == 'report':
        generate_report()
    elif args.action == 'chart':
        print("Chart generation not yet implemented")


if __name__ == '__main__':
    main()
```

### Task 2.5: Enhanced Error Messages (30 min)

**Update validation scripts with better errors**:

```python
# In validate_registry.py - Enhanced error messages

ERROR_MESSAGES = {
    'missing_field': """
    Missing required field '{field}' in doc {doc_id}
    
    Fix: Add the missing field to the doc entry:
      {field}: {suggested_value}
    
    See: doc_id/specs/DOC_ID_FRAMEWORK.md#required-fields
    """,
    
    'duplicate_id': """
    Duplicate doc_id: {doc_id}
    
    This ID appears {count} times in the registry.
    
    Fix: Run the deduplication tool:
      python scripts/clean_registry_duplicates.py
    
    Or manually search and fix:
      grep -n "{doc_id}" doc_id/specs/DOC_ID_REGISTRY.yaml
    """,
    
    'invalid_module': """
    Invalid module_id: {module_id} in doc {doc_id}
    
    Valid modules: {valid_modules}
    
    Fix: Update the module_id to match taxonomy:
      module_id: {suggested_module}
    
    See: doc_id/specs/module_taxonomy.yaml
    """
}

def format_error(error_type: str, **kwargs) -> str:
    """Format error with helpful context"""
    template = ERROR_MESSAGES.get(error_type, "Error: {message}")
    return template.format(**kwargs).strip()
```

### Task 2.6: Conflict Detection (25 min)

**Add to**: `scripts/validate_registry.py`

```python
def detect_conflicts(self) -> List[Dict]:
    """
    Detect conflicts in registry:
    - Duplicate doc_ids
    - Same file with multiple doc_ids  
    - Orphaned entries (file doesn't exist)
    """
    conflicts = []
    
    # Track doc_id usage
    id_usage = defaultdict(list)
    
    # Track file paths
    path_usage = defaultdict(list)
    
    for doc in self.registry['docs']:
        doc_id = doc['doc_id']
        id_usage[doc_id].append(doc)
        
        # Check artifact paths
        for artifact in doc.get('artifacts', []):
            path = artifact.get('path')
            if path:
                path_usage[path].append(doc_id)
                
                # Check if file exists
                file_path = REPO_ROOT / path
                if not file_path.exists():
                    conflicts.append({
                        'type': 'orphaned_file',
                        'doc_id': doc_id,
                        'path': path,
                        'message': f"File not found: {path}"
                    })
    
    # Find duplicates
    for doc_id, docs in id_usage.items():
        if len(docs) > 1:
            conflicts.append({
                'type': 'duplicate_id',
                'doc_id': doc_id,
                'count': len(docs),
                'message': f"Duplicate doc_id: {doc_id} ({len(docs)} times)"
            })
    
    # Find files with multiple IDs
    for path, doc_ids in path_usage.items():
        if len(doc_ids) > 1:
            conflicts.append({
                'type': 'multiple_ids',
                'path': path,
                'doc_ids': doc_ids,
                'message': f"File has multiple doc_ids: {path}"
            })
    
    return conflicts
```

---

## Testing Plan

### Test 1: Fixed Registry Validation
```bash
python scripts/validate_registry.py
# Expected: PASS (0 errors)
```

### Test 2: Enhanced Exclusions
```bash
python scripts/validate_doc_id_coverage.py
# Expected: Coverage unchanged or improved (no ccpm/ files counted)
```

### Test 3: Coverage Tracking
```bash
python scripts/doc_id_coverage_trend.py snapshot
python scripts/doc_id_coverage_trend.py report
# Expected: Snapshot saved, report generated
```

### Test 4: Conflict Detection
```bash
python scripts/validate_registry.py
# Expected: Reports any conflicts found
```

---

## Success Criteria

- [ ] Registry validation passes (0 errors)
- [ ] Enhanced exclusions working
- [ ] Coverage trend tracking functional
- [ ] Better error messages implemented
- [ ] Conflict detection working
- [ ] All tests passing
- [ ] Documentation updated

---

## Timeline

```
Hour 1 (0:00-1:00):
  0:00-0:10  Fix registry issue
  0:10-0:40  Enhanced name sanitization
  0:40-1:00  Better exclusion patterns

Hour 2 (1:00-2:00):
  1:00-1:45  Coverage trend tracking
  1:45-2:00  Enhanced error messages

Hour 2.5 (2:00-2:30):
  2:00-2:25  Conflict detection
  2:25-2:30  Testing and documentation
```

---

## Next Phase

**Phase 3.5: Documentation Consolidation** (4 hours)
- Organize documentation by module
- Generate module-specific docs
- Create navigation structure

---

**Ready to begin Phase 2 Production Hardening!**
