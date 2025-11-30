---
doc_id: DOC-GUIDE-WEEK1-IMPLEMENTATION-1298
---

# UET Integration - Week 1 Implementation Plan

**Date**: 2025-11-22  
**Phase**: Foundation Setup  
**Estimated Time**: 10-12 hours  
**Status**: Ready to Start  

---

## Overview

Week 1 focuses on **safe, non-breaking integration** of UET framework modules into the existing pipeline structure. All changes are additive - no existing functionality is modified.

---

## Day 1-2: Module Integration (4 hours)

### Task 1.1: Copy UET Bootstrap System

**Action:**
```bash
# Create target directory
mkdir -p core/bootstrap_uet

# Copy UET bootstrap modules
cp UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/bootstrap/*.py core/bootstrap_uet/

# Verify files
ls core/bootstrap_uet/
# Expected: __init__.py, discovery.py, selector.py, generator.py, validator.py, orchestrator.py
```

**Verification:**
```python
# Test import
python -c "from core.bootstrap_uet import ProjectScanner; print('✓ Bootstrap import OK')"
```

### Task 1.2: Copy UET Resilience Module

**Action:**
```bash
# Create target directory
mkdir -p core/engine/resilience

# Copy UET resilience modules
cp UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/resilience/*.py core/engine/resilience/

# Verify files
ls core/engine/resilience/
# Expected: __init__.py, circuit_breaker.py, retry.py, resilient_executor.py
```

**Verification:**
```python
# Test import
python -c "from core.engine.resilience import ResilientExecutor; print('✓ Resilience import OK')"
```

### Task 1.3: Copy UET Monitoring Module

**Action:**
```bash
# Create target directory
mkdir -p core/engine/monitoring

# Copy UET monitoring modules
cp UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/core/engine/monitoring/*.py core/engine/monitoring/

# Verify files
ls core/engine/monitoring/
# Expected: __init__.py, progress_tracker.py, run_monitor.py
```

**Verification:**
```python
# Test import
python -c "from core.engine.monitoring import ProgressTracker; print('✓ Monitoring import OK')"
```

---

## Day 2-3: Schema Integration (3 hours)

### Task 2.1: Copy UET Schemas

**Action:**
```bash
# Copy project profile schema
cp UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/schema/project_profile.v1.json schema/

# Copy router config schema
cp UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/schema/router_config.v1.json schema/

# Verify
ls schema/*.v1.json
```

### Task 2.2: Copy UET Profiles

**Action:**
```bash
# Create profiles directory
mkdir -p profiles

# Copy all UET profiles
cp -r UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/profiles/* profiles/

# Verify
ls profiles/
# Expected: software-dev-python/, data-pipeline/, documentation/, operations/, generic/
```

### Task 2.3: Create Database Migration

**File**: `schema/migrations/002_uet_foundation.sql`

