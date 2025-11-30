---
doc_id: TBD
title: Complete Repository ID Coverage Plan
status: active
version: 1.0
created: 2025-11-30
---

# Complete Repository ID Coverage Plan

## Executive Summary

This plan extends the doc_id framework to **100% coverage** of all files in the repository with automated guards and enforcement.

**Current State**:
- 271 documents have doc_ids (Phase 3 complete)
- ~2,000+ files in repo need IDs
- Manual batch workflow proven (3 scripts, delta-based)

**Target State**:
- 100% coverage of all tracked files
- CI gates prevent commits without doc_ids
- Automated ID assignment on file creation
- Lifecycle management (split/merge/delete)

**Timeline**: 2 weeks (incremental rollout)

---

## Phase 1: Infrastructure & Automation (Days 1-3)

### 1.1 Enhanced Auto-Assigner

**Create**: `scripts/auto_assign_doc_ids.py`

```python
#!/usr/bin/env python3
"""
Auto-assign doc_ids to all files without them.

Usage:
    python auto_assign_doc_ids.py --scan          # Scan and report
    python auto_assign_doc_ids.py --assign        # Assign IDs
    python auto_assign_doc_ids.py --category core # Assign to specific category
"""

from pathlib import Path
import yaml
import json
from typing import List, Dict, Optional
import re

# File type categorization
FILE_CATEGORIES = {
    "core": ["core/**/*.py"],
    "error": ["error/**/*.py"],
    "aim": ["aim/**/*.py"],
    "pm": ["pm/**/*.py"],
    "spec": ["specifications/**/*.py", "openspec/**/*.yaml"],
    "test": ["tests/**/*.py"],
    "script": ["scripts/**/*.py", "scripts/**/*.ps1"],
    "config": ["config/**/*.yaml", "config/**/*.json"],
    "doc": ["docs/**/*.md", "adr/**/*.md"],
    "guide": ["**/*README*.md", "**/*GUIDE*.md"],
    "pattern": ["UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/**/*.md"],
}

EXCLUSIONS = [
    ".git/**",
    ".venv/**",
    ".worktrees/**",
    ".state/**",
    "__pycache__/**",
    "node_modules/**",
    "*.pyc",
    ".pytest_cache/**",
]


class AutoAssigner:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.registry_path = repo_root / "doc_id/specs/DOC_ID_REGISTRY.yaml"
        self.inventory_path = repo_root / "doc_id/reports/docs_inventory.jsonl"
        
    def scan_unassigned(self) -> Dict[str, List[Path]]:
        """Find all files without doc_ids, grouped by category."""
        unassigned = {cat: [] for cat in FILE_CATEGORIES}
        
        # Load existing IDs from registry
        assigned_paths = self._load_assigned_paths()
        
        # Scan each category
        for category, patterns in FILE_CATEGORIES.items():
            for pattern in patterns:
                for file in self.repo_root.glob(pattern):
                    if self._should_skip(file):
                        continue
                    
                    rel_path = file.relative_to(self.repo_root)
                    if str(rel_path) not in assigned_paths:
                        if not self._has_doc_id_in_file(file):
                            unassigned[category].append(file)
        
        return unassigned
    
    def _load_assigned_paths(self) -> set:
        """Load all paths that already have doc_ids."""
        registry = yaml.safe_load(self.registry_path.read_text(encoding='utf-8'))
        paths = set()
        
        for doc in registry.get('docs', []):
            for artifact in doc.get('artifacts', []):
                paths.add(artifact['path'])
        
        return paths
    
    def _should_skip(self, file: Path) -> bool:
        """Check if file should be excluded."""
        rel_path = str(file.relative_to(self.repo_root))
        
        for exclusion in EXCLUSIONS:
            if Path(rel_path).match(exclusion):
                return True
        
        return False
    
    def _has_doc_id_in_file(self, file: Path) -> bool:
        """Check if file already has doc_id in content."""
        if not file.is_file():
            return False
        
        try:
            content = file.read_text(encoding='utf-8', errors='ignore')
            
            # Check for doc_id in front matter or header
            if file.suffix in ['.md', '.markdown']:
                # YAML front matter
                if content.startswith('---'):
                    fm_end = content.find('---', 3)
                    if fm_end > 0:
                        fm = content[3:fm_end]
                        if 'doc_id:' in fm:
                            return True
            
            elif file.suffix in ['.py', '.ps1']:
                # Header comment
                lines = content.split('\n', 50)[:50]
                for line in lines:
                    if re.search(r'#\s*DOC_(?:ID|LINK):', line, re.IGNORECASE):
                        return True
            
        except Exception:
            pass
        
        return False
    
    def generate_batch_spec(self, category: str, files: List[Path]) -> dict:
        """Generate batch spec for auto-assignment."""
        items = []
        
        for file in files:
            logical_name = self._derive_logical_name(file)
            title = self._derive_title(file)
            
            items.append({
                'logical_name': logical_name,
                'title': title,
                'artifacts': [
                    {'path': str(file.relative_to(self.repo_root))}
                ]
            })
        
        return {
            'batch_id': f'DOCID-BATCH-AUTO-{category.upper()}-001',
            'description': f'Auto-assign doc_ids to {category} files',
            'category': category,
            'items': items,
            'tags': [f'type:auto', f'category:{category}']
        }
    
    def _derive_logical_name(self, file: Path) -> str:
        """Derive logical name from file path."""
        # Remove extension and convert to uppercase snake case
        name = file.stem.upper().replace('-', '_').replace(' ', '_')
        return name
    
    def _derive_title(self, file: Path) -> str:
        """Derive title from file path."""
        # Try to extract from first heading or docstring
        try:
            content = file.read_text(encoding='utf-8', errors='ignore')
            
            if file.suffix in ['.md', '.markdown']:
                # Find first # heading
                for line in content.split('\n', 20)[:20]:
                    if line.startswith('# '):
                        return line[2:].strip()
            
            elif file.suffix == '.py':
                # Find module docstring
                match = re.search(r'"""([^"]+)"""', content)
                if match:
                    return match.group(1).strip().split('\n')[0]
        
        except Exception:
            pass
        
        # Fallback: use filename
        return file.stem.replace('_', ' ').replace('-', ' ').title()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-assign doc_ids')
    parser.add_argument('--scan', action='store_true', help='Scan and report unassigned files')
    parser.add_argument('--assign', action='store_true', help='Generate batch specs for assignment')
    parser.add_argument('--category', help='Process specific category only')
    parser.add_argument('--limit', type=int, help='Limit files per category')
    
    args = parser.parse_args()
    
    repo_root = Path(__file__).parent.parent
    assigner = AutoAssigner(repo_root)
    
    if args.scan:
        unassigned = assigner.scan_unassigned()
        
        print("📊 Unassigned Files by Category\n")
        total = 0
        for category, files in unassigned.items():
            if args.category and category != args.category:
                continue
            
            count = len(files)
            total += count
            print(f"{category:12} {count:5} files")
            
            if count > 0 and count <= 10:
                for file in files[:10]:
                    print(f"  - {file.relative_to(repo_root)}")
        
        print(f"\nTotal: {total} files need doc_ids")
    
    elif args.assign:
        unassigned = assigner.scan_unassigned()
        
        for category, files in unassigned.items():
            if args.category and category != args.category:
                continue
            
            if not files:
                continue
            
            if args.limit:
                files = files[:args.limit]
            
            spec = assigner.generate_batch_spec(category, files)
            
            # Save batch spec
            batch_dir = repo_root / 'doc_id/batches'
            batch_dir.mkdir(parents=True, exist_ok=True)
            
            batch_file = batch_dir / f'batch_auto_{category}.yaml'
            batch_file.write_text(yaml.dump(spec, sort_keys=False), encoding='utf-8')
            
            print(f"✅ Generated {batch_file.name} ({len(files)} files)")


if __name__ == '__main__':
    main()
```

