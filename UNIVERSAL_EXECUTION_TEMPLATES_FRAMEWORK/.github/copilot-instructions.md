# GitHub Copilot Instructions – Universal Execution Templates Framework

## Quick Context

**Framework**: Universal Execution Templates (UET) - AI orchestration system  
**Language**: Python 3.8+  
**Architecture**: 4-layer spec-driven (Bootstrap → Engine → Adapters → Resilience)  
**Tests**: 196/196 passing (100%)  
**Status**: Phase 3 Complete (Orchestration Engine operational)

## Critical Rules

### Import Paths (CI ENFORCED)

✅ **Correct**:
```python
from core.bootstrap.orchestrator import BootstrapOrchestrator
from core.engine.orchestrator import Orchestrator
from core.engine.resilience import ResilientExecutor
from core.adapters import AdapterRegistry
from core.state.db import get_db
```

❌ **Forbidden** (will fail CI):
```python
from src.pipeline.*        # Deprecated
from MOD_ERROR_PIPELINE.*  # Deprecated
from legacy.*              # Never import
```

### Edit Zones

**Safe to suggest**:
- `core/**/*.py` - Core implementation
- `tests/**/*.py` - Test files
- `tools/**/*.py` - Utility scripts

**Avoid**:
- `schema/**/*.json` - Schema contracts (review required)
- `specs/**/*.md` - Documentation (read-only)
- `profiles/**` - Project templates (review required)

## Common Patterns

### Adding Tests
```python
# Follow existing patterns in tests/
import pytest
from core.module import MyClass

def test_my_feature():
    """Test description following existing style."""
    obj = MyClass()
    result = obj.method()
    assert result.status == "expected"
```

### Resilience Patterns
```python
from core.engine.resilience import ResilientExecutor

executor = ResilientExecutor()
executor.register_tool(
    "tool_name",
    failure_threshold=5,
    recovery_timeout=60,
    max_retries=3,
    base_delay=1.0
)
result = executor.execute("tool_name", lambda: operation())
```

### Schema Validation
```python
# All artifacts must validate against schemas
from jsonschema import validate
import json

with open('schema/phase_spec.v1.json') as f:
    schema = json.load(f)
validate(instance=my_artifact, schema=schema)
```

## Code Style

- **Indent**: 4 spaces
- **Style**: Black/PEP8 compliant
- **Type hints**: Prefer for new code
- **Docstrings**: Google style for public APIs
- **Naming**: `snake_case` functions, `PascalCase` classes

## Testing Requirements

**Before suggesting changes**:
- All 196 tests must pass: `pytest tests/ -v`
- Add tests for new functionality
- Never comment out or delete tests

**Test command**:
```bash
pytest tests/ -v  # All tests
pytest tests/engine/ -v  # Specific suite
pytest tests/path/test_file.py::test_name -v  # Specific test
```

## Key Modules

| Module | Purpose | Entry Point |
|--------|---------|-------------|
| `core/bootstrap/` | Project auto-discovery | `orchestrator.BootstrapOrchestrator` |
| `core/engine/` | Task orchestration | `orchestrator.Orchestrator` |
| `core/engine/resilience/` | Fault tolerance | `resilient_executor.ResilientExecutor` |
| `core/adapters/` | Tool integration | `registry.AdapterRegistry` |
| `core/state/` | SQLite persistence | `db.get_db()` |

## Schema-Driven Development

1. **All artifacts validate** against JSON schemas in `schema/`
2. **Schema changes** require new version (`.v1.json` → `.v2.json`)
3. **No schema modifications** without backwards compatibility plan

## Common Validation Commands

```bash
# Run all tests (REQUIRED before commits)
pytest tests/ -v

# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('file.yaml'))"

# Validate JSON syntax
python -c "import json; json.load(open('file.json'))"

# Check import paths (CI gate)
grep -r "from src\\." core/ tests/  # Should return nothing
```

## Invariants (Must Always Hold)

1. ✅ **196/196 tests pass** - No exceptions
2. ✅ **Schema validation** - All artifacts conform to schemas
3. ✅ **Import paths** - Use `core.*`, never `src.*` or `MOD_*`
4. ✅ **Phase constraints** - ExecutionRequest ≤ Phase constraints
5. ✅ **State machine** - All transitions via `RunStateMachine`
6. ✅ **No secrets** - Never commit credentials

## Quick Reference Links

- **Full guidance**: See `CLAUDE.md` in repository root
- **Module index**: See `CODEBASE_INDEX.yaml`
- **Edit policies**: See `ai_policies.yaml`
- **Quality gates**: See `QUALITY_GATE.yaml`
- **Quick start**: See `.meta/AI_GUIDANCE.md`

## Suggestions Should Be

✅ **Small** - 1-3 functions per suggestion  
✅ **Targeted** - Fix specific issue, don't refactor unrelated code  
✅ **Safe** - Respect edit zones and constraints  
✅ **Tested** - Remind to run tests after changes  

❌ **Avoid**:
- Large refactors across many files
- Breaking changes without deprecation
- Modifying test assertions to make them pass
- Introducing new dependencies without discussion

---

**Version**: 1.0.0  
**Generated**: 2025-11-23  
**Maintenance**: Update when common Copilot patterns emerge