```sql
-- UET Foundation Migration
-- Version: 002
-- Created: 2025-11-22
-- Purpose: Add UET framework tables (workers, events, cost_tracking)

-- ============================================================================
-- Workers Table - Track tool adapter instances
-- ============================================================================

CREATE TABLE IF NOT EXISTS workers (
  worker_id TEXT PRIMARY KEY,
  adapter_type TEXT NOT NULL,
  state TEXT NOT NULL CHECK(state IN ('IDLE', 'BUSY', 'TERMINATED')),
  current_task_id TEXT,
  heartbeat_at TEXT,
  spawned_at TEXT NOT NULL DEFAULT (datetime('now')),
  terminated_at TEXT,
  FOREIGN KEY (current_task_id) REFERENCES steps(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_workers_state ON workers(state);
CREATE INDEX IF NOT EXISTS idx_workers_adapter ON workers(adapter_type);

-- ============================================================================
-- Events Table - Centralized event logging
-- ============================================================================

CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_type TEXT NOT NULL,
  worker_id TEXT,
  task_id TEXT,
  run_id TEXT,
  timestamp TEXT NOT NULL DEFAULT (datetime('now')),
  payload JSON,
  FOREIGN KEY (worker_id) REFERENCES workers(worker_id) ON DELETE SET NULL,
  FOREIGN KEY (task_id) REFERENCES steps(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_run ON events(run_id);

-- ============================================================================
-- Cost Tracking Table - Token usage and API costs
-- ============================================================================

CREATE TABLE IF NOT EXISTS cost_tracking (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  step_id TEXT NOT NULL,
  worker_id TEXT,
  input_tokens INTEGER DEFAULT 0,
  output_tokens INTEGER DEFAULT 0,
  estimated_cost_usd REAL DEFAULT 0.0,
  model_name TEXT,
  timestamp TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (step_id) REFERENCES steps(id) ON DELETE CASCADE,
  FOREIGN KEY (worker_id) REFERENCES workers(worker_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_cost_step ON cost_tracking(step_id);
CREATE INDEX IF NOT EXISTS idx_cost_timestamp ON cost_tracking(timestamp);

-- ============================================================================
-- Migration Metadata
-- ============================================================================

INSERT OR IGNORE INTO schema_version (version, applied_at, description)
VALUES (
  2,
  datetime('now'),
  'UET Foundation: workers, events, cost_tracking tables'
);
```

**Test Migration:**
```bash
# Apply migration to test database
sqlite3 .worktrees/pipeline_state_test.db < schema/migrations/002_uet_foundation.sql

# Verify tables created
sqlite3 .worktrees/pipeline_state_test.db "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('workers', 'events', 'cost_tracking');"
```

---

## Day 3-4: Bootstrap Integration (3 hours)

### Task 3.1: Create Bootstrap Wrapper

**File**: `core/bootstrap_uet/__init__.py`