### 1.2 Pre-Commit Hook (Git Guard)

**Create**: `.githooks/pre-commit-doc-id`

```bash
#!/bin/bash
# Pre-commit hook to enforce doc_id presence

set -e

echo "🔍 Checking doc_id compliance..."

# Get list of staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

# Categories that REQUIRE doc_ids
REQUIRED_PATTERNS=(
    "*.py"
    "*.md"
    "*.ps1"
)

VIOLATIONS=()

for file in $STAGED_FILES; do
    # Skip excluded files
    if [[ "$file" =~ ^\.git/ ]] || \
       [[ "$file" =~ ^\.venv/ ]] || \
       [[ "$file" =~ ^__pycache__/ ]] || \
       [[ "$file" =~ ^node_modules/ ]]; then
        continue
    fi
    
    # Check if file requires doc_id
    REQUIRES_ID=false
    for pattern in "${REQUIRED_PATTERNS[@]}"; do
        if [[ "$file" == $pattern ]]; then
            REQUIRES_ID=true
            break
        fi
    done
    
    if [ "$REQUIRES_ID" = true ]; then
        # Check if doc_id present
        if ! grep -q -E "doc_id:|DOC_ID:|DOC_LINK:" "$file" 2>/dev/null; then
            VIOLATIONS+=("$file")
        fi
    fi
done

# Report violations
if [ ${#VIOLATIONS[@]} -gt 0 ]; then
    echo "❌ ERROR: The following files are missing doc_id:"
    printf '  - %s\n' "${VIOLATIONS[@]}"
    echo ""
    echo "To fix:"
    echo "  1. Run: python scripts/auto_assign_doc_ids.py --scan"
    echo "  2. Run: python scripts/auto_assign_doc_ids.py --assign"
    echo "  3. Run: python batch_mint.py && python merge_deltas.py && python write_doc_ids_to_files.py"
    echo ""
    echo "Or bypass this check (not recommended):"
    echo "  git commit --no-verify"
    exit 1
fi

echo "✅ All staged files have doc_ids"
exit 0
```

