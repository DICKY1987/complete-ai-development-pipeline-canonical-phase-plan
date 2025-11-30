---
doc_id: DOC-GUIDE-QUICK-REFERENCE-199
---

# Abstraction Layer - Quick Reference

**Quick Start Guide for Implementing Abstractions**

---

## 🚀 One-Command Execution

### Generate All Workstream Files
```bash
cd "C:\Users\richg\ALL_AI\Complete AI Development Pipeline – Canonical Phase Plan"

# Create all 12 workstream JSON files
python scripts/batch_file_creator.py \
    --template abstraction/workstream_template.json \
    --items abstraction/workstream_specs.json \
    --output workstreams/ \
    --batch-size 4
```

### Execute by Wave
```bash
# Wave 1 (Week 1-2): Foundation P0
python scripts/run_workstream.py --ws-id ws-abs-003-process-executor  # 2 days
python scripts/run_workstream.py --parallel --ws-ids ws-abs-001-tool-adapter,ws-abs-002-state-store  # 3 days

# Wave 2 (Week 2-3): Config & Events P1
python scripts/run_workstream.py --parallel --ws-ids ws-abs-004-config-manager,ws-abs-005-event-logger,ws-abs-006-workstream-service  # 3 days

# Wave 3 (Week 3-4): File Ops & Data P2
python scripts/run_workstream.py --parallel --ws-ids ws-abs-007-file-store,ws-abs-008-data-provider,ws-abs-009-validation-suite  # 3 days

# Wave 4 (Week 4-6): Advanced P3
python scripts/run_workstream.py --parallel --ws-ids ws-abs-010-error-handler,ws-abs-011-metrics-collector,ws-abs-012-dependency-resolver  # 3 days
```

### Validate After Each Wave
```bash
# Verify all abstractions in wave
pytest tests/interfaces/ -v --cov=core/interfaces --cov-report=term-missing

# Check type safety
mypy core/interfaces/ --strict

# Validate ground truth
./abstraction/verify_wave.sh 1  # Replace 1 with wave number
```

---

## 📋 Abstraction Checklist (Per Workstream)

### Before You Start
- [ ] Read execution pattern: EXEC-002 (Module Generator)
- [ ] Enable all 11 anti-pattern guards
- [ ] Set up ground truth verification command
- [ ] Create workstream branch: `git checkout -b ws-abs-NNN`

### Implementation Steps
1. [ ] **Create Protocol** (`core/interfaces/{name}.py`)
   - Define methods with type hints
   - Add docstrings with usage examples
   - Mark as `@runtime_checkable` Protocol

2. [ ] **Implement Concrete Class** (`core/{module}/{name}_impl.py`)
   - Inherit from Protocol
   - Implement all methods
   - Add error handling

3. [ ] **Write Tests** (`tests/interfaces/test_{name}.py`)
   - Test protocol compliance
   - Test happy path
   - Test error cases
   - Test edge cases
   - Aim for 80%+ coverage

4. [ ] **Migrate Consumers** (varies by abstraction)
   - Update imports
   - Replace direct calls with abstraction
   - Keep old code working with deprecation warnings

5. [ ] **Verify Ground Truth**
   - Run ground truth command
   - Ensure all tests pass
   - Check mypy compliance

6. [ ] **Document**
   - Add usage examples to docstrings
   - Update module README if exists
   - Add migration guide

### After Completion
- [ ] Run full test suite: `pytest tests/ -v`
- [ ] Check code coverage: `pytest --cov=core/interfaces --cov-report=html`
- [ ] Verify no mypy errors: `mypy core/interfaces/ --strict`
- [ ] Update ABSTRACTION_PHASE_PLAN.md with status
- [ ] Create PR with title: `[WS-ABS-NNN] {Title}`
- [ ] Merge to main after review

---

## 🎯 Ground Truth Verification Commands

**Copy-paste these for quick verification**