```python
"""
UET Bootstrap Integration

Wraps UET bootstrap system for seamless integration with existing pipeline.
Maintains compatibility with existing bootstrap scripts.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Optional, Any

__version__ = "1.0.0"

# Import UET bootstrap modules
try:
    from .discovery import ProjectScanner
    from .selector import ProfileSelector
    from .generator import ArtifactGenerator
    from .validator import BootstrapValidator
    from .orchestrator import BootstrapOrchestrator
except ImportError as e:
    print(f"Warning: UET bootstrap modules not available: {e}", file=sys.stderr)
    ProjectScanner = None
    ProfileSelector = None
    ArtifactGenerator = None
    BootstrapValidator = None
    BootstrapOrchestrator = None

__all__ = [
    'bootstrap_project',
    'validate_bootstrap',
    'ProjectScanner',
    'ProfileSelector',
    'ArtifactGenerator',
    'BootstrapValidator',
    'BootstrapOrchestrator'
]


def bootstrap_project(
    project_path: str = ".",
    output_dir: Optional[str] = None,
    quiet: bool = False,
    validate_only: bool = False
) -> Dict[str, Any]:
    """
    Bootstrap the current project with UET framework.
    
    This function analyzes the project structure, selects an appropriate
    profile, and generates configuration files (PROJECT_PROFILE.yaml,
    router_config.json).
    
    Args:
        project_path: Path to project root (default: current directory)
        output_dir: Output directory for artifacts (default: project_path)
        quiet: Suppress output (default: False)
        validate_only: Only validate existing artifacts (default: False)
    
    Returns:
        Bootstrap result dictionary with keys:
        - success: bool - Whether bootstrap succeeded
        - domain: str - Detected project domain
        - profile_id: str - Selected profile ID
        - generated_files: list - Files created
        - error: str - Error message (if failed)
    
    Example:
        >>> result = bootstrap_project(".", quiet=True)
        >>> if result['success']:
        >>>     print(f"Profile: {result['profile_id']}")
    """
    if BootstrapOrchestrator is None:
        return {
            'success': False,
            'error': 'UET bootstrap modules not available'
        }
    
    try:
        orchestrator = BootstrapOrchestrator(project_path, output_dir)
        result = orchestrator.run()
        
        if not quiet:
            _print_bootstrap_summary(result)
        
        return result
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def validate_bootstrap(
    project_path: str = ".",
    quiet: bool = False
) -> Dict[str, Any]:
    """
    Validate existing bootstrap artifacts without regeneration.
    
    Args:
        project_path: Path to project root
        quiet: Suppress output
    
    Returns:
        Validation result dictionary
    """
    if BootstrapValidator is None:
        return {
            'valid': False,
            'error': 'UET bootstrap modules not available'
        }
    
    try:
        project_root = Path(project_path).resolve()
        profile_file = project_root / "PROJECT_PROFILE.yaml"
        router_file = project_root / "router_config.json"
        
        if not profile_file.exists() or not router_file.exists():
            return {
                'valid': False,
                'error': 'Missing bootstrap artifacts. Run bootstrap_project() first.'
            }
        
        validator = BootstrapValidator(
            str(profile_file),
            str(router_file),
            None  # Will detect from profile
        )
        
        result = validator.validate()
        
        if not quiet:
            _print_validation_summary(result)
        
        return result
    
    except Exception as e:
        return {
            'valid': False,
            'error': str(e)
        }


def _print_bootstrap_summary(result: Dict[str, Any]) -> None:
    """Print human-readable bootstrap summary."""
    print("\n" + "="*60)
    if result.get('success'):
        print("✅ UET Bootstrap Complete!")
        print(f"  Domain: {result.get('domain', 'unknown')}")
        print(f"  Profile: {result.get('profile_id', 'unknown')}")
        if result.get('primary_language'):
            print(f"  Language: {result.get('primary_language')}")
        print("\n  Generated files:")
        for f in result.get('generated_files', []):
            print(f"    - {f}")
    else:
        print("❌ Bootstrap Failed")
        print(f"  Error: {result.get('error', 'unknown error')}")
    print("="*60 + "\n")


def _print_validation_summary(result: Dict[str, Any]) -> None:
    """Print human-readable validation summary."""
    print("\n" + "="*60)
    if result.get('valid'):
        print("✅ Bootstrap Artifacts Valid")
    else:
        print("❌ Validation Failed")
        if result.get('errors'):
            print("\n  Errors:")
            for err in result['errors']:
                print(f"    - {err}")
        if result.get('warnings'):
            print("\n  Warnings:")
            for warn in result['warnings']:
                print(f"    - {warn}")
    print("="*60 + "\n")
```

### Task 3.2: Create CLI Script

**File**: `scripts/bootstrap_uet.py`

```python
#!/usr/bin/env python3
"""
UET Bootstrap CLI

Standalone tool for running UET bootstrap on any project.

Usage:
    python scripts/bootstrap_uet.py                 # Bootstrap current directory
    python scripts/bootstrap_uet.py /path/to/proj   # Bootstrap specific project
    python scripts/bootstrap_uet.py --validate-only # Validate existing artifacts
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.bootstrap_uet import bootstrap_project, validate_bootstrap

def main():
    parser = argparse.ArgumentParser(
        description="Bootstrap project with UET Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Bootstrap current directory
  %(prog)s /path/to/project          # Bootstrap specific project
  %(prog)s --validate-only           # Validate existing artifacts
  %(prog)s --output-dir /tmp/test    # Custom output directory
        """
    )
    
    parser.add_argument(
        'project_path',
        nargs='?',
        default='.',
        help='Path to project root (default: current directory)'
    )
    
    parser.add_argument(
        '--output-dir',
        help='Output directory for generated files (default: project_path)'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress output'
    )
    
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Validate existing artifacts without regeneration'
    )
    
    args = parser.parse_args()
    
    try:
        if args.validate_only:
            result = validate_bootstrap(args.project_path, args.quiet)
            success = result.get('valid', False)
        else:
            result = bootstrap_project(
                args.project_path,
                args.output_dir,
                args.quiet
            )
            success = result.get('success', False)
        
        sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.", file=sys.stderr)
        sys.exit(130)
    
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
```