**Install**:
```bash
# Make executable
chmod +x .githooks/pre-commit-doc-id

# Configure git to use .githooks/
git config core.hooksPath .githooks
```

### 1.3 CI Gate (GitHub Actions)

**Create**: `.github/workflows/doc-id-gate.yml`

```yaml
name: Doc ID Gate

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  check-doc-ids:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install pyyaml
      
      - name: Scan for missing doc_ids
        run: |
          python scripts/auto_assign_doc_ids.py --scan > scan_results.txt
          cat scan_results.txt
          
          # Check if any violations found
          if grep -q "files need doc_ids" scan_results.txt; then
            MISSING=$(tail -1 scan_results.txt | grep -oE '[0-9]+')
            if [ "$MISSING" -gt 0 ]; then
              echo "❌ ERROR: $MISSING files missing doc_ids"
              exit 1
            fi
          fi
      
      - name: Validate registry consistency
        run: |
          python doc_id/tools/doc_id_registry_cli.py validate
      
      - name: Check for duplicate doc_ids
        run: |
          python -c "
          from pathlib import Path
          import yaml
          
          registry = yaml.safe_load(Path('doc_id/specs/DOC_ID_REGISTRY.yaml').read_text())
          doc_ids = [d['doc_id'] for d in registry['docs']]
          
          if len(doc_ids) != len(set(doc_ids)):
              print('❌ ERROR: Duplicate doc_ids found')
              exit(1)
          
          print('✅ No duplicate doc_ids')
          "
```

---

## Phase 2: Batch Assignment (Days 4-7)

### 2.1 Priority Order

Process files in order of importance:

```bash
# Day 4: Core Python modules
python auto_assign_doc_ids.py --assign --category core
python batch_mint.py && python merge_deltas.py && python write_doc_ids_to_files.py
git add -A && git commit -m "feat(doc_id): Assign IDs to core modules"

# Day 5: Error & AIM modules  
python auto_assign_doc_ids.py --assign --category error
python batch_mint.py && python merge_deltas.py && python write_doc_ids_to_files.py
git add -A && git commit -m "feat(doc_id): Assign IDs to error modules"

python auto_assign_doc_ids.py --assign --category aim
python batch_mint.py && python merge_deltas.py && python write_doc_ids_to_files.py
git add -A && git commit -m "feat(doc_id): Assign IDs to aim modules"

# Day 6: Tests & scripts
python auto_assign_doc_ids.py --assign --category test
python batch_mint.py && python merge_deltas.py && python write_doc_ids_to_files.py
git add -A && git commit -m "feat(doc_id): Assign IDs to tests"

python auto_assign_doc_ids.py --assign --category script
python batch_mint.py && python merge_deltas.py && python write_doc_ids_to_files.py
git add -A && git commit -m "feat(doc_id): Assign IDs to scripts"

# Day 7: Documentation
python auto_assign_doc_ids.py --assign --category doc
python batch_mint.py && python merge_deltas.py && python write_doc_ids_to_files.py
git add -A && git commit -m "feat(doc_id): Assign IDs to documentation"

python auto_assign_doc_ids.py --assign --category guide
python batch_mint.py && python merge_deltas.py && python write_doc_ids_to_files.py
git add -A && git commit -m "feat(doc_id): Assign IDs to guides"
```

### 2.2 Verification After Each Batch

```bash
# Check coverage
python scripts/auto_assign_doc_ids.py --scan

# Validate registry
python doc_id/tools/doc_id_registry_cli.py validate

# Generate report
python doc_id/tools/doc_id_scanner.py report
```

---

## Phase 3: Lifecycle Management (Days 8-10)

### 3.1 File Lifecycle Tracker

**Create**: `scripts/doc_id_lifecycle.py`

