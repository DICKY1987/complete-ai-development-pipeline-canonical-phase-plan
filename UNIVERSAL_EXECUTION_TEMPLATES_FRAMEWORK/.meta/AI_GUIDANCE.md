# AI Agent Quick Start Guide
**Read this FIRST before any session - saves 25 min onboarding time**

---

## 1. This Codebase in 60 Seconds

**What**: Universal Execution Templates (UET) Framework - production AI orchestration system
**Architecture**: 4-layer spec-driven pipeline (Bootstrap → Engine → Adapters → Resilience)
**Database**: `.worktrees/pipeline_state.db` (SQLite) - ENV > arg > default path resolution
**Entry Point**: `core.engine.orchestrator.Orchestrator` (run management + task routing)
**Tests**: 337 tests, 100% collection rate
**Status**: Phase 3 Complete (78% overall), fully operational orchestration engine

**Section Architecture**:
```
core/          - Engine, state management, planning
error/         - Plugin-based error detection/fixing
aim/           - AI tool bridge (capability matching)
pm/            - Project metadata management
specifications/- Spec tooling (validator, indexer, generator)
```

---

## 2. Common AI Gotchas (CRITICAL - Read First)

### ❌ **NEVER** Import From These (CI WILL BLOCK):
```python
from src.pipeline.*           # ❌ Deprecated - use core.*
from MOD_ERROR_PIPELINE.*     # ❌ Deprecated - use error.*
from legacy.*                 # ❌ Never import
```

### ✅ **ALWAYS** Use Section-Based Paths:
```python
from core.state.db import init_db
from core.engine.orchestrator import Orchestrator
from error.engine.error_engine import ErrorEngine
from error.plugins.python_ruff.plugin import parse
from aim.bridge import get_tool_info
```

### Database Path Resolution:
```python
# Order: ENV var > function arg > default
db_path = os.getenv('UET_DB_PATH') or db_path_arg or '.worktrees/pipeline_state.db'
```

### Workstream DAG Validation:
- **Always check for cycles** before committing workstreams
- Use `scripts/validate_workstreams.py` to verify
- Dependencies must form directed acyclic graph

### Error Plugin Discovery:
- Plugins auto-discovered via `manifest.json` in plugin directory
- Must implement `parse()` method (required)
- Optional: `fix()` method for auto-repair

---

## 3. Typical Task Patterns

### Add Error Plugin
```bash
# 1. Copy template
cp -r error/plugins/python_ruff error/plugins/my_plugin

# 2. Update manifest
edit error/plugins/my_plugin/manifest.json

# 3. Implement parse()
edit error/plugins/my_plugin/plugin.py

# 4. Add tests
create tests/error/plugins/test_my_plugin.py

# 5. Validate
python -m pytest tests/error/plugins/test_my_plugin.py -q
```

### Add Script to Scripts/
```bash
# 1. Create script
create scripts/my_script.py

# 2. If validation script, add to QUALITY_GATE.yaml
edit QUALITY_GATE.yaml  # Add gate definition

# 3. Test
python scripts/my_script.py --help
```

### Modify DB Schema
```bash
# 1. Create migration
create schema/migrations/00X_description.sql

# 2. Update schema docs
edit schema/README.md

# 3. Test migration
python core/state/db.py --migrate

# 4. Validate
python -m pytest tests/state/test_db.py -q
```

---

## 4. Quick Commands (Copy-Paste Ready)

```bash
# Run all tests
python -m pytest tests -q

# Run specific test file
python -m pytest tests/engine/test_orchestrator.py -q

# Validate workstreams (check DAG cycles)
python scripts/validate_workstreams.py

# Check deprecated import paths (CI gate)
python scripts/paths_index_cli.py gate --db refactor_paths.db

# Generate architecture index
python scripts/generate_codebase_index.py

# Run quality gates
python scripts/run_quality_gates.py
```

---

## 5. Speed Demon Principles (Decision Elimination)

### Ground Truth Over Vibes
✅ **DO**: Base decisions ONLY on observable CLI output
```bash
python -m pytest tests -q
# Output: "337 passed in 2.5s" → GROUND TRUTH: All tests pass
```

❌ **DON'T**: "This looks right" without running verification

### Atomic Execution
✅ **DO**: Small, focused changes (1-3 files per commit)
❌ **DON'T**: Refactor 20+ files in one phase

### No Planning Overhead
✅ **DO**: Use existing templates and patterns
❌ **DON'T**: Spend 80k tokens planning before first line of code

### Template-Driven
✅ **DO**: Copy working patterns (error plugin template, test template)
❌ **DON'T**: Reinvent structure for every similar task

---

## 6. Module Navigation Quick Reference

| Module | Purpose | Entry Point | Layer |
|--------|---------|-------------|-------|
| `core.engine` | Orchestrator, scheduler, router | `orchestrator.Orchestrator` | domain |
| `core.state` | SQLite state management | `db.init_db()` | infra |
| `core.planning` | Workstream/phase specs | `workstream.Workstream` | domain |
| `error.engine` | Error detection pipeline | `error_engine.ErrorEngine` | domain |
| `error.plugins.*` | Tool-specific detectors | `plugin.parse()` | api |
| `aim.bridge` | AI tool capability matching | `bridge.get_tool_info()` | api |
| `pm.metadata` | Project profile management | `metadata.load_profile()` | domain |
| `specifications.tools` | Spec generator/validator | `indexer.generate_index()` | api |