**Make executable:**
```bash
chmod +x scripts/bootstrap_uet.py
```

### Task 3.3: Update Main Bootstrap Script

**File**: `scripts/bootstrap.ps1` (append to end)

```powershell
# ============================================================================
# UET Bootstrap Integration
# ============================================================================

Write-Host "`n==> UET Framework Bootstrap..." -ForegroundColor Cyan

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Warning "Python not found, skipping UET bootstrap"
} else {
    try {
        python scripts/bootstrap_uet.py . --quiet
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   OK - PROJECT_PROFILE.yaml generated" -ForegroundColor Green
            Write-Host "   OK - router_config.json generated" -ForegroundColor Green
        } else {
            Write-Warning "UET bootstrap failed (continuing anyway)"
        }
    } catch {
        Write-Warning "UET bootstrap error: $_"
    }
}
```

---

## Day 4-5: Testing & Validation (2 hours)

### Task 4.1: Run Bootstrap on Pipeline

```bash
# Test bootstrap CLI
python scripts/bootstrap_uet.py .

# Verify generated files
ls PROJECT_PROFILE.yaml router_config.json

# Validate artifacts
python scripts/bootstrap_uet.py --validate-only
```

### Task 4.2: Create Integration Tests

**File**: `tests/uet_integration/test_bootstrap.py`

```python
"""Test UET bootstrap integration."""

import pytest
import yaml
import json
from pathlib import Path
from core.bootstrap_uet import bootstrap_project, validate_bootstrap

class TestBootstrapIntegration:
    """Test UET bootstrap integration."""
    
    def test_import_modules(self):
        """Test UET modules can be imported."""
        from core.bootstrap_uet import ProjectScanner
        from core.bootstrap_uet import ProfileSelector
        from core.bootstrap_uet import ArtifactGenerator
        from core.bootstrap_uet import BootstrapValidator
        
        assert ProjectScanner is not None
        assert ProfileSelector is not None
        assert ArtifactGenerator is not None
        assert BootstrapValidator is not None
    
    def test_bootstrap_current_project(self):
        """Test bootstrapping the pipeline itself."""
        result = bootstrap_project(".", quiet=True)
        
        assert result['success'], f"Bootstrap failed: {result.get('error')}"
        assert result['domain'] in ['software-dev', 'mixed']
        assert 'profile_id' in result
        assert Path('PROJECT_PROFILE.yaml').exists()
        assert Path('router_config.json').exists()
    
    def test_generated_profile_valid_yaml(self):
        """Test generated profile is valid YAML."""
        with open('PROJECT_PROFILE.yaml') as f:
            profile = yaml.safe_load(f)
        
        # Basic structure checks
        assert 'project_id' in profile
        assert 'domain' in profile
        assert 'profile_id' in profile
        assert 'available_tools' in profile
        assert 'framework_paths' in profile
    
    def test_generated_router_valid_json(self):
        """Test generated router config is valid JSON."""
        with open('router_config.json') as f:
            router = json.load(f)
        
        # Basic structure checks
        assert 'adapters' in router or 'tools' in router
    
    def test_validate_bootstrap(self):
        """Test validation of existing artifacts."""
        result = validate_bootstrap(".", quiet=True)
        
        # Should be valid after bootstrap
        assert result.get('valid', False), f"Validation failed: {result.get('error')}"
    
    def test_bootstrap_idempotent(self):
        """Test bootstrap can be run multiple times safely."""
        result1 = bootstrap_project(".", quiet=True)
        result2 = bootstrap_project(".", quiet=True)
        
        assert result1['success']
        assert result2['success']
        # Profile should be consistent
        assert result1.get('profile_id') == result2.get('profile_id')