```bash
# WS-ABS-001: ToolAdapter
test -f core/interfaces/tool_adapter.py && \
python -c "from core.interfaces.tool_adapter import ToolAdapter" && \
pytest tests/interfaces/test_tool_adapter.py -q && \
echo "✅ WS-ABS-001 COMPLETE"

# WS-ABS-002: StateStore
test -f core/interfaces/state_store.py && \
python -c "from core.state.sqlite_store import SQLiteStateStore" && \
pytest tests/interfaces/test_state_store.py -q && \
echo "✅ WS-ABS-002 COMPLETE"

# WS-ABS-003: ProcessExecutor
test -f core/interfaces/process_executor.py && \
python -c "from core.execution.subprocess_executor import SubprocessExecutor" && \
pytest tests/interfaces/test_process_executor.py -q && \
echo "✅ WS-ABS-003 COMPLETE"

# WS-ABS-004: ConfigManager
test -f core/interfaces/config_manager.py && \
pytest tests/interfaces/test_config_manager.py -q && \
echo "✅ WS-ABS-004 COMPLETE"

# WS-ABS-005: EventBus & Logger
test -f core/interfaces/event_bus.py && \
test -f core/interfaces/logger.py && \
pytest tests/interfaces/test_event_bus.py tests/interfaces/test_logger.py -q && \
echo "✅ WS-ABS-005 COMPLETE"

# WS-ABS-006: WorkstreamService
test -f core/interfaces/workstream_service.py && \
pytest tests/interfaces/test_workstream_service.py -q && \
echo "✅ WS-ABS-006 COMPLETE"

# WS-ABS-007: FileStore & PathResolver
test -f core/interfaces/file_store.py && \
test -f core/interfaces/path_resolver.py && \
pytest tests/interfaces/test_file_store.py -q && \
echo "✅ WS-ABS-007 COMPLETE"

# WS-ABS-008: DataProvider
test -f core/interfaces/data_provider.py && \
pytest tests/gui/test_data_provider.py -q && \
echo "✅ WS-ABS-008 COMPLETE"

# WS-ABS-009: ValidationSuite
test -f core/interfaces/validator.py && \
pytest tests/interfaces/test_validator.py -q && \
echo "✅ WS-ABS-009 COMPLETE"

# WS-ABS-010: ErrorHandler
test -f core/interfaces/error_handler.py && \
pytest tests/interfaces/test_error_handler.py -q && \
echo "✅ WS-ABS-010 COMPLETE"

# WS-ABS-011: MetricsCollector
test -f core/interfaces/metrics_collector.py && \
pytest tests/interfaces/test_metrics_collector.py -q && \
echo "✅ WS-ABS-011 COMPLETE"

# WS-ABS-012: DependencyResolver
test -f core/interfaces/dependency_resolver.py && \
pytest tests/interfaces/test_dependency_resolver.py -q && \
echo "✅ WS-ABS-012 COMPLETE"

# Verify all 12 abstractions
for i in {001..012}; do
  test -f core/interfaces/*_${i:1}*.py && echo "✅ Interface ${i} exists" || echo "❌ Interface ${i} missing"
done
```

---

## 📊 Progress Tracking

### Wave 1 (P0 - Foundation)
- [ ] WS-ABS-003: ProcessExecutor (2 days) - **START HERE**
- [ ] WS-ABS-001: ToolAdapter (3 days)
- [ ] WS-ABS-002: StateStore (3 days)

**Wave Completion**: [ ] All tests pass [ ] Mypy clean [ ] 80%+ coverage

### Wave 2 (P1 - Config & Events)
- [ ] WS-ABS-004: ConfigManager (2 days)
- [ ] WS-ABS-005: EventBus & Logger (3 days)
- [ ] WS-ABS-006: WorkstreamService (3 days)

**Wave Completion**: [ ] All tests pass [ ] Mypy clean [ ] 80%+ coverage

### Wave 3 (P2 - File Ops & Data)
- [ ] WS-ABS-007: FileStore & PathResolver (2 days)
- [ ] WS-ABS-008: DataProvider (3 days)
- [ ] WS-ABS-009: ValidationSuite (3 days)

**Wave Completion**: [ ] All tests pass [ ] Mypy clean [ ] 80%+ coverage

### Wave 4 (P3 - Advanced)
- [ ] WS-ABS-010: ErrorHandler (3 days)
- [ ] WS-ABS-011: MetricsCollector (2 days)
- [ ] WS-ABS-012: DependencyResolver (2 days)