```python
#!/usr/bin/env python3
"""
Track doc_id lifecycle events: split, merge, move, delete.

Usage:
    python doc_id_lifecycle.py split OLD_FILE NEW_FILE1 NEW_FILE2
    python doc_id_lifecycle.py merge FILE1 FILE2 NEW_FILE
    python doc_id_lifecycle.py move OLD_PATH NEW_PATH
    python doc_id_lifecycle.py delete FILE
"""

from pathlib import Path
import yaml
import sys
from datetime import datetime


class LifecycleTracker:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.registry_path = repo_root / "doc_id/specs/DOC_ID_REGISTRY.yaml"
        self.lifecycle_log = repo_root / "doc_id/reports/lifecycle_events.jsonl"
    
    def handle_split(self, old_file: str, new_files: list):
        """Handle file split: primary keeps ID, derived get new IDs."""
        registry = self._load_registry()
        
        # Find original doc_id
        old_doc = self._find_doc_by_path(registry, old_file)
        if not old_doc:
            print(f"❌ ERROR: {old_file} has no doc_id")
            return
        
        original_id = old_doc['doc_id']
        
        # Primary file (first in list) keeps original ID
        primary = new_files[0]
        print(f"✅ {primary} keeps {original_id}")
        
        # Update path in registry
        for artifact in old_doc['artifacts']:
            if artifact['path'] == old_file:
                artifact['path'] = primary
        
        # Derived files get new IDs
        for derived in new_files[1:]:
            # Create new entry (user must mint via batch_mint.py)
            print(f"📝 {derived} needs new doc_id (derived_from: {original_id})")
        
        # Log event
        self._log_event({
            'event': 'split',
            'timestamp': datetime.utcnow().isoformat(),
            'original_file': old_file,
            'original_doc_id': original_id,
            'primary_file': primary,
            'derived_files': new_files[1:]
        })
        
        self._save_registry(registry)
    
    def handle_merge(self, old_files: list, new_file: str):
        """Handle file merge: merged file gets new ID, originals marked superseded."""
        registry = self._load_registry()
        
        # Find original doc_ids
        old_ids = []
        for old_file in old_files:
            doc = self._find_doc_by_path(registry, old_file)
            if doc:
                old_ids.append(doc['doc_id'])
                # Mark as superseded
                doc['status'] = 'superseded'
                doc['superseded_by'] = 'TBD'  # Will be filled when new ID assigned
        
        print(f"📝 {new_file} needs new doc_id")
        print(f"📋 Supersedes: {', '.join(old_ids)}")
        
        # Log event
        self._log_event({
            'event': 'merge',
            'timestamp': datetime.utcnow().isoformat(),
            'original_files': old_files,
            'original_doc_ids': old_ids,
            'merged_file': new_file
        })
        
        self._save_registry(registry)
    
    def handle_move(self, old_path: str, new_path: str):
        """Handle file move: doc_id unchanged, path updated."""
        registry = self._load_registry()
        
        doc = self._find_doc_by_path(registry, old_path)
        if not doc:
            print(f"❌ ERROR: {old_path} has no doc_id")
            return
        
        doc_id = doc['doc_id']
        
        # Update path, keep doc_id
        for artifact in doc['artifacts']:
            if artifact['path'] == old_path:
                artifact['path'] = new_path
        
        # Track previous path
        if 'previous_paths' not in doc:
            doc['previous_paths'] = []
        doc['previous_paths'].append({
            'path': old_path,
            'moved_at': datetime.utcnow().isoformat()
        })
        
        print(f"✅ {new_path} keeps {doc_id} (moved from {old_path})")
        
        # Log event
        self._log_event({
            'event': 'move',
            'timestamp': datetime.utcnow().isoformat(),
            'doc_id': doc_id,
            'old_path': old_path,
            'new_path': new_path
        })
        
        self._save_registry(registry)
    
    def handle_delete(self, file_path: str):
        """Handle file delete: mark doc_id as retired."""
        registry = self._load_registry()
        
        doc = self._find_doc_by_path(registry, file_path)
        if not doc:
            print(f"❌ ERROR: {file_path} has no doc_id")
            return
        
        doc_id = doc['doc_id']
        
        # Mark as retired
        doc['status'] = 'retired'
        doc['retired_at'] = datetime.utcnow().isoformat()
        
        print(f"✅ {doc_id} marked as retired (was: {file_path})")
        
        # Log event
        self._log_event({
            'event': 'delete',
            'timestamp': datetime.utcnow().isoformat(),
            'doc_id': doc_id,
            'file_path': file_path
        })
        
        self._save_registry(registry)
    
    def _load_registry(self) -> dict:
        return yaml.safe_load(self.registry_path.read_text(encoding='utf-8'))
    
    def _save_registry(self, registry: dict):
        self.registry_path.write_text(
            yaml.dump(registry, sort_keys=False, allow_unicode=True),
            encoding='utf-8'
        )
    
    def _find_doc_by_path(self, registry: dict, path: str) -> dict:
        for doc in registry['docs']:
            for artifact in doc.get('artifacts', []):
                if artifact['path'] == path:
                    return doc
        return None
    
    def _log_event(self, event: dict):
        import json
        self.lifecycle_log.parent.mkdir(parents=True, exist_ok=True)
        with self.lifecycle_log.open('a', encoding='utf-8') as f:
            f.write(json.dumps(event) + '\n')


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    repo_root = Path(__file__).parent.parent
    tracker = LifecycleTracker(repo_root)
    
    command = sys.argv[1]
    
    if command == 'split':
        if len(sys.argv) < 4:
            print("Usage: doc_id_lifecycle.py split OLD_FILE NEW_FILE1 NEW_FILE2 ...")
            sys.exit(1)
        tracker.handle_split(sys.argv[2], sys.argv[3:])
    
    elif command == 'merge':
        if len(sys.argv) < 4:
            print("Usage: doc_id_lifecycle.py merge FILE1 FILE2 ... NEW_FILE")
            sys.exit(1)
        tracker.handle_merge(sys.argv[2:-1], sys.argv[-1])
    
    elif command == 'move':
        if len(sys.argv) != 4:
            print("Usage: doc_id_lifecycle.py move OLD_PATH NEW_PATH")
            sys.exit(1)
        tracker.handle_move(sys.argv[2], sys.argv[3])
    
    elif command == 'delete':
        if len(sys.argv) != 3:
            print("Usage: doc_id_lifecycle.py delete FILE")
            sys.exit(1)
        tracker.handle_delete(sys.argv[2])
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
```