---

## 7. Common Edit Patterns

### ✅ Safe to Edit (No Review Needed)
Work directly in these zones:
- `core/**/*.py` - Core engine, state, planning
- `error/**/*.py` - Error engine, plugins
- `aim/**/*.py` - AI tool bridge
- `pm/**/*.py` - Project management
- `specifications/tools/**/*.py` - Spec tooling
- `tests/**/*.py` - All test files
- `scripts/**/*.{py,ps1}` - Automation scripts

### ⚠️ Review Required
Coordinate before editing:
- `schema/**/*.json` - Schema contracts (validate downstream impact)
- `config/**/*.yaml` - Configuration (affects all tools)
- `core/state/db*.py` - Database operations (coordinate with migrations)

### ❌ Read-Only (Never Edit)
- `legacy/**` - Archived deprecated code
- `src/pipeline/**` - Deprecated (use `core.*` instead)
- `MOD_ERROR_PIPELINE/**` - Deprecated (use `error.*` instead)
- `docs/adr/**` - Architecture Decision Records (append only)

---

## 8. Decision Elimination Cheatsheet

| Decision | Pre-Made Answer |
|----------|----------------|
| **"What structure?"** | Use template from similar module |
| **"How detailed?"** | Good enough > perfect (50-100 lines for manifests, complete functions for code) |
| **"How to verify?"** | Run ground truth command (pytest, validate script) |
| **"Is it complete?"** | Tests pass + files exist + CLI output matches expected |
| **"Should I continue?"** | Yes, until all acceptance checks green |
| **"Need permission?"** | No for safe zones, auto-fix scenarios. Yes for destructive ops. |
| **"How to handle errors?"** | Check pre-authorized auto-fixes first, then ask |

---

## 9. File Existence Quick Checks

```bash
# Check module manifest exists
Test-Path core/.ai-module-manifest

# Check test file exists
Test-Path tests/engine/test_orchestrator.py

# Check schema exists
Test-Path schema/phase_spec.v1.json

# List all manifests
Get-ChildItem -Recurse -Filter .ai-module-manifest
```

---

## 10. Test Patterns

### Run Tests Before/After Changes
```bash
# Before: Establish baseline
python -m pytest tests -q

# After: Verify no regression
python -m pytest tests -q
```

### Test-Driven Development
```bash
# 1. Write failing test
python -m pytest tests/my_test.py::test_new_feature -v
# Expected: FAILED

# 2. Implement feature
edit src/module.py

# 3. Verify test passes
python -m pytest tests/my_test.py::test_new_feature -v
# Expected: PASSED
```

---

## 11. Common Validation Commands

```bash
# Validate all schemas
python scripts/validate_all_schemas.py

# Check ACS conformance
python scripts/validate_acs_conformance.py

# Validate module manifests
python scripts/validate_module_manifests.py --strict

# Check documentation links
python scripts/validate_doc_links.py --report-only
```

---

## 12. When to Ask for Help

### ✅ Proceed Without Asking
- Creating test files in `tests/`
- Fixing obvious bugs in `core/`, `error/`, `aim/`, `pm/`
- Adding scripts to `scripts/`
- Improving docstrings/comments
- Auto-fixing import errors (install missing packages)
- Auto-creating missing directories

### ⚠️ Ask First
- Modifying database schema
- Changing CI/CD pipelines (`.github/workflows/`)
- Removing or disabling tests
- Editing deprecated paths (should never happen)
- Large refactors (>10 files)

---

## 13. Success Criteria (Ground Truth)

A task is complete when **ALL** of these are true:
1. ✅ Tests pass: `python -m pytest tests -q` → "X passed"
2. ✅ Files exist: `Test-Path <file>` → True
3. ✅ No scope violations: Only declared files touched
4. ✅ Validation scripts pass: Exit code 0
5. ✅ Git status clean or expected: No surprise modifications

**NOT** complete if:
- ❌ "This looks right" (without running tests)
- ❌ "Probably works" (without CLI verification)
- ❌ "Should be fine" (without ground truth check)

---

## 14. Emergency Recovery

### Undo Last Commit
```bash
git reset --soft HEAD~1
```

### Restore File to Last Commit
```bash
git checkout HEAD -- path/to/file
```

### Check What Would Be Committed
```bash
git status --porcelain
git diff --staged
```

---

## 15. Speed Optimization Tips

1. **Batch similar operations** - Create 3 test files in one turn, not 3 separate turns
2. **Use parallel tool calls** - Read 3 files simultaneously with multiple `view` calls
3. **Trust ground truth** - If tests pass, don't manually re-verify
4. **Template everything** - Second time doing similar task? Extract template
5. **No planning documents** - Work in memory, only create files when user asks

---

**Version**: 1.0  
**Last Updated**: 2025-11-23  
**Maintenance**: Update when onboarding pain points discovered  