**Wave Completion**: [ ] All tests pass [ ] Mypy clean [ ] 80%+ coverage

---

## 🔧 Common Commands

### Testing
```bash
# Run single abstraction tests
pytest tests/interfaces/test_{abstraction}.py -v

# Run all interface tests
pytest tests/interfaces/ -v

# With coverage
pytest tests/interfaces/ --cov=core/interfaces --cov-report=term-missing

# Watch mode (re-run on file change)
pytest-watch tests/interfaces/
```

### Type Checking
```bash
# Check single file
mypy core/interfaces/{abstraction}.py --strict

# Check all interfaces
mypy core/interfaces/ --strict

# Generate type coverage report
mypy core/interfaces/ --html-report mypy-report/
```

### Code Quality
```bash
# Format code
black core/interfaces/ tests/interfaces/

# Lint
ruff check core/interfaces/ tests/interfaces/

# Sort imports
isort core/interfaces/ tests/interfaces/
```

---

## 🚨 Anti-Pattern Guards (Enable ALL)

Before starting ANY workstream, verify these guards are enabled:

1. ✅ **Hallucination of Success** - Use ground truth verification
2. ✅ **Planning Loop Trap** - Max 2 iterations, then execute
3. ✅ **Incomplete Implementation** - No TODO/pass in production code
4. ✅ **Silent Failures** - Explicit error handling required
5. ✅ **Framework Over-Engineering** - Only implement what's needed
6. ✅ **Test-Code Mismatch** - Every method has a test
7. ✅ **Configuration Drift** - Use ConfigManager only
8. ✅ **Module Integration Gap** - Integration tests required
9. ✅ **Documentation Lies** - Type hints enforced
10. ✅ **Partial Success Amnesia** - Checkpoint after each workstream
11. ✅ **Approval Loop** - Automated verification, no human approval

**Verification**: Run `python scripts/enforce_guards.py --check` before starting.

---

## 💡 Quick Tips

### Protocol Definition Template
```python
from typing import Protocol, Any, runtime_checkable

@runtime_checkable
class MyAbstraction(Protocol):
    """One-line description.
    
    Detailed description with usage example.
    
    Example:
        >>> abstraction = ConcreteImplementation()
        >>> result = abstraction.method(args)
    """
    
    def method(self, arg: str) -> Any:
        """Method description.
        
        Args:
            arg: Argument description
            
        Returns:
            Return value description
            
        Raises:
            ValueError: When validation fails
        """
        ...
```

### Test Template
```python
import pytest
from core.interfaces.my_abstraction import MyAbstraction
from core.module.concrete_impl import ConcreteImplementation

class TestMyAbstraction:
    """Test suite for MyAbstraction protocol."""
    
    def test_protocol_compliance(self):
        """Concrete implementation follows protocol."""
        impl = ConcreteImplementation()
        assert isinstance(impl, MyAbstraction)
    
    def test_happy_path(self):
        """Method works with valid input."""
        impl = ConcreteImplementation()
        result = impl.method("valid")
        assert result is not None
    
    def test_error_handling(self):
        """Method raises expected errors."""
        impl = ConcreteImplementation()
        with pytest.raises(ValueError):
            impl.method("invalid")
```

### Migration Pattern
```python
# Step 1: Add abstraction import
from core.interfaces.my_abstraction import MyAbstraction

# Step 2: Inject dependency instead of direct creation
class Consumer:
    def __init__(self, abstraction: MyAbstraction):
        self.abstraction = abstraction
    
    def use(self):
        return self.abstraction.method("data")

# Step 3: Keep old API with deprecation warning
def old_function():
    import warnings
    warnings.warn("Use MyAbstraction instead", DeprecationWarning)
    # ... old implementation
```

---

## 📞 Need Help?

- **Phase Plan**: `abstraction/ABSTRACTION_PHASE_PLAN.md`
- **Workstream Specs**: `abstraction/workstream_specs.json`
- **Execution Patterns**: `docs/reference/ai-agents/EXECUTION_PATTERNS_MANDATORY.md`
- **Templates**: `abstraction/templates/`

**Good luck! 🚀**