### 3.2 Conflict Resolver

**Create**: `scripts/doc_id_conflicts.py`

```python
#!/usr/bin/env python3
"""
Detect and resolve doc_id conflicts.

Usage:
    python doc_id_conflicts.py scan     # Find conflicts
    python doc_id_conflicts.py resolve  # Interactive resolution
"""

from pathlib import Path
import yaml
from collections import defaultdict


class ConflictResolver:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.registry_path = repo_root / "doc_id/specs/DOC_ID_REGISTRY.yaml"
    
    def scan_conflicts(self) -> dict:
        """Scan for doc_id conflicts."""
        registry = yaml.safe_load(self.registry_path.read_text(encoding='utf-8'))
        
        conflicts = {
            'duplicate_ids': defaultdict(list),
            'duplicate_paths': defaultdict(list),
            'missing_files': []
        }
        
        # Check for duplicate doc_ids
        for doc in registry['docs']:
            doc_id = doc['doc_id']
            conflicts['duplicate_ids'][doc_id].append(doc)
        
        # Check for duplicate paths
        for doc in registry['docs']:
            for artifact in doc.get('artifacts', []):
                path = artifact['path']
                conflicts['duplicate_paths'][path].append(doc)
        
        # Check for missing files
        for doc in registry['docs']:
            for artifact in doc.get('artifacts', []):
                path = self.repo_root / artifact['path']
                if not path.exists() and doc.get('status') != 'retired':
                    conflicts['missing_files'].append({
                        'doc_id': doc['doc_id'],
                        'path': artifact['path']
                    })
        
        # Filter to only actual conflicts
        conflicts['duplicate_ids'] = {
            k: v for k, v in conflicts['duplicate_ids'].items() if len(v) > 1
        }
        conflicts['duplicate_paths'] = {
            k: v for k, v in conflicts['duplicate_paths'].items() if len(v) > 1
        }
        
        return conflicts
    
    def report_conflicts(self):
        """Print conflict report."""
        conflicts = self.scan_conflicts()
        
        has_conflicts = False
        
        if conflicts['duplicate_ids']:
            has_conflicts = True
            print("❌ DUPLICATE DOC_IDS")
            for doc_id, docs in conflicts['duplicate_ids'].items():
                print(f"\n  {doc_id} appears in {len(docs)} entries:")
                for doc in docs:
                    paths = [a['path'] for a in doc.get('artifacts', [])]
                    print(f"    - {', '.join(paths)}")
        
        if conflicts['duplicate_paths']:
            has_conflicts = True
            print("\n❌ DUPLICATE PATHS")
            for path, docs in conflicts['duplicate_paths'].items():
                print(f"\n  {path} has {len(docs)} doc_ids:")
                for doc in docs:
                    print(f"    - {doc['doc_id']}")
        
        if conflicts['missing_files']:
            has_conflicts = True
            print("\n⚠️  MISSING FILES")
            for item in conflicts['missing_files'][:10]:
                print(f"  - {item['doc_id']}: {item['path']}")
            if len(conflicts['missing_files']) > 10:
                print(f"  ... and {len(conflicts['missing_files']) - 10} more")
        
        if not has_conflicts:
            print("✅ No conflicts found")


def main():
    import sys
    
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    repo_root = Path(__file__).parent.parent
    resolver = ConflictResolver(repo_root)
    
    if sys.argv[1] == 'scan':
        resolver.report_conflicts()
    else:
        print(f"Unknown command: {sys.argv[1]}")


if __name__ == '__main__':
    main()
```

---

## Phase 4: Enforcement & Monitoring (Days 11-14)

### 4.1 Enable CI Gate

```bash
# Commit the CI workflow
git add .github/workflows/doc-id-gate.yml
git commit -m "feat(ci): Add doc_id compliance gate"

# Configure as required status check in GitHub
# Settings > Branches > main > Require status checks
# Check: "Doc ID Gate / check-doc-ids"
```

### 4.2 Enable Pre-Commit Hook