```

**Run tests:**
```bash
pytest tests/uet_integration/test_bootstrap.py -v
```

### Task 4.3: Database Migration Test

```bash
# Create test database
cp .worktrees/pipeline_state.db .worktrees/pipeline_state_backup.db

# Apply migration
sqlite3 .worktrees/pipeline_state.db < schema/migrations/002_uet_foundation.sql

# Verify tables exist
sqlite3 .worktrees/pipeline_state.db "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
# Should see: workers, events, cost_tracking (among others)

# Check migration metadata
sqlite3 .worktrees/pipeline_state.db "SELECT version, description FROM schema_version ORDER BY version;"
```

---

## Week 1 Checklist

### Module Integration
- [ ] Copy `core/bootstrap_uet/` modules
- [ ] Copy `core/engine/resilience/` modules
- [ ] Copy `core/engine/monitoring/` modules
- [ ] Verify imports work

### Schema Integration
- [ ] Copy `schema/project_profile.v1.json`
- [ ] Copy `schema/router_config.v1.json`
- [ ] Copy `profiles/` directory
- [ ] Create `schema/migrations/002_uet_foundation.sql`
- [ ] Test migration on copy of database

### Bootstrap Integration
- [ ] Create `core/bootstrap_uet/__init__.py` wrapper
- [ ] Create `scripts/bootstrap_uet.py` CLI
- [ ] Update `scripts/bootstrap.ps1`
- [ ] Test bootstrap on pipeline itself

### Testing
- [ ] Create `tests/uet_integration/test_bootstrap.py`
- [ ] Run bootstrap tests
- [ ] Verify generated files are valid
- [ ] Test migration idempotency

### Documentation
- [ ] Review `docs/UET_INTEGRATION_DESIGN.md`
- [ ] Create user guide (optional for Week 1)
- [ ] Update README.md (optional for Week 1)

---

## Expected Outcomes

By end of Week 1, you should have:

1. ✅ **UET modules integrated** - Bootstrap, resilience, monitoring available
2. ✅ **Schemas added** - Project profile and router config schemas
3. ✅ **Database extended** - Workers, events, cost_tracking tables
4. ✅ **Bootstrap working** - Can run `python scripts/bootstrap_uet.py .`
5. ✅ **Generated artifacts** - PROJECT_PROFILE.yaml and router_config.json
6. ✅ **Tests passing** - Bootstrap integration tests green
7. ✅ **Zero regressions** - All existing tests still pass

---

## Troubleshooting

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'core.bootstrap_uet'`

**Solution**:
```bash
# Verify files copied correctly
ls core/bootstrap_uet/
# Should see: __init__.py and other modules

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
# Should include project root
```

### Bootstrap Fails

**Problem**: Bootstrap crashes or returns `success: False`

**Solution**:
```bash
# Run with verbose output
python scripts/bootstrap_uet.py . --verbose

# Check UET framework is accessible
ls UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK/

# Try UET's own orchestrator directly
cd UNIVERSAL_EXECUTION_TEMPLATES_FRAMEWORK
python core/bootstrap/orchestrator.py ..
```

### Migration Errors

**Problem**: Migration fails with "table already exists"

**Solution**:
```sql
-- Migration uses CREATE TABLE IF NOT EXISTS
-- Safe to run multiple times

-- If you need to reset:
DROP TABLE IF EXISTS workers;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS cost_tracking;

-- Then re-run migration
```

---

## Next Week Preview

Week 2 will focus on **Resilience Integration**:
- Wrap existing tool invocations with `ResilientExecutor`
- Configure circuit breakers for each tool
- Add retry logic with exponential backoff
- Create health monitoring CLI

---

**Ready to proceed? Run:**
```bash
pwsh scripts/bootstrap.ps1
python scripts/bootstrap_uet.py .
pytest tests/uet_integration/test_bootstrap.py -v
```