```bash
# Install hook
git config core.hooksPath .githooks

# Test it
touch test_file.py
git add test_file.py
git commit -m "test"  # Should fail with doc_id error

# Clean up
git reset HEAD test_file.py
rm test_file.py
```

### 4.3 Monitoring Dashboard

**Create**: `doc_id/reports/COVERAGE_DASHBOARD.md`

```markdown
# Doc ID Coverage Dashboard

**Last Updated**: {timestamp}

## Overall Coverage

- **Total Files**: {total_files}
- **Files with doc_ids**: {files_with_ids}
- **Coverage**: {coverage_pct}%

## By Category

| Category | Total | With ID | Coverage |
|----------|-------|---------|----------|
| core     | 123   | 123     | 100%     |
| error    | 45    | 45      | 100%     |
| aim      | 34    | 34      | 100%     |
| tests    | 234   | 200     | 85%      |
| docs     | 156   | 156     | 100%     |

## Recent Activity

- 2025-11-30: Assigned IDs to 45 core modules
- 2025-11-29: Assigned IDs to 271 pattern docs
- 2025-11-28: Framework v1.0 complete

## Conflicts

- ✅ No duplicate doc_ids
- ✅ No duplicate paths  
- ⚠️  12 files missing (marked for deletion)
```

**Auto-generate**:
```bash
python scripts/generate_coverage_dashboard.py > doc_id/reports/COVERAGE_DASHBOARD.md
```

---

## Success Criteria

### Phase 1 Complete When:
- ✅ auto_assign_doc_ids.py working
- ✅ Pre-commit hook installed
- ✅ CI gate configured

### Phase 2 Complete When:
- ✅ 100% coverage of core/error/aim modules
- ✅ 100% coverage of tests
- ✅ 100% coverage of docs
- ✅ 90%+ coverage overall

### Phase 3 Complete When:
- ✅ Lifecycle tracker operational
- ✅ Conflict resolver operational
- ✅ Lifecycle events logged

### Phase 4 Complete When:
- ✅ CI gate enforced on main branch
- ✅ Pre-commit hook active
- ✅ Coverage dashboard updating daily
- ✅ Zero conflicts detected

---

## Rollback Plan

If issues arise:

```bash
# Disable pre-commit hook
git config --unset core.hooksPath

# Disable CI gate
git mv .github/workflows/doc-id-gate.yml .github/workflows/doc-id-gate.yml.disabled

# Revert batch assignments
git revert <commit-hash>
```

---

## Future Enhancements

1. **IDE Integration**: VSCode extension to show doc_ids in file tree
2. **Auto-sync on Save**: IDE plugin auto-assigns doc_id on file creation
3. **Doc ID Search**: CLI tool to find files by doc_id
4. **Batch Retirement**: Retire doc_ids for deleted files in bulk
5. **Analytics**: Track doc_id churn rate, most-moved files, etc.

---

## Timeline

```
Week 1:
  Day 1: Create auto_assign_doc_ids.py
  Day 2: Create pre-commit hook & CI gate
  Day 3: Test infrastructure
  Day 4: Batch assign core modules
  Day 5: Batch assign error/aim modules
  Day 6: Batch assign tests/scripts
  Day 7: Batch assign docs

Week 2:
  Day 8: Create lifecycle tracker
  Day 9: Create conflict resolver
  Day 10: Test lifecycle workflows
  Day 11: Enable CI gate
  Day 12: Enable pre-commit hook
  Day 13: Create monitoring dashboard
  Day 14: Final validation & documentation
```

---

## Summary

This plan achieves **100% doc_id coverage** through:

1. **Automated scanning** (auto_assign_doc_ids.py)
2. **Batch processing** (existing batch_mint workflow)
3. **Guard rails** (pre-commit hook + CI gate)
4. **Lifecycle management** (split/merge/move/delete tracking)
5. **Conflict resolution** (duplicate detection & resolution)
6. **Monitoring** (coverage dashboard)

**Total effort**: ~40 hours over 2 weeks  
**Maintenance**: ~1 hour/week after setup

All tools integrate with existing batch workflow (batch_mint.py, merge_deltas.py, write_doc_ids_to_files.py).
